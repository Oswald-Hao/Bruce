#!/usr/bin/env python3
"""
电商价格监控系统 - 测试脚本
Price Monitor - Test Suite
"""

import unittest
import sys
import os

# 添加技能目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from monitor import PriceMonitor, ProductInfo


class TestPriceMonitor(unittest.TestCase):
    """价格监控器测试"""

    def setUp(self):
        """测试前设置"""
        self.monitor = PriceMonitor(platforms=["taobao", "pinduoduo"])

    def test_01_init(self):
        """测试初始化"""
        self.assertEqual(len(self.monitor.platforms), 2)
        self.assertIn("taobao", self.monitor.platforms)
        self.assertIn("pinduoduo", self.monitor.platforms)
        self.assertFalse(self.monitor.monitoring)

    def test_02_add_product(self):
        """测试添加监控商品"""
        self.monitor.add_product(
            product_id="p001",
            name="测试商品",
            url="https://example.com/item.htm?id=123",
            platform="taobao"
        )

        self.assertIn("p001", self.monitor.products)
        product = self.monitor.products["p001"]
        self.assertEqual(product.name, "测试商品")
        self.assertEqual(product.platform, "taobao")
        self.assertGreater(product.current_price, 0)

    def test_03_get_current_price(self):
        """测试获取当前价格"""
        self.monitor.add_product(
            product_id="p001",
            name="测试商品",
            url="https://example.com/item.htm?id=123",
            platform="taobao"
        )

        price_info = self.monitor.get_current_price("p001")

        self.assertIn("current_price", price_info)
        self.assertIn("old_price", price_info)
        self.assertIn("change_rate", price_info)
        self.assertIn("stock", price_info)
        self.assertIn("sales", price_info)
        self.assertGreater(price_info["current_price"], 0)

    def test_04_compare_platforms(self):
        """测试跨平台比价"""
        self.monitor.add_product(
            product_id="p001",
            name="测试商品",
            url="https://example.com/item.htm?id=123",
            platform="taobao"
        )

        comparison = self.monitor.compare_platforms("p001")

        self.assertIn("platforms", comparison)
        self.assertIn("lowest_price", comparison)
        self.assertIn("highest_price", comparison)
        self.assertIn("price_range", comparison)
        self.assertIn("taobao", comparison["platforms"])

    def test_05_find_arbitrage(self):
        """测试发现套利机会"""
        self.monitor.add_product(
            product_id="p001",
            name="测试商品",
            url="https://example.com/item.htm?id=123",
            platform="taobao"
        )

        opportunities = self.monitor.find_arbitrage("p001", min_profit_rate=0.15)

        self.assertIsInstance(opportunities, list)
        # 套利机会数量可能为0到平台数量的组合数
        for opp in opportunities:
            self.assertIn("source", opp)
            self.assertIn("target", opp)
            self.assertIn("profit_rate", opp)
            self.assertIn("risk_level", opp)

    def test_06_get_price_history(self):
        """测试获取价格历史"""
        self.monitor.add_product(
            product_id="p001",
            name="测试商品",
            url="https://example.com/item.htm?id=123",
            platform="taobao"
        )

        # 获取几次价格以生成历史
        self.monitor.get_current_price("p001")
        self.monitor.get_current_price("p001")

        history = self.monitor.get_price_history("p001", days=30)

        self.assertIsInstance(history, list)
        # 至少应该有几条历史记录
        self.assertGreater(len(history), 0)
        for h in history:
            self.assertIn("date", h)
            self.assertIn("price", h)
            self.assertIn("stock", h)

    def test_07_analyze_trend(self):
        """测试分析趋势"""
        self.monitor.add_product(
            product_id="p001",
            name="测试商品",
            url="https://example.com/item.htm?id=123",
            platform="taobao"
        )

        # 生成一些历史数据
        for _ in range(5):
            self.monitor.get_current_price("p001")

        trend = self.monitor.analyze_trend("p001", period="7d")

        self.assertIn("current_price", trend)
        self.assertIn("lowest_price", trend)
        self.assertIn("highest_price", trend)
        self.assertIn("trend", trend)
        self.assertIn("change_rate", trend)
        self.assertIn("recommendation", trend)
        self.assertIn(trend["trend"], ["上升", "下降", "稳定"])

    def test_08_export_data(self):
        """测试导出数据"""
        import tempfile
        import json

        self.monitor.add_product(
            product_id="p001",
            name="测试商品",
            url="https://example.com/item.htm?id=123",
            platform="taobao"
        )

        # 测试导出到临时文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name

        try:
            self.monitor.export_data(temp_file)

            # 验证文件存在
            self.assertTrue(os.path.exists(temp_file))

            # 验证文件内容
            with open(temp_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.assertIn("products", data)
            self.assertIn("price_history", data)

        finally:
            # 清理临时文件
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_09_invalid_platform(self):
        """测试不支持的平台"""
        with self.assertRaises(ValueError):
            PriceMonitor(platforms=["invalid_platform"])

    def test_10_invalid_product_id(self):
        """测试无效的商品ID"""
        with self.assertRaises(ValueError):
            self.monitor.get_current_price("invalid_id")

        with self.assertRaises(ValueError):
            self.monitor.compare_platforms("invalid_id")

        with self.assertRaises(ValueError):
            self.monitor.find_arbitrage("invalid_id")


class TestProductInfo(unittest.TestCase):
    """商品信息测试"""

    def test_product_info_creation(self):
        """测试商品信息创建"""
        product = ProductInfo(
            product_id="p001",
            name="测试商品",
            url="https://example.com",
            platform="taobao",
            current_price=299.99,
            stock=100,
            sales=1000,
            last_update="2026-02-06 12:00:00"
        )

        self.assertEqual(product.product_id, "p001")
        self.assertEqual(product.name, "测试商品")
        self.assertEqual(product.current_price, 299.99)
        self.assertEqual(product.stock, 100)
        self.assertEqual(product.sales, 1000)
        self.assertEqual(product.target_price, None)
        self.assertEqual(product.alert_threshold, 0.05)

    def test_product_info_with_target_price(self):
        """测试带目标价格的商品信息"""
        product = ProductInfo(
            product_id="p001",
            name="测试商品",
            url="https://example.com",
            platform="taobao",
            current_price=299.99,
            stock=100,
            sales=1000,
            last_update="2026-02-06 12:00:00",
            target_price=250.00,
            alert_threshold=0.10
        )

        self.assertEqual(product.target_price, 250.00)
        self.assertEqual(product.alert_threshold, 0.10)


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("电商价格监控系统 - 测试套件")
    print("=" * 60)
    print()

    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试
    suite.addTests(loader.loadTestsFromTestCase(TestPriceMonitor))
    suite.addTests(loader.loadTestsFromTestCase(TestProductInfo))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 打印摘要
    print()
    print("=" * 60)
    print("测试摘要")
    print("=" * 60)
    print(f"总测试数: {result.testsRun}")
    print(f"成功数: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败数: {len(result.failures)}")
    print(f"错误数: {len(result.errors)}")

    if result.wasSuccessful():
        print()
        print("✅ 所有测试通过！")
        return 0
    else:
        print()
        print("❌ 部分测试失败")
        if result.failures:
            print("\n失败的测试:")
            for test, traceback in result.failures:
                print(f"  - {test}")
        if result.errors:
            print("\n错误的测试:")
            for test, traceback in result.errors:
                print(f"  - {test}")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
