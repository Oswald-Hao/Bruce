"""
内容管理器 - 管理发布的内容
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any


class ContentManager:
    """内容管理器"""

    def __init__(self, config_path: str = "config.json"):
        """初始化内容管理器"""
        self.config = self._load_config(config_path)
        self.content_db = self.config['storage']['content_db']
        self.contents = self._load_contents()

    def _load_config(self, config_path: str) -> Dict:
        """加载配置"""
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'storage': {
                'content_db': 'content_db.json'
            }
        }

    def _load_contents(self) -> List[Dict]:
        """加载内容列表"""
        if os.path.exists(self.content_db):
            with open(self.content_db, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_contents(self):
        """保存内容列表"""
        with open(self.content_db, 'w', encoding='utf-8') as f:
            json.dump(self.contents, f, indent=2, ensure_ascii=False)

    def save_content(
        self,
        platform_name: str,
        content: str,
        media_files: List[str] = None,
        status: bool = False,
        post_id: str = None
    ) -> str:
        """
        保存内容记录

        Args:
            platform_name: 平台名称
            content: 内容文本
            media_files: 媒体文件
            status: 发布状态
            post_id: 帖子ID

        Returns:
            记录ID
        """
        import uuid
        content_id = str(uuid.uuid4())[:8]

        record = {
            'content_id': content_id,
            'platform': platform_name,
            'content': content,
            'media_files': media_files or [],
            'status': status,
            'post_id': post_id,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.contents.append(record)
        self._save_contents()

        return content_id

    def list_content(self, platform: str = None) -> List[Dict]:
        """
        列出内容

        Args:
            platform: 平台过滤（可选）

        Returns:
            内容列表
        """
        if platform:
            return [c for c in self.contents if c['platform'] == platform]
        return self.contents

    def get_content(self, content_id: str) -> Dict:
        """获取单条内容"""
        for content in self.contents:
            if content['content_id'] == content_id:
                return content
        return None

    def update_content(self, content_id: str, **kwargs):
        """更新内容"""
        for content in self.contents:
            if content['content_id'] == content_id:
                content.update(kwargs)
                self._save_contents()
                break

    def delete_content(self, content_id: str) -> bool:
        """删除内容"""
        for idx, content in enumerate(self.contents):
            if content['content_id'] == content_id:
                self.contents.pop(idx)
                self._save_contents()
                return True
        return False

    def get_stats(self, days: int = 7) -> Dict[str, Any]:
        """获取内容统计"""
        cutoff_time = datetime.now() - datetime.timedelta(days=days)

        filtered_contents = [
            c for c in self.contents
            if datetime.strptime(c['created_at'], "%Y-%m-%d %H:%M:%S") > cutoff_time
        ]

        total = len(filtered_contents)
        successful = len([c for c in filtered_contents if c['status']])
        failed = total - successful

        # 按平台统计
        by_platform = {}
        for content in filtered_contents:
            platform = content['platform']
            if platform not in by_platform:
                by_platform[platform] = {'total': 0, 'successful': 0, 'failed': 0}
            by_platform[platform]['total'] += 1
            if content['status']:
                by_platform[platform]['successful'] += 1
            else:
                by_platform[platform]['failed'] += 1

        return {
            'total': total,
            'successful': successful,
            'failed': failed,
            'by_platform': by_platform
        }
