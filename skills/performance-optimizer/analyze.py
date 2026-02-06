#!/usr/bin/env python3
"""
性能分析命令行工具
"""

import sys
import os
from performance_optimizer import PerformanceOptimizer


def main():
    """主函数"""
    optimizer = PerformanceOptimizer()

    # 简单实现：分析指定脚本
    if len(sys.argv) > 1:
        script_path = sys.argv[1]
        print(f"分析脚本: {script_path}")

        result = optimizer.analyze_script(script_path)

        print(f"\n总执行时间: {result.total_time:.4f}s")
        print(f"\n识别到 {len(result.functions)} 个函数:")
        for func in result.functions[:10]:
            print(f"  - {func.name}: {func.time:.4f}s ({func.calls}次)")

        print(f"\n检测到 {len(result.bottlenecks)} 个瓶颈:")
        for bottleneck in result.bottlenecks:
            print(f"  - {bottleneck.type}: {bottleneck.suggestion}")

        # 生成报告
        report_dir = os.path.join(os.path.dirname(script_path), "performance_reports")
        os.makedirs(report_dir, exist_ok=True)

        html_report = os.path.join(report_dir, "report.html")
        md_report = os.path.join(report_dir, "report.md")

        optimizer.generate_html_report(result, html_report)
        optimizer.generate_markdown_report(result, md_report)

        print(f"\n报告已生成:")
        print(f"  - HTML: {html_report}")
        print(f"  - Markdown: {md_report}")
    else:
        print("用法: python analyze.py <脚本路径>")
        sys.exit(1)


if __name__ == "__main__":
    main()
