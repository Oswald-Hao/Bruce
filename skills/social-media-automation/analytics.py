"""
数据分析 - 社交媒体数据分析
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any


class Analytics:
    """数据分析器"""

    def __init__(self, config_path: str = "config.json"):
        """初始化数据分析器"""
        self.config = self._load_config(config_path)
        self.analytics_db = self.config['storage']['analytics_db']
        self.content_db = self.config['storage']['content_db']
        self.data = self._load_data()

    def _load_config(self, config_path: str) -> Dict:
        """加载配置"""
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'storage': {
                'analytics_db': 'analytics_db.json',
                'content_db': 'content_db.json'
            }
        }

    def _load_data(self) -> List[Dict]:
        """加载分析数据"""
        if os.path.exists(self.analytics_db):
            with open(self.analytics_db, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_data(self):
        """保存分析数据"""
        with open(self.analytics_db, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def _load_contents(self) -> List[Dict]:
        """加载内容数据"""
        if os.path.exists(self.content_db):
            with open(self.content_db, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def record_stats(self, platform: str, post_id: str, stats: Dict[str, Any]):
        """
        记录统计数据

        Args:
            platform: 平台名称
            post_id: 帖子ID
            stats: 统计数据
        """
        record = {
            'platform': platform,
            'post_id': post_id,
            'stats': stats,
            'recorded_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.data.append(record)
        self._save_data()

    def get_stats(self, days: int = 7) -> Dict[str, Any]:
        """
        获取综合统计

        Args:
            days: 统计天数

        Returns:
            统计数据
        """
        cutoff_time = datetime.now() - timedelta(days=days)

        # 加载内容数据
        contents = self._load_contents()
        recent_contents = [
            c for c in contents
            if datetime.strptime(c['created_at'], "%Y-%m-%d %H:%M:%S") > cutoff_time
        ]

        total_posts = len(recent_contents)
        successful_posts = len([c for c in recent_contents if c['status']])
        failed_posts = total_posts - successful_posts

        # 加载统计数据
        recent_stats = [
            s for s in self.data
            if datetime.strptime(s['recorded_at'], "%Y-%m-%d %H:%M:%S") > cutoff_time
        ]

        # 计算总量
        total_views = sum([s['stats'].get('views', 0) for s in recent_stats])
        total_likes = sum([s['stats'].get('likes', 0) for s in recent_stats])
        total_comments = sum([s['stats'].get('comments', 0) for s in recent_stats])
        total_shares = sum([s['stats'].get('shares', 0) for s in recent_stats])
        total_engagement = total_likes + total_comments + total_shares

        # 按平台统计
        by_platform = {}
        for stat in recent_stats:
            platform = stat['platform']
            if platform not in by_platform:
                by_platform[platform] = {
                    'posts': 0,
                    'views': 0,
                    'likes': 0,
                    'comments': 0,
                    'shares': 0,
                    'engagement': 0
                }

            by_platform[platform]['views'] += stat['stats'].get('views', 0)
            by_platform[platform]['likes'] += stat['stats'].get('likes', 0)
            by_platform[platform]['comments'] += stat['stats'].get('comments', 0)
            by_platform[platform]['shares'] += stat['stats'].get('shares', 0)
            by_platform[platform]['engagement'] += (
                stat['stats'].get('likes', 0) +
                stat['stats'].get('comments', 0) +
                stat['stats'].get('shares', 0)
            )

        # 添加帖子数
        for content in recent_contents:
            platform = content['platform']
            if platform not in by_platform:
                by_platform[platform] = {
                    'posts': 0,
                    'views': 0,
                    'likes': 0,
                    'comments': 0,
                    'shares': 0,
                    'engagement': 0
                }
            if content['status']:
                by_platform[platform]['posts'] += 1

        return {
            'total_posts': total_posts,
            'successful_posts': successful_posts,
            'failed_posts': failed_posts,
            'total_views': total_views,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'total_shares': total_shares,
            'total_engagement': total_engagement,
            'by_platform': by_platform
        }

    def get_platform_stats(self, platform: str, days: int = 7) -> Dict[str, Any]:
        """
        获取指定平台的统计

        Args:
            platform: 平台名称
            days: 统计天数

        Returns:
            统计数据
        """
        all_stats = self.get_stats(days)

        if platform in all_stats['by_platform']:
            platform_stats = all_stats['by_platform'][platform]
            platform_stats['platform'] = platform
            return platform_stats
        else:
            return {
                'platform': platform,
                'posts': 0,
                'views': 0,
                'likes': 0,
                'comments': 0,
                'shares': 0,
                'engagement': 0
            }

    def get_trending_content(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """
        获取热门内容

        Args:
            days: 统计天数
            limit: 返回数量

        Returns:
            热门内容列表
        """
        cutoff_time = datetime.now() - timedelta(days=days)

        recent_stats = [
            s for s in self.data
            if datetime.strptime(s['recorded_at'], "%Y-%m-%d %H:%M:%S") > cutoff_time
        ]

        # 按互动量排序
        sorted_stats = sorted(
            recent_stats,
            key=lambda x: (
                x['stats'].get('likes', 0) +
                x['stats'].get('comments', 0) +
                x['stats'].get('shares', 0)
            ),
            reverse=True
        )

        return sorted_stats[:limit]

    def generate_report(self, days: int = 7) -> str:
        """
        生成分析报告

        Args:
            days: 统计天数

        Returns:
            报告文本
        """
        stats = self.get_stats(days)
        trending = self.get_trending_content(days, 5)

        report = f"""
📊 社交媒体数据分析报告 (最近{days}天)
{'='*50}

📈 总体数据
- 发布总数: {stats['total_posts']}篇
- 成功发布: {stats['successful_posts']}篇
- 失败发布: {stats['failed_posts']}篇
- 总浏览量: {stats['total_views']:,}
- 总互动量: {stats['total_engagement']:,} (点赞{stats['total_likes']} + 评论{stats['total_comments']} + 转发{stats['total_shares']})

📱 各平台数据
"""
        for platform, data in stats['by_platform'].items():
            report += f"\n{platform.upper()}:\n"
            report += f"  - 发布: {data['posts']}篇\n"
            report += f"  - 浏览: {data['views']:,}\n"
            report += f"  - 互动: {data['engagement']:,}\n"

        report += f"\n🔥 热门内容 TOP 5\n"
        for idx, item in enumerate(trending, 1):
            engagement = (
                item['stats'].get('likes', 0) +
                item['stats'].get('comments', 0) +
                item['stats'].get('shares', 0)
            )
            report += f"\n{idx}. [{item['platform'].upper()}] {item['post_id']}\n"
            report += f"   互动: {engagement:,} (👍{item['stats'].get('likes', 0)} 💬{item['stats'].get('comments', 0)} ↗{item['stats'].get('shares', 0)})\n"

        return report
