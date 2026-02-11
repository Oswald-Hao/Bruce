#!/usr/bin/env python3
"""
自动化营销 - 客户分群系统
Marketing Automation - Customer Segmentation
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict, field
from pathlib import Path
from enum import Enum


class SegmentType(Enum):
    """分群类型"""
    BEHAVIORAL = "behavioral"  # 行为分群
    DEMOGRAPHIC = "demographic"  # 属性分群
    RFM = "rfm"  # RFM价值分群
    CUSTOM = "custom"  # 自定义分群


@dataclass
class Segment:
    """客户分群"""
    id: str
    name: str
    description: str = ""
    type: SegmentType = SegmentType.CUSTOM
    conditions: Dict = field(default_factory=dict)
    customer_ids: List[str] = field(default_factory=list)
    created_at: str = None
    updated_at: str = None
    is_dynamic: bool = True  # 是否动态分群

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()


@dataclass
class CustomerRFM:
    """客户RFM数据"""
    recency: int  # 最近一次购买距今天数
    frequency: int  # 购买频率
    monetary: float  # 消费金额
    recency_score: int = 1  # R分数（1-5）
    frequency_score: int = 1  # F分数（1-5）
    monetary_score: int = 1  # M分数（1-5）
    rfm_segment: str = ""  # RFM分群（如"5-5-5"）
    customer_type: str = ""  # 客户类型


class CustomerSegmentation:
    """客户分群系统"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.segments = {}
        self.rfm_data = {}

        self._load_data()

    def _load_data(self):
        """加载数据"""
        segments_file = self.data_dir / "segments.json"
        if segments_file.exists():
            with open(segments_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for id_, segment_data in data.items():
                    segment_data["type"] = SegmentType(segment_data.get("type", "custom"))
                    self.segments[id_] = Segment(**segment_data)

        rfm_file = self.data_dir / "rfm_data.json"
        if rfm_file.exists():
            with open(rfm_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for id_, rfm_data in data.items():
                    self.rfm_data[id_] = CustomerRFM(**rfm_data)

    def _save_data(self):
        """保存数据"""
        segments_file = self.data_dir / "segments.json"
        segments_data = {}
        for id_, segment in self.segments.items():
            segment_dict = asdict(segment)
            segment_dict["type"] = segment.type.value
            segments_data[id_] = segment_dict

        with open(segments_file, 'w', encoding='utf-8') as f:
            json.dump(segments_data, f, indent=2, ensure_ascii=False)

        rfm_file = self.data_dir / "rfm_data.json"
        rfm_data = {id_: asdict(rfm) for id_, rfm in self.rfm_data.items()}
        with open(rfm_file, 'w', encoding='utf-8') as f:
            json.dump(rfm_data, f, indent=2, ensure_ascii=False)

    # ========== 分群管理 ==========

    def create_segment(
        self,
        name: str,
        segment_type: SegmentType,
        conditions: Dict = None,
        description: str = "",
        is_dynamic: bool = True
    ) -> Segment:
        """创建分群"""
        segment_id = str(uuid.uuid4())
        segment = Segment(
            id=segment_id,
            name=name,
            description=description,
            type=segment_type,
            conditions=conditions or {},
            is_dynamic=is_dynamic
        )

        self.segments[segment_id] = segment
        self._save_data()

        return segment

    def get_segment(self, segment_id: str) -> Optional[Segment]:
        """获取分群"""
        return self.segments.get(segment_id)

    def list_segments(self, segment_type: SegmentType = None) -> List[Segment]:
        """列出分群"""
        segments = list(self.segments.values())

        if segment_type:
            segments = [s for s in segments if s.type == segment_type]

        return segments

    def delete_segment(self, segment_id: str) -> bool:
        """删除分群"""
        if segment_id in self.segments:
            del self.segments[segment_id]
            self._save_data()
            return True
        return False

    # ========== RFM分群 ==========

    def calculate_rfm(self, customers: Dict) -> Dict[str, CustomerRFM]:
        """计算RFM数据"""
        rfm_results = {}

        # 计算每个客户的RFM
        for customer_id, customer in customers.items():
            recency = self._calculate_recency(customer)
            frequency = customer.order_count
            monetary = customer.total_spent

            rfm = CustomerRFM(
                recency=recency,
                frequency=frequency,
                monetary=monetary
            )

            rfm_results[customer_id] = rfm

        # 计算RFM分数
        if rfm_results:
            self._calculate_rfm_scores(rfm_results)

        # 更新数据
        self.rfm_data.update(rfm_results)
        self._save_data()

        return rfm_results

    def _calculate_recency(self, customer) -> int:
        """计算最近购买天数"""
        if customer.last_active:
            last_date = datetime.fromisoformat(customer.last_active)
            return (datetime.now() - last_date).days
        return 365  # 默认一年前

    def _calculate_rfm_scores(self, rfm_data: Dict[str, CustomerRFM]):
        """计算RFM分数"""
        # 提取R、F、M值
        r_values = [rfm.recency for rfm in rfm_data.values()]
        f_values = [rfm.frequency for rfm in rfm_data.values()]
        m_values = [rfm.monetary for rfm in rfm_data.values()]

        # 分位数（5个等级）
        r_quantiles = self._calculate_quantiles(r_values, reverse=True)  # R越小越好
        f_quantiles = self._calculate_quantiles(f_values)
        m_quantiles = self._calculate_quantiles(m_values)

        # 分数计算
        for rfm in rfm_data.values():
            rfm.recency_score = self._get_score(rfm.recency, r_quantiles, reverse=True)
            rfm.frequency_score = self._get_score(rfm.frequency, f_quantiles)
            rfm.monetary_score = self._get_score(rfm.monetary, m_quantiles)

            # RFM分群
            rfm.rfm_segment = f"{rfm.recency_score}-{rfm.frequency_score}-{rfm.monetary_score}"
            rfm.customer_type = self._get_customer_type(rfm)

    def _calculate_quantiles(self, values: List, reverse: bool = False) -> List[float]:
        """计算分位数"""
        if not values:
            return []

        sorted_values = sorted(values, reverse=reverse)
        n = len(sorted_values)
        quantiles = []

        for i in range(1, 6):  # 5个等级
            index = int(n * i / 5) - 1
            if index < 0:
                index = 0
            elif index >= n:
                index = n - 1
            quantiles.append(sorted_values[index])

        return quantiles

    def _get_score(self, value: float, quantiles: List[float], reverse: bool = False) -> int:
        """获取分数（1-5）"""
        if not quantiles:
            return 1

        for i, threshold in enumerate(quantiles):
            if reverse:
                if value <= threshold:
                    return 5 - i
            else:
                if value <= threshold:
                    return i + 1

        return 1

    def _get_customer_type(self, rfm: CustomerRFM) -> str:
        """获取客户类型"""
        r, f, m = rfm.recency_score, rfm.frequency_score, rfm.monetary_score

        if r >= 4 and f >= 4 and m >= 4:
            return "价值客户"  # 高价值、活跃、消费高
        elif r >= 4 and f <= 2:
            return "新客户"  # 新注册、购买少
        elif r <= 2 and f >= 4:
            return "流失风险"  # 曾经活跃、最近沉默
        elif r <= 2 and f <= 2 and m <= 2:
            return "低价值客户"  # 不活跃、消费低
        else:
            return "普通客户"

    def get_rfm_segments(self) -> Dict[str, List[str]]:
        """获取RFM分群"""
        segments = {
            "价值客户": [],
            "新客户": [],
            "流失风险": [],
            "低价值客户": [],
            "普通客户": []
        }

        for customer_id, rfm in self.rfm_data.items():
            customer_type = rfm.customer_type
            if customer_type in segments:
                segments[customer_type].append(customer_id)

        return segments

    # ========== 行为分群 ==========

    def create_behavioral_segment(
        self,
        name: str,
        conditions: Dict,
        description: str = ""
    ) -> Segment:
        """创建行为分群"""
        return self.create_segment(
            name=name,
            segment_type=SegmentType.BEHAVIORAL,
            conditions=conditions,
            description=description,
            is_dynamic=True
        )

    def update_behavioral_segments(self, customers: Dict):
        """更新行为分群"""
        for segment in self.segments.values():
            if segment.type == SegmentType.BEHAVIORAL and segment.is_dynamic:
                matched_customers = self._match_behavioral_conditions(
                    customers,
                    segment.conditions
                )
                segment.customer_ids = matched_customers
                segment.updated_at = datetime.now().isoformat()

        self._save_data()

    def _match_behavioral_conditions(self, customers: Dict, conditions: Dict) -> List[str]:
        """匹配行为条件"""
        matched_ids = []

        for customer_id, customer in customers.items():
            if self._evaluate_conditions(customer, conditions):
                matched_ids.append(customer_id)

        return matched_ids

    def _evaluate_conditions(self, customer, conditions: Dict) -> bool:
        """评估条件"""
        for key, condition in conditions.items():
            if key == "total_spent":
                operator = condition.get("op", ">=")
                value = condition.get("value", 0)
                if operator == ">=" and customer.total_spent < value:
                    return False
                elif operator == ">" and customer.total_spent <= value:
                    return False
                elif operator == "<=" and customer.total_spent > value:
                    return False
                elif operator == "<" and customer.total_spent >= value:
                    return False

            elif key == "order_count":
                operator = condition.get("op", ">=")
                value = condition.get("value", 0)
                if operator == ">=" and customer.order_count < value:
                    return False
                elif operator == ">" and customer.order_count <= value:
                    return False

            elif key == "tags":
                # 标签匹配
                required_tags = condition.get("value", [])
                if condition.get("op", "any") == "all":
                    if not all(tag in customer.tags for tag in required_tags):
                        return False
                else:
                    if not any(tag in customer.tags for tag in required_tags):
                        return False

            elif key == "days_since_last_active":
                operator = condition.get("op", "<=")
                value = condition.get("value", 0)
                days_since = self._calculate_recency(customer)
                if operator == "<=" and days_since > value:
                    return False
                elif operator == ">" and days_since <= value:
                    return False

        return True

    # ========== 分群查询 ==========

    def get_segment_customers(self, segment_id: str) -> List[str]:
        """获取分群中的客户"""
        segment = self.segments.get(segment_id)
        return segment.customer_ids if segment else []

    def get_customer_segments(self, customer_id: str) -> List[Segment]:
        """获取客户所属的所有分群"""
        return [
            segment for segment in self.segments.values()
            if customer_id in segment.customer_ids
        ]

    # ========== 快捷方法 ==========

    def create_default_segments(self):
        """创建默认分群"""
        segments_to_create = [
            {
                "name": "VIP客户",
                "type": SegmentType.BEHAVIORAL,
                "conditions": {"total_spent": {"op": ">=", "value": 1000}},
                "description": "累计消费超过1000元的客户"
            },
            {
                "name": "活跃用户",
                "type": SegmentType.BEHAVIORAL,
                "conditions": {"days_since_last_active": {"op": "<=", "value": 7}},
                "description": "最近7天活跃的用户"
            },
            {
                "name": "新注册用户",
                "type": SegmentType.BEHAVIORAL,
                "conditions": {"order_count": {"op": "==", "value": 0}},
                "description": "尚未下单的用户"
            }
        ]

        for seg_config in segments_to_create:
            if not any(s.name == seg_config["name"] for s in self.segments.values()):
                self.create_segment(**seg_config)

        self._save_data()


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="客户分群系统")
    subparsers = parser.add_subparsers(dest="command", help="命令")

    # 创建分群
    create_parser = subparsers.add_parser("create", help="创建分群")
    create_parser.add_argument("--name", required=True, help="分群名称")
    create_parser.add_argument("--segment-type", required=True, choices=["behavioral", "demographic", "rfm", "custom"], help="分群类型")
    create_parser.add_argument("--description", help="描述")
    create_parser.add_argument("--static", action="store_true", help="静态分群")

    # 列出分群
    list_parser = subparsers.add_parser("list", help="列出分群")
    list_parser.add_argument("--type", choices=["behavioral", "demographic", "rfm", "custom"], help="按类型筛选")

    # 删除分群
    delete_parser = subparsers.add_parser("delete", help="删除分群")
    delete_parser.add_argument("--segment", required=True, help="分群ID或名称")

    # 查看RFM分群
    subparsers.add_parser("rfm", help="查看RFM分群")

    # 创建默认分群
    subparsers.add_parser("create-default", help="创建默认分群")

    args = parser.parse_args()

    segmentation = CustomerSegmentation()

    if args.command == "create":
        segment = segmentation.create_segment(
            name=args.name,
            segment_type=SegmentType(args.type),
            description=args.description or "",
            is_dynamic=not args.static
        )
        print(f"✅ 分群已创建: {segment.id}")
        print(f"   名称: {segment.name}")
        print(f"   类型: {segment.type.value}")
        print(f"   动态: {segment.is_dynamic}")

    elif args.command == "list":
        segments = segmentation.list_segments(
            segment_type=SegmentType(args.type) if args.type else None
        )
        print(f"客户分群列表 ({len(segments)}):")
        for s in segments:
            print(f"  [{s.id[:8]}] {s.name} ({s.type.value}, {len(s.customer_ids)}客户)")

    elif args.command == "delete":
        segment = None
        for s in segmentation.segments.values():
            if s.id == args.segment or s.name == args.segment:
                segment = s
                break

        if not segment:
            print(f"❌ 未找到分群: {args.segment}")
            return

        if segmentation.delete_segment(segment.id):
            print(f"✅ 分群已删除: {segment.name}")
        else:
            print(f"❌ 删除失败")

    elif args.command == "rfm":
        rfm_segments = segmentation.get_rfm_segments()
        print("RFM分群结果:")
        for segment_type, customer_ids in rfm_segments.items():
            print(f"  {segment_type}: {len(customer_ids)}人")

    elif args.command == "create-default":
        segmentation.create_default_segments()
        print("✅ 默认分群已创建")


if __name__ == "__main__":
    main()
