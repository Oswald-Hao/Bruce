#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Format Handler 测试脚本
测试JSON/YAML转换、格式化、验证、合并等功能
"""

import sys
import os
import tempfile
import shutil
sys.path.insert(0, os.path.dirname(__file__))

from data_format_handler import DataFormatHandler


def test_1_initialization():
    """测试1: 初始化"""
    print("测试1: 初始化")

    handler = DataFormatHandler()

    assert handler.encoding == 'utf-8'

    print("✅ 测试1通过: 初始化正常")
    return True


def test_2_json_format():
    """测试2: JSON格式化"""
    print("\n测试2: JSON格式化")

    handler = DataFormatHandler()
    input_file = tempfile.mktemp(suffix='.json')
    output_file = tempfile.mktemp(suffix='.json')

    try:
        # 创建测试JSON
        ugly_json = '{"name":"test","value":123,"nested":{"key":"val"}}'
        with open(input_file, 'w') as f:
            f.write(ugly_json)

        # 格式化
        formatted = handler.format_json(input_file, output_file, indent=2)

        # 验证
        assert '  "name": "test"' in formatted
        assert '  "value": 123' in formatted
        assert os.path.exists(output_file)

        # 读取格式化后的文件
        with open(output_file) as f:
            content = f.read()
        assert '  "name": "test"' in content

        print("✅ 测试2通过: JSON格式化正常")
        return True
    finally:
        for path in [input_file, output_file]:
            if os.path.exists(path):
                os.unlink(path)


def test_3_yaml_format():
    """测试3: YAML格式化"""
    print("\n测试3: YAML格式化")

    handler = DataFormatHandler()

    if not handler.yaml_available:
        print("⚠️  测试3跳过: PyYAML未安装")
        return True

    input_file = tempfile.mktemp(suffix='.yaml')
    output_file = tempfile.mktemp(suffix='.yaml')

    try:
        # 创建测试YAML（正确格式）
        ugly_yaml = 'name: test\nvalue: 123\nnested:\n  key: val'
        with open(input_file, 'w') as f:
            f.write(ugly_yaml)

        # 格式化
        formatted = handler.format_yaml(input_file, output_file, indent=2)

        # 验证
        assert 'name: test' in formatted
        assert 'value: 123' in formatted
        assert os.path.exists(output_file)

        print("✅ 测试3通过: YAML格式化正常")
        return True
    finally:
        for path in [input_file, output_file]:
            if os.path.exists(path):
                os.unlink(path)


def test_4_json_to_yaml():
    """测试4: JSON转YAML"""
    print("\n测试4: JSON转YAML")

    handler = DataFormatHandler()

    if not handler.yaml_available:
        print("⚠️  测试4跳过: PyYAML未安装")
        return True

    json_file = tempfile.mktemp(suffix='.json')
    yaml_file = tempfile.mktemp(suffix='.yaml')

    try:
        # 创建测试JSON
        test_data = {'name': 'test', 'value': 123, 'nested': {'key': 'val'}}
        with open(json_file, 'w') as f:
            import json
            json.dump(test_data, f)

        # 转换
        success = handler.convert(json_file, yaml_file, from_format='json', to_format='yaml')

        assert success == True
        assert os.path.exists(yaml_file)

        # 验证YAML内容
        with open(yaml_file) as f:
            content = f.read()
        assert 'name: test' in content
        assert 'value: 123' in content

        print("✅ 测试4通过: JSON转YAML正常")
        return True
    finally:
        for path in [json_file, yaml_file]:
            if os.path.exists(path):
                os.unlink(path)


def test_5_yaml_to_json():
    """测试5: YAML转JSON"""
    print("\n测试5: YAML转JSON")

    handler = DataFormatHandler()

    if not handler.yaml_available:
        print("⚠️  测试5跳过: PyYAML未安装")
        return True

    yaml_file = tempfile.mktemp(suffix='.yaml')
    json_file = tempfile.mktemp(suffix='.json')

    try:
        # 创建测试YAML
        test_yaml = 'name: test\nvalue: 123\nnested:\n  key: val'
        with open(yaml_file, 'w') as f:
            f.write(test_yaml)

        # 转换
        success = handler.convert(yaml_file, json_file, from_format='yaml', to_format='json')

        assert success == True
        assert os.path.exists(json_file)

        # 验证JSON内容
        with open(json_file) as f:
            import json
            data = json.load(f)
        assert data['name'] == 'test'
        assert data['value'] == 123
        assert data['nested']['key'] == 'val'

        print("✅ 测试5通过: YAML转JSON正常")
        return True
    finally:
        for path in [yaml_file, json_file]:
            if os.path.exists(path):
                os.unlink(path)


def test_6_json_validate():
    """测试6: JSON验证"""
    print("\n测试6: JSON验证")

    handler = DataFormatHandler()
    json_file = tempfile.mktemp(suffix='.json')

    try:
        # 创建测试JSON
        test_data = {'name': 'test', 'age': 25, 'email': 'test@example.com'}
        import json
        with open(json_file, 'w') as f:
            json.dump(test_data, f)

        # 验证
        schema = {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'age': {'type': 'number'},
                'email': {'type': 'string'}
            },
            'required': ['name', 'email']
        }

        result = handler.validate_json(json_file, schema)
        assert result['valid'] == True

        # 测试缺少必需字段
        bad_data = {'age': 25}
        with open(json_file, 'w') as f:
            json.dump(bad_data, f)

        result2 = handler.validate_json(json_file, schema)
        assert result2['valid'] == False
        assert len(result2['errors']) > 0

        print("✅ 测试6通过: JSON验证正常")
        return True
    finally:
        if os.path.exists(json_file):
            os.unlink(json_file)


def test_7_json_merge():
    """测试7: JSON合并"""
    print("\n测试7: JSON合并")

    handler = DataFormatHandler()
    file1 = tempfile.mktemp(suffix='.json')
    file2 = tempfile.mktemp(suffix='.json')
    merged_file = tempfile.mktemp(suffix='.json')

    try:
        # 创建测试文件
        data1 = {'name': 'Alice', 'age': 25}
        data2 = {'name': 'Bob', 'city': 'NYC'}

        import json
        with open(file1, 'w') as f:
            json.dump(data1, f)
        with open(file2, 'w') as f:
            json.dump(data2, f)

        # 合并（replace策略）
        handler.merge_json_files([file1, file2], merged_file, merge_strategy='replace')

        with open(merged_file) as f:
            merged = json.load(f)

        # replace策略应该完全覆盖
        assert merged == data2

        print("✅ 测试7通过: JSON合并正常")
        return True
    finally:
        for path in [file1, file2, merged_file]:
            if os.path.exists(path):
                os.unlink(path)


def test_8_json_merge_deep():
    """测试8: JSON深度合并"""
    print("\n测试8: JSON深度合并")

    handler = DataFormatHandler()
    file1 = tempfile.mktemp(suffix='.json')
    file2 = tempfile.mktemp(suffix='.json')
    merged_file = tempfile.mktemp(suffix='.json')

    try:
        # 创建测试文件（有重叠字段）
        data1 = {
            'name': 'Alice',
            'info': {
                'age': 25,
                'city': 'Boston'
            }
        }
        data2 = {
            'info': {
                'age': 26,
                'email': 'alice@example.com'
            }
        }

        import json
        with open(file1, 'w') as f:
            json.dump(data1, f)
        with open(file2, 'w') as f:
            json.dump(data2, f)

        # 深度合并
        handler.merge_json_files([file1, file2], merged_file, merge_strategy='merge')

        with open(merged_file) as f:
            merged = json.load(f)

        # 验证深度合并
        assert merged['name'] == 'Alice'  # 来自file1
        assert merged['info']['age'] == 26  # 被file2覆盖
        assert merged['info']['city'] == 'Boston'  # 来自file1
        assert merged['info']['email'] == 'alice@example.com'  # 来自file2

        print("✅ 测试8通过: JSON深度合并正常")
        return True
    finally:
        for path in [file1, file2, merged_file]:
            if os.path.exists(path):
                os.unlink(path)


def test_9_json_diff():
    """测试9: JSON比较"""
    print("\n测试9: JSON比较")

    handler = DataFormatHandler()
    file1 = tempfile.mktemp(suffix='.json')
    file2 = tempfile.mktemp(suffix='.json')
    file3 = tempfile.mktemp(suffix='.json')

    try:
        import json
        data1 = {'name': 'Alice', 'age': 25}
        data2 = {'name': 'Bob', 'age': 25}
        data3 = {'name': 'Alice', 'age': 25}

        with open(file1, 'w') as f:
            json.dump(data1, f)
        with open(file2, 'w') as f:
            json.dump(data2, f)
        with open(file3, 'w') as f:
            json.dump(data3, f)

        # 比较不同文件
        diff1 = handler.diff_json(file1, file2)
        assert diff1['identical'] == False

        # 比较相同文件
        diff2 = handler.diff_json(file1, file3)
        assert diff2['identical'] == True

        print("✅ 测试9通过: JSON比较正常")
        return True
    finally:
        for path in [file1, file2, file3]:
            if os.path.exists(path):
                os.unlink(path)


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("Data Format Handler 测试套件")
    print("=" * 60)

    tests = [
        test_1_initialization,
        test_2_json_format,
        test_3_yaml_format,
        test_4_json_to_yaml,
        test_5_yaml_to_json,
        test_6_json_validate,
        test_7_json_merge,
        test_8_json_merge_deep,
        test_9_json_diff
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"❌ 测试失败: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)

    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
