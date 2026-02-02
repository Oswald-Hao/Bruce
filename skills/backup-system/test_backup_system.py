#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backup System 测试脚本
测试文件备份、目录备份、增量备份、压缩、恢复等功能
"""

import sys
import os
import tempfile
import shutil
sys.path.insert(0, os.path.dirname(__file__))

from backup_system import BackupSystem


def test_1_initialization():
    """测试1: 初始化"""
    print("测试1: 初始化")

    # 初始化备份系统
    backup = BackupSystem()

    assert backup.backup_log_dir == '/tmp/backup_logs'
    assert os.path.exists(backup.backup_log_dir)

    # 自定义日志目录
    custom_log_dir = tempfile.mkdtemp()
    backup2 = BackupSystem(backup_log_dir=custom_log_dir)
    assert backup2.backup_log_dir == custom_log_dir

    shutil.rmtree(custom_log_dir, ignore_errors=True)

    print("✅ 测试1通过: 初始化正常")
    return True


def test_2_file_backup():
    """测试2: 文件备份"""
    print("\n测试2: 文件备份")

    backup = BackupSystem()

    # 创建测试文件
    source_file = tempfile.mktemp(suffix='.txt')
    dest_file = tempfile.mktemp(suffix='.txt')

    try:
        with open(source_file, 'w') as f:
            f.write('Test content for backup')

        # 备份文件
        success = backup.backup_file(source_file, dest_file)
        assert success == True
        assert os.path.exists(dest_file)

        # 验证内容
        with open(dest_file, 'r') as f:
            content = f.read()
        assert content == 'Test content for backup'

        # 测试不覆盖
        success2 = backup.backup_file(source_file, dest_file, overwrite=False)
        assert success2 == False

        # 测试覆盖
        success3 = backup.backup_file(source_file, dest_file, overwrite=True)
        assert success3 == True

        print("✅ 测试2通过: 文件备份正常")
        return True
    finally:
        for path in [source_file, dest_file]:
            if os.path.exists(path):
                os.unlink(path)


def test_3_file_backup_compress():
    """测试3: 文件备份（压缩）"""
    print("\n测试3: 文件备份（压缩）")

    backup = BackupSystem()

    # 创建测试文件
    source_file = tempfile.mktemp(suffix='.txt')
    dest_file = tempfile.mktemp(suffix='.gz')

    try:
        # 创建较大的测试内容
        test_content = 'Test content for backup\n' * 1000
        with open(source_file, 'w') as f:
            f.write(test_content)

        # 压缩备份
        success = backup.backup_file(source_file, dest_file, compress=True)
        assert success == True
        assert os.path.exists(dest_file)

        # 验证压缩后文件更小
        source_size = os.path.getsize(source_file)
        dest_size = os.path.getsize(dest_file)
        assert dest_size < source_size

        # 验证可以解压读取
        import gzip
        with gzip.open(dest_file, 'rt') as f:
            content = f.read()
        assert content == test_content

        print("✅ 测试3通过: 文件备份（压缩）正常")
        return True
    finally:
        for path in [source_file, dest_file]:
            if os.path.exists(path):
                os.unlink(path)


def test_4_directory_backup():
    """测试4: 目录备份"""
    print("\n测试4: 目录备份")

    backup = BackupSystem()

    # 创建测试目录结构
    source_dir = tempfile.mkdtemp()
    dest_dir = tempfile.mkdtemp()
    dest_path = os.path.join(dest_dir, 'backup')

    try:
        # 创建文件
        os.makedirs(os.path.join(source_dir, 'subdir'))
        with open(os.path.join(source_dir, 'file1.txt'), 'w') as f:
            f.write('Content 1')
        with open(os.path.join(source_dir, 'file2.txt'), 'w') as f:
            f.write('Content 2')
        with open(os.path.join(source_dir, 'subdir', 'file3.txt'), 'w') as f:
            f.write('Content 3')

        # 备份目录（overwrite=True）
        result = backup.backup_directory(source_dir, dest_path, overwrite=True)
        assert result['success'] == True
        assert result['files_copied'] == 3
        assert result['files_skipped'] == 0

        # 验证文件存在
        assert os.path.exists(os.path.join(dest_path, 'file1.txt'))
        assert os.path.exists(os.path.join(dest_path, 'file2.txt'))
        assert os.path.exists(os.path.join(dest_path, 'subdir', 'file3.txt'))

        # 验证内容
        with open(os.path.join(dest_path, 'file1.txt')) as f:
            assert f.read() == 'Content 1'

        print("✅ 测试4通过: 目录备份正常")
        return True
    finally:
        shutil.rmtree(source_dir, ignore_errors=True)
        shutil.rmtree(dest_dir, ignore_errors=True)


def test_5_directory_backup_exclude():
    """测试5: 目录备份（排除规则）"""
    print("\n测试5: 目录备份（排除规则）")

    backup = BackupSystem()

    # 创建测试目录结构
    source_dir = tempfile.mkdtemp()
    dest_dir = tempfile.mkdtemp()
    dest_path = os.path.join(dest_dir, 'backup')

    try:
        # 创建文件
        with open(os.path.join(source_dir, 'file1.txt'), 'w') as f:
            f.write('Content 1')
        with open(os.path.join(source_dir, 'file2.tmp'), 'w') as f:
            f.write('Content 2')
        with open(os.path.join(source_dir, 'file3.log'), 'w') as f:
            f.write('Content 3')

        # 带排除规则备份
        result = backup.backup_directory(
            source_dir,
            dest_path,
            exclude=['*.tmp', '*.log'],
            overwrite=True
        )

        assert result['success'] == True
        assert result['files_copied'] == 1  # 只复制.txt文件
        assert result['files_skipped'] == 2  # 跳过.tmp和.log文件

        # 验证只有.txt文件被复制
        assert os.path.exists(os.path.join(dest_path, 'file1.txt'))
        assert not os.path.exists(os.path.join(dest_path, 'file2.tmp'))
        assert not os.path.exists(os.path.join(dest_path, 'file3.log'))

        print("✅ 测试5通过: 目录备份（排除规则）正常")
        return True
    finally:
        shutil.rmtree(source_dir, ignore_errors=True)
        shutil.rmtree(dest_dir, ignore_errors=True)


def test_6_incremental_backup():
    """测试6: 增量备份"""
    print("\n测试6: 增量备份")

    backup = BackupSystem()

    # 创建源目录和初始备份
    source_dir = tempfile.mkdtemp()
    base_backup_dir = tempfile.mkdtemp()
    base_backup = os.path.join(base_backup_dir, 'base')
    inc_backup_dir = tempfile.mkdtemp()
    inc_backup = os.path.join(inc_backup_dir, 'inc')

    try:
        # 创建初始文件
        with open(os.path.join(source_dir, 'file1.txt'), 'w') as f:
            f.write('Original content 1')
        with open(os.path.join(source_dir, 'file2.txt'), 'w') as f:
            f.write('Original content 2')

        # 完整备份
        result_base = backup.backup_directory(source_dir, base_backup, overwrite=True)
        assert result_base['success'] == True, f"基础备份失败: {result_base.get('error')}"

        # 修改文件1
        with open(os.path.join(source_dir, 'file1.txt'), 'w') as f:
            f.write('Modified content 1')

        # 创建新文件
        with open(os.path.join(source_dir, 'file3.txt'), 'w') as f:
            f.write('New content 3')

        # 增量备份
        result = backup.incremental_backup(
            source_dir,
            inc_backup,
            base_backup=base_backup
        )

        assert result['success'] == True, f"增量备份失败: {result.get('error')}"
        assert result['files_updated'] == 1, f"files_updated错误: {result.get('files_updated')}"
        assert result['files_added'] == 1, f"files_added错误: {result.get('files_added')}"
        assert result['files_unchanged'] == 1, f"files_unchanged错误: {result.get('files_unchanged')}"

        # 验证增量备份中只包含变更和新文件
        assert os.path.exists(os.path.join(inc_backup, 'file1.txt'))
        assert os.path.exists(os.path.join(inc_backup, 'file3.txt'))

        with open(os.path.join(inc_backup, 'file1.txt')) as f:
            assert f.read() == 'Modified content 1'

        print("✅ 测试6通过: 增量备份正常")
        return True
    finally:
        shutil.rmtree(source_dir, ignore_errors=True)
        shutil.rmtree(base_backup_dir, ignore_errors=True)
        shutil.rmtree(inc_backup_dir, ignore_errors=True)


def test_7_restore_file():
    """测试7: 文件恢复"""
    print("\n测试7: 文件恢复")

    backup = BackupSystem()

    # 创建备份文件
    backup_file = tempfile.mktemp(suffix='.txt')
    restore_file = tempfile.mktemp(suffix='.txt')

    try:
        with open(backup_file, 'w') as f:
            f.write('Backup content')

        # 恢复文件
        success = backup.restore_file(backup_file, restore_file)
        assert success == True
        assert os.path.exists(restore_file)

        # 验证内容
        with open(restore_file) as f:
            assert f.read() == 'Backup content'

        print("✅ 测试7通过: 文件恢复正常")
        return True
    finally:
        for path in [backup_file, restore_file]:
            if os.path.exists(path):
                os.unlink(path)


def test_8_restore_directory():
    """测试8: 目录恢复"""
    print("\n测试8: 目录恢复")

    backup = BackupSystem()

    # 创建备份目录
    backup_dir = tempfile.mkdtemp()
    restore_dir = tempfile.mkdtemp()
    restore_path = os.path.join(restore_dir, 'restored')

    try:
        # 创建备份文件
        with open(os.path.join(backup_dir, 'file1.txt'), 'w') as f:
            f.write('Backup content 1')
        with open(os.path.join(backup_dir, 'file2.txt'), 'w') as f:
            f.write('Backup content 2')

        # 恢复目录（overwrite=True）
        result = backup.restore_directory(backup_dir, restore_path, overwrite=True)
        assert result['success'] == True
        assert result['files_restored'] == 2

        # 验证文件
        assert os.path.exists(os.path.join(restore_path, 'file1.txt'))
        assert os.path.exists(os.path.join(restore_path, 'file2.txt'))

        with open(os.path.join(restore_path, 'file1.txt')) as f:
            assert f.read() == 'Backup content 1'

        print("✅ 测试8通过: 目录恢复正常")
        return True
    finally:
        shutil.rmtree(backup_dir, ignore_errors=True)
        shutil.rmtree(restore_dir, ignore_errors=True)


def test_9_backup_info():
    """测试9: 备份信息"""
    print("\n测试9: 备份信息")

    backup = BackupSystem()

    # 文件备份信息
    test_file = tempfile.mktemp(suffix='.txt')
    try:
        with open(test_file, 'w') as f:
            f.write('Test content')

        info = backup.get_backup_info(test_file)
        assert info is not None
        assert info['type'] == 'file'
        assert info['size'] > 0
        assert info['count'] == 0

    finally:
        if os.path.exists(test_file):
            os.unlink(test_file)

    # 目录备份信息
    test_dir = tempfile.mkdtemp()
    try:
        with open(os.path.join(test_dir, 'file1.txt'), 'w') as f:
            f.write('Content 1')
        with open(os.path.join(test_dir, 'file2.txt'), 'w') as f:
            f.write('Content 2')

        info = backup.get_backup_info(test_dir)
        assert info is not None
        assert info['type'] == 'directory'
        assert info['count'] == 2
        assert info['size'] > 0

        print("✅ 测试9通过: 备份信息正常")
        return True
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("Backup System 测试套件")
    print("=" * 60)

    tests = [
        test_1_initialization,
        test_2_file_backup,
        test_3_file_backup_compress,
        test_4_directory_backup,
        test_5_directory_backup_exclude,
        test_6_incremental_backup,
        test_7_restore_file,
        test_8_restore_directory,
        test_9_backup_info
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"❌ 测试失败: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)

    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
