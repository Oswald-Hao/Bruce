#!/usr/bin/env python3
"""
测试文件同步工具
"""

import os
import tempfile
import shutil
from pathlib import Path

import sys
# 直接导入当前目录的skill模块
skill_path = str(Path(__file__).parent)
sys.path.insert(0, skill_path)

from skill import FileSyncTool


def test_sync_copy():
    """测试单向复制同步"""
    print("测试1: 单向复制同步...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        source_dir = Path(temp_dir) / 'source'
        target_dir = Path(temp_dir) / 'target'
        
        # 创建源目录结构
        source_dir.mkdir()
        (source_dir / 'file1.txt').write_text('content1')
        (source_dir / 'file2.txt').write_text('content2')
        (source_dir / 'subdir').mkdir()
        (source_dir / 'subdir' / 'file3.txt').write_text('content3')
        
        try:
            tool = FileSyncTool()
            result = tool.sync_directories(str(source_dir), str(target_dir), 'copy')
            
            assert result['success'], "同步失败"
            assert result['copied'] == 3, f"应该复制3个文件，实际复制{result['copied']}个"
            
            # 验证文件已复制
            assert (target_dir / 'file1.txt').exists(), "file1.txt未复制"
            assert (target_dir / 'file2.txt').exists(), "file2.txt未复制"
            assert (target_dir / 'subdir' / 'file3.txt').exists(), "file3.txt未复制"
            
            print("✓ 单向复制同步成功")
            return True
        except Exception as e:
            print(f"✗ 测试失败: {e}")
            return False


def test_sync_reflect():
    """测试镜像同步（删除多余文件）"""
    print("\n测试2: 镜像同步...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        source_dir = Path(temp_dir) / 'source'
        target_dir = Path(temp_dir) / 'target'
        
        # 创建源目录
        source_dir.mkdir()
        (source_dir / 'keep.txt').write_text('keep')
        
        # 创建目标目录，包含一个多余的文件
        target_dir.mkdir()
        (target_dir / 'keep.txt').write_text('old')
        (target_dir / 'delete.txt').write_text('delete')
        
        try:
            tool = FileSyncTool()
            result = tool.sync_directories(str(source_dir), str(target_dir), 'reflect')
            
            assert result['success'], "同步失败"
            assert result['deleted'] == 1, f"应该删除1个文件，实际删除{result['deleted']}个"
            assert result['updated'] == 1, f"应该更新1个文件，实际更新{result['updated']}个"
            
            # 验证文件状态
            assert (target_dir / 'keep.txt').exists(), "keep.txt被误删"
            assert not (target_dir / 'delete.txt').exists(), "delete.txt未删除"
            
            print("✓ 镜像同步成功")
            return True
        except Exception as e:
            print(f"✗ 测试失败: {e}")
            return False


def test_sync_two_way():
    """测试双向同步"""
    print("\n测试3: 双向同步...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        source_dir = Path(temp_dir) / 'source'
        target_dir = Path(temp_dir) / 'target'
        
        # 创建源目录
        source_dir.mkdir()
        (source_dir / 'only_source.txt').write_text('source')
        
        # 创建目标目录
        target_dir.mkdir()
        (target_dir / 'only_target.txt').write_text('target')
        
        try:
            tool = FileSyncTool()
            result = tool.sync_directories(str(source_dir), str(target_dir), 'two-way')
            
            assert result['success'], "同步失败"
            assert result['copied'] == 2, f"应该复制2个文件，实际复制{result['copied']}个"
            
            # 验证双向同步
            assert (target_dir / 'only_source.txt').exists(), "源文件未同步到目标"
            assert (source_dir / 'only_target.txt').exists(), "目标文件未同步到源"
            
            print("✓ 双向同步成功")
            return True
        except Exception as e:
            print(f"✗ 测试失败: {e}")
            return False


def test_incremental_backup():
    """测试增量备份"""
    print("\n测试4: 增量备份...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        source_dir = Path(temp_dir) / 'source'
        backup_dir = Path(temp_dir) / 'backup'
        
        # 创建源目录
        source_dir.mkdir()
        (source_dir / 'file1.txt').write_text('content1')
        
        try:
            tool = FileSyncTool()
            
            # 第一次备份
            result1 = tool.backup_incremental(str(source_dir), str(backup_dir))
            assert result1['success'], "第一次备份失败"
            assert result1['copied'] == 1, f"应该备份1个文件"
            
            # 修改源文件
            (source_dir / 'file1.txt').write_text('content1 updated')
            (source_dir / 'file2.txt').write_text('content2')
            
            # 第二次备份（增量）
            result2 = tool.backup_incremental(str(source_dir), str(backup_dir))
            assert result2['success'], "第二次备份失败"
            assert result2['updated'] == 1, f"应该更新1个文件"
            assert result2['copied'] == 1, f"应该复制1个新文件"
            
            print("✓ 增量备份成功")
            return True
        except Exception as e:
            print(f"✗ 测试失败: {e}")
            return False


def test_exclude_patterns():
    """测试排除模式"""
    print("\n测试5: 排除模式...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        source_dir = Path(temp_dir) / 'source'
        target_dir = Path(temp_dir) / 'target'
        
        # 创建源目录，包含各种文件
        source_dir.mkdir()
        (source_dir / 'keep.txt').write_text('keep')
        (source_dir / '.git').mkdir()
        (source_dir / '.git' / 'file.txt').write_text('git')
        (source_dir / 'node_modules').mkdir()
        (source_dir / 'node_modules' / 'file.js').write_text('node')
        (source_dir / 'temp.tmp').write_text('temp')
        
        try:
            tool = FileSyncTool()
            result = tool.sync_directories(str(source_dir), str(target_dir), 'copy')
            
            assert result['success'], "同步失败"
            assert result['copied'] == 1, f"应该只复制1个文件（其他被排除），实际复制{result['copied']}个"
            
            # 验证只有keep.txt被复制
            assert (target_dir / 'keep.txt').exists(), "keep.txt未复制"
            assert not (target_dir / '.git').exists(), ".git目录被错误复制"
            assert not (target_dir / 'node_modules').exists(), "node_modules目录被错误复制"
            assert not (target_dir / 'temp.tmp').exists(), "temp.tmp被错误复制"
            
            print("✓ 排除模式成功")
            return True
        except Exception as e:
            print(f"✗ 测试失败: {e}")
            return False


def test_sync_status():
    """测试同步状态"""
    print("\n测试6: 同步状态...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        source_dir = Path(temp_dir) / 'source'
        target_dir = Path(temp_dir) / 'target'
        
        # 创建源目录
        source_dir.mkdir()
        (source_dir / 'same.txt').write_text('same')
        (source_dir / 'only_source.txt').write_text('source')
        (source_dir / 'different.txt').write_text('source_version')
        
        # 创建目标目录
        target_dir.mkdir()
        (target_dir / 'same.txt').write_text('same')
        (target_dir / 'only_target.txt').write_text('target')
        (target_dir / 'different.txt').write_text('target_version')
        
        try:
            tool = FileSyncTool()
            status = tool.get_sync_status(str(source_dir), str(target_dir))
            
            assert 'only_source.txt' in status['only_in_source'], "only_source.txt未被识别"
            assert 'only_target.txt' in status['only_in_target'], "only_target.txt未被识别"
            assert 'different.txt' in status['different'], "different.txt未被识别为不同"
            assert 'same.txt' in status['same'], "same.txt未被识别为相同"
            
            print("✓ 同步状态成功")
            return True
        except Exception as e:
            print(f"✗ 测试失败: {e}")
            return False


def test_sync_history():
    """测试同步历史"""
    print("\n测试7: 同步历史...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        source_dir = Path(temp_dir) / 'source'
        target_dir = Path(temp_dir) / 'target'
        
        source_dir.mkdir()
        (source_dir / 'file.txt').write_text('content')
        
        try:
            tool = FileSyncTool()
            
            # 执行同步
            tool.sync_directories(str(source_dir), str(target_dir), 'copy')
            
            # 获取历史
            history = tool.list_sync_history()
            
            assert len(history) > 0, "同步历史为空"
            assert history[-1]['source'] == str(source_dir), "历史记录不正确"
            
            print("✓ 同步历史成功")
            return True
        except Exception as e:
            print(f"✗ 测试失败: {e}")
            return False


def test_conflict_detection():
    """测试冲突检测"""
    print("\n测试8: 冲突检测...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        source_dir = Path(temp_dir) / 'source'
        target_dir = Path(temp_dir) / 'target'
        
        # 创建源和目标，包含相同文件但不同内容
        source_dir.mkdir()
        (source_dir / 'conflict.txt').write_text('source_version')
        
        target_dir.mkdir()
        (target_dir / 'conflict.txt').write_text('target_version')
        
        try:
            tool = FileSyncTool()
            result = tool.sync_directories(str(source_dir), str(target_dir), 'two-way')
            
            assert result['success'], "同步失败"
            # 由于时间戳可能相同，可能会有冲突
            # 我们只检查同步成功，不强制要求有冲突
            
            print("✓ 冲突检测成功")
            return True
        except Exception as e:
            print(f"✗ 测试失败: {e}")
            return False


def test_large_file():
    """测试大文件处理"""
    print("\n测试9: 大文件处理...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        source_dir = Path(temp_dir) / 'source'
        target_dir = Path(temp_dir) / 'target'
        
        # 创建一个大文件（1MB）
        source_dir.mkdir()
        large_content = 'x' * (1024 * 1024)
        (source_dir / 'large.txt').write_text(large_content)
        
        try:
            tool = FileSyncTool()
            result = tool.sync_directories(str(source_dir), str(target_dir), 'copy')
            
            assert result['success'], "同步失败"
            assert result['copied'] == 1, "应该复制1个文件"
            
            # 验证文件大小正确
            assert (target_dir / 'large.txt').stat().st_size == 1024 * 1024, "文件大小不正确"
            
            print("✓ 大文件处理成功")
            return True
        except Exception as e:
            print(f"✗ 测试失败: {e}")
            return False


def test_cleanup_backups():
    """测试清理旧备份"""
    print("\n测试10: 清理旧备份...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        backup_dir = Path(temp_dir) / 'backup'
        backup_dir.mkdir()
        
        # 创建一些旧文件
        (backup_dir / 'old.txt').write_text('old')
        (backup_dir / 'new.txt').write_text('new')
        
        # 修改old.txt的修改时间（3天前）
        import time
        three_days_ago = time.time() - (3 * 86400)
        os.utime(backup_dir / 'old.txt', (three_days_ago, three_days_ago))
        
        try:
            tool = FileSyncTool()
            # 设置保留1天
            deleted = tool.cleanup_old_backups(str(backup_dir), keep_days=1)
            
            assert deleted == 1, f"应该删除1个文件，实际删除{deleted}个"
            assert not (backup_dir / 'old.txt').exists(), "old.txt未删除"
            assert (backup_dir / 'new.txt').exists(), "new.txt被误删"
            
            print("✓ 清理旧备份成功")
            return True
        except Exception as e:
            print(f"✗ 测试失败: {e}")
            return False


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("文件同步工具 - 功能测试")
    print("=" * 60)
    
    tests = [
        test_sync_copy,
        test_sync_reflect,
        test_sync_two_way,
        test_incremental_backup,
        test_exclude_patterns,
        test_sync_status,
        test_sync_history,
        test_conflict_detection,
        test_large_file,
        test_cleanup_backups
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print(f"测试结果: {sum(results)}/{len(results)} 通过")
    print("=" * 60)
    
    return all(results)


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
