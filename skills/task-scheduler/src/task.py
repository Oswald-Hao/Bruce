"""
任务定义
"""

import time
from typing import Callable, Any, Optional, Dict
from datetime import datetime
from .utils import (
    generate_task_id,
    validate_task_function,
    validate_cron_expression,
    serialize_task,
    deserialize_task
)


class Task:
    """任务类"""

    def __init__(
        self,
        task_id: str,
        func: Callable,
        args: tuple = (),
        kwargs: dict = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        timeout: Optional[float] = None
    ):
        self.task_id = task_id
        self.func = func
        self.args = args
        self.kwargs = kwargs or {}
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        self.created_at = datetime.now()
        self.last_run_time = None
        self.next_run_time = None
        self.run_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.last_error = None
        self.status = 'pending'  # pending, running, success, failed

    def run(self) -> Any:
        """执行任务"""
        if not validate_task_function(self.func):
            raise ValueError(f"Invalid task function: {self.func}")

        self.status = 'running'
        self.last_run_time = datetime.now()
        self.run_count += 1

        try:
            result = self.func(*self.args, **self.kwargs)
            self.status = 'success'
            self.success_count += 1
            self.last_error = None
            return result
        except Exception as e:
            self.status = 'failed'
            self.failure_count += 1
            self.last_error = str(e)
            raise

    def after_run(self):
        """运行后更新状态（可被子类重写）"""
        pass

    def should_retry(self) -> bool:
        """判断是否应该重试"""
        return self.failure_count < self.max_retries

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'task_id': self.task_id,
            'func_name': self.func.__name__,
            'args': self.args,
            'kwargs': self.kwargs,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
            'timeout': self.timeout,
            'created_at': self.created_at.isoformat(),
            'last_run_time': self.last_run_time.isoformat() if self.last_run_time else None,
            'next_run_time': self.next_run_time.isoformat() if self.next_run_time else None,
            'run_count': self.run_count,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'last_error': self.last_error,
            'status': self.status
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        """从字典创建任务（简化版）"""
        # 注意：这需要func可以从某个注册表获取
        return cls(
            task_id=data['task_id'],
            func=lambda: None,  # 实际应用中需要从注册表获取
            args=data.get('args', ()),
            kwargs=data.get('kwargs', {}),
            max_retries=data.get('max_retries', 3),
            retry_delay=data.get('retry_delay', 1.0),
            timeout=data.get('timeout')
        )


class CronTask(Task):
    """Cron定时任务"""

    def __init__(
        self,
        task_id: str,
        func: Callable,
        cron_expr: str,
        args: tuple = (),
        kwargs: dict = None,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        super().__init__(task_id, func, args, kwargs, max_retries, retry_delay)
        self.cron_expr = cron_expr

        if not validate_cron_expression(cron_expr):
            raise ValueError(f"Invalid cron expression: {cron_expr}")

        # 计算下次运行时间
        self.update_next_run_time()

    def update_next_run_time(self):
        """更新下次运行时间"""
        from .utils import calculate_next_run_time
        self.next_run_time = calculate_next_run_time(self.cron_expr)

    def should_run(self) -> bool:
        """判断是否应该运行"""
        if self.status == 'running':
            return False
        if self.next_run_time is None:
            return False

        return datetime.now() >= self.next_run_time

    def after_run(self):
        """运行后更新状态"""
        super().after_run()
        self.update_next_run_time()


class IntervalTask(Task):
    """间隔任务"""

    def __init__(
        self,
        task_id: str,
        func: Callable,
        interval_seconds: float,
        args: tuple = (),
        kwargs: dict = None,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        super().__init__(task_id, func, args, kwargs, max_retries, retry_delay)
        self.interval_seconds = interval_seconds
        self.update_next_run_time()

    def update_next_run_time(self):
        """更新下次运行时间"""
        from datetime import timedelta
        self.next_run_time = datetime.now() + timedelta(seconds=self.interval_seconds)

    def should_run(self) -> bool:
        """判断是否应该运行"""
        if self.status == 'running':
            return False
        if self.next_run_time is None:
            return False

        return datetime.now() >= self.next_run_time

    def after_run(self):
        """运行后更新状态"""
        super().after_run()
        self.update_next_run_time()
