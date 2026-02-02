"""
Task Scheduler Optimizer - 主类
"""

from typing import Dict, List, Optional, Callable, Any
import os
import importlib.util

# 动态导入模块（避免相对导入问题）
def load_module(name, file_path):
    spec = importlib.util.spec_from_file_location(name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

src_dir = os.path.dirname(os.path.abspath(__file__))
utils_module = load_module("utils", os.path.join(src_dir, "utils.py"))
task_module = load_module("task", os.path.join(src_dir, "task.py"))
scheduler_module = load_module("scheduler", os.path.join(src_dir, "scheduler.py"))

# 设置循环引用
scheduler_module.set_task_classes(
    task_module.Task,
    task_module.CronTask,
    task_module.IntervalTask
)

Scheduler = scheduler_module.Scheduler
Task = task_module.Task
CronTask = task_module.CronTask
IntervalTask = task_module.IntervalTask
validate_task_function = utils_module.validate_task_function
validate_cron_expression = utils_module.validate_cron_expression
format_duration = utils_module.format_duration


class TaskScheduler:
    """任务调度优化器"""

    def __init__(self, use_redis: bool = False, redis_url: str = None):
        """
        初始化任务调度器

        Args:
            use_redis: 是否使用Redis进行分布式调度
            redis_url: Redis连接URL
        """
        self.scheduler = Scheduler()
        self.use_redis = use_redis
        self.redis_url = redis_url

        if use_redis:
            print("警告: Redis分布式调度需要额外配置")

    # 任务管理方法
    def add_task(self, task: Task) -> str:
        """添加任务"""
        return self.scheduler.add_task(task)

    def add_cron_task(
        self,
        task_id: str,
        func: Callable,
        cron_expr: str,
        args: tuple = (),
        kwargs: dict = None,
        max_retries: int = 3
    ) -> str:
        """
        添加Cron定时任务

        Args:
            task_id: 任务ID
            func: 任务函数
            cron_expr: Cron表达式（例如：0 2 * * * 表示每天2:00）
            args: 位置参数
            kwargs: 关键字参数
            max_retries: 最大重试次数

        Returns:
            任务ID
        """
        return self.scheduler.add_cron_task(
            func=func,
            cron_expr=cron_expr,
            args=args,
            kwargs=kwargs,
            max_retries=max_retries,
            task_id=task_id
        )

    def add_interval_task(
        self,
        task_id: str,
        func: Callable,
        interval_seconds: float,
        args: tuple = (),
        kwargs: dict = None,
        max_retries: int = 3
    ) -> str:
        """
        添加间隔任务

        Args:
            task_id: 任务ID
            func: 任务函数
            interval_seconds: 间隔秒数
            args: 位置参数
            kwargs: 关键字参数
            max_retries: 最大重试次数

        Returns:
            任务ID
        """
        return self.scheduler.add_interval_task(
            func=func,
            interval_seconds=interval_seconds,
            args=args,
            kwargs=kwargs,
            max_retries=max_retries,
            task_id=task_id
        )

    def remove_task(self, task_id: str) -> bool:
        """移除任务"""
        return self.scheduler.remove_task(task_id)

    def get_task(self, task_id: str) -> Optional[dict]:
        """获取任务详情"""
        task = self.scheduler.get_task(task_id)
        if task:
            return task.to_dict()
        return None

    def list_tasks(self) -> List[dict]:
        """列出所有任务"""
        return self.scheduler.list_tasks()

    # 控制方法
    def start(self):
        """启动调度器"""
        self.scheduler.start()

    def stop(self):
        """停止调度器"""
        self.scheduler.stop()

    def is_running(self) -> bool:
        """检查调度器是否在运行"""
        return self.scheduler.running

    # 回调设置
    def on_task_start(self, callback: Callable[[Task], None]):
        """设置任务开始回调"""
        self.scheduler.on_task_start = callback

    def on_task_success(self, callback: Callable[[Task, Any], None]):
        """设置任务成功回调"""
        self.scheduler.on_task_success = callback

    def on_task_failure(self, callback: Callable[[Task, Exception], None]):
        """设置任务失败回调"""
        self.scheduler.on_task_failure = callback

    # 统计信息
    def get_statistics(self) -> dict:
        """获取统计信息"""
        return self.scheduler.get_statistics()

    def clear_tasks(self):
        """清空所有任务"""
        self.scheduler.clear_tasks()

    # 高级功能
    def add_task_with_dependencies(
        self,
        task_id: str,
        func: Callable,
        dependencies: List[str],
        cron_expr: Optional[str] = None,
        interval_seconds: Optional[float] = None,
        args: tuple = (),
        kwargs: dict = None,
        max_retries: int = 3
    ) -> str:
        """
        添加带依赖的任务

        注意：这是简化版，实际依赖管理需要更复杂的实现

        Args:
            task_id: 任务ID
            func: 任务函数
            dependencies: 依赖的任务ID列表
            cron_expr: Cron表达式（可选）
            interval_seconds: 间隔秒数（可选）
            args: 位置参数
            kwargs: 关键字参数
            max_retries: 最大重试次数

        Returns:
            任务ID
        """
        # 检查依赖是否存在
        for dep_id in dependencies:
            if not self.scheduler.get_task(dep_id):
                raise ValueError(f"依赖任务不存在: {dep_id}")

        # 添加任务（依赖信息可以存储在task的元数据中）
        if cron_expr:
            task_id = self.add_cron_task(
                task_id=task_id,
                func=func,
                cron_expr=cron_expr,
                args=args,
                kwargs=kwargs,
                max_retries=max_retries
            )
        elif interval_seconds:
            task_id = self.add_interval_task(
                task_id=task_id,
                func=func,
                interval_seconds=interval_seconds,
                args=args,
                kwargs=kwargs,
                max_retries=max_retries
            )
        else:
            raise ValueError("必须提供cron_expr或interval_seconds")

        return task_id

    def add_distributed_task(
        self,
        task_id: str,
        func: Callable,
        cron_expr: str,
        args: tuple = (),
        kwargs: dict = None,
        max_retries: int = 3,
        workers: int = 1
    ) -> str:
        """
        添加分布式任务

        注意：这是简化版，需要Redis或类似的分布式队列

        Args:
            task_id: 任务ID
            func: 任务函数
            cron_expr: Cron表达式
            args: 位置参数
            kwargs: 关键字参数
            max_retries: 最大重试次数
            workers: 工作节点数量

        Returns:
            任务ID
        """
        if not self.use_redis:
            raise ValueError("分布式任务需要启用Redis支持")

        # 实际应用中，这里应该将任务添加到Redis队列
        # 简化版仍然添加到本地调度器
        task_id = self.add_cron_task(
            task_id=task_id,
            func=func,
            cron_expr=cron_expr,
            args=args,
            kwargs=kwargs,
            max_retries=max_retries
        )

        print(f"分布式任务 {task_id} 已添加（workers={workers}）")
        return task_id

    def get_task_history(
        self,
        task_id: str,
        limit: int = 10
    ) -> List[dict]:
        """
        获取任务执行历史

        注意：这是简化版，实际应用中需要持久化历史记录

        Args:
            task_id: 任务ID
            limit: 返回的记录数量

        Returns:
            执行历史列表
        """
        task = self.scheduler.get_task(task_id)
        if not task:
            return []

        # 简化版只返回当前任务信息
        return [
            {
                'run_time': task.last_run_time,
                'status': task.status,
                'error': task.last_error
            }
        ]

    def get_failed_tasks(self) -> List[dict]:
        """获取所有失败的任务"""
        return [
            task.to_dict()
            for task in self.scheduler.tasks.values()
            if task.status == 'failed' and task.failure_count > 0
        ]

    def retry_failed_tasks(self):
        """重试所有失败的任务"""
        failed_tasks = self.get_failed_tasks()

        for task_data in failed_tasks:
            task = self.scheduler.get_task(task_data['task_id'])
            if task and task.should_retry():
                # 重置任务状态以便重试
                task.status = 'pending'
                task.last_error = None
                print(f"任务 {task.task_id} 已重置为待执行状态")
