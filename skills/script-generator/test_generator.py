#!/usr/bin/env python3
"""
测试自动化脚本生成器
"""

import sys
import tempfile
import shutil
from pathlib import Path

# 添加技能目录到路径
skill_dir = Path(__file__).parent
sys.path.insert(0, str(skill_dir))

from generator import ScriptGenerator, DANGEROUS_PATTERNS


def test_generator_creation():
    """测试1: 生成器创建"""
    print("测试1: 生成器创建...")
    try:
        generator = ScriptGenerator()
        assert generator is not None
        assert hasattr(generator, 'templates')
        assert hasattr(generator, '_analyze_prompt')
        assert hasattr(generator, 'generate')
        print("✅ 通过\n")
        return True
    except Exception as e:
        print(f"❌ 失败: {e}\n")
        return False


def test_prompt_analysis():
    """测试2: 需求解析"""
    print("测试2: 需求解析...")
    try:
        generator = ScriptGenerator()

        # 测试Shell脚本需求
        analysis1 = generator._analyze_prompt("创建一个bash脚本备份/data目录")
        print(f"  分析bash需求: {analysis1['language_preference']}")
        assert analysis1['language_preference'] == 'shell'

        # 测试Python脚本需求
        analysis2 = generator._analyze_prompt("写一个python脚本监控CPU")
        print(f"  分析python需求: {analysis2['language_preference']}")
        assert analysis2['language_preference'] == 'python'

        # 测试Node脚本需求
        analysis3 = generator._analyze_prompt("使用node.js创建API服务器")
        print(f"  分析node需求: {analysis3['language_preference']}")
        assert analysis3['language_preference'] == 'node'

        # 测试任务类型识别
        analysis4 = generator._analyze_prompt("定时备份文件")
        print(f"  分析备份任务: {analysis4['task_type']}")
        assert analysis4['task_type'] == 'backup'

        analysis5 = generator._analyze_prompt("监控服务器状态")
        print(f"  分析监控任务: {analysis5['task_type']}")
        assert analysis5['task_type'] == 'monitor'

        # 测试路径提取
        analysis6 = generator._analyze_prompt("备份 /data 目录到 /backup")
        print(f"  提取路径: {analysis6['parameters'].get('paths', [])}")
        assert '/data' in analysis6['parameters'].get('paths', [])
        assert '/backup' in analysis6['parameters'].get('paths', [])

        # 测试数字提取
        analysis7 = generator._analyze_prompt("保留最近7天的备份，每2小时执行一次")
        print(f"  提取数字: {analysis7['parameters'].get('numbers', [])}")
        assert 7 in analysis7['parameters'].get('numbers', [])
        assert 2 in analysis7['parameters'].get('numbers', [])

        print("✅ 通过\n")
        return True
    except AssertionError as e:
        import traceback
        print(f"❌ 断言失败: {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        import traceback
        print(f"❌ 失败: {e}")
        traceback.print_exc()
        return False


def test_code_generation():
    """测试3: 代码生成"""
    print("测试3: 代码生成...")
    try:
        generator = ScriptGenerator()

        # 测试Python脚本生成
        code_py, _, _ = generator.generate("创建一个监控脚本", 'python')
        print(f"  Python代码长度: {len(code_py)}")
        print(f"  Python代码前200字符: {code_py[:200]}")
        assert '#!/usr/bin/env python3' in code_py
        # 可能使用monitor模板，不一定有import sys
        assert 'def ' in code_py or 'class ' in code_py

        # 测试Shell脚本生成
        code_sh, _, _ = generator.generate("创建备份脚本", 'shell')
        print(f"  Shell代码长度: {len(code_sh)}")
        assert '#!/bin/bash' in code_sh
        assert 'set -e' in code_sh
        assert 'echo' in code_sh

        # 测试Node脚本生成
        code_js, _, _ = generator.generate("创建部署脚本", 'node')
        print(f"  Node代码长度: {len(code_js)}")
        assert '#!/usr/bin/env node' in code_js
        assert 'console.log' in code_js

        print("✅ 通过\n")
        return True
    except AssertionError as e:
        import traceback
        print(f"❌ 断言失败: {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        import traceback
        print(f"❌ 失败: {e}")
        traceback.print_exc()
        return False


def test_safety_check():
    """测试4: 安全检查"""
    print("测试4: 安全检查...")
    try:
        generator = ScriptGenerator()

        # 测试危险命令检测
        dangerous_codes = [
            "rm -rf /",
            ":(){:|:&};:",
            "dd if=/dev/zero of=/dev/sda",
        ]

        for code in dangerous_codes:
            is_safe, warnings = generator._safety_check(code)
            assert not is_safe, f"应该检测到危险命令: {code}"
            assert len(warnings) > 0

        # 测试安全代码
        safe_code = "echo 'hello world'"
        is_safe, warnings = generator._safety_check(safe_code)
        assert is_safe
        assert len(warnings) == 0

        print("✅ 通过\n")
        return True
    except Exception as e:
        print(f"❌ 失败: {e}\n")
        return False


def test_file_output():
    """测试5: 文件输出"""
    print("测试5: 文件输出...")
    try:
        generator = ScriptGenerator()

        # 创建临时目录
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_script.py"

            # 生成脚本到文件
            code, _, _ = generator.generate("测试脚本", 'python')

            output_path.write_text(code, encoding='utf-8')

            # 验证文件存在
            assert output_path.exists()

            # 验证文件内容
            content = output_path.read_text(encoding='utf-8')
            assert '#!/usr/bin/env python3' in content

        print("✅ 通过\n")
        return True
    except Exception as e:
        print(f"❌ 失败: {e}\n")
        return False


def test_template_filling():
    """测试6: 模板填充"""
    print("测试6: 模板填充...")
    try:
        generator = ScriptGenerator()

        # 生成带参数的脚本
        code, _, _ = generator.generate(
            "备份/data目录到/backup，保留7天",
            'python'
        )

        # 验证参数是否被填充
        assert '2026-' in code  # timestamp
        assert '/data' in code  # paths
        assert '/backup' in code
        assert '7' in code  # numbers

        print("✅ 通过\n")
        return True
    except Exception as e:
        print(f"❌ 失败: {e}\n")
        return False


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("自动化脚本生成器 - 测试套件")
    print("=" * 60)
    print()

    tests = [
        test_generator_creation,
        test_prompt_analysis,
        test_code_generation,
        test_safety_check,
        test_file_output,
        test_template_filling,
    ]

    results = []
    for test in tests:
        results.append(test())

    # 汇总结果
    print("=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"\n通过: {passed}/{total}")

    if passed == total:
        print("✅ 所有测试通过！\n")
        return 0
    else:
        print(f"❌ {total - passed} 个测试失败\n")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
