# 性能分析报告

**脚本:** /home/lejurobot/clawd/skills/performance-optimizer/test_scripts/md_report_test.py
**总执行时间:** 0.00s
**分析时间:** 2026-02-07T00:11:38.913332

## 函数性能

| 函数名 | 文件 | 行号 | 总时间(s) | 调用次数 | 平均时间(s) |
|--------|------|------|-----------|----------|-------------|
| <built-in method builtins.exec> | ~ | 0 | 0.0000 | 1 | 0.000004 |
| test_func | /home/lejurobot/clawd/skills/performance-optimizer/test_scripts/md_report_test.py | 2 | 0.0000 | 1 | 0.000000 |
| <module> | /home/lejurobot/clawd/skills/performance-optimizer/test_scripts/md_report_test.py | 1 | 0.0000 | 1 | 0.000001 |
| <method 'disable' of '_lsprof.Profiler' objects> | ~ | 0 | 0.0000 | 1 | 0.000000 |

## 性能瓶颈

### 1. slow_function

- **位置:** ~:0
- **影响:** 0.00
- **建议:** 函数'<built-in method builtins.exec>'执行时间过长(0.00s)。建议：1) 检查算法复杂度 2) 使用缓存 3) 异步处理

### 2. slow_function

- **位置:** /home/lejurobot/clawd/skills/performance-optimizer/test_scripts/md_report_test.py:1
- **影响:** 0.00
- **建议:** 函数'<module>'执行时间过长(0.00s)。建议：1) 检查算法复杂度 2) 使用缓存 3) 异步处理


## 优化建议

- ⚠️ 函数'<built-in method builtins.exec>'执行时间过长(0.00s)。建议：1) 检查算法复杂度 2) 使用缓存 3) 异步处理
- ⚠️ 函数'<module>'执行时间过长(0.00s)。建议：1) 检查算法复杂度 2) 使用缓存 3) 异步处理
- 💡 使用内置函数和库（如itertools, collections）替代手动实现
- 💡 考虑使用@lru_cache装饰器缓存函数结果
- 💡 对大列表使用生成器表达式替代列表推导式
- 💡 使用set/dict进行O(1)查找，避免在列表中线性搜索
- 💡 对于I/O密集型操作，考虑使用asyncio或多线程
