#!/usr/bin/env python3
"""
测试安全扫描技能
"""

import os
import sys
import tempfile
import json
import socket

# 添加技能路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_port_scanner_init():
    """测试1: 端口扫描器初始化"""
    print("\n测试1: 端口扫描器初始化")

    try:
        from port_scanner import PortScanner

        # 使用localhost测试
        scanner = PortScanner(target="127.0.0.1", ports="80,443,8080")
        assert scanner.target == "127.0.0.1", "目标设置错误"
        assert len(scanner.port_range) == 3, "端口数量错误"
        print("  ✓ 端口扫描器初始化")

        return True

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_port_range_parsing():
    """测试2: 端口范围解析"""
    print("\n测试2: 端口范围解析")

    try:
        from port_scanner import PortScanner

        # 测试范围
        scanner1 = PortScanner(target="127.0.0.1", ports="1-10")
        assert len(scanner1.port_range) == 10, "范围解析错误"
        print("  ✓ 范围解析")

        # 测试列表
        scanner2 = PortScanner(target="127.0.0.1", ports="80,443,8080")
        assert 80 in scanner2.port_range, "列表解析错误"
        assert 443 in scanner2.port_range, "列表解析错误"
        assert 8080 in scanner2.port_range, "列表解析错误"
        print("  ✓ 列表解析")

        return True

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vuln_scanner_init():
    """测试3: 漏洞扫描器初始化"""
    print("\n测试3: 漏洞扫描器初始化")

    try:
        from vuln_scanner import VulnScanner

        scanner = VulnScanner(target="192.168.1.1")
        assert scanner.target == "192.168.1.1", "目标设置错误"
        assert len(scanner.vulnerabilities) == 0, "初始化漏洞列表应为空"
        print("  ✓ 漏洞扫描器初始化")

        return True

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_common_vuln_detection():
    """测试4: 常见漏洞检测"""
    print("\n测试4: 常见漏洞检测")

    try:
        from vuln_scanner import VulnScanner

        scanner = VulnScanner(target="test")

        # 模拟开放端口（包含SSH和MySQL）
        open_ports = [
            {"port": 22, "service": "ssh"},
            {"port": 80, "service": "http"},
            {"port": 3306, "service": "mysql"}
        ]

        # 检测漏洞
        scanner.check_common_vulns(open_ports)

        # 验证
        assert len(scanner.vulnerabilities) > 0, "应该检测到漏洞"
        print(f"  ✓ 检测到 {len(scanner.vulnerabilities)} 个潜在漏洞")

        # 检查具体漏洞
        vuln_names = [v["name"] for v in scanner.vulnerabilities]
        assert "SSH weak authentication" in vuln_names, "应该检测到SSH漏洞"
        assert "MySQL default credentials" in vuln_names, "应该检测到MySQL漏洞"
        print("  ✓ 特定漏洞检测")

        return True

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_save_results():
    """测试5: 结果保存"""
    print("\n测试5: 结果保存")

    try:
        from port_scanner import PortScanner

        scanner = PortScanner(target="127.0.0.1", ports="80")
        scanner.open_ports = [
            {"port": 80, "service": "http", "status": "open"}
        ]

        # 测试JSON格式
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            json_path = f.name

        scanner.save_results(json_path, format="json")
        assert os.path.exists(json_path), "JSON文件未创建"

        # 验证JSON格式
        with open(json_path, "r") as f:
            data = json.load(f)
            assert "target" in data, "JSON缺少target字段"
            assert "open_ports" in data, "JSON缺少open_ports字段"

        os.remove(json_path)
        print("  ✓ JSON格式保存")

        # 测试TXT格式
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            txt_path = f.name

        scanner.save_results(txt_path, format="txt")
        assert os.path.exists(txt_path), "TXT文件未创建"
        os.remove(txt_path)
        print("  ✓ TXT格式保存")

        return True

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vuln_scanner_save():
    """测试6: 漏洞扫描器结果保存"""
    print("\n测试6: 漏洞扫描器结果保存")

    try:
        from vuln_scanner import VulnScanner

        scanner = VulnScanner(target="test")
        scanner.vulnerabilities = [
            {
                "name": "Test Vuln",
                "port": 80,
                "description": "Test",
                "severity": "high"
            }
        ]

        # 测试JSON格式
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            json_path = f.name

        scanner.save_results(json_path, format="json")
        assert os.path.exists(json_path), "JSON文件未创建"

        with open(json_path, "r") as f:
            data = json.load(f)
            assert "vulnerabilities" in data, "JSON缺少vulnerabilities字段"
            assert "by_severity" in data, "JSON缺少by_severity字段"

        os.remove(json_path)
        print("  ✓ JSON格式保存")

        # 测试HTML格式
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            html_path = f.name

        scanner.save_results(html_path, format="html")
        assert os.path.exists(html_path), "HTML文件未创建"

        with open(html_path, "r") as f:
            html_content = f.read()
            assert "<html>" in html_content, "HTML格式错误"
            assert "漏洞扫描报告" in html_content, "HTML缺少标题"

        os.remove(html_path)
        print("  ✓ HTML格式保存")

        return True

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_structure():
    """测试7: API结构完整性"""
    print("\n测试7: API结构完整性")

    try:
        from port_scanner import PortScanner
        from vuln_scanner import VulnScanner
        import inspect

        # 检查PortScanner类
        members_scanner = [name for name in dir(PortScanner) if not name.startswith('_') or name == '__init__']
        assert "scan" in members_scanner, "PortScanner缺少scan方法"
        assert "print_results" in members_scanner, "PortScanner缺少print_results方法"
        assert "save_results" in members_scanner, "PortScanner缺少save_results方法"
        print("  ✓ PortScanner API完整")

        # 检查VulnScanner类
        members_vuln = [name for name in dir(VulnScanner) if not name.startswith('_')]
        assert "scan" in members_vuln, "VulnScanner缺少scan方法"
        assert "check_common_vulns" in members_vuln, "VulnScanner缺少check_common_vulns方法"
        print("  ✓ VulnScanner API完整")

        print("  ✓ API结构测试通过")
        return True

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_import():
    """测试0: 模块导入"""
    print("\n测试0: 模块导入")

    try:
        from port_scanner import PortScanner
        from vuln_scanner import VulnScanner
        print("  ✓ 端口扫描模块导入成功")
        print("  ✓ 漏洞扫描模块导入成功")
        return True
    except Exception as e:
        print(f"  ✗ 导入失败: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("安全扫描技能测试")
    print("=" * 60)
    print("注意: 使用本地测试，不扫描外部网络\n")

    tests = [
        test_import,
        test_port_scanner_init,
        test_port_range_parsing,
        test_vuln_scanner_init,
        test_common_vuln_detection,
        test_save_results,
        test_vuln_scanner_save,
        test_api_structure
    ]

    results = []

    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ✗ 测试异常: {e}")
            results.append(False)

    # 汇总
    print("\n" + "=" * 60)
    print("测试汇总")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total}")

    if passed == total:
        print("\n✓ 所有测试通过！")
        return 0
    else:
        print(f"\n✗ {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
