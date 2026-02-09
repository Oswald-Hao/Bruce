#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康管理分析系统测试
Health Management and Analysis System Tests
"""

import unittest
import os
import sys
import json
import shutil
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import HealthManager


class TestHealthManager(unittest.TestCase):
    """测试健康管理器"""

    @classmethod
    def setUpClass(cls):
        """测试前设置"""
        cls.test_dir = '/tmp/test_health_manager'
        os.makedirs(cls.test_dir, exist_ok=True)
        cls.manager = HealthManager(data_dir=cls.test_dir)

    @classmethod
    def tearDownClass(cls):
        """测试后清理"""
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)

    def test_01_log_exercise(self):
        """测试记录运动"""
        result = self.manager.log_exercise(
            exercise_type='running',
            duration=30,
            calories=300,
            steps=5000,
            heart_rate=140
        )
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['exercise']['type'], 'running')
        self.assertEqual(result['exercise']['duration'], 30)
        print('✓ 测试1：记录运动 - 通过')

    def test_02_get_exercises(self):
        """测试获取运动记录"""
        exercises = self.manager.get_exercises(days=1)
        self.assertGreater(len(exercises), 0)
        self.assertEqual(exercises[0]['type'], 'running')
        print('✓ 测试2：获取运动记录 - 通过')

    def test_03_analyze_exercises(self):
        """测试分析运动数据"""
        # 添加更多运动记录
        self.manager.log_exercise('fitness', 45, calories=250)
        self.manager.log_exercise('swimming', 30, calories=400)

        analysis = self.manager.analyze_exercises(days=1)
        self.assertEqual(analysis['status'], 'success')
        self.assertEqual(analysis['exercise_count'], 3)
        self.assertGreater(analysis['total_duration'], 0)
        print('✓ 测试3：分析运动数据 - 通过')

    def test_04_log_food(self):
        """测试记录饮食"""
        result = self.manager.log_food(
            name='鸡胸肉沙拉',
            calories=350,
            protein=30,
            carbs=15,
            fat=10
        )
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['food']['calories'], 350)
        print('✓ 测试4：记录饮食 - 通过')

    def test_05_get_foods(self):
        """测试获取饮食记录"""
        foods = self.manager.get_foods(days=1)
        self.assertGreater(len(foods), 0)
        self.assertEqual(foods[0]['name'], '鸡胸肉沙拉')
        print('✓ 测试5：获取饮食记录 - 通过')

    def test_06_analyze_foods(self):
        """测试分析饮食数据"""
        # 添加更多饮食记录
        self.manager.log_food('香蕉', 90, protein=1, carbs=23, fat=0)
        self.manager.log_food('燕麦片', 150, protein=5, carbs=27, fat=3)

        analysis = self.manager.analyze_foods(days=1)
        self.assertEqual(analysis['status'], 'success')
        self.assertGreater(analysis['total_calories'], 0)
        self.assertEqual(analysis['meal_count'], 3)
        print('✓ 测试6：分析饮食数据 - 通过')

    def test_07_log_sleep(self):
        """测试记录睡眠"""
        result = self.manager.log_sleep(
            duration=7.5,
            deep=3.0,
            light=3.5,
            rem=1.0,
            quality=4
        )
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['sleep']['duration'], 7.5)
        print('✓ 测试7：记录睡眠 - 通过')

    def test_08_get_sleeps(self):
        """测试获取睡眠记录"""
        sleeps = self.manager.get_sleeps(days=1)
        self.assertGreater(len(sleeps), 0)
        self.assertEqual(sleeps[0]['duration'], 7.5)
        print('✓ 测试8：获取睡眠记录 - 通过')

    def test_09_analyze_sleeps(self):
        """测试分析睡眠数据"""
        # 添加更多睡眠记录
        self.manager.log_sleep(duration=8.0, deep=3.2, light=3.8, rem=1.0, quality=5)
        self.manager.log_sleep(duration=7.0, deep=2.8, light=3.2, rem=1.0, quality=3)

        analysis = self.manager.analyze_sleeps(days=1)
        self.assertEqual(analysis['status'], 'success')
        self.assertEqual(analysis['sleep_count'], 3)
        self.assertGreater(analysis['avg_duration'], 0)
        print('✓ 测试9：分析睡眠数据 - 通过')

    def test_10_log_metric(self):
        """测试记录健康指标"""
        result = self.manager.log_metric(metric_type='weight', value=70.5)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['metric']['value'], 70.5)
        print('✓ 测试10：记录健康指标 - 通过')

    def test_11_get_metrics(self):
        """测试获取健康指标"""
        metrics = self.manager.get_metrics(metric_type='weight', days=1)
        self.assertGreater(len(metrics), 0)
        self.assertEqual(metrics[0]['value'], 70.5)
        print('✓ 测试11：获取健康指标 - 通过')

    def test_12_analyze_metric(self):
        """测试分析健康指标"""
        # 添加更多指标
        self.manager.log_metric('weight', 70.3)
        self.manager.log_metric('weight', 70.2)

        analysis = self.manager.analyze_metric('weight', days=1)
        self.assertEqual(analysis['status'], 'success')
        self.assertEqual(analysis['count'], 3)
        self.assertIn('avg', analysis)
        self.assertIn('min', analysis)
        self.assertIn('max', analysis)
        print('✓ 测试12：分析健康指标 - 通过')

    def test_13_calculate_bmi(self):
        """测试计算BMI"""
        result = self.manager.calculate_bmi(weight=70, height=175)
        self.assertEqual(result['bmi'], 22.9)  # 70 / (1.75^2) = 22.857 ≈ 22.9
        self.assertEqual(result['category'], '正常')
        print('✓ 测试13：计算BMI - 通过')

    def test_14_bmi_categories(self):
        """测试BMI分类"""
        # 偏瘦
        result = self.manager.calculate_bmi(50, 175)
        self.assertEqual(result['category'], '偏瘦')

        # 正常
        result = self.manager.calculate_bmi(70, 175)
        self.assertEqual(result['category'], '正常')

        # 超重
        result = self.manager.calculate_bmi(80, 175)
        self.assertEqual(result['category'], '超重')

        # 肥胖
        result = self.manager.calculate_bmi(100, 175)
        self.assertEqual(result['category'], '肥胖')

        print('✓ 测试14：BMI分类 - 通过')

    def test_15_generate_report(self):
        """测试生成健康报告"""
        report = self.manager.generate_report(days=1)
        self.assertIn('exercise', report)
        self.assertIn('food', report)
        self.assertIn('sleep', report)
        self.assertEqual(report['period_days'], 1)
        print('✓ 测试15：生成健康报告 - 通过')

    def test_16_save_report(self):
        """测试保存报告"""
        report = self.manager.generate_report(days=1)
        output_path = os.path.join(self.test_dir, 'health_report.json')
        result = self.manager.save_report(report, output_path)

        self.assertEqual(result['status'], 'success')
        self.assertTrue(os.path.exists(output_path))

        # 验证报告内容
        with open(output_path, 'r', encoding='utf-8') as f:
            saved_report = json.load(f)
        self.assertEqual(saved_report['period_days'], 1)
        print('✓ 测试16：保存报告 - 通过')

    def test_17_get_advice(self):
        """测试获取健康建议"""
        advice = self.manager.get_advice(category='exercise')
        self.assertIn('general', advice)
        self.assertIn('running', advice)
        print('✓ 测试17：获取健康建议 - 通过')

    def test_18_get_all_advice(self):
        """测试获取所有健康建议"""
        advice = self.manager.get_advice(category='all')
        self.assertIn('exercise', advice)
        self.assertIn('food', advice)
        self.assertIn('sleep', advice)
        self.assertIn('weight', advice)
        print('✓ 测试18：获取所有健康建议 - 通过')

    def test_19_data_persistence(self):
        """测试数据持久化"""
        # 创建新的管理器实例，验证数据持久化
        new_manager = HealthManager(data_dir=self.test_dir)

        # 检查运动记录
        exercises = new_manager.get_exercises(days=1)
        self.assertGreater(len(exercises), 0)

        # 检查饮食记录
        foods = new_manager.get_foods(days=1)
        self.assertGreater(len(foods), 0)

        # 检查睡眠记录
        sleeps = new_manager.get_sleeps(days=1)
        self.assertGreater(len(sleeps), 0)

        print('✓ 测试19：数据持久化 - 通过')

    def test_20_different_exercise_types(self):
        """测试不同运动类型"""
        types = ['running', 'fitness', 'cycling', 'swimming', 'walking']
        for etype in types:
            result = self.manager.log_exercise(etype, 30)
            self.assertEqual(result['status'], 'success')

        exercises = self.manager.get_exercises(days=1)
        type_counts = {}
        for e in exercises:
            t = e['type']
            type_counts[t] = type_counts.get(t, 0) + 1

        for t in types:
            self.assertGreater(type_counts.get(t, 0), 0)

        print('✓ 测试20：不同运动类型 - 通过')


def run_tests():
    """运行所有测试"""
    print('\n' + '='*60)
    print('健康管理分析系统 - 测试套件')
    print('='*60 + '\n')

    # 运行测试
    suite = unittest.TestLoader().loadTestsFromTestCase(TestHealthManager)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 输出统计
    print('\n' + '='*60)
    print('测试统计')
    print('='*60)
    print(f'总测试数: {result.testsRun}')
    print(f'成功: {result.testsRun - len(result.failures) - len(result.errors)}')
    print(f'失败: {len(result.failures)}')
    print(f'错误: {len(result.errors)}')
    print(f'通过率: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%')
    print('='*60)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
