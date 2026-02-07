#!/usr/bin/env python3
"""
实时数据监控系统
支持多数据源监控、智能预警、自动响应
"""

import json
import yaml
import logging
import time
import threading
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from enum import Enum
import random
import requests
import hashlib

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TaskType(Enum):
    """任务类型"""
    PRICE = "price"
    NEWS = "news"
    COMPETITOR = "competitor"
    STOCK = "stock"
    SOCIAL = "social"


class AlertLevel(Enum):
    """预警级别"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class ActionType(Enum):
    """动作类型"""
    ALERT = "alert"
    BUY = "buy"
    LOG = "log"
    WEBHOOK = "webhook"
    FEISHU = "feishu"
    EMAIL = "email"


@dataclass
class MonitorTask:
    """监控任务"""
    task_id: str
    name: str
    type: TaskType
    source: str
    keywords: List[str]
    target_urls: List[str]
    interval: int  # 监控间隔（秒）
    threshold: str
    action: str
    enabled: bool
    last_check: Optional[datetime]
    last_value: Optional[Any]


@dataclass
class MonitorData:
    """监控数据"""
    data_id: str
    task_id: str
    timestamp: datetime
    data_type: str
    value: Any
    raw_data: str
    source: str


@dataclass
class Alert:
    """预警"""
    alert_id: str
    task_id: str
    timestamp: datetime
    level: AlertLevel
    message: str
    data: Dict
    action_taken: str


class MonitorEngine:
    """监控引擎"""

    def __init__(self, config_file: str = "config/monitor.yaml"):
        """
        初始化监控引擎

        Args:
            config_file: 配置文件路径
        """
        self.config = self._load_config(config_file)
        self.tasks: List[MonitorTask] = []
        self.data: List[MonitorData] = []
        self.alerts: List[Alert] = []
        self.is_running = False
        self.worker_thread = None
        self.db_conn = self._init_db()

    def _load_config(self, config_file: str) -> Dict:
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return {}

    def _init_db(self) -> sqlite3.Connection:
        """初始化数据库"""
        import os
        os.makedirs("data", exist_ok=True)

        conn = sqlite3.connect("data/monitor.db", check_same_thread=False)
        cursor = conn.cursor()

        # 创建任务表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                name TEXT,
                type TEXT,
                source TEXT,
                keywords TEXT,
                target_urls TEXT,
                interval INTEGER,
                threshold TEXT,
                action TEXT,
                enabled INTEGER,
                last_check TEXT,
                last_value TEXT
            )
        """)

        # 创建数据表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monitor_data (
                data_id TEXT PRIMARY KEY,
                task_id TEXT,
                timestamp TEXT,
                data_type TEXT,
                value TEXT,
                raw_data TEXT,
                source TEXT
            )
        """)

        # 创建预警表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                alert_id TEXT PRIMARY KEY,
                task_id TEXT,
                timestamp TEXT,
                level TEXT,
                message TEXT,
                data TEXT,
                action_taken TEXT
            )
        """)

        conn.commit()
        return conn

    def add_task(
        self,
        name: str,
        type: str,
        source: str,
        keywords: List[str],
        target_urls: List[str],
        interval: int,
        threshold: str,
        action: str
    ) -> MonitorTask:
        """
        添加监控任务

        Args:
            name: 任务名称
            type: 任务类型
            source: 数据源
            keywords: 关键词
            target_urls: 目标URL
            interval: 监控间隔（秒）
            threshold: 阈值规则
            action: 动作

        Returns:
            监控任务
        """
        import uuid

        task_id = f"task_{uuid.uuid4().hex[:8]}"

        task = MonitorTask(
            task_id=task_id,
            name=name,
            type=TaskType(type),
            source=source,
            keywords=keywords,
            target_urls=target_urls,
            interval=interval,
            threshold=threshold,
            action=action,
            enabled=True,
            last_check=None,
            last_value=None
        )

        self.tasks.append(task)

        # 保存到数据库
        self._save_task(task)

        logger.info(f"添加监控任务: {name} ({task_id})")
        return task

    def _save_task(self, task: MonitorTask):
        """保存任务到数据库"""
        cursor = self.db_conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO tasks
            (task_id, name, type, source, keywords, target_urls, interval, threshold, action, enabled, last_check, last_value)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task.task_id,
            task.name,
            task.type.value,
            task.source,
            json.dumps(task.keywords),
            json.dumps(task.target_urls),
            task.interval,
            task.threshold,
            task.action,
            1 if task.enabled else 0,
            task.last_check.isoformat() if task.last_check else None,
            json.dumps(task.last_value) if task.last_value else None
        ))

        self.db_conn.commit()

    def load_tasks_from_db(self):
        """从数据库加载任务"""
        cursor = self.db_conn.cursor()

        cursor.execute("SELECT * FROM tasks")
        rows = cursor.fetchall()

        for row in rows:
            task = MonitorTask(
                task_id=row[0],
                name=row[1],
                type=TaskType(row[2]),
                source=row[3],
                keywords=json.loads(row[4]),
                target_urls=json.loads(row[5]),
                interval=row[6],
                threshold=row[7],
                action=row[8],
                enabled=bool(row[9]),
                last_check=datetime.fromisoformat(row[10]) if row[10] else None,
                last_value=json.loads(row[11]) if row[11] else None
            )
            self.tasks.append(task)

        logger.info(f"从数据库加载 {len(self.tasks)} 个任务")

    def start(self):
        """启动监控"""
        if self.is_running:
            logger.warning("监控已在运行中")
            return

        self.is_running = True
        self.worker_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.worker_thread.start()

        logger.info("监控已启动")

    def stop(self):
        """停止监控"""
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)

        logger.info("监控已停止")

    def _monitor_loop(self):
        """监控循环"""
        while self.is_running:
            try:
                current_time = datetime.now()

                for task in self.tasks:
                    if not task.enabled:
                        continue

                    # 检查是否需要执行
                    if task.last_check is None or \
                       (current_time - task.last_check).total_seconds() >= task.interval:

                        self._check_task(task)

                time.sleep(1)

            except Exception as e:
                logger.error(f"监控循环异常: {e}")

    def _check_task(self, task: MonitorTask):
        """
        检查任务

        Args:
            task: 监控任务
        """
        try:
            # 获取数据
            data = self._fetch_data(task)

            if data:
                # 检查变化
                try:
                    if self._check_threshold(task, data):
                        # 触发预警
                        self._trigger_alert(task, data)
                except Exception as e:
                    logger.error(f"触发预警失败: {e}")

                # 更新任务（即使预警失败也要更新）
                task.last_check = datetime.now()
                task.last_value = data["value"]
                self._save_task(task)

        except Exception as e:
            logger.error(f"检查任务失败 {task.task_id}: {e}")

    def _fetch_data(self, task: MonitorTask) -> Optional[Dict]:
        """
        获取数据

        Args:
            task: 监控任务

        Returns:
            数据
        """
        # 模拟获取数据
        # 实际使用时调用各平台API
        if task.type == TaskType.PRICE:
            return self._fetch_price_data(task)
        elif task.type == TaskType.NEWS:
            return self._fetch_news_data(task)
        elif task.type == TaskType.COMPETITOR:
            return self._fetch_competitor_data(task)

        return None

    def _fetch_price_data(self, task: MonitorTask) -> Optional[Dict]:
        """获取价格数据"""
        # 模拟价格数据
        import random

        price = random.uniform(3000, 10000)

        return {
            "type": "price",
            "value": price,
            "source": task.source,
            "keywords": task.keywords,
            "timestamp": datetime.now().isoformat()
        }

    def _fetch_news_data(self, task: MonitorTask) -> Optional[Dict]:
        """获取新闻数据"""
        # 模拟新闻数据
        news_list = [
            "OpenAI发布新版本GPT-5",
            "百度文心一言升级",
            "腾讯推出AI助手",
            "阿里云AI服务降价"
        ]

        import random

        news = random.choice(news_list)
        contains_keyword = any(keyword in news for keyword in task.keywords)

        return {
            "type": "news",
            "value": {
                "title": news,
                "contains_keyword": contains_keyword
            },
            "source": task.source,
            "keywords": task.keywords,
            "timestamp": datetime.now().isoformat()
        }

    def _fetch_competitor_data(self, task: MonitorTask) -> Optional[Dict]:
        """获取竞品数据"""
        # 模拟竞品数据
        import random

        competitor_prices = {
            "comp_1": random.uniform(3000, 10000),
            "comp_2": random.uniform(3000, 10000)
        }

        return {
            "type": "competitor",
            "value": competitor_prices,
            "source": task.source,
            "target_urls": task.target_urls,
            "timestamp": datetime.now().isoformat()
        }

    def _check_threshold(self, task: MonitorTask, data: Dict) -> bool:
        """
        检查阈值

        Args:
            task: 监控任务
            data: 数据

        Returns:
            是否触发
        """
        # 简化的阈值检查
        # 实际使用时解析和执行threshold规则

        if task.type == TaskType.PRICE:
            # 价格变化检测
            current_price = data["value"]
            if task.last_value:
                old_price = task.last_value
                change_percent = ((current_price - old_price) / old_price * 100)
                return abs(change_percent) > 5  # 变化超过5%

        elif task.type == TaskType.NEWS:
            # 关键词匹配
            return data["value"]["contains_keyword"]

        return False

    def _trigger_alert(self, task: MonitorTask, data: Dict):
        """
        触发预警

        Args:
            task: 监控任务
            data: 数据
        """
        import uuid

        alert_id = f"alert_{uuid.uuid4().hex[:8]}"

        # 确定预警级别
        if task.type == TaskType.PRICE:
            level = AlertLevel.WARNING
            message = f"价格变化: {task.name}"
        elif task.type == TaskType.NEWS:
            level = AlertLevel.INFO
            message = f"关键词匹配: {task.name}"
        else:
            level = AlertLevel.INFO
            message = f"数据变化: {task.name}"

        alert = Alert(
            alert_id=alert_id,
            task_id=task.task_id,
            timestamp=datetime.now(),
            level=level,
            message=message,
            data=data,
            action_taken=task.action
        )

        self.alerts.append(alert)

        # 保存到数据库
        self._save_alert(alert)

        logger.warning(f"[{level.value.upper()}] {task.name}: {message}")

        # 执行动作
        self._execute_action(alert)

    def _save_alert(self, alert: Alert):
        """保存预警到数据库"""
        cursor = self.db_conn.cursor()

        cursor.execute("""
            INSERT INTO alerts
            (alert_id, task_id, timestamp, level, message, data, action_taken)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            alert.alert_id,
            alert.task_id,
            alert.timestamp.isoformat(),
            alert.level.value,
            alert.message,
            json.dumps(alert.data),
            alert.action_taken
        ))

        self.db_conn.commit()

    def _execute_action(self, alert: Alert):
        """
        执行动作

        Args:
            alert: 预警
        """
        # 解析动作
        if alert.action_taken.startswith("webhook:"):
            url = alert.action_taken.split(":", 1)[1]
            self._send_webhook(url, alert)
        elif alert.action_taken.startswith("feishu:"):
            self._send_feishu(alert)

    def _send_webhook(self, url: str, alert: Alert):
        """发送Webhook"""
        try:
            data = {
                "alert_id": alert.alert_id,
                "task_id": alert.task_id,
                "timestamp": alert.timestamp.isoformat(),
                "level": alert.level.value,
                "message": alert.message,
                "data": alert.data
            }

            response = requests.post(url, json=data, timeout=10)
            logger.info(f"Webhook发送成功: {response.status_code}")
        except Exception as e:
            logger.error(f"Webhook发送失败: {e}")

    def _send_feishu(self, alert: Alert):
        """发送飞书通知"""
        logger.info(f"发送飞书通知: {alert.message}")
        # 实际实现需要集成飞书Webhook

    def list_tasks(self) -> List[Dict]:
        """列出所有任务"""
        return [asdict(task) for task in self.tasks]

    def get_task(self, task_id: str) -> Optional[MonitorTask]:
        """获取任务"""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None

    def get_recent_alerts(self, hours: int = 24) -> List[Alert]:
        """获取最近的预警"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [alert for alert in self.alerts if alert.timestamp >= cutoff]

    def export_data(self, task_id: str, start_date: str, end_date: str) -> List[Dict]:
        """
        导出监控数据

        Args:
            task_id: 任务ID
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            数据列表
        """
        # 从数据库查询数据
        cursor = self.db_conn.cursor()

        cursor.execute("""
            SELECT * FROM monitor_data
            WHERE task_id = ? AND timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp DESC
        """, (task_id, start_date, end_date))

        rows = cursor.fetchall()
        return [dict(zip([col[0] for col in cursor.description], row)) for row in rows]


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="实时数据监控系统")
    parser.add_argument("command", choices=["add", "list", "show", "start", "history"],
                        help="命令")
    parser.add_argument("--name", help="任务名称")
    parser.add_argument("--type", choices=["price", "news", "competitor"], help="任务类型")
    parser.add_argument("--source", help="数据源")
    parser.add_argument("--keywords", nargs="+", help="关键词")
    parser.add_argument("--target_urls", nargs="+", help="目标URL")
    parser.add_argument("--interval", type=int, help="监控间隔（秒）")
    parser.add_argument("--threshold", help="阈值规则")
    parser.add_argument("--action", help="动作")
    parser.add_argument("--task_id", help="任务ID")

    args = parser.parse_args()

    # 创建监控引擎
    engine = MonitorEngine()

    if args.command == "add":
        task = engine.add_task(
            name=args.name,
            type=args.type,
            source=args.source,
            keywords=args.keywords or [],
            target_urls=args.target_urls or [],
            interval=args.interval,
            threshold=args.threshold,
            action=args.action
        )
        print(f"任务创建成功: {task.task_id}")

    elif args.command == "list":
        tasks = engine.list_tasks()
        print(f"共有 {len(tasks)} 个任务:")
        for task in tasks:
            print(f"  - {task['task_id']}: {task['name']} ({task['type']})")

    elif args.command == "show":
        task = engine.get_task(args.task_id)
        if task:
            print(json.dumps(asdict(task), ensure_ascii=False, indent=2))
        else:
            print(f"未找到任务: {args.task_id}")

    elif args.command == "start":
        # 加载任务
        engine.load_tasks_from_db()

        # 启动监控
        engine.start()
        print("监控已启动，按 Ctrl+C 停止")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            engine.stop()

    elif args.command == "history":
        data = engine.export_data(
            task_id=args.task_id,
            start_date="2026-01-01",
            end_date="2026-12-31"
        )
        print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
