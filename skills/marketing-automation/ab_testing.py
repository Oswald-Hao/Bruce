#!/usr/bin/env python3
"""
自动化营销 - A/B测试系统
Marketing Automation - A/B Testing System
"""

import json
import uuid
import math
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from pathlib import Path
from enum import Enum


class MetricType(Enum):
    """指标类型"""
    OPEN_RATE = "open_rate"
    CLICK_RATE = "click_rate"
    CONVERSION_RATE = "conversion_rate"
    REVENUE = "revenue"
    CUSTOM = "custom"


class TestStatus(Enum):
    """测试状态"""
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    PAUSED = "paused"


@dataclass
class Variant:
    """测试变体"""
    id: str
    name: str
    config: Dict  # 变体配置
    traffic_allocation: float = 0.5  # 流量分配（0-1）
    metrics: Dict = field(default_factory=dict)
    sample_size: int = 0

    def __post_init__(self):
        if not self.metrics:
            self.metrics = {
                "exposures": 0,
                "conversions": 0,
                "value": 0
            }


@dataclass
class ABTest:
    """A/B测试"""
    id: str
    name: str
    description: str = ""
    type: str = "custom"  # email_subject, email_content, send_time, landing_page, custom
    status: TestStatus = TestStatus.DRAFT
    variants: List[Variant] = field(default_factory=list)
    primary_metric: MetricType = MetricType.CONVERSION_RATE
    created_at: str = None
    started_at: str = None
    completed_at: str = None
    min_sample_size: int = 100
    confidence_level: float = 0.95
    result: Dict = field(default_factory=dict)
    winner: str = None  # 获胜变体ID

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


@dataclass
class ABTestParticipant:
    """测试参与者"""
    id: str
    test_id: str
    variant_id: str
    user_id: str
    assigned_at: str
    converted: bool = False
    value: float = 0.0


class ABTesting:
    """A/B测试系统"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.tests = {}
        self.participants = {}

        self._load_data()

    def _load_data(self):
        """加载数据"""
        tests_file = self.data_dir / "ab_tests.json"
        if tests_file.exists():
            with open(tests_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for id_, test_data in data.items():
                    # 重建变体对象
                    variants_data = test_data.get("variants", [])
                    variants = []
                    for variant_data in variants_data:
                        variants.append(Variant(**variant_data))

                    test_data["variants"] = variants
                    test_data["status"] = TestStatus(test_data.get("status", "draft"))
                    test_data["primary_metric"] = MetricType(test_data.get("primary_metric", "conversion_rate"))

                    self.tests[id_] = ABTest(**test_data)

        participants_file = self.data_dir / "ab_test_participants.json"
        if participants_file.exists():
            with open(participants_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for id_, participant_data in data.items():
                    self.participants[id_] = ABTestParticipant(**participant_data)

    def _save_data(self):
        """保存数据"""
        tests_file = self.data_dir / "ab_tests.json"
        tests_data = {}
        for id_, test in self.tests.items():
            test_dict = asdict(test)
            test_dict["status"] = test.status.value
            test_dict["primary_metric"] = test.primary_metric.value
            tests_data[id_] = test_dict

        with open(tests_file, 'w', encoding='utf-8') as f:
            json.dump(tests_data, f, indent=2, ensure_ascii=False)

        participants_file = self.data_dir / "ab_test_participants.json"
        participants_data = {id_: asdict(p) for id_, p in self.participants.items()}
        with open(participants_file, 'w', encoding='utf-8') as f:
            json.dump(participants_data, f, indent=2, ensure_ascii=False)

    # ========== 测试管理 ==========

    def create_test(
        self,
        name: str,
        test_type: str,
        variants: List[Dict],
        primary_metric: MetricType = MetricType.CONVERSION_RATE,
        min_sample_size: int = 100
    ) -> ABTest:
        """创建A/B测试"""
        test_id = str(uuid.uuid4())

        variant_objs = []
        total_allocation = 0

        for i, variant_config in enumerate(variants):
            allocation = variant_config.get("traffic_allocation", 1.0 / len(variants))
            variant_objs.append(Variant(
                id=str(uuid.uuid4()),
                name=variant_config.get("name", f"Variant {i+1}"),
                config=variant_config.get("config", {}),
                traffic_allocation=allocation
            ))
            total_allocation += allocation

        # 归一化流量分配
        for variant in variant_objs:
            variant.traffic_allocation = variant.traffic_allocation / total_allocation

        test = ABTest(
            id=test_id,
            name=name,
            type=test_type,
            variants=variant_objs,
            primary_metric=primary_metric,
            min_sample_size=min_sample_size
        )

        self.tests[test_id] = test
        self._save_data()

        return test

    def get_test(self, test_id: str) -> Optional[ABTest]:
        """获取测试"""
        return self.tests.get(test_id)

    def list_tests(self, status: TestStatus = None) -> List[ABTest]:
        """列出测试"""
        tests = list(self.tests.values())

        if status:
            tests = [t for t in tests if t.status == status]

        return tests

    def start_test(self, test_id: str) -> bool:
        """启动测试"""
        test = self.tests.get(test_id)
        if test and test.status in [TestStatus.DRAFT, TestStatus.PAUSED]:
            if test.status == TestStatus.DRAFT:
                test.started_at = datetime.now().isoformat()
            test.status = TestStatus.RUNNING
            self._save_data()
            return True
        return False

    def pause_test(self, test_id: str) -> bool:
        """暂停测试"""
        test = self.tests.get(test_id)
        if test and test.status == TestStatus.RUNNING:
            test.status = TestStatus.PAUSED
            self._save_data()
            return True
        return False

    def complete_test(self, test_id: str) -> bool:
        """完成测试"""
        test = self.tests.get(test_id)
        if test and test.status in [TestStatus.RUNNING, TestStatus.PAUSED]:
            test.status = TestStatus.COMPLETED
            test.completed_at = datetime.now().isoformat()
            self._analyze_test(test_id)
            self._save_data()
            return True
        return False

    # ========== 参与者分配 ==========

    def assign_variant(self, test_id: str, user_id: str, force_variant_id: str = None) -> Optional[Variant]:
        """为用户分配测试变体"""
        test = self.tests.get(test_id)
        if not test or test.status != TestStatus.RUNNING:
            return None

        # 检查用户是否已经参与过该测试
        for participant in self.participants.values():
            if participant.test_id == test_id and participant.user_id == user_id:
                # 返回已分配的变体
                for variant in test.variants:
                    if variant.id == participant.variant_id:
                        return variant
                return None

        # 强制指定变体
        if force_variant_id:
            for variant in test.variants:
                if variant.id == force_variant_id:
                    self._create_participant(test_id, user_id, variant.id)
                    return variant
            return None

        # 根据流量分配随机选择变体
        import random
        rand = random.random()
        cumulative = 0.0

        for variant in test.variants:
            cumulative += variant.traffic_allocation
            if rand <= cumulative:
                self._create_participant(test_id, user_id, variant.id)
                return variant

        return None

    def _create_participant(self, test_id: str, user_id: str, variant_id: str):
        """创建参与者记录"""
        participant_id = str(uuid.uuid4())
        participant = ABTestParticipant(
            id=participant_id,
            test_id=test_id,
            variant_id=variant_id,
            user_id=user_id,
            assigned_at=datetime.now().isoformat()
        )

        self.participants[participant_id] = participant

        # 更新变体指标
        test = self.tests.get(test_id)
        if test:
            for variant in test.variants:
                if variant.id == variant_id:
                    variant.metrics["exposures"] += 1
                    variant.sample_size += 1
                    break

        self._save_data()

    # ========== 转化追踪 ==========

    def track_conversion(self, test_id: str, user_id: str, value: float = 0.0) -> bool:
        """追踪转化"""
        test = self.tests.get(test_id)
        if not test:
            return False

        # 查找用户参与的记录
        for participant in self.participants.values():
            if participant.test_id == test_id and participant.user_id == user_id:
                if not participant.converted:
                    participant.converted = True
                    participant.value = value

                    # 更新变体指标
                    for variant in test.variants:
                        if variant.id == participant.variant_id:
                            variant.metrics["conversions"] += 1
                            variant.metrics["value"] += value
                            break

                    self._save_data()
                    return True

        return False

    # ========== 统计分析 ==========

    def get_test_results(self, test_id: str) -> Dict:
        """获取测试结果"""
        test = self.tests.get(test_id)
        if not test:
            return {}

        results = {
            "test_id": test_id,
            "name": test.name,
            "status": test.status.value,
            "variants": [],
            "winner": test.winner
        }

        for variant in test.variants:
            variant_result = {
                "id": variant.id,
                "name": variant.name,
                "exposures": variant.metrics.get("exposures", 0),
                "conversions": variant.metrics.get("conversions", 0),
                "value": variant.metrics.get("value", 0),
                "conversion_rate": 0,
                "avg_value": 0
            }

            if variant.metrics.get("exposures", 0) > 0:
                variant_result["conversion_rate"] = variant.metrics.get("conversions", 0) / variant.metrics.get("exposures", 0)

            if variant.metrics.get("conversions", 0) > 0:
                variant_result["avg_value"] = variant.metrics.get("value", 0) / variant.metrics.get("conversions", 0)

            results["variants"].append(variant_result)

        # 计算相对提升
        if len(results["variants"]) >= 2:
            baseline = results["variants"][0]
            for variant in results["variants"][1:]:
                if baseline["conversion_rate"] > 0:
                    variant["relative_improvement"] = (
                        (variant["conversion_rate"] - baseline["conversion_rate"]) /
                        baseline["conversion_rate"] * 100
                    )
                else:
                    variant["relative_improvement"] = 0

        return results

    def _calculate_statistical_significance(
        self,
        control_conversions: int,
        control_exposures: int,
        treatment_conversions: int,
        treatment_exposures: int
    ) -> float:
        """计算统计显著性（Z-test）"""
        # 转化率
        p1 = control_conversions / control_exposures if control_exposures > 0 else 0
        p2 = treatment_conversions / treatment_exposures if treatment_exposures > 0 else 0

        # 合并转化率
        p = (control_conversions + treatment_conversions) / (control_exposures + treatment_exposures)

        # 标准误差
        se = math.sqrt(p * (1 - p) * (1/control_exposures + 1/treatment_exposures))

        if se == 0:
            return 0

        # Z分数
        z = (p2 - p1) / se

        # P值（双尾测试）
        p_value = 2 * (1 - self._normal_cdf(abs(z)))

        return p_value

    def _normal_cdf(self, x: float) -> float:
        """标准正态分布累积分布函数"""
        # 近似计算
        return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

    def _analyze_test(self, test_id: str):
        """分析测试结果"""
        test = self.tests.get(test_id)
        if not test or len(test.variants) < 2:
            return

        # 使用对照组（第一个变体）作为基准
        control = test.variants[0]
        best_variant = control
        best_p_value = 1.0

        for variant in test.variants[1:]:
            p_value = self._calculate_statistical_significance(
                control.metrics.get("conversions", 0),
                control.metrics.get("exposures", 0),
                variant.metrics.get("conversions", 0),
                variant.metrics.get("exposures", 0)
            )

            # 如果P值小于0.05，说明结果具有统计显著性
            if p_value < 0.05 and p_value < best_p_value:
                best_p_value = p_value
                best_variant = variant

        # 检查是否达到最小样本量
        all_reached_min = all(v.sample_size >= test.min_sample_size for v in test.variants)

        if all_reached_min and best_p_value < 0.05:
            test.winner = best_variant.id

        test.result = {
            "best_variant_id": best_variant.id,
            "p_value": best_p_value,
            "statistically_significant": best_p_value < 0.05,
            "min_sample_size_reached": all_reached_min,
            "analyzed_at": datetime.now().isoformat()
        }

    # ========== 快捷方法 ==========

    def create_email_subject_test(
        self,
        name: str,
        subjects: List[str],
        min_sample_size: int = 100
    ) -> ABTest:
        """创建邮件主题测试"""
        variants = [
            {"name": f"Subject {i+1}", "config": {"subject": subject}}
            for i, subject in enumerate(subjects)
        ]

        return self.create_test(
            name=name,
            test_type="email_subject",
            variants=variants,
            primary_metric=MetricType.OPEN_RATE,
            min_sample_size=min_sample_size
        )

    def create_email_content_test(
        self,
        name: str,
        contents: List[Dict],
        min_sample_size: int = 100
    ) -> ABTest:
        """创建邮件内容测试"""
        variants = [
            {"name": f"Content {i+1}", "config": content}
            for i, content in enumerate(contents)
        ]

        return self.create_test(
            name=name,
            test_type="email_content",
            variants=variants,
            primary_metric=MetricType.CONVERSION_RATE,
            min_sample_size=min_sample_size
        )


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="A/B测试系统")
    subparsers = parser.add_subparsers(dest="command", help="命令")

    # 创建测试
    create_parser = subparsers.add_parser("create", help="创建测试")
    create_parser.add_argument("--name", required=True, help="测试名称")
    create_parser.add_argument("--type", required=True, help="测试类型")
    create_parser.add_argument("--variants", required=True, nargs='+', help="变体名称列表")

    # 启动测试
    start_parser = subparsers.add_parser("start", help="启动测试")
    start_parser.add_argument("--test", required=True, help="测试ID或名称")

    # 完成测试
    complete_parser = subparsers.add_parser("complete", help="完成测试")
    complete_parser.add_argument("--test", required=True, help="测试ID或名称")

    # 分配变体
    assign_parser = subparsers.add_parser("assign", help="分配变体")
    assign_parser.add_argument("--test", required=True, help="测试ID或名称")
    assign_parser.add_argument("--user", required=True, help="用户ID")

    # 追踪转化
    convert_parser = subparsers.add_parser("convert", help="追踪转化")
    convert_parser.add_argument("--test", required=True, help="测试ID或名称")
    convert_parser.add_argument("--user", required=True, help="用户ID")
    convert_parser.add_argument("--value", type=float, default=0.0, help="转化价值")

    # 查看结果
    results_parser = subparsers.add_parser("results", help="查看结果")
    results_parser.add_argument("--test", required=True, help="测试ID或名称")

    # 列出测试
    list_parser = subparsers.add_parser("list", help="列出测试")

    args = parser.parse_args()

    ab_testing = ABTesting()

    if args.command == "create":
        variants = [{"name": name} for name in args.variants]
        test = ab_testing.create_test(args.name, args.type, variants)
        print(f"✅ A/B测试已创建: {test.id}")
        print(f"   名称: {test.name}")
        print(f"   类型: {test.type}")
        print(f"   变体: {len(test.variants)}")

    elif args.command == "start":
        test = None
        for t in ab_testing.tests.values():
            if t.id == args.test or t.name == args.test:
                test = t
                break

        if not test:
            print(f"❌ 未找到测试: {args.test}")
            return

        if ab_testing.start_test(test.id):
            print(f"✅ 测试已启动: {test.name}")
        else:
            print(f"❌ 启动失败")

    elif args.command == "complete":
        test = None
        for t in ab_testing.tests.values():
            if t.id == args.test or t.name == args.test:
                test = t
                break

        if not test:
            print(f"❌ 未找到测试: {args.test}")
            return

        if ab_testing.complete_test(test.id):
            print(f"✅ 测试已完成: {test.name}")
            results = ab_testing.get_test_results(test.id)
            print(f"   获胜者: {results.get('winner', 'N/A')}")
        else:
            print(f"❌ 完成失败")

    elif args.command == "assign":
        test = None
        for t in ab_testing.tests.values():
            if t.id == args.test or t.name == args.test:
                test = t
                break

        if not test:
            print(f"❌ 未找到测试: {args.test}")
            return

        variant = ab_testing.assign_variant(test.id, args.user)
        if variant:
            print(f"✅ 已分配变体: {variant.name}")
        else:
            print(f"❌ 分配失败")

    elif args.command == "convert":
        test = None
        for t in ab_testing.tests.values():
            if t.id == args.test or t.name == args.test:
                test = t
                break

        if not test:
            print(f"❌ 未找到测试: {args.test}")
            return

        if ab_testing.track_conversion(test.id, args.user, args.value):
            print(f"✅ 已记录转化")
        else:
            print(f"❌ 记录失败")

    elif args.command == "results":
        test = None
        for t in ab_testing.tests.values():
            if t.id == args.test or t.name == args.test:
                test = t
                break

        if not test:
            print(f"❌ 未找到测试: {args.test}")
            return

        results = ab_testing.get_test_results(test.id)
        print(f"A/B测试结果: {results['name']}")
        print(f"  状态: {results['status']}")
        print(f"  获胜者: {results.get('winner', 'N/A')}")
        print(f"\n  变体对比:")
        for variant in results['variants']:
            print(f"    {variant['name']}:")
            print(f"      曝光: {variant['exposures']}")
            print(f"      转化: {variant['conversions']}")
            print(f"      转化率: {variant['conversion_rate']:.2%}")
            if 'relative_improvement' in variant:
                print(f"      相对提升: {variant['relative_improvement']:.1f}%")

    elif args.command == "list":
        tests = ab_testing.list_tests()
        print(f"A/B测试列表 ({len(tests)}):")
        for t in tests:
            print(f"  [{t.id[:8]}] {t.name} ({t.type}, {t.status.value})")
            print(f"    变体: {len(t.variants)}")


if __name__ == "__main__":
    main()
