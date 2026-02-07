#!/usr/bin/env python3
"""
广告效果分析器
分析广告投放效果，生成洞察和建议
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class AdMetrics:
    """广告指标"""
    platform: str
    account: str
    start_date: str
    end_date: str
    total_budget: float
    total_spent: float
    total_impressions: int
    total_clicks: int
    total_conversions: int
    avg_ctr: float
    avg_cpc: float
    avg_cpa: float
    avg_roi: float
    top_campaigns: List[Dict]
    worst_campaigns: List[Dict]


@dataclass
class Insight:
    """洞察"""
    type: str
    message: str
    impact: str
    recommendation: str


class AdAnalyzer:
    """广告分析器"""

    def __init__(self, platform: str):
        """
        初始化广告分析器

        Args:
            platform: 广告平台
        """
        self.platform = platform

    def load_metrics(
        self,
        start_date: str,
        end_date: str,
        account: Optional[str] = None
    ) -> Optional[AdMetrics]:
        """
        加载广告指标

        Args:
            start_date: 开始日期（YYYY-MM-DD）
            end_date: 结束日期（YYYY-MM-DD）
            account: 账户ID

        Returns:
            广告指标
        """
        try:
            # 模拟加载指标数据
            # 实际使用时调用各平台API
            campaigns = []

            for i in range(1, 11):
                budget = random.uniform(1000, 10000)
                spent = random.uniform(budget * 0.5, budget)
                impressions = random.randint(10000, 200000)
                clicks = random.randint(100, 5000)
                conversions = random.randint(5, 100)

                cpc = spent / clicks if clicks > 0 else 0
                cpa = spent / conversions if conversions > 0 else 0
                ctr = (clicks / impressions * 100) if impressions > 0 else 0
                roi = ((conversions * 300) - spent) / spent * 100 if spent > 0 else 0

                campaigns.append({
                    "campaign_id": f"cmp_{i}",
                    "name": f"广告活动_{i}",
                    "budget": round(budget, 2),
                    "spent": round(spent, 2),
                    "impressions": impressions,
                    "clicks": clicks,
                    "conversions": conversions,
                    "cpc": round(cpc, 2),
                    "cpa": round(cpa, 2),
                    "ctr": round(ctr, 2),
                    "roi": round(roi, 2)
                })

            # 计算汇总指标
            total_budget = sum(c["budget"] for c in campaigns)
            total_spent = sum(c["spent"] for c in campaigns)
            total_impressions = sum(c["impressions"] for c in campaigns)
            total_clicks = sum(c["clicks"] for c in campaigns)
            total_conversions = sum(c["conversions"] for c in campaigns)

            avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            avg_cpc = (total_spent / total_clicks) if total_clicks > 0 else 0
            avg_cpa = (total_spent / total_conversions) if total_conversions > 0 else 0
            avg_roi = ((total_conversions * 300) - total_spent) / total_spent * 100 if total_spent > 0 else 0

            # 排序
            top_campaigns = sorted(campaigns, key=lambda x: x["roi"], reverse=True)[:3]
            worst_campaigns = sorted(campaigns, key=lambda x: x["roi"])[:3]

            metrics = AdMetrics(
                platform=self.platform,
                account=account or "all",
                start_date=start_date,
                end_date=end_date,
                total_budget=round(total_budget, 2),
                total_spent=round(total_spent, 2),
                total_impressions=total_impressions,
                total_clicks=total_clicks,
                total_conversions=total_conversions,
                avg_ctr=round(avg_ctr, 2),
                avg_cpc=round(avg_cpc, 2),
                avg_cpa=round(avg_cpa, 2),
                avg_roi=round(avg_roi, 2),
                top_campaigns=top_campaigns,
                worst_campaigns=worst_campaigns
            )

            logger.info(f"成功加载指标: {start_date} 至 {end_date}")
            return metrics

        except Exception as e:
            logger.error(f"加载指标失败: {e}")
            return None

    def generate_insights(self, metrics: AdMetrics) -> List[Insight]:
        """
        生成洞察和建议

        Args:
            metrics: 广告指标

        Returns:
            洞察列表
        """
        insights = []

        # 预算使用率洞察
        budget_utilization = (metrics.total_spent / metrics.total_budget * 100) if metrics.total_budget > 0 else 0
        if budget_utilization < 50:
            insights.append(Insight(
                type="budget",
                message=f"预算使用率仅{budget_utilization:.1f}%，可能需要降低预算或优化出价",
                impact="中",
                recommendation="建议检查账户设置，考虑增加出价或扩大受众范围"
            ))
        elif budget_utilization > 95:
            insights.append(Insight(
                type="budget",
                message=f"预算使用率{budget_utilization:.1f}%，可能错失机会",
                impact="高",
                recommendation="建议增加预算或调整出价策略"
            ))

        # CPA洞察
        if metrics.avg_cpa > 150:
            insights.append(Insight(
                type="cpa",
                message=f"平均CPA ({metrics.avg_cpa:.2f}) 较高",
                impact="高",
                recommendation="建议优化受众定向、改进创意素材或调整出价"
            ))
        elif metrics.avg_cpa < 80:
            insights.append(Insight(
                type="cpa",
                message=f"平均CPA ({metrics.avg_cpa:.2f}) 表现优异",
                impact="高",
                recommendation="建议增加预算扩大投放"
            ))

        # CTR洞察
        if metrics.avg_ctr < 1.0:
            insights.append(Insight(
                type="ctr",
                message=f"平均CTR ({metrics.avg_ctr:.2f}%) 低于行业平均水平",
                impact="中",
                recommendation="建议优化创意素材、标题或调整受众定向"
            ))
        elif metrics.avg_ctr > 3.0:
            insights.append(Insight(
                type="ctr",
                message=f"平均CTR ({metrics.avg_ctr:.2f}%) 表现优异",
                impact="高",
                recommendation="建议扩大投放或增加预算"
            ))

        # ROI洞察
        if metrics.avg_roi > 200:
            insights.append(Insight(
                type="roi",
                message=f"ROI ({metrics.avg_roi:.2f}%) 表现优异",
                impact="高",
                recommendation="建议加大投入，扩大投放规模"
            ))
        elif metrics.avg_roi < 100:
            insights.append(Insight(
                type="roi",
                message=f"ROI ({metrics.avg_roi:.2f}%) 低于盈亏平衡点",
                impact="高",
                recommendation="建议立即优化或暂停低效活动"
            ))

        # 活动表现洞察
        if metrics.top_campaigns:
            top_roi = metrics.top_campaigns[0]["roi"]
            insights.append(Insight(
                type="campaign",
                message=f"最佳活动 '{metrics.top_campaigns[0]['name']}' 的ROI为{top_roi:.2f}%",
                impact="高",
                recommendation=f"建议将该活动的策略应用到其他活动"
            ))

        if metrics.worst_campaigns:
            worst_roi = metrics.worst_campaigns[0]["roi"]
            if worst_roi < 0:
                insights.append(Insight(
                    type="campaign",
                    message=f"最差活动 '{metrics.worst_campaigns[0]['name']}' 亏损{abs(worst_roi):.2f}%",
                    impact="高",
                    recommendation="建议立即暂停该活动并分析原因"
                ))

        return insights

    def generate_report(
        self,
        metrics: AdMetrics,
        insights: List[Insight],
        format: str = "markdown"
    ) -> str:
        """
        生成分析报告

        Args:
            metrics: 广告指标
            insights: 洞察列表
            format: 报告格式（markdown/html/json）

        Returns:
            报告文本
        """
        if format == "markdown":
            return self._generate_markdown_report(metrics, insights)
        elif format == "html":
            return self._generate_html_report(metrics, insights)
        elif format == "json":
            return json.dumps({
                "metrics": asdict(metrics),
                "insights": [asdict(i) for i in insights]
            }, ensure_ascii=False, indent=2)
        else:
            raise ValueError(f"不支持的格式: {format}")

    def _generate_markdown_report(self, metrics: AdMetrics, insights: List[Insight]) -> str:
        """生成Markdown报告"""
        report = []
        report.append("# 广告效果分析报告\n")
        report.append(f"**平台:** {metrics.platform}")
        report.append(f"**账户:** {metrics.account}")
        report.append(f"**分析周期:** {metrics.start_date} 至 {metrics.end_date}")
        report.append(f"**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # 总览
        report.append("## 总览\n")
        report.append(f"- 总预算: {metrics.total_budget:.2f} 元")
        report.append(f"- 总花费: {metrics.total_spent:.2f} 元")
        report.append(f"- 总展现量: {metrics.total_impressions:,}")
        report.append(f"- 总点击数: {metrics.total_clicks:,}")
        report.append(f"- 总转化数: {metrics.total_conversions:,}")
        report.append(f"- 平均CTR: {metrics.avg_ctr:.2f}%")
        report.append(f"- 平均CPC: {metrics.avg_cpc:.2f} 元")
        report.append(f"- 平均CPA: {metrics.avg_cpa:.2f} 元")
        report.append(f"- 平均ROI: {metrics.avg_roi:.2f}%\n")

        # 最佳活动
        report.append("## 最佳活动 (Top 3)\n")
        for i, campaign in enumerate(metrics.top_campaigns, 1):
            report.append(f"### {i}. {campaign['name']}")
            report.append(f"- ROI: {campaign['roi']:.2f}%")
            report.append(f"- CPA: {campaign['cpa']:.2f} 元")
            report.append(f"- CTR: {campaign['ctr']:.2f}%")
            report.append(f"- 转化数: {campaign['conversions']}\n")

        # 最差活动
        report.append("## 最差活动 (Bottom 3)\n")
        for i, campaign in enumerate(metrics.worst_campaigns, 1):
            report.append(f"### {i}. {campaign['name']}")
            report.append(f"- ROI: {campaign['roi']:.2f}%")
            report.append(f"- CPA: {campaign['cpa']:.2f} 元")
            report.append(f"- CTR: {campaign['ctr']:.2f}%")
            report.append(f"- 转化数: {campaign['conversions']}\n")

        # 洞察和建议
        report.append("## 洞察和建议\n")
        for i, insight in enumerate(insights, 1):
            emoji = "🔴" if insight.impact == "高" else "🟡" if insight.impact == "中" else "🟢"
            report.append(f"### {emoji} {insight.type.upper()} - {insight.message}")
            report.append(f"- **影响程度:** {insight.impact}")
            report.append(f"- **建议:** {insight.recommendation}\n")

        return "\n".join(report)

    def _generate_html_report(self, metrics: AdMetrics, insights: List[Insight]) -> str:
        """生成HTML报告"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>广告效果分析报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        h3 {{ color: #888; }}
        .metric {{ background: #f9f9f9; padding: 10px; margin: 5px 0; border-radius: 5px; }}
        .insight {{ padding: 10px; margin: 10px 0; border-left: 4px solid #ccc; }}
        .high {{ border-left-color: #e74c3c; background: #fdf0ed; }}
        .medium {{ border-left-color: #f39c12; background: #fef5e6; }}
        .low {{ border-left-color: #27ae60; background: #eafaf1; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>广告效果分析报告</h1>
    <p><strong>平台:</strong> {metrics.platform}</p>
    <p><strong>账户:</strong> {metrics.account}</p>
    <p><strong>分析周期:</strong> {metrics.start_date} 至 {metrics.end_date}</p>
    <p><strong>生成时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

    <h2>总览</h2>
    <div class="metric">总预算: {metrics.total_budget:.2f} 元</div>
    <div class="metric">总花费: {metrics.total_spent:.2f} 元</div>
    <div class="metric">总展现量: {metrics.total_impressions:,}</div>
    <div class="metric">总点击数: {metrics.total_clicks:,}</div>
    <div class="metric">总转化数: {metrics.total_conversions:,}</div>
    <div class="metric">平均CTR: {metrics.avg_ctr:.2f}%</div>
    <div class="metric">平均CPC: {metrics.avg_cpc:.2f} 元</div>
    <div class="metric">平均CPA: {metrics.avg_cpa:.2f} 元</div>
    <div class="metric">平均ROI: {metrics.avg_roi:.2f}%</div>

    <h2>最佳活动 (Top 3)</h2>
    <table>
        <tr><th>名称</th><th>ROI</th><th>CPA</th><th>CTR</th><th>转化数</th></tr>
        """

        for campaign in metrics.top_campaigns:
            html += f"""
        <tr>
            <td>{campaign['name']}</td>
            <td>{campaign['roi']:.2f}%</td>
            <td>{campaign['cpa']:.2f} 元</td>
            <td>{campaign['ctr']:.2f}%</td>
            <td>{campaign['conversions']}</td>
        </tr>
            """

        html += """
    </table>

    <h2>最差活动 (Bottom 3)</h2>
    <table>
        <tr><th>名称</th><th>ROI</th><th>CPA</th><th>CTR</th><th>转化数</th></tr>
        """

        for campaign in metrics.worst_campaigns:
            html += f"""
        <tr>
            <td>{campaign['name']}</td>
            <td>{campaign['roi']:.2f}%</td>
            <td>{campaign['cpa']:.2f} 元</td>
            <td>{campaign['ctr']:.2f}%</td>
            <td>{campaign['conversions']}</td>
        </tr>
            """

        html += """
    </table>

    <h2>洞察和建议</h2>
    """

        for insight in insights:
            impact_class = insight.impact.lower()
            html += f"""
    <div class="insight {impact_class}">
        <strong>{insight.type.upper()} - {insight.message}</strong><br>
        <em>影响程度: {insight.impact}</em><br>
        <strong>建议:</strong> {insight.recommendation}
    </div>
            """

        html += """
</body>
</html>
        """

        return html

    def analyze(
        self,
        start_date: str,
        end_date: str,
        account: Optional[str] = None,
        format: str = "markdown"
    ) -> Optional[str]:
        """
        执行完整分析流程

        Args:
            start_date: 开始日期（YYYY-MM-DD）
            end_date: 结束日期（YYYY-MM-DD）
            account: 账户ID
            format: 报告格式

        Returns:
            报告文本
        """
        # 加载指标
        metrics = self.load_metrics(start_date, end_date, account)
        if not metrics:
            logger.error("加载指标失败")
            return None

        # 生成洞察
        insights = self.generate_insights(metrics)
        logger.info(f"生成 {len(insights)} 条洞察")

        # 生成报告
        report = self.generate_report(metrics, insights, format)

        return report


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="广告效果分析器")
    parser.add_argument("--platform", required=True, choices=["baidu", "tencent", "google", "facebook", "all"],
                        help="广告平台")
    parser.add_argument("--start_date", required=True, help="开始日期（YYYY-MM-DD）")
    parser.add_argument("--end_date", required=True, help="结束日期（YYYY-MM-DD）")
    parser.add_argument("--account", help="账户ID")
    parser.add_argument("--output", required=True, help="输出文件路径")
    parser.add_argument("--format", choices=["markdown", "html", "json"],
                        default="markdown", help="报告格式")

    args = parser.parse_args()

    # 创建分析器
    analyzer = AdAnalyzer(args.platform)

    # 执行分析
    report = analyzer.analyze(
        start_date=args.start_date,
        end_date=args.end_date,
        account=args.account,
        format=args.format
    )

    if report:
        print(report)

        # 保存报告
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n报告已保存到: {args.output}")
    else:
        logger.error("分析失败")


if __name__ == "__main__":
    main()
