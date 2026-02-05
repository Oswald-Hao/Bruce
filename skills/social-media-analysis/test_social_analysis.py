#!/usr/bin/env python3
"""
测试社交媒体分析系统
"""

# 直接导入social-analyzer.py中的所有类和函数
with open('social-analyzer.py', 'r') as f:
    code = f.read()

# 移除main()调用部分以避免在import时执行
if '__name__' in code:
    code = code[:code.index('if __name__')]

exec(code)


def test_sentiment_analysis():
    """测试情感分析"""
    print('测试1: 情感分析...')

    analyzer = SentimentAnalyzer()

    # 正面情感
    pos_text = "这个产品太棒了，强烈推荐！"
    pos_result = analyzer.analyze(pos_text)

    assert 'sentiment' in pos_result, '结果应该有sentiment字段'
    assert 'confidence' in pos_result, '结果应该有confidence字段'
    assert 'score' in pos_result, '结果应该有score字段'
    assert pos_result['sentiment'] in ['positive', 'negative', 'neutral'], 'sentiment应该是有效值'
    assert 0 <= pos_result['confidence'] <= 1, 'confidence应该在0-1之间'

    # 负面情感
    neg_text = "这个产品太差了，不推荐"
    neg_result = analyzer.analyze(neg_text)

    assert neg_result['sentiment'] in ['positive', 'negative', 'neutral'], 'sentiment应该是有效值'

    # 中性情感
    neu_text = "今天看到了这个产品的广告"
    neu_result = analyzer.analyze(neu_text)

    assert neu_result['sentiment'] in ['positive', 'negative', 'neutral'], 'sentiment应该是有效值'

    # 关键词提取
    assert 'keywords' in pos_result, '结果应该有keywords字段'
    assert isinstance(pos_result['keywords'], list), 'keywords应该是列表'

    print('  ✓ 情感分析测试通过')
    return True


def test_batch_sentiment_analysis():
    """测试批量情感分析"""
    print('测试2: 批量情感分析...')

    analyzer = SentimentAnalyzer()

    texts = [
        "这个产品太棒了",
        "不推荐这个产品",
        "这个产品还可以",
        "强烈推荐"
    ]

    results = analyzer.batch_analyze(texts)

    assert len(results) == len(texts), '结果数量应该匹配输入数量'

    for result in results:
        assert 'sentiment' in result, '每个结果应该有sentiment字段'
        assert 'confidence' in result, '每个结果应该有confidence字段'
        assert result['sentiment'] in ['positive', 'negative', 'neutral'], 'sentiment应该是有效值'

    print('  ✓ 批量情感分析测试通过')
    return True


def test_trend_data_generation():
    """测试趋势数据生成"""
    print('测试3: 趋势数据生成...')

    data = TrendAnalyzer.generate_mock_data('AI', 7)

    assert len(data) == 7, '应该生成7天的数据'
    assert all('date' in d for d in data), '每条数据应该有date字段'
    assert all('topic' in d for d in data), '每条数据应该有topic字段'
    assert all('mentions' in d for d in data), '每条数据应该有mentions字段'
    assert all('engagement' in d for d in data), '每条数据应该有engagement字段'
    assert all('reach' in d for d in data), '每条数据应该有reach字段'
    assert all('sentiment_score' in d for d in data), '每条数据应该有sentiment_score字段'

    # 检查数据有效性
    for d in data:
        assert d['mentions'] > 0, 'mentions应该大于0'
        assert d['engagement'] > 0, 'engagement应该大于0'
        assert d['reach'] > 0, 'reach应该大于0'
        assert -1 <= d['sentiment_score'] <= 1, 'sentiment_score应该在-1到1之间'

    print('  ✓ 趋势数据生成测试通过')
    return True


def test_trend_analysis():
    """测试趋势分析"""
    print('测试4: 趋势分析...')

    data = TrendAnalyzer.generate_mock_data('Test', 10)
    trend = TrendAnalyzer.analyze_trend(data)

    assert 'trend_type' in trend, '趋势分析应该有trend_type字段'
    assert 'growth_rate' in trend, '趋势分析应该有growth_rate字段'
    assert 'burst_points' in trend, '趋势分析应该有burst_points字段'
    assert 'stats' in trend, '趋势分析应该有stats字段'
    assert 'sentiment' in trend, '趋势分析应该有sentiment字段'

    assert trend['trend_type'] in ['rising', 'declining', 'stable'], 'trend_type应该是有效值'
    assert isinstance(trend['burst_points'], list), 'burst_points应该是列表'
    assert isinstance(trend['stats'], dict), 'stats应该是字典'

    # 检查统计数据
    stats = trend['stats']
    assert 'avg_mentions' in stats, 'stats应该有avg_mentions'
    assert 'total_mentions' in stats, 'stats应该有total_mentions'
    assert stats['avg_mentions'] > 0, 'avg_mentions应该大于0'

    # 检查情感数据
    sentiment = trend['sentiment']
    assert 'avg_score' in sentiment, 'sentiment应该有avg_score'
    assert 'trend' in sentiment, 'sentiment应该有trend'

    print('  ✓ 趋势分析测试通过')
    return True


def test_hot_topic_detection():
    """测试热门话题检测"""
    print('测试5: 热门话题检测...')

    topics = ['AI', '区块链', '新能源', '元宇宙', '直播带货', '短视频', '电商', '游戏', '运动', '美食']
    hot_topics = TrendAnalyzer.detect_hot_topics(topics, limit=10)

    assert len(hot_topics) == 10, '应该返回10个话题'

    for topic in hot_topics:
        assert 'topic' in topic, '话题应该有topic字段'
        assert 'mentions' in topic, '话题应该有mentions字段'
        assert 'trend_type' in topic, '话题应该有trend_type字段'
        assert 'growth_rate' in topic, '话题应该有growth_rate字段'

        assert topic['mentions'] > 0, 'mentions应该大于0'
        assert topic['trend_type'] in ['rising', 'declining', 'stable'], 'trend_type应该是有效值'

    # 检查排序（按提及量降序）
    for i in range(len(hot_topics) - 1):
        assert hot_topics[i]['mentions'] >= hot_topics[i+1]['mentions'], '应该按提及量降序排列'

    print('  ✓ 热门话题检测测试通过')
    return True


def test_brand_monitoring():
    """测试品牌监控"""
    print('测试6: 品牌监控...')

    monitor = BrandMonitor()

    result = monitor.monitor('TestBrand', 7)

    assert 'keyword' in result, '结果应该有keyword字段'
    assert 'trend' in result, '结果应该有trend字段'
    assert 'total_mentions' in result, '结果应该有total_mentions字段'
    assert 'sentiment_distribution' in result, '结果应该有sentiment_distribution字段'
    assert 'daily_data' in result, '结果应该有daily_data字段'

    assert result['keyword'] == 'TestBrand', 'keyword应该匹配'
    assert result['total_mentions'] > 0, 'total_mentions应该大于0'
    assert isinstance(result['daily_data'], list), 'daily_data应该是列表'
    assert len(result['daily_data']) == 7, 'daily_data应该有7天的数据'

    # 检查情感分布
    sentiment_dist = result['sentiment_distribution']
    assert 'positive' in sentiment_dist, '应该有positive情感'
    assert 'negative' in sentiment_dist, '应该有negative情感'
    assert 'neutral' in sentiment_dist, '应该有neutral情感'

    # 检查总和是否接近100%（可能有舍入误差）
    total_pct = sum(sentiment_dist.values())
    assert 90 <= total_pct <= 110, f'情感分布总和应该在90-110%之间, 实际是{total_pct}%'

    print('  ✓ 品牌监控测试通过')
    return True


def test_brand_comparison():
    """测试品牌对比"""
    print('测试7: 品牌对比...')

    monitor = BrandMonitor()

    brands = ['BrandA', 'BrandB', 'BrandC']
    comparison = monitor.compare_brands(brands)

    assert len(comparison) == 3, '应该返回3个品牌的对比'

    for brand in comparison:
        assert 'brand' in brand, '品牌应该有brand字段'
        assert 'mentions' in brand, '品牌应该有mentions字段'
        assert 'positive_rate' in brand, '品牌应该有positive_rate字段'
        assert 'negative_rate' in brand, '品牌应该有negative_rate字段'
        assert 'trend' in brand, '品牌应该有trend字段'

        assert brand['mentions'] > 0, 'mentions应该大于0'

    # 检查排序（按提及量降序）
    for i in range(len(comparison) - 1):
        assert comparison[i]['mentions'] >= comparison[i+1]['mentions'], '应该按提及量降序排列'

    print('  ✓ 品牌对比测试通过')
    return True


def test_user_data_generation():
    """测试用户数据生成"""
    print('测试8: 用户数据生成...')

    user_data = UserProfiler.generate_mock_user_data('test_user')

    assert 'user_id' in user_data, '用户数据应该有user_id字段'
    assert 'name' in user_data, '用户数据应该有name字段'
    assert 'followers' in user_data, '用户数据应该有followers字段'
    assert 'following' in user_data, '用户数据应该有following字段'
    assert 'posts_count' in user_data, '用户数据应该有posts_count字段'
    assert 'avg_likes' in user_data, '用户数据应该有avg_likes字段'
    assert 'avg_comments' in user_data, '用户数据应该有avg_comments字段'
    assert 'location' in user_data, '用户数据应该有location字段'
    assert 'interests' in user_data, '用户数据应该有interests字段'
    assert 'active_hours' in user_data, '用户数据应该有active_hours字段'

    assert user_data['followers'] > 0, 'followers应该大于0'
    assert user_data['following'] > 0, 'following应该大于0'
    assert user_data['posts_count'] > 0, 'posts_count应该大于0'
    assert isinstance(user_data['interests'], list), 'interests应该是列表'
    assert isinstance(user_data['active_hours'], list), 'active_hours应该是列表'

    # 活跃小时应该在0-23之间
    for hour in user_data['active_hours']:
        assert 0 <= hour <= 23, f'active_hours应该在0-23之间, 实际是{hour}'

    print('  ✓ 用户数据生成测试通过')
    return True


def test_user_profile_analysis():
    """测试用户画像分析"""
    print('测试9: 用户画像分析...')

    user_data = UserProfiler.generate_mock_user_data('test_user')
    profile = UserProfiler.analyze_profile(user_data)

    assert 'influence' in profile, '画像应该有influence字段'
    assert 'activity' in profile, '画像应该有activity字段'
    assert 'content' in profile, '画像应该有content字段'
    assert 'interests' in profile, '画像应该有interests字段'
    assert 'location' in profile, '画像应该有location字段'
    assert 'health' in profile, '画像应该有health字段'

    # 检查影响力
    influence = profile['influence']
    assert 'level' in influence, 'influence应该有level字段'
    assert 'score' in influence, 'influence应该有score字段'
    assert influence['level'] in ['high', 'medium', 'low'], 'level应该是有效值'
    assert 0 <= influence['score'] <= 100, 'score应该在0-100之间'

    # 检查活跃度
    activity = profile['activity']
    assert 'peak_hours' in activity, 'activity应该有peak_hours字段'
    assert isinstance(activity['peak_hours'], list), 'peak_hours应该是列表'

    # 检查内容质量
    content = profile['content']
    assert 'quality_level' in content, 'content应该有quality_level字段'
    assert content['quality_level'] in ['high', 'medium', 'low'], 'quality_level应该是有效值'

    # 检查健康度
    health = profile['health']
    assert 'score' in health, 'health应该有score字段'
    assert 'level' in health, 'health应该有level字段'
    assert 0 <= health['score'] <= 100, 'score应该在0-100之间'

    print('  ✓ 用户画像分析测试通过')
    return True


def test_campaign_data_generation():
    """测试营销数据生成"""
    print('测试10: 营销数据生成...')

    campaign_data = MarketingEvaluator.generate_mock_campaign_data('test_campaign', 30)

    assert 'campaign_id' in campaign_data, '营销数据应该有campaign_id字段'
    assert 'name' in campaign_data, '营销数据应该有name字段'
    assert 'start_date' in campaign_data, '营销数据应该有start_date字段'
    assert 'end_date' in campaign_data, '营销数据应该有end_date字段'
    assert 'budget' in campaign_data, '营销数据应该有budget字段'
    assert 'daily_data' in campaign_data, '营销数据应该有daily_data字段'
    assert 'total_revenue' in campaign_data, '营销数据应该有total_revenue字段'

    assert campaign_data['budget'] > 0, 'budget应该大于0'
    assert len(campaign_data['daily_data']) == 30, 'daily_data应该有30天的数据'
    assert campaign_data['total_revenue'] >= 0, 'total_revenue应该大于等于0'

    # 检查每日数据
    for daily in campaign_data['daily_data']:
        assert 'date' in daily, '每日数据应该有date字段'
        assert 'impressions' in daily, '每日数据应该有impressions字段'
        assert 'clicks' in daily, '每日数据应该有clicks字段'
        assert 'conversions' in daily, '每日数据应该有conversions字段'
        assert 'revenue' in daily, '每日数据应该有revenue字段'
        assert 'cost' in daily, '每日数据应该有cost字段'

        assert daily['impressions'] >= daily['clicks'], 'impressions应该>=clicks'
        assert daily['clicks'] >= daily['conversions'], 'clicks应该>=conversions'

    print('  ✓ 营销数据生成测试通过')
    return True


def test_campaign_evaluation():
    """测试营销活动评估"""
    print('测试11: 营销活动评估...')

    campaign_data = MarketingEvaluator.generate_mock_campaign_data('test_campaign', 30)
    evaluation = MarketingEvaluator.evaluate_campaign(campaign_data)

    assert 'campaign_name' in evaluation, '评估结果应该有campaign_name字段'
    assert 'effectiveness' in evaluation, '评估结果应该有effectiveness字段'
    assert 'metrics' in evaluation, '评估结果应该有metrics字段'
    assert 'trend' in evaluation, '评估结果应该有trend字段'

    assert evaluation['effectiveness'] in ['excellent', 'good', 'acceptable', 'poor'], 'effectiveness应该是有效值'

    # 检查核心指标
    metrics = evaluation['metrics']
    assert 'impressions' in metrics, 'metrics应该有impressions'
    assert 'clicks' in metrics, 'metrics应该有clicks'
    assert 'conversions' in metrics, 'metrics应该有conversions'
    assert 'revenue' in metrics, 'metrics应该有revenue'
    assert 'cost' in metrics, 'metrics应该有cost'
    assert 'profit' in metrics, 'metrics应该有profit'
    assert 'ctr' in metrics, 'metrics应该有ctr'
    assert 'conversion_rate' in metrics, 'metrics应该有conversion_rate'
    assert 'cpa' in metrics, 'metrics应该有cpa'
    assert 'roi' in metrics, 'metrics应该有roi'

    assert metrics['impressions'] > 0, 'impressions应该大于0'
    assert metrics['clicks'] > 0, 'clicks应该大于0'
    assert metrics['ctr'] >= 0, 'ctr应该>=0'
    assert metrics['conversion_rate'] >= 0, 'conversion_rate应该>=0'

    # 检查趋势
    trend = evaluation['trend']
    assert 'clicks_growth' in trend, 'trend应该有clicks_growth'
    assert 'conversions_growth' in trend, 'trend应该有conversions_growth'

    print('  ✓ 营销活动评估测试通过')
    return True


def test_keyword_chinese_tokenization():
    """测试中文分词"""
    print('测试12: 中文分词...')

    analyzer = SentimentAnalyzer()

    # 测试中文文本
    text = "这个产品太棒了"
    words = analyzer._tokenize_chinese(text)

    assert isinstance(words, list), '应该返回列表'
    assert len(words) > 0, '应该能分出词'

    # 测试英文文本（应该返回空）
    english_text = "This is a test"
    english_words = analyzer._tokenize_chinese(english_text)
    assert len(english_words) == 0, '英文文本分词应该为空'

    print('  ✓ 中文分词测试通过')
    return True


def test_keyword_extraction():
    """测试关键词提取"""
    print('测试13: 关键词提取...')

    analyzer = SentimentAnalyzer()

    # 准备测试词列表
    words = ['产品', '服务', '产品', '推荐', '体验', '产品', '很好']

    keywords = analyzer._extract_keywords(words)

    assert isinstance(keywords, list), '应该返回列表'
    assert len(keywords) <= 5, '最多返回5个关键词'

    # '产品'出现最多，应该排在前面
    if keywords:
        assert '产品' in keywords, '高频词应该在关键词列表中'

    print('  ✓ 关键词提取测试通过')
    return True


def test_full_sentiment_analysis_workflow():
    """测试完整的情感分析流程"""
    print('测试14: 完整情感分析流程...')

    texts = [
        "这个产品太棒了，强烈推荐！",
        "不推荐这个产品，体验很差",
        "这个产品还可以，没什么特别的",
        "最好的产品，必须买！"
    ]

    results = [analyze_sentiment(text) for text in texts]

    assert len(results) == len(texts), '结果数量应该匹配'

    # 检查每个结果
    for result in results:
        assert 'sentiment' in result
        assert 'confidence' in result
        assert 'score' in result
        assert 0 <= result['confidence'] <= 1
        assert -1 <= result['score'] <= 1

    print('  ✓ 完整情感分析流程测试通过')
    return True


def test_full_monitor_workflow():
    """测试完整的监控流程"""
    print('测试15: 完整监控流程...')

    result = monitor_keyword('测试品牌', 7)

    assert 'keyword' in result
    assert 'trend' in result
    assert 'total_mentions' in result
    assert 'sentiment_distribution' in result
    assert result['total_mentions'] > 0

    # 检查情感分布
    sentiment_dist = result['sentiment_distribution']
    assert 'positive' in sentiment_dist
    assert 'negative' in sentiment_dist
    assert 'neutral' in sentiment_dist

    print('  ✓ 完整监控流程测试通过')
    return True


def test_full_profile_workflow():
    """测试完整的用户画像流程"""
    print('测试16: 完整用户画像流程...')

    result = create_user_profile('test_user')

    assert 'influence' in result
    assert 'activity' in result
    assert 'content' in result
    assert 'health' in result

    # 检查影响力
    assert 0 <= result['influence']['score'] <= 100
    assert result['influence']['level'] in ['high', 'medium', 'low']

    print('  ✓ 完整用户画像流程测试通过')
    return True


def run_all_tests():
    """运行所有测试"""
    print('=' * 60)
    print('开始测试社交媒体分析系统')
    print('=' * 60)

    tests = [
        test_sentiment_analysis,
        test_batch_sentiment_analysis,
        test_trend_data_generation,
        test_trend_analysis,
        test_hot_topic_detection,
        test_brand_monitoring,
        test_brand_comparison,
        test_user_data_generation,
        test_user_profile_analysis,
        test_campaign_data_generation,
        test_campaign_evaluation,
        test_keyword_chinese_tokenization,
        test_keyword_extraction,
        test_full_sentiment_analysis_workflow,
        test_full_monitor_workflow,
        test_full_profile_workflow
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
