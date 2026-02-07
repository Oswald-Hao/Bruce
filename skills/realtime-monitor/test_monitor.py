#!/usr/bin/env python3
"""
实时数据监控系统测试用例
"""

import unittest
import os
import json
import tempfile
import shutil
import time
from datetime import datetime, timedelta

from monitor import MonitorEngine, MonitorTask, Alert, TaskType, AlertLevel


class TestMonitorEngine(unittest.TestCase):
    """测试监控引擎"""

    def setUp(self):
        """设置测试环境"""
        self.test_dir = tempfile.mkdtemp()
        self.engine = MonitorEngine(config_file="config/monitor.yaml")

    def tearDown(self):
        """清理测试环境"""
        self.engine.stop()
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        if os.path.exists("data"):
            shutil.rmtree("data")

    def test_init(self):
        """测试初始化"""
        self.assertIsInstance(self.engine.tasks, list)
        self.assertIsInstance(self.engine.data, list)
        self.assertIsInstance(self.engine.alerts, list)
        self.assertFalse(self.engine.is_running)

    def test_add_task(self):
        """测试添加任务"""
        task = self.engine.add_task(
            name="测试任务",
            type="price",
            source="taobao",
            keywords=["iPhone"],
            target_urls=[],
            interval=300,
            threshold="price > 5000",
            action="webhook:url"
        )

        self.assertIsInstance(task, MonitorTask)
        self.assertEqual(task.name, "测试任务")
        self.assertEqual(task.type, TaskType.PRICE)
        self.assertTrue(task.enabled)

    def test_list_tasks(self):
        """测试列出任务"""
        self.engine.add_task(
            name="任务1",
            type="price",
            source="taobao",
            keywords=["iPhone"],
            target_urls=[],
            interval=300,
            threshold="price > 5000",
            action="webhook:url"
        )

        tasks = self.engine.list_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["name"], "任务1")

    def test_get_task(self):
        """测试获取任务"""
        task = self.engine.add_task(
            name="测试任务",
            type="price",
            source="taobao",
            keywords=["iPhone"],
            target_urls=[],
            interval=300,
            threshold="price > 5000",
            action="webhook:url"
        )

        found_task = self.engine.get_task(task.task_id)
        self.assertIsNotNone(found_task)
        self.assertEqual(found_task.task_id, task.task_id)
        self.assertEqual(found_task.name, "测试任务")

    def test_fetch_price_data(self):
        """测试获取价格数据"""
        task = MonitorTask(
            task_id="task_test",
            name="价格监控",
            type=TaskType.PRICE,
            source="taobao",
            keywords=["iPhone"],
            target_urls=[],
            interval=300,
            threshold="price > 5000",
            action="webhook:url",
            enabled=True,
            last_check=None,
            last_value=None
        )

        data = self.engine._fetch_price_data(task)
        self.assertIsNotNone(data)
        self.assertEqual(data["type"], "price")
        self.assertIn("value", data)
        self.assertIn("source", data)

    def test_fetch_news_data(self):
        """测试获取新闻数据"""
        task = MonitorTask(
            task_id="task_test",
            name="新闻监控",
            type=TaskType.NEWS,
            source="toutiao",
            keywords=["人工智能", "AI"],
            target_urls=[],
            interval=600,
            threshold="keyword in content",
            action="feishu:robot_id",
            enabled=True,
            last_check=None,
            last_value=None
        )

        data = self.engine._fetch_news_data(task)
        self.assertIsNotNone(data)
        self.assertEqual(data["type"], "news")
        self.assertIn("value", data)
        self.assertIn("title", data["value"])

    def test_fetch_competitor_data(self):
        """测试获取竞品数据"""
        task = MonitorTask(
            task_id="task_test",
            name="竞品监控",
            type=TaskType.COMPETITOR,
            source="jd",
            keywords=[],
            target_urls=["url1", "url2"],
            interval=1800,
            threshold="price < our_price",
            action="webhook:url",
            enabled=True,
            last_check=None,
            last_value=None
        )

        data = self.engine._fetch_competitor_data(task)
        self.assertIsNotNone(data)
        self.assertEqual(data["type"], "competitor")
        self.assertIn("value", data)
        self.assertIsInstance(data["value"], dict)

    def test_check_threshold_price(self):
        """测试检查价格阈值"""
        task = MonitorTask(
            task_id="task_test",
            name="价格监控",
            type=TaskType.PRICE,
            source="taobao",
            keywords=["iPhone"],
            target_urls=[],
            interval=300,
            threshold="price > 5000",
            action="webhook:url",
            enabled=True,
            last_check=datetime.now(),
            last_value=5000.0
        )

        # 价格变化超过5%
        data = {"value": 6000, "type": "price"}
        result = self.engine._check_threshold(task, data)
        self.assertTrue(result)

        # 价格变化不超过5%
        data = {"value": 5100, "type": "price"}
        result = self.engine._check_threshold(task, data)
        self.assertFalse(result)

    def test_check_threshold_news(self):
        """测试检查新闻阈值"""
        task = MonitorTask(
            task_id="task_test",
            name="新闻监控",
            type=TaskType.NEWS,
            source="toutiao",
            keywords=["人工智能", "AI"],
            target_urls=[],
            interval=600,
            threshold="keyword in content",
            action="feishu:robot_id",
            enabled=True,
            last_check=None,
            last_value=None
        )

        # 包含关键词
        data = {"value": {"title": "OpenAI发布新GPT-5模型", "contains_keyword": True}, "type": "news"}
        result = self.engine._check_threshold(task, data)
        self.assertTrue(result)

        # 不包含关键词
        data = {"value": {"title": "今日天气预报", "contains_keyword": False}, "type": "news"}
        result = self.engine._check_threshold(task, data)
        self.assertFalse(result)

    def test_trigger_alert(self):
        """测试触发预警"""
        self.engine.add_task(
            name="测试任务",
            type="price",
            source="taobao",
            keywords=["iPhone"],
            target_urls=[],
            interval=300,
            threshold="price > 5000",
            action="webhook:url"
        )

        task = self.engine.tasks[0]
        data = {"value": 6000, "type": "price"}

        self.engine._trigger_alert(task, data)

        self.assertEqual(len(self.engine.alerts), 1)
        self.assertEqual(self.engine.alerts[0].level, AlertLevel.WARNING)
        self.assertEqual(self.engine.alerts[0].task_id, task.task_id)

    def test_get_recent_alerts(self):
        """测试获取最近预警"""
        # 添加预警
        alert = Alert(
            alert_id="alert_test",
            task_id="task_test",
            timestamp=datetime.now(),
            level=AlertLevel.WARNING,
            message="测试预警",
            data={},
            action_taken="webhook:url"
        )

        self.engine.alerts.append(alert)

        recent_alerts = self.engine.get_recent_alerts(hours=24)
        self.assertEqual(len(recent_alerts), 1)

        # 获取1小时内的预警（应该为空）
        old_alert = Alert(
            alert_id="alert_old",
            task_id="task_test",
            timestamp=datetime.now() - timedelta(hours=2),
            level=AlertLevel.INFO,
            message="旧预警",
            data={},
            action_taken="log"
        )

        self.engine.alerts.append(old_alert)

        recent_alerts_1h = self.engine.get_recent_alerts(hours=1)
        self.assertEqual(len(recent_alerts_1h), 1)

    def test_monitor_loop(self):
        """测试监控循环"""
        # 添加一个短间隔的任务
        task = self.engine.add_task(
            name="快速测试任务",
            type="price",
            source="taobao",
            keywords=["iPhone"],
            target_urls=[],
            interval=1,  # 1秒
            threshold="price > 5000",
            action="log"
        )

        # 启动监控
        self.engine.start()
        self.assertTrue(self.engine.is_running)

        # 等待几秒，让任务执行几次
        time.sleep(3)

        # 停止监控
        self.engine.stop()
        self.assertFalse(self.engine.is_running)

        # 检查任务是否执行
        self.assertIsNotNone(task.last_check)

    def test_multiple_tasks(self):
        """测试多任务并发"""
        # 添加多个任务
        for i in range(3):
            self.engine.add_task(
                name=f"任务{i}",
                type="price" if i % 2 == 0 else "news",
                source="taobao" if i % 2 == 0 else "toutiao",
                keywords=["iPhone"] if i % 2 == 0 else ["AI"],
                target_urls=[],
                interval=2,
                threshold="price > 5000" if i % 2 == 0 else "keyword in content",
                action="log"
            )

        # 启动监控
        self.engine.start()
        time.sleep(5)
        self.engine.stop()

        # 检查所有任务都执行了
        for task in self.engine.tasks:
            self.assertIsNotNone(task.last_check)

    def test_export_data(self):
        """测试导出数据"""
        task = self.engine.add_task(
            name="导出测试任务",
            type="price",
            source="taobao",
            keywords=["iPhone"],
            target_urls=[],
            interval=300,
            threshold="price > 5000",
            action="log"
        )

        # 导出数据（因为没有数据，应该是空列表）
        data = self.engine.export_data(
            task_id=task.task_id,
            start_date="2026-01-01",
            end_date="2026-12-31"
        )

        self.assertIsInstance(data, list)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestMonitorEngine))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 返回测试结果
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
