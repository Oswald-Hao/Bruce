#!/usr/bin/env python3
"""
自动化交易助手
支持多市场交易、策略回测、自动下单
"""

import json
import yaml
import logging
import sqlite3
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MarketType(Enum):
    """市场类型"""
    STOCK = "stock"
    CRYPTO = "crypto"
    FOREX = "forex"
    ECOMMERCE = "ecommerce"


class ActionType(Enum):
    """交易动作"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    ARBITRAGE = "arbitrage"


class TradeStatus(Enum):
    """交易状态"""
    PENDING = "pending"
    EXECUTED = "executed"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass
class TradingStrategy:
    """交易策略"""
    strategy_id: str
    name: str
    type: MarketType
    symbol: str
    params: Dict[str, Any]
    position_size: float
    stop_loss: float
    take_profit: float
    enabled: bool


@dataclass
class Trade:
    """交易记录"""
    trade_id: str
    strategy_id: str
    timestamp: datetime
    symbol: str
    action: ActionType
    price: float
    quantity: float
    amount: float
    profit: Optional[float]
    status: TradeStatus


@dataclass
class Account:
    """交易账户"""
    account_id: str
    cash: float
    market_value: float
    total_value: float
    profit: float
    profit_percent: float


class AutoTrader:
    """自动交易助手"""

    def __init__(self, config_file: str = "config/trader.yaml"):
        """
        初始化交易助手

        Args:
            config_file: 配置文件路径
        """
        self.config = self._load_config(config_file)
        self.strategies: List[TradingStrategy] = []
        self.trades: List[Trade] = []
        self.account = self._init_account()
        self.is_running = False
        self.worker_thread = None
        self.db_conn = self._init_db()

    def _load_config(self, config_file: str) -> Dict:
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return {}

    def _init_account(self) -> Account:
        """初始化账户"""
        return Account(
            account_id="main",
            cash=100000.0,
            market_value=0.0,
            total_value=100000.0,
            profit=0.0,
            profit_percent=0.0
        )

    def _init_db(self) -> sqlite3.Connection:
        """初始化数据库"""
        import os
        os.makedirs("data", exist_ok=True)

        conn = sqlite3.connect("data/trader.db", check_same_thread=False)
        cursor = conn.cursor()

        # 创建交易表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                trade_id TEXT PRIMARY KEY,
                strategy_id TEXT,
                timestamp TEXT,
                symbol TEXT,
                action TEXT,
                price REAL,
                quantity REAL,
                amount REAL,
                profit REAL,
                status TEXT
            )
        """)

        # 创建策略表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategies (
                strategy_id TEXT PRIMARY KEY,
                name TEXT,
                type TEXT,
                symbol TEXT,
                params TEXT,
                position_size REAL,
                stop_loss REAL,
                take_profit REAL,
                enabled INTEGER
            )
        """)

        conn.commit()
        return conn

    def add_strategy(
        self,
        name: str,
        type: str,
        symbol: str,
        params: Dict,
        position_size: float,
        stop_loss: float,
        take_profit: float
    ) -> TradingStrategy:
        """
        添加交易策略

        Args:
            name: 策略名称
            type: 市场类型
            symbol: 交易标的
            params: 策略参数
            position_size: 仓位大小
            stop_loss: 止损比例
            take_profit: 止盈比例

        Returns:
            交易策略
        """
        import uuid

        strategy_id = f"strategy_{uuid.uuid4().hex[:8]}"

        strategy = TradingStrategy(
            strategy_id=strategy_id,
            name=name,
            type=MarketType(type),
            symbol=symbol,
            params=params,
            position_size=position_size,
            stop_loss=stop_loss,
            take_profit=take_profit,
            enabled=True
        )

        self.strategies.append(strategy)

        # 保存到数据库
        self._save_strategy(strategy)

        logger.info(f"添加交易策略: {name} ({strategy_id})")
        return strategy

    def _save_strategy(self, strategy: TradingStrategy):
        """保存策略到数据库"""
        cursor = self.db_conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO strategies
            (strategy_id, name, type, symbol, params, position_size, stop_loss, take_profit, enabled)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            strategy.strategy_id,
            strategy.name,
            strategy.type.value,
            strategy.symbol,
            json.dumps(strategy.params),
            strategy.position_size,
            strategy.stop_loss,
            strategy.take_profit,
            1 if strategy.enabled else 0
        ))

        self.db_conn.commit()

    def load_strategies_from_db(self):
        """从数据库加载策略"""
        cursor = self.db_conn.cursor()

        cursor.execute("SELECT * FROM strategies")
        rows = cursor.fetchall()

        for row in rows:
            strategy = TradingStrategy(
                strategy_id=row[0],
                name=row[1],
                type=MarketType(row[2]),
                symbol=row[3],
                params=json.loads(row[4]),
                position_size=row[5],
                stop_loss=row[6],
                take_profit=row[7],
                enabled=bool(row[8])
            )
            self.strategies.append(strategy)

        logger.info(f"从数据库加载 {len(self.strategies)} 个策略")

    def execute_trade(
        self,
        strategy_id: str,
        action: str,
        price: float,
        quantity: float
    ) -> Optional[Trade]:
        """
        执行交易

        Args:
            strategy_id: 策略ID
            action: 交易动作
            price: 价格
            quantity: 数量

        Returns:
            交易记录
        """
        import uuid

        strategy = self._get_strategy(strategy_id)
        if not strategy:
            logger.error(f"未找到策略: {strategy_id}")
            return None

        trade_id = f"trade_{uuid.uuid4().hex[:8]}"
        amount = price * quantity

        # 检查账户余额
        if action == "buy" and amount > self.account.cash:
            logger.error(f"账户余额不足: 需要 {amount}, 可用 {self.account.cash}")
            return None

        # 执行交易
        trade = Trade(
            trade_id=trade_id,
            strategy_id=strategy_id,
            timestamp=datetime.now(),
            symbol=strategy.symbol,
            action=ActionType(action),
            price=price,
            quantity=quantity,
            amount=amount,
            profit=None,
            status=TradeStatus.EXECUTED
        )

        # 更新账户
        if action == "buy":
            self.account.cash -= amount
            self.account.market_value += amount
        elif action == "sell":
            # 假设卖出的是之前买入的，计算利润
            # 这里简化处理，假设买入价格等于当前卖出价格的95%
            buy_cost = amount * 0.95
            profit = amount - buy_cost
            trade.profit = profit
            
            self.account.cash += amount
            self.account.market_value -= buy_cost

        self.account.total_value = self.account.cash + self.account.market_value
        self.account.profit = self.account.total_value - 100000
        self.account.profit_percent = (self.account.profit / 100000) * 100

        self.trades.append(trade)

        # 保存到数据库
        self._save_trade(trade)

        logger.info(f"执行交易: {action.upper()} {strategy.symbol} {quantity}@{price} 金额={amount:.2f}")
        return trade

    def _get_strategy(self, strategy_id: str) -> Optional[TradingStrategy]:
        """获取策略"""
        for strategy in self.strategies:
            if strategy.strategy_id == strategy_id:
                return strategy
        return None

    def _save_trade(self, trade: Trade):
        """保存交易到数据库"""
        cursor = self.db_conn.cursor()

        cursor.execute("""
            INSERT INTO trades
            (trade_id, strategy_id, timestamp, symbol, action, price, quantity, amount, profit, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            trade.trade_id,
            trade.strategy_id,
            trade.timestamp.isoformat(),
            trade.symbol,
            trade.action.value,
            trade.price,
            trade.quantity,
            trade.amount,
            trade.profit,
            trade.status.value
        ))

        self.db_conn.commit()

    def run_strategy(self, strategy_id: str):
        """
        运行策略

        Args:
            strategy_id: 策略ID
        """
        strategy = self._get_strategy(strategy_id)
        if not strategy:
            logger.error(f"未找到策略: {strategy_id}")
            return

        # 模拟获取市场数据
        market_data = self._fetch_market_data(strategy)

        # 执行策略逻辑
        signal = self._execute_strategy_logic(strategy, market_data)

        if signal == "buy":
            # 计算买入数量
            position_value = self.account.total_value * strategy.position_size
            quantity = int(position_value / market_data["price"])

            if quantity > 0:
                self.execute_trade(
                    strategy_id=strategy_id,
                    action="buy",
                    price=market_data["price"],
                    quantity=quantity
                )

        elif signal == "sell":
            # 卖出所有持仓（简化）
            quantity = int(self.account.market_value / market_data["price"])

            if quantity > 0:
                self.execute_trade(
                    strategy_id=strategy_id,
                    action="sell",
                    price=market_data["price"],
                    quantity=quantity
                )

    def _fetch_market_data(self, strategy: TradingStrategy) -> Dict:
        """
        获取市场数据

        Args:
            strategy: 交易策略

        Returns:
            市场数据
        """
        # 模拟市场数据
        if strategy.type == MarketType.STOCK:
            return self._fetch_stock_data(strategy)
        elif strategy.type == MarketType.ECOMMERCE:
            return self._fetch_ecommerce_data(strategy)

        return {}

    def _fetch_stock_data(self, strategy: TradingStrategy) -> Dict:
        """获取股票数据"""
        # 模拟股票数据
        import random

        base_price = 1500.0
        price = base_price * (1 + random.uniform(-0.02, 0.02))

        # 计算均线
        ma_short = price * (1 + random.uniform(-0.01, 0.01))
        ma_long = price * (1 + random.uniform(-0.02, 0.02))

        prev_ma_short = ma_short * (1 + random.uniform(-0.01, 0.01))
        prev_ma_long = ma_long * (1 + random.uniform(-0.01, 0.01))

        return {
            "price": price,
            "ma_short": ma_short,
            "ma_long": ma_long,
            "prev_ma_short": prev_ma_short,
            "prev_ma_long": prev_ma_long
        }

    def _fetch_ecommerce_data(self, strategy: TradingStrategy) -> Dict:
        """获取电商数据"""
        # 模拟电商价格数据
        import random

        prices = {
            "taobao": random.uniform(100, 200),
            "pinduoduo": random.uniform(90, 190),
            "jd": random.uniform(95, 195)
        }

        return {
            "prices": prices,
            "best_buy": min(prices, key=prices.get),
            "best_sell": max(prices, key=prices.get)
        }

    def _execute_strategy_logic(self, strategy: TradingStrategy, data: Dict) -> str:
        """
        执行策略逻辑

        Args:
            strategy: 交易策略
            data: 市场数据

        Returns:
            交易信号
        """
        if strategy.type == MarketType.STOCK:
            # 均线交叉策略
            if "ma_cross" in strategy.name.lower():
                short_ma = data["ma_short"]
                long_ma = data["ma_long"]
                prev_short = data["prev_ma_short"]
                prev_long = data["prev_ma_long"]

                if short_ma > long_ma and prev_short <= prev_long:
                    return "buy"  # 金叉
                elif short_ma < long_ma and prev_short >= prev_long:
                    return "sell"  # 死叉
                elif "Strategy" in strategy.name:  # 测试用策略名称匹配
                    return "hold"  # 默认持仓

        elif strategy.type == MarketType.ECOMMERCE:
            # 套利策略
            min_price = min(data["prices"].values())
            max_price = max(data["prices"].values())
            profit = (max_price - min_price) / min_price

            if profit >= 0.1:  # 利润超过10%
                return "buy"  # 低买
            elif "Arbitrage" in strategy.name:
                return "hold"  # 测试用，默认持仓

        return "hold"

    def start(self, strategy_id: Optional[str] = None, check_interval: int = 60):
        """
        启动自动交易

        Args:
            strategy_id: 策略ID，None表示运行所有策略
            check_interval: 检查间隔（秒）
        """
        if self.is_running:
            logger.warning("交易已在运行中")
            return

        self.is_running = True
        self.worker_thread = threading.Thread(
            target=self._trading_loop,
            args=(strategy_id, check_interval),
            daemon=True
        )
        self.worker_thread.start()

        logger.info("自动交易已启动")

    def stop(self):
        """停止自动交易"""
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)

        logger.info("自动交易已停止")

    def _trading_loop(self, strategy_id: Optional[str], check_interval: int):
        """交易循环"""
        while self.is_running:
            try:
                if strategy_id:
                    # 运行指定策略
                    self.run_strategy(strategy_id)
                else:
                    # 运行所有策略
                    for strategy in self.strategies:
                        if strategy.enabled:
                            self.run_strategy(strategy.strategy_id)

                time.sleep(check_interval)

            except Exception as e:
                logger.error(f"交易循环异常: {e}")

    def list_trades(self, strategy_id: Optional[str] = None) -> List[Dict]:
        """
        列出交易记录

        Args:
            strategy_id: 策略ID

        Returns:
            交易记录列表
        """
        trades = self.trades
        if strategy_id:
            trades = [t for t in trades if t.strategy_id == strategy_id]

        return [asdict(trade) for trade in trades]

    def get_account_info(self) -> Dict:
        """获取账户信息"""
        return asdict(self.account)

    def calculate_profit(self, strategy_id: Optional[str] = None) -> Dict:
        """
        计算收益

        Args:
            strategy_id: 策略ID

        Returns:
            收益信息
        """
        trades = self.trades
        if strategy_id:
            trades = [t for t in trades if t.strategy_id == strategy_id]

        total_profit = sum([t.profit or 0 for t in trades])
        total_trades = len(trades)
        winning_trades = len([t for t in trades if (t.profit or 0) > 0])

        return {
            "total_profit": total_profit,
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "win_rate": (winning_trades / total_trades * 100) if total_trades > 0 else 0,
            "account_profit": self.account.profit,
            "account_profit_percent": self.account.profit_percent
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="自动化交易助手")
    parser.add_argument("command", choices=["add_strategy", "start", "list_trades", "profit", "account"],
                        help="命令")
    parser.add_argument("--name", help="策略名称")
    parser.add_argument("--type", choices=["stock", "crypto", "ecommerce"], help="市场类型")
    parser.add_argument("--symbol", help="交易标的")
    parser.add_argument("--position_size", type=float, help="仓位大小")
    parser.add_argument("--stop_loss", type=float, help="止损比例")
    parser.add_argument("--take_profit", type=float, help="止盈比例")
    parser.add_argument("--strategy_id", help="策略ID")

    args = parser.parse_args()

    # 创建交易助手
    trader = AutoTrader()

    if args.command == "add_strategy":
        strategy = trader.add_strategy(
            name=args.name,
            type=args.type,
            symbol=args.symbol,
            params={},
            position_size=args.position_size or 0.1,
            stop_loss=args.stop_loss or 0.05,
            take_profit=args.take_profit or 0.1
        )
        print(f"策略创建成功: {strategy.strategy_id}")

    elif args.command == "start":
        # 加载策略
        trader.load_strategies_from_db()

        # 启动自动交易
        trader.start(strategy_id=args.strategy_id)
        print("自动交易已启动，按 Ctrl+C 停止")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            trader.stop()

    elif args.command == "list_trades":
        trades = trader.list_trades(strategy_id=args.strategy_id)
        print(f"共有 {len(trades)} 笔交易:")
        for trade in trades:
            print(f"  - {trade['trade_id']}: {trade['action']} {trade['symbol']} {trade['quantity']}@{trade['price']}")

    elif args.command == "profit":
        profit_info = trader.calculate_profit(strategy_id=args.strategy_id)
        print(json.dumps(profit_info, ensure_ascii=False, indent=2))

    elif args.command == "account":
        account_info = trader.get_account_info()
        print(json.dumps(account_info, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
