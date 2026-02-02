# Task Scheduler Optimizer - 定时任务优化器

强大的定时任务管理系统，支持任务调度优化、任务依赖管理、分布式调度、任务监控等功能，提高定时任务的可靠性和效率。

## 功能特性

- **灵活调度**: Cron表达式、间隔调度、定时调度
- **任务依赖**: 依赖检查、依赖顺序、并行执行
- **失败重试**: 自动重试、指数退避、重试策略
- **任务监控**: 执行状态、执行历史、性能统计
- **任务队列**: 任务优先级、任务持久化、任务去重
- **日志记录**: 详细日志、执行统计

## 快速开始

### 基础定时任务
```python
from task_scheduler import TaskScheduler

scheduler = TaskScheduler()

# 添加Cron任务（每天2:00执行）
scheduler.add_cron_task(
    task_id="daily_backup",
    func=backup_database,
    cron_expr="0 2 * * *",
    args=["/backup/path"]
)

# 添加间隔任务（每5分钟执行）
scheduler.add_interval_task(
    task_id="check_status",
    func=check_system_status,
    interval_seconds=300
)

# 启动调度器
scheduler.start()
```

### 带回调的任务
```python
# 设置回调
def on_success(task, result):
    print(f"任务 {task.task_id} 成功: {result}")

def on_failure(task, error):
    print(f"任务 {task.task_id} 失败: {error}")

scheduler.on_task_success(on_success)
scheduler.on_task_failure(on_failure)
```

### 任务统计
```python
# 获取统计信息
stats = scheduler.get_statistics()
print(f"总任务数: {stats['total_tasks']}")
print(f"总执行次数: {stats['total_runs']}")
print(f"成功率: {stats['success_rate']:.2%}")
```

## 运行测试

```bash
cd /home/lejurobot/clawd/skills/task-scheduler/
python tests/test_all.py
```

## 测试覆盖

- ✅ 工具函数测试（任务ID生成、Cron验证）
- ✅ 任务创建测试（基础任务、Cron任务、间隔任务）
- ✅ 调度器基本功能（添加、删除、列表）
- ✅ 调度器运行测试
- ✅ 任务重试测试
- ✅ 统计信息测试
- ✅ 依赖管理测试

## 项目结构

```
skills/task-scheduler/
├── SKILL.md
├── README.md
├── src/
│   ├── __init__.py
│   ├── task_scheduler.py    # 主类
│   ├── task.py              # 任务定义
│   ├── scheduler.py         # 调度器实现
│   └── utils.py             # 工具函数
└── tests/
    └── test_all.py
```

## 核心价值

1. **简化定时任务管理**: 统一的API，支持多种调度方式
2. **提高可靠性**: 自动重试、错误处理、任务监控
3. **灵活扩展**: 易于添加新的调度策略
4. **性能优化**: 高效的任务调度和执行

## 依赖项

- Python 3.7+
- threading (标准库)
- apscheduler (可选，用于更精确的Cron调度)
- croniter (可选，用于Cron表达式解析)

## 创建时间

2026-02-03 00:45
