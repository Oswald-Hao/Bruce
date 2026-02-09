#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识图谱构建系统
Knowledge Graph Construction System

提供实体管理、关系管理、图谱查询、分析、导出等功能
"""

import json
import os
import re
from collections import defaultdict
from pathlib import Path


class KnowledgeGraph:
    """知识图谱核心类"""

    def __init__(self, data_dir=None):
        if data_dir is None:
            data_dir = os.path.expanduser('~/.knowledge_graph')
        self.data_dir = data_dir
        self.entities_file = os.path.join(data_dir, 'entities.json')
        self.relations_file = os.path.join(data_dir, 'relations.json')

        # 创建数据目录
        os.makedirs(data_dir, exist_ok=True)

        # 初始化数据文件
        self._init_data_files()

    def _init_data_files(self):
        """初始化数据文件"""
        for file_path in [self.entities_file, self.relations_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f, indent=2)

    def _load_data(self, file_path):
        """加载数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_data(self, file_path, data):
        """保存数据"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ========== 实体管理 ==========
    def add_entity(self, name, entity_type, properties=None):
        """添加实体"""
        entities = self._load_data(self.entities_file)

        entity = {
            'name': name,
            'type': entity_type,
            'properties': properties or {},
            'created_at': self._get_timestamp()
        }

        entities[name] = entity
        self._save_data(self.entities_file, entities)

        return {'status': 'success', 'entity': entity}

    def get_entity(self, name):
        """获取实体"""
        entities = self._load_data(self.entities_file)
        return entities.get(name)

    def update_entity(self, name, properties=None):
        """更新实体"""
        entities = self._load_data(self.entities_file)

        if name not in entities:
            return {'status': 'error', 'message': f'实体 {name} 不存在'}

        if properties:
            entities[name]['properties'].update(properties)

        self._save_data(self.entities_file, entities)

        return {'status': 'success', 'entity': entities[name]}

    def delete_entity(self, name):
        """删除实体"""
        entities = self._load_data(self.entities_file)

        if name not in entities:
            return {'status': 'error', 'message': f'实体 {name} 不存在'}

        # 删除实体
        del entities[name]
        self._save_data(self.entities_file, entities)

        # 删除相关关系
        relations = self._load_data(self.relations_file)
        relations = [r for r in relations if r['source'] != name and r['target'] != name]
        self._save_data(self.relations_file, relations)

        return {'status': 'success', 'message': f'实体 {name} 已删除'}

    def list_entities(self, entity_type=None):
        """列出实体"""
        entities = self._load_data(self.entities_file)

        if entity_type:
            return [e for e in entities.values() if e['type'] == entity_type]

        return list(entities.values())

    # ========== 关系管理 ==========
    def add_relation(self, source, target, relation_type, properties=None):
        """添加关系"""
        entities = self._load_data(self.entities_file)

        if source not in entities:
            return {'status': 'error', 'message': f'源实体 {source} 不存在'}
        if target not in entities:
            return {'status': 'error', 'message': f'目标实体 {target} 不存在'}

        relations = self._load_data(self.relations_file)
        if not isinstance(relations, list):
            relations = []

        relation = {
            'source': source,
            'target': target,
            'type': relation_type,
            'properties': properties or {},
            'created_at': self._get_timestamp()
        }

        relations.append(relation)
        self._save_data(self.relations_file, relations)

        return {'status': 'success', 'relation': relation}

    def get_relations(self, source=None, target=None, relation_type=None):
        """获取关系"""
        relations = self._load_data(self.relations_file)
        if not isinstance(relations, list):
            return []

        filtered = relations

        if source:
            filtered = [r for r in filtered if r['source'] == source]
        if target:
            filtered = [r for r in filtered if r['target'] == target]
        if relation_type:
            filtered = [r for r in filtered if r['type'] == relation_type]

        return filtered

    def delete_relation(self, index):
        """删除关系"""
        relations = self._load_data(self.relations_file)

        if not isinstance(relations, list):
            return {'status': 'error', 'message': '关系列表格式错误'}

        if index < 0 or index >= len(relations):
            return {'status': 'error', 'message': f'关系索引 {index} 超出范围'}

        deleted_relation = relations.pop(index)
        self._save_data(self.relations_file, relations)

        return {'status': 'success', 'deleted_relation': deleted_relation}

    # ========== 图谱查询 ==========
    def get_neighbors(self, entity_name):
        """获取实体的邻居节点"""
        relations = self.get_relations(source=entity_name)
        relations += self.get_relations(target=entity_name)

        neighbors = set()
        for r in relations:
            neighbors.add(r['source'])
            neighbors.add(r['target'])

        neighbors.discard(entity_name)

        return list(neighbors)

    def find_path(self, start, end, max_depth=3):
        """查找两个实体之间的路径"""
        if start == end:
            return [start]

        visited = set()
        paths = [[start]]

        for depth in range(max_depth):
            new_paths = []
            for path in paths:
                current = path[-1]
                neighbors = self.get_neighbors(current)

                for neighbor in neighbors:
                    if neighbor == end:
                        return path + [end]

                    if neighbor not in visited:
                        visited.add(neighbor)
                        new_paths.append(path + [neighbor])

            paths = new_paths

            if not paths:
                break

        return None

    def get_subgraph(self, entity_name, depth=1):
        """获取子图"""
        visited = set()
        result_entities = {}
        result_relations = []

        def traverse(node, current_depth):
            if current_depth > depth:
                return

            if node in visited:
                return

            visited.add(node)
            entities = self._load_data(self.entities_file)
            if node in entities:
                result_entities[node] = entities[node]

            relations = self.get_relations(source=node)
            for r in relations:
                result_relations.append(r)
                traverse(r['target'], current_depth + 1)

            relations = self.get_relations(target=node)
            for r in relations:
                result_relations.append(r)
                traverse(r['source'], current_depth + 1)

        traverse(entity_name, 0)

        return {
            'entities': result_entities,
            'relations': result_relations
        }

    # ========== 图谱分析 ==========
    def analyze(self):
        """分析图谱"""
        entities = self._load_data(self.entities_file)
        relations = self.get_relations()

        # 统计
        entity_count = len(entities)
        relation_count = len(relations)

        # 类型统计
        entity_types = defaultdict(int)
        for e in entities.values():
            entity_types[e['type']] += 1

        relation_types = defaultdict(int)
        for r in relations:
            relation_types[r['type']] += 1

        # 度中心性（节点的连接数）
        degrees = defaultdict(int)
        for r in relations:
            degrees[r['source']] += 1
            degrees[r['target']] += 1

        # 按度数排序
        top_entities = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            'entity_count': entity_count,
            'relation_count': relation_count,
            'entity_types': dict(entity_types),
            'relation_types': dict(relation_types),
            'top_entities': top_entities,
            'avg_degree': sum(degrees.values()) / len(degrees) if degrees else 0
        }

    # ========== 实体抽取 ==========
    def extract_entities(self, text, entity_patterns=None):
        """从文本中抽取实体"""
        if entity_patterns is None:
            entity_patterns = {
                '人名': r'([A-Z][a-z]+|[张王李赵刘陈杨黄周吴徐孙胡朱高林何郭马罗梁宋郑谢韩唐冯于董萧程曹袁邓许傅沈曾彭吕苏卢蒋蔡贾丁魏薛叶阎余潘杜戴夏钟汪田任姜范方石姚谭廖邹熊金陆郝孔白崔康毛邱秦江史顾侯邵孟龙万段漕钱汤尹黎易常武乔贺赖龚文][^\\s]+)',
                '时间': r'(\\d{4}年\\d{1,2}月\\d{1,2}日|\\d{4}-\\d{1,2}-\\d{1,2}|今天|明天|昨天)',
                '数字': r'(\\d+(\\.\\d+)?)'
            }

        entities = []

        for entity_type, pattern in entity_patterns.items():
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    entity_name = match[0]
                else:
                    entity_name = match

                entities.append({
                    'name': entity_name,
                    'type': entity_type
                })

        return entities

    # ========== 图谱导出 ==========
    def export(self, output_path, format='json'):
        """导出图谱"""
        entities = self._load_data(self.entities_file)
        relations = self.get_relations()

        graph_data = {
            'entities': entities,
            'relations': relations
        }

        if format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(graph_data, f, indent=2, ensure_ascii=False)

        elif format == 'csv':
            # 导出实体
            entities_csv = os.path.join(os.path.dirname(output_path), 'entities.csv')
            with open(entities_csv, 'w', encoding='utf-8') as f:
                f.write('name,type,properties\n')
                for name, entity in entities.items():
                    props_str = json.dumps(entity['properties'], ensure_ascii=False)
                    f.write(f'{name},{entity["type"]},{props_str}\n')

            # 导出关系
            relations_csv = os.path.join(os.path.dirname(output_path), 'relations.csv')
            with open(relations_csv, 'w', encoding='utf-8') as f:
                f.write('source,target,type,properties\n')
                for r in relations:
                    props_str = json.dumps(r['properties'], ensure_ascii=False)
                    f.write(f'{r["source"]},{r["target"]},{r["type"]},{props_str}\n')

            graph_data['entities_csv'] = entities_csv
            graph_data['relations_csv'] = relations_csv

        return {'status': 'success', 'output': graph_data}

    # ========== 可视化 ==========
    def visualize(self, entity_name=None, depth=1):
        """生成可视化数据"""
        if entity_name:
            graph_data = self.get_subgraph(entity_name, depth)
        else:
            entities = self._load_data(self.entities_file)
            relations = self.get_relations()
            graph_data = {
                'entities': entities,
                'relations': relations
            }

        # 转换为可视化格式
        nodes = []
        for name, entity in graph_data['entities'].items():
            nodes.append({
                'id': name,
                'label': name,
                'type': entity['type'],
                'properties': entity['properties']
            })

        edges = []
        for r in graph_data['relations']:
            edges.append({
                'source': r['source'],
                'target': r['target'],
                'label': r['type'],
                'properties': r['properties']
            })

        return {
            'nodes': nodes,
            'edges': edges
        }

    # ========== 辅助方法 ==========
    def _get_timestamp(self):
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()

    def import_data(self, data_path):
        """导入数据"""
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if 'entities' in data:
            entities = self._load_data(self.entities_file)
            for name, entity in data['entities'].items():
                entities[name] = entity
            self._save_data(self.entities_file, entities)

        if 'relations' in data:
            relations = self._load_data(self.relations_file)
            if not isinstance(relations, list):
                relations = []
            relations.extend(data['relations'])
            self._save_data(self.relations_file, relations)

        return {'status': 'success', 'message': '数据导入成功'}


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description='知识图谱构建系统')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 添加实体命令
    add_entity_parser = subparsers.add_parser('add-entity', help='添加实体')
    add_entity_parser.add_argument('--name', required=True, help='实体名称')
    add_entity_parser.add_argument('--type', required=True, help='实体类型')
    add_entity_parser.add_argument('--properties', help='属性（JSON格式）')

    # 添加关系命令
    add_relation_parser = subparsers.add_parser('add-relation', help='添加关系')
    add_relation_parser.add_argument('--source', required=True, help='源实体')
    add_relation_parser.add_argument('--target', required=True, help='目标实体')
    add_relation_parser.add_argument('--type', required=True, help='关系类型')
    add_relation_parser.add_argument('--properties', help='属性（JSON格式）')

    # 查询实体命令
    query_entity_parser = subparsers.add_parser('query-entity', help='查询实体')
    query_entity_parser.add_argument('--name', required=True, help='实体名称')

    # 查询关系命令
    query_relation_parser = subparsers.add_parser('query-relation', help='查询关系')
    query_relation_parser.add_argument('--source', help='源实体')
    query_relation_parser.add_argument('--target', help='目标实体')
    query_relation_parser.add_argument('--type', help='关系类型')

    # 查询路径命令
    query_path_parser = subparsers.add_parser('query-path', help='查询路径')
    query_path_parser.add_argument('--start', required=True, help='起点实体')
    query_path_parser.add_argument('--end', required=True, help='终点实体')

    # 导出命令
    export_parser = subparsers.add_parser('export', help='导出图谱')
    export_parser.add_argument('--output', required=True, help='输出文件路径')
    export_parser.add_argument('--format', choices=['json', 'csv'], default='json', help='输出格式')

    # 分析命令
    analyze_parser = subparsers.add_parser('analyze', help='分析图谱')

    # 实体抽取命令
    extract_parser = subparsers.add_parser('extract', help='实体抽取')
    extract_parser.add_argument('--text', required=True, help='文本内容')

    # 可视化命令
    visualize_parser = subparsers.add_parser('visualize', help='可视化图谱')
    visualize_parser.add_argument('--entity', help='中心实体')
    visualize_parser.add_argument('--depth', type=int, default=1, help='深度')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    graph = KnowledgeGraph()

    if args.command == 'add-entity':
        properties = json.loads(args.properties) if args.properties else None
        result = graph.add_entity(args.name, args.type, properties)
    elif args.command == 'add-relation':
        properties = json.loads(args.properties) if args.properties else None
        result = graph.add_relation(args.source, args.target, args.type, properties)
    elif args.command == 'query-entity':
        entity = graph.get_entity(args.name)
        if entity:
            result = {'status': 'success', 'entity': entity}
        else:
            result = {'status': 'error', 'message': '实体不存在'}
    elif args.command == 'query-relation':
        relations = graph.get_relations(args.source, args.target, args.type)
        result = {'status': 'success', 'relations': relations}
    elif args.command == 'query-path':
        path = graph.find_path(args.start, args.end)
        if path:
            result = {'status': 'success', 'path': path}
        else:
            result = {'status': 'error', 'message': '未找到路径'}
    elif args.command == 'export':
        result = graph.export(args.output, args.format)
    elif args.command == 'analyze':
        result = graph.analyze()
    elif args.command == 'extract':
        entities = graph.extract_entities(args.text)
        result = {'status': 'success', 'entities': entities}
    elif args.command == 'visualize':
        result = graph.visualize(args.entity, args.depth)
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
