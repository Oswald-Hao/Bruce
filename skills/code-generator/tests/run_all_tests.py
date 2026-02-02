"""
Code Generator - 完整测试套件

运行所有测试以确保代码生成器功能正常。
"""

import sys
import os

# 添加src目录到Python路径
src_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, src_dir)


def run_test_module(module_name):
    """运行单个测试模块"""
    print(f"\n{'='*60}")
    print(f"运行测试: {module_name}")
    print('='*60)

    try:
        module = __import__(module_name)
        if hasattr(module, 'main'):
            result = module.main()
            return result == 0
        else:
            # 如果没有main函数，运行所有测试函数
            test_functions = [
                getattr(module, name)
                for name in dir(module)
                if name.startswith('test_') and callable(getattr(module, name))
            ]
            for test_func in test_functions:
                try:
                    test_func()
                except Exception as e:
                    print(f"❌ {test_func.__name__} 失败: {e}")
                    return False
            return True
    except Exception as e:
        print(f"❌ 加载模块失败: {e}")
        return False


def main():
    """主测试函数"""
    test_modules = [
        'test_completers',
        'test_refactors',
        'test_analyzers',
        'test_code_generator'
    ]

    print("\n" + "="*60)
    print("Code Generator 测试套件")
    print("="*60)

    results = {}
    for module_name in test_modules:
        success = run_test_module(module_name)
        results[module_name] = success

    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)

    passed = sum(results.values())
    total = len(results)

    for module_name, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{module_name:30s} {status}")

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
