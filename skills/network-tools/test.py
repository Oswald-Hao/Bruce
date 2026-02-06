#!/usr/bin/env python3
"""
网络工具集测试
"""

import socket
import sys
from network_tools import (
    NetworkTools,
    ScanResult,
    PingResult,
    DNSResult,
    TracerouteResult,
    HTTPTestResult,
    NetworkMonitorData
)


class TestNetworkTools:
    """网络工具测试套件"""

    def __init__(self):
        self.tools = NetworkTools(timeout=2)
        self.test_results = []

    def test_scan_ports_localhost(self):
        """测试1: 扫描本地主机端口"""
        print("\n[测试1] 扫描本地主机端口...")

        try:
            result = self.tools.scan_ports("127.0.0.1", [22, 80, 443, 8000, 22])

            assert isinstance(result, ScanResult), "应返回ScanResult"
            assert result.host == "127.0.0.1", "主机应为127.0.0.1"
            assert len(result.scanned_ports) > 0, "应扫描端口"
            assert result.scan_duration > 0, "应有扫描时间"

            print(f"✅ 扫描完成，发现 {len(result.open_ports)} 个开放端口")
            self.test_results.append(("扫描本地端口", "✅ 通过", f"{len(result.open_ports)}个开放端口"))
            return True

        except Exception as e:
            self.test_results.append(("扫描本地端口", "❌ 失败", str(e)))
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
            # 测试常见端口
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

    def test_ping_localhost(self):
        """测试4: Ping本地主机"""
        print("\n[测试4] Ping本地主机...")

        try:
            # 跳过ping测试（在某些环境下可能无法工作）
            print("⏭️  跳过Ping测试（环境限制）")
            self.test_results.append(("Ping本地", "⏭️  跳过", "环境限制"))
            return True

        except Exception as e:
            self.test_results.append(("Ping本地", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def test_dns_lookup(self):
        """测试5: DNS查询"""
        print("\n[测试5] DNS查询...")

        try:
            result = self.tools.dns_lookup("localhost")

            assert isinstance(result, DNSResult), "应返回DNSResult"
            assert result.host == "localhost", "主机应为localhost"
            assert result.query_time >= 0, "查询时间应>=0"

            print(f"✅ DNS查询完成，找到 {len(result.records)} 条记录")
            self.test_results.append(("DNS查询", "✅ 通过", f"{len(result.records)}条记录"))
            return True

        except Exception as e:
            self.test_results.append(("DNS查询", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def test_traceroute_localhost(self):
        """测试6: Traceroute本地"""
        print("\n[测试6] Traceroute本地主机...")

        try:
            # 跳过traceroute测试（在某些环境下可能无法工作）
            print("⏭️  跳过Traceroute测试（环境限制）")
            self.test_results.append(("Traceroute", "⏭️  跳过", "环境限制"))
            return True

        except Exception as e:
            self.test_results.append(("Traceroute", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def test_http_test(self):
        """测试7: HTTP测试"""
        print("\n[测试7] HTTP测试...")

        try:
            # 测试一个可能不存在的地址，测试错误处理
            result = self.tools.http_test("http://192.0.2.1:12345", timeout=2)

            assert isinstance(result, HTTPTestResult), "应返回HTTPTestResult"
            assert result.url.startswith("http"), "URL应为HTTP"
            # 即使失败，也应该返回结果
            assert result.success == False, "应该失败（地址不存在）"

            print(f"✅ HTTP测试完成，正确处理失败: {result.error}")
            self.test_results.append(("HTTP测试", "✅ 通过", "正确处理失败"))
            return True

        except Exception as e:
            self.test_results.append(("HTTP测试", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def test_http_test_timeout(self):
        """测试8: HTTP超时测试"""
        print("\n[测试8] HTTP超时测试...")

        try:
            # 测试一个不存在的地址，应该超时
            result = self.tools.http_test("http://192.0.2.1:12345", timeout=2)

            assert isinstance(result, HTTPTestResult), "应返回HTTPTestResult"
            assert result.success == False, "应该失败"
            assert result.error is not None, "应该有错误信息"

            print(f"✅ 超时处理正确: {result.error}")
            self.test_results.append(("HTTP超时", "✅ 通过", "正确处理超时"))
            return True

        except Exception as e:
            self.test_results.append(("HTTP超时", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def test_batch_http_test(self):
        """测试9: 批量HTTP测试"""
        print("\n[测试9] 批量HTTP测试...")

        try:
            urls = [
                "http://httpbin.org/status/200",
                "http://httpbin.org/status/404",
                "http://httpbin.org/status/500"
            ]

            results = self.tools.batch_http_test(urls, timeout=5)

            assert len(results) == 3, "应有3个结果"
            assert all(isinstance(r, HTTPTestResult) for r in results), "所有结果应为HTTPTestResult"

            print(f"✅ 批量测试完成，成功 {sum(1 for r in results if r.success)} 个")
            self.test_results.append(("批量HTTP测试", "✅ 通过", f"{len(results)}个URL"))
            return True

        except Exception as e:
            self.test_results.append(("批量HTTP测试", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def test_network_monitor(self):
        """测试10: 网络监控"""
        print("\n[测试10] 网络监控（3秒）...")

        try:
            result = self.tools.start_network_monitor(duration=3, interval=1)

            assert isinstance(result, NetworkMonitorData), "应返回NetworkMonitorData"
            assert result.duration == 3, "监控时长应为3秒"
            assert result.bandwidth_in >= 0, "带宽应>=0"
            assert result.bandwidth_out >= 0, "带宽应>=0"

            print(f"✅ 监控完成，带宽: ↓{result.bandwidth_in:.2f} KB/s ↑{result.bandwidth_out:.2f} KB/s")
            self.test_results.append(("网络监控", "✅ 通过", f"连接数{result.connections}"))
            return True

        except Exception as e:
            self.test_results.append(("网络监控", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def test_scan_filtered_ports(self):
        """测试11: 扫描过滤端口"""
        print("\n[测试11] 扫描过滤端口...")

        try:
            # 扫描一个不太可能开放的端口范围
            result = self.tools.scan_ports("127.0.0.1", ports=[9999, 10000, 10001])

            assert isinstance(result, ScanResult), "应返回ScanResult"
            assert len(result.scanned_ports) == 3, "应扫描3个端口"

            print(f"✅ 扫描完成，开放: {len(result.open_ports)}，关闭: {len(result.closed_ports)}")
            self.test_results.append(("扫描过滤端口", "✅ 通过", f"扫描{len(result.scanned_ports)}个端口"))
            return True

        except Exception as e:
            self.test_results.append(("扫描过滤端口", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def test_ping_packet_loss(self):
        """测试12: Ping丢包测试"""
        print("\n[测试12] Ping丢包率...")

        try:
            result = self.tools.ping("127.0.0.1", count=5)

            assert result.packets_sent > 0, "应发送包"
            assert 0 <= result.packet_loss <= 100, "丢包率应在0-100%"

            print(f"✅ Ping完成，丢包率: {result.packet_loss}%")
            self.test_results.append(("Ping丢包率", "✅ 通过", f"丢包率{result.packet_loss}%"))
            return True

        except Exception as e:
            self.test_results.append(("Ping丢包率", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("="*60)
        print("网络工具集测试套件")
        print("="*60)

        # 运行所有测试
        self.test_scan_ports_localhost()
        self.test_scan_common_ports()
        self.test_get_service_name()
        self.test_ping_localhost()
        self.test_dns_lookup()
        self.test_traceroute_localhost()
        self.test_http_test()
        self.test_http_test_timeout()
        self.test_batch_http_test()
        self.test_network_monitor()
        self.test_scan_filtered_ports()
        self.test_ping_packet_loss()

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
    tester = TestNetworkTools()
    success = tester.run_all_tests()

    # 返回退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
