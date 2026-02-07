#!/usr/bin/env python3
"""
广告投放优化器测试用例
"""

import unittest
import os
import json
import tempfile
from datetime import datetime, timedelta
import shutil

from optimize import AdOptimizer, AdCampaign, OptimizationResult
from ab_test import ABTester, ABTest, TestVariant, TestResult, TestStatus
from analyze import AdAnalyzer, AdMetrics, Insight
from monitor import AdMonitor, MonitorConfig, Alert, AlertLevel


class TestAdOptimizer(unittest.TestCase):
    """测试广告优化器"""

    def setUp(self):
        """设置测试环境"""
        self.optimizer = AdOptimizer("baidu")
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """清理测试环境"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.optimizer.platform, "baidu")
        self.assertIsInstance(self.optimizer.campaigns, list)

    def test_load_campaigns(self):
        """测试加载广告活动"""
        result = self.optimizer.load_campaigns()
        self.assertTrue(result)
        self.assertGreater(len(self.optimizer.campaigns), 0)

    def test_optimize_budget(self):
        """测试优化预算"""
        # 加载广告活动
        self.optimizer.load_campaigns()

        # 优化预算
        results = self.optimizer.optimize_budget(max_cpa=100, goal="conversion")

        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)

        # 检查结果格式
        for result in results:
            self.assertIsInstance(result, OptimizationResult)
            self.assertIsInstance(result.campaign_id, str)
            self.assertIsInstance(result.action, str)

    def test_apply_optimization(self):
        """测试应用优化"""
        self.optimizer.load_campaigns()

        results = self.optimizer.optimize_budget(max_cpa=100, goal="conversion")

        result = self.optimizer.apply_optimization(results)
        self.assertTrue(result)

    def test_generate_report(self):
        """测试生成报告"""
        self.optimizer.load_campaigns()

        results = self.optimizer.optimize_budget(max_cpa=100, goal="conversion")

        report = self.optimizer.generate_report(results)
        self.assertIsInstance(report, str)
        self.assertIn("广告投放优化报告", report)
        self.assertIn("优化建议", report)

    def test_optimize_full_workflow(self):
        """测试完整优化流程"""
        results, report = self.optimizer.optimize(
            budget=5000,
            goal="conversion",
            max_cpa=100
        )

        self.assertIsInstance(results, list)
        self.assertIsInstance(report, str)
        self.assertIn("广告投放优化报告", report)


class TestABTester(unittest.TestCase):
    """测试A/B测试器"""

    def setUp(self):
        """设置测试环境"""
        self.tester = ABTester("tencent")

    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.tester.platform, "tencent")
        self.assertIsInstance(self.tester.tests, list)

    def test_create_test(self):
        """测试创建A/B测试"""
        test = self.tester.create_test(
            name="测试1",
            creative_a="ad_a.jpg",
            creative_b="ad_b.jpg",
            budget=1000,
            duration=7
        )

        self.assertIsInstance(test, ABTest)
        self.assertEqual(test.name, "测试1")
        self.assertEqual(len(test.variants), 2)
        self.assertEqual(test.status, TestStatus.PENDING)

    def test_run_test(self):
        """测试运行A/B测试"""
        test = self.tester.create_test(
            name="测试2",
            creative_a="ad_a.jpg",
            creative_b="ad_b.jpg",
            budget=1000,
            duration=7
        )

        result = self.tester.run_test(test.test_id)
        self.assertTrue(result)
        self.assertEqual(test.status, TestStatus.COMPLETED)
        self.assertIsNotNone(test.winner)

    def test_analyze_result(self):
        """测试分析测试结果"""
        test = self.tester.create_test(
            name="测试3",
            creative_a="ad_a.jpg",
            creative_b="ad_b.jpg",
            budget=1000,
            duration=7
        )

        self.tester.run_test(test.test_id)
        result = self.tester.analyze_result(test)

        self.assertIsInstance(result, TestResult)
        self.assertIn(result.winner, ["A", "B", "Tie"])
        self.assertIsInstance(result.significance, float)
        self.assertIsInstance(result.recommendation, str)

    def test_generate_report(self):
        """测试生成测试报告"""
        test = self.tester.create_test(
            name="测试4",
            creative_a="ad_a.jpg",
            creative_b="ad_b.jpg",
            budget=1000,
            duration=7
        )

        self.tester.run_test(test.test_id)
        report = self.tester.generate_report(test.test_id)

        self.assertIsInstance(report, str)
        self.assertIn("A/B测试报告", report)
        self.assertIn("变体对比", report)
        self.assertIn("结论", report)

    def test_run_test_series(self):
        """测试批量运行A/B测试"""
        tests = [
            {"name": "系列测试1", "creative_a": "ad_a.jpg", "creative_b": "ad_b.jpg", "budget": 1000},
            {"name": "系列测试2", "creative_a": "ad_c.jpg", "creative_b": "ad_d.jpg", "budget": 2000},
        ]

        results = self.tester.run_test_series(tests)

        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertIsInstance(result, TestResult)


class TestAdAnalyzer(unittest.TestCase):
    """测试广告分析器"""

    def setUp(self):
        """设置测试环境"""
        self.analyzer = AdAnalyzer("google")
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """清理测试环境"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.analyzer.platform, "google")

    def test_load_metrics(self):
        """测试加载指标"""
        metrics = self.analyzer.load_metrics(
            start_date="2026-01-01",
            end_date="2026-01-31"
        )

        self.assertIsInstance(metrics, AdMetrics)
        self.assertEqual(metrics.platform, "google")
        self.assertGreater(metrics.total_budget, 0)
        self.assertGreater(len(metrics.top_campaigns), 0)
        self.assertGreater(len(metrics.worst_campaigns), 0)

    def test_generate_insights(self):
        """测试生成洞察"""
        metrics = self.analyzer.load_metrics(
            start_date="2026-01-01",
            end_date="2026-01-31"
        )

        insights = self.analyzer.generate_insights(metrics)

        self.assertIsInstance(insights, list)
        self.assertGreater(len(insights), 0)

        for insight in insights:
            self.assertIsInstance(insight, Insight)
            self.assertIsInstance(insight.type, str)
            self.assertIsInstance(insight.message, str)
            self.assertIn(insight.impact, ["高", "中", "低"])

    def test_generate_markdown_report(self):
        """测试生成Markdown报告"""
        metrics = self.analyzer.load_metrics(
            start_date="2026-01-01",
            end_date="2026-01-31"
        )

        insights = self.analyzer.generate_insights(metrics)
        report = self.analyzer.generate_report(metrics, insights, format="markdown")

        self.assertIsInstance(report, str)
        self.assertIn("广告效果分析报告", report)
        self.assertIn("总览", report)
        self.assertIn("最佳活动", report)
        self.assertIn("洞察和建议", report)

    def test_generate_html_report(self):
        """测试生成HTML报告"""
        metrics = self.analyzer.load_metrics(
            start_date="2026-01-01",
            end_date="2026-01-31"
        )

        insights = self.analyzer.generate_insights(metrics)
        report = self.analyzer.generate_report(metrics, insights, format="html")

        self.assertIsInstance(report, str)
        self.assertIn("<!DOCTYPE html>", report)
        self.assertIn("广告效果分析报告", report)
        self.assertIn("<table>", report)

    def test_generate_json_report(self):
        """测试生成JSON报告"""
        metrics = self.analyzer.load_metrics(
            start_date="2026-01-01",
            end_date="2026-01-31"
        )

        insights = self.analyzer.generate_insights(metrics)
        report = self.analyzer.generate_report(metrics, insights, format="json")

        self.assertIsInstance(report, str)
        report_dict = json.loads(report)
        self.assertIn("metrics", report_dict)
        self.assertIn("insights", report_dict)

    def test_analyze_full_workflow(self):
        """测试完整分析流程"""
        report = self.analyzer.analyze(
            start_date="2026-01-01",
            end_date="2026-01-31",
            format="markdown"
        )

        self.assertIsInstance(report, str)
        self.assertIn("广告效果分析报告", report)


class TestAdMonitor(unittest.TestCase):
    """测试广告监控器"""

    def setUp(self):
        """设置测试环境"""
        self.config = MonitorConfig(
            platform="baidu",
            account="test_account",
            interval=10,  # 测试时使用较短的间隔
            alerts_enabled=True,
            alert_channels=[],
            thresholds={
                "cpa": 150.0,
                "ctr": 1.0,
                "roi": 100.0
            }
        )
        self.monitor = AdMonitor(self.config)

    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.monitor.config.platform, "baidu")
        self.assertEqual(self.monitor.is_running, False)
        self.assertIsInstance(self.monitor.alerts, list)

    def test_add_alert_callback(self):
        """测试添加预警回调"""
        callback_called = []

        def test_callback(alert: Alert):
            callback_called.append(alert)

        self.monitor.add_alert_callback(test_callback)
        self.assertEqual(len(self.monitor.alert_callbacks), 1)

    def test_fetch_realtime_metrics(self):
        """测试获取实时指标"""
        metrics = self.monitor._fetch_realtime_metrics()

        self.assertIsInstance(metrics, list)
        self.assertGreater(len(metrics), 0)

        for metric in metrics:
            self.assertIn("campaign_id", metric)
            self.assertIn("cpa", metric)
            self.assertIn("ctr", metric)
            self.assertIn("roi", metric)

    def test_get_recent_alerts(self):
        """测试获取最近预警"""
        # 添加一些测试预警（当前时间）
        test_alert = Alert(
            timestamp=datetime.now(),
            level=AlertLevel.WARNING,
            platform="baidu",
            campaign_id="cmp_1",
            message="测试预警",
            metric="cpa",
            current_value=200.0,
            threshold=150.0
        )

        self.monitor.alerts.append(test_alert)

        recent_alerts = self.monitor.get_recent_alerts(hours=24)
        self.assertEqual(len(recent_alerts), 1)

        # 添加一个26小时前的预警
        old_alert = Alert(
            timestamp=datetime.now() - timedelta(hours=25, minutes=1),
            level=AlertLevel.WARNING,
            platform="baidu",
            campaign_id="cmp_2",
            message="旧预警",
            metric="cpa",
            current_value=200.0,
            threshold=150.0
        )

        self.monitor.alerts.append(old_alert)

        # 获取24小时内的预警（应该只有1个）
        recent_alerts_24h = self.monitor.get_recent_alerts(hours=24)
        self.assertEqual(len(recent_alerts_24h), 1)

        # 获取26小时内的预警（应该有2个）
        recent_alerts_30h = self.monitor.get_recent_alerts(hours=30)
        self.assertEqual(len(recent_alerts_30h), 2)

    def test_get_alerts_by_level(self):
        """测试按级别获取预警"""
        # 添加不同级别的预警
        warning_alert = Alert(
            timestamp=datetime.now(),
            level=AlertLevel.WARNING,
            platform="baidu",
            campaign_id="cmp_1",
            message="警告",
            metric="cpa",
            current_value=200.0,
            threshold=150.0
        )

        critical_alert = Alert(
            timestamp=datetime.now(),
            level=AlertLevel.CRITICAL,
            platform="baidu",
            campaign_id="cmp_2",
            message="严重",
            metric="roi",
            current_value=-10.0,
            threshold=100.0
        )

        self.monitor.alerts.append(warning_alert)
        self.monitor.alerts.append(critical_alert)

        warning_alerts = self.monitor.get_alerts_by_level(AlertLevel.WARNING)
        self.assertEqual(len(warning_alerts), 1)

        critical_alerts = self.monitor.get_alerts_by_level(AlertLevel.CRITICAL)
        self.assertEqual(len(critical_alerts), 1)

    def test_get_alert_summary(self):
        """测试获取预警摘要"""
        # 添加预警
        warning_alert = Alert(
            timestamp=datetime.now(),
            level=AlertLevel.WARNING,
            platform="baidu",
            campaign_id="cmp_1",
            message="警告",
            metric="cpa",
            current_value=200.0,
            threshold=150.0
        )

        self.monitor.alerts.append(warning_alert)

        summary = self.monitor.get_alert_summary()
        self.assertEqual(summary["total"], 1)
        self.assertEqual(summary["warning"], 1)
        self.assertEqual(summary["critical"], 0)

    def test_export_alerts_json(self):
        """测试导出预警为JSON"""
        # 添加预警
        test_alert = Alert(
            timestamp=datetime.now(),
            level=AlertLevel.WARNING,
            platform="baidu",
            campaign_id="cmp_1",
            message="测试",
            metric="cpa",
            current_value=200.0,
            threshold=150.0
        )

        self.monitor.alerts.append(test_alert)

        exported = self.monitor.export_alerts("json")
        self.assertIsInstance(exported, str)

        # 验证JSON格式
        alerts_data = json.loads(exported)
        self.assertEqual(len(alerts_data), 1)
        self.assertIn("timestamp", alerts_data[0])
        self.assertIn("level", alerts_data[0])

    def test_export_alerts_csv(self):
        """测试导出预警为CSV"""
        # 添加预警
        test_alert = Alert(
            timestamp=datetime.now(),
            level=AlertLevel.WARNING,
            platform="baidu",
            campaign_id="cmp_1",
            message="测试",
            metric="cpa",
            current_value=200.0,
            threshold=150.0
        )

        self.monitor.alerts.append(test_alert)

        exported = self.monitor.export_alerts("csv")
        self.assertIsInstance(exported, str)
        self.assertIn("timestamp,level", exported)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestAdOptimizer))
    suite.addTests(loader.loadTestsFromTestCase(TestABTester))
    suite.addTests(loader.loadTestsFromTestCase(TestAdAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestAdMonitor))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 返回测试结果
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
