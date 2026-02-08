"""
缓存管理器
"""

import json
import os
from hashlib import md5
from typing import Dict, List, Any


class CacheManager:
    """缓存管理器"""

    def __init__(self, config: Dict):
        """初始化缓存管理器"""
        self.config = config
        self.cache_db = config['storage']['cache_db']
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict:
        """加载缓存"""
        if os.path.exists(self.cache_db):
            with open(self.cache_db, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_cache(self):
        """保存缓存"""
        with open(self.cache_db, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, indent=2, ensure_ascii=False)

    def get_cache_key(self, prompt: str, model: str) -> str:
        """生成缓存键"""
        combined = f"{model}:{prompt}"
        return md5(combined.encode()).hexdigest()

    def get(self, prompt: str, model: str) -> Dict[str, Any]:
        """
        从缓存获取响应

        Args:
            prompt: 提示词
            model: 模型名称

        Returns:
            缓存的响应，不存在返回None
        """
        cache_key = self.get_cache_key(prompt, model)

        if cache_key in self.cache:
            self.cache[cache_key]['hits'] += 1
            self._save_cache()

            return {
                'response': self.cache[cache_key]['response'],
                'tokens': self.cache[cache_key]['tokens'],
                'from_cache': True
            }

        return None

    def set(
        self,
        prompt: str,
        model: str,
        response: str,
        tokens: int
    ):
        """
        设置缓存

        Args:
            prompt: 提示词
            model: 模型名称
            response: 响应
            tokens: Token数量
        """
        cache_key = self.get_cache_key(prompt, model)

        self.cache[cache_key] = {
            'prompt': prompt,
            'model': model,
            'response': response,
            'tokens': tokens,
            'created_at': self._get_timestamp(),
            'hits': 0
        }

        self._save_cache()

    def analyze(self, file_path: str = None) -> Dict[str, Any]:
        """
        分析缓存使用情况

        Args:
            file_path: 缓存日志文件（可选）

        Returns:
            分析结果
        """
        cache = self.cache

        if not cache:
            return {
                'cache_entries': 0,
                'total_hits': 0,
                'hit_rate': 0.0,
                'api_calls_avoided': 0,
                'cost_savings': 0.0,
                'most_common': 0
            }

        total_entries = len(cache)
        total_hits = sum([entry['hits'] for entry in cache.values()])
        hit_rate = total_hits / (total_entries + total_hits) if (total_entries + total_hits) > 0 else 0.0

        # 计算避免的API调用
        api_calls_avoided = total_hits

        # 计算成本节省（假设平均每调用花费0.002元）
        cost_savings = api_calls_avoided * 0.002

        # 找出最常用的缓存键
        most_common = max([entry['hits'] for entry in cache.values()]) if cache else 0

        return {
            'cache_entries': total_entries,
            'total_hits': total_hits,
            'hit_rate': hit_rate,
            'api_calls_avoided': api_calls_avoided,
            'cost_savings': cost_savings,
            'most_common': most_common
        }

    def clear_cache(self, days: int = None):
        """
        清理缓存

        Args:
            days: 清理N天前的缓存，None表示清理全部
        """
        from datetime import datetime, timedelta

        if days is None:
            self.cache = {}
        else:
            cutoff_time = datetime.now() - timedelta(days=days)

            self.cache = {
                key: value
                for key, value in self.cache.items()
                if datetime.fromisoformat(value['created_at']) > cutoff_time
            }

        self._save_cache()

    def get_top_cached(self, limit: int = 10) -> List[Dict]:
        """
        获取最常用的缓存

        Args:
            limit: 返回数量

        Returns:
            缓存列表
        """
        sorted_cache = sorted(
            self.cache.items(),
            key=lambda x: x[1]['hits'],
            reverse=True
        )

        return [
            {
                'cache_key': key,
                'prompt': value['prompt'][:50] + '...' if len(value['prompt']) > 50 else value['prompt'],
                'model': value['model'],
                'hits': value['hits'],
                'tokens': value['tokens'],
                'created_at': value['created_at']
            }
            for key, value in sorted_cache[:limit]
        ]

    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
