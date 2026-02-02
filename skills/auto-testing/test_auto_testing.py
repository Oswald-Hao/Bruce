#!/usr/bin/env python3
"""
测试 Auto Testing Framework
"""

import os
import sys
import tempfile
import shutil
import unittest
from pathlib import Path


# 添加技能目录到路径
sys.path.insert(0, str(Path(__file__).parent))


class TestAutoTesting(unittest.TestCase):
    """测试 Auto Testing Framework"""

    def setUp(self):
        """测试前准备"""
        # 创建临时测试目录
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir, ignore_errors=True)

        # 导入模块
        from auto_testing import AutoTesting
        self.tester = AutoTesting(self.test_dir)

    def test_init_framework(self):
        """测试初始化测试框架"""
        result = self.tester.init_framework()

        self.assertTrue(result)
        self.assertTrue(self.tester.test_dir.exists())
        self.assertTrue((self.tester.test_dir / "__init__.py").exists())
        self.assertTrue((self.tester.test_dir / "test_example.py").exists())
        self.assertTrue((self.tester.project_path / "pytest.ini").exists())

    def test_run_tests(self):
        """测试运行测试"""
        # 先初始化
        self.tester.init_framework()

        # 运行测试
        results = self.tester.run_tests()

        self.assertGreater(results["total"], 0)
        self.assertGreaterEqual(results["passed"], 0)
        self.assertGreaterEqual(results["failed"], 0)
        self.assertGreaterEqual(results["duration"], 0)

    def test_generate_test_file(self):
        """测试生成测试文件"""
        module_name = "calculator"
        functions = ["add", "subtract", "multiply", "divide"]

        test_file = self.tester.generate_test_file(module_name, functions)

        self.assertTrue(os.path.exists(test_file))
        content = Path(test_file).read_text()
        self.assertIn("test_add", content)
        self.assertIn("test_subtract", content)
        self.assertIn("test_multiply", content)
        self.assertIn("test_divide", content)

    def test_print_summary(self):
        """测试打印摘要"""
        # 先初始化并运行测试
        self.tester.init_framework()
        self.tester.run_tests()

        # 测试打印摘要（不应抛出异常）
        try:
            self.tester.print_summary()
            summary_exists = (self.tester.project_path / "test_results.json").exists()
            self.assertTrue(summary_exists)
        except Exception as e:
            self.fail(f"print_summary抛出异常: {e}")

    def test_save_results(self):
        """测试保存结果"""
        # 先初始化并运行测试
        self.tester.init_framework()
        self.tester.run_tests()
        self.tester.print_summary()  # 保存结果

        # 检查JSON结果文件
        results_file = self.tester.project_path / "test_results.json"
        self.assertTrue(results_file.exists())

        # 验证JSON格式
        import json
        with open(results_file, 'r') as f:
            data = json.load(f)

        self.assertIn("timestamp", data)
        self.assertIn("total", data)
        self.assertIn("passed", data)
        self.assertIn("failed", data)


if __name__ == '__main__':
    unittest.main(verbosity=2)
