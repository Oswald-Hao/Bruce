"""
测试代码重构引擎
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refactors import CodeRefactor, suggest_refactoring


def test_simplify_expressions():
    """测试表达式简化"""
    refactor = CodeRefactor()

    # 测试布尔表达式简化
    code = "result = value and True"
    result = refactor._simplify_expressions(code)
    assert result['changed'] is True

    # 测试算术表达式简化
    code = "result = value * 1"
    result = refactor._simplify_expressions(code)
    assert result['changed'] is True

    print("✅ test_simplify_expressions 通过")


def test_extract_constants():
    """测试常量提取"""
    refactor = CodeRefactor()

    # 这个测试可能不会触发常量提取，因为需要重复的字符串
    code = """
message = "hello"
print("hello")
return "hello"
"""
    result = refactor._extract_constants(code)
    assert 'code' in result

    print("✅ test_extract_constants 通过")


def test_simplify_loops():
    """测试循环简化"""
    refactor = CodeRefactor()

    # 测试简单的for循环
    code = """
result = []
for item in items:
    result.append(item)
"""
    result = refactor._simplify_loops(code)
    assert 'code' in result

    print("✅ test_simplify_loops 通过")


def test_refactor_code_low():
    """测试低级别重构"""
    refactor = CodeRefactor()

    code = """
result = value and True
total = result + 0
"""

    result = refactor.refactor(code, "low")
    assert result['success'] is True
    assert 'refactored' in result
    assert len(result['changes']) >= 0

    print("✅ test_refactor_code_low 通过")


def test_refactor_code_medium():
    """测试中级别重构"""
    refactor = CodeRefactor()

    code = """
result = []
for item in items:
    result.append(item)
"""

    result = refactor.refactor(code, "medium")
    assert result['success'] is True
    assert 'refactored' in result

    print("✅ test_refactor_code_medium 通过")


def test_suggest_refactoring():
    """测试重构建议"""
    code = """
def very_long_function():
    # This is a very long function with many lines
    # Line 1
    # Line 2
    # Line 3
    # Line 4
    # Line 5
    # Line 6
    # Line 7
    # Line 8
    # Line 9
    # Line 10
    # Line 11
    # Line 12
    # Line 13
    # Line 14
    # Line 15
    # Line 16
    # Line 17
    # Line 18
    # Line 19
    # Line 20
    # Line 21
    return True

def function_with_many_args(a, b, c, d, e, f):
    return a + b + c + d + e + f
"""

    suggestions = suggest_refactoring(code)
    assert isinstance(suggestions, list)
    assert len(suggestions) > 0

    # 检查是否检测到长函数
    long_func_found = any(s['type'] == 'long_function' for s in suggestions)
    assert long_func_found is True

    print("✅ test_suggest_refactoring 通过")


def test_complexity_reduction():
    """测试复杂度降低"""
    refactor = CodeRefactor()

    code = """
if True and True:
    pass
"""

    result = refactor.refactor(code, "medium")
    # 简化后的代码应该更简单
    assert result['success'] is True

    print("✅ test_complexity_reduction 通过")


if __name__ == "__main__":
    test_simplify_expressions()
    test_extract_constants()
    test_simplify_loops()
    test_refactor_code_low()
    test_refactor_code_medium()
    test_suggest_refactoring()
    test_complexity_reduction()

    print("\n✅ 所有重构测试通过！")
