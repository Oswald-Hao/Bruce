#!/usr/bin/env python3
"""
自动化交易助手测试用例
"""

import unittest
import os
import tempfile
import shutil
import time
from datetime import datetime

from trader import AutoTrader, TradingStrategy, Trade, Account, MarketType, ActionType, TradeStatus


class TestAutoTrader(unittest.TestCase):
    """测试自动交易助手"""

    def setUp(self):
        """设置测试环境"""
        self.test_dir = tempfile.mkdtemp()
        self.trader = AutoTrader(config_file="config/trader.yaml")

    def tearDown(self):
        """清理测试环境"""
        self.trader.stop()
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        if os.path.exists("data"):
            shutil.rmtree("data")

    def test_init(self):
        """测试初始化"""
        self.assertIsInstance(self.trader.strategies, list)
        self.assertIsInstance(self.trader.trades, list)
        self.assertIsInstance(self.trader.account, Account)
        self.assertFalse(self.trader.is_running)

    def test_add_strategy(self):
        """测试添加策略"""
        strategy = self.trader.add_strategy(
            name="测试策略",
            type="stock",
            symbol="600519.SH",
            params={},
            position_size=0.1,
            stop_loss=0.05,
            take_profit=0.1
        )

        self.assertIsInstance(strategy, TradingStrategy)
        self.assertEqual(strategy.name, "测试策略")
        self.assertEqual(strategy.type, MarketType.STOCK)
        self.assertTrue(strategy.enabled)

    def test_get_strategy(self):
        """测试获取策略"""
        strategy = self.trader.add_strategy(
            name="获取测试",
            type="stock",
            symbol="600519.SH",
            params={},
            position_size=0.1,
            stop_loss=0.05,
            take_profit=0.1
        )

        found_strategy = self.trader._get_strategy(strategy.strategy_id)
        self.assertIsNotNone(found_strategy)
        self.assertEqual(found_strategy.strategy_id, strategy.strategy_id)
        self.assertEqual(found_strategy.name, "获取测试")

    def test_fetch_stock_data(self):
        """测试获取股票数据"""
        strategy = TradingStrategy(
            strategy_id="strategy_test",
            name="测试",
            type=MarketType.STOCK,
            symbol="600519.SH",
            params={},
            position_size=0.1,
            stop_loss=0.05,
            take_profit=0.1,
            enabled=True
        )

        data = self.trader._fetch_stock_data(strategy)
        self.assertIsNotNone(data)
        self.assertIn("price", data)
        self.assertIn("ma_short", data)
        self.assertIn("ma_long", data)
        self.assertGreater(data["price"], 0)

    def test_fetch_ecommerce_data(self):
        """测试获取电商数据"""
        strategy = TradingStrategy(
            strategy_id="strategy_test",
            name="测试",
            type=MarketType.ECOMMERCE,
            symbol="product_123",
            params={},
            position_size=0.1,
            stop_loss=0.05,
            take_profit=0.1,
            enabled=True
        )

        data = self.trader._fetch_ecommerce_data(strategy)
        self.assertIsNotNone(data)
        self.assertIn("prices", data)
        self.assertIn("best_buy", data)
        self.assertIn("best_sell", data)
        self.assertEqual(len(data["prices"]), 3)

    def test_execute_strategy_logic_ma_cross(self):
        """测试均线交叉策略逻辑"""
        strategy = TradingStrategy(
            strategy_id="strategy_test",
            name="MA Cross Strategy",
            type=MarketType.STOCK,
            symbol="600519.SH",
            params={},
            position_size=0.1,
            stop_loss=0.05,
            take_profit=0.1,
            enabled=True
        )

        # 金叉信号
        data = {
            "ma_short": 1505.0,
            "ma_long": 1500.0,
            "prev_ma_short": 1495.0,
            "prev_ma_long": 1500.0
        }
        signal = self.trader._execute_strategy_logic(strategy, data)
        self.assertEqual(signal, "buy")

        # 死叉信号
        data = {
            "ma_short": 1495.0,
            "ma_long": 1500.0,
            "prev_ma_short": 1505.0,
            "prev_ma_long": 1500.0
        }
        signal = self.trader._execute_strategy_logic(strategy, data)
        self.assertEqual(signal, "sell")

    def test_execute_strategy_logic_arbitrage(self):
        """测试套利策略逻辑"""
        strategy = TradingStrategy(
            strategy_id="strategy_test",
            name="Arbitrage Strategy",
            type=MarketType.ECOMMERCE,
            symbol="product_123",
            params={},
            position_size=0.1,
            stop_loss=0.05,
            take_profit=0.1,
            enabled=True
        )

        # 利润超过10%
        data = {
            "prices": {
                "taobao": 100.0,
                "pinduoduo": 90.0,
                "jd": 110.0
            },
            "best_buy": "pinduoduo",
            "best_sell": "jd"
        }
        signal = self.trader._execute_strategy_logic(strategy, data)
        self.assertEqual(signal, "buy")

        # 利润不足10%
        data = {
            "prices": {
                "taobao": 100.0,
                "pinduoduo": 95.0,
                "jd": 105.0
            },
            "best_buy": "pinduoduo",
            "best_sell": "jd"
        }
        signal = self.trader._execute_strategy_logic(strategy, data)
        self.assertEqual(signal, "hold")

    def test_execute_trade_buy(self):
        """测试执行买入交易"""
        strategy = self.trader.add_strategy(
            name="买入测试",
            type="stock",
            symbol="600519.SH",
            params={},
            position_size=0.1,
            stop_loss=0.05,
            take_profit=0.1
        )

        trade = self.trader.execute_trade(
            strategy_id=strategy.strategy_id,
            action="buy",
            price=1500.0,
            quantity=10
        )

        self.assertIsNotNone(trade)
        self.assertEqual(trade.action, ActionType.BUY)
        self.assertEqual(trade.price, 1500.0)
        self.assertEqual(trade.quantity, 10)
        self.assertEqual(trade.amount, 15000.0)
        self.assertEqual(trade.status, TradeStatus.EXECUTED)

        # 检查账户更新
        self.assertEqual(self.trader.account.cash, 85000.0)
        self.assertEqual(self.trader.account.market_value, 15000.0)

    def test_execute_trade_sell(self):
        """测试执行卖出交易"""
        strategy = self.trader.add_strategy(
            name="卖出测试",
            type="stock",
            symbol="600519.SH",
            params={},
            position_size=0.1,
            stop_loss=0.05,
            take_profit=0.1
        )

        # 先买入
        self.trader.execute_trade(
            strategy_id=strategy.strategy_id,
            action="buy",
            price=1500.0,
            quantity=10
        )

        # 再卖出
        trade = self.trader.execute_trade(
            strategy_id=strategy.strategy_id,
            action="sell",
            price=1550.0,
            quantity=10
        )

        self.assertIsNotNone(trade)
        self.assertEqual(trade.action, ActionType.SELL)
        self.assertEqual(trade.price, 1550.0)
        self.assertEqual(trade.quantity, 10)
        self.assertEqual(trade.amount, 15500.0)

        # 检查账户更新
        self.assertEqual(self.trader.account.cash, 100500.0)
        self.assertEqual(self.trader.account.market_value, 0.0)
        self.assertEqual(self.trader.account.profit, 500.0)

    def test_execute_trade_insufficient_funds(self):
        """测试资金不足的情况"""
        strategy = self.trader.add_strategy(
            name="资金测试",
            type="stock",
            symbol="600519.SH",
            params={},
            position_size=0.1,
            stop_loss=0.05,
            take_profit=0.1
        )

        trade = self.trader.execute_trade(
            strategy_id=strategy.strategy_id,
            action="buy",
            price=1500.0,
            quantity=1000  # 超过账户余额
        )

        self.assertIsNone(trade)

    def test_list_trades(self):
        """测试列出交易"""
        strategy = self.trader.add_strategy(
            name="列表测试",
            type="stock",
            symbol="600519.SH",
            params={},
            position_size=0.1,
            stop_loss=0.05,
            take_profit=0.1
        )

        self.trader.execute_trade(
            strategy_id=strategy.strategy_id,
            action="buy",
            price=1500.0,
            quantity=10
        )

        trades = self.trader.list_trades()
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0]["action"], "buy")

    def test_list_trades_by_strategy(self):
        """测试按策略列出交易"""
        strategy1 = self.trader.add_strategy(
            name="策略1",
            type="stock",
            symbol="600519.SH",
            params={},
            position_size=0.1,
            stop_loss=0.05,
            take_profit=0.1
        )

        strategy2 = self.trader.add_strategy(
            name="策略2",
            type="stock",
            symbol="000001.SZ",
            params={},
            position_size=0.1,
            stop_loss=0.05,
            take_profit=0.1
        )

        self.trader.execute_trade(
            strategy_id=strategy1.strategy_id,
            action="buy",
            price=1500.0,
            quantity=10
        )

        self.trader.execute_trade(
            strategy_id=strategy2.strategy_id,
            action="buy",
            price=10.0,
            quantity=1000
        )

        trades1 = self.trader.list_trades(strategy_id=strategy1.strategy_id)
        trades2 = self.trader.list_trades(strategy_id=strategy2.strategy_id)

        self.assertEqual(len(trades1), 1)
        self.assertEqual(len(trades2), 1)
        self.assertEqual(trades1[0]["symbol"], "600519.SH")
        self.assertEqual(trades2[0]["symbol"], "000001.SZ")

    def test_get_account_info(self):
        """测试获取账户信息"""
        account_info = self.trader.get_account_info()

        self.assertIn("account_id", account_info)
        self.assertIn("cash", account_info)
        self.assertIn("market_value", account_info)
        self.assertIn("total_value", account_info)
        self.assertIn("profit", account_info)
        self.assertEqual(account_info["cash"], 100000.0)
        self.assertEqual(account_info["market_value"], 0.0)

    def test_calculate_profit(self):
        """测试计算收益"""
        strategy = self.trader.add_strategy(
            name="收益测试",
            type="stock",
            symbol="600519.SH",
            params={},
            position_size=0.1,
            stop_loss=0.05,
            take_profit=0.1
        )

        self.trader.execute_trade(
            strategy_id=strategy.strategy_id,
            action="buy",
            price=1500.0,
            quantity=10
        )

        self.trader.execute_trade(
            strategy_id=strategy.strategy_id,
            action="sell",
            price=1550.0,
            quantity=10
        )

        profit_info = self.trader.calculate_profit(strategy_id=strategy.strategy_id)

        self.assertEqual(profit_info["account_profit"], 500.0)
        self.assertEqual(profit_info["total_trades"], 2)
        self.assertGreater(profit_info["account_profit_percent"], 0)

    def test_trading_loop(self):
        """测试交易循环"""
        strategy = self.trader.add_strategy(
            name="循环测试",
            type="stock",
            symbol="600519.SH",
            params={},
            position_size=0.1,
            stop_loss=0.05,
            take_profit=0.1
        )

        # 启动交易
        self.trader.start(strategy_id=strategy.strategy_id, check_interval=1)
        self.assertTrue(self.trader.is_running)

        # 等待几秒，让策略执行几次
        time.sleep(3)

        # 停止交易
        self.trader.stop()
        self.assertFalse(self.trader.is_running)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestAutoTrader))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 返回测试结果
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
