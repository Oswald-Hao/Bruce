# Financial Analysis - 金融数据分析系统

## 功能描述

提供全面的金融数据分析能力，包括股票分析、技术指标计算、趋势预测和投资建议生成，帮助做出更明智的投资决策。

## 核心功能

### 1. 技术指标分析
- MACD（移动平均收敛发散指标）
- RSI（相对强弱指数）
- KDJ（随机指标）
- MA（移动平均线）
- BOLL（布林线）
- MACD
- 成交量分析

### 2. 趋势分析
- 上涨/下跌/震荡趋势判断
- 支撑位和阻力位识别
- 买卖信号生成
- 趋势强度评估

### 3. 风险评估
- 仓位建议
- 止损点计算
- 风险收益比分析
- 波动率评估

### 4. 投资建议
- 买入/持有/卖出建议
- 目标价位
- 持仓时间建议
- 投资组合优化

## 工具说明

### financial-analyzer.py

核心分析引擎，提供所有金融分析功能。

**使用方法：**

```bash
# 分析单只股票
python financial-analyzer.py analyze --symbol AAPL --days 30

# 技术指标分析
python financial-analyzer.py indicators --symbol AAPL

# 趋势分析
python financial-analyzer.py trend --symbol AAPL

# 投资建议
python financial-analyzer.py suggest --symbol AAPL

# 风险评估
python financial-analyzer.py risk --symbol AAPL

# 批量分析多只股票
python financial-analyzer.py batch --symbols AAPL,MSFT,GOOGL

# 回测策略
python financial-analyzer.py backtest --symbol AAPL --strategy macd
```

### 主要函数

```python
# 技术指标
calculate_macd(prices)  # 计算MACD
calculate_rsi(prices)   # 计算RSI
calculate_kdj(prices)   # 计算KDJ
calculate_ma(prices, period)  # 计算移动平均线
calculate_boll(prices)   # 计算布林线

# 趋势分析
analyze_trend(prices)   # 趋势分析
find_support_resistance(prices)  # 支撑阻力位
generate_signal(indicators)  # 买卖信号

# 风险评估
calculate_risk(prices)   # 风险评估
suggest_position(risk_level)  # 仓位建议
calculate_stop_loss(price, risk_level)  # 止损点

# 投资建议
generate_suggestion(data)  # 生成投资建议
optimize_portfolio(stocks)  # 投资组合优化
```

## 数据源

支持多种数据源：
- Yahoo Finance
- Alpha Vantage
- 本地CSV/JSON文件
- API数据

## 输出格式

- JSON（程序化处理）
- Markdown（人类可读）
- HTML（可视化）
- CSV（Excel导入）

## 注意事项

1. **模拟数据：** 当前使用模拟数据，生产环境需要接入真实数据源
2. **风险提示：** 所有分析仅供参考，投资有风险
3. **合规性：** 确保符合金融监管要求

## 应用场景

- 个人投资分析
- 量化交易策略回测
- 投资组合管理
- 风险评估
- 投资决策辅助

## 赚钱价值

1. **直接赚钱：** 通过精准分析获得投资收益
2. **量化交易：** 开发自动化交易策略
3. **投资咨询：** 提供专业的投资建议服务
4. **教育价值：** 金融知识普及和培训
