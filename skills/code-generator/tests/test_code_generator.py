"""
测试 Code Generator 主类
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from code_generator import CodeGenerator


def test_complete_code_python():
    """测试Python代码补全"""
    generator = CodeGenerator()

    # 测试函数定义补全
    completion = generator.complete_code("def add_numbers(a, b)", "python")
    assert completion is not None
    assert ":" in completion or "pass" in completion

    # 测试类定义补全
    completion = generator.complete_code("class Calculator", "python")
    assert completion is not None
    assert ":" in completion or "__init__" in completion

    # 测试if语句补全
    completion = generator.complete_code("if condition", "python")
    assert completion is not None

    # 测试for循环补全
    completion = generator.complete_code("for item in items", "python")
    assert completion is not None

    print("✅ test_complete_code_python 通过")


def test_complete_code_javascript():
    """测试JavaScript代码补全"""
    generator = CodeGenerator()

    completion = generator.complete_code("function add(a, b)", "javascript")
    assert completion is not None

    print("✅ test_complete_code_javascript 通过")


def test_refactor_code():
    """测试代码重构"""
    generator = CodeGenerator()

    # 测试表达式简化
    code = """
result = value * 1
total = result + 0
"""
    result = generator.refactor_code(code, "low")
    assert result['success'] is True
    assert 'refactored' in result

    # 测试完整重构
    code = """
result = []
for item in items:
    result.append(item * 2)
"""
    result = generator.refactor_code(code, "medium")
    assert result['success'] is True
    assert len(result['changes']) > 0 or 'refactored' in result

    print("✅ test_refactor_code 通过")


def test_analyze_code():
    """测试代码分析"""
    generator = CodeGenerator()

    code = """
def calculate_sum(a, b):
    return a + b

class Calculator:
    def __init__(self):
        self.value = 0
"""
    result = generator.analyze_code(code, "python")
    assert result['valid'] is True
    assert 'metrics' in result
    assert 'issues' in result
    assert result['metrics']['function_count'] >= 1

    print("✅ test_analyze_code 通过")


def test_generate_function():
    """测试函数生成"""
    generator = CodeGenerator()

    func_code = generator.generate_function("add", "Add two numbers", "python")
    assert "def add" in func_code
    assert "Add two numbers" in func_code

    func_code = generator.generate_function("subtract", "Subtract two numbers", "javascript")
    assert "function subtract" in func_code

    print("✅ test_generate_function 通过")


def test_generate_class():
    """测试类生成"""
    generator = CodeGenerator()

    class_code = generator.generate_class("Calculator", "A simple calculator", "python")
    assert "class Calculator" in class_code
    assert "A simple calculator" in class_code

    class_code = generator.generate_class("User", "User class", "javascript")
    assert "class User" in class_code

    print("✅ test_generate_class 通过")


def test_get_code_quality_score():
    """测试代码质量评分"""
    generator = CodeGenerator()

    # 测试简单代码
    simple_code = "def f(): pass"
    score = generator.get_code_quality_score(simple_code, "python")
    assert 0 <= score <= 100

    # 测试更复杂的代码
    complex_code = '''
def calculate(x, y):
    """
    Calculate something
    """
    if x > 0:
        return x + y
    else:
        return x - y
'''
    score = generator.get_code_quality_score(complex_code, "python")
    assert 0 <= score <= 100

    print("✅ test_get_code_quality_score 通过")


if __name__ == "__main__":
    test_complete_code_python()
    test_complete_code_javascript()
    test_refactor_code()
    test_analyze_code()
    test_generate_function()
    test_generate_class()
    test_get_code_quality_score()

    print("\n✅ 所有测试通过！")
