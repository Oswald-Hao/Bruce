"""
调度器实现
"""

import time
import threading
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime


# 由于循环导入问题，这些类在运行时动态获取
Task = None
CronTask = None
IntervalTask = None


def set_task_classes(task_cls, cron_task_cls, interval_task_cls):
    """设置任务类（避免循环导入）"""
    global Task, CronTask, IntervalTask
    Task = task_cls
    CronTask = cron_task_cls
    IntervalTask = interval_task_cls


def generate_task_id(func: Callable, *args, **kwargs) -> str:
    """生成任务ID"""
    import hashlib
    import json

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


class Scheduler:
    """任务调度器"""

    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.running = False
        self.thread = None
        self.lock = threading.Lock()
        self.on_task_start = None
        self.on_task_success = None
        self.on_task_failure = None

    def add_task(
        self,
        task: Task
    ) -> str:
        """添加任务"""
        with self.lock:
            self.tasks[task.task_id] = task
            return task.task_id

    def add_cron_task(
        self,
        func: Callable,
        cron_expr: str,
        args: tuple = (),
        kwargs: dict = None,
        max_retries: int = 3,
        task_id: Optional[str] = None
    ) -> str:
        """添加Cron任务"""
        if not task_id:
            task_id = generate_task_id(func, *args, **kwargs)

        task = CronTask(
            task_id=task_id,
            func=func,
            cron_expr=cron_expr,
            args=args,
            kwargs=kwargs,
            max_retries=max_retries
        )

        return self.add_task(task)

    def add_interval_task(
        self,
        func: Callable,
        interval_seconds: float,
        args: tuple = (),
        kwargs: dict = None,
        max_retries: int = 3,
        task_id: Optional[str] = None
    ) -> str:
        """添加间隔任务"""
        if not task_id:
            task_id = generate_task_id(func, *args, **kwargs)

        task = IntervalTask(
            task_id=task_id,
            func=func,
            interval_seconds=interval_seconds,
            args=args,
            kwargs=kwargs,
            max_retries=max_retries
        )

        return self.add_task(task)

    def remove_task(self, task_id: str) -> bool:
        """移除任务"""
        with self.lock:
            if task_id in self.tasks:
                del self.tasks[task_id]
                return True
            return False

    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        with self.lock:
            return self.tasks.get(task_id)

    def list_tasks(self) -> List[dict]:
        """列出所有任务"""
        with self.lock:
            return [task.to_dict() for task in self.tasks.values()]

    def start(self):
        """启动调度器"""
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """停止调度器"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5.0)

    def _run_loop(self):
        """调度循环"""
        while self.running:
            try:
                self._check_and_run_tasks()
                time.sleep(1)  # 每秒检查一次
            except Exception as e:
                print(f"调度器错误: {e}")

    def _check_and_run_tasks(self):
        """检查并运行任务"""
        with self.lock:
            tasks_to_run = [
                task
                for task in self.tasks.values()
                if hasattr(task, 'should_run') and task.should_run()
            ]

        for task in tasks_to_run:
            self._execute_task(task)

    def _execute_task(self, task: Task):
        """执行任务"""
        # 触发任务开始回调
        if self.on_task_start:
            self.on_task_start(task)

        try:
            # 执行任务
            result = task.run()

            # 更新状态
            if hasattr(task, 'after_run'):
                task.after_run()

            # 触发成功回调
            if self.on_task_success:
                self.on_task_success(task, result)

        except Exception as e:
            print(f"任务执行失败: {task.task_id}, 错误: {e}")

            # 检查是否需要重试
            if task.should_retry():
                print(f"任务 {task.task_id} 将在 {task.retry_delay}s 后重试")
                time.sleep(task.retry_delay)
                self._execute_task(task)
            else:
                # 触发失败回调
                if self.on_task_failure:
                    self.on_task_failure(task, e)

    def get_statistics(self) -> dict:
        """获取统计信息"""
        with self.lock:
            total_tasks = len(self.tasks)
            running_tasks = sum(1 for t in self.tasks.values() if t.status == 'running')
            success_tasks = sum(t.success_count for t in self.tasks.values())
            failure_tasks = sum(t.failure_count for t in self.tasks.values())

            return {
                'total_tasks': total_tasks,
                'running_tasks': running_tasks,
                'total_runs': sum(t.run_count for t in self.tasks.values()),
                'total_successes': success_tasks,
                'total_failures': failure_tasks,
                'success_rate': success_tasks / (success_tasks + failure_tasks) if (success_tasks + failure_tasks) > 0 else 0.0
            }

    def clear_tasks(self):
        """清空所有任务"""
        with self.lock:
            self.tasks.clear()
