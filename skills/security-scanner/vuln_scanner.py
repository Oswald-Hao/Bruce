#!/usr/bin/env python3
"""
漏洞扫描工具
检测常见安全漏洞
"""

import argparse
import json
import sys
from datetime import datetime


class VulnScanner:
    """漏洞扫描器"""

    # 常见漏洞特征
    COMMON_VULNS = {
        "SSH weak authentication": {
            "port": 22,
            "description": "SSH弱认证风险",
            "severity": "medium"
        },
        "HTTP outdated version": {
            "port": 80,
            "description": "HTTP服务版本过旧",
            "severity": "low"
        },
        "FTP anonymous login": {
            "port": 21,
            "description": "FTP允许匿名登录",
            "severity": "high"
        },
        "Telnet insecure protocol": {
            "port": 23,
            "description": "Telnet是不安全协议",
            "severity": "high"
        },
        "SMTP open relay": {
            "port": 25,
            "description": "SMTP可能开放中继",
            "severity": "medium"
        },
        "DNS recursion": {
            "port": 53,
            "description": "DNS可能允许递归查询",
            "severity": "medium"
        },
        "MySQL default credentials": {
            "port": 3306,
            "description": "MySQL可能使用默认凭证",
            "severity": "high"
        },
        "RDP vulnerable": {
            "port": 3389,
            "description": "RDP服务可能存在漏洞",
            "severity": "high"
        }
    }

    def __init__(self, target):
        """
        初始化扫描器

        Args:
            target: 目标IP
        """
        self.target = target
        self.vulnerabilities = []

    def check_common_vulns(self, open_ports):
        """
        检查常见漏洞

        Args:
            open_ports: 开放端口列表
        """
        open_port_nums = {p["port"] for p in open_ports}

        for vuln_name, vuln_info in self.COMMON_VULNS.items():
            if vuln_info["port"] in open_port_nums:
                self.vulnerabilities.append({
                    "name": vuln_name,
                    "port": vuln_info["port"],
                    "description": vuln_info["description"],
                    "severity": vuln_info["severity"]
                })

    def scan(self, open_ports):
        """
        执行扫描

        Args:
            open_ports: 开放端口列表
        """
        print("\n正在检测常见漏洞...")
        self.check_common_vulns(open_ports)
        print(f"检测完成！发现 {len(self.vulnerabilities)} 个潜在漏洞")
        return self.vulnerabilities

    def print_results(self):
        """打印结果"""
        if not self.vulnerabilities:
            print("\n未发现常见漏洞")
            return

        print(f"\n发现 {len(self.vulnerabilities)} 个潜在漏洞:")
        print("=" * 80)
        print(f"{'漏洞名称':<30} {'端口':<10} {'严重性':<10} {'描述':<20}")
        print("-" * 80)

        for vuln in self.vulnerabilities:
            severity_color = {
                "high": "⚠️ ",
                "medium": "⚡ ",
                "low": "ℹ️ "
            }.get(vuln["severity"], "")

            print(f"{severity_color}{vuln['name']:<30} {vuln['port']:<10} {vuln['severity']:<10} {vuln['description']:<20}")

    def save_results(self, output_file, format="json"):
        """
        保存结果

        Args:
            output_file: 输出文件
            format: 格式（json/html）
        """
        results = {
            "target": self.target,
            "scan_time": datetime.now().isoformat(),
            "vulnerabilities": self.vulnerabilities,
            "total": len(self.vulnerabilities),
            "by_severity": {
                "high": len([v for v in self.vulnerabilities if v["severity"] == "high"]),
                "medium": len([v for v in self.vulnerabilities if v["severity"] == "medium"]),
                "low": len([v for v in self.vulnerabilities if v["severity"] == "low"])
            }
        }

        if format == "json":
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
        elif format == "html":
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("<!DOCTYPE html>\n")
                f.write("<html>\n<head><title>漏洞扫描报告</title></head>\n<body>\n")
                f.write(f"<h1>漏洞扫描报告</h1>\n")
                f.write(f"<p>目标: {self.target}</p>\n")
                f.write(f"<p>扫描时间: {datetime.now()}</p>\n")
                f.write(f"<h2>漏洞列表</h2>\n")
                f.write("<table border='1'>\n")
                f.write("<tr><th>漏洞名称</th><th>端口</th><th>严重性</th><th>描述</th></tr>\n")
                for vuln in self.vulnerabilities:
                    f.write(f"<tr><td>{vuln['name']}</td><td>{vuln['port']}</td>")
                    f.write(f"<td>{vuln['severity']}</td><td>{vuln['description']}</td></tr>\n")
                f.write("</table>\n</body>\n</html>")

        print(f"\n报告已保存到: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="漏洞扫描工具")
    parser.add_argument("--target", required=True, help="目标IP")
    parser.add_argument("--open-ports", help="开放端口列表（JSON文件）")
    parser.add_argument("--scan-type", default="basic", choices=["basic", "full"], help="扫描类型")
    parser.add_argument("--output", help="输出文件")
    parser.add_argument("--format", default="json", choices=["json", "html"], help="输出格式")

    args = parser.parse_args()

    # 创建扫描器
    scanner = VulnScanner(target=args.target)

    # 加载开放端口
    if args.open_ports:
        with open(args.open_ports, "r") as f:
            open_ports = json.load(f)["open_ports"]
    else:
        # 模拟一些开放端口用于测试
        print("未指定开放端口，使用模拟数据")
        open_ports = [
            {"port": 22, "service": "ssh"},
            {"port": 80, "service": "http"},
            {"port": 3306, "service": "mysql"}
        ]

    # 执行扫描
    scanner.scan(open_ports)

    # 打印结果
    scanner.print_results()

    # 保存结果
    if args.output:
        scanner.save_results(args.output, format=args.format)


if __name__ == "__main__":
    main()
