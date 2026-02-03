#!/usr/bin/env python3
"""
监听 /home/lejurobot/moltbot 的文件变化
自动同步到 /home/lejurobot/clawd/vendor/moltbot 并提交
"""

import os
import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

MOLTBOT_DIR = "/home/lejurobot/moltbot"
VENDOR_MOLTBOT = "/home/lejurobot/clawd/vendor/moltbot"

# 需要监听的目录
WATCH_DIRS = [
    "extensions",
    "src",
    "docs",
]

# 排除的目录/文件
EXCLUDE_PATTERNS = [
    "node_modules",
    ".git",
    "dist",
    ".cache",
    "*.log",
    "*.pyc",
    "__pycache__",
]


class MoltbotSyncHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_sync = 0
        self.sync_delay = 2  # 等待2秒后再同步，避免频繁触发

    def should_process(self, path):
        """检查是否应该处理这个文件"""
        # 检查排除模式
        for pattern in EXCLUDE_PATTERNS:
            if pattern in path:
                return False
        return True

    def on_modified(self, event):
        if event.is_directory:
            return

        if not self.should_process(event.src_path):
            return

        # 避免频繁同步
        now = time.time()
        if now - self.last_sync < self.sync_delay:
            return

        self.last_sync = now
        self.sync_changes()

    def sync_changes(self):
        """同步更改到 vendor moltbot"""
        try:
            print("🔄 检测到 moltbot 变化，正在同步...")

            # 同步各个目录
            for watch_dir in WATCH_DIRS:
                src_dir = os.path.join(MOLTBOT_DIR, watch_dir)
                dst_dir = os.path.join(VENDOR_MOLTBOT, watch_dir)

                if not os.path.exists(src_dir):
                    continue

                print(f"  📦 同步 {watch_dir}/...")

                # 使用 rsync 同步
                cmd = [
                    "rsync", "-av", "--delete",
                    "--exclude=/node_modules",
                    "--exclude=/dist",
                    "--exclude=/.cache",
                    f"{src_dir}/",
                    f"{dst_dir}/"
                ]

                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"  ❌ 同步失败: {result.stderr}")
                    return

            # 提交到 vendor moltbot
            self.commit_changes()

        except Exception as e:
            print(f"❌ 同步出错: {e}")

    def commit_changes(self):
        """提交更改到 vendor moltbot"""
        try:
            os.chdir(VENDOR_MOLTBOT)

            # 检查是否有变化
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True
            )

            if not result.stdout.strip():
                print("  ℹ️  没有需要提交的变化")
                return

            print("  💾 提交更改...")

            # 添加所有更改
            subprocess.run(["git", "add", "-A"], check=True)

            # 获取 moltbot 的最新提交信息
            result = subprocess.run(
                ["git", "-C", MOLTBOT_DIR, "log", "-1", "--pretty=%B"],
                capture_output=True,
                text=True,
                check=True
            )
            commit_msg = result.stdout.strip()

            result = subprocess.run(
                ["git", "-C", MOLTBOT_DIR, "log", "-1", "--oneline"],
                capture_output=True,
                text=True,
                check=True
            )
            commit_ref = result.stdout.strip()

            # 提交
            full_msg = f"""{commit_msg}

---
Synced from {MOLTBOT_DIR}
Commit: {commit_ref}"""

            subprocess.run(
                ["git", "commit", "-m", full_msg],
                check=True,
                capture_output=True
            )

            print("  ✅ 同步完成！git-auto-pusher 将自动推送")

        except subprocess.CalledProcessError as e:
            print(f"  ❌ 提交失败: {e}")
        except Exception as e:
            print(f"  ❌ 错误: {e}")


def main():
    print("🚀 Moltbot 文件监听器启动")
    print(f"📂 监听目录: {MOLTBOT_DIR}")
    print(f"📦 目标目录: {VENDOR_MOLTBOT}")
    print()

    event_handler = MoltbotSyncHandler()
    observer = Observer()

    # 监听各个子目录
    for watch_dir in WATCH_DIRS:
        watch_path = os.path.join(MOLTBOT_DIR, watch_dir)
        if os.path.exists(watch_path):
            observer.schedule(event_handler, watch_path, recursive=True)
            print(f"  ✓ 监听: {watch_dir}/")

    print()
    print("⏳ 监听中... (按 Ctrl+C 停止)")

    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n👋 监听器已停止")

    observer.join()


if __name__ == "__main__":
    main()
