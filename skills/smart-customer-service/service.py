#!/usr/bin/env python3
"""
智能客服系统
支持多渠道接入、AI问答、工单管理
"""

import json
import yaml
import logging
import sqlite3
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ChannelType(Enum):
    """渠道类型"""
    WECHAT = "wechat"
    WEB = "web"
    APP = "app"
    PHONE = "phone"
    EMAIL = "email"


class TicketStatus(Enum):
    """工单状态"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class TicketPriority(Enum):
    """工单优先级"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Channel:
    """渠道"""
    channel_id: str
    type: ChannelType
    enabled: bool
    config: Dict


@dataclass
class Customer:
    """客户"""
    customer_id: str
    name: str
    email: str
    phone: str
    tags: List[str]
    total_orders: int
    total_spent: float
    last_purchase: str
    tickets_count: int
    satisfaction_score: float


@dataclass
class Ticket:
    """工单"""
    ticket_id: str
    customer_id: str
    channel_id: str
    type: str
    priority: TicketPriority
    title: str
    description: str
    status: TicketStatus
    assigned_agent_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]
    resolution: Optional[str]
    satisfaction_score: Optional[float]


@dataclass
class Agent:
    """客服"""
    agent_id: str
    name: str
    email: str
    status: str  # online/offline/busy/away
    active_chats: int
    max_concurrent_chats: int
    tickets_handled: int
    satisfaction_score: float


@dataclass
class FAQ:
    """FAQ"""
    faq_id: str
    question: str
    answer: str
    category: str
    tags: List[str]


class CustomerService:
    """智能客服系统"""

    def __init__(self, config_file: str = "config/service.yaml"):
        """
        初始化客服系统

        Args:
            config_file: 配置文件路径
        """
        self.config = self._load_config(config_file)
        self.channels: List[Channel] = []
        self.customers: Dict[str, Customer] = {}
        self.tickets: List[Ticket] = []
        self.agents: List[Agent] = []
        self.faq: List[FAQ] = []
        self.is_running = False
        self.worker_thread = None
        self.db_conn = self._init_db()

    def _load_config(self, config_file: str) -> Dict:
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return {}

    def _init_db(self) -> sqlite3.Connection:
        """初始化数据库"""
        import os
        os.makedirs("data", exist_ok=True)

        conn = sqlite3.connect("data/service.db", check_same_thread=False)
        cursor = conn.cursor()

        # 创建客户表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id TEXT PRIMARY KEY,
                name TEXT,
                email TEXT,
                phone TEXT,
                tags TEXT,
                total_orders INTEGER,
                total_spent REAL,
                last_purchase TEXT,
                tickets_count INTEGER,
                satisfaction_score REAL
            )
        """)

        # 创建工单表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id TEXT PRIMARY KEY,
                customer_id TEXT,
                channel_id TEXT,
                type TEXT,
                priority TEXT,
                title TEXT,
                description TEXT,
                status TEXT,
                assigned_agent_id TEXT,
                created_at TEXT,
                updated_at TEXT,
                resolved_at TEXT,
                resolution TEXT,
                satisfaction_score REAL
            )
        """)

        # 创建客服表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                agent_id TEXT PRIMARY KEY,
                name TEXT,
                email TEXT,
                status TEXT,
                active_chats INTEGER,
                max_concurrent_chats INTEGER,
                tickets_handled INTEGER,
                satisfaction_score REAL
            )
        """)

        # 创建FAQ表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS faq (
                faq_id TEXT PRIMARY KEY,
                question TEXT,
                answer TEXT,
                category TEXT,
                tags TEXT
            )
        """)

        conn.commit()
        return conn

    def add_channel(
        self,
        type: str,
        config: Dict
    ) -> Channel:
        """
        添加渠道

        Args:
            type: 渠道类型
            config: 渠道配置

        Returns:
            渠道
        """
        import uuid

        channel_id = f"channel_{uuid.uuid4().hex[:8]}"

        channel = Channel(
            channel_id=channel_id,
            type=ChannelType(type),
            enabled=True,
            config=config
        )

        self.channels.append(channel)
        logger.info(f"添加渠道: {type} ({channel_id})")
        return channel

    def add_customer(
        self,
        customer_id: str,
        name: str,
        email: str,
        phone: str
    ) -> Customer:
        """
        添加客户

        Args:
            customer_id: 客户ID
            name: 姓名
            email: 邮箱
            phone: 电话

        Returns:
            客户
        """
        customer = Customer(
            customer_id=customer_id,
            name=name,
            email=email,
            phone=phone,
            tags=[],
            total_orders=0,
            total_spent=0.0,
            last_purchase="",
            tickets_count=0,
            satisfaction_score=0.0
        )

        self.customers[customer_id] = customer
        self._save_customer(customer)
        return customer

    def _save_customer(self, customer: Customer):
        """保存客户到数据库"""
        cursor = self.db_conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO customers
            (customer_id, name, email, phone, tags, total_orders, total_spent, last_purchase, tickets_count, satisfaction_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            customer.customer_id,
            customer.name,
            customer.email,
            customer.phone,
            json.dumps(customer.tags),
            customer.total_orders,
            customer.total_spent,
            customer.last_purchase,
            customer.tickets_count,
            customer.satisfaction_score
        ))

        self.db_conn.commit()

    def create_ticket(
        self,
        customer_id: str,
        type: str,
        priority: str,
        title: str,
        description: str,
        channel_id: Optional[str] = None
    ) -> Ticket:
        """
        创建工单

        Args:
            customer_id: 客户ID
            type: 工单类型
            priority: 优先级
            title: 标题
            description: 描述
            channel_id: 渠道ID

        Returns:
            工单
        """
        import uuid

        ticket_id = f"ticket_{uuid.uuid4().hex[:8]}"
        now = datetime.now()

        # 自动分配客服
        assigned_agent_id = self._auto_assign_agent(priority)

        ticket = Ticket(
            ticket_id=ticket_id,
            customer_id=customer_id,
            channel_id=channel_id or "default",
            type=type,
            priority=TicketPriority(priority),
            title=title,
            description=description,
            status=TicketStatus.OPEN,
            assigned_agent_id=assigned_agent_id,
            created_at=now,
            updated_at=now,
            resolved_at=None,
            resolution=None,
            satisfaction_score=None
        )

        self.tickets.append(ticket)

        # 更新客户工单数
        if customer_id in self.customers:
            self.customers[customer_id].tickets_count += 1
            self._save_customer(self.customers[customer_id])

        # 保存到数据库
        self._save_ticket(ticket)

        logger.info(f"创建工单: {title} ({ticket_id}), 分配给: {assigned_agent_id}")
        return ticket

    def _auto_assign_agent(self, priority: str) -> Optional[str]:
        """
        自动分配客服

        Args:
            priority: 优先级

        Returns:
            客服ID
        """
        # 找到在线且不忙的客服
        available_agents = [
            agent for agent in self.agents
            if agent.status == "online"
            and agent.active_chats < agent.max_concurrent_chats
        ]

        if not available_agents:
            return None

        # 按活跃会话数排序
        available_agents.sort(key=lambda a: a.active_chats)

        return available_agents[0].agent_id

    def _save_ticket(self, ticket: Ticket):
        """保存工单到数据库"""
        cursor = self.db_conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO tickets
            (ticket_id, customer_id, channel_id, type, priority, title, description, status, assigned_agent_id, created_at, updated_at, resolved_at, resolution, satisfaction_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ticket.ticket_id,
            ticket.customer_id,
            ticket.channel_id,
            ticket.type,
            ticket.priority.value,
            ticket.title,
            ticket.description,
            ticket.status.value,
            ticket.assigned_agent_id,
            ticket.created_at.isoformat(),
            ticket.updated_at.isoformat(),
            ticket.resolved_at.isoformat() if ticket.resolved_at else None,
            ticket.resolution,
            ticket.satisfaction_score
        ))

        self.db_conn.commit()

    def assign_ticket(self, ticket_id: str, agent_id: str) -> bool:
        """
        分配工单

        Args:
            ticket_id: 工单ID
            agent_id: 客服ID

        Returns:
            是否成功
        """
        ticket = self._get_ticket(ticket_id)
        if not ticket:
            logger.error(f"未找到工单: {ticket_id}")
            return False

        agent = self._get_agent(agent_id)
        if not agent:
            logger.error(f"未找到客服: {agent_id}")
            return False

        ticket.assigned_agent_id = agent_id
        ticket.status = TicketStatus.IN_PROGRESS
        ticket.updated_at = datetime.now()

        # 更新客服活跃会话数
        agent.active_chats += 1

        self._save_ticket(ticket)
        self._save_agent(agent)

        logger.info(f"分配工单 {ticket_id} 给 {agent.name}")
        return True

    def update_ticket(
        self,
        ticket_id: str,
        status: Optional[str] = None,
        comment: Optional[str] = None
    ) -> bool:
        """
        更新工单

        Args:
            ticket_id: 工单ID
            status: 状态
            comment: 评论

        Returns:
            是否成功
        """
        ticket = self._get_ticket(ticket_id)
        if not ticket:
            logger.error(f"未找到工单: {ticket_id}")
            return False

        if status:
            ticket.status = TicketStatus(status)

        ticket.updated_at = datetime.now()

        if ticket.status == TicketStatus.RESOLVED:
            ticket.resolved_at = datetime.now()

            # 减少客服活跃会话数
            if ticket.assigned_agent_id:
                agent = self._get_agent(ticket.assigned_agent_id)
                if agent:
                    agent.active_chats = max(0, agent.active_chats - 1)
                    agent.tickets_handled += 1
                    self._save_agent(agent)

        self._save_ticket(ticket)
        logger.info(f"更新工单 {ticket_id}: status={status}, comment={comment}")
        return True

    def close_ticket(self, ticket_id: str, resolution: str) -> bool:
        """
        关闭工单

        Args:
            ticket_id: 工单ID
            resolution: 解决方案

        Returns:
            是否成功
        """
        ticket = self._get_ticket(ticket_id)
        if not ticket:
            logger.error(f"未找到工单: {ticket_id}")
            return False

        ticket.status = TicketStatus.CLOSED
        ticket.resolution = resolution
        ticket.resolved_at = datetime.now()
        ticket.updated_at = datetime.now()

        # 减少客服活跃会话数
        if ticket.assigned_agent_id:
            agent = self._get_agent(ticket.assigned_agent_id)
            if agent:
                agent.active_chats = max(0, agent.active_chats - 1)
                agent.tickets_handled += 1
                self._save_agent(agent)

        self._save_ticket(ticket)
        logger.info(f"关闭工单 {ticket_id}: {resolution}")
        return True

    def add_agent(
        self,
        name: str,
        email: str,
        max_concurrent_chats: int = 5
    ) -> Agent:
        """
        添加客服

        Args:
            name: 姓名
            email: 邮箱
            max_concurrent_chats: 最大并发会话数

        Returns:
            客服
        """
        import uuid

        agent_id = f"agent_{uuid.uuid4().hex[:8]}"

        agent = Agent(
            agent_id=agent_id,
            name=name,
            email=email,
            status="offline",
            active_chats=0,
            max_concurrent_chats=max_concurrent_chats,
            tickets_handled=0,
            satisfaction_score=0.0
        )

        self.agents.append(agent)
        self._save_agent(agent)
        logger.info(f"添加客服: {name} ({agent_id})")
        return agent

    def _save_agent(self, agent: Agent):
        """保存客服到数据库"""
        cursor = self.db_conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO agents
            (agent_id, name, email, status, active_chats, max_concurrent_chats, tickets_handled, satisfaction_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            agent.agent_id,
            agent.name,
            agent.email,
            agent.status,
            agent.active_chats,
            agent.max_concurrent_chats,
            agent.tickets_handled,
            agent.satisfaction_score
        ))

        self.db_conn.commit()

    def add_faq(
        self,
        question: str,
        answer: str,
        category: str,
        tags: List[str]
    ) -> FAQ:
        """
        添加FAQ

        Args:
            question: 问题
            answer: 答案
            category: 分类
            tags: 标签

        Returns:
            FAQ
        """
        import uuid

        faq_id = f"faq_{uuid.uuid4().hex[:8]}"

        faq = FAQ(
            faq_id=faq_id,
            question=question,
            answer=answer,
            category=category,
            tags=tags
        )

        self.faq.append(faq)
        self._save_faq(faq)
        logger.info(f"添加FAQ: {question} ({faq_id})")
        return faq

    def _save_faq(self, faq: FAQ):
        """保存FAQ到数据库"""
        cursor = self.db_conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO faq
            (faq_id, question, answer, category, tags)
            VALUES (?, ?, ?, ?, ?)
        """, (
            faq.faq_id,
            faq.question,
            faq.answer,
            faq.category,
            json.dumps(faq.tags)
        ))

        self.db_conn.commit()

    def search_kb(self, query: str, limit: int = 5) -> List[Dict]:
        """
        搜索知识库

        Args:
            query: 查询
            limit: 结果数量限制

        Returns:
            FAQ列表
        """
        # 简化的关键词匹配
        results = []

        query_lower = query.lower()
        for faq in self.faq:
            score = 0

            # 问题匹配
            if query_lower in faq.question.lower():
                score += 2

            # 标签匹配
            for tag in faq.tags:
                if query_lower in tag.lower():
                    score += 1

            # 分类匹配
            if query_lower in faq.category.lower():
                score += 1

            if score > 0:
                results.append({
                    "faq_id": faq.faq_id,
                    "question": faq.question,
                    "answer": faq.answer,
                    "category": faq.category,
                    "score": score
                })

        # 按分数排序
        results.sort(key=lambda x: x["score"], reverse=True)

        return results[:limit]

    def ai_answer(self, message: str, customer_id: str) -> str:
        """
        AI自动回答

        Args:
            message: 用户消息
            customer_id: 客户ID

        Returns:
            回答
        """
        # 先搜索知识库
        kb_results = self.search_kb(message, limit=3)

        if kb_results:
            # 找到匹配的FAQ
            best_match = kb_results[0]
            if best_match["score"] >= 2:
                return best_match["answer"]

        # 没有找到，使用简单的规则
        if "退款" in message:
            return "您可以登录账户，进入订单中心，选择需要退款的订单，点击申请退款。"
        elif "发货" in message or "物流" in message:
            return "通常情况下，我们会在24小时内发货，快递需要3-5天送达。"
        elif "价格" in message:
            return "我们的价格都是官网明码标价，您可以放心购买。如有疑问，请联系客服。"
        else:
            return "感谢您的咨询，已为您转接人工客服，请稍等。"

    def get_ticket(self, ticket_id: str) -> Optional[Dict]:
        """
        获取工单

        Args:
            ticket_id: 工单ID

        Returns:
            工单信息
        """
        ticket = self._get_ticket(ticket_id)
        if not ticket:
            return None

        return asdict(ticket)

    def _get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """获取工单"""
        for ticket in self.tickets:
            if ticket.ticket_id == ticket_id:
                return ticket
        return None

    def _get_agent(self, agent_id: str) -> Optional[Agent]:
        """获取客服"""
        for agent in self.agents:
            if agent.agent_id == agent_id:
                return agent
        return None

    def list_tickets(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None
    ) -> List[Dict]:
        """
        列出工单

        Args:
            status: 状态
            priority: 优先级

        Returns:
            工单列表
        """
        tickets = self.tickets

        if status:
            tickets = [t for t in tickets if t.status.value == status]

        if priority:
            tickets = [t for t in tickets if t.priority.value == priority]

        return [asdict(ticket) for ticket in tickets]

    def get_stats(self) -> Dict:
        """
        获取统计信息

        Returns:
            统计信息
        """
        total_tickets = len(self.tickets)
        open_tickets = len([t for t in self.tickets if t.status == TicketStatus.OPEN])
        in_progress_tickets = len([t for t in self.tickets if t.status == TicketStatus.IN_PROGRESS])
        resolved_tickets = len([t for t in self.tickets if t.status == TicketStatus.RESOLVED])
        closed_tickets = len([t for t in self.tickets if t.status == TicketStatus.CLOSED])

        total_agents = len(self.agents)
        online_agents = len([a for a in self.agents if a.status == "online"])

        return {
            "tickets": {
                "total": total_tickets,
                "open": open_tickets,
                "in_progress": in_progress_tickets,
                "resolved": resolved_tickets,
                "closed": closed_tickets
            },
            "agents": {
                "total": total_agents,
                "online": online_agents
            },
            "customers": len(self.customers),
            "faq": len(self.faq)
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="智能客服系统")
    parser.add_argument("command", choices=["add_channel", "add_customer", "create_ticket", "assign_ticket", "update_ticket", "close_ticket", "add_agent", "add_faq", "search_kb", "list_tickets", "stats"],
                        help="命令")
    parser.add_argument("--type", help="类型")
    parser.add_argument("--config", help="配置JSON")
    parser.add_argument("--customer_id", help="客户ID")
    parser.add_argument("--name", help="姓名")
    parser.add_argument("--email", help="邮箱")
    parser.add_argument("--phone", help="电话")
    parser.add_argument("--ticket_id", help="工单ID")
    parser.add_argument("--agent_id", help="客服ID")
    parser.add_argument("--priority", help="优先级")
    parser.add_argument("--title", help="标题")
    parser.add_argument("--description", help="描述")
    parser.add_argument("--status", help="状态")
    parser.add_argument("--comment", help="评论")
    parser.add_argument("--resolution", help="解决方案")
    parser.add_argument("--question", help="问题")
    parser.add_argument("--answer", help="答案")
    parser.add_argument("--category", help="分类")
    parser.add_argument("--tags", nargs="+", help="标签")
    parser.add_argument("--query", help="查询")

    args = parser.parse_args()

    # 创建客服系统
    service = CustomerService()

    if args.command == "add_channel":
        config = json.loads(args.config) if args.config else {}
        channel = service.add_channel(
            type=args.type,
            config=config
        )
        print(f"渠道创建成功: {channel.channel_id}")

    elif args.command == "add_customer":
        customer = service.add_customer(
            customer_id=args.customer_id,
            name=args.name,
            email=args.email,
            phone=args.phone
        )
        print(f"客户创建成功: {customer.customer_id}")

    elif args.command == "create_ticket":
        ticket = service.create_ticket(
            customer_id=args.customer_id,
            type=args.type,
            priority=args.priority,
            title=args.title,
            description=args.description
        )
        print(f"工单创建成功: {ticket.ticket_id}")

    elif args.command == "assign_ticket":
        success = service.assign_ticket(
            ticket_id=args.ticket_id,
            agent_id=args.agent_id
        )
        if success:
            print("工单分配成功")
        else:
            print("工单分配失败")

    elif args.command == "update_ticket":
        success = service.update_ticket(
            ticket_id=args.ticket_id,
            status=args.status,
            comment=args.comment
        )
        if success:
            print("工单更新成功")
        else:
            print("工单更新失败")

    elif args.command == "close_ticket":
        success = service.close_ticket(
            ticket_id=args.ticket_id,
            resolution=args.resolution
        )
        if success:
            print("工单关闭成功")
        else:
            print("工单关闭失败")

    elif args.command == "add_agent":
        agent = service.add_agent(
            name=args.name,
            email=args.email
        )
        print(f"客服创建成功: {agent.agent_id}")

    elif args.command == "add_faq":
        faq = service.add_faq(
            question=args.question,
            answer=args.answer,
            category=args.category,
            tags=args.tags or []
        )
        print(f"FAQ创建成功: {faq.faq_id}")

    elif args.command == "search_kb":
        results = service.search_kb(query=args.query)
        print(f"找到 {len(results)} 条FAQ:")
        for result in results:
            print(f"  [{result['score']}] {result['question']}")
            print(f"    {result['answer']}")
            print()

    elif args.command == "list_tickets":
        tickets = service.list_tickets(status=args.status, priority=args.priority)
        print(f"共有 {len(tickets)} 个工单:")
        for ticket in tickets:
            print(f"  - {ticket['ticket_id']}: {ticket['title']} ({ticket['status']}, {ticket['priority']})")

    elif args.command == "stats":
        stats = service.get_stats()
        print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
