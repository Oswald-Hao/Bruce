#!/usr/bin/env python3
"""
智能广告投放优化系统测试
测试广告账户管理、广告系列、A/B测试、ROI分析、自动化优化
"""

import os
import sys
import json
import shutil
from datetime import datetime, timedelta

# 添加技能目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from ad import (
    AdOptimizer,
    Platform,
    BiddingStrategy,
    CampaignStatus,
    TestStatus
)


class TestAdOptimizer:
    """智能广告投放优化系统测试"""

    def __init__(self):
        self.optimizer = AdOptimizer()
        self.test_results = []

    def setup(self):
        """测试前准备"""
        # 清理测试数据
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        if os.path.exists(data_dir):
            shutil.rmtree(data_dir)
        os.makedirs(data_dir, exist_ok=True)

        # 重新初始化
        self.optimizer = AdOptimizer()

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

    def test_account_management(self):
        """测试广告账户管理"""
        print("\n📋 测试广告账户管理...")

        # 测试1: 添加账户
        account = self.optimizer.add_account(
            platform="google",
            account_id="123-456-7890",
            name="主账户"
        )
        self.assert_equal(account.account_id, "123-456-7890", "账户ID正确")
        self.assert_equal(account.platform, "google", "平台正确")
        self.assert_equal(account.name, "主账户", "账户名称正确")

        # 测试2: 列出账户
        accounts = self.optimizer.list_accounts(platform="google")
        self.assert_true(len(accounts) >= 1, "列出账户数量正确")

        # 测试3: 添加更多账户
        self.optimizer.add_account("facebook", "act_123456", "Facebook账户")
        self.optimizer.add_account("douyin", "123456", "抖音账户")

    def test_campaign_management(self):
        """测试广告系列管理"""
        print("\n📋 测试广告系列管理...")

        # 创建账户
        account = self.optimizer.add_account("google", "123-456-7890", "测试账户")

        # 测试1: 创建广告系列
        campaign = self.optimizer.create_campaign(
            account_id=account.account_id,
            name="测试广告系列",
            budget=10000
        )
        self.assert_true(campaign.campaign_id.startswith("camp_"), "广告系列ID格式正确")
        self.assert_equal(campaign.name, "测试广告系列", "广告系列名称正确")
        self.assert_equal(campaign.budget, 10000, "预算正确")

        # 测试2: 暂停广告系列
        success = self.optimizer.pause_campaign(campaign.campaign_id)
        self.assert_true(success, "暂停广告系列成功")

        paused_campaign = self.optimizer.campaign_mgr.get_campaign(campaign.campaign_id)
        self.assert_equal(paused_campaign.status, CampaignStatus.PAUSED.value, "状态已更新")

        # 测试3: 激活广告系列
        success = self.optimizer.activate_campaign(campaign.campaign_id)
        self.assert_true(success, "激活广告系列成功")

        # 测试4: 列出广告系列
        campaigns = self.optimizer.list_campaigns(status=CampaignStatus.ACTIVE.value)
        self.assert_true(len(campaigns) >= 1, "列出广告系列数量正确")

    def test_metrics_update(self):
        """测试广告数据更新"""
        print("\n📋 测试广告数据更新...")

        # 创建广告系列
        account = self.optimizer.add_account("google", "987-654-3210", "数据测试账户")
        campaign = self.optimizer.create_campaign(account.account_id, "数据测试", 5000)

        # 测试1: 更新数据
        metrics = {
            'impressions': 10000,
            'clicks': 500,
            'conversions': 25,
            'cost': 1000,
            'revenue': 3000
        }
        success = self.optimizer.update_metrics(campaign.campaign_id, metrics)
        self.assert_true(success, "数据更新成功")

        # 测试2: 验证数据
        updated_campaign = self.optimizer.campaign_mgr.get_campaign(campaign.campaign_id)
        self.assert_equal(updated_campaign.metrics['impressions'], 10000, "展示数正确")
        self.assert_equal(updated_campaign.metrics['clicks'], 500, "点击数正确")
        self.assert_equal(updated_campaign.metrics['conversions'], 25, "转化数正确")
        self.assert_equal(updated_campaign.metrics['cost'], 1000, "成本正确")
        self.assert_equal(updated_campaign.metrics['revenue'], 3000, "收入正确")
        self.assert_equal(updated_campaign.metrics['roi'], 3.0, "ROI计算正确")
        self.assert_true(round(updated_campaign.metrics['ctr'], 2) == 0.05, "CTR计算正确")
        self.assert_true(round(updated_campaign.metrics['conversion_rate'], 2) == 0.05, "转化率计算正确")

    def test_roi_analysis(self):
        """测试ROI分析"""
        print("\n📋 测试ROI分析...")

        # 创建广告系列和数据
        account = self.optimizer.add_account("google", "111-222-3333", "ROI测试账户")
        campaign = self.optimizer.create_campaign(account.account_id, "ROI测试", 10000)
        
        metrics = {
            'impressions': 50000,
            'clicks': 2500,
            'conversions': 125,
            'cost': 5000,
            'revenue': 15000
        }
        self.optimizer.update_metrics(campaign.campaign_id, metrics)

        # 测试1: ROI分析
        analysis = self.optimizer.roi_analysis(campaign.campaign_id)

        self.assert_equal(analysis['campaign_id'], campaign.campaign_id, "广告系列ID正确")
        self.assert_equal(analysis['name'], "ROI测试", "名称正确")
        self.assert_equal(analysis['budget'], 10000, "预算正确")
        self.assert_equal(analysis['cost'], 5000, "成本正确")
        self.assert_equal(analysis['revenue'], 15000, "收入正确")
        self.assert_equal(analysis['roi'], 3.0, "ROI正确")
        self.assert_equal(analysis['impressions'], 50000, "展示数正确")
        self.assert_equal(analysis['clicks'], 2500, "点击数正确")
        self.assert_equal(analysis['conversions'], 125, "转化数正确")

    def test_roi_report(self):
        """测试ROI报告"""
        print("\n📋 测试ROI报告...")

        # 创建一个账户的广告系列
        account_id = "444-555-6666"
        account = self.optimizer.add_account("google", account_id, "报告测试账户")
        
        camp1 = self.optimizer.create_campaign(account.account_id, "广告A", 5000)
        metrics1 = {'impressions': 20000, 'clicks': 1000, 'conversions': 50, 'cost': 2000, 'revenue': 4000}
        self.optimizer.update_metrics(camp1.campaign_id, metrics1)
        
        camp2 = self.optimizer.create_campaign(account.account_id, "广告B", 3000)
        metrics2 = {'impressions': 10000, 'clicks': 300, 'conversions': 10, 'cost': 1000, 'revenue': 500}
        self.optimizer.update_metrics(camp2.campaign_id, metrics2)

        # 测试: 生成单个账户的报告
        report = self.optimizer.roi_report(account_id=account_id)
        summary = report['summary']

        self.assert_equal(len(report['campaigns']), 2, "广告系列数量正确")
        self.assert_equal(summary['total_cost'], 3000, "总成本正确")
        self.assert_equal(summary['total_revenue'], 4500, "总收入正确")
        self.assert_true(round(summary['total_roi'], 2) == 1.5, "总ROI正确")
        self.assert_equal(summary['total_impressions'], 30000, "总展示正确")
        self.assert_equal(summary['total_clicks'], 1300, "总点击正确")
        self.assert_equal(summary['total_conversions'], 60, "总转化正确")

    def test_ab_testing(self):
        """测试A/B测试"""
        print("\n📋 测试A/B测试...")

        # 创建广告系列
        account = self.optimizer.add_account("google", "777-888-9999", "A/B测试账户")
        campaign = self.optimizer.create_campaign(account.account_id, "A/B测试广告", 5000)

        # 测试1: 创建A/B测试
        test = self.optimizer.create_ab_test(
            name="创意测试",
            campaign_id=campaign.campaign_id,
            variable="creative",
            variants=["A", "B", "C"]
        )
        self.assert_true(test.test_id.startswith("test_"), "测试ID格式正确")
        self.assert_equal(test.name, "创意测试", "测试名称正确")
        self.assert_equal(test.variable, "creative", "变量正确")
        self.assert_equal(len(test.variants), 3, "变体数量正确")

        # 测试2: 记录变体结果
        metrics_a = {'impressions': 5000, 'clicks': 250, 'conversions': 12}
        metrics_b = {'impressions': 5000, 'clicks': 280, 'conversions': 15}
        metrics_c = {'impressions': 5000, 'clicks': 230, 'conversions': 10}
        
        self.optimizer.record_variant_result(test.test_id, "A", metrics_a)
        self.optimizer.record_variant_result(test.test_id, "B", metrics_b)
        self.optimizer.record_variant_result(test.test_id, "C", metrics_c)

        # 测试3: 计算胜出变体
        winner = self.optimizer.calculate_winner(test.test_id)
        self.assert_equal(winner, "B", "胜出变体正确")

        # 测试4: 结束测试
        success = self.optimizer.conclude_test(test.test_id)
        self.assert_true(success, "结束测试成功")

        updated_test = self.optimizer.ab_test_mgr.get_test(test.test_id)
        self.assert_equal(updated_test.status, TestStatus.COMPLETED.value, "状态已更新")
        self.assert_equal(updated_test.winner, "B", "胜出变体已记录")

    def test_auto_optimize(self):
        """测试自动化优化"""
        print("\n📋 测试自动化优化...")

        # 创建高ROI和低ROI广告系列
        account = self.optimizer.add_account("google", "000-111-2222", "自动优化账户")
        
        camp_high = self.optimizer.create_campaign(account.account_id, "高ROI广告", 5000)
        metrics_high = {'impressions': 20000, 'clicks': 1000, 'conversions': 100, 'cost': 1000, 'revenue': 5000}
        self.optimizer.update_metrics(camp_high.campaign_id, metrics_high)

        camp_low = self.optimizer.create_campaign(account.account_id, "低ROI广告", 5000)
        metrics_low = {'impressions': 10000, 'clicks': 200, 'conversions': 5, 'cost': 2000, 'revenue': 500}
        self.optimizer.update_metrics(camp_low.campaign_id, metrics_low)

        # 添加优化规则
        self.optimizer.add_optimization_rule(
            type="pause_low_roi",
            name="低ROI自动暂停",
            condition="roi < 1.0",
            action="pause"
        )

        # 测试: 自动优化
        actions = self.optimizer.auto_optimize(roi_threshold=1.0)

        self.assert_true(len(actions) >= 1, "有优化操作")
        self.assert_true(any("低ROI" in action for action in actions), "有暂停低ROI广告的操作")

    def test_optimization_suggestions(self):
        """测试优化建议"""
        print("\n📋 测试优化建议...")

        # 创建广告系列
        account = self.optimizer.add_account("google", "333-444-5555", "建议测试账户")
        campaign = self.optimizer.create_campaign(account.account_id, "建议测试", 5000)
        
        # 创建低ROI广告数据
        metrics = {
            'impressions': 10000,
            'clicks': 50,  # CTR = 0.005 (< 1%)
            'conversions': 1,  # 转化率 = 0.02 (< 1%)
            'cost': 1000,
            'revenue': 500  # ROI = 0.5
        }
        self.optimizer.update_metrics(campaign.campaign_id, metrics)

        # 测试: 生成优化建议
        suggestions = self.optimizer.optimization_suggestions(campaign.campaign_id)

        self.assert_true(len(suggestions) >= 3, "有优化建议")
        self.assert_true(any(s['type'] == 'pause' for s in suggestions), "有暂停建议")
        self.assert_true(any(s['type'] == 'optimize_creative' for s in suggestions), "有优化创意建议")
        self.assert_true(any(s['type'] == 'optimize_landing' for s in suggestions), "有优化落地页建议")

    def test_competitor_management(self):
        """测试竞品管理"""
        print("\n📋 测试竞品管理...")

        # 测试1: 添加竞品
        competitor = self.optimizer.add_competitor(
            name="竞争对手A",
            platform="google",
            keywords=["关键词1", "关键词2", "关键词3"]
        )
        self.assert_true(competitor.competitor_id.startswith("comp_"), "竞品ID格式正确")
        self.assert_equal(competitor.name, "竞争对手A", "竞品名称正确")
        self.assert_equal(competitor.platform, "google", "平台正确")
        self.assert_equal(len(competitor.keywords), 3, "关键词数量正确")

        # 测试2: 列出竞品
        competitors = self.optimizer.list_competitors(platform="google")
        self.assert_true(len(competitors) >= 1, "列出竞品数量正确")

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始智能广告投放优化系统测试...")
        print("=" * 60)

        try:
            self.setup()

            # 运行所有测试
            self.test_account_management()
            self.test_campaign_management()
            self.test_metrics_update()
            self.test_roi_analysis()
            self.test_roi_report()
            self.test_ab_testing()
            self.test_auto_optimize()
            self.test_optimization_suggestions()
            self.test_competitor_management()

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
    tester = TestAdOptimizer()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
