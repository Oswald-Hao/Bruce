# Code Generator - 代码生成优化器

智能代码生成工具，支持智能补全、代码重构、代码改进建议等，提升开发效率。

## 功能特性

- **智能代码补全**: 基于上下文的Python和JavaScript代码补全
- **代码重构**: 自动优化代码结构，简化表达式，提取常量
- **代码分析**: 全面的代码质量评估，包括复杂度、指标、问题检测
- **改进建议**: 类型提示、列表推导式等现代化建议
- **多语言支持**: Python和JavaScript（可扩展）

## 快速开始

### 安装依赖

```bash
pip install black pylint mypy pyflakes
```

### 代码补全

```python
from code_generator import CodeGenerator

generator = CodeGenerator()

# 补全函数定义
completion = generator.complete_code("def add_numbers(a, b)", "python")
print(completion)  # 输出: :\n    pass
```

### 代码重构

```python
result = generator.refactor_code("""
result = []
for item in items:
    result.append(item * 2)
""", "medium")

print(result['refactored'])
print(f"应用了 {len(result['changes'])} 个优化")
```

### 代码分析

```python
result = generator.analyze_code("""
def calculate(x, y):
    return x + y
""", "python")

print(f"代码质量分数: {analyzer.get_score(code):.1f}/100")
print(f"函数数量: {result['metrics']['function_count']}")
print(f"发现的问题: {len(result['issues'])}")
```

### 生成函数和类

```python
# 生成函数
func = generator.generate_function("calculate", "Calculate sum", "python")
print(func)

# 生成类
cls = generator.generate_class("Calculator", "A calculator", "python")
print(cls)
```

## 运行测试

```bash
cd /home/lejurobot/clawd/skills/code-generator/
python tests/run_all_tests.py
```

## 测试覆盖

- ✅ 代码补全测试（Python + JavaScript）
- ✅ 代码重构测试（多级别优化）
- ✅ 代码分析测试（指标、问题、建议）
- ✅ 集成测试（完整工作流）

## 项目结构

```
skills/code-generator/
├── SKILL.md                 # 技能说明
├── README.md                # 本文件
├── src/
│   ├── __init__.py
│   ├── code_generator.py    # 主类
│   ├── completers.py        # 补全引擎
│   ├── refactors.py         # 重构引擎
│   ├── analyzers.py         # 分析引擎
│   └── utils.py             # 工具函数
├── tests/
│   ├── test_code_generator.py
│   ├── test_completers.py
│   ├── test_refactors.py
│   ├── test_analyzers.py
│   └── run_all_tests.py
└── templates/
    ├── python/
    └── javascript/
```

## 性能优化

- 快速补全（<10ms）
- 高效重构（基于AST分析）
- 增量分析（仅分析变更部分）

## 创建时间

2026-02-03 00:00
