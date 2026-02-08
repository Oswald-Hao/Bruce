"""
内容调度器 - 管理定时发布任务
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
import threading
import time


class ContentScheduler:
    """内容发布调度器"""

    def __init__(self, config_path: str = "config.json"):
        """初始化调度器"""
        self.config = self._load_config(config_path)
        self.scheduled_db = self.config['storage']['scheduled_db']
        self.tasks = self._load_tasks()
        self.running = False
        self.scheduler_thread = None

    def _load_config(self, config_path: str) -> Dict:
        """加载配置"""
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'storage': {
                'scheduled_db': 'scheduled_db.json'
            }
        }

    def _load_tasks(self) -> List[Dict]:
        """加载任务列表"""
        if os.path.exists(self.scheduled_db):
            with open(self.scheduled_db, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_tasks(self):
        """保存任务列表"""
        with open(self.scheduled_db, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, indent=2, ensure_ascii=False)

    def add_task(
        self,
        content: str,
        platforms: List[str],
        publish_time: datetime,
        media_files: List[str] = None,
        **kwargs
    ) -> str:
        """
        添加定时任务

        Args:
            content: 内容
            platforms: 平台列表
            publish_time: 发布时间
            media_files: 媒体文件
            **kwargs: 其他参数

        Returns:
            任务ID
        """
        import uuid
        task_id = str(uuid.uuid4())[:8]

        task = {
            'task_id': task_id,
            'content': content,
            'platforms': platforms,
            'publish_time': publish_time.strftime("%Y-%m-%d %H:%M:%S"),
            'media_files': media_files or [],
            'status': 'pending',
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'kwargs': kwargs
        }

        self.tasks.append(task)
        self._save_tasks()

        return task_id

    def remove_task(self, task_id: str) -> bool:
        """
        移除定时任务

        Args:
            task_id: 任务ID

        Returns:
            是否成功
        """
        for idx, task in enumerate(self.tasks):
            if task['task_id'] == task_id and task['status'] == 'pending':
                self.tasks.pop(idx)
                self._save_tasks()
                return True
        return False

    def list_tasks(self) -> List[Dict]:
        """列出所有任务"""
        # 按时间排序
        return sorted(self.tasks, key=lambda x: x['publish_time'])

    def get_pending_tasks(self) -> List[Dict]:
        """获取待执行的任务"""
        now = datetime.now()
        return [
            task for task in self.tasks
            if task['status'] == 'pending'
            and datetime.strptime(task['publish_time'], "%Y-%m-%d %H:%M:%S") <= now
        ]

    def mark_task_completed(self, task_id: str, result: Dict = None):
        """标记任务为已完成"""
        for task in self.tasks:
            if task['task_id'] == task_id:
                task['status'] = 'completed'
                task['completed_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                task['result'] = result
                self._save_tasks()
                break

    def mark_task_failed(self, task_id: str, error: str):
        """标记任务为失败"""
        for task in self.tasks:
            if task['task_id'] == task_id:
                task['status'] = 'failed'
                task['failed_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                task['error'] = error
                self._save_tasks()
                break

    def start_scheduler(self, callback):
        """
        启动调度器

        Args:
            callback: 执行任务的回调函数
        """
        if self.running:
            return

        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, args=(callback,))
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()

    def stop_scheduler(self):
        """停止调度器"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()

    def _scheduler_loop(self, callback):
        """调度器循环"""
        while self.running:
            try:
                pending_tasks = self.get_pending_tasks()
                for task in pending_tasks:
                    try:
                        result = callback(task)
                        self.mark_task_completed(task['task_id'], result)
                    except Exception as e:
                        self.mark_task_failed(task['task_id'], str(e))

                time.sleep(self.config.get('scheduler', {}).get('check_interval', 60))
            except Exception as e:
                print(f"⚠️  调度器错误: {e}")
                time.sleep(5)
