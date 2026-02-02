#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moltbot 配置监听器
监听 Moltbot 的配置文件变化，同步到 Bruce 仓库
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

class MoltbotWatcher:
    def __init__(self):
        self.moltbot_config_dir = Path("/home/lejurobot/.moltbot")
        self.bruce_config_dir = Path("/home/lejurobot/clawd/moltbot-config")
        self.last_sync_time = 0
        self.sync_cooldown = 60  # 同步冷却时间（秒）

        # 需要监听的文件（相对路径）
        self.watch_files = [
            "moltbot.json",
            "feishu/dedup-cache.json",
            "cron/jobs.json",
        ]

    def get_file_hash(self, file_path):
        """获取文件的哈希值（用于检测变化）"""
        try:
            if not file_path.exists():
                return None
            mtime = os.path.getmtime(file_path)
            size = os.path.getsize(file_path)
            return f"{mtime}:{size}"
        except Exception:
            return None

    def check_changes(self):
        """检查文件是否有变化"""
        changes = []
        current_time = time.time()

        # 检查冷却时间
        if current_time - self.last_sync_time < self.sync_cooldown:
            return None

        for rel_path in self.watch_files:
            source_file = self.moltbot_config_dir / rel_path
            target_file = self.bruce_config_dir / rel_path

            # 确保目标目录存在
            target_file.parent.mkdir(parents=True, exist_ok=True)

            source_hash = self.get_file_hash(source_file)
            target_hash = self.get_file_hash(target_file)

            # 如果文件有变化，或者目标文件不存在
            if source_hash and source_hash != target_hash:
                changes.append({
                    'rel_path': rel_path,
                    'source': source_file,
                    'target': target_file
                })

        return changes if changes else None

    def sync_file(self, change):
        """同步单个文件"""
        try:
            import shutil
            shutil.copy2(change['source'], change['target'])
            print(f"✅ 同步文件：{change['rel_path']}")
            return True
        except Exception as e:
            print(f"❌ 同步失败 {change['rel_path']}：{e}")
            return False

    def commit_changes(self, changes):
        """提交更改到 Bruce 仓库"""
        try:
            # 进入 Bruce 仓库目录
            os.chdir("/home/lejurobot/clawd")

            # 添加更改的文件
            for change in changes:
                target_file = change['target']
                subprocess.run(["git", "add", str(target_file)], check=True)

            # 生成 commit 信息
            file_names = [change['rel_path'] for change in changes]
            if len(file_names) == 1:
                message = f"同步 Moltbot 配置：{file_names[0]}"
            else:
                message = f"同步 Moltbot 配置：{len(file_names)} 个文件"

            # 提交（会自动触发 Git 钩子推送）
            subprocess.run(["git", "commit", "-m", message], check=True)

            print(f"📦 已提交：{message}")
            self.last_sync_time = time.time()
            return True
        except subprocess.CalledProcessError as e:
            # 可能没有需要提交的更改
            print(f"⚠️  没有需要提交的更改")
            return False
        except Exception as e:
            print(f"❌ 提交失败：{e}")
            return False

    def start_watching(self, interval=30):
        """开始监听"""
        print(f"👀 Moltbot 配置监听器启动")
        print(f"📂 源目录：{self.moltbot_config_dir}")
        print(f"📂 目标目录：{self.bruce_config_dir}")
        print(f"📋 监听文件：")
        for file in self.watch_files:
            print(f"   - {file}")
        print(f"⏰ 检查间隔：{interval}秒")
        print(f"❄️  冷却时间：{self.sync_cooldown}秒")
        print("按Ctrl+C停止监听\n")

        try:
            while True:
                changes = self.check_changes()
                if changes:
                    print(f"\n🔔 检测到 {len(changes)} 个文件变化：")
                    for change in changes:
                        print(f"   - {change['rel_path']}")

                    # 同步所有文件
                    all_success = True
                    for change in changes:
                        if not self.sync_file(change):
                            all_success = False

                    # 如果全部同步成功，提交更改
                    if all_success:
                        self.commit_changes(changes)
                    print()

                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n👋 停止监听")

if __name__ == "__main__":
    import sys

    watcher = MoltbotWatcher()

    # 默认检查间隔30秒
    interval = int(sys.argv[1]) if len(sys.argv) > 1 else 30

    watcher.start_watching(interval)
