# Log Analyzer - 日志分析系统

## 技能描述

智能日志分析工具，支持日志挖掘、异常检测、性能分析、错误统计、趋势分析等功能。

## 核心功能

- 日志解析（多种日志格式）
- 异常检测（错误、警告、异常堆栈）
- 性能分析（响应时间、吞吐量、延迟）
- 错误统计（按类型、频次、趋势）
- 日志搜索（关键词、正则表达式）
- 报告生成（文本、JSON、CSV）

## 使用方法

### 基本日志分析
```python
from log_analyzer import LogAnalyzer

# 初始化
analyzer = LogAnalyzer()

# 分析日志文件
result = analyzer.analyze('app.log')
print(result)
# {'total_lines': 1000, 'errors': 10, 'warnings': 50, 'errors_by_type': {...}}
```

### 日志搜索
```python
# 关键词搜索
matches = analyzer.search('app.log', keywords=['ERROR', 'CRITICAL'])
print(f"找到 {len(matches)} 条匹配")

# 正则表达式搜索
pattern = r'\d{4}-\d{2}-\d{2}.*ERROR'
matches = analyzer.search_regex('app.log', pattern)
```

### 异常检测
```python
# 检测错误
errors = analyzer.detect_errors('app.log')

# 检测异常模式
patterns = analyzer.detect_patterns('app.log')
```

### 性能分析
```python
# 分析Apache/Nginx访问日志
performance = analyzer.analyze_performance('access.log')

# 分析响应时间分布
time_dist = performance['response_time_distribution']
```

### 生成报告
```python
# 生成文本报告
analyzer.generate_report('app.log', 'report.txt')

# 生成JSON报告
analyzer.generate_report('app.log', 'report.json', format='json')

# 生成CSV报告
analyzer.generate_report('app.log', 'report.csv', format='csv')
```

## 支持的日志格式

- 通用文本日志
- Apache访问日志
- Nginx访问日志
- 自定义格式（支持正则表达式）

## 依赖安装

```bash
# 无额外依赖，使用Python标准库
```

## 文件结构

- log_analyzer.py - 主程序
- test_log_analyzer.py - 测试脚本
- SKILL.md - 技能文档
