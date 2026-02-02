"""
任务定义
"""

import time
from typing import Callable, Any, Optional, Dict
from datetime import datetime


def validate_task_function(func: Callable) -> bool:
    """验证任务函数是否有效"""
    return callable(func)


def validate_cron_expression(cron_expr: str) -> bool:
    """验证Cron表达式是否有效"""
    try:
        parts = cron_expr.split()
        if len(parts) != 5:
            return False

        # 检查每部分是否为*或数字
        for part in parts:
            if part != '*':
                try:
                    # 检查是否为数字或范围（如1-5）或列表（如1,3,5）
                    if '-' in part:
                        start, end = part.split('-')
                        int(start)
                        int(end)
                    elif ',' in part:
                        for item in part.split(','):
                            int(item)
                    else:
                        int(part)
                except ValueError:
                    return False

        return True
    except Exception:
        return False


def generate_task_id(func: Callable, *args, **kwargs) -> str:
    """生成任务ID"""
    import hashlib
    import json

    # 使用函数名和参数生成唯一的任务ID
    func_name = func.__name__
    params_str = json.dumps({
        'args': str(args),
        'kwargs': str(kwargs)
    }, sort_keys=True)

    hash_input = f"{func_name}:{params_str}"
    hash_value = hashlib.md5(hash_input.encode()).hexdigest()
    return f"task_{func_name}_{hash_value[:8]}"


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
        def calculate_next_run_time_simple(cron_expr, current_time=None):
            """简化版的下次运行时间计算"""
            from datetime import timedelta

            if current_time is None:
                current_time = datetime.now()

            # 解析Cron表达式
            parts = cron_expr.split()
            minute = int(parts[0]) if parts[0] != '*' else current_time.minute
            hour = int(parts[1]) if parts[1] != '*' else current_time.hour

            # 构建下次运行时间
            next_time = current_time.replace(minute=minute, hour=hour, second=0, microsecond=0)

            # 如果已经过了这个时间，设置为明天
            if next_time <= current_time:
                next_time += timedelta(days=1)

            return next_time

        self.next_run_time = calculate_next_run_time_simple(self.cron_expr)

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
