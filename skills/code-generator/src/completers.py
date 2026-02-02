"""
代码补全引擎
"""

import re
import ast
from typing import Optional, List, Dict, Any


class PythonCompleter:
    """Python代码补全器"""

    def __init__(self):
        self.common_patterns = {
            'def': ['def {name}({args}):\n    return {expr}\n'],
            'class': ['class {name}:\n    def __init__(self):\n        pass\n'],
            'for': ['for {item} in {iterable}:\n    pass\n'],
            'if': ['if {condition}:\n    pass\n'],
            'ifelse': ['if {condition}:\n    pass\nelse:\n    pass\n'],
            'try': ['try:\n    pass\nexcept Exception as e:\n    pass\n'],
            'with': ['with {context} as {name}:\n    pass\n'],
        }

    def complete(self, code: str, language: str = "python") -> Optional[str]:
        """补全代码"""
        if language.lower() != "python":
            return None

        # 去除首尾空白
        code = code.strip()

        # 尝试不同的补全策略
        strategies = [
            self._complete_function_definition,
            self._complete_class_definition,
            self._complete_loop,
            self._complete_condition,
            self._complete_context_manager,
            self._complete_return_statement,
            self._complete_expression
        ]

        for strategy in strategies:
            completion = strategy(code)
            if completion:
                return completion

        return None

    def _complete_function_definition(self, code: str) -> Optional[str]:
        """补全函数定义"""
        match = re.match(r'def\s+(\w+)\s*\(([^)]*)\):?\s*$', code)
        if match:
            func_name = match.group(1)
            # 根据函数名推断返回类型
            if 'get_' in func_name or 'find_' in func_name:
                return '    return None'
            elif 'is_' in func_name or 'has_' in func_name:
                return '    return False'
            elif 'set_' in func_name or 'add_' in func_name or 'update_' in func_name:
                return '    pass'
            else:
                return '    pass'

        # 检查是否是函数定义的中间状态
        if code.startswith('def ') and '(' in code:
            return ':\n    pass'

        return None

    def _complete_class_definition(self, code: str) -> Optional[str]:
        """补全类定义"""
        if code.startswith('class ') and not code.endswith(':'):
            return ':\n    def __init__(self):\n        pass'

        return None

    def _complete_loop(self, code: str) -> Optional[str]:
        """补全循环语句"""
        # for循环
        match = re.match(r'for\s+(\w+)\s+in\s+(\w+):\s*$', code)
        if match:
            return '    pass'

        if code.startswith('for ') and not code.endswith(':'):
            return ':\n    pass'

        # while循环
        match = re.match(r'while\s+(.+):\s*$', code)
        if match:
            return '    pass'

        if code.startswith('while ') and not code.endswith(':'):
            return ':\n    pass'

        return None

    def _complete_condition(self, code: str) -> Optional[str]:
        """补全条件语句"""
        # if语句
        if code.startswith('if ') and not code.endswith(':'):
            return ':\n    pass'

        # elif语句
        if code.startswith('elif ') and not code.endswith(':'):
            return ':\n    pass'

        # else语句
        if code.strip() == 'else':
            return ':\n    pass'

        return None

    def _complete_context_manager(self, code: str) -> Optional[str]:
        """补全上下文管理器"""
        if code.startswith('with ') and not code.endswith(':'):
            return ':\n    pass'

        return None

    def _complete_return_statement(self, code: str) -> Optional[str]:
        """补全return语句"""
        if code.strip().startswith('return ') and code.strip() == 'return':
            return ' None'

        return None

    def _complete_expression(self, code: str) -> Optional[str]:
        """补全表达式"""
        # 如果代码以操作符结尾，尝试补全
        if code.endswith(('=', '+', '-', '*', '/', '%')):
            return ' value'

        # 如果代码是变量赋值
        match = re.match(r'(\w+)\s*=\s*$', code)
        if match:
            var_name = match.group(1)
            if 'list' in var_name.lower():
                return ' []'
            elif 'dict' in var_name.lower() or 'map' in var_name.lower():
                return ' {}'
            elif 'str' in var_name.lower():
                return ' ""'
            elif 'bool' in var_name.lower():
                return ' False'
            else:
                return ' None'

        return None

    def get_suggestions(self, code: str, language: str = "python") -> List[str]:
        """获取补全建议"""
        suggestions = []

        # 基于关键字的建议
        if language.lower() == "python":
            keywords = ['def ', 'class ', 'if ', 'for ', 'while ', 'try:']
            for kw in keywords:
                if code.endswith(kw[:-1]) or code.endswith(kw):
                    suggestions.append(kw + code[len(kw):])

        return suggestions


class JavaScriptCompleter:
    """JavaScript代码补全器"""

    def complete(self, code: str, language: str = "javascript") -> Optional[str]:
        """补全JavaScript代码"""
        if language.lower() != "javascript" and language.lower() != "js":
            return None

        code = code.strip()

        # 函数定义
        if code.startswith('function ') and not code.endswith('{'):
            return '{\n    \n}'

        # 箭头函数
        if '=>' in code and not code.endswith('{'):
            return ' {\n    \n}'

        # if语句
        if code.startswith('if ') and not code.endswith('{'):
            return '{\n    \n}'

        # for循环
        if code.startswith('for ') and not code.endswith('{'):
            return '{\n    \n}'

        return None
