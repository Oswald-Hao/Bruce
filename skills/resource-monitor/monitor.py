#!/usr/bin/env python3
"""
Resource Monitor - 系统资源监控系统
监控CPU、内存、磁盘、网络等系统资源
"""

import psutil
import time
import json
import argparse
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional


class ResourceMonitor:
    """系统资源监控器"""

    def __init__(self, config_path: str = "~/.monitor_config.json"):
        self.config_path = os.path.expanduser(config_path)
        self.config = self._load_config()
        self.history_path = os.path.expanduser(self.config.get("history", {}).get("path", "~/.monitor_history.json"))
        self.last_network = None
        self.last_network_time = None

    def _load_config(self) -> Dict:
        """加载配置文件"""
        default_config = {
            "thresholds": {
                "cpu": 80,
                "memory": 85,
                "disk": 90
            },
            "alert": {
                "enabled": False,
                "email": ""
            },
            "history": {
                "enabled": True,
                "path": "~/.monitor_history.json",
                "maxDays": 7
            }
        }

        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    default_config.update(loaded)
            except Exception:
                pass

        return default_config

    def _save_config(self):
        """保存配置文件"""
        os.makedirs(os.path.dirname(self.config_path) or ".", exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def get_cpu_info(self) -> Dict:
        """获取CPU信息"""
        cpu_times = psutil.cpu_times_percent(interval=0.1)

        # 获取负载（Linux/macOS）
        try:
            load1, load5, load15 = os.getloadavg() if hasattr(os, 'getloadavg') else (0, 0, 0)
        except OSError:
            load1 = load5 = load15 = 0

        # Top 10 CPU进程
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                proc_info = proc.info
                if proc_info['cpu_percent']:
                    processes.append(proc_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)

        return {
            "percent": psutil.cpu_percent(interval=0.1),
            "percent_per_core": psutil.cpu_percent(interval=0.1, percpu=True),
            "count_physical": psutil.cpu_count(logical=False),
            "count_logical": psutil.cpu_count(logical=True),
            "freq_current": psutil.cpu_freq().current if psutil.cpu_freq() else 0,
            "freq_max": psutil.cpu_freq().max if psutil.cpu_freq() else 0,
            "load": {
                "1min": round(load1, 2),
                "5min": round(load5, 2),
                "15min": round(load15, 2)
            },
            "top_processes": processes[:10]
        }

    def get_memory_info(self) -> Dict:
        """获取内存信息"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        # Top 10 内存进程
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
            try:
                proc_info = proc.info
                if proc_info['memory_percent']:
                    processes.append(proc_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        processes.sort(key=lambda x: x['memory_percent'] or 0, reverse=True)

        return {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "free": memory.free,
            "percent": memory.percent,
            "cached": getattr(memory, 'cached', 0),
            "buffers": getattr(memory, 'buffers', 0),
            "swap": {
                "total": swap.total,
                "used": swap.used,
                "free": swap.free,
                "percent": swap.percent
            },
            "top_processes": processes[:10]
        }

    def get_disk_info(self) -> Dict:
        """获取磁盘信息"""
        partitions = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                partitions.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent
                })
            except PermissionError:
                continue

        # 磁盘IO统计
        io = psutil.disk_io_counters()
        io_info = {
            "read_count": io.read_count if io else 0,
            "write_count": io.write_count if io else 0,
            "read_bytes": io.read_bytes if io else 0,
            "write_bytes": io.write_bytes if io else 0,
            "read_time_ms": io.read_time if io else 0,
            "write_time_ms": io.write_time if io else 0
        }

        # Top 10 IO进程（Linux）
        io_processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'io_counters']):
                try:
                    proc_info = proc.info
                    counters = proc_info.get('io_counters')
                    if counters:
                        io_total = counters.read_bytes + counters.write_bytes
                        if io_total > 0:
                            io_processes.append({
                                "pid": proc_info['pid'],
                                "name": proc_info['name'],
                                "io_bytes": io_total
                            })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except AttributeError:
            pass

        io_processes.sort(key=lambda x: x['io_bytes'], reverse=True)

        return {
            "partitions": partitions,
            "io": io_info,
            "top_io_processes": io_processes[:10]
        }

    def get_network_info(self) -> Dict:
        """获取网络信息"""
        current = psutil.net_io_counters()

        # 计算速度（需要上次数据）
        upload_speed = 0
        download_speed = 0
        if self.last_network and self.last_network_time:
            elapsed = time.time() - self.last_network_time
            if elapsed > 0:
                upload_speed = (current.bytes_sent - self.last_network.bytes_sent) / elapsed
                download_speed = (current.bytes_recv - self.last_network.bytes_recv) / elapsed

        self.last_network = current
        self.last_network_time = time.time()

        # 网络连接数
        connections = psutil.net_connections(kind='inet')
        tcp_count = len([c for c in connections if c.type == 1])
        udp_count = len([c for c in connections if c.type == 2])

        # 网络错误统计
        errors = {
            "dropin": current.dropin if hasattr(current, 'dropin') else 0,
            "dropout": current.dropout if hasattr(current, 'dropout') else 0,
            "errin": current.errin if hasattr(current, 'errin') else 0,
            "errout": current.errout if hasattr(current, 'errout') else 0
        }

        return {
            "bytes_sent": current.bytes_sent,
            "bytes_recv": current.bytes_recv,
            "packets_sent": current.packets_sent,
            "packets_recv": current.packets_recv,
            "upload_speed": upload_speed,
            "download_speed": download_speed,
            "connections": {
                "tcp": tcp_count,
                "udp": udp_count
            },
            "errors": errors
        }

    def get_all_resources(self) -> Dict[str, Any]:
        """获取所有资源信息"""
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu": self.get_cpu_info(),
            "memory": self.get_memory_info(),
            "disk": self.get_disk_info(),
            "network": self.get_network_info()
        }

    def check_thresholds(self) -> Dict[str, bool]:
        """检查资源是否超过阈值"""
        resources = self.get_all_resources()
        thresholds = self.config.get("thresholds", {})

        results = {
            "cpu": resources["cpu"]["percent"] > thresholds.get("cpu", 80),
            "memory": resources["memory"]["percent"] > thresholds.get("memory", 85),
            "disk": any(p["percent"] > thresholds.get("disk", 90) for p in resources["disk"]["partitions"])
        }

        return results

    def save_history(self, data: Dict):
        """保存历史数据"""
        if not self.config.get("history", {}).get("enabled", True):
            return

        history = {"records": []}
        if os.path.exists(self.history_path):
            try:
                with open(self.history_path, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except Exception:
                pass

        # 清理旧数据
        max_days = self.config.get("history", {}).get("maxDays", 7)
        cutoff = time.time() - max_days * 24 * 3600
        history["records"] = [
            r for r in history.get("records", [])
            if time.mktime(datetime.fromisoformat(r["timestamp"]).timetuple()) > cutoff
        ]

        # 添加新数据
        history["records"].append(data)

        # 保存
        os.makedirs(os.path.dirname(self.history_path) or ".", exist_ok=True)
        with open(self.history_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)

    def get_history(self, hours: int = 1) -> List[Dict]:
        """获取历史数据"""
        if not os.path.exists(self.history_path):
            return []

        try:
            with open(self.history_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except Exception:
            return []

        cutoff = time.time() - hours * 3600
        return [
            r for r in history.get("records", [])
            if time.mktime(datetime.fromisoformat(r["timestamp"]).timetuple()) > cutoff
        ]

    def format_output(self, data: Dict, format_type: str = "text") -> str:
        """格式化输出"""
        if format_type == "json":
            return json.dumps(data, indent=2, ensure_ascii=False)

        elif format_type == "csv":
            lines = []
            for key, value in data.items():
                if isinstance(value, (int, float)):
                    lines.append(f"{key},{value}")
                elif isinstance(value, dict):
                    for k, v in value.items():
                        if isinstance(v, (int, float)):
                            lines.append(f"{key}_{k},{v}")
            return "\n".join(lines)

        else:  # text
            lines = []
            lines.append("=" * 60)
            lines.append(f"资源监控 - {data.get('timestamp', '')}")
            lines.append("=" * 60)

            # CPU
            cpu = data.get("cpu", {})
            lines.append("\n📊 CPU")
            lines.append(f"  使用率: {cpu.get('percent', 0):.1f}%")
            lines.append(f"  物理核心: {cpu.get('count_physical', 0)}  逻辑核心: {cpu.get('count_logical', 0)}")
            if cpu.get('freq_current'):
                lines.append(f"  当前频率: {cpu['freq_current']:.0f} MHz  最高频率: {cpu['freq_max']:.0f} MHz")
            load = cpu.get('load', {})
            lines.append(f"  负载平均值: {load.get('1min', 0):.2f} / {load.get('5min', 0):.2f} / {load.get('15min', 0):.2f}")

            # 内存
            memory = data.get("memory", {})
            total_gb = memory.get('total', 0) / (1024**3)
            used_gb = memory.get('used', 0) / (1024**3)
            avail_gb = memory.get('available', 0) / (1024**3)
            lines.append(f"\n🧠 内存")
            lines.append(f"  使用率: {memory.get('percent', 0):.1f}%")
            lines.append(f"  总计: {total_gb:.2f} GB  已用: {used_gb:.2f} GB  可用: {avail_gb:.2f} GB")
            if memory.get('swap', {}).get('total', 0) > 0:
                swap = memory['swap']
                lines.append(f"  交换空间: {swap['percent']:.1f}%")

            # 磁盘
            lines.append(f"\n💾 磁盘")
            for p in data.get("disk", {}).get("partitions", []):
                total_gb = p['total'] / (1024**3)
                used_gb = p['used'] / (1024**3)
                lines.append(f"  {p['mountpoint']:15s} {p['percent']:4.0f}%  {used_gb:6.2f} GB / {total_gb:6.2f} GB")

            # 网络
            net = data.get("network", {})
            lines.append(f"\n🌐 网络")
            lines.append(f"  上传: {self._format_bytes(net['upload_speed'])}/s")
            lines.append(f"  下载: {self._format_bytes(net['download_speed'])}/s")
            lines.append(f"  连接: TCP={net.get('connections', {}).get('tcp', 0)} UDP={net.get('connections', {}).get('udp', 0)}")

            lines.append("\n" + "=" * 60)
            return "\n".join(lines)

    @staticmethod
    def _format_bytes(bytes_per_sec: float) -> str:
        """格式化字节速度"""
        if bytes_per_sec < 1024:
            return f"{bytes_per_sec:.1f} B"
        elif bytes_per_sec < 1024**2:
            return f"{bytes_per_sec/1024:.1f} KB"
        elif bytes_per_sec < 1024**3:
            return f"{bytes_per_sec/(1024**2):.1f} MB"
        else:
            return f"{bytes_per_sec/(1024**3):.2f} GB"


def main():
    parser = argparse.ArgumentParser(description="系统资源监控")
    parser.add_argument('--format', choices=['text', 'json', 'csv'], default='text', help='输出格式（用于单次监控）')
    subparsers = parser.add_subparsers(dest='command', help='命令')

    # monitor命令
    monitor_parser = subparsers.add_parser('monitor', help='持续监控')
    monitor_parser.add_argument('--interval', type=int, default=5, help='监控间隔（秒）')
    monitor_parser.add_argument('--format', choices=['text', 'json', 'csv'], default='text', help='输出格式')
    monitor_parser.add_argument('--save', action='store_true', help='保存历史数据')

    # check命令
    check_parser = subparsers.add_parser('check', help='检查资源阈值')
    check_parser.add_argument('--type', choices=['cpu', 'memory', 'disk', 'all'], default='all', help='资源类型')
    check_parser.add_argument('--threshold', type=int, help='自定义阈值')

    # history命令
    history_parser = subparsers.add_parser('history', help='查看历史数据')
    history_parser.add_argument('--hours', type=int, default=1, help='查看小时数')

    args = parser.parse_args()

    monitor = ResourceMonitor()

    if args.command == 'monitor':
        print("开始监控... 按 Ctrl+C 停止")
        try:
            while True:
                data = monitor.get_all_resources()
                print(monitor.format_output(data, args.format))
                print()  # 空行分隔

                if args.save:
                    monitor.save_history(data)

                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n监控已停止")

    elif args.command == 'check':
        if args.threshold:
            threshold_key = f"{args.type}_threshold"
            monitor.config['thresholds'][args.type] = args.threshold

        results = monitor.check_thresholds()
        print("资源阈值检查结果:")
        for key, value in results.items():
            status = "⚠️  超限" if value else "✅ 正常"
            print(f"  {key}: {status}")

    elif args.command == 'history':
        history = monitor.get_history(args.hours)
        if not history:
            print(f"过去{args.hours}小时无历史数据")
        else:
            print(f"过去{args.hours}小时的历史数据（共{len(history)}条记录）:")
            for record in history:
                timestamp = record.get('timestamp', '')
                cpu = record.get('cpu', {}).get('percent', 0)
                memory = record.get('memory', {}).get('percent', 0)
                print(f"  {timestamp}: CPU {cpu:.1f}%  内存 {memory:.1f}%")

    else:
        # 默认：单次监控
        data = monitor.get_all_resources()
        print(monitor.format_output(data, args.format))


if __name__ == "__main__":
    main()
