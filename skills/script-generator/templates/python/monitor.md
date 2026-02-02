#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Description: 监控指定进程的CPU和内存使用率，超过阈值时记录日志
"""
自动生成的Python脚本 - 监控脚本
生成时间: {{timestamp}}
需求: {{prompt}}
"""

import psutil
import time
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from pathlib import Path
import argparse


class ProcessMonitor:
    """进程监控器"""

    def __init__(self, process_name: str, cpu_threshold: float = 80.0,
                 memory_threshold: float = 80.0, interval: int = 60,
                 log_file: str = "/var/log/monitor.log"):
        self.process_name = process_name
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.interval = interval
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def find_process(self):
        """查找进程"""
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            if self.process_name.lower() in proc.info['name'].lower():
                return proc
        return None

    def log(self, message: str, level: str = "INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}\n"

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_line)

        print(log_line.strip())

    def check(self):
        """检查进程状态"""
        proc = self.find_process()

        if proc is None:
            self.log(f"进程 {self.process_name} 未运行", "WARNING")
            return

        try:
            cpu = proc.cpu_percent(interval=1)
            memory = proc.memory_percent()

            self.log(f"{self.process_name} (PID: {proc.pid}) CPU: {cpu:.1f}% MEM: {memory:.1f}%")

            # CPU告警
            if cpu > self.cpu_threshold:
                self.log(f"⚠️ CPU告警: {cpu:.1f}% > {self.cpu_threshold}%", "WARNING")

            # 内存告警
            if memory > self.memory_threshold:
                self.log(f"⚠️ 内存告警: {memory:.1f}% > {self.memory_threshold}%", "WARNING")

        except psutil.NoSuchProcess:
            self.log(f"进程 {self.process_name} 已停止", "INFO")

    def run(self):
        """持续监控"""
        self.log(f"开始监控进程: {self.process_name}")
        self.log(f"CPU阈值: {self.cpu_threshold}%, 内存阈值: {self.memory_threshold}%")

        try:
            while True:
                self.check()
                time.sleep(self.interval)
        except KeyboardInterrupt:
            self.log("监控已停止", "INFO")


def main():
    parser = argparse.ArgumentParser(description="进程监控脚本")
    parser.add_argument("--process", default="python", help="监控的进程名")
    parser.add_argument("--cpu-threshold", type=float, default=80.0, help="CPU阈值(%)")
    parser.add_argument("--memory-threshold", type=float, default=80.0, help="内存阈值(%)")
    parser.add_argument("--interval", type=int, default=60, help="检查间隔(秒)")
    parser.add_argument("--log", default="/var/log/monitor.log", help="日志文件")

    args = parser.parse_args()

    monitor = ProcessMonitor(
        args.process,
        args.cpu_threshold,
        args.memory_threshold,
        args.interval,
        args.log
    )

    monitor.run()


if __name__ == "__main__":
    main()
