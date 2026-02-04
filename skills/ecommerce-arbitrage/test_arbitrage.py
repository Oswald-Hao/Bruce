#!/usr/bin/env python3
"""
测试电商套利系统
"""

import sys
import json
from arbitrage import ArbitrageSystem, ArbitrageAnalyzer, PriceMonitor


def test_price_monitor():
    """测试价格监控"""
    print("\n" + "=" * 60)
    print("测试1: 价格监控器")
    print("=" * 60)

    monitor = PriceMonitor()

    # 测试淘宝搜索
    results = monitor.search_taobao("iPhone")
    print(f"✓ 淘宝搜索返回 {len(results)} 个结果")
    assert len(results) > 0, "淘宝搜索应该返回结果"
    assert all("platform" in p for p in results), "结果应包含platform字段"

    # 测试拼多多搜索
    results = monitor.search_pinduoduo("AirPods")
    print(f"✓ 拼多多搜索返回 {len(results)} 个结果")
    assert len(results) > 0, "拼多多搜索应该返回结果"

    # 测试京东搜索
    results = monitor.search_jd("MacBook")
    print(f"✓ 京东搜索返回 {len(results)} 个结果")
    assert len(results) > 0, "京东搜索应该返回结果"

    # 测试全平台搜索
    results = monitor.search_all_platforms("Nike")
    print(f"✓ 全平台搜索返回 {len(results)} 个结果")
    assert len(results) > 0, "全平台搜索应该返回结果"

    print("✓ 价格监控器测试通过！\n")


def test_arbitrage_analyzer():
    """测试套利分析器"""
    print("\n" + "=" * 60)
    print("测试2: 套利分析器")
    print("=" * 60)

    analyzer = ArbitrageAnalyzer(min_profit_rate=10.0)

    # 创建测试数据
    products = [
        {"platform": "拼多多", "title": "iPhone 15 Pro", "price": 7000},
        {"platform": "淘宝", "title": "iPhone 15 Pro", "price": 7800},
        {"platform": "京东", "title": "iPhone 15 Pro", "price": 7700},
        {"platform": "拼多多", "title": "AirPods Pro", "price": 1500},
        {"platform": "淘宝", "title": "AirPods Pro", "price": 1800},
        {"platform": "京东", "title": "MacBook Pro", "price": 12000},
        {"platform": "淘宝", "title": "MacBook Pro", "price": 11500},  # 低价
    ]

    # 测试套利发现
    opportunities = analyzer.find_arbitrage(products)
    print(f"✓ 发现 {len(opportunities)} 个套利机会")

    # 验证结果
    for opp in opportunities:
        assert "buy" in opp, "套利机会应包含buy字段"
        assert "sell" in opp, "套利机会应包含sell字段"
        assert "profit" in opp, "套利机会应包含profit字段"
        assert "profit_rate" in opp, "套利机会应包含profit_rate字段"
        assert opp["profit_rate"] >= 10.0, "利润率应>=10%"

        print(f"  - {opp['buy']['title']}: 买入¥{opp['buy']['price']}, 卖出¥{opp['sell']['price']}, 利润{opp['profit_rate']:.1f}%")

    assert len(opportunities) >= 2, "应该至少发现2个套利机会"

    print("✓ 套利分析器测试通过！\n")


def test_arbitrage_system():
    """测试完整系统"""
    print("\n" + "=" * 60)
    print("测试3: 完整系统")
    print("=" * 60)

    system = ArbitrageSystem()

    # 测试关键词监控
    keywords = ["iPhone", "AirPods"]
    opportunities = system.monitor_keywords(keywords)

    print(f"✓ 监控 {len(keywords)} 个关键词，发现 {len(opportunities)} 个机会")

    # 测试保存功能
    if opportunities:
        system.save_opportunities(opportunities, "test_opportunities.json")

        # 验证文件存在
        import os
        assert os.path.exists("test_opportunities.json"), "应该创建保存文件"

        # 验证文件内容
        with open("test_opportunities.json", "r") as f:
            saved_data = json.load(f)
        assert len(saved_data) == len(opportunities), "保存的数据应一致"

        print("✓ 保存功能正常")

    print("✓ 完整系统测试通过！\n")


def test_edge_cases():
    """测试边界情况"""
    print("\n" + "=" * 60)
    print("测试4: 边界情况")
    print("=" * 60)

    analyzer = ArbitrageAnalyzer(min_profit_rate=10.0)

    # 测试无商品
    opportunities = analyzer.find_arbitrage([])
    assert len(opportunities) == 0, "无商品时应返回空列表"
    print("✓ 无商品情况正常")

    # 测试单个商品
    products = [{"platform": "淘宝", "title": "iPhone", "price": 7000}]
    opportunities = analyzer.find_arbitrage(products)
    assert len(opportunities) == 0, "单个商品应无套利机会"
    print("✓ 单个商品情况正常")

    # 测试低利润率
    products = [
        {"platform": "拼多多", "title": "iPhone", "price": 7000},
        {"platform": "淘宝", "title": "iPhone", "price": 7200},  # 利润率<3%
    ]
    opportunities = analyzer.find_arbitrage(products)
    assert len(opportunities) == 0, "低利润率应被过滤"
    print("✓ 低利润率过滤正常")

    # 测试相似度判断
    assert analyzer._is_similar("iPhone 15 Pro", "iPhone 15 Pro Max") == True
    assert analyzer._is_similar("iPhone", "MacBook") == False
    print("✓ 相似度判断正常")

    print("✓ 边界情况测试通过！\n")


def cleanup():
    """清理测试文件"""
    import os

    test_files = [
        "test_opportunities.json",
        "arbitrage_opportunities.json",
    ]

    for f in test_files:
        if os.path.exists(f):
            os.remove(f)
            print(f"✓ 清理测试文件: {f}")


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("电商套利系统 - 测试套件")
    print("=" * 60)

    try:
        test_price_monitor()
        test_arbitrage_analyzer()
        test_arbitrage_system()
        test_edge_cases()

        print("\n" + "=" * 60)
        print("✓✓✓ 所有测试通过！ ✓✓✓")
        print("=" * 60 + "\n")

        return True

    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}\n")
        return False

    except Exception as e:
        print(f"\n❌ 测试出错: {e}\n")
        import traceback
        traceback.print_exc()
        return False

    finally:
        cleanup()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
