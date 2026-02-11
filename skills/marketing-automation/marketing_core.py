#!/usr/bin/env python3
"""
自动化营销系统 - 核心营销引擎
Marketing Automation System - Core Marketing Engine
"""

import json
import uuid
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import random


@dataclass
class Customer:
    """客户数据模型"""
    id: str
    email: str
    phone: Optional[str] = None
    name: str = ""
    tags: List[str] = None
    created_at: str = None
    last_active: str = None
    total_spent: float = 0.0
    order_count: int = 0
    custom_fields: Dict = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.custom_fields is None:
            self.custom_fields = {}
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.last_active is None:
            self.last_active = datetime.now().isoformat()


@dataclass
class Campaign:
    """营销活动数据模型"""
    id: str
    name: str
    channel: str  # email, sms, wechat, app, social
    audience: str  # 目标人群
    template: str
    content: Dict
    status: str = "draft"  # draft, scheduled, running, completed
    scheduled_at: Optional[str] = None
    sent_at: Optional[str] = None
    created_at: str = None
    metrics: Dict = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.metrics is None:
            self.metrics = {
                "sent": 0,
                "delivered": 0,
                "opened": 0,
                "clicked": 0,
                "converted": 0,
                "bounced": 0
            }


@dataclass
class MessageLog:
    """消息发送日志"""
    id: str
    campaign_id: str
    customer_id: str
    channel: str
    status: str  # sent, delivered, opened, clicked, bounced, failed
    sent_at: str
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class MarketingAutomation:
    """营销自动化核心引擎"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.customers = {}
        self.campaigns = {}
        self.message_logs = []

        self._load_data()

    def _load_data(self):
        """加载数据"""
        # 加载客户
        customers_file = self.data_dir / "customers.json"
        if customers_file.exists():
            with open(customers_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for id_, customer_data in data.items():
                    self.customers[id_] = Customer(**customer_data)

        # 加载营销活动
        campaigns_file = self.data_dir / "campaigns.json"
        if campaigns_file.exists():
            with open(campaigns_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for id_, campaign_data in data.items():
                    self.campaigns[id_] = Campaign(**campaign_data)

        # 加载消息日志
        logs_file = self.data_dir / "message_logs.json"
        if logs_file.exists():
            with open(logs_file, 'r', encoding='utf-8') as f:
                self.message_logs = [MessageLog(**item) for item in json.load(f)]

    def _save_data(self):
        """保存数据"""
        # 保存客户
        customers_file = self.data_dir / "customers.json"
        customers_data = {id_: asdict(customer) for id_, customer in self.customers.items()}
        with open(customers_file, 'w', encoding='utf-8') as f:
            json.dump(customers_data, f, indent=2, ensure_ascii=False)

        # 保存营销活动
        campaigns_file = self.data_dir / "campaigns.json"
        campaigns_data = {id_: asdict(campaign) for id_, campaign in self.campaigns.items()}
        with open(campaigns_file, 'w', encoding='utf-8') as f:
            json.dump(campaigns_data, f, indent=2, ensure_ascii=False)

        # 保存消息日志
        logs_file = self.data_dir / "message_logs.json"
        logs_data = [asdict(log) for log in self.message_logs]
        with open(logs_file, 'w', encoding='utf-8') as f:
            json.dump(logs_data, f, indent=2, ensure_ascii=False)

    # ========== 客户管理 ==========

    def add_customer(self, email: str, phone: str = None, name: str = "", **kwargs) -> Customer:
        """添加客户"""
        customer_id = str(uuid.uuid4())
        customer = Customer(
            id=customer_id,
            email=email,
            phone=phone,
            name=name,
            custom_fields=kwargs
        )
        self.customers[customer_id] = customer
        self._save_data()
        return customer

    def get_customer(self, customer_id: str) -> Optional[Customer]:
        """获取客户"""
        return self.customers.get(customer_id)

    def list_customers(self, tag: str = None, limit: int = None) -> List[Customer]:
        """列出客户"""
        customers = list(self.customers.values())

        if tag:
            customers = [c for c in customers if tag in c.tags]

        if limit:
            customers = customers[:limit]

        return customers

    def update_customer(self, customer_id: str, **kwargs) -> Optional[Customer]:
        """更新客户"""
        customer = self.customers.get(customer_id)
        if customer:
            for key, value in kwargs.items():
                if hasattr(customer, key):
                    setattr(customer, key, value)
            self._save_data()
        return customer

    def add_tag(self, customer_id: str, tag: str) -> bool:
        """为客户添加标签"""
        customer = self.customers.get(customer_id)
        if customer and tag not in customer.tags:
            customer.tags.append(tag)
            self._save_data()
            return True
        return False

    def get_audience(self, audience: str) -> List[Customer]:
        """获取目标受众"""
        if audience == "all":
            return list(self.customers.values())
        elif audience == "vip":
            return [c for c in self.customers.values() if c.total_spent >= 1000]
        elif audience == "active":
            last_week = datetime.now() - timedelta(days=7)
            return [c for c in self.customers.values()
                    if datetime.fromisoformat(c.last_active) >= last_week]
        elif audience == "new":
            last_month = datetime.now() - timedelta(days=30)
            return [c for c in self.customers.values()
                    if datetime.fromisoformat(c.created_at) >= last_month]
        else:
            # 按标签分群
            return [c for c in self.customers.values() if audience in c.tags]

    # ========== 营销活动管理 ==========

    def create_campaign(
        self,
        name: str,
        channel: str,
        audience: str,
        template: str = "",
        content: Dict = None,
        scheduled_at: str = None
    ) -> Campaign:
        """创建营销活动"""
        campaign_id = str(uuid.uuid4())
        campaign = Campaign(
            id=campaign_id,
            name=name,
            channel=channel,
            audience=audience,
            template=template,
            content=content or {}
        )

        if scheduled_at:
            campaign.scheduled_at = scheduled_at
            campaign.status = "scheduled"

        self.campaigns[campaign_id] = campaign
        self._save_data()
        return campaign

    def get_campaign(self, campaign_id: str) -> Optional[Campaign]:
        """获取营销活动"""
        return self.campaigns.get(campaign_id)

    def list_campaigns(self, status: str = None) -> List[Campaign]:
        """列出营销活动"""
        campaigns = list(self.campaigns.values())

        if status:
            campaigns = [c for c in campaigns if c.status == status]

        return campaigns

    def schedule_campaign(self, campaign_id: str, scheduled_at: str) -> bool:
        """调度营销活动"""
        campaign = self.campaigns.get(campaign_id)
        if campaign:
            campaign.scheduled_at = scheduled_at
            campaign.status = "scheduled"
            self._save_data()
            return True
        return False

    def send_campaign(self, campaign_id: str, simulate: bool = True) -> Dict:
        """发送营销活动"""
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            return {"success": False, "error": "Campaign not found"}

        # 获取目标受众
        audience = self.get_audience(campaign.audience)

        if not audience:
            return {"success": False, "error": "No audience found"}

        sent_count = 0
        logs = []

        for customer in audience:
            if simulate:
                # 模拟发送
                status = "sent"
                # 模拟各种状态
                rand = random.random()
                if rand < 0.1:
                    status = "bounced"
                elif rand < 0.7:
                    status = "delivered"

                log = MessageLog(
                    id=str(uuid.uuid4()),
                    campaign_id=campaign_id,
                    customer_id=customer.id,
                    channel=campaign.channel,
                    status=status,
                    sent_at=datetime.now().isoformat()
                )
                self.message_logs.append(log)
                logs.append(log)
                sent_count += 1
            else:
                # 实际发送（待实现）
                pass

        # 更新营销活动
        campaign.status = "running"
        campaign.sent_at = datetime.now().isoformat()
        campaign.metrics["sent"] = sent_count
        campaign.metrics["delivered"] = len([l for l in logs if l.status == "delivered"])
        campaign.metrics["bounced"] = len([l for l in logs if l.status == "bounced"])

        self._save_data()

        return {
            "success": True,
            "campaign_id": campaign_id,
            "sent": sent_count,
            "audience_size": len(audience),
            "logs": len(logs)
        }

    def get_campaign_metrics(self, campaign_id: str) -> Dict:
        """获取营销活动指标"""
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            return {}

        logs = [log for log in self.message_logs if log.campaign_id == campaign_id]

        metrics = {
            "sent": campaign.metrics.get("sent", 0),
            "delivered": len([l for l in logs if l.status == "delivered"]),
            "opened": len([l for l in logs if l.status == "opened"]),
            "clicked": len([l for l in logs if l.status == "clicked"]),
            "converted": len([l for l in logs if l.status == "converted"]),
            "bounced": len([l for l in logs if l.status == "bounced"])
        }

        # 计算转化率
        if metrics["delivered"] > 0:
            metrics["open_rate"] = metrics["opened"] / metrics["delivered"] * 100
            metrics["click_rate"] = metrics["clicked"] / metrics["delivered"] * 100
            metrics["conversion_rate"] = metrics["converted"] / metrics["delivered"] * 100
        else:
            metrics["open_rate"] = 0
            metrics["click_rate"] = 0
            metrics["conversion_rate"] = 0

        return metrics

    # ========== 消息追踪 ==========

    def track_open(self, campaign_id: str, customer_id: str) -> bool:
        """追踪打开"""
        for log in self.message_logs:
            if log.campaign_id == campaign_id and log.customer_id == customer_id:
                log.status = "opened"

                # 更新营销活动指标
                campaign = self.campaigns.get(campaign_id)
                if campaign:
                    campaign.metrics["opened"] += 1

                self._save_data()
                return True
        return False

    def track_click(self, campaign_id: str, customer_id: str) -> bool:
        """追踪点击"""
        for log in self.message_logs:
            if log.campaign_id == campaign_id and log.customer_id == customer_id:
                log.status = "clicked"

                # 更新营销活动指标
                campaign = self.campaigns.get(campaign_id)
                if campaign:
                    campaign.metrics["clicked"] += 1

                self._save_data()
                return True
        return False

    def track_conversion(self, campaign_id: str, customer_id: str) -> bool:
        """追踪转化"""
        for log in self.message_logs:
            if log.campaign_id == campaign_id and log.customer_id == customer_id:
                log.status = "converted"

                # 更新营销活动指标
                campaign = self.campaigns.get(campaign_id)
                if campaign:
                    campaign.metrics["converted"] += 1

                self._save_data()
                return True
        return False

    # ========== 统计分析 ==========

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return {
            "total_customers": len(self.customers),
            "total_campaigns": len(self.campaigns),
            "total_messages": len(self.message_logs),
            "campaigns_by_status": {
                status: len([c for c in self.campaigns.values() if c.status == status])
                for status in ["draft", "scheduled", "running", "completed"]
            }
        }


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="自动化营销系统")
    subparsers = parser.add_subparsers(dest="command", help="命令")

    # 添加客户
    add_customer_parser = subparsers.add_parser("add-customer", help="添加客户")
    add_customer_parser.add_argument("--email", required=True, help="邮箱")
    add_customer_parser.add_argument("--phone", help="手机号")
    add_customer_parser.add_argument("--name", help="姓名")
    add_customer_parser.add_argument("--tag", action="append", help="标签")

    # 创建营销活动
    create_campaign_parser = subparsers.add_parser("create-campaign", help="创建营销活动")
    create_campaign_parser.add_argument("--name", required=True, help="活动名称")
    create_campaign_parser.add_argument("--channel", required=True, choices=["email", "sms", "wechat", "app", "social"], help="渠道")
    create_campaign_parser.add_argument("--audience", required=True, help="受众（all/vip/active/new/标签名）")
    create_campaign_parser.add_argument("--template", help="模板")

    # 发送营销活动
    send_parser = subparsers.add_parser("send", help="发送营销活动")
    send_parser.add_argument("--campaign", required=True, help="活动ID或名称")
    send_parser.add_argument("--simulate", action="store_true", default=True, help="模拟发送")

    # 列出营销活动
    list_parser = subparsers.add_parser("list", help="列出营销活动")
    list_parser.add_argument("--status", choices=["draft", "scheduled", "running", "completed"], help="按状态筛选")

    # 查看指标
    metrics_parser = subparsers.add_parser("metrics", help="查看营销指标")
    metrics_parser.add_argument("--campaign", required=True, help="活动ID或名称")

    # 统计信息
    subparsers.add_parser("stats", help="查看统计信息")

    args = parser.parse_args()

    ma = MarketingAutomation()

    if args.command == "add-customer":
        customer = ma.add_customer(
            email=args.email,
            phone=args.phone,
            name=args.name
        )
        for tag in args.tag or []:
            ma.add_tag(customer.id, tag)
        print(f"✅ 客户已添加: {customer.id}")
        print(f"   邮箱: {customer.email}")
        print(f"   标签: {', '.join(customer.tags)}")

    elif args.command == "create-campaign":
        campaign = ma.create_campaign(
            name=args.name,
            channel=args.channel,
            audience=args.audience,
            template=args.template or ""
        )
        print(f"✅ 营销活动已创建: {campaign.id}")
        print(f"   名称: {campaign.name}")
        print(f"   渠道: {campaign.channel}")
        print(f"   受众: {campaign.audience}")

    elif args.command == "send":
        # 查找营销活动
        campaign = None
        for c in ma.campaigns.values():
            if c.id == args.campaign or c.name == args.campaign:
                campaign = c
                break

        if not campaign:
            print(f"❌ 未找到营销活动: {args.campaign}")
            return

        result = ma.send_campaign(campaign.id, simulate=args.simulate)
        if result["success"]:
            print(f"✅ 营销活动已发送: {campaign.name}")
            print(f"   发送数: {result['sent']}")
            print(f"   受众数: {result['audience_size']}")
        else:
            print(f"❌ 发送失败: {result['error']}")

    elif args.command == "list":
        campaigns = ma.list_campaigns(status=args.status)
        print(f"营销活动列表 ({len(campaigns)}):")
        for c in campaigns:
            print(f"  [{c.id[:8]}] {c.name} ({c.channel}, {c.status})")

    elif args.command == "metrics":
        # 查找营销活动
        campaign = None
        for c in ma.campaigns.values():
            if c.id == args.campaign or c.name == args.campaign:
                campaign = c
                break

        if not campaign:
            print(f"❌ 未找到营销活动: {args.campaign}")
            return

        metrics = ma.get_campaign_metrics(campaign.id)
        print(f"营销活动指标: {campaign.name}")
        print(f"  发送: {metrics.get('sent', 0)}")
        print(f"  送达: {metrics.get('delivered', 0)}")
        print(f"  打开: {metrics.get('opened', 0)} ({metrics.get('open_rate', 0):.1f}%)")
        print(f"  点击: {metrics.get('clicked', 0)} ({metrics.get('click_rate', 0):.1f}%)")
        print(f"  转化: {metrics.get('converted', 0)} ({metrics.get('conversion_rate', 0):.1f}%)")
        print(f"  退回: {metrics.get('bounced', 0)}")

    elif args.command == "stats":
        stats = ma.get_statistics()
        print(f"营销系统统计:")
        print(f"  总客户数: {stats['total_customers']}")
        print(f"  总活动数: {stats['total_campaigns']}")
        print(f"  总消息数: {stats['total_messages']}")
        print(f"  活动状态:")
        for status, count in stats['campaigns_by_status'].items():
            print(f"    {status}: {count}")


if __name__ == "__main__":
    main()
