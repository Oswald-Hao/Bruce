#!/usr/bin/env python3
"""
数据库管理系统 - Database Manager

功能：
- 多数据库支持（MySQL、PostgreSQL、SQLite、MongoDB）
- 自动备份和恢复
- 数据迁移和同步
- SQL查询优化
- 数据库监控和健康检查
- 表结构管理
"""

import sqlite3
import subprocess
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path


class DatabaseManager:
    """数据库管理器 - 多数据库统一管理接口"""

    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化数据库管理器

        Args:
            config: 配置字典，包含数据库连接信息
        """
        self.config = config or {}
        self.connections: Dict[str, Any] = {}
        # 使用绝对路径作为备份目录
        backup_dir = self.config.get('backup_dir', './backups')
        self.backup_dir = Path(backup_dir).resolve()
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def connect_sqlite(self, db_path: str) -> sqlite3.Connection:
        """
        连接SQLite数据库

        Args:
            db_path: 数据库文件路径

        Returns:
            SQLite连接对象
        """
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        # 使用数据库路径作为key，支持多个SQLite连接
        conn_key = f'sqlite_{db_path}'
        self.connections[conn_key] = conn
        # 同时保存到'sqlite'作为默认连接（最后一个连接）
        self.connections['sqlite'] = conn
        return conn

    def connect_postgresql(self, host: str, database: str, user: str, password: str, port: int = 5432):
        """
        连接PostgreSQL数据库

        Args:
            host: 主机地址
            database: 数据库名
            user: 用户名
            password: 密码
            port: 端口

        Returns:
            连接对象（需要psycopg2）
        """
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=host,
                database=database,
                user=user,
                password=password,
                port=port
            )
            self.connections['postgresql'] = conn
            return conn
        except ImportError:
            raise ImportError("需要安装 psycopg2: pip install psycopg2-binary")

    def connect_mysql(self, host: str, database: str, user: str, password: str, port: int = 3306):
        """
        连接MySQL数据库

        Args:
            host: 主机地址
            database: 数据库名
            user: 用户名
            password: 密码
            port: 端口

        Returns:
            连接对象（需要PyMySQL）
        """
        try:
            import pymysql
            conn = pymysql.connect(
                host=host,
                database=database,
                user=user,
                password=password,
                port=port,
                cursorclass=pymysql.cursors.DictCursor
            )
            self.connections['mysql'] = conn
            return conn
        except ImportError:
            raise ImportError("需要安装 pymysql: pip install pymysql")

    def backup_sqlite(self, db_path: str, backup_name: str = None) -> str:
        """
        备份SQLite数据库

        Args:
            db_path: 数据库文件路径
            backup_name: 备份名称（可选）

        Returns:
            备份文件路径
        """
        if backup_name is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"backup_{timestamp}.db"

        backup_path = self.backup_dir / backup_name
        subprocess.run(['cp', db_path, str(backup_path)], check=True)

        # 压缩备份
        compressed_path = backup_path.with_suffix('.db.gz')
        subprocess.run(['gzip', '-f', str(backup_path)], check=True)

        return str(compressed_path)

    def backup_postgresql(self, host: str, database: str, user: str, backup_name: str = None) -> str:
        """
        备份PostgreSQL数据库

        Args:
            host: 主机地址
            database: 数据库名
            user: 用户名
            backup_name: 备份名称

        Returns:
            备份文件路径
        """
        if backup_name is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"pg_backup_{timestamp}.sql"

        backup_path = self.backup_dir / backup_name

        env = os.environ.copy()
        env['PGPASSWORD'] = input("请输入PostgreSQL密码: ")

        subprocess.run([
            'pg_dump',
            '-h', host,
            '-U', user,
            '-d', database,
            '-f', str(backup_path)
        ], env=env, check=True)

        # 压缩备份
        compressed_path = backup_path.with_suffix('.sql.gz')
        subprocess.run(['gzip', '-f', str(backup_path)], check=True)

        return str(compressed_path)

    def restore_sqlite(self, backup_path: str, target_path: str) -> bool:
        """
        恢复SQLite数据库

        Args:
            backup_path: 备份文件路径
            target_path: 目标数据库路径

        Returns:
            是否成功
        """
        try:
            # 解压缩
            if backup_path.endswith('.gz'):
                decompressed = backup_path[:-3]
                subprocess.run(['gunzip', '-k', backup_path], check=True)
                backup_path = decompressed

            subprocess.run(['cp', backup_path, target_path], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def _get_connection(self, db_type: str = 'sqlite'):
        """
        获取连接对象（辅助方法）

        Args:
            db_type: 数据库类型

        Returns:
            连接对象
        """
        conn = self.connections.get(db_type)
        if conn:
            return conn
        
        # 如果是sqlite且未找到，尝试找到第一个sqlite连接
        if db_type == 'sqlite':
            for key, conn in self.connections.items():
                if key.startswith('sqlite_'):
                    return conn
        
        raise ValueError(f"未找到 {db_type} 连接")

    def list_tables(self, db_type: str = 'sqlite') -> List[str]:
        """
        列出数据库中的所有表

        Args:
            db_type: 数据库类型

        Returns:
            表名列表
        """
        conn = self._get_connection(db_type)

        if db_type == 'sqlite':
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            return [row[0] for row in cursor.fetchall()]
        elif db_type == 'postgresql':
            cursor = conn.cursor()
            cursor.execute("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
            return [row[0] for row in cursor.fetchall()]
        elif db_type == 'mysql':
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            return [list(row.values())[0] for row in cursor.fetchall()]
        else:
            raise ValueError(f"不支持的数据库类型: {db_type}")

    def get_table_structure(self, table_name: str, db_type: str = 'sqlite') -> Dict[str, Any]:
        """
        获取表结构

        Args:
            table_name: 表名
            db_type: 数据库类型

        Returns:
            表结构信息
        """
        conn = self._get_connection(db_type)

        if db_type == 'sqlite':
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            return {
                'table': table_name,
                'columns': [
                    {
                        'name': col['name'],
                        'type': col['type'],
                        'notnull': bool(col['notnull']),
                        'primary_key': bool(col['pk'])
                    }
                    for col in columns
                ]
            }
        elif db_type == 'postgresql':
            cursor = conn.cursor()
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = %s
            """, (table_name,))
            columns = cursor.fetchall()

            return {
                'table': table_name,
                'columns': [
                    {
                        'name': col[0],
                        'type': col[1],
                        'nullable': col[2] == 'YES',
                        'default': col[3]
                    }
                    for col in columns
                ]
            }
        elif db_type == 'mysql':
            cursor = conn.cursor()
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()

            return {
                'table': table_name,
                'columns': [
                    {
                        'name': col['Field'],
                        'type': col['Type'],
                        'nullable': col['Null'] == 'YES',
                        'key': col['Key'],
                        'default': col['Default']
                    }
                    for col in columns
                ]
            }
        else:
            raise ValueError(f"不支持的数据库类型: {db_type}")

    def query(self, sql: str, db_type: str = 'sqlite', params: Tuple = None) -> List[Dict]:
        """
        执行查询

        Args:
            sql: SQL语句
            db_type: 数据库类型
            params: 查询参数

        Returns:
            查询结果列表
        """
        conn = self._get_connection(db_type)

        cursor = conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)

        return [dict(row) for row in cursor.fetchall()]

    def execute(self, sql: str, db_type: str = 'sqlite', params: Tuple = None) -> int:
        """
        执行SQL语句（INSERT/UPDATE/DELETE）

        Args:
            sql: SQL语句
            db_type: 数据库类型
            params: 查询参数

        Returns:
            受影响的行数
        """
        conn = self._get_connection(db_type)

        cursor = conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)

        conn.commit()
        return cursor.rowcount

    def create_table(self, table_name: str, columns: Dict[str, str], db_type: str = 'sqlite') -> bool:
        """
        创建表

        Args:
            table_name: 表名
            columns: 列定义 {列名: 类型}
            db_type: 数据库类型

        Returns:
            是否成功
        """
        columns_def = ', '.join([f"{name} {ctype}" for name, ctype in columns.items()])
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def})"

        try:
            self.execute(sql, db_type)
            return True
        except Exception as e:
            print(f"创建表失败: {e}")
            return False

    def drop_table(self, table_name: str, db_type: str = 'sqlite') -> bool:
        """
        删除表

        Args:
            table_name: 表名
            db_type: 数据库类型

        Returns:
            是否成功
        """
        sql = f"DROP TABLE IF EXISTS {table_name}"

        try:
            self.execute(sql, db_type)
            return True
        except Exception as e:
            print(f"删除表失败: {e}")
            return False

    def health_check(self, db_type: str = 'sqlite') -> Dict[str, Any]:
        """
        数据库健康检查

        Args:
            db_type: 数据库类型

        Returns:
            健康状态信息
        """
        conn = self._get_connection(db_type)
        if not conn:
            return {'status': 'disconnected', 'error': '未找到连接'}

        try:
            # 测试查询
            if db_type == 'sqlite':
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()

                # 获取数据库大小
                if 'sqlite' in self.connections:
                    import os
                    db_path = self.connections['sqlite'].execute("PRAGMA database_list").fetchone()[2]
                    size = os.path.getsize(db_path) if db_path and os.path.exists(db_path) else 0

                    return {
                        'status': 'healthy',
                        'database': 'SQLite',
                        'size_bytes': size,
                        'size_mb': size / (1024 * 1024),
                        'tables': len(self.list_tables(db_type))
                    }
            elif db_type == 'postgresql':
                cursor = conn.cursor()
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public'")
                table_count = cursor.fetchone()[0]

                return {
                    'status': 'healthy',
                    'database': 'PostgreSQL',
                    'version': version,
                    'tables': table_count
                }
            elif db_type == 'mysql':
                cursor = conn.cursor()
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()[0]
                cursor.execute("SHOW TABLES")
                table_count = len(cursor.fetchall())

                return {
                    'status': 'healthy',
                    'database': 'MySQL',
                    'version': version,
                    'tables': table_count
                }

        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

        return {'status': 'unknown'}

    def close(self, db_type: str = None):
        """
        关闭连接

        Args:
            db_type: 数据库类型（None表示关闭所有）
        """
        if db_type:
            if db_type in self.connections:
                self.connections[db_type].close()
                del self.connections[db_type]
        else:
            for conn in self.connections.values():
                conn.close()
            self.connections.clear()

    def export_schema(self, output_file: str, db_type: str = 'sqlite') -> bool:
        """
        导出数据库结构

        Args:
            output_file: 输出文件路径
            db_type: 数据库类型

        Returns:
            是否成功
        """
        try:
            schema = {
                'database': db_type,
                'exported_at': datetime.now().isoformat(),
                'tables': {}
            }

            for table in self.list_tables(db_type):
                schema['tables'][table] = self.get_table_structure(table, db_type)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(schema, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"导出结构失败: {e}")
            return False

    def optimize_query(self, sql: str, db_type: str = 'sqlite') -> Dict[str, Any]:
        """
        SQL查询优化建议

        Args:
            sql: SQL语句
            db_type: 数据库类型

        Returns:
            优化建议
        """
        suggestions = []

        # 基础优化检查
        sql_upper = sql.upper()

        # 检查是否使用SELECT *
        if 'SELECT *' in sql_upper:
            suggestions.append({
                'issue': '使用 SELECT *',
                'suggestion': '明确列出需要的列名，减少数据传输',
                'priority': 'medium'
            })

        # 检查是否缺少WHERE条件
        if 'FROM' in sql_upper and 'WHERE' not in sql_upper and 'JOIN' not in sql_upper:
            suggestions.append({
                'issue': '缺少 WHERE 条件',
                'suggestion': '添加适当的WHERE条件限制结果集',
                'priority': 'high'
            })

        # 检查是否使用ORDER BY但没有LIMIT
        if 'ORDER BY' in sql_upper and 'LIMIT' not in sql_upper:
            suggestions.append({
                'issue': 'ORDER BY 没有 LIMIT',
                'suggestion': '添加LIMIT限制返回的行数',
                'priority': 'low'
            })

        # 检查子查询
        if 'SELECT' in sql_upper and sql_upper.count('SELECT') > 1:
            suggestions.append({
                'issue': '可能包含子查询',
                'suggestion': '考虑使用JOIN代替子查询提高性能',
                'priority': 'medium'
            })

        return {
            'sql': sql,
            'suggestions': suggestions,
            'total': len(suggestions)
        }


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description='数据库管理系统')
    parser.add_argument('action', choices=['backup', 'restore', 'list', 'structure', 'health', 'export'])
    parser.add_argument('--db-path', help='SQLite数据库路径')
    parser.add_argument('--backup-name', help='备份名称')
    parser.add_argument('--table', help='表名')
    parser.add_argument('--output', help='输出文件')

    args = parser.parse_args()

    db = DatabaseManager()

    if args.action == 'backup' and args.db_path:
        backup_path = db.backup_sqlite(args.db_path, args.backup_name)
        print(f"备份完成: {backup_path}")

    elif args.action == 'restore':
        print("恢复功能需要指定备份文件和目标路径")

    elif args.action == 'list' and args.db_path:
        db.connect_sqlite(args.db_path)
        tables = db.list_tables()
        print("数据库表:")
        for table in tables:
            print(f"  - {table}")
        db.close()

    elif args.action == 'structure' and args.db_path and args.table:
        db.connect_sqlite(args.db_path)
        structure = db.get_table_structure(args.table)
        print(f"表 {args.table} 结构:")
        print(json.dumps(structure, indent=2, ensure_ascii=False))
        db.close()

    elif args.action == 'health' and args.db_path:
        db.connect_sqlite(args.db_path)
        health = db.health_check()
        print("数据库健康状态:")
        print(json.dumps(health, indent=2, ensure_ascii=False))
        db.close()

    elif args.action == 'export' and args.db_path and args.output:
        db.connect_sqlite(args.db_path)
        if db.export_schema(args.output):
            print(f"结构导出完成: {args.output}")
        db.close()


if __name__ == '__main__':
    main()
