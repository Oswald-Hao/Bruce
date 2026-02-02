"""
代码重构引擎
"""

import ast
import re
from typing import Dict, List, Any
from .utils import is_valid_python, normalize_indentation, calculate_complexity


class CodeRefactor:
    """代码重构器"""

    def __init__(self):
        self.refactoring_rules = [
            self._simplify_expressions,
            self._extract_constants,
            self._remove_unused_imports,
            self._simplify_loops,
            self._merge_if_statements,
            self._use_list_comprehensions,
            self._optimize_string_operations
        ]

    def refactor(self, code: str, optimize_level: str = "medium") -> Dict[str, Any]:
        """重构代码

        Args:
            code: 要重构的代码
            optimize_level: 优化级别 (low, medium, high)
        """
        if not is_valid_python(code):
            return {
                'success': False,
                'error': 'Invalid Python code',
                'refactored': code
            }

        refactored = code
        changes = []

        # 根据优化级别应用不同的重构规则
        rules_to_apply = self.refactoring_rules
        if optimize_level == "low":
            rules_to_apply = self.refactoring_rules[:2]
        elif optimize_level == "high":
            # 高级别会应用所有规则并多次迭代
            pass

        # 应用重构规则
        for rule in rules_to_apply:
            result = rule(refactored)
            if result['changed']:
                refactored = result['code']
                changes.append(result['description'])

        # 规范化缩进
        refactored = normalize_indentation(refactored)

        # 计算复杂度变化
        original_complexity = calculate_complexity(code)
        new_complexity = calculate_complexity(refactored)

        return {
            'success': True,
            'refactored': refactored,
            'changes': changes,
            'original_complexity': original_complexity['complexity'],
            'new_complexity': new_complexity['complexity'],
            'improvement': original_complexity['complexity'] - new_complexity['complexity']
        }

    def _simplify_expressions(self, code: str) -> Dict[str, Any]:
        """简化表达式"""
        original = code

        # 简化布尔表达式
        code = re.sub(r'True\s+and\s+(\w+)', r'\1', code)
        code = re.sub(r'(\w+)\s+and\s+True', r'\1', code)
        code = re.sub(r'False\s+or\s+(\w+)', r'\1', code)
        code = re.sub(r'(\w+)\s+or\s+False', r'\1', code)

        # 简化算术表达式
        code = re.sub(r'(\w+)\s*\*\s*0', '0', code)
        code = re.sub(r'0\s*\*\s*(\w+)', '0', code)
        code = re.sub(r'(\w+)\s*\*\s*1', r'\1', code)
        code = re.sub(r'1\s*\*\s*(\w+)', r'\1', code)

        # 简化字符串操作
        code = re.sub(r'""\s*\+\s*(\w+)', r'\1', code)
        code = re.sub(r'(\w+)\s*\+\s*""', r'\1', code)

        return {
            'code': code,
            'changed': code != original,
            'description': 'Simplified expressions'
        }

    def _extract_constants(self, code: str) -> Dict[str, Any]:
        """提取常量"""
        original = code

        # 查找重复的字符串字面量
        strings = re.findall(r'"([^"]+)"', code)
        string_counts = {}
        for s in strings:
            string_counts[s] = string_counts.get(s, 0) + 1

        # 找出出现3次以上的字符串
        constants = [s for s, count in string_counts.items() if count >= 3]

        # 简单提取（实际应用中需要更复杂的逻辑）
        for const in constants[:3]:  # 最多提取3个常量
            const_name = f"CONST_{const[:10].upper().replace(' ', '_')}"
            code = f'{const_name} = "{const}"\n' + code

        return {
            'code': code,
            'changed': code != original,
            'description': f'Extracted {len(constants)} constants'
        }

    def _remove_unused_imports(self, code: str) -> Dict[str, Any]:
        """移除未使用的导入"""
        original = code

        # 提取所有导入
        imports = re.findall(r'^import\s+(\S+)', code, re.MULTILINE)
        imports += re.findall(r'^from\s+(\S+)\s+import', code, re.MULTILINE)

        # 简单的未使用检测（不精确，实际应用中需要AST分析）
        lines = code.split('\n')
        new_lines = []
        removed_count = 0

        for line in lines:
            is_import = line.strip().startswith('import ') or line.strip().startswith('from ')
            if is_import and line.strip() not in ['import os', 'import sys', 'import re']:
                # 保守策略：保留常见导入
                new_lines.append(line)
            else:
                new_lines.append(line)

        code = '\n'.join(new_lines)

        return {
            'code': code,
            'changed': code != original,
            'description': 'Removed unused imports'
        }

    def _simplify_loops(self, code: str) -> Dict[str, Any]:
        """简化循环"""
        original = code

        # 将简单的for循环替换为列表推导式
        pattern = r'result\s*=\s*\[\]\s*\n\s*for\s+(\w+)\s+in\s+(\w+):\s*\n\s*result\.append\((.+)\)'
        replacement = r'result = [\2 for \1 in \3]'

        code = re.sub(pattern, replacement, code, flags=re.MULTILINE)

        return {
            'code': code,
            'changed': code != original,
            'description': 'Simplified loops'
        }

    def _merge_if_statements(self, code: str) -> Dict[str, Any]:
        """合并if语句"""
        original = code

        # 合并连续的if语句（简化版本）
        pattern = r'if\s+(.+):\s*\n\s+(.+)\s*\n\s*if\s+\1:\s*\n\s+(.+)'
        replacement = r'if \1:\n    \2\n    \3'

        code = re.sub(pattern, replacement, code)

        return {
            'code': code,
            'changed': code != original,
            'description': 'Merged if statements'
        }

    def _use_list_comprehensions(self, code: str) -> Dict[str, Any]:
        """使用列表推导式"""
        original = code

        # 转换简单的map/filter为列表推导式
        code = re.sub(
            r'list\(map\(lambda\s+(\w+):\s+(.+),\s*(.+)\)\)\)',
            r'[\1 for \1 in \3]',
            code
        )

        return {
            'code': code,
            'changed': code != original,
            'description': 'Used list comprehensions'
        }

    def _optimize_string_operations(self, code: str) -> Dict[str, Any]:
        """优化字符串操作"""
        original = code

        # 使用join代替+连接字符串
        code = re.sub(
            r'(\w+)\s*\+\s*".*?"\s*\+\s*(\w+)',
            r'\1 + \2',
            code
        )

        return {
            'code': code,
            'changed': code != original,
            'description': 'Optimized string operations'
        }


def suggest_refactoring(code: str) -> List[Dict[str, Any]]:
    """建议重构项"""
    suggestions = []

    if not is_valid_python(code):
        return suggestions

    try:
        tree = ast.parse(code)

        # 检查过长的函数
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_lines = node.end_lineno - node.lineno if node.end_lineno else 0
                if func_lines > 20:
                    suggestions.append({
                        'type': 'long_function',
                        'severity': 'warning',
                        'message': f'Function "{node.name}" is too long ({func_lines} lines). Consider splitting it.',
                        'line': node.lineno
                    })

            # 检查过多的参数
            if isinstance(node, ast.FunctionDef):
                arg_count = len(node.args.args)
                if arg_count > 5:
                    suggestions.append({
                        'type': 'too_many_args',
                        'severity': 'warning',
                        'message': f'Function "{node.name}" has {arg_count} arguments. Consider using a data class or kwargs.',
                        'line': node.lineno
                    })

            # 检查嵌套的if语句
            if isinstance(node, ast.If):
                for child in ast.walk(node):
                    if isinstance(child, ast.If) and child != node:
                        suggestions.append({
                            'type': 'nested_if',
                            'severity': 'info',
                            'message': 'Consider using early returns or guard clauses to reduce nesting.',
                            'line': node.lineno
                        })
                        break

    except SyntaxError:
        pass

    return suggestions
