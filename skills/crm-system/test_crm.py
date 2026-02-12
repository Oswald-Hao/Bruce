#!/usr/bin/env python3
"""
CRM系统测试
测试客户管理、联系人管理、线索管理、商机管理、任务管理、数据分析
"""

import os
import sys
import json
import shutil
from datetime import datetime

# 添加技能目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from crm import (
    CRMSystem,
    CustomerStatus,
    LeadStatus,
    OpportunityStage,
    TaskStatus,
    InteractionType
)


class TestCRM:
    """CRM系统测试"""

    def __init__(self):
        self.crm = CRMSystem()
        self.test_results = []

    def setup(self):
        """测试前准备"""
        # 清理测试数据
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        if os.path.exists(data_dir):
            shutil.rmtree(data_dir)
        os.makedirs(data_dir, exist_ok=True)

        # 重新初始化
        self.crm = CRMSystem()

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

    def test_customer_management(self):
        """测试客户管理"""
        print("\n📋 测试客户管理...")

        # 测试1: 添加客户
        customer = self.crm.add_customer(
            name="测试公司A",
            industry="软件",
            scale="中型",
            phone="0755-12345678",
            email="test@companya.com"
        )
        self.assert_true(customer.customer_id.startswith("cust_"), "客户ID格式正确")
        self.assert_equal(customer.name, "测试公司A", "客户名称正确")

        # 测试2: 搜索客户
        customers = self.crm.search_customers(name="测试公司A")
        self.assert_equal(len(customers), 1, "搜索客户数量正确")

        # 测试3: 更新客户
        success = self.crm.update_customer(customer.customer_id, scale="大型")
        self.assert_true(success, "更新客户成功")

        updated_customer = self.crm.customer_mgr.get_customer(customer.customer_id)
        self.assert_equal(updated_customer.scale, "大型", "客户更新验证成功")

        # 测试4: 添加标签
        success = self.crm.add_tag(customer.customer_id, "VIP")
        self.assert_true(success, "添加标签成功")

        # 测试5: 添加更多客户用于分析
        self.crm.add_customer(name="测试公司B", industry="互联网", scale="小型")
        self.crm.add_customer(name="测试公司C", industry="金融", scale="大型")

    def test_contact_management(self):
        """测试联系人管理"""
        print("\n📋 测试联系人管理...")

        # 先创建客户
        customer = self.crm.add_customer(name="联系人测试公司")

        # 测试1: 添加联系人
        contact = self.crm.add_contact(
            customer_id=customer.customer_id,
            name="张三",
            position="CTO",
            phone="13800138000",
            email="zhangsan@company.com"
        )
        self.assert_true(contact.contact_id.startswith("contact_"), "联系人ID格式正确")
        self.assert_equal(contact.name, "张三", "联系人名称正确")

        # 测试2: 获取客户联系人
        contacts = self.crm.list_contacts(customer.customer_id)
        self.assert_equal(len(contacts), 1, "联系人数量正确")

        # 测试3: 添加沟通记录
        success = self.crm.add_interaction(
            contact_id=contact.contact_id,
            interaction_type="phone",
            content="讨论产品方案"
        )
        self.assert_true(success, "添加沟通记录成功")

        # 测试4: 添加更多联系人
        self.crm.add_contact(
            customer_id=customer.customer_id,
            name="李四",
            position="CEO"
        )

        contacts = self.crm.list_contacts(customer.customer_id)
        self.assert_equal(len(contacts), 2, "多个联系人正确")

    def test_lead_management(self):
        """测试线索管理"""
        print("\n📋 测试线索管理...")

        # 测试1: 添加线索（来源为推荐，应该有高分数）
        lead1 = self.crm.add_lead(
            name="王五",
            company="潜在客户A",
            phone="13900139000",
            email="wangwu@potential.com",
            position="CEO",
            source="referral",
            interest="CRM系统"
        )
        self.assert_true(lead1.lead_id.startswith("lead_"), "线索ID格式正确")
        self.assert_equal(lead1.company, "潜在客户A", "线索公司正确")
        self.assert_true(lead1.score > 50, "线索评分计算正确（推荐来源加分）")

        # 测试2: 添加线索（来源为网站）
        lead2 = self.crm.add_lead(
            name="赵六",
            company="潜在客户B",
            source="website"
        )
        self.assert_true(lead2.score >= 50, "线索评分基础分正确")

        # 测试3: 查询线索
        leads = self.crm.lead_mgr.list_leads(source="referral")
        self.assert_equal(len(leads), 1, "筛选线索数量正确")

        # 测试4: 线索评分
        score = self.crm.score_lead(lead1.lead_id)
        self.assert_equal(score, lead1.score, "线索评分查询正确")

    def test_lead_conversion(self):
        """测试线索转化"""
        print("\n📋 测试线索转化...")

        # 创建线索
        lead = self.crm.add_lead(
            name="转化测试",
            company="将转化的公司",
            phone="13700137000",
            email="convert@test.com",
            position="CTO"
        )

        # 测试: 转化线索
        customer = self.crm.convert_lead(lead.lead_id, "转化后的公司")
        self.assert_true(customer is not None, "线索转化成功")
        self.assert_equal(customer.name, "转化后的公司", "转化后的客户名称正确")
        self.assert_true(len(customer.tags) > 0, "转化客户有标签标记")

        # 验证线索状态已更新
        updated_lead = self.crm.lead_mgr.get_lead(lead.lead_id)
        self.assert_equal(updated_lead.status, LeadStatus.CONVERTED.value, "线索状态已更新")

        # 验证联系人已创建
        contacts = self.crm.list_contacts(customer.customer_id)
        self.assert_true(len(contacts) > 0, "转化后创建了联系人")

    def test_opportunity_management(self):
        """测试商机管理"""
        print("\n📋 测试商机管理...")

        # 先创建客户
        customer = self.crm.add_customer(name="商机测试公司")

        # 测试1: 创建商机（初始阶段）
        opportunity = self.crm.create_opportunity(
            customer_id=customer.customer_id,
            title="CRM系统采购",
            amount=100000,
            stage=OpportunityStage.INITIAL.value
        )
        self.assert_true(opportunity.opportunity_id.startswith("opp_"), "商机ID格式正确")
        self.assert_equal(opportunity.title, "CRM系统采购", "商机标题正确")
        self.assert_equal(opportunity.amount, 100000, "商机金额正确")
        self.assert_equal(opportunity.stage, OpportunityStage.INITIAL.value, "商机阶段正确")
        self.assert_equal(opportunity.probability, 10, "初始阶段概率正确")

        # 测试2: 更新商机阶段
        success = self.crm.update_opportunity(
            opportunity.opportunity_id,
            stage=OpportunityStage.PROPOSAL.value
        )
        self.assert_true(success, "更新商机阶段成功")

        updated_opp = self.crm.opportunity_mgr.get_opportunity(opportunity.opportunity_id)
        self.assert_equal(updated_opp.stage, OpportunityStage.PROPOSAL.value, "阶段更新正确")
        self.assert_equal(updated_opp.probability, 50, "概率自动更新正确")

        # 测试3: 创建多个商机用于漏斗分析
        self.crm.create_opportunity(customer.customer_id, "商机B", 50000, stage=OpportunityStage.INITIAL.value)
        self.crm.create_opportunity(customer.customer_id, "商机C", 200000, stage=OpportunityStage.DISCOVERY.value)

        # 测试4: 查询商机
        opps = self.crm.list_opportunities(stage=OpportunityStage.INITIAL.value)
        self.assert_true(len(opps) >= 1, f"查询商机数量正确 (实际: {len(opps)})")

    def test_opportunity_close(self):
        """测试商机关闭"""
        print("\n📋 测试商机关闭...")

        customer = self.crm.add_customer(name="成交测试公司")

        # 创建商机
        opportunity = self.crm.create_opportunity(
            customer_id=customer.customer_id,
            title="测试商机",
            amount=80000,
            stage=OpportunityStage.NEGOTIATION.value
        )

        # 测试1: 商机成交
        success = self.crm.close_opportunity(
            opportunity.opportunity_id,
            status="won",
            actual_amount=75000
        )
        self.assert_true(success, "商机成交成功")

        closed_opp = self.crm.opportunity_mgr.get_opportunity(opportunity.opportunity_id)
        self.assert_equal(closed_opp.status, "won", "商机状态正确")
        self.assert_equal(closed_opp.stage, OpportunityStage.WON.value, "商机阶段正确")

        # 测试2: 商机流失
        opp2 = self.crm.create_opportunity(customer.customer_id, "测试商机2", 50000)
        success = self.crm.close_opportunity(opp2.opportunity_id, status="lost")
        self.assert_true(success, "商机流失成功")

        closed_opp2 = self.crm.opportunity_mgr.get_opportunity(opp2.opportunity_id)
        self.assert_equal(closed_opp2.status, "lost", "流失状态正确")
        self.assert_equal(closed_opp2.stage, OpportunityStage.LOST.value, "流失阶段正确")

    def test_task_management(self):
        """测试任务管理"""
        print("\n📋 测试任务管理...")

        customer = self.crm.add_customer(name="任务测试公司")
        contact = self.crm.add_contact(customer.customer_id, "测试联系人")
        opportunity = self.crm.create_opportunity(customer.customer_id, "测试商机", 60000)

        # 测试1: 创建任务
        task = self.crm.create_task(
            task_type="followup",
            title="回访客户",
            customer_id=customer.customer_id,
            contact_id=contact.contact_id,
            opportunity_id=opportunity.opportunity_id,
            description="确认产品使用情况",
            assignee="sales_001"
        )
        self.assert_true(task.task_id.startswith("task_"), "任务ID格式正确")
        self.assert_equal(task.title, "回访客户", "任务标题正确")
        self.assert_equal(task.status, TaskStatus.PENDING.value, "任务初始状态正确")

        # 测试2: 完成任务
        success = self.crm.complete_task(task.task_id)
        self.assert_true(success, "完成任务成功")

        completed_task = self.crm.task_mgr.get_task(task.task_id)
        self.assert_equal(completed_task.status, TaskStatus.COMPLETED.value, "任务状态已更新")
        self.assert_true(completed_task.completed_at is not None, "任务完成时间已记录")

        # 测试3: 查询任务
        self.crm.create_task("call", "电话回访", customer_id=customer.customer_id)
        tasks = self.crm.list_tasks(status=TaskStatus.PENDING.value)
        self.assert_true(len(tasks) >= 1, "查询任务数量正确")

    def test_sales_funnel(self):
        """测试销售漏斗分析"""
        print("\n📋 测试销售漏斗分析...")

        # 创建新客户
        customer = self.crm.add_customer(name="漏斗测试公司")

        # 创建各阶段的商机
        self.crm.create_opportunity(customer.customer_id, "初始商机", 100000, stage=OpportunityStage.INITIAL.value)
        self.crm.create_opportunity(customer.customer_id, "需求确认商机", 80000, stage=OpportunityStage.DISCOVERY.value)
        self.crm.create_opportunity(customer.customer_id, "方案提交商机", 120000, stage=OpportunityStage.PROPOSAL.value)
        self.crm.create_opportunity(customer.customer_id, "谈判商机", 150000, stage=OpportunityStage.NEGOTIATION.value)

        # 重新加载数据
        self.crm.opportunity_mgr.load()

        # 分析销售漏斗
        funnel = self.crm.sales_funnel()

        print(f"DEBUG - 漏斗数据: {funnel}")
        self.assert_true('初步接触' in funnel, "漏斗包含初始阶段")
        self.assert_true('需求确认' in funnel, "漏斗包含需求确认阶段")
        self.assert_true('方案提交' in funnel, "漏斗包含方案提交阶段")
        self.assert_true('商务谈判' in funnel, "漏斗包含谈判阶段")
        self.assert_true(funnel['初步接触']['count'] >= 1, "初始阶段有商机")
        self.assert_true(funnel['需求确认']['count'] >= 1, "需求确认阶段有商机")
        self.assert_equal(funnel['初步接触']['probability'], 10, "初始阶段概率正确")
        self.assert_equal(funnel['需求确认']['probability'], 30, "需求确认概率正确")

    def test_customer_value(self):
        """测试客户价值分析"""
        print("\n📋 测试客户价值分析...")

        # 创建客户和成交商机
        customer1 = self.crm.add_customer(name="高价值客户")
        self.crm.create_opportunity(customer1.customer_id, "大单A", 200000, stage=OpportunityStage.NEGOTIATION.value)
        opp1 = self.crm.create_opportunity(customer1.customer_id, "大单B", 150000, stage=OpportunityStage.INITIAL.value)
        self.crm.close_opportunity(opp1.opportunity_id, status="won", actual_amount=150000)

        customer2 = self.crm.add_customer(name="普通客户")
        opp2 = self.crm.create_opportunity(customer2.customer_id, "小单", 30000, stage=OpportunityStage.PROPOSAL.value)
        self.crm.close_opportunity(opp2.opportunity_id, status="won", actual_amount=28000)

        # 重新加载manager以确保最新数据
        self.crm.opportunity_mgr.load()
        self.crm.customer_mgr.load()

        # 分析客户价值
        value = self.crm.customer_value()

        print(f"DEBUG - 客户价值数据: {value}")
        self.assert_true(value['total_customers'] >= 2, "客户总数正确")
        self.assert_true(value['active_customers'] >= 2, "活跃客户数正确")
        self.assert_true(len(value['revenue_by_customer']) >= 2, "客户收入列表正确")

        # 验证客户收入排序（高价值客户应该在前）
        if len(value['revenue_by_customer']) >= 2:
            self.assert_true(value['revenue_by_customer'][0]['revenue'] >=
                           value['revenue_by_customer'][1]['revenue'],
                           "客户收入按降序排列")

    def test_rfm_analysis(self):
        """测试RFM分析"""
        print("\n📋 测试RFM分析...")

        # 创建客户、线索和成交
        customer = self.crm.add_customer(name="RFM测试客户")

        # 创建线索
        self.crm.add_lead("线索A", "潜在客户A")
        self.crm.add_lead("线索B", "潜在客户B")

        # 创建并成交多个商机
        opp1 = self.crm.create_opportunity(customer.customer_id, "订单1", 120000, stage=OpportunityStage.PROPOSAL.value)
        self.crm.close_opportunity(opp1.opportunity_id, status="won", actual_amount=115000)

        opp2 = self.crm.create_opportunity(customer.customer_id, "订单2", 80000, stage=OpportunityStage.INITIAL.value)
        self.crm.close_opportunity(opp2.opportunity_id, status="won", actual_amount=75000)

        # 重新加载manager以确保最新数据
        self.crm.opportunity_mgr.load()
        self.crm.lead_mgr.load()

        # RFM分析
        rfm = self.crm.rfm_analysis()

        print(f"DEBUG - RFM数据: {rfm}")
        self.assert_true(rfm['customer_count'] >= 1, "客户数量正确")
        self.assert_true(rfm['lead_count'] >= 2, "线索数量正确")
        self.assert_true(len(rfm['top_customers']) >= 1, "Top客户列表正确")

        # 验证RFM分数
        if rfm['top_customers']:
            top_customer = rfm['top_customers'][0]
            self.assert_true('recency_score' in top_customer[1], "有R分数")
            self.assert_true('frequency_score' in top_customer[1], "有F分数")
            self.assert_true('monetary_score' in top_customer[1], "有M分数")
            self.assert_true('total_score' in top_customer[1], "有总分")

    def test_sales_performance(self):
        """测试销售业绩分析"""
        print("\n📋 测试销售业绩分析...")

        customer = self.crm.add_customer(name="业绩测试公司")

        # 为销售人员创建商机和任务
        opp1 = self.crm.create_opportunity(
            customer.customer_id, "商机A", 100000,
            stage=OpportunityStage.INITIAL.value,
            assignee="sales_001"
        )
        opp2 = self.crm.create_opportunity(
            customer.customer_id, "商机B", 150000,
            stage=OpportunityStage.INITIAL.value,
            assignee="sales_002"
        )

        # 成交部分商机
        self.crm.close_opportunity(opp1.opportunity_id, status="won", actual_amount=95000)

        # 创建任务
        task1 = self.crm.create_task("call", "电话回访", assignee="sales_001")
        task2 = self.crm.create_task("email", "发送邮件", assignee="sales_001")
        self.crm.complete_task(task1.task_id)

        # 重新加载manager以确保最新数据
        self.crm.opportunity_mgr.load()
        self.crm.task_mgr.load()

        # 销售业绩分析
        performance = self.crm.sales_performance()

        self.assert_true('sales_reps' in performance, "有销售人员列表")
        self.assert_true('performance' in performance, "有业绩数据")
        self.assert_true('sales_001' in performance['performance'], "有sales_001业绩")

        sales_001_perf = performance['performance']['sales_001']
        self.assert_true(sales_001_perf['opportunities'] >= 1, "商机数正确")
        self.assert_true(sales_001_perf['won_amount'] >= 95000, "成交金额正确")
        self.assert_true(sales_001_perf['won_count'] >= 1, "成交数正确")
        self.assert_true(sales_001_perf['tasks_completed'] >= 1, "完成任务数正确")

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始CRM系统测试...")
        print("=" * 60)

        try:
            self.setup()

            # 运行所有测试
            self.test_customer_management()
            self.test_contact_management()
            self.test_lead_management()
            self.test_lead_conversion()
            self.test_opportunity_management()
            self.test_opportunity_close()
            self.test_task_management()
            self.test_sales_funnel()
            self.test_customer_value()
            self.test_rfm_analysis()
            self.test_sales_performance()

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
    tester = TestCRM()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
