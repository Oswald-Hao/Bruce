#!/usr/bin/env python3
"""
跨境电商系统 - 测试套件
Cross-Border E-commerce - Test Suite
"""

import os
import sys
from pathlib import Path

# 添加技能目录到Python路径
skill_dir = Path(__file__).parent
sys.path.insert(0, str(skill_dir))

from product_manager import ProductManager, Product, Platform, Currency, SKU


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


def test_product_manager():
    """测试商品管理器"""
    print("\n=== 测试商品管理器 ===")

    result = TestResult()

    # 使用临时数据目录
    data_dir = Path(__file__).parent / "test_data"
    data_dir.mkdir(exist_ok=True)

    # 清理旧数据
    for f in data_dir.glob("*.json"):
        f.unlink()

    pm = ProductManager(str(data_dir))

    try:
        # 测试1: 添加商品
        product = pm.add_product(
            sku="SKU001",
            name="无线耳机",
            description="高品质蓝牙耳机",
            price=29.99,
            cost=15.00,
            stock=100,
            platform=Platform.AMAZON,
            currency=Currency.USD
        )
        result.add("添加商品", product is not None)

        # 测试2: 获取商品
        found_product = pm.get_product(product.id)
        result.add("获取商品", found_product is not None and found_product.sku == "SKU001")

        # 测试3: 通过SKU获取商品
        found_product = pm.get_product_by_sku("SKU001")
        result.add("通过SKU获取", found_product is not None)

        # 测试4: 列出商品
        products = pm.list_products()
        result.add("列出商品", len(products) >= 1)

        # 测试5: 按平台列出商品
        amazon_products = pm.list_products(platform=Platform.AMAZON)
        result.add("按平台列出", len(amazon_products) >= 1)

        # 测试6: 更新商品
        updated = pm.update_product(product.id, name="无线耳机 Pro", price=34.99)
        result.add("更新商品", updated.name == "无线耳机 Pro" and updated.price == 34.99)

        # 测试7: 添加SKU
        sku = pm.add_sku(product.id, "颜色", "黑色", price=29.99, stock=50)
        result.add("添加SKU", sku is not None)

        # 测试8: 更新SKU
        updated_sku = pm.update_sku(product.id, sku.id, price=31.99)
        result.add("更新SKU", updated_sku.price == 31.99)

        # 测试9: 添加多个SKU
        pm.add_sku(product.id, "颜色", "白色", price=29.99, stock=30)
        pm.add_sku(product.id, "颜色", "红色", price=29.99, stock=20)
        result.add("添加多个SKU", len(product.skus) == 3)

        # 测试10: 删除SKU
        success = pm.delete_sku(product.id, sku.id)
        result.add("删除SKU", success and len(product.skus) == 2)

        # 测试11: 更新库存
        success = pm.update_stock(product.id, 150)
        result.add("更新库存", success and product.stock == 150)

        # 测试12: 更新SKU库存
        pm.add_sku(product.id, "颜色", "蓝色", price=29.99, stock=100)
        sku2 = product.skus[-1]
        success = pm.update_sku_stock(product.id, sku2.id, 80)
        result.add("更新SKU库存", success and sku2.stock == 80)

        # 测试13: 库存不足状态
        pm.update_stock(product.id, 0)
        result.add("库存不足状态", product.status == "out_of_stock")

        # 测试14: 恢复库存
        pm.update_stock(product.id, 50)
        result.add("恢复库存", product.status == "active")

        # 测试15: 同步到平台
        mapping = pm.sync_to_platform(product.id, Platform.EBAY)
        result.add("同步到平台", mapping is not None and mapping.platform == Platform.EBAY)

        # 测试16: 获取平台映射
        found_mapping = pm.get_platform_mapping(product.id, Platform.EBAY)
        result.add("获取平台映射", found_mapping is not None)

        # 测试17: 列出平台映射
        mappings = pm.list_platform_mappings(product.id)
        result.add("列出平台映射", len(mappings) >= 1)

        # 测试18: 同步到多个平台
        pm.sync_to_platform(product.id, Platform.ALIEXPRESS)
        pm.sync_to_platform(product.id, Platform.SHOPEE)
        mappings = pm.list_platform_mappings(product_id=product.id)
        result.add("同步多平台", len(mappings) == 3)

        # 测试19: 计算利润
        pm.update_product(product.id, cost=15.00, price=29.99)
        profit_data = pm.calculate_profit(product.id)
        result.add("计算利润", abs(profit_data["profit"] - 14.99) < 0.01)

        # 测试20: 计算利润率
        margin = profit_data.get("margin", 0)
        result.add("计算利润率", abs(margin - 99.93) < 0.1)

        # 测试21: 统计信息
        stats = pm.get_statistics()
        result.add("统计信息", stats["total_products"] >= 1)

        # 测试22: 创建多个商品
        for i in range(5):
            pm.add_product(
                sku=f"SKU00{i+2}",
                name=f"商品{i+2}",
                price=19.99 + i * 5,
                stock=50
            )
        products = pm.list_products()
        result.add("创建多个商品", len(products) == 6)

        # 测试23: 按状态筛选
        pm.update_stock(product.id, 0)
        out_of_stock = pm.list_products(status="out_of_stock")
        result.add("按状态筛选", len(out_of_stock) >= 1)

        # 测试24: 限制数量
        limited = pm.list_products(limit=3)
        result.add("限制数量", len(limited) == 3)

        # 测试25: 删除商品
        test_product = pm.add_product(sku="DELETE001", name="待删除")
        success = pm.delete_product(test_product.id)
        result.add("删除商品", success and test_product.id not in pm.products)

        # 测试26: 删除后映射也删除
        pm.add_product(sku="DELETE002", name="待删除2")
        pm.sync_to_platform("DELETE002", Platform.EBAY)
        pm.delete_product("DELETE002")
        mappings = pm.list_platform_mappings()
        result.add("删除后清理映射", not any(m.product_id == "DELETE002" for m in mappings))

        # 测试27: 低库存预警
        pm.update_stock(product.id, 5)
        stats = pm.get_statistics()
        result.add("低库存预警", stats["low_stock"] >= 1)

        # 测试28: 添加图片
        pm.update_product(product.id, images=["image1.jpg", "image2.jpg"])
        result.add("添加图片", len(product.images) == 2)

        # 测试29: 添加标签
        pm.update_product(product.id, tags=["热销", "新品"])
        result.add("添加标签", "热销" in product.tags and "新品" in product.tags)

        # 测试30: 自定义字段
        pm.update_product(product.id, custom_fields={"weight": "100g", "material": "塑料"})
        result.add("自定义字段", product.custom_fields.get("weight") == "100g")

        # 测试31: 不同货币
        product_eur = pm.add_product(
            sku="SKU_EUR",
            name="欧元商品",
            price=25.00,
            currency=Currency.EUR
        )
        result.add("不同货币", product_eur.currency == Currency.EUR)

        # 测试32: 不同平台
        product_ebay = pm.add_product(
            sku="SKU_EBAY",
            name="eBay商品",
            platform=Platform.EBAY
        )
        result.add("不同平台", product_ebay.platform == Platform.EBAY)

        # 测试33: 更新时间
        import time
        old_updated = product.updated_at
        time.sleep(0.1)
        pm.update_product(product.id, name="新名称")
        result.add("更新时间", product.updated_at > old_updated)

        # 测试34: 创建时间不变
        old_created = product.created_at
        pm.update_product(product.id, name="新名称2")
        result.add("创建时间不变", product.created_at == old_created)

        # 测试35: 批量更新库存
        pm.update_stock(product.id, 100)
        pm.update_stock("DELETE002" if "DELETE002" in pm.products else list(pm.products.keys())[1], 200)
        result.add("批量更新库存", product.stock == 100)

        # 测试36: 通过不存在的SKU获取
        found = pm.get_product_by_sku("NOTEXIST")
        result.add("不存在的SKU", found is None)

        # 测试37: 通过不存在的ID获取
        found = pm.get_product("NOTEXISTID")
        result.add("不存在的ID", found is None)

        # 测试38: 更新不存在的商品
        updated = pm.update_product("NOTEXISTID", name="test")
        result.add("更新不存在商品", updated is None)

        # 测试39: 删除不存在的商品
        success = pm.delete_product("NOTEXISTID")
        result.add("删除不存在商品", not success)

        # 测试40: 列出所有平台
        stats = pm.get_statistics()
        result.add("列出所有平台", stats["total_platforms"] >= 2)

    except Exception as e:
        result.add("商品管理器测试", False, f"异常: {str(e)}")

    return result


def main():
    """运行所有测试"""
    print("=" * 60)
    print("跨境电商系统 - 测试套件")
    print("=" * 60)

    # 运行所有测试模块
    results = []
    results.append(test_product_manager())

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
