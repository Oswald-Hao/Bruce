"""
模型选择器
"""

from typing import Dict, List, Any


class ModelSelector:
    """模型选择器"""

    def __init__(self, config: Dict):
        """初始化选择器"""
        self.config = config
        self.models = config['models']

        # 模型能力评分
        self.model_capabilities = {
            'gpt-4': {
                'code': 9.5,
                'writing': 9.0,
                'analysis': 9.5,
                'reasoning': 9.5,
                'creativity': 9.0
            },
            'gpt-3.5-turbo': {
                'code': 7.5,
                'writing': 7.0,
                'analysis': 7.0,
                'reasoning': 7.5,
                'creativity': 7.0
            },
            'claude-3-opus': {
                'code': 9.0,
                'writing': 9.5,
                'analysis': 9.5,
                'reasoning': 9.5,
                'creativity': 9.0
            }
        }

        # 任务类型映射
        self.task_types = {
            'code': ['代码', '编程', 'code', 'programming', 'debug', '写', '编写', '函数'],
            'writing': ['写作', '文案', 'writing', 'content', '文章'],
            'analysis': ['分析', '研究', 'analysis', 'research'],
            'reasoning': ['推理', '逻辑', 'reasoning', 'logic']
        }

    def suggest(
        self,
        task: str,
        budget: float = None,
        quality_priority: bool = False
    ) -> Dict[str, Any]:
        """
        推荐模型

        Args:
            task: 任务描述
            budget: 预算
            quality_priority: 是否优先考虑质量

        Returns:
            推荐结果
        """
        # 识别任务类型
        task_type = self._identify_task_type(task)

        # 计算每个模型的得分
        scored_models = []
        for model, info in self.models.items():
            score = self._calculate_model_score(
                model,
                task_type,
                budget,
                quality_priority
            )

            scored_models.append({
                'model': model,
                'score': score,
                'quality_score': self._get_quality_score(model, task_type),
                'cost_score': self._get_cost_score(model, budget),
                'estimated_cost': self._estimate_cost(model, task)
            })

        # 按得分排序
        scored_models.sort(key=lambda x: x['score'], reverse=True)

        recommended = scored_models[0]

        # 生成备选方案
        alternatives = scored_models[1:3] if len(scored_models) > 1 else []

        return {
            'task': task,
            'task_type': task_type,
            'recommended_model': recommended['model'],
            'reason': self._generate_reason(recommended, task_type),
            'estimated_cost': recommended['estimated_cost'],
            'quality_score': recommended['quality_score'],
            'alternatives': [
                {
                    'model': alt['model'],
                    'cost': alt['estimated_cost'],
                    'quality': alt['quality_score'],
                    'reason': self._generate_reason(alt, task_type)
                }
                for alt in alternatives
            ]
        }

    def _identify_task_type(self, task: str) -> str:
        """识别任务类型"""
        task_lower = task.lower()

        # 按优先级检查任务类型
        priority_order = ['code', 'analysis', 'reasoning', 'writing']

        for task_type in priority_order:
            if task_type in self.task_types:
                keywords = self.task_types[task_type]
                if any(keyword in task_lower for keyword in keywords):
                    return task_type

        return 'general'

    def _calculate_model_score(
        self,
        model: str,
        task_type: str,
        budget: float,
        quality_priority: bool
    ) -> float:
        """计算模型得分"""
        quality_score = self._get_quality_score(model, task_type)
        cost_score = self._get_cost_score(model, budget)

        if quality_priority:
            # 质量优先：90%质量 + 10%成本
            return quality_score * 0.9 + cost_score * 0.1
        else:
            # 平衡模式：50%质量 + 50%成本
            return quality_score * 0.5 + cost_score * 0.5

    def _get_quality_score(self, model: str, task_type: str) -> float:
        """获取质量评分"""
        if model not in self.model_capabilities:
            return 5.0

        capabilities = self.model_capabilities[model]

        if task_type in capabilities:
            return capabilities[task_type]
        else:
            # 使用平均分
            return sum(capabilities.values()) / len(capabilities)

    def _get_cost_score(self, model: str, budget: float) -> float:
        """获取成本评分（越高越好）"""
        if model not in self.models:
            return 5.0

        cost_per_1k = self.models[model]['cost_per_1k_input']

        if not budget:
            # 没有预算限制，根据成本排名
            max_cost = max([m['cost_per_1k_input'] for m in self.models.values()])
            min_cost = min([m['cost_per_1k_input'] for m in self.models.values()])

            if max_cost == min_cost:
                return 10.0

            # 成本越低分数越高
            return 10 - ((cost_per_1k - min_cost) / (max_cost - min_cost)) * 10
        else:
            # 有预算限制，计算是否在预算内
            estimated_cost = self._estimate_cost(model, "test")

            if estimated_cost <= budget:
                return 10.0
            else:
                # 超出预算，分数降低
                return 10.0 * (budget / estimated_cost)

    def _estimate_cost(self, model: str, task: str) -> float:
        """估算成本"""
        if model not in self.models:
            return 0.01

        # 估算Token数量（简化）
        task_length = len(task)
        estimated_tokens = task_length * 2  # 简化估算

        cost_per_1k = self.models[model]['cost_per_1k_input']
        cost = (estimated_tokens / 1000) * cost_per_1k

        return cost

    def _generate_reason(self, model_info: Dict, task_type: str) -> str:
        """生成推荐理由"""
        model = model_info['model']
        quality = model_info['quality_score']
        cost = model_info['estimated_cost']

        reasons = []

        if quality >= 8.5:
            reasons.append("质量优秀")
        elif quality >= 7.0:
            reasons.append("质量良好")

        if cost <= 0.001:
            reasons.append("成本极低")
        elif cost <= 0.005:
            reasons.append("成本适中")

        if task_type in ['code', 'analysis', 'reasoning']:
            reasons.append("适合复杂任务")

        if not reasons:
            reasons.append("综合性能最佳")

        return "，".join(reasons)
