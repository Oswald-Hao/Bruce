#!/usr/bin/env python3
"""
CRM系统 - 客户关系管理系统
功能：客户管理、联系人管理、线索管理、商机管理、任务管理、数据分析
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
import uuid
import re


# 数据目录
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
CONFIG_DIR = os.path.join(os.path.dirname(__file__), 'config')
BACKUP_DIR = os.path.join(os.path.dirname(__file__), 'backups')

# 创建必要的目录
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)


class CustomerStatus(Enum):
    """客户状态"""
    POTENTIAL = "potential"  # 潜在客户
    NEW = "new"  # 新客户
    ACTIVE = "active"  # 活跃客户
    INACTIVE = "inactive"  # 非活跃客户
    CHURNED = "churned"  # 流失客户


class LeadStatus(Enum):
    """线索状态"""
    NEW = "new"  # 新线索
    CONTACTED = "contacted"  # 已联系
    QUALIFIED = "qualified"  # 已确认
    CONVERTED = "converted"  # 已转化
    LOST = "lost"  # 已流失


class OpportunityStage(Enum):
    """商机阶段"""
    INITIAL = "初步接触"
    DISCOVERY = "需求确认"
    PROPOSAL = "方案提交"
    NEGOTIATION = "商务谈判"
    WON = "成交"
    LOST = "流失"


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"  # 待处理
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消


class InteractionType(Enum):
    """沟通类型"""
    PHONE = "phone"
    EMAIL = "email"
    MEETING = "meeting"
    VISIT = "visit"


@dataclass
class Customer:
    """客户"""
    customer_id: str
    name: str
    industry: Optional[str] = None
    scale: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = CustomerStatus.ACTIVE.value
    rfm_score: Dict[str, int] = field(default_factory=dict)


@dataclass
class Contact:
    """联系人"""
    contact_id: str
    customer_id: str
    name: str
    position: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    wechat: Optional[str] = None
    role: Optional[str] = None  # 决策人、影响人、使用人
    interactions: List[Dict] = field(default_factory=list)


@dataclass
class Interaction:
    """沟通记录"""
    date: str
    type: str
    content: str
    notes: Optional[str] = None


@dataclass
class Lead:
    """销售线索"""
    lead_id: str
    name: str
    company: str
    phone: Optional[str] = None
    email: Optional[str] = None
    position: Optional[str] = None
    source: Optional[str] = None
    interest: Optional[str] = None
    score: int = 50
    status: str = LeadStatus.NEW.value
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    assigned_to: Optional[str] = None


@dataclass
class Opportunity:
    """销售机会（商机）"""
    opportunity_id: str
    customer_id: str
    title: str
    amount: float
    stage: str
    probability: int
    expected_close_date: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    assigned_to: Optional[str] = None
    competitors: List[str] = field(default_factory=list)
    status: str = "open"  # open, won, lost


@dataclass
class Task:
    """任务"""
    task_id: str
    type: str  # followup, call, email, meeting
    customer_id: Optional[str] = None
    contact_id: Optional[str] = None
    opportunity_id: Optional[str] = None
    title: str = ""
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: str = "normal"  # low, normal, high, urgent
    status: str = TaskStatus.PENDING.value
    assignee: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None


class DataManager:
    """数据管理基类"""

    def __init__(self, filename: str):
        self.filepath = os.path.join(DATA_DIR, filename)
        self.data: List[Dict] = []
        self.load()

    def load(self):
        """加载数据"""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except Exception as e:
                print(f"加载数据失败: {e}")
                self.data = []

    def save(self):
        """保存数据"""
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存数据失败: {e}")


class CustomerManager(DataManager):
    """客户管理"""

    def __init__(self):
        super().__init__('customers.json')

    def add_customer(self, name: str, **kwargs) -> Customer:
        """添加客户"""
        customer = Customer(
            customer_id=f"cust_{uuid.uuid4().hex[:8]}",
            name=name,
            **kwargs
        )
        self.data.append(asdict(customer))
        self.save()
        return customer

    def get_customer(self, customer_id: str) -> Optional[Customer]:
        """获取客户"""
        for cust in self.data:
            if cust['customer_id'] == customer_id:
                return Customer(**cust)
        return None

    def update_customer(self, customer_id: str, **kwargs) -> bool:
        """更新客户"""
        for i, cust in enumerate(self.data):
            if cust['customer_id'] == customer_id:
                self.data[i].update(kwargs)
                self.data[i]['updated_at'] = datetime.now().isoformat()
                self.save()
                return True
        return False

    def delete_customer(self, customer_id: str) -> bool:
        """删除客户"""
        for i, cust in enumerate(self.data):
            if cust['customer_id'] == customer_id:
                del self.data[i]
                self.save()
                return True
        return False

    def search_customers(self, **filters) -> List[Customer]:
        """搜索客户"""
        results = []
        for cust in self.data:
            match = True
            for key, value in filters.items():
                if key not in cust:
                    match = False
                    break
                if isinstance(value, str) and value.lower() not in str(cust[key]).lower():
                    match = False
                    break
            if match:
                results.append(Customer(**cust))
        return results

    def add_tag(self, customer_id: str, tag: str) -> bool:
        """添加标签"""
        for cust in self.data:
            if cust['customer_id'] == customer_id:
                if tag not in cust['tags']:
                    cust['tags'].append(tag)
                    cust['updated_at'] = datetime.now().isoformat()
                    self.save()
                return True
        return False

    def list_all(self) -> List[Customer]:
        """列出所有客户"""
        return [Customer(**cust) for cust in self.data]


class ContactManager(DataManager):
    """联系人管理"""

    def __init__(self):
        super().__init__('contacts.json')

    def add_contact(self, customer_id: str, name: str, **kwargs) -> Contact:
        """添加联系人"""
        contact = Contact(
            contact_id=f"contact_{uuid.uuid4().hex[:8]}",
            customer_id=customer_id,
            name=name,
            **kwargs
        )
        self.data.append(asdict(contact))
        self.save()
        return contact

    def get_contacts(self, customer_id: str) -> List[Contact]:
        """获取客户的所有联系人"""
        return [Contact(**c) for c in self.data if c['customer_id'] == customer_id]

    def add_interaction(self, contact_id: str, interaction_type: str, content: str, **kwargs) -> bool:
        """添加沟通记录"""
        for contact in self.data:
            if contact['contact_id'] == contact_id:
                interaction = Interaction(
                    date=datetime.now().isoformat(),
                    type=interaction_type,
                    content=content,
                    **kwargs
                )
                contact['interactions'].append(asdict(interaction))
                self.save()
                return True
        return False


class LeadManager(DataManager):
    """线索管理"""

    def __init__(self):
        super().__init__('leads.json')

    def add_lead(self, name: str, company: str, **kwargs) -> Lead:
        """添加线索"""
        lead = Lead(
            lead_id=f"lead_{uuid.uuid4().hex[:8]}",
            name=name,
            company=company,
            **kwargs
        )
        # 自动评分
        lead.score = self._score_lead(asdict(lead))
        self.data.append(asdict(lead))
        self.save()
        return lead

    def _score_lead(self, lead: Dict) -> int:
        """线索评分"""
        score = 50  # 基础分

        # 行业加分
        if lead.get('source') == 'referral':
            score += 20
        elif lead.get('source') == 'website':
            score += 10
        elif lead.get('source') == 'exhibition':
            score += 15

        # 职位加分
        position = lead.get('position', '').lower()
        if 'ceo' in position or 'cto' in position or 'vp' in position:
            score += 15
        elif 'manager' in position or 'director' in position:
            score += 10

        # 公司信息加分
        if lead.get('phone') and lead.get('email'):
            score += 10
        if lead.get('interest'):
            score += 5

        return min(score, 100)

    def get_lead(self, lead_id: str) -> Optional[Lead]:
        """获取线索"""
        for lead in self.data:
            if lead['lead_id'] == lead_id:
                return Lead(**lead)
        return None

    def update_lead(self, lead_id: str, **kwargs) -> bool:
        """更新线索"""
        for i, lead in enumerate(self.data):
            if lead['lead_id'] == lead_id:
                self.data[i].update(kwargs)
                self.save()
                return True
        return False

    def list_leads(self, **filters) -> List[Lead]:
        """列出线索"""
        results = []
        for lead in self.data:
            match = True
            for key, value in filters.items():
                if key not in lead or lead[key] != value:
                    match = False
                    break
            if match:
                results.append(Lead(**lead))
        return results


class OpportunityManager(DataManager):
    """商机管理"""

    def __init__(self):
        super().__init__('opportunities.json')

    def create_opportunity(self, customer_id: str, title: str, amount: float, **kwargs) -> Opportunity:
        """创建商机"""
        # 根据阶段设置概率
        stage = kwargs.get('stage', OpportunityStage.INITIAL.value)
        probability = kwargs.get('probability', self._get_stage_probability(stage))

        opportunity = Opportunity(
            opportunity_id=f"opp_{uuid.uuid4().hex[:8]}",
            customer_id=customer_id,
            title=title,
            amount=amount,
            stage=stage,
            probability=probability,
            **kwargs
        )
        self.data.append(asdict(opportunity))
        self.save()
        return opportunity

    def _get_stage_probability(self, stage: str) -> int:
        """获取阶段概率"""
        stage_prob = {
            OpportunityStage.INITIAL.value: 10,
            OpportunityStage.DISCOVERY.value: 30,
            OpportunityStage.PROPOSAL.value: 50,
            OpportunityStage.NEGOTIATION.value: 70,
            OpportunityStage.WON.value: 100,
            OpportunityStage.LOST.value: 0
        }
        return stage_prob.get(stage, 10)

    def update_opportunity(self, opportunity_id: str, **kwargs) -> bool:
        """更新商机"""
        for i, opp in enumerate(self.data):
            if opp['opportunity_id'] == opportunity_id:
                # 如果更新阶段，自动更新概率
                if 'stage' in kwargs:
                    kwargs['probability'] = self._get_stage_probability(kwargs['stage'])
                self.data[i].update(kwargs)
                self.data[i]['updated_at'] = datetime.now().isoformat()
                self.save()
                return True
        return False

    def close_opportunity(self, opportunity_id: str, status: str, **kwargs) -> bool:
        """关闭商机"""
        if status == 'won':
            kwargs['stage'] = OpportunityStage.WON.value
            kwargs['probability'] = 100
        elif status == 'lost':
            kwargs['stage'] = OpportunityStage.LOST.value
            kwargs['probability'] = 0

        kwargs['status'] = status
        return self.update_opportunity(opportunity_id, **kwargs)

    def list_opportunities(self, **filters) -> List[Opportunity]:
        """列出商机"""
        results = []
        for opp in self.data:
            match = True
            for key, value in filters.items():
                if key not in opp or opp[key] != value:
                    match = False
                    break
            if match:
                results.append(Opportunity(**opp))
        return results

    def get_opportunity(self, opportunity_id: str) -> Optional[Opportunity]:
        """获取商机"""
        for opp in self.data:
            if opp['opportunity_id'] == opportunity_id:
                return Opportunity(**opp)
        return None


class TaskManager(DataManager):
    """任务管理"""

    def __init__(self):
        super().__init__('tasks.json')

    def create_task(self, task_type: str, title: str, **kwargs) -> Task:
        """创建任务"""
        task = Task(
            task_id=f"task_{uuid.uuid4().hex[:8]}",
            type=task_type,
            title=title,
            **kwargs
        )
        self.data.append(asdict(task))
        self.save()
        return task

    def complete_task(self, task_id: str) -> bool:
        """完成任务"""
        for i, task in enumerate(self.data):
            if task['task_id'] == task_id:
                self.data[i]['status'] = TaskStatus.COMPLETED.value
                self.data[i]['completed_at'] = datetime.now().isoformat()
                self.save()
                return True
        return False

    def list_tasks(self, **filters) -> List[Task]:
        """列出任务"""
        results = []
        for task in self.data:
            match = True
            for key, value in filters.items():
                if key not in task or task[key] != value:
                    match = False
                    break
            if match:
                results.append(Task(**task))
        return results

    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        for task in self.data:
            if task['task_id'] == task_id:
                return Task(**task)
        return None


class AnalyticsManager:
    """数据分析"""

    def __init__(self):
        self.customer_mgr = CustomerManager()
        self.opportunity_mgr = OpportunityManager()
        self.lead_mgr = LeadManager()
        self.task_mgr = TaskManager()

    def sales_funnel(self) -> Dict:
        """销售漏斗分析"""
        opps = self.opportunity_mgr.list_opportunities(status="open")

        funnel = {}
        for stage in [OpportunityStage.INITIAL.value,
                      OpportunityStage.DISCOVERY.value,
                      OpportunityStage.PROPOSAL.value,
                      OpportunityStage.NEGOTIATION.value]:
            count = sum(1 for opp in opps if opp.stage == stage)
            amount = sum(opp.amount for opp in opps if opp.stage == stage)
            funnel[stage] = {
                'count': count,
                'amount': amount,
                'probability': self.opportunity_mgr._get_stage_probability(stage)
            }

        return funnel

    def customer_value(self) -> Dict:
        """客户价值分析"""
        customers = self.customer_mgr.list_all()
        opps = self.opportunity_mgr.list_opportunities(status="won")

        # 按客户统计成交金额
        customer_revenue = {}
        for opp in opps:
            if opp.customer_id not in customer_revenue:
                customer_revenue[opp.customer_id] = 0
            customer_revenue[opp.customer_id] += opp.amount

        # 排序
        sorted_customers = sorted(customer_revenue.items(),
                                   key=lambda x: x[1],
                                   reverse=True)

        return {
            'total_customers': len(customers),
            'active_customers': len([c for c in customers
                                    if c.status == CustomerStatus.ACTIVE.value]),
            'revenue_by_customer': [
                {
                    'customer_id': cid,
                    'customer_name': self.customer_mgr.get_customer(cid).name,
                    'revenue': revenue
                }
                for cid, revenue in sorted_customers[:10]  # 前10名
            ]
        }

    def rfm_analysis(self) -> Dict:
        """RFM分析"""
        opps = self.opportunity_mgr.list_opportunities(status="won")
        leads = self.lead_mgr.list_leads()

        if not opps:
            return {'message': '暂无成交数据'}

        # 计算RFM分数（简化版）
        # Recency: 最近一次成交
        # Frequency: 成交次数
        # Monetary: 成交金额

        customer_rfm = {}
        for opp in opps:
            cid = opp.customer_id
            if cid not in customer_rfm:
                customer_rfm[cid] = {
                    'recency_date': opp.updated_at,
                    'frequency': 0,
                    'monetary': 0
                }
            customer_rfm[cid]['frequency'] += 1
            customer_rfm[cid]['monetary'] += opp.amount
            # 更新最近成交时间
            if opp.updated_at > customer_rfm[cid]['recency_date']:
                customer_rfm[cid]['recency_date'] = opp.updated_at

        # 计算分数（1-5分）
        now = datetime.now()
        for cid, rfm in customer_rfm.items():
            # Recency: 距今天数，越近分数越高
            recency_days = (now - datetime.fromisoformat(rfm['recency_date'])).days
            rfm['recency_score'] = max(1, 6 - recency_days // 30)

            # Frequency: 成交次数，越多分数越高
            rfm['frequency_score'] = min(5, 1 + rfm['frequency'])

            # Monetary: 金额，越大分数越高
            if rfm['monetary'] >= 100000:
                rfm['monetary_score'] = 5
            elif rfm['monetary'] >= 50000:
                rfm['monetary_score'] = 4
            elif rfm['monetary'] >= 10000:
                rfm['monetary_score'] = 3
            elif rfm['monetary'] >= 1000:
                rfm['monetary_score'] = 2
            else:
                rfm['monetary_score'] = 1

            rfm['total_score'] = (rfm['recency_score'] +
                                 rfm['frequency_score'] +
                                 rfm['monetary_score'])

        return {
            'customer_count': len(customer_rfm),
            'lead_count': len(leads),
            'conversion_rate': round(len(leads) / max(len(customer_rfm), 1), 2),
            'top_customers': sorted(customer_rfm.items(),
                                    key=lambda x: x[1]['total_score'],
                                    reverse=True)[:10]
        }

    def sales_performance(self, period: str = None) -> Dict:
        """销售业绩分析"""
        opps = self.opportunity_mgr.list_all()
        tasks = self.task_mgr.list_tasks()

        # 按销售人员统计
        sales_performance = {}
        for opp in opps:
            if opp.assigned_to:
                if opp.assigned_to not in sales_performance:
                    sales_performance[opp.assigned_to] = {
                        'opportunities': 0,
                        'won_amount': 0,
                        'won_count': 0,
                        'tasks_completed': 0
                    }
                sales_performance[opp.assigned_to]['opportunities'] += 1
                if opp.status == 'won':
                    sales_performance[opp.assigned_to]['won_amount'] += opp.amount
                    sales_performance[opp.assigned_to]['won_count'] += 1

        for task in tasks:
            if task.assignee and task.status == TaskStatus.COMPLETED.value:
                if task.assignee not in sales_performance:
                    sales_performance[task.assignee] = {
                        'opportunities': 0,
                        'won_amount': 0,
                        'won_count': 0,
                        'tasks_completed': 0
                    }
                sales_performance[task.assignee]['tasks_completed'] += 1

        return {
            'sales_reps': list(sales_performance.keys()),
            'performance': sales_performance
        }


class CRMSystem:
    """CRM系统主类"""

    def __init__(self):
        self.customer_mgr = CustomerManager()
        self.contact_mgr = ContactManager()
        self.lead_mgr = LeadManager()
        self.opportunity_mgr = OpportunityManager()
        self.task_mgr = TaskManager()
        self.analytics = AnalyticsManager()

    # 客户管理
    def add_customer(self, name: str, **kwargs) -> Customer:
        return self.customer_mgr.add_customer(name, **kwargs)

    def search_customers(self, **filters) -> List[Customer]:
        return self.customer_mgr.search_customers(**filters)

    def update_customer(self, customer_id: str, **kwargs) -> bool:
        return self.customer_mgr.update_customer(customer_id, **kwargs)

    def delete_customer(self, customer_id: str) -> bool:
        return self.customer_mgr.delete_customer(customer_id)

    def add_tag(self, customer_id: str, tag: str) -> bool:
        return self.customer_mgr.add_tag(customer_id, tag)

    # 联系人管理
    def add_contact(self, customer_id: str, name: str, **kwargs) -> Contact:
        return self.contact_mgr.add_contact(customer_id, name, **kwargs)

    def list_contacts(self, customer_id: str) -> List[Contact]:
        return self.contact_mgr.get_contacts(customer_id)

    def add_interaction(self, contact_id: str, interaction_type: str,
                      content: str, **kwargs) -> bool:
        return self.contact_mgr.add_interaction(contact_id, interaction_type,
                                                 content, **kwargs)

    # 线索管理
    def add_lead(self, name: str, company: str, **kwargs) -> Lead:
        return self.lead_mgr.add_lead(name, company, **kwargs)

    def score_lead(self, lead_id: str) -> int:
        lead = self.lead_mgr.get_lead(lead_id)
        if lead:
            return lead.score
        return 0

    def convert_lead(self, lead_id: str, customer_name: str) -> Optional[Customer]:
        """转化线索为客户"""
        lead = self.lead_mgr.get_lead(lead_id)
        if not lead:
            return None

        # 创建客户
        customer = self.customer_mgr.add_customer(
            name=customer_name,
            phone=lead.phone,
            email=lead.email,
            tags=['从线索转化']
        )

        # 创建联系人
        self.contact_mgr.add_contact(
            customer_id=customer.customer_id,
            name=lead.name,
            position=lead.position,
            phone=lead.phone,
            email=lead.email
        )

        # 更新线索状态
        self.lead_mgr.update_lead(lead_id, status=LeadStatus.CONVERTED.value)

        return customer

    # 商机管理
    def create_opportunity(self, customer_id: str, title: str,
                           amount: float, **kwargs) -> Opportunity:
        return self.opportunity_mgr.create_opportunity(customer_id, title,
                                                       amount, **kwargs)

    def update_opportunity(self, opportunity_id: str, **kwargs) -> bool:
        return self.opportunity_mgr.update_opportunity(opportunity_id, **kwargs)

    def close_opportunity(self, opportunity_id: str, status: str,
                         **kwargs) -> bool:
        return self.opportunity_mgr.close_opportunity(opportunity_id,
                                                       status, **kwargs)

    def list_opportunities(self, **filters) -> List[Opportunity]:
        return self.opportunity_mgr.list_opportunities(**filters)

    # 任务管理
    def create_task(self, task_type: str, title: str, **kwargs) -> Task:
        return self.task_mgr.create_task(task_type, title, **kwargs)

    def complete_task(self, task_id: str) -> bool:
        return self.task_mgr.complete_task(task_id)

    def list_tasks(self, **filters) -> List[Task]:
        return self.task_mgr.list_tasks(**filters)

    # 数据分析
    def sales_funnel(self) -> Dict:
        return self.analytics.sales_funnel()

    def customer_value(self) -> Dict:
        return self.analytics.customer_value()

    def rfm_analysis(self) -> Dict:
        return self.analytics.rfm_analysis()

    def sales_performance(self, period: str = None) -> Dict:
        return self.analytics.sales_performance(period)


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("CRM系统 - 客户关系管理系统")
        print("\n使用方法:")
        print("  python3 crm.py add_customer --name <客户名称>")
        print("  python3 crm.py search_customers [--name <关键词>]")
        print("  python3 crm.py add_contact --customer_id <客户ID> --name <联系人姓名>")
        print("  python3 crm.py add_lead --name <姓名> --company <公司>")
        print("  python3 crm.py create_opportunity --customer_id <客户ID> --title <商机标题> --amount <金额>")
        print("  python3 crm.py create_task --type <任务类型> --title <任务标题>")
        print("  python3 crm.py sales_funnel")
        print("  python3 crm.py customer_value")
        print("  python3 crm.py rfm_analysis")
        print("  python3 crm.py sales_performance")
        return

    crm = CRMSystem()
    command = sys.argv[1]

    # 解析参数
    def get_arg(name, default=None):
        idx = sys.argv.index(name) if name in sys.argv else -1
        return sys.argv[idx + 1] if idx >= 0 else default

    try:
        if command == "add_customer":
            name = get_arg("--name")
            if not name:
                print("错误: 需要客户名称 (--name)")
                return

            customer = crm.add_customer(
                name=name,
                industry=get_arg("--industry"),
                scale=get_arg("--scale"),
                phone=get_arg("--phone"),
                email=get_arg("--email"),
                address=get_arg("--address")
            )
            print(f"✅ 客户创建成功")
            print(f"   客户ID: {customer.customer_id}")
            print(f"   客户名称: {customer.name}")

        elif command == "search_customers":
            filters = {}
            if "--name" in sys.argv:
                filters['name'] = get_arg("--name")
            if "--industry" in sys.argv:
                filters['industry'] = get_arg("--industry")

            customers = crm.search_customers(**filters)
            print(f"📋 找到 {len(customers)} 个客户:")
            for cust in customers[:10]:
                print(f"   - {cust.customer_id}: {cust.name} ({cust.industry or '未知行业'})")

        elif command == "update_customer":
            customer_id = get_arg("--customer_id")
            if not customer_id:
                print("错误: 需要客户ID (--customer_id)")
                return

            success = crm.update_customer(customer_id,
                                         scale=get_arg("--scale"),
                                         status=get_arg("--status"))
            if success:
                print(f"✅ 客户更新成功")
            else:
                print(f"❌ 客户未找到")

        elif command == "add_tag":
            customer_id = get_arg("--customer_id")
            tag = get_arg("--tag")
            if not customer_id or not tag:
                print("错误: 需要客户ID和标签")
                return

            success = crm.add_tag(customer_id, tag)
            if success:
                print(f"✅ 标签添加成功")
            else:
                print(f"❌ 客户未找到")

        elif command == "add_contact":
            customer_id = get_arg("--customer_id")
            name = get_arg("--name")
            if not customer_id or not name:
                print("错误: 需要客户ID和联系人姓名")
                return

            contact = crm.add_contact(
                customer_id=customer_id,
                name=name,
                position=get_arg("--position"),
                phone=get_arg("--phone"),
                email=get_arg("--email")
            )
            print(f"✅ 联系人创建成功")
            print(f"   联系人ID: {contact.contact_id}")

        elif command == "add_lead":
            name = get_arg("--name")
            company = get_arg("--company")
            if not name or not company:
                print("错误: 需要姓名和公司")
                return

            lead = crm.add_lead(
                name=name,
                company=company,
                phone=get_arg("--phone"),
                email=get_arg("--email"),
                position=get_arg("--position"),
                source=get_arg("--source"),
                interest=get_arg("--interest")
            )
            print(f"✅ 线索创建成功")
            print(f"   线索ID: {lead.lead_id}")
            print(f"   评分: {lead.score}")

        elif command == "convert_lead":
            lead_id = get_arg("--lead_id")
            customer_name = get_arg("--customer_name")
            if not lead_id or not customer_name:
                print("错误: 需要线索ID和客户名称")
                return

            customer = crm.convert_lead(lead_id, customer_name)
            if customer:
                print(f"✅ 线索转化成功")
                print(f"   客户ID: {customer.customer_id}")
            else:
                print(f"❌ 线索未找到")

        elif command == "create_opportunity":
            customer_id = get_arg("--customer_id")
            title = get_arg("--title")
            amount = get_arg("--amount")
            if not customer_id or not title or not amount:
                print("错误: 需要客户ID、商机标题和金额")
                return

            opportunity = crm.create_opportunity(
                customer_id=customer_id,
                title=title,
                amount=float(amount),
                stage=get_arg("--stage", OpportunityStage.INITIAL.value),
                probability=int(get_arg("--probability", 10))
            )
            print(f"✅ 商机创建成功")
            print(f"   商机ID: {opportunity.opportunity_id}")
            print(f"   阶段: {opportunity.stage}")
            print(f"   金额: {opportunity.amount}")

        elif command == "update_opportunity":
            opportunity_id = get_arg("--opportunity_id")
            if not opportunity_id:
                print("错误: 需要商机ID")
                return

            success = crm.update_opportunity(
                opportunity_id,
                stage=get_arg("--stage"),
                probability=int(get_arg("--probability", 0)) if get_arg("--probability") else None
            )
            if success:
                print(f"✅ 商机更新成功")
            else:
                print(f"❌ 商机未找到")

        elif command == "close_opportunity":
            opportunity_id = get_arg("--opportunity_id")
            status = get_arg("--status")
            if not opportunity_id or not status:
                print("错误: 需要商机ID和状态")
                return

            success = crm.close_opportunity(
                opportunity_id,
                status=status,
                actual_amount=float(get_arg("--actual_amount")) if get_arg("--actual_amount") else None
            )
            if success:
                print(f"✅ 商机{status}成功")
            else:
                print(f"❌ 商机未找到")

        elif command == "list_opportunities":
            filters = {}
            if "--stage" in sys.argv:
                filters['stage'] = get_arg("--stage")
            if "--status" in sys.argv:
                filters['status'] = get_arg("--status")

            opportunities = crm.list_opportunities(**filters)
            print(f"📋 找到 {len(opportunities)} 个商机:")
            for opp in opportunities[:10]:
                print(f"   - {opp.opportunity_id}: {opp.title} ({opp.stage}) - ¥{opp.amount}")

        elif command == "create_task":
            task_type = get_arg("--type", "followup")
            title = get_arg("--title")
            if not title:
                print("错误: 需要任务标题")
                return

            task = crm.create_task(
                task_type=task_type,
                title=title,
                customer_id=get_arg("--customer_id"),
                contact_id=get_arg("--contact_id"),
                opportunity_id=get_arg("--opportunity_id"),
                description=get_arg("--description"),
                due_date=get_arg("--due_date"),
                assignee=get_arg("--assignee")
            )
            print(f"✅ 任务创建成功")
            print(f"   任务ID: {task.task_id}")

        elif command == "complete_task":
            task_id = get_arg("--task_id")
            if not task_id:
                print("错误: 需要任务ID")
                return

            success = crm.complete_task(task_id)
            if success:
                print(f"✅ 任务完成成功")
            else:
                print(f"❌ 任务未找到")

        elif command == "list_tasks":
            filters = {}
            if "--status" in sys.argv:
                filters['status'] = get_arg("--status")
            if "--assignee" in sys.argv:
                filters['assignee'] = get_arg("--assignee")

            tasks = crm.list_tasks(**filters)
            print(f"📋 找到 {len(tasks)} 个任务:")
            for task in tasks[:10]:
                print(f"   - {task.task_id}: {task.title} ({task.status})")

        elif command == "sales_funnel":
            funnel = crm.sales_funnel()
            print("📊 销售漏斗分析:")
            for stage, data in funnel.items():
                print(f"   {stage}: {data['count']}个商机, ¥{data['amount']}, 概率{data['probability']}%")

        elif command == "customer_value":
            value = crm.customer_value()
            print(f"💰 客户价值分析:")
            print(f"   总客户数: {value['total_customers']}")
            print(f"   活跃客户数: {value['active_customers']}")
            print(f"   前10名客户:")
            for customer in value['revenue_by_customer']:
                print(f"   - {customer['customer_name']}: ¥{customer['revenue']}")

        elif command == "rfm_analysis":
            rfm = crm.rfm_analysis()
            if 'message' in rfm:
                print(rfm['message'])
            else:
                print(f"📊 RFM分析:")
                print(f"   客户数: {rfm['customer_count']}")
                print(f"   线索数: {rfm['lead_count']}")
                print(f"   转化率: {rfm['conversion_rate']}")
                print(f"   前10名客户:")
                for cid, data in rfm['top_customers']:
                    customer = crm.customer_mgr.get_customer(cid)
                    print(f"   - {customer.name if customer else cid}: R{data['recency_score']}F{data['frequency_score']}M{data['monetary_score']} (总分{data['total_score']})")

        elif command == "sales_performance":
            performance = crm.sales_performance()
            print(f"📊 销售业绩分析:")
            for rep_id, data in performance['performance'].items():
                print(f"   {rep_id}:")
                print(f"     - 商机数: {data['opportunities']}")
                print(f"     - 成交数: {data['won_count']}")
                print(f"     - 成交金额: ¥{data['won_amount']}")
                print(f"     - 完成任务: {data['tasks_completed']}")

        else:
            print(f"❌ 未知命令: {command}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
