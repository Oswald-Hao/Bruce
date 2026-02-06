# 性能优化工具

提供全面的性能分析、优化建议和瓶颈定位能力。

## 功能

- 代码性能分析（执行时间、内存使用、调用链）
- 瓶颈定位（热点代码、慢查询、资源泄漏）
- 优化建议（代码重构、算法优化、缓存策略）
- 资源监控（CPU、内存、I/O实时监控）
- 性能报告生成（JSON/HTML/Markdown）
- 批量分析支持

## 安装

```bash
pip install psutil memory-profiler
```

## 快速开始

### 1. 分析脚本

```bash
python analyze.py script.py
```

### 2. 使用Python API

```python
from performance_optimizer import PerformanceOptimizer

optimizer = PerformanceOptimizer()
result = optimizer.analyze_script("script.py")

# 查看结果
print(result.total_time)
print(result.functions)
print(result.bottlenecks)
```

### 3. 装饰器分析函数

```python
from performance_optimizer import profile_function

@profile_function
def my_function():
    # 你的代码
    pass

my_function()
```

### 4. 资源监控

```python
optimizer = PerformanceOptimizer()
monitor = optimizer.start_monitor(duration=60, interval=1)

print(f"CPU: {monitor.cpu_usage}")
print(f"内存: {monitor.memory_usage}")
```

## 测试

```bash
python test.py
```

## 输出示例

```bash
分析脚本: example.py

总执行时间: 2.3450s

识别到 15 个函数:
  - main: 2.3450s (1次)
  - process_data: 1.2340s (100次)
  - load_data: 0.5670s (1次)

检测到 2 个瓶颈:
  - slow_function: 函数执行时间过长(1.234s)。建议：检查算法复杂度

报告已生成:
  - HTML: /path/to/performance_reports/report.html
  - Markdown: /path/to/performance_reports/report.md
```

## 技术栈

- Python 3.x
- psutil（系统监控）
- cProfile（性能分析）
- memory-profiler（内存分析）
