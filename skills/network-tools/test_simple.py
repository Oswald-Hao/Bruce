#!/usr/bin/env python3
"""
网络工具集测试 - 简化版
"""

import sys
from network_tools import (
    NetworkTools,
    ScanResult,
    HTTPTestResult,
    NetworkMonitorData
)


class TestNetworkToolsSimple:
    """网络工具测试套件 - 简化版"""

    def __init__(self):
        self.tools = NetworkTools(timeout=1)
        self.test_results = []

    def test_scan_ports(self):
        """测试1: 扫描端口"""
        print("\n[测试1] 扫描端口...")

        try:
            result = self.tools.scan_ports("127.0.0.1", ports=[22, 80, 8000, 9999])

            assert isinstance(result, ScanResult), "应返回ScanResult"
            assert result.host == "127.0.0.1", "主机应为127.0.0.1"
            assert len(result.scanned_ports) == 4, "应扫描4个端口"

            print(f"✅ 扫描完成，发现 {len(result.open_ports)} 个开放端口")
            self.test_results.append(("扫描端口", "✅ 通过", f"{len(result.open_ports)}个开放端口"))
            return True

        except Exception as e:
            self.test_results.append(("扫描端口", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def test_scan_common_ports(self):
        """测试2: 扫描常用端口"""
        print("\n[测试2] 扫描常用端口...")

        try:
            result = self.tools.scan_common_ports("127.0.0.1")

            assert len(result.scanned_ports) > 0, "应扫描常用端口"
            assert result.scan_duration > 0, "应有扫描时间"

            print(f"✅ 扫描了 {len(result.scanned_ports)} 个常用端口")
            self.test_results.append(("扫描常用端口", "✅ 通过", f"{len(result.scanned_ports)}个端口"))
            return True

        except Exception as e:
            self.test_results.append(("扫描常用端口", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def test_get_service_name(self):
        """测试3: 获取服务名"""
        print("\n[测试3] 获取服务名...")

        try:
            assert self.tools._get_service_name(80) == "http", "80应为http"
            assert self.tools._get_service_name(443) == "https", "443应为https"
            assert self.tools._get_service_name(22) == "ssh", "22应为ssh"

            print("✅ 服务名映射正确")
            self.test_results.append(("获取服务名", "✅ 通过", "映射正确"))
            return True

        except Exception as e:
            self.test_results.append(("获取服务名", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def test_http_test(self):
        """测试4: HTTP测试（失败处理）"""
        print("\n[测试4] HTTP测试...")

        try:
            result = self.tools.http_test("http://192.0.2.1:12345", timeout=1)

            assert isinstance(result, HTTPTestResult), "应返回HTTPTestResult"
            assert result.success == False, "应该失败（地址不存在）"

            print(f"✅ HTTP测试完成，正确处理失败: {result.error}")
            self.test_results.append(("HTTP测试", "✅ 通过", "正确处理失败"))
            return True

        except Exception as e:
            self.test_results.append(("HTTP测试", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def test_network_monitor(self):
        """测试5: 网络监控（3秒）"""
        print("\n[测试5] 网络监控（3秒）...")

        try:
            result = self.tools.start_network_monitor(duration=3, interval=1)

            assert isinstance(result, NetworkMonitorData), "应返回NetworkMonitorData"
            assert result.duration == 3, "监控时长应为3秒"

            print(f"✅ 监控完成，连接数: {result.connections}")
            self.test_results.append(("网络监控", "✅ 通过", f"连接数{result.connections}"))
            return True

        except Exception as e:
            self.test_results.append(("网络监控", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def test_dns_lookup(self):
        """测试6: DNS查询"""
        print("\n[测试6] DNS查询...")

        try:
            result = self.tools.dns_lookup("localhost")

            assert result.host == "localhost", "主机应为localhost"
            assert result.query_time >= 0, "查询时间应>=0"

            print(f"✅ DNS查询完成")
            self.test_results.append(("DNS查询", "✅ 通过", f"{len(result.records)}条记录"))
            return True

        except Exception as e:
            self.test_results.append(("DNS查询", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("="*60)
        print("网络工具集测试套件（简化版）")
        print("="*60)

        # 运行所有测试
        self.test_scan_ports()
        self.test_scan_common_ports()
        self.test_get_service_name()
        self.test_http_test()
        self.test_network_monitor()
        self.test_dns_lookup()

        # 打印结果汇总
        print("\n" + "="*60)
        print("测试结果汇总")
        print("="*60)

        passed = sum(1 for _, status, _ in self.test_results if "✅" in status)
        total = len(self.test_results)

        for test_name, status, detail in self.test_results:
            print(f"{status} {test_name}: {detail}")

        print("\n" + "="*60)
        print(f"通过: {passed}/{total}")
        print("="*60)

        if passed == total:
            print("\n🎉 所有测试通过！")
            return True
        else:
            print(f"\n⚠️ {total - passed} 个测试失败")
            return False


def main():
    """主函数"""
    tester = TestNetworkToolsSimple()
    success = tester.run_all_tests()

    # 返回退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
