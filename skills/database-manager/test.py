#!/usr/bin/env python3
"""
测试数据库管理系统
"""

import os
import sqlite3
import json
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from skills.database_manager.skill import DatabaseManager


def test_sqlite_connection():
    """测试SQLite连接"""
    print("测试1: SQLite连接...")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        db = DatabaseManager()
        conn = db.connect_sqlite(db_path)
        
        assert conn is not None, "连接失败"
        assert 'sqlite' in db.connections, "连接未保存"
        
        db.close()
        print("✓ SQLite连接成功")
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_create_table():
    """测试创建表"""
    print("\n测试2: 创建表...")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        db = DatabaseManager()
        db.connect_sqlite(db_path)
        
        columns = {
            'id': 'INTEGER PRIMARY KEY',
            'name': 'TEXT NOT NULL',
            'age': 'INTEGER',
            'email': 'TEXT'
        }
        
        result = db.create_table('users', columns)
        assert result, "创建表失败"
        
        tables = db.list_tables()
        assert 'users' in tables, "表未创建"
        
        db.close()
        print("✓ 创建表成功")
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_insert_and_query():
    """测试插入和查询"""
    print("\n测试3: 插入和查询...")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        db = DatabaseManager()
        db.connect_sqlite(db_path)
        
        # 创建表
        columns = {
            'id': 'INTEGER PRIMARY KEY',
            'name': 'TEXT NOT NULL',
            'age': 'INTEGER'
        }
        db.create_table('users', columns)
        
        # 插入数据
        db.execute("INSERT INTO users (name, age) VALUES (?, ?)", 'sqlite', params=('Alice', 25))
        db.execute("INSERT INTO users (name, age) VALUES (?, ?)", 'sqlite', params=('Bob', 30))
        
        # 查询数据
        results = db.query("SELECT * FROM users", 'sqlite')
        assert len(results) == 2, "查询结果不正确"
        assert results[0]['name'] == 'Alice', "数据不正确"
        
        db.close()
        print("✓ 插入和查询成功")
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_table_structure():
    """测试获取表结构"""
    print("\n测试4: 获取表结构...")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        db = DatabaseManager()
        db.connect_sqlite(db_path)
        
        columns = {
            'id': 'INTEGER PRIMARY KEY',
            'name': 'TEXT NOT NULL',
            'age': 'INTEGER'
        }
        db.create_table('users', columns)
        
        structure = db.get_table_structure('users')
        assert structure['table'] == 'users', "表名不正确"
        assert len(structure['columns']) == 3, "列数不正确"
        
        # 检查列信息
        col_names = [col['name'] for col in structure['columns']]
        assert 'id' in col_names, "缺少id列"
        assert 'name' in col_names, "缺少name列"
        
        db.close()
        print("✓ 获取表结构成功")
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_backup():
    """测试备份"""
    print("\n测试5: 备份...")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        db = DatabaseManager()
        db.connect_sqlite(db_path)
        
        # 创建表并插入数据
        columns = {
            'id': 'INTEGER PRIMARY KEY',
            'name': 'TEXT NOT NULL'
        }
        db.create_table('test_table', columns)
        db.execute("INSERT INTO test_table (name) VALUES (?)", 'sqlite', params=('Test',))
        
        db.close()
        
        # 创建新实例进行备份
        db2 = DatabaseManager()
        backup_path = db2.backup_sqlite(db_path, 'test_backup')
        
        assert os.path.exists(backup_path), "备份文件不存在"
        assert backup_path.endswith('.gz'), "备份文件未压缩"
        
        # 检查备份文件大小
        assert os.path.getsize(backup_path) > 0, "备份文件为空"
        
        print(f"✓ 备份成功: {backup_path}")
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False
    finally:
        # 清理
        if os.path.exists(db_path):
            os.unlink(db_path)
        # 清理备份目录
        backup_dir = Path('./backups')
        if backup_dir.exists():
            shutil.rmtree(backup_dir)


def test_health_check():
    """测试健康检查"""
    print("\n测试6: 健康检查...")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        db = DatabaseManager()
        db.connect_sqlite(db_path)
        
        # 创建表
        columns = {'id': 'INTEGER PRIMARY KEY', 'name': 'TEXT'}
        db.create_table('users', columns)
        
        # 健康检查
        health = db.health_check('sqlite')
        assert health['status'] == 'healthy', "状态不正确"
        assert health['database'] == 'SQLite', "数据库类型不正确"
        assert health['tables'] == 1, "表数不正确"
        assert 'size_bytes' in health, "缺少大小信息"
        
        db.close()
        print("✓ 健康检查成功")
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_drop_table():
    """测试删除表"""
    print("\n测试7: 删除表...")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        db = DatabaseManager()
        db.connect_sqlite(db_path)
        
        columns = {'id': 'INTEGER PRIMARY KEY', 'name': 'TEXT'}
        db.create_table('temp_table', columns)
        
        # 确认表存在
        assert 'temp_table' in db.list_tables(), "表未创建"
        
        # 删除表
        result = db.drop_table('temp_table')
        assert result, "删除表失败"
        
        # 确认表已删除
        assert 'temp_table' not in db.list_tables(), "表未删除"
        
        db.close()
        print("✓ 删除表成功")
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_export_schema():
    """测试导出结构"""
    print("\n测试8: 导出结构...")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        output_file = f.name

    try:
        db = DatabaseManager()
        db.connect_sqlite(db_path)
        
        columns = {
            'id': 'INTEGER PRIMARY KEY',
            'name': 'TEXT NOT NULL',
            'age': 'INTEGER'
        }
        db.create_table('users', columns)
        db.create_table('products', {'id': 'INTEGER PRIMARY KEY', 'title': 'TEXT'})
        
        # 导出结构
        result = db.export_schema(output_file)
        assert result, "导出失败"
        assert os.path.exists(output_file), "输出文件不存在"
        
        # 验证导出内容
        with open(output_file, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        
        assert schema['database'] == 'sqlite', "数据库类型不正确"
        assert len(schema['tables']) == 2, "表数不正确"
        assert 'users' in schema['tables'], "缺少users表"
        assert 'products' in schema['tables'], "缺少products表"
        
        db.close()
        print("✓ 导出结构成功")
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)
        if os.path.exists(output_file):
            os.unlink(output_file)


def test_query_optimization():
    """测试查询优化"""
    print("\n测试9: 查询优化建议...")
    
    try:
        db = DatabaseManager()
        
        # 测试SELECT *
        suggestions = db.optimize_query("SELECT * FROM users")
        assert suggestions['total'] > 0, "应该有优化建议"
        
        # 测试缺少WHERE
        suggestions = db.optimize_query("SELECT id FROM users")
        assert any(s['issue'] == '缺少 WHERE 条件' for s in suggestions['suggestions']), "应该检测到缺少WHERE"
        
        # 测试ORDER BY无LIMIT
        suggestions = db.optimize_query("SELECT id FROM users ORDER BY name")
        assert any(s['issue'] == 'ORDER BY 没有 LIMIT' for s in suggestions['suggestions']), "应该检测到缺少LIMIT"
        
        # 测试子查询
        suggestions = db.optimize_query("SELECT * FROM users WHERE id IN (SELECT user_id FROM orders)")
        assert any(s['issue'] == '可能包含子查询' for s in suggestions['suggestions']), "应该检测到子查询"
        
        print("✓ 查询优化建议成功")
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def test_multiple_connections():
    """测试多连接管理"""
    print("\n测试10: 多连接管理...")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path1 = f.name

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path2 = f.name

    try:
        db = DatabaseManager()
        
        # 连接两个数据库
        conn1 = db.connect_sqlite(db_path1)
        conn2 = db.connect_sqlite(db_path2)
        
        assert len(db.connections) == 2, "连接数不正确"
        
        # 在第一个数据库创建表
        db.create_table('users', {'id': 'INTEGER PRIMARY KEY'}, 'sqlite')
        
        # 在第二个数据库创建表
        db.execute("CREATE TABLE products (id INTEGER PRIMARY KEY)", 'sqlite')
        
        # 关闭所有连接
        db.close()
        assert len(db.connections) == 0, "连接未全部关闭"
        
        print("✓ 多连接管理成功")
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False
    finally:
        if os.path.exists(db_path1):
            os.unlink(db_path1)
        if os.path.exists(db_path2):
            os.unlink(db_path2)


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("数据库管理系统 - 功能测试")
    print("=" * 60)
    
    tests = [
        test_sqlite_connection,
        test_create_table,
        test_insert_and_query,
        test_table_structure,
        test_backup,
        test_health_check,
        test_drop_table,
        test_export_schema,
        test_query_optimization,
        test_multiple_connections
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print(f"测试结果: {sum(results)}/{len(results)} 通过")
    print("=" * 60)
    
    return all(results)


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
