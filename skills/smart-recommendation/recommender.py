#!/usr/bin/env python3
"""
智能推荐系统 - 推荐引擎核心
Smart Recommendation System - Recommender Core
"""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from pathlib import Path
from collections import defaultdict
import math


@dataclass
class User:
    """用户数据模型"""
    id: str
    name: str = ""
    email: str = ""
    tags: List[str] = field(default_factory=list)
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


@dataclass
class Item:
    """商品数据模型"""
    id: str
    name: str
    category: str = ""
    tags: List[str] = field(default_factory=list)
    features: Dict = field(default_factory=dict)
    price: float = 0.0
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


@dataclass
class Interaction:
    """用户交互数据"""
    id: str
    user_id: str
    item_id: str
    rating: float = 0.0
    action: str = "view"  # view, click, purchase, cart, favorite
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class Recommendation:
    """推荐结果"""
    item_id: str
    score: float
    reason: str = ""
    algorithm: str = ""


class SmartRecommender:
    """智能推荐系统核心引擎"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.users = {}
        self.items = {}
        self.interactions = []

        self._load_data()

    def _load_data(self):
        """加载数据"""
        # 加载用户
        users_file = self.data_dir / "users.json"
        if users_file.exists():
            with open(users_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for id_, user_data in data.items():
                    self.users[id_] = User(**user_data)

        # 加载商品
        items_file = self.data_dir / "items.json"
        if items_file.exists():
            with open(items_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for id_, item_data in data.items():
                    self.items[id_] = Item(**item_data)

        # 加载交互
        interactions_file = self.data_dir / "interactions.json"
        if interactions_file.exists():
            with open(interactions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.interactions = [Interaction(**item) for item in data]

    def _save_data(self):
        """保存数据"""
        # 保存用户
        users_file = self.data_dir / "users.json"
        users_data = {id_: asdict(user) for id_, user in self.users.items()}
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, indent=2, ensure_ascii=False)

        # 保存商品
        items_file = self.data_dir / "items.json"
        items_data = {id_: asdict(item) for id_, item in self.items.items()}
        with open(items_file, 'w', encoding='utf-8') as f:
            json.dump(items_data, f, indent=2, ensure_ascii=False)

        # 保存交互
        interactions_file = self.data_dir / "interactions.json"
        interactions_data = [asdict(interaction) for interaction in self.interactions]
        with open(interactions_file, 'w', encoding='utf-8') as f:
            json.dump(interactions_data, f, indent=2, ensure_ascii=False)

    # ========== 用户管理 ==========

    def add_user(self, user_id: str, name: str = "", email: str = "") -> User:
        """添加用户"""
        user = User(id=user_id, name=name, email=email)
        self.users[user_id] = user
        self._save_data()
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        """获取用户"""
        return self.users.get(user_id)

    def list_users(self, limit: int = None) -> List[User]:
        """列出用户"""
        users = list(self.users.values())
        if limit:
            users = users[:limit]
        return users

    # ========== 商品管理 ==========

    def add_item(
        self,
        item_id: str,
        name: str,
        category: str = "",
        tags: List[str] = None,
        price: float = 0.0,
        features: Dict = None
    ) -> Item:
        """添加商品"""
        item = Item(
            id=item_id,
            name=name,
            category=category,
            tags=tags or [],
            price=price,
            features=features or {}
        )
        self.items[item_id] = item
        self._save_data()
        return item

    def get_item(self, item_id: str) -> Optional[Item]:
        """获取商品"""
        return self.items.get(item_id)

    def list_items(self, category: str = None, limit: int = None) -> List[Item]:
        """列出商品"""
        items = list(self.items.values())

        if category:
            items = [item for item in items if item.category == category]

        if limit:
            items = items[:limit]

        return items

    # ========== 交互管理 ==========

    def add_interaction(
        self,
        user_id: str,
        item_id: str,
        rating: float = 0.0,
        action: str = "view"
    ) -> Optional[Interaction]:
        """添加交互"""
        interaction = Interaction(
            id=str(uuid.uuid4()),
            user_id=user_id,
            item_id=item_id,
            rating=rating,
            action=action
        )
        self.interactions.append(interaction)
        self._save_data()
        return interaction

    def get_user_interactions(self, user_id: str) -> List[Interaction]:
        """获取用户的所有交互"""
        return [i for i in self.interactions if i.user_id == user_id]

    def get_item_interactions(self, item_id: str) -> List[Interaction]:
        """获取商品的所有交互"""
        return [i for i in self.interactions if i.item_id == item_id]

    def get_user_items(self, user_id: str, action: str = None) -> List[str]:
        """获取用户交互过的商品ID列表"""
        interactions = self.get_user_interactions(user_id)
        if action:
            interactions = [i for i in interactions if i.action == action]
        return list(set(i.item_id for i in interactions))

    # ========== 协同过滤 ==========

    def _calculate_similarity(
        self,
        vector1: Dict[str, float],
        vector2: Dict[str, float],
        method: str = "cosine"
    ) -> float:
        """计算相似度"""
        if method == "cosine":
            # 余弦相似度
            common_items = set(vector1.keys()) & set(vector2.keys())
            if not common_items:
                return 0.0

            dot_product = sum(vector1[item] * vector2[item] for item in common_items)
            norm1 = math.sqrt(sum(v ** 2 for v in vector1.values()))
            norm2 = math.sqrt(sum(v ** 2 for v in vector2.values()))

            if norm1 == 0 or norm2 == 0:
                return 0.0

            return dot_product / (norm1 * norm2)

        elif method == "pearson":
            # 皮尔逊相关系数
            common_items = set(vector1.keys()) & set(vector2.keys())
            if len(common_items) < 2:
                return 0.0

            mean1 = sum(vector1[item] for item in common_items) / len(common_items)
            mean2 = sum(vector2[item] for item in common_items) / len(common_items)

            numerator = sum((vector1[item] - mean1) * (vector2[item] - mean2) for item in common_items)
            denominator1 = math.sqrt(sum((vector1[item] - mean1) ** 2 for item in common_items))
            denominator2 = math.sqrt(sum((vector2[item] - mean2) ** 2 for item in common_items))

            if denominator1 == 0 or denominator2 == 0:
                return 0.0

            return numerator / (denominator1 * denominator2)

        return 0.0

    def _build_user_item_matrix(self) -> Dict[str, Dict[str, float]]:
        """构建用户-物品矩阵"""
        matrix = defaultdict(dict)
        for interaction in self.interactions:
            if interaction.rating > 0:
                matrix[interaction.user_id][interaction.item_id] = interaction.rating
        return dict(matrix)

    def _get_similar_users(
        self,
        user_id: str,
        n_neighbors: int = 10,
        similarity_method: str = "cosine"
    ) -> List[Tuple[str, float]]:
        """获取相似用户（基于用户的协同过滤）"""
        matrix = self._build_user_item_matrix()

        if user_id not in matrix:
            return []

        user_vector = matrix[user_id]
        similarities = []

        for other_user_id, other_vector in matrix.items():
            if other_user_id != user_id:
                similarity = self._calculate_similarity(
                    user_vector,
                    other_vector,
                    method=similarity_method
                )
                similarities.append((other_user_id, similarity))

        # 按相似度降序排序
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:n_neighbors]

    def _get_similar_items(
        self,
        item_id: str,
        n_neighbors: int = 10,
        similarity_method: str = "cosine"
    ) -> List[Tuple[str, float]]:
        """获取相似商品（基于物品的协同过滤）"""
        matrix = defaultdict(dict)
        for interaction in self.interactions:
            if interaction.rating > 0:
                matrix[interaction.user_id][interaction.item_id] = interaction.rating

        # 转置矩阵
        item_users = defaultdict(dict)
        for user_id, items in matrix.items():
            for item_id_inner, rating in items.items():
                item_users[item_id_inner][user_id] = rating

        if item_id not in item_users:
            return []

        item_vector = item_users[item_id]
        similarities = []

        for other_item_id, other_vector in item_users.items():
            if other_item_id != item_id:
                similarity = self._calculate_similarity(
                    item_vector,
                    other_vector,
                    method=similarity_method
                )
                similarities.append((other_item_id, similarity))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:n_neighbors]

    # ========== 基于内容的推荐 ==========

    def _calculate_content_similarity(self, item1: Item, item2: Item) -> float:
        """计算内容相似度"""
        # 基于标签的相似度
        tags1 = set(item1.tags)
        tags2 = set(item2.tags)

        if not tags1 or not tags2:
            return 0.0

        intersection = len(tags1 & tags2)
        union = len(tags1 | tags2)

        tag_similarity = intersection / union if union > 0 else 0.0

        # 基于类别的相似度
        category_similarity = 1.0 if item1.category == item2.category else 0.0

        # 综合相似度
        return 0.7 * tag_similarity + 0.3 * category_similarity

    def _get_content_based_recommendations(
        self,
        item_id: str,
        top_n: int = 10
    ) -> List[Tuple[str, float]]:
        """获取基于内容的推荐"""
        item = self.get_item(item_id)
        if not item:
            return []

        similarities = []
        for other_item_id, other_item in self.items.items():
            if other_item_id != item_id:
                similarity = self._calculate_content_similarity(item, other_item)
                if similarity > 0:
                    similarities.append((other_item_id, similarity))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_n]

    # ========== 推荐生成 ==========

    def recommend(
        self,
        user_id: str,
        top_n: int = 10,
        method: str = "hybrid",
        n_neighbors: int = 10
    ) -> List[Recommendation]:
        """生成推荐"""
        recommendations = []

        # 获取用户已交互的商品
        user_items = self.get_user_items(user_id)

        if method == "collaborative_user_based":
            # 基于用户的协同过滤
            similar_users = self._get_similar_users(user_id, n_neighbors)

            # 收集推荐
            item_scores = defaultdict(float)
            for similar_user_id, similarity in similar_users:
                similar_user_items = self.get_user_items(similar_user_id)
                for item_id in similar_user_items:
                    if item_id not in user_items:
                        item_scores[item_id] += similarity

            # 排序
            sorted_items = sorted(item_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]

            for item_id, score in sorted_items:
                recommendations.append(Recommendation(
                    item_id=item_id,
                    score=score,
                    reason="基于相似用户的偏好",
                    algorithm="collaborative_user_based"
                ))

        elif method == "collaborative_item_based":
            # 基于物品的协同过滤
            item_scores = defaultdict(float)
            for item_id in user_items:
                similar_items = self._get_similar_items(item_id, top_n)
                for similar_item_id, similarity in similar_items:
                    if similar_item_id not in user_items:
                        item_scores[similar_item_id] += similarity

            sorted_items = sorted(item_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]

            for item_id, score in sorted_items:
                recommendations.append(Recommendation(
                    item_id=item_id,
                    score=score,
                    reason="基于您喜欢的相似商品",
                    algorithm="collaborative_item_based"
                ))

        elif method == "content_based":
            # 基于内容的推荐
            item_scores = defaultdict(float)
            for item_id in user_items:
                similar_items = self._get_content_based_recommendations(item_id, top_n)
                for similar_item_id, similarity in similar_items:
                    if similar_item_id not in user_items:
                        item_scores[similar_item_id] += similarity

            sorted_items = sorted(item_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]

            for item_id, score in sorted_items:
                recommendations.append(Recommendation(
                    item_id=item_id,
                    score=score,
                    reason="与您浏览的商品相似",
                    algorithm="content_based"
                ))

        elif method == "hybrid":
            # 混合推荐
            collaborative_recs = self.recommend(user_id, top_n, method="collaborative_user_based", n_neighbors=n_neighbors)
            content_recs = self.recommend(user_id, top_n, method="content_based")

            # 合并推荐
            item_scores = defaultdict(float)
            for rec in collaborative_recs:
                item_scores[rec.item_id] += rec.score * 0.6

            for rec in content_recs:
                item_scores[rec.item_id] += rec.score * 0.4

            sorted_items = sorted(item_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]

            for item_id, score in sorted_items:
                recommendations.append(Recommendation(
                    item_id=item_id,
                    score=score,
                    reason="个性化推荐",
                    algorithm="hybrid"
                ))

        elif method == "popular":
            # 热门推荐
            item_counts = defaultdict(int)
            for interaction in self.interactions:
                item_counts[interaction.item_id] += 1

            # 排除用户已交互的商品
            for item_id in user_items:
                if item_id in item_counts:
                    del item_counts[item_id]

            sorted_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]

            for item_id, count in sorted_items:
                recommendations.append(Recommendation(
                    item_id=item_id,
                    score=float(count),
                    reason="热门商品",
                    algorithm="popular"
                ))

        return recommendations

    # ========== 统计分析 ==========

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return {
            "total_users": len(self.users),
            "total_items": len(self.items),
            "total_interactions": len(self.interactions),
            "interactions_by_action": self._count_by_action(),
            "categories": self._count_by_category()
        }

    def _count_by_action(self) -> Dict[str, int]:
        """按行为类型统计"""
        counts = defaultdict(int)
        for interaction in self.interactions:
            counts[interaction.action] += 1
        return dict(counts)

    def _count_by_category(self) -> Dict[str, int]:
        """按类别统计商品"""
        counts = defaultdict(int)
        for item in self.items.values():
            if item.category:
                counts[item.category] += 1
        return dict(counts)

    # ========== 推荐效果评估 ==========

    def evaluate(
        self,
        test_interactions: List[Interaction],
        top_n: int = 10
    ) -> Dict[str, float]:
        """评估推荐效果"""
        precision_sum = 0.0
        recall_sum = 0.0
        users_counted = 0

        # 按用户分组
        user_interactions = defaultdict(list)
        for interaction in test_interactions:
            user_interactions[interaction.user_id].append(interaction)

        for user_id, interactions in user_interactions.items():
            if len(interactions) < top_n:
                continue

            # 生成推荐
            recommendations = self.recommend(user_id, top_n)
            recommended_items = set(rec.item_id for rec in recommendations)

            # 真实交互的商品
            actual_items = set(interaction.item_id for interaction in interactions[:top_n])

            if not recommended_items:
                continue

            # 计算Precision@N
            precision = len(recommended_items & actual_items) / top_n
            precision_sum += precision

            # 计算Recall@N
            recall = len(recommended_items & actual_items) / len(actual_items) if actual_items else 0
            recall_sum += recall

            users_counted += 1

        if users_counted == 0:
            return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

        precision = precision_sum / users_counted
        recall = recall_sum / users_counted
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        return {
            "precision": precision,
            "recall": recall,
            "f1": f1
        }


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="智能推荐系统")
    subparsers = parser.add_subparsers(dest="command", help="命令")

    # 推荐
    recommend_parser = subparsers.add_parser("recommend", help="生成推荐")
    recommend_parser.add_argument("--user", required=True, help="用户ID")
    recommend_parser.add_argument("--top-n", type=int, default=10, help="推荐数量")
    recommend_parser.add_argument("--method", choices=["collaborative_user_based", "collaborative_item_based", "content_based", "hybrid", "popular"], default="hybrid", help="推荐方法")

    # 添加用户
    add_user_parser = subparsers.add_parser("add-user", help="添加用户")
    add_user_parser.add_argument("--id", required=True, help="用户ID")
    add_user_parser.add_argument("--name", help="用户名")

    # 添加商品
    add_item_parser = subparsers.add_parser("add-item", help="添加商品")
    add_item_parser.add_argument("--id", required=True, help="商品ID")
    add_item_parser.add_argument("--name", required=True, help="商品名称")
    add_item_parser.add_argument("--category", help="类别")
    add_item_parser.add_argument("--tags", nargs='+', help="标签")

    # 添加交互
    add_interaction_parser = subparsers.add_parser("add-interaction", help="添加交互")
    add_interaction_parser.add_argument("--user", required=True, help="用户ID")
    add_interaction_parser.add_argument("--item", required=True, help="商品ID")
    add_interaction_parser.add_argument("--rating", type=float, default=0.0, help="评分")
    add_interaction_parser.add_argument("--action", default="view", help="行为类型")

    # 相似商品
    similar_parser = subparsers.add_parser("similar", help="相似商品")
    similar_parser.add_argument("--item", required=True, help="商品ID")
    similar_parser.add_argument("--top-n", type=int, default=10, help="数量")

    # 统计
    subparsers.add_parser("stats", help="统计信息")

    args = parser.parse_args()

    recommender = SmartRecommender()

    if args.command == "recommend":
        recommendations = recommender.recommend(args.user, args.top_n, args.method)
        print(f"推荐列表 ({len(recommendations)}):")
        for i, rec in enumerate(recommendations, 1):
            item = recommender.get_item(rec.item_id)
            if item:
                print(f"  {i}. {item.name} (得分: {rec.score:.2f})")
                print(f"     理由: {rec.reason} ({rec.algorithm})")
            else:
                print(f"  {i}. {rec.item_id} (得分: {rec.score:.2f})")

    elif args.command == "add-user":
        user = recommender.add_user(args.id, args.name or "")
        print(f"✅ 用户已添加: {user.id}")

    elif args.command == "add-item":
        item = recommender.add_item(
            args.id,
            args.name,
            category=args.category or "",
            tags=args.tags or []
        )
        print(f"✅ 商品已添加: {item.id} - {item.name}")

    elif args.command == "add-interaction":
        interaction = recommender.add_interaction(
            args.user,
            args.item,
            args.rating,
            args.action
        )
        print(f"✅ 交互已添加")

    elif args.command == "similar":
        similar_items = recommender._get_content_based_recommendations(args.item, args.top_n)
        print(f"相似商品 ({len(similar_items)}):")
        for i, (item_id, similarity) in enumerate(similar_items, 1):
            item = recommender.get_item(item_id)
            if item:
                print(f"  {i}. {item.name} (相似度: {similarity:.2f})")
            else:
                print(f"  {i}. {item_id} (相似度: {similarity:.2f})")

    elif args.command == "stats":
        stats = recommender.get_statistics()
        print(f"系统统计:")
        print(f"  总用户数: {stats['total_users']}")
        print(f"  总商品数: {stats['total_items']}")
        print(f"  总交互数: {stats['total_interactions']}")
        print(f"  交互类型: {stats['interactions_by_action']}")
        print(f"  商品类别: {stats['categories']}")


if __name__ == "__main__":
    main()
