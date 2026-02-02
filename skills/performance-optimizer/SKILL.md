# Performance Optimization Skill

性能优化工具 - 代码分析和性能瓶颈定位

## 功能说明

- 代码复杂度分析
- 性能瓶颈定位
- 资源使用分析（CPU/内存/IO）
- 代码热图分析
- 优化建议生成
- 性能对比报告

## 使用方式

```bash
# 分析代码性能
cd /home/lejurobot/clawd/skills/performance-optimizer
python3 performance_optimizer.py --analyze <file_or_directory>

# 生成性能报告
python3 performance_optimizer.py --report <results_file>

# 性能对比
python3 performance_optimizer.py --compare <old_results> <new_results>
```

## 测试用例

```bash
# 运行测试
cd /home/lejurobot/clawd/skills/performance-optimizer
python3 test_performance_optimizer.py
```

## 实现方式

Python 3 + cProfile（标准库） + pstats（性能统计） + ast（抽象语法树） + line_profiler（可选）
