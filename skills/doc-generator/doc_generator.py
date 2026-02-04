#!/usr/bin/env python3
"""
文档自动生成器 - 从代码、注释和配置生成各种文档
"""

import os
import sys
import json
import re
import ast
import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

try:
    from jinja2 import Template
    HAS_JINJA2 = True
except ImportError:
    HAS_JINJA2 = False


@dataclass
class MethodInfo:
    """方法信息"""
    name: str
    doc: str
    params: List[str]
    returns: str
    is_private: bool


@dataclass
class ClassInfo:
    """类信息"""
    name: str
    doc: str
    methods: List[MethodInfo]
    is_private: bool


@dataclass
class FunctionInfo:
    """函数信息"""
    name: str
    doc: str
    params: List[str]
    returns: str
    is_private: bool


class DocGenerator:
    """文档生成器"""

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path) if config_path else {}

    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                return yaml.safe_load(f)
            else:
                return json.load(f)

    def generate_readme(self, project_name: str = '', description: str = '',
                        installation: str = '', usage: str = '',
                        features: List[str] = None, template: str = 'detailed',
                        output_path: Optional[str] = None) -> str:
        """生成README文档"""
        features = features or []

        if template == 'basic':
            readme = self._generate_basic_readme(project_name, description, installation, usage)
        elif template == 'detailed':
            readme = self._generate_detailed_readme(project_name, description, installation, usage, features)
        elif template == 'open_source':
            readme = self._generate_open_source_readme(project_name, description, installation, usage, features)
        elif template == 'commercial':
            readme = self._generate_commercial_readme(project_name, description, installation, usage, features)
        else:
            readme = self._generate_detailed_readme(project_name, description, installation, usage, features)

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(readme)

        return readme

    def _generate_basic_readme(self, project_name: str, description: str,
                                installation: str, usage: str) -> str:
        """生成基础版README"""
        return f"""# {project_name or 'Project'}

{description or 'Project description'}

## Installation

```
{installation or 'pip install project'}
```

## Usage

```
{usage or 'python -m project'}
```
"""

    def _generate_detailed_readme(self, project_name: str, description: str,
                                   installation: str, usage: str,
                                   features: List[str]) -> str:
        """生成详细版README"""
        features_html = '\n'.join([f'- {f}' for f in features]) if features else ''

        # 避免在f-string中使用反斜杠
        default_usage = 'from project import main\nmain()'

        return f"""# {project_name or 'Project'}

{description or 'Project description'}

## Features

{features_html or '- Feature 1\n- Feature 2\n- Feature 3'}

## Installation

```bash
{installation or 'pip install project'}
```

## Usage

```python
{usage or default_usage}
```

## License

MIT License
"""

    def _generate_open_source_readme(self, project_name: str, description: str,
                                     installation: str, usage: str,
                                     features: List[str]) -> str:
        """生成开源项目README"""
        features_html = '\n'.join([f'- {f}' for f in features]) if features else ''

        return f"""# {project_name or 'Project'}

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)

{description or 'Project description'}

## Features

{features_html or '- Feature 1\n- Feature 2\n- Feature 3'}

## Installation

```bash
{installation or 'pip install project'}
```

## Usage

```python
{usage or 'from project import main\nmain()'}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
"""

    def _generate_commercial_readme(self, project_name: str, description: str,
                                    installation: str, usage: str,
                                    features: List[str]) -> str:
        """生成商业项目README"""
        features_html = '\n'.join([f'- {f}' for f in features]) if features else ''

        return f"""# {project_name or 'Project'}

**Version:** 1.0.0

{description or 'Project description'}

## Features

{features_html or '- Feature 1\n- Feature 2\n- Feature 3'}

## Installation

```bash
{installation or 'pip install project'}
```

## Usage

```python
{usage or 'from project import main\nmain()'}
```

## Documentation

For detailed documentation, please visit our [Documentation Site](https://docs.example.com).

## Support

For support, please contact support@example.com

## License

Copyright © 2026 Company Name. All rights reserved.
"""

    def generate_api_doc(self, code_path: str, output_path: Optional[str] = None,
                        format: str = 'markdown', include_examples: bool = True,
                        include_auth: bool = False) -> str:
        """生成API文档"""
        if not os.path.exists(code_path):
            raise FileNotFoundError(f"Code file not found: {code_path}")

        # 分析Python代码
        if code_path.endswith('.py'):
            classes, functions = self._analyze_python_file(code_path)
        else:
            return f"# API Documentation\n\nFormat {format} not supported for {os.path.splitext(code_path)[1]}"

        # 生成文档
        doc = self._generate_api_doc_from_analysis(classes, functions, include_examples, include_auth)

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(doc)

        return doc

    def _analyze_python_file(self, file_path: str) -> tuple:
        """分析Python文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return [], []

        classes = []
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = self._extract_class_info(node)
                if class_info:
                    classes.append(class_info)
            elif isinstance(node, ast.FunctionDef) and not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree)):
                func_info = self._extract_function_info(node)
                if func_info:
                    functions.append(func_info)

        return classes, functions

    def _extract_class_info(self, node: ast.ClassDef) -> Optional[ClassInfo]:
        """提取类信息"""
        if node.name.startswith('_'):
            return None

        doc = ast.get_docstring(node) or 'No documentation'

        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self._extract_function_info(item)
                if method_info:
                    methods.append(method_info)

        return ClassInfo(
            name=node.name,
            doc=doc,
            methods=methods,
            is_private=node.name.startswith('_')
        )

    def _extract_function_info(self, node: ast.FunctionDef) -> Optional[FunctionInfo]:
        """提取函数信息"""
        if node.name.startswith('_'):
            return None

        doc = ast.get_docstring(node) or 'No documentation'

        params = [arg.arg for arg in node.args.args]

        returns = ''
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == 'returns':
                # 简化的返回类型提取
                pass

        return FunctionInfo(
            name=node.name,
            doc=doc,
            params=params,
            returns=returns,
            is_private=node.name.startswith('_')
        )

    def _generate_api_doc_from_analysis(self, classes: List[ClassInfo],
                                        functions: List[FunctionInfo],
                                        include_examples: bool,
                                        include_auth: bool) -> str:
        """从分析结果生成API文档"""
        doc = "# API Documentation\n\n"

        if include_auth:
            doc += "## Authentication\n\n"
            doc += "All API requests require authentication. Include your API key in the header:\n\n"
            doc += "```\nAuthorization: Bearer YOUR_API_KEY\n```\n\n"

        # 函数文档
        if functions:
            doc += "## Functions\n\n"

            for func in functions:
                doc += f"### {func.name}\n\n"
                doc += f"{func.doc}\n\n"

                if func.params:
                    doc += "**Parameters:**\n\n"
                    for param in func.params:
                        doc += f"- `{param}`\n"
                    doc += "\n"

                if func.returns:
                    doc += f"**Returns:** {func.returns}\n\n"

                if include_examples:
                    doc += "**Example:**\n\n"
                    doc += f"```python\nresult = {func.name}({', '.join(func.params) if func.params else ''})\n```\n\n"

                doc += "---\n\n"

        # 类文档
        if classes:
            doc += "## Classes\n\n"

            for cls in classes:
                doc += f"### {cls.name}\n\n"
                doc += f"{cls.doc}\n\n"

                if cls.methods:
                    doc += "**Methods:**\n\n"

                    for method in cls.methods:
                        doc += f"#### {method.name}\n\n"
                        doc += f"{method.doc}\n\n"

                        if method.params:
                            doc += "**Parameters:**\n\n"
                            for param in method.params:
                                doc += f"- `{param}`\n"
                            doc += "\n"

                        if include_examples:
                            doc += "**Example:**\n\n"
                            doc += f"```python\nobj = {cls.name}()\n"
                            doc += f"obj.{method.name}({', '.join(method.params) if method.params else ''})\n```\n\n"

                        doc += "---\n\n"

        return doc

    def generate_from_comments(self, code_path: str, output_path: Optional[str] = None,
                               include_private: bool = False) -> str:
        """从代码注释生成文档"""
        if not os.path.exists(code_path):
            raise FileNotFoundError(f"Code directory not found: {code_path}")

        doc = "# Code Documentation\n\n"

        if os.path.isfile(code_path):
            files = [code_path]
        else:
            files = []
            for root, dirs, filenames in os.walk(code_path):
                for filename in filenames:
                    if filename.endswith('.py'):
                        files.append(os.path.join(root, filename))

        for file_path in files:
            rel_path = os.path.relpath(file_path, code_path)
            doc += f"## File: {rel_path}\n\n"

            classes, functions = self._analyze_python_file(file_path)

            if classes:
                for cls in classes:
                    if include_private or not cls.is_private:
                        doc += f"### Class: {cls.name}\n\n"
                        doc += f"{cls.doc}\n\n"

                        if cls.methods:
                            for method in cls.methods:
                                if include_private or not method.is_private:
                                    doc += f"#### Method: {method.name}\n\n"
                                    doc += f"{method.doc}\n\n"

            if functions:
                for func in functions:
                    if include_private or not func.is_private:
                        doc += f"### Function: {func.name}\n\n"
                        doc += f"{func.doc}\n\n"

            doc += "---\n\n"

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(doc)

        return doc

    def generate_user_manual(self, title: str, chapters: List[Dict[str, str]],
                            output_path: Optional[str] = None) -> str:
        """生成用户手册"""
        doc = f"# {title}\n\n"

        for i, chapter in enumerate(chapters, 1):
            doc += f"## {i}. {chapter['title']}\n\n"
            doc += f"{chapter['content']}\n\n"
            doc += "---\n\n"

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(doc)

        return doc

    def generate_tech_doc(self, title: str, sections: List[Dict[str, str]],
                         output_path: Optional[str] = None) -> str:
        """生成技术文档"""
        doc = f"# {title}\n\n"

        for section in sections:
            doc += f"## {section['title']}\n\n"
            doc += f"{section['content']}\n\n"
            doc += "---\n\n"

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(doc)

        return doc

    def generate_openapi_doc(self, spec_path: str, output_path: Optional[str] = None) -> str:
        """从OpenAPI规范生成文档"""
        if not os.path.exists(spec_path):
            raise FileNotFoundError(f"OpenAPI spec file not found: {spec_path}")

        with open(spec_path, 'r', encoding='utf-8') as f:
            if spec_path.endswith('.yaml') or spec_path.endswith('.yml'):
                spec = yaml.safe_load(f)
            else:
                spec = json.load(f)

        doc = "# API Documentation (OpenAPI)\n\n"

        info = spec.get('info', {})
        doc += f"**Title:** {info.get('title', 'API')}\n\n"
        doc += f"**Version:** {info.get('version', '1.0.0')}\n\n"
        doc += f"**Description:** {info.get('description', 'No description')}\n\n"

        # 服务器信息
        servers = spec.get('servers', [])
        if servers:
            doc += "## Servers\n\n"
            for server in servers:
                doc += f"- {server.get('url', 'Unknown')}: {server.get('description', '')}\n"
            doc += "\n"

        # API端点
        paths = spec.get('paths', {})
        if paths:
            doc += "## Endpoints\n\n"

            for path, methods in paths.items():
                for method, details in methods.items():
                    summary = details.get('summary', 'No summary')
                    description = details.get('description', 'No description')

                    doc += f"### {method.upper()} {path}\n\n"
                    doc += f"**{summary}**\n\n"
                    doc += f"{description}\n\n"

                    # 参数
                    parameters = details.get('parameters', [])
                    if parameters:
                        doc += "**Parameters:**\n\n"
                        for param in parameters:
                            param_name = param.get('name', '')
                            param_type = param.get('schema', {}).get('type', 'string')
                            required = param.get('required', False)
                            doc += f"- `{param_name}` ({param_type}) {'(required)' if required else '(optional)'}\n"
                        doc += "\n"

                    # 响应
                    responses = details.get('responses', {})
                    if responses:
                        doc += "**Responses:**\n\n"
                        for status, response in responses.items():
                            description = response.get('description', 'No description')
                            doc += f"- {status}: {description}\n"
                        doc += "\n"

                    doc += "---\n\n"

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(doc)

        return doc

    def generate_from_config(self, config_path: str, output_path: Optional[str] = None) -> str:
        """从配置文件生成文档"""
        config = self._load_config(config_path)

        doc_config = config.get('document', {})
        output_config = config.get('output', {})
        sections = config.get('sections', [])

        doc = f"# {doc_config.get('title', 'Documentation')}\n\n"

        # 添加元信息
        if 'author' in doc_config:
            doc += f"**Author:** {doc_config['author']}\n\n"
        if 'version' in doc_config:
            doc += f"**Version:** {doc_config['version']}\n\n"

        doc += "---\n\n"

        # 处理各个部分
        for section in sections:
            section_type = section.get('type', '')

            if section_type == 'title':
                doc += f"# {section['content']}\n\n"
            elif section_type == 'description':
                doc += f"{section['content']}\n\n"
            elif section_type == 'installation':
                doc += "## Installation\n\n"
                doc += f"```bash\n{section.get('command', 'pip install')}\n```\n\n"
            elif section_type == 'usage':
                doc += "## Usage\n\n"
                doc += f"```python\n{section.get('code', '')}\n```\n\n"
            elif section_type == 'features':
                doc += "## Features\n\n"
                items = section.get('items', [])
                for item in items:
                    doc += f"- {item}\n"
                doc += "\n"
            elif section_type == 'api':
                code_path = section.get('path', '')
                if code_path and os.path.exists(code_path):
                    api_doc = self.generate_api_doc(code_path)
                    doc += api_doc + "\n\n"
            elif section_type == 'changelog':
                doc += "## Changelog\n\n"
                versions = section.get('versions', [])
                for version in versions:
                    doc += f"### {version['version']} ({version.get('date', '')})\n\n"
                    changes = version.get('changes', [])
                    for change in changes:
                        doc += f"- {change}\n"
                    doc += "\n"

            doc += "---\n\n"

        output_file = output_path or output_config.get('path', 'README.md')

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(doc)

        return doc

    def generate_index(self, docs: List[str], output_path: str) -> str:
        """生成文档索引"""
        doc = "# Documentation Index\n\n"

        for doc_file in docs:
            title = os.path.splitext(os.path.basename(doc_file))[0].replace('_', ' ').title()
            doc += f"- [{title}]({doc_file})\n"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(doc)

        return doc

    def generate_multi_format(self, config_path: str, formats: List[str]) -> List[str]:
        """生成多种格式的文档"""
        output_files = []

        for format in formats:
            if format == 'markdown':
                doc = self.generate_from_config(config_path)
                output_path = './docs/README.md'
            elif format == 'html':
                # 简化的HTML生成
                doc = self._generate_html_from_config(config_path)
                output_path = './docs/README.html'
            elif format == 'rst':
                # 简化的RST生成
                doc = self._generate_rst_from_config(config_path)
                output_path = './docs/README.rst'
            else:
                continue

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(doc)

            output_files.append(output_path)

        return output_files

    def _generate_html_from_config(self, config_path: str) -> str:
        """从配置生成HTML"""
        config = self._load_config(config_path)
        doc_config = config.get('document', {})

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{doc_config.get('title', 'Documentation')}</title>
</head>
<body>
    <h1>{doc_config.get('title', 'Documentation')}</h1>
"""

        # 简化实现，实际应用中需要更完整的HTML生成
        html += """
</body>
</html>"""

        return html

    def _generate_rst_from_config(self, config_path: str) -> str:
        """从配置生成RST"""
        config = self._load_config(config_path)
        doc_config = config.get('document', {})

        rst = f"{doc_config.get('title', 'Documentation')}\n"
        rst += "=" * len(doc_config.get('title', 'Documentation')) + "\n\n"

        # 简化实现
        return rst


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='文档自动生成器')
    parser.add_argument('action', choices=['readme', 'api', 'generate', 'all'])
    parser.add_argument('--name', help='项目名称')
    parser.add_argument('--code', help='代码路径')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--output', default='README.md', help='输出文件路径')
    parser.add_argument('--format', default='markdown', help='输出格式')

    args = parser.parse_args()

    generator = DocGenerator()

    if args.action == 'readme':
        readme = generator.generate_readme(
            project_name=args.name or 'MyProject',
            output_path=args.output
        )
        print(f'Generated: {args.output}')

    elif args.action == 'api':
        if not args.code:
            print('Error: --code is required for api action')
            sys.exit(1)

        doc = generator.generate_api_doc(
            code_path=args.code,
            output_path=args.output
        )
        print(f'Generated: {args.output}')

    elif args.action == 'generate':
        if not args.config:
            print('Error: --config is required for generate action')
            sys.exit(1)

        doc = generator.generate_from_config(args.config)
        print(f'Generated from config')

    elif args.action == 'all':
        if not args.config:
            print('Error: --config is required for all action')
            sys.exit(1)

        docs = generator.generate_multi_format(
            config_path=args.config,
            formats=['markdown', 'html', 'rst']
        )
        print(f'Generated {len(docs)} documents')


if __name__ == '__main__':
    main()
