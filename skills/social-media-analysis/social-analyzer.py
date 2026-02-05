#!/usr/bin/env python3
"""
Social Media Analysis System - 社交媒体分析系统
提供趋势追踪、舆情监控、情感分析、用户画像和营销效果评估
"""

import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import random
from collections import defaultdict
import re


class SentimentAnalyzer:
    """情感分析器"""

    # 简化的情感词典
    POSITIVE_WORDS = ['好', '棒', '优秀', '喜欢', '爱', '推荐', '赞', '太棒了', '完美',
                     'good', 'great', 'excellent', 'love', 'recommend', 'amazing', 'perfect']

    NEGATIVE_WORDS = ['差', '坏', '讨厌', '垃圾', '糟糕', '失望', '不推荐', '烂', '坑',
                     'bad', 'terrible', 'hate', 'disappoint', 'awful', 'worst', 'poor']

    def __init__(self):
        self.positive_set = set(self.POSITIVE_WORDS)
        self.negative_set = set(self.NEGATIVE_WORDS)

    def analyze(self, text: str) -> Dict:
        """分析单条文本的情感"""
        # 中文分词（简化版）
        words = self._tokenize_chinese(text) + self._tokenize_english(text)

        # 计算情感分数
        positive_count = sum(1 for w in words if w in self.positive_set)
        negative_count = sum(1 for w in words if w in self.negative_set)

        total = positive_count + negative_count

        if total == 0:
            sentiment = 'neutral'
            confidence = 0.5
            score = 0
        elif positive_count > negative_count:
            sentiment = 'positive'
            confidence = positive_count / total
            score = (positive_count - negative_count) / total
        else:
            sentiment = 'negative'
            confidence = negative_count / total
            score = -(negative_count - positive_count) / total

        # 提取关键词
        keywords = self._extract_keywords(words)

        return {
            'sentiment': sentiment,
            'confidence': round(confidence, 2),
            'score': round(score, 2),
            'positive_words': positive_count,
            'negative_words': negative_count,
            'keywords': keywords
        }

    def _tokenize_chinese(self, text: str) -> List[str]:
        """简化的中文分词"""
        # 匹配2-4个连续的汉字
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]{2,4}')
        return chinese_pattern.findall(text)

    def _tokenize_english(self, text: str) -> List[str]:
        """英文分词"""
        english_pattern = re.compile(r'\b[a-zA-Z]{2,}\b')
        words = english_pattern.findall(text.lower())
        return words

    def _extract_keywords(self, words: List[str]) -> List[str]:
        """提取关键词"""
        # 简单的词频统计
        word_freq = defaultdict(int)
        for word in words:
            if len(word) >= 2:  # 过滤单字
                word_freq[word] += 1

        # 返回高频词
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:5]]

    def batch_analyze(self, texts: List[str]) -> List[Dict]:
        """批量分析文本情感"""
        return [self.analyze(text) for text in texts]


class TrendAnalyzer:
    """趋势分析器"""

    @staticmethod
    def generate_mock_data(topic: str, days: int = 7) -> List[Dict]:
        """生成模拟话题数据"""
        data = []

        for i in range(days):
            date = (datetime.now() - timedelta(days=days - i - 1)).strftime('%Y-%m-%d')

            # 模拟热度趋势（随机波动但有趋势）
            base_trend = random.uniform(0.8, 1.2)
            daily_variation = random.uniform(0.7, 1.3)

            if i > days // 2:  # 后期可能爆发
                burst_factor = random.uniform(1.0, 2.5)
            else:
                burst_factor = random.uniform(0.8, 1.2)

            mentions = int(1000 * base_trend * daily_variation * burst_factor)
            engagement = int(mentions * random.uniform(0.1, 0.5))
            reach = int(engagement * random.uniform(5, 20))

            data.append({
                'date': date,
                'topic': topic,
                'mentions': mentions,
                'engagement': engagement,
                'reach': reach,
                'sentiment_score': random.uniform(-0.3, 0.7)
            })

        return data

    @staticmethod
    def analyze_trend(data: List[Dict]) -> Dict:
        """分析趋势"""
        if not data:
            return {}

        # 计算增长趋势
        mentions = [d['mentions'] for d in data]

        if len(mentions) >= 2:
            growth_rate = (mentions[-1] - mentions[0]) / mentions[0] if mentions[0] > 0 else 0
        else:
            growth_rate = 0

        # 判断趋势类型
        if growth_rate > 0.5:
            trend_type = 'rising'
        elif growth_rate < -0.2:
            trend_type = 'declining'
        else:
            trend_type = 'stable'

        # 检测爆发点
        burst_points = []
        for i in range(1, len(data)):
            if data[i]['mentions'] > data[i-1]['mentions'] * 1.5:
                burst_points.append(data[i]['date'])

        # 计算平均值
        avg_mentions = sum(d['mentions'] for d in data) / len(data)
        avg_engagement = sum(d['engagement'] for d in data) / len(data)
        avg_reach = sum(d['reach'] for d in data) / len(data)

        # 情感趋势
        sentiment_scores = [d['sentiment_score'] for d in data]
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)

        return {
            'trend_type': trend_type,
            'growth_rate': round(growth_rate * 100, 2),
            'burst_points': burst_points,
            'stats': {
                'avg_mentions': int(avg_mentions),
                'avg_engagement': int(avg_engagement),
                'avg_reach': int(avg_reach),
                'total_mentions': sum(d['mentions'] for d in data)
            },
            'sentiment': {
                'avg_score': round(avg_sentiment, 2),
                'trend': 'improving' if sentiment_scores[-1] > sentiment_scores[0] else 'declining'
            }
        }

    @staticmethod
    def detect_hot_topics(topics: List[str], limit: int = 10) -> List[Dict]:
        """检测热门话题"""
        hot_topics = []

        for topic in topics[:limit]:
            data = TrendAnalyzer.generate_mock_data(topic, 7)
            trend = TrendAnalyzer.analyze_trend(data)

            hot_topics.append({
                'topic': topic,
                'mentions': trend['stats']['total_mentions'],
                'trend_type': trend['trend_type'],
                'growth_rate': trend['growth_rate']
            })

        # 按提及量排序
        hot_topics.sort(key=lambda x: x['mentions'], reverse=True)

        return hot_topics


class BrandMonitor:
    """品牌监控器"""

    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()

    def monitor(self, keyword: str, days: int = 7) -> Dict:
        """监控品牌/关键词"""
        # 生成模拟数据
        mentions = []
        sentiments = {'positive': 0, 'negative': 0, 'neutral': 0}

        for i in range(days):
            date = (datetime.now() - timedelta(days=days - i - 1)).strftime('%Y-%m-%d')
            daily_mentions = random.randint(50, 500)

            daily_data = {
                'date': date,
                'mentions': daily_mentions,
                'posts': []
            }

            # 生成模拟帖子
            for _ in range(min(50, daily_mentions)):
                sentiment_type = random.choices(
                    ['positive', 'negative', 'neutral'],
                    weights=[0.5, 0.2, 0.3]
                )[0]

                post = self._generate_mock_post(keyword, sentiment_type)
                sentiment = self.sentiment_analyzer.analyze(post)

                daily_data['posts'].append({
                    'text': post,
                    'sentiment': sentiment['sentiment'],
                    'confidence': sentiment['confidence']
                })

                sentiments[sentiment['sentiment']] += 1

            mentions.append(daily_data)

        # 分析趋势
        mentions_trend = [m['mentions'] for m in mentions]
        trend = 'rising' if mentions_trend[-1] > mentions_trend[0] * 1.2 else 'stable'

        total_sentiments = sum(sentiments.values())
        sentiment_distribution = {
            k: round(v / total_sentiments * 100, 2) if total_sentiments > 0 else 0
            for k, v in sentiments.items()
        }

        return {
            'keyword': keyword,
            'trend': trend,
            'total_mentions': sum(m['mentions'] for m in mentions),
            'sentiment_distribution': sentiment_distribution,
            'daily_data': mentions
        }

    def compare_brands(self, brands: List[str]) -> List[Dict]:
        """对比多个品牌"""
        comparisons = []

        for brand in brands:
            data = self.monitor(brand, 7)
            comparisons.append({
                'brand': brand,
                'mentions': data['total_mentions'],
                'positive_rate': data['sentiment_distribution']['positive'],
                'negative_rate': data['sentiment_distribution']['negative'],
                'trend': data['trend']
            })

        # 按提及量排序
        comparisons.sort(key=lambda x: x['mentions'], reverse=True)

        return comparisons

    def _generate_mock_post(self, keyword: str, sentiment: str) -> str:
        """生成模拟帖子"""
        templates = {
            'positive': [
                f'{keyword}这个产品太棒了，强烈推荐！',
                f'刚用了{keyword}，体验非常好，超出预期',
                f'{keyword}的服务一流，点赞',
            ],
            'negative': [
                f'{keyword}太差了，浪费钱',
                f'不推荐{keyword}，体验很差',
                f'{keyword}的客服太糟糕了，再也不用了',
            ],
            'neutral': [
                f'今天看到了{keyword}的广告',
                f'有人用过{keyword}吗？想了解一下',
                f'{keyword}看起来还行吧',
            ]
        }

        return random.choice(templates.get(sentiment, templates['neutral']))


class UserProfiler:
    """用户画像分析器"""

    @staticmethod
    def generate_mock_user_data(user_id: str) -> Dict:
        """生成模拟用户数据"""
        return {
            'user_id': user_id,
            'name': f'用户_{random.randint(1000, 9999)}',
            'followers': random.randint(100, 50000),
            'following': random.randint(50, 1000),
            'posts_count': random.randint(50, 2000),
            'avg_likes': random.randint(10, 1000),
            'avg_comments': random.randint(1, 50),
            'location': random.choice(['北京', '上海', '深圳', '广州', '杭州', '成都']),
            'interests': random.sample([
                '科技', '美食', '旅行', '健身', '音乐', '电影',
                '游戏', '阅读', '摄影', '时尚', '教育', '投资'
            ], k=random.randint(2, 5)),
            'active_hours': random.sample(list(range(24)), k=random.randint(3, 8))
        }

    @staticmethod
    def analyze_profile(user_data: Dict) -> Dict:
        """分析用户画像"""
        # 计算影响力
        follower_count = user_data['followers']
        following_count = user_data['following']

        if follower_count > 10000:
            influence_level = 'high'
            influence_score = min(100, 60 + (follower_count / 10000) * 10)
        elif follower_count > 1000:
            influence_level = 'medium'
            influence_score = min(60, 30 + (follower_count / 1000) * 10)
        else:
            influence_level = 'low'
            influence_score = min(30, follower_count / 100)

        # 活跃时间分析
        active_hours = user_data['active_hours']
        if not active_hours:
            peak_hours = []
        else:
            # 找出活跃高峰时段
            hour_freq = defaultdict(int)
            for hour in active_hours:
                hour_freq[hour] += 1

            peak_hours = [h for h, count in sorted(hour_freq.items(), key=lambda x: x[1], reverse=True)[:3]]

        # 内容质量
        avg_likes = user_data['avg_likes']
        avg_comments = user_data['avg_comments']
        avg_engagement = avg_likes + avg_comments * 2  # 评论权重更高

        if avg_engagement > 500:
            quality_level = 'high'
        elif avg_engagement > 100:
            quality_level = 'medium'
        else:
            quality_level = 'low'

        # 账号健康度
        follower_ratio = follower_count / following_count if following_count > 0 else 0

        health_score = min(100, 0)
        if follower_ratio > 1:
            health_score += 40
        if quality_level == 'high':
            health_score += 30
        elif quality_level == 'medium':
            health_score += 20
        if influence_level == 'high':
            health_score += 30
        elif influence_level == 'medium':
            health_score += 10

        return {
            'influence': {
                'level': influence_level,
                'score': round(influence_score, 2)
            },
            'activity': {
                'peak_hours': sorted(peak_hours),
                'active_hours_count': len(active_hours)
            },
            'content': {
                'quality_level': quality_level,
                'avg_engagement': avg_engagement
            },
            'interests': user_data['interests'],
            'location': user_data['location'],
            'health': {
                'score': round(health_score, 2),
                'level': 'healthy' if health_score > 70 else 'normal' if health_score > 40 else 'needs_improvement'
            }
        }


class MarketingEvaluator:
    """营销效果评估器"""

    @staticmethod
    def generate_mock_campaign_data(campaign_id: str, days: int = 30) -> Dict:
        """生成模拟营销数据"""
        data = {
            'campaign_id': campaign_id,
            'name': f'营销活动_{campaign_id}',
            'start_date': (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
            'end_date': datetime.now().strftime('%Y-%m-%d'),
            'budget': random.randint(5000, 50000),
            'daily_data': []
        }

        total_revenue = 0

        for i in range(days):
            date = (datetime.now() - timedelta(days=days - i - 1)).strftime('%Y-%m-%d')

            # 模拟营销效果
            impressions = random.randint(1000, 10000)
            clicks = int(impressions * random.uniform(0.01, 0.05))
            conversions = int(clicks * random.uniform(0.05, 0.2))
            revenue = conversions * random.randint(50, 200)

            total_revenue += revenue

            data['daily_data'].append({
                'date': date,
                'impressions': impressions,
                'clicks': clicks,
                'conversions': conversions,
                'revenue': revenue,
                'cost': data['budget'] / days  # 平均分摊成本
            })

        data['total_revenue'] = total_revenue

        return data

    @staticmethod
    def evaluate_campaign(data: Dict) -> Dict:
        """评估营销活动效果"""
        daily_data = data['daily_data']

        # 汇总数据
        total_impressions = sum(d['impressions'] for d in daily_data)
        total_clicks = sum(d['clicks'] for d in daily_data)
        total_conversions = sum(d['conversions'] for d in daily_data)
        total_revenue = data['total_revenue']
        total_cost = data['budget']

        # 计算指标
        ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        cpa = (total_cost / total_conversions) if total_conversions > 0 else 0
        roi = ((total_revenue - total_cost) / total_cost * 100) if total_cost > 0 else 0

        # 评估效果等级
        if roi > 100:
            effectiveness = 'excellent'
        elif roi > 50:
            effectiveness = 'good'
        elif roi > 0:
            effectiveness = 'acceptable'
        else:
            effectiveness = 'poor'

        # 趋势分析
        clicks_trend = [d['clicks'] for d in daily_data]
        conversions_trend = [d['conversions'] for d in daily_data]

        if len(clicks_trend) > 1:
            clicks_growth = (clicks_trend[-1] - clicks_trend[0]) / clicks_trend[0] * 100
            conversions_growth = (conversions_trend[-1] - conversions_trend[0]) / conversions_trend[0] * 100
        else:
            clicks_growth = 0
            conversions_growth = 0

        return {
            'campaign_name': data['name'],
            'effectiveness': effectiveness,
            'metrics': {
                'impressions': total_impressions,
                'clicks': total_clicks,
                'conversions': total_conversions,
                'revenue': total_revenue,
                'cost': total_cost,
                'profit': total_revenue - total_cost,
                'ctr': round(ctr, 2),
                'conversion_rate': round(conversion_rate, 2),
                'cpa': round(cpa, 2),
                'roi': round(roi, 2)
            },
            'trend': {
                'clicks_growth': round(clicks_growth, 2),
                'conversions_growth': round(conversions_growth, 2)
            }
        }


def analyze_sentiment(text: str) -> Dict:
    """分析单条文本情感"""
    analyzer = SentimentAnalyzer()
    return analyzer.analyze(text)


def monitor_keyword(keyword: str, days: int = 7) -> Dict:
    """监控关键词"""
    monitor = BrandMonitor()
    return monitor.monitor(keyword, days)


def analyze_trend(topic: str, days: int = 7) -> Dict:
    """分析话题趋势"""
    data = TrendAnalyzer.generate_mock_data(topic, days)
    return TrendAnalyzer.analyze_trend(data)


def create_user_profile(user_id: str) -> Dict:
    """创建用户画像"""
    user_data = UserProfiler.generate_mock_user_data(user_id)
    return UserProfiler.analyze_profile(user_data)


def evaluate_campaign(campaign_id: str) -> Dict:
    """评估营销活动"""
    data = MarketingEvaluator.generate_mock_campaign_data(campaign_id)
    return MarketingEvaluator.evaluate_campaign(data)


def main():
    parser = argparse.ArgumentParser(description='Social Media Analysis System')
    parser.add_argument('action',
                       choices=['analyze-trend', 'monitor', 'sentiment', 'batch-sentiment',
                               'profile', 'evaluate', 'report'],
                       help='Action to perform')
    parser.add_argument('--topic', help='Topic to analyze')
    parser.add_argument('--keyword', help='Keyword to monitor')
    parser.add_argument('--text', help='Text to analyze sentiment')
    parser.add_argument('--input', help='Input file for batch processing')
    parser.add_argument('--user', help='User ID to profile')
    parser.add_argument('--campaign', help='Campaign ID to evaluate')
    parser.add_argument('--days', type=int, default=7, help='Number of days to analyze')
    parser.add_argument('--output', choices=['json', 'markdown'], default='json', help='Output format')

    args = parser.parse_args()

    if args.action == 'analyze-trend':
        if not args.topic:
            print('Error: --topic is required')
            return
        result = analyze_trend(args.topic, args.days)
        result['topic'] = args.topic

    elif args.action == 'monitor':
        if not args.keyword:
            print('Error: --keyword is required')
            return
        result = monitor_keyword(args.keyword, args.days)

    elif args.action == 'sentiment':
        if not args.text:
            print('Error: --text is required')
            return
        result = analyze_sentiment(args.text)

    elif args.action == 'profile':
        if not args.user:
            print('Error: --user is required')
            return
        result = create_user_profile(args.user)

    elif args.action == 'evaluate':
        if not args.campaign:
            print('Error: --campaign is required')
            return
        result = evaluate_campaign(args.campaign)

    else:
        result = {'error': 'Not implemented'}

    # 输出结果
    if args.output == 'json':
        print(json.dumps(result, indent=2, default=str))
    elif args.output == 'markdown':
        print(format_markdown(result))


def format_markdown(data: Dict) -> str:
    """格式化为Markdown"""
    lines = []

    if 'topic' in data:
        lines.append(f"# 话题趋势分析: {data['topic']}")
        lines.append('')
        lines.append(f"## 趋势类型")
        lines.append(f"- {data['trend_type']}")
        lines.append('')
        lines.append(f"## 增长率")
        lines.append(f"- {data['growth_rate']}%")
        lines.append('')
        lines.append(f"## 统计数据")
        lines.append(f"- 平均提及: {data['stats']['avg_mentions']}")
        lines.append(f"- 总提及: {data['stats']['total_mentions']}")
        lines.append('')
        if data['burst_points']:
            lines.append(f"## 爆发点")
            for point in data['burst_points']:
                lines.append(f"- {point}")

    elif 'keyword' in data:
        lines.append(f"# 关键词监控: {data['keyword']}")
        lines.append('')
        lines.append(f"## 总提及量")
        lines.append(f"- {data['total_mentions']}")
        lines.append('')
        lines.append(f"## 情感分布")
        for sent, pct in data['sentiment_distribution'].items():
            lines.append(f"- {sent}: {pct}%")

    elif 'sentiment' in data:
        lines.append("# 情感分析结果")
        lines.append('')
        lines.append(f"## 情感类型")
        lines.append(f"- {data['sentiment']}")
        lines.append('')
        lines.append(f"## 置信度")
        lines.append(f"- {data['confidence']}")
        lines.append('')
        lines.append(f"## 关键词")
        for kw in data.get('keywords', []):
            lines.append(f"- {kw}")

    elif 'campaign_name' in data:
        lines.append(f"# 营销活动评估: {data['campaign_name']}")
        lines.append('')
        lines.append(f"## 效果评级")
        lines.append(f"- {data['effectiveness']}")
        lines.append('')
        lines.append(f"## 核心指标")
        metrics = data['metrics']
        lines.append(f"- 展示量: {metrics['impressions']}")
        lines.append(f"- 点击数: {metrics['clicks']}")
        lines.append(f"- 转化数: {metrics['conversions']}")
        lines.append(f"- 收入: ¥{metrics['revenue']}")
        lines.append(f"- 成本: ¥{metrics['cost']}")
        lines.append(f"- 利润: ¥{metrics['profit']}")
        lines.append(f"- 点击率: {metrics['ctr']}%")
        lines.append(f"- 转化率: {metrics['conversion_rate']}%")
        lines.append(f"- ROI: {metrics['roi']}%")

    return '\n'.join(lines)


if __name__ == '__main__':
    main()
