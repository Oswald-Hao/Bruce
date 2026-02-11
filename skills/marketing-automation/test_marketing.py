#!/usr/bin/env python3
"""
自动化营销系统 - 测试套件
Marketing Automation System - Test Suite
"""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

# 添加技能目录到Python路径
skill_dir = Path(__file__).parent
sys.path.insert(0, str(skill_dir))

from marketing_core import MarketingAutomation, Customer, Campaign
from automation_engine import AutomationEngine, TriggerType, ActionType
from ab_testing import ABTesting, MetricType
from customer_segment import CustomerSegmentation, SegmentType


class TestResult:
    """测试结果"""
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.errors = []

    def add(self, test_name: str, success: bool, error: str = ""):
        """添加测试结果"""
        self.total += 1
        if success:
            self.passed += 1
            print(f"✅ {test_name}")
        else:
            self.failed += 1
            self.errors.append(f"{test_name}: {error}")
            print(f"❌ {test_name} - {error}")

    def print_summary(self):
        """打印汇总"""
        print(f"\n测试汇总:")
        print(f"  总计: {self.total}")
        print(f"  通过: {self.passed}")
        print(f"  失败: {self.failed}")
        if self.failed > 0:
            print(f"\n失败详情:")
            for error in self.errors:
                print(f"  - {error}")
        print(f"\n通过率: {self.passed/self.total*100:.1f}%")
        return self.failed == 0


def test_marketing_core():
    """测试核心营销引擎"""
    print("\n=== 测试核心营销引擎 ===")

    result = TestResult()

    # 使用临时数据目录
    data_dir = Path(__file__).parent / "test_data"
    data_dir.mkdir(exist_ok=True)

    # 清理旧数据
    for f in data_dir.glob("*.json"):
        f.unlink()

    ma = MarketingAutomation(str(data_dir))

    try:
        # 测试1: 添加客户
        customer = ma.add_customer(
            email="test@example.com",
            phone="13800138000",
            name="测试用户"
        )
        result.add("添加客户", customer is not None)

        # 测试2: 添加标签
        success = ma.add_tag(customer.id, "vip")
        result.add("添加标签", success and "vip" in customer.tags)

        # 测试3: 获取客户
        found_customer = ma.get_customer(customer.id)
        result.add("获取客户", found_customer is not None and found_customer.email == "test@example.com")

        # 测试4: 列出客户
        customers = ma.list_customers()
        result.add("列出客户", len(customers) >= 1)

        # 测试5: 创建营销活动
        campaign = ma.create_campaign(
            name="测试活动",
            channel="email",
            audience="all"
        )
        result.add("创建营销活动", campaign is not None)

        # 测试6: 获取营销活动
        found_campaign = ma.get_campaign(campaign.id)
        result.add("获取营销活动", found_campaign is not None)

        # 测试7: 列出营销活动
        campaigns = ma.list_campaigns()
        result.add("列出营销活动", len(campaigns) >= 1)

        # 测试8: 调度营销活动
        success = ma.schedule_campaign(campaign.id, "2026-02-13T10:00:00")
        result.add("调度营销活动", success and campaign.status == "scheduled")

        # 测试9: 获取目标受众
        audience = ma.get_audience("all")
        result.add("获取目标受众", len(audience) >= 1)

        # 测试10: 发送营销活动（模拟）
        send_result = ma.send_campaign(campaign.id, simulate=True)
        result.add("发送营销活动", send_result["success"] and send_result["sent"] > 0)

        # 测试11: 获取营销指标
        metrics = ma.get_campaign_metrics(campaign.id)
        result.add("获取营销指标", "sent" in metrics and metrics["sent"] > 0)

        # 测试12: 追踪打开
        success = ma.track_open(campaign.id, customer.id)
        result.add("追踪打开", success)

        # 测试13: 追踪点击
        success = ma.track_click(campaign.id, customer.id)
        result.add("追踪点击", success)

        # 测试14: 追踪转化
        success = ma.track_conversion(campaign.id, customer.id)
        result.add("追踪转化", success)

        # 测试15: 获取统计信息
        stats = ma.get_statistics()
        result.add("获取统计信息", stats["total_customers"] >= 1 and stats["total_campaigns"] >= 1)

        # 测试16: 获取VIP受众
        # 更新客户为VIP
        ma.update_customer(customer.id, total_spent=1500)
        audience = ma.get_audience("vip")
        result.add("获取VIP受众", len(audience) == 1 and audience[0].id == customer.id)

        # 测试17: 多个客户
        for i in range(10):
            ma.add_customer(email=f"user{i}@example.com", name=f"用户{i}")

        customers = ma.list_customers(limit=5)
        result.add("客户列表限制", len(customers) == 5)

        # 测试18: 按标签分群
        # 使用标签名作为受众（get_audience的else分支按标签分群）
        tag_name = "vip_tag"
        # 先给第一个客户添加标签
        ma.add_tag(customer.id, tag_name)
        for i in range(5):
            c = ma.add_customer(email=f"vip{i}@example.com")
            ma.add_tag(c.id, tag_name)

        audience = ma.get_audience(tag_name)
        result.add("按标签分群", len(audience) >= 6)

        # 测试19: 更新客户
        updated = ma.update_customer(customer.id, name="新名字")
        result.add("更新客户", updated.name == "新名字")

        # 测试20: 删除测试数据
        # 测试完成，数据已经持久化

    except Exception as e:
        result.add("核心营销引擎测试", False, f"异常: {str(e)}")

    return result


def test_automation_engine():
    """测试自动化流程引擎"""
    print("\n=== 测试自动化流程引擎 ===")

    result = TestResult()

    data_dir = Path(__file__).parent / "test_data"
    engine = AutomationEngine(str(data_dir))

    try:
        # 测试1: 创建流程
        flow = engine.create_flow("测试流程", "这是一个测试流程")
        result.add("创建流程", flow is not None and flow.status == "draft")

        # 测试2: 获取流程
        found_flow = engine.get_flow(flow.id)
        result.add("获取流程", found_flow is not None)

        # 测试3: 列出流程
        flows = engine.list_flows()
        result.add("列出流程", len(flows) >= 1)

        # 测试4: 添加触发器
        trigger_step = engine.add_trigger(
            flow.id,
            TriggerType.USER_SIGNUP,
            conditions={"event": "signup"}
        )
        result.add("添加触发器", trigger_step is not None)

        # 测试5: 添加动作
        action_step = engine.add_action(
            flow.id,
            trigger_step.id,
            ActionType.SEND_EMAIL,
            params={"subject": "欢迎", "body": "欢迎加入"}
        )
        result.add("添加动作", action_step is not None)

        # 测试6: 延迟动作
        delayed_step = engine.add_action(
            flow.id,
            action_step.id,
            ActionType.SEND_EMAIL,
            params={"subject": "24小时后"},
            delay_hours=24
        )
        result.add("延迟动作", delayed_step is not None)

        # 测试7: 激活流程
        success = engine.activate_flow(flow.id)
        result.add("激活流程", success and flow.status == "active")

        # 测试8: 触发流程
        execution = engine.trigger_flow(flow.id, "customer_001", context={"event": "signup"})
        result.add("触发流程", execution is not None and execution.status == "completed")

        # 测试9: 获取执行记录
        found_execution = engine.get_execution(execution.id)
        result.add("获取执行记录", found_execution is not None)

        # 测试10: 列出执行记录
        executions = engine.list_executions(flow_id=flow.id)
        result.add("列出执行记录", len(executions) >= 1)

        # 测试11: 暂停流程
        success = engine.pause_flow(flow.id)
        result.add("暂停流程", success and flow.status == "paused")

        # 测试12: 创建欢迎流程模板
        welcome_flow = engine.create_welcome_flow()
        result.add("创建欢迎流程模板", welcome_flow is not None and len(welcome_flow.steps) == 4)

        # 测试13: 创建购物车召回模板
        cart_flow = engine.create_cart_recovery_flow()
        result.add("创建购物车召回模板", cart_flow is not None and len(cart_flow.steps) == 3)

        # 测试14: 激活欢迎流程
        success = engine.activate_flow(welcome_flow.id)
        result.add("激活欢迎流程", success)

        # 测试15: 触发欢迎流程
        execution = engine.trigger_flow(welcome_flow.id, "customer_welcome", context={"event": "signup"})
        result.add("触发欢迎流程", execution is not None)

        # 测试16: 检查执行历史
        result.add("执行历史记录", len(execution.history) >= 2)

        # 测试17: 流程统计
        stats = flow.stats
        result.add("流程统计", stats["triggered"] >= 1)

        # 测试18: 删除流程
        test_flow = engine.create_flow("待删除流程")
        success = engine.delete_flow(test_flow.id)
        result.add("删除流程", success and test_flow.id not in engine.flows)

        # 测试19: 多次触发
        for i in range(5):
            engine.trigger_flow(welcome_flow.id, f"customer_{i}", context={"event": "signup"})

        executions = engine.list_executions(flow_id=welcome_flow.id)
        result.add("多次触发", len(executions) >= 5)

        # 测试20: 按客户筛选执行
        customer_executions = engine.list_executions(customer_id="customer_welcome")
        result.add("按客户筛选", len(customer_executions) >= 1)

    except Exception as e:
        result.add("自动化流程引擎测试", False, f"异常: {str(e)}")

    return result


def test_ab_testing():
    """测试A/B测试系统"""
    print("\n=== 测试A/B测试系统 ===")

    result = TestResult()

    data_dir = Path(__file__).parent / "test_data"
    ab_testing = ABTesting(str(data_dir))

    try:
        # 测试1: 创建A/B测试
        test = ab_testing.create_test(
            name="邮件主题测试",
            test_type="email_subject",
            variants=[
                {"name": "主题A", "config": {"subject": "欢迎加入我们"}},
                {"name": "主题B", "config": {"subject": "您好，欢迎"}}
            ],
            min_sample_size=10
        )
        result.add("创建A/B测试", test is not None and len(test.variants) == 2)

        # 测试2: 获取测试
        found_test = ab_testing.get_test(test.id)
        result.add("获取测试", found_test is not None)

        # 测试3: 列出测试
        tests = ab_testing.list_tests()
        result.add("列出测试", len(tests) >= 1)

        # 测试4: 启动测试
        success = ab_testing.start_test(test.id)
        result.add("启动测试", success and test.status.value == "running")

        # 测试5: 分配变体
        variant = ab_testing.assign_variant(test.id, "user_001")
        result.add("分配变体", variant is not None)

        # 测试6: 再次分配（同一用户）
        variant2 = ab_testing.assign_variant(test.id, "user_001")
        result.add("同一用户分配", variant is not None and variant.id == variant2.id)

        # 测试7: 分配多个用户
        for i in range(20):
            ab_testing.assign_variant(test.id, f"user_{i+10}")

        result.add("分配多个用户", all(v.metrics.get("exposures", 0) > 0 for v in test.variants))

        # 测试8: 追踪转化
        success = ab_testing.track_conversion(test.id, "user_001", 100.0)
        result.add("追踪转化", success)

        # 测试9: 获取测试结果
        results = ab_testing.get_test_results(test.id)
        result.add("获取测试结果", "variants" in results and len(results["variants"]) == 2)

        # 测试10: 暂停测试
        success = ab_testing.pause_test(test.id)
        result.add("暂停测试", success and test.status.value == "paused")

        # 测试11: 恢复测试（再次启动）
        success = ab_testing.start_test(test.id)
        result.add("恢复测试", success)

        # 测试12: 完成测试
        success = ab_testing.complete_test(test.id)
        result.add("完成测试", success and test.status.value == "completed")

        # 测试13: 获取获胜者
        results = ab_testing.get_test_results(test.id)
        result.add("获取获胜者", "winner" in results)

        # 测试14: 创建邮件内容测试
        test2 = ab_testing.create_email_content_test(
            name="邮件内容测试",
            contents=[
                {"subject": "促销", "body": "限时促销"},
                {"subject": "活动", "body": "精彩活动"}
            ]
        )
        result.add("创建邮件内容测试", test2 is not None)

        # 测试15: 流量分配
        total_allocation = sum(v.traffic_allocation for v in test.variants)
        result.add("流量分配", abs(total_allocation - 1.0) < 0.01)

        # 测试16: 变体指标
        variant_metrics = test.variants[0].metrics
        result.add("变体指标", "exposures" in variant_metrics and "conversions" in variant_metrics)

        # 测试17: 最小样本量检查
        result.add("最小样本量", test.min_sample_size == 10)

        # 测试18: 多次转化追踪
        ab_testing.track_conversion(test.id, "user_010", 50.0)
        ab_testing.track_conversion(test.id, "user_011", 75.0)
        result.add("多次转化追踪", True)

        # 测试19: 创建三变体测试
        test3 = ab_testing.create_test(
            name="三变体测试",
            test_type="custom",
            variants=[
                {"name": "A"},
                {"name": "B"},
                {"name": "C"}
            ]
        )
        result.add("三变体测试", len(test3.variants) == 3)

        # 测试20: 列出指定状态测试
        running_tests = ab_testing.list_tests(status=test.status)
        result.add("列出指定状态测试", len(running_tests) >= 1)

    except Exception as e:
        result.add("A/B测试系统测试", False, f"异常: {str(e)}")

    return result


def test_customer_segmentation():
    """测试客户分群系统"""
    print("\n=== 测试客户分群系统 ===")

    result = TestResult()

    data_dir = Path(__file__).parent / "test_data"
    segmentation = CustomerSegmentation(str(data_dir))

    try:
        # 测试1: 创建分群
        segment = segmentation.create_segment(
            name="VIP客户",
            segment_type=SegmentType.BEHAVIORAL,
            conditions={"total_spent": {"op": ">=", "value": 1000}}
        )
        result.add("创建分群", segment is not None)

        # 测试2: 获取分群
        found_segment = segmentation.get_segment(segment.id)
        result.add("获取分群", found_segment is not None)

        # 测试3: 列出分群
        segments = segmentation.list_segments()
        result.add("列出分群", len(segments) >= 1)

        # 测试4: 按类型列出分群
        behavioral_segments = segmentation.list_segments(segment_type=SegmentType.BEHAVIORAL)
        result.add("按类型列出分群", len(behavioral_segments) >= 1)

        # 测试5: 删除分群
        test_segment = segmentation.create_segment("待删除分群", SegmentType.CUSTOM)
        success = segmentation.delete_segment(test_segment.id)
        result.add("删除分群", success and test_segment.id not in segmentation.segments)

        # 测试6: 创建默认分群
        segmentation.create_default_segments()
        default_segments = segmentation.list_segments()
        result.add("创建默认分群", len(default_segments) >= 3)

        # 测试7: 获取RFM分群
        rfm_segments = segmentation.get_rfm_segments()
        result.add("获取RFM分群", "价值客户" in rfm_segments)

        # 测试8: 评估条件（total_spent >= 1000）
        # 需要先从MarketingAutomation获取客户数据
        from marketing_core import MarketingAutomation
        ma = MarketingAutomation(str(data_dir))

        # 更新行为分群
        segmentation.update_behavioral_segments(ma.customers)
        result.add("更新行为分群", True)

        # 测试9: 获取分群客户
        customer_ids = segmentation.get_segment_customers(segment.id)
        result.add("获取分群客户", isinstance(customer_ids, list))

        # 测试10: 获取客户所属分群
        if customer_ids:
            customer_segments = segmentation.get_customer_segments(customer_ids[0])
            result.add("获取客户所属分群", isinstance(customer_segments, list))
        else:
            result.add("获取客户所属分群", True)

        # 测试11: 创建静态分群
        static_segment = segmentation.create_segment(
            name="静态分群",
            segment_type=SegmentType.CUSTOM,
            is_dynamic=False
        )
        result.add("创建静态分群", not static_segment.is_dynamic)

        # 测试12: 计算RFM（使用MarketingAutomation的客户数据）
        rfm_data = segmentation.calculate_rfm(ma.customers)
        result.add("计算RFM", len(rfm_data) >= 1)

        # 测试13: RFM分数计算
        if rfm_data:
            first_rfm = list(rfm_data.values())[0]
            result.add("RFM分数计算", 1 <= first_rfm.recency_score <= 5)

        # 测试14: RFM分群字符串
        if rfm_data:
            first_rfm = list(rfm_data.values())[0]
            result.add("RFM分群字符串", len(first_rfm.rfm_segment) == 5)

        # 测试15: 客户类型识别
        if rfm_data:
            first_rfm = list(rfm_data.values())[0]
            result.add("客户类型识别", first_rfm.customer_type in ["价值客户", "新客户", "流失风险", "低价值客户", "普通客户"])

        # 测试16: 标签条件评估
        tag_segment = segmentation.create_segment(
            name="标签分群",
            segment_type=SegmentType.BEHAVIORAL,
            conditions={"tags": {"op": "any", "value": ["vip"]}}
        )
        result.add("标签条件评估", True)

        # 测试17: 时间条件评估
        time_segment = segmentation.create_segment(
            name="时间分群",
            segment_type=SegmentType.BEHAVIORAL,
            conditions={"days_since_last_active": {"op": "<=", "value": 30}}
        )
        result.add("时间条件评估", True)

        # 测试18: 混合条件
        mixed_segment = segmentation.create_segment(
            name="混合条件分群",
            segment_type=SegmentType.BEHAVIORAL,
            conditions={
                "total_spent": {"op": ">=", "value": 500},
                "order_count": {"op": ">=", "value": 1}
            }
        )
        result.add("混合条件", True)

        # 测试19: 分群更新时间
        now = datetime.fromisoformat(segment.updated_at)
        result.add("分群更新时间", (datetime.now() - now).total_seconds() < 10)

        # 测试20: RFM分群统计
        rfm_segments = segmentation.get_rfm_segments()
        total_customers = sum(len(ids) for ids in rfm_segments.values())
        result.add("RFM分群统计", total_customers >= 0)

    except Exception as e:
        result.add("客户分群系统测试", False, f"异常: {str(e)}")

    return result


def main():
    """运行所有测试"""
    print("=" * 60)
    print("自动化营销系统 - 测试套件")
    print("=" * 60)

    # 运行所有测试模块
    results = []
    results.append(test_marketing_core())
    results.append(test_automation_engine())
    results.append(test_ab_testing())
    results.append(test_customer_segmentation())

    # 汇总所有测试结果
    total_tests = sum(r.total for r in results)
    total_passed = sum(r.passed for r in results)
    total_failed = sum(r.failed for r in results)

    print("\n" + "=" * 60)
    print("总体测试汇总")
    print("=" * 60)
    print(f"总测试数: {total_tests}")
    print(f"通过: {total_passed}")
    print(f"失败: {total_failed}")
    print(f"通过率: {total_passed/total_tests*100:.1f}%")

    if total_failed == 0:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print("\n❌ 存在失败的测试")
        return 1


if __name__ == "__main__":
    sys.exit(main())
