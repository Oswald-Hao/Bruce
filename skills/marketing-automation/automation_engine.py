#!/usr/bin/env python3
"""
自动化营销 - 自动化流程引擎
Marketing Automation - Automation Flow Engine
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass, asdict, field
from pathlib import Path
from enum import Enum


class TriggerType(Enum):
    """触发器类型"""
    USER_SIGNUP = "user_signup"
    USER_LOGIN = "user_login"
    PURCHASE_MADE = "purchase_made"
    CART_ABANDONED = "cart_abandoned"
    BIRTHDAY = "birthday"
    TAG_ADDED = "tag_added"
    CUSTOM = "custom"


class ActionType(Enum):
    """动作类型"""
    SEND_EMAIL = "send_email"
    SEND_SMS = "send_sms"
    SEND_WECHAT = "send_wechat"
    SEND_APP_PUSH = "send_app_push"
    ADD_TAG = "add_tag"
    REMOVE_TAG = "remove_tag"
    UPDATE_FIELD = "update_field"
    WAIT = "wait"
    CUSTOM = "custom"


@dataclass
class Trigger:
    """触发器"""
    type: TriggerType
    conditions: Dict = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)


@dataclass
class Action:
    """动作"""
    type: ActionType
    params: Dict = field(default_factory=dict)
    delay_minutes: int = 0
    delay_hours: int = 0
    delay_days: int = 0


@dataclass
class FlowStep:
    """流程步骤"""
    id: str
    trigger: Optional[Trigger] = None
    action: Optional[Action] = None
    next_step_ids: List[str] = field(default_factory=list)


@dataclass
class AutomationFlow:
    """自动化流程"""
    id: str
    name: str
    description: str = ""
    status: str = "draft"  # draft, active, paused
    created_at: str = None
    steps: Dict[str, FlowStep] = field(default_factory=dict)
    entry_points: List[str] = field(default_factory=list)
    stats: Dict = field(default_factory=dict)

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if not self.stats:
            self.stats = {
                "triggered": 0,
                "executed": 0,
                "failed": 0
            }


@dataclass
class FlowExecution:
    """流程执行记录"""
    id: str
    flow_id: str
    customer_id: str
    status: str = "running"  # running, completed, failed
    started_at: str = None
    completed_at: str = None
    current_step_id: str = None
    context: Dict = field(default_factory=dict)
    history: List[Dict] = field(default_factory=list)

    def __post_init__(self):
        if self.started_at is None:
            self.started_at = datetime.now().isoformat()


class AutomationEngine:
    """自动化流程引擎"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.flows = {}
        self.executions = {}

        self._load_data()

    def _load_data(self):
        """加载数据"""
        flows_file = self.data_dir / "automation_flows.json"
        if flows_file.exists():
            with open(flows_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for id_, flow_data in data.items():
                    # 重建步骤对象
                    steps_data = flow_data.get("steps", {})
                    steps = {}
                    for step_id, step_data in steps_data.items():
                        trigger_data = step_data.get("trigger")
                        action_data = step_data.get("action")

                        trigger = Trigger(**trigger_data) if trigger_data else None
                        action = Action(**action_data) if action_data else None

                        steps[step_id] = FlowStep(
                            id=step_id,
                            trigger=trigger,
                            action=action,
                            next_step_ids=step_data.get("next_step_ids", [])
                        )

                    flow_data["steps"] = steps
                    self.flows[id_] = AutomationFlow(**flow_data)

        executions_file = self.data_dir / "flow_executions.json"
        if executions_file.exists():
            with open(executions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for id_, execution_data in data.items():
                    self.executions[id_] = FlowExecution(**execution_data)

    def _save_data(self):
        """保存数据"""
        def serialize_flow(flow):
            flow_dict = asdict(flow)
            # 序列化步骤中的枚举类型
            steps_data = {}
            for step_id, step in flow_dict["steps"].items():
                if "trigger" in step and step["trigger"]:
                    if isinstance(step["trigger"]["type"], TriggerType):
                        step["trigger"]["type"] = step["trigger"]["type"].value
                if "action" in step and step["action"]:
                    if isinstance(step["action"]["type"], ActionType):
                        step["action"]["type"] = step["action"]["type"].value
                steps_data[step_id] = step
            flow_dict["steps"] = steps_data
            return flow_dict

        flows_file = self.data_dir / "automation_flows.json"
        flows_data = {id_: serialize_flow(flow) for id_, flow in self.flows.items()}
        with open(flows_file, 'w', encoding='utf-8') as f:
            json.dump(flows_data, f, indent=2, ensure_ascii=False)

        executions_file = self.data_dir / "flow_executions.json"
        executions_data = {id_: asdict(execution) for id_, execution in self.executions.items()}
        with open(executions_file, 'w', encoding='utf-8') as f:
            json.dump(executions_data, f, indent=2, ensure_ascii=False)

    # ========== 流程管理 ==========

    def create_flow(self, name: str, description: str = "") -> AutomationFlow:
        """创建自动化流程"""
        flow_id = str(uuid.uuid4())
        flow = AutomationFlow(
            id=flow_id,
            name=name,
            description=description
        )
        self.flows[flow_id] = flow
        self._save_data()
        return flow

    def get_flow(self, flow_id: str) -> Optional[AutomationFlow]:
        """获取流程"""
        return self.flows.get(flow_id)

    def list_flows(self, status: str = None) -> List[AutomationFlow]:
        """列出流程"""
        flows = list(self.flows.values())

        if status:
            flows = [f for f in flows if f.status == status]

        return flows

    def delete_flow(self, flow_id: str) -> bool:
        """删除流程"""
        if flow_id in self.flows:
            del self.flows[flow_id]
            self._save_data()
            return True
        return False

    def activate_flow(self, flow_id: str) -> bool:
        """激活流程"""
        flow = self.flows.get(flow_id)
        if flow:
            flow.status = "active"
            self._save_data()
            return True
        return False

    def pause_flow(self, flow_id: str) -> bool:
        """暂停流程"""
        flow = self.flows.get(flow_id)
        if flow:
            flow.status = "paused"
            self._save_data()
            return True
        return False

    # ========== 步骤管理 ==========

    def add_trigger(
        self,
        flow_id: str,
        trigger_type: TriggerType,
        conditions: Dict = None,
        metadata: Dict = None
    ) -> Optional[FlowStep]:
        """添加触发器步骤"""
        flow = self.flows.get(flow_id)
        if not flow:
            return None

        step_id = str(uuid.uuid4())
        trigger = Trigger(
            type=trigger_type,
            conditions=conditions or {},
            metadata=metadata or {}
        )

        step = FlowStep(id=step_id, trigger=trigger)
        flow.steps[step_id] = step
        flow.entry_points.append(step_id)
        self._save_data()

        return step

    def add_action(
        self,
        flow_id: str,
        previous_step_id: str,
        action_type: ActionType,
        params: Dict = None,
        delay_minutes: int = 0,
        delay_hours: int = 0,
        delay_days: int = 0
    ) -> Optional[FlowStep]:
        """添加动作步骤"""
        flow = self.flows.get(flow_id)
        if not flow:
            return None

        step_id = str(uuid.uuid4())
        action = Action(
            type=action_type,
            params=params or {},
            delay_minutes=delay_minutes,
            delay_hours=delay_hours,
            delay_days=delay_days
        )

        step = FlowStep(id=step_id, action=action)

        # 链接步骤
        flow.steps[step_id] = step
        if previous_step_id in flow.steps:
            flow.steps[previous_step_id].next_step_ids.append(step_id)

        self._save_data()

        return step

    # ========== 流程执行 ==========

    def trigger_flow(self, flow_id: str, customer_id: str, context: Dict = None) -> Optional[FlowExecution]:
        """触发流程"""
        flow = self.flows.get(flow_id)
        if not flow or flow.status != "active":
            return None

        execution_id = str(uuid.uuid4())
        execution = FlowExecution(
            id=execution_id,
            flow_id=flow_id,
            customer_id=customer_id,
            context=context or {}
        )

        # 从入口点开始执行
        if flow.entry_points:
            execution.current_step_id = flow.entry_points[0]

        self.executions[execution_id] = execution
        flow.stats["triggered"] += 1
        self._save_data()

        # 执行第一步
        self._execute_step(execution_id)

        return execution

    def _execute_step(self, execution_id: str):
        """执行步骤"""
        execution = self.executions.get(execution_id)
        if not execution:
            return

        flow = self.flows.get(execution.flow_id)
        if not flow:
            return

        step = flow.steps.get(execution.current_step_id)
        if not step:
            return

        try:
            if step.trigger:
                # 触发器步骤，检查条件
                result = self._evaluate_trigger(step.trigger, execution.context)
                if result:
                    self._record_execution(execution, step.id, "triggered", {})
                    # 转到下一步
                    if step.next_step_ids:
                        execution.current_step_id = step.next_step_ids[0]
                        self._execute_step(execution_id)

            elif step.action:
                # 动作步骤，执行动作
                result = self._execute_action(step.action, execution.context)
                self._record_execution(execution, step.id, "executed", result)

                # 转到下一步
                if step.next_step_ids:
                    execution.current_step_id = step.next_step_ids[0]
                    self._execute_step(execution_id)
                else:
                    # 流程完成
                    execution.status = "completed"
                    execution.completed_at = datetime.now().isoformat()
                    flow.stats["executed"] += 1

            self._save_data()

        except Exception as e:
            execution.status = "failed"
            self._record_execution(execution, step.id, "failed", {"error": str(e)})
            flow.stats["failed"] += 1
            self._save_data()

    def _evaluate_trigger(self, trigger: Trigger, context: Dict) -> bool:
        """评估触发器"""
        # 简化实现：检查触发器类型
        if trigger.type == TriggerType.USER_SIGNUP:
            return context.get("event") == "signup"
        elif trigger.type == TriggerType.USER_LOGIN:
            return context.get("event") == "login"
        elif trigger.type == TriggerType.PURCHASE_MADE:
            return context.get("event") == "purchase"
        elif trigger.type == TriggerType.CART_ABANDONED:
            return context.get("event") == "cart_abandoned"
        elif trigger.type == TriggerType.TAG_ADDED:
            return context.get("event") == "tag_added" and context.get("tag") == trigger.conditions.get("tag")
        else:
            return True

    def _execute_action(self, action: Action, context: Dict) -> Dict:
        """执行动作（模拟）"""
        result = {"action": action.type.value}

        if action.delay_minutes or action.delay_hours or action.delay_days:
            result["delay"] = f"{action.delay_days}d {action.delay_hours}h {action.delay_minutes}m"

        if action.type == ActionType.SEND_EMAIL:
            result["to"] = context.get("email")
            result["subject"] = action.params.get("subject")
            result["body"] = action.params.get("body", "")
        elif action.type == ActionType.SEND_SMS:
            result["to"] = context.get("phone")
            result["message"] = action.params.get("message", "")
        elif action.type == ActionType.ADD_TAG:
            result["tag"] = action.params.get("tag")
        elif action.type == ActionType.REMOVE_TAG:
            result["tag"] = action.params.get("tag")
        elif action.type == ActionType.WAIT:
            result["wait_seconds"] = action.params.get("seconds", 0)

        return result

    def _record_execution(self, execution: FlowExecution, step_id: str, status: str, result: Dict):
        """记录执行历史"""
        history_entry = {
            "step_id": step_id,
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "result": result
        }
        execution.history.append(history_entry)

    # ========== 执行记录 ==========

    def get_execution(self, execution_id: str) -> Optional[FlowExecution]:
        """获取执行记录"""
        return self.executions.get(execution_id)

    def list_executions(self, flow_id: str = None, customer_id: str = None) -> List[FlowExecution]:
        """列出执行记录"""
        executions = list(self.executions.values())

        if flow_id:
            executions = [e for e in executions if e.flow_id == flow_id]

        if customer_id:
            executions = [e for e in executions if e.customer_id == customer_id]

        return executions

    # ========== 快捷方法 ==========

    def create_welcome_flow(self) -> AutomationFlow:
        """创建欢迎流程模板"""
        flow = self.create_flow("欢迎流程", "新用户注册欢迎流程")

        # 触发器：用户注册
        self.add_trigger(flow.id, TriggerType.USER_SIGNUP)

        # 动作1：立即发送欢迎邮件
        self.add_action(
            flow.id,
            flow.entry_points[0],
            ActionType.SEND_EMAIL,
            params={
                "subject": "欢迎加入我们！",
                "body": "亲爱的用户，欢迎加入我们的大家庭！"
            }
        )

        # 动作2：24小时后发送新手指南
        previous_step = list(flow.steps.values())[-1]
        self.add_action(
            flow.id,
            previous_step.id,
            ActionType.SEND_EMAIL,
            params={
                "subject": "新手指南",
                "body": "这里是新手指南，帮助您快速上手。"
            },
            delay_hours=24
        )

        # 动作3：7天后发送专属优惠码
        previous_step = list(flow.steps.values())[-1]
        self.add_action(
            flow.id,
            previous_step.id,
            ActionType.SEND_EMAIL,
            params={
                "subject": "专属优惠码",
                "body": "这是您的专属优惠码：WELCOME10"
            },
            delay_days=7
        )

        return flow

    def create_cart_recovery_flow(self) -> AutomationFlow:
        """创建购物车召回流程"""
        flow = self.create_flow("购物车召回流程", "购物车放弃召回流程")

        # 触发器：购物车有商品但未支付
        self.add_trigger(
            flow.id,
            TriggerType.CART_ABANDONED,
            conditions={"abandoned_minutes": 60}
        )

        # 动作1：1小时后发送提醒
        self.add_action(
            flow.id,
            flow.entry_points[0],
            ActionType.SEND_EMAIL,
            params={
                "subject": "您还有商品未支付",
                "body": "您的购物车里还有商品等待结算！"
            },
            delay_minutes=60
        )

        # 动作2：24小时后发送优惠券
        previous_step = list(flow.steps.values())[-1]
        self.add_action(
            flow.id,
            previous_step.id,
            ActionType.SEND_EMAIL,
            params={
                "subject": "限时优惠券",
                "body": "这是一张5%的优惠券，助您完成购买！"
            },
            delay_hours=23
        )

        return flow


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="自动化流程引擎")
    subparsers = parser.add_subparsers(dest="command", help="命令")

    # 创建流程
    create_parser = subparsers.add_parser("create", help="创建流程")
    create_parser.add_argument("--name", required=True, help="流程名称")
    create_parser.add_argument("--description", help="描述")

    # 列出流程
    list_parser = subparsers.add_parser("list", help="列出流程")
    list_parser.add_argument("--status", choices=["draft", "active", "paused"], help="按状态筛选")

    # 激活流程
    activate_parser = subparsers.add_parser("activate", help="激活流程")
    activate_parser.add_argument("--flow", required=True, help="流程ID或名称")

    # 暂停流程
    pause_parser = subparsers.add_parser("pause", help="暂停流程")
    pause_parser.add_argument("--flow", required=True, help="流程ID或名称")

    # 触发流程
    trigger_parser = subparsers.add_parser("trigger", help="触发流程")
    trigger_parser.add_argument("--flow", required=True, help="流程ID或名称")
    trigger_parser.add_argument("--customer", required=True, help="客户ID")

    # 列出执行记录
    executions_parser = subparsers.add_parser("executions", help="列出执行记录")
    executions_parser.add_argument("--flow", help="流程ID")
    executions_parser.add_argument("--customer", help="客户ID")

    # 创建欢迎流程模板
    subparsers.add_parser("template-welcome", help="创建欢迎流程模板")

    # 创建购物车召回模板
    subparsers.add_parser("template-cart", help="创建购物车召回模板")

    args = parser.parse_args()

    engine = AutomationEngine()

    if args.command == "create":
        flow = engine.create_flow(args.name, args.description or "")
        print(f"✅ 流程已创建: {flow.id}")
        print(f"   名称: {flow.name}")

    elif args.command == "list":
        flows = engine.list_flows(status=args.status)
        print(f"自动化流程列表 ({len(flows)}):")
        for f in flows:
            print(f"  [{f.id[:8]}] {f.name} ({f.status})")
            print(f"    入口点: {len(f.entry_points)}")
            print(f"    步骤数: {len(f.steps)}")

    elif args.command == "activate":
        flow = None
        for f in engine.flows.values():
            if f.id == args.flow or f.name == args.flow:
                flow = f
                break

        if not flow:
            print(f"❌ 未找到流程: {args.flow}")
            return

        if engine.activate_flow(flow.id):
            print(f"✅ 流程已激活: {flow.name}")
        else:
            print(f"❌ 激活失败")

    elif args.command == "pause":
        flow = None
        for f in engine.flows.values():
            if f.id == args.flow or f.name == args.flow:
                flow = f
                break

        if not flow:
            print(f"❌ 未找到流程: {args.flow}")
            return

        if engine.pause_flow(flow.id):
            print(f"✅ 流程已暂停: {flow.name}")
        else:
            print(f"❌ 暂停失败")

    elif args.command == "trigger":
        flow = None
        for f in engine.flows.values():
            if f.id == args.flow or f.name == args.flow:
                flow = f
                break

        if not flow:
            print(f"❌ 未找到流程: {args.flow}")
            return

        execution = engine.trigger_flow(flow.id, args.customer, context={"event": "signup"})
        if execution:
            print(f"✅ 流程已触发: {flow.name}")
            print(f"   执行ID: {execution.id}")
            print(f"   状态: {execution.status}")
        else:
            print(f"❌ 触发失败（流程可能未激活）")

    elif args.command == "executions":
        executions = engine.list_executions(
            flow_id=getattr(args, 'flow', None),
            customer_id=getattr(args, 'customer', None)
        )
        print(f"执行记录列表 ({len(executions)}):")
        for e in executions:
            flow = engine.flows.get(e.flow_id)
            print(f"  [{e.id[:8]}] {flow.name if flow else e.flow_id} -> {e.customer_id} ({e.status})")
            print(f"    步骤: {len(e.history)}")

    elif args.command == "template-welcome":
        flow = engine.create_welcome_flow()
        print(f"✅ 欢迎流程模板已创建: {flow.id}")
        print(f"   步骤数: {len(flow.steps)}")

    elif args.command == "template-cart":
        flow = engine.create_cart_recovery_flow()
        print(f"✅ 购物车召回模板已创建: {flow.id}")
        print(f"   步骤数: {len(flow.steps)}")


if __name__ == "__main__":
    main()
