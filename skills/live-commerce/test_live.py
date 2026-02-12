#!/usr/bin/env python3
"""
直播电商助手测试
测试商品管理、直播管理、观众管理、弹幕管理、数据分析
"""

import os
import sys
import json
import shutil
from datetime import datetime

# 添加技能目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from live import (
    LiveCommerceSystem,
    LiveStatus,
    ProductStatus,
    ChatType,
    Sentiment
)


class TestLiveCommerce:
    """直播电商系统测试"""

    def __init__(self):
        self.system = LiveCommerceSystem()
        self.test_results = []

    def setup(self):
        """测试前准备"""
        # 清理测试数据
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        if os.path.exists(data_dir):
            shutil.rmtree(data_dir)
        os.makedirs(data_dir, exist_ok=True)

        # 重新初始化
        self.system = LiveCommerceSystem()

    def teardown(self):
        """测试后清理"""
        pass

    def assert_equal(self, actual, expected, test_name):
        """断言相等"""
        if actual == expected:
            self.test_results.append((test_name, True, f"✅ {test_name} 通过"))
            print(f"✅ {test_name} 通过")
            return True
        else:
            self.test_results.append((test_name, False,
                                       f"❌ {test_name} 失败: 期望 {expected}, 实际 {actual}"))
            print(f"❌ {test_name} 失败: 期望 {expected}, 实际 {actual}")
            return False

    def assert_true(self, condition, test_name):
        """断言为真"""
        if condition:
            self.test_results.append((test_name, True, f"✅ {test_name} 通过"))
            print(f"✅ {test_name} 通过")
            return True
        else:
            self.test_results.append((test_name, False, f"❌ {test_name} 失败"))
            print(f"❌ {test_name} 失败")
            return False

    def test_product_management(self):
        """测试商品管理"""
        print("\n📋 测试商品管理...")

        # 测试1: 添加商品
        product = self.system.add_product(
            name="智能手机",
            price=2999,
            stock=100,
            category="数码",
            description="高性能智能手机"
        )
        self.assert_true(product.product_id.startswith("prod_"), "商品ID格式正确")
        self.assert_equal(product.name, "智能手机", "商品名称正确")
        self.assert_equal(product.price, 2999, "商品价格正确")
        self.assert_equal(product.stock, 100, "商品库存正确")

        # 测试2: 调整价格
        success = self.system.adjust_price(product.product_id, 2799)
        self.assert_true(success, "调整价格成功")

        updated_product = self.system.product_mgr.get_product(product.product_id)
        self.assert_equal(updated_product.price, 2799, "价格调整验证成功")

        # 测试3: 改变库存
        success = self.system.change_stock(product.product_id, -10)
        self.assert_true(success, "库存减少成功")

        updated_product = self.system.product_mgr.get_product(product.product_id)
        self.assert_equal(updated_product.stock, 90, "库存减少验证成功")

        # 测试4: 添加更多商品
        self.system.add_product("蓝牙耳机", 299, 200, category="数码")
        self.system.add_product("充电宝", 99, 500, category="数码")

        # 测试5: 列出商品
        products = self.system.list_products(category="数码")
        self.assert_true(len(products) >= 3, "列出商品数量正确")

    def test_product_stats(self):
        """测试商品统计"""
        print("\n📋 测试商品统计...")

        # 创建商品
        product = self.system.add_product("测试商品", 100, 50, category="测试")

        # 记录点击和销售
        self.system.record_click(product.product_id)
        self.system.record_click(product.product_id)
        self.system.record_sale(product.product_id, 5)

        # 获取统计
        stats = self.system.get_product_stats(product.product_id)

        self.assert_equal(stats['name'], "测试商品", "商品名称正确")
        self.assert_equal(stats['click_count'], 2, "点击数正确")
        self.assert_equal(stats['sales_count'], 5, "销量正确")
        self.assert_equal(stats['stock'], 45, "库存正确")
        self.assert_equal(stats['total_revenue'], 500, "总收入正确")

    def test_live_management(self):
        """测试直播管理"""
        print("\n📋 测试直播管理...")

        # 测试1: 创建直播
        live = self.system.create_live(
            room_id="123456789",
            platform="douyin",
            title="新品发布直播"
        )
        self.assert_true(live.live_id.startswith("live_"), "直播ID格式正确")
        self.assert_equal(live.room_id, "123456789", "房间号正确")
        self.assert_equal(live.platform, "douyin", "平台正确")
        self.assert_equal(live.title, "新品发布直播", "标题正确")
        self.assert_equal(live.status, LiveStatus.LIVE.value, "直播状态正确")

        # 测试2: 添加商品到直播
        product = self.system.add_product("直播商品", 199, 30)
        success = self.system.add_product_to_live(live.live_id, product.product_id)
        self.assert_true(success, "添加商品到直播成功")

        # 测试3: 记录观看人数
        success = self.system.record_viewers(live.live_id, 1000)
        self.assert_true(success, "记录观看人数成功")

        updated_live = self.system.live_mgr.get_live(live.live_id)
        self.assert_equal(updated_live.max_viewers, 1000, "峰值观看人数正确")

        # 测试4: 记录互动
        success = self.system.record_interaction(live.live_id)
        self.assert_true(success, "记录互动成功")

        # 测试5: 结束直播
        success = self.system.end_live(live.live_id)
        self.assert_true(success, "结束直播成功")

        updated_live = self.system.live_mgr.get_live(live.live_id)
        self.assert_equal(updated_live.status, LiveStatus.ENDED.value, "直播状态已更新")
        self.assert_true(updated_live.end_time is not None, "结束时间已记录")

    def test_live_stats(self):
        """测试直播统计"""
        print("\n📋 测试直播统计...")

        # 创建直播
        live = self.system.create_live(
            room_id="987654321",
            platform="tiktok",
            title="测试直播"
        )

        # 添加一些数据
        self.system.record_viewers(live.live_id, 500)
        self.system.record_viewers(live.live_id, 800)
        self.system.record_interaction(live.live_id)
        self.system.record_interaction(live.live_id)
        self.system.record_interaction(live.live_id)

        # 获取统计
        stats = self.system.get_live_stats(live.live_id)

        self.assert_equal(stats['title'], "测试直播", "直播标题正确")
        self.assert_equal(stats['platform'], "tiktok", "平台正确")
        self.assert_equal(stats['max_viewers'], 800, "峰值观看人数正确")
        self.assert_equal(stats['interaction_count'], 3, "互动数正确")

    def test_viewer_management(self):
        """测试观众管理"""
        print("\n📋 测试观众管理...")

        # 创建直播
        live = self.system.create_live(
            room_id="111222333",
            platform="douyin",
            title="观众测试直播"
        )

        # 测试1: 添加观众
        viewer = self.system.add_viewer(
            room_id=live.room_id,
            user_id="user_001",
            platform="douyin",
            is_follower=True
        )
        self.assert_true(viewer.viewer_id.startswith("viewer_"), "观众ID格式正确")
        self.assert_equal(viewer.room_id, live.room_id, "房间号正确")
        self.assert_true(viewer.is_follower, "粉丝标记正确")

        # 测试2: 记录互动
        success = self.system.record_viewer_interaction(viewer.viewer_id)
        self.assert_true(success, "记录观众互动成功")

        # 测试3: 记录购买
        success = self.system.record_viewer_purchase(viewer.viewer_id)
        self.assert_true(success, "记录观众购买成功")

        # 测试4: 记录离开
        success = self.system.record_leave(viewer.viewer_id)
        self.assert_true(success, "记录离开成功")

        updated_viewer = self.system.viewer_mgr.get_viewer(viewer.viewer_id)
        self.assert_true(updated_viewer.leave_time is not None, "离开时间已记录")
        self.assert_true(updated_viewer.watch_duration >= 0, "观看时长已计算")

    def test_viewer_profile(self):
        """测试观众画像"""
        print("\n📋 测试观众画像...")

        # 创建直播和观众
        live = self.system.create_live(
            room_id="444555666",
            platform="douyin",
            title="画像测试直播"
        )

        # 添加多个观众
        self.system.add_viewer(live.room_id, "user_a", platform="douyin", is_follower=True)
        self.system.add_viewer(live.room_id, "user_b", platform="douyin", is_follower=False)
        self.system.add_viewer(live.room_id, "user_c", platform="douyin", is_follower=True)

        # 记录一些互动
        viewers = self.system.viewer_mgr.list_viewers(room_id=live.room_id)
        for v in viewers[:2]:
            self.system.viewer_mgr.record_interaction(v.viewer_id)
            self.system.viewer_mgr.record_purchase(v.viewer_id)

        # 获取观众画像
        profile = self.system.get_viewer_profile(live.room_id)

        self.assert_equal(profile['room_id'], live.room_id, "房间号正确")
        self.assert_equal(profile['total_viewers'], 3, "观众总数正确")
        self.assert_equal(profile['followers_count'], 2, "粉丝数正确")
        self.assert_true(profile['total_interactions'] >= 2, "总互动数正确")
        self.assert_true(profile['total_purchases'] >= 2, "总购买数正确")

    def test_chat_management(self):
        """测试弹幕管理"""
        print("\n📋 测试弹幕管理...")

        # 测试1: 添加弹幕
        chat = self.system.add_chat(
            room_id="777888999",
            user_id="user_001",
            username="用户A",
            content="这个商品多少钱？"
        )
        self.assert_true(chat.chat_id.startswith("chat_"), "弹幕ID格式正确")
        self.assert_equal(chat.content, "这个商品多少钱？", "弹幕内容正确")

        # 测试2: 添加更多弹幕
        self.system.add_chat("777888999", "user_002", "用户B", "买一送一吗？")
        self.system.add_chat("777888999", "user_003", "用户C", "价格不错")
        self.system.add_chat("777888999", "user_001", "用户A", "多少钱")
        self.system.add_chat("777888999", "user_004", "用户D", "价格")

        # 测试3: 获取热门话题
        topics = self.system.get_hot_topics("777888999", limit=5)
        self.assert_true(len(topics) > 0, "热门话题列表不为空")

        # 验证"价格"是热门话题
        price_topic = [t for t in topics if t['topic'] == '价格']
        self.assert_true(len(price_topic) > 0, "'价格'是热门话题")

    def test_conversion_funnel(self):
        """测试转化漏斗"""
        print("\n📋 测试转化漏斗...")

        # 创建直播和商品
        live = self.system.create_live(
            room_id="000111222",
            platform="douyin",
            title="转化测试直播"
        )

        product = self.system.add_product("测试商品A", 199, 50)
        self.system.add_product_to_live(live.live_id, product.product_id)

        # 添加观众
        self.system.add_viewer(live.room_id, "user_1", platform="douyin")
        self.system.add_viewer(live.room_id, "user_2", platform="douyin")
        self.system.add_viewer(live.room_id, "user_3", platform="douyin")
        self.system.add_viewer(live.room_id, "user_4", platform="douyin")
        self.system.add_viewer(live.room_id, "user_5", platform="douyin")

        # 记录互动和购买
        viewers = self.system.viewer_mgr.list_viewers(room_id=live.room_id)
        self.system.viewer_mgr.record_interaction(viewers[0].viewer_id)
        self.system.viewer_mgr.record_interaction(viewers[1].viewer_id)
        self.system.viewer_mgr.record_interaction(viewers[2].viewer_id)
        self.system.viewer_mgr.record_purchase(viewers[0].viewer_id)
        self.system.viewer_mgr.record_purchase(viewers[1].viewer_id)

        # 记录点击和销售
        self.system.record_click(product.product_id)
        self.system.record_click(product.product_id)
        self.system.record_sale(product.product_id, 2)

        # 获取转化漏斗
        funnel = self.system.conversion_funnel(live.live_id)

        self.assert_equal(funnel['total_viewers'], 5, "总观众数正确")
        self.assert_equal(funnel['interaction_viewers'], 3, "互动观众数正确")
        self.assert_equal(funnel['purchasing_viewers'], 2, "购买观众数正确")
        self.assert_equal(funnel['total_clicks'], 2, "总点击数正确")
        self.assert_true(funnel['interaction_rate'] > 0, "互动率大于0")
        self.assert_true(funnel['purchase_rate'] > 0, "购买率大于0")

    def test_live_summary(self):
        """测试直播总览"""
        print("\n📋 测试直播总览...")

        # 创建完整的直播场景
        live = self.system.create_live(
            room_id="333444555",
            platform="douyin",
            title="总览测试直播"
        )

        product = self.system.add_product("总览测试商品", 299, 100)
        self.system.add_product_to_live(live.live_id, product.product_id)

        # 添加观众和互动
        self.system.add_viewer(live.room_id, "user_x", platform="douyin", is_follower=True)
        self.system.add_viewer(live.room_id, "user_y", platform="douyin", is_follower=False)

        viewers = self.system.viewer_mgr.list_viewers(room_id=live.room_id)
        self.system.viewer_mgr.record_interaction(viewers[0].viewer_id)
        self.system.viewer_mgr.record_purchase(viewers[0].viewer_id)

        # 记录直播数据
        self.system.record_viewers(live.live_id, 100)
        self.system.record_interaction(live.live_id)

        # 获取总览
        summary = self.system.live_summary(live.live_id)

        self.assert_true(summary.get('live') is not None, "有直播数据")
        self.assert_true(summary.get('viewer_profile') is not None, "有观众画像")
        self.assert_true(summary.get('conversion') is not None, "有转化数据")

        # 验证直播数据
        live_data = summary['live']
        self.assert_equal(live_data['title'], "总览测试直播", "直播标题正确")
        self.assert_equal(live_data['max_viewers'], 100, "峰值观看正确")

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始直播电商系统测试...")
        print("=" * 60)

        try:
            self.setup()

            # 运行所有测试
            self.test_product_management()
            self.test_product_stats()
            self.test_live_management()
            self.test_live_stats()
            self.test_viewer_management()
            self.test_viewer_profile()
            self.test_chat_management()
            self.test_conversion_funnel()
            self.test_live_summary()

            # 打印测试总结
            print("\n" + "=" * 60)
            print("📊 测试总结")
            print("=" * 60)

            total_tests = len(self.test_results)
            passed_tests = sum(1 for _, passed, _ in self.test_results if passed)
            failed_tests = total_tests - passed_tests

            print(f"总测试数: {total_tests}")
            print(f"通过: {passed_tests} ✅")
            print(f"失败: {failed_tests} ❌")
            print(f"通过率: {passed_tests/total_tests*100:.1f}%")

            if failed_tests > 0:
                print("\n❌ 失败的测试:")
                for name, passed, message in self.test_results:
                    if not passed:
                        print(f"   {message}")

            return failed_tests == 0

        finally:
            self.teardown()


if __name__ == "__main__":
    tester = TestLiveCommerce()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
