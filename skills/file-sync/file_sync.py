#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Sync Tool - 文件同步工具
支持双向同步、单向同步、增量同步、冲突处理等功能
"""

import os
import shutil
import hashlib
import json
import fnmatch
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime
from collections import defaultdict


class FileSync:
    """文件同步工具类"""

    def __init__(self, verbose: bool = False):
        """
        初始化文件同步工具

        Args:
            verbose: 是否输出详细日志
        """
        self.verbose = verbose
        self.sync_log = []

    def _log(self, message: str):
        """
        输出日志

        Args:
            message: 日志消息
        """
        self.sync_log.append(message)
        if self.verbose:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def _get_file_hash(self, filepath: str) -> str:
        """
        计算文件哈希

        Args:
            filepath: 文件路径

        Returns:
            MD5哈希值
        """
        hash_md5 = hashlib.md5()
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return None

    def _should_exclude(self, filepath: str, exclude_patterns: List[str]) -> bool:
        """
        判断文件是否应该被排除

        Args:
            filepath: 文件路径
            exclude_patterns: 排除模式列表

        Returns:
            是否排除
        """
        filename = os.path.basename(filepath)
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(filename, pattern):
                return True
            # 检查路径
            if pattern in filepath:
                return True
        return False

    def _collect_files(self, directory: str, exclude_patterns: List[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        收集目录中的所有文件

        Args:
            directory: 目录路径
            exclude_patterns: 排除模式列表

        Returns:
            文件字典 {相对路径: {hash, size, mtime}}
        """
        exclude_patterns = exclude_patterns or []
        files = {}

        for root, dirs, filenames in os.walk(directory):
            # 排除目录
            dirs[:] = [d for d in dirs if not self._should_exclude(os.path.join(root, d), exclude_patterns)]

            for filename in filenames:
                filepath = os.path.join(root, filename)

                if self._should_exclude(filepath, exclude_patterns):
                    continue

                try:
                    rel_path = os.path.relpath(filepath, directory)
                    stat = os.stat(filepath)

                    files[rel_path] = {
                        'hash': self._get_file_hash(filepath),
                        'size': stat.st_size,
                        'mtime': stat.st_mtime
                    }
                except Exception as e:
                    self._log(f"无法读取文件 {filepath}: {e}")

        return files

    def _detect_changes(
        self,
        source_files: Dict[str, Dict[str, Any]],
        target_files: Dict[str, Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """
        检测文件变更

        Args:
            source_files: 源文件字典
            target_files: 目标文件字典

        Returns:
            变更分类
        """
        changes = {
            'new_in_source': [],      # 源有，目标无
            'new_in_target': [],      # 目标有，源无
            'modified_in_source': [], # 源修改
            'modified_in_target': [], # 目标修改
            'conflicts': []           # 冲突（两边都修改）
        }

        # 检查源文件
        for rel_path, source_info in source_files.items():
            if rel_path not in target_files:
                changes['new_in_source'].append(rel_path)
            else:
                target_info = target_files[rel_path]
                if source_info['hash'] != target_info['hash']:
                    if source_info['mtime'] > target_info['mtime']:
                        changes['modified_in_source'].append(rel_path)
                    else:
                        changes['modified_in_target'].append(rel_path)

        # 检查目标独有的文件
        for rel_path in target_files:
            if rel_path not in source_files:
                changes['new_in_target'].append(rel_path)

        return changes

    def _copy_file(self, source: str, target: str) -> bool:
        """
        复制文件

        Args:
            source: 源文件路径
            target: 目标文件路径

        Returns:
            是否成功
        """
        try:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copy2(source, target)
            self._log(f"复制: {source} → {target}")
            return True
        except Exception as e:
            self._log(f"复制失败 {source}: {e}")
            return False

    def sync_one_way(
        self,
        source_dir: str,
        target_dir: str,
        exclude_patterns: List[str] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        单向同步（源 → 目标）

        Args:
            source_dir: 源目录
            target_dir: 目标目录
            exclude_patterns: 排除模式列表
            dry_run: 预演模式

        Returns:
            同步结果
        """
        result = {
            'success': True,
            'files_copied': 0,
            'files_updated': 0,
            'files_deleted': 0,
            'errors': [],
            'dry_run': dry_run
        }

        self._log(f"单向同步: {source_dir} → {target_dir}")

        # 收集文件
        source_files = self._collect_files(source_dir, exclude_patterns)
        target_files = self._collect_files(target_dir, exclude_patterns)

        # 复制新文件和更新文件
        for rel_path, source_info in source_files.items():
            target_path = os.path.join(target_dir, rel_path)
            source_path = os.path.join(source_dir, rel_path)

            if rel_path not in target_files:
                # 新文件
                if not dry_run:
                    if self._copy_file(source_path, target_path):
                        result['files_copied'] += 1
                else:
                    self._log(f"[预演] 将复制: {rel_path}")
                    result['files_copied'] += 1

            elif source_info['hash'] != target_files[rel_path]['hash']:
                # 文件已变更
                if not dry_run:
                    if self._copy_file(source_path, target_path):
                        result['files_updated'] += 1
                else:
                    self._log(f"[预演] 将更新: {rel_path}")
                    result['files_updated'] += 1

        # 删除目标中多余的文件（可选）
        # for rel_path in target_files:
        #     if rel_path not in source_files:
        #         if not dry_run:
        #             try:
        #                 os.remove(os.path.join(target_dir, rel_path))
        #                 result['files_deleted'] += 1
        #                 self._log(f"删除: {rel_path}")
        #             except Exception as e:
        #                 result['errors'].append(str(e))
        #         else:
        #             self._log(f"[预演] 将删除: {rel_path}")
        #             result['files_deleted'] += 1

        return result

    def sync_two_way(
        self,
        dir1: str,
        dir2: str,
        exclude_patterns: List[str] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        双向同步

        Args:
            dir1: 目录1
            dir2: 目录2
            exclude_patterns: 排除模式列表
            dry_run: 预演模式

        Returns:
            同步结果
        """
        result = {
            'success': True,
            'conflicts': [],
            'synced_to_dir1': 0,
            'synced_to_dir2': 0,
            'errors': [],
            'dry_run': dry_run
        }

        self._log(f"双向同步: {dir1} ↔ {dir2}")

        # 收集文件
        files1 = self._collect_files(dir1, exclude_patterns)
        files2 = self._collect_files(dir2, exclude_patterns)

        # 检测变更
        changes = self._detect_changes(files1, files2)

        # 处理dir1独有的文件 → dir2
        for rel_path in changes['new_in_source']:
            source = os.path.join(dir1, rel_path)
            target = os.path.join(dir2, rel_path)
            if not dry_run:
                if self._copy_file(source, target):
                    result['synced_to_dir2'] += 1
            else:
                self._log(f"[预演] 将复制到dir2: {rel_path}")
                result['synced_to_dir2'] += 1

        # 处理dir2独有的文件 → dir1
        for rel_path in changes['new_in_target']:
            source = os.path.join(dir2, rel_path)
            target = os.path.join(dir1, rel_path)
            if not dry_run:
                if self._copy_file(source, target):
                    result['synced_to_dir1'] += 1
            else:
                self._log(f"[预演] 将复制到dir1: {rel_path}")
                result['synced_to_dir1'] += 1

        # 处理修改的文件
        for rel_path in changes['modified_in_source']:
            source = os.path.join(dir1, rel_path)
            target = os.path.join(dir2, rel_path)
            if not dry_run:
                if self._copy_file(source, target):
                    result['synced_to_dir2'] += 1
            else:
                self._log(f"[预演] 将更新dir2: {rel_path}")
                result['synced_to_dir2'] += 1

        for rel_path in changes['modified_in_target']:
            source = os.path.join(dir2, rel_path)
            target = os.path.join(dir1, rel_path)
            if not dry_run:
                if self._copy_file(source, target):
                    result['synced_to_dir1'] += 1
            else:
                self._log(f"[预演] 将更新dir1: {rel_path}")
                result['synced_to_dir1'] += 1

        return result

    def get_sync_stats(
        self,
        source_dir: str,
        target_dir: str,
        exclude_patterns: List[str] = None
    ) -> Dict[str, Any]:
        """
        获取同步统计信息

        Args:
            source_dir: 源目录
            target_dir: 目标目录
            exclude_patterns: 排除模式列表

        Returns:
            统计信息
        """
        source_files = self._collect_files(source_dir, exclude_patterns)
        target_files = self._collect_files(target_dir, exclude_patterns)

        changes = self._detect_changes(source_files, target_files)

        total_size = sum(f['size'] for f in source_files.values())

        return {
            'source_files': len(source_files),
            'target_files': len(target_files),
            'new_in_source': len(changes['new_in_source']),
            'new_in_target': len(changes['new_in_target']),
            'modified_in_source': len(changes['modified_in_source']),
            'modified_in_target': len(changes['modified_in_target']),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'estimated_sync_files': (
                len(changes['new_in_source']) +
                len(changes['new_in_target']) +
                len(changes['modified_in_source']) +
                len(changes['modified_in_target'])
            )
        }

    def compare_dirs(
        self,
        dir1: str,
        dir2: str,
        exclude_patterns: List[str] = None
    ) -> Dict[str, Any]:
        """
        比较两个目录的差异

        Args:
            dir1: 目录1
            dir2: 目录2
            exclude_patterns: 排除模式列表

        Returns:
            差异信息
        """
        files1 = self._collect_files(dir1, exclude_patterns)
        files2 = self._collect_files(dir2, exclude_patterns)

        changes = self._detect_changes(files1, files2)

        return {
            'files_only_in_dir1': changes['new_in_source'],
            'files_only_in_dir2': changes['new_in_target'],
            'files_modified_in_dir1': changes['modified_in_source'],
            'files_modified_in_dir2': changes['modified_in_target'],
            'files_identical': [
                f for f in files1
                if f in files2 and files1[f]['hash'] == files2[f]['hash']
            ]
        }

    def get_sync_log(self) -> List[str]:
        """
        获取同步日志

        Returns:
            日志列表
        """
        return self.sync_log

    def clear_sync_log(self):
        """清空同步日志"""
        self.sync_log = []


def main():
    """命令行示例"""
    import argparse

    parser = argparse.ArgumentParser(description='文件同步工具')
    parser.add_argument('--action', choices=['sync', 'stats', 'compare'], required=True, help='操作类型')
    parser.add_argument('--source', help='源目录')
    parser.add_argument('--target', help='目标目录')
    parser.add_argument('--mode', choices=['one-way', 'two-way'], default='one-way', help='同步模式')
    parser.add_argument('--exclude', help='排除模式（逗号分隔）')
    parser.add_argument('--dry-run', action='store_true', help='预演模式')
    parser.add_argument('--verbose', action='store_true', help='详细输出')
    args = parser.parse_args()

    sync = FileSync(verbose=args.verbose)

    if args.action == 'sync' and args.source and args.target:
        exclude = [e.strip() for e in args.exclude.split(',')] if args.exclude else None

        if args.mode == 'one-way':
            result = sync.sync_one_way(args.source, args.target, exclude, args.dry_run)
        else:
            result = sync.sync_two_way(args.source, args.target, exclude, args.dry_run)

        print(f"同步完成: {result}")

    elif args.action == 'stats' and args.source and args.target:
        exclude = [e.strip() for e in args.exclude.split(',')] if args.exclude else None
        stats = sync.get_sync_stats(args.source, args.target, exclude)
        print(f"同步统计: {json.dumps(stats, indent=2)}")

    elif args.action == 'compare' and args.source and args.target:
        exclude = [e.strip() for e in args.exclude.split(',')] if args.exclude else None
        diff = sync.compare_dirs(args.source, args.target, exclude)
        print(f"目录差异: {json.dumps(diff, indent=2)}")


if __name__ == '__main__':
    main()
