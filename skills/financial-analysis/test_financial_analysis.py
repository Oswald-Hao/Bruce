#!/usr/bin/env python3
"""
测试金融数据分析系统
直接执行financial-analyzer.py并运行测试
"""

# 执行financial-analyzer.py获取所有类和函数
with open('financial-analyzer.py', 'r') as f:
    code = f.read()

# 移除main()调用部分以避免在import时执行
if '__name__' in code:
    code = code[:code.index('if __name__')]

exec(code)


def test_data_generator():
    """测试数据生成"""
    print('测试1: 数据生成器...')

    data = DataGenerator.generate_stock_data('TEST', 30)

    assert len(data) == 30, '应该生成30天的数据'
    assert all('date' in d for d in data), '每条数据应该有date字段'
    assert all('open' in d for d in data), '每条数据应该有open字段'
    assert all('high' in d for d in data), '每条数据应该有high字段'
    assert all('low' in d for d in data), '每条数据应该有low字段'
    assert all('close' in d for d in data), '每条数据应该有close字段'
    assert all('volume' in d for d in data), '每条数据应该有volume字段'

    # 检查OHLC关系
    for d in data:
        assert d['high'] >= d['open'], 'high >= open'
        assert d['high'] >= d['close'], 'high >= close'
        assert d['low'] <= d['open'], 'low <= open'
        assert d['low'] <= d['close'], 'low <= close'
        assert d['volume'] > 0, 'volume > 0'

    print('  ✓ 数据生成器测试通过')
    return True


def test_stock_data():
    """测试StockData类"""
    print('测试2: StockData类...')

    data = DataGenerator.generate_stock_data('TEST', 20)
    stock = StockData('TEST', data)

    assert len(stock.dates) == 20, 'dates长度应该正确'
    assert len(stock.prices) == 20, 'prices长度应该正确'
    assert len(stock.opens) == 20, 'opens长度应该正确'
    assert len(stock.highs) == 20, 'highs长度应该正确'
    assert len(stock.lows) == 20, 'lows长度应该正确'
    assert len(stock.volumes) == 20, 'volumes长度应该正确'
    assert stock.symbol == 'TEST', 'symbol应该正确'

    # 检查prices提取正确
    for i, d in enumerate(data):
        assert stock.prices[i] == d['close'], f'prices[{i}]应该等于close'
        assert stock.opens[i] == d['open'], f'opens[{i}]应该等于open'
        assert stock.highs[i] == d['high'], f'highs[{i}]应该等于high'
        assert stock.lows[i] == d['low'], f'lows[{i}]应该等于low'

    print('  ✓ StockData类测试通过')
    return True


def test_sma():
    """测试简单移动平均线"""
    print('测试3: SMA计算...')

    indicators = TechnicalIndicators()
    prices = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

    sma = indicators.calculate_sma(prices, 5)

    # 前4个应该是None
    assert sma[0] is None, '第1个SMA应该是None'
    assert sma[1] is None, '第2个SMA应该是None'
    assert sma[2] is None, '第3个SMA应该是None'
    assert sma[3] is None, '第4个SMA应该是None'

    # 第5个应该是(10+11+12+13+14)/5 = 12
    assert abs(sma[4] - 12.0) < 0.01, f'第5个SMA应该是12.0, 实际是{sma[4]}'

    # 最后一个应该是(16+17+18+19+20)/5 = 18
    assert abs(sma[-1] - 18.0) < 0.01, f'最后一个SMA应该是18.0, 实际是{sma[-1]}'

    print('  ✓ SMA计算测试通过')
    return True


def test_ema():
    """测试指数移动平均线"""
    print('测试4: EMA计算...')

    indicators = TechnicalIndicators()
    prices = [10, 11, 12, 13, 14]

    ema = indicators.calculate_ema(prices, 3)

    # 第一个值应该等于第一个价格
    assert ema[0] == prices[0], '第一个EMA应该等于第一个价格'

    # 所有值应该不为None
    assert all(e is not None for e in ema), 'EMA不应该有None值'

    # EMA应该跟随价格趋势
    assert ema[-1] > ema[0], '价格上涨时EMA应该上涨'

    print('  ✓ EMA计算测试通过')
    return True


def test_macd():
    """测试MACD指标"""
    print('测试5: MACD指标...')

    indicators = TechnicalIndicators()
    prices = [100 + i * 2 for i in range(50)]  # 上涨趋势

    macd = indicators.calculate_macd(prices, fast=12, slow=26, signal=9)

    assert 'macd' in macd, 'MACD应该有macd字段'
    assert 'signal' in macd, 'MACD应该有signal字段'
    assert 'histogram' in macd, 'MACD应该有histogram字段'

    assert len(macd['macd']) == len(prices), 'MACD长度应该匹配价格长度'
    assert len(macd['signal']) == len(prices), 'signal长度应该匹配价格长度'
    assert len(macd['histogram']) == len(prices), 'histogram长度应该匹配价格长度'

    print('  ✓ MACD指标测试通过')
    return True


def test_rsi():
    """测试RSI指标"""
    print('测试6: RSI指标...')

    indicators = TechnicalIndicators()

    # 上涨趋势
    prices_up = [100 + i for i in range(30)]
    rsi_up = indicators.calculate_rsi(prices_up, 14)

    assert len(rsi_up) == len(prices_up), 'RSI长度应该匹配价格长度'

    # 前13个应该是None
    assert all(v is None for v in rsi_up[:13]), '前13个RSI应该是None'

    # 后面的值应该在0-100之间
    for rsi in rsi_up[13:]:
        if rsi is not None:
            assert 0 <= rsi <= 100, f'RSI应该在0-100之间, 实际是{rsi}'

    # 上涨趋势中RSI应该较高
    last_rsi = rsi_up[-1] if rsi_up[-1] is not None else rsi_up[-2]
    if last_rsi is not None:
        assert last_rsi > 50, '上涨趋势RSI应该大于50'

    print('  ✓ RSI指标测试通过')
    return True


def test_kdj():
    """测试KDJ指标"""
    print('测试7: KDJ指标...')

    indicators = TechnicalIndicators()

    highs = [100 + i for i in range(30)]
    lows = [95 + i for i in range(30)]
    closes = [97 + i for i in range(30)]

    kdj = indicators.calculate_kdj(highs, lows, closes, 9)

    assert 'k' in kdj, 'KDJ应该有k字段'
    assert 'd' in kdj, 'KDJ应该有d字段'
    assert 'j' in kdj, 'KDJ应该有j字段'

    assert len(kdj['k']) == len(closes), 'K长度应该匹配价格长度'
    assert len(kdj['d']) == len(closes), 'D长度应该匹配价格长度'
    assert len(kdj['j']) == len(closes), 'J长度应该匹配价格长度'

    # KDJ值应该在0-100之间
    for k, d, j in zip(kdj['k'], kdj['d'], kdj['j']):
        if k is not None:
            assert 0 <= k <= 100, f'K应该在0-100之间, 实际是{k}'
        if d is not None:
            assert 0 <= d <= 100, f'D应该在0-100之间, 实际是{d}'

    print('  ✓ KDJ指标测试通过')
    return True


def test_boll():
    """测试布林线"""
    print('测试8: 布林线计算...')

    indicators = TechnicalIndicators()
    prices = [100 + i for i in range(30)]

    boll = indicators.calculate_boll(prices, period=20, std_dev=2)

    assert 'middle' in boll, 'BOLL应该有middle字段'
    assert 'upper' in boll, 'BOLL应该有upper字段'
    assert 'lower' in boll, 'BOLL应该有lower字段'

    assert len(boll['middle']) == len(prices), 'middle长度应该匹配价格长度'
    assert len(boll['upper']) == len(prices), 'upper长度应该匹配价格长度'
    assert len(boll['lower']) == len(prices), 'lower长度应该匹配价格长度'

    # 前19个应该是None
    assert all(v is None for v in boll['middle'][:19]), '前19个middle应该是None'
    assert all(v is None for v in boll['upper'][:19]), '前19个upper应该是None'
    assert all(v is None for v in boll['lower'][:19]), '前19个lower应该是None'

    # upper >= middle >= lower
    for m, u, l in zip(boll['middle'], boll['upper'], boll['lower']):
        if m is not None and u is not None and l is not None:
            assert u >= m, f'upper应该>=middle, {u} >= {m}'
            assert m >= l, f'middle应该>=lower, {m} >= {l}'

    print('  ✓ 布林线计算测试通过')
    return True


def test_trend_analysis():
    """测试趋势分析"""
    print('测试9: 趋势分析...')

    analyzer = TrendAnalyzer()

    # 上涨趋势
    prices_up = [100 + i * 2 for i in range(30)]
    trend_up = analyzer.analyze_trend(prices_up)

    assert 'trend' in trend_up, '趋势分析应该有trend字段'
    assert 'strength' in trend_up, '趋势分析应该有strength字段'
    assert trend_up['trend'] in ['uptrend', 'downtrend', 'sideways'], 'trend应该是有效值'
    assert 0 <= trend_up['strength'] <= 100, 'strength应该在0-100之间'

    # 下跌趋势
    prices_down = [200 - i * 2 for i in range(30)]
    trend_down = analyzer.analyze_trend(prices_down)

    assert trend_down['trend'] in ['uptrend', 'downtrend', 'sideways'], '趋势应该是有效值'

    # 震荡
    prices_sideways = [100 + (i % 5) * 2 for i in range(30)]
    trend_sideways = analyzer.analyze_trend(prices_sideways)

    assert trend_sideways['trend'] in ['uptrend', 'downtrend', 'sideways'], '趋势应该是有效值'

    print('  ✓ 趋势分析测试通过')
    return True


def test_support_resistance():
    """测试支撑阻力位"""
    print('测试10: 支撑阻力位识别...')

    analyzer = TrendAnalyzer()

    # 波动价格
    prices = [100, 105, 100, 110, 95, 115, 90, 120, 85, 125, 80]

    sr = analyzer.find_support_resistance(prices)

    assert 'support' in sr, '应该有support字段'
    assert 'resistance' in sr, '应该有resistance字段'
    assert isinstance(sr['support'], list), 'support应该是列表'
    assert isinstance(sr['resistance'], list), 'resistance应该是列表'

    # 支撑位应该较低，阻力位应该较高
    if sr['support'] and sr['resistance']:
        assert min(sr['support']) < max(sr['resistance']), '支撑位应该低于阻力位'

    print('  ✓ 支撑阻力位识别测试通过')
    return True


def test_signal_generation():
    """测试信号生成"""
    print('测试11: 买卖信号生成...')

    analyzer = TrendAnalyzer()

    # 上涨趋势
    prices_up = [100 + i for i in range(30)]
    signal_up = analyzer.generate_signal(prices_up, {
        'macd': {'histogram': [None] * 25 + [-0.1, 0.1]},
        'rsi': [None] * 13 + [40] * 17,
        'trend': {'trend': 'uptrend'}
    })

    assert 'signal' in signal_up, '信号应该有signal字段'
    assert 'confidence' in signal_up, '信号应该有confidence字段'
    assert signal_up['signal'] in ['buy', 'sell', 'hold'], 'signal应该是有效值'
    assert 0 <= signal_up['confidence'] <= 100, 'confidence应该在0-100之间'

    print('  ✓ 买卖信号生成测试通过')
    return True


def test_risk_analysis():
    """测试风险评估"""
    print('测试12: 风险评估...')

    analyzer = RiskAnalyzer()

    # 低波动
    prices_low_vol = [100 + (i % 3) for i in range(30)]
    vol_low = analyzer.calculate_volatility(prices_low_vol)

    assert vol_low >= 0, '波动率应该>=0'

    risk_low = analyzer.assess_risk(prices_low_vol, vol_low)

    assert 'risk_level' in risk_low, '风险评估应该有risk_level字段'
    assert 'risk_score' in risk_low, '风险评估应该有risk_score字段'
    assert risk_low['risk_level'] in ['low', 'medium', 'high'], 'risk_level应该是有效值'
    assert 0 <= risk_low['risk_score'] <= 100, 'risk_score应该在0-100之间'

    # 高波动
    prices_high_vol = [100 + i * 5 for i in range(30)]
    vol_high = analyzer.calculate_volatility(prices_high_vol)

    assert vol_high >= 0, '波动率应该>=0'

    risk_high = analyzer.assess_risk(prices_high_vol, vol_high)

    assert risk_high['risk_level'] in ['low', 'medium', 'high'], 'risk_level应该是有效值'

    print('  ✓ 风险评估测试通过')
    return True


def test_position_suggestion():
    """测试仓位建议"""
    print('测试13: 仓位建议...')

    analyzer = RiskAnalyzer()

    pos_low = analyzer.suggest_position('low')
    pos_medium = analyzer.suggest_position('medium')
    pos_high = analyzer.suggest_position('high')

    assert 0 < pos_low <= 1, '仓位应该在0-1之间'
    assert 0 < pos_medium <= 1, '仓位应该在0-1之间'
    assert 0 < pos_high <= 1, '仓位应该在0-1之间'

    # 高风险仓位应该最小
    assert pos_high <= pos_medium, '高风险仓位应该<=中风险仓位'
    assert pos_medium <= pos_low, '中风险仓位应该<=低风险仓位'

    print('  ✓ 仓位建议测试通过')
    return True


def test_stop_loss():
    """测试止损点计算"""
    print('测试14: 止损点计算...')

    analyzer = RiskAnalyzer()

    current_price = 100

    stop_low = analyzer.calculate_stop_loss(current_price, 'low')
    stop_medium = analyzer.calculate_stop_loss(current_price, 'medium')
    stop_high = analyzer.calculate_stop_loss(current_price, 'high')

    # 所有止损点都应该低于当前价格
    assert stop_low < current_price, '止损点应该低于当前价格'
    assert stop_medium < current_price, '止损点应该低于当前价格'
    assert stop_high < current_price, '止损点应该低于当前价格'

    # 高风险止损应该最高（离当前价格最近）
    assert stop_high >= stop_medium, '高风险止损应该>=中风险止损'
    assert stop_medium >= stop_low, '中风险止损应该>=低风险止损'

    print('  ✓ 止损点计算测试通过')
    return True


def test_investment_advisor():
    """测试投资建议"""
    print('测试15: 投资建议生成...')

    advisor = InvestmentAdvisor()

    data = {
        'signal': 'buy',
        'confidence': 75,
        'risk': {'risk_level': 'medium'},
        'trend': {'trend': 'uptrend'},
        'support_resistance': {'support': [95], 'resistance': [110]},
        'current_price': 100
    }

    suggestion = advisor.generate_suggestion(data)

    assert 'action' in suggestion, '建议应该有action字段'
    assert 'position' in suggestion, '建议应该有position字段'
    assert 'hold_time' in suggestion, '建议应该有hold_time字段'
    assert 'target_price' in suggestion, '建议应该有target_price字段'
    assert 'stop_loss' in suggestion, '建议应该有stop_loss字段'
    assert 'risk_reward_ratio' in suggestion, '建议应该有risk_reward_ratio字段'
    assert 'reason' in suggestion, '建议应该有reason字段'
    assert 'warnings' in suggestion, '建议应该有warnings字段'

    # 目标价应该高于当前价
    if data['signal'] == 'buy':
        assert suggestion['target_price'] >= data['current_price'], '买入建议目标价应该>=当前价'
        assert suggestion['stop_loss'] <= data['current_price'], '止损价应该<=当前价'

    # 应该有风险提示
    assert len(suggestion['warnings']) > 0, '应该有风险提示'

    print('  ✓ 投资建议生成测试通过')
    return True


def test_full_analysis():
    """测试完整分析流程"""
    print('测试16: 完整分析流程...')

    result = analyze_stock('AAPL', 30)

    assert 'symbol' in result, '结果应该有symbol字段'
    assert 'data' in result, '结果应该有data字段'
    assert 'indicators' in result, '结果应该有indicators字段'
    assert 'trend' in result, '结果应该有trend字段'
    assert 'signal' in result, '结果应该有signal字段'
    assert 'risk' in result, '结果应该有risk字段'
    assert 'suggestion' in result, '结果应该有suggestion字段'

    # 检查indicators
    assert 'macd' in result['indicators'], 'indicators应该有macd'
    assert 'rsi' in result['indicators'], 'indicators应该有rsi'
    assert 'kdj' in result['indicators'], 'indicators应该有kdj'
    assert 'boll' in result['indicators'], 'indicators应该有boll'

    # 检查数据
    assert len(result['data']) == 30, '应该有30天数据'

    # 检查suggestion
    assert 'action' in result['suggestion'], 'suggestion应该有action'
    assert 'target_price' in result['suggestion'], 'suggestion应该有target_price'

    print('  ✓ 完整分析流程测试通过')
    return True


def run_all_tests():
    """运行所有测试"""
    print('=' * 60)
    print('开始测试金融数据分析系统')
    print('=' * 60)

    tests = [
        test_data_generator,
        test_stock_data,
        test_sma,
        test_ema,
        test_macd,
        test_rsi,
        test_kdj,
        test_boll,
        test_trend_analysis,
        test_support_resistance,
        test_signal_generation,
        test_risk_analysis,
        test_position_suggestion,
        test_stop_loss,
        test_investment_advisor,
        test_full_analysis
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f'  ✗ {test.__name__} 失败: {e}')
            failed += 1

    print('=' * 60)
    print(f'测试完成: {passed} 通过, {failed} 失败')
    print('=' * 60)

    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    import sys
    sys.exit(0 if success else 1)
