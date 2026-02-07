#!/usr/bin/env python3
"""
智能客服系统测试用例
"""

import unittest
import os
import tempfile
import shutil

from service import (
    CustomerService,
    Channel,
    Customer,
    Ticket,
    Agent,
    FAQ,
    ChannelType,
    TicketStatus,
    TicketPriority
)


class TestCustomerService(unittest.TestCase):
    """测试客服系统"""

    def setUp(self):
        """设置测试环境"""
        self.test_dir = tempfile.mkdtemp()
        self.service = CustomerService(config_file="config/service.yaml")

    def tearDown(self):
        """清理测试环境"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        if os.path.exists("data"):
            shutil.rmtree("data")

    def test_init(self):
        """测试初始化"""
        self.assertIsInstance(self.service.channels, list)
        self.assertIsInstance(self.service.customers, dict)
        self.assertIsInstance(self.service.tickets, list)
        self.assertIsInstance(self.service.agents, list)
        self.assertIsInstance(self.service.faq, list)

    def test_add_channel(self):
        """测试添加渠道"""
        channel = self.service.add_channel(
            type="wechat",
            config={"app_id": "test_app_id"}
        )

        self.assertIsInstance(channel, Channel)
        self.assertEqual(channel.type, ChannelType.WECHAT)
        self.assertTrue(channel.enabled)

    def test_add_customer(self):
        """测试添加客户"""
        customer = self.service.add_customer(
            customer_id="user_123",
            name="张三",
            email="zhangsan@example.com",
            phone="13800138000"
        )

        self.assertIsInstance(customer, Customer)
        self.assertEqual(customer.name, "张三")
        self.assertEqual(customer.email, "zhangsan@example.com")
        self.assertEqual(customer.tickets_count, 0)

    def test_create_ticket(self):
        """测试创建工单"""
        # 先添加客户
        self.service.add_customer(
            customer_id="user_123",
            name="张三",
            email="zhangsan@example.com",
            phone="13800138000"
        )

        # 添加客服并设置为在线
        agent = self.service.add_agent(
            name="客服A",
            email="agent_a@example.com"
        )
        agent.status = "online"

        # 创建工单
        ticket = self.service.create_ticket(
            customer_id="user_123",
            type="退款",
            priority="normal",
            title="订单退款申请",
            description="订单号12345需要退款"
        )

        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.type, "退款")
        self.assertEqual(ticket.title, "订单退款申请")
        self.assertEqual(ticket.status, TicketStatus.OPEN)
        self.assertIsNotNone(ticket.assigned_agent_id)

    def test_assign_ticket(self):
        """测试分配工单"""
        # 添加客服
        agent = self.service.add_agent(
            name="客服A",
            email="agent_a@example.com"
        )

        # 添加客户
        self.service.add_customer(
            customer_id="user_123",
            name="张三",
            email="zhangsan@example.com",
            phone="13800138000"
        )

        # 创建工单
        ticket = self.service.create_ticket(
            customer_id="user_123",
            type="退款",
            priority="normal",
            title="订单退款申请",
            description="订单号12345需要退款"
        )

        # 分配工单
        success = self.service.assign_ticket(
            ticket_id=ticket.ticket_id,
            agent_id=agent.agent_id
        )

        self.assertTrue(success)

        # 检查工单状态
        updated_ticket = self.service._get_ticket(ticket.ticket_id)
        self.assertEqual(updated_ticket.status, TicketStatus.IN_PROGRESS)

        # 检查客服活跃会话数
        updated_agent = self.service._get_agent(agent.agent_id)
        self.assertEqual(updated_agent.active_chats, 1)

    def test_update_ticket(self):
        """测试更新工单"""
        # 添加客服
        agent = self.service.add_agent(
            name="客服A",
            email="agent_a@example.com"
        )

        # 添加客户
        self.service.add_customer(
            customer_id="user_123",
            name="张三",
            email="zhangsan@example.com",
            phone="13800138000"
        )

        # 创建工单
        ticket = self.service.create_ticket(
            customer_id="user_123",
            type="退款",
            priority="normal",
            title="订单退款申请",
            description="订单号12345需要退款"
        )

        # 更新工单
        success = self.service.update_ticket(
            ticket_id=ticket.ticket_id,
            status="in_progress",
            comment="正在处理退款申请"
        )

        self.assertTrue(success)

        # 检查工单状态
        updated_ticket = self.service._get_ticket(ticket.ticket_id)
        self.assertEqual(updated_ticket.status, TicketStatus.IN_PROGRESS)

    def test_close_ticket(self):
        """测试关闭工单"""
        # 添加客服并设置为在线
        agent = self.service.add_agent(
            name="客服A",
            email="agent_a@example.com"
        )
        agent.status = "online"  # 设置为在线，才能被自动分配

        # 添加客户
        self.service.add_customer(
            customer_id="user_123",
            name="张三",
            email="zhangsan@example.com",
            phone="13800138000"
        )

        # 创建工单
        ticket = self.service.create_ticket(
            customer_id="user_123",
            type="退款",
            priority="normal",
            title="订单退款申请",
            description="订单号12345需要退款"
        )

        # 关闭工单
        success = self.service.close_ticket(
            ticket_id=ticket.ticket_id,
            resolution="已成功退款"
        )

        self.assertTrue(success)

        # 检查工单状态
        updated_ticket = self.service._get_ticket(ticket.ticket_id)
        self.assertEqual(updated_ticket.status, TicketStatus.CLOSED)
        self.assertEqual(updated_ticket.resolution, "已成功退款")

        # 检查客服活跃会话数
        updated_agent = self.service._get_agent(agent.agent_id)
        self.assertEqual(updated_agent.active_chats, 0)
        self.assertEqual(updated_agent.tickets_handled, 1)  # 关闭时+1

    def test_add_agent(self):
        """测试添加客服"""
        agent = self.service.add_agent(
            name="客服A",
            email="agent_a@example.com"
        )

        self.assertIsInstance(agent, Agent)
        self.assertEqual(agent.name, "客服A")
        self.assertEqual(agent.email, "agent_a@example.com")
        self.assertEqual(agent.status, "offline")
        self.assertEqual(agent.active_chats, 0)

    def test_add_faq(self):
        """测试添加FAQ"""
        faq = self.service.add_faq(
            question="如何退款？",
            answer="您可以登录账户，进入订单中心，选择需要退款的订单，点击申请退款。",
            category="订单",
            tags=["退款", "订单"]
        )

        self.assertIsInstance(faq, FAQ)
        self.assertEqual(faq.question, "如何退款？")
        self.assertEqual(faq.category, "订单")
        self.assertEqual(len(faq.tags), 2)

    def test_search_kb(self):
        """测试搜索知识库"""
        # 添加FAQ
        self.service.add_faq(
            question="如何退款？",
            answer="您可以登录账户，进入订单中心，选择需要退款的订单，点击申请退款。",
            category="订单",
            tags=["退款", "订单"]
        )

        # 搜索
        results = self.service.search_kb("退款")

        self.assertGreater(len(results), 0)
        self.assertIn("退款", results[0]["question"])

    def test_ai_answer(self):
        """测试AI回答"""
        # 添加FAQ
        self.service.add_faq(
            question="如何退款？",
            answer="您可以登录账户，进入订单中心，选择需要退款的订单，点击申请退款。",
            category="订单",
            tags=["退款", "订单"]
        )

        # AI回答
        answer = self.service.ai_answer("我想退款", customer_id="user_123")

        self.assertIsNotNone(answer)
        self.assertIn("退款", answer)

    def test_list_tickets(self):
        """测试列出工单"""
        # 添加客服
        self.service.add_agent(
            name="客服A",
            email="agent_a@example.com"
        )

        # 添加客户
        self.service.add_customer(
            customer_id="user_123",
            name="张三",
            email="zhangsan@example.com",
            phone="13800138000"
        )

        # 创建工单
        ticket1 = self.service.create_ticket(
            customer_id="user_123",
            type="退款",
            priority="normal",
            title="工单1",
            description="描述1"
        )

        ticket2 = self.service.create_ticket(
            customer_id="user_123",
            type="发货",
            priority="high",
            title="工单2",
            description="描述2"
        )

        # 列出所有工单
        tickets = self.service.list_tickets()
        self.assertEqual(len(tickets), 2)

        # 列出高优先级工单
        high_priority_tickets = self.service.list_tickets(priority="high")
        self.assertEqual(len(high_priority_tickets), 1)

    def test_get_stats(self):
        """测试获取统计信息"""
        # 添加客服
        self.service.add_agent(
            name="客服A",
            email="agent_a@example.com"
        )

        # 添加客户
        self.service.add_customer(
            customer_id="user_123",
            name="张三",
            email="zhangsan@example.com",
            phone="13800138000"
        )

        # 创建工单
        self.service.create_ticket(
            customer_id="user_123",
            type="退款",
            priority="normal",
            title="工单1",
            description="描述1"
        )

        # 添加FAQ
        self.service.add_faq(
            question="如何退款？",
            answer="您可以登录账户，进入订单中心，选择需要退款的订单，点击申请退款。",
            category="订单",
            tags=["退款", "订单"]
        )

        # 获取统计
        stats = self.service.get_stats()

        self.assertIn("tickets", stats)
        self.assertIn("agents", stats)
        self.assertIn("customers", stats)
        self.assertIn("faq", stats)
        self.assertEqual(stats["tickets"]["total"], 1)
        self.assertEqual(stats["agents"]["total"], 1)
        self.assertEqual(stats["customers"], 1)
        self.assertEqual(stats["faq"], 1)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestCustomerService))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 返回测试结果
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
