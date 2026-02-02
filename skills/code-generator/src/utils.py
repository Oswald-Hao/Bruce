"""
工具函数
"""

import ast
import re
from typing import List, Dict, Any


def is_valid_python(code: str) -> bool:
    """检查代码是否是有效的Python代码"""
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False


def extract_indentation(line: str) -> str:
    """提取行首的缩进"""
    match = re.match(r'^(\s+)', line)
    return match.group(1) if match else ''


def get_code_indentation(code: str) -> int:
    """获取代码的基础缩进级别"""
    lines = [line for line in code.split('\n') if line.strip()]
    if not lines:
        return 0
    min_indent = min(len(extract_indentation(line)) for line in lines)
    return min_indent


def normalize_indentation(code: str, spaces: int = 4) -> str:
    """规范化代码缩进"""
    lines = code.split('\n')
    normalized = []
    for line in lines:
        if line.strip():
            current_indent = len(extract_indentation(line))
            new_indent = (current_indent // 4) * spaces
            normalized.append(' ' * new_indent + line.lstrip())
        else:
            normalized.append('')
    return '\n'.join(normalized)


def find_common_prefix(strings: List[str]) -> str:
    """找到字符串列表的共同前缀"""
    if not strings:
        return ''
    prefix = strings[0]
    for s in strings[1:]:
        while not s.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ''
    return prefix


def split_code_blocks(code: str) -> List[str]:
    """将代码分割成多个块"""
    lines = code.split('\n')
    blocks = []
    current_block = []
    current_indent = 0

    for line in lines:
        if line.strip():
            indent = len(extract_indentation(line))
            if indent == current_indent:
                current_block.append(line)
            elif indent > current_indent:
                # 缩进增加，是子块
                current_block.append(line)
                current_indent = indent
            else:
                # 缩进减少，新块开始
                if current_block:
                    blocks.append('\n'.join(current_block))
                current_block = [line]
                current_indent = indent
        elif current_block:
            current_block.append(line)

    if current_block:
        blocks.append('\n'.join(current_block))

    return blocks


def suggest_variable_name(expression: str) -> str:
    """根据表达式建议变量名"""
    # 简单的变量名建议逻辑
    if re.search(r'sum|total|add', expression, re.I):
        return 'total'
    elif re.search(r'count|len|length', expression, re.I):
        return 'count'
    elif re.search(r'max|maximum', expression, re.I):
        return 'max_value'
    elif re.search(r'min|minimum', expression, re.I):
        return 'min_value'
    elif re.search(r'avg|average', expression, re.I):
        return 'average'
    elif re.search(r'list|array', expression, re.I):
        return 'items'
    else:
        return 'result'


def calculate_complexity(code: str) -> Dict[str, Any]:
    """计算代码复杂度"""
    try:
        tree = ast.parse(code)
        complexity = 1  # 基础复杂度

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1

        return {
            'complexity': complexity,
            'is_simple': complexity <= 5,
            'is_complex': complexity > 10
        }
    except SyntaxError:
        return {
            'complexity': 0,
            'is_simple': False,
            'is_complex': False
        }
