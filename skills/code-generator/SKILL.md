# Code Generator - 代码生成优化器

## 功能描述

智能代码生成工具，支持智能补全、代码重构、代码改进建议等，提升开发效率。

## 核心功能

- 智能代码补全（基于上下文）
- 代码重构建议（优化结构、提取重复代码）
- 代码改进建议（性能优化、安全增强）
- 多语言支持（Python、JavaScript、TypeScript、Go等）
- 代码审查报告
- 自动化文档生成

## 安装依赖

```bash
pip install ast black pylint mypy pyflakes
pip install openai  # 用于AI辅助代码生成（可选）
```

## 使用方法

### 代码补全
```python
from code_generator import CodeGenerator

generator = CodeGenerator()
completion = generator.complete_code(
    code="def add_numbers(a, b):\n    ",
    language="python"
)
print(completion)
# 输出: return a + b
```

### 代码重构
```python
refactored = generator.refactor_code(
    code="""
def calculate_total(price, quantity, discount):
    result = price * quantity
    result = result * (1 - discount)
    return result
""",
    optimize_level="medium"
)
print(refactored)
```

### 代码审查
```python
suggestions = generator.analyze_code(
    code="your_code_here",
    language="python"
)
for suggestion in suggestions:
    print(f"[{suggestion['severity']}] {suggestion['message']}")
```

## 工具结构

```
skills/code-generator/
├── SKILL.md
├── README.md
├── src/
│   ├── __init__.py
│   ├── code_generator.py      # 主类
│   ├── completers.py          # 补全引擎
│   ├── refactors.py           # 重构引擎
│   ├── analyzers.py           # 分析引擎
│   └── utils.py               # 工具函数
├── templates/
│   ├── python/
│   ├── javascript/
│   └── go/
└── tests/
    ├── test_code_generator.py
    ├── test_completers.py
    ├── test_refactors.py
    └── test_analyzers.py
```

## 测试

运行测试：
```bash
cd /home/lejurobot/clawd/skills/code-generator/
python -m pytest tests/ -v
```

## 创建时间

2026-02-03 00:00
