#!/usr/bin/env python3
"""
AI工具优化器 - 主程序
"""

import argparse
import json
import os
from typing import Dict, List, Any

from optimizer import PromptOptimizer
from token_analyzer import TokenAnalyzer
from model_selector import ModelSelector
from cache_manager import CacheManager
from quality_evaluator import QualityEvaluator


class AIToolOptimizer:
    """AI工具优化器"""

    def __init__(self, config_path: str = "config.json"):
        """初始化系统"""
        self.config = self.load_config(config_path)
        self.prompt_optimizer = PromptOptimizer(self.config)
        self.token_analyzer = TokenAnalyzer(self.config)
        self.model_selector = ModelSelector(self.config)
        self.cache_manager = CacheManager(self.config)
        self.quality_evaluator = QualityEvaluator(self.config)

    def load_config(self, config_path: str) -> Dict:
        """加载配置"""
        default_config = {
            "models": {
                "gpt-4": {
                    "cost_per_1k_input": 0.03,
                    "cost_per_1k_output": 0.06,
                    "max_tokens": 8192
                },
                "gpt-3.5-turbo": {
                    "cost_per_1k_input": 0.0005,
                    "cost_per_1k_output": 0.0015,
                    "max_tokens": 4096
                },
                "claude-3-opus": {
                    "cost_per_1k_input": 0.015,
                    "cost_per_1k_output": 0.075,
                    "max_tokens": 200000
                }
            },
            "budget": {
                "monthly_limit": 1000,
                "daily_limit": 50
            },
            "storage": {
                "usage_db": "usage_db.json",
                "cache_db": "cache_db.json",
                "quality_db": "quality_db.json"
            }
        }

        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            return default_config

    def optimize_prompt(
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
        return self.prompt_optimizer.optimize(prompt, model, task_type)

    def analyze_tokens(
        self,
        file_path: str = None,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        分析Token使用情况

        Args:
            file_path: 使用日志文件
            days: 统计天数

        Returns:
            分析结果
        """
        return self.token_analyzer.analyze(file_path, days)

    def suggest_model(
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
        return self.model_selector.suggest(task, budget, quality_priority)

    def analyze_cache(self, file_path: str = None) -> Dict[str, Any]:
        """
        分析缓存使用情况

        Args:
            file_path: 缓存日志文件

        Returns:
            分析结果
        """
        return self.cache_manager.analyze(file_path)

    def evaluate_quality(self, file_path: str = None) -> Dict[str, Any]:
        """
        评估响应质量

        Args:
            file_path: 响应日志文件

        Returns:
            评估结果
        """
        return self.quality_evaluator.evaluate(file_path)

    def get_usage_report(self, days: int = 7) -> Dict[str, Any]:
        """
        获取使用报告

        Args:
            days: 统计天数

        Returns:
            使用报告
        """
        token_analysis = self.analyze_tokens(None, days)
        quality_report = self.evaluate_quality(None)

        return {
            'token_usage': token_analysis,
            'quality': quality_report,
            'total_cost': token_analysis.get('total_cost', 0),
            'optimization_suggestions': self._generate_suggestions(token_analysis, quality_report)
        }

    def _generate_suggestions(
        self,
        token_analysis: Dict,
        quality_report: Dict
    ) -> List[str]:
        """生成优化建议"""
        suggestions = []

        # Token优化建议
        if token_analysis.get('potential_savings', 0) > 0:
            savings = token_analysis['potential_savings']
            suggestions.append(f"💰 通过缓存可以节省约{savings:.2f}元")

        if token_analysis.get('avg_tokens_per_request', 0) > 2000:
            suggestions.append("📝 平均Token使用量偏高，建议优化提示词长度")

        # 质量优化建议
        if quality_report.get('avg_quality_score', 1.0) < 0.8:
            suggestions.append("⚠️  响应质量低于标准，建议检查提示词")

        if quality_report.get('error_rate', 0) > 0.05:
            suggestions.append("🔧 错误率偏高，建议增加错误处理和重试机制")

        return suggestions


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='AI工具优化器')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 优化提示词命令
    optimize_parser = subparsers.add_parser('optimize-prompt', help='优化提示词')
    optimize_parser.add_argument('--prompt', required=True, help='提示词')
    optimize_parser.add_argument('--model', help='目标模型')
    optimize_parser.add_argument('--task', help='任务类型')

    # Token分析命令
    token_parser = subparsers.add_parser('analyze-tokens', help='分析Token使用')
    token_parser.add_argument('--file', help='使用日志文件')
    token_parser.add_argument('--days', type=int, default=7, help='统计天数')

    # 模型推荐命令
    model_parser = subparsers.add_parser('suggest-model', help='推荐模型')
    model_parser.add_argument('--task', required=True, help='任务描述')
    model_parser.add_argument('--budget', type=float, help='预算')
    model_parser.add_argument('--quality-priority', action='store_true', help='优先质量')

    # 缓存分析命令
    cache_parser = subparsers.add_parser('analyze-cache', help='分析缓存')
    cache_parser.add_argument('--file', help='缓存日志文件')

    # 质量评估命令
    quality_parser = subparsers.add_parser('evaluate-quality', help='评估质量')
    quality_parser.add_argument('--file', help='响应日志文件')

    # 使用报告命令
    report_parser = subparsers.add_parser('report', help='生成使用报告')
    report_parser.add_argument('--days', type=int, default=7, help='统计天数')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # 初始化优化器
    optimizer = AIToolOptimizer()

    # 执行命令
    if args.command == 'optimize-prompt':
        result = optimizer.optimize_prompt(
            prompt=args.prompt,
            model=args.model,
            task_type=args.task
        )

        print("\n📝 提示词优化结果:")
        print(f"\n原始提示词:\n{result['original_prompt']}")
        print(f"\n优化后提示词:\n{result['optimized_prompt']}")
        print(f"\n改进点:")
        for improvement in result['improvements']:
            print(f"  • {improvement}")

        if 'estimated_token_reduction' in result:
            print(f"\n预估Token减少: {result['estimated_token_reduction']:.1f}%")
            print(f"预估成本节省: {result['estimated_cost_savings']:.4f}元")

    elif args.command == 'analyze-tokens':
        result = optimizer.analyze_tokens(args.file, args.days)

        print(f"\n📊 Token使用分析 (最近{args.days}天):")
        print(f"  总请求数: {result['total_requests']}")
        print(f"  总Token数: {result['total_tokens']:,}")
        print(f"  平均Token/请求: {result['avg_tokens_per_request']:.1f}")
        print(f"  总成本: {result['total_cost']:.4f}元")
        print(f"  日均成本: {result['daily_cost']:.4f}元")

        if result.get('by_model'):
            print(f"\n  各模型使用:")
            for model, data in result['by_model'].items():
                print(f"    {model}: {data['requests']}次, {data['tokens']:,}tokens, {data['cost']:.4f}元")

        if result.get('potential_savings', 0) > 0:
            print(f"\n💰 潜在节省: {result['potential_savings']:.4f}元（通过缓存）")

    elif args.command == 'suggest-model':
        result = optimizer.suggest_model(
            task=args.task,
            budget=args.budget,
            quality_priority=args.quality_priority
        )

        print(f"\n🎯 模型推荐结果:")
        print(f"  任务: {result['task']}")
        print(f"\n推荐模型: {result['recommended_model']}")
        print(f"  原因: {result['reason']}")
        print(f"  预估成本: {result['estimated_cost']:.4f}元")
        print(f"  质量评分: {result['quality_score']:.1f}/10")

        if result.get('alternatives'):
            print(f"\n备选模型:")
            for alt in result['alternatives']:
                print(f"  • {alt['model']}: {alt['cost']:.4f}元, 质量{alt['quality']:.1f}/10 - {alt['reason']}")

    elif args.command == 'analyze-cache':
        result = optimizer.analyze_cache(args.file)

        print(f"\n💾 缓存分析:")
        print(f"  缓存条目数: {result['cache_entries']}")
        print(f"  缓存命中率: {result['hit_rate']:.1%}")
        print(f"  避免的API调用: {result['api_calls_avoided']}")
        print(f"  成本节省: {result['cost_savings']:.4f}元")

        if result.get('most_common', 0) > 0:
            print(f"\n  最常用的缓存键: {result['most_common']}次")

    elif args.command == 'evaluate-quality':
        result = optimizer.evaluate_quality(args.file)

        print(f"\n✨ 质量评估:")
        print(f"  总响应数: {result['total_responses']}")
        print(f"  平均质量评分: {result['avg_quality_score']:.2f}/1.0")
        print(f"  错误率: {result['error_rate']:.1%}")

        if result.get('by_quality'):
            print(f"\n  质量分布:")
            for level, count in result['by_quality'].items():
                print(f"    {level}: {count}次")

        if result.get('common_issues'):
            print(f"\n  常见问题:")
            for issue in result['common_issues'][:5]:
                print(f"    • {issue}")

    elif args.command == 'report':
        report = optimizer.get_usage_report(args.days)

        print(f"\n📋 AI工具使用报告 (最近{args.days}天):")
        print(f"\n💰 成本统计:")
        print(f"  总成本: {report['total_cost']:.4f}元")
        print(f"  Token总数: {report['token_usage']['total_tokens']:,}")
        print(f"  平均Token/请求: {report['token_usage']['avg_tokens_per_request']:.1f}")

        print(f"\n✨ 质量评估:")
        print(f"  平均评分: {report['quality']['avg_quality_score']:.2f}")
        print(f"  错误率: {report['quality']['error_rate']:.1%}")

        if report['optimization_suggestions']:
            print(f"\n💡 优化建议:")
            for suggestion in report['optimization_suggestions']:
                print(f"  {suggestion}")


if __name__ == '__main__':
    main()
