#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件监听和自动推送工具
监听skills/目录的变化，自动提交并推送到GitHub
"""

import os
import time
import subprocess
from pathlib import Path

class GitAutoPusher:
    def __init__(self, watch_path="/home/lejurobot/clawd/skills"):
        self.watch_path = Path(watch_path)
        self.last_push = 0
        self.push_cooldown = 60  # 推送冷却时间（秒）

    def get_changes(self):
        """检查是否有未提交的更改"""
        try:
            # 检查未跟踪的文件
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd="/home/lejurobot/clawd"
            )
            return result.stdout.strip() != ""
        except Exception as e:
            print(f"检查Git状态失败：{e}")
            return False

    def git_add_and_commit(self, message="自动更新：文件变化"):
        """添加更改并提交"""
        try:
            # 添加所有更改
            subprocess.run(
                ["git", "add", "."],
                cwd="/home/lejurobot/clawd",
                check=True
            )

            # 提交
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd="/home/lejurobot/clawd",
                check=True
            )

            print(f"✅ 已提交：{message}")
            return True
        except subprocess.CalledProcessError as e:
            # 可能没有需要提交的更改
            print(f"⚠️  没有需要提交的更改")
            return False
        except Exception as e:
            print(f"❌ 提交失败：{e}")
            return False

    def start_watching(self, interval=30):
        """开始监听文件变化"""
        print(f"👀 开始监听文件变化：{self.watch_path}")
        print(f"🔄 检查间隔：{interval}秒")
        print("按Ctrl+C停止监听\n")

        try:
            while True:
                # 检查是否有更改
                if self.get_changes():
                    current_time = time.time()

                    # 检查冷却时间
                    if current_time - self.last_push >= self.push_cooldown:
                        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                        message = f"自动更新：{timestamp} 文件变化"

                        # 提交更改（会自动触发Git钩子推送）
                        if self.git_add_and_commit(message):
                            self.last_push = current_time
                    else:
                        remaining = int(self.push_cooldown - (current_time - self.last_push))
                        print(f"⏳ 冷却中，{remaining}秒后可推送...")

                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n👋 停止监听")

if __name__ == "__main__":
    import sys

    # 支持命令行参数指定监听路径
    watch_path = sys.argv[1] if len(sys.argv) > 1 else "/home/lejurobot/clawd"

    pusher = GitAutoPusher(watch_path)

    # 默认检查间隔30秒
    interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30

    pusher.start_watching(interval)
