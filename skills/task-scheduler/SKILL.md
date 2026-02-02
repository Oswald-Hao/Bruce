# Task Scheduler Optimizer - 定时任务优化器

## 功能描述

强大的定时任务管理系统，支持任务调度优化、任务依赖管理、分布式调度、任务监控等功能，提高定时任务的可靠性和效率。

## 核心功能

- 灵活调度（Cron表达式、间隔调度、定时调度）
- 任务依赖管理（依赖检查、依赖顺序、并行执行）
- 分布式调度（集群支持、任务分配、负载均衡）
- 任务监控（执行状态、执行历史、性能统计）
- 失败重试（自动重试、指数退避、重试策略）
- 任务队列（任务优先级、任务持久化、任务去重）
- 日志记录（详细日志、日志归档、日志分析）

## 安装依赖

```bash
pip install apscheduler croniter
pip install redis  # 用于分布式调度（可选）
```

## 使用方法

### 基础定时任务
```python
from task_scheduler import TaskScheduler

scheduler = TaskScheduler()

# 添加Cron任务
scheduler.add_cron_task(
    task_id="daily_backup",
    func=backup_database,
    cron_expr="0 2 * * *",  # 每天2:00
    args=["/backup/path"]
)

# 添加间隔任务
scheduler.add_interval_task(
    task_id="check_status",
    func=check_system_status,
    interval_minutes=5
)
```

### 任务依赖管理
```python
# 添加带依赖的任务
scheduler.add_task_with_dependencies(
    task_id="deploy_app",
    func=deploy_application,
    dependencies=["build_app", "run_tests"],
    cron_expr="0 */2 * * *"
)
```

### 分布式调度
```python
# 创建分布式调度器
scheduler = TaskScheduler(
    use_redis=True,
    redis_url="redis://localhost:6379/0"
)

scheduler.add_distributed_task(
    task_id="data_sync",
    func=sync_data,
    workers=3  # 3个工作节点
)
```

## 工具结构

```
skills/task-scheduler/
├── SKILL.md
├── README.md
├── src/
│   ├── __init__.py
│   ├── task_scheduler.py    # 主类
│   ├── task.py              # 任务定义
│   ├── scheduler.py         # 调度器实现
│   ├── dependency.py        # 依赖管理
│   ├── distributed.py       # 分布式调度
│   ├── monitor.py           # 任务监控
│   └── utils.py             # 工具函数
├── tests/
│   ├── test_task_scheduler.py
│   ├── test_scheduler.py
│   ├── test_dependency.py
│   ├── test_distributed.py
│   └── test_monitor.py
└── examples/
    ├── basic_usage.py
    ├── advanced_usage.py
    └── distributed_usage.py
```

## 测试

运行测试：
```bash
cd /home/lejurobot/clawd/skills/task-scheduler/
python -m pytest tests/ -v
```

## 创建时间

2026-02-03 00:45
