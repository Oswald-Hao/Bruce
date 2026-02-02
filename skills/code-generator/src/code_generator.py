"""
Code Generator - 主类
"""

from typing import Optional, Dict, List, Any

try:
    from .completers import PythonCompleter, JavaScriptCompleter
    from .refactors import CodeRefactor, suggest_refactoring
    from .analyzers import CodeAnalyzer
except ImportError:
    # 如果相对导入失败，尝试直接导入（用于测试）
    import importlib.util
    import os

    def load_module(name, file_path):
        spec = importlib.util.spec_from_file_location(name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    src_dir = os.path.dirname(os.path.abspath(__file__))
    completers_module = load_module("completers", os.path.join(src_dir, "completers.py"))
    refactors_module = load_module("refactors", os.path.join(src_dir, "refactors.py"))
    analyzers_module = load_module("analyzers", os.path.join(src_dir, "analyzers.py"))

    PythonCompleter = completers_module.PythonCompleter
    JavaScriptCompleter = completers_module.JavaScriptCompleter
    CodeRefactor = refactors_module.CodeRefactor
    suggest_refactoring = refactors_module.suggest_refactoring
    CodeAnalyzer = analyzers_module.CodeAnalyzer


class CodeGenerator:
    """代码生成器主类"""

    def __init__(self):
        self.python_completer = PythonCompleter()
        self.js_completer = JavaScriptCompleter()
        self.refactor = CodeRefactor()
        self.analyzer = CodeAnalyzer()

    def complete_code(self, code: str, language: str = "python") -> Optional[str]:
        """智能代码补全

        Args:
            code: 当前已输入的代码
            language: 编程语言

        Returns:
            补全后的代码片段
        """
        language = language.lower()

        if language in ["python", "py"]:
            return self.python_completer.complete(code, language)
        elif language in ["javascript", "js"]:
            return self.js_completer.complete(code, language)
        else:
            return None

    def refactor_code(self, code: str, optimize_level: str = "medium") -> Dict[str, Any]:
        """代码重构

        Args:
            code: 要重构的代码
            optimize_level: 优化级别 (low, medium, high)

        Returns:
            重构结果字典
        """
        return self.refactor.refactor(code, optimize_level)

    def analyze_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """代码分析

        Args:
            code: 要分析的代码
            language: 编程语言

        Returns:
            分析结果字典
        """
        return self.analyzer.analyze(code, language)

    def get_suggestions(self, code: str, language: str = "python") -> List[str]:
        """获取代码补全建议

        Args:
            code: 当前代码
            language: 编程语言

        Returns:
            建议列表
        """
        language = language.lower()

        if language in ["python", "py"]:
            return self.python_completer.get_suggestions(code, language)
        elif language in ["javascript", "js"]:
            return self.js_completer.get_suggestions(code, language)
        else:
            return []

    def get_refactoring_suggestions(self, code: str) -> List[Dict[str, Any]]:
        """获取重构建议

        Args:
            code: 要分析的代码

        Returns:
            重构建议列表
        """
        return suggest_refactoring(code)

    def get_code_quality_score(self, code: str, language: str = "python") -> float:
        """获取代码质量分数

        Args:
            code: 要评分的代码
            language: 编程语言

        Returns:
            质量分数（0-100）
        """
        language = language.lower()

        if language in ["python", "py"]:
            return self.analyzer.get_score(code)
        else:
            return 0.0

    def generate_function(self, name: str, description: str, language: str = "python") -> str:
        """根据描述生成函数

        Args:
            name: 函数名
            description: 函数描述
            language: 编程语言

        Returns:
            生成的函数代码
        """
        # 简单的模板生成
        if language.lower() in ["python", "py"]:
            return f'''def {name}():
    """
    {description}
    """
    # TODO: Implement this function
    pass
'''
        elif language.lower() in ["javascript", "js"]:
            return f'''function {name}() {{
    /**
     * {description}
     */
    // TODO: Implement this function
}}
'''
        else:
            return f"# Language {language} not supported yet"

    def generate_class(self, name: str, description: str, language: str = "python") -> str:
        """根据描述生成类

        Args:
            name: 类名
            description: 类描述
            language: 编程语言

        Returns:
            生成的类代码
        """
        if language.lower() in ["python", "py"]:
            return f'''class {name}:
    """
    {description}
    """

    def __init__(self):
        """Initialize the class."""
        self._initialized = True

    def __str__(self):
        """String representation."""
        return f"{name}()"
'''
        elif language.lower() in ["javascript", "js"]:
            return f'''class {name} {{
    /**
     * {description}
     */
    constructor() {{
        this._initialized = true;
    }}

    toString() {{
        return "{name}()";
    }}
}}
'''
        else:
            return f"# Language {language} not supported yet"
