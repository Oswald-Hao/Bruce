#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SerpAPI搜索技能测试
"""

import sys
sys.path.insert(0, "/home/lejurobot/clawd/skills/serpapi-search")
from search import SerpAPISearch

def test_search():
    """测试搜索功能"""
    print("测试1：基本搜索")
    search = SerpAPISearch()
    results = search.get_organic_results("Python编程", 3)
    assert len(results) <= 3, "结果数量超过限制"
    assert len(results) > 0, "没有返回结果"
    for r in results:
        assert "title" in r, "缺少title字段"
        assert "link" in r, "缺少link字段"
    print("✓ 基本搜索通过\n")

def test_format():
    """测试格式化输出"""
    print("测试2：结果格式化")
    search = SerpAPISearch()
    results = search.get_organic_results("AI工具", 2)
    formatted = search.format_results(results)
    assert "AI工具" in formatted or "AI" in formatted, "结果内容不正确"
    print("✓ 格式化通过\n")
    print(formatted)

def test_error_handling():
    """测试错误处理"""
    print("测试3：错误处理")
    search = SerpAPISearch("invalid_key")
    results = search.get_organic_results("test", 5)
    assert "error" in results[0], "错误处理失败"
    print("✓ 错误处理通过\n")

def test_empty_query():
    """测试空查询"""
    print("测试4：空查询处理")
    search = SerpAPISearch()
    # 这个测试可能因为API的不同表现而不同，主要验证不会崩溃
    results = search.search("", num=1)
    print("✓ 空查询处理完成\n")

def main():
    """运行所有测试"""
    print("=" * 50)
    print("SerpAPI搜索技能测试")
    print("=" * 50 + "\n")

    try:
        test_search()
        test_format()
        test_error_handling()
        test_empty_query()

        print("=" * 50)
        print("所有测试通过！✓")
        print("=" * 50)
        return True
    except AssertionError as e:
        print(f"✗ 测试失败：{e}")
        return False
    except Exception as e:
        print(f"✗ 测试出错：{e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
