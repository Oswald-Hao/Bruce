#!/usr/bin/env python3
"""
跨境电商系统 - 商品管理器
Cross-Border E-commerce - Product Manager
"""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict, field
from pathlib import Path
from enum import Enum


class Platform(Enum):
    """平台类型"""
    AMAZON = "amazon"
    EBAY = "ebay"
    ALIEXPRESS = "aliexpress"
    SHOPEE = "shopee"
    CUSTOM = "custom"


class Currency(Enum):
    """货币类型"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CNY = "CNY"
    SGD = "SGD"


@dataclass
class SKU:
    """SKU规格"""
    id: str
    name: str
    value: str
    price: float = 0.0
    stock: int = 0
    cost: float = 0.0


@dataclass
class Product:
    """商品数据模型"""
    id: str
    sku: str
    name: str
    description: str = ""
    category: str = ""
    brand: str = ""
    images: List[str] = field(default_factory=list)
    skus: List[SKU] = field(default_factory=list)
    price: float = 0.0
    cost: float = 0.0
    currency: Currency = Currency.USD
    stock: int = 0
    platform: Platform = Platform.CUSTOM
    platform_product_id: str = ""
    status: str = "active"  # active, inactive, out_of_stock
    created_at: str = None
    updated_at: str = None
    tags: List[str] = field(default_factory=list)
    custom_fields: Dict = field(default_factory=dict)

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()


@dataclass
class PlatformMapping:
    """平台映射"""
    id: str
    product_id: str
    platform: Platform
    platform_product_id: str = ""
    price: float = 0.0
    currency: Currency = Currency.USD
    status: str = "active"
    synced_at: str = None
    last_sync_status: str = "success"


class ProductManager:
    """商品管理器"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.products = {}
        self.platform_mappings = {}

        self._load_data()

    def _load_data(self):
        """加载数据"""
        products_file = self.data_dir / "products.json"
        if products_file.exists():
            with open(products_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for id_, product_data in data.items():
                    # 重建SKU对象
                    skus_data = product_data.get("skus", [])
                    skus = []
                    for sku_data in skus_data:
                        skus.append(SKU(**sku_data))

                    product_data["skus"] = skus
                    product_data["currency"] = Currency(product_data.get("currency", "USD"))
                    product_data["platform"] = Platform(product_data.get("platform", "custom"))

                    self.products[id_] = Product(**product_data)

        mappings_file = self.data_dir / "platform_mappings.json"
        if mappings_file.exists():
            with open(mappings_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for id_, mapping_data in data.items():
                    mapping_data["platform"] = Platform(mapping_data.get("platform", "custom"))
                    mapping_data["currency"] = Currency(mapping_data.get("currency", "USD"))
                    self.platform_mappings[id_] = PlatformMapping(**mapping_data)

    def _save_data(self):
        """保存数据"""
        products_file = self.data_dir / "products.json"
        products_data = {id_: asdict(product) for id_, product in self.products.items()}
        for product_data in products_data.values():
            product_data["currency"] = product_data["currency"].value
            product_data["platform"] = product_data["platform"].value
            for sku_data in product_data.get("skus", []):
                sku_data["currency"] = Currency.USD.value  # SKU货币简化处理

        with open(products_file, 'w', encoding='utf-8') as f:
            json.dump(products_data, f, indent=2, ensure_ascii=False)

        mappings_file = self.data_dir / "platform_mappings.json"
        mappings_data = {id_: asdict(mapping) for id_, mapping in self.platform_mappings.items()}
        for mapping_data in mappings_data.values():
            mapping_data["platform"] = mapping_data["platform"].value
            mapping_data["currency"] = mapping_data["currency"].value

        with open(mappings_file, 'w', encoding='utf-8') as f:
            json.dump(mappings_data, f, indent=2, ensure_ascii=False)

    # ========== 商品管理 ==========

    def add_product(
        self,
        sku: str,
        name: str,
        description: str = "",
        category: str = "",
        brand: str = "",
        images: List[str] = None,
        price: float = 0.0,
        cost: float = 0.0,
        currency: Currency = Currency.USD,
        stock: int = 0,
        platform: Platform = Platform.CUSTOM,
        **kwargs
    ) -> Product:
        """添加商品"""
        product_id = str(uuid.uuid4())
        product = Product(
            id=product_id,
            sku=sku,
            name=name,
            description=description,
            category=category,
            brand=brand,
            images=images or [],
            price=price,
            cost=cost,
            currency=currency,
            stock=stock,
            platform=platform,
            custom_fields=kwargs
        )

        self.products[product_id] = product
        self._save_data()
        return product

    def get_product(self, product_id: str) -> Optional[Product]:
        """获取商品"""
        return self.products.get(product_id)

    def get_product_by_sku(self, sku: str) -> Optional[Product]:
        """通过SKU获取商品"""
        for product in self.products.values():
            if product.sku == sku:
                return product
        return None

    def list_products(
        self,
        platform: Platform = None,
        status: str = None,
        category: str = None,
        limit: int = None
    ) -> List[Product]:
        """列出商品"""
        products = list(self.products.values())

        if platform:
            products = [p for p in products if p.platform == platform]

        if status:
            products = [p for p in products if p.status == status]

        if category:
            products = [p for p in products if p.category == category]

        if limit:
            products = products[:limit]

        return products

    def update_product(self, product_id: str, **kwargs) -> Optional[Product]:
        """更新商品"""
        product = self.products.get(product_id)
        if product:
            for key, value in kwargs.items():
                if hasattr(product, key):
                    setattr(product, key, value)
            product.updated_at = datetime.now().isoformat()
            self._save_data()
        return product

    def delete_product(self, product_id: str) -> bool:
        """删除商品"""
        if product_id in self.products:
            del self.products[product_id]
            # 删除相关平台映射
            mappings_to_delete = [
                id_ for id_, mapping in self.platform_mappings.items()
                if mapping.product_id == product_id
            ]
            for mapping_id in mappings_to_delete:
                del self.platform_mappings[mapping_id]
            self._save_data()
            return True
        return False

    # ========== SKU管理 ==========

    def add_sku(
        self,
        product_id: str,
        name: str,
        value: str,
        price: float = 0.0,
        stock: int = 0,
        cost: float = 0.0
    ) -> Optional[SKU]:
        """添加SKU"""
        product = self.products.get(product_id)
        if product:
            sku = SKU(
                id=str(uuid.uuid4()),
                name=name,
                value=value,
                price=price,
                stock=stock,
                cost=cost
            )
            product.skus.append(sku)
            product.updated_at = datetime.now().isoformat()
            self._save_data()
            return sku
        return None

    def update_sku(self, product_id: str, sku_id: str, **kwargs) -> Optional[SKU]:
        """更新SKU"""
        product = self.products.get(product_id)
        if product:
            for sku in product.skus:
                if sku.id == sku_id:
                    for key, value in kwargs.items():
                        if hasattr(sku, key):
                            setattr(sku, key, value)
                    product.updated_at = datetime.now().isoformat()
                    self._save_data()
                    return sku
        return None

    def delete_sku(self, product_id: str, sku_id: str) -> bool:
        """删除SKU"""
        product = self.products.get(product_id)
        if product:
            product.skus = [sku for sku in product.skus if sku.id != sku_id]
            product.updated_at = datetime.now().isoformat()
            self._save_data()
            return True
        return False

    # ========== 库存管理 ==========

    def update_stock(self, product_id: str, stock: int) -> bool:
        """更新库存"""
        product = self.products.get(product_id)
        if product:
            product.stock = stock
            if stock <= 0:
                product.status = "out_of_stock"
            elif product.status == "out_of_stock":
                product.status = "active"
            product.updated_at = datetime.now().isoformat()
            self._save_data()
            return True
        return False

    def update_sku_stock(self, product_id: str, sku_id: str, stock: int) -> bool:
        """更新SKU库存"""
        product = self.products.get(product_id)
        if product:
            for sku in product.skus:
                if sku.id == sku_id:
                    sku.stock = stock
                    product.updated_at = datetime.now().isoformat()
                    self._save_data()
                    return True
        return False

    # ========== 平台映射 ==========

    def sync_to_platform(
        self,
        product_id: str,
        platform: Platform,
        platform_product_id: str = "",
        price: float = None,
        currency: Currency = None
    ) -> Optional[PlatformMapping]:
        """同步到平台"""
        product = self.products.get(product_id)
        if not product:
            return None

        mapping_id = f"{product_id}_{platform.value}"

        mapping = PlatformMapping(
            id=mapping_id,
            product_id=product_id,
            platform=platform,
            platform_product_id=platform_product_id,
            price=price or product.price,
            currency=currency or product.currency,
            synced_at=datetime.now().isoformat()
        )

        self.platform_mappings[mapping_id] = mapping
        self._save_data()

        return mapping

    def get_platform_mapping(self, product_id: str, platform: Platform) -> Optional[PlatformMapping]:
        """获取平台映射"""
        mapping_id = f"{product_id}_{platform.value}"
        return self.platform_mappings.get(mapping_id)

    def list_platform_mappings(self, product_id: str = None) -> List[PlatformMapping]:
        """列出平台映射"""
        mappings = list(self.platform_mappings.values())

        if product_id:
            mappings = [m for m in mappings if m.product_id == product_id]

        return mappings

    # ========== 统计分析 ==========

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return {
            "total_products": len(self.products),
            "total_platforms": len(set(m.platform for m in self.platform_mappings.values())),
            "by_platform": {
                platform.value: len(list(self.list_products(platform=platform)))
                for platform in Platform
            },
            "by_status": {
                status: len(list(self.list_products(status=status)))
                for status in ["active", "inactive", "out_of_stock"]
            },
            "low_stock": len([p for p in self.products.values() if p.stock < 10 and p.stock > 0]),
            "out_of_stock": len([p for p in self.products.values() if p.stock <= 0])
        }

    def calculate_profit(self, product_id: str) -> Dict:
        """计算利润"""
        product = self.products.get(product_id)
        if not product:
            return {}

        profit = product.price - product.cost
        margin = (profit / product.cost * 100) if product.cost > 0 else 0

        return {
            "price": product.price,
            "cost": product.cost,
            "profit": profit,
            "margin": round(margin, 2)
        }


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="商品管理器")
    subparsers = parser.add_subparsers(dest="command", help="命令")

    # 添加商品
    add_parser = subparsers.add_parser("add", help="添加商品")
    add_parser.add_argument("--sku", required=True, help="SKU")
    add_parser.add_argument("--name", required=True, help="商品名称")
    add_parser.add_argument("--description", help="描述")
    add_parser.add_argument("--price", type=float, default=0.0, help="价格")
    add_parser.add_argument("--cost", type=float, default=0.0, help="成本")
    add_parser.add_argument("--stock", type=int, default=0, help="库存")
    add_parser.add_argument("--platform", default="custom", choices=["amazon", "ebay", "aliexpress", "shopee", "custom"], help="平台")
    add_parser.add_argument("--currency", default="USD", choices=["USD", "EUR", "GBP", "JPY", "CNY", "SGD"], help="货币")

    # 列出商品
    list_parser = subparsers.add_parser("list", help="列出商品")
    list_parser.add_argument("--platform", choices=["amazon", "ebay", "aliexpress", "shopee", "custom"], help="按平台筛选")
    list_parser.add_argument("--status", choices=["active", "inactive", "out_of_stock"], help="按状态筛选")
    list_parser.add_argument("--limit", type=int, help="限制数量")

    # 更新商品
    update_parser = subparsers.add_parser("update", help="更新商品")
    update_parser.add_argument("--product", required=True, help="商品ID")
    update_parser.add_argument("--name", help="商品名称")
    update_parser.add_argument("--price", type=float, help="价格")
    update_parser.add_argument("--stock", type=int, help="库存")

    # 删除商品
    delete_parser = subparsers.add_parser("delete", help="删除商品")
    delete_parser.add_argument("--product", required=True, help="商品ID")

    # 同步到平台
    sync_parser = subparsers.add_parser("sync", help="同步到平台")
    sync_parser.add_argument("--product", required=True, help="商品ID")
    sync_parser.add_argument("--platform", required=True, choices=["amazon", "ebay", "aliexpress", "shopee"], help="目标平台")

    # 统计
    subparsers.add_parser("stats", help="查看统计信息")

    # 利润计算
    profit_parser = subparsers.add_parser("profit", help="计算利润")
    profit_parser.add_argument("--product", required=True, help="商品ID")

    args = parser.parse_args()

    pm = ProductManager()

    if args.command == "add":
        product = pm.add_product(
            sku=args.sku,
            name=args.name,
            description=args.description or "",
            price=args.price,
            cost=args.cost,
            stock=args.stock,
            platform=Platform(args.platform),
            currency=Currency(args.currency)
        )
        print(f"✅ 商品已添加: {product.id}")
        print(f"   SKU: {product.sku}")
        print(f"   名称: {product.name}")
        print(f"   价格: {product.price} {product.currency.value}")

    elif args.command == "list":
        products = pm.list_products(
            platform=Platform(args.platform) if args.platform else None,
            status=args.status,
            limit=args.limit
        )
        print(f"商品列表 ({len(products)}):")
        for p in products:
            print(f"  [{p.id[:8]}] {p.sku} - {p.name} ({p.platform.value}, {p.stock}库存, {p.price}{p.currency.value})")

    elif args.command == "update":
        kwargs = {}
        if args.name:
            kwargs["name"] = args.name
        if args.price is not None:
            kwargs["price"] = args.price
        if args.stock is not None:
            kwargs["stock"] = args.stock

        product = pm.update_product(args.product, **kwargs)
        if product:
            print(f"✅ 商品已更新: {product.name}")
        else:
            print(f"❌ 商品未找到: {args.product}")

    elif args.command == "delete":
        if pm.delete_product(args.product):
            print(f"✅ 商品已删除")
        else:
            print(f"❌ 删除失败")

    elif args.command == "sync":
        mapping = pm.sync_to_platform(args.product, Platform(args.platform))
        if mapping:
            print(f"✅ 已同步到 {args.platform}")
            print(f"   映射ID: {mapping.id}")
        else:
            print(f"❌ 同步失败")

    elif args.command == "stats":
        stats = pm.get_statistics()
        print(f"商品统计:")
        print(f"  总商品数: {stats['total_products']}")
        print(f"  平台数: {stats['total_platforms']}")
        print(f"  低库存: {stats['low_stock']}")
        print(f"  缺货: {stats['out_of_stock']}")

    elif args.command == "profit":
        profit = pm.calculate_profit(args.product)
        if profit:
            product = pm.get_product(args.product)
            print(f"利润分析: {product.name if product else args.product}")
            print(f"  售价: {profit['price']}")
            print(f"  成本: {profit['cost']}")
            print(f"  利润: {profit['profit']}")
            print(f"  利润率: {profit['margin']}%")


if __name__ == "__main__":
    main()
