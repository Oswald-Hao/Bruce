#!/usr/bin/env python3
"""
广告投放优化系统 - 数据分析模块
Ad Optimization System - Data Analyzer

主要功能：
- 广告数据分析
- 趋势分析
- 对比分析
- 洞察发现
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import statistics


class AdDataAnalyzer:
    """广告数据分析器"""

    def __init__(self):
        """初始化数据分析器"""
        self.data = {}

    def load_data(self, data: Dict[str, Any]) -> None:
        """
        加载数据

        Args:
            data: 广告数据字典
        """
        self.data = data

    def calculate_metrics(self, data: Dict[str, Any]) -> Dict[str, float]:
        """
        计算核心指标

        Args:
            data: 广告数据

        Returns:
            指标字典
        """
        metrics = {
            "ctr": 0.0,  # 点击率
            "cpc": 0.0,  # 每次点击成本
            "cpm": 0.0,  # 千次展示成本
            "cvr": 0.0,  # 转化率
            "cpa": 0.0,  # 每次转化成本
            "roi": 0.0,  # 投资回报率
            "roas": 0.0  # 广告支出回报率
        }

        # 计算CTR
        if data.get("impressions", 0) > 0:
            metrics["ctr"] = (data.get("clicks", 0) / data["impressions"]) * 100

        # 计算CPC
        if data.get("clicks", 0) > 0:
            metrics["cpc"] = data.get("spend", 0) / data["clicks"]

        # 计算CPM
        if data.get("impressions", 0) > 0:
            metrics["cpm"] = (data.get("spend", 0) / data["impressions"]) * 1000

        # 计算CVR
        if data.get("clicks", 0) > 0:
            metrics["cvr"] = (data.get("conversions", 0) / data["clicks"]) * 100

        # 计算CPA
        if data.get("conversions", 0) > 0:
            metrics["cpa"] = data.get("spend", 0) / data["conversions"]

        # 计算ROI
        if data.get("spend", 0) > 0:
            revenue = data.get("revenue", 0)
            metrics["roi"] = ((revenue - data["spend"]) / data["spend"]) * 100

        # 计算ROAS
        if data.get("spend", 0) > 0:
            metrics["roas"] = data.get("revenue", 0) / data["spend"]

        return metrics

    def compare_ads(self, ads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        对比多个广告

        Args:
            ads: 广告列表

        Returns:
            对比结果
        """
        # 计算每个广告的指标
        ad_metrics = []
        for ad in ads:
            metrics = self.calculate_metrics(ad)
            ad_metrics.append({
                "ad_id": ad.get("id", "unknown"),
                "name": ad.get("name", "unknown"),
                **metrics
            })

        # 计算统计数据
        ctr_values = [m["ctr"] for m in ad_metrics]
        cvr_values = [m["cvr"] for m in ad_metrics]
        roi_values = [m["roi"] for m in ad_metrics]

        stats = {
            "ctr": {
                "avg": statistics.mean(ctr_values) if ctr_values else 0,
                "max": max(ctr_values) if ctr_values else 0,
                "min": min(ctr_values) if ctr_values else 0
            },
            "cvr": {
                "avg": statistics.mean(cvr_values) if cvr_values else 0,
                "max": max(cvr_values) if cvr_values else 0,
                "min": min(cvr_values) if cvr_values else 0
            },
            "roi": {
                "avg": statistics.mean(roi_values) if roi_values else 0,
                "max": max(roi_values) if roi_values else 0,
                "min": min(roi_values) if roi_values else 0
            }
        }

        # 识别最佳和最差广告
        best_by_ctr = max(ad_metrics, key=lambda x: x["ctr"]) if ad_metrics else None
        best_by_cvr = max(ad_metrics, key=lambda x: x["cvr"]) if ad_metrics else None
        best_by_roi = max(ad_metrics, key=lambda x: x["roi"]) if ad_metrics else None

        worst_by_roi = min(ad_metrics, key=lambda x: x["roi"]) if ad_metrics else None

        return {
            "ad_metrics": ad_metrics,
            "statistics": stats,
            "best": {
                "by_ctr": best_by_ctr,
                "by_cvr": best_by_cvr,
                "by_roi": best_by_roi
            },
            "worst": {
                "by_roi": worst_by_roi
            },
            "recommendations": self._generate_comparison_recommendations(ad_metrics)
        }

    def analyze_trend(self, daily_data: List[Dict[str, Any]], metric: str = "ctr") -> Dict[str, Any]:
        """
        分析趋势

        Args:
            daily_data: 每日数据列表
            metric: 分析的指标

        Returns:
            趋势分析结果
        """
        # 提取指标值
        values = [d.get(metric, 0) for d in daily_data]

        if not values:
            return {"error": "没有数据"}

        # 计算趋势
        if len(values) >= 2:
            first_half = values[:len(values)//2]
            second_half = values[len(values)//2:]

            avg_first = statistics.mean(first_half) if first_half else 0
            avg_second = statistics.mean(second_half) if second_half else 0

            if avg_second > avg_first:
                trend = "上升"
                change_rate = ((avg_second - avg_first) / avg_first) * 100 if avg_first > 0 else 0
            elif avg_second < avg_first:
                trend = "下降"
                change_rate = ((avg_second - avg_first) / avg_first) * 100 if avg_first > 0 else 0
            else:
                trend = "稳定"
                change_rate = 0
        else:
            trend = "数据不足"
            change_rate = 0

        return {
            "metric": metric,
            "values": values,
            "average": statistics.mean(values),
            "trend": trend,
            "change_rate": change_rate,
            "recommendation": self._generate_trend_recommendation(trend, metric, change_rate)
        }

    def detect_anomalies(self, data: List[Dict[str, Any]], metric: str = "ctr", threshold: float = 2.0) -> List[Dict[str, Any]]:
        """
        检测异常值

        Args:
            data: 数据列表
            metric: 检测的指标
            threshold: 标准差倍数阈值

        Returns:
            异常值列表
        """
        # 提取指标值
        values = [d.get(metric, 0) for d in data]

        if len(values) < 3:
            return []

        # 计算平均值和标准差
        mean = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0

        # 检测异常值
        anomalies = []
        for i, d in enumerate(data):
            value = d.get(metric, 0)
            if std_dev > 0 and abs(value - mean) > threshold * std_dev:
                anomalies.append({
                    "index": i,
                    "date": d.get("date", "unknown"),
                    "value": value,
                    "expected_range": [mean - threshold * std_dev, mean + threshold * std_dev],
                    "deviation": abs(value - mean) / std_dev if std_dev > 0 else 0,
                    "type": "high" if value > mean else "low"
                })

        return anomalies

    def segment_audience(self, data: List[Dict[str, Any]], segmentation_field: str = "age") -> Dict[str, Any]:
        """
        受众分群

        Args:
            data: 数据列表
            segmentation_field: 分群字段

        Returns:
            分群结果
        """
        # 按字段分群
        segments = {}
        for d in data:
            segment_value = d.get(segmentation_field, "unknown")
            if segment_value not in segments:
                segments[segment_value] = []
            segments[segment_value].append(d)

        # 计算每个分群的指标
        segment_analysis = {}
        for segment_value, segment_data in segments.items():
            total_spend = sum(d.get("spend", 0) for d in segment_data)
            total_clicks = sum(d.get("clicks", 0) for d in segment_data)
            total_conversions = sum(d.get("conversions", 0) for d in segment_data)
            total_impressions = sum(d.get("impressions", 0) for d in segment_data)

            metrics = {
                "count": len(segment_data),
                "spend": total_spend,
                "clicks": total_clicks,
                "conversions": total_conversions,
                "impressions": total_impressions
            }

            # 计算比率
            if total_impressions > 0:
                metrics["ctr"] = (total_clicks / total_impressions) * 100
            if total_clicks > 0:
                metrics["cvr"] = (total_conversions / total_clicks) * 100
            if total_conversions > 0:
                metrics["cpa"] = total_spend / total_conversions

            segment_analysis[segment_value] = metrics

        return {
            "segmentation_field": segmentation_field,
            "segments": segment_analysis,
            "best_segment": max(segment_analysis.items(), key=lambda x: x[1].get("conversions", 0)) if segment_analysis else None
        }

    def _generate_comparison_recommendations(self, ad_metrics: List[Dict[str, Any]]) -> List[str]:
        """生成对比建议"""
        recommendations = []

        # 基于ROI的建议
        roi_values = [m["roi"] for m in ad_metrics]
        avg_roi = statistics.mean(roi_values) if roi_values else 0

        low_roi_ads = [m for m in ad_metrics if m["roi"] < avg_roi * 0.5]
        if low_roi_ads:
            recommendations.append(f"暂停或优化{len(low_roi_ads)}个低ROI广告")

        high_roi_ads = [m for m in ad_metrics if m["roi"] > avg_roi * 1.5]
        if high_roi_ads:
            recommendations.append(f"增加对{len(high_roi_ads)}个高ROI广告的预算")

        # 基于CTR的建议
        ctr_values = [m["ctr"] for m in ad_metrics]
        avg_ctr = statistics.mean(ctr_values) if ctr_values else 0

        low_ctr_ads = [m for m in ad_metrics if m["ctr"] < avg_ctr * 0.5]
        if low_ctr_ads:
            recommendations.append(f"优化{len(low_ctr_ads)}个低CTR广告的创意")

        return recommendations

    def _generate_trend_recommendation(self, trend: str, metric: str, change_rate: float) -> str:
        """生成趋势建议"""
        if trend == "上升":
            if change_rate > 20:
                return f"{metric}呈显著上升趋势，建议保持当前策略"
            else:
                return f"{metric}稳步上升，可以考虑增加预算"
        elif trend == "下降":
            if change_rate < -20:
                return f"{metric}快速下降，建议立即检查并优化"
            else:
                return f"{metric}轻微下降，建议分析原因并调整"
        else:
            return f"{metric}保持稳定，可以考虑测试新的优化方案"

    def export_report(self, data: Dict[str, Any], filename: str = "report.json"):
        """
        导出报告

        Args:
            data: 报告数据
            filename: 文件名
        """
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"报告已导出到: {filename}")


def main():
    """主函数 - 演示使用"""
    print("=== 广告数据分析器 ===\n")

    analyzer = AdDataAnalyzer()

    # 示例数据
    ads = [
        {
            "id": "ad001",
            "name": "广告A",
            "impressions": 10000,
            "clicks": 200,
            "conversions": 10,
            "spend": 100,
            "revenue": 200
        },
        {
            "id": "ad002",
            "name": "广告B",
            "impressions": 8000,
            "clicks": 240,
            "conversions": 15,
            "spend": 120,
            "revenue": 300
        },
        {
            "id": "ad003",
            "name": "广告C",
            "impressions": 12000,
            "clicks": 180,
            "conversions": 8,
            "spend": 90,
            "revenue": 160
        }
    ]

    # 对比广告
    print("1. 对比广告...")
    comparison = analyzer.compare_ads(ads)
    print(f"   广告数量: {len(comparison['ad_metrics'])}")
    print(f"   平均CTR: {comparison['statistics']['ctr']['avg']:.2f}%")
    print(f"   平均ROI: {comparison['statistics']['roi']['avg']:.2f}%")
    if comparison['best']['by_roi']:
        print(f"   最佳ROI广告: {comparison['best']['by_roi']['name']}")
    print()

    # 分析趋势
    print("2. 分析趋势...")
    daily_data = [
        {"date": "2026-02-01", "ctr": 1.5},
        {"date": "2026-02-02", "ctr": 1.8},
        {"date": "2026-02-03", "ctr": 2.1},
        {"date": "2026-02-04", "ctr": 1.9},
        {"date": "2026-02-05", "ctr": 2.3}
    ]
    trend = analyzer.analyze_trend(daily_data, "ctr")
    print(f"   趋势: {trend['trend']}")
    print(f"   变化率: {trend['change_rate']:.2f}%")
    print(f"   建议: {trend['recommendation']}")
    print()

    print("=== 演示完成 ===")


if __name__ == "__main__":
    main()
