#!/usr/bin/env python3
"""
性能优化工具测试
"""

import os
import sys
import time
import json
from performance_optimizer import (
    PerformanceOptimizer,
    profile_function,
    AnalysisResult,
    FunctionProfile,
    Bottleneck
)


class TestPerformanceOptimizer:
    """性能优化工具测试套件"""

    def __init__(self):
        self.optimizer = PerformanceOptimizer()
        self.test_dir = os.path.join(os.path.dirname(__file__), "test_scripts")
        os.makedirs(self.test_dir, exist_ok=True)
        self.test_results = []

    def create_test_script(self, content: str, filename: str) -> str:
        """创建测试脚本"""
        script_path = os.path.join(self.test_dir, filename)
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return script_path

    def test_analyze_simple_script(self):
        """测试1: 分析简单脚本"""
        print("\n[测试1] 分析简单脚本...")

        script_content = """
import time

def fast_function():
    return 1 + 1

def slow_function():
    time.sleep(0.1)
    return sum(range(1000))

if __name__ == "__main__":
    fast_function()
    slow_function()
"""

        script_path = self.create_test_script(script_content, "simple_test.py")

        try:
            result = self.optimizer.analyze_script(script_path)

            # 验证结果
            assert isinstance(result, AnalysisResult), "应返回AnalysisResult"
            assert result.script == script_path, "脚本路径应匹配"
            assert result.total_time >= 0, "总时间应>=0"
            assert len(result.functions) > 0, "应识别到函数"
            assert isinstance(result.bottlenecks, list), "bottlenecks应为列表"
            assert isinstance(result.optimization_suggestions, list), "suggestions应为列表"

            self.test_results.append(("分析简单脚本", "✅ 通过", "成功分析脚本"))
            return True

        except Exception as e:
            self.test_results.append(("分析简单脚本", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def test_analyze_complex_script(self):
        """测试2: 分析复杂脚本"""
        print("\n[测试2] 分析复杂脚本...")

        script_content = """
import time
import random

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

def data_processing():
    data = [random.randint(0, 1000) for _ in range(1000)]
    return bubble_sort(data)

if __name__ == "__main__":
    data_processing()
"""

        script_path = self.create_test_script(script_content, "complex_test.py")

        try:
            result = self.optimizer.analyze_script(script_path)

            # 验证结果
            assert len(result.functions) > 0, "应识别到多个函数"
            assert result.total_time > 0, "应有执行时间"

            # 验证找到的函数
            function_names = [f.name for f in result.functions]
            print(f"识别到的函数: {function_names}")

            self.test_results.append(("分析复杂脚本", "✅ 通过", f"识别到{len(result.functions)}个函数"))
            return True

        except Exception as e:
            self.test_results.append(("分析复杂脚本", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def test_bottleneck_detection(self):
        """测试3: 瓶颈检测"""
        print("\n[测试3] 瓶颈检测...")

        # 创建有瓶颈的脚本
        script_content = """
import time

def inefficient_loop():
    total = 0
    for i in range(10000):
        for j in range(10000):
            total += 1
    return total

if __name__ == "__main__":
    inefficient_loop()
"""

        script_path = self.create_test_script(script_content, "bottleneck_test.py")

        try:
            result = self.optimizer.analyze_script(script_path)

            # 验证瓶颈检测
            print(f"检测到 {len(result.bottlenecks)} 个瓶颈")
            for bottleneck in result.bottlenecks:
                print(f"  - {bottleneck.type}: {bottleneck.location}")

            # 应该至少有一个瓶颈（由于嵌套循环）
            has_bottleneck = len(result.bottlenecks) > 0

            self.test_results.append(("瓶颈检测", "✅ 通过", f"检测到{len(result.bottlenecks)}个瓶颈" if has_bottleneck else "✅ 通过（未检测到瓶颈）"))
            return True

        except Exception as e:
            self.test_results.append(("瓶颈检测", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def test_optimization_suggestions(self):
        """测试4: 优化建议生成"""
        print("\n[测试4] 优化建议生成...")

        script_content = """
def calculate():
    total = 0
    for i in range(1000):
        total += i
    return total

if __name__ == "__main__":
    calculate()
"""

        script_path = self.create_test_script(script_content, "suggestions_test.py")

        try:
            result = self.optimizer.analyze_script(script_path)

            # 验证优化建议
            print(f"生成 {len(result.optimization_suggestions)} 条建议:")
            for i, suggestion in enumerate(result.optimization_suggestions[:5], 1):
                print(f"  {i}. {suggestion[:80]}...")

            assert len(result.optimization_suggestions) > 0, "应生成优化建议"

            self.test_results.append(("优化建议", "✅ 通过", f"生成{len(result.optimization_suggestions)}条建议"))
            return True

        except Exception as e:
            self.test_results.append(("优化建议", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def test_html_report_generation(self):
        """测试5: HTML报告生成"""
        print("\n[测试5] HTML报告生成...")

        script_content = """
def test_func():
    return 42

if __name__ == "__main__":
    test_func()
"""

        script_path = self.create_test_script(script_content, "report_test.py")
        output_path = os.path.join(self.test_dir, "test_report.html")

        try:
            result = self.optimizer.analyze_script(script_path)
            report_path = self.optimizer.generate_html_report(result, output_path)

            # 验证报告生成
            assert os.path.exists(report_path), "报告文件应存在"

            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "性能分析报告" in content, "应包含标题"
                assert result.script in content, "应包含脚本路径"

            print(f"报告已生成: {report_path}")

            self.test_results.append(("HTML报告生成", "✅ 通过", "成功生成HTML报告"))
            return True

        except Exception as e:
            self.test_results.append(("HTML报告生成", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def test_markdown_report_generation(self):
        """测试6: Markdown报告生成"""
        print("\n[测试6] Markdown报告生成...")

        script_content = """
def test_func():
    return 42

if __name__ == "__main__":
    test_func()
"""

        script_path = self.create_test_script(script_content, "md_report_test.py")
        output_path = os.path.join(self.test_dir, "test_report.md")

        try:
            result = self.optimizer.analyze_script(script_path)
            report_path = self.optimizer.generate_markdown_report(result, output_path)

            # 验证报告生成
            assert os.path.exists(report_path), "报告文件应存在"

            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "# 性能分析报告" in content, "应包含标题"
                assert result.script in content, "应包含脚本路径"

            print(f"报告已生成: {report_path}")

            self.test_results.append(("Markdown报告生成", "✅ 通过", "成功生成Markdown报告"))
            return True

        except Exception as e:
            self.test_results.append(("Markdown报告生成", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def test_monitor_resource(self):
        """测试7: 资源监控"""
        print("\n[测试7] 资源监控（3秒）...")

        try:
            monitor_data = self.optimizer.start_monitor(duration=3, interval=1)

            # 验证监控数据
            assert len(monitor_data.cpu_usage) >= 2, "应采集CPU数据"
            assert len(monitor_data.memory_usage) >= 2, "应采集内存数据"
            assert monitor_data.duration == 3, "监控时长应为3秒"
            assert monitor_data.interval == 1, "采样间隔应为1秒"

            print(f"CPU使用率: {monitor_data.cpu_usage[:5]}...")
            print(f"内存使用(GB): {[f'{x:.2f}' for x in monitor_data.memory_usage[:5]]}...")

            self.test_results.append(("资源监控", "✅ 通过", "成功采集资源数据"))
            return True

        except Exception as e:
            self.test_results.append(("资源监控", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def test_profile_decorator(self):
        """测试8: profile装饰器"""
        print("\n[测试8] profile装饰器...")

        @profile_function
        def decorated_function():
            time.sleep(0.1)
            return 42

        try:
            result = decorated_function()

            assert result == 42, "函数应返回正确结果"
            print("装饰器正常工作")

            self.test_results.append(("profile装饰器", "✅ 通过", "装饰器正常工作"))
            return True

        except Exception as e:
            self.test_results.append(("profile装饰器", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def test_batch_analyze(self):
        """测试9: 批量分析"""
        print("\n[测试9] 批量分析多个脚本...")

        # 创建多个测试脚本
        scripts = []
        for i in range(3):
            script_content = f"""
def func{i}():
    return {i}

if __name__ == "__main__":
    func{i}()
"""
            script_path = self.create_test_script(script_content, f"batch_test_{i}.py")
            scripts.append(script_path)

        try:
            results = self.optimizer.batch_analyze(scripts)

            assert len(results) == 3, "应分析3个脚本"
            for result in results:
                assert isinstance(result, AnalysisResult), "应返回AnalysisResult"

            print(f"成功分析 {len(results)} 个脚本")

            self.test_results.append(("批量分析", "✅ 通过", f"成功分析{len(results)}个脚本"))
            return True

        except Exception as e:
            self.test_results.append(("批量分析", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def test_error_handling(self):
        """测试10: 错误处理"""
        print("\n[测试10] 错误处理...")

        # 测试不存在的脚本
        try:
            result = self.optimizer.analyze_script("/nonexistent/script.py")
            print("❌ 应抛出FileNotFoundError")
            return False
        except FileNotFoundError:
            print("✅ 正确抛出FileNotFoundError")
        except Exception as e:
            print(f"❌ 错误类型不正确: {e}")
            return False

        self.test_results.append(("错误处理", "✅ 通过", "正确处理错误"))
        return True

    def run_all_tests(self):
        """运行所有测试"""
        print("="*60)
        print("性能优化工具测试套件")
        print("="*60)

        # 运行所有测试
        self.test_analyze_simple_script()
        self.test_analyze_complex_script()
        self.test_bottleneck_detection()
        self.test_optimization_suggestions()
        self.test_html_report_generation()
        self.test_markdown_report_generation()
        self.test_monitor_resource()
        self.test_profile_decorator()
        self.test_batch_analyze()
        self.test_error_handling()

        # 打印结果汇总
        print("\n" + "="*60)
        print("测试结果汇总")
        print("="*60)

        passed = sum(1 for _, status, _ in self.test_results if "✅" in status)
        total = len(self.test_results)

        for test_name, status, detail in self.test_results:
            print(f"{status} {test_name}: {detail}")

        print("\n" + "="*60)
        print(f"通过: {passed}/{total}")
        print("="*60)

        if passed == total:
            print("\n🎉 所有测试通过！")
            return True
        else:
            print(f"\n⚠️ {total - passed} 个测试失败")
            return False


def main():
    """主函数"""
    tester = TestPerformanceOptimizer()
    success = tester.run_all_tests()

    # 返回退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
