"""
代码分析引擎
"""

import ast
import re
from typing import Dict, List, Any


def is_valid_python(code: str) -> bool:
    """检查代码是否是有效的Python代码"""
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False


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


class CodeAnalyzer:
    """代码分析器"""

    def __init__(self):
        pass

    def analyze(self, code: str, language: str = "python") -> Dict[str, Any]:
        """分析代码

        Returns:
            包含代码质量指标和改进建议的字典
        """
        if language.lower() != "python":
            return {
                'language': language,
                'supported': False,
                'error': f'Language {language} is not supported yet'
            }

        if not is_valid_python(code):
            return {
                'language': language,
                'supported': True,
                'valid': False,
                'error': 'Invalid Python syntax'
            }

        result = {
            'language': language,
            'supported': True,
            'valid': True,
            'metrics': self._calculate_metrics(code),
            'issues': self._find_issues(code),
            'suggestions': self._generate_suggestions(code),
            'complexity': calculate_complexity(code)
        }

        return result

    def _calculate_metrics(self, code: str) -> Dict[str, Any]:
        """计算代码指标"""
        lines = code.split('\n')
        non_empty_lines = [l for l in lines if l.strip()]
        comment_lines = [l for l in lines if l.strip().startswith('#')]

        try:
            tree = ast.parse(code)

            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]

            total_lines = len(lines)
            code_lines = len(non_empty_lines) - len(comment_lines)
            docstring_lines = self._count_docstrings(tree)

            return {
                'total_lines': total_lines,
                'code_lines': code_lines,
                'comment_lines': len(comment_lines),
                'docstring_lines': docstring_lines,
                'blank_lines': total_lines - len(non_empty_lines),
                'function_count': len(functions),
                'class_count': len(classes),
                'import_count': len(imports),
                'avg_function_length': sum(self._get_function_length(f) for f in functions) / len(functions) if functions else 0
            }
        except SyntaxError:
            return {
                'total_lines': len(lines),
                'code_lines': len(non_empty_lines),
                'comment_lines': len(comment_lines),
                'blank_lines': len(lines) - len(non_empty_lines),
                'function_count': 0,
                'class_count': 0,
                'import_count': 0,
                'avg_function_length': 0
            }

    def _count_docstrings(self, tree: ast.AST) -> int:
        """计算文档字符串行数"""
        docstring_lines = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                if ast.get_docstring(node):
                    docstring_lines += 1
        return docstring_lines

    def _get_function_length(self, func: ast.FunctionDef) -> int:
        """获取函数长度"""
        if func.end_lineno and func.lineno:
            return func.end_lineno - func.lineno
        return 0

    def _find_issues(self, code: str) -> List[Dict[str, Any]]:
        """查找代码问题"""
        issues = []

        try:
            tree = ast.parse(code)

            # 检查未使用的导入（简化版）
            import_names = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        import_names.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        import_names.add(node.module.split('.')[0])

            # 检查太长的行
            lines = code.split('\n')
            for i, line in enumerate(lines, 1):
                if len(line) > 100:
                    issues.append({
                        'type': 'line_too_long',
                        'severity': 'warning',
                        'line': i,
                        'message': f'Line {i} is too long ({len(line)} characters, max 100)'
                    })

            # 检查未使用的变量（简化版）
            defined_vars = set()
            used_vars = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            defined_vars.add(target.id)
                elif isinstance(node, ast.Name):
                    used_vars.add(node.id)

            unused_vars = defined_vars - used_vars - {'self', 'cls', '_'}
            for var in unused_vars:
                issues.append({
                    'type': 'unused_variable',
                    'severity': 'info',
                    'message': f'Variable "{var}" is assigned but never used'
                })

        except SyntaxError:
            pass

        return issues

    def _generate_suggestions(self, code: str) -> List[Dict[str, Any]]:
        """生成改进建议"""
        suggestions = []

        try:
            tree = ast.parse(code)

            # 建议添加类型注解
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not node.returns:
                        suggestions.append({
                            'type': 'type_hints',
                            'severity': 'info',
                            'message': f'Consider adding return type annotation to function "{node.name}"',
                            'line': node.lineno
                        })

                    for arg in node.args.args:
                        if not arg.annotation:
                            suggestions.append({
                                'type': 'type_hints',
                                'severity': 'info',
                                'message': f'Consider adding type annotation for argument "{arg.arg}" in function "{node.name}"',
                                'line': node.lineno
                            })

            # 建议使用列表推导式
            for node in ast.walk(tree):
                if isinstance(node, ast.For):
                    parent = self._get_parent(tree, node)
                    if parent and isinstance(parent, ast.Expr):
                        suggestions.append({
                            'type': 'list_comprehension',
                            'severity': 'info',
                            'message': 'Consider using list comprehension instead of loop with append',
                            'line': node.lineno
                        })

        except SyntaxError:
            pass

        return suggestions

    def _get_parent(self, tree: ast.AST, node: ast.AST) -> ast.AST:
        """获取节点的父节点（简化版）"""
        # 实际应用中需要更复杂的遍历
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                if child == node:
                    return parent
        return None

    def get_score(self, code: str) -> float:
        """获取代码质量分数（0-100）"""
        if not is_valid_python(code):
            return 0.0

        result = self.analyze(code)
        metrics = result.get('metrics', {})
        issues = result.get('issues', [])

        # 基础分
        score = 100.0

        # 根据问题扣分
        for issue in issues:
            if issue.get('severity') == 'error':
                score -= 10
            elif issue.get('severity') == 'warning':
                score -= 5
            elif issue.get('severity') == 'info':
                score -= 2

        # 根据指标调整
        avg_func_len = metrics.get('avg_function_length', 0)
        if avg_func_len > 50:
            score -= 10
        elif avg_func_len > 30:
            score -= 5

        comment_ratio = metrics.get('comment_lines', 0) / max(metrics.get('code_lines', 1), 1)
        if comment_ratio < 0.1:
            score -= 5
        elif comment_ratio > 0.3:
            score += 5  # 良好的注释比例

        return max(0.0, min(100.0, score))
