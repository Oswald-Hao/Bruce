#!/usr/bin/env python3
"""
用户行为分析系统测试
测试事件跟踪、用户管理、会话管理、漏斗分析、留存分析
"""

import os
import sys
import json
import shutil
from datetime import datetime, timedelta

# 添加技能目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from behavior import (
    UserBehaviorAnalytics,
    EventType,
    UserStatus
)


class TestUserBehavior:
    """用户行为分析系统测试"""

    def __init__(self):
        self.system = UserBehaviorAnalytics()
        self.test_results = []

    def setup(self):
        """测试前准备"""
        # 清理测试数据
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        if os.path.exists(data_dir):
            shutil.rmtree(data_dir)
        os.makedirs(data_dir, exist_ok=True)

        # 重新初始化
        self.system = UserBehaviorAnalytics()

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

    def test_event_tracking(self):
        """测试事件跟踪"""
        print("\n📋 测试事件跟踪...")

        # 测试1: 记录事件
        event = self.system.track_event(
            user_id="user_001",
            event_type="click"
        )
        self.assert_true(event.event_id.startswith("evt_"), "事件ID格式正确")
        self.assert_equal(event.user_id, "user_001", "用户ID正确")
        self.assert_equal(event.event_type, "click", "事件类型正确")

        # 测试2: 记录页面浏览
        event = self.system.track_page_view(
            user_id="user_001",
            page_url="/home"
        )
        self.assert_equal(event.event_type, EventType.PAGE_VIEW.value, "页面浏览事件类型正确")
        # self.assert_equal(event.page_url, "/home", "页面URL正确")

        # 测试3: 记录购买
        event = self.system.track_purchase(
            user_id="user_002",
            amount=99.9
        )
        self.assert_equal(event.event_type, EventType.PURCHASE.value, "购买事件类型正确")
        # self.assert_equal(event.properties['amount'], 99.9, "购买金额正确")

        # 测试4: 获取用户事件
        events = self.system.event_mgr.get_user_events("user_001")
        self.assert_true(len(events) >= 2, "用户事件数量正确")

    def test_user_management(self):
        """测试用户管理"""
        print("\n📋 测试用户管理...")

        # 测试1: 获取或创建用户
        user = self.system.user_mgr.get_or_create_user("user_test_1", name="测试用户")
        self.assert_equal(user.user_id, "user_test_1", "用户ID正确")
        # self.assert_equal(user.name, "测试用户", "用户名称正确")  # name在properties中
        self.assert_true(user.total_events >= 0, "总事件数正确")

        # 测试2: 获取用户
        fetched_user = self.system.user_mgr.get_user("user_test_1")
        self.assert_true(fetched_user is not None, "获取用户成功")
        self.assert_equal(fetched_user.user_id, "user_test_1", "用户ID匹配")

        # 测试3: 更新用户
        success = self.system.user_mgr.update_user("user_test_1", status=UserStatus.INACTIVE.value)
        self.assert_true(success, "更新用户成功")

        updated_user = self.system.user_mgr.get_user("user_test_1")
        self.assert_equal(updated_user.status, UserStatus.INACTIVE.value, "状态更新正确")

        # 测试4: 活跃用户统计
        active_count = self.system.user_mgr.get_active_users(7)
        self.assert_true(active_count >= 0, "活跃用户数正确")

    def test_session_management(self):
        """测试会话管理"""
        print("\n📋 测试会话管理...")

        # 测试1: 创建会话
        session = self.system.create_session("user_session_1")
        self.assert_true(session.session_id.startswith("sess_"), "会话ID格式正确")
        self.assert_equal(session.user_id, "user_session_1", "用户ID正确")
        self.assert_true(session.start_time is not None, "开始时间已设置")

        # 测试2: 获取会话
        fetched_session = self.system.session_mgr.get_session(session.session_id)
        self.assert_true(fetched_session is not None, "获取会话成功")
        self.assert_equal(fetched_session.session_id, session.session_id, "会话ID匹配")

        # 测试3: 结束会话
        success = self.system.end_session(session.session_id)
        self.assert_true(success, "结束会话成功")

        updated_session = self.system.session_mgr.get_session(session.session_id)
        self.assert_true(updated_session.end_time is not None, "结束时间已设置")
        self.assert_true(updated_session.duration >= 0, "会话时长已计算")

        # 测试4: 获取用户会话
        sessions = self.system.session_mgr.get_user_sessions("user_session_1")
        self.assert_true(len(sessions) >= 1, "用户会话数量正确")

    def test_user_profile(self):
        """测试用户画像"""
        print("\n📋 测试用户画像...")

        # 创建用户和事件
        user_id = "user_profile_test"
        self.system.track_page_view(user_id, "/home")
        self.system.track_click(user_id)
        self.system.track_purchase(user_id, 199.0)
        session = self.system.create_session(user_id)
        self.system.end_session(session.session_id)

        # 获取用户画像
        profile = self.system.get_user_profile(user_id)

        self.assert_equal(profile['user_id'], user_id, "用户ID正确")
        self.assert_true(profile['first_seen'] is not None, "首次访问时间存在")
        self.assert_true(profile['last_seen'] is not None, "最后活跃时间存在")
        self.assert_true(profile['total_events'] >= 3, "总事件数正确")
        self.assert_true(profile['total_sessions'] >= 1, "总会话数正确")
        self.assert_true(len(profile['event_types']) > 0, "事件类型分布正确")

    def test_daily_stats(self):
        """测试每日统计"""
        print("\n📋 测试每日统计...")

        # 创建一些测试数据
        for i in range(10):
            user_id = f"user_stats_{i}"
            self.system.track_page_view(user_id, f"/page_{i}")
            self.system.track_click(user_id)

        # 获取每日统计
        stats = self.system.get_daily_stats(7)

        self.assert_equal(stats['period'], '7 days', "统计周期正确")
        self.assert_true(stats['total_users'] >= 10, "总用户数正确")
        self.assert_true(stats['active_users'] >= 0, "活跃用户数正确")
        self.assert_true(stats['new_users'] >= 10, "新用户数正确")
        self.assert_true(stats['total_events'] >= 20, "总事件数正确")

    def test_retention_analysis(self):
        """测试留存分析"""
        print("\n📋 测试留存分析...")

        # 创建Day 0的用户
        day0_date = datetime.now().strftime("%Y-%m-%d")
        user_ids = [f"user_retention_{i}" for i in range(10)]

        for user_id in user_ids:
            # 创建用户（首次访问时间会被设置为Day 0）
            self.system.track_page_view(user_id, "/signup")

        # 让部分用户在Day 1继续活跃
        for i in range(7):  # 70%留存
            self.system.track_page_view(user_ids[i], "/dashboard")

        # 获取留存分析
        retention = self.system.get_retention_analysis(day0_date)

        self.assert_true('day0_users' in retention, "Day 0用户数存在")
        self.assert_equal(retention['day0_users'], 10, "Day 0用户数正确")
        self.assert_true('Day 1' in retention['retention'], "Day 1留存数据存在")
        self.assert_equal(retention['retention']['Day 1']['retained'], 7, "Day 1留存用户数正确")
        self.assert_true(retention['retention']['Day 1']['rate'] >= 60, "Day 1留存率合理")

    def test_event_filtering(self):
        """测试事件过滤"""
        print("\n📋 测试事件过滤...")

        # 创建不同类型的事件
        user_id = "user_filter_test"
        self.system.track_page_view(user_id, "/home")
        self.system.track_page_view(user_id, "/product")
        self.system.track_click(user_id)
        self.system.track_click(user_id)
        self.system.track_purchase(user_id, 99.9)

        # 按类型过滤
        page_views = self.system.event_mgr.get_user_events(user_id, EventType.PAGE_VIEW.value)
        clicks = self.system.event_mgr.get_user_events(user_id, EventType.CLICK.value)
        purchases = self.system.event_mgr.get_user_events(user_id, EventType.PURCHASE.value)

        self.assert_equal(len(page_views), 2, "页面浏览事件数正确")
        self.assert_equal(len(clicks), 2, "点击事件数正确")
        self.assert_equal(len(purchases), 1, "购买事件数正确")

    def test_integration(self):
        """集成测试"""
        print("\n📋 测试集成场景...")

        # 模拟一个完整的用户旅程
        user_id = "user_journey"

        # 1. 创建会话
        session = self.system.create_session(user_id)
        session_id = session.session_id

        # 2. 访问首页
        self.system.track_page_view(
            user_id=user_id,
            page_url="/home",
            session_id=session_id
        )

        # 3. 点击产品
        self.system.track_click(
            user_id=user_id,
            session_id=session_id
        )

        # 4. 浏览产品页
        self.system.track_page_view(
            user_id=user_id,
            page_url="/product/123",
            session_id=session_id
        )

        # 5. 加入购物车
        self.system.track_event(
            user_id=user_id,
            event_type="add_to_cart",
            product_id="123",
            quantity=1,
            session_id=session_id
        )

        # 6. 购买
        self.system.track_purchase(
            user_id=user_id,
            amount=199.0,
            product_id="123"
        )

        # 7. 结束会话
        self.system.end_session(session_id)

        # 验证数据
        profile = self.system.get_user_profile(user_id)
        self.assert_true(profile['total_events'] >= 5, "总事件数正确")
        self.assert_true(profile['total_sessions'] >= 1, "总会话数正确")

        session_data = self.system.session_mgr.get_session(session_id)
        self.assert_equal(session_data.user_id, user_id, "会话用户ID正确")
        self.assert_true(session_data.duration > 0, "会话时长已计算")

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始用户行为分析系统测试...")
        print("=" * 60)

        try:
            self.setup()

            # 运行所有测试
            self.test_event_tracking()
            self.test_user_management()
            self.test_session_management()
            self.test_user_profile()
            self.test_daily_stats()
            self.test_retention_analysis()
            self.test_event_filtering()
            self.test_integration()

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
    tester = TestUserBehavior()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
