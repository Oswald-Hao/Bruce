#!/usr/bin/env python3
"""
社交媒体自动化系统 - 主程序
"""

import argparse
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

# 导入模块
from platforms.base import BasePlatform
from scheduler import ContentScheduler
from analytics import Analytics
from content_manager import ContentManager


class SocialMediaAutomation:
    """社交媒体自动化管理系统"""

    def __init__(self, config_path: str = "config.json"):
        """初始化系统"""
        self.config = self.load_config(config_path)
        self.scheduler = ContentScheduler(config_path)
        self.analytics = Analytics(config_path)
        self.content_manager = ContentManager(config_path)
        self.platforms = self.load_platforms()

    def load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        default_config = {
            "platforms": {},
            "scheduler": {
                "enabled": True,
                "check_interval": 60
            },
            "storage": {
                "content_db": "content_db.json",
                "scheduled_db": "scheduled_db.json",
                "analytics_db": "analytics_db.json"
            }
        }

        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            return default_config

    def load_platforms(self) -> Dict[str, BasePlatform]:
        """加载平台适配器"""
        platforms = {}

        # 加载各个平台的适配器
        platform_classes = {
            'douyin': 'platforms.douyin:DouyinPlatform',
            'xiaohongshu': 'platforms.xiaohongshu:XiaohongshuPlatform',
            'weibo': 'platforms.weibo:WeiboPlatform',
            'zhihu': 'platforms.zhihu:ZhihuPlatform',
        }

        for platform_name, class_path in platform_classes.items():
            try:
                module_path, class_name = class_path.split(':')
                module = __import__(module_path, fromlist=[class_name])
                platform_class = getattr(module, class_name)
                platforms[platform_name] = platform_class(self.config.get('platforms', {}).get(platform_name, {}))
            except Exception as e:
                print(f"⚠️  加载平台 {platform_name} 失败: {e}")

        return platforms

    def publish(
        self,
        content: str,
        platforms: List[str],
        media_files: List[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """发布内容到指定平台"""
        results = {}

        for platform_name in platforms:
            if platform_name not in self.platforms:
                results[platform_name] = {
                    'success': False,
                    'error': f'平台 {platform_name} 未配置'
                }
                continue

            try:
                platform = self.platforms[platform_name]
                result = platform.publish(content, media_files or [], **kwargs)

                # 记录到数据库
                self.content_manager.save_content(
                    platform_name=platform_name,
                    content=content,
                    media_files=media_files,
                    status=result.get('success', False),
                    post_id=result.get('post_id')
                )

                results[platform_name] = result

            except Exception as e:
                results[platform_name] = {
                    'success': False,
                    'error': str(e)
                }

        return results

    def schedule_publish(
        self,
        content: str,
        platforms: List[str],
        publish_time: str,
        media_files: List[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """定时发布内容"""
        try:
            # 解析时间
            publish_datetime = datetime.strptime(publish_time, "%Y-%m-%d %H:%M")

            # 添加到调度器
            task_id = self.scheduler.add_task(
                content=content,
                platforms=platforms,
                publish_time=publish_datetime,
                media_files=media_files,
                **kwargs
            )

            return {
                'success': True,
                'task_id': task_id,
                'publish_time': publish_time,
                'platforms': platforms
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def list_scheduled(self) -> List[Dict]:
        """列出所有定时任务"""
        return self.scheduler.list_tasks()

    def cancel_schedule(self, task_id: str) -> bool:
        """取消定时任务"""
        return self.scheduler.remove_task(task_id)

    def get_stats(self, days: int = 7) -> Dict[str, Any]:
        """获取统计数据"""
        return self.analytics.get_stats(days)

    def get_platform_stats(self, platform: str, days: int = 7) -> Dict[str, Any]:
        """获取指定平台的统计数据"""
        return self.analytics.get_platform_stats(platform, days)

    def get_content_library(self, platform: str = None) -> List[Dict]:
        """获取内容库"""
        return self.content_manager.list_content(platform)


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='社交媒体自动化系统')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 发布命令
    publish_parser = subparsers.add_parser('publish', help='发布内容')
    publish_parser.add_argument('--content', required=True, help='要发布的内容')
    publish_parser.add_argument('--platforms', required=True, help='平台列表，逗号分隔')
    publish_parser.add_argument('--media', help='媒体文件，逗号分隔')
    publish_parser.add_argument('--title', help='标题（部分平台需要）')

    # 定时发布命令
    schedule_parser = subparsers.add_parser('schedule', help='定时发布')
    schedule_parser.add_argument('--content', required=True, help='要发布的内容')
    schedule_parser.add_argument('--platforms', required=True, help='平台列表，逗号分隔')
    schedule_parser.add_argument('--time', required=True, help='发布时间，格式：YYYY-MM-DD HH:MM')
    schedule_parser.add_argument('--media', help='媒体文件，逗号分隔')
    schedule_parser.add_argument('--title', help='标题')

    # 列出定时任务
    subparsers.add_parser('list-scheduled', help='列出定时任务')

    # 取消定时任务
    cancel_parser = subparsers.add_parser('cancel-schedule', help='取消定时任务')
    cancel_parser.add_argument('--task-id', required=True, help='任务ID')

    # 统计命令
    stats_parser = subparsers.add_parser('stats', help='查看统计')
    stats_parser.add_argument('--days', type=int, default=7, help='统计天数')
    stats_parser.add_argument('--platform', help='指定平台')

    # 内容库命令
    library_parser = subparsers.add_parser('library', help='内容库')
    library_parser.add_argument('--platform', help='指定平台')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # 初始化系统
    sma = SocialMediaAutomation()

    # 执行命令
    if args.command == 'publish':
        platforms = args.platforms.split(',')
        media_files = args.media.split(',') if args.media else []

        results = sma.publish(
            content=args.content,
            platforms=platforms,
            media_files=media_files,
            title=getattr(args, 'title', None)
        )

        print("\n📤 发布结果:")
        for platform, result in results.items():
            status = "✅" if result.get('success') else "❌"
            print(f"  {status} {platform}: {result.get('error', '发布成功')}")

    elif args.command == 'schedule':
        platforms = args.platforms.split(',')
        media_files = args.media.split(',') if args.media else []

        result = sma.schedule_publish(
            content=args.content,
            platforms=platforms,
            publish_time=args.time,
            media_files=media_files,
            title=getattr(args, 'title', None)
        )

        if result['success']:
            print(f"\n✅ 定时任务已创建")
            print(f"   任务ID: {result['task_id']}")
            print(f"   发布时间: {result['publish_time']}")
            print(f"   目标平台: {', '.join(result['platforms'])}")
        else:
            print(f"\n❌ 创建失败: {result['error']}")

    elif args.command == 'list-scheduled':
        tasks = sma.list_scheduled()
        if tasks:
            print("\n📅 定时任务列表:")
            for task in tasks:
                print(f"  • ID: {task['task_id']}")
                print(f"    时间: {task['publish_time']}")
                print(f"    平台: {', '.join(task['platforms'])}")
                print(f"    内容: {task['content'][:50]}...")
                print()
        else:
            print("\n📭 暂无定时任务")

    elif args.command == 'cancel-schedule':
        if sma.cancel_schedule(args.task_id):
            print(f"\n✅ 任务 {args.task_id} 已取消")
        else:
            print(f"\n❌ 取消失败，任务ID不存在")

    elif args.command == 'stats':
        if args.platform:
            stats = sma.get_platform_stats(args.platform, args.days)
            print(f"\n📊 {args.platform} 统计 (最近{args.days}天):")
        else:
            stats = sma.get_stats(args.days)
            print(f"\n📊 综合统计 (最近{args.days}天):")

        print(f"  发布总数: {stats.get('total_posts', 0)}")
        print(f"  成功发布: {stats.get('successful_posts', 0)}")
        print(f"  失败发布: {stats.get('failed_posts', 0)}")
        print(f"  总浏览量: {stats.get('total_views', 0)}")
        print(f"  总互动量: {stats.get('total_engagement', 0)}")

        if 'by_platform' in stats:
            print("\n  各平台统计:")
            for platform, data in stats['by_platform'].items():
                print(f"    {platform}: {data.get('posts', 0)}篇, {data.get('views', 0)}浏览, {data.get('engagement', 0)}互动")

    elif args.command == 'library':
        contents = sma.get_content_library(args.platform)
        if contents:
            print(f"\n📚 内容库 (共{len(contents)}条):")
            for idx, content in enumerate(contents, 1):
                print(f"  {idx}. [{content['platform']}] {content['content'][:50]}...")
                print(f"     状态: {'✅' if content['status'] else '❌'} | 时间: {content['created_at']}")
        else:
            print("\n📭 内容库为空")


if __name__ == '__main__':
    main()
