"""
Code Generator - 完整测试套件

运行所有测试以确保代码生成器功能正常。
"""

import sys
import os
import subprocess


def run_test_file(test_file):
    """运行单个测试文件"""
    print(f"\n{'='*60}")
    print(f"运行测试: {test_file}")
    print('='*60)

    test_dir = os.path.dirname(os.path.abspath(__file__))
    test_path = os.path.join(test_dir, test_file)

    result = subprocess.run(
        [sys.executable, test_path],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    return result.returncode == 0


def main():
    """主测试函数"""
    test_files = [
        'test_completers.py',
        'test_refactors.py',
        'test_analyzers.py',
        'test_code_generator.py'
    ]

    print("\n" + "="*60)
    print("Code Generator 测试套件")
    print("="*60)

    results = {}
    for test_file in test_files:
        success = run_test_file(test_file)
        results[test_file] = success

    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)

    passed = sum(results.values())
    total = len(results)

    for test_file, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_file:30s} {status}")

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
