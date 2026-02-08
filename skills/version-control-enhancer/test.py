#!/usr/bin/env python3
"""
版本控制增强器测试
"""

import os
import sys
import unittest
import tempfile
import shutil
import subprocess

# 添加技能目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from version_control import VersionControl


class TestVersionControl(unittest.TestCase):
    """版本控制器测试"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.temp_dir = tempfile.mkdtemp()
        cls.repo_path = os.path.join(cls.temp_dir, "test_repo")
        os.makedirs(cls.repo_path)

        # 初始化Git仓库
        subprocess.run(["git", "init"], cwd=cls.repo_path, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Bruce"], cwd=cls.repo_path, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "bruce@ai.com"], cwd=cls.repo_path, check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        if os.path.exists(cls.temp_dir):
            shutil.rmtree(cls.temp_dir)

    def setUp(self):
        """每个测试前执行"""
        self.vc = VersionControl(self.repo_path)

    def test_01_init(self):
        """测试1: 初始化"""
        vc = VersionControl(self.repo_path)
        self.assertIsNotNone(vc)
        self.assertEqual(vc.repo_path, self.repo_path)

    def test_02_status_no_changes(self):
        """测试2: 状态检查（无变更）"""
        status = self.vc.status()

        self.assertIn("has_changes", status)
        self.assertFalse(status["has_changes"])
        self.assertEqual(len(status["modified"]), 0)
        self.assertEqual(len(status["added"]), 0)

    def test_03_status_with_changes(self):
        """测试3: 状态检查（有变更）"""
        # 创建文件
        test_file = os.path.join(self.repo_path, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")

        status = self.vc.status()

        self.assertTrue(status["has_changes"])
        self.assertIn("test.txt", status["untracked"])

        # 清理
        os.remove(test_file)

    def test_04_smart_commit(self):
        """测试4: 智能提交"""
        # 创建并提交文件
        test_file = os.path.join(self.repo_path, "feature.py")
        with open(test_file, 'w') as f:
            f.write("# feature\n")

        status = self.vc.status()
        self.assertTrue(status["has_changes"])

        result = self.vc.smart_commit("添加新功能")

        self.assertTrue(result)

        # 验证提交成功
        status = self.vc.status()
        self.assertFalse(status["has_changes"])

    def test_05_smart_commit_auto_message(self):
        """测试5: 智能提交（自动生成信息）"""
        # 创建文件
        test_file = os.path.join(self.repo_path, "utils.py")
        with open(test_file, 'w') as f:
            f.write("# utils\n")

        result = self.vc.smart_commit()  # 不提供message，自动生成

        self.assertTrue(result)

        # 验证提交成功
        status = self.vc.status()
        self.assertFalse(status["has_changes"])

    def test_06_create_and_switch_branch(self):
        """测试6: 创建和切换分支"""
        # 创建分支
        result = self.vc.create_branch("feature/test", checkout=True)

        self.assertTrue(result)

        # 验证分支创建
        branches = self.vc.list_branches()
        self.assertIn("feature/test", branches["branches"])

    def test_07_list_branches(self):
        """测试7: 列出分支"""
        # 创建几个分支
        self.vc.create_branch("feature1", checkout=False)
        self.vc.create_branch("feature2", checkout=False)

        branches = self.vc.list_branches()

        self.assertIn("branches", branches)
        self.assertIn("current", branches)
        self.assertIn("master", branches["branches"])
        self.assertIn("feature1", branches["branches"])
        self.assertIn("feature2", branches["branches"])

    def test_08_switch_branch(self):
        """测试8: 切换分支"""
        # 先切换到master
        self.vc.switch_branch("master")

        # 创建并切换到新分支
        self.vc.create_branch("dev", checkout=True)

        # 验证当前分支
        branches = self.vc.list_branches()
        self.assertEqual(branches["current"], "dev")

    def test_09_analyze_history(self):
        """测试9: 分析历史"""
        # 进行几次提交
        for i in range(3):
            test_file = os.path.join(self.repo_path, f"file{i}.py")
            with open(test_file, 'w') as f:
                f.write(f"# file{i}\n")
            self.vc.smart_commit(f"添加文件{i}")

        # 分析历史
        history = self.vc.analyze_history(count=10)

        self.assertIn("total_commits", history)
        self.assertIn("commits", history)
        self.assertIn("authors", history)
        self.assertGreater(history["total_commits"], 2)
        self.assertIn("top_author", history)

    def test_10_get_diff(self):
        """测试10: 获取差异"""
        # 创建两个文件并提交
        file1 = os.path.join(self.repo_path, "file1.txt")
        with open(file1, 'w') as f:
            f.write("version 1")

        self.vc.smart_commit("第一个版本")

        # 修改文件
        with open(file1, 'w') as f:
            f.write("version 2")

        file2 = os.path.join(self.repo_path, "file2.txt")
        with open(file2, 'w') as f:
            f.write("new file")

        self.vc.smart_commit("修改文件并添加新文件")

        # 获取差异
        diff = self.vc.get_diff()

        self.assertIn("version 1", diff)
        self.assertIn("version 2", diff)

        # 获取特定文件的差异
        file_diff = self.vc.get_diff(file1)

        self.assertIn("version 1", file_diff)
        self.assertIn("version 2", file_diff)

    def test_11_commit_message_generation(self):
        """测试11: 提交信息生成"""
        # 创建多个文件
        test_dir = os.path.join(self.repo_path, "src")
        os.makedirs(test_dir)

        for i in range(3):
            file_path = os.path.join(test_dir, f"module{i}.py")
            with open(file_path, 'w') as f:
                f.write(f"# module{i}\n")

        # 获取状态
        status = self.vc.status()

        # 验证生成正确的提交信息
        message = self.vc._generate_commit_message(status)

        self.assertIn("添加", message)

        # 清理
        shutil.rmtree(test_dir)


def run_tests():
    """运行测试"""
    print("=" * 60)
    print("版本控制增强器 - 测试套件")
    print("=" * 60)

    # 创建测试套件
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestVersionControl)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 输出测试结果摘要
    print("\n" + "=" * 60)
    print(f"测试总数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("=" * 60)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
