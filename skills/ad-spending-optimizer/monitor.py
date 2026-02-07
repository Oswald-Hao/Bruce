#!/usr/bin/env python3
"""
广告投放实时监控器
实时监控广告投放数据，异常预警
"""

import json
import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """预警级别"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Alert:
    """预警"""
    timestamp: datetime
    level: AlertLevel
    platform: str
    campaign_id: str
    message: str
    metric: str
    current_value: float
    threshold: float


@dataclass
class MonitorConfig:
    """监控配置"""
    platform: str
    account: str
    interval: int  # 监控间隔（秒）
    alerts_enabled: bool
    alert_channels: List[str]  # 预警渠道（email/webhook等）
    thresholds: Dict[str, float]  # 各指标的阈值


class AdMonitor:
    """广告监控器"""

    def __init__(self, config: MonitorConfig):
        """
        初始化广告监控器

        Args:
            config: 监控配置
        """
        self.config = config
        self.alerts: List[Alert] = []
        self.is_running = False
        self.monitor_thread = None
        self.alert_callbacks: List[Callable[[Alert], None]] = []

    def add_alert_callback(self, callback: Callable[[Alert], None]):
        """
        添加预警回调函数

        Args:
            callback: 回调函数
        """
        self.alert_callbacks.append(callback)

    def start(self):
        """启动监控"""
        if self.is_running:
            logger.warning("监控已在运行中")
            return

        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

        logger.info(f"监控已启动，平台: {self.config.platform}, 间隔: {self.config.interval}秒")

    def stop(self):
        """停止监控"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

        logger.info("监控已停止")

    def _monitor_loop(self):
        """监控循环"""
        while self.is_running:
            try:
                self._check_metrics()
                time.sleep(self.config.interval)
            except Exception as e:
                logger.error(f"监控循环异常: {e}")

    def _check_metrics(self):
        """检查指标"""
        # 模拟获取实时指标
        # 实际使用时调用各平台API
        campaigns = self._fetch_realtime_metrics()

        for campaign in campaigns:
            # 检查各指标
            self._check_thresholds(campaign)

    def _fetch_realtime_metrics(self) -> List[Dict]:
        """
        获取实时指标

        Returns:
            活动指标列表
        """
        # 模拟实时数据
        campaigns = []

        for i in range(1, 6):
            cpa = random.uniform(50, 200)
            ctr = random.uniform(0.5, 3.5)
            roi = random.uniform(-50, 300)

            campaigns.append({
                "campaign_id": f"cmp_{i}",
                "name": f"广告活动_{i}",
                "cpa": cpa,
                "ctr": ctr,
                "roi": roi,
                "spent": random.uniform(1000, 5000)
            })

        return campaigns

    def _check_thresholds(self, campaign: Dict):
        """
        检查阈值

        Args:
            campaign: 活动数据
        """
        # CPA检查
        if "cpa" in self.config.thresholds:
            max_cpa = self.config.thresholds["cpa"]
            current_cpa = campaign.get("cpa", 0)

            if current_cpa > max_cpa:
                self._trigger_alert(
                    level=AlertLevel.WARNING,
                    campaign_id=campaign["campaign_id"],
                    message=f"CPA ({current_cpa:.2f}) 超过阈值 ({max_cpa:.2f})",
                    metric="cpa",
                    current_value=current_cpa,
                    threshold=max_cpa
                )

        # CTR检查
        if "ctr" in self.config.thresholds:
            min_ctr = self.config.thresholds["ctr"]
            current_ctr = campaign.get("ctr", 0)

            if current_ctr < min_ctr:
                self._trigger_alert(
                    level=AlertLevel.WARNING,
                    campaign_id=campaign["campaign_id"],
                    message=f"CTR ({current_ctr:.2f}%) 低于阈值 ({min_ctr:.2f}%)",
                    metric="ctr",
                    current_value=current_ctr,
                    threshold=min_ctr
                )

        # ROI检查
        if "roi" in self.config.thresholds:
            min_roi = self.config.thresholds["roi"]
            current_roi = campaign.get("roi", 0)

            if current_roi < min_roi:
                level = AlertLevel.CRITICAL if current_roi < 0 else AlertLevel.WARNING
                self._trigger_alert(
                    level=level,
                    campaign_id=campaign["campaign_id"],
                    message=f"ROI ({current_roi:.2f}%) 低于阈值 ({min_roi:.2f}%)",
                    metric="roi",
                    current_value=current_roi,
                    threshold=min_roi
                )

    def _trigger_alert(
        self,
        level: AlertLevel,
        campaign_id: str,
        message: str,
        metric: str,
        current_value: float,
        threshold: float
    ):
        """
        触发预警

        Args:
            level: 预警级别
            campaign_id: 活动ID
            message: 预警消息
            metric: 指标名称
            current_value: 当前值
            threshold: 阈值
        """
        alert = Alert(
            timestamp=datetime.now(),
            level=level,
            platform=self.config.platform,
            campaign_id=campaign_id,
            message=message,
            metric=metric,
            current_value=current_value,
            threshold=threshold
        )

        self.alerts.append(alert)

        logger.warning(f"[{level.value.upper()}] {campaign_id}: {message}")

        # 调用回调函数
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"预警回调异常: {e}")

    def get_recent_alerts(self, hours: int = 24) -> List[Alert]:
        """
        获取最近的预警

        Args:
            hours: 最近几小时

        Returns:
            预警列表
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        return [alert for alert in self.alerts if alert.timestamp >= cutoff]

    def get_alerts_by_level(self, level: AlertLevel) -> List[Alert]:
        """
        按级别获取预警

        Args:
            level: 预警级别

        Returns:
            预警列表
        """
        return [alert for alert in self.alerts if alert.level == level]

    def get_alert_summary(self) -> Dict:
        """
        获取预警摘要

        Returns:
            预警摘要
        """
        summary = {
            "total": len(self.alerts),
            "critical": len(self.get_alerts_by_level(AlertLevel.CRITICAL)),
            "warning": len(self.get_alerts_by_level(AlertLevel.WARNING)),
            "info": len(self.get_alerts_by_level(AlertLevel.INFO)),
            "recent_24h": len(self.get_recent_alerts(24))
        }

        return summary

    def export_alerts(self, format: str = "json") -> str:
        """
        导出预警数据

        Args:
            format: 导出格式（json/csv）

        Returns:
            导出的数据
        """
        if format == "json":
            alerts_data = []
            for alert in self.alerts:
                alert_dict = asdict(alert)
                alert_dict["timestamp"] = alert.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                alert_dict["level"] = alert.level.value
                alerts_data.append(alert_dict)

            return json.dumps(alerts_data, ensure_ascii=False, indent=2)

        elif format == "csv":
            import csv
            import io

            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["timestamp", "level", "platform", "campaign_id", "message", "metric", "current_value", "threshold"])

            for alert in self.alerts:
                writer.writerow([
                    alert.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    alert.level.value,
                    alert.platform,
                    alert.campaign_id,
                    alert.message,
                    alert.metric,
                    alert.current_value,
                    alert.threshold
                ])

            return output.getvalue()

        else:
            raise ValueError(f"不支持的格式: {format}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="广告投放实时监控器")
    parser.add_argument("--platform", required=True, choices=["baidu", "tencent", "google", "facebook"],
                        help="广告平台")
    parser.add_argument("--account", required=True, help="账户ID")
    parser.add_argument("--interval", type=int, default=60, help="监控间隔（秒）")
    parser.add_argument("--duration", type=int, default=300, help="监控时长（秒）")
    parser.add_argument("--max_cpa", type=float, help="最大CPA阈值")
    parser.add_argument("--min_ctr", type=float, help="最小CTR阈值（%）")
    parser.add_argument("--min_roi", type=float, help="最小ROI阈值（%）")
    parser.add_argument("--output", help="输出文件路径")

    args = parser.parse_args()

    # 配置阈值
    thresholds = {}
    if args.max_cpa:
        thresholds["cpa"] = args.max_cpa
    if args.min_ctr:
        thresholds["ctr"] = args.min_ctr
    if args.min_roi:
        thresholds["roi"] = args.min_roi

    # 创建监控配置
    config = MonitorConfig(
        platform=args.platform,
        account=args.account,
        interval=args.interval,
        alerts_enabled=True,
        alert_channels=[],
        thresholds=thresholds
    )

    # 创建监控器
    monitor = AdMonitor(config)

    # 添加预警回调
    def alert_callback(alert: Alert):
        print(f"\n🚨 [{alert.level.value.upper()}] {alert.campaign_id}")
        print(f"   消息: {alert.message}")
        print(f"   当前值: {alert.current_value:.2f}, 阈值: {alert.threshold:.2f}\n")

    monitor.add_alert_callback(alert_callback)

    # 启动监控
    monitor.start()

    print(f"监控已启动，平台: {args.platform}")
    print(f"监控时长: {args.duration} 秒")
    print("按 Ctrl+C 停止监控\n")

    try:
        # 等待指定时长或手动停止
        time.sleep(args.duration)
    except KeyboardInterrupt:
        print("\n接收到停止信号")

    # 停止监控
    monitor.stop()

    # 输出预警摘要
    summary = monitor.get_alert_summary()
    print("\n预警摘要:")
    print(f"  总计: {summary['total']}")
    print(f"  严重: {summary['critical']}")
    print(f"  警告: {summary['warning']}")
    print(f"  信息: {summary['info']}")
    print(f"  最近24小时: {summary['recent_24h']}")

    # 导出预警
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(monitor.export_alerts("json"))
        print(f"\n预警数据已保存到: {args.output}")


if __name__ == "__main__":
    main()
