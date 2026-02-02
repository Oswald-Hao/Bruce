#!/usr/bin/env python3
"""
测试 Performance Optimizer
"""

import os
import sys
import tempfile
import shutil
import unittest
from pathlib import Path


# 添加技能目录到路径
sys.path.insert(0, str(Path(__file__).parent))


class TestPerformanceOptimizer(unittest.TestCase):
    """测试 Performance Optimizer"""

    def setUp(self):
        """测试前准备"""
        # 创建临时测试目录
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir, ignore_errors=True)

        # 导入模块
        from performance_optimizer import PerformanceAnalyzer
        self.analyzer = PerformanceAnalyzer(self.test_dir)

        # 创建测试Python文件
        self.test_file = Path(self.test_dir) / "test_code.py"
        self.test_file.write_text('''"""测试代码"""

def simple_function():
    """简单函数"""
    return 1 + 1

def complex_function():
    """复杂函数"""
    result = 0
    for i in range(100):
        if i % 2 == 0:
            result += i
        else:
            result -= i
    return result

class TestClass:
    """测试类"""

    def method1(self):
        """方法1"""
        pass

    def method2(self):
        """方法2"""
        pass
''')

    def test_analyze_complexity(self):
        """测试分析代码复杂度"""
        complexity = self.analyzer.analyze_complexity()

        self.assertIn(str(self.test_file), complexity)
        file_data = complexity[str(self.test_file)]
        self.assertIn("cyclomatic", file_data)
        self.assertIn("lines", file_data)
        self.assertGreater(file_data["cyclomatic"], 0)

    def test_analyze_resources(self):
        """测试分析资源使用"""
        resources = self.analyzer.analyze_resources()

        self.assertIn("total_size", resources)
        self.assertIn("file_count", resources)
        self.assertIn("largest_files", resources)
        self.assertGreater(resources["file_count"], 0)

    def test_generate_recommendations(self):
        """测试生成优化建议"""
        # 先执行分析
        self.analyzer.analyze_complexity()
        self.analyzer.analyze_resources()

        recommendations = self.analyzer.generate_recommendations()

        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)

    def test_analyze(self):
        """测试完整分析流程"""
        results = self.analyzer.analyze()

        self.assertIn("timestamp", results)
        self.assertIn("analysis", results)
        self.assertIn("complexity", results["analysis"])
        self.assertIn("resources", results["analysis"])

    def test_save_results(self):
        """测试保存结果"""
        # 先执行分析
        self.analyzer.analyze()

        # 保存结果
        output_file = Path(self.test_dir) / "performance_report.json"
        self.analyzer.save_results(output_file)

        self.assertTrue(output_file.exists())

        # 验证JSON格式
        import json
        with open(output_file, 'r') as f:
            data = json.load(f)

        self.assertIn("timestamp", data)
        self.assertIn("analysis", data)


if __name__ == '__main__':
    unittest.main(verbosity=2)
