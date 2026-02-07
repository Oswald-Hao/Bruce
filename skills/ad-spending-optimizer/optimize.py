#!/usr/bin/env python3
"""
广告投放优化器
智能优化广告投放策略，降低获客成本，提升ROI
"""

import json
import yaml
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import random

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class AdCampaign:
    """广告活动数据"""
    campaign_id: str
    name: str
    platform: str
    budget: float
    spent: float
    impressions: int
    clicks: int
    conversions: int
    cpa: float
    cpc: float
    ctr: float
    roi: float
    status: str


@dataclass
class OptimizationResult:
    """优化结果"""
    campaign_id: str
    action: str
    new_budget: float
    new_bid: float
    reason: str
    expected_improvement: str


class AdOptimizer:
    """广告优化器"""

    def __init__(self, platform: str, config_file: str = "config/ad_accounts.yaml"):
        """
        初始化广告优化器

        Args:
            platform: 广告平台（baidu/tencent/google/facebook）
            config_file: 配置文件路径
        """
        self.platform = platform
        self.config = self._load_config(config_file)
        self.campaigns: List[AdCampaign] = []

    def _load_config(self, config_file: str) -> Dict:
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return {}

    def load_campaigns(self) -> bool:
        """
        加载广告活动数据

        Returns:
            是否加载成功
        """
        # 模拟加载广告活动数据
        # 实际使用时调用各平台的API
        try:
            # 模拟数据
            for i in range(1, 6):
                budget = random.uniform(1000, 10000)
                spent = random.uniform(0, budget)
                impressions = random.randint(10000, 100000)
                clicks = random.randint(100, 5000)
                conversions = random.randint(5, 100)

                cpc = spent / clicks if clicks > 0 else 0
                cpa = spent / conversions if conversions > 0 else 0
                ctr = (clicks / impressions * 100) if impressions > 0 else 0
                roi = ((conversions * 300) - spent) / spent * 100 if spent > 0 else 0

                campaign = AdCampaign(
                    campaign_id=f"cmp_{i}",
                    name=f"广告活动_{i}",
                    platform=self.platform,
                    budget=budget,
                    spent=spent,
                    impressions=impressions,
                    clicks=clicks,
                    conversions=conversions,
                    cpa=round(cpa, 2),
                    cpc=round(cpc, 2),
                    ctr=round(ctr, 2),
                    roi=round(roi, 2),
                    status="running"
                )
                self.campaigns.append(campaign)

            logger.info(f"成功加载 {len(self.campaigns)} 个广告活动")
            return True

        except Exception as e:
            logger.error(f"加载广告活动失败: {e}")
            return False

    def optimize_budget(self, max_cpa: float, goal: str = "conversion") -> List[OptimizationResult]:
        """
        优化预算分配

        Args:
            max_cpa: 最大CPA目标
            goal: 优化目标（conversion/clicks/impressions）

        Returns:
            优化结果列表
        """
        results = []

        for campaign in self.campaigns:
            if campaign.status != "running":
                continue

            result = self._optimize_single_campaign(campaign, max_cpa, goal)
            if result:
                results.append(result)

        return results

    def _optimize_single_campaign(
        self,
        campaign: AdCampaign,
        max_cpa: float,
        goal: str
    ) -> Optional[OptimizationResult]:
        """
        优化单个广告活动

        Args:
            campaign: 广告活动
            max_cpa: 最大CPA
            goal: 优化目标

        Returns:
            优化结果
        """
        action = "keep"
        new_budget = campaign.budget
        new_bid = campaign.cpc
        reason = ""
        expected_improvement = ""

        if goal == "conversion":
            # 优化转化
            if campaign.cpa > max_cpa:
                # CPA过高，降低预算
                new_budget = campaign.budget * 0.8
                new_bid = campaign.cpc * 0.9
                action = "decrease"
                reason = f"CPA ({campaign.cpa}) 超过目标 ({max_cpa})"
                expected_improvement = "预计CPA降低10-20%"
            elif campaign.cpa < max_cpa * 0.7:
                # CPA很低，增加预算
                new_budget = campaign.budget * 1.3
                new_bid = campaign.cpc * 1.1
                action = "increase"
                reason = f"CPA ({campaign.cpa}) 远低于目标 ({max_cpa})"
                expected_improvement = "预计转化数增加20-30%"

        elif goal == "clicks":
            # 优化点击
            if campaign.ctr < 1.0:
                # CTR过低，优化创意
                new_bid = campaign.cpc * 1.2
                action = "optimize_creative"
                reason = f"CTR ({campaign.ctr:.2f}%) 低于目标 (1%)"
                expected_improvement = "建议优化创意素材"
            elif campaign.ctr > 3.0:
                # CTR很高，增加预算
                new_budget = campaign.budget * 1.2
                action = "increase"
                reason = f"CTR ({campaign.ctr:.2f}%) 表现优异"
                expected_improvement = "预计点击数增加20%"

        elif goal == "impressions":
            # 优化展现量
            if campaign.spent / campaign.budget < 0.5:
                # 预算未花完，降低出价
                new_bid = campaign.cpc * 0.8
                action = "decrease_bid"
                reason = "预算利用率低"
                expected_improvement = "预计CPM降低20%"

        return OptimizationResult(
            campaign_id=campaign.campaign_id,
            action=action,
            new_budget=round(new_budget, 2),
            new_bid=round(new_bid, 2),
            reason=reason,
            expected_improvement=expected_improvement
        )

    def apply_optimization(self, results: List[OptimizationResult]) -> bool:
        """
        应用优化策略

        Args:
            results: 优化结果列表

        Returns:
            是否应用成功
        """
        try:
            # 模拟应用优化
            # 实际使用时调用各平台的API
            logger.info(f"应用 {len(results)} 个优化策略")

            for result in results:
                logger.info(f"  - {result.campaign_id}: {result.action}, 新预算: {result.new_budget}, 新出价: {result.new_bid}")

            return True

        except Exception as e:
            logger.error(f"应用优化失败: {e}")
            return False

    def generate_report(self, results: List[OptimizationResult]) -> str:
        """
        生成优化报告

        Args:
            results: 优化结果列表

        Returns:
            报告文本
        """
        report = []
        report.append("# 广告投放优化报告\n")
        report.append(f"平台: {self.platform}")
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"优化活动数: {len(results)}\n")
        report.append("## 优化建议\n")

        for i, result in enumerate(results, 1):
            report.append(f"### {i}. {result.campaign_id}")
            report.append(f"- 操作: {result.action}")
            report.append(f"- 新预算: {result.new_budget}")
            report.append(f"- 新出价: {result.new_bid}")
            report.append(f"- 原因: {result.reason}")
            report.append(f"- 预期效果: {result.expected_improvement}\n")

        return "\n".join(report)

    def optimize(
        self,
        budget: float,
        goal: str,
        max_cpa: Optional[float] = None,
        max_cpc: Optional[float] = None
    ) -> Tuple[List[OptimizationResult], str]:
        """
        执行完整优化流程

        Args:
            budget: 总预算
            goal: 优化目标
            max_cpa: 最大CPA目标
            max_cpc: 最大CPC目标

        Returns:
            (优化结果列表, 报告)
        """
        # 加载广告活动
        if not self.load_campaigns():
            logger.error("加载广告活动失败")
            return [], ""

        # 优化预算
        if max_cpa:
            results = self.optimize_budget(max_cpa, goal)
        else:
            logger.warning("未设置max_cpa，使用默认优化")
            results = []

        # 应用优化
        if results:
            self.apply_optimization(results)

        # 生成报告
        report = self.generate_report(results)

        return results, report


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="广告投放优化器")
    parser.add_argument("--platform", required=True, choices=["baidu", "tencent", "google", "facebook"],
                        help="广告平台")
    parser.add_argument("--account", required=True, help="账户ID")
    parser.add_argument("--budget", type=float, required=True, help="总预算")
    parser.add_argument("--goal", choices=["conversion", "clicks", "impressions"],
                        default="conversion", help="优化目标")
    parser.add_argument("--max_cpa", type=float, help="最大CPA目标")
    parser.add_argument("--max_cpc", type=float, help="最大CPC目标")
    parser.add_argument("--output", help="输出文件路径")

    args = parser.parse_args()

    # 创建优化器
    optimizer = AdOptimizer(args.platform)

    # 执行优化
    results, report = optimizer.optimize(
        budget=args.budget,
        goal=args.goal,
        max_cpa=args.max_cpa,
        max_cpc=args.max_cpc
    )

    # 输出结果
    print(report)

    # 保存报告
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n报告已保存到: {args.output}")


if __name__ == "__main__":
    main()
