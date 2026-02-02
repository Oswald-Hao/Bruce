#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Log Analyzer 测试脚本
测试日志解析、搜索、错误检测、性能分析等功能
"""

import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(__file__))

from log_analyzer import LogAnalyzer


def create_test_log(filepath: str):
    """创建测试日志文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("""2026-02-01 10:00:00 INFO Application started
2026-02-01 10:00:01 INFO Database connected
2026-02-01 10:00:02 ERROR Failed to connect to API
2026-02-01 10:00:03 WARNING Deprecated function used
2026-02-01 10:00:04 INFO User logged in
2026-02-01 10:00:05 ERROR Database connection failed
2026-02-01 10:00:06 WARNING Timeout waiting for response
2026-02-01 10:00:07 INFO Processing request
2026-02-01 10:00:08 CRITICAL System crash detected
2026-02-01 10:00:09 ERROR Exception occurred
2026-02-01 10:00:10 INFO Application running
""")


def create_access_log(filepath: str):
    """创建测试访问日志"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("""192.168.1.100 - - [01/Feb/2026:10:00:00 +0000] "GET /api/users HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
192.168.1.101 - - [01/Feb/2026:10:00:01 +0000] "POST /api/login HTTP/1.1" 200 567 "-" "Mozilla/5.0"
192.168.1.102 - - [01/Feb/2026:10:00:02 +0000] "GET /api/products HTTP/1.1" 404 89 "-" "Mozilla/5.0"
192.168.1.100 - - [01/Feb/2026:10:00:03 +0000] "GET /api/users HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
192.168.1.103 - - [01/Feb/2026:10:00:04 +0000] "GET /api/orders HTTP/1.1" 500 234 "-" "Mozilla/5.0"
192.168.1.101 - - [01/Feb/2026:10:00:05 +0000] "POST /api/logout HTTP/1.1" 200 123 "-" "Mozilla/5.0"
192.168.1.104 - - [01/Feb/2026:10:00:06 +0000] "GET /api/dashboard HTTP/1.1" 403 456 "-" "Mozilla/5.0"
192.168.1.100 - - [01/Feb/2026:10:00:07 +0000] "GET /api/settings HTTP/1.1" 200 789 "-" "Mozilla/5.0"
""")


def test_1_initialization():
    """测试1: 初始化"""
    print("测试1: 初始化")

    analyzer = LogAnalyzer()

    assert analyzer.ERROR_KEYWORDS is not None
    assert len(analyzer.ERROR_KEYWORDS) > 0
    assert analyzer.WARNING_KEYWORDS is not None

    print("✅ 测试1通过: 初始化正常")
    return True


def test_2_analyze_log():
    """测试2: 分析日志"""
    print("\n测试2: 分析日志")

    analyzer = LogAnalyzer()
    log_file = tempfile.mktemp(suffix='.log')

    try:
        create_test_log(log_file)

        result = analyzer.analyze(log_file)

        assert result['total_lines'] == 11
        assert result['errors'] == 4  # ERROR + CRITICAL
        assert result['warnings'] == 2
        assert 'ERROR' in result['errors_by_type']
        assert result['time_range'] is not None

        print("✅ 测试2通过: 分析日志正常")
        return True
    finally:
        if os.path.exists(log_file):
            os.unlink(log_file)


def test_3_search_keywords():
    """测试3: 搜索关键词"""
    print("\n测试3: 搜索关键词")

    analyzer = LogAnalyzer()
    log_file = tempfile.mktemp(suffix='.log')

    try:
        create_test_log(log_file)

        matches = analyzer.search(log_file, ['ERROR', 'CRITICAL'])

        assert len(matches) == 4
        assert any(m['keyword'] == 'ERROR' for m in matches)
        assert any(m['keyword'] == 'CRITICAL' for m in matches)

        # 测试区分大小写
        matches_case = analyzer.search(log_file, ['error'], case_sensitive=True)
        assert len(matches_case) == 0

        print("✅ 测试3通过: 搜索关键词正常")
        return True
    finally:
        if os.path.exists(log_file):
            os.unlink(log_file)


def test_4_search_regex():
    """测试4: 正则表达式搜索"""
    print("\n测试4: 正则表达式搜索")

    analyzer = LogAnalyzer()
    log_file = tempfile.mktemp(suffix='.log')

    try:
        create_test_log(log_file)

        matches = analyzer.search_regex(log_file, r'ERROR.*API')

        assert len(matches) == 1
        assert 'API' in matches[0]['content']

        # 测试数字模式
        matches_time = analyzer.search_regex(log_file, r'\d{2}:\d{2}:\d{2}')
        assert len(matches_time) == 11

        print("✅ 测试4通过: 正则表达式搜索正常")
        return True
    finally:
        if os.path.exists(log_file):
            os.unlink(log_file)


def test_5_detect_errors():
    """测试5: 检测错误"""
    print("\n测试5: 检测错误")

    analyzer = LogAnalyzer()
    log_file = tempfile.mktemp(suffix='.log')

    try:
        create_test_log(log_file)

        errors = analyzer.detect_errors(log_file)

        assert len(errors) == 4
        assert errors[0]['type'] in ['ERROR', 'CRITICAL']

        print("✅ 测试5通过: 检测错误正常")
        return True
    finally:
        if os.path.exists(log_file):
            os.unlink(log_file)


def test_6_detect_patterns():
    """测试6: 检测模式"""
    print("\n测试6: 检测模式")

    analyzer = LogAnalyzer()
    log_file = tempfile.mktemp(suffix='.log')

    try:
        create_test_log(log_file)

        patterns = analyzer.detect_patterns(log_file)

        assert 'DATETIME' in patterns
        assert patterns['DATETIME'] == 11

        print("✅ 测试6通过: 检测模式正常")
        return True
    finally:
        if os.path.exists(log_file):
            os.unlink(log_file)


def test_7_analyze_performance():
    """测试7: 性能分析"""
    print("\n测试7: 性能分析")

    analyzer = LogAnalyzer()
    access_file = tempfile.mktemp(suffix='.log')

    try:
        create_access_log(access_file)

        performance = analyzer.analyze_performance(access_file, 'apache_combined')

        assert 'error' not in performance, f"性能分析错误: {performance.get('error')}"
        assert performance['total_requests'] == 8, f"总请求数错误: {performance['total_requests']}"
        assert '200' in performance['status_codes'], "缺少200状态码"
        assert performance['status_codes']['200'] == 5, f"200状态码数量错误: {performance['status_codes']['200']}"
        assert 'GET' in performance['methods'], "缺少GET方法"
        assert performance['methods']['GET'] == 6, f"GET方法数量错误: {performance['methods']['GET']}"
        assert performance['methods']['POST'] == 2, f"POST方法数量错误: {performance['methods']['POST']}"
        assert len(performance['top_paths']) > 0, "没有top_paths数据"

        print("✅ 测试7通过: 性能分析正常")
        return True
    finally:
        if os.path.exists(access_file):
            os.unlink(access_file)


def test_8_generate_report():
    """测试8: 生成报告"""
    print("\n测试8: 生成报告")

    analyzer = LogAnalyzer()
    log_file = tempfile.mktemp(suffix='.log')
    report_text = tempfile.mktemp(suffix='.txt')
    report_json = tempfile.mktemp(suffix='.json')
    report_csv = tempfile.mktemp(suffix='.csv')

    try:
        create_test_log(log_file)

        # 测试文本报告
        success_text = analyzer.generate_report(log_file, report_text, 'text')
        assert success_text == True
        assert os.path.exists(report_text)

        # 测试JSON报告
        success_json = analyzer.generate_report(log_file, report_json, 'json')
        assert success_json == True
        assert os.path.exists(report_json)

        # 验证JSON内容
        import json
        with open(report_json) as f:
            report_data = json.load(f)
        assert 'total_lines' in report_data

        # 测试CSV报告
        success_csv = analyzer.generate_report(log_file, report_csv, 'csv')
        assert success_csv == True
        assert os.path.exists(report_csv)

        print("✅ 测试8通过: 生成报告正常")
        return True
    finally:
        for path in [log_file, report_text, report_json, report_csv]:
            if os.path.exists(path):
                os.unlink(path)


def test_9_tail_head():
    """测试9: 读取首尾"""
    print("\n测试9: 读取首尾")

    analyzer = LogAnalyzer()
    log_file = tempfile.mktemp(suffix='.log')

    try:
        create_test_log(log_file)

        # 测试tail（最后2行）
        tail_lines = analyzer.tail(log_file, 2)
        assert len(tail_lines) == 2, f"tail行数错误: {len(tail_lines)}"
        tail_content = ''.join(tail_lines)
        assert 'CRITICAL' not in tail_content, f"CRITICAL不应该在最后2行中: {tail_content}"

        # 测试head
        head_lines = analyzer.head(log_file, 3)
        assert len(head_lines) == 3, f"head行数错误: {len(head_lines)}"
        head_content = ''.join(head_lines)
        assert 'Application started' in head_content, f"应该包含'Application started': {head_content}"

        print("✅ 测试9通过: 读取首尾正常")
        return True
    finally:
        if os.path.exists(log_file):
            os.unlink(log_file)


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("Log Analyzer 测试套件")
    print("=" * 60)

    tests = [
        test_1_initialization,
        test_2_analyze_log,
        test_3_search_keywords,
        test_4_search_regex,
        test_5_detect_errors,
        test_6_detect_patterns,
        test_7_analyze_performance,
        test_8_generate_report,
        test_9_tail_head
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"❌ 测试失败: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)

    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
