"""
测试代码补全引擎
"""

import sys
import os

# 添加src目录到路径
src_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, src_dir)

# 直接导入模块
import importlib.util
spec = importlib.util.spec_from_file_location("completers", os.path.join(src_dir, "completers.py"))
completers_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(completers_module)

PythonCompleter = completers_module.PythonCompleter
JavaScriptCompleter = completers_module.JavaScriptCompleter


def test_python_completer_function():
    """测试Python函数定义补全"""
    completer = PythonCompleter()

    completion = completer.complete("def add(a, b)", "python")
    assert completion is not None

    completion = completer.complete("def get_value", "python")
    assert completion is not None

    print("✅ test_python_completer_function 通过")


def test_python_completer_class():
    """测试Python类定义补全"""
    completer = PythonCompleter()

    completion = completer.complete("class Calculator", "python")
    assert completion is not None
    assert "__init__" in completion

    print("✅ test_python_completer_class 通过")


def test_python_completer_loops():
    """测试Python循环补全"""
    completer = PythonCompleter()

    # for循环
    completion = completer.complete("for item in items:", "python")
    assert completion is not None

    # while循环
    completion = completer.complete("while condition:", "python")
    assert completion is not None

    print("✅ test_python_completer_loops 通过")


def test_python_completer_conditions():
    """测试Python条件语句补全"""
    completer = PythonCompleter()

    # if语句
    completion = completer.complete("if x > 0:", "python")
    assert completion is not None

    # else语句
    completion = completer.complete("else", "python")
    assert completion is not None

    print("✅ test_python_completer_conditions 通过")


def test_python_completer_expressions():
    """测试Python表达式补全"""
    completer = PythonCompleter()

    # return语句
    completion = completer.complete("return", "python")
    assert completion is not None

    # 变量赋值
    completion = completer.complete("items =", "python")
    assert completion is not None

    print("✅ test_python_completer_expressions 通过")


def test_javascript_completer():
    """测试JavaScript补全"""
    completer = JavaScriptCompleter()

    # 函数定义
    completion = completer.complete("function add(a, b)", "javascript")
    assert completion is not None

    # 箭头函数
    completion = completer.complete("const add = (a, b) =>", "javascript")
    assert completion is not None

    # if语句
    completion = completer.complete("if (x > 0)", "javascript")
    assert completion is not None

    print("✅ test_javascript_completer 通过")


if __name__ == "__main__":
    test_python_completer_function()
    test_python_completer_class()
    test_python_completer_loops()
    test_python_completer_conditions()
    test_python_completer_expressions()
    test_javascript_completer()

    print("\n✅ 所有补全器测试通过！")
