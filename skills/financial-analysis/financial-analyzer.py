#!/usr/bin/env python3
"""
Financial Analysis System - 金融数据分析系统
提供股票分析、技术指标计算、趋势预测和投资建议生成
"""

import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import math
import random


class StockData:
    """股票数据容器"""

    def __init__(self, symbol: str, data: List[Dict]):
        self.symbol = symbol
        self.data = data

    @property
    def dates(self) -> List[str]:
        return [d['date'] for d in self.data]

    @property
    def prices(self) -> List[float]:
        return [d['close'] for d in self.data]

    @property
    def opens(self) -> List[float]:
        return [d['open'] for d in self.data]

    @property
    def highs(self) -> List[float]:
        return [d['high'] for d in self.data]

    @property
    def lows(self) -> List[float]:
        return [d['low'] for d in self.data]

    @property
    def volumes(self) -> List[int]:
        return [d['volume'] for d in self.data]


class TechnicalIndicators:
    """技术指标计算器"""

    @staticmethod
    def calculate_sma(prices: List[float], period: int = 20) -> List[float]:
        """计算简单移动平均线"""
        sma = []
        for i in range(len(prices)):
            if i < period - 1:
                sma.append(None)
            else:
                avg = sum(prices[i - period + 1:i + 1]) / period
                sma.append(avg)
        return sma

    @staticmethod
    def calculate_ema(prices: List[float], period: int = 12) -> List[float]:
        """计算指数移动平均线"""
        ema = []
        multiplier = 2 / (period + 1)

        for i in range(len(prices)):
            if i == 0:
                ema.append(prices[0])
            else:
                ema_val = (prices[i] - ema[i - 1]) * multiplier + ema[i - 1]
                ema.append(ema_val)
        return ema

    @staticmethod
    def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """计算MACD指标"""
        ema_fast = TechnicalIndicators.calculate_ema(prices, fast)
        ema_slow = TechnicalIndicators.calculate_ema(prices, slow)

        macd_line = [f - s if f is not None and s is not None else None
                    for f, s in zip(ema_fast, ema_slow)]

        # 去除None值
        macd_values = [v for v in macd_line if v is not None]
        signal_line = TechnicalIndicators.calculate_ema(macd_values, signal)

        # 补齐长度
        signal_full = [None] * (len(macd_line) - len(signal_line)) + signal_line

        histogram = [m - s if m is not None and s is not None else None
                    for m, s in zip(macd_line, signal_full)]

        return {
            'macd': macd_line,
            'signal': signal_full,
            'histogram': histogram
        }

    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> List[float]:
        """计算RSI相对强弱指数"""
        rsi = []
        gains = []
        losses = []

        for i in range(1, len(prices)):
            change = prices[i] - prices[i - 1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        for i in range(len(prices)):
            if i < period:
                rsi.append(None)
            else:
                avg_gain = sum(gains[i - period:i]) / period
                avg_loss = sum(losses[i - period:i]) / period

                if avg_loss == 0:
                    rsi.append(100)
                else:
                    rs = avg_gain / avg_loss
                    rsi_val = 100 - (100 / (1 + rs))
                    rsi.append(rsi_val)

        return rsi

    @staticmethod
    def calculate_kdj(highs: List[float], lows: List[float], closes: List[float],
                     period: int = 9) -> Dict:
        """计算KDJ随机指标"""
        k_values = []
        d_values = []
        j_values = []

        prev_k = 50
        prev_d = 50

        for i in range(len(closes)):
            if i < period - 1:
                k_values.append(None)
                d_values.append(None)
                j_values.append(None)
            else:
                high_n = max(highs[i - period + 1:i + 1])
                low_n = min(lows[i - period + 1:i + 1])

                if high_n == low_n:
                    rsv = 50
                else:
                    rsv = ((closes[i] - low_n) / (high_n - low_n)) * 100

                k = (2 * prev_k + rsv) / 3
                d = (2 * prev_d + k) / 3
                j = 3 * k - 2 * d

                k_values.append(k)
                d_values.append(d)
                j_values.append(j)

                prev_k = k
                prev_d = d

        return {'k': k_values, 'd': d_values, 'j': j_values}

    @staticmethod
    def calculate_boll(prices: List[float], period: int = 20, std_dev: int = 2) -> Dict:
        """计算布林线"""
        sma = TechnicalIndicators.calculate_sma(prices, period)

        upper_band = []
        lower_band = []

        for i in range(len(prices)):
            if i < period - 1:
                upper_band.append(None)
                lower_band.append(None)
            else:
                std = math.sqrt(sum((x - sma[i]) ** 2 for x in prices[i - period + 1:i + 1]) / period)
                upper_band.append(sma[i] + std_dev * std)
                lower_band.append(sma[i] - std_dev * std)

        return {
            'middle': sma,
            'upper': upper_band,
            'lower': lower_band
        }


class TrendAnalyzer:
    """趋势分析器"""

    @staticmethod
    def analyze_trend(prices: List[float]) -> Dict:
        """分析价格趋势"""
        if len(prices) < 10:
            return {'trend': 'unknown', 'strength': 0}

        # 计算短期和长期趋势
        short_ma = sum(prices[-5:]) / 5
        long_ma = sum(prices[-20:]) / 20

        # 计算斜率
        if len(prices) >= 5:
            slope = (prices[-1] - prices[-5]) / 5
        else:
            slope = 0

        # 判断趋势
        if short_ma > long_ma and slope > 0:
            trend = 'uptrend'  # 上涨趋势
            strength = min(1, slope / (prices[-1] * 0.01))  # 归一化强度
        elif short_ma < long_ma and slope < 0:
            trend = 'downtrend'  # 下跌趋势
            strength = min(1, abs(slope) / (prices[-1] * 0.01))
        else:
            trend = 'sideways'  # 震荡趋势
            strength = 0.5

        return {
            'trend': trend,
            'strength': round(strength * 100, 2),
            'short_ma': round(short_ma, 2),
            'long_ma': round(long_ma, 2),
            'slope': round(slope, 2)
        }

    @staticmethod
    def find_support_resistance(prices: List[float]) -> Dict:
        """寻找支撑位和阻力位"""
        if len(prices) < 10:
            return {'support': [], 'resistance': []}

        highs = sorted(prices, reverse=True)[:5]
        lows = sorted(prices)[:5]

        # 寻找相对低点作为支撑位
        support_levels = []
        for i in range(2, len(prices) - 2):
            if prices[i] == min(prices[i-2:i+3]):
                support_levels.append(prices[i])

        support_levels = sorted(list(set(support_levels)))[:3]

        # 寻找相对高点作为阻力位
        resistance_levels = []
        for i in range(2, len(prices) - 2):
            if prices[i] == max(prices[i-2:i+3]):
                resistance_levels.append(prices[i])

        resistance_levels = sorted(list(set(resistance_levels)), reverse=True)[:3]

        return {
            'support': [round(s, 2) for s in support_levels],
            'resistance': [round(r, 2) for r in resistance_levels]
        }

    @staticmethod
    def generate_signal(prices: List[float], indicators: Dict) -> Dict:
        """生成买卖信号"""
        macd = indicators.get('macd', {})
        rsi = indicators.get('rsi', [])
        trend = indicators.get('trend', {})

        signals = []
        current_price = prices[-1] if prices else 0

        # MACD信号
        if macd:
            macd_hist = macd.get('histogram', [])
            if macd_hist and len(macd_hist) > 1:
                if macd_hist[-2] < 0 and macd_hist[-1] > 0:
                    signals.append(('buy', 'MACD金叉', 'strong'))
                elif macd_hist[-2] > 0 and macd_hist[-1] < 0:
                    signals.append(('sell', 'MACD死叉', 'strong'))

        # RSI信号
        if rsi:
            current_rsi = rsi[-1] if rsi else 50
            if current_rsi < 30:
                signals.append(('buy', f'RSI超卖({current_rsi:.1f})', 'medium'))
            elif current_rsi > 70:
                signals.append(('sell', f'RSI超买({current_rsi:.1f})', 'medium'))

        # 趋势信号
        trend_type = trend.get('trend', '')
        if trend_type == 'uptrend':
            signals.append(('buy', '上涨趋势确认', 'weak'))
        elif trend_type == 'downtrend':
            signals.append(('sell', '下跌趋势确认', 'weak'))

        # 综合判断
        buy_count = sum(1 for s in signals if s[0] == 'buy')
        sell_count = sum(1 for s in signals if s[0] == 'sell')

        if buy_count > sell_count:
            final_signal = 'buy'
            confidence = min(95, 50 + (buy_count - sell_count) * 15)
        elif sell_count > buy_count:
            final_signal = 'sell'
            confidence = min(95, 50 + (sell_count - buy_count) * 15)
        else:
            final_signal = 'hold'
            confidence = 50

        return {
            'signal': final_signal,
            'confidence': confidence,
            'details': signals,
            'current_price': round(current_price, 2)
        }


class RiskAnalyzer:
    """风险评估器"""

    @staticmethod
    def calculate_volatility(prices: List[float]) -> float:
        """计算波动率"""
        if len(prices) < 2:
            return 0

        returns = []
        for i in range(1, len(prices)):
            ret = (prices[i] - prices[i - 1]) / prices[i - 1]
            returns.append(ret)

        avg_return = sum(returns) / len(returns)
        variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
        volatility = math.sqrt(variance)

        return round(volatility * 100, 2)  # 百分比

    @staticmethod
    def assess_risk(prices: List[float], volatility: float) -> Dict:
        """评估风险水平"""
        risk_level = 'low'
        risk_score = 0

        if volatility > 5:
            risk_level = 'high'
            risk_score = min(100, volatility * 10)
        elif volatility > 2:
            risk_level = 'medium'
            risk_score = volatility * 10
        else:
            risk_level = 'low'
            risk_score = volatility * 10

        # 计算最大回撤
        max_drawdown = 0
        peak = prices[0]

        for price in prices:
            if price > peak:
                peak = price
            else:
                drawdown = (peak - price) / peak
                if drawdown > max_drawdown:
                    max_drawdown = drawdown

        return {
            'risk_level': risk_level,
            'risk_score': round(risk_score, 2),
            'volatility': volatility,
            'max_drawdown': round(max_drawdown * 100, 2)
        }

    @staticmethod
    def suggest_position(risk_level: str) -> float:
        """建议仓位"""
        if risk_level == 'low':
            return 0.3  # 30%
        elif risk_level == 'medium':
            return 0.2  # 20%
        else:
            return 0.1  # 10%

    @staticmethod
    def calculate_stop_loss(current_price: float, risk_level: str) -> float:
        """计算止损点"""
        if risk_level == 'low':
            stop_loss_percent = 0.08  # 8%
        elif risk_level == 'medium':
            stop_loss_percent = 0.05  # 5%
        else:
            stop_loss_percent = 0.03  # 3%

        return round(current_price * (1 - stop_loss_percent), 2)


class InvestmentAdvisor:
    """投资建议生成器"""

    @staticmethod
    def generate_suggestion(data: Dict) -> Dict:
        """生成投资建议"""
        signal = data.get('signal', 'hold')
        confidence = data.get('confidence', 50)
        risk = data.get('risk', {})
        trend = data.get('trend', {})
        support_resistance = data.get('support_resistance', {})

        current_price = data.get('current_price', 0)

        # 建议类型
        if signal == 'buy' and confidence > 60:
            action = '强烈建议买入'
            position = '中等仓位（20-30%）'
            hold_time = '短期至中期'
        elif signal == 'buy':
            action = '建议买入'
            position = '小仓位（10-20%）'
            hold_time = '短期'
        elif signal == 'sell' and confidence > 60:
            action = '强烈建议卖出'
            position = '减仓至0-10%'
            hold_time = '立即退出'
        elif signal == 'sell':
            action = '建议卖出'
            position = '减仓至10-20%'
            hold_time = '短期'
        else:
            action = '建议持有'
            position = '保持当前仓位'
            hold_time = '观望'

        # 目标价位
        support = support_resistance.get('support', [])
        resistance = support_resistance.get('resistance', [])

        target_price = resistance[0] if resistance else current_price * 1.1
        stop_loss = support[0] if support else current_price * 0.95

        # 风险收益比
        potential_profit = target_price - current_price
        potential_loss = current_price - stop_loss
        risk_reward = potential_profit / potential_loss if potential_loss > 0 else 0

        return {
            'action': action,
            'signal': signal,
            'confidence': confidence,
            'position': position,
            'hold_time': hold_time,
            'target_price': round(target_price, 2),
            'stop_loss': round(stop_loss, 2),
            'risk_reward_ratio': round(risk_reward, 2),
            'reason': InvestmentAdvisor._generate_reason(data),
            'warnings': InvestmentAdvisor._generate_warnings(data)
        }

    @staticmethod
    def _generate_reason(data: Dict) -> str:
        """生成理由"""
        reasons = []

        signal = data.get('signal', '')
        trend = data.get('trend', {}).get('trend', '')
        risk_level = data.get('risk', {}).get('risk_level', '')

        if signal == 'buy':
            if trend == 'uptrend':
                reasons.append('处于上涨趋势中')
            reasons.append('技术指标显示买入信号')
        elif signal == 'sell':
            if trend == 'downtrend':
                reasons.append('处于下跌趋势中')
            reasons.append('技术指标显示卖出信号')

        if risk_level == 'low':
            reasons.append('风险较低，可控')
        elif risk_level == 'high':
            reasons.append('风险较高，需谨慎')

        return '；'.join(reasons) if reasons else '综合分析建议'

    @staticmethod
    def _generate_warnings(data: Dict) -> List[str]:
        """生成风险提示"""
        warnings = []

        risk_level = data.get('risk', {}).get('risk_level', '')
        volatility = data.get('risk', {}).get('volatility', 0)

        if risk_level == 'high':
            warnings.append('高风险警告：波动较大，建议小仓位')
        if volatility > 3:
            warnings.append(f'高波动警告：日波动率{volatility}%，注意风险控制')

        warnings.append('投资有风险，建议结合基本面分析')
        warnings.append('本建议仅供参考，不构成投资保证')

        return warnings


class DataGenerator:
    """模拟数据生成器"""

    @staticmethod
    def generate_stock_data(symbol: str, days: int = 30) -> List[Dict]:
        """生成模拟股票数据"""
        base_price = random.uniform(50, 200)
        data = []

        for i in range(days):
            date = (datetime.now() - timedelta(days=days - i)).strftime('%Y-%m-%d')

            # 随机波动
            change_pct = random.uniform(-0.05, 0.05)
            if i > 0:
                base_price = data[-1]['close'] * (1 + change_pct)

            # 生成OHLC数据
            high = base_price * random.uniform(1.0, 1.02)
            low = base_price * random.uniform(0.98, 1.0)
            open_price = low + random.uniform(0, high - low)
            close = low + random.uniform(0, high - low)

            # 确保open/close在high/low之间
            high = max(high, open_price, close)
            low = min(low, open_price, close)

            volume = random.randint(1000000, 10000000)

            data.append({
                'date': date,
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close, 2),
                'volume': volume
            })

        return data


def analyze_stock(symbol: str, days: int = 30) -> Dict:
    """分析股票"""
    data = DataGenerator.generate_stock_data(symbol, days)
    stock = StockData(symbol, data)

    # 计算技术指标
    indicators = TechnicalIndicators()

    macd = indicators.calculate_macd(stock.prices)
    rsi = indicators.calculate_rsi(stock.prices)
    kdj = indicators.calculate_kdj(stock.highs, stock.lows, stock.prices)
    boll = indicators.calculate_boll(stock.prices)

    # 趋势分析
    trend_analyzer = TrendAnalyzer()
    trend = trend_analyzer.analyze_trend(stock.prices)
    support_resistance = trend_analyzer.find_support_resistance(stock.prices)

    # 生成信号
    signal = trend_analyzer.generate_signal(stock.prices, {
        'macd': macd,
        'rsi': rsi,
        'trend': trend
    })

    # 风险评估
    risk_analyzer = RiskAnalyzer()
    volatility = risk_analyzer.calculate_volatility(stock.prices)
    risk = risk_analyzer.assess_risk(stock.prices, volatility)

    # 投资建议
    advisor = InvestmentAdvisor()
    suggestion = advisor.generate_suggestion({
        'signal': signal['signal'],
        'confidence': signal['confidence'],
        'risk': risk,
        'trend': trend,
        'support_resistance': support_resistance,
        'current_price': signal['current_price']
    })

    return {
        'symbol': symbol,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'data': data,
        'indicators': {
            'macd': macd,
            'rsi': rsi,
            'kdj': kdj,
            'boll': boll
        },
        'trend': trend,
        'support_resistance': support_resistance,
        'signal': signal,
        'risk': risk,
        'suggestion': suggestion
    }


def main():
    parser = argparse.ArgumentParser(description='Financial Analysis System')
    parser.add_argument('action', choices=['analyze', 'indicators', 'trend', 'suggest', 'risk', 'batch'],
                       help='Action to perform')
    parser.add_argument('--symbol', help='Stock symbol (e.g., AAPL)')
    parser.add_argument('--symbols', help='Comma-separated symbols for batch analysis')
    parser.add_argument('--days', type=int, default=30, help='Number of days to analyze')
    parser.add_argument('--output', choices=['json', 'markdown'], default='json', help='Output format')
    parser.add_argument('--strategy', help='Strategy for backtesting')

    args = parser.parse_args()

    if args.action in ['analyze', 'indicators', 'trend', 'suggest', 'risk']:
        if not args.symbol:
            print('Error: --symbol is required')
            return

        result = analyze_stock(args.symbol, args.days)

        # 根据action返回不同信息
        if args.action == 'indicators':
            result = {'symbol': args.symbol, 'indicators': result['indicators']}
        elif args.action == 'trend':
            result = {'symbol': args.symbol, 'trend': result['trend'], 'support_resistance': result['support_resistance']}
        elif args.action == 'suggest':
            result = {'symbol': args.symbol, 'suggestion': result['suggestion']}
        elif args.action == 'risk':
            result = {'symbol': args.symbol, 'risk': result['risk']}

    elif args.action == 'batch':
        if not args.symbols:
            print('Error: --symbols is required for batch analysis')
            return

        symbols = args.symbols.split(',')
        results = []
        for symbol in symbols:
            result = analyze_stock(symbol.strip(), args.days)
            results.append({
                'symbol': symbol,
                'signal': result['signal'],
                'suggestion': result['suggestion'],
                'risk': result['risk']
            })
        result = {'results': results}

    # 输出结果
    if args.output == 'json':
        print(json.dumps(result, indent=2, default=str))
    elif args.output == 'markdown':
        print(format_markdown(result))


def format_markdown(data: Dict) -> str:
    """格式化为Markdown"""
    if 'results' in data:  # 批量结果
        lines = ['# 批量分析结果\n']
        for r in data['results']:
            lines.append(f"## {r['symbol']}")
            lines.append(f"- 信号: {r['signal']['signal']} (置信度: {r['signal']['confidence']}%)")
            lines.append(f"- 建议: {r['suggestion']['action']}")
            lines.append(f"- 目标价: {r['suggestion']['target_price']}")
            lines.append(f"- 止损价: {r['suggestion']['stop_loss']}")
            lines.append(f"- 风险等级: {r['risk']['risk_level']}")
            lines.append('')
        return '\n'.join(lines)
    else:  # 单个股票结果
        symbol = data.get('symbol', 'UNKNOWN')
        suggestion = data.get('suggestion', {})
        signal = data.get('signal', {})
        risk = data.get('risk', {})

        lines = [
            f'# {symbol} 分析报告',
            f'## 投资建议',
            f'- **操作**: {suggestion.get("action", "N/A")}',
            f'- **仓位**: {suggestion.get("position", "N/A")}',
            f'- **持有时间**: {suggestion.get("hold_time", "N/A")}',
            f'- **目标价**: ${suggestion.get("target_price", 0)}',
            f'- **止损价**: ${suggestion.get("stop_loss", 0)}',
            f'- **风险收益比**: {suggestion.get("risk_reward_ratio", 0)}',
            f'',
            f'## 技术信号',
            f'- **信号**: {signal.get("signal", "N/A")}',
            f'- **置信度**: {signal.get("confidence", 0)}%',
            f'- **当前价格**: ${signal.get("current_price", 0)}',
            f'',
            f'## 风险评估',
            f'- **风险等级**: {risk.get("risk_level", "N/A")}',
            f'- **风险分数**: {risk.get("risk_score", 0)}/100',
            f'- **波动率**: {risk.get("volatility", 0)}%',
            f'- **最大回撤**: {risk.get("max_drawdown", 0)}%',
            f'',
            f'## 理由',
            f'{suggestion.get("reason", "N/A")}',
            f'',
            f'## 风险提示',
        ]
        for warning in suggestion.get("warnings", []):
            lines.append(f'- {warning}')

        return '\n'.join(lines)


if __name__ == '__main__':
    main()
