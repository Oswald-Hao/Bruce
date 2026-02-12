#!/usr/bin/env python3
"""
智能广告投放优化系统 - Smart Ad Optimizer
功能：广告账户管理、广告系列、A/B测试、ROI分析、自动化优化
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
import uuid


# 数据目录
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
CONFIG_DIR = os.path.join(os.path.dirname(__file__), 'config')

# 创建必要的目录
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)


class Platform(Enum):
    """平台"""
    GOOGLE = "google"
    FACEBOOK = "facebook"
    DOUYIN = "douyin"
    KUAISHOU = "kuaishou"


class BiddingStrategy(Enum):
    """出价策略"""
    MAXIMIZE_CLICKS = "MAXIMIZE_CLICKS"
    MAXIMIZE_CONVERSIONS = "MAXIMIZE_CONVERSIONS"
    TARGET_CPA = "TARGET_CPA"
    TARGET_ROAS = "TARGET_ROAS"
    MANUAL_CPC = "MANUAL_CPC"


class CampaignStatus(Enum):
    """广告系列状态"""
    ACTIVE = "active"
    PAUSED = "paused"
    REMOVED = "removed"


class TestStatus(Enum):
    """测试状态"""
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class AdAccount:
    """广告账户"""
    account_id: str
    platform: str
    name: str
    currency: str = "CNY"
    status: str = "active"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    api_config: Dict = field(default_factory=dict)


@dataclass
class Campaign:
    """广告系列"""
    campaign_id: str
    account_id: str
    name: str
    status: str = CampaignStatus.ACTIVE.value
    budget: float = 0.0
    bidding_strategy: str = BiddingStrategy.MAXIMIZE_CONVERSIONS.value
    target_roas: Optional[float] = None
    start_date: str = field(default_factory=lambda: datetime.now().date().isoformat())
    end_date: Optional[str] = None
    metrics: Dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ABTest:
    """A/B测试"""
    test_id: str
    name: str
    campaign_id: str
    variable: str  # creative, audience, bidding, title
    variants: List[str]
    start_date: str
    end_date: Optional[str] = None
    status: str = TestStatus.RUNNING.value
    results: Dict = field(default_factory=dict)
    winner: Optional[str] = None
    significance: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class OptimizationRule:
    """优化规则"""
    rule_id: str
    type: str  # pause_low_roi, increase_high_roi, adjust_bidding
    name: str
    condition: str  # roi < 0.5
    action: str  # pause, increase, decrease
    enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Competitor:
    """竞品"""
    competitor_id: str
    name: str
    platform: str
    keywords: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


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


class AccountManager(DataManager):
    """广告账户管理"""

    def __init__(self):
        super().__init__('accounts.json')

    def add_account(self, platform: str, account_id: str, name: str, **kwargs) -> AdAccount:
        """添加账户"""
        account = AdAccount(
            account_id=account_id,
            platform=platform,
            name=name,
            **kwargs
        )
        self.data.append(asdict(account))
        self.save()
        return account

    def get_account(self, account_id: str) -> Optional[AdAccount]:
        """获取账户"""
        for acc in self.data:
            if acc['account_id'] == account_id:
                return AdAccount(**acc)
        return None

    def list_accounts(self, **filters) -> List[AdAccount]:
        """列出账户"""
        results = []
        for acc in self.data:
            match = True
            for key, value in filters.items():
                if key not in acc or acc[key] != value:
                    match = False
                    break
            if match:
                results.append(AdAccount(**acc))
        return results


class CampaignManager(DataManager):
    """广告系列管理"""

    def __init__(self):
        super().__init__('campaigns.json')

    def create_campaign(self, account_id: str, name: str, budget: float, **kwargs) -> Campaign:
        """创建广告系列"""
        campaign = Campaign(
            campaign_id=f"camp_{uuid.uuid4().hex[:8]}",
            account_id=account_id,
            name=name,
            budget=budget,
            **kwargs
        )
        self.data.append(asdict(campaign))
        self.save()
        return campaign

    def get_campaign(self, campaign_id: str) -> Optional[Campaign]:
        """获取广告系列"""
        for camp in self.data:
            if camp['campaign_id'] == campaign_id:
                return Campaign(**camp)
        return None

    def update_campaign(self, campaign_id: str, **kwargs) -> bool:
        """更新广告系列"""
        for i, camp in enumerate(self.data):
            if camp['campaign_id'] == campaign_id:
                self.data[i].update(kwargs)
                self.save()
                return True
        return False

    def pause_campaign(self, campaign_id: str) -> bool:
        """暂停广告系列"""
        return self.update_campaign(campaign_id, status=CampaignStatus.PAUSED.value)

    def activate_campaign(self, campaign_id: str) -> bool:
        """激活广告系列"""
        return self.update_campaign(campaign_id, status=CampaignStatus.ACTIVE.value)

    def update_metrics(self, campaign_id: str, metrics: Dict) -> bool:
        """更新广告数据"""
        campaign = self.get_campaign(campaign_id)
        if campaign:
            # 合并metrics
            updated_metrics = {**campaign.metrics, **metrics}
            # 计算ROI
            cost = updated_metrics.get('cost', 0)
            revenue = updated_metrics.get('revenue', 0)
            updated_metrics['roi'] = revenue / cost if cost > 0 else 0
            updated_metrics['ctr'] = updated_metrics.get('clicks', 0) / updated_metrics.get('impressions', 1)
            updated_metrics['conversion_rate'] = updated_metrics.get('conversions', 0) / updated_metrics.get('clicks', 1)
            return self.update_campaign(campaign_id, metrics=updated_metrics)
        return False

    def list_campaigns(self, **filters) -> List[Campaign]:
        """列出广告系列"""
        results = []
        for camp in self.data:
            match = True
            for key, value in filters.items():
                if key not in camp or camp[key] != value:
                    match = False
                    break
            if match:
                results.append(Campaign(**camp))
        return results


class ABTestManager(DataManager):
    """A/B测试管理"""

    def __init__(self):
        super().__init__('ab_tests.json')

    def create_test(self, name: str, campaign_id: str, variable: str,
                   variants: List[str]) -> ABTest:
        """创建A/B测试"""
        test = ABTest(
            test_id=f"test_{uuid.uuid4().hex[:8]}",
            name=name,
            campaign_id=campaign_id,
            variable=variable,
            variants=variants,
            start_date=datetime.now().date().isoformat()
        )
        self.data.append(asdict(test))
        self.save()
        return test

    def get_test(self, test_id: str) -> Optional[ABTest]:
        """获取测试"""
        for test in self.data:
            if test['test_id'] == test_id:
                return ABTest(**test)
        return None

    def update_test(self, test_id: str, **kwargs) -> bool:
        """更新测试"""
        for i, test in enumerate(self.data):
            if test['test_id'] == test_id:
                self.data[i].update(kwargs)
                self.save()
                return True
        return False

    def record_variant_result(self, test_id: str, variant: str, metrics: Dict) -> bool:
        """记录变体结果"""
        test = self.get_test(test_id)
        if test:
            if variant not in test.results:
                test.results[variant] = {}
            test.results[variant].update(metrics)
            self.update_test(test_id, results=test.results)
            return True
        return False

    def calculate_winner(self, test_id: str) -> Optional[str]:
        """计算胜出变体"""
        test = self.get_test(test_id)
        if not test:
            return None

        best_variant = None
        best_conversion_rate = 0

        for variant, metrics in test.results.items():
            conversion_rate = metrics.get('conversion_rate', 0)
            if conversion_rate > best_conversion_rate:
                best_conversion_rate = conversion_rate
                best_variant = variant

        return best_variant

    def conclude_test(self, test_id: str, apply_winner: bool = False) -> bool:
        """结束测试"""
        winner = self.calculate_winner(test_id)
        if winner:
            return self.update_test(
                test_id,
                end_date=datetime.now().date().isoformat(),
                status=TestStatus.COMPLETED.value,
                winner=winner
            )
        return False

    def list_tests(self, **filters) -> List[ABTest]:
        """列出测试"""
        results = []
        for test in self.data:
            match = True
            for key, value in filters.items():
                if key not in test or test[key] != value:
                    match = False
                    break
            if match:
                results.append(ABTest(**test))
        return results


class OptimizationRuleManager(DataManager):
    """优化规则管理"""

    def __init__(self):
        super().__init__('optimization_rules.json')

    def add_rule(self, type: str, name: str, condition: str, action: str) -> OptimizationRule:
        """添加优化规则"""
        rule = OptimizationRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            type=type,
            name=name,
            condition=condition,
            action=action
        )
        self.data.append(asdict(rule))
        self.save()
        return rule

    def get_rule(self, rule_id: str) -> Optional[OptimizationRule]:
        """获取规则"""
        for rule in self.data:
            if rule['rule_id'] == rule_id:
                return OptimizationRule(**rule)
        return None

    def list_rules(self, **filters) -> List[OptimizationRule]:
        """列出规则"""
        results = []
        for rule in self.data:
            match = True
            for key, value in filters.items():
                if key not in rule or rule[key] != value:
                    match = False
                    break
            if match:
                results.append(OptimizationRule(**rule))
        return results


class CompetitorManager(DataManager):
    """竞品管理"""

    def __init__(self):
        super().__init__('competitors.json')

    def add_competitor(self, name: str, platform: str, keywords: List[str]) -> Competitor:
        """添加竞品"""
        competitor = Competitor(
            competitor_id=f"comp_{uuid.uuid4().hex[:8]}",
            name=name,
            platform=platform,
            keywords=keywords
        )
        self.data.append(asdict(competitor))
        self.save()
        return competitor

    def get_competitor(self, competitor_id: str) -> Optional[Competitor]:
        """获取竞品"""
        for comp in self.data:
            if comp['competitor_id'] == competitor_id:
                return Competitor(**comp)
        return None

    def list_competitors(self, **filters) -> List[Competitor]:
        """列出竞品"""
        results = []
        for comp in self.data:
            match = True
            for key, value in filters.items():
                if key not in comp or comp[key] != value:
                    match = False
                    break
            if match:
                results.append(Competitor(**comp))
        return results


class AdOptimizer:
    """智能广告投放优化系统"""

    def __init__(self):
        self.account_mgr = AccountManager()
        self.campaign_mgr = CampaignManager()
        self.ab_test_mgr = ABTestManager()
        self.rule_mgr = OptimizationRuleManager()
        self.competitor_mgr = CompetitorManager()

    # 账户管理
    def add_account(self, platform: str, account_id: str, name: str, **kwargs) -> AdAccount:
        return self.account_mgr.add_account(platform, account_id, name, **kwargs)

    def list_accounts(self, **filters) -> List[AdAccount]:
        return self.account_mgr.list_accounts(**filters)

    # 广告系列管理
    def create_campaign(self, account_id: str, name: str, budget: float, **kwargs) -> Campaign:
        return self.campaign_mgr.create_campaign(account_id, name, budget, **kwargs)

    def update_campaign(self, campaign_id: str, **kwargs) -> bool:
        return self.campaign_mgr.update_campaign(campaign_id, **kwargs)

    def pause_campaign(self, campaign_id: str) -> bool:
        return self.campaign_mgr.pause_campaign(campaign_id)

    def activate_campaign(self, campaign_id: str) -> bool:
        return self.campaign_mgr.activate_campaign(campaign_id)

    def update_metrics(self, campaign_id: str, metrics: Dict) -> bool:
        return self.campaign_mgr.update_metrics(campaign_id, metrics)

    def list_campaigns(self, **filters) -> List[Campaign]:
        return self.campaign_mgr.list_campaigns(**filters)

    # A/B测试
    def create_ab_test(self, name: str, campaign_id: str, variable: str,
                      variants: List[str]) -> ABTest:
        return self.ab_test_mgr.create_test(name, campaign_id, variable, variants)

    def record_variant_result(self, test_id: str, variant: str, metrics: Dict) -> bool:
        return self.ab_test_mgr.record_variant_result(test_id, variant, metrics)

    def calculate_winner(self, test_id: str) -> Optional[str]:
        return self.ab_test_mgr.calculate_winner(test_id)

    def conclude_test(self, test_id: str, apply_winner: bool = False) -> bool:
        return self.ab_test_mgr.conclude_test(test_id, apply_winner)

    def list_tests(self, **filters) -> List[ABTest]:
        return self.ab_test_mgr.list_tests(**filters)

    # 优化规则
    def add_optimization_rule(self, type: str, name: str, condition: str, action: str) -> OptimizationRule:
        return self.rule_mgr.add_rule(type, name, condition, action)

    def list_rules(self, **filters) -> List[OptimizationRule]:
        return self.rule_mgr.list_rules(**filters)

    # ROI分析
    def roi_analysis(self, campaign_id: str) -> Dict:
        """ROI分析"""
        campaign = self.campaign_mgr.get_campaign(campaign_id)
        if not campaign:
            return {}

        metrics = campaign.metrics
        return {
            'campaign_id': campaign_id,
            'name': campaign.name,
            'budget': campaign.budget,
            'cost': metrics.get('cost', 0),
            'revenue': metrics.get('revenue', 0),
            'roi': metrics.get('roi', 0),
            'impressions': metrics.get('impressions', 0),
            'clicks': metrics.get('clicks', 0),
            'conversions': metrics.get('conversions', 0),
            'ctr': metrics.get('ctr', 0),
            'conversion_rate': metrics.get('conversion_rate', 0)
        }

    def roi_report(self, platform: str = None, account_id: str = None) -> Dict:
        """ROI报告"""
        filters = {}
        if platform:
            # 需要先获取账户，然后获取账户下的广告系列
            accounts = self.account_mgr.list_accounts(platform=platform)
            account_ids = [acc.account_id for acc in accounts]
            filters['account_id'] = account_ids if account_ids else ['']

        if account_id:
            filters['account_id'] = account_id

        campaigns = self.campaign_mgr.list_campaigns(**filters)

        total_cost = 0
        total_revenue = 0
        total_impressions = 0
        total_clicks = 0
        total_conversions = 0

        campaign_details = []
        for camp in campaigns:
            metrics = camp.metrics
            total_cost += metrics.get('cost', 0)
            total_revenue += metrics.get('revenue', 0)
            total_impressions += metrics.get('impressions', 0)
            total_clicks += metrics.get('clicks', 0)
            total_conversions += metrics.get('conversions', 0)

            campaign_details.append({
                'campaign_id': camp.campaign_id,
                'name': camp.name,
                'status': camp.status,
                'budget': camp.budget,
                'cost': metrics.get('cost', 0),
                'revenue': metrics.get('revenue', 0),
                'roi': metrics.get('roi', 0),
                'conversions': metrics.get('conversions', 0)
            })

        return {
            'campaigns': campaign_details,
            'summary': {
                'total_cost': total_cost,
                'total_revenue': total_revenue,
                'total_roi': total_revenue / total_cost if total_cost > 0 else 0,
                'total_impressions': total_impressions,
                'total_clicks': total_clicks,
                'total_conversions': total_conversions,
                'avg_ctr': total_clicks / total_impressions if total_impressions > 0 else 0,
                'avg_conversion_rate': total_conversions / total_clicks if total_clicks > 0 else 0
            }
        }

    # 自动化优化
    def auto_optimize(self, roi_threshold: float = 1.0) -> List[str]:
        """自动优化"""
        rules = self.rule_mgr.list_rules(enabled=True)
        actions_taken = []

        for rule in rules:
            if rule.type == "pause_low_roi":
                # 找出低ROI的广告系列
                campaigns = self.campaign_mgr.list_campaigns(status=CampaignStatus.ACTIVE.value)
                for camp in campaigns:
                    if camp.metrics.get('roi', 0) < roi_threshold:
                        if self.pause_campaign(camp.campaign_id):
                            actions_taken.append(f"暂停低ROI广告系列: {camp.name} (ROI: {camp.metrics.get('roi', 0)})")

            elif rule.type == "increase_high_roi":
                # 增加高ROI广告系列的预算
                campaigns = self.campaign_mgr.list_campaigns(status=CampaignStatus.ACTIVE.value)
                for camp in campaigns:
                    if camp.metrics.get('roi', 0) > roi_threshold * 2:
                        new_budget = camp.budget * 1.2
                        if self.update_campaign(camp.campaign_id, budget=new_budget):
                            actions_taken.append(f"增加高ROI广告系列预算: {camp.name} (新预算: {new_budget})")

        return actions_taken

    # 优化建议
    def optimization_suggestions(self, campaign_id: str) -> List[Dict]:
        """优化建议"""
        campaign = self.campaign_mgr.get_campaign(campaign_id)
        if not campaign:
            return []

        suggestions = []
        metrics = campaign.metrics

        # ROI建议
        if metrics.get('roi', 0) < 1.0:
            suggestions.append({
                'type': 'pause',
                'reason': f'ROI过低 ({metrics.get("roi", 0)})',
                'suggestion': '暂停广告或优化受众定位'
            })
        elif metrics.get('roi', 0) > 3.0:
            suggestions.append({
                'type': 'increase_budget',
                'reason': f'ROI较高 ({metrics.get("roi", 0)})',
                'suggestion': '增加预算以获得更多转化'
            })

        # CTR建议
        if metrics.get('ctr', 0) < 0.01:
            suggestions.append({
                'type': 'optimize_creative',
                'reason': f'CTR过低 ({metrics.get("ctr", 0)})',
                'suggestion': '优化广告创意或标题'
            })

        # 转化率建议
        if metrics.get('conversion_rate', 0) < 0.01:
            suggestions.append({
                'type': 'optimize_landing',
                'reason': f'转化率过低 ({metrics.get("conversion_rate", 0)})',
                'suggestion': '优化落地页或出价策略'
            })

        return suggestions

    # 竞品分析
    def add_competitor(self, name: str, platform: str, keywords: List[str]) -> Competitor:
        return self.competitor_mgr.add_competitor(name, platform, keywords)

    def list_competitors(self, **filters) -> List[Competitor]:
        return self.competitor_mgr.list_competitors(**filters)


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("智能广告投放优化系统 - Smart Ad Optimizer")
        print("\n使用方法:")
        print("  python3 ad.py add_account --platform <平台> --account_id <账户ID> --name <名称>")
        print("  python3 ad.py create_campaign --account_id <账户ID> --name <名称> --budget <预算>")
        print("  python3 ad.py roi_analysis --campaign_id <广告系列ID>")
        print("  python3 ad.py roi_report --platform <平台>")
        print("  python3 ad.py create_ab_test --name <测试名称> --campaign_id <广告系列ID> --variable <变量> --variants <变体>")
        print("  python3 ad.py auto_optimize --roi_threshold <阈值>")
        return

    optimizer = AdOptimizer()
    command = sys.argv[1]

    # 解析参数
    def get_arg(name, default=None):
        idx = sys.argv.index(name) if name in sys.argv else -1
        return sys.argv[idx + 1] if idx >= 0 else default

    try:
        if command == "add_account":
            platform = get_arg("--platform")
            account_id = get_arg("--account_id")
            name = get_arg("--name")
            if not platform or not account_id or not name:
                print("错误: 需要平台、账户ID和名称")
                return

            account = optimizer.add_account(platform, account_id, name)
            print(f"✅ 账户添加成功")
            print(f"   账户ID: {account.account_id}")
            print(f"   平台: {platform}")
            print(f"   名称: {name}")

        elif command == "create_campaign":
            account_id = get_arg("--account_id")
            name = get_arg("--name")
            budget = get_arg("--budget")
            if not account_id or not name or not budget:
                print("错误: 需要账户ID、名称和预算")
                return

            campaign = optimizer.create_campaign(account_id, name, float(budget))
            print(f"✅ 广告系列创建成功")
            print(f"   广告系列ID: {campaign.campaign_id}")
            print(f"   名称: {name}")
            print(f"   预算: ¥{budget}")

        elif command == "update_metrics":
            campaign_id = get_arg("--campaign_id")
            if not campaign_id:
                print("错误: 需要广告系列ID")
                return

            metrics = {}
            if "--impressions" in sys.argv:
                metrics['impressions'] = int(get_arg("--impressions"))
            if "--clicks" in sys.argv:
                metrics['clicks'] = int(get_arg("--clicks"))
            if "--conversions" in sys.argv:
                metrics['conversions'] = int(get_arg("--conversions"))
            if "--cost" in sys.argv:
                metrics['cost'] = float(get_arg("--cost"))
            if "--revenue" in sys.argv:
                metrics['revenue'] = float(get_arg("--revenue"))

            success = optimizer.update_metrics(campaign_id, metrics)
            if success:
                print(f"✅ 广告数据更新成功")
            else:
                print(f"❌ 广告系列未找到")

        elif command == "roi_analysis":
            campaign_id = get_arg("--campaign_id")
            if not campaign_id:
                print("错误: 需要广告系列ID")
                return

            analysis = optimizer.roi_analysis(campaign_id)
            if analysis:
                print(f"📊 ROI分析:")
                print(f"   名称: {analysis['name']}")
                print(f"   预算: ¥{analysis['budget']}")
                print(f"   成本: ¥{analysis['cost']}")
                print(f"   收入: ¥{analysis['revenue']}")
                print(f"   ROI: {analysis['roi']:.2f}")
                print(f"   点击数: {analysis['clicks']}")
                print(f"   转化数: {analysis['conversions']}")
                print(f"   CTR: {analysis['ctr']:.2%}")
                print(f"   转化率: {analysis['conversion_rate']:.2%}")
            else:
                print(f"❌ 广告系列未找到")

        elif command == "roi_report":
            platform = get_arg("--platform")
            account_id = get_arg("--account_id")

            filters = {}
            if platform:
                filters['platform'] = platform
            if account_id:
                filters['account_id'] = account_id

            report = optimizer.roi_report(platform=platform, account_id=account_id)
            summary = report['summary']
            print(f"📊 ROI报告:")
            print(f"   总成本: ¥{summary['total_cost']}")
            print(f"   总收入: ¥{summary['total_revenue']}")
            print(f"   总ROI: {summary['total_roi']:.2f}")
            print(f"   总展示: {summary['total_impressions']}")
            print(f"   总点击: {summary['total_clicks']}")
            print(f"   总转化: {summary['total_conversions']}")
            print(f"   平均CTR: {summary['avg_ctr']:.2%}")
            print(f"   平均转化率: {summary['avg_conversion_rate']:.2%}")

        elif command == "create_ab_test":
            name = get_arg("--name")
            campaign_id = get_arg("--campaign_id")
            variable = get_arg("--variable")
            variants_str = get_arg("--variants")
            if not name or not campaign_id or not variable or not variants_str:
                print("错误: 需要测试名称、广告系列ID、变量和变体")
                return

            variants = variants_str.split(',')
            test = optimizer.create_ab_test(name, campaign_id, variable, variants)
            print(f"✅ A/B测试创建成功")
            print(f"   测试ID: {test.test_id}")
            print(f"   变量: {variable}")
            print(f"   变体: {variants}")

        elif command == "record_variant":
            test_id = get_arg("--test_id")
            variant = get_arg("--variant")
            if not test_id or not variant:
                print("错误: 需要测试ID和变体")
                return

            metrics = {}
            if "--impressions" in sys.argv:
                metrics['impressions'] = int(get_arg("--impressions"))
            if "--clicks" in sys.argv:
                metrics['clicks'] = int(get_arg("--clicks"))
            if "--conversions" in sys.argv:
                metrics['conversions'] = int(get_arg("--conversions"))
            
            success = optimizer.record_variant_result(test_id, variant, metrics)
            if success:
                print(f"✅ 变体结果记录成功")
            else:
                print(f"❌ 测试未找到")

        elif command == "ab_test_results":
            test_id = get_arg("--test_id")
            if not test_id:
                print("错误: 需要测试ID")
                return

            test = optimizer.ab_test_mgr.get_test(test_id)
            if test:
                winner = optimizer.calculate_winner(test_id)
                print(f"📊 A/B测试结果:")
                print(f"   测试名称: {test.name}")
                print(f"   变量: {test.variable}")
                print(f"   状态: {test.status}")
                print(f"   胜出变体: {winner}")
                print(f"   各变体数据:")
                for variant, data in test.results.items():
                    print(f"     {variant}:")
                    print(f"       展示: {data.get('impressions', 0)}")
                    print(f"       点击: {data.get('clicks', 0)}")
                    print(f"       转化: {data.get('conversions', 0)}")
            else:
                print(f"❌ 测试未找到")

        elif command == "conclude_ab_test":
            test_id = get_arg("--test_id")
            apply_winner = "--apply_winner" in sys.argv
            if not test_id:
                print("错误: 需要测试ID")
                return

            success = optimizer.conclude_test(test_id, apply_winner)
            if success:
                test = optimizer.ab_test_mgr.get_test(test_id)
                print(f"✅ 测试已结束")
                print(f"   胜出变体: {test.winner}")
                print(f"   是否应用: {apply_winner}")
            else:
                print(f"❌ 测试未找到")

        elif command == "auto_optimize":
            roi_threshold = float(get_arg("--roi_threshold", 1.0))
            actions = optimizer.auto_optimize(roi_threshold)
            print(f"🤖 自动优化结果:")
            if actions:
                for action in actions:
                    print(f"   - {action}")
            else:
                print(f"   无需优化的广告系列")

        elif command == "optimization_suggestions":
            campaign_id = get_arg("--campaign_id")
            if not campaign_id:
                print("错误: 需要广告系列ID")
                return

            suggestions = optimizer.optimization_suggestions(campaign_id)
            print(f"💡 优化建议:")
            if suggestions:
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"   {i}. {suggestion['type']}:")
                    print(f"      原因: {suggestion['reason']}")
                    print(f"      建议: {suggestion['suggestion']}")
            else:
                print(f"   无优化建议")

        elif command == "add_competitor":
            name = get_arg("--name")
            platform = get_arg("--platform")
            keywords_str = get_arg("--keywords")
            if not name or not platform or not keywords_str:
                print("错误: 需要名称、平台和关键词")
                return

            keywords = keywords_str.split(',')
            competitor = optimizer.add_competitor(name, platform, keywords)
            print(f"✅ 竞品添加成功")
            print(f"   竞品ID: {competitor.competitor_id}")
            print(f"   名称: {name}")
            print(f"   关键词: {keywords}")

        else:
            print(f"❌ 未知命令: {command}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
