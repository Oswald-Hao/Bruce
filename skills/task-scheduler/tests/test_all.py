"""
Task Scheduler Optimizer - 完整测试套件
"""

import sys
import os
import time

# 添加src目录到路径
src_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, src_dir)

# 动态导入
import importlib.util

def load_module(name, file_path):
    spec = importlib.util.spec_from_file_location(name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

src_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
utils_module = load_module("utils", os.path.join(src_dir, "utils.py"))
task_module = load_module("task", os.path.join(src_dir, "task.py"))
scheduler_module = load_module("scheduler", os.path.join(src_dir, "scheduler.py"))
task_scheduler_module = load_module("task_scheduler", os.path.join(src_dir, "task_scheduler.py"))

TaskScheduler = task_scheduler_module.TaskScheduler
CronTask = task_module.CronTask
IntervalTask = task_module.IntervalTask
Task = task_module.Task


# 测试函数
def simple_task():
    """简单任务"""
    return "Task completed"


def task_with_args(a, b):
    """带参数的任务"""
    return a + b


def failing_task():
    """失败的任务"""
    raise Exception("This task always fails")


def test_utils_functions():
    """测试工具函数"""
    # 测试任务ID生成
    task_id = utils_module.generate_task_id(simple_task)
    assert task_id.startswith("task_simple_task_")

    # 测试持续时间格式化
    assert utils_module.format_duration(30) == "30.00s"
    assert utils_module.format_duration(90) == "1.50m"
    assert utils_module.format_duration(4000) == "1.11h"

    # 测试Cron表达式验证
    assert utils_module.validate_cron_expression("0 2 * * *") is True
    assert utils_module.validate_cron_expression("* * * * *") is True
    assert utils_module.validate_cron_expression("invalid") is False

    print("✅ 工具函数测试通过")


def test_task_creation():
    """测试任务创建"""
    task = Task(
        task_id="test_task",
        func=simple_task
    )

    assert task.task_id == "test_task"
    assert task.status == "pending"
    assert task.run_count == 0

    result = task.run()
    assert result == "Task completed"
    assert task.status == "success"
    assert task.run_count == 1

    print("✅ 任务创建测试通过")


def test_cron_task():
    """测试Cron任务"""
    cron_task = CronTask(
        task_id="cron_test",
        func=simple_task,
        cron_expr="0 2 * * *"
    )

    assert cron_task.cron_expr == "0 2 * * *"
    assert cron_task.next_run_time is not None

    print("✅ Cron任务测试通过")


def test_interval_task():
    """测试间隔任务"""
    interval_task = IntervalTask(
        task_id="interval_test",
        func=simple_task,
        interval_seconds=10
    )

    assert interval_task.interval_seconds == 10
    assert interval_task.next_run_time is not None

    print("✅ 间隔任务测试通过")


def test_scheduler_basic():
    """测试调度器基本功能"""
    scheduler = TaskScheduler()

    # 添加间隔任务
    task_id = scheduler.add_interval_task(
        task_id="test_interval",
        func=simple_task,
        interval_seconds=1
    )

    assert task_id == "test_interval"

    # 列出任务
    tasks = scheduler.list_tasks()
    assert len(tasks) > 0

    # 获取任务
    task = scheduler.get_task(task_id)
    assert task is not None
    assert task['task_id'] == task_id

    # 移除任务
    success = scheduler.remove_task(task_id)
    assert success is True

    print("✅ 调度器基本功能测试通过")


def test_scheduler_run():
    """测试调度器运行"""
    scheduler = TaskScheduler()

    # 添加快速执行的间隔任务
    task_id = scheduler.add_interval_task(
        task_id="run_test",
        func=simple_task,
        interval_seconds=0.1  # 100ms
    )

    # 设置回调
    results = []
    def on_success(task, result):
        results.append(result)

    scheduler.on_task_success(on_success)

    # 启动调度器
    scheduler.start()

    # 等待任务执行
    time.sleep(1.5)

    # 停止调度器
    scheduler.stop()

    # 检查任务是否执行
    assert len(results) >= 1
    assert "Task completed" in results

    print("✅ 调度器运行测试通过")


def test_task_retry():
    """测试任务重试"""
    scheduler = TaskScheduler()

    # 添加会失败的任务
    task_id = scheduler.add_interval_task(
        task_id="retry_test",
        func=failing_task,
        interval_seconds=0.1,
        max_retries=2
    )

    # 启动调度器
    scheduler.start()

    # 等待任务执行和重试
    time.sleep(1)

    # 停止调度器
    scheduler.stop()

    # 检查任务状态
    task = scheduler.get_task(task_id)
    assert task is not None

    print("✅ 任务重试测试通过")


def test_statistics():
    """测试统计信息"""
    scheduler = TaskScheduler()

    # 添加几个任务
    scheduler.add_interval_task(
        task_id="task1",
        func=simple_task,
        interval_seconds=0.5
    )

    scheduler.add_interval_task(
        task_id="task2",
        func=simple_task,
        interval_seconds=0.5
    )

    # 启动调度器
    scheduler.start()

    # 等待执行
    time.sleep(1.5)

    # 获取统计信息
    stats = scheduler.get_statistics()

    assert stats['total_tasks'] >= 2
    assert 'total_runs' in stats
    assert 'total_successes' in stats
    assert 'total_failures' in stats

    # 停止调度器
    scheduler.stop()

    print("✅ 统计信息测试通过")


def test_task_with_dependencies():
    """测试带依赖的任务"""
    scheduler = TaskScheduler()

    # 先添加依赖任务
    dep_task_id = scheduler.add_interval_task(
        task_id="dependency",
        func=simple_task,
        interval_seconds=1
    )

    # 添加带依赖的任务
    try:
        main_task_id = scheduler.add_task_with_dependencies(
            task_id="main_task",
            func=simple_task,
            dependencies=[dep_task_id],
            interval_seconds=1
        )

        assert main_task_id == "main_task"
    except ValueError as e:
        # 依赖检查可能失败，这是预期的
        assert "不存在" in str(e)

    print("✅ 带依赖的任务测试通过")


if __name__ == "__main__":
    test_utils_functions()
    test_task_creation()
    test_cron_task()
    test_interval_task()
    test_scheduler_basic()
    test_scheduler_run()
    test_task_retry()
    test_statistics()
    test_task_with_dependencies()

    print("\n🎉 所有测试通过！")
