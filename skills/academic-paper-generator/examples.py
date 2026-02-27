#!/usr/bin/env python3
"""
学术论文生成器 - 使用示例
"""

import subprocess
import sys

def example_1_basic():
    """示例1: 基本用法 - 从标题生成论文"""
    print("\n" + "="*60)
    print("📝 示例1: 基本用法")
    print("="*60)

    cmd = """
    python3 paper_generator.py \
        --title "A Novel Approach to Machine Learning" \
        --authors "John Doe, Jane Smith" \
        --type conference \
        --venue "NeurIPS 2026"
    """

    print("命令:")
    print(cmd)
    print("\n运行中...")
    subprocess.run(cmd, shell=True)


def example_2_from_project():
    """示例2: 从项目代码生成论文"""
    print("\n" + "="*60)
    print("📝 示例2: 从项目代码生成")
    print("="*60)

    cmd = """
    python3 paper_generator.py \
        --title "Auto-Generated Paper from Codebase" \
        --authors "Bruce AI" \
        --source /path/to/your/project \
        --type conference \
        --figures \
        --output-dir ./generated_paper
    """

    print("命令:")
    print(cmd)
    print("\n说明: 给我一个项目路径，我会分析代码并生成完整论文")


def example_3_with_data():
    """示例3: 使用实验数据生成"""
    print("\n" + "="*60)
    print("📝 示例3: 带实验数据生成")
    print("="*60)

    cmd = """
    python3 paper_generator.py \
        --title "Experimental Analysis of Deep Learning Models" \
        --authors "Research Team" \
        --results /path/to/experiments.csv \
        --figures \
        --type journal \
        --venue "Journal of Machine Learning Research"
    """

    print("命令:")
    print(cmd)
    print("\n说明: 给我实验结果CSV文件，我会生成图表和分析")


def example_4_complete():
    """示例4: 完整定制"""
    print("\n" + "="*60)
    print("📝 示例4: 完整定制（推荐用法）")
    print("="*60)

    cmd = """
    python3 paper_generator.py \
        --title "Bruce: An AI-Powered Research Assistant" \
        --authors "Oswald, Bruce AI" \
        --source /home/lejurobot/clawd \
        --results experiments/results.csv \
        --type conference \
        --venue "AAAI 2026" \
        --figures \
        --output-dir ./bruce_paper
    """

    print("命令:")
    print(cmd)
    print("\n说明: 完整参数，生成会议论文")


def example_5_review():
    """示例5: 生成综述论文"""
    print("\n" + "="*60)
    print("📝 示例5: 生成综述论文")
    print("="*60)

    cmd = """
    python3 paper_generator.py \
        --title "Recent Advances in Large Language Models: A Survey" \
        --authors "Survey Team" \
        --topic "大语言模型的最新进展综述" \
        --type review \
        --figures
    """

    print("命令:")
    print(cmd)
    print("\n说明: 从研究主题生成综述论文")


def interactive_example():
    """交互式示例"""
    print("\n" + "="*60)
    print("🤝 交互式使用指南")
    print("="*60)

    print("""
给你一个项目，我来生成论文：

1️⃣  给我项目路径：
   --source /home/user/my_project

2️⃣  给我论文标题：
   --title "My Awesome Research"

3️⃣  给我实验数据（可选）：
   --results /path/to/results.csv

4️⃣  我会自动：
   ✓ 分析代码结构
   ✓ 生成系统架构图
   ✓ 创建实验结果图表
   ✓ 生成对比分析图
   ✓ 撰写完整LaTeX论文
   ✓ 尝试编译PDF

输出文件：
   📄 main.tex - LaTeX源码
   📊 figures/ - 所有图表（PDF格式，300+ DPI）
   📋 metadata.json - 论文元数据
   📕 main.pdf - 最终论文（如果安装了LaTeX）

使用流程：
   1. 给我项目 → 我分析代码
   2. 我生成论文初稿
   3. 你检查修改LaTeX
   4. 我帮你编译PDF
   5. 提交到arXiv/会议
""")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("📚 学术论文生成器 - 使用示例")
    print("="*60)

    print("\n选择示例:")
    print("1. 基本用法")
    print("2. 从项目代码生成")
    print("3. 带实验数据生成")
    print("4. 完整定制")
    print("5. 生成综述论文")
    print("6. 交互式指南")
    print("0. 退出")

    while True:
        choice = input("\n请选择 (0-6): ").strip()

        if choice == "1":
            example_1_basic()
        elif choice == "2":
            example_2_from_project()
        elif choice == "3":
            example_3_with_data()
        elif choice == "4":
            example_4_complete()
        elif choice == "5":
            example_5_review()
        elif choice == "6":
            interactive_example()
        elif choice == "0":
            print("👋 再见！")
            break
        else:
            print("❌ 无效选择，请重试")


if __name__ == '__main__':
    main()
