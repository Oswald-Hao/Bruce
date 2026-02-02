#!/usr/bin/env python3
"""
Data Collector - 数据自动采集系统
智能爬虫，支持多页面采集、过滤、去重、多种输出格式
"""

import argparse
import json
import csv
import re
import sys
import time
from typing import List, Dict, Set
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("错误: 缺少必要的依赖库")
    print("请运行: pip install beautifulsoup4 requests lxml")
    print("或使用: data-collector --install")
    sys.exit(1)


class DataCollector:
    """数据采集器"""

    def __init__(self, delay: float = 1, timeout: int = 30, dedupe: bool = True, clean: bool = True):
        self.delay = delay
        self.timeout = timeout
        self.dedupe = dedupe
        self.clean = clean
        self.seen: Set[str] = set()  # 用于去重
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch_url(self, url: str) -> str:
        """获取网页内容"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            return response.text
        except requests.RequestException as e:
            print(f"警告: 无法获取 {url}: {e}")
            return ""

    def extract_data(self, html: str, selector: str, url: str, limit: int = 100) -> List[Dict]:
        """从HTML中提取数据"""
        if not html:
            return []

        soup = BeautifulSoup(html, 'lxml')
        elements = soup.select(selector)

        data = []
        for elem in elements[:limit]:
            text = elem.get_text(strip=True)

            if not text:
                continue

            # 数据清洗
            if self.clean:
                text = re.sub(r'\s+', ' ', text)
                text = text.strip()

            # 去重
            if self.dedupe and text in self.seen:
                continue
            if self.dedupe:
                self.seen.add(text)

            data.append({
                'text': text,
                'url': url
            })

        return data

    def filter_data(self, data: List[Dict], keyword: str) -> List[Dict]:
        """过滤数据"""
        if not keyword:
            return data

        keyword_lower = keyword.lower()
        filtered = []
        for item in data:
            if keyword_lower in item['text'].lower():
                filtered.append(item)

        return filtered

    def collect_from_urls(self, urls: List[str], selector: str, limit: int = 100) -> List[Dict]:
        """从多个URL采集数据"""
        all_data = []

        for i, url in enumerate(urls):
            print(f"采集 {i+1}/{len(urls)}: {url}")

            html = self.fetch_url(url)
            if html:
                data = self.extract_data(html, selector, url, limit)
                all_data.extend(data)
                print(f"  -> 提取 {len(data)} 条数据")

            # 延迟，避免请求过快
            if i < len(urls) - 1:
                time.sleep(self.delay)

        return all_data

    def save_as_json(self, data: List[Dict], output: str):
        """保存为JSON格式"""
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"已保存 {len(data)} 条数据到 {output}")

    def save_as_csv(self, data: List[Dict], output: str):
        """保存为CSV格式"""
        with open(output, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['text', 'url'])
            writer.writeheader()
            writer.writerows(data)
        print(f"已保存 {len(data)} 条数据到 {output}")

    def save_as_txt(self, data: List[Dict], output: str):
        """保存为TXT格式"""
        with open(output, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(f"{item['text']}\n")
                f.write(f"  来源: {item['url']}\n\n")
        print(f"已保存 {len(data)} 条数据到 {output}")

    def print_data(self, data: List[Dict], format: str = 'txt'):
        """打印数据到控制台"""
        if format == 'json':
            print(json.dumps(data, ensure_ascii=False, indent=2))
        elif format == 'csv':
            writer = csv.DictWriter(sys.stdout, fieldnames=['text', 'url'])
            writer.writeheader()
            writer.writerows(data)
        else:  # txt
            for item in data:
                print(f"{item['text']}")
                print(f"  来源: {item['url']}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Data Collector - 数据自动采集系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  采集单个页面:
    data-collector --url "https://example.com" --selector "div.product"

  采集多个页面:
    data-collector --urls urls.txt --selector "h2.title" --format json

  按关键词过滤:
    data-collector --url "https://example.com" --filter "AI" --format csv
        """
    )

    parser.add_argument('--url', help='单个URL')
    parser.add_argument('--urls', help='包含URL列表的文件')
    parser.add_argument('--selector', required=True, help='CSS选择器')
    parser.add_argument('--filter', help='关键词过滤')
    parser.add_argument('--format', choices=['json', 'csv', 'txt'], default='txt', help='输出格式')
    parser.add_argument('--output', help='输出文件路径')
    parser.add_argument('--limit', type=int, default=100, help='每页最多提取数量')
    parser.add_argument('--delay', type=float, default=1, help='请求间隔秒数')
    parser.add_argument('--timeout', type=int, default=30, help='请求超时秒数')
    parser.add_argument('--no-dedupe', action='store_true', help='禁用去重')
    parser.add_argument('--no-clean', action='store_true', help='禁用数据清洗')
    parser.add_argument('--install', action='store_true', help='安装依赖')

    args = parser.parse_args()

    # 安装依赖
    if args.install:
        import subprocess
        print("正在安装依赖...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'beautifulsoup4', 'requests', 'lxml'])
        print("安装完成！")
        return

    # 获取URL列表
    urls = []
    if args.url:
        urls.append(args.url)
    elif args.urls:
        try:
            with open(args.urls, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"错误: 找不到文件 {args.urls}")
            sys.exit(1)
    else:
        parser.error("必须指定 --url 或 --urls")

    # 创建采集器
    collector = DataCollector(
        delay=args.delay,
        timeout=args.timeout,
        dedupe=not args.no_dedupe,
        clean=not args.no_clean
    )

    # 采集数据
    print(f"\n开始采集 {len(urls)} 个URL...")
    data = collector.collect_from_urls(urls, args.selector, args.limit)

    # 过滤数据
    if args.filter:
        print(f"\n应用过滤: {args.filter}")
        before = len(data)
        data = collector.filter_data(data, args.filter)
        print(f"过滤后: {len(data)} 条数据（从 {before} 条中）")

    # 输出结果
    print(f"\n总共采集: {len(data)} 条数据")

    if args.output:
        if args.format == 'json':
            collector.save_as_json(data, args.output)
        elif args.format == 'csv':
            collector.save_as_csv(data, args.output)
        else:
            collector.save_as_txt(data, args.output)
    else:
        collector.print_data(data, args.format)


if __name__ == '__main__':
    main()
