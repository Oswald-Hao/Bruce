"""
Code Generator - 代码生成优化器包
"""

from .code_generator import CodeGenerator
from .completers import PythonCompleter, JavaScriptCompleter
from .refactors import CodeRefactor, suggest_refactoring
from .analyzers import CodeAnalyzer

__version__ = "1.0.0"
__all__ = [
    "CodeGenerator",
    "PythonCompleter",
    "JavaScriptCompleter",
    "CodeRefactor",
    "suggest_refactoring",
    "CodeAnalyzer"
]
