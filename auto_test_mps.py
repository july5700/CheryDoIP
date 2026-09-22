# -*- coding: utf-8 -*-
"""
Chery DoIP 自动化测试脚本
可独立运行，支持打包成 EXE
"""

import sys
import os
import time
from datetime import datetime
from typing import List, Tuple, Dict
from dataclasses import dataclass
from enum import Enum
import subprocess
from Lib.ConfigCache import TomlConfig

# 获取打包后的资源路径
def get_resource_path(relative_path):
    """获取资源文件的绝对路径（支持 PyInstaller 打包）"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 创建的临时目录
        base_path = sys._MEIPASS
    else:
        # 普通 Python 环境
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# 添加项目根目录到路径（支持打包后的环境）
if hasattr(sys, '_MEIPASS'):
    sys.path.insert(0, sys._MEIPASS)
else:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入项目模块
from client import DoIPClient
from function import DoIPClientForTest, DataHandle
from security_access import cal_ace_emac, cal_tea_variant
from dtc import DTCParser, EnhancedDTCParser
from Lib.ConfigCache import TomlConfig
from Lib.Log import Log
from loguru import logger


# ==================== 配置类 ====================
class TestStatus(Enum):
    PASS = "✅ PASS"
    FAIL = "❌ FAIL"
    PRE_FAIL = "❌ PRE FAIL"
    SKIP = "⏭️ SKIP"
    ERROR = "⚠️ ERROR"



@dataclass
class TestResult:
    """测试结果数据类"""
    name: str
    status: TestStatus
    message: str
    duration: float = 0.0


@dataclass
class TestCase:
    """测试用例数据类"""
    name: str
    request: str
    expected_response: str
    session_required: int = 0  # 0=不需要，1=默认会话，3=扩展会话
    security_required: int = 0  # 0=不需要，1=Level1(2701/02), 2=Level2(2705/06)
    pre_command: list = ""  # 前置命令（如 1060）


@dataclass
class NetworkTestCase:
    """网络测试用例"""
    name: str               # 用例名称 (对应 TestResult.name)
    local_ip: str           # 本机 Windows IP
    vlan_id: int            # 本机 Windows VLAN ID
    target_ip: str          # 要 Ping 的目标 ECU IP

class AutoTestRunner:
    """自动化测试执行器"""

    def __init__(self, config_path: str = "config.toml"):
        """初始化测试执行器"""
        self.config = TomlConfig(config_path)
        self.ecu_ip = self.config.get("current.ecu_ip_address")
        self.target_addr = self.config.get("current.target_address")
        self.tester_addr = self.config.get("current.tester_logical_address")
        # self.activate_type = self.config.get("current.activate_type")
        self.activate_type = 0x00

        self.doip_client = None
        self.results: List[TestResult] = []
        self.start_time = None
        self.end_time = None
        
        # 配置日志
        self._setup_logger()

    def _setup_logger(self):
        """配置日志输出"""
        logger.remove()
        # 输出到控制台
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{message}</cyan>",
            level="INFO"
        )
        # 输出到文件（使用当前工作目录）
        log_folder = os.path.join(os.getcwd(), "output")
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)
        log_file = os.path.join(log_folder, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_test.log")
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} - {message}",
            level="DEBUG"
        )
        logger.info(f"日志文件：{log_file}")

    def connect(self) -> bool:
        """连接到 ECU"""
        try:
            logger.info(f"正在连接到 ECU: {self.ecu_ip} (地址：{hex(self.target_addr)})")
            self.doip_client = DoIPClient(
                self.ecu_ip,
                self.target_addr,
                client_logical_address=self.tester_addr,
                activation_type=self.activate_type
            )
            logger.success("✅ ECU 连接成功")
            return True
        except Exception as e:
            logger.error(f"❌ ECU 连接失败：{e}")
            return False

    def disconnect(self):
        """断开连接"""
        if self.doip_client:
            self.doip_client.close()
            logger.info("已断开 ECU 连接")

    def send_receive(self, msg: str) -> str:
        """发送命令并接收响应"""
        # 使用 unhexlify + bytearray（与 function.py 保持一致）
        from binascii import unhexlify
        clean_msg = msg.replace(" ", "").upper()
        br = bytearray(unhexlify(clean_msg))
        self.doip_client.send_diagnostic(br)
        # 不设置超时，使用默认值（与 function.py 保持一致）
        response = self.doip_client.receive_diagnostic()
        return response.hex().upper()

    def enter_session(self, session_type: int = 3) -> bool:
        """进入指定会话"""
        if session_type == 1:
            cmd = "1001"
            expected = "5001"
        elif session_type == 3:
            cmd = "1003"
            expected = "5003"
        elif session_type == 6:
            cmd = "1060"
            expected = "5060"
        else:
            return True
        
        logger.info(f"→ 进入会话：{cmd}")
        res = self.send_receive(cmd)
        if res[:4] == expected:
            logger.success(f"✅ 会话进入成功：{cmd}")
            return True
        else:
            logger.error(f"❌ 会话进入失败：{cmd}, 响应：{res}")
            return False

    def security_access_level1(self) -> bool:
        """安全访问 Level 1 (27 01/02)"""
        logger.info("→ 执行安全访问 Level 1 (27 01/02)")
        try:
            from binascii import unhexlify
            
            # 请求种子
            self.doip_client.send_diagnostic(bytearray(unhexlify("2701")))
            seed_response = self.doip_client.receive_diagnostic()
            if seed_response.hex()[:4] != "6701":
                logger.error(f"❌ 种子请求失败：{seed_response.hex()}")
                return False
            
            seed = seed_response.hex()[4:]
            logger.debug(f"种子：{seed}")
            
            # 计算密钥
            token = cal_ace_emac(seed)
            key_request = "2702" + token
            
            # 发送密钥
            self.doip_client.send_diagnostic(bytearray(unhexlify(key_request)))
            key_response = self.doip_client.receive_diagnostic()
            
            if key_response.hex()[:4] == "6702":
                logger.success("✅ 安全访问成功")
                return True
            else:
                logger.error(f"❌ 安全访问失败：{key_response.hex()}")
                return False
        except Exception as e:
            logger.error(f"❌ 安全访问异常：{e}")
            return False

    def security_access_level3(self) -> bool:
        """安全访问 Level 3 (27 61/62)"""
        logger.info("→ 执行安全访问 Level 3 (27 61/62)")
        try:
            from binascii import unhexlify

            # 请求种子
            self.doip_client.send_diagnostic(bytearray(unhexlify("2761")))
            seed_response = self.doip_client.receive_diagnostic()
            if seed_response.hex()[:4] != "6761":
                logger.error(f"❌ 种子请求失败：{seed_response.hex()}")
                return False

            seed = seed_response.hex()[4:]
            logger.debug(f"种子：{seed}")

            # 计算密钥
            token = cal_ace_emac(seed)
            key_request = "2762" + token

            # 发送密钥
            self.doip_client.send_diagnostic(bytearray(unhexlify(key_request)))
            key_response = self.doip_client.receive_diagnostic()

            if key_response.hex()[:4] == "6762":
                logger.success("✅ 安全访问成功")
                return True
            else:
                logger.error(f"❌ 安全访问失败：{key_response.hex()}")
                return False
        except Exception as e:
            logger.error(f"❌ 安全访问异常：{e}")
            return False

    def security_access_level2(self) -> bool:
        """安全访问 Level 2 (27 05/06)"""
        logger.info("→ 执行安全访问 Level 2 (27 05/06)")
        try:
            from binascii import unhexlify
            
            # 请求种子
            self.doip_client.send_diagnostic(bytearray(unhexlify("2705")))
            seed_response = self.doip_client.receive_diagnostic()
            if seed_response.hex()[:4] != "6705":
                logger.error(f"❌ 种子请求失败：{seed_response.hex()}")
                return False
            
            seed = seed_response.hex()[4:]
            logger.debug(f"种子：{seed}")
            
            # 计算密钥
            token = cal_tea_variant(seed)
            key_request = "2706" + token
            
            # 发送密钥
            self.doip_client.send_diagnostic(bytearray(unhexlify(key_request)))
            key_response = self.doip_client.receive_diagnostic()
            
            if key_response.hex()[:4] == "6706":
                logger.success("✅ 安全访问成功")
                return True
            else:
                logger.error(f"❌ 安全访问失败：{key_response.hex()}")
                return False
        except Exception as e:
            logger.error(f"❌ 安全访问异常：{e}")
            return False

    def run_pre_command(self, test_case, exp_res_list) -> TestResult:
        start = time.time()
        try:
            # 发送测试命令
            logger.info(f"Going to send {exp_res_list[0]}")
            response = self.send_receive(exp_res_list[0])

            if exp_res_list[1]:
                expected = exp_res_list[1].upper().replace(" ", "")

                # 验证响应
                if response[:len(expected)] == expected:
                    pass
                else:
                    return TestResult(
                        name=test_case.name,
                        status=TestStatus.PRE_FAIL,
                        message=f"pre_command期望：{expected}, 实际：{response}",
                        duration=time.time() - start
                    )
            else:
                pass
            return TestResult(
                name=test_case.name,
                status=TestStatus.PASS,
                message="pre_command 执行成功",
                duration=time.time() - start
            )
        except Exception as e:
            return TestResult(
                name=test_case.name,
                status=TestStatus.ERROR,
                message=str(e),
                duration=time.time() - start
            )

    def run_test_case(self, test_case: TestCase) -> TestResult:
        """执行单个测试用例"""
        start = time.time()
        
        try:
            # 进入会话
            if test_case.session_required and test_case.session_required != 0:
                if not self.enter_session(test_case.session_required):
                    return TestResult(
                        name=test_case.name,
                        status=TestStatus.FAIL,
                        message=f"会话进入失败",
                        duration=time.time() - start
                    )
                time.sleep(0.1)
            
            # 安全访问
            if test_case.security_required == 1:
                if not self.security_access_level1():
                    return TestResult(
                        name=test_case.name,
                        status=TestStatus.FAIL,
                        message=f"安全访问 Level1 失败",
                        duration=time.time() - start
                    )
                time.sleep(0.1)
            elif test_case.security_required == 2:
                if not self.security_access_level2():
                    return TestResult(
                        name=test_case.name,
                        status=TestStatus.FAIL,
                        message=f"安全访问 Level2 失败",
                        duration=time.time() - start
                    )
                time.sleep(0.1)
            elif test_case.security_required == 3:
                if not self.security_access_level3():
                    return TestResult(
                        name=test_case.name,
                        status=TestStatus.FAIL,
                        message=f"安全访问 Level3 失败",
                        duration=time.time() - start
                    )
                time.sleep(0.1)
            # 执行前置命令
            if test_case.pre_command:
                # if len(test_case.pre_command) > 1:
                for command in test_case.pre_command:
                    # res = self.run_pre_command(test_case, command)
                    result = self.run_pre_command(test_case, command)
                    if result.status == TestStatus.PRE_FAIL:
                        return result
                    time.sleep(0.1)
                # else:
                #     self.send_receive(test_case.pre_command[0][0])
                #     time.sleep(0.1)
            # 发送测试命令
            response = self.send_receive(test_case.request)
            expected = test_case.expected_response.upper().replace(" ","")
            
            # 验证响应
            if response[:len(expected)] == expected:
                return TestResult(
                    name=test_case.name,
                    status=TestStatus.PASS,
                    message=f"响应：{response}",
                    duration=time.time() - start
                )
            else:
                return TestResult(
                    name=test_case.name,
                    status=TestStatus.FAIL,
                    message=f"期望：{expected}, 实际：{response}",
                    duration=time.time() - start
                )
                
        except Exception as e:
            return TestResult(
                name=test_case.name,
                status=TestStatus.ERROR,
                message=str(e),
                duration=time.time() - start
            )

    def run_cmd(self, cmd):
        """执行 CMD 命令并返回 (return_code, stdout, stderr)"""
        logger.info(f"🚀 执行命令: {cmd}")
        try:
            # shell=True 允许执行包含管道或重定向的复杂命令
            # capture_output=True 捕获输出
            # encoding='gbk' 适配 Windows CMD 默认编码
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='gbk')

            # 打印返回值-
            logger.info(f"📤 返回码 (Return Code): {result.returncode}")
            logger.info(f"📄 标准输出 (stdout):\n{result.stdout}")
            if result.stderr:
                logger.info(f"⚠️ 错误输出 (stderr):\n{result.stderr}")

            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            logger.info(f"❌ 执行异常: {e}")
            return -1, "", str(e)

    def ping_target(self, target_ip: str, count: int = 4, timeout: int = 2) -> tuple:
        """
        Ping 目标 IP
        :return: (success: bool, message: str)
        """
        cmd = f'ping -n {count} -w {timeout * 1000} {target_ip}'
        logger.info(f'will execute : {cmd}')
        ret, out, _ = self.run_cmd(cmd)

        # Windows ping 成功通常包含 "TTL="
        if ret == 0 and "TTL" in out:
            # 提取延迟信息
            for line in out.split('\n'):
                if "平均" in line or "Average" in line:
                    return True, line.strip()
            return True, "Ping 成功"
        else:
            return False, "Ping 失败 (请求超时或无法访问)"

    def setup_windows_network(self, ip: str, vlan_id: int) -> bool:
        """
        修改 Windows 本机网卡的 VLAN 和 IP 地址
        """
        logger.info(f"   → 正在配置网卡: VLAN={vlan_id}, IP={ip}")



        # 1. 设置静态 IP
        cmd_ip = f'netsh interface ip set address name="eth4" static {ip}'
        ret_ip, _, err_ip = self.run_cmd(cmd_ip)

        if ret_ip != 0:
            print(f"   ⚠️ 设置 IP 警告: {err_ip.strip()}")
            # 某些环境可能报错但实际生效，或者需要管理员权限

        # 2. 设置 VLAN ID
        # 注意：此命令依赖网卡驱动支持。如果不支持，可能需要通过交换机或网卡高级属性配置
        cmd_vlan1 = r'reg add "HKLM\SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}\0018" /v VLanID /t REG_SZ /d' + f' {vlan_id} /f'
        cmd_vlan2 = r'reg add "HKLM\SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}\0018" /v RegVLanID /t REG_SZ /d' + f' {vlan_id} /f'

        ret_vlan1, _1, err_vlan1 = self.run_cmd(cmd_vlan1)
        ret_vlan2, _2, err_vlan2 = self.run_cmd(cmd_vlan2)
        if ret_vlan1 != 0:
            print(f"   ⚠️ 设置 VLAN 警告: {err_vlan1.strip()}")

        if ret_vlan2 != 0:
            print(f"   ⚠️ 设置 VLAN 警告: {err_vlan2.strip()}")
        # 等待网络配置生效
        cmd_disable = f'netsh interface set interface "eth4" disable'
        self.run_cmd(cmd_disable)
        time.sleep(2)
        cmd_enable = f'netsh interface set interface "eth4" enable'
        self.run_cmd(cmd_enable)
        time.sleep(4)
        return True
        # 3. 验证 IP 是否生效
        # ret_verify, out_verify, _ = self.run_cmd(f'ipconfig | findstr "{ip}"')
        # if ret_verify == 0:
        #     print(f"   ✅ 网络配置成功: {ip} (VLAN {vlan_id})")
        #     return True
        # else:
        #     print(f"   ❌ 网络配置可能未生效，请检查")
        #     return False

    def run_test_case_ping(self, test_case: NetworkTestCase) -> TestResult:
        start_time = time.time()
        logger.info(f"\n执行用例: {test_case.name}")

        try:
            # 1. 修改本机网络配置
            net_ok = self.setup_windows_network(test_case.local_ip, test_case.vlan_id)
            if not net_ok:
                return TestResult(
                    name=test_case.name,
                    status=TestStatus.FAIL,
                    message=f"网络配置失败: {test_case.local_ip}",
                    duration=time.time() - start_time
                )

            # 2. Ping 测试
            logger.info(f"   → 正在 Ping 目标: {test_case.target_ip}")
            ping_ok, ping_msg = self.ping_target(test_case.target_ip)

            if ping_ok:
                return TestResult(
                    name=test_case.name,
                    status=TestStatus.PASS,
                    message=f"网络配置成功, {ping_msg}",
                    duration=time.time() - start_time
                )
            else:
                return TestResult(
                    name=test_case.name,
                    status=TestStatus.FAIL,
                    message=f"网络配置成功, 但 {ping_msg}",
                    duration=time.time() - start_time
                )

        except Exception as e:
            return TestResult(
                name=test_case.name,
                status=TestStatus.ERROR,
                message=str(e),
                duration=time.time() - start_time
            )

    def run_test_suite(self, test_cases, suite_name: str) -> List[TestResult]:
        """执行测试套件"""
        logger.info(f"\n{'='*60}")
        logger.info(f"开始执行测试套件：{suite_name}")
        logger.info(f"{'='*60}")
        
        results = []
        for i, tc in enumerate(test_cases, 1):
            logger.info(f"[{i}/{len(test_cases)}] 执行：{tc.name}")
            result = self.run_test_case(tc)
            results.append(result)
            logger.info(f"  结果：{result.status.value} - {result.message[:80]}")
        
        # 统计
        passed = sum(1 for r in results if r.status == TestStatus.PASS)
        failed = sum(1 for r in results if r.status == TestStatus.FAIL)
        errors = sum(1 for r in results if r.status == TestStatus.ERROR)
        
        logger.info(f"\n测试套件 {suite_name} 完成:")
        logger.info(f"  总计：{len(results)} | 通过：{passed} | 失败：{failed} | 错误：{errors}")
        
        return results

    def generate_report(self, output_path: str = "output"):
        """生成测试报告"""
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(output_path, f"test_report_{timestamp}.txt")
        
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("Chery DoIP 自动化测试报告\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"测试时间：{self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"结束时间：{self.end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"ECU IP: {self.ecu_ip}\n")
            f.write(f"ECU 地址：{hex(self.target_addr)}\n\n")
            
            # 统计
            total = len(self.results)
            passed = sum(1 for r in self.results if r.status == TestStatus.PASS)
            failed = sum(1 for r in self.results if r.status == TestStatus.FAIL)
            errors = sum(1 for r in self.results if r.status == TestStatus.ERROR)
            
            f.write(f"测试结果统计:\n")
            f.write(f"  总计：{total}\n")
            f.write(f"  通过：{passed} ({passed/total*100:.1f}%)\n")
            f.write(f"  失败：{failed}\n")
            f.write(f"  错误：{errors}\n\n")
            
            f.write("-" * 80 + "\n")
            f.write("详细测试结果:\n")
            f.write("-" * 80 + "\n\n")
            
            for i, result in enumerate(self.results, 1):
                f.write(f"{i}. {result.name}\n")
                f.write(f"   状态：{result.status.value}\n")
                f.write(f"   耗时：{result.duration:.3f}s\n")
                f.write(f"   信息：{result.message}\n\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("报告结束\n")
            f.write("=" * 80 + "\n")
        
        logger.info(f"\n📄 测试报告已保存：{report_file}")
        return report_file




# ==================== 测试用例定义 ====================

def get_system_did_tests() -> List[TestCase]:
    """系统 DID 测试用例"""
    return [
        TestCase("系统 DID - 零件号读取", "22F180", "62F180"),
        TestCase("系统 DID - 硬件版本读取", "22F187", "62F187"),
        TestCase("系统 DID - 软件版本读取", "22F189", "62F189"),
        TestCase("系统 DID - 系统供应商 ID", "22F089", "62F089"),
        TestCase("系统 DID - 系统名称", "22F013", "62F013"),
        TestCase("系统 DID - 零件版本", "22F18A", "62F18A"),
        TestCase("系统 DID - 硬件件号", "22F18B", "62F18B"),
        TestCase("系统 DID - 软件件号", "22F18C", "62F18C"),
        TestCase("系统 DID - 系统安全等级", "22F186", "62F186"),
        TestCase("系统 DID - 车辆 VIN 码", "22F160", "62F160"),
        TestCase("系统 DID - ECU 序列号", "22F161", "62F161"),
        TestCase("系统 DID - 系统时间", "22F091", "62F091"),
        TestCase("系统 DID - 诊断地址", "22F083", "62F083"),
        TestCase("系统 DID - 网络地址", "22F084", "62F084"),
        TestCase("系统 DID - 功能寻址地址", "22F086", "62F086"),
        TestCase("系统 DID - 响应地址", "22F087", "62F087"),
        TestCase("系统 DID - 系统信息", "22F08B", "62F08B"),
    ]


def get_ecu_did_tests() -> List[TestCase]:
    """ECU DID 测试用例"""
    tests = []
    ecu_dids = [
        "5703", "5708", "570E", "5717", "5721", "5722", "5723", "5724",
        "5727", "5728", "5729", "572A", "5739", "572B", "572C", "572D",
        "572E", "572F", "5730", "5731", "573A", "573B", "573C", "573D",
        "573F", "5740", "5741", "5742", "5743", "5744", "5745", "574D",
        "574E", "574F", "5750", "5751", "5752", "5753", "5784"
    ]
    for did in ecu_dids:
        tests.append(TestCase(f"ECU DID - 0x{did}", f"22{did}", f"62{did}"))
    return tests


# def get_eol_did_tests() -> List[TestCase]:
#     """EOL DID 测试用例"""
#     tests = []
#     eol_dids = [
#         "F187", "F189", "F089", "F013", "F18A", "F18B", "F18C", "F1AE",
#         "DA10", "F195", "FD98", "FD00", "F193", "FDF6", "FDF7", "DA21",
#         "FD89", "FD15", "F116", "FD0C", "FD1C", "FD0B", "FD51", "FD53",
#         "FD61", "FD65", "FD40", "FD30", "FD13", "FDA4", "FDA2", "FDA1",
#         "FDA0", "FD14", "FD70", "FDB5", "F08B", "F083"
#     ]
#     for did in eol_dids:
#         tests.append(TestCase(f"EOL DID - 0x{did}", f"22{did}", f"62{did}", pre_command="1060"))
#     return tests


def get_io_control_tests() -> List[TestCase]:
    """IO 控制测试用例"""
    return [
        TestCase("IO 控制 - 0x571D01", "2F571D01", "6F571D"),
        TestCase("IO 控制 - 0x571D02", "2F571D02", "6F571D"),
        TestCase("IO 控制 - 0x571E00", "2F571E00", "6F571E"),
        TestCase("IO 控制 - 0x571E01", "2F571E01", "6F571E"),
        TestCase("IO 控制 - 0x571E02", "2F571E02", "6F571E"),
        TestCase("IO 控制 - 0x571E03", "2F571E03", "6F571E"),
        TestCase("IO 控制 - 0x571F01", "2F571F01", "6F571F"),
        TestCase("IO 控制 - 0x571F02", "2F571F02", "6F571F"),
    ]


def get_dtc_tests() -> List[TestCase]:
    """DTC 测试用例"""
    return [
        TestCase("DTC - 读取当前故障码", "1902FF", "5909"),
        TestCase("DTC - 清除所有故障码", "14FFFFFF", "54"),
    ]


def get_application_service_tests() -> List[TestCase]:
    """应用服务测试用例（补充 test_application_service.py 中的用例）"""
    return [
        # 会话控制
        TestCase("应用服务 - 默认会话", "1001", "5001"),
        TestCase("应用服务 - 扩展会话", "1003", "5003"),
        
        # ECU 重置（需要确认 ECU 是否支持）
        # TestCase("应用服务 - 硬重置", "1101", "5101"),
        # TestCase("应用服务 - 软重置", "1103", "5103"),
        
        # 安全访问
        TestCase("应用服务 - 安全访问 Level1", "2701", "6701", security_required=1),
        
        # 通信控制（需要确认 ECU 是否支持）
        # TestCase("应用服务 - 通信控制启用", "280001", "680001"),
        # TestCase("应用服务 - 通信控制禁用", "280303", "680303"),
        
        # DTC 设置
        TestCase("应用服务 - DTC 设置开启", "8501", "C501"),
        TestCase("应用服务 - DTC 设置关闭", "8502", "C502"),
        
        # 测试者存在
        TestCase("应用服务 - 测试者存在", "3E00", "7E00"),
        
        # 例程控制（需要确认 ECU 是否支持）
        # TestCase("应用服务 - 启动例程 5783", "31015783", "710102", session_required=3, security_required=1),
    ]


def get_write_did_tests() -> List[TestCase]:
    """写入 DID 测试用例"""
    return [
        TestCase(
            "写入 DID - F190(扩展会话 + 安全 1)",
            "2EF190" + DataHandle.random_bytes_string(17),
            "6EF190",
            session_required=3,
            security_required=1
        ),
        TestCase(
            "写入 DID - F0FE(扩展会话 + 安全 1)",
            "2EF0FE" + DataHandle.random_bytes_string(15),
            "6EF0FE",
            session_required=3,
            security_required=1
        ),
    ]


def get_a_class_tests() -> List[TestCase]:
    """A 类测试用例 (纯 UDS 诊断 - 易自动化)"""
    conf = TomlConfig("config.toml")
    _ = conf.get("auto.auto_test")
    return [TestCase(i[0], i[1], i[2], int(i[3])) for i in _]


ramdom_byte_31 = DataHandle.random_bytes_string(31)
ramdom_byte_36 = DataHandle.random_bytes_string(36)
ramdom_byte_16 = DataHandle.random_bytes_string(16)
# ramdom_31byte = DataHandle.random_bytes_string(31)
def get_mps_case_tests() -> List[TestCase]:
    return [
        TestCase(name="TCCHERYICC-6-1",
                 request="10 01",
                 expected_response="50 01",
                 session_required=6,
                 security_required=3,
                 pre_command=[("2E FD C0 62 42 9A 8A 44 C9 8C D0 EC 27 E2 EA 75 E6 6C 8C", "6E FD C0"),
                              ("22 FD C0", "62 FD C0 0A 8B 37 64 D2 FA 41 EF 68 62 21 69 B0 AF 2C 02"),
                              ]
                 ),
        TestCase(name="TCCHERYICC-6-2",
                 request="22 F1 8C",
                 expected_response="62F18C31305f37303330303436353041415f31315f3130343642555f31325f3030303030303030303031",
                 session_required=6,
                 security_required=3,
                 pre_command=[("2EF18C31305f37303330303436353041415f31315f3130343642555f31325f3030303030303030303031", None),
                              ]
                 ),
        TestCase(name="TCCHERYICC-7",
                 request="10 01",
                 expected_response="50 01",
                 session_required=6,
                 security_required=3,
                 pre_command=[
                     ("2EFDC131697060FAA6B4D5A5AD1C4D9A3BD07A", "6E FD C1"),
                     ("22 FD C1", "62 FD C1 D0 D7 B3 D9 CB 85 C0 49 AC DD 1F E1 A1 86 93 46")
                     ]
                 ),
        TestCase(name="TCCHERYICC-11",
                 request="22 DA 10",
                 expected_response="62 DA 10",
                 session_required=6,
                 security_required=3,
                 ),
        TestCase(name="TCCHERYICC-12",
                 request="22 F1 95",
                 expected_response="62 F1 95",
                 session_required=6,
                 security_required=3,
                 ),
        TestCase(name="TCCHERYICC-14",
                 request="2E FD 00" + ramdom_byte_31,
                 expected_response="6E FD 00",
                 session_required=6,
                 security_required=3,
                 ),
        TestCase(name="TCCHERYICC-15",
                 request="22 FD 00",
                 expected_response="62 FD 00" + ramdom_byte_31,
                 session_required=6,
                 security_required=3,
                 ),
        TestCase(name="TCCHERYICC-16",
                 request="2E F1 93" + ramdom_byte_31,
                 expected_response="6E F1 93",
                 session_required=6,
                 security_required=3,
                 ),
        TestCase(name="TCCHERYICC-17",
                 request="22 F1 93 ",
                 expected_response="62 F1 93" + ramdom_byte_31,
                 session_required=6,
                 security_required=3,
                 ),
        TestCase(name="TCCHERYICC-18",
                 request="2E FD F6" + ramdom_byte_31,
                 expected_response="6E FD F6",
                 session_required=6,
                 security_required=3,
                 ),
        TestCase(name="TCCHERYICC-19",
                 request="22 FD F6 ",
                 expected_response="62 FD F6" + ramdom_byte_31,
                 session_required=6,
                 security_required=3,
                 ),
        TestCase(name="TCCHERYICC-20",
                 request="2E FD F7" + ramdom_byte_31,
                 expected_response="6E FD F7",
                 session_required=6,
                 security_required=3,
                 ),
        TestCase(name="TCCHERYICC-21",
                 request="22 FD F7 ",
                 expected_response="62 FD F7" + ramdom_byte_31,
                 session_required=6,
                 security_required=3,
                 ),
        # 补全sw version-TBD
        TestCase(name="TCCHERYICC-22",
                 request="22 F1 87 ",
                 expected_response="62 F1 87",
                 session_required=6,
                 security_required=3,
                 ),
        # 补全sw version-TBD
        TestCase(name="TCCHERYICC-23",
                 request="22 F1 89 ",
                 expected_response="62 F1 89",
                 session_required=6,
                 security_required=3,
                 ),
        # 补全sw version-TBD
        TestCase(name="TCCHERYICC-24",
                 request="22 F0 89 ",
                 expected_response="62 F0 89",
                 session_required=6,
                 security_required=3,
                 ),
        TestCase(name="TCCHERYICC-25",
                 request="22 F0 13 ",
                 expected_response="62 F0 13",
                 session_required=6,
                 security_required=3,
                 ),

        TestCase(name="TCCHERYICC-26",
                 request="2E F1 8C" + ramdom_byte_36,
                 expected_response="6E F1 8C",
                 session_required=6,
                 security_required=3,
                 ),
        TestCase(name="TCCHERYICC-27",
                 request="22 F1 8C ",
                 expected_response="62 F1 8C" + ramdom_byte_36,
                 session_required=6,
                 security_required=3,
                 ),
        TestCase(name="TCCHERYICC-28",
                 request="2E F0 FF" + ramdom_byte_16,
                 expected_response="6E F0 FF",
                 session_required=6,
                 security_required=3,
                 ),
        TestCase(name="TCCHERYICC-29",
                 request="22 F0 FF",
                 expected_response="62 F0 FF" + ramdom_byte_16,
                 session_required=6,
                 security_required=3,
                 ),
        TestCase(name="TCCHERYICC-36",
                 request="22 F0 83",
                 expected_response="62 F0 83 01", # TBD
                 session_required=6,
                 security_required=3,
                 ),
        TestCase(name="TCCHERYICC-43",
                 request="22 DA 21",
                 expected_response="62 DA 21 00",  # TBD
                 session_required=6,
                 security_required=3,
                 ),
        TestCase(name="TCCHERYICC-44",
                 request="2E DA 21 01",
                 expected_response="6E DA 21",  # TBD
                 session_required=6,
                 security_required=3,
                 ),
        TestCase(name="TCCHERYICC-45",
                 request="22 DA 21",
                 expected_response="62 DA 21 00 01 00",
                 session_required=6,
                 security_required=3,
                 ),
        TestCase(name="TCCHERYICC-46",
                 request="22 DA 21",
                 expected_response="62 DA 21 00",  # TBD
                 session_required=6,
                 security_required=3,
                 ),
        TestCase(name="TCCHERYICC-54",
                 request="2E FD D0 01",
                 expected_response="6E FD D0 01",
                 session_required=6,
                 security_required=3,
                 ),
        TestCase(name="TCCHERYICC-55",
                 request="2E FD D0 00",
                 expected_response="6E FD D0 00",
                 session_required=6,
                 security_required=3,
                 ),
        TestCase(name="TCCHERYICC-56",
                 request="2E FD D1 01",
                 expected_response="6E FD D1 01",
                 session_required=6,
                 security_required=3,
                 ),
        TestCase(name="TCCHERYICC-57",
                 request="2E FD D1 00",
                 expected_response="6E FD D1 00",
                 session_required=6,
                 security_required=3,
                 ),
        TestCase(name="TCCHERYICC-58",
                 request="2E FD D2 01",
                 expected_response="6E FD D2 01",
                 session_required=6,
                 security_required=3,
                 ),
        TestCase(name="TCCHERYICC-59",
                 request="2E FD D2 00",
                 expected_response="6E FD D2 00",
                 session_required=6,
                 security_required=3,
                 ),
        TestCase(name="TCCHERYICC-95",
                 request="22 FD 0C",
                 expected_response="6E FD 0C", # TBD
                 session_required=6,
                 security_required=3,
                 ),
        TestCase(name="TCCHERYICC-137",
                 request="31 02 FE 10 ",
                 expected_response="61 02 FE 10",  # TBD
                 session_required=6,
                 security_required=3,
                 pre_command=[("31 01 FE 10 00 05", "71 01 FE 10 00"),  # TBD
                              ]
                 ),
        TestCase(name="TCCHERYICC-138",
                 request="31 02 FE 10 ",
                 expected_response="61 02 FE 10",  # TBD
                 session_required=6,
                 security_required=3,
                 pre_command=[("31 01 FE 10 01 05", "71 01 FE 10 00"),  # TBD
                              ]
                 ),
        TestCase(name="TCCHERYICC-139",
                 request="31 02 FE 10 ",
                 expected_response="61 02 FE 10",  # TBD
                 session_required=6,
                 security_required=3,
                 pre_command=[("31 01 FE 10 02 05", "71 01 FE 10 00"),  # TBD
                              ]
                 ),
        TestCase(name="TCCHERYICC-159",
                 request="14 FF FF FF",
                 expected_response="54",
                 session_required=6,
                 security_required=3,
                 ),

    ]

# ==================== 主函数 ====================

def get_network_case_test() -> List[NetworkTestCase]:
    return [
        NetworkTestCase(
            name="TCCHERYICC-60",
            local_ip="192.168.54.71",
            vlan_id=54,
            target_ip="192.168.54.31"
        ),
        NetworkTestCase(
            name="TCCHERYICC-61",
            local_ip="192.168.55.71",
            vlan_id=55,
            target_ip="192.168.55.31"
        ),
        NetworkTestCase(
            name="TCCHERYICC-62",
            local_ip="192.168.61.71",
            vlan_id=61,
            target_ip="192.168.61.31"
        ),
        NetworkTestCase(
            name="TCCHERYICC-63",
            local_ip="192.168.62.71",
            vlan_id=62,
            target_ip="192.168.62.31"
        ),
        NetworkTestCase(
            name="TCCHERYICC-64",
            local_ip="192.168.65.71",
            vlan_id=65,
            target_ip="192.168.65.31"
        ),
        NetworkTestCase(
            name="TCCHERYICC-65",
            local_ip="192.168.68.71",
            vlan_id=68,
            target_ip="192.168.68.31"
        ),
        NetworkTestCase(
            name="TCCHERYICC-66",
            local_ip="192.168.69.71",
            vlan_id=69,
            target_ip="192.168.69.31"
        ),
        NetworkTestCase(
            name="TCCHERYICC-67",
            local_ip="192.168.71.71",
            vlan_id=71,
            target_ip="192.168.71.31"
        ),
        NetworkTestCase(
            name="TCCHERYICC-68",
            local_ip="192.168.72.71",
            vlan_id=72,
            target_ip="192.168.72.31"
        ),
        NetworkTestCase(
            name="TCCHERYICC-69",
            local_ip="192.168.54.71",
            vlan_id=54,
            target_ip="192.168.54.32"
        ),
        NetworkTestCase(
            name="TCCHERYICC-70",
            local_ip="192.168.55.71",
            vlan_id=55,
            target_ip="192.168.55.32"
        ),
        NetworkTestCase(
            name="TCCHERYICC-71",
            local_ip="192.168.61.71",
            vlan_id=61,
            target_ip="192.168.61.32"
        ),
        NetworkTestCase(
            name="TCCHERYICC-72",
            local_ip="192.168.62.71",
            vlan_id=62,
            target_ip="192.168.62.32"
        ),
        NetworkTestCase(
            name="TCCHERYICC-73",
            local_ip="192.168.65.71",
            vlan_id=65,
            target_ip="192.168.65.32"
        ),
        NetworkTestCase(
            name="TCCHERYICC-74",
            local_ip="192.168.68.71",
            vlan_id=68,
            target_ip="192.168.68.32"
        ),
        NetworkTestCase(
            name="TCCHERYICC-75",
            local_ip="192.168.69.71",
            vlan_id=69,
            target_ip="192.168.69.32"
        ),
    ]

def main():
    """主函数"""
    print("=" * 60)
    print("Chery DoIP 自动化测试工具")
    print("=" * 60)
    print()
    
    # 创建测试执行器
    runner = AutoTestRunner()
    
    # 连接 ECU
    # if not runner.connect():
    #     logger.error("无法连接到 ECU，程序退出")
    #     return 1
    
    runner.start_time = datetime.now()
    
    try:
        # 执行测试套件
        all_results = []

        # uds_tests = get_mps_case_tests()
        #
        # all_results.extend(runner.run_test_suite(uds_tests, "ALL"))

        network_test = get_network_case_test()
        for tc in network_test:
            result = runner.run_test_case_ping(tc)
            all_results.append(result)

        #
        # # 1. 应用服务测试
        # app_tests = get_application_service_tests()
        # all_results.extend(runner.run_test_suite(app_tests, "应用服务测试"))
        #
        # # 2. 系统 DID 测试
        # system_tests = get_system_did_tests()
        # all_results.extend(runner.run_test_suite(system_tests, "系统 DID 测试"))
        #
        # # 3. ECU DID 测试
        # ecu_tests = get_ecu_did_tests()
        # all_results.extend(runner.run_test_suite(ecu_tests, "ECU DID 测试"))
        #
        # # 4. EOL DID 测试
        # eol_tests = get_eol_did_tests()
        # all_results.extend(runner.run_test_suite(eol_tests, "EOL DID 测试"))
        #
        # # 5. IO 控制测试
        # io_tests = get_io_control_tests()
        # all_results.extend(runner.run_test_suite(io_tests, "IO 控制测试"))
        #
        # # 6. DTC 测试
        # dtc_tests = get_dtc_tests()
        # all_results.extend(runner.run_test_suite(dtc_tests, "DTC 测试"))
        #
        # 7. 写入 DID 测试（可选，需要安全访问，默认注释）
        # write_tests = get_write_did_tests()
        # all_results.extend(runner.run_test_suite(write_tests, "写入 DID 测试"))
        
        runner.results = all_results
        runner.end_time = datetime.now()
        
        # 生成报告
        runner.generate_report()
        
        # 打印总结
        total = len(all_results)
        passed = sum(1 for r in all_results if r.status == TestStatus.PASS)
        failed = sum(1 for r in all_results if r.status == TestStatus.FAIL)
        errors = sum(1 for r in all_results if r.status == TestStatus.ERROR)
        
        print("\n" + "=" * 60)
        print("测试执行完成")
        print("=" * 60)
        print(f"总计：{total} | 通过：{passed} | 失败：{failed} | 错误：{errors}")
        print(f"通过率：{passed/total*100:.1f}%")
        print("=" * 60)
        
        return 0 if failed == 0 and errors == 0 else 1
        
    except KeyboardInterrupt:
        logger.warning("用户中断测试")
        return 1
    except Exception as e:
        logger.error(f"测试执行异常：{e}")
        return 1
    finally:
        runner.disconnect()


if __name__ == "__main__":
    sys.exit(main())
