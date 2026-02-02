"""
测试代码分析引擎
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from analyzers import CodeAnalyzer


def test_analyze_valid_code():
    """测试分析有效代码"""
    analyzer = CodeAnalyzer()

    code = """
def calculate(x, y):
    return x + y
"""

    result = analyzer.analyze(code, "python")
    assert result['valid'] is True
    assert result['supported'] is True
    assert 'metrics' in result
    assert 'issues' in result
    assert 'suggestions' in result

    print("✅ test_analyze_valid_code 通过")


def test_analyze_invalid_code():
    """测试分析无效代码"""
    analyzer = CodeAnalyzer()

    code = """
def calculate(x, y:
    return x + y
"""

    result = analyzer.analyze(code, "python")
    assert result['valid'] is False
    assert 'error' in result

    print("✅ test_analyze_invalid_code 通过")


def test_analyze_unsupported_language():
    """测试分析不支持的语言"""
    analyzer = CodeAnalyzer()

    code = "function add() { return 1 + 1; }"
    result = analyzer.analyze(code, "rust")
    assert result['supported'] is False

    print("✅ test_analyze_unsupported_language 通过")


def test_calculate_metrics():
    """测试计算代码指标"""
    analyzer = CodeAnalyzer()

    code = """
# This is a comment
def function1():
    pass

class MyClass:
    def method(self):
        pass
"""

    result = analyzer._calculate_metrics(code)
    assert result['total_lines'] > 0
    assert result['function_count'] >= 1
    assert result['class_count'] >= 1
    assert result['comment_lines'] >= 1

    print("✅ test_calculate_metrics 通过")


def test_find_issues():
    """测试查找代码问题"""
    analyzer = CodeAnalyzer()

    # 测试长行
    code = "x = " + "a" * 150 + "\n"
    issues = analyzer._find_issues(code)
    assert any(issue['type'] == 'line_too_long' for issue in issues)

    # 测试未使用的变量
    code = """
unused_var = 10
x = 5
"""
    issues = analyzer._find_issues(code)
    assert any(issue['type'] == 'unused_variable' for issue in issues)

    print("✅ test_find_issues 通过")


def test_generate_suggestions():
    """测试生成建议"""
    analyzer = CodeAnalyzer()

    code = """
def my_function(x, y):
    return x + y
"""

    suggestions = analyzer._generate_suggestions(code)
    # 应该有类型提示的建议
    assert isinstance(suggestions, list)

    # 测试有返回类型注解的函数
    code = """
def my_function(x: int, y: int) -> int:
    return x + y
"""
    suggestions = analyzer._generate_suggestions(code)
    assert isinstance(suggestions, list)

    print("✅ test_generate_suggestions 通过")


def test_get_score():
    """测试代码质量评分"""
    analyzer = CodeAnalyzer()

    # 简单代码
    simple_code = "def f(): pass"
    score = analyzer.get_score(simple_code)
    assert 0 <= score <= 100

    # 带注释的代码
    commented_code = """
# This is a function
# It does something
def function():
    # Return a value
    return 42
"""
    score = analyzer.get_score(commented_code)
    assert 0 <= score <= 100

    # 无效代码
    invalid_code = "def invalid(:"
    score = analyzer.get_score(invalid_code)
    assert score == 0.0

    print("✅ test_get_score 通过")


def test_analyze_complex_code():
    """测试分析复杂代码"""
    analyzer = CodeAnalyzer()

    code = """
import os
import sys

def calculate_total(price, quantity, discount):
    total = price * quantity
    final = total * (1 - discount)
    return final

class Order:
    def __init__(self, items):
        self.items = items

    def get_total(self):
        total = 0
        for item in self.items:
            total += item.price * item.quantity
        return total
"""

    result = analyzer.analyze(code, "python")
    assert result['valid'] is True
    assert result['metrics']['function_count'] >= 2
    assert result['metrics']['class_count'] >= 1
    assert result['metrics']['import_count'] >= 2

    # 检查复杂度
    complexity = result['complexity']
    assert 'complexity' in complexity
    assert complexity['complexity'] > 0

    print("✅ test_analyze_complex_code 通过")


if __name__ == "__main__":
    test_analyze_valid_code()
    test_analyze_invalid_code()
    test_analyze_unsupported_language()
    test_calculate_metrics()
    test_find_issues()
    test_generate_suggestions()
    test_get_score()
    test_analyze_complex_code()

    print("\n✅ 所有分析器测试通过！")
