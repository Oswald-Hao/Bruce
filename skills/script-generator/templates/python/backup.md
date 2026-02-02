#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Description: 定时备份指定目录到目标位置，支持保留指定天数的备份
"""
自动生成的Python脚本 - 备份脚本
生成时间: {{timestamp}}
需求: {{prompt}}
"""

import os
import shutil
import tarfile
from datetime import datetime, timedelta
from pathlib import Path
import argparse


def backup_directory(source_dir: str, backup_dir: str, days_to_keep: int = 7):
    """
    备份目录到指定位置
    """
    source = Path(source_dir)
    backup = Path(backup_dir)

    if not source.exists():
        print(f"错误: 源目录不存在: {source_dir}")
        return False

    # 创建备份目录
    backup.mkdir(parents=True, exist_ok=True)

    # 生成备份文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup / f"backup_{timestamp}.tar.gz"

    print(f"开始备份: {source} -> {backup_file}")

    # 创建tar归档
    with tarfile.open(backup_file, "w:gz") as tar:
        tar.add(source, arcname=source.name)

    print(f"备份完成: {backup_file.stat().st_size / 1024 / 1024:.2f} MB")

    # 清理旧备份
    cleanup_old_backups(backup, days_to_keep)

    return True


def cleanup_old_backups(backup_dir: Path, days: int):
    """
    删除超过指定天数的旧备份
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    print(f"清理 {days} 天前的备份 (早于 {cutoff_date})...")

    deleted_count = 0
    for backup_file in backup_dir.glob("backup_*.tar.gz"):
        if datetime.fromtimestamp(backup_file.stat().st_mtime) < cutoff_date:
            backup_file.unlink()
            print(f"删除旧备份: {backup_file.name}")
            deleted_count += 1

    print(f"已删除 {deleted_count} 个旧备份")


def main():
    parser = argparse.ArgumentParser(description="目录备份脚本")
    parser.add_argument("--source", default="/data", help="源目录")
    parser.add_argument("--backup", default="/backup", help="备份目录")
    parser.add_argument("--days", type=int, default=7, help="保留天数")

    args = parser.parse_args()

    backup_directory(args.source, args.backup, args.days)


if __name__ == "__main__":
    main()
