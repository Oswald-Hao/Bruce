"""
Token使用分析器
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any


class TokenAnalyzer:
    """Token使用分析器"""

    def __init__(self, config: Dict):
        """初始化分析器"""
        self.config = config
        self.usage_db = config['storage']['usage_db']

    def analyze(self, file_path: str = None, days: int = 7) -> Dict[str, Any]:
        """
        分析Token使用

        Args:
            file_path: 使用日志文件
            days: 统计天数

        Returns:
            分析结果
        """
        # 加载使用数据
        usage_data = self._load_usage_data(file_path)

        # 过滤指定天数的数据
        cutoff_time = datetime.now() - timedelta(days=days)
        recent_data = [
            record for record in usage_data
            if datetime.fromisoformat(record['timestamp']) > cutoff_time
        ]

        if not recent_data:
            return {
                'total_requests': 0,
                'total_tokens': 0,
                'avg_tokens_per_request': 0,
                'total_cost': 0,
                'daily_cost': 0,
                'by_model': {},
                'potential_savings': 0
            }

        # 统计数据
        total_requests = len(recent_data)
        total_tokens = sum([r.get('tokens', 0) for r in recent_data])
        total_cost = sum([r.get('cost', 0) for r in recent_data])
        avg_tokens = total_tokens / total_requests if total_requests > 0 else 0

        # 按模型统计
        by_model = {}
        for record in recent_data:
            model = record.get('model', 'unknown')
            if model not in by_model:
                by_model[model] = {
                    'requests': 0,
                    'tokens': 0,
                    'cost': 0
                }

            by_model[model]['requests'] += 1
            by_model[model]['tokens'] += record.get('tokens', 0)
            by_model[model]['cost'] += record.get('cost', 0)

        # 计算日均成本
        daily_cost = total_cost / days

        # 计算潜在节省（通过缓存）
        potential_savings = self._calculate_potential_savings(recent_data)

        return {
            'total_requests': total_requests,
            'total_tokens': total_tokens,
            'avg_tokens_per_request': avg_tokens,
            'total_cost': total_cost,
            'daily_cost': daily_cost,
            'by_model': by_model,
            'potential_savings': potential_savings
        }

    def _load_usage_data(self, file_path: str = None) -> List[Dict]:
        """加载使用数据"""
        if file_path and os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        # 尝试加载默认数据库
        if os.path.exists(self.usage_db):
            with open(self.usage_db, 'r', encoding='utf-8') as f:
                return json.load(f)

        # 返回示例数据
        return self._generate_sample_data()

    def _generate_sample_data(self) -> List[Dict]:
        """生成示例数据"""
        import random
        from datetime import datetime, timedelta

        models = ['gpt-3.5-turbo', 'gpt-4', 'claude-3-opus']
        data = []

        for i in range(100):
            model = random.choice(models)
            timestamp = (datetime.now() - timedelta(hours=random.randint(0, 168))).isoformat()
            tokens = random.randint(500, 5000)

            # 计算成本
            if model in self.config['models']:
                cost_per_1k = self.config['models'][model]['cost_per_1k_input']
                cost = (tokens / 1000) * cost_per_1k
            else:
                cost = (tokens / 1000) * 0.001  # 默认成本

            data.append({
                'model': model,
                'timestamp': timestamp,
                'tokens': tokens,
                'cost': cost
            })

        # 保存示例数据（仅在数据库不存在时）
        if not os.path.exists(self.usage_db):
            with open(self.usage_db, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return data

        # 数据库已存在，返回现有数据
        with open(self.usage_db, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _calculate_potential_savings(self, usage_data: List[Dict]) -> float:
        """
        计算潜在节省（通过缓存）

        假设重复率约为30%，可以节省对应的成本
        """
        if not usage_data:
            return 0.0

        # 简化计算：假设30%的请求可以通过缓存避免
        total_cost = sum([r.get('cost', 0) for r in usage_data])
        return total_cost * 0.3

    def record_usage(
        self,
        model: str,
        tokens: int,
        cost: float,
        prompt_hash: str = None
    ):
        """
        记录使用情况

        Args:
            model: 模型名称
            tokens: Token数量
            cost: 成本
            prompt_hash: 提示词哈希（用于缓存分析）
        """
        usage_data = self._load_usage_data()

        record = {
            'model': model,
            'timestamp': datetime.now().isoformat(),
            'tokens': tokens,
            'cost': cost,
            'prompt_hash': prompt_hash
        }

        usage_data.append(record)

        with open(self.usage_db, 'w', encoding='utf-8') as f:
            json.dump(usage_data, f, indent=2, ensure_ascii=False)

    def get_top_prompts(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """
        获取最常用的提示词

        Args:
            days: 统计天数
            limit: 返回数量

        Returns:
            提示词列表
        """
        usage_data = self._load_usage_data()
        cutoff_time = datetime.now() - timedelta(days=days)

        recent_data = [
            r for r in usage_data
            if datetime.fromisoformat(r['timestamp']) > cutoff_time
            and r.get('prompt_hash')
        ]

        # 统计提示词使用频率
        prompt_counts = {}
        for record in recent_data:
            prompt_hash = record['prompt_hash']
            if prompt_hash not in prompt_counts:
                prompt_counts[prompt_hash] = {
                    'count': 0,
                    'total_tokens': 0,
                    'total_cost': 0
                }

            prompt_counts[prompt_hash]['count'] += 1
            prompt_counts[prompt_hash]['total_tokens'] += record.get('tokens', 0)
            prompt_counts[prompt_hash]['total_cost'] += record.get('cost', 0)

        # 排序
        sorted_prompts = sorted(
            prompt_counts.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )

        return [
            {
                'prompt_hash': hash_val,
                'count': data['count'],
                'total_tokens': data['total_tokens'],
                'total_cost': data['total_cost']
            }
            for hash_val, data in sorted_prompts[:limit]
        ]
