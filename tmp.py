# -*- coding: utf-8 -*-
"""
网络连通性自动化测试工具 (tmp.py)
- 修改 Windows 本机网卡 VLAN 和 IP
- Ping 目标 ECU IP
- 生成测试报告
"""

import os
import sys
import time
import subprocess
from datetime import datetime
from typing import List
from dataclasses import dataclass
from enum import Enum

# ==================== 基础类定义 (参考 auto_test_mps.py) ====================

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
class NetworkTestCase:
    """网络测试用例"""
    name: str               # 用例名称 (对应 TestResult.name)
    local_ip: str           # 本机 Windows IP
    vlan_id: int            # 本机 Windows VLAN ID
    target_ip: str          # 要 Ping 的目标 ECU IP



class NetworkTestRunner:
    """网络测试执行器"""

    def __init__(self, interface_name: str = "以太网"):
        """
        初始化
        :param interface_name: Windows 网卡名称 (如 "以太网", "Ethernet")
        """
        self.interface_name = interface_name
        self.results: List[TestResult] = []

    def _run_cmd(self, cmd: str) -> tuple:
        """执行 Windows 系统命令"""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, encoding='gbk'
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return -1, "", str(e)

    def setup_windows_network(self, ip: str, vlan_id: int, subnet: str = "255.255.255.0") -> bool:
        """
        修改 Windows 本机网卡的 VLAN 和 IP 地址
        """
        print(f"   → 正在配置网卡: VLAN={vlan_id}, IP={ip}")
        
        # 1. 设置静态 IP
        cmd_ip = f'netsh interface ip set address name="{self.interface_name}" static {ip} {subnet} gateway=none'
        ret_ip, _, err_ip = self._run_cmd(cmd_ip)
        
        if ret_ip != 0:
            print(f"   ⚠️ 设置 IP 警告: {err_ip.strip()}")
            # 某些环境可能报错但实际生效，或者需要管理员权限

        # 2. 设置 VLAN ID
        # 注意：此命令依赖网卡驱动支持。如果不支持，可能需要通过交换机或网卡高级属性配置
        cmd_vlan = f'netsh interface ipv4 set interface "{self.interface_name}" vlan={vlan_id}'
        ret_vlan, _, err_vlan = self._run_cmd(cmd_vlan)
        
        if ret_vlan != 0:
            print(f"   ⚠️ 设置 VLAN 警告: {err_vlan.strip()}")

        # 等待网络配置生效
        time.sleep(2)
        
        # 3. 验证 IP 是否生效
        ret_verify, out_verify, _ = self._run_cmd(f'ipconfig | findstr "{ip}"')
        if ret_verify == 0:
            print(f"   ✅ 网络配置成功: {ip} (VLAN {vlan_id})")
            return True
        else:
            print(f"   ❌ 网络配置可能未生效，请检查")
            return False

    def ping_target(self, target_ip: str, count: int = 4, timeout: int = 2) -> tuple:
        """
        Ping 目标 IP
        :return: (success: bool, message: str)
        """
        cmd = f'ping -n {count} -w {timeout * 1000} {target_ip}'
        ret, out, _ = self._run_cmd(cmd)
        
        # Windows ping 成功通常包含 "TTL="
        if ret == 0 and "TTL" in out:
            # 提取延迟信息
            for line in out.split('\n'):
                if "平均" in line or "Average" in line:
                    return True, line.strip()
            return True, "Ping 成功"
        else:
            return False, "Ping 失败 (请求超时或无法访问)"

    def run_test_case(self, test_case: NetworkTestCase) -> TestResult:
        """执行单个网络测试用例"""
        start_time = time.time()
        print(f"\n执行用例: {test_case.name}")

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
            print(f"   → 正在 Ping 目标: {test_case.target_ip}")
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

    def run_suite(self, test_cases: List[NetworkTestCase]) -> List[TestResult]:
        """执行测试套件"""
        print(f"\n{'='*60}")
        print(f"开始执行网络测试套件 (网卡: {self.interface_name})")
        print(f"{'='*60}")

        self.results = []
        for i, tc in enumerate(test_cases, 1):
            print(f"[{i}/{len(test_cases)}]")
            result = self.run_test_case(tc)
            self.results.append(result)
            print(f"   结果: {result.status.value} - {result.message}")
            time.sleep(1) # 用例间隔

        return self.results

    def generate_report(self, output_path: str = "output"):
        """生成测试报告"""
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(output_path, f"network_test_report_{timestamp}.txt")

        with open(report_file, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("网络连通性自动化测试报告\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"测试网卡：{self.interface_name}\n\n")

            # 统计
            total = len(self.results)
            passed = sum(1 for r in self.results if r.status == TestStatus.PASS)
            failed = sum(1 for r in self.results if r.status == TestStatus.FAIL)
            errors = sum(1 for r in self.results if r.status == TestStatus.ERROR)

            f.write(f"测试结果统计:\n")
            f.write(f"  总计：{total}\n")
            f.write(f"  通过：{passed}\n")
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

        print(f"\n📄 测试报告已保存：{report_file}")
        return report_file


# ==================== 测试用例定义 ====================

def get_network_tests() -> List[NetworkTestCase]:
    """定义网络测试用例"""
    return [
        NetworkTestCase(
            name="网络测试 - 54 网段",
            local_ip="192.168.54.71",
            vlan_id=54,
            target_ip="192.168.54.31"
        ),
        NetworkTestCase(
            name="网络测试 - 55 网段",
            local_ip="192.168.55.71",
            vlan_id=55,
            target_ip="192.168.55.31"
        ),
        NetworkTestCase(
            name="网络测试 - 61 网段",
            local_ip="192.168.61.71",
            vlan_id=61,
            target_ip="192.168.61.31"
        ),
        NetworkTestCase(
            name="网络测试 - 69 网段",
            local_ip="192.168.69.71",
            vlan_id=69,
            target_ip="192.168.69.31"
        ),
    ]


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("=" * 60)
    print("网络连通性自动化测试工具")
    print("=" * 60)

    # 配置 Windows 网卡名称 (请在"网络连接"中确认)
    # 常见名称: "以太网", "Ethernet", "WLAN", "本地连接"
    INTERFACE_NAME = "以太网" 

    # 创建测试执行器
    runner = NetworkTestRunner(interface_name=INTERFACE_NAME)

    # 获取测试用例
    test_cases = get_network_tests()

    # 执行测试套件
    all_results = runner.run_suite(test_cases)

    # 生成报告
    runner.generate_report()

    # 打印总结
    total = len(all_results)
    passed = sum(1 for r in all_results if r.status == TestStatus.PASS)
    failed = sum(1 for r in all_results if r.status == TestStatus.FAIL)

    print("\n" + "=" * 60)
    print("测试执行完成")
    print("=" * 60)
    print(f"总计：{total} | 通过：{passed} | 失败：{failed}")
    print(f"通过率：{passed/total*100:.1f}%")
    print("=" * 60)

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
