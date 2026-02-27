#!/usr/bin/env python3
"""
测试学术论文生成器
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

def run_test(name, command, description):
    """运行单个测试"""
    print(f"\n{'='*60}")
    print(f"🧪 测试 {name}: {description}")
    print(f"{'='*60}")

    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=120
    )

    print(f"📝 命令: {command}")
    print(f"📤 返回码: {result.returncode}")

    if result.stdout:
        print(f"✅ 标准输出:\n{result.stdout[:500]}")

    if result.stderr:
        print(f"⚠️  标准错误:\n{result.stderr[:500]}")

    success = result.returncode == 0
    print(f"{'✅ 通过' if success else '❌ 失败'}")

    return success


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("🧪 学术论文生成器 - 测试套件")
    print("="*60)

    test_results = []

    # 测试1: 基本功能测试
    test1 = run_test(
        "基本功能",
        "cd /home/lejurobot/clawd/skills/academic-paper-generator && "
        "python3 paper_generator.py "
        "--title 'Test Paper' "
        "--authors 'Test Author' "
        "--type conference "
        "--output-dir /tmp/test_paper_basic",
        "测试基本论文生成功能"
    )
    test_results.append(("基本功能", test1))

    # 测试2: 从项目生成
    # 创建测试项目
    test_project = "/tmp/test_project"
    os.makedirs(test_project, exist_ok=True)

    # 创建测试Python文件
    with open(f"{test_project}/main.py", "w") as f:
        f.write("""
'''This is the main module of the project.'''
def process_data(data):
    '''Process the input data and return results.'''
    return data * 2

class Model:
    '''Main model class for prediction.'''
    def __init__(self):
        self.params = {}

    def train(self, X, y):
        '''Train the model on data.'''
        pass
""")

    test2 = run_test(
        "从项目生成",
        "cd /home/lejurobot/clawd/skills/academic-paper-generator && "
        "python3 paper_generator.py "
        "--title 'Auto Generated Paper from Project' "
        "--authors 'Auto Generator' "
        "--source /tmp/test_project "
        "--figures "
        "--output-dir /tmp/test_paper_project",
        "从项目代码自动生成论文"
    )
    test_results.append(("从项目生成", test2))

    # 测试3: 带实验数据生成
    # 创建测试数据
    test_data = "/tmp/test_results.csv"
    with open(test_data, "w") as f:
        f.write("epoch,accuracy,loss\n")
        f.write("1,75.2,0.65\n")
        f.write("2,78.5,0.58\n")
        f.write("3,82.1,0.52\n")
        f.write("4,85.7,0.45\n")
        f.write("5,88.9,0.38\n")

    test3 = run_test(
        "带实验数据",
        "cd /home/lejurobot/clawd/skills/academic-paper-generator && "
        "python3 paper_generator.py "
        "--title 'Experimental Results Paper' "
        "--authors 'Research Team' "
        "--results /tmp/test_results.csv "
        "--figures "
        "--output-dir /tmp/test_paper_results",
        "使用实验数据生成论文和图表"
    )
    test_results.append(("带实验数据", test3))

    # 测试4: 检查输出文件
    print(f"\n{'='*60}")
    print("🧪 测试4: 文件结构检查")
    print(f"{'='*60}")

    test_dirs = [
        "/tmp/test_paper_basic",
        "/tmp/test_paper_project",
        "/tmp/test_paper_results"
    ]

    all_files_exist = True
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            print(f"\n📁 检查目录: {test_dir}")

            files = list(Path(test_dir).rglob("*"))
            print(f"   文件数量: {len(files)}")

            for file in files:
                if file.is_file():
                    size = file.stat().st_size
                    print(f"   ✓ {file.name} ({size} bytes)")

            # 检查关键文件
            tex_file = Path(test_dir) / "main.tex"
            figures_dir = Path(test_dir) / "figures"

            if tex_file.exists():
                print(f"   ✅ main.tex 存在")
            else:
                print(f"   ❌ main.tex 缺失")
                all_files_exist = False

            if figures_dir.exists():
                figures = list(figures_dir.glob("*.pdf"))
                print(f"   ✅ figures/ 目录存在 ({len(figures)}个PDF)")
            else:
                print(f"   ⚠️  figures/ 目录不存在")
        else:
            print(f"   ❌ 目录不存在: {test_dir}")
            all_files_exist = False

    test_results.append(("文件结构", all_files_exist))

    # 测试5: LaTeX语法检查
    print(f"\n{'='*60}")
    print("🧪 测试5: LaTeX语法检查")
    print(f"{'='*60}")

    syntax_ok = True
    for test_dir in test_dirs:
        tex_file = Path(test_dir) / "main.tex"
        if tex_file.exists():
            print(f"\n📄 检查文件: {tex_file}")

            with open(tex_file, 'r') as f:
                content = f.read()

            # 检查基本LaTeX结构
            checks = {
                "documentclass": r"\documentclass" in content,
                "begin{document}": r"\begin{document}" in content,
                "end{document}": r"\end{document}" in content,
                "title": r"\title" in content,
                "author": r"\author" in content,
                "abstract": r"\begin{abstract}" in content,
                "section": r"\section" in content,
            }

            all_checks = all(checks.values())
            print(f"   LaTeX结构: {'✅ 完整' if all_checks else '⚠️  不完整'}")

            for check, passed in checks.items():
                status = "✅" if passed else "❌"
                print(f"      {status} {check}")

            if not all_checks:
                syntax_ok = False

    test_results.append(("LaTeX语法", syntax_ok))

    # 测试6: 图表生成检查
    print(f"\n{'='*60}")
    print("🧪 测试6: 图表生成检查")
    print(f"{'='*60}")

    figures_ok = True
    for test_dir in test_dirs:
        figures_dir = Path(test_dir) / "figures"
        if figures_dir.exists():
            figures = list(figures_dir.glob("*.pdf"))
            print(f"\n📊 {test_dir}: {len(figures)}个图表")

            for fig in figures:
                size = fig.stat().st_size
                # 检查文件大小（至少1KB）
                if size > 1024:
                    print(f"   ✅ {fig.name} ({size} bytes)")
                else:
                    print(f"   ⚠️  {fig.name} ({size} bytes) - 可能损坏")
                    figures_ok = False

    test_results.append(("图表生成", figures_ok))

    # 测试7: 主题生成测试
    test7 = run_test(
        "主题生成",
        "cd /home/lejurobot/clawd/skills/academic-paper-generator && "
        "python3 paper_generator.py "
        "--title 'Deep Learning in Computer Vision' "
        "--authors 'AI Research Lab' "
        "--topic '深度学习在计算机视觉中的应用' "
        "--type journal "
        "--figures "
        "--output-dir /tmp/test_paper_topic",
        "从研究主题生成论文"
    )
    test_results.append(("主题生成", test7))

    # 汇总结果
    print(f"\n{'='*60}")
    print("📊 测试结果汇总")
    print(f"{'='*60}")

    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)

    for name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1


if __name__ == '__main__':
    sys.exit(main())
