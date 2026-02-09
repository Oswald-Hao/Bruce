#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康管理分析系统
Health Management and Analysis System

提供运动分析、饮食记录、睡眠分析、健康监测等功能
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import math


class HealthManager:
    """健康管理核心类"""

    def __init__(self, data_dir=None):
        if data_dir is None:
            data_dir = os.path.expanduser('~/.health_manager')
        self.data_dir = data_dir
        self.exercises_file = os.path.join(data_dir, 'exercises.json')
        self.foods_file = os.path.join(data_dir, 'foods.json')
        self.sleeps_file = os.path.join(data_dir, 'sleeps.json')
        self.metrics_file = os.path.join(data_dir, 'metrics.json')

        # 创建数据目录
        os.makedirs(data_dir, exist_ok=True)

        # 初始化数据文件
        self._init_data_files()

    def _init_data_files(self):
        """初始化数据文件"""
        for file_path in [self.exercises_file, self.foods_file, self.sleeps_file, self.metrics_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, indent=2)

    def _load_data(self, file_path):
        """加载数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_data(self, file_path, data):
        """保存数据"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ========== 运动相关 ==========
    def log_exercise(self, exercise_type, duration, calories=None, steps=None, heart_rate=None, notes=None):
        """记录运动"""
        exercise = {
            'timestamp': datetime.now().isoformat(),
            'type': exercise_type,
            'duration': duration,  # 分钟
            'calories': calories,
            'steps': steps,
            'heart_rate': heart_rate,
            'notes': notes
        }

        exercises = self._load_data(self.exercises_file)
        exercises.append(exercise)
        self._save_data(self.exercises_file, exercises)

        return {'status': 'success', 'exercise': exercise}

    def get_exercises(self, days=7):
        """获取运动记录"""
        exercises = self._load_data(self.exercises_file)
        cutoff_date = datetime.now() - timedelta(days=days)

        return [e for e in exercises if datetime.fromisoformat(e['timestamp']) >= cutoff_date]

    def analyze_exercises(self, days=7):
        """分析运动数据"""
        exercises = self.get_exercises(days)

        if not exercises:
            return {'status': 'no_data'}

        # 统计
        total_duration = sum(e['duration'] for e in exercises)
        total_calories = sum(e.get('calories', 0) for e in exercises if e.get('calories'))
        total_steps = sum(e.get('steps', 0) for e in exercises if e.get('steps'))

        # 按类型分组
        type_stats = {}
        for e in exercises:
            etype = e['type']
            if etype not in type_stats:
                type_stats[etype] = {'count': 0, 'duration': 0}
            type_stats[etype]['count'] += 1
            type_stats[etype]['duration'] += e['duration']

        # 平均心率
        heart_rates = [e.get('heart_rate') for e in exercises if e.get('heart_rate')]
        avg_heart_rate = sum(heart_rates) / len(heart_rates) if heart_rates else None

        return {
            'status': 'success',
            'period': f'{days}天',
            'total_duration': total_duration,
            'total_calories': total_calories,
            'total_steps': total_steps,
            'avg_duration_per_day': total_duration / days,
            'type_stats': type_stats,
            'avg_heart_rate': avg_heart_rate,
            'exercise_count': len(exercises)
        }

    # ========== 饮食相关 ==========
    def log_food(self, name, calories, protein=None, carbs=None, fat=None, notes=None):
        """记录饮食"""
        food = {
            'timestamp': datetime.now().isoformat(),
            'name': name,
            'calories': calories,
            'protein': protein,
            'carbs': carbs,
            'fat': fat,
            'notes': notes
        }

        foods = self._load_data(self.foods_file)
        foods.append(food)
        self._save_data(self.foods_file, foods)

        return {'status': 'success', 'food': food}

    def get_foods(self, days=7):
        """获取饮食记录"""
        foods = self._load_data(self.foods_file)
        cutoff_date = datetime.now() - timedelta(days=days)

        return [f for f in foods if datetime.fromisoformat(f['timestamp']) >= cutoff_date]

    def analyze_foods(self, days=7):
        """分析饮食数据"""
        foods = self.get_foods(days)

        if not foods:
            return {'status': 'no_data'}

        # 统计
        total_calories = sum(f['calories'] for f in foods)
        total_protein = sum(f.get('protein', 0) for f in foods if f.get('protein'))
        total_carbs = sum(f.get('carbs', 0) for f in foods if f.get('carbs'))
        total_fat = sum(f.get('fat', 0) for f in foods if f.get('fat'))

        # 每日平均
        avg_calories_per_day = total_calories / days
        avg_calories_per_meal = total_calories / len(foods) if foods else 0

        # 营养比例
        if total_protein + total_carbs + total_fat > 0:
            protein_pct = (total_protein * 4 / total_calories) * 100 if total_calories > 0 else 0
            carbs_pct = (total_carbs * 4 / total_calories) * 100 if total_calories > 0 else 0
            fat_pct = (total_fat * 9 / total_calories) * 100 if total_calories > 0 else 0
        else:
            protein_pct = carbs_pct = fat_pct = 0

        return {
            'status': 'success',
            'period': f'{days}天',
            'total_calories': total_calories,
            'total_protein': total_protein,
            'total_carbs': total_carbs,
            'total_fat': total_fat,
            'avg_calories_per_day': avg_calories_per_day,
            'avg_calories_per_meal': avg_calories_per_meal,
            'nutrition_ratios': {
                'protein': protein_pct,
                'carbs': carbs_pct,
                'fat': fat_pct
            },
            'meal_count': len(foods)
        }

    # ========== 睡眠相关 ==========
    def log_sleep(self, duration, deep=None, light=None, rem=None, quality=None, notes=None):
        """记录睡眠"""
        sleep = {
            'timestamp': datetime.now().isoformat(),
            'duration': duration,  # 小时
            'deep': deep,
            'light': light,
            'rem': rem,
            'quality': quality,  # 1-5评分
            'notes': notes
        }

        sleeps = self._load_data(self.sleeps_file)
        sleeps.append(sleep)
        self._save_data(self.sleeps_file, sleeps)

        return {'status': 'success', 'sleep': sleep}

    def get_sleeps(self, days=7):
        """获取睡眠记录"""
        sleeps = self._load_data(self.sleeps_file)
        cutoff_date = datetime.now() - timedelta(days=days)

        return [s for s in sleeps if datetime.fromisoformat(s['timestamp']) >= cutoff_date]

    def analyze_sleeps(self, days=7):
        """分析睡眠数据"""
        sleeps = self.get_sleeps(days)

        if not sleeps:
            return {'status': 'no_data'}

        # 统计
        total_duration = sum(s['duration'] for s in sleeps)
        total_deep = sum(s.get('deep', 0) for s in sleeps if s.get('deep'))
        total_light = sum(s.get('light', 0) for s in sleeps if s.get('light'))
        total_rem = sum(s.get('rem', 0) for s in sleeps if s.get('rem'))

        # 平均值
        avg_duration = total_duration / len(sleeps)
        avg_deep = total_deep / len(sleeps) if total_deep > 0 else None
        avg_light = total_light / len(sleeps) if total_light > 0 else None
        avg_rem = total_rem / len(sleeps) if total_rem > 0 else None

        # 质量评分
        qualities = [s.get('quality') for s in sleeps if s.get('quality')]
        avg_quality = sum(qualities) / len(qualities) if qualities else None

        # 睡眠结构
        if total_deep + total_light + total_rem > 0:
            structure = {
                'deep': (total_deep / (total_deep + total_light + total_rem)) * 100,
                'light': (total_light / (total_deep + total_light + total_rem)) * 100,
                'rem': (total_rem / (total_deep + total_light + total_rem)) * 100
            }
        else:
            structure = {'deep': 0, 'light': 0, 'rem': 0}

        return {
            'status': 'success',
            'period': f'{days}天',
            'total_duration': total_duration,
            'avg_duration': avg_duration,
            'avg_deep': avg_deep,
            'avg_light': avg_light,
            'avg_rem': avg_rem,
            'avg_quality': avg_quality,
            'sleep_structure': structure,
            'sleep_count': len(sleeps)
        }

    # ========== 健康指标相关 ==========
    def log_metric(self, metric_type, value, notes=None):
        """记录健康指标"""
        metric = {
            'timestamp': datetime.now().isoformat(),
            'type': metric_type,
            'value': value,
            'notes': notes
        }

        metrics = self._load_data(self.metrics_file)
        metrics.append(metric)
        self._save_data(self.metrics_file, metrics)

        return {'status': 'success', 'metric': metric}

    def get_metrics(self, metric_type=None, days=7):
        """获取健康指标"""
        metrics = self._load_data(self.metrics_file)
        cutoff_date = datetime.now() - timedelta(days=days)

        filtered = [m for m in metrics if datetime.fromisoformat(m['timestamp']) >= cutoff_date]

        if metric_type:
            filtered = [m for m in filtered if m['type'] == metric_type]

        return filtered

    def analyze_metric(self, metric_type, days=7):
        """分析健康指标"""
        metrics = self.get_metrics(metric_type, days)

        if not metrics:
            return {'status': 'no_data'}

        values = [m['value'] for m in metrics]

        return {
            'status': 'success',
            'type': metric_type,
            'period': f'{days}天',
            'latest': values[-1] if values else None,
            'avg': sum(values) / len(values),
            'min': min(values),
            'max': max(values),
            'count': len(values),
            'trend': 'up' if values[-1] > values[0] else 'down' if values[-1] < values[0] else 'stable'
        }

    # ========== BMI计算 ==========
    def calculate_bmi(self, weight, height):
        """计算BMI"""
        bmi = weight / ((height / 100) ** 2)
        bmi = round(bmi, 1)

        if bmi < 18.5:
            category = '偏瘦'
        elif 18.5 <= bmi < 24:
            category = '正常'
        elif 24 <= bmi < 28:
            category = '超重'
        else:
            category = '肥胖'

        return {
            'bmi': bmi,
            'category': category,
            'weight': weight,
            'height': height
        }

    # ========== 健康报告 ==========
    def generate_report(self, days=7):
        """生成健康报告"""
        exercise_analysis = self.analyze_exercises(days)
        food_analysis = self.analyze_foods(days)
        sleep_analysis = self.analyze_sleeps(days)

        report = {
            'generated_at': datetime.now().isoformat(),
            'period_days': days,
            'exercise': exercise_analysis,
            'food': food_analysis,
            'sleep': sleep_analysis
        }

        return report

    def save_report(self, report, output_path):
        """保存报告"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return {'status': 'success', 'output': output_path}

    # ========== 健康建议 ==========
    def get_advice(self, category='all'):
        """获取健康建议"""
        advice = {
            'exercise': {
                'general': '每天至少运动30分钟，每周至少150分钟中等强度运动',
                'running': '跑步是最有效的有氧运动之一，建议每周2-3次',
                'strength': '力量训练每周2-3次，每次45-60分钟',
                'heart_rate': '中等强度运动时，心率应保持在最大心率的60-80%'
            },
            'food': {
                'general': '均衡饮食，每天摄入1500-2000卡路里',
                'protein': '每天每公斤体重需要1-1.2克蛋白质',
                'carbs': '碳水化合物应占总热量的45-65%',
                'fat': '脂肪应占总热量的20-35%',
                'water': '每天至少喝8杯水（约2升）'
            },
            'sleep': {
                'general': '成年人每晚需要7-9小时睡眠',
                'quality': '保持规律的作息时间，避免睡前使用电子设备',
                'deep': '深度睡眠应占总睡眠时间的15-25%',
                'rem': 'REM睡眠应占总睡眠时间的20-25%'
            },
            'weight': {
                'bmi': 'BMI应在18.5-24之间为正常范围',
                'loss': '每周减重0.5-1公斤是健康且可持续的速度',
                'gain': '每周增重0.5-1公斤，通过增加蛋白质摄入和力量训练'
            }
        }

        if category == 'all':
            return advice
        else:
            return advice.get(category, {})


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description='健康管理分析系统')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 运动记录命令
    exercise_parser = subparsers.add_parser('log-exercise', help='记录运动')
    exercise_parser.add_argument('--type', required=True, help='运动类型 (running/fitness/cycling/swimming/walking)')
    exercise_parser.add_argument('--duration', type=float, required=True, help='持续时间（分钟）')
    exercise_parser.add_argument('--calories', type=int, help='消耗卡路里')
    exercise_parser.add_argument('--steps', type=int, help='步数')
    exercise_parser.add_argument('--heart-rate', type=int, help='平均心率')
    exercise_parser.add_argument('--notes', help='备注')

    # 饮食记录命令
    food_parser = subparsers.add_parser('log-food', help='记录饮食')
    food_parser.add_argument('--name', required=True, help='食物名称')
    food_parser.add_argument('--calories', type=int, required=True, help='卡路里')
    food_parser.add_argument('--protein', type=int, help='蛋白质（克）')
    food_parser.add_argument('--carbs', type=int, help='碳水化合物（克）')
    food_parser.add_argument('--fat', type=int, help='脂肪（克）')
    food_parser.add_argument('--notes', help='备注')

    # 睡眠记录命令
    sleep_parser = subparsers.add_parser('log-sleep', help='记录睡眠')
    sleep_parser.add_argument('--duration', type=float, required=True, help='睡眠时长（小时）')
    sleep_parser.add_argument('--deep', type=float, help='深睡时长（小时）')
    sleep_parser.add_argument('--light', type=float, help='浅睡时长（小时）')
    sleep_parser.add_argument('--rem', type=float, help='REM睡眠时长（小时）')
    sleep_parser.add_argument('--quality', type=int, choices=[1, 2, 3, 4, 5], help='睡眠质量评分（1-5）')
    sleep_parser.add_argument('--notes', help='备注')

    # 健康指标命令
    metric_parser = subparsers.add_parser('log-metric', help='记录健康指标')
    metric_parser.add_argument('--type', required=True, help='指标类型 (weight/bp/sugar)')
    metric_parser.add_argument('--value', type=float, required=True, help='数值')
    metric_parser.add_argument('--notes', help='备注')

    # BMI计算命令
    bmi_parser = subparsers.add_parser('bmi', help='计算BMI')
    bmi_parser.add_argument('--weight', type=float, required=True, help='体重（公斤）')
    bmi_parser.add_argument('--height', type=float, required=True, help='身高（厘米）')

    # 分析命令
    analyze_parser = subparsers.add_parser('analyze', help='分析健康数据')
    analyze_parser.add_argument('--type', required=True, choices=['exercise', 'food', 'sleep', 'metric'],
                               help='分析类型')
    analyze_parser.add_argument('--days', type=int, default=7, help='分析天数')
    analyze_parser.add_argument('--metric-type', help='指标类型（仅当type=metric时）')

    # 报告命令
    report_parser = subparsers.add_parser('report', help='生成健康报告')
    report_parser.add_argument('--period', choices=['day', 'week', 'month'], default='week', help='报告周期')
    report_parser.add_argument('--output', help='输出文件路径')

    # 建议命令
    advice_parser = subparsers.add_parser('advice', help='获取健康建议')
    advice_parser.add_argument('--type', choices=['exercise', 'food', 'sleep', 'weight', 'all'],
                              default='all', help='建议类型')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    manager = HealthManager()

    if args.command == 'log-exercise':
        result = manager.log_exercise(args.type, args.duration, args.calories, args.steps, args.heart_rate, args.notes)
    elif args.command == 'log-food':
        result = manager.log_food(args.name, args.calories, args.protein, args.carbs, args.fat, args.notes)
    elif args.command == 'log-sleep':
        result = manager.log_sleep(args.duration, args.deep, args.light, args.rem, args.quality, args.notes)
    elif args.command == 'log-metric':
        result = manager.log_metric(args.type, args.value, args.notes)
    elif args.command == 'bmi':
        result = manager.calculate_bmi(args.weight, args.height)
    elif args.command == 'analyze':
        if args.type == 'exercise':
            result = manager.analyze_exercises(args.days)
        elif args.type == 'food':
            result = manager.analyze_foods(args.days)
        elif args.type == 'sleep':
            result = manager.analyze_sleeps(args.days)
        elif args.type == 'metric':
            result = manager.analyze_metric(args.metric_type, args.days)
    elif args.command == 'report':
        period_map = {'day': 1, 'week': 7, 'month': 30}
        report = manager.generate_report(period_map[args.period])
        if args.output:
            result = manager.save_report(report, args.output)
        else:
            print(json.dumps(report, indent=2, ensure_ascii=False))
            return
    elif args.command == 'advice':
        result = manager.get_advice(args.type)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    if result['status'] == 'success':
        print(f'✓ {args.command} 成功')
        for key, value in result.items():
            if key != 'status':
                print(f'  {key}: {value}')
    else:
        print(f'✗ {args.command} 失败: {result.get("message", "未知错误")}')


if __name__ == '__main__':
    main()
