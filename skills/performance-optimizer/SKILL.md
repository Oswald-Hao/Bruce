# 性能优化工具 - SKILL.md

## 技能描述

提供全面的性能分析、优化建议和瓶颈定位能力，支持代码分析、资源监控和自动优化。

## 核心功能

- 代码性能分析（执行时间、内存使用、调用链）
- 瓶颈定位（热点代码、慢查询、资源泄漏）
- 优化建议（代码重构、算法优化、缓存策略）
- 资源监控（CPU、内存、I/O实时监控）
- 性能报告生成（JSON/HTML/Markdown）
- 批量分析支持

## 安装依赖

```bash
pip install psutil memory-profiler line-profiler
```

## 使用方法

### 1. 代码性能分析

```python
from performance_optimizer import PerformanceOptimizer

optimizer = PerformanceOptimizer()

# 分析Python脚本
result = optimizer.analyze_script("path/to/script.py")
print(result.report)

# 分析函数
from performance_optimizer import profile_function

@profile_function
def my_function():
    # 你的代码
    pass

my_function()
```

### 2. 实时资源监控

```python
# 启动监控
monitor = optimizer.start_monitor(duration=60, interval=1)

# 获取监控数据
print(monitor.cpu_usage)
print(monitor.memory_usage)
print(monitor.io_stats)
```

### 3. 生成性能报告

```python
# 生成HTML报告
report = optimizer.generate_html_report(result, "performance_report.html")

# 生成Markdown报告
report = optimizer.generate_markdown_report(result, "performance_report.md")
```

### 4. 批量分析

```python
# 分析多个文件
results = optimizer.batch_analyze(["file1.py", "file2.py", "file3.py"])
```

## 命令行工具

```bash
# 分析脚本
python skills/performance-optimizer/analyze.py script.py

# 生成性能报告
python skills/performance-optimizer/report.py --output report.html

# 实时监控
python skills/performance-optimizer/monitor.py --duration 60
```

## 输出示例

### 性能分析报告

```json
{
  "script": "example.py",
  "total_time": 2.345,
  "functions": [
    {
      "name": "process_data",
      "time": 1.234,
      "calls": 100,
      "avg_time": 0.01234,
      "memory_peak": 45.6
    }
  ],
  "bottlenecks": [
    {
      "type": "slow_query",
      "location": "example.py:45",
      "time": 0.567,
      "suggestion": "添加数据库索引或使用缓存"
    }
  ]
}
```

## 核心价值

- **代码优化：** 发现性能瓶颈，提供优化建议
- **资源管理：** 监控资源使用，避免资源泄漏
- **开发效率：** 快速定位问题，减少调试时间
- **自动化：** 自动化性能测试，集成到CI/CD

## 测试

```bash
# 运行所有测试
python skills/performance-optimizer/test.py

# 运行特定测试
python skills/performance-optimizer/test.py --test analyze
python skills/performance-optimizer/test.py --test monitor
python skills/performance-optimizer/test.py --test optimize
```

## 注意事项

- 性能分析会添加额外开销，不要在生产环境长期运行
- 内存分析需要重启Python进程
- 使用 @profile 装饰器会影响函数性能，仅用于分析
