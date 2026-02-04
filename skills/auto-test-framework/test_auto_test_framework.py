#!/usr/bin/env python3
"""
自动化测试框架的测试用例
"""

import sys
import os
import time
import tempfile
import shutil

# 添加技能目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auto_test_framework import (
    UnitTest,
    IntegrationTest,
    PerformanceTest,
    UITest,
    CoverageAnalyzer,
    TestReporter
)


def test_unit_test_basic():
    """测试单元测试基础功能"""
    print("测试1: 单元测试基础功能...")

    test = UnitTest()

    # 添加测试用例
    test.add_test({
        'name': 'test_addition',
        'code': '''
def test_addition():
    assert 2 + 2 == 4
    assert 1 + 1 != 3
''',
        'type': 'function'
    })

    # 运行测试
    result = test.run()

    assert result['total'] == 1
    assert result['passed'] == 1
    assert result['failed'] == 0

    print("✅ 单元测试基础功能测试通过")


def test_unit_test_multiple():
    """测试多个单元测试"""
    print("测试2: 多个单元测试...")

    test = UnitTest()

    # 添加多个测试用例
    test.add_test({
        'name': 'test_addition',
        'code': '''
def test_addition():
    assert 2 + 2 == 4
''',
        'type': 'function'
    })

    test.add_test({
        'name': 'test_subtraction',
        'code': '''
def test_subtraction():
    assert 5 - 3 == 2
''',
        'type': 'function'
    })

    # 运行测试
    result = test.run()

    assert result['total'] == 2
    assert result['passed'] >= 1  # 至少一个通过

    print("✅ 多个单元测试通过")


def test_performance_test():
    """测试性能测试"""
    print("测试3: 性能测试...")

    perf_test = PerformanceTest()

    # 添加性能测试（sleep 0.1秒，最大允许0.15秒）
    perf_test.add_test({
        'name': 'test_sleep_performance',
        'function': lambda: time.sleep(0.1),
        'max_duration': 0.15,
        'iterations': 10
    })

    # 运行测试
    result = perf_test.run()

    assert result['total'] == 1
    assert result['passed'] == 1
    assert result['results'][0]['avg_duration'] >= 0.1

    print("✅ 性能测试通过")


def test_performance_test_failure():
    """测试性能测试失败场景"""
    print("测试4: 性能测试失败场景...")

    perf_test = PerformanceTest()

    # 添加性能测试（sleep 0.2秒，最大允许0.1秒 - 应该失败）
    perf_test.add_test({
        'name': 'test_sleep_failure',
        'function': lambda: time.sleep(0.2),
        'max_duration': 0.1,
        'iterations': 5
    })

    # 运行测试
    result = perf_test.run()

    assert result['total'] == 1
    assert result['failed'] == 1  # 应该失败

    print("✅ 性能测试失败场景测试通过")


def test_integration_test_mock():
    """测试集成测试（模拟模式）"""
    print("测试5: 集成测试（模拟模式）...")

    test = IntegrationTest(base_url='http://localhost:8000')

    # 添加测试用例（无端点，只测试结构）
    test.add_test({
        'name': 'test_structure',
        'type': 'mock'
    })

    # 运行测试
    result = test.run()

    assert 'total' in result
    assert 'passed' in result
    assert 'failed' in result

    print("✅ 集成测试（模拟模式）通过")


def test_ui_test_mock():
    """测试UI测试（模拟模式）"""
    print("测试6: UI测试（模拟模式）...")

    test = UITest()

    # 如果没有Playwright，测试应该能正常运行
    result = test.run(headless=True)

    assert 'total' in result
    assert 'passed' in result
    assert 'failed' in result

    print("✅ UI测试（模拟模式）通过")


def test_coverage_analyzer():
    """测试覆盖率分析器"""
    print("测试7: 覆盖率分析器...")

    analyzer = CoverageAnalyzer(module_path='./src')

    # 运行分析（如果pytest-cov不可用，应该返回0）
    result = analyzer.analyze()

    assert 'percentage' in result
    assert 'missing_lines' in result
    assert isinstance(result['percentage'], (int, float))

    print("✅ 覆盖率分析器测试通过")


def test_reporter_html():
    """测试HTML报告生成"""
    print("测试8: HTML报告生成...")

    # 创建临时目录
    temp_dir = tempfile.mkdtemp()

    try:
        reporter = TestReporter(output_dir=temp_dir)

        # 添加模拟测试结果
        reporter.add_result({
            'total': 10,
            'passed': 8,
            'failed': 2
        })

        # 生成HTML报告
        html_path = reporter.generate_html()

        assert os.path.exists(html_path)
        assert html_path.endswith('.html')

        # 检查内容
        with open(html_path, 'r') as f:
            content = f.read()
            assert 'Test Report' in content
            assert '10' in content
            assert '8' in content
            assert '2' in content

        print("✅ HTML报告生成测试通过")

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)


def test_reporter_json():
    """测试JSON报告生成"""
    print("测试9: JSON报告生成...")

    # 创建临时目录
    temp_dir = tempfile.mkdtemp()

    try:
        reporter = TestReporter(output_dir=temp_dir)

        # 添加模拟测试结果
        reporter.add_result({
            'total': 5,
            'passed': 5,
            'failed': 0
        })

        # 生成JSON报告
        json_path = reporter.generate_json()

        assert os.path.exists(json_path)
        assert json_path.endswith('.json')

        # 检查内容
        import json
        with open(json_path, 'r') as f:
            data = json.load(f)
            assert 'summary' in data
            assert data['summary']['total'] == 5
            assert data['summary']['passed'] == 5

        print("✅ JSON报告生成测试通过")

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)


def test_reporter_markdown():
    """测试Markdown报告生成"""
    print("测试10: Markdown报告生成...")

    # 创建临时目录
    temp_dir = tempfile.mkdtemp()

    try:
        reporter = TestReporter(output_dir=temp_dir)

        # 添加模拟测试结果
        reporter.add_result({
            'total': 3,
            'passed': 2,
            'failed': 1
        })

        # 生成Markdown报告
        md_path = reporter.generate_markdown()

        assert os.path.exists(md_path)
        assert md_path.endswith('.md')

        # 检查内容
        with open(md_path, 'r') as f:
            content = f.read()
            assert '# Test Report' in content
            assert '3' in content
            assert '2' in content
            assert '1' in content

        print("✅ Markdown报告生成测试通过")

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("开始测试自动化测试框架")
    print("=" * 60)

    tests = [
        test_unit_test_basic,
        test_unit_test_multiple,
        test_performance_test,
        test_performance_test_failure,
        test_integration_test_mock,
        test_ui_test_mock,
        test_coverage_analyzer,
        test_reporter_html,
        test_reporter_json,
        test_reporter_markdown,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            failed += 1
            print(f"❌ 测试失败: {test.__name__}")
            print(f"   错误: {e}")
        except Exception as e:
            failed += 1
            print(f"❌ 测试异常: {test.__name__}")
            print(f"   错误: {e}")

    print("=" * 60)
    print(f"测试完成: {passed} 通过, {failed} 失败")
    print("=" * 60)

    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
