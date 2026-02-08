#!/usr/bin/env python3
"""
社交媒体自动化系统 - 测试套件
"""

import unittest
import os
import json
import shutil
from datetime import datetime, timedelta

# 导入主模块
from main import SocialMediaAutomation


class TestSocialMediaAutomation(unittest.TestCase):
    """社交媒体自动化系统测试"""

    @classmethod
    def setUpClass(cls):
        """测试前准备"""
        cls.test_dir = "test_data"
        cls.original_dir = os.getcwd()
        os.makedirs(cls.test_dir, exist_ok=True)
        os.chdir(cls.test_dir)

    @classmethod
    def tearDownClass(cls):
        """测试后清理"""
        os.chdir(cls.original_dir)
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)

    def setUp(self):
        """每个测试前的准备"""
        # 创建测试配置
        config = {
            "platforms": {
                "douyin": {},
                "xiaohongshu": {},
                "weibo": {},
                "zhihu": {}
            },
            "scheduler": {
                "enabled": False,
                "check_interval": 60
            },
            "storage": {
                "content_db": "test_content_db.json",
                "scheduled_db": "test_scheduled_db.json",
                "analytics_db": "test_analytics_db.json"
            }
        }

        with open("config.json", 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        # 初始化系统
        self.sma = SocialMediaAutomation("config.json")

    def tearDown(self):
        """每个测试后的清理"""
        # 删除测试数据库
        for db_file in ["test_content_db.json", "test_scheduled_db.json", "test_analytics_db.json"]:
            if os.path.exists(db_file):
                os.remove(db_file)

    def test_platform_initialization(self):
        """测试1: 平台初始化"""
        platforms = self.sma.platforms

        self.assertIsNotNone(platforms)
        self.assertIn('douyin', platforms)
        self.assertIn('xiaohongshu', platforms)
        self.assertIn('weibo', platforms)
        self.assertIn('zhihu', platforms)

        print("✓ 测试1通过: 平台初始化成功")

    def test_publish_content(self):
        """测试2: 发布内容"""
        content = "这是一条测试内容"
        platforms = ['douyin', 'xiaohongshu']

        results = self.sma.publish(
            content=content,
            platforms=platforms
        )

        self.assertIsNotNone(results)
        self.assertIn('douyin', results)
        self.assertIn('xiaohongshu', results)
        self.assertTrue(results['douyin']['success'])
        self.assertTrue(results['xiaohongshu']['success'])
        self.assertIsNotNone(results['douyin']['post_id'])

        print("✓ 测试2通过: 内容发布成功")

    def test_publish_with_media(self):
        """测试3: 带媒体文件发布"""
        content = "带媒体文件的测试内容"
        media_files = ["video1.mp4", "image1.jpg"]
        platforms = ['weibo']

        results = self.sma.publish(
            content=content,
            platforms=platforms,
            media_files=media_files
        )

        self.assertTrue(results['weibo']['success'])

        print("✓ 测试3通过: 带媒体文件发布成功")

    def test_schedule_publish(self):
        """测试4: 定时发布"""
        content = "定时发布的测试内容"
        platforms = ['douyin']
        publish_time = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")

        result = self.sma.schedule_publish(
            content=content,
            platforms=platforms,
            publish_time=publish_time
        )

        self.assertTrue(result['success'])
        self.assertIsNotNone(result['task_id'])
        self.assertEqual(result['platforms'], platforms)

        print("✓ 测试4通过: 定时发布设置成功")

    def test_list_scheduled(self):
        """测试5: 列出定时任务"""
        # 先添加几个任务
        for i in range(3):
            publish_time = (datetime.now() + timedelta(hours=1 + i)).strftime("%Y-%m-%d %H:%M")
            self.sma.schedule_publish(
                content=f"测试内容{i}",
                platforms=['douyin'],
                publish_time=publish_time
            )

        tasks = self.sma.list_scheduled()

        self.assertEqual(len(tasks), 3)
        self.assertIsNotNone(tasks[0]['task_id'])
        self.assertEqual(tasks[0]['status'], 'pending')

        print("✓ 测试5通过: 列出定时任务成功")

    def test_cancel_schedule(self):
        """测试6: 取消定时任务"""
        publish_time = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
        result = self.sma.schedule_publish(
            content="测试内容",
            platforms=['douyin'],
            publish_time=publish_time
        )

        task_id = result['task_id']

        # 取消任务
        cancelled = self.sma.cancel_schedule(task_id)
        self.assertTrue(cancelled)

        # 验证任务已删除
        tasks = self.sma.list_scheduled()
        self.assertEqual(len(tasks), 0)

        print("✓ 测试6通过: 取消定时任务成功")

    def test_get_stats(self):
        """测试7: 获取统计数据"""
        # 先发布一些内容
        for i in range(5):
            self.sma.publish(
                content=f"测试内容{i}",
                platforms=['douyin']
            )

        stats = self.sma.get_stats(days=7)

        self.assertIsNotNone(stats)
        self.assertGreater(stats['total_posts'], 0)
        self.assertIn('by_platform', stats)

        print("✓ 测试7通过: 获取统计数据成功")

    def test_get_platform_stats(self):
        """测试8: 获取平台统计"""
        # 发布内容
        self.sma.publish(
            content="测试内容",
            platforms=['douyin', 'xiaohongshu']
        )

        douyin_stats = self.sma.get_platform_stats('douyin', days=7)

        self.assertIsNotNone(douyin_stats)
        self.assertEqual(douyin_stats['platform'], 'douyin')
        self.assertGreater(douyin_stats['posts'], 0)

        print("✓ 测试8通过: 获取平台统计成功")

    def test_content_library(self):
        """测试9: 内容库管理"""
        # 发布内容
        self.sma.publish(
            content="测试内容1",
            platforms=['douyin']
        )
        self.sma.publish(
            content="测试内容2",
            platforms=['xiaohongshu']
        )

        # 获取所有内容
        all_contents = self.sma.get_content_library()
        self.assertGreater(len(all_contents), 0)

        # 获取指定平台内容
        douyin_contents = self.sma.get_content_library('douyin')
        self.assertGreater(len(douyin_contents), 0)

        print("✓ 测试9通过: 内容库管理成功")

    def test_multiple_platforms_publish(self):
        """测试10: 多平台同时发布"""
        content = "多平台发布测试"
        platforms = ['douyin', 'xiaohongshu', 'weibo', 'zhihu']

        results = self.sma.publish(
            content=content,
            platforms=platforms
        )

        # 验证所有平台都发布成功
        self.assertEqual(len(results), 4)
        for platform in platforms:
            self.assertIn(platform, results)
            self.assertTrue(results[platform]['success'])

        print("✓ 测试10通过: 多平台同时发布成功")

    def test_invalid_platform(self):
        """测试11: 无效平台处理"""
        results = self.sma.publish(
            content="测试内容",
            platforms=['invalid_platform']
        )

        self.assertFalse(results['invalid_platform']['success'])
        self.assertIn('未配置', results['invalid_platform']['error'])

        print("✓ 测试11通过: 无效平台处理正确")

    def test_long_content(self):
        """测试12: 长内容发布"""
        # 创建一个长内容（微博限制140字符）
        long_content = "测试内容" * 50

        results = self.sma.publish(
            content=long_content,
            platforms=['douyin']  # 抖音支持长内容
        )

        self.assertTrue(results['douyin']['success'])

        # 微博应该失败（超长）
        results_weibo = self.sma.publish(
            content=long_content,
            platforms=['weibo']
        )

        self.assertFalse(results_weibo['weibo']['success'])

        print("✓ 测试12通过: 长内容处理正确")

    def test_scheduler_task_persistence(self):
        """测试13: 定时任务持久化"""
        import json

        publish_time = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
        result = self.sma.schedule_publish(
            content="持久化测试",
            platforms=['douyin'],
            publish_time=publish_time
        )

        # 重新初始化系统
        sma2 = SocialMediaAutomation("config.json")
        tasks = sma2.list_scheduled()

        # 验证任务已保存
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['task_id'], result['task_id'])

        print("✓ 测试13通过: 定时任务持久化成功")

    def test_analytics_recording(self):
        """测试14: 数据记录"""
        # 发布内容
        results = self.sma.publish(
            content="数据分析测试",
            platforms=['douyin']
        )

        post_id = results['douyin']['post_id']

        # 记录模拟统计
        stats = {
            'views': 1000,
            'likes': 50,
            'comments': 10,
            'shares': 5
        }
        self.sma.analytics.record_stats('douyin', post_id, stats)

        # 获取统计
        analytics = self.sma.analytics.get_stats(days=1)

        self.assertEqual(analytics['total_views'], 1000)
        self.assertEqual(analytics['total_likes'], 50)

        print("✓ 测试14通过: 数据记录成功")


class TestIntegration(unittest.TestCase):
    """集成测试"""

    def setUp(self):
        """测试前准备"""
        self.test_dir = "test_integration"
        self.original_dir = os.getcwd()
        os.makedirs(self.test_dir, exist_ok=True)
        os.chdir(self.test_dir)

        # 创建配置
        config = {
            "platforms": {
                "douyin": {},
                "xiaohongshu": {}
            },
            "scheduler": {
                "enabled": False,
                "check_interval": 60
            },
            "storage": {
                "content_db": "test_content_db.json",
                "scheduled_db": "test_scheduled_db.json",
                "analytics_db": "test_analytics_db.json"
            }
        }

        with open("config.json", 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        self.sma = SocialMediaAutomation("config.json")

    def tearDown(self):
        """测试后清理"""
        os.chdir(self.original_dir)
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_complete_workflow(self):
        """测试15: 完整工作流程"""
        # 1. 发布内容到多个平台
        results = self.sma.publish(
            content="完整工作流程测试",
            platforms=['douyin', 'xiaohongshu']
        )
        self.assertTrue(all([r['success'] for r in results.values()]))

        # 2. 设置定时发布
        publish_time = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
        schedule_result = self.sma.schedule_publish(
            content="定时发布测试",
            platforms=['douyin'],
            publish_time=publish_time
        )
        self.assertTrue(schedule_result['success'])

        # 3. 查看定时任务
        tasks = self.sma.list_scheduled()
        self.assertEqual(len(tasks), 1)

        # 4. 获取统计
        stats = self.sma.get_stats(days=7)
        self.assertGreater(stats['total_posts'], 0)

        # 5. 查看内容库
        contents = self.sma.get_content_library()
        self.assertGreater(len(contents), 0)

        print("✓ 测试15通过: 完整工作流程成功")


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
