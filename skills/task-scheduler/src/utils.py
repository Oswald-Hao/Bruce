"""
工具函数
"""

import time
import hashlib
import json
from typing import Any, Callable, Optional
from datetime import datetime


def generate_task_id(func: Callable, *args, **kwargs) -> str:
    """生成任务ID"""
    # 使用函数名和参数生成唯一的任务ID
    func_name = func.__name__
    params_str = json.dumps({
        'args': str(args),
        'kwargs': str(kwargs)
    }, sort_keys=True)

    hash_input = f"{func_name}:{params_str}"
    hash_value = hashlib.md5(hash_input.encode()).hexdigest()
    return f"task_{func_name}_{hash_value[:8]}"


def format_duration(seconds: float) -> str:
    """格式化持续时间"""
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        return f"{seconds/60:.2f}m"
    else:
        return f"{seconds/3600:.2f}h"


def parse_cron_expression(cron_expr: str) -> dict:
    """解析Cron表达式

    格式: 分 时 日 月 周
    示例: "0 2 * * *" 每天2:00
    """
    parts = cron_expr.split()
    if len(parts) != 5:
        raise ValueError(f"Invalid cron expression: {cron_expr}")

    return {
        'minute': parts[0],
        'hour': parts[1],
        'day': parts[2],
        'month': parts[3],
        'day_of_week': parts[4]
    }


def calculate_next_run_time(
    cron_expr: str,
    current_time: Optional[datetime] = None
) -> datetime:
    """计算下次运行时间（简化版）

    完整版需要使用croniter库
    """
    try:
        from croniter import croniter
        if current_time is None:
            current_time = datetime.now()
        cron = croniter(cron_expr, current_time)
        return cron.get_next(datetime)
    except ImportError:
        # 如果没有croniter，使用简化计算
        print("警告: croniter未安装，使用简化计算")
        return calculate_next_run_time_simple(cron_expr, current_time)


def calculate_next_run_time_simple(
    cron_expr: str,
    current_time: Optional[datetime] = None
) -> datetime:
    """简化版的下次运行时间计算"""
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
        from datetime import timedelta
        next_time += timedelta(days=1)

    return next_time


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


def serialize_task(task: dict) -> str:
    """序列化任务"""
    return json.dumps(task, default=str)


def deserialize_task(task_str: str) -> dict:
    """反序列化任务"""
    return json.loads(task_str)


def should_retry(
    attempt: int,
    max_retries: int,
    backoff_factor: float = 2.0
) -> bool:
    """判断是否应该重试"""
    return attempt < max_retries


def calculate_backoff_time(
    attempt: int,
    base_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 300.0
) -> float:
    """计算退避时间（指数退避）"""
    delay = base_delay * (backoff_factor ** attempt)
    return min(delay, max_delay)
