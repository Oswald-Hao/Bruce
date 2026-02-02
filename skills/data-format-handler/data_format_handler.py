#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Format Handler - JSON/YAML处理工具
支持转换、格式化、验证、合并等功能
"""

import os
import json
from typing import List, Dict, Any, Optional, Union


class DataFormatHandler:
    """数据格式处理工具类"""

    def __init__(self, encoding: str = 'utf-8'):
        """
        初始化数据格式处理器

        Args:
            encoding: 文件编码
        """
        self.encoding = encoding

        # 尝试导入PyYAML
        try:
            import yaml
            self.yaml = yaml
            self.yaml_available = True
        except ImportError:
            self.yaml = None
            self.yaml_available = False
            print("Warning: PyYAML not installed. Install with: pip install pyyaml")

    def _read_file(self, filepath: str) -> str:
        """读取文件内容"""
        try:
            with open(filepath, 'r', encoding=self.encoding) as f:
                return f.read()
        except Exception as e:
            raise Exception(f"读取文件失败 {filepath}: {e}")

    def _write_file(self, filepath: str, content: str):
        """写入文件内容"""
        try:
            os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
            with open(filepath, 'w', encoding=self.encoding) as f:
                f.write(content)
        except Exception as e:
            raise Exception(f"写入文件失败 {filepath}: {e}")

    def parse_json(self, content: str) -> Any:
        """解析JSON字符串"""
        try:
            return json.loads(content)
        except Exception as e:
            raise Exception(f"JSON解析失败: {e}")

    def parse_yaml(self, content: str) -> Any:
        """解析YAML字符串"""
        if not self.yaml_available:
            raise RuntimeError("PyYAML未安装")

        try:
            return self.yaml.safe_load(content)
        except Exception as e:
            raise Exception(f"YAML解析失败: {e}")

    def dump_json(self, data: Any, indent: int = 2, sort_keys: bool = False, ensure_ascii: bool = False) -> str:
        """转储为JSON字符串"""
        try:
            return json.dumps(data, indent=indent, sort_keys=sort_keys, ensure_ascii=ensure_ascii)
        except Exception as e:
            raise Exception(f"JSON序列化失败: {e}")

    def dump_yaml(self, data: Any, indent: int = 2) -> str:
        """转储为YAML字符串"""
        if not self.yaml_available:
            raise RuntimeError("PyYAML未安装")

        try:
            return self.yaml.dump(data, default_flow_style=False, indent=indent, allow_unicode=True)
        except Exception as e:
            raise Exception(f"YAML序列化失败: {e}")

    def convert(
        self,
        input_file: str,
        output_file: str,
        from_format: str = 'auto',
        to_format: str = 'auto',
        **kwargs
    ) -> bool:
        """
        转换文件格式

        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径
            from_format: 输入格式（json/yaml/auto）
            to_format: 输出格式（json/yaml/auto）
            **kwargs: 其他参数（indent等）

        Returns:
            是否成功
        """
        # 自动检测格式
        if from_format == 'auto':
            if input_file.endswith('.json'):
                from_format = 'json'
            elif input_file.endswith('.yaml') or input_file.endswith('.yml'):
                from_format = 'yaml'
            else:
                raise Exception("无法自动检测输入格式，请明确指定from_format")

        if to_format == 'auto':
            if output_file.endswith('.json'):
                to_format = 'json'
            elif output_file.endswith('.yaml') or output_file.endswith('.yml'):
                to_format = 'yaml'
            else:
                raise Exception("无法自动检测输出格式，请明确指定to_format")

        # 读取并解析
        content = self._read_file(input_file)

        if from_format == 'json':
            data = self.parse_json(content)
        elif from_format == 'yaml':
            data = self.parse_yaml(content)
        else:
            raise Exception(f"不支持的输入格式: {from_format}")

        # 序列化并写入
        if to_format == 'json':
            output_content = self.dump_json(data, **kwargs)
        elif to_format == 'yaml':
            output_content = self.dump_yaml(data, **kwargs)
        else:
            raise Exception(f"不支持的输出格式: {to_format}")

        self._write_file(output_file, output_content)
        return True

    def format_json(
        self,
        input_file: str,
        output_file: str = None,
        indent: int = 2,
        sort_keys: bool = False,
        ensure_ascii: bool = False
    ) -> str:
        """
        格式化JSON文件

        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径（可选，None则返回字符串）
            indent: 缩进空格数
            sort_keys: 是否排序键
            ensure_ascii: 是否转义ASCII

        Returns:
            格式化后的字符串
        """
        content = self._read_file(input_file)
        data = self.parse_json(content)
        formatted = self.dump_json(data, indent=indent, sort_keys=sort_keys, ensure_ascii=ensure_ascii)

        if output_file:
            self._write_file(output_file, formatted)

        return formatted

    def format_yaml(
        self,
        input_file: str,
        output_file: str = None,
        indent: int = 2
    ) -> str:
        """
        格式化YAML文件

        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径（可选，None则返回字符串）
            indent: 缩进空格数

        Returns:
            格式化后的字符串
        """
        content = self._read_file(input_file)
        data = self.parse_yaml(content)
        formatted = self.dump_yaml(data, indent=indent)

        if output_file:
            self._write_file(output_file, formatted)

        return formatted

    def validate_json(
        self,
        input_file: str,
        schema: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        验证JSON文件

        Args:
            input_file: 输入文件路径
            schema: JSON Schema（可选）

        Returns:
            验证结果
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }

        try:
            content = self._read_file(input_file)
            data = self.parse_json(content)

            if schema:
                # 简单schema验证
                if 'type' in schema:
                    expected_type = schema['type']
                    if expected_type == 'object' and not isinstance(data, dict):
                        result['valid'] = False
                        result['errors'].append(f"期望object类型，实际为{type(data).__name__}")

                if 'required' in schema and isinstance(data, dict):
                    for field in schema['required']:
                        if field not in data:
                            result['valid'] = False
                            result['errors'].append(f"缺少必需字段: {field}")

                if 'properties' in schema and isinstance(data, dict):
                    for prop, prop_schema in schema['properties'].items():
                        if prop in data:
                            if 'type' in prop_schema:
                                expected_type = prop_schema['type']
                                type_map = {
                                    'string': str,
                                    'number': (int, float),
                                    'integer': int,
                                    'boolean': bool,
                                    'array': list,
                                    'object': dict
                                }
                                expected_python_type = type_map.get(expected_type)
                                if expected_python_type and not isinstance(data[prop], expected_python_type):
                                    result['valid'] = False
                                    result['errors'].append(
                                        f"字段{prop}类型错误: 期望{expected_type}，实际为{type(data[prop]).__name__}"
                                    )

        except Exception as e:
            result['valid'] = False
            result['errors'].append(str(e))

        return result

    def merge_json_files(
        self,
        input_files: List[str],
        output_file: str,
        merge_strategy: str = 'replace'  # replace或merge
    ) -> bool:
        """
        合并JSON文件

        Args:
            input_files: 输入文件列表
            output_file: 输出文件路径
            merge_strategy: 合并策略（replace=覆盖，merge=递归合并）

        Returns:
            是否成功
        """
        merged = {}

        for filepath in input_files:
            content = self._read_file(filepath)
            data = self.parse_json(content)

            if merge_strategy == 'merge' and isinstance(data, dict) and isinstance(merged, dict):
                merged = self._deep_merge(merged, data)
            else:
                merged = data

        output_content = self.dump_json(merged, indent=2)
        self._write_file(output_file, output_content)
        return True

    def _deep_merge(self, base: Any, update: Any) -> Any:
        """深度合并两个字典"""
        if not isinstance(base, dict) or not isinstance(update, dict):
            return update

        result = base.copy()
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def merge_yaml_files(
        self,
        input_files: List[str],
        output_file: str,
        merge_strategy: str = 'replace'
    ) -> bool:
        """
        合并YAML文件

        Args:
            input_files: 输入文件列表
            output_file: 输出文件路径
            merge_strategy: 合并策略

        Returns:
            是否成功
        """
        if not self.yaml_available:
            raise RuntimeError("PyYAML未安装")

        merged = {}

        for filepath in input_files:
            content = self._read_file(filepath)
            data = self.parse_yaml(content)

            if merge_strategy == 'merge' and isinstance(data, dict) and isinstance(merged, dict):
                merged = self._deep_merge(merged, data)
            else:
                merged = data

        output_content = self.dump_yaml(merged, indent=2)
        self._write_file(output_file, output_content)
        return True

    def diff_json(self, file1: str, file2: str) -> Dict[str, Any]:
        """
        比较两个JSON文件

        Args:
            file1: 文件1路径
            file2: 文件2路径

        Returns:
            差异结果
        """
        content1 = self._read_file(file1)
        content2 = self._read_file(file2)

        data1 = self.parse_json(content1)
        data2 = self.parse_json(content2)

        return {
            'file1': file1,
            'file2': file2,
            'identical': data1 == data2,
            'data1': data1,
            'data2': data2
        }

    def batch_convert(
        self,
        input_dir: str,
        output_dir: str,
        from_format: str,
        to_format: str,
        **kwargs
    ) -> List[Dict[str, str]]:
        """
        批量转换文件

        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            from_format: 输入格式
            to_format: 输出格式
            **kwargs: 其他参数

        Returns:
            处理结果列表
        """
        results = []

        # 文件扩展名映射
        ext_map = {
            'json': '.json',
            'yaml': '.yaml',
            'yml': '.yml'
        }

        from_ext = ext_map.get(from_format, '')

        for filename in os.listdir(input_dir):
            if not filename.endswith(from_ext):
                continue

            input_file = os.path.join(input_dir, filename)

            # 生成输出文件名
            base_name = os.path.splitext(filename)[0]
            output_file = os.path.join(output_dir, base_name + ext_map.get(to_format, ''))

            try:
                success = self.convert(input_file, output_file, from_format, to_format, **kwargs)
                results.append({
                    'input': input_file,
                    'output': output_file,
                    'status': 'success' if success else 'failed'
                })
            except Exception as e:
                results.append({
                    'input': input_file,
                    'output': output_file,
                    'status': 'failed',
                    'error': str(e)
                })

        return results


def main():
    """命令行示例"""
    import argparse

    parser = argparse.ArgumentParser(description='JSON/YAML处理工具')
    parser.add_argument('--action', choices=['convert', 'format', 'validate', 'merge'], required=True, help='操作类型')
    parser.add_argument('--input', help='输入文件')
    parser.add_argument('--output', help='输出文件')
    parser.add_argument('--from', dest='from_format', help='输入格式')
    parser.add_argument('--to', dest='to_format', help='输出格式')
    parser.add_argument('--indent', type=int, default=2, help='缩进')
    args = parser.parse_args()

    handler = DataFormatHandler()

    if args.action == 'convert' and args.input and args.output:
        handler.convert(
            args.input,
            args.output,
            from_format=args.from_format or 'auto',
            to_format=args.to_format or 'auto',
            indent=args.indent
        )
        print(f"转换完成: {args.input} → {args.output}")

    elif args.action == 'format' and args.input:
        if args.input.endswith('.json'):
            formatted = handler.format_json(args.input, args.output, indent=args.indent)
        elif args.input.endswith('.yaml') or args.input.endswith('.yml'):
            formatted = handler.format_yaml(args.input, args.output, indent=args.indent)
        else:
            print("不支持的文件格式")

        if not args.output:
            print(formatted)
        else:
            print(f"格式化完成: {args.output}")

    elif args.action == 'validate' and args.input:
        result = handler.validate_json(args.input)
        print(f"验证结果: {'通过' if result['valid'] else '失败'}")
        if result['errors']:
            print("错误:", result['errors'])


if __name__ == '__main__':
    main()
