#!/usr/bin/env python3
"""
AI工具优化器 - 测试套件
"""

import unittest
import os
import json
import shutil

# 导入主模块
from main import AIToolOptimizer
from optimizer import PromptOptimizer
from token_analyzer import TokenAnalyzer
from model_selector import ModelSelector
from cache_manager import CacheManager
from quality_evaluator import QualityEvaluator


class TestPromptOptimizer(unittest.TestCase):
    """提示词优化器测试"""

    def setUp(self):
        """测试前准备"""
        config = {
            'models': {
                'gpt-4': {
                    'cost_per_1k_input': 0.03
                },
                'gpt-3.5-turbo': {
                    'cost_per_1k_input': 0.0005
                }
            },
            'storage': {}
        }
        self.optimizer = PromptOptimizer(config)

    def test_optimize_simple_prompt(self):
        """测试1: 优化简单提示词"""
        prompt = "请帮我解释什么是人工智能"
        result = self.optimizer.optimize(prompt)

        self.assertIsNotNone(result)
        self.assertIn('optimized_prompt', result)
        self.assertEqual(result['original_prompt'], prompt)
        self.assertTrue(len(result['improvements']) > 0)

        print("✓ 测试1通过: 简单提示词优化成功")

    def test_optimize_long_prompt(self):
        """测试2: 优化长提示词"""
        prompt = "我希望你能帮我解释人工智能" * 20
        result = self.optimizer.optimize(prompt)

        self.assertIsNotNone(result)
        self.assertLess(result['optimized_token_count'], result['original_token_count'])

        print("✓ 测试2通过: 长提示词优化成功")

    def test_optimize_with_task_type(self):
        """测试3: 带任务类型的优化"""
        prompt = "写一个函数"
        result = self.optimizer.optimize(prompt, task_type='code')

        optimized = result['optimized_prompt']
        self.assertIn('代码', optimized) or self.assertIn('function', optimized)

        print("✓ 测试3通过: 带任务类型优化成功")

    def test_token_count(self):
        """测试4: Token计数"""
        text = "这是一个测试"
        count = self.optimizer._count_tokens(text)

        self.assertGreater(count, 0)

        print("✓ 测试4通过: Token计数成功")


class TestTokenAnalyzer(unittest.TestCase):
    """Token分析器测试"""

    @classmethod
    def setUpClass(cls):
        """测试类准备"""
        cls.test_dir = "test_token_data"
        cls.original_dir = os.getcwd()
        os.makedirs(cls.test_dir, exist_ok=True)
        os.chdir(cls.test_dir)

    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        os.chdir(cls.original_dir)
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)

    def setUp(self):
        """测试前准备"""
        config = {
            'models': {
                'gpt-3.5-turbo': {
                    'cost_per_1k_input': 0.0005
                }
            },
            'storage': {
                'usage_db': 'test_usage_db.json'
            }
        }
        self.analyzer = TokenAnalyzer(config)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists('test_usage_db.json'):
            os.remove('test_usage_db.json')

    def test_analyze_usage(self):
        """测试5: 分析使用情况"""
        result = self.analyzer.analyze(days=7)

        self.assertIn('total_requests', result)
        self.assertIn('total_tokens', result)
        self.assertIn('total_cost', result)

        print("✓ 测试5通过: 使用分析成功")

    def test_record_usage(self):
        """测试6: 记录使用"""
        self.analyzer.record_usage(
            model='gpt-3.5-turbo',
            tokens=1000,
            cost=0.001,
            prompt_hash='abc123'
        )

        result = self.analyzer.analyze()
        self.assertEqual(result['total_requests'], 1)

        print("✓ 测试6通过: 使用记录成功")

    def test_get_top_prompts(self):
        """测试7: 获取常用提示词"""
        # 记录多个使用
        for i in range(10):
            self.analyzer.record_usage(
                model='gpt-3.5-turbo',
                tokens=1000,
                cost=0.001,
                prompt_hash='hash1' if i < 5 else f'hash{i}'
            )

        top_prompts = self.analyzer.get_top_prompts()
        self.assertGreater(len(top_prompts), 0)
        self.assertEqual(top_prompts[0]['count'], 5)

        print("✓ 测试7通过: 常用提示词获取成功")


class TestModelSelector(unittest.TestCase):
    """模型选择器测试"""

    def setUp(self):
        """测试前准备"""
        config = {
            'models': {
                'gpt-4': {
                    'cost_per_1k_input': 0.03
                },
                'gpt-3.5-turbo': {
                    'cost_per_1k_input': 0.0005
                }
            },
            'storage': {}
        }
        self.selector = ModelSelector(config)

    def test_suggest_model_for_code(self):
        """测试8: 代码任务模型推荐"""
        result = self.selector.suggest(task='编写Python代码', budget=0.01)

        self.assertIn('recommended_model', result)
        self.assertIn('quality_score', result)
        self.assertIn('estimated_cost', result)

        print("✓ 测试8通过: 代码任务模型推荐成功")

    def test_suggest_model_with_budget(self):
        """测试9: 有预算限制的模型推荐"""
        result = self.selector.suggest(
            task='分析数据',
            budget=0.001  # 低预算，应该推荐便宜模型
        )

        # 低预算应该推荐便宜的模型
        self.assertIn('recommended_model', result)

        print("✓ 测试9通过: 有预算限制的推荐成功")

    def test_quality_priority(self):
        """测试10: 质量优先模式"""
        result = self.selector.suggest(
            task='复杂分析',
            quality_priority=True
        )

        self.assertEqual(result['recommended_model'], 'gpt-4')  # 质量优先

        print("✓ 测试10通过: 质量优先模式成功")

    def test_identify_task_type(self):
        """测试11: 任务类型识别"""
        self.assertEqual(
            self.selector._identify_task_type('编写代码'),
            'code'
        )
        self.assertEqual(
            self.selector._identify_task_type('写一篇文章'),
            'writing'
        )

        print("✓ 测试11通过: 任务类型识别成功")


class TestCacheManager(unittest.TestCase):
    """缓存管理器测试"""

    @classmethod
    def setUpClass(cls):
        """测试类准备"""
        cls.test_dir = "test_cache_data"
        cls.original_dir = os.getcwd()
        os.makedirs(cls.test_dir, exist_ok=True)
        os.chdir(cls.test_dir)

    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        os.chdir(cls.original_dir)
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)

    def setUp(self):
        """测试前准备"""
        config = {
            'storage': {
                'cache_db': 'test_cache_db.json'
            }
        }
        self.cache = CacheManager(config)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists('test_cache_db.json'):
            os.remove('test_cache_db.json')

    def test_cache_set_and_get(self):
        """测试12: 缓存设置和获取"""
        prompt = "测试提示词"
        model = "gpt-3.5-turbo"
        response = "测试响应"

        # 设置缓存
        self.cache.set(prompt, model, response, 100)

        # 获取缓存
        cached = self.cache.get(prompt, model)

        self.assertIsNotNone(cached)
        self.assertEqual(cached['response'], response)
        self.assertTrue(cached['from_cache'])

        print("✓ 测试12通过: 缓存设置和获取成功")

    def test_cache_miss(self):
        """测试13: 缓存未命中"""
        result = self.cache.get("不存在的提示词", "gpt-3.5-turbo")

        self.assertIsNone(result)

        print("✓ 测试13通过: 缓存未命中处理正确")

    def test_cache_analyze(self):
        """测试14: 缓存分析"""
        # 添加一些缓存
        for i in range(5):
            self.cache.set(f"提示词{i}", "gpt-3.5-turbo", f"响应{i}", 100)

        # 命中一些缓存
        self.cache.get("提示词0", "gpt-3.5-turbo")
        self.cache.get("提示词1", "gpt-3.5-turbo")

        analysis = self.cache.analyze()
        self.assertEqual(analysis['cache_entries'], 5)
        self.assertEqual(analysis['total_hits'], 2)

        print("✓ 测试14通过: 缓存分析成功")


class TestQualityEvaluator(unittest.TestCase):
    """质量评估器测试"""

    @classmethod
    def setUpClass(cls):
        """测试类准备"""
        cls.test_dir = "test_quality_data"
        cls.original_dir = os.getcwd()
        os.makedirs(cls.test_dir, exist_ok=True)
        os.chdir(cls.test_dir)

    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        os.chdir(cls.original_dir)
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)

    def setUp(self):
        """测试前准备"""
        config = {
            'storage': {
                'quality_db': 'test_quality_db.json'
            }
        }
        self.evaluator = QualityEvaluator(config)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists('test_quality_db.json'):
            os.remove('test_quality_db.json')

    def test_evaluate_good_response(self):
        """测试15: 评估好的响应"""
        prompt = "什么是AI？"
        response = "人工智能是指由计算机系统表现出的智能..."

        result = self.evaluator.evaluate_response(prompt, response)

        self.assertGreater(result['quality_score'], 0.7)
        self.assertFalse(result['is_error'])

        print("✓ 测试15通过: 好响应评估成功")

    def test_evaluate_empty_response(self):
        """测试16: 评估空响应"""
        result = self.evaluator.evaluate_response("问题", "")

        self.assertEqual(result['quality_score'], 0.0)
        self.assertTrue(result['is_error'])

        print("✓ 测试16通过: 空响应评估成功")

    def test_evaluate_short_response(self):
        """测试17: 评估过短响应"""
        prompt = "请详细解释人工智能的发展历程"
        response = "AI发展很快"

        result = self.evaluator.evaluate_response(prompt, response, expected_length=500)

        self.assertLess(result['quality_score'], 0.9)
        self.assertIn('响应过短', result['issues'])

        print("✓ 测试17通过: 过短响应评估成功")

    def test_quality_analyze(self):
        """测试18: 质量分析"""
        # 记录一些响应
        for i in range(10):
            self.evaluator.record_response(
                prompt=f"问题{i}",
                response=f"响应{i}" * 10,
                quality_score=0.8 + (i % 3) * 0.1,
                issues=[]
            )

        analysis = self.evaluator.evaluate()
        self.assertEqual(analysis['total_responses'], 10)
        self.assertGreater(analysis['avg_quality_score'], 0.7)

        print("✓ 测试18通过: 质量分析成功")


class TestIntegration(unittest.TestCase):
    """集成测试"""

    @classmethod
    def setUpClass(cls):
        """测试类准备"""
        cls.test_dir = "test_integration_data"
        cls.original_dir = os.getcwd()
        os.makedirs(cls.test_dir, exist_ok=True)
        os.chdir(cls.test_dir)

    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        os.chdir(cls.original_dir)
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)

    def test_complete_workflow(self):
        """测试19: 完整工作流程"""
        optimizer = AIToolOptimizer()

        # 1. 优化提示词
        prompt_result = optimizer.optimize_prompt(
            prompt="请帮我解释人工智能",
            task_type="writing"
        )
        self.assertTrue(len(prompt_result['improvements']) > 0)

        # 2. Token分析
        token_result = optimizer.analyze_tokens()
        self.assertIn('total_requests', token_result)

        # 3. 模型推荐
        model_result = optimizer.suggest_model(task="编写Python代码", budget=0.01)
        self.assertIn('recommended_model', model_result)

        # 4. 缓存分析
        cache_result = optimizer.analyze_cache()
        self.assertIn('cache_entries', cache_result)

        # 5. 质量评估
        quality_result = optimizer.evaluate_quality()
        self.assertIn('avg_quality_score', quality_result)

        # 6. 生成报告
        report = optimizer.get_usage_report()
        self.assertIn('token_usage', report)
        self.assertIn('quality', report)

        print("✓ 测试19通过: 完整工作流程成功")


if __name__ == '__main__':
    # 运行所有测试
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(__import__(__name__))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 输出测试摘要
    print("\n" + "="*60)
    print("📊 测试摘要")
    print("="*60)
    print(f"总测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n✅ 所有测试通过！")
    else:
        print("\n❌ 部分测试失败")
