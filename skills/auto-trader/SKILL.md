# 自动化交易助手

自动化执行交易策略，支持电商、股票、加密货币等多种市场，实现智能买卖和利润最大化。

## 功能

- 多市场支持（电商、股票、加密货币、外汇）
- 策略编写和回测
- 自动下单执行
- 风险控制和仓位管理
- 止盈止损自动触发
- 套利机会发现
- 账户管理
- 收益分析
- 交易日志

## 使用方法

### 配置交易策略

```bash
cd /home/lejurobot/clawd/skills/auto-trader

# 添加交易策略
python3 trader.py add_strategy \
  --name "均线交叉策略" \
  --type stock \
  --symbol "600519.SH" \
  --params "short_ma=5,long_ma=20" \
  --position_size 0.1 \
  --stop_loss 0.05 \
  --take_profit 0.1

# 添加电商套利策略
python3 trader.py add_strategy \
  --name "拼多多-淘宝套利" \
  --type ecommerce \
  --product_id "123456" \
  --platforms "taobao,pinduoduo" \
  --min_profit 0.1 \
  --max_capital 5000
```

### 回测策略

```bash
# 回测股票策略
python3 trader.py backtest \
  --strategy_id strategy_123 \
  --start_date "2025-01-01" \
  --end_date "2026-01-31"

# 回测电商套利策略
python3 trader.py backtest_ecommerce \
  --strategy_id strategy_456 \
  --days 30
```

### 执行交易

```bash
# 启动自动交易
python3 trader.py start --strategy_id strategy_123

# 启动电商自动交易
python3 trader.py start_ecommerce \
  --strategy_id strategy_456 \
  --check_interval 300
```

### 查看交易记录

```bash
# 查看所有交易
python3 trader.py list_trades

# 查看特定策略的交易
python3 trader.py list_trades --strategy_id strategy_123

# 查看收益分析
python3 trader.py profit --strategy_id strategy_123
```

## 配置

配置文件：`config/trader.yaml`

```yaml
# 股票交易配置
stock:
  broker: "tushare"  # 数据源
  api_key: "your_api_key"
  trading_account:
    account_id: "your_account"
    cash: 100000
    positions: {}

# 电商交易配置
ecommerce:
  platforms:
    taobao:
      enabled: true
      api_key: "your_taobao_key"

    pinduoduo:
      enabled: true
      api_key: "your_pdd_key"

    jd:
      enabled: true
      api_key: "your_jd_key"

# 风险控制
risk_management:
  max_position_size: 0.3  # 单只股票最大仓位
  max_daily_loss: 0.05  # 最大日亏损
  max_drawdown: 0.15  # 最大回撤
  stop_loss_default: 0.05  # 默认止损
  take_profit_default: 0.1  # 默认止盈

# 交易设置
trading:
  trading_hours: "09:30-15:00"  # 交易时间
  order_type: "limit"  # 限价单
  slippage: 0.001  # 滑点容忍度
  commission: 0.0003  # 手续费率

# 通知设置
notifications:
  trade_executed: true
  profit_target: true
  stop_loss_triggered: true
  daily_summary: true
  channels: ["feishu", "email"]
```

## 策略类型

### 股票策略

```python
# 均线交叉策略
def ma_cross_strategy(data, short_ma=5, long_ma=20):
    if data['ma_short'] > data['ma_long'] and data['prev_ma_short'] <= data['prev_ma_long']:
        return "buy"  # 金叉，买入
    elif data['ma_short'] < data['ma_long'] and data['prev_ma_short'] >= data['prev_ma_long']:
        return "sell"  # 死叉，卖出
    return "hold"

# 突破策略
def breakout_strategy(data, period=20, threshold=0.02):
    if data['close'] > data['high_period'] * (1 + threshold):
        return "buy"
    elif data['close'] < data['low_period'] * (1 - threshold):
        return "sell"
    return "hold"
```

### 电商套利策略

```python
# 跨平台套利
def arbitrage_strategy(prices, min_profit=0.1):
    best_buy = min(prices, key=prices.get)
    best_sell = max(prices, key=prices.get)

    profit = (prices[best_sell] - prices[best_buy]) / prices[best_buy]

    if profit >= min_profit:
        return {
            "action": "arbitrage",
            "buy_platform": best_buy,
            "sell_platform": best_sell,
            "expected_profit": profit
        }
    return None
```

## 交易记录

交易记录保存在SQLite数据库中：

```sql
-- 交易表
CREATE TABLE trades (
    trade_id TEXT PRIMARY KEY,
    strategy_id TEXT,
    timestamp TEXT,
    symbol TEXT,
    action TEXT,  -- buy/sell
    price REAL,
    quantity REAL,
    amount REAL,
    profit REAL,
    status TEXT
)

-- 账户表
CREATE TABLE accounts (
    account_id TEXT PRIMARY KEY,
    cash REAL,
    market_value REAL,
    total_value REAL,
    profit REAL,
    profit_percent REAL
)
```

## 风险控制

- 最大仓位限制
- 止损自动触发
- 止盈自动触发
- 最大回撤控制
- 日亏损限制
- 流动性检查
- 交易时间限制

## 输出

- 交易记录
- 收益报告
- 策略表现
- 风险分析
- 资产配置

## API接口

```python
# 获取账户信息
GET /api/account

# 获取交易记录
GET /api/trades?strategy_id=xxx

# 获取策略表现
GET /api/strategy/performance?id=xxx

# 手动下单
POST /api/order
{
  "symbol": "600519.SH",
  "action": "buy",
  "quantity": 100,
  "price": 1500.0
}
```

## 注意事项

1. 交易有风险，请谨慎使用
2. 建议先回测验证策略
3. 控制仓位，分散投资
4. 设置合理的止损止盈
5. 定期检查和调整策略
6. 注意交易手续费和滑点
7. 遵守相关法律法规

## 赚钱价值

- 股票收益：通过策略交易获得收益（月1000-10000元）
- 电商套利：跨平台价差套利（月2000-10000元）
- 代交易服务：帮助他人执行策略（月5000-20000元）
- 策略销售：出售优质策略（月1000-5000元）

预期收益：月5000-30000元（取决于资金规模和策略表现）
