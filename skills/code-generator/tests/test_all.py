"""
Code Generator - 简化测试套件

使用pytest框架运行测试
"""

import pytest
import sys
import os

# 添加src目录到路径
src_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, src_dir)

# 导入模块
from code_generator import CodeGenerator


def test_code_generator_complete():
    """测试代码补全"""
    generator = CodeGenerator()

    # 测试Python补全
    completion = generator.complete_code("def add(a, b)", "python")
    assert completion is not None

    # 测试JavaScript补全
    completion = generator.complete_code("function add(a, b)", "javascript")
    assert completion is not None

    print("✅ 代码补全测试通过")


def test_code_generator_refactor():
    """测试代码重构"""
    generator = CodeGenerator()

    code = """
result = []
for item in items:
    result.append(item * 2)
"""
    result = generator.refactor_code(code, "medium")
    assert result['success'] is True
    assert 'refactored' in result

    print("✅ 代码重构测试通过")


def test_code_generator_analyze():
    """测试代码分析"""
    generator = CodeGenerator()

    code = """
def calculate(x, y):
    return x + y
"""
    result = generator.analyze_code(code, "python")
    assert result['valid'] is True
    assert 'metrics' in result
    assert result['metrics']['function_count'] >= 1

    print("✅ 代码分析测试通过")


def test_code_generator_generate():
    """测试代码生成"""
    generator = CodeGenerator()

    # 生成函数
    func = generator.generate_function("add", "Add two numbers", "python")
    assert "def add" in func
    assert "Add two numbers" in func

    # 生成类
    cls = generator.generate_class("Calculator", "A calculator", "python")
    assert "class Calculator" in cls
    assert "A calculator" in cls

    print("✅ 代码生成测试通过")


def test_code_quality_score():
    """测试代码质量评分"""
    generator = CodeGenerator()

    code = "def f(): pass"
    score = generator.get_code_quality_score(code, "python")
    assert 0 <= score <= 100

    print("✅ 代码质量评分测试通过")


if __name__ == "__main__":
    # 直接运行测试
    test_code_generator_complete()
    test_code_generator_refactor()
    test_code_generator_analyze()
    test_code_generator_generate()
    test_code_quality_score()

    print("\n🎉 所有核心功能测试通过！")
