#!/usr/bin/env python3
"""
智能推荐系统 - 测试套件
Smart Recommendation System - Test Suite
"""

import os
import sys
from pathlib import Path

# 添加技能目录到Python路径
skill_dir = Path(__file__).parent
sys.path.insert(0, str(skill_dir))

from recommender import (
    SmartRecommender, User, Item, Interaction,
    Recommendation
)


class TestResult:
    """测试结果"""
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.errors = []

    def add(self, test_name: str, success: bool, error: str = ""):
        """添加测试结果"""
        self.total += 1
        if success:
            self.passed += 1
            print(f"✅ {test_name}")
        else:
            self.failed += 1
            self.errors.append(f"{test_name}: {error}")
            print(f"❌ {test_name} - {error}")

    def print_summary(self):
        """打印汇总"""
        print(f"\n测试汇总:")
        print(f"  总计: {self.total}")
        print(f"  通过: {self.passed}")
        print(f"  失败: {self.failed}")
        if self.failed > 0:
            print(f"\n失败详情:")
            for error in self.errors:
                print(f"  - {error}")
        print(f"\n通过率: {self.passed/self.total*100:.1f}%")
        return self.failed == 0


def test_recommender():
    """测试推荐引擎"""
    print("\n=== 测试推荐引擎 ===")

    result = TestResult()

    # 使用临时数据目录
    data_dir = Path(__file__).parent / "test_data"
    data_dir.mkdir(exist_ok=True)

    # 清理旧数据
    for f in data_dir.glob("*.json"):
        f.unlink()

    recommender = SmartRecommender(str(data_dir))

    try:
        # 测试1: 添加用户
        user = recommender.add_user("user001", "Alice", "alice@example.com")
        result.add("添加用户", user is not None and user.id == "user001")

        # 测试2: 获取用户
        found_user = recommender.get_user("user001")
        result.add("获取用户", found_user is not None and found_user.name == "Alice")

        # 测试3: 列出用户
        users = recommender.list_users()
        result.add("列出用户", len(users) >= 1)

        # 测试4: 添加多个用户
        for i in range(10):
            recommender.add_user(f"user00{i+2}", f"User{i+2}")
        users = recommender.list_users()
        result.add("添加多个用户", len(users) == 11)

        # 测试5: 添加商品
        item = recommender.add_item(
            "item001",
            "无线耳机",
            category="电子产品",
            tags=["音频", "蓝牙"],
            price=299.0
        )
        result.add("添加商品", item is not None and item.category == "电子产品")

        # 测试6: 获取商品
        found_item = recommender.get_item("item001")
        result.add("获取商品", found_item is not None and found_item.name == "无线耳机")

        # 测试7: 列出商品
        items = recommender.list_items()
        result.add("列出商品", len(items) >= 1)

        # 测试8: 按类别列出商品
        recommender.add_item("item002", "有线耳机", category="电子产品")
        electronics = recommender.list_items(category="电子产品")
        result.add("按类别列出", len(electronics) == 2)

        # 测试9: 添加交互
        interaction = recommender.add_interaction("user001", "item001", rating=5, action="purchase")
        result.add("添加交互", interaction is not None)

        # 测试10: 获取用户交互
        user_interactions = recommender.get_user_interactions("user001")
        result.add("获取用户交互", len(user_interactions) >= 1)

        # 测试11: 获取用户商品
        user_items = recommender.get_user_items("user001")
        result.add("获取用户商品", len(user_items) >= 1)

        # 测试12: 获取商品交互
        item_interactions = recommender.get_item_interactions("item001")
        result.add("获取商品交互", len(item_interactions) >= 1)

        # 测试13: 多个交互
        for i in range(10):
            recommender.add_interaction(f"user00{i+2}", f"item00{(i%5)+1}", rating=i%5+1)
        result.add("添加多个交互", len(recommender.interactions) >= 10)

        # 测试14: 构建用户-物品矩阵
        matrix = recommender._build_user_item_matrix()
        result.add("构建矩阵", len(matrix) >= 1)

        # 测试15: 计算余弦相似度
        vector1 = {"item001": 5, "item002": 3}
        vector2 = {"item001": 4, "item002": 4}
        similarity = recommender._calculate_similarity(vector1, vector2, "cosine")
        result.add("余弦相似度", 0.9 < similarity < 1.0)

        # 测试16: 计算皮尔逊相关
        similarity = recommender._calculate_similarity(vector1, vector2, "pearson")
        result.add("皮尔逊相关", isinstance(similarity, float))

        # 测试17: 获取相似用户
        similar_users = recommender._get_similar_users("user001", n_neighbors=5)
        result.add("相似用户", isinstance(similar_users, list))

        # 测试18: 获取相似商品
        similar_items = recommender._get_similar_items("item001", n_neighbors=5)
        result.add("相似商品", isinstance(similar_items, list))

        # 测试19: 内容相似度
        item1 = recommender.get_item("item001")
        item2 = recommender.get_item("item002")
        content_similarity = recommender._calculate_content_similarity(item1, item2)
        result.add("内容相似度", 0 <= content_similarity <= 1)

        # 测试20: 基于内容的推荐
        content_recs = recommender._get_content_based_recommendations("item001", top_n=5)
        result.add("内容推荐", isinstance(content_recs, list))

        # 测试21: 协同过滤推荐（基于用户）
        user_recs = recommender.recommend("user001", top_n=5, method="collaborative_user_based")
        result.add("用户协同过滤", isinstance(user_recs, list))

        # 测试22: 协同过滤推荐（基于物品）
        item_recs = recommender.recommend("user001", top_n=5, method="collaborative_item_based")
        result.add("物品协同过滤", isinstance(item_recs, list))

        # 测试23: 基于内容的推荐
        content_recs = recommender.recommend("user001", top_n=5, method="content_based")
        result.add("基于内容推荐", isinstance(content_recs, list))

        # 测试24: 混合推荐
        hybrid_recs = recommender.recommend("user001", top_n=5, method="hybrid")
        result.add("混合推荐", isinstance(hybrid_recs, list))

        # 测试25: 热门推荐
        popular_recs = recommender.recommend("user001", top_n=5, method="popular")
        result.add("热门推荐", isinstance(popular_recs, list))

        # 测试26: 推荐数量限制
        limited_recs = recommender.recommend("user001", top_n=3)
        result.add("推荐数量限制", len(limited_recs) <= 3)

        # 测试27: 推荐结果格式
        if limited_recs:
            result.add("推荐结果格式", isinstance(limited_recs[0], Recommendation))

        # 测试28: 统计信息
        stats = recommender.get_statistics()
        result.add("统计信息", stats["total_users"] >= 10 and stats["total_items"] >= 2)

        # 测试29: 按行为统计
        by_action = stats["interactions_by_action"]
        result.add("按行为统计", isinstance(by_action, dict))

        # 测试30: 按类别统计
        by_category = stats["categories"]
        result.add("按类别统计", isinstance(by_category, dict))

        # 测试31: 添加更多商品
        for i in range(5):
            recommender.add_item(
                f"item00{i+6}",
                f"商品{i+6}",
                category="电子产品" if i < 3 else "服装",
                tags=[f"标签{i}"]
            )
        items = recommender.list_items()
        result.add("添加更多商品", len(items) == 12)

        # 测试32: 不同类别的推荐
        recommender.add_item("item011", "T恤", category="服装")
        items = recommender.list_items(category="服装")
        result.add("不同类别", len(items) >= 3)

        # 测试33: 限制用户列表
        limited_users = recommender.list_users(limit=5)
        result.add("限制用户列表", len(limited_users) == 5)

        # 测试34: 限制商品列表
        limited_items = recommender.list_items(limit=5)
        result.add("限制商品列表", len(limited_items) == 5)

        # 测试35: 用户交互的特定行为
        purchase_items = recommender.get_user_items("user001", action="purchase")
        result.add("特定行为", isinstance(purchase_items, list))

        # 测试36: 推荐算法标记
        recs = recommender.recommend("user001", top_n=1, method="hybrid")
        if recs:
            result.add("算法标记", recs[0].algorithm == "hybrid")

        # 测试37: 推荐理由
        if recs:
            result.add("推荐理由", len(recs[0].reason) > 0)

        # 测试38: 推荐得分
        if recs:
            result.add("推荐得分", recs[0].score >= 0)

        # 测试39: 评估函数
        # 创建测试数据
        test_interactions = [
            Interaction(id="t1", user_id="user002", item_id="item001", rating=5),
            Interaction(id="t2", user_id="user002", item_id="item002", rating=4)
        ]
        metrics = recommender.evaluate(test_interactions)
        result.add("评估函数", "precision" in metrics and "recall" in metrics)

        # 测试40: F1分数
        if metrics["precision"] + metrics["recall"] > 0:
            expected_f1 = 2 * metrics["precision"] * metrics["recall"] / (metrics["precision"] + metrics["recall"])
            result.add("F1分数", abs(metrics["f1"] - expected_f1) < 0.01)
        else:
            result.add("F1分数", metrics["f1"] == 0.0)

    except Exception as e:
        result.add("推荐引擎测试", False, f"异常: {str(e)}")

    return result


def main():
    """运行所有测试"""
    print("=" * 60)
    print("智能推荐系统 - 测试套件")
    print("=" * 60)

    # 运行所有测试模块
    results = []
    results.append(test_recommender())

    # 汇总所有测试结果
    total_tests = sum(r.total for r in results)
    total_passed = sum(r.passed for r in results)
    total_failed = sum(r.failed for r in results)

    print("\n" + "=" * 60)
    print("总体测试汇总")
    print("=" * 60)
    print(f"总测试数: {total_tests}")
    print(f"通过: {total_passed}")
    print(f"失败: {total_failed}")
    print(f"通过率: {total_passed/total_tests*100:.1f}%")

    if total_failed == 0:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print("\n❌ 存在失败的测试")
        return 1


if __name__ == "__main__":
    sys.exit(main())
