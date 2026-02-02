#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moltbot 代码仓库监听器
监听 Moltbot 代码仓库的变化，同步到 Bruce 仓库
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

class MoltbotCodeWatcher:
    def __init__(self):
        self.moltbot_dir = Path("/home/lejurobot/moltbot")
        self.bruce_vendor_dir = Path("/home/lejurobot/clawd/vendor/moltbot")
        self.last_sync_time = 0
        self.sync_cooldown = 60  # 同步冷却时间（秒）

    def get_latest_commit_hash(self, repo_dir):
        """获取仓库的最新 commit hash"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd=repo_dir
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            print(f"获取 commit hash 失败：{e}")
        return None

    def get_branch_name(self, repo_dir):
        """获取当前分支名"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                cwd=repo_dir
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            print(f"获取分支名失败：{e}")
        return "main"

    def check_moltbot_changes(self):
        """检查 Moltbot 代码仓库是否有新的 commit"""
        current_time = time.time()

        # 检查冷却时间
        if current_time - self.last_sync_time < self.sync_cooldown:
            return None

        # 获取最新 commit hash
        moltbot_hash = self.get_latest_commit_hash(self.moltbot_dir)
        if not moltbot_hash:
            return None

        # 获取分支名
        branch = self.get_branch_name(self.moltbot_dir)

        # 检查 Bruce vendor 目录中的记录
        record_file = self.bruce_vendor_dir / ".moltbot-sync-record.json"
        synced_hash = None

        if record_file.exists():
            try:
                with open(record_file, 'r') as f:
                    data = json.load(f)
                    synced_hash = data.get('moltbot_commit')
            except Exception as e:
                print(f"读取同步记录失败：{e}")

        # 如果有新的 commit
        if moltbot_hash != synced_hash:
            return {
                'commit_hash': moltbot_hash,
                'branch': branch,
                'previous_hash': synced_hash
            }

        return None

    def sync_moltbot_to_bruce(self, change_info):
        """同步 Moltbot 代码到 Bruce vendor 目录"""
        try:
            print(f"\n📦 开始同步 Moltbot 代码...")
            print(f"   Commit: {change_info['commit_hash']}")
            print(f"   分支: {change_info['branch']}")

            # 确保 vendor/moltbot 目录存在
            self.bruce_vendor_dir.mkdir(parents=True, exist_ok=True)

            # 方法1：使用 git fetch + git checkout
            # 先在 vendor/moltbot 初始化（如果不存在）
            if not (self.bruce_vendor_dir / ".git").exists():
                print("   首次同步，克隆仓库...")
                subprocess.run(
                    ["git", "clone", "--depth", "1", str(self.moltbot_dir), str(self.bruce_vendor_dir)],
                    check=True,
                    capture_output=True
                )
            else:
                # 拉取最新代码
                print("   拉取最新代码...")
                subprocess.run(
                    ["git", "fetch", "origin"],
                    cwd=self.bruce_vendor_dir,
                    check=True,
                    capture_output=True
                )
                subprocess.run(
                    ["git", "checkout", change_info['branch']],
                    cwd=self.bruce_vendor_dir,
                    check=True,
                    capture_output=True
                )
                subprocess.run(
                    ["git", "pull", "origin", change_info['branch']],
                    cwd=self.bruce_vendor_dir,
                    check=True,
                    capture_output=True
                )

            # 方法2：直接 rsync（更快，但不会保留 git 历史）
            # subprocess.run(
            #     ["rsync", "-av", "--delete", "--exclude=node_modules", "--exclude=.git",
            #      str(self.moltbot_dir) + "/", str(self.bruce_vendor_dir) + "/"],
            #     check=True
            # )

            # 更新同步记录
            record_file = self.bruce_vendor_dir / ".moltbot-sync-record.json"
            with open(record_file, 'w') as f:
                json.dump({
                    'moltbot_commit': change_info['commit_hash'],
                    'branch': change_info['branch'],
                    'sync_time': datetime.now().isoformat()
                }, f, indent=2)

            print(f"✅ 同步完成！")

            return True

        except Exception as e:
            print(f"❌ 同步失败：{e}")
            return False

    def commit_changes(self, change_info):
        """提交 Bruce 仓库的更改"""
        try:
            os.chdir("/home/lejurobot/clawd")

            # 添加 vendor/moltbot 目录
            subprocess.run(
                ["git", "add", "vendor/moltbot"],
                check=True
            )

            # 检查是否有更改
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True
            )

            if not result.stdout.strip():
                print("⚠️  没有需要提交的更改")
                return False

            # 生成 commit 信息
            commit_msg = f"同步 Moltbot 代码：{change_info['commit_hash'][:8]}"

            # 提交（会自动触发 Git 钩子推送）
            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                check=True
            )

            print(f"📦 已提交：{commit_msg}")
            self.last_sync_time = time.time()
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ 提交失败：{e}")
            return False
        except Exception as e:
            print(f"❌ 提交失败：{e}")
            return False

    def start_watching(self, interval=60):
        """开始监听"""
        print(f"👀 Moltbot 代码监听器启动")
        print(f"📂 源目录：{self.moltbot_dir}")
        print(f"📂 目标目录：{self.bruce_vendor_dir}")
        print(f"⏰ 检查间隔：{interval}秒")
        print(f"❄️  冷却时间：{self.sync_cooldown}秒")
        print("按Ctrl+C停止监听\n")

        try:
            while True:
                changes = self.check_moltbot_changes()
                if changes:
                    print(f"\n🔔 检测到新的 Moltbot commit:")
                    print(f"   Hash: {changes['commit_hash'][:8]}")
                    print(f"   分支: {changes['branch']}")

                    # 同步代码
                    if self.sync_moltbot_to_bruce(changes):
                        # 提交更改
                        self.commit_changes(changes)
                    print()

                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n👋 停止监听")

if __name__ == "__main__":
    import sys

    watcher = MoltbotCodeWatcher()

    # 默认检查间隔60秒
    interval = int(sys.argv[1]) if len(sys.argv) > 1 else 60

    watcher.start_watching(interval)
