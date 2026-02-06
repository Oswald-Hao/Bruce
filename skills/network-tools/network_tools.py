#!/usr/bin/env python3
"""
网络工具集 - 核心实现
提供端口扫描、网络诊断、流量分析和网络监控能力
"""

import socket
import time
import subprocess
import json
import threading
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed


@dataclass
class PortInfo:
    """端口信息"""
    port: int
    service: str
    state: str  # open, closed, filtered
    version: Optional[str] = None


@dataclass
class ScanResult:
    """扫描结果"""
    host: str
    scanned_ports: List[int]
    open_ports: List[PortInfo]
    closed_ports: List[int]
    filtered_ports: List[int]
    scan_duration: float


@dataclass
class PingResult:
    """Ping结果"""
    host: str
    packets_sent: int
    packets_received: int
    packet_loss: float
    min_latency: float
    max_latency: float
    avg_latency: float
    jitter: float


@dataclass
class DNSRecord:
    """DNS记录"""
    record_type: str
    record_name: str
    record_value: str


@dataclass
class DNSResult:
    """DNS查询结果"""
    host: str
    records: List[DNSRecord]
    query_time: float


@dataclass
class Hop:
    """Traceroute跳点"""
    hop_number: int
    ip_address: str
    hostname: str
    latency: float


@dataclass
class TracerouteResult:
    """Traceroute结果"""
    host: str
    hops: List[Hop]
    total_duration: float


@dataclass
class HTTPTestResult:
    """HTTP测试结果"""
    url: str
    status_code: int
    response_time: float
    size: int
    headers: Dict[str, str]
    success: bool
    error: Optional[str] = None


@dataclass
class NetworkMonitorData:
    """网络监控数据"""
    bandwidth_in: float  # KB/s
    bandwidth_out: float  # KB/s
    connections: int
    active_connections: int
    duration: float


class NetworkTools:
    """网络工具集"""

    def __init__(self, timeout: int = 1):
        self.timeout = timeout
        self.common_ports = [
            21, 22, 23, 25, 53, 80, 110, 143, 443,
            445, 993, 995, 3306, 3389, 5432, 5900,
            6379, 8080, 8443, 8888, 9000, 9200, 27017
        ]

    def scan_ports(
        self,
        host: str,
        ports: Optional[List[int]] = None,
        thread_count: int = 50
    ) -> ScanResult:
        """
        扫描端口

        Args:
            host: 目标主机
            ports: 端口列表（可选，默认扫描常用端口）
            thread_count: 线程数

        Returns:
            ScanResult: 扫描结果
        """
        if ports is None:
            ports = self.common_ports

        start_time = time.time()

        open_ports = []
        closed_ports = []
        filtered_ports = []

        def check_port(port: int) -> Optional[PortInfo]:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.timeout)
                result = sock.connect_ex((host, port))

                if result == 0:
                    service = self._get_service_name(port)
                    sock.close()
                    return PortInfo(port=port, service=service, state="open")
                else:
                    sock.close()
                    return None
            except socket.timeout:
                return None
            except Exception:
                return None

        # 多线程扫描
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            future_to_port = {executor.submit(check_port, port): port for port in ports}

            for future in as_completed(future_to_port):
                port_info = future.result()
                if port_info:
                    open_ports.append(port_info)
                else:
                    closed_ports.append(future_to_port[future])

        scan_duration = time.time() - start_time

        return ScanResult(
            host=host,
            scanned_ports=ports,
            open_ports=open_ports,
            closed_ports=closed_ports,
            filtered_ports=filtered_ports,
            scan_duration=scan_duration
        )

    def scan_common_ports(self, host: str) -> ScanResult:
        """扫描常用端口"""
        return self.scan_ports(host, self.common_ports)

    def _get_service_name(self, port: int) -> str:
        """获取端口对应的服务名"""
        common_services = {
            21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp",
            53: "dns", 80: "http", 110: "pop3", 143: "imap",
            443: "https", 445: "smb", 993: "imaps", 995: "pop3s",
            3306: "mysql", 3389: "rdp", 5432: "postgresql",
            5900: "vnc", 6379: "redis", 8080: "http-alt",
            8443: "https-alt", 8888: "http-alt", 9000: "http-alt",
            9200: "elasticsearch", 27017: "mongodb"
        }
        return common_services.get(port, "unknown")

    def ping(self, host: str, count: int = 4) -> PingResult:
        """
        Ping测试

        Args:
            host: 目标主机
            count: Ping次数

        Returns:
            PingResult: Ping结果
        """
        try:
            result = subprocess.run(
                ["ping", "-c", str(count), host],
                capture_output=True,
                text=True,
                timeout=count * 2
            )

            # 解析ping结果
            output = result.stdout

            # 提取统计数据
            lines = output.split('\n')
            for line in lines:
                if 'packet loss' in line:
                    loss_str = line.split(',')[2].strip().split()[0]
                    packet_loss = float(loss_str.strip('%'))
                elif 'min/avg/max/mdev' in line or 'min/avg/max' in line:
                    stats = line.split('=')[1].strip().split()
                    min_latency = float(stats[0].split('/')[0])
                    avg_latency = float(stats[0].split('/')[1])
                    max_latency = float(stats[0].split('/')[2])

                    if len(stats) > 1:
                        jitter = float(stats[1].strip('ms()'))
                    else:
                        jitter = max_latency - min_latency

            return PingResult(
                host=host,
                packets_sent=count,
                packets_received=count - int(count * packet_loss / 100),
                packet_loss=packet_loss,
                min_latency=min_latency,
                max_latency=max_latency,
                avg_latency=avg_latency,
                jitter=jitter
            )

        except Exception as e:
            # 返回默认值
            return PingResult(
                host=host,
                packets_sent=count,
                packets_received=0,
                packet_loss=100.0,
                min_latency=0,
                max_latency=0,
                avg_latency=0,
                jitter=0
            )

    def dns_lookup(self, host: str, record_type: str = "A") -> DNSResult:
        """
        DNS查询

        Args:
            host: 域名
            record_type: 记录类型（A, AAAA, MX, NS, CNAME）

        Returns:
            DNSResult: DNS查询结果
        """
        start_time = time.time()

        try:
            result = subprocess.run(
                ["dig", host, record_type, "+short"],
                capture_output=True,
                text=True,
                timeout=5
            )

            records = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    records.append(DNSRecord(
                        record_type=record_type,
                        record_name=host,
                        record_value=line.strip()
                    ))

        except Exception as e:
            records = []

        query_time = time.time() - start_time

        return DNSResult(
            host=host,
            records=records,
            query_time=query_time
        )

    def traceroute(self, host: str, max_hops: int = 30) -> TracerouteResult:
        """
        Traceroute

        Args:
            host: 目标主机
            max_hops: 最大跳数

        Returns:
            TracerouteResult: Traceroute结果
        """
        start_time = time.time()

        try:
            result = subprocess.run(
                ["traceroute", "-n", "-m", str(max_hops), host],
                capture_output=True,
                text=True,
                timeout=60
            )

            hops = []
            lines = result.stdout.split('\n')[1:]  # 跳过第一行

            for line in lines:
                if not line.strip() or line.startswith('traceroute'):
                    continue

                parts = line.split()
                if len(parts) >= 2:
                    try:
                        hop_number = int(parts[0])
                        ip_address = parts[1]

                        # 尝试获取延迟
                        latencies = []
                        for part in parts[2:]:
                            try:
                                latency = float(part)
                                latencies.append(latency)
                            except ValueError:
                                pass

                        avg_latency = sum(latencies) / len(latencies) if latencies else 0

                        hops.append(Hop(
                            hop_number=hop_number,
                            ip_address=ip_address,
                            hostname="",
                            latency=avg_latency
                        ))
                    except (ValueError, IndexError):
                        continue

        except Exception as e:
            hops = []

        total_duration = time.time() - start_time

        return TracerouteResult(
            host=host,
            hops=hops,
            total_duration=total_duration
        )

    def http_test(self, url: str, timeout: int = 10) -> HTTPTestResult:
        """
        HTTP/HTTPS测试

        Args:
            url: 目标URL
            timeout: 超时时间

        Returns:
            HTTPTestResult: HTTP测试结果
        """
        try:
            import requests

            start_time = time.time()
            response = requests.get(url, timeout=timeout)
            response_time = (time.time() - start_time) * 1000  # 转换为毫秒

            return HTTPTestResult(
                url=url,
                status_code=response.status_code,
                response_time=response_time,
                size=len(response.content),
                headers=dict(response.headers),
                success=response.status_code < 400
            )

        except requests.exceptions.Timeout:
            return HTTPTestResult(
                url=url,
                status_code=0,
                response_time=timeout * 1000,
                size=0,
                headers={},
                success=False,
                error="Request timeout"
            )
        except Exception as e:
            return HTTPTestResult(
                url=url,
                status_code=0,
                response_time=0,
                size=0,
                headers={},
                success=False,
                error=str(e)
            )

    def batch_http_test(
        self,
        urls: List[str],
        timeout: int = 10
    ) -> List[HTTPTestResult]:
        """
        批量HTTP测试

        Args:
            urls: URL列表
            timeout: 超时时间

        Returns:
            List[HTTPTestResult]: 测试结果列表
        """
        results = []

        for url in urls:
            result = self.http_test(url, timeout)
            results.append(result)

        return results

    def start_network_monitor(
        self,
        duration: int = 60,
        interval: int = 1
    ) -> NetworkMonitorData:
        """
        启动网络监控

        Args:
            duration: 监控时长（秒）
            interval: 采样间隔（秒）

        Returns:
            NetworkMonitorData: 监控数据
        """
        # 这里简化实现，实际应该使用psutil监控网络
        try:
            import psutil

            initial_stats = psutil.net_io_counters()
            time.sleep(duration)
            final_stats = psutil.net_io_counters()

            # 计算带宽
            bytes_sent = final_stats.bytes_sent - initial_stats.bytes_sent
            bytes_recv = final_stats.bytes_recv - initial_stats.bytes_recv

            bandwidth_out = (bytes_sent / duration) / 1024  # KB/s
            bandwidth_in = (bytes_recv / duration) / 1024  # KB/s

            # 获取连接数
            connections = len(psutil.net_connections())
            active_connections = sum(
                1 for conn in psutil.net_connections()
                if conn.status == 'ESTABLISHED'
            )

            return NetworkMonitorData(
                bandwidth_in=bandwidth_in,
                bandwidth_out=bandwidth_out,
                connections=connections,
                active_connections=active_connections,
                duration=duration
            )

        except Exception as e:
            return NetworkMonitorData(
                bandwidth_in=0,
                bandwidth_out=0,
                connections=0,
                active_connections=0,
                duration=duration
            )

    def test_throughput(
        self,
        host: str,
        port: int = 80,
        duration: int = 10
    ) -> float:
        """
        测试网络吞吐量

        Args:
            host: 目标主机
            port: 端口
            duration: 测试时长

        Returns:
            float: 吞吐量（KB/s）
        """
        try:
            import requests

            # 创建测试数据
            data = b"0" * 1024 * 100  # 100KB数据

            start_time = time.time()
            total_bytes = 0

            # 持续发送数据
            while time.time() - start_time < duration:
                try:
                    response = requests.post(
                        f"http://{host}:{port}",
                        data=data,
                        timeout=5
                    )
                    total_bytes += len(data)
                except:
                    pass

            actual_duration = time.time() - start_time
            throughput = (total_bytes / actual_duration) / 1024  # KB/s

            return throughput

        except Exception as e:
            return 0.0
