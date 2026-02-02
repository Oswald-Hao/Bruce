#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Sync Tool 测试脚本
测试单向同步、双向同步、文件对比等功能
"""

import sys
import os
import tempfile
import shutil
sys.path.insert(0, os.path.dirname(__file__))

from file_sync import FileSync


def test_1_initialization():
    """测试1: 初始化"""
    print("测试1: 初始化")

    sync = FileSync()

    assert sync.sync_log == []
    assert sync.verbose == False

    # 详细模式
    sync_verbose = FileSync(verbose=True)
    assert sync_verbose.verbose == True

    print("✅ 测试1通过: 初始化正常")
    return True


def test_2_collect_files():
    """测试2: 收集文件"""
    print("\n测试2: 收集文件")

    sync = FileSync()
    test_dir = tempfile.mkdtemp()

    try:
        # 创建测试文件
        os.makedirs(os.path.join(test_dir, 'subdir'))
        with open(os.path.join(test_dir, 'file1.txt'), 'w') as f:
            f.write('Content 1')
        with open(os.path.join(test_dir, 'file2.txt'), 'w') as f:
            f.write('Content 2')
        with open(os.path.join(test_dir, 'subdir', 'file3.txt'), 'w') as f:
            f.write('Content 3')
        with open(os.path.join(test_dir, 'file.tmp'), 'w') as f:
            f.write('Temp file')

        # 收集所有文件
        files = sync._collect_files(test_dir)
        assert len(files) == 4

        # 带排除规则
        files_excluded = sync._collect_files(test_dir, exclude_patterns=['*.tmp'])
        assert len(files_excluded) == 3
        assert 'file.tmp' not in files_excluded

        print("✅ 测试2通过: 收集文件正常")
        return True
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_3_one_way_sync():
    """测试3: 单向同步"""
    print("\n测试3: 单向同步")

    sync = FileSync()
    source_dir = tempfile.mkdtemp()
    target_dir = tempfile.mkdtemp()
    target_path = os.path.join(target_dir, 'sync')

    try:
        # 创建源文件
        with open(os.path.join(source_dir, 'file1.txt'), 'w') as f:
            f.write('Source content 1')
        with open(os.path.join(source_dir, 'file2.txt'), 'w') as f:
            f.write('Source content 2')

        # 单向同步
        result = sync.sync_one_way(source_dir, target_path, dry_run=False)

        assert result['success'] == True
        assert result['files_copied'] == 2

        # 验证文件已复制
        assert os.path.exists(os.path.join(target_path, 'file1.txt'))
        assert os.path.exists(os.path.join(target_path, 'file2.txt'))

        # 验证内容
        with open(os.path.join(target_path, 'file1.txt')) as f:
            assert f.read() == 'Source content 1'

        print("✅ 测试3通过: 单向同步正常")
        return True
    finally:
        shutil.rmtree(source_dir, ignore_errors=True)
        shutil.rmtree(target_dir, ignore_errors=True)


def test_4_two_way_sync():
    """测试4: 双向同步"""
    print("\n测试4: 双向同步")

    sync = FileSync()
    dir1 = tempfile.mkdtemp()
    dir2 = tempfile.mkdtemp()
    path1 = os.path.join(dir1, 'sync')
    path2 = os.path.join(dir2, 'sync')

    try:
        # 创建目录
        os.makedirs(path1, exist_ok=True)
        os.makedirs(path2, exist_ok=True)

        # 创建dir1的文件
        with open(os.path.join(path1, 'file1.txt'), 'w') as f:
            f.write('Dir1 content 1')

        # 创建dir2的文件
        with open(os.path.join(path2, 'file2.txt'), 'w') as f:
            f.write('Dir2 content 2')

        # 双向同步
        result = sync.sync_two_way(path1, path2, dry_run=False)

        assert result['success'] == True
        assert result['synced_to_dir2'] == 1  # file1 → dir2
        assert result['synced_to_dir1'] == 1  # file2 → dir1

        # 验证双方都有两个文件
        assert os.path.exists(os.path.join(path1, 'file1.txt'))
        assert os.path.exists(os.path.join(path1, 'file2.txt'))
        assert os.path.exists(os.path.join(path2, 'file1.txt'))
        assert os.path.exists(os.path.join(path2, 'file2.txt'))

        print("✅ 测试4通过: 双向同步正常")
        return True
    finally:
        shutil.rmtree(dir1, ignore_errors=True)
        shutil.rmtree(dir2, ignore_errors=True)


def test_5_sync_stats():
    """测试5: 同步统计"""
    print("\n测试5: 同步统计")

    sync = FileSync()
    source_dir = tempfile.mkdtemp()
    target_dir = tempfile.mkdtemp()
    source_path = os.path.join(source_dir, 'files')
    target_path = os.path.join(target_dir, 'files')

    try:
        # 创建目录
        os.makedirs(source_path, exist_ok=True)
        os.makedirs(target_path, exist_ok=True)

        # 创建源文件
        for i in range(5):
            with open(os.path.join(source_path, f'file{i}.txt'), 'w') as f:
                f.write(f'Content {i}')

        # 创建部分目标文件
        with open(os.path.join(target_path, 'file0.txt'), 'w') as f:
            f.write('Different content')

        stats = sync.get_sync_stats(source_path, target_path)

        assert stats['source_files'] == 5
        assert stats['target_files'] == 1
        assert stats['new_in_source'] == 4  # 4个新文件
        assert stats['total_size_bytes'] > 0

        print("✅ 测试5通过: 同步统计正常")
        return True
    finally:
        shutil.rmtree(source_dir, ignore_errors=True)
        shutil.rmtree(target_dir, ignore_errors=True)


def test_6_compare_dirs():
    """测试6: 比较目录"""
    print("\n测试6: 比较目录")

    sync = FileSync()
    dir1 = tempfile.mkdtemp()
    dir2 = tempfile.mkdtemp()
    path1 = os.path.join(dir1, 'files')
    path2 = os.path.join(dir2, 'files')

    try:
        # 创建目录
        os.makedirs(path1, exist_ok=True)
        os.makedirs(path2, exist_ok=True)

        # 相同的文件
        common_content = 'Common content'
        with open(os.path.join(path1, 'common.txt'), 'w') as f:
            f.write(common_content)
        with open(os.path.join(path2, 'common.txt'), 'w') as f:
            f.write(common_content)

        # dir1独有的文件
        with open(os.path.join(path1, 'only1.txt'), 'w') as f:
            f.write('Only in dir1')

        # dir2独有的文件
        with open(os.path.join(path2, 'only2.txt'), 'w') as f:
            f.write('Only in dir2')

        diff = sync.compare_dirs(path1, path2)

        assert 'only1.txt' in diff['files_only_in_dir1']
        assert 'only2.txt' in diff['files_only_in_dir2']
        assert 'common.txt' in diff['files_identical']

        print("✅ 测试6通过: 比较目录正常")
        return True
    finally:
        shutil.rmtree(dir1, ignore_errors=True)
        shutil.rmtree(dir2, ignore_errors=True)


def test_7_exclude_patterns():
    """测试7: 排除规则"""
    print("\n测试7: 排除规则")

    sync = FileSync()
    source_dir = tempfile.mkdtemp()
    target_dir = tempfile.mkdtemp()
    source_path = os.path.join(source_dir, 'files')
    target_path = os.path.join(target_dir, 'files')

    try:
        # 创建目录
        os.makedirs(source_path, exist_ok=True)

        # 创建各种文件
        with open(os.path.join(source_path, 'file1.txt'), 'w') as f:
            f.write('Content 1')
        with open(os.path.join(source_path, 'file2.tmp'), 'w') as f:
            f.write('Temp content')
        with open(os.path.join(source_path, 'file3.log'), 'w') as f:
            f.write('Log content')
        with open(os.path.join(source_path, 'file4.txt'), 'w') as f:
            f.write('Content 4')

        # 同步时排除.tmp和.log
        result = sync.sync_one_way(
            source_path,
            target_path,
            exclude_patterns=['*.tmp', '*.log'],
            dry_run=False
        )

        assert result['success'] == True
        assert result['files_copied'] == 2  # 只复制.txt文件

        # 验证排除的文件未被复制
        assert os.path.exists(os.path.join(target_path, 'file1.txt'))
        assert not os.path.exists(os.path.join(target_path, 'file2.tmp'))
        assert not os.path.exists(os.path.join(target_path, 'file3.log'))

        print("✅ 测试7通过: 排除规则正常")
        return True
    finally:
        shutil.rmtree(source_dir, ignore_errors=True)
        shutil.rmtree(target_dir, ignore_errors=True)


def test_8_dry_run():
    """测试8: 预演模式"""
    print("\n测试8: 预演模式")

    sync = FileSync()
    source_dir = tempfile.mkdtemp()
    target_dir = tempfile.mkdtemp()
    target_path = os.path.join(target_dir, 'sync')

    try:
        # 创建源文件
        with open(os.path.join(source_dir, 'file1.txt'), 'w') as f:
            f.write('Content')

        # 预演模式
        result = sync.sync_one_way(source_dir, target_path, dry_run=True)

        assert result['dry_run'] == True
        assert result['files_copied'] == 1

        # 验证文件未被实际复制
        assert not os.path.exists(os.path.join(target_path, 'file1.txt'))

        # 检查日志中有预演标记
        log_has_preview = any('[预演]' in log for log in sync.get_sync_log())
        assert log_has_preview

        print("✅ 测试8通过: 预演模式正常")
        return True
    finally:
        shutil.rmtree(source_dir, ignore_errors=True)
        shutil.rmtree(target_dir, ignore_errors=True)


def test_9_sync_log():
    """测试9: 同步日志"""
    print("\n测试9: 同步日志")

    sync = FileSync(verbose=True)
    source_dir = tempfile.mkdtemp()
    target_dir = tempfile.mkdtemp()
    target_path = os.path.join(target_dir, 'sync')

    try:
        # 创建源文件
        with open(os.path.join(source_dir, 'file1.txt'), 'w') as f:
            f.write('Content')

        # 执行同步
        sync.sync_one_way(source_dir, target_path, dry_run=False)

        # 检查日志
        logs = sync.get_sync_log()
        assert len(logs) > 0
        assert any('单向同步' in log for log in logs)
        assert any('复制:' in log for log in logs)

        # 清空日志
        sync.clear_sync_log()
        assert len(sync.get_sync_log()) == 0

        print("✅ 测试9通过: 同步日志正常")
        return True
    finally:
        shutil.rmtree(source_dir, ignore_errors=True)
        shutil.rmtree(target_dir, ignore_errors=True)


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("File Sync Tool 测试套件")
    print("=" * 60)

    tests = [
        test_1_initialization,
        test_2_collect_files,
        test_3_one_way_sync,
        test_4_two_way_sync,
        test_5_sync_stats,
        test_6_compare_dirs,
        test_7_exclude_patterns,
        test_8_dry_run,
        test_9_sync_log
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
