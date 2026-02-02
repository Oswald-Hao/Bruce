#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backup System - 备份恢复系统
支持文件备份、目录备份、增量备份、压缩、恢复等功能
"""

import os
import shutil
import hashlib
import json
import gzip
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import fnmatch


class BackupSystem:
    """备份恢复工具类"""

    def __init__(self, backup_log_dir: str = None):
        """
        初始化备份系统

        Args:
            backup_log_dir: 备份日志目录（默认在/tmp/backup_logs）
        """
        self.backup_log_dir = backup_log_dir or '/tmp/backup_logs'
        os.makedirs(self.backup_log_dir, exist_ok=True)

    def _get_file_hash(self, filepath: str) -> str:
        """
        计算文件MD5哈希

        Args:
            filepath: 文件路径

        Returns:
            MD5哈希值
        """
        hash_md5 = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

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
        return False

    def backup_file(
        self,
        source: str,
        destination: str,
        compress: bool = False,
        overwrite: bool = False
    ) -> bool:
        """
        备份单个文件

        Args:
            source: 源文件路径
            destination: 目标路径
            compress: 是否压缩
            overwrite: 是否覆盖已存在的文件

        Returns:
            是否成功
        """
        try:
            if not os.path.exists(source):
                print(f"源文件不存在: {source}")
                return False

            if os.path.exists(destination) and not overwrite:
                print(f"目标文件已存在: {destination}")
                return False

            if compress:
                with open(source, 'rb') as f_in:
                    with gzip.open(destination, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                shutil.copy2(source, destination)

            return True
        except Exception as e:
            print(f"备份文件失败: {str(e)}")
            return False

    def backup_directory(
        self,
        source: str,
        destination: str,
        exclude: List[str] = None,
        compress: bool = False,
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """
        备份目录

        Args:
            source: 源目录路径
            destination: 目标目录路径
            exclude: 排除模式列表（如['*.tmp', '*.log']）
            compress: 是否压缩（单个压缩文件）
            overwrite: 是否覆盖已存在的目标

        Returns:
            备份结果统计
        """
        if not os.path.exists(source):
            return {'success': False, 'error': '源目录不存在'}

        exclude = exclude or []
        result = {
            'success': True,
            'source': source,
            'destination': destination,
            'files_copied': 0,
            'files_skipped': 0,
            'total_size': 0,
            'start_time': datetime.now().isoformat()
        }

        try:
            if compress:
                # 压缩到单个文件
                self._compress_directory(source, destination, exclude)
                result['compress'] = True
            else:
                # 复制目录
                if os.path.exists(destination):
                    if overwrite:
                        shutil.rmtree(destination)
                    else:
                        result['success'] = False
                        result['error'] = '目标目录已存在'
                        return result

                os.makedirs(destination, exist_ok=True)

                for root, dirs, files in os.walk(source):
                    # 复制目录结构
                    relative_path = os.path.relpath(root, source)
                    target_dir = os.path.join(destination, relative_path)
                    os.makedirs(target_dir, exist_ok=True)

                    for filename in files:
                        source_file = os.path.join(root, filename)
                        if self._should_exclude(source_file, exclude):
                            result['files_skipped'] += 1
                            continue

                        target_file = os.path.join(target_dir, filename)
                        shutil.copy2(source_file, target_file)
                        result['files_copied'] += 1
                        result['total_size'] += os.path.getsize(source_file)

            result['end_time'] = datetime.now().isoformat()
            result['duration'] = (datetime.now() - datetime.fromisoformat(result['start_time'])).total_seconds()

        except Exception as e:
            result['success'] = False
            result['error'] = str(e)

        return result

    def _compress_directory(
        self,
        source: str,
        destination: str,
        exclude: List[str] = None
    ):
        """
        压缩目录到单个文件

        Args:
            source: 源目录
            destination: 目标文件路径
            exclude: 排除模式列表
        """
        import tarfile

        exclude = exclude or []

        with tarfile.open(destination, 'w:gz') as tar:
            for root, dirs, files in os.walk(source):
                for filename in files:
                    filepath = os.path.join(root, filename)
                    if self._should_exclude(filepath, exclude):
                        continue

                    arcname = os.path.relpath(filepath, os.path.dirname(source))
                    tar.add(filepath, arcname=arcname)

    def incremental_backup(
        self,
        source: str,
        destination: str,
        exclude: List[str] = None,
        base_backup: str = None
    ) -> Dict[str, Any]:
        """
        增量备份（仅备份变更的文件）

        Args:
            source: 源目录路径
            destination: 目标目录路径
            exclude: 排除模式列表
            base_backup: 基础备份路径（用于对比，默认使用上次备份）

        Returns:
            备份结果统计
        """
        if not os.path.exists(source):
            return {'success': False, 'error': '源目录不存在'}

        exclude = exclude or []
        result = {
            'success': True,
            'source': source,
            'destination': destination,
            'files_updated': 0,
            'files_added': 0,
            'files_unchanged': 0,
            'total_size': 0,
            'start_time': datetime.now().isoformat()
        }

        # 查找基础备份
        if base_backup is None:
            # 尝试找到上次的备份
            backup_log = self._get_backup_log(source)
            if backup_log and 'last_backup' in backup_log:
                base_backup = backup_log['last_backup']

        # 创建文件哈希映射（如果存在基础备份）
        base_hashes = {}
        if base_backup and os.path.exists(base_backup):
            for root, dirs, files in os.walk(base_backup):
                for filename in files:
                    filepath = os.path.join(root, filename)
                    try:
                        file_hash = self._get_file_hash(filepath)
                        rel_path = os.path.relpath(filepath, base_backup)
                        base_hashes[rel_path] = file_hash
                    except Exception:
                        pass

        try:
            os.makedirs(destination, exist_ok=True)

            for root, dirs, files in os.walk(source):
                relative_path = os.path.relpath(root, source)
                target_dir = os.path.join(destination, relative_path)
                os.makedirs(target_dir, exist_ok=True)

                for filename in files:
                    source_file = os.path.join(root, filename)
                    if self._should_exclude(source_file, exclude):
                        continue

                    # 确保relative_path格式一致（去掉开头的./）
                    rel_path = os.path.join(relative_path, filename)
                    if rel_path.startswith('./'):
                        rel_path = rel_path[2:]

                    target_file = os.path.join(target_dir, filename)

                    # 计算当前文件哈希
                    try:
                        current_hash = self._get_file_hash(source_file)

                        if rel_path in base_hashes:
                            if current_hash != base_hashes[rel_path]:
                                # 文件已变更
                                shutil.copy2(source_file, target_file)
                                result['files_updated'] += 1
                            else:
                                result['files_unchanged'] += 1
                        else:
                            # 新文件
                            shutil.copy2(source_file, target_file)
                            result['files_added'] += 1

                        result['total_size'] += os.path.getsize(source_file)

                    except Exception as e:
                        print(f"处理文件失败 {source_file}: {e}")

            # 更新备份日志
            self._update_backup_log(source, destination)

            result['end_time'] = datetime.now().isoformat()
            result['duration'] = (datetime.now() - datetime.fromisoformat(result['start_time'])).total_seconds()

        except Exception as e:
            result['success'] = False
            result['error'] = str(e)

        return result

    def _get_backup_log(self, source: str) -> Optional[Dict[str, Any]]:
        """
        获取备份日志

        Args:
            source: 源路径

        Returns:
            备份日志字典
        """
        log_path = os.path.join(self.backup_log_dir, hashlib.md5(source.encode()).hexdigest() + '.json')
        try:
            if os.path.exists(log_path):
                with open(log_path, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return None

    def _update_backup_log(self, source: str, destination: str):
        """
        更新备份日志

        Args:
            source: 源路径
            destination: 备份目标路径
        """
        log_path = os.path.join(self.backup_log_dir, hashlib.md5(source.encode()).hexdigest() + '.json')
        log = {
            'source': source,
            'last_backup': destination,
            'backup_time': datetime.now().isoformat(),
            'history': []
        }

        # 读取现有日志
        existing_log = self._get_backup_log(source)
        if existing_log:
            log['history'] = existing_log.get('history', [])
            if 'last_backup' in existing_log:
                log['history'].append({
                    'backup': existing_log['last_backup'],
                    'time': existing_log.get('backup_time', '')
                })

        # 保存日志
        with open(log_path, 'w') as f:
            json.dump(log, f, indent=2)

    def restore_file(
        self,
        source: str,
        destination: str,
        overwrite: bool = False
    ) -> bool:
        """
        恢复文件

        Args:
            source: 备份文件路径
            destination: 恢复目标路径
            overwrite: 是否覆盖已存在的文件

        Returns:
            是否成功
        """
        try:
            if not os.path.exists(source):
                print(f"备份文件不存在: {source}")
                return False

            if os.path.exists(destination) and not overwrite:
                print(f"目标文件已存在: {destination}")
                return False

            os.makedirs(os.path.dirname(destination), exist_ok=True)
            shutil.copy2(source, destination)
            return True

        except Exception as e:
            print(f"恢复文件失败: {str(e)}")
            return False

    def restore_directory(
        self,
        source: str,
        destination: str,
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """
        恢复目录

        Args:
            source: 备份目录路径
            destination: 恢复目标路径
            overwrite: 是否覆盖已存在的目录

        Returns:
            恢复结果统计
        """
        if not os.path.exists(source):
            return {'success': False, 'error': '备份目录不存在'}

        result = {
            'success': True,
            'source': source,
            'destination': destination,
            'files_restored': 0,
            'total_size': 0,
            'start_time': datetime.now().isoformat()
        }

        try:
            # 检查是否是压缩备份
            if source.endswith('.tar.gz') or source.endswith('.tgz'):
                self._decompress_directory(source, destination, overwrite)
                result['compress'] = True
            else:
                if os.path.exists(destination):
                    if overwrite:
                        shutil.rmtree(destination)
                    else:
                        result['success'] = False
                        result['error'] = '目标目录已存在'
                        return result

                os.makedirs(destination, exist_ok=True)

                for root, dirs, files in os.walk(source):
                    relative_path = os.path.relpath(root, source)
                    target_dir = os.path.join(destination, relative_path)
                    os.makedirs(target_dir, exist_ok=True)

                    for filename in files:
                        source_file = os.path.join(root, filename)
                        target_file = os.path.join(target_dir, filename)
                        shutil.copy2(source_file, target_file)
                        result['files_restored'] += 1
                        result['total_size'] += os.path.getsize(source_file)

            result['end_time'] = datetime.now().isoformat()
            result['duration'] = (datetime.now() - datetime.fromisoformat(result['start_time'])).total_seconds()

        except Exception as e:
            result['success'] = False
            result['error'] = str(e)

        return result

    def _decompress_directory(
        self,
        source: str,
        destination: str,
        overwrite: bool = False
    ):
        """
        解压目录

        Args:
            source: 压缩文件路径
            destination: 目标目录
            overwrite: 是否覆盖
        """
        import tarfile

        if os.path.exists(destination):
            if overwrite:
                shutil.rmtree(destination)
            else:
                raise FileExistsError('目标目录已存在')

        os.makedirs(destination, exist_ok=True)

        with tarfile.open(source, 'r:gz') as tar:
            tar.extractall(destination)

    def cleanup_old_backups(
        self,
        backup_dir: str,
        retention_days: int = 30
    ) -> List[str]:
        """
        清理过期备份

        Args:
            backup_dir: 备份目录
            retention_days: 保留天数

        Returns:
            删除的备份列表
        """
        deleted = []
        cutoff_time = datetime.now() - timedelta(days=retention_days)

        try:
            for item in os.listdir(backup_dir):
                item_path = os.path.join(backup_dir, item)

                if os.path.isfile(item_path):
                    mtime = datetime.fromtimestamp(os.path.getmtime(item_path))
                    if mtime < cutoff_time:
                        os.remove(item_path)
                        deleted.append(item_path)

                elif os.path.isdir(item_path):
                    mtime = datetime.fromtimestamp(os.path.getmtime(item_path))
                    if mtime < cutoff_time:
                        shutil.rmtree(item_path)
                        deleted.append(item_path)

        except Exception as e:
            print(f"清理备份失败: {e}")

        return deleted

    def get_backup_info(self, backup_path: str) -> Optional[Dict[str, Any]]:
        """
        获取备份信息

        Args:
            backup_path: 备份路径

        Returns:
            备份信息字典
        """
        if not os.path.exists(backup_path):
            return None

        info = {
            'path': backup_path,
            'type': 'directory' if os.path.isdir(backup_path) else 'file',
            'size': 0,
            'count': 0,
            'modified': datetime.fromtimestamp(os.path.getmtime(backup_path)).isoformat()
        }

        if os.path.isfile(backup_path):
            info['size'] = os.path.getsize(backup_path)
        else:
            for root, dirs, files in os.walk(backup_path):
                for filename in files:
                    filepath = os.path.join(root, filename)
                    info['size'] += os.path.getsize(filepath)
                    info['count'] += 1

        return info


def main():
    """命令行示例"""
    import argparse

    parser = argparse.ArgumentParser(description='备份恢复系统')
    parser.add_argument('--action', choices=['backup', 'restore', 'info'], required=True, help='操作类型')
    parser.add_argument('--source', help='源路径')
    parser.add_argument('--destination', help='目标路径')
    args = parser.parse_args()

    backup = BackupSystem()

    if args.action == 'backup' and args.source and args.destination:
        if os.path.isfile(args.source):
            success = backup.backup_file(args.source, args.destination)
            print(f"备份{'成功' if success else '失败'}")
        else:
            result = backup.backup_directory(args.source, args.destination)
            print(f"备份结果: {result}")

    elif args.action == 'restore' and args.source and args.destination:
        if os.path.isfile(args.source):
            success = backup.restore_file(args.source, args.destination)
            print(f"恢复{'成功' if success else '失败'}")
        else:
            result = backup.restore_directory(args.source, args.destination)
            print(f"恢复结果: {result}")

    elif args.action == 'info' and args.source:
        info = backup.get_backup_info(args.source)
        if info:
            print(f"备份信息: {info}")


if __name__ == '__main__':
    main()
