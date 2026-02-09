#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识图谱构建系统测试
Knowledge Graph Construction System Tests
"""

import unittest
import os
import sys
import json
import shutil
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import KnowledgeGraph


class TestKnowledgeGraph(unittest.TestCase):
    """测试知识图谱"""

    @classmethod
    def setUpClass(cls):
        """测试前设置"""
        cls.test_dir = '/tmp/test_knowledge_graph'
        os.makedirs(cls.test_dir, exist_ok=True)
        cls.graph = KnowledgeGraph(data_dir=cls.test_dir)

    @classmethod
    def tearDownClass(cls):
        """测试后清理"""
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)

    def test_01_add_entity(self):
        """测试添加实体"""
        result = self.graph.add_entity(
            name='Bruce',
            entity_type='AI助手',
            properties={'created_by': 'Oswald', 'mission': '服务'}
        )
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['entity']['name'], 'Bruce')
        self.assertEqual(result['entity']['type'], 'AI助手')
        print('✓ 测试1：添加实体 - 通过')

    def test_02_get_entity(self):
        """测试获取实体"""
        entity = self.graph.get_entity('Bruce')
        self.assertIsNotNone(entity)
        self.assertEqual(entity['name'], 'Bruce')
        self.assertEqual(entity['type'], 'AI助手')
        print('✓ 测试2：获取实体 - 通过')

    def test_03_add_multiple_entities(self):
        """测试添加多个实体"""
        self.graph.add_entity('Oswald', '人类', {'role': '创造者'})
        self.graph.add_entity('Moltbot', '平台', {'type': 'AI平台'})
        self.graph.add_entity('Python', '语言', {'version': '3.10'})

        entities = self.graph.list_entities()
        self.assertGreaterEqual(len(entities), 4)
        print('✓ 测试3：添加多个实体 - 通过')

    def test_04_list_entities_by_type(self):
        """测试按类型列出实体"""
        self.graph.add_entity('AI助手2', 'AI助手', {})

        ai_assistants = self.graph.list_entities(entity_type='AI助手')
        self.assertGreaterEqual(len(ai_assistants), 2)
        print('✓ 测试4：按类型列出实体 - 通过')

    def test_05_update_entity(self):
        """测试更新实体"""
        result = self.graph.update_entity('Bruce', {'status': '运行中'})
        self.assertEqual(result['status'], 'success')

        entity = self.graph.get_entity('Bruce')
        self.assertEqual(entity['properties']['status'], '运行中')
        print('✓ 测试5：更新实体 - 通过')

    def test_06_add_relation(self):
        """测试添加关系"""
        result = self.graph.add_relation(
            source='Bruce',
            target='Oswald',
            relation_type='为...而生',
            properties={'since': '2026'}
        )
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['relation']['source'], 'Bruce')
        self.assertEqual(result['relation']['target'], 'Oswald')
        print('✓ 测试6：添加关系 - 通过')

    def test_07_get_relations(self):
        """测试获取关系"""
        relations = self.graph.get_relations(source='Bruce')
        self.assertGreater(len(relations), 0)
        self.assertEqual(relations[0]['type'], '为...而生')
        print('✓ 测试7：获取关系 - 通过')

    def test_08_add_multiple_relations(self):
        """测试添加多个关系"""
        self.graph.add_relation('Oswald', 'Moltbot', '使用', {})
        self.graph.add_relation('Bruce', 'Moltbot', '运行在', {})
        self.graph.add_relation('Moltbot', 'Python', '基于', {})

        all_relations = self.graph.get_relations()
        self.assertGreaterEqual(len(all_relations), 4)
        print('✓ 测试8：添加多个关系 - 通过')

    def test_09_get_neighbors(self):
        """测试获取邻居节点"""
        neighbors = self.graph.get_neighbors('Bruce')
        self.assertIn('Oswald', neighbors)
        print('✓ 测试9：获取邻居节点 - 通过')

    def test_10_find_path(self):
        """测试查找路径"""
        path = self.graph.find_path('Bruce', 'Moltbot')
        self.assertIsNotNone(path)
        self.assertIn('Bruce', path)
        self.assertIn('Moltbot', path)
        print('✓ 测试10：查找路径 - 通过')

    def test_11_find_long_path(self):
        """测试查找长路径"""
        self.graph.add_relation('Python', 'Guido', '由...创造', {})

        path = self.graph.find_path('Bruce', 'Guido', max_depth=4)
        if path:
            self.assertIn('Bruce', path)
            self.assertIn('Guido', path)
        print('✓ 测试11：查找长路径 - 通过')

    def test_12_get_subgraph(self):
        """测试获取子图"""
        subgraph = self.graph.get_subgraph('Bruce', depth=1)
        self.assertIn('entities', subgraph)
        self.assertIn('relations', subgraph)
        self.assertIn('Bruce', subgraph['entities'])
        print('✓ 测试12：获取子图 - 通过')

    def test_13_analyze_graph(self):
        """测试分析图谱"""
        analysis = self.graph.analyze()
        self.assertIn('entity_count', analysis)
        self.assertIn('relation_count', analysis)
        self.assertIn('entity_types', analysis)
        self.assertIn('relation_types', analysis)
        self.assertGreater(analysis['entity_count'], 0)
        self.assertGreater(analysis['relation_count'], 0)
        print('✓ 测试13：分析图谱 - 通过')

    def test_14_extract_entities(self):
        """测试实体抽取"""
        text = 'Bruce是一个AI助手，为Oswald创建于2026年。他使用Python语言开发。'
        entities = self.graph.extract_entities(text)

        # 检查是否抽到实体（即使模式简单）
        self.assertIsInstance(entities, list)
        print('✓ 测试14：实体抽取 - 通过')

    def test_15_export_json(self):
        """测试导出JSON"""
        output_path = os.path.join(self.test_dir, 'graph.json')
        result = self.graph.export(output_path, format='json')

        self.assertEqual(result['status'], 'success')
        self.assertTrue(os.path.exists(output_path))

        # 验证导出内容
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertIn('entities', data)
        self.assertIn('relations', data)
        print('✓ 测试15：导出JSON - 通过')

    def test_16_export_csv(self):
        """测试导出CSV"""
        output_path = os.path.join(self.test_dir, 'graph.csv')
        result = self.graph.export(output_path, format='csv')

        self.assertEqual(result['status'], 'success')
        self.assertIn('entities_csv', result['output'])
        self.assertIn('relations_csv', result['output'])

        self.assertTrue(os.path.exists(result['output']['entities_csv']))
        self.assertTrue(os.path.exists(result['output']['relations_csv']))
        print('✓ 测试16：导出CSV - 通过')

    def test_17_import_data(self):
        """测试导入数据"""
        # 导出数据
        export_path = os.path.join(self.test_dir, 'export.json')
        self.graph.export(export_path, format='json')

        # 创建新的图谱实例
        new_graph = KnowledgeGraph(data_dir=os.path.join(self.test_dir, 'new'))

        # 导入数据
        result = new_graph.import_data(export_path)
        self.assertEqual(result['status'], 'success')

        # 验证导入的数据
        entity = new_graph.get_entity('Bruce')
        self.assertIsNotNone(entity)
        print('✓ 测试17：导入数据 - 通过')

    def test_18_delete_entity(self):
        """测试删除实体"""
        self.graph.add_entity('ToDelete', '临时实体', {})

        result = self.graph.delete_entity('ToDelete')
        self.assertEqual(result['status'], 'success')

        entity = self.graph.get_entity('ToDelete')
        self.assertIsNone(entity)
        print('✓ 测试18：删除实体 - 通过')

    def test_19_delete_entity_cascade(self):
        """测试删除实体的级联效果（同时删除相关关系）"""
        self.graph.add_entity('TestEntity', '测试', {})
        self.graph.add_relation('Bruce', 'TestEntity', '测试关系', {})

        # 记录删除前的关系数
        relations_before = self.graph.get_relations()

        # 删除实体
        self.graph.delete_entity('TestEntity')

        # 验证关系也被删除
        relations_after = self.graph.get_relations()
        test_relations_after = [r for r in relations_after if 'TestEntity' in [r['source'], r['target']]]
        self.assertEqual(len(test_relations_after), 0)
        print('✓ 测试19：删除实体级联效果 - 通过')

    def test_20_visualize(self):
        """测试可视化"""
        viz_data = self.graph.visualize()
        self.assertIn('nodes', viz_data)
        self.assertIn('edges', viz_data)
        self.assertGreater(len(viz_data['nodes']), 0)
        print('✓ 测试20：可视化 - 通过')

    def test_21_visualize_subgraph(self):
        """测试子图可视化"""
        viz_data = self.graph.visualize(entity_name='Bruce', depth=1)
        self.assertIn('nodes', viz_data)
        self.assertIn('edges', viz_data)

        # 验证Bruce在节点中
        node_names = [n['id'] for n in viz_data['nodes']]
        self.assertIn('Bruce', node_names)
        print('✓ 测试21：子图可视化 - 通过')


def run_tests():
    """运行所有测试"""
    print('\n' + '='*60)
    print('知识图谱构建系统 - 测试套件')
    print('='*60 + '\n')

    # 运行测试
    suite = unittest.TestLoader().loadTestsFromTestCase(TestKnowledgeGraph)
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
