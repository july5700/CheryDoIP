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
    session_required: int = 0  # 0=不需要，1=默认会话，3=扩展会话, 6=1060，工厂模式
    security_required: int = 0  # 0=不需要，1=Level1(2701/02), 2=Level2(2705/06)
    pre_command: str = ""  # 前置命令（如 1060）


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
        br = bytearray(unhexlify(msg))
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

    def run_test_case(self, test_case: TestCase) -> TestResult:
        """执行单个测试用例"""
        start = time.time()
        
        try:
            # 执行前置命令
            if test_case.pre_command:
                self.send_receive(test_case.pre_command)
                time.sleep(0.1)
            
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
            
            # 发送测试命令
            response = self.send_receive(test_case.request)
            expected = test_case.expected_response.upper()
            
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

    def run_test_suite(self, test_cases: List[TestCase], suite_name: str) -> List[TestResult]:
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


def get_eol_did_tests() -> List[TestCase]:
    """EOL DID 测试用例"""
    tests = []
    eol_dids = [
        "F187", "F189", "F089", "F013", "F18A", "F18B", "F18C", "F1AE",
        "DA10", "F195", "FD98", "FD00", "F193", "FDF6", "FDF7", "DA21",
        "FD89", "FD15", "F116", "FD0C", "FD1C", "FD0B", "FD51", "FD53",
        "FD61", "FD65", "FD40", "FD30", "FD13", "FDA4", "FDA2", "FDA1",
        "FDA0", "FD14", "FD70", "FDB5", "F08B", "F083"
    ]
    for did in eol_dids:
        tests.append(TestCase(f"EOL DID - 0x{did}", f"22{did}", f"62{did}", pre_command="1060"))
    return tests


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


#
# def get_b_class_tests():
#     conf = TomlConfig("config.toml")
#     return conf.get("current.auto_test")


def get_a_class_tests() -> List[TestCase]:
    """A 类测试用例 (纯 UDS 诊断 - 易自动化)"""
    conf = TomlConfig("config.toml")
    _ = conf.get("auto.auto_test")
    return [TestCase(i[0], i[1], i[2], int(i[3]), int(i[3])) for i in _]


    # return [
    #     TestCase("TCCHERYICC-192", "1001", "5001", 0),
    #     TestCase("TCCHERYICC-196", "1002", "7F1012", 0),
    #     TestCase("TCCHERYICC-197", "1003", "5003", 0),
    #
    #     TestCase("TCCHERYICC-223-1", "1102", "7F1112", 1),
    #     TestCase("TCCHERYICC-223-2", "1102", "7F1112", 3),
    #     TestCase("TCCHERYICC-224-1", "1182", "7F1112", 1),
    #     TestCase("TCCHERYICC-224-2", "1182", "7F1112", 3),
    #     TestCase("TCCHERYICC-227-1", "1101", "7F1113", 1),
    #     TestCase("TCCHERYICC-227-2", "1101", "7F1113", 3),
    #     TestCase("TCCHERYICC-228-1", "11", "7F1113", 1),
    #     TestCase("TCCHERYICC-228-2", "11", "7F1113", 3),
    #     TestCase("TCCHERYICC-229-1", "110201", "7F1112", 1),
    #     TestCase("TCCHERYICC-229-2", "110201", "7F1112", 3),
    #     TestCase("TCCHERYICC-230", "1101", "7F1122", 0),
    #     TestCase("TCCHERYICC-231", "110101", "7F1113", 0),
    #     TestCase("TCCHERYICC-232", "1102", "7F1112", 0),
    #     TestCase("TCCHERYICC-233-1", "14FFFFFF", "54", 1),
    #     TestCase("TCCHERYICC-233-2", "14FFFFFF", "54", 3),
    #     TestCase("TCCHERYICC-234-1", "14C14287", "7F1431", 1),
    #     TestCase("TCCHERYICC-234-2", "14C14287", "7F1431", 1),
    #     TestCase("TCCHERYICC-235-1", "14000000", "7F1431", 1),
    #     TestCase("TCCHERYICC-235-32", "14000000", "7F1431", 3),
    #     TestCase("TCCHERYICC-236-1", "14", "7F1413", 1),
    #     TestCase("TCCHERYICC-236-2", "14FF", "7F1413", 1),
    #     TestCase("TCCHERYICC-236-3", "14FFFF", "7F1413", 1),
    #     TestCase("TCCHERYICC-236-4", "14FFFFFF01", "7F1413", 1),
    #     TestCase("TCCHERYICC-236-5", "14", "7F1413", 3),
    #     TestCase("TCCHERYICC-236-6", "14FF", "7F1413", 3),
    #     TestCase("TCCHERYICC-236-7", "14FFFF", "7F1413", 3),
    #     TestCase("TCCHERYICC-236-8", "14FFFFFF01", "7F1413", 3),
    #     TestCase("TCCHERYICC-237", "14FFFFFF", "7F1422", 0),
    #     TestCase("TCCHERYICC-238", "14FFFFFF01", "7F1413", 0),
    #     TestCase("TCCHERYICC-239", "14FFFFFF01", "7F1413", 0),
    #
    #     TestCase("TCCHERYICC-240", "14000000", "7F1431", 0),
    #     TestCase("TCCHERYICC-242", "190209", "590209", 3),
    #     TestCase("TCCHERYICC-257-1", "19020905", "7F1913", 1),
    #     TestCase("TCCHERYICC-257-2", "1902", "7F1913", 3),
    #     TestCase("TCCHERYICC-258-1", "190105", "7F1912", 1),
    #     TestCase("TCCHERYICC-258-2", "190105", "7F1912", 3),
    #
    #     TestCase("TCCHERYICC-259-1", "190A0905", "7F1913", 1),
    #     TestCase("TCCHERYICC-259-2", "190A0905", "7F1913", 3),
    #     TestCase("TCCHERYICC-261-1", "1901FFFF", "7F1912", 1),
    #     TestCase("TCCHERYICC-261-2", "1903050000", "7F1912", 1),
    #     TestCase("TCCHERYICC-261-3", "1901FFFF", "7F1912", 3),
    #     TestCase("TCCHERYICC-261-4", "1903050000", "7F1912", 3),
    #     TestCase("TCCHERYICC-262-1", "1902FF06", "7F1913", 1),
    #     TestCase("TCCHERYICC-262-2", "1902FF06", "7F1913", 3),
    #     TestCase("TCCHERYICC-263-1", "190108", "7F1912", 1),
    #     TestCase("TCCHERYICC-263-3", "190108", "7F1912", 3),
    #     TestCase("TCCHERYICC-264-1", "22F187", "62F187", 1),
    #     TestCase("TCCHERYICC-264-2", "22F187", "62F187", 3),
    #     TestCase("TCCHERYICC-265-1", "22F189", "62F189", 1),
    #     TestCase("TCCHERYICC-265-2", "22F189", "62F189", 3),
    #     TestCase("TCCHERYICC-266-1", "22F089", "62F089", 1),
    #     TestCase("TCCHERYICC-266-2", "22F089", "62F089", 3),
    #     TestCase("TCCHERYICC-267-1", "22F013", "62F013", 1),
    #     TestCase("TCCHERYICC-267-2", "22F013", "62F013", 3),
    #     TestCase("TCCHERYICC-268-1", "22F18A", "62F18A", 1),
    #     TestCase("TCCHERYICC-268-2", "22F18A", "62F18A", 3),
    #     TestCase("TCCHERYICC-269-1", "22F18B", "62F18B", 1),
    #     TestCase("TCCHERYICC-269-2", "22F18B", "62F18B", 3),
    #     TestCase("TCCHERYICC-270-1", "22F18C", "62F18C", 1),
    #     TestCase("TCCHERYICC-270-2", "22F18C", "62F18C", 3),
    #     TestCase("TCCHERYICC-271-1", "22F190", "62F190", 1),
    #     TestCase("TCCHERYICC-271-2", "22F190", "62F190", 3),
    #     TestCase("TCCHERYICC-272-1", "22F186", "62F186", 1),
    #     TestCase("TCCHERYICC-272-2", "22F186", "62F186", 3),
    #     TestCase("TCCHERYICC-273-1", "22F0FE", "62F0FE", 1),
    #     TestCase("TCCHERYICC-273-2", "22F0FE", "62F0FE", 3),
    #     TestCase("TCCHERYICC-274-1", "22F091", "62F091", 1),
    #     TestCase("TCCHERYICC-274-2", "22F091", "62F091", 3),
    #     TestCase("TCCHERYICC-275-1-TBD", "22F083", "62F08302", 1),
    #     TestCase("TCCHERYICC-275-2-TBD", "22F083", "62F08302", 3),
    #     TestCase("TCCHERYICC-276-1", "22F084", "62F08400", 1),
    #     TestCase("TCCHERYICC-276-2", "22F084", "62F08400", 3),
    #
    #     TestCase("TCCHERYICC-277-1", "22F085", "7F2222", 1),
    #     TestCase("TCCHERYICC-277-2", "22F085", "7F2222", 3),
    #     TestCase("TCCHERYICC-278-1", "22F086", "7F2222", 1),
    #     TestCase("TCCHERYICC-278-2", "22F086", "7F2222", 3),
    #     TestCase("TCCHERYICC-279-1", "22F087", "7F2222", 1),
    #     TestCase("TCCHERYICC-279-2", "22F087", "7F2222", 3),
    #     TestCase("TCCHERYICC-280-1-TBD", "22F092", "62F092", 1),
    #     TestCase("TCCHERYICC-280-2-TBD", "22F092", "62F092", 3),
    #
    #     TestCase("TCCHERYICC-281-1", "22F083", "62F08301", 1),
    #     TestCase("TCCHERYICC-281-2", "22F083", "62F08301", 3),
    #     TestCase("TCCHERYICC-282-1", "22F084", "62F08401", 1),
    #     TestCase("TCCHERYICC-282-2", "22F084", "62F08401", 3),
    #     TestCase("TCCHERYICC-283-1", "22F085", "62F085", 1),
    #     TestCase("TCCHERYICC-283-2", "22F085", "62F085", 3),
    #     TestCase("TCCHERYICC-284-1", "22F086", "62F086", 1),
    #     TestCase("TCCHERYICC-284-2", "22F086", "62F086", 3),
    #     TestCase("TCCHERYICC-285-1", "22F087", "62F087", 1),
    #     TestCase("TCCHERYICC-285-2", "22F087", "62F087", 3),
    #     TestCase("TCCHERYICC-286-1", "22F092", "62F092", 1),
    #     TestCase("TCCHERYICC-286-2", "22F092", "62F092", 3),
    #
    #
    #     TestCase("TCCHERYICC-287-1", "22F083", "62F08301", 1),
    #     TestCase("TCCHERYICC-287-2", "22F083", "62F08301", 3),
    #     TestCase("TCCHERYICC-288-1", "22F084", "62F08401", 1),
    #     TestCase("TCCHERYICC-288-2", "22F084", "62F08401", 3),
    #     TestCase("TCCHERYICC-289-1", "22F085", "62F085", 1),
    #     TestCase("TCCHERYICC-289-2", "22F085", "62F085", 3),
    #     TestCase("TCCHERYICC-290-1", "22F086", "62F086", 1),
    #     TestCase("TCCHERYICC-290-2", "22F086", "62F086", 3),
    #     TestCase("TCCHERYICC-291-1", "22F087", "62F087", 1),
    #     TestCase("TCCHERYICC-291-2", "22F087", "62F087", 3),
    #     TestCase("TCCHERYICC-292-1", "22F092", "62F092", 1),
    #     TestCase("TCCHERYICC-292-2", "22F092", "62F092", 3),
    #     TestCase("TCCHERYICC-293-1", "22F083", "62F083", 1),
    #     TestCase("TCCHERYICC-293-2", "22F083", "62F083", 3),
    #     TestCase("TCCHERYICC-294-1", "22F084", "62F084", 1),
    #     TestCase("TCCHERYICC-294-2", "22F084", "62F084", 3),
    #     TestCase("TCCHERYICC-295-1", "22F085", "62F085", 1),
    #     TestCase("TCCHERYICC-295-2", "22F085", "62F085", 3),
    #     TestCase("TCCHERYICC-296-1", "22F086", "62F086", 1),
    #     TestCase("TCCHERYICC-296-2", "22F086", "62F086", 3),
    #
    #
    #     TestCase("TCCHERYICC-297-1", "22F087", "62F087", 1),
    #     TestCase("TCCHERYICC-297-2", "22F087", "62F087", 3),
    #     TestCase("TCCHERYICC-298-1", "22F087", "62F092", 1),
    #     TestCase("TCCHERYICC-298-2", "22F087", "62F092", 3),
    #
    #
    #     TestCase("TCCHERYICC-300-1", "225708", "625708", 1),
    #     TestCase("TCCHERYICC-300-2", "225708", "625708", 3),
    #     TestCase("TCCHERYICC-301-1", "22570E", "62570E", 1),
    #     TestCase("TCCHERYICC-301-2", "22570E", "62570E", 3),
    #     TestCase("TCCHERYICC-302-1", "225717", "625717", 1),
    #     TestCase("TCCHERYICC-302-2", "225717", "625717", 3),
    #     TestCase("TCCHERYICC-303-1", "225721", "625721", 1),
    #     TestCase("TCCHERYICC-303-2", "225721", "625721", 3),
    #     TestCase("TCCHERYICC-304-1", "225722", "625722", 1),
    #     TestCase("TCCHERYICC-304-2", "225722", "625722", 3),
    #     TestCase("TCCHERYICC-305-1", "225723", "625723", 1),
    #     TestCase("TCCHERYICC-305-2", "225723", "625723", 3),
    #     TestCase("TCCHERYICC-306-1", "225724", "625724", 1),
    #     TestCase("TCCHERYICC-306-2", "225724", "625724", 3),
    #     TestCase("TCCHERYICC-307-1", "225727", "625727", 1),
    #     TestCase("TCCHERYICC-307-2", "225727", "625727", 3),
    #     TestCase("TCCHERYICC-308-1", "225728", "625728", 1),
    #     TestCase("TCCHERYICC-308-2", "225728", "625728", 3),
    #     TestCase("TCCHERYICC-309-1", "225729", "625729", 1),
    #     TestCase("TCCHERYICC-309-2", "225729", "625729", 3),
    #     TestCase("TCCHERYICC-310-1", "22572A", "62572A", 1),
    #     TestCase("TCCHERYICC-310-2", "22572A", "62572A", 3),
    #     TestCase("TCCHERYICC-312-1", "22572B", "62572B", 1),
    #     TestCase("TCCHERYICC-312-2", "22572B", "62572B", 3),
    #     TestCase("TCCHERYICC-313-1", "22572C", "62572C", 1),
    #     TestCase("TCCHERYICC-313-2", "22572C", "62572C", 3),
    #     TestCase("TCCHERYICC-314-1", "22572D", "62572D", 1),
    #     TestCase("TCCHERYICC-314-2", "22572D", "62572D", 3),
    #     TestCase("TCCHERYICC-315-1", "22572E", "62572E", 1),
    #     TestCase("TCCHERYICC-315-2", "22572E", "62572E", 3),
    #     TestCase("TCCHERYICC-316-1", "22572F", "62572F", 1),
    #     TestCase("TCCHERYICC-316-2", "22572F", "62572F", 3),
    #     TestCase("TCCHERYICC-317-1", "225730", "625730", 1),
    #     TestCase("TCCHERYICC-317-2", "225730", "625730", 3),
    #     TestCase("TCCHERYICC-318-1", "225731", "625731", 1),
    #     TestCase("TCCHERYICC-318-2", "225731", "625731", 3),
    #     TestCase("TCCHERYICC-319-1", "22573A", "62573A", 1),
    #     TestCase("TCCHERYICC-319-2", "22573A", "62573A", 3),
    #     TestCase("TCCHERYICC-320-1", "22573B", "62573B", 1),
    #     TestCase("TCCHERYICC-320-2", "22573B", "62573B", 3),
    #     TestCase("TCCHERYICC-321-1", "22573C", "62573C", 1),
    #     TestCase("TCCHERYICC-321-2", "22573C", "62573C", 3),
    #     TestCase("TCCHERYICC-322-1", "22573D", "62573D", 1),
    #     TestCase("TCCHERYICC-322-2", "22573D", "62573D", 3),
    #     TestCase("TCCHERYICC-323-1", "22573F", "62573F", 1),
    #     TestCase("TCCHERYICC-323-2", "22573F", "62573F", 3),
    #     TestCase("TCCHERYICC-324-1", "225740", "625740", 1),
    #     TestCase("TCCHERYICC-324-2", "225740", "625740", 3),
    #     TestCase("TCCHERYICC-325-1", "225741", "625741", 1),
    #     TestCase("TCCHERYICC-325-2", "225741", "625741", 3),
    #     TestCase("TCCHERYICC-326-1", "225742", "625742", 1),
    #     TestCase("TCCHERYICC-326-2", "225742", "625742", 3),
    #     TestCase("TCCHERYICC-327-1", "225743", "625743", 1),
    #     TestCase("TCCHERYICC-327-2", "225743", "625743", 3),
    #     TestCase("TCCHERYICC-328-1", "225744", "625744", 1),
    #     TestCase("TCCHERYICC-328-2", "225744", "625744", 3),
    #     TestCase("TCCHERYICC-329-1", "225745", "625745", 1),
    #     TestCase("TCCHERYICC-329-2", "225745", "625745", 3),
    #     TestCase("TCCHERYICC-330-1", "22574D", "62574D", 1),
    #     TestCase("TCCHERYICC-330-2", "22574D", "62574D", 3),
    #     TestCase("TCCHERYICC-331-1", "22574E", "62574E", 1),
    #     TestCase("TCCHERYICC-331-2", "22574E", "62574E", 3),
    #     TestCase("TCCHERYICC-332-1", "22574F", "62574F", 1),
    #     TestCase("TCCHERYICC-332-2", "22574F", "62574F", 3),
    #     TestCase("TCCHERYICC-333-1", "225750", "625750", 1),
    #     TestCase("TCCHERYICC-333-2", "225750", "625750", 3),
    #     TestCase("TCCHERYICC-334-1", "225751", "625751", 1),
    #     TestCase("TCCHERYICC-334-2", "225751", "625751", 3),
    #     TestCase("TCCHERYICC-335-1", "225752", "625752", 1),
    #     TestCase("TCCHERYICC-335-2", "225752", "625752", 3),
    #     TestCase("TCCHERYICC-336-1", "225753", "625753", 1),
    #     TestCase("TCCHERYICC-336-2", "225753", "625753", 3),
    #     TestCase("TCCHERYICC-338-1", "22F011", "62F011", 1),
    #     TestCase("TCCHERYICC-338-2", "22F011", "62F011", 3),
    #     TestCase("TCCHERYICC-339-1", "22F190100000", "7F2213", 1),
    #     TestCase("TCCHERYICC-339-2", "22F190100000", "7F2213", 3),
    #     TestCase("TCCHERYICC-340-1", "22F351", "7F2231", 1),
    #     TestCase("TCCHERYICC-340-2", "22F351", "7F2231", 3),
    #     TestCase("TCCHERYICC-341-1", "22598411", "7F2213", 1),
    #     TestCase("TCCHERYICC-341-2", "22598411", "7F2213", 3),
    #     TestCase("TCCHERYICC-342", "2701", "67", 3),
    #     TestCase("TCCHERYICC-343", "2702", "6702", 3),
    #     TestCase("TCCHERYICC-344", "270122", "7F2713", 3),
    #     TestCase("TCCHERYICC-345", "2703", "7F2712", 3),
    #     TestCase("TCCHERYICC-346", "2701", "7F277F", 1),
    #     TestCase("TCCHERYICC-348", "270311", "7F2712", 3),
    #     TestCase("TCCHERYICC-349-1", "2701", "7F2713", 3),
    #     TestCase("TCCHERYICC-349-2", "2702", "7F2713", 3),
    #     TestCase("TCCHERYICC-349-3", "2701", "7F2713", 3),
    #     TestCase("TCCHERYICC-349-4", "2702", "7F2713", 3),
    #     TestCase("TCCHERYICC-349-5", "2701", "7F2713", 3),
    #     TestCase("TCCHERYICC-349-6", "2702", "7F2713", 3),
    #     TestCase("TCCHERYICC-349-7", "270100", "7F2713", 3),
    #     TestCase("TCCHERYICC-350-1", "2701", "7F2712", 3),
    #     TestCase("TCCHERYICC-350-2", "2702", "7F2712", 3),
    #     TestCase("TCCHERYICC-350-3", "2701", "7F2712", 3),
    #     TestCase("TCCHERYICC-350-4", "2702", "7F2712", 3),
    #     TestCase("TCCHERYICC-350-5", "2701", "7F2712", 3),
    #     TestCase("TCCHERYICC-350-6", "2702", "7F2712", 3),
    #     TestCase("TCCHERYICC-350-7", "2703", "7F2712", 3),
    #     TestCase("TCCHERYICC-351-1", "2701", "7F2735", 3),
    #     TestCase("TCCHERYICC-351-2", "2702", "7F2735", 3),
    #     TestCase("TCCHERYICC-352-1", "2701", "7F2735", 0),
    #     TestCase("TCCHERYICC-352-2", "2702", "7F2735", 0),
    #     TestCase("TCCHERYICC-353-1", "2701", "7F2736", 0),
    #     TestCase("TCCHERYICC-353-2", "2702", "7F2736", 0),
    #     TestCase("TCCHERYICC-354", "2701", "7F2737", 0),
    #     TestCase("TCCHERYICC-355", "2702", "7F2736", 0),
    #     TestCase("TCCHERYICC-356-1", "2701", "7F2724", 3),
    #     TestCase("TCCHERYICC-356-2", "2702", "7F2724", 3),
    #     TestCase("TCCHERYICC-356-3", "2702", "7F2724", 3),
    #     TestCase("TCCHERYICC-357", "2702", "67", 0),
    #     TestCase("TCCHERYICC-358", "2702", "7F2724", 3),
    #     TestCase("TCCHERYICC-359", "2702", "7F277F", 1),
    #     TestCase("TCCHERYICC-360", "2703", "7F2712", 3),
    #     TestCase("TCCHERYICC-361", "2702", "7F2713", 3),
    #     TestCase("TCCHERYICC-362-1", "2701", "7F2713", 3),
    #     TestCase("TCCHERYICC-362-2", "2702", "7F2713", 3),
    #     TestCase("TCCHERYICC-363-1", "2701", "7F2713", 3),
    #     TestCase("TCCHERYICC-363-2", "2702", "7F2713", 3),
    #     TestCase("TCCHERYICC-363-3", "2701", "7F2713", 3),
    #     TestCase("TCCHERYICC-363-4", "2702", "7F2713", 3),
    #     TestCase("TCCHERYICC-364-1", "2701", "7F2713", 3),
    #     TestCase("TCCHERYICC-364-2", "2702", "7F2713", 3),
    #     TestCase("TCCHERYICC-364-3", "2701", "7F2713", 3),
    #     TestCase("TCCHERYICC-364-4", "2702", "7F2713", 3),
    #     TestCase("TCCHERYICC-364-5", "2701", "7F2713", 3),
    #     TestCase("TCCHERYICC-364-6", "2702", "7F2713", 3),
    #     TestCase("TCCHERYICC-365", "2704", "7F2712", 3),
    #     TestCase("TCCHERYICC-366-1", "2701", "7F2712", 3),
    #     TestCase("TCCHERYICC-366-2", "2704", "7F2712", 3),
    #     TestCase("TCCHERYICC-367-1", "2701", "7F2712", 3),
    #     TestCase("TCCHERYICC-367-2", "2704", "7F2712", 3),
    #     TestCase("TCCHERYICC-367-3", "2701", "7F2712", 3),
    #     TestCase("TCCHERYICC-367-4", "2704", "7F2712", 3),
    #     TestCase("TCCHERYICC-367-5", "2701", "7F2712", 3),
    #     TestCase("TCCHERYICC-367-6", "2704", "7F2712", 3),
    #     TestCase("TCCHERYICC-368", "2705", "7F2712", 3),
    #     TestCase("TCCHERYICC-369", "2706", "7F2712", 3),
    #     TestCase("TCCHERYICC-371", "280001", "6800", 3),
    #     TestCase("TCCHERYICC-373", "280101", "7F2812", 3),
    #     TestCase("TCCHERYICC-374", "280201", "7F2812", 3),
    #     TestCase("TCCHERYICC-375", "280301", "68", 3),
    #     TestCase("TCCHERYICC-377", "280002", "6800", 3),
    #     TestCase("TCCHERYICC-379", "280102", "7F2812", 3),
    #     TestCase("TCCHERYICC-380", "280202", "7F2812", 3),
    #     TestCase("TCCHERYICC-381", "280302", "6803", 3),
    #     TestCase("TCCHERYICC-383", "280003", "6800", 3),
    #     TestCase("TCCHERYICC-385", "280103", "7F2812", 3),
    #     TestCase("TCCHERYICC-386", "280203", "7F2812", 3),
    #     TestCase("TCCHERYICC-387", "280303", "68", 3),
    #     TestCase("TCCHERYICC-389", "2800", "7F2813", 3),
    #     TestCase("TCCHERYICC-390", "28000101", "7F2813", 3),
    #     TestCase("TCCHERYICC-391", "280401", "7F2812", 3),
    #     TestCase("TCCHERYICC-392", "280001", "7F287F", 1),
    #     TestCase("TCCHERYICC-411", "28010000", "7F2812", 3),
    #     TestCase("TCCHERYICC-412", "28000000", "7F287F", 1),
    #     TestCase("TCCHERYICC-413", "280100", "7F287F", 1),
    #     TestCase("TCCHERYICC-414", "28020000", "7F2813", 3),
    #     TestCase("TCCHERYICC-415", "28030000", "7F287F", 1),
    #     TestCase("TCCHERYICC-416", "280200", "7F287F", 1),
    #     TestCase("TCCHERYICC-423", "2EF0FE41054501B200005000050001104004", "6EF0FE", 3),
    #     TestCase("TCCHERYICC-424", "2EF0FE178E4201000000", "7F2E13", 0),
    #     TestCase("TCCHERYICC-425", "2EF0FF41054501B200005000050001104004", "7F2E31", 0),
    #     TestCase("TCCHERYICC-426", "2EF0FE41054501B200005000050001104004", "7F2E33", 3),
    #     TestCase("TCCHERYICC-427", "2EF0FE41054501B20000500005000110400411", "7F2E13", 3),
    #     TestCase("TCCHERYICC-428", "2EF0FE41054501B200005000050001104004", "7F2E7F", 1),
    #     TestCase("TCCHERYICC-429", "2EF09200", "6EF092", 3),
    #     TestCase("TCCHERYICC-430-1", "2EF0", "7F2E13", 0),
    #     TestCase("TCCHERYICC-430-2", "2EF092", "7F2E13", 0),
    #     TestCase("TCCHERYICC-430-3", "2EF0920000", "7F2E13", 0),
    #     TestCase("TCCHERYICC-431", "2EF0FF00", "7F2E31", 0),
    #     TestCase("TCCHERYICC-432", "2EF09200", "7F2E33", 0),
    #     TestCase("TCCHERYICC-433", "2EF09200", "7F2E7F", 1),
    #     TestCase("TCCHERYICC-434", "2EF09201", "6EF092", 3),
    #     TestCase("TCCHERYICC-435-1", "2EF0", "7F2E13", 0),
    #     TestCase("TCCHERYICC-435-2", "2EF092", "7F2E13", 0),
    #     TestCase("TCCHERYICC-435-3", "2EF0920100", "7F2E13", 0),
    #     TestCase("TCCHERYICC-436", "2EF0FF01", "7F2E31", 0),
    #     TestCase("TCCHERYICC-437", "2EF09201", "7F2E33", 0),
    #     TestCase("TCCHERYICC-438", "2EF09201", "7F2E7F", 1),
    #     TestCase("TCCHERYICC-445", "2E573C1122334455667788991011121314151617181920212223242526272829303132", "6E573C", 3),
    #     TestCase("TCCHERYICC-446", "2E573C112233", "7F2E13", 0),
    #     TestCase("TCCHERYICC-447", "2E57FF1122334455667788991011121314151617181920212223242526272829303132", "7F2E31", 0),
    #     TestCase("TCCHERYICC-448", "2E573C1122334455667788991011121314151617181920212223242526272829303132", "7F2E33", 0),
    #     TestCase("TCCHERYICC-449", "2E573C112233445566778899101112131415161718192021222324252627282930313211", "7F2E13", 3),
    #     TestCase("TCCHERYICC-450", "2E573C1122334455667788991011121314151617181920212223242526272829303132", "7F2E7F", 1),
    #     TestCase("TCCHERYICC-451", "2E573D1122334455667788991011121314151617181920212223242526272829303132", "6E573D", 3),
    #     TestCase("TCCHERYICC-452-1", "2E57", "7F2E13", 0),
    #     TestCase("TCCHERYICC-452-2", "2E573D", "7F2E13", 0),
    #     TestCase("TCCHERYICC-452-3", "2E573D11", "7F2E13", 0),
    #     TestCase("TCCHERYICC-452-4", "2E573D1122", "7F2E13", 0),
    #     TestCase("TCCHERYICC-452-5", "2E573D112233", "7F2E13", 0),
    #     TestCase("TCCHERYICC-452-6", "2E573D11223344", "7F2E13", 0),
    #     TestCase("TCCHERYICC-453", "2E57FF1122334455667788991011121314151617181920212223242526272829303132", "7F2E31", 0),
    #     TestCase("TCCHERYICC-454", "2E573D1122334455667788991011121314151617181920212223242526272829303132", "7F2E33", 0),
    #     TestCase("TCCHERYICC-455", "2E573D112233445566778899101112131415161718192021222324252627282930313222", "7F2E13", 3),
    #     TestCase("TCCHERYICC-456", "2E573D1122334455667788991011121314151617181920212223242526272829303132", "7F2E7F", 1),
    #     TestCase("TCCHERYICC-457", "2EF011", "6EF011", 3),
    #     TestCase("TCCHERYICC-458", "2EF0112233", "7F2E13", 0),
    #     TestCase("TCCHERYICC-459", "2EF0FF", "7F2E31", 0),
    #     TestCase("TCCHERYICC-460", "2EF011", "7F2E33", 0),
    #     TestCase("TCCHERYICC-461", "2EF011", "7F2E7F", 1),
    #     TestCase("TCCHERYICC-462", "2E0000", "7F2E13", 3),
    #     TestCase("TCCHERYICC-466", "2EF0FE41054501B20000500005000110400400", "7F2E7F", 1),
    #     TestCase("TCCHERYICC-467", "2EF0FE41054501B20000500005000110400400", "7F2E13", 3),
    #     TestCase("TCCHERYICC-468", "2EF0FE41054501B200005000050001104004", "7F2E7F", 1),
    #     TestCase("TCCHERYICC-477", "2F571E0301", "6F571E0301", 0),
    #     TestCase("TCCHERYICC-478", "2F571E0302", "6F571E0302", 0),
    #     TestCase("TCCHERYICC-479", "2F571E0303", "6F571E0303", 0),
    #     TestCase("TCCHERYICC-480", "2F571E0304FF", "7F2F31", 0),
    #     TestCase("TCCHERYICC-481", "2F571E00", "6F571E00", 0),
    #     TestCase("TCCHERYICC-482-1", "2F57", "7F2F13", 0),
    #     TestCase("TCCHERYICC-482-2", "2F571E03", "7F2F13", 0),
    #     TestCase("TCCHERYICC-482-3", "2F571E0300000000", "7F2F13", 0),
    #     TestCase("TCCHERYICC-483", "2F571E01", "7F2F31", 0),
    #     TestCase("TCCHERYICC-484", "2F571E0303", "7F2F33", 0),
    #     TestCase("TCCHERYICC-485", "2F571E0300", "7F2F31", 1),
    #     TestCase("TCCHERYICC-486", "2F571F0300", "7F2F31", 3),
    #     TestCase("TCCHERYICC-487", "2F571F0301", "6F571F0301", 0),
    #     TestCase("TCCHERYICC-488", "2F571F0302", "6F571F0302", 0),
    #     TestCase("TCCHERYICC-489", "2F571F00", "6F571F00", 0),
    #     TestCase("TCCHERYICC-490-1", "2F57", "7F2F13", 0),
    #     TestCase("TCCHERYICC-490-2", "2F571F03", "7F2F13", 0),
    #     TestCase("TCCHERYICC-490-3", "2F571F0300000000", "7F2F13", 0),
    #     TestCase("TCCHERYICC-491-1", "2F571F01FF", "7F2F31", 0),
    #     TestCase("TCCHERYICC-491-2", "2F571F0303FF", "7F2F31", 0),
    #     TestCase("TCCHERYICC-492-1", "2F571F00", "7F2F33", 0),
    #     TestCase("TCCHERYICC-492-2", "2F571F0301", "7F2F33", 0),
    #     TestCase("TCCHERYICC-492-3", "2F571F0302", "7F2F33", 0),
    #     TestCase("TCCHERYICC-493-1", "2F571F00", "7F2F31", 1),
    #     TestCase("TCCHERYICC-493-2", "2F571F0301", "7F2F31", 1),
    #     TestCase("TCCHERYICC-493-3", "2F571F0302", "7F2F31", 1),
    #     TestCase("TCCHERYICC-494-1", "2F57", "7F2F13", 1),
    #     TestCase("TCCHERYICC-494-2", "2F571D", "7F2F13", 1),
    #     TestCase("TCCHERYICC-495", "2F571D", "7F2F13", 3),
    #     TestCase("TCCHERYICC-500", "3E00", "7E00", 1),
    #     TestCase("TCCHERYICC-502", "3E0000", "7F3E13", 1),
    #     TestCase("TCCHERYICC-503", "3E8000", "7F3E13", 1),
    #     TestCase("TCCHERYICC-504", "3E01", "7F3E12", 1),
    #     TestCase("TCCHERYICC-505", "3E02", "7F3E12", 1),
    #     TestCase("TCCHERYICC-507-1", "3E0200", "7F3E12", 1),
    #     TestCase("TCCHERYICC-507-2", "3E0300", "7F3E12", 1),
    #     TestCase("TCCHERYICC-507-3", "3E0400", "7F3E12", 1),
    #     TestCase("TCCHERYICC-508", "8501", "C5", 3),
    #     TestCase("TCCHERYICC-510", "8502", "C5", 3),
    #     TestCase("TCCHERYICC-512", "8503", "7F8512", 3),
    #     TestCase("TCCHERYICC-513", "8583", "7F8512", 3),
    #     TestCase("TCCHERYICC-514", "850211", "7F8513", 3),
    #     TestCase("TCCHERYICC-515-1", "8501", "7F857F", 1),
    #     TestCase("TCCHERYICC-515-2", "8502", "7F857F", 1),
    #     TestCase("TCCHERYICC-517", "850301", "7F8512", 3),
    #     TestCase("TCCHERYICC-518", "850301", "7F857F", 1),
    #     TestCase("TCCHERYICC-520", "31015783", "710157", 3),
    #     TestCase("TCCHERYICC-521", "31025783", "7F3112", 0),
    #     TestCase("TCCHERYICC-522", "31035783", "7F3112", 0),
    #     TestCase("TCCHERYICC-523", "31005783", "7F3112", 0),
    #     TestCase("TCCHERYICC-524-1", "310157", "7F3113", 0),
    #     TestCase("TCCHERYICC-524-2", "3101578300", "7F3113", 0),
    #     TestCase("TCCHERYICC-524-3", "310157830000", "7F3113", 0),
    #     TestCase("TCCHERYICC-525", "31015683", "7F3131", 0),
    #     TestCase("TCCHERYICC-526", "31015783", "7F3133", 0),
    #     TestCase("TCCHERYICC-527", "31015783", "7F317F", 1),
    #     TestCase("TCCHERYICC-528", "3101578500", "7F3131", 3),
    #     TestCase("TCCHERYICC-530-1", "3102578600", "7F3112", 0),
    #     TestCase("TCCHERYICC-530-2", "030007", "7F3112", 0),
    #     TestCase("TCCHERYICC-531-1", "3103578600", "7F3112", 0),
    #     TestCase("TCCHERYICC-531-2", "030007", "7F3112", 0),
    #     TestCase("TCCHERYICC-532-1", "3100578600", "7F3112", 0),
    #     TestCase("TCCHERYICC-532-2", "030007", "7F3112", 0),
    #     TestCase("TCCHERYICC-533-1", "31015786", "7F3113", 0),
    #     TestCase("TCCHERYICC-533-2", "3101578600", "7F3113", 0),
    #     TestCase("TCCHERYICC-533-3", "310157860000FF", "7F3113", 0),
    #     TestCase("TCCHERYICC-534-1", "310157860407", "7F3131", 0),
    #     TestCase("TCCHERYICC-534-2", "310157860108", "7F3131", 0),
    #     TestCase("TCCHERYICC-534-3", "31015786FFFF", "7F3131", 0),
    #     TestCase("TCCHERYICC-535-1", "3101578600", "7F3133", 0),
    #     TestCase("TCCHERYICC-535-2", "030007", "7F3133", 0),
    #     TestCase("TCCHERYICC-536-1", "3101578600", "7F317F", 1),
    #     TestCase("TCCHERYICC-536-2", "030007", "7F317F", 1),
    #     TestCase("TCCHERYICC-537", "31015788", "7F3131", 3),
    #     TestCase("TCCHERYICC-538", "31025788", "7F3131", 3),
    #     TestCase("TCCHERYICC-539", "31015789", "7F3131", 3),
    #     TestCase("TCCHERYICC-540", "31025789", "7F3131", 3),
    #     TestCase("TCCHERYICC-541", "31015790", "7F3131", 3),
    #     TestCase("TCCHERYICC-542", "31025790", "7F3131", 3),
    #     TestCase("TCCHERYICC-544", "31025791", "7F3112", 0),
    #     TestCase("TCCHERYICC-545", "31035791", "710357", 0),
    #     TestCase("TCCHERYICC-546", "31005791", "7F3112", 0),
    #     TestCase("TCCHERYICC-547-1", "31015791", "7F3113", 0),
    #     TestCase("TCCHERYICC-547-2", "310157910000", "7F3113", 0),
    #     TestCase("TCCHERYICC-547-3", "310357", "7F3113", 0),
    #     TestCase("TCCHERYICC-547-4", "3103579100", "7F3113", 0),
    #     TestCase("TCCHERYICC-548-1", "3101579100", "7F3131", 0),
    #     TestCase("TCCHERYICC-548-2", "03FF", "7F3131", 0),
    #     TestCase("TCCHERYICC-549", "3101579101", "7F3133", 0),
    #     TestCase("TCCHERYICC-550", "31035791", "7F3133", 0),
    #     TestCase("TCCHERYICC-551", "3101579101", "7F317F", 1),
    #     TestCase("TCCHERYICC-552", "31035791", "7F317F", 1),
    #     TestCase("TCCHERYICC-553", "31015792", "710157", 3),
    #     TestCase("TCCHERYICC-554", "31025792", "7F3112", 0),
    #     TestCase("TCCHERYICC-555", "31035792", "7F3112", 0),
    #     TestCase("TCCHERYICC-556", "31005792", "7F3112", 0),
    #     TestCase("TCCHERYICC-557-1", "310192", "7F3113", 0),
    #     TestCase("TCCHERYICC-557-2", "310157920F", "7F3113", 0),
    #     TestCase("TCCHERYICC-558", "310192FFFF", "7F3131", 0),
    #     TestCase("TCCHERYICC-559", "31015792", "7F3133", 0),
    #     TestCase("TCCHERYICC-560", "31015792", "7F317F", 1),
    #     TestCase("TCCHERYICC-561", "31015793", "710157", 3),
    #     TestCase("TCCHERYICC-562", "31025793", "7F3112", 0),
    #     TestCase("TCCHERYICC-563", "31035793", "7F3112", 0),
    #     TestCase("TCCHERYICC-564", "31005793", "7F3112", 0),
    #     TestCase("TCCHERYICC-565-1", "310193", "7F3113", 0),
    #     TestCase("TCCHERYICC-565-2", "3101579304", "7F3113", 0),
    #     TestCase("TCCHERYICC-566", "310193FFFF", "7F3131", 0),
    #     TestCase("TCCHERYICC-567", "31015793", "7F3133", 0),
    #     TestCase("TCCHERYICC-568", "31015793", "7F317F", 1),
    #     TestCase("TCCHERYICC-569-1", "31015795000C", "7F3131", 3),
    #     TestCase("TCCHERYICC-569-2", "31025795", "7F3131", 3),
    #     TestCase("TCCHERYICC-569-3", "31035795", "7F3131", 3),
    #     TestCase("TCCHERYICC-571", "31025781", "7102578104", 0),
    #     TestCase("TCCHERYICC-572", "31035781", "710357", 0),
    #     TestCase("TCCHERYICC-573", "31005781", "7F3112", 0),
    #     TestCase("TCCHERYICC-574-1", "310157", "7F3113", 0),
    #     TestCase("TCCHERYICC-574-2", "3101578100", "7F3113", 0),
    #     TestCase("TCCHERYICC-574-3", "310157810000", "7F3113", 0),
    #     TestCase("TCCHERYICC-575-1", "31015782", "7F3131", 0),
    #     TestCase("TCCHERYICC-575-2", "84FF", "7F3131", 0),
    #     TestCase("TCCHERYICC-575-3", "31025782", "7F3131", 0),
    #     TestCase("TCCHERYICC-575-4", "84FF", "7F3131", 0),
    #     TestCase("TCCHERYICC-575-5", "31035782", "7F3131", 0),
    #     TestCase("TCCHERYICC-575-6", "84FF", "7F3131", 0),
    #     TestCase("TCCHERYICC-576", "31025781", "7F3124", 3),
    #     TestCase("TCCHERYICC-577-1", "3101", "7F3133", 0),
    #     TestCase("TCCHERYICC-577-2", "035781", "7F3133", 0),
    #     TestCase("TCCHERYICC-578-1", "3101", "7F317F", 1),
    #     TestCase("TCCHERYICC-578-2", "035781", "7F317F", 1),
    #     TestCase("TCCHERYICC-579", "3101DD4501", "7101DD4501", 3),
    #     TestCase("TCCHERYICC-580", "3101DD4500", "7101DD", 3),
    #     TestCase("TCCHERYICC-581", "3102DD45", "7F3112", 0),
    #     TestCase("TCCHERYICC-582", "3103DD45", "7F3112", 0),
    #     TestCase("TCCHERYICC-583", "3100DD45", "7F3112", 0),
    #     TestCase("TCCHERYICC-584-1", "3101DD", "7F3113", 0),
    #     TestCase("TCCHERYICC-584-2", "3101DD45", "7F3113", 0),
    #     TestCase("TCCHERYICC-584-3", "3101DD450100", "7F3113", 0),
    #     TestCase("TCCHERYICC-585", "3101DD4502FF", "7F3131", 0),
    #     TestCase("TCCHERYICC-586", "3101DD4500", "7F3133", 0),
    #     TestCase("TCCHERYICC-587", "3101DD4500", "7F317F", 1),
    #     TestCase("TCCHERYICC-591", "3101DD4600", "7101DD", 3),
    #     TestCase("TCCHERYICC-592", "3102DD46", "7F3112", 0),
    #     TestCase("TCCHERYICC-593", "3103DD46", "7F3112", 0),
    #     TestCase("TCCHERYICC-594", "3100DD46", "7F3112", 0),
    #     TestCase("TCCHERYICC-595-1", "3101DD", "7F3113", 0),
    #     TestCase("TCCHERYICC-595-2", "3101DD46", "7F3113", 0),
    #     TestCase("TCCHERYICC-596", "310146FF", "7F3131", 0),
    #     TestCase("TCCHERYICC-597", "3101DD4600", "7F3133", 0),
    #     TestCase("TCCHERYICC-598", "3101DD4600", "7F317F", 1),
    #     TestCase("TCCHERYICC-599", "3101578100", "7F3113", 3),
    #     TestCase("TCCHERYICC-600-1", "3101", "7F3113", 3),
    #     TestCase("TCCHERYICC-600-2", "310157", "7F3113", 3),
    #     TestCase("TCCHERYICC-601-1", "3102", "7F3113", 3),
    #     TestCase("TCCHERYICC-601-2", "310257", "7F3113", 3),
    #     TestCase("TCCHERYICC-602", "31005781", "7F3133", 3),
    #     TestCase("TCCHERYICC-603", "31025781", "7F3133", 3),
    #     TestCase("TCCHERYICC-604", "1001", "5001003201F4", 0),
    #     TestCase("TCCHERYICC-606", "1003", "5003003201F4", 0),
    #     TestCase("TCCHERYICC-609", "100101", "7F1013", 0),
    #     TestCase("TCCHERYICC-611-1", "1101", "5101", 1),
    #     TestCase("TCCHERYICC-611-2", "1101", "5101", 3),
    #     TestCase("TCCHERYICC-615-1", "1103", "5103", 1),
    #     TestCase("TCCHERYICC-615-2", "1103", "5103", 3),
    #     TestCase("TCCHERYICC-617-1", "110101", "7F1113", 1),
    #     TestCase("TCCHERYICC-617-2", "110101", "7F1113", 3),
    #     TestCase("TCCHERYICC-619", "1101", "7F1122", 0),
    #     TestCase("TCCHERYICC-620", "110101", "7F1113", 0),
    #     TestCase("TCCHERYICC-622-1", "14FFFFFF", "54", 1),
    #     TestCase("TCCHERYICC-622-2", "14FFFFFF", "54", 3),
    #     TestCase("TCCHERYICC-625-1", "14FF", "7F1413", 1),
    #     TestCase("TCCHERYICC-625-2", "14FFFF", "7F1413", 1),
    #     TestCase("TCCHERYICC-625-3", "14FFFFFF01", "7F1413", 1),
    #     TestCase("TCCHERYICC-625-4", "14FF", "7F1413", 3),
    #     TestCase("TCCHERYICC-625-5", "14FFFF", "7F1413", 3),
    #     TestCase("TCCHERYICC-625-6", "14FFFFFF01", "7F1413", 3),
    #     TestCase("TCCHERYICC-626", "14FFFFFF", "7F1422", 0),
    #     TestCase("TCCHERYICC-627", "1400000001", "7F1413", 0),
    #     TestCase("TCCHERYICC-628", "14FFFFFF01", "7F1413", 0),
    #     TestCase("TCCHERYICC-640-1", "22F187", "62F187", 1),
    #     TestCase("TCCHERYICC-640-2", "22F187", "62F187", 3),
    #     TestCase("TCCHERYICC-641-1", "22F189", "62F189", 1),
    #     TestCase("TCCHERYICC-641-2", "22F189", "62F189", 3),
    #     TestCase("TCCHERYICC-642-1", "22F089", "62F089", 1),
    #     TestCase("TCCHERYICC-642-2", "22F089", "62F089", 3),
    #     TestCase("TCCHERYICC-643-1", "22F013", "62F013", 1),
    #     TestCase("TCCHERYICC-643-2", "22F013", "62F013", 3),
    #     TestCase("TCCHERYICC-644-1", "22F18A", "62F18A", 1),
    #     TestCase("TCCHERYICC-644-2", "22F18A", "62F18A", 3),
    #     TestCase("TCCHERYICC-645-1", "22F18B", "62F18B", 1),
    #     TestCase("TCCHERYICC-645-2", "22F18B", "62F18B", 3),
    #     TestCase("TCCHERYICC-646-1", "22F18C", "62F18C", 1),
    #     TestCase("TCCHERYICC-646-2", "22F18C", "62F18C", 3),
    #     TestCase("TCCHERYICC-647-1", "22F190", "62F190", 1),
    #     TestCase("TCCHERYICC-647-2", "22F190", "62F190", 3),
    #     TestCase("TCCHERYICC-648-1", "22F186", "62F186", 1),
    #     TestCase("TCCHERYICC-648-2", "22F186", "62F186", 3),
    #     TestCase("TCCHERYICC-649-1", "22F0FE", "62F0FE", 1),
    #     TestCase("TCCHERYICC-649-2", "22F0FE", "62F0FE", 3),
    #     TestCase("TCCHERYICC-650-1", "22F091", "62F091", 1),
    #     TestCase("TCCHERYICC-650-2", "22F091", "62F091", 3),
    #     TestCase("TCCHERYICC-651-1", "22F083", "62F083", 1),
    #     TestCase("TCCHERYICC-651-2", "22F083", "62F083", 3),
    #     TestCase("TCCHERYICC-652-1", "22F084", "62F084", 1),
    #     TestCase("TCCHERYICC-652-2", "22F084", "62F084", 3),
    #     TestCase("TCCHERYICC-653-1", "22F085", "62F085", 1),
    #     TestCase("TCCHERYICC-653-2", "22F085", "62F085", 3),
    #     TestCase("TCCHERYICC-654-1", "22F086", "62F086", 1),
    #     TestCase("TCCHERYICC-654-2", "22F086", "62F086", 3),
    #     TestCase("TCCHERYICC-655-1", "22F087", "62F087", 1),
    #     TestCase("TCCHERYICC-655-2", "22F087", "62F087", 3),
    #     TestCase("TCCHERYICC-656-1", "22F092", "62F092", 1),
    #     TestCase("TCCHERYICC-656-2", "22F092", "62F092", 3),
    #     TestCase("TCCHERYICC-657-1", "225703", "625703", 1),
    #     TestCase("TCCHERYICC-657-2", "225703", "625703", 3),
    #     TestCase("TCCHERYICC-658-1", "225708", "625708", 1),
    #     TestCase("TCCHERYICC-658-2", "225708", "625708", 3),
    #     TestCase("TCCHERYICC-659-1", "22570E", "62570E", 1),
    #     TestCase("TCCHERYICC-659-2", "22570E", "62570E", 3),
    #     TestCase("TCCHERYICC-660-1", "225717", "625717", 1),
    #     TestCase("TCCHERYICC-660-2", "225717", "625717", 3),
    #     TestCase("TCCHERYICC-661-1", "225721", "625721", 1),
    #     TestCase("TCCHERYICC-661-2", "225721", "625721", 3),
    #     TestCase("TCCHERYICC-662-1", "225722", "625722", 1),
    #     TestCase("TCCHERYICC-662-2", "225722", "625722", 3),
    #     TestCase("TCCHERYICC-663-1", "225723", "625723", 1),
    #     TestCase("TCCHERYICC-663-2", "225723", "625723", 3),
    #     TestCase("TCCHERYICC-664-1", "225724", "625724", 1),
    #     TestCase("TCCHERYICC-664-2", "225724", "625724", 3),
    #     TestCase("TCCHERYICC-665-1", "225727", "625727", 1),
    #     TestCase("TCCHERYICC-665-2", "225727", "625727", 3),
    #     TestCase("TCCHERYICC-666-1", "225728", "625728", 1),
    #     TestCase("TCCHERYICC-666-2", "225728", "625728", 3),
    #     TestCase("TCCHERYICC-667-1", "225729", "625729", 1),
    #     TestCase("TCCHERYICC-667-2", "225729", "625729", 3),
    #     TestCase("TCCHERYICC-668-1", "22572A", "62572A", 1),
    #     TestCase("TCCHERYICC-668-2", "22572A", "62572A", 3),
    #     TestCase("TCCHERYICC-670-1", "22572B", "62572B", 1),
    #     TestCase("TCCHERYICC-670-2", "22572B", "62572B", 3),
    #     TestCase("TCCHERYICC-671-1", "22572C", "62572C", 1),
    #     TestCase("TCCHERYICC-671-2", "22572C", "62572C", 3),
    #     TestCase("TCCHERYICC-672-1", "22572D", "62572D", 1),
    #     TestCase("TCCHERYICC-672-2", "22572D", "62572D", 3),
    #     TestCase("TCCHERYICC-673-1", "22572E", "62572E", 1),
    #     TestCase("TCCHERYICC-673-2", "22572E", "62572E", 3),
    #     TestCase("TCCHERYICC-674-1", "22572F", "62572F", 1),
    #     TestCase("TCCHERYICC-674-2", "22572F", "62572F", 3),
    #     TestCase("TCCHERYICC-675-1", "225730", "625730", 1),
    #     TestCase("TCCHERYICC-675-2", "225730", "625730", 3),
    #     TestCase("TCCHERYICC-676-1", "225731", "625731", 1),
    #     TestCase("TCCHERYICC-676-2", "225731", "625731", 3),
    #     TestCase("TCCHERYICC-677-1", "22573A", "62573A", 1),
    #     TestCase("TCCHERYICC-677-2", "22573A", "62573A", 3),
    #     TestCase("TCCHERYICC-678-1", "22573B", "62573B", 1),
    #     TestCase("TCCHERYICC-678-2", "22573B", "62573B", 3),
    #     TestCase("TCCHERYICC-679-1", "22573C", "62573C", 1),
    #     TestCase("TCCHERYICC-679-2", "22573C", "62573C", 3),
    #     TestCase("TCCHERYICC-680-1", "22573D", "62573D", 1),
    #     TestCase("TCCHERYICC-680-2", "22573D", "62573D", 3),
    #     TestCase("TCCHERYICC-681-1", "22573F", "62573F", 1),
    #     TestCase("TCCHERYICC-681-2", "22573F", "62573F", 3),
    #     TestCase("TCCHERYICC-682-1", "225740", "625740", 1),
    #     TestCase("TCCHERYICC-682-2", "225740", "625740", 3),
    #     TestCase("TCCHERYICC-683-1", "225741", "625741", 1),
    #     TestCase("TCCHERYICC-683-2", "225741", "625741", 3),
    #     TestCase("TCCHERYICC-684-1", "225742", "625742", 1),
    #     TestCase("TCCHERYICC-684-2", "225742", "625742", 3),
    #     TestCase("TCCHERYICC-685-1", "225743", "625743", 1),
    #     TestCase("TCCHERYICC-685-2", "225743", "625743", 3),
    #     TestCase("TCCHERYICC-686-1", "225744", "625744", 1),
    #     TestCase("TCCHERYICC-686-2", "225744", "625744", 3),
    #     TestCase("TCCHERYICC-687-1", "225745", "625745", 1),
    #     TestCase("TCCHERYICC-687-2", "225745", "625745", 3),
    #     TestCase("TCCHERYICC-688-1", "22574D", "62574D", 1),
    #     TestCase("TCCHERYICC-688-2", "22574D", "62574D", 3),
    #     TestCase("TCCHERYICC-689-1", "22574E", "62574E", 1),
    #     TestCase("TCCHERYICC-689-2", "22574E", "62574E", 3),
    #     TestCase("TCCHERYICC-690-1", "22574F", "62574F", 1),
    #     TestCase("TCCHERYICC-690-2", "22574F", "62574F", 3),
    #     TestCase("TCCHERYICC-691-1", "225750", "625750", 1),
    #     TestCase("TCCHERYICC-691-2", "225750", "625750", 3),
    #     TestCase("TCCHERYICC-692-1", "225751", "625751", 1),
    #     TestCase("TCCHERYICC-692-2", "225751", "625751", 3),
    #     TestCase("TCCHERYICC-693-1", "225752", "625752", 1),
    #     TestCase("TCCHERYICC-693-2", "225752", "625752", 3),
    #     TestCase("TCCHERYICC-694-1", "225753", "625753", 1),
    #     TestCase("TCCHERYICC-694-2", "225753", "625753", 3),
    #     TestCase("TCCHERYICC-696-1", "22F011", "62F011", 1),
    #     TestCase("TCCHERYICC-696-2", "22F011", "62F011", 3),
    #     TestCase("TCCHERYICC-697-1", "22F190100000", "7F2213", 1),
    #     TestCase("TCCHERYICC-697-2", "22F190100000", "7F2213", 3),
    #     TestCase("TCCHERYICC-699-1", "22598411", "7F2213", 1),
    #     TestCase("TCCHERYICC-699-2", "22598411", "7F2213", 3),
    #     TestCase("TCCHERYICC-704", "280001", "6800", 3),
    #     TestCase("TCCHERYICC-708", "280301", "6803", 3),
    #     TestCase("TCCHERYICC-710", "280002", "6800", 3),
    #     TestCase("TCCHERYICC-714", "280302", "6803", 3),
    #     TestCase("TCCHERYICC-716", "280003", "6800", 3),
    #     TestCase("TCCHERYICC-720", "280303", "6803", 3),
    #     TestCase("TCCHERYICC-722", "2800", "7F2813", 3),
    #     TestCase("TCCHERYICC-723", "28000101", "7F2813", 3),
    #     TestCase("TCCHERYICC-828", "3E00", "7E00", 1),
    #     TestCase("TCCHERYICC-830", "3E0000", "7F3E13", 1),
    #     TestCase("TCCHERYICC-831", "3E8000", "7F3E13", 1),
    #     TestCase("TCCHERYICC-835", "8501", "C501", 3),
    #     TestCase("TCCHERYICC-837", "8502", "C502", 3),
    #     TestCase("TCCHERYICC-841", "850211", "7F8513", 3),
    #     TestCase("TCCHERYICC-844", "850301", "7F8513", 3),
    #     TestCase("TCCHERYICC-931", "1003", "5003003201F4", 0),
    #     TestCase("TCCHERYICC-932", "1101", "5101", 0),
    #     TestCase("TCCHERYICC-933", "14FFFFFF", "54", 0),
    #     TestCase("TCCHERYICC-935-1", "2701", "67", 0),
    #     TestCase("TCCHERYICC-935-2", "2702", "67", 0),
    #     TestCase("TCCHERYICC-936", "22F190", "62F190", 0),
    #     TestCase("TCCHERYICC-937", "280001", "6800", 3),
    #     TestCase("TCCHERYICC-940", "3E00", "7E00", 0),
    #     TestCase("TCCHERYICC-941", "8501", "C501", 3),
    #     TestCase("TCCHERYICC-942", "1003", "5003003201F4", 0),
    #     TestCase("TCCHERYICC-943", "1101", "5101", 0),
    #     TestCase("TCCHERYICC-944", "14FFFFFF", "54", 0),
    #     TestCase("TCCHERYICC-946-1", "2701", "67", 0),
    #     TestCase("TCCHERYICC-946-2", "2702", "67", 0),
    #     TestCase("TCCHERYICC-947", "22F190", "62F190", 0),
    #     TestCase("TCCHERYICC-948", "280001", "6800", 3),
    #     TestCase("TCCHERYICC-951", "3E00", "7E00", 0),
    #     TestCase("TCCHERYICC-952", "8501", "C501", 3),
    #     TestCase("TCCHERYICC-953", "1003", "5003003201F4", 0),
    #     TestCase("TCCHERYICC-954", "1101", "5101", 0),
    #     TestCase("TCCHERYICC-955", "14FFFFFF", "54", 0),
    #     TestCase("TCCHERYICC-957-1", "2701", "67", 0),
    #     TestCase("TCCHERYICC-957-2", "2702", "67", 0),
    #     TestCase("TCCHERYICC-958", "22F190", "62F190", 0),
    #     TestCase("TCCHERYICC-959", "280001", "6800", 3),
    #     TestCase("TCCHERYICC-962", "3E00", "7E00", 0),
    #     TestCase("TCCHERYICC-963", "8501", "C501", 3),
    # ]


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("=" * 60)
    print("Chery DoIP 自动化测试工具")
    print("=" * 60)
    print()
    
    # 创建测试执行器
    runner = AutoTestRunner()
    
    # 连接 ECU
    if not runner.connect():
        logger.error("无法连接到 ECU，程序退出")
        return 1
    
    runner.start_time = datetime.now()
    
    try:
        # 执行测试套件
        all_results = []

        all_tests = get_a_class_tests()
        all_results.extend(runner.run_test_suite(all_tests, "ALL"))
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
