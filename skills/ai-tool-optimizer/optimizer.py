"""
提示词优化器
"""

import re
from typing import Dict, List, Any


class PromptOptimizer:
    """提示词优化器"""

    def __init__(self, config: Dict):
        """初始化优化器"""
        self.config = config

    def optimize(
        self,
        prompt: str,
        model: str = None,
        task_type: str = None
    ) -> Dict[str, Any]:
        """
        优化提示词

        Args:
            prompt: 原始提示词
            model: 目标模型
            task_type: 任务类型

        Returns:
            优化结果
        """
        original_token_count = self._count_tokens(prompt)

        # 应用优化规则
        optimized_prompt = prompt
        improvements = []

        # 优化规则1: 移除冗余内容
        optimized_prompt = self._remove_redundancy(optimized_prompt)
        if optimized_prompt != prompt:
            improvements.append("移除了冗余表述和重复内容")

        # 优化规则2: 简化表达
        optimized_prompt = self._simplify_expressions(optimized_prompt)
        if optimized_prompt != prompt:
            improvements.append("简化了复杂表达和句式")

        # 优化规则3: 添加明确约束
        optimized_prompt = self._add_constraints(optimized_prompt, task_type)
        if optimized_prompt != prompt:
            improvements.append("添加了明确的任务约束和输出格式要求")

        # 优化规则4: 结构化提示词
        optimized_prompt = self._structure_prompt(optimized_prompt)
        if optimized_prompt != prompt:
            improvements.append("使用了结构化的提示词格式")

        # 优化规则5: 优化上下文
        optimized_prompt = self._optimize_context(optimized_prompt)
        if optimized_prompt != prompt:
            improvements.append("优化了上下文信息的组织方式")

        optimized_token_count = self._count_tokens(optimized_prompt)
        token_reduction = (
            (original_token_count - optimized_token_count) / original_token_count * 100
            if original_token_count > 0 else 0
        )

        # 估算成本节省
        cost_savings = self._estimate_cost_savings(
            original_token_count,
            optimized_token_count,
            model
        )

        return {
            'original_prompt': prompt,
            'optimized_prompt': optimized_prompt,
            'improvements': improvements,
            'original_token_count': original_token_count,
            'optimized_token_count': optimized_token_count,
            'estimated_token_reduction': token_reduction,
            'estimated_cost_savings': cost_savings
        }

    def _count_tokens(self, text: str) -> int:
        """估算Token数量（简化版本）"""
        # 实际使用时可以用tiktoken库
        # 这里使用简化估算：中文约1字符=1.5token，英文约1词=1.3token
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        other_chars = len(text) - chinese_chars

        # 简化估算
        return int(chinese_chars * 1.5 + other_chars * 0.6)

    def _remove_redundancy(self, prompt: str) -> str:
        """移除冗余内容"""
        # 移除重复的短语
        lines = prompt.split('\n')
        seen_lines = set()
        unique_lines = []

        for line in lines:
            stripped = line.strip()
            if stripped and stripped not in seen_lines:
                seen_lines.add(stripped)
                unique_lines.append(line)

        return '\n'.join(unique_lines)

    def _simplify_expressions(self, prompt: str) -> str:
        """简化表达"""
        # 简化常见的冗余表达
        replacements = [
            (r'请你', '请'),
            (r'希望能够', '希望'),
            (r'尽量', ''),
            (r'尽可能', ''),
            (r'我们需要', '需要'),
            (r'我想让你', '请'),
            (r'帮我', ''),
        ]

        result = prompt
        for pattern, replacement in replacements:
            result = re.sub(pattern, replacement, result)

        return result.strip()

    def _add_constraints(self, prompt: str, task_type: str) -> str:
        """添加明确的约束"""
        constraints = []

        # 根据任务类型添加特定约束
        if task_type:
            if 'code' in task_type.lower():
                constraints.append("- 输出完整可运行的代码")
                constraints.append("- 添加必要的注释")

            elif 'writing' in task_type.lower():
                constraints.append("- 输出格式清晰，段落分明")
                constraints.append("- 使用简洁的表达")

            elif 'analysis' in task_type.lower():
                constraints.append("- 提供详细的分析过程")
                constraints.append("- 给出具体的数据和证据")

        # 通用约束
        if not ('格式' in prompt or 'format' in prompt.lower()):
            constraints.append("- 使用清晰的输出格式")

        # 添加约束到提示词
        if constraints:
            if prompt[-1] != '\n':
                prompt += '\n\n'
            prompt += '要求:\n' + '\n'.join(constraints)

        return prompt

    def _structure_prompt(self, prompt: str) -> str:
        """结构化提示词"""
        # 如果提示词已经结构化，返回原样
        if re.search(r'^#+\s|^\*\*|^- ', prompt, re.MULTILINE):
            return prompt

        # 尝试识别不同部分
        parts = {
            'task': [],
            'context': [],
            'requirements': []
        }

        lines = prompt.split('\n')
        current_section = 'task'

        for line in lines:
            stripped = line.strip()

            if not stripped:
                continue

            # 简单的启发式规则
            if any(keyword in stripped.lower() for keyword in ['背景', '语境', 'context']):
                current_section = 'context'
            elif any(keyword in stripped.lower() for keyword in ['要求', '需要', '请', '要求']):
                current_section = 'requirements'

            parts[current_section].append(line)

        # 重建结构化提示词
        structured = []

        if parts['task']:
            structured.append('## 任务')
            structured.extend(parts['task'])
            structured.append('')

        if parts['context']:
            structured.append('## 背景')
            structured.extend(parts['context'])
            structured.append('')

        if parts['requirements']:
            structured.append('## 要求')
            structured.extend(parts['requirements'])

        return '\n'.join(structured) if structured else prompt

    def _optimize_context(self, prompt: str) -> str:
        """优化上下文"""
        # 移除过长的上下文，只保留关键信息
        lines = prompt.split('\n')
        key_info = []

        for line in lines:
            stripped = line.strip()

            # 保留：问题、要求、关键数据
            if (any(keyword in stripped for keyword in ['?', '？', '如何', '怎么', '需要', '要求']) or
                re.search(r'\d+', stripped)):  # 包含数字的行可能包含关键数据
                key_info.append(line)

        # 如果过滤后内容太少，返回原样
        if len(key_info) < len(lines) * 0.5:
            return prompt

        return '\n'.join(key_info)

    def _estimate_cost_savings(
        self,
        original_tokens: int,
        optimized_tokens: int,
        model: str = None
    ) -> float:
        """估算成本节省"""
        if model not in self.config['models']:
            model = 'gpt-3.5-turbo'

        cost_per_1k = self.config['models'][model]['cost_per_1k_input']

        token_diff = original_tokens - optimized_tokens
        if token_diff <= 0:
            return 0.0

        return (token_diff / 1000) * cost_per_1k
