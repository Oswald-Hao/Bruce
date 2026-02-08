"""
质量评估器
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import re


class QualityEvaluator:
    """质量评估器"""

    def __init__(self, config: Dict):
        """初始化评估器"""
        self.config = config
        self.quality_db = config['storage']['quality_db']

    def evaluate(self, file_path: str = None) -> Dict[str, Any]:
        """
        评估响应质量

        Args:
            file_path: 响应日志文件

        Returns:
            评估结果
        """
        # 加载质量数据
        quality_data = self._load_quality_data(file_path)

        if not quality_data:
            return {
                'total_responses': 0,
                'avg_quality_score': 0.0,
                'error_rate': 0.0,
                'by_quality': {},
                'common_issues': []
            }

        # 统计数据
        total_responses = len(quality_data)
        total_score = sum([r.get('quality_score', 0) for r in quality_data])
        avg_quality = total_score / total_responses if total_responses > 0 else 0.0

        # 错误率
        error_count = len([r for r in quality_data if r.get('is_error', False)])
        error_rate = error_count / total_responses if total_responses > 0 else 0.0

        # 按质量等级分类
        by_quality = {
            '优秀': 0,    # 0.9-1.0
            '良好': 0,    # 0.7-0.9
            '一般': 0,    # 0.5-0.7
            '较差': 0,    # 0.3-0.5
            '很差': 0     # 0.0-0.3
        }

        for record in quality_data:
            score = record.get('quality_score', 0)
            if score >= 0.9:
                by_quality['优秀'] += 1
            elif score >= 0.7:
                by_quality['良好'] += 1
            elif score >= 0.5:
                by_quality['一般'] += 1
            elif score >= 0.3:
                by_quality['较差'] += 1
            else:
                by_quality['很差'] += 1

        # 常见问题
        common_issues = self._identify_common_issues(quality_data)

        return {
            'total_responses': total_responses,
            'avg_quality_score': avg_quality,
            'error_rate': error_rate,
            'by_quality': by_quality,
            'common_issues': common_issues
        }

    def _load_quality_data(self, file_path: str = None) -> List[Dict]:
        """加载质量数据"""
        if file_path and os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        # 尝试加载默认数据库
        if os.path.exists(self.quality_db):
            with open(self.quality_db, 'r', encoding='utf-8') as f:
                return json.load(f)

        # 返回示例数据
        return self._generate_sample_data()

    def _generate_sample_data(self) -> List[Dict]:
        """生成示例数据"""
        import random
        from datetime import datetime, timedelta

        data = []

        for i in range(50):
            # 随机生成质量分数
            quality_score = random.uniform(0.5, 1.0)

            # 随机生成错误
            is_error = random.random() < 0.05  # 5%错误率

            # 识别问题
            issues = []
            if is_error:
                issues.append('API错误')
            elif quality_score < 0.7:
                issues.append('响应质量低')
            if random.random() < 0.1:
                issues.append('响应不完整')

            timestamp = (datetime.now() - timedelta(hours=random.randint(0, 168))).isoformat()

            data.append({
                'timestamp': timestamp,
                'quality_score': quality_score,
                'is_error': is_error,
                'issues': issues,
                'response_length': random.randint(100, 5000)
            })

        # 保存示例数据（仅在数据库不存在时）
        if not os.path.exists(self.quality_db):
            with open(self.quality_db, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return data

        # 数据库已存在，返回现有数据
        with open(self.quality_db, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _identify_common_issues(self, quality_data: List[Dict]) -> List[str]:
        """识别常见问题"""
        issue_counts = {}

        for record in quality_data:
            for issue in record.get('issues', []):
                if issue not in issue_counts:
                    issue_counts[issue] = 0
                issue_counts[issue] += 1

        # 排序
        sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)

        return [issue for issue, count in sorted_issues]

    def evaluate_response(
        self,
        prompt: str,
        response: str,
        expected_length: int = None
    ) -> Dict[str, Any]:
        """
        评估单个响应的质量

        Args:
            prompt: 提示词
            response: 响应
            expected_length: 期望长度

        Returns:
            质量评估结果
        """
        issues = []
        quality_score = 1.0

        # 检查1: 响应是否为空
        if not response or len(response.strip()) == 0:
            issues.append('响应为空')
            quality_score *= 0.0
            return {
                'quality_score': quality_score,
                'issues': issues,
                'is_error': True
            }

        # 检查2: 响应长度是否合理
        if expected_length and len(response) < expected_length * 0.3:
            issues.append('响应过短')
            quality_score *= 0.7

        # 检查3: 是否包含错误信息
        error_patterns = [
            r'error',
            r'错误',
            r'sorry',
            r'抱歉',
            r'unable to',
            r'无法'
        ]

        for pattern in error_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                issues.append('响应包含错误信息')
                quality_score *= 0.5
                break

        # 检查4: 响应是否包含结构
        has_structure = (
            re.search(r'[1-9]\.', response) or  # 编号列表
            re.search(r'^-', response, re.MULTILINE) or  # 无序列表
            re.search(r'\n\n', response)  # 段落
        )

        if has_structure:
            quality_score *= 1.1  # 有结构加分

        # 检查5: 是否回答了问题（简单启发式）
        if '?' in prompt or '？' in prompt:
            # 问题型提示词，响应应该包含解释或答案
            if len(response) < 50:
                issues.append('响应过短，可能未充分回答')
                quality_score *= 0.8

        # 限制分数范围
        quality_score = max(0.0, min(1.0, quality_score))

        return {
            'quality_score': quality_score,
            'issues': issues,
            'is_error': quality_score < 0.3
        }

    def record_response(
        self,
        prompt: str,
        response: str,
        quality_score: float,
        issues: List[str] = None
    ):
        """
        记录响应质量

        Args:
            prompt: 提示词
            response: 响应
            quality_score: 质量分数
            issues: 问题列表
        """
        quality_data = self._load_quality_data()

        record = {
            'timestamp': datetime.now().isoformat(),
            'prompt': prompt[:100] + '...' if len(prompt) > 100 else prompt,
            'response': response[:200] + '...' if len(response) > 200 else response,
            'quality_score': quality_score,
            'is_error': quality_score < 0.3,
            'issues': issues or [],
            'response_length': len(response)
        }

        quality_data.append(record)

        with open(self.quality_db, 'w', encoding='utf-8') as f:
            json.dump(quality_data, f, indent=2, ensure_ascii=False)
