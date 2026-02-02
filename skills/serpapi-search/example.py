#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SerpAPI搜索示例代码
展示各种使用场景
"""

import sys
sys.path.insert(0, "/home/lejurobot/clawd/skills/serpapi-search")
from search import SerpAPISearch

def example_basic_search():
    """示例1：基本搜索"""
    print("=" * 60)
    print("示例1：基本搜索 - Python教程")
    print("=" * 60)
    search = SerpAPISearch()
    results = search.get_organic_results("Python入门教程", 3)
    print(search.format_results(results))
    print()

def example_multi_engine():
    """示例2：使用不同搜索引擎"""
    print("=" * 60)
    print("示例2：使用Bing搜索引擎")
    print("=" * 60)
    search = SerpAPISearch()
    # 使用bing引擎
    data = search.search("人工智能最新进展", engine="bing", num=2)
    if "organic_results" in data:
        for i, item in enumerate(data["organic_results"][:2], 1):
            print(f"{i}. {item['title']}")
            print(f"   {item['link']}\n")
    print()

def example_specific_num():
    """示例3：指定结果数量"""
    print("=" * 60)
    print("示例3：只获取前5个结果")
    print("=" * 60)
    search = SerpAPISearch()
    results = search.get_organic_results("免费AI工具", 5)
    print(f"获取到 {len(results)} 个结果：\n")
    print(search.format_results(results))
    print()

def example_get_links_only():
    """示例4：只提取链接"""
    print("=" * 60)
    print("示例4：只提取链接列表")
    print("=" * 60)
    search = SerpAPISearch()
    results = search.get_organic_results("GitHub项目", 3)
    print("相关链接：")
    for r in results:
        print(f"- {r['link']}")
    print()

def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("SerpAPI搜索功能示例")
    print("=" * 60 + "\n")

    example_basic_search()
    example_multi_engine()
    example_specific_num()
    example_get_links_only()

    print("=" * 60)
    print("示例运行完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
