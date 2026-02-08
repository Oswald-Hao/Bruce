#!/usr/bin/env python3
"""
情感分析系统测试
"""

import os
import sys
import unittest
import tempfile
import json

# 添加技能目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from sentiment_analyzer import SentimentAnalyzer


class TestSentimentAnalyzer(unittest.TestCase):
    """情感分析器测试"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.sa = SentimentAnalyzer()

    def test_01_init(self):
        """测试1: 初始化"""
        sa = SentimentAnalyzer()
        self.assertIsNotNone(sa)
        self.assertTrue(hasattr(sa, 'zh_positive'))
        self.assertTrue(hasattr(sa, 'zh_negative'))
        self.assertTrue(hasattr(sa, 'en_positive'))
        self.assertTrue(hasattr(sa, 'en_negative'))

    def test_02_analyze_positive_chinese(self):
        """测试2: 分析中文正面情感"""
        result = self.sa.analyze("这个产品非常好用，我很满意！")

        self.assertEqual(result["label"], "positive")
        self.assertGreater(result["score"], 0)
        self.assertGreater(result["confidence"], 0.5)
        self.assertTrue(any("好" in t for t in result["positive_tokens"]))

    def test_03_analyze_negative_chinese(self):
        """测试3: 分析中文负面情感"""
        result = self.sa.analyze("这个产品太糟糕了，我很失望")

        self.assertEqual(result["label"], "negative")
        self.assertLess(result["score"], 0)
        self.assertGreater(result["confidence"], 0.5)
        self.assertTrue(any("糟糕" in t or "失望" in t for t in result["negative_tokens"]))

    def test_04_analyze_neutral_chinese(self):
        """测试4: 分析中文中性情感"""
        result = self.sa.analyze("这个产品还行吧")

        self.assertIn(result["label"], ["neutral", "positive"])
        self.assertAlmostEqual(result["score"], 0.0, delta=0.5)

    def test_05_analyze_positive_english(self):
        """测试5: 分析英文正面情感"""
        result = self.sa.analyze("This product is amazing, I love it!")

        self.assertEqual(result["label"], "positive")
        self.assertGreater(result["score"], 0)
        self.assertGreater(result["confidence"], 0.5)

    def test_06_analyze_negative_english(self):
        """测试6: 分析英文负面情感"""
        result = self.sa.analyze("This product is terrible, I hate it")

        self.assertEqual(result["label"], "negative")
        self.assertLess(result["score"], 0)
        self.assertGreater(result["confidence"], 0.5)

    def test_07_analyze_neutral_english(self):
        """测试7: 分析英文中性情感"""
        result = self.sa.analyze("The product is okay")

        self.assertIn(result["label"], ["neutral", "positive"])
        self.assertAlmostEqual(result["score"], 0.0, delta=0.5)

    def test_08_analyze_with_negation_chinese(self):
        """测试8: 中文否定词处理"""
        result = self.sa.analyze("这个产品不好")

        self.assertEqual(result["label"], "negative")
        self.assertLess(result["score"], 0)

    def test_09_analyze_with_negation_english(self):
        """测试9: 英文否定词处理"""
        result = self.sa.analyze("This product is not good")

        self.assertEqual(result["label"], "negative")
        self.assertLess(result["score"], 0)

    def test_10_analyze_with_degree_chinese(self):
        """测试10: 中文程度副词处理"""
        result1 = self.sa.analyze("这个产品好")
        result2 = self.sa.analyze("这个产品非常好")
        result3 = self.sa.analyze("这个产品特别好")

        # 检查是否有程度副词影响（通过置信度或token数量）
        self.assertGreaterEqual(result2["confidence"], result1["confidence"])
        self.assertGreaterEqual(result3["confidence"], result2["confidence"])

    def test_11_analyze_with_degree_english(self):
        """测试11: 英文程度副词处理"""
        result1 = self.sa.analyze("This product is good")
        result2 = self.sa.analyze("This product is very good")
        result3 = self.sa.analyze("This product is extremely good")

        # 检查是否有程度副词影响
        self.assertGreaterEqual(result2["confidence"], result1["confidence"])
        self.assertGreaterEqual(result3["confidence"], result2["confidence"])

    def test_12_analyze_empty_text(self):
        """测试12: 空文本处理"""
        result = self.sa.analyze("")

        self.assertEqual(result["label"], "neutral")
        self.assertEqual(result["score"], 0.0)
        self.assertEqual(result["confidence"], 0.0)

    def test_13_analyze_batch_chinese(self):
        """测试13: 批量分析中文"""
        texts = [
            "这个产品很棒",
            "这个产品很差",
            "这个产品还行"
        ]

        results = self.sa.analyze_batch(texts)

        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["label"], "positive")
        self.assertEqual(results[1]["label"], "negative")

    def test_14_analyze_batch_english(self):
        """测试14: 批量分析英文"""
        texts = [
            "Great product!",
            "Terrible product!",
            "Okay product"
        ]

        results = self.sa.analyze_batch(texts)

        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["label"], "positive")
        self.assertEqual(results[1]["label"], "negative")

    def test_15_analyze_summary(self):
        """测试15: 汇总分析"""
        texts = [
            "这个产品很棒",
            "这个产品很差",
            "这个产品还行",
            "非常喜欢",
            "太糟糕了"
        ]

        summary = self.sa.analyze_summary(texts)

        self.assertEqual(summary["total"], 5)
        self.assertIn("average_score", summary)
        self.assertIn("distribution", summary)
        self.assertIn("positive", summary["distribution"])
        self.assertIn("negative", summary["distribution"])

    def test_16_analyze_trend(self):
        """测试16: 趋势分析"""
        texts = [
            "这个产品很好",
            "这个产品一般",
            "这个产品很差",
            "这个产品还行",
            "这个产品很棒"
        ]

        trend = self.sa.analyze_trend(texts)

        self.assertEqual(len(trend), 5)
        for i, item in enumerate(trend):
            self.assertEqual(item["index"], i)
            self.assertEqual(item["timestamp"], i)
            self.assertIn("label", item)
            self.assertIn("score", item)

    def test_17_get_dict_info(self):
        """测试17: 获取词典信息"""
        info = self.sa.get_dict_info()

        self.assertIn("zh_positive", info)
        self.assertIn("zh_negative", info)
        self.assertIn("en_positive", info)
        self.assertIn("en_negative", info)

        self.assertGreater(info["zh_positive"], 50)
        self.assertGreater(info["zh_negative"], 50)
        self.assertGreater(info["en_positive"], 50)
        self.assertGreater(info["en_negative"], 50)

    def test_18_mixed_language(self):
        """测试18: 混合语言处理"""
        result = self.sa.analyze("这个产品很 good")

        # 应该能检测到两种语言的情感词
        self.assertIn("label", result)
        self.assertIn("score", result)

    def test_19_confidence_calculation(self):
        """测试19: 置信度计算"""
        # 情感词多的文本置信度更高
        result1 = self.sa.analyze("好")
        result2 = self.sa.analyze("非常好，很棒，满意，喜欢")

        self.assertGreater(result2["confidence"], result1["confidence"])

    def test_20_score_normalization(self):
        """测试20: 得分归一化"""
        result = self.sa.analyze("非常好非常棒非常满意")

        self.assertGreaterEqual(result["score"], -1.0)
        self.assertLessEqual(result["score"], 1.0)


def run_tests():
    """运行测试"""
    print("=" * 60)
    print("情感分析系统 - 测试套件")
    print("=" * 60)

    # 创建测试套件
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSentimentAnalyzer)

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
