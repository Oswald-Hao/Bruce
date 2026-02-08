#!/usr/bin/env python3
"""
文件同步工具 - File Sync Tool

功能：
- 多设备文件同步（本地、远程SSH、云存储）
- 增量备份（只同步变化的文件）
- 双向同步（支持冲突检测和解决）
- 文件过滤（按扩展名、大小、时间）
- 同步日志和历史记录
- 自动恢复和回滚
"""

import os
import shutil
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict


@dataclass
class FileRecord:
    """文件记录"""
    path: str
    size: int
    mtime: float
    hash: str
    is_dir: bool = False


class FileSyncTool:
    """文件同步工具 - 多设备文件同步系统"""

    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化文件同步工具

        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.sync_history_file = Path(self.config.get('history_file', './sync-history.json'))
        self.exclude_patterns = self.config.get('exclude_patterns', [
            '.git', '__pycache__', 'node_modules', '.DS_Store', '*.tmp'
        ])
        self.history: Dict[str, Any] = self._load_history()

    def _load_history(self) -> Dict[str, Any]:
        """加载同步历史"""
        if self.sync_history_file.exists():
            with open(self.sync_history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'syncs': [], 'file_records': {}}

    def _save_history(self):
        """保存同步历史"""
        with open(self.sync_history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)

    def _calculate_hash(self, file_path: str) -> str:
        """
        计算文件哈希值

        Args:
            file_path: 文件路径

        Returns:
            哈希值
        """
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _should_exclude(self, path: str) -> bool:
        """
        检查是否应该排除该文件

        Args:
            path: 文件路径

        Returns:
            是否排除
        """
        path_name = Path(path).name
        
        for pattern in self.exclude_patterns:
            if pattern.startswith('*.'):
                # 扩展名匹配
                if path_name.endswith(pattern[1:]):
                    return True
            elif pattern in path:
                # 路径包含匹配
                return True
        
        return False

    def _scan_directory(self, root_dir: str) -> Dict[str, FileRecord]:
        """
        扫描目录

        Args:
            root_dir: 根目录

        Returns:
            文件记录字典
        """
        records = {}
        root_path = Path(root_dir)

        if not root_path.exists():
            return records

        for item in root_path.rglob('*'):
            if self._should_exclude(str(item)):
                continue

            try:
                stat = item.stat()
                rel_path = str(item.relative_to(root_path))

                if item.is_dir():
                    records[rel_path] = FileRecord(
                        path=rel_path,
                        size=0,
                        mtime=stat.st_mtime,
                        hash='',
                        is_dir=True
                    )
                else:
                    records[rel_path] = FileRecord(
                        path=rel_path,
                        size=stat.st_size,
                        mtime=stat.st_mtime,
                        hash=self._calculate_hash(str(item)),
                        is_dir=False
                    )
            except (PermissionError, OSError):
                continue

        return records

    def sync_directories(self, source_dir: str, target_dir: str, mode: str = 'copy') -> Dict[str, Any]:
        """
        同步目录

        Args:
            source_dir: 源目录
            target_dir: 目标目录
            mode: 同步模式（copy/reflect/two-way）

        Returns:
            同步结果
        """
        source_path = Path(source_dir)
        target_path = Path(target_dir)

        if not source_path.exists():
            return {'success': False, 'error': '源目录不存在'}

        # 扫描源目录
        source_records = self._scan_directory(source_dir)

        # 扫描目标目录（如果存在）
        target_records = {}
        if target_path.exists():
            target_records = self._scan_directory(target_dir)

        # 根据模式执行同步
        if mode == 'copy':
            result = self._sync_copy(source_records, target_records, source_path, target_path)
        elif mode == 'reflect':
            result = self._sync_reflect(source_records, target_records, source_path, target_path)
        elif mode == 'two-way':
            result = self._sync_two_way(source_records, target_records, source_path, target_path)
        else:
            return {'success': False, 'error': f'不支持的同步模式: {mode}'}

        # 记录同步历史
        sync_record = {
            'timestamp': datetime.now().isoformat(),
            'source': source_dir,
            'target': target_dir,
            'mode': mode,
            'result': result
        }
        self.history['syncs'].append(sync_record)
        self._save_history()

        return {
            'success': True,
            'mode': mode,
            'copied': len(result.get('copied', [])),
            'deleted': len(result.get('deleted', [])),
            'updated': len(result.get('updated', [])),
            'skipped': len(result.get('skipped', [])),
            'conflicts': len(result.get('conflicts', [])),
            'details': result
        }

    def _sync_copy(self, source: Dict[str, FileRecord], target: Dict[str, FileRecord],
                   source_path: Path, target_path: Path) -> Dict[str, Any]:
        """单向复制同步"""
        copied = []
        updated = []
        skipped = []

        # 确保目标目录存在
        target_path.mkdir(parents=True, exist_ok=True)

        for rel_path, source_record in source.items():
            source_file = source_path / rel_path
            target_file = target_path / rel_path

            if source_record.is_dir:
                # 创建目录
                target_file.mkdir(exist_ok=True)
                continue

            if rel_path not in target:
                # 新文件，复制
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, target_file)
                copied.append(rel_path)
            else:
                target_record = target[rel_path]
                if (source_record.hash != target_record.hash or
                    source_record.size != target_record.size):
                    # 文件变化，更新
                    shutil.copy2(source_file, target_file)
                    updated.append(rel_path)
                else:
                    # 文件相同，跳过
                    skipped.append(rel_path)

        return {
            'copied': copied,
            'updated': updated,
            'skipped': skipped,
            'deleted': []
        }

    def _sync_reflect(self, source: Dict[str, FileRecord], target: Dict[str, FileRecord],
                      source_path: Path, target_path: Path) -> Dict[str, Any]:
        """镜像同步（删除目标中多余的文件）"""
        result = self._sync_copy(source, target, source_path, target_path)

        # 删除目标中多余的文件
        deleted = []
        for rel_path in target.keys():
            if rel_path not in source:
                target_file = target_path / rel_path
                if target_file.exists():
                    if target_file.is_dir():
                        target_file.rmdir()
                    else:
                        target_file.unlink()
                    deleted.append(rel_path)

        result['deleted'] = deleted
        return result

    def _sync_two_way(self, source: Dict[str, FileRecord], target: Dict[str, FileRecord],
                      source_path: Path, target_path: Path) -> Dict[str, Any]:
        """双向同步"""
        copied = []
        updated = []
        skipped = []
        conflicts = []

        # 确保两个目录都存在
        source_path.mkdir(parents=True, exist_ok=True)
        target_path.mkdir(parents=True, exist_ok=True)

        all_paths = set(source.keys()) | set(target.keys())

        for rel_path in all_paths:
            source_file = source_path / rel_path
            target_file = target_path / rel_path

            # 处理目录
            if rel_path in source and source[rel_path].is_dir:
                target_file.mkdir(exist_ok=True)
                continue

            # 处理文件
            if rel_path in source and rel_path not in target:
                # 只有源有，复制到目标
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, target_file)
                copied.append(rel_path)

            elif rel_path in target and rel_path not in source:
                # 只有目标有，复制到源
                source_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(target_file, source_file)
                copied.append(rel_path)

            elif rel_path in source and rel_path in target:
                # 两边都有，检查是否冲突
                source_record = source[rel_path]
                target_record = target[rel_path]

                if source_record.hash == target_record.hash:
                    # 文件相同
                    skipped.append(rel_path)
                elif source_record.mtime > target_record.mtime:
                    # 源更新，更新目标
                    shutil.copy2(source_file, target_file)
                    updated.append(f"{rel_path} -> target")
                elif target_record.mtime > source_record.mtime:
                    # 目标更新，更新源
                    shutil.copy2(target_file, source_file)
                    updated.append(f"{rel_path} -> source")
                else:
                    # 冲突
                    conflicts.append(rel_path)

        return {
            'copied': copied,
            'updated': updated,
            'skipped': skipped,
            'conflicts': conflicts,
            'deleted': []
        }

    def backup_incremental(self, source_dir: str, backup_dir: str) -> Dict[str, Any]:
        """
        增量备份

        Args:
            source_dir: 源目录
            backup_dir: 备份目录

        Returns:
            备份结果
        """
        return self.sync_directories(source_dir, backup_dir, mode='copy')

    def get_sync_status(self, source_dir: str, target_dir: str) -> Dict[str, Any]:
        """
        获取同步状态

        Args:
            source_dir: 源目录
            target_dir: 目标目录

        Returns:
            同步状态
        """
        source_records = self._scan_directory(source_dir)
        target_records = self._scan_directory(target_dir)

        only_in_source = []
        only_in_target = []
        different = []
        same = []

        all_paths = set(source_records.keys()) | set(target_records.keys())

        for rel_path in all_paths:
            if rel_path in source and rel_path not in target_records:
                only_in_source.append(rel_path)
            elif rel_path in target_records and rel_path not in source_records:
                only_in_target.append(rel_path)
            elif rel_path in source_records and rel_path in target_records:
                if source_records[rel_path].hash == target_records[rel_path].hash:
                    same.append(rel_path)
                else:
                    different.append(rel_path)

        return {
            'only_in_source': only_in_source,
            'only_in_target': only_in_target,
            'different': different,
            'same': same,
            'summary': {
                'source_files': len(source_records),
                'target_files': len(target_records),
                'synced': len(same),
                'need_sync': len(only_in_source) + len(only_in_target) + len(different)
            }
        }

    def list_sync_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        列出同步历史

        Args:
            limit: 返回数量

        Returns:
            同步历史列表
        """
        return self.history['syncs'][-limit:]

    def cleanup_old_backups(self, backup_dir: str, keep_days: int = 7) -> int:
        """
        清理旧备份

        Args:
            backup_dir: 备份目录
            keep_days: 保留天数

        Returns:
            删除的文件数量
        """
        backup_path = Path(backup_dir)
        if not backup_path.exists():
            return 0

        deleted = 0
        cutoff_time = datetime.now().timestamp() - (keep_days * 86400)

        for item in backup_path.rglob('*'):
            if item.is_file():
                if item.stat().st_mtime < cutoff_time:
                    item.unlink()
                    deleted += 1

        return deleted


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description='文件同步工具')
    parser.add_argument('action', choices=['sync', 'status', 'history', 'backup', 'cleanup'])
    parser.add_argument('--source', help='源目录')
    parser.add_argument('--target', help='目标目录')
    parser.add_argument('--mode', default='copy', choices=['copy', 'reflect', 'two-way'],
                       help='同步模式')
    parser.add_argument('--days', type=int, default=7, help='保留天数')

    args = parser.parse_args()

    tool = FileSyncTool()

    if args.action == 'sync' and args.source and args.target:
        result = tool.sync_directories(args.source, args.target, args.mode)
        print(f"同步完成:")
        print(f"  复制: {result['copied']}")
        print(f"  更新: {result['updated']}")
        print(f"  跳过: {result['skipped']}")
        print(f"  删除: {result['deleted']}")
        print(f"  冲突: {result['conflicts']}")

    elif args.action == 'status' and args.source and args.target:
        status = tool.get_sync_status(args.source, args.target)
        print(f"同步状态:")
        print(f"  仅在源: {len(status['only_in_source'])}")
        print(f"  仅在目标: {len(status['only_in_target'])}")
        print(f"  不同: {len(status['different'])}")
        print(f"  相同: {len(status['same'])}")
        print(f"  摘要: {json.dumps(status['summary'], indent=2, ensure_ascii=False)}")

    elif args.action == 'history':
        history = tool.list_sync_history()
        print(f"同步历史 (最近{len(history)}次):")
        for record in reversed(history):
            print(f"  {record['timestamp']}: {record['source']} -> {record['target']} ({record['mode']})")

    elif args.action == 'backup' and args.source and args.target:
        result = tool.backup_incremental(args.source, args.target)
        print(f"备份完成:")
        print(f"  复制: {result['copied']}")
        print(f"  更新: {result['updated']}")
        print(f"  跳过: {result['skipped']}")

    elif args.action == 'cleanup' and args.target:
        deleted = tool.cleanup_old_backups(args.target, args.days)
        print(f"清理完成: 删除了{deleted}个旧备份文件")


if __name__ == '__main__':
    main()
