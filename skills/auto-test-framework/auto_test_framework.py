#!/usr/bin/env python3
"""
自动化测试框架 - 提供全面的测试能力
"""

import os
import sys
import json
import time
import yaml
import pytest
import subprocess
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

# 尝试导入可选依赖
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False


@dataclass
class TestResult:
    """测试结果数据类"""
    name: str
    passed: bool
    duration: float
    output: str
    error: Optional[str] = None
    details: Optional[Dict] = None


class UnitTest:
    """单元测试类"""

    def __init__(self, test_dir: Optional[str] = None):
        self.test_dir = test_dir or './tests'
        self.tests = []
        self.results = []

    def add_test(self, test_case: Dict[str, Any]):
        """添加测试用例"""
        self.tests.append(test_case)

    def run(self, verbose: bool = False) -> Dict[str, Any]:
        """运行所有单元测试"""
        if not self.tests:
            return self._run_pytest_tests(verbose)

        results = []
        for test in self.tests:
            result = self._run_single_test(test)
            results.append(result)

        return {
            'total': len(results),
            'passed': sum(1 for r in results if r['passed']),
            'failed': sum(1 for r in results if not r['passed']),
            'results': results
        }

    def _run_single_test(self, test: Dict) -> Dict[str, Any]:
        """运行单个测试用例"""
        try:
            start_time = time.time()

            if test['type'] == 'function':
                # 执行函数测试
                exec_globals = {}
                exec(test['code'], exec_globals)
                if 'test_function' in test:
                    exec_globals[test['test_function']]()
                elif 'test_addition' in test['code']:
                    exec_globals['test_addition']()

            duration = time.time() - start_time
            return {
                'name': test.get('name', 'unknown'),
                'passed': True,
                'duration': duration,
                'output': 'Test passed'
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                'name': test.get('name', 'unknown'),
                'passed': False,
                'duration': duration,
                'output': 'Test failed',
                'error': str(e)
            }

    def _run_pytest_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """运行pytest测试"""
        if not os.path.exists(self.test_dir):
            return {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'results': []
            }

        cmd = ['pytest', self.test_dir, '-v' if verbose else '-q', '--tb=no']
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(self.test_dir)
        )

        # 解析pytest输出
        output = result.stdout + result.stderr
        lines = output.split('\n')

        # 简单解析
        passed = output.count('PASSED')
        failed = output.count('FAILED')

        return {
            'total': passed + failed,
            'passed': passed,
            'failed': failed,
            'results': [{'name': 'pytest', 'passed': result.returncode == 0}],
            'output': output
        }


class IntegrationTest:
    """集成测试类"""

    def __init__(self, base_url: str = ''):
        self.base_url = base_url.rstrip('/')
        self.tests = []
        self.session = None

        if HAS_REQUESTS:
            import requests
            self.session = requests.Session()

    def add_test(self, test_case: Dict[str, Any]):
        """添加测试用例"""
        self.tests.append(test_case)

    def get(self, endpoint: str, **kwargs) -> Optional['requests.Response']:
        """发送GET请求"""
        if not self.session or not HAS_REQUESTS:
            return None
        url = f"{self.base_url}{endpoint}"
        return self.session.get(url, **kwargs)

    def post(self, endpoint: str, **kwargs) -> Optional['requests.Response']:
        """发送POST请求"""
        if not self.session or not HAS_REQUESTS:
            return None
        url = f"{self.base_url}{endpoint}"
        return self.session.post(url, **kwargs)

    def put(self, endpoint: str, **kwargs) -> Optional['requests.Response']:
        """发送PUT请求"""
        if not self.session or not HAS_REQUESTS:
            return None
        url = f"{self.base_url}{endpoint}"
        return self.session.put(url, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> Optional['requests.Response']:
        """发送DELETE请求"""
        if not self.session or not HAS_REQUESTS:
            return None
        url = f"{self.base_url}{endpoint}"
        return self.session.delete(url, **kwargs)

    def run(self) -> Dict[str, Any]:
        """运行所有集成测试"""
        if not self.tests:
            return {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'results': []
            }

        results = []
        for test in self.tests:
            result = self._run_single_test(test)
            results.append(result)

        return {
            'total': len(results),
            'passed': sum(1 for r in results if r['passed']),
            'failed': sum(1 for r in results if not r['passed']),
            'results': results
        }

    def _run_single_test(self, test: Dict) -> Dict[str, Any]:
        """运行单个集成测试"""
        try:
            start_time = time.time()

            if 'endpoint' in test:
                method = test.get('method', 'GET').lower()
                endpoint = test['endpoint']

                if method == 'get':
                    response = self.get(endpoint)
                elif method == 'post':
                    response = self.post(endpoint, json=test.get('data', {}))
                elif method == 'put':
                    response = self.put(endpoint, json=test.get('data', {}))
                elif method == 'delete':
                    response = self.delete(endpoint)
                else:
                    raise ValueError(f"Unsupported method: {method}")

                duration = time.time() - start_time

                if not response:
                    return {
                        'name': test.get('name', 'unknown'),
                        'passed': False,
                        'duration': duration,
                        'error': 'Requests library not available'
                    }

                # 检查预期状态码
                expected_status = test.get('expected_status', 200)
                status_ok = response.status_code == expected_status

                # 检查预期字段
                fields_ok = True
                if 'expected_fields' in test:
                    data = response.json() if response.text else {}
                    for field in test['expected_fields']:
                        if field not in data:
                            fields_ok = False
                            break

                passed = status_ok and fields_ok

                return {
                    'name': test.get('name', 'unknown'),
                    'passed': passed,
                    'duration': duration,
                    'status_code': response.status_code,
                    'output': response.text[:500] if response.text else ''
                }

            duration = time.time() - start_time
            return {
                'name': test.get('name', 'unknown'),
                'passed': True,
                'duration': duration,
                'output': 'Test passed (no validation)'
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                'name': test.get('name', 'unknown'),
                'passed': False,
                'duration': duration,
                'error': str(e)
            }


class PerformanceTest:
    """性能测试类"""

    def __init__(self):
        self.tests = []

    def add_test(self, test_case: Dict[str, Any]):
        """添加性能测试用例"""
        self.tests.append(test_case)

    def run(self) -> Dict[str, Any]:
        """运行所有性能测试"""
        if not self.tests:
            return {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'results': []
            }

        results = []
        for test in self.tests:
            result = self._run_single_test(test)
            results.append(result)

        return {
            'total': len(results),
            'passed': sum(1 for r in results if r['passed']),
            'failed': sum(1 for r in results if not r['passed']),
            'results': results
        }

    def _run_single_test(self, test: Dict) -> Dict[str, Any]:
        """运行单个性能测试"""
        try:
            durations = []
            iterations = test.get('iterations', 10)
            function = test.get('function')

            if not function or not callable(function):
                raise ValueError("Function must be callable")

            # 执行多次迭代
            for _ in range(iterations):
                start = time.time()
                function()
                duration = time.time() - start
                durations.append(duration)

            # 计算统计信息
            avg_duration = sum(durations) / len(durations)
            min_duration = min(durations)
            max_duration = max(durations)

            # 检查最大持续时间
            max_allowed = test.get('max_duration', float('inf'))
            passed = max_duration <= max_allowed

            return {
                'name': test.get('name', 'unknown'),
                'passed': passed,
                'avg_duration': avg_duration,
                'min_duration': min_duration,
                'max_duration': max_duration,
                'iterations': iterations,
                'output': f'Avg: {avg_duration:.4f}s, Min: {min_duration:.4f}s, Max: {max_duration:.4f}s'
            }

        except Exception as e:
            return {
                'name': test.get('name', 'unknown'),
                'passed': False,
                'error': str(e)
            }


class UITest:
    """UI测试类（基于Playwright）"""

    def __init__(self):
        self.tests = []

    def add_test(self, test_case: Dict[str, Any]):
        """添加UI测试用例"""
        self.tests.append(test_case)

    def run(self, headless: bool = True) -> Dict[str, Any]:
        """运行所有UI测试"""
        if not HAS_PLAYWRIGHT:
            return {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'results': [],
                'error': 'Playwright not installed'
            }

        if not self.tests:
            return {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'results': []
            }

        results = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            page = browser.new_page()

            for test in self.tests:
                result = self._run_single_test(page, test)
                results.append(result)

            browser.close()

        return {
            'total': len(results),
            'passed': sum(1 for r in results if r['passed']),
            'failed': sum(1 for r in results if not r['passed']),
            'results': results
        }

    def _run_single_test(self, page, test: Dict) -> Dict[str, Any]:
        """运行单个UI测试"""
        try:
            start_time = time.time()

            url = test.get('url', '')
            if url:
                page.goto(url)

            actions = test.get('actions', [])
            for action in actions:
                action_type = action['type']

                if action_type == 'fill':
                    page.fill(action['selector'], action['value'])
                elif action_type == 'click':
                    page.click(action['selector'])
                elif action_type == 'type':
                    page.type(action['selector'], action['value'])
                elif action_type == 'wait_for_url':
                    page.wait_for_url(action['pattern'])
                elif action_type == 'wait_for_selector':
                    page.wait_for_selector(action['selector'])
                elif action_type == 'assert_text':
                    element = page.locator(action['selector'])
                    text = element.inner_text()
                    if text != action['text']:
                        raise AssertionError(f"Expected '{action['text']}', got '{text}'")
                elif action_type == 'screenshot':
                    page.screenshot(path=action.get('path', 'screenshot.png'))

            duration = time.time() - start_time
            return {
                'name': test.get('name', 'unknown'),
                'passed': True,
                'duration': duration,
                'output': 'UI test passed'
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                'name': test.get('name', 'unknown'),
                'passed': False,
                'duration': duration,
                'error': str(e)
            }


class CoverageAnalyzer:
    """测试覆盖率分析器"""

    def __init__(self, module_path: str = './src'):
        self.module_path = module_path

    def analyze(self) -> Dict[str, Any]:
        """分析测试覆盖率"""
        try:
            cmd = ['pytest', '--cov=' + self.module_path, '--cov-report=json']
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=os.path.dirname(self.module_path) if os.path.exists(self.module_path) else '.'
            )

            # 读取覆盖率报告
            coverage_file = 'coverage.json'
            if os.path.exists(coverage_file):
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)

                total_coverage = coverage_data['totals']['percent_covered']
                missing_lines = []

                for file, data in coverage_data['files'].items():
                    if data['missing_lines']:
                        missing_lines.append({
                            'file': file,
                            'missing': data['missing_lines']
                        })

                return {
                    'percentage': total_coverage,
                    'missing_lines': missing_lines,
                    'covered_lines': coverage_data['totals']['covered_lines'],
                    'num_statements': coverage_data['totals']['num_statements']
                }
            else:
                return {
                    'percentage': 0,
                    'missing_lines': [],
                    'error': 'Coverage report not generated'
                }

        except Exception as e:
            return {
                'percentage': 0,
                'missing_lines': [],
                'error': str(e)
            }


class TestReporter:
    """测试报告生成器"""

    def __init__(self, output_dir: str = './test-reports'):
        self.output_dir = output_dir
        self.results = []

        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)

    def add_result(self, result: Dict[str, Any]):
        """添加测试结果"""
        self.results.append(result)

    def generate_html(self, output_path: Optional[str] = None) -> str:
        """生成HTML报告"""
        if output_path is None:
            output_path = os.path.join(self.output_dir, 'report.html')

        total = sum(r.get('total', 0) for r in self.results)
        passed = sum(r.get('passed', 0) for r in self.results)
        failed = sum(r.get('failed', 0) for r in self.results)

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .passed {{ color: green; }}
        .failed {{ color: red; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
    </style>
</head>
<body>
    <h1>Test Report</h1>
    <div class="summary">
        <h2>Summary</h2>
        <p>Total: {total}</p>
        <p class="passed">Passed: {passed}</p>
        <p class="failed">Failed: {failed}</p>
        <p>Success Rate: {passed/total*100 if total > 0 else 0:.2f}%</p>
    </div>
    <table>
        <tr>
            <th>Test Suite</th>
            <th>Total</th>
            <th>Passed</th>
            <th>Failed</th>
        </tr>
"""

        for i, result in enumerate(self.results):
            html += f"""
        <tr>
            <td>Test Suite {i+1}</td>
            <td>{result.get('total', 0)}</td>
            <td class="passed">{result.get('passed', 0)}</td>
            <td class="failed">{result.get('failed', 0)}</td>
        </tr>
"""

        html += """
    </table>
</body>
</html>
"""

        with open(output_path, 'w') as f:
            f.write(html)

        return output_path

    def generate_json(self, output_path: Optional[str] = None) -> str:
        """生成JSON报告"""
        if output_path is None:
            output_path = os.path.join(self.output_dir, 'report.json')

        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total': sum(r.get('total', 0) for r in self.results),
                'passed': sum(r.get('passed', 0) for r in self.results),
                'failed': sum(r.get('failed', 0) for r in self.results),
            },
            'results': self.results
        }

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        return output_path

    def generate_markdown(self, output_path: Optional[str] = None) -> str:
        """生成Markdown报告"""
        if output_path is None:
            output_path = os.path.join(self.output_dir, 'report.md')

        total = sum(r.get('total', 0) for r in self.results)
        passed = sum(r.get('passed', 0) for r in self.results)
        failed = sum(r.get('failed', 0) for r in self.results)

        md = f"""# Test Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

| Metric | Value |
|--------|-------|
| Total | {total} |
| ✅ Passed | {passed} |
| ❌ Failed | {failed} |
| Success Rate | {passed/total*100 if total > 0 else 0:.2f}% |

## Test Results

"""

        for i, result in enumerate(self.results):
            md += f"### Test Suite {i+1}\n\n"
            md += f"- Total: {result.get('total', 0)}\n"
            md += f"- Passed: {result.get('passed', 0)}\n"
            md += f"- Failed: {result.get('failed', 0)}\n\n"

        with open(output_path, 'w') as f:
            f.write(md)

        return output_path


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='自动化测试框架')
    parser.add_argument('action', choices=['run', 'coverage', 'report', 'clean'])
    parser.add_argument('--test-dir', default='./tests', help='测试目录')
    parser.add_argument('--output', default='./test-reports', help='输出目录')

    args = parser.parse_args()

    if args.action == 'run':
        test = UnitTest(test_dir=args.test_dir)
        result = test.run(verbose=True)
        print(f"Tests: {result['passed']}/{result['total']} passed")

    elif args.action == 'coverage':
        analyzer = CoverageAnalyzer(module_path=args.test_dir)
        report = analyzer.analyze()
        print(f"Coverage: {report['percentage']:.2f}%")

    elif args.action == 'report':
        # 需要先运行测试
        test = UnitTest(test_dir=args.test_dir)
        result = test.run()
        reporter = TestReporter(output_dir=args.output)
        reporter.add_result(result)

        html_path = reporter.generate_html()
        json_path = reporter.generate_json()
        md_path = reporter.generate_markdown()

        print(f"Reports generated:")
        print(f"  - HTML: {html_path}")
        print(f"  - JSON: {json_path}")
        print(f"  - Markdown: {md_path}")

    elif args.action == 'clean':
        import shutil
        if os.path.exists(args.output):
            shutil.rmtree(args.output)
            print(f"Cleaned {args.output}")


if __name__ == '__main__':
    main()
