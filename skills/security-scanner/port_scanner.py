#!/usr/bin/env python3
"""
端口扫描工具
快速发现开放端口和服务
"""

import socket
import threading
import argparse
import json
import sys
from datetime import datetime


class PortScanner:
    """端口扫描器"""

    def __init__(self, target, ports="1-1024", timeout=1, threads=100):
        """
        初始化扫描器

        Args:
            target: 目标IP或域名
            ports: 端口范围
            timeout: 超时时间（秒）
            threads: 线程数
        """
        self.target = target
        self.timeout = timeout
        self.threads = threads
        self.open_ports = []
        self.lock = threading.Lock()
        self._parse_ports(ports)

    def _parse_ports(self, ports):
        """解析端口范围"""
        if isinstance(ports, str):
            if '-' in ports:
                start, end = map(int, ports.split('-'))
                self.port_range = range(start, end + 1)
            elif ',' in ports:
                self.port_range = [int(p) for p in ports.split(',')]
            else:
                self.port_range = [int(ports)]
        else:
            self.port_range = ports

    def scan_port(self, port):
        """
        扫描单个端口

        Args:
            port: 端口号
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.target, port))

            if result == 0:
                try:
                    service = socket.getservbyport(port)
                except:
                    service = "unknown"

                with self.lock:
                    self.open_ports.append({
                        "port": port,
                        "service": service,
                        "status": "open"
                    })

            sock.close()

        except:
            pass

    def scan(self):
        """执行扫描"""
        print(f"\n正在扫描 {self.target}...")
        print(f"端口范围: {min(self.port_range)}-{max(self.port_range)}")
        print(f"线程数: {self.threads}")
        print(f"超时: {self.timeout}秒\n")

        start_time = datetime.now()

        # 创建线程
        threads = []
        for port in self.port_range:
            t = threading.Thread(target=self.scan_port, args=(port,))
            threads.append(t)

            # 控制并发数
            if len(threads) >= self.threads:
                for thread in threads:
                    thread.start()
                for thread in threads:
                    thread.join()
                threads = []

        # 处理剩余线程
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print(f"\n扫描完成！用时: {duration:.2f}秒")

        return self.open_ports

    def print_results(self):
        """打印结果"""
        if not self.open_ports:
            print("\n未发现开放端口")
            return

        print(f"\n发现 {len(self.open_ports)} 个开放端口:")
        print("=" * 60)
        print(f"{'端口':<10} {'服务':<20} {'状态':<10}")
        print("-" * 60)

        for port_info in sorted(self.open_ports, key=lambda x: x["port"]):
            print(f"{port_info['port']:<10} {port_info['service']:<20} {port_info['status']:<10}")

    def save_results(self, output_file, format="json"):
        """
        保存结果

        Args:
            output_file: 输出文件
            format: 格式（json/txt）
        """
        results = {
            "target": self.target,
            "scan_time": datetime.now().isoformat(),
            "open_ports": self.open_ports,
            "total_open": len(self.open_ports)
        }

        if format == "json":
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
        else:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"端口扫描结果\n")
                f.write(f"目标: {self.target}\n")
                f.write(f"扫描时间: {datetime.now()}\n")
                f.write(f"\n开放端口:\n")
                for port_info in sorted(self.open_ports, key=lambda x: x["port"]):
                    f.write(f"  {port_info['port']}: {port_info['service']}\n")

        print(f"\n结果已保存到: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="端口扫描工具")
    parser.add_argument("--target", required=True, help="目标IP或域名")
    parser.add_argument("--ports", default="1-1024", help="端口范围（默认1-1024）")
    parser.add_argument("--timeout", type=int, default=1, help="超时时间（秒）")
    parser.add_argument("--threads", type=int, default=100, help="线程数")
    parser.add_argument("--output", help="输出文件")
    parser.add_argument("--format", default="json", choices=["json", "txt"], help="输出格式")

    args = parser.parse_args()

    # 解析目标
    try:
        target = socket.gethostbyname(args.target)
    except socket.gaierror:
        print(f"错误: 无法解析目标 {args.target}")
        sys.exit(1)

    # 创建扫描器
    scanner = PortScanner(
        target=target,
        ports=args.ports,
        timeout=args.timeout,
        threads=args.threads
    )

    # 执行扫描
    scanner.scan()

    # 打印结果
    scanner.print_results()

    # 保存结果
    if args.output:
        scanner.save_results(args.output, format=args.format)


if __name__ == "__main__":
    main()
