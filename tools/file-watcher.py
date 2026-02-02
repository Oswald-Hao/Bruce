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

    def get_changes_summary(self):
        """获取更改的文件列表和类型"""
        try:
            # 获取git状态
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd="/home/lejurobot/clawd"
            )

            if not result.stdout.strip():
                return None

            # 解析git状态
            added = []
            modified = []
            deleted = []

            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                status, file = line[:2], line[3:]
                if 'A' in status:
                    added.append(file)
                elif 'M' in status or 'R' in status:
                    modified.append(file)
                elif 'D' in status:
                    deleted.append(file)

            return {
                'added': added,
                'modified': modified,
                'deleted': deleted
            }
        except Exception as e:
            print(f"检查Git状态失败：{e}")
            return None

    def generate_commit_message(self, changes):
        """生成智能的commit信息"""
        if not changes:
            return "自动更新：文件变化"

        message_parts = []

        # 新增文件
        if changes['added']:
            # 只取前5个文件，避免太长
            files = changes['added'][:5]
            # 简化文件路径
            files = [f.split('/')[-1] if '/' in f else f for f in files]
            if len(files) == 1:
                message_parts.append(f"新增：{files[0]}")
            else:
                message_parts.append(f"新增{len(files)}个文件")

        # 修改文件
        if changes['modified']:
            files = changes['modified'][:5]
            files = [f.split('/')[-1] if '/' in f else f for f in files]
            if len(files) == 1:
                message_parts.append(f"修改：{files[0]}")
            else:
                message_parts.append(f"修改{len(files)}个文件")

        # 删除文件
        if changes['deleted']:
            files = changes['deleted'][:5]
            files = [f.split('/')[-1] if '/' in f else f for f in files]
            if len(files) == 1:
                message_parts.append(f"删除：{files[0]}")
            else:
                message_parts.append(f"删除{len(files)}个文件")

        # 生成最终信息
        if not message_parts:
            return "自动更新：文件变化"

        return "自动更新：" + "，".join(message_parts)

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
                changes = self.get_changes_summary()
                if changes:
                    current_time = time.time()

                    # 检查冷却时间
                    if current_time - self.last_push >= self.push_cooldown:
                        # 生成智能commit信息
                        message = self.generate_commit_message(changes)

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
