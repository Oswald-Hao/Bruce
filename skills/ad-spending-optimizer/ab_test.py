#!/usr/bin/env python3
"""
广告A/B测试器
自动化测试不同广告创意的效果
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


class TestStatus(Enum):
    """测试状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TestVariant:
    """测试变体"""
    variant_id: str
    name: str
    creative: str
    budget: float
    impressions: int
    clicks: int
    conversions: int
    ctr: float
    cpc: float
    cpa: float
    roi: float


@dataclass
class ABTest:
    """A/B测试"""
    test_id: str
    platform: str
    name: str
    variants: List[TestVariant]
    status: TestStatus
    start_date: datetime
    end_date: Optional[datetime]
    duration: int  # 测试天数
    winner: Optional[str]  # 获胜变体ID


@dataclass
class TestResult:
    """测试结果"""
    variant_a: TestVariant
    variant_b: TestVariant
    winner: str
    significance: float
    recommendation: str


class ABTester:
    """A/B测试器"""

    def __init__(self, platform: str):
        """
        初始化A/B测试器

        Args:
            platform: 广告平台
        """
        self.platform = platform
        self.tests: List[ABTest] = []

    def create_test(
        self,
        name: str,
        creative_a: str,
        creative_b: str,
        budget: float,
        duration: int = 7
    ) -> ABTest:
        """
        创建A/B测试

        Args:
            name: 测试名称
            creative_a: 变体A创意素材
            creative_b: 变体B创意素材
            budget: 总预算
            duration: 测试天数

        Returns:
            A/B测试对象
        """
        import uuid

        test_id = f"ab_{uuid.uuid4().hex[:8]}"

        # 创建变体
        variant_a = TestVariant(
            variant_id=f"{test_id}_a",
            name="变体A",
            creative=creative_a,
            budget=budget / 2,
            impressions=0,
            clicks=0,
            conversions=0,
            ctr=0,
            cpc=0,
            cpa=0,
            roi=0
        )

        variant_b = TestVariant(
            variant_id=f"{test_id}_b",
            name="变体B",
            creative=creative_b,
            budget=budget / 2,
            impressions=0,
            clicks=0,
            conversions=0,
            ctr=0,
            cpc=0,
            cpa=0,
            roi=0
        )

        test = ABTest(
            test_id=test_id,
            platform=self.platform,
            name=name,
            variants=[variant_a, variant_b],
            status=TestStatus.PENDING,
            start_date=datetime.now(),
            end_date=None,
            duration=duration,
            winner=None
        )

        self.tests.append(test)
        logger.info(f"创建A/B测试: {name} ({test_id})")
        return test

    def run_test(self, test_id: str) -> bool:
        """
        运行A/B测试

        Args:
            test_id: 测试ID

        Returns:
            是否运行成功
        """
        test = self._find_test(test_id)
        if not test:
            logger.error(f"未找到测试: {test_id}")
            return False

        try:
            test.status = TestStatus.RUNNING

            # 模拟运行测试
            # 实际使用时调用各平台API创建广告活动
            for variant in test.variants:
                # 模拟数据
                spent = variant.budget * random.uniform(0.7, 0.95)
                impressions = random.randint(50000, 100000)
                clicks = random.randint(1000, 3000)
                conversions = random.randint(20, 100)

                variant.impressions = impressions
                variant.clicks = clicks
                variant.conversions = conversions
                variant.ctr = (clicks / impressions * 100) if impressions > 0 else 0
                variant.cpc = (spent / clicks) if clicks > 0 else 0
                variant.cpa = (spent / conversions) if conversions > 0 else 0
                variant.roi = ((conversions * 300) - spent) / spent * 100 if spent > 0 else 0

            # 计算测试结果
            result = self.analyze_result(test)
            if result:
                test.winner = result.winner
                test.status = TestStatus.COMPLETED
                test.end_date = datetime.now()

                logger.info(f"测试完成: {test_id}, 获胜者: {result.winner}")
                return True

            return False

        except Exception as e:
            logger.error(f"运行测试失败: {e}")
            test.status = TestStatus.FAILED
            return False

    def analyze_result(self, test: ABTest) -> Optional[TestResult]:
        """
        分析测试结果

        Args:
            test: A/B测试对象

        Returns:
            测试结果
        """
        if len(test.variants) != 2:
            logger.error("测试必须有2个变体")
            return None

        variant_a = test.variants[0]
        variant_b = test.variants[1]

        # 比较CPA（越低越好）
        if variant_a.cpa < variant_b.cpa:
            winner = "A"
            improvement = ((variant_b.cpa - variant_a.cpa) / variant_b.cpa * 100)
            significance = min(improvement * 0.1, 99.9)
            recommendation = f"变体A的CPA更低，推荐使用。预计CPA降低{improvement:.1f}%"
        elif variant_b.cpa < variant_a.cpa:
            winner = "B"
            improvement = ((variant_a.cpa - variant_b.cpa) / variant_a.cpa * 100)
            significance = min(improvement * 0.1, 99.9)
            recommendation = f"变体B的CPA更低，推荐使用。预计CPA降低{improvement:.1f}%"
        else:
            winner = "Tie"
            significance = 0
            recommendation = "两个变体效果相当，可以继续测试或根据其他指标选择"

        return TestResult(
            variant_a=variant_a,
            variant_b=variant_b,
            winner=winner,
            significance=round(significance, 2),
            recommendation=recommendation
        )

    def _find_test(self, test_id: str) -> Optional[ABTest]:
        """查找测试"""
        for test in self.tests:
            if test.test_id == test_id:
                return test
        return None

    def generate_report(self, test_id: str) -> Optional[str]:
        """
        生成测试报告

        Args:
            test_id: 测试ID

        Returns:
            报告文本
        """
        test = self._find_test(test_id)
        if not test:
            logger.error(f"未找到测试: {test_id}")
            return None

        result = self.analyze_result(test)
        if not result:
            return None

        report = []
        report.append("# A/B测试报告\n")
        report.append(f"测试ID: {test.test_id}")
        report.append(f"测试名称: {test.name}")
        report.append(f"平台: {test.platform}")
        report.append(f"开始时间: {test.start_date.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"结束时间: {test.end_date.strftime('%Y-%m-%d %H:%M:%S') if test.end_date else '进行中'}")
        report.append(f"状态: {test.status.value}")
        report.append(f"获胜者: {result.winner}\n")

        report.append("## 变体对比\n")

        # 变体A
        report.append(f"### 变体A: {result.variant_a.name}")
        report.append(f"- 创意素材: {result.variant_a.creative}")
        report.append(f"- 预算: {result.variant_a.budget}")
        report.append(f"- 展现量: {result.variant_a.impressions}")
        report.append(f"- 点击数: {result.variant_a.clicks}")
        report.append(f"- 转化数: {result.variant_a.conversions}")
        report.append(f"- CTR: {result.variant_a.ctr:.2f}%")
        report.append(f"- CPC: {result.variant_a.cpc:.2f}")
        report.append(f"- CPA: {result.variant_a.cpa:.2f}")
        report.append(f"- ROI: {result.variant_a.roi:.2f}%\n")

        # 变体B
        report.append(f"### 变体B: {result.variant_b.name}")
        report.append(f"- 创意素材: {result.variant_b.creative}")
        report.append(f"- 预算: {result.variant_b.budget}")
        report.append(f"- 展现量: {result.variant_b.impressions}")
        report.append(f"- 点击数: {result.variant_b.clicks}")
        report.append(f"- 转化数: {result.variant_b.conversions}")
        report.append(f"- CTR: {result.variant_b.ctr:.2f}%")
        report.append(f"- CPC: {result.variant_b.cpc:.2f}")
        report.append(f"- CPA: {result.variant_b.cpa:.2f}")
        report.append(f"- ROI: {result.variant_b.roi:.2f}%\n")

        report.append("## 结论\n")
        report.append(f"- 获胜者: {result.winner}")
        report.append(f"- 显著性: {result.significance}%")
        report.append(f"- 建议: {result.recommendation}")

        return "\n".join(report)

    def run_test_series(
        self,
        tests: List[Dict],
        concurrent: bool = False
    ) -> List[TestResult]:
        """
        批量运行A/B测试

        Args:
            tests: 测试配置列表
            concurrent: 是否并发执行

        Returns:
            测试结果列表
        """
        results = []

        for test_config in tests:
            test = self.create_test(
                name=test_config.get("name", ""),
                creative_a=test_config["creative_a"],
                creative_b=test_config["creative_b"],
                budget=test_config["budget"],
                duration=test_config.get("duration", 7)
            )

            if self.run_test(test.test_id):
                result = self.analyze_result(test)
                if result:
                    results.append(result)

        return results


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="广告A/B测试器")
    parser.add_argument("--platform", required=True, choices=["baidu", "tencent", "google", "facebook"],
                        help="广告平台")
    parser.add_argument("--creative_a", required=True, help="变体A创意素材")
    parser.add_argument("--creative_b", required=True, help="变体B创意素材")
    parser.add_argument("--budget", type=float, required=True, help="测试预算")
    parser.add_argument("--duration", type=int, default=7, help="测试天数")
    parser.add_argument("--output", help="输出文件路径")

    args = parser.parse_args()

    # 创建测试器
    tester = ABTester(args.platform)

    # 创建并运行测试
    test = tester.create_test(
        name=f"A/B测试_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        creative_a=args.creative_a,
        creative_b=args.creative_b,
        budget=args.budget,
        duration=args.duration
    )

    # 运行测试
    if tester.run_test(test.test_id):
        # 生成报告
        report = tester.generate_report(test.test_id)

        print(report)

        # 保存报告
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\n报告已保存到: {args.output}")
    else:
        logger.error("测试失败")


if __name__ == "__main__":
    main()
