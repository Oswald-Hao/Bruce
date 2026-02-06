#!/usr/bin/env python3
"""
广告投放优化系统 - 核心优化器类
Ad Optimization System - Core Optimizer

主要功能：
- 多平台广告管理
- 数据分析
- 受众优化
- 出价调整
- 创意测试
"""

import time
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import requests


class AdOptimizer:
    """广告优化器核心类"""

    def __init__(self, platform: str, api_key: str, config: Optional[Dict] = None):
        """
        初始化广告优化器

        Args:
            platform: 平台名称（facebook/google/tiktok/baidu）
            api_key: API密钥
            config: 配置字典
        """
        self.platform = platform.lower()
        self.api_key = api_key
        self.config = config or {}
        self.base_url = self._get_base_url()
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # 支持的平台
        self.supported_platforms = ["facebook", "google", "tiktok", "baidu"]

        if self.platform not in self.supported_platforms:
            raise ValueError(f"不支持的平台: {platform}")

    def _get_base_url(self) -> str:
        """获取平台API基础URL"""
        urls = {
            "facebook": "https://graph.facebook.com/v18.0",
            "google": "https://googleads.googleapis.com/v16",
            "tiktok": "https://business-api.tiktok.com/open_api/v1.3",
            "baidu": "https://api.baidu.com/json"
        }
        return urls.get(self.platform, "")

    def _request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict:
        """
        发送API请求

        Args:
            endpoint: API端点
            method: HTTP方法
            data: 请求数据

        Returns:
            响应数据
        """
        url = f"{self.base_url}/{endpoint}"

        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data, timeout=10)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, json=data, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers, timeout=10)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            raise Exception(f"API请求失败: {str(e)}")

    def analyze_performance(self, ad_ids: List[str], period: str = "7d") -> Dict[str, Any]:
        """
        分析广告表现

        Args:
            ad_ids: 广告ID列表
            period: 分析周期（1d/7d/30d）

        Returns:
            分析结果
        """
        # 模拟数据（实际应该调用真实API）
        results = {
            "total_spend": 0,
            "total_clicks": 0,
            "total_impressions": 0,
            "conversions": 0,
            "revenue": 0,
            "ads": []
        }

        for ad_id in ad_ids:
            # 模拟每个广告的数据
            ad_data = {
                "id": ad_id,
                "impressions": 10000 + int(hash(ad_id) % 50000),
                "clicks": 100 + int(hash(ad_id) % 900),
                "spend": 10 + (int(hash(ad_id)) % 90),
                "conversions": 1 + (int(hash(ad_id)) % 10),
                "revenue": 20 + (int(hash(ad_id)) % 180)
            }

            # 计算指标
            ad_data["ctr"] = (ad_data["clicks"] / ad_data["impressions"]) * 100
            ad_data["cpc"] = ad_data["spend"] / ad_data["clicks"] if ad_data["clicks"] > 0 else 0
            ad_data["cpa"] = ad_data["spend"] / ad_data["conversions"] if ad_data["conversions"] > 0 else 0
            ad_data["conversion_rate"] = (ad_data["conversions"] / ad_data["clicks"]) * 100 if ad_data["clicks"] > 0 else 0
            ad_data["roi"] = ((ad_data["revenue"] - ad_data["spend"]) / ad_data["spend"] * 100) if ad_data["spend"] > 0 else 0

            results["ads"].append(ad_data)
            results["total_spend"] += ad_data["spend"]
            results["total_clicks"] += ad_data["clicks"]
            results["total_impressions"] += ad_data["impressions"]
            results["conversions"] += ad_data["conversions"]
            results["revenue"] += ad_data["revenue"]

        # 计算总体指标
        results["ctr"] = (results["total_clicks"] / results["total_impressions"]) * 100 if results["total_impressions"] > 0 else 0
        results["cpc"] = results["total_spend"] / results["total_clicks"] if results["total_clicks"] > 0 else 0
        results["cpa"] = results["total_spend"] / results["conversions"] if results["conversions"] > 0 else 0
        results["conversion_rate"] = (results["conversions"] / results["total_clicks"]) * 100 if results["total_clicks"] > 0 else 0
        results["roi"] = ((results["revenue"] - results["total_spend"]) / results["total_spend"] * 100) if results["total_spend"] > 0 else 0

        # 识别最佳和最差广告
        if results["ads"]:
            results["best_ad"] = max(results["ads"], key=lambda x: x.get("roi", 0))
            results["worst_ad"] = min(results["ads"], key=lambda x: x.get("roi", 0))

        return results

    def optimize_audience(self, campaign_id: str, metrics: str = "conversion_rate") -> Dict[str, Any]:
        """
        优化受众

        Args:
            campaign_id: 广告活动ID
            metrics: 优化指标（conversion_rate/ctr/roi）

        Returns:
            优化建议
        """
        # 生成优化ID
        optimization_id = f"opt_{int(time.time())}"

        # 模拟分析结果
        suggestions = [
            {
                "type": "expand_lookalike",
                "description": "基于高转化用户创建Lookalike受众",
                "expected_improvement": 25,
                "action": "create_lookalike_audience"
            },
            {
                "type": "exclude_low_performance",
                "description": "排除过去30天未转化的用户",
                "expected_improvement": 15,
                "action": "exclude_audience"
            },
            {
                "type": "add_interest_targeting",
                "description": "添加相关兴趣标签",
                "expected_improvement": 20,
                "action": "add_interests"
            }
        ]

        return {
            "optimization_id": optimization_id,
            "campaign_id": campaign_id,
            "metrics": metrics,
            "suggestions": suggestions,
            "expected_improvement": 20
        }

    def adjust_bids(self, campaign_id: str, strategy: str = "auto") -> Dict[str, Any]:
        """
        调整出价

        Args:
            campaign_id: 广告活动ID
            strategy: 出价策略（auto/conservative/aggressive）

        Returns:
            调整结果
        """
        # 模拟出价调整
        ads_count = 5 + (int(hash(campaign_id)) % 10)
        adjusted_ads = []

        for i in range(ads_count):
            old_bid = 1.0 + (i * 0.5)
            change_rate = {
                "auto": 0.1,
                "conservative": -0.1,
                "aggressive": 0.2
            }.get(strategy, 0.0)

            new_bid = old_bid * (1 + change_rate)

            adjusted_ads.append({
                "ad_id": f"ad_{i}",
                "old_bid": round(old_bid, 2),
                "new_bid": round(new_bid, 2),
                "change": round(change_rate * 100, 1)
            })

        return {
            "campaign_id": campaign_id,
            "strategy": strategy,
            "adjusted_ads": ads_count,
            "ad_adjustments": adjusted_ads,
            "avg_bid_change": round(sum(a["change"] for a in adjusted_ads) / len(adjusted_ads), 1),
            "expected_roi_increase": 15
        }

    def test_creatives(self, campaign_id: str, creatives: List[Dict], budget: float = 100, duration: str = "7d") -> Dict[str, Any]:
        """
        测试创意

        Args:
            campaign_id: 广告活动ID
            creatives: 创意列表
            budget: 测试预算
            duration: 测试周期

        Returns:
            测试结果
        """
        # 生成测试ID
        test_id = f"test_{int(time.time())}"

        # 计算每个创意的预算
        budget_per_creative = budget / len(creatives)

        # 模拟测试结果
        results = {
            "test_id": test_id,
            "campaign_id": campaign_id,
            "budget": budget,
            "budget_per_creative": budget_per_creative,
            "duration": duration,
            "variants": [],
            "winner": None
        }

        for i, creative in enumerate(creatives):
            # 模拟每个创意的表现
            performance = {
                "creative_id": creative.get("creative_id", f"creative_{i}"),
                "name": creative.get("name", f"创意{i+1}"),
                "impressions": 5000 + (int(hash(creative.get("name", str(i)))) % 10000),
                "clicks": 50 + (int(hash(creative.get("name", str(i)))) % 200),
                "conversions": 1 + (int(hash(creative.get("name", str(i)))) % 10),
                "spend": budget_per_creative
            }

            # 计算指标
            performance["ctr"] = (performance["clicks"] / performance["impressions"]) * 100
            performance["conversion_rate"] = (performance["conversions"] / performance["clicks"]) * 100 if performance["clicks"] > 0 else 0
            performance["cpa"] = performance["spend"] / performance["conversions"] if performance["conversions"] > 0 else 0
            performance["roi"] = ((performance["conversions"] * 50 - performance["spend"]) / performance["spend"] * 100) if performance["spend"] > 0 else 0

            # 计算胜率
            performance["win_rate"] = max(0, min(100, performance["roi"]))

            results["variants"].append(performance)

        # 确定获胜者
        if results["variants"]:
            results["winner"] = max(results["variants"], key=lambda x: x.get("roi", 0))

        return results

    def analyze_competitors(self, industry: str, keywords: List[str], limit: int = 10) -> Dict[str, Any]:
        """
        分析竞品

        Args:
            industry: 行业
            keywords: 关键词列表
            limit: 返回数量

        Returns:
            竞品分析结果
        """
        # 模拟竞品数据
        competitors = []

        for i in range(min(limit, 10)):
            brand = f"品牌{i+1}"
            competitors.append({
                "brand": brand,
                "ad_count": 5 + (int(hash(brand)) % 20),
                "estimated_monthly_budget": 10000 + (int(hash(brand)) % 50000),
                "avg_ctr": 0.5 + (int(hash(brand)) % 200) / 100,
                "avg_conversion_rate": 1.0 + (int(hash(brand)) % 400) / 100,
                "top_audiences": ["兴趣1", "兴趣2", "兴趣3"],
                "top_themes": ["主题1", "主题2"]
            })

        return {
            "industry": industry,
            "keywords": keywords,
            "competitors": competitors,
            "total_competitors": len(competitors)
        }

    def generate_competitor_strategy(self, competitors: Dict[str, Any]) -> List[str]:
        """
        生成竞品策略建议

        Args:
            competitors: 竞品分析结果

        Returns:
            策略建议列表
        """
        suggestions = []

        # 分析竞品平均表现
        avg_ctr = sum(c["avg_ctr"] for c in competitors.get("competitors", [])) / len(competitors.get("competitors", [1]))
        avg_budget = sum(c["estimated_monthly_budget"] for c in competitors.get("competitors", [])) / len(competitors.get("competitors", [1]))

        suggestions.append(f"竞品平均点击率: {avg_ctr:.2f}%，如果你的CTR低于此值，需要优化创意")
        suggestions.append(f"竞品平均月预算: ${avg_budget:,.0f}，建议根据预算调整出价策略")
        suggestions.append("关注竞品的主要受众和创意主题，寻找差异化机会")
        suggestions.append("竞品正在投放的关键词，考虑是否需要增加或调整")
        suggestions.append("定期监控竞品变化，及时调整策略")

        return suggestions

    def monitor_ads(self, campaign_ids: List[str], interval: int = 300, alert_rules: Optional[Dict] = None, alert_handler: Optional[callable] = None):
        """
        实时监控广告

        Args:
            campaign_ids: 广告活动ID列表
            interval: 检查间隔（秒）
            alert_rules: 告警规则
            alert_handler: 告警处理函数
        """
        print(f"开始监控广告活动: {campaign_ids}")
        print(f"检查间隔: {interval}秒")

        # 设置默认告警规则
        default_rules = {
            "low_ctr": {"threshold": 0.01, "action": "pause"},
            "low_conversion_rate": {"threshold": 0.05, "action": "adjust_bid"},
            "high_cpa": {"threshold": 50, "action": "pause"}
        }

        rules = alert_rules or default_rules

        # 模拟监控（实际应该用定时任务）
        for _ in range(3):  # 模拟3次检查
            for campaign_id in campaign_ids:
                # 模拟实时数据
                performance = {
                    "ctr": 0.005 + (hash(campaign_id) % 30) / 1000,
                    "conversion_rate": 0.03 + (hash(campaign_id)) % 50 / 1000,
                    "cpa": 30 + (hash(campaign_id)) % 50
                }

                # 检查告警规则
                for rule_name, rule in rules.items():
                    current_value = performance.get(rule_name.split("_")[1]) if "_" in rule_name else performance.get(rule_name)
                    threshold = rule["threshold"]

                    # 检查是否触发告警
                    if rule_name == "low_ctr" and current_value < threshold:
                        self._trigger_alert(campaign_id, rule_name, current_value, threshold, alert_handler)
                    elif rule_name == "low_conversion_rate" and current_value < threshold:
                        self._trigger_alert(campaign_id, rule_name, current_value, threshold, alert_handler)
                    elif rule_name == "high_cpa" and current_value > threshold:
                        self._trigger_alert(campaign_id, rule_name, current_value, threshold, alert_handler)

            print(f"完成一次检查，等待{interval}秒...")
            # time.sleep(interval)  # 实际应该等待

        print("监控结束")

    def _trigger_alert(self, campaign_id: str, alert_type: str, current_value: float, threshold: float, alert_handler: Optional[callable] = None):
        """触发告警"""
        type_names = {
            "low_ctr": "点击率过低",
            "low_conversion_rate": "转化率过低",
            "high_cpa": "单次转化成本过高"
        }

        recommendations = {
            "low_ctr": "优化创意或暂停广告",
            "low_conversion_rate": "调整出价或优化着陆页",
            "high_cpa": "暂停广告或优化受众"
        }

        alert = {
            "type": type_names.get(alert_type, alert_type),
            "campaign_id": campaign_id,
            "issue": f"{type_names.get(alert_type, alert_type)}",
            "current_value": current_value,
            "threshold": threshold,
            "recommendation": recommendations.get(alert_type, "请检查广告表现")
        }

        if alert_handler:
            alert_handler(alert)
        else:
            print(f"⚠️ 告警: {alert}")

    def generate_report(self, campaign_id: str, period: str = "7d", format: str = "markdown") -> Dict[str, Any]:
        """
        生成报告

        Args:
            campaign_id: 广告活动ID
            period: 报告周期
            format: 报告格式（markdown/html）

        Returns:
            报告内容
        """
        # 分析广告表现
        ad_ids = [f"ad_{i}" for i in range(5)]
        analysis = self.analyze_performance(ad_ids, period)

        # 生成报告摘要
        summary = f"""
# 广告投放报告 - {period}

## 概要

- 总花费: ¥{analysis['total_spend']:.2f}
- 总点击: {analysis['total_clicks']}
- 点击率: {analysis['ctr']:.2f}%
- 转化数: {analysis['conversions']}
- 转化率: {analysis['conversion_rate']:.2f}%
- 单次转化成本: ¥{analysis['cpa']:.2f}
- 投资回报率: {analysis['roi']:.2f}%

## 最佳广告

- 广告ID: {analysis.get('best_ad', {}).get('id', 'N/A')}
- ROI: {analysis.get('best_ad', {}).get('roi', 0):.2f}%

## 最差广告

- 广告ID: {analysis.get('worst_ad', {}).get('id', 'N/A')}
- ROI: {analysis.get('worst_ad', {}).get('roi', 0):.2f}%

## 优化建议

1. 暂停或优化ROI过低的广告
2. 增加对高ROI广告的预算
3. 测试新的创意素材
4. 优化受众定位
5. 调整出价策略
"""

        # 生成优化建议
        recommendations = [
            "暂停ROI低于50%的广告",
            "增加对最佳广告的预算分配",
            "测试新的创意和文案组合",
            "优化受众定向，排除不转化人群",
            "根据时段动态调整出价"
        ]

        return {
            "campaign_id": campaign_id,
            "period": period,
            "format": format,
            "summary": summary.strip(),
            "analysis": analysis,
            "recommendations": recommendations
        }

    def apply_audience_optimization(self, campaign_id: str, optimization_id: str) -> Dict[str, Any]:
        """
        应用受众优化

        Args:
            campaign_id: 广告活动ID
            optimization_id: 优化ID

        Returns:
            应用结果
        """
        return {
            "campaign_id": campaign_id,
            "optimization_id": optimization_id,
            "status": "success",
            "message": "受众优化已应用"
        }


def main():
    """主函数 - 演示使用"""
    print("=== 广告投放优化系统 ===\n")

    # 初始化优化器
    optimizer = AdOptimizer(platform="facebook", api_key="demo_key")

    # 分析广告表现
    print("1. 分析广告表现...")
    ad_ids = ["ad_001", "ad_002", "ad_003", "ad_004", "ad_005"]
    analysis = optimizer.analyze_performance(ad_ids, period="7d")
    print(f"   总花费: ¥{analysis['total_spend']:.2f}")
    print(f"   总点击: {analysis['total_clicks']}")
    print(f"   点击率: {analysis['ctr']:.2f}%")
    print(f"   转化率: {analysis['conversion_rate']:.2f}%")
    print(f"   ROI: {analysis['roi']:.2f}%")
    print()

    # 优化受众
    print("2. 优化受众...")
    audience = optimizer.optimize_audience("camp_001", "conversion_rate")
    print(f"   优化ID: {audience['optimization_id']}")
    print(f"   建议数量: {len(audience['suggestions'])}")
    print()

    # 调整出价
    print("3. 调整出价...")
    bids = optimizer.adjust_bids("camp_001", strategy="auto")
    print(f"   调整的广告数: {bids['adjusted_ads']}")
    print(f"   预期ROI提升: {bids['expected_roi_increase']}%")
    print()

    # 测试创意
    print("4. 测试创意...")
    creatives = [
        {"creative_id": "c1", "name": "创意A", "image": "img1.jpg"},
        {"creative_id": "c2", "name": "创意B", "image": "img2.jpg"}
    ]
    creative_test = optimizer.test_creatives("camp_001", creatives, budget=100)
    print(f"   测试ID: {creative_test['test_id']}")
    if creative_test['winner']:
        print(f"   最佳创意: {creative_test['winner']['name']}")
    print()

    # 生成报告
    print("5. 生成报告...")
    report = optimizer.generate_report("camp_001", period="7d")
    print(f"   报告格式: {report['format']}")
    print()

    print("=== 演示完成 ===")


if __name__ == "__main__":
    main()
