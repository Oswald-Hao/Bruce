#!/usr/bin/env python3
"""
文档自动生成器的测试用例
"""

import sys
import os
import tempfile
import shutil

# 添加技能目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from doc_generator import DocGenerator


def test_basic_readme_generation():
    """测试基础README生成"""
    print("测试1: 基础README生成...")

    generator = DocGenerator()
    readme = generator.generate_readme(
        project_name='TestProject',
        description='Test Description',
        installation='pip install testproject',
        usage='from testproject import main',
        template='basic'
    )

    assert 'TestProject' in readme
    assert 'Test Description' in readme
    assert 'pip install testproject' in readme
    assert 'from testproject import main' in readme
    assert '## Installation' in readme
    assert '## Usage' in readme

    print("✅ 基础README生成测试通过")


def test_detailed_readme_generation():
    """测试详细README生成"""
    print("测试2: 详细README生成...")

    generator = DocGenerator()
    readme = generator.generate_readme(
        project_name='DetailedProject',
        description='Detailed Description',
        installation='pip install detailedproject',
        usage='from detailedproject import main',
        features=['Feature 1', 'Feature 2', 'Feature 3'],
        template='detailed'
    )

    assert 'DetailedProject' in readme
    assert 'Detailed Description' in readme
    assert '## Features' in readme
    assert 'Feature 1' in readme
    assert 'Feature 2' in readme
    assert 'Feature 3' in readme

    print("✅ 详细README生成测试通过")


def test_open_source_readme_generation():
    """测试开源项目README生成"""
    print("测试3: 开源项目README生成...")

    generator = DocGenerator()
    readme = generator.generate_readme(
        project_name='OpenSourceProject',
        description='Open Source Description',
        template='open_source'
    )

    assert 'OpenSourceProject' in readme
    assert 'License' in readme
    assert 'Contributing' in readme
    assert 'MIT License' in readme
    assert 'README.md' not in readme  # 应该没有这个内容

    print("✅ 开源项目README生成测试通过")


def test_commercial_readme_generation():
    """测试商业项目README生成"""
    print("测试4: 商业项目README生成...")

    generator = DocGenerator()
    readme = generator.generate_readme(
        project_name='CommercialProject',
        description='Commercial Description',
        template='commercial'
    )

    assert 'CommercialProject' in readme
    assert 'Version: 1.0.0' in readme or 'Version' in readme
    assert 'Documentation' in readme
    assert 'Support' in readme
    assert 'Copyright' in readme

    print("✅ 商业项目README生成测试通过")


def test_api_doc_generation():
    """测试API文档生成"""
    print("测试5: API文档生成...")

    # 创建临时Python文件
    temp_dir = tempfile.mkdtemp()

    try:
        code_file = os.path.join(temp_dir, 'test_api.py')

        code = '''
def add(a, b):
    """Add two numbers."""
    return a + b

def multiply(a, b):
    """Multiply two numbers."""
    return a * b

class Calculator:
    """A simple calculator class."""

    def __init__(self):
        """Initialize the calculator."""
        self.value = 0

    def add(self, x):
        """Add value to calculator."""
        self.value += x

    def get_value(self):
        """Get current value."""
        return self.value
'''

        with open(code_file, 'w') as f:
            f.write(code)

        generator = DocGenerator()
        doc = generator.generate_api_doc(code_path=code_file)

        assert '# API Documentation' in doc
        assert 'add' in doc
        assert 'multiply' in doc
        assert 'Calculator' in doc
        assert 'Add two numbers' in doc

        print("✅ API文档生成测试通过")

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)


def test_user_manual_generation():
    """测试用户手册生成"""
    print("测试6: 用户手册生成...")

    generator = DocGenerator()
    manual = generator.generate_user_manual(
        title='User Manual',
        chapters=[
            {'title': 'Getting Started', 'content': 'Installation guide...'},
            {'title': 'Basic Usage', 'content': 'How to use...'},
            {'title': 'Advanced Features', 'content': 'Advanced usage...'}
        ]
    )

    assert '# User Manual' in manual
    assert '## 1. Getting Started' in manual
    assert '## 2. Basic Usage' in manual
    assert '## 3. Advanced Features' in manual
    assert 'Installation guide...' in manual

    print("✅ 用户手册生成测试通过")


def test_tech_doc_generation():
    """测试技术文档生成"""
    print("测试7: 技术文档生成...")

    generator = DocGenerator()
    doc = generator.generate_tech_doc(
        title='Architecture Documentation',
        sections=[
            {'title': 'Overview', 'content': 'System overview...'},
            {'title': 'Components', 'content': 'Component descriptions...'},
            {'title': 'API', 'content': 'API reference...'}
        ]
    )

    assert '# Architecture Documentation' in doc
    assert '## Overview' in doc
    assert '## Components' in doc
    assert '## API' in doc
    assert 'System overview...' in doc

    print("✅ 技术文档生成测试通过")


def test_openapi_doc_generation():
    """测试OpenAPI文档生成"""
    print("测试8: OpenAPI文档生成...")

    # 创建临时OpenAPI规范文件
    temp_dir = tempfile.mkdtemp()

    try:
        spec_file = os.path.join(temp_dir, 'openapi.yaml')

        spec = '''
openapi: 3.0.0
info:
  title: Test API
  version: 1.0.0
  description: Test API description
servers:
  - url: https://api.example.com/v1
    description: Production server
paths:
  /users:
    get:
      summary: Get users
      description: Get all users
      responses:
        '200':
          description: Success
'''

        with open(spec_file, 'w') as f:
            f.write(spec)

        generator = DocGenerator()
        doc = generator.generate_openapi_doc(spec_path=spec_file)

        assert '# API Documentation' in doc
        assert 'Test API' in doc
        assert '1.0.0' in doc
        assert 'GET /users' in doc
        assert 'Get users' in doc

        print("✅ OpenAPI文档生成测试通过")

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)


def test_config_based_generation():
    """测试基于配置的生成"""
    print("测试9: 基于配置的生成...")

    # 创建临时配置文件
    temp_dir = tempfile.mkdtemp()

    try:
        config_file = os.path.join(temp_dir, 'doc_config.yaml')

        config = '''
document:
  title: "Configured Documentation"
  author: "Test Author"
  version: "1.0.0"

output:
  format: markdown
  path: "./README.md"

sections:
  - type: title
    content: "Introduction"

  - type: description
    content: "This is a configured documentation."

  - type: installation
    command: "pip install myproject"

  - type: usage
    code: "from myproject import main"

  - type: features
    items:
      - Feature 1
      - Feature 2
'''

        with open(config_file, 'w') as f:
            f.write(config)

        generator = DocGenerator()
        doc = generator.generate_from_config(config_path=config_file)

        assert 'Configured Documentation' in doc
        assert 'Test Author' in doc
        assert 'Introduction' in doc
        assert 'This is a configured documentation' in doc
        assert 'pip install myproject' in doc
        assert 'from myproject import main' in doc
        assert 'Feature 1' in doc

        print("✅ 基于配置的生成测试通过")

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)


def test_file_output():
    """测试文件输出"""
    print("测试10: 文件输出...")

    # 创建临时目录
    temp_dir = tempfile.mkdtemp()

    try:
        generator = DocGenerator()
        output_path = os.path.join(temp_dir, 'test.md')

        readme = generator.generate_readme(
            project_name='TestOutput',
            output_path=output_path
        )

        assert os.path.exists(output_path)

        with open(output_path, 'r') as f:
            content = f.read()
            assert 'TestOutput' in content

        print("✅ 文件输出测试通过")

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)


def test_code_comment_analysis():
    """测试代码注释分析"""
    print("测试11: 代码注释分析...")

    # 创建临时Python文件
    temp_dir = tempfile.mkdtemp()

    try:
        code_file = os.path.join(temp_dir, 'test_code.py')

        code = '''
def public_function():
    """This is a public function."""
    pass

def _private_function():
    """This is a private function."""
    pass

class PublicClass:
    """This is a public class."""

    def public_method(self):
        """Public method."""
        pass

    def _private_method(self):
        """Private method."""
        pass
'''

        with open(code_file, 'w') as f:
            f.write(code)

        generator = DocGenerator()
        doc = generator.generate_from_comments(code_path=code_file, include_private=False)

        assert '# Code Documentation' in doc
        assert 'public_function' in doc
        assert 'PublicClass' in doc
        assert 'public_method' in doc

        # 私有函数不应该出现在文档中
        assert '_private_function' not in doc
        assert '_private_method' not in doc

        print("✅ 代码注释分析测试通过")

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)


def test_index_generation():
    """测试索引生成"""
    print("测试12: 索引生成...")

    # 创建临时目录
    temp_dir = tempfile.mkdtemp()

    try:
        # 创建一些文档文件
        doc1 = os.path.join(temp_dir, 'api.md')
        doc2 = os.path.join(temp_dir, 'user_guide.md')

        with open(doc1, 'w') as f:
            f.write('API Documentation')
        with open(doc2, 'w') as f:
            f.write('User Guide')

        generator = DocGenerator()
        index_path = os.path.join(temp_dir, 'INDEX.md')

        index = generator.generate_index(
            docs=['api.md', 'user_guide.md'],
            output_path=index_path
        )

        assert '# Documentation Index' in index
        assert '[Api](api.md)' in index
        assert '[User Guide](user_guide.md)' in index
        assert os.path.exists(index_path)

        print("✅ 索引生成测试通过")

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)


def test_multi_format_generation():
    """测试多格式生成"""
    print("测试13: 多格式生成...")

    # 创建临时目录和配置文件
    temp_dir = tempfile.mkdtemp()

    try:
        config_file = os.path.join(temp_dir, 'config.yaml')

        config = '''
document:
  title: "Multi Format Test"

sections:
  - type: title
    content: "Test"
  - type: description
    content: "Test description"
'''

        with open(config_file, 'w') as f:
            f.write(config)

        generator = DocGenerator()
        docs = generator.generate_multi_format(
            config_path=config_file,
            formats=['markdown', 'html', 'rst']
        )

        assert len(docs) == 3
        assert all(os.path.exists(doc) for doc in docs)

        print("✅ 多格式生成测试通过")

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)


def test_changelog_generation():
    """测试变更日志生成"""
    print("测试14: 变更日志生成...")

    # 创建临时配置文件
    temp_dir = tempfile.mkdtemp()

    try:
        config_file = os.path.join(temp_dir, 'config.yaml')

        config = '''
document:
  title: "Project Docs"

sections:
  - type: changelog
    versions:
      - version: "1.0.0"
        date: "2026-01-01"
        changes:
          - Initial release
          - Basic features
      - version: "0.9.0"
        date: "2025-12-01"
        changes:
          - Beta release
'''

        with open(config_file, 'w') as f:
            f.write(config)

        generator = DocGenerator()
        doc = generator.generate_from_config(config_path=config_file)

        assert '## Changelog' in doc
        assert '### 1.0.0 (2026-01-01)' in doc
        assert '### 0.9.0 (2025-12-01)' in doc
        assert 'Initial release' in doc
        assert 'Beta release' in doc

        print("✅ 变更日志生成测试通过")

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)


def test_empty_defaults():
    """测试空值默认处理"""
    print("测试15: 空值默认处理...")

    generator = DocGenerator()
    readme = generator.generate_readme()

    # 应该使用默认值而不报错
    assert '# Project' in readme or '#' in readme
    assert '## Installation' in readme
    assert '## Usage' in readme

    print("✅ 空值默认处理测试通过")


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("开始测试文档自动生成器")
    print("=" * 60)

    tests = [
        test_basic_readme_generation,
        test_detailed_readme_generation,
        test_open_source_readme_generation,
        test_commercial_readme_generation,
        test_api_doc_generation,
        test_user_manual_generation,
        test_tech_doc_generation,
        test_openapi_doc_generation,
        test_config_based_generation,
        test_file_output,
        test_code_comment_analysis,
        test_index_generation,
        test_multi_format_generation,
        test_changelog_generation,
        test_empty_defaults,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            failed += 1
            print(f"❌ 测试失败: {test.__name__}")
            print(f"   错误: {e}")
        except Exception as e:
            failed += 1
            print(f"❌ 测试异常: {test.__name__}")
            print(f"   错误: {e}")

    print("=" * 60)
    print(f"测试完成: {passed} 通过, {failed} 失败")
    print("=" * 60)

    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
