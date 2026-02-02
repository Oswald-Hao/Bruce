#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Log Analyzer - 日志分析系统
支持日志解析、异常检测、性能分析、错误统计等功能
"""

import os
import re
import json
import csv
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict, Counter


class LogAnalyzer:
    """日志分析工具类"""

    # 常见错误关键词
    ERROR_KEYWORDS = [
        'error', 'exception', 'failed', 'failure', 'crash',
        'fatal', 'critical', 'alert', 'emergency'
    ]

    # 常见警告关键词
    WARNING_KEYWORDS = [
        'warning', 'warn', 'deprecated', 'timeout'
    ]

    def __init__(self):
        """初始化日志分析器"""
        self.patterns = {
            # 通用日志格式
            'generic': r'(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(?P<level>\w+)\s+(?P<message>.*)',

            # Apache Combined Log Format
            'apache_combined': r'(?P<ip>\S+)\s+\S+\s+(?P<user>\S+)\s+\[(?P<timestamp>[^\]]+)\]\s+"(?P<method>\w+)\s+(?P<path>\S+)\s+(?P<protocol>\S+)"\s+(?P<status>\d+)\s+(?P<size>\d+|-)\s+"(?P<referrer>[^"]*)"\s+"(?P<user_agent>[^"]*)"',

            # Nginx Combined Log Format
            'nginx_combined': r'(?P<ip>\S+)\s+-\s+(?P<user>\S+)\s+\[(?P<timestamp>[^\]]+)\]\s+"(?P<method>\w+)\s+(?P<path>\S+)\s+(?P<protocol>\S+)"\s+(?P<status>\d+)\s+(?P<size>\d+)\s+"(?P<referrer>[^"]*)"\s+"(?P<user_agent>[^"]*)"'
        }

    def _read_lines(self, filepath: str) -> List[str]:
        """
        读取日志文件行

        Args:
            filepath: 日志文件路径

        Returns:
            行列表
        """
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.readlines()
        except Exception as e:
            print(f"读取日志文件失败: {e}")
            return []

    def analyze(self, filepath: str) -> Dict[str, Any]:
        """
        分析日志文件

        Args:
            filepath: 日志文件路径

        Returns:
            分析结果字典
        """
        lines = self._read_lines(filepath)

        result = {
            'total_lines': len(lines),
            'errors': 0,
            'warnings': 0,
            'errors_by_type': Counter(),
            'warnings_by_type': Counter(),
            'time_range': None,
            'unique_ips': set(),
            'status_codes': Counter()
        }

        timestamps = []

        for line in lines:
            # 检测错误
            for keyword in self.ERROR_KEYWORDS:
                if keyword.lower() in line.lower():
                    result['errors'] += 1
                    result['errors_by_type'][keyword.upper()] += 1
                    break

            # 检测警告
            for keyword in self.WARNING_KEYWORDS:
                if keyword.lower() in line.lower():
                    result['warnings'] += 1
                    result['warnings_by_type'][keyword.upper()] += 1
                    break

            # 提取时间戳
            timestamp_match = re.search(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}', line)
            if timestamp_match:
                timestamps.append(timestamp_match.group())

            # 提取IP地址（针对访问日志）
            ip_match = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', line)
            if ip_match:
                result['unique_ips'].add(ip_match.group())

            # 提取HTTP状态码
            status_match = re.search(r'\s(\d{3})\s', line)
            if status_match:
                result['status_codes'][status_match.group(1)] += 1

        # 计算时间范围
        if timestamps:
            result['time_range'] = {
                'first': timestamps[0] if timestamps else None,
                'last': timestamps[-1] if timestamps else None
            }

        # 转换Counter为普通dict
        result['errors_by_type'] = dict(result['errors_by_type'])
        result['warnings_by_type'] = dict(result['warnings_by_type'])
        result['status_codes'] = dict(result['status_codes'])
        result['unique_ips_count'] = len(result['unique_ips'])
        result['unique_ips'] = list(result['unique_ips'])  # 转换set为list

        return result

    def search(self, filepath: str, keywords: List[str], case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """
        搜索日志中的关键词

        Args:
            filepath: 日志文件路径
            keywords: 关键词列表
            case_sensitive: 是否区分大小写

        Returns:
            匹配行列表
        """
        lines = self._read_lines(filepath)
        matches = []

        for i, line in enumerate(lines, 1):
            for keyword in keywords:
                search_line = line if case_sensitive else line.lower()
                search_keyword = keyword if case_sensitive else keyword.lower()

                if search_keyword in search_line:
                    matches.append({
                        'line_number': i,
                        'keyword': keyword,
                        'content': line.strip()
                    })
                    break  # 只记录第一个匹配的关键词

        return matches

    def search_regex(self, filepath: str, pattern: str) -> List[Dict[str, Any]]:
        """
        使用正则表达式搜索日志

        Args:
            filepath: 日志文件路径
            pattern: 正则表达式

        Returns:
            匹配行列表
        """
        lines = self._read_lines(filepath)
        matches = []

        try:
            regex = re.compile(pattern)
        except Exception as e:
            print(f"正则表达式错误: {e}")
            return []

        for i, line in enumerate(lines, 1):
            match = regex.search(line)
            if match:
                matches.append({
                    'line_number': i,
                    'pattern': pattern,
                    'match': match.group(),
                    'content': line.strip()
                })

        return matches

    def detect_errors(self, filepath: str) -> List[Dict[str, Any]]:
        """
        检测日志中的错误

        Args:
            filepath: 日志文件路径

        Returns:
            错误列表
        """
        lines = self._read_lines(filepath)
        errors = []

        for i, line in enumerate(lines, 1):
            line_lower = line.lower()
            for keyword in self.ERROR_KEYWORDS:
                if keyword in line_lower:
                    errors.append({
                        'line_number': i,
                        'type': keyword.upper(),
                        'content': line.strip()
                    })
                    break

        return errors

    def detect_patterns(self, filepath: str) -> Dict[str, int]:
        """
        检测日志中的常见模式

        Args:
            filepath: 日志文件路径

        Returns:
            模式计数字典
        """
        lines = self._read_lines(filepath)

        patterns = Counter()

        for line in lines:
            # 检测IP地址
            if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', line):
                patterns['IP_ADDRESS'] += 1

            # 检测URL
            if re.search(r'https?://\S+', line):
                patterns['URL'] += 1

            # 检测邮箱
            if re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', line):
                patterns['EMAIL'] += 1

            # 检测日期时间
            if re.search(r'\d{4}-\d{2}-\d{2}', line):
                patterns['DATETIME'] += 1

            # 检测HTTP方法
            if re.search(r'\b(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\b', line):
                patterns['HTTP_METHOD'] += 1

            # 检测HTTP状态码
            if re.search(r'\s[45]\d{2}\s', line):
                patterns['HTTP_ERROR'] += 1

        return dict(patterns)

    def analyze_performance(self, filepath: str, log_format: str = 'apache_combined') -> Dict[str, Any]:
        """
        分析访问日志性能

        Args:
            filepath: 日志文件路径
            log_format: 日志格式（apache_combined/nginx_combined）

        Returns:
            性能分析结果
        """
        lines = self._read_lines(filepath)
        pattern = self.patterns.get(log_format)

        if not pattern:
            return {'error': f'不支持的日志格式: {log_format}'}

        result = {
            'total_requests': 0,
            'status_codes': Counter(),
            'methods': Counter(),
            'top_paths': Counter(),
            'top_ips': Counter(),
            'response_time_distribution': Counter(),
            'time_range': None
        }

        timestamps = []

        for line in lines:
            match = re.search(pattern, line)
            if match:
                result['total_requests'] += 1

                # 状态码
                status = match.group('status')
                result['status_codes'][status] += 1

                # HTTP方法
                if 'method' in match.groupdict():
                    method = match.group('method')
                    result['methods'][method] += 1

                # 路径
                if 'path' in match.groupdict():
                    path = match.group('path')
                    result['top_paths'][path] += 1

                # IP地址
                if 'ip' in match.groupdict():
                    ip = match.group('ip')
                    result['top_ips'][ip] += 1

                # 时间戳
                if 'timestamp' in match.groupdict():
                    timestamp = match.group('timestamp')
                    timestamps.append(timestamp)

        # 计算时间范围
        if timestamps:
            result['time_range'] = {
                'first': timestamps[0] if timestamps else None,
                'last': timestamps[-1] if timestamps else None
            }

        # 转换Counter为dict
        result['status_codes'] = dict(result['status_codes'])
        result['methods'] = dict(result['methods'])
        result['top_paths'] = dict(result['top_paths'].most_common(10))
        result['top_ips'] = dict(result['top_ips'].most_common(10))

        return result

    def generate_report(
        self,
        filepath: str,
        output_path: str,
        format: str = 'text'
    ) -> bool:
        """
        生成分析报告

        Args:
            filepath: 日志文件路径
            output_path: 输出文件路径
            format: 报告格式（text/json/csv）

        Returns:
            是否成功
        """
        analysis = self.analyze(filepath)

        try:
            if format == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(analysis, f, indent=2, ensure_ascii=False)

            elif format == 'csv':
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['指标', '值'])

                    for key, value in analysis.items():
                        if isinstance(value, (int, float, str)):
                            writer.writerow([key, value])

            else:  # text格式
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write("=" * 60 + "\n")
                    f.write("日志分析报告\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(f"文件: {filepath}\n")
                    f.write(f"总行数: {analysis['total_lines']}\n")
                    f.write(f"错误数: {analysis['errors']}\n")
                    f.write(f"警告数: {analysis['warnings']}\n")
                    f.write(f"唯一IP数: {analysis['unique_ips_count']}\n")

                    if analysis['time_range']:
                        f.write(f"\n时间范围:\n")
                        f.write(f"  开始: {analysis['time_range']['first']}\n")
                        f.write(f"  结束: {analysis['time_range']['last']}\n")

                    if analysis['errors_by_type']:
                        f.write(f"\n错误类型:\n")
                        for error_type, count in analysis['errors_by_type'].items():
                            f.write(f"  {error_type}: {count}\n")

                    if analysis['status_codes']:
                        f.write(f"\n状态码统计:\n")
                        for status, count in sorted(analysis['status_codes'].items()):
                            f.write(f"  {status}: {count}\n")

            return True

        except Exception as e:
            print(f"生成报告失败: {e}")
            return False

    def tail(self, filepath: str, lines: int = 100) -> List[str]:
        """
        读取日志最后几行

        Args:
            filepath: 日志文件路径
            lines: 行数

        Returns:
            最后几行列表
        """
        all_lines = self._read_lines(filepath)
        return all_lines[-lines:]

    def head(self, filepath: str, lines: int = 100) -> List[str]:
        """
        读取日志前几行

        Args:
            filepath: 日志文件路径
            lines: 行数

        Returns:
            前几行列表
        """
        all_lines = self._read_lines(filepath)
        return all_lines[:lines]


def main():
    """命令行示例"""
    import argparse

    parser = argparse.ArgumentParser(description='日志分析工具')
    parser.add_argument('--action', choices=['analyze', 'search', 'report', 'tail'], required=True, help='操作类型')
    parser.add_argument('--file', help='日志文件路径')
    parser.add_argument('--output', help='输出文件路径')
    parser.add_argument('--keywords', help='搜索关键词（逗号分隔）')
    parser.add_argument('--lines', type=int, default=100, help='行数')
    args = parser.parse_args()

    analyzer = LogAnalyzer()

    if args.action == 'analyze' and args.file:
        result = analyzer.analyze(args.file)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.action == 'search' and args.file and args.keywords:
        keywords = [k.strip() for k in args.keywords.split(',')]
        matches = analyzer.search(args.file, keywords)
        for match in matches:
            print(f"Line {match['line_number']}: {match['content']}")

    elif args.action == 'report' and args.file and args.output:
        success = analyzer.generate_report(args.file, args.output)
        print(f"生成报告{'成功' if success else '失败'}")

    elif args.action == 'tail' and args.file:
        lines = analyzer.tail(args.file, args.lines)
        for line in lines:
            print(line, end='')


if __name__ == '__main__':
    main()
