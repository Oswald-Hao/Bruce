#!/usr/bin/env python3
"""
Performance Optimizer - 性能优化工具
代码复杂度分析、性能瓶颈定位、资源使用分析、优化建议
"""

import os
import sys
import ast
import time
import cProfile
import pstats
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict


class PerformanceAnalyzer:
    """性能分析器"""

    def __init__(self, target_path: str = None):
        self.target_path = Path(target_path) if target_path else Path.cwd()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "target": str(self.target_path),
            "analysis": {
                "complexity": {},
                "bottlenecks": [],
                "resources": {},
                "recommendations": []
            }
        }

    def analyze_complexity(self) -> Dict[str, Any]:
        """分析代码复杂度"""
        complexity_data = {}

        # 遍历Python文件
        py_files = list(self.target_path.rglob("*.py"))

        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    source = f.read()

                tree = ast.parse(source)
                visitor = ComplexityVisitor()
                visitor.visit(tree)

                complexity_data[str(py_file)] = {
                    "cyclomatic": visitor.max_complexity,
                    "functions": visitor.function_complexity,
                    "classes": visitor.class_count,
                    "lines": source.count('\n') + 1
                }

            except Exception as e:
                complexity_data[str(py_file)] = {"error": str(e)}

        self.results["analysis"]["complexity"] = complexity_data
        return complexity_data

    def profile_code(self, file_path: str = None) -> List[Dict[str, Any]]:
        """分析代码性能（使用cProfile）"""
        if not file_path:
            # 如果没有指定文件，分析整个目录
            return []

        profiler = cProfile.Profile()

        try:
            # 导入并执行模块
            import importlib.util
            spec = importlib.util.spec_from_file_location("test_module", file_path)
            module = importlib.util.module_from_spec(spec)

            # 执行并分析
            profiler.enable()
            spec.loader.exec_module(module)
            profiler.disable()

            # 获取统计结果
            stats = pstats.Stats(profiler)

            # 提取瓶颈函数
            bottlenecks = []
            stats.strip_dirs()
            stats.sort_stats('cumulative')

            stats_stream = pstats.Stats(profiler, stream=None)
            stats_stream.strip_dirs()
            stats_stream.sort_stats('cumulative')

            # 获取前20个瓶颈
            stats_stream.stream = None
            stats_data = []
            for func, (cc, nc, tt, ct, callers) in stats_stream.get_stats_profile().func_profiles.items():
                stats_data.append({
                    "function": f"{func[0]}:{func[1]}({func[2]})",
                    "calls": cc,
                    "total_time": tt,
                    "cumulative_time": ct
                })

            # 排序并取前20
            stats_data.sort(key=lambda x: x['cumulative_time'], reverse=True)
            bottlenecks = stats_data[:20]

            self.results["analysis"]["bottlenecks"] = bottlenecks
            return bottlenecks

        except Exception as e:
            print(f"⚠️  性能分析失败: {e}")
            return []

    def analyze_resources(self) -> Dict[str, Any]:
        """分析资源使用情况"""
        # 分析文件大小
        file_sizes = []
        total_size = 0

        for file_path in self.target_path.rglob("*"):
            if file_path.is_file():
                size = file_path.stat().st_size
                file_sizes.append({
                    "file": str(file_path.relative_to(self.target_path)),
                    "size": size
                })
                total_size += size

        # 找出最大的文件
        file_sizes.sort(key=lambda x: x['size'], reverse=True)
        top_files = file_sizes[:10]

        self.results["analysis"]["resources"] = {
            "total_size": total_size,
            "file_count": len(file_sizes),
            "largest_files": top_files
        }

        return self.results["analysis"]["resources"]

    def generate_recommendations(self) -> List[str]:
        """生成优化建议"""
        recommendations = []

        # 基于复杂度的建议
        complexity = self.results["analysis"].get("complexity", {})
        for file, data in complexity.items():
            if isinstance(data, dict) and "cyclomatic" in data:
                if data["cyclomatic"] > 10:
                    recommendations.append(
                        f"⚠️  {file}: 复杂度过高({data['cyclomatic']})，建议拆分函数"
                    )

        # 基于瓶颈的建议
        bottlenecks = self.results["analysis"].get("bottlenecks", [])
        if bottlenecks:
            top_bottleneck = bottlenecks[0]
            if top_bottleneck['cumulative_time'] > 1.0:
                recommendations.append(
                    f"🔥 性能瓶颈: {top_bottleneck['function']}"
                    f" 耗时{top_bottleneck['cumulative_time']:.2f}秒，建议优化"
                )

        # 基于资源的建议
        resources = self.results["analysis"].get("resources", {})
        if resources.get("total_size", 0) > 100 * 1024 * 1024:  # >100MB
            recommendations.append(
                f"💾 总大小超过100MB，建议清理不必要文件或使用压缩"
            )

        # 通用建议
        if not recommendations:
            recommendations.append("✅ 代码质量良好，暂无明显性能问题")

        self.results["analysis"]["recommendations"] = recommendations
        return recommendations

    def analyze(self, profile_file: str = None) -> Dict[str, Any]:
        """执行完整分析"""
        print(f"🔍 分析目标: {self.target_path}")

        # 1. 分析复杂度
        print("  📊 分析代码复杂度...")
        self.analyze_complexity()

        # 2. 性能分析（如果指定了文件）
        if profile_file and os.path.exists(profile_file):
            print(f"  ⏱️  分析性能: {profile_file}")
            self.profile_code(profile_file)

        # 3. 分析资源
        print("  💾 分析资源使用...")
        self.analyze_resources()

        # 4. 生成建议
        print("  💡 生成优化建议...")
        self.generate_recommendations()

        return self.results

    def print_report(self):
        """打印分析报告"""
        print("\n" + "=" * 60)
        print("性能优化报告")
        print("=" * 60)

        # 复杂度分析
        print("\n📊 代码复杂度分析")
        print("-" * 60)
        complexity = self.results["analysis"]["complexity"]
        for file, data in complexity.items():
            if isinstance(data, dict) and "cyclomatic" in data:
                print(f"{file}:")
                print(f"  复杂度: {data['cyclomatic']}")
                print(f"  函数数: {len(data.get('functions', {}))}")
                print(f"  行数: {data.get('lines', 0)}")

        # 性能瓶颈
        bottlenecks = self.results["analysis"].get("bottlenecks", [])
        if bottlenecks:
            print("\n⏱️  性能瓶颈（Top 10）")
            print("-" * 60)
            for i, b in enumerate(bottlenecks[:10], 1):
                print(f"{i}. {b['function']}")
                print(f"   调用: {b['calls']}, 耗时: {b['cumulative_time']:.4f}s")

        # 优化建议
        print("\n💡 优化建议")
        print("-" * 60)
        recommendations = self.results["analysis"]["recommendations"]
        for rec in recommendations:
            print(rec)

        print("\n" + "=" * 60)

    def save_results(self, output_file: str = None):
        """保存分析结果"""
        if not output_file:
            output_file = self.target_path / "performance_report.json"

        output_file = Path(output_file)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"\n报告已保存: {output_file}")


class ComplexityVisitor(ast.NodeVisitor):
    """AST访问器，用于计算复杂度"""

    def __init__(self):
        self.max_complexity = 1
        self.current_complexity = 1
        self.function_complexity = {}
        self.class_count = 0
        self.current_function = None

    def visit_FunctionDef(self, node):
        self.current_function = node.name
        self.current_complexity = 1
        self.generic_visit(node)
        self.function_complexity[node.name] = self.current_complexity
        self.max_complexity = max(self.max_complexity, self.current_complexity)
        self.current_function = None

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_ClassDef(self, node):
        self.class_count += 1
        self.generic_visit(node)

    def visit_If(self, node):
        self.current_complexity += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.current_complexity += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.current_complexity += 1
        self.generic_visit(node)

    def visit_With(self, node):
        self.current_complexity += 1
        self.generic_visit(node)

    def visit_Try(self, node):
        self.current_complexity += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        self.current_complexity += 1
        self.generic_visit(node)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="性能优化工具")
    parser.add_argument("--analyze", metavar="PATH", help="分析代码性能")
    parser.add_argument("--profile", metavar="FILE", help="性能分析指定文件")
    parser.add_argument("--report", metavar="FILE", help="生成报告")
    parser.add_argument("--output", metavar="FILE", help="输出文件")

    args = parser.parse_args()

    analyzer = PerformanceAnalyzer(args.analyze)

    if args.analyze:
        analyzer.analyze(args.profile)
        analyzer.print_report()
        analyzer.save_results(args.output)

    elif args.report:
        with open(args.report, 'r') as f:
            data = json.load(f)
        print(json.dumps(data, indent=2, ensure_ascii=False))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
