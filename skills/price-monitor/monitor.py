#!/usr/bin/env python3
"""
电商价格监控系统 - 核心监控器
Price Monitor - Core Monitor

主要功能：
- 实时价格监控
- 跨平台比价
- 套利机会发现
- 价格趋势分析
"""

import time
import json
import hashlib
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import requests
from bs4 import BeautifulSoup


@dataclass
class ProductInfo:
    """商品信息"""
    product_id: str
    name: str
    url: str
    platform: str
    current_price: float
    stock: int
    sales: int
    last_update: str
    target_price: Optional[float] = None
    alert_threshold: float = 0.05


class PriceMonitor:
    """价格监控器核心类"""

    def __init__(self, platforms: List[str], config: Optional[Dict] = None):
        """
        初始化价格监控器

        Args:
            platforms: 平台列表（taobao/pinduoduo/jd/xianyu）
            config: 配置字典
        """
        self.platforms = platforms
        self.config = config or {}
        self.products: Dict[str, ProductInfo] = {}
        self.price_history: Dict[str, List[Dict]] = {}

        # 支持的平台
        self.supported_platforms = ["taobao", "pinduoduo", "jd", "xianyu"]

        for platform in platforms:
            if platform not in self.supported_platforms:
                raise ValueError(f"不支持的平台: {platform}")

        # 监控状态
        self.monitoring = False

    def add_product(self, product_id: str, name: str, url: str,
                  platform: str, target_price: Optional[float] = None,
                  alert_threshold: float = 0.05) -> None:
        """
        添加监控商品

        Args:
            product_id: 商品ID
            name: 商品名称
            url: 商品链接
            platform: 平台
            target_price: 目标价格
            alert_threshold: 价格变动告警阈值（百分比）
        """
        # 获取初始价格
        current_price = self._fetch_price(url, platform)
        stock = self._check_stock(url, platform)
        sales = self._get_sales_count(url, platform)

        product = ProductInfo(
            product_id=product_id,
            name=name,
            url=url,
            platform=platform,
            current_price=current_price,
            stock=stock,
            sales=sales,
            last_update=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            target_price=target_price,
            alert_threshold=alert_threshold
        )

        self.products[product_id] = product
        self._save_price_history(product_id, product)

        print(f"✅ 已添加商品: {name} - ¥{current_price}")

    def _fetch_price(self, url: str, platform: str) -> float:
        """
        获取商品价格

        Args:
            url: 商品链接
            platform: 平台

        Returns:
            价格
        """
        # 模拟价格获取（实际应该调用真实API或爬虫）
        price_hash = int(hashlib.md5(url.encode()).hexdigest()[:8], 16)
        base_price = 100 + (price_hash % 900)
        return float(base_price)

    def _check_stock(self, url: str, platform: str) -> int:
        """
        检查库存

        Args:
            url: 商品链接
            platform: 平台

        Returns:
            库存数量
        """
        # 模拟库存检查
        stock_hash = int(hashlib.md5(url.encode()).hexdigest()[:8], 16)
        return (stock_hash % 1000)

    def _get_sales_count(self, url: str, platform: str) -> int:
        """
        获取销量

        Args:
            url: 商品链接
            platform: 平台

        Returns:
            销量
        """
        # 模拟销量
        sales_hash = int(hashlib.md5(url.encode()).hexdigest()[:8], 16)
        return 100 + (sales_hash % 10000)

    def get_current_price(self, product_id: str, platform: Optional[str] = None) -> Dict[str, Any]:
        """
        获取当前价格

        Args:
            product_id: 商品ID
            platform: 平台（可选）

        Returns:
            价格信息
        """
        if product_id not in self.products:
            raise ValueError(f"商品不存在: {product_id}")

        product = self.products[product_id]

        # 刷新价格
        current_price = self._fetch_price(product.url, platform or product.platform)
        old_price = product.current_price

        # 更新商品信息
        product.current_price = current_price
        product.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        product.stock = self._check_stock(product.url, platform or product.platform)
        product.sales = self._get_sales_count(product.url, platform or product.platform)

        # 保存历史
        self._save_price_history(product_id, product)

        # 计算变化
        price_change_rate = ((current_price - old_price) / old_price) * 100 if old_price > 0 else 0

        return {
            "product_id": product_id,
            "name": product.name,
            "platform": platform or product.platform,
            "current_price": current_price,
            "old_price": old_price,
            "change_rate": round(price_change_rate, 2),
            "stock": product.stock,
            "sales": product.sales,
            "last_update": product.last_update
        }

    def compare_platforms(self, product_id: str) -> Dict[str, Any]:
        """
        跨平台比价

        Args:
            product_id: 商品ID

        Returns:
            比价结果
        """
        if product_id not in self.products:
            raise ValueError(f"商品不存在: {product_id}")

        base_product = self.products[product_id]
        platform_prices = {}

        # 获取各平台价格
        for platform in self.platforms:
            try:
                price_info = self.get_current_price(product_id, platform)
                platform_prices[platform] = {
                    "price": price_info["current_price"],
                    "stock": price_info["stock"],
                    "sales": price_info["sales"]
                }
            except Exception as e:
                print(f"获取{platform}价格失败: {e}")

        # 找出最低价
        if platform_prices:
            lowest = min(platform_prices.items(), key=lambda x: x[1]["price"])
            highest = max(platform_prices.items(), key=lambda x: x[1]["price"])
        else:
            lowest = (None, {"price": 0})
            highest = (None, {"price": 0})

        return {
            "product_id": product_id,
            "product_name": base_product.name,
            "platforms": platform_prices,
            "lowest_price": {
                "platform": lowest[0],
                "price": lowest[1]["price"]
            },
            "highest_price": {
                "platform": highest[0],
                "price": highest[1]["price"]
            },
            "price_range": highest[1]["price"] - lowest[1]["price"] if lowest[0] else 0
        }

    def find_arbitrage(self, product_id: str, min_profit_rate: float = 0.15) -> List[Dict[str, Any]]:
        """
        发现套利机会

        Args:
            product_id: 商品ID
            min_profit_rate: 最低利润率

        Returns:
            套利机会列表
        """
        if product_id not in self.products:
            raise ValueError(f"商品不存在: {product_id}")

        comparison = self.compare_platforms(product_id)
        opportunities = []

        # 计算所有平台组合的套利机会
        platforms = list(comparison["platforms"].keys())
        for i, source in enumerate(platforms):
            for target in platforms[i+1:]:
                source_price = comparison["platforms"][source]["price"]
                target_price = comparison["platforms"][target]["price"]

                # 计算利润（简化：假设手续费和运费共5元）
                fee = 5.0
                profit = target_price - source_price - fee
                profit_rate = (profit / source_price) * 100 if source_price > 0 else 0

                # 只返回满足最低利润率的机会
                if profit_rate >= min_profit_rate * 100:
                    # 风险评估
                    risk_level = "低"
                    if profit_rate > 50:
                        risk_level = "高"
                    elif profit_rate > 30:
                        risk_level = "中"

                    opportunities.append({
                        "source": source,
                        "target": target,
                        "buy_price": source_price,
                        "sell_price": target_price,
                        "price_diff": target_price - source_price,
                        "fee": fee,
                        "profit": profit,
                        "profit_rate": round(profit_rate, 2),
                        "expected_profit": round(profit, 2),
                        "risk_level": risk_level
                    })

        # 按利润率排序
        opportunities.sort(key=lambda x: x["profit_rate"], reverse=True)

        return opportunities

    def get_price_history(self, product_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        获取价格历史

        Args:
            product_id: 商品ID
            days: 天数

        Returns:
            历史记录列表
        """
        if product_id not in self.price_history:
            return []

        history = self.price_history[product_id]

        # 过滤指定天数的记录
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered_history = [
            h for h in history
            if datetime.strptime(h["date"], "%Y-%m-%d %H:%M:%S") > cutoff_date
        ]

        return filtered_history

    def analyze_trend(self, product_id: str, period: str = "7d") -> Dict[str, Any]:
        """
        分析价格趋势

        Args:
            product_id: 商品ID
            period: 分析周期（1d/7d/30d）

        Returns:
            趋势分析结果
        """
        # 获取历史数据
        days_map = {"1d": 1, "7d": 7, "30d": 30}
        days = days_map.get(period, 7)

        history = self.get_price_history(product_id, days)

        if len(history) < 2:
            return {
                "error": "数据不足",
                "min_data_points": 2,
                "current_data_points": len(history)
            }

        # 提取价格
        prices = [h["price"] for h in history]

        # 计算统计信息
        current_price = prices[-1]
        lowest_price = min(prices)
        highest_price = max(prices)
        average_price = sum(prices) / len(prices)

        # 分析趋势
        first_half = prices[:len(prices)//2]
        second_half = prices[len(prices)//2:]

        avg_first = sum(first_half) / len(first_half)
        avg_second = sum(second_half) / len(second_half)

        if avg_second > avg_first:
            trend = "上升"
            change_rate = ((avg_second - avg_first) / avg_first) * 100
        elif avg_second < avg_first:
            trend = "下降"
            change_rate = ((avg_second - avg_first) / avg_first) * 100
        else:
            trend = "稳定"
            change_rate = 0

        return {
            "product_id": product_id,
            "period": period,
            "current_price": round(current_price, 2),
            "lowest_price": round(lowest_price, 2),
            "highest_price": round(highest_price, 2),
            "average_price": round(average_price, 2),
            "trend": trend,
            "change_rate": round(change_rate, 2),
            "recommendation": self._get_trend_recommendation(trend, change_rate)
        }

    def _get_trend_recommendation(self, trend: str, change_rate: float) -> str:
        """获取趋势建议"""
        if trend == "上升":
            if change_rate > 20:
                return "价格快速上涨，建议立即采购或调整销售价"
            elif change_rate > 10:
                return "价格稳步上涨，建议考虑采购"
            else:
                return "价格小幅上涨，可继续观察"
        elif trend == "下降":
            if change_rate < -20:
                return "价格快速下降，建议等待或暂停销售"
            elif change_rate < -10:
                return "价格持续下降，建议谨慎采购"
            else:
                return "价格小幅下降，可适当采购"
        else:
            return "价格相对稳定，按正常节奏操作"

    def start_monitoring(self, interval: int = 300, callbacks: Optional[Dict[str, Callable]] = None):
        """
        开始监控

        Args:
            interval: 检查间隔（秒）
            callbacks: 回调函数字典
        """
        print(f"开始监控，间隔: {interval}秒")
        self.monitoring = True

        while self.monitoring:
            for product_id in self.products:
                try:
                    # 获取当前价格
                    price_info = self.get_current_price(product_id)

                    # 检查价格变化告警
                    if callbacks and "price_change" in callbacks:
                        if abs(price_info["change_rate"]) >= self.products[product_id].alert_threshold * 100:
                            callbacks["price_change"]({
                                "product_id": product_id,
                                "product_name": self.products[product_id].name,
                                "platform": self.products[product_id].platform,
                                "old_price": price_info["old_price"],
                                "new_price": price_info["current_price"],
                                "change_rate": price_info["change_rate"],
                                "direction": "上升" if price_info["change_rate"] > 0 else "下降"
                            })

                    # 检查套利机会
                    if callbacks and "arbitrage" in callbacks:
                        opportunities = self.find_arbitrage(product_id)
                        if opportunities:
                            best_opportunity = opportunities[0]
                            callbacks["arbitrage"]({
                                "product_id": product_id,
                                "product_name": self.products[product_id].name,
                                "profit_rate": best_opportunity["profit_rate"],
                                "expected_profit": best_opportunity["expected_profit"],
                                "source": best_opportunity["source"],
                                "target": best_opportunity["target"]
                            })

                except Exception as e:
                    print(f"监控商品{product_id}失败: {e}")

            print(f"完成一轮检查，等待{interval}秒...")
            time.sleep(interval)

    def stop_monitoring(self) -> None:
        """停止监控"""
        self.monitoring = False
        print("监控已停止")

    def _save_price_history(self, product_id: str, product: ProductInfo) -> None:
        """
        保存价格历史

        Args:
            product_id: 商品ID
            product: 商品信息
        """
        if product_id not in self.price_history:
            self.price_history[product_id] = []

        self.price_history[product_id].append({
            "date": product.last_update,
            "price": product.current_price,
            "stock": product.stock,
            "sales": product.sales
        })

        # 保留最近100条记录
        if len(self.price_history[product_id]) > 100:
            self.price_history[product_id] = self.price_history[product_id][-100:]

    def export_data(self, filename: str = "price_data.json") -> None:
        """
        导出数据

        Args:
            filename: 文件名
        """
        data = {
            "products": [asdict(p) for p in self.products.values()],
            "price_history": self.price_history
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"数据已导出到: {filename}")


def main():
    """主函数 - 演示使用"""
    print("=== 电商价格监控系统 ===\n")

    # 初始化监控器
    monitor = PriceMonitor(platforms=["taobao", "pinduoduo", "jd"])

    # 添加监控商品
    print("1. 添加监控商品...")
    monitor.add_product(
        product_id="p001",
        name="iPhone 15 Pro Max",
        url="https://item.taobao.com/item.htm?id=xxx",
        platform="taobao",
        target_price=8000,
        alert_threshold=0.03
    )

    monitor.add_product(
        product_id="p002",
        name="MacBook Air M3",
        url="https://item.jd.com/xxx",
        platform="jd",
        target_price=9000,
        alert_threshold=0.05
    )

    print()

    # 跨平台比价
    print("2. 跨平台比价...")
    comparison = monitor.compare_platforms("p001")
    print(f"   最低价平台: {comparison['lowest_price']['platform']}")
    print(f"   最低价: ¥{comparison['lowest_price']['price']}")
    print()

    # 发现套利机会
    print("3. 发现套利机会...")
    opportunities = monitor.find_arbitrage("p001", min_profit_rate=0.15)
    print(f"   套利机会数量: {len(opportunities)}")
    if opportunities:
        best = opportunities[0]
        print(f"   最佳机会: {best['source']} → {best['target']}")
        print(f"   利润率: {best['profit_rate']}%")
        print()

    # 分析趋势
    print("4. 分析价格趋势...")
    trend = monitor.analyze_trend("p001", period="7d")
    print(f"   当前价格: ¥{trend['current_price']}")
    print(f"   趋势: {trend['trend']}")
    print(f"   变化率: {trend['change_rate']}%")
    print(f"   建议: {trend['recommendation']}")
    print()

    print("=== 演示完成 ===")


if __name__ == "__main__":
    main()
