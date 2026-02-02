#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SerpAPI搜索工具
支持多个搜索引擎，无需信用卡，每月100次免费查询
"""

import requests
import json
import sys
from typing import Dict, List, Optional

class SerpAPISearch:
    def __init__(self, api_key: str = "7f2e8da583426b56dda5d8ccec53ebf4e6d5f024fe7bcd2108b886fcf142b761"):
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search"

    def search(
        self,
        query: str,
        engine: str = "google",
        num: int = 10,
        country: str = "us",
        language: str = "en"
    ) -> Dict:
        """
        执行搜索

        Args:
            query: 搜索关键词
            engine: 搜索引擎 (google, bing, yahoo, duckduckgo)
            num: 返回结果数量 (1-100)
            country: 国家代码
            language: 语言代码

        Returns:
            搜索结果字典
        """
        params = {
            "engine": engine,
            "q": query,
            "api_key": self.api_key,
            "num": num,
            "gl": country,
            "hl": language
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def get_organic_results(self, query: str, num: int = 10) -> List[Dict]:
        """
        获取有机搜索结果（简化版）

        Args:
            query: 搜索关键词
            num: 返回结果数量

        Returns:
            结果列表，每个包含title, link, snippet
        """
        data = self.search(query, num=num)

        if "error" in data:
            return [{"error": data["error"]}]

        results = []
        organic = data.get("organic_results", [])

        for item in organic[:num]:
            results.append({
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "date": item.get("date", "")
            })

        return results

    def format_results(self, results: List[Dict]) -> str:
        """
        格式化搜索结果为易读文本

        Args:
            results: 搜索结果列表

        Returns:
            格式化的文本
        """
        if not results:
            return "未找到结果"

        if "error" in results[0]:
            return f"搜索错误：{results[0]['error']}"

        output = []
        for i, r in enumerate(results, 1):
            date_str = f" [{r['date']}]" if r.get('date') else ""
            output.append(f"{i}. {r['title']}{date_str}")
            output.append(f"   {r['link']}")
            output.append(f"   {r['snippet']}\n")

        return "\n".join(output)


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("使用方法: python search.py '搜索关键词' [结果数量]")
        print("示例: python search.py 'AI最新资讯' 5")
        sys.exit(1)

    query = sys.argv[1]
    num = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    search = SerpAPISearch()
    results = search.get_organic_results(query, num)
    print(search.format_results(results))


if __name__ == "__main__":
    main()
