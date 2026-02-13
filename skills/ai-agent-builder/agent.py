#!/usr/bin/env python3
"""
AI Agent开发系统 - 智能代理构建和管理
支持工具调用、记忆管理、对话历史、任务分解和多Agent协作
"""

import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Callable, Optional, Union
from datetime import datetime
from abc import ABC, abstractmethod
import re


@dataclass
class Message:
    """消息基类"""
    role: str  # system, user, assistant, tool
    content: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Tool:
    """工具定义"""
    name: str
    description: str
    parameters: Dict[str, Any]
    function: Callable

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }


@dataclass
class Memory:
    """记忆存储"""
    short_term: List[Message] = field(default_factory=list)
    long_term: Dict[str, Any] = field(default_factory=dict)
    facts: List[Dict[str, Any]] = field(default_factory=list)

    def add_message(self, message: Message):
        """添加消息到短期记忆"""
        self.short_term.append(message)
        # 保持短期记忆在合理大小
        if len(self.short_term) > 100:
            self.short_term = self.short_term[-50:]

    def add_fact(self, fact: str, category: str = "general"):
        """添加事实到记忆"""
        fact_record = {
            "fact": fact,
            "category": category,
            "timestamp": time.time()
        }
        self.facts.append(fact_record)

    def search_facts(self, query: str, top_k: int = 5) -> List[Dict]:
        """搜索相关事实"""
        query_lower = query.lower()
        scored_facts = []

        for fact in self.facts:
            score = 0
            if query_lower in fact["fact"].lower():
                score = 1.0
            elif any(word in fact["fact"].lower() for word in query_lower.split()):
                score = 0.5

            if score > 0:
                scored_facts.append((score, fact))

        # 按分数排序
        scored_facts.sort(key=lambda x: x[0], reverse=True)
        return [fact for _, fact in scored_facts[:top_k]]

    def get_context(self, limit: int = 10) -> List[Dict]:
        """获取上下文"""
        messages = self.short_term[-limit:]
        return [msg.to_dict() for msg in messages]


class BaseAgent(ABC):
    """Agent基类"""

    def __init__(self, name: str, role: str, instructions: str, model: str = "default"):
        self.id = str(uuid.uuid4())
        self.name = name
        self.role = role
        self.instructions = instructions
        self.model = model
        self.memory = Memory()
        self.tools: Dict[str, Tool] = {}
        self.created_at = time.time()
        self.status = "idle"  # idle, thinking, acting, error

    def register_tool(self, tool: Tool):
        """注册工具"""
        self.tools[tool.name] = tool

    def add_tool(self, name: str, description: str, parameters: Dict[str, Any], function: Callable):
        """添加工具"""
        tool = Tool(name=name, description=description, parameters=parameters, function=function)
        self.register_tool(tool)

    def think(self, message: str) -> str:
        """思考并生成响应"""
        self.status = "thinking"

        # 添加用户消息到记忆
        user_msg = Message(role="user", content=message)
        self.memory.add_message(user_msg)

        # 搜索相关记忆
        relevant_facts = self.memory.search_facts(message)

        # 构建上下文
        context = self.memory.get_context()

        # 生成响应（简化版，实际应该调用LLM）
        response = self._generate_response(message, context, relevant_facts)

        # 添加助手消息到记忆
        assistant_msg = Message(role="assistant", content=response)
        self.memory.add_message(assistant_msg)

        self.status = "idle"
        return response

    @abstractmethod
    def _generate_response(self, message: str, context: List[Dict], facts: List[Dict]) -> str:
        """生成响应（子类实现）"""
        pass

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """执行工具"""
        self.status = "acting"

        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")

        tool = self.tools[tool_name]
        try:
            result = tool.function(**parameters)
            self.status = "idle"
            return result
        except Exception as e:
            self.status = "error"
            raise e

    def learn(self, fact: str, category: str = "general"):
        """学习新知识"""
        self.memory.add_fact(fact, category)

    def get_state(self) -> Dict:
        """获取状态"""
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "status": self.status,
            "created_at": self.created_at,
            "tools": list(self.tools.keys()),
            "memory_size": len(self.memory.short_term),
            "facts_count": len(self.memory.facts)
        }

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "instructions": self.instructions,
            "model": self.model,
            "created_at": self.created_at,
            "status": self.status,
            "tools": {name: tool.to_dict() for name, tool in self.tools.items()},
            "memory": {
                "short_term": [msg.to_dict() for msg in self.memory.short_term],
                "long_term": self.memory.long_term,
                "facts": self.memory.facts
            }
        }


class SimpleAgent(BaseAgent):
    """简单Agent实现"""

    def _generate_response(self, message: str, context: List[Dict], facts: List[Dict]) -> str:
        """生成响应"""
        # 检查是否需要调用工具
        tool_calls = self._detect_tool_calls(message)
        if tool_calls:
            return self._execute_tool_calls(tool_calls, message)

        # 检查相关事实
        if facts:
            fact_text = "\n".join([f"• {f['fact']}" for f in facts])
            return f"根据我掌握的信息：\n{fact_text}\n\n这对你有帮助吗？"

        # 基于指令生成响应
        return f"作为{self.role}，我理解你的请求：{message}\n\n{self.instructions}"

    def _detect_tool_calls(self, message: str) -> List[Dict]:
        """检测是否需要调用工具"""
        tool_calls = []

        for tool_name, tool in self.tools.items():
            # 简单的关键词匹配
            keywords = tool_name.split("_")
            if any(keyword.lower() in message.lower() for keyword in keywords):
                tool_calls.append({
                    "name": tool_name,
                    "parameters": {}
                })

        return tool_calls

    def _execute_tool_calls(self, tool_calls: List[Dict], original_message: str) -> str:
        """执行工具调用"""
        results = []

        for call in tool_calls:
            try:
                result = self.execute_tool(call["name"], call["parameters"])
                results.append(f"✓ {call['name']}: {str(result)[:100]}")
            except Exception as e:
                results.append(f"✗ {call['name']}: {str(e)}")

        return f"执行了{len(results)}个操作：\n" + "\n".join(results)


class TaskAgent(SimpleAgent):
    """任务型Agent - 支持任务分解和执行"""

    def __init__(self, name: str, role: str, instructions: str, model: str = "default"):
        super().__init__(name, role, instructions, model)
        self.tasks: List[Dict] = []
        self.current_task: Optional[Dict] = None

    def decompose_task(self, task_description: str) -> List[Dict]:
        """分解任务为子任务"""
        # 简化的任务分解逻辑
        steps = re.split(r'[，,；;。\n]', task_description)
        subtasks = []

        for i, step in enumerate(steps):
            if step.strip():
                subtasks.append({
                    "id": str(uuid.uuid4()),
                    "description": step.strip(),
                    "status": "pending",
                    "order": i + 1
                })

        return subtasks

    def execute_task(self, task_description: str) -> Dict:
        """执行任务"""
        # 分解任务
        subtasks = self.decompose_task(task_description)
        self.tasks = subtasks

        results = {
            "task": task_description,
            "total_steps": len(subtasks),
            "completed": 0,
            "failed": 0,
            "steps": []
        }

        # 执行每个子任务
        for subtask in subtasks:
            self.current_task = subtask
            subtask["status"] = "in_progress"

            try:
                # 这里应该调用LLM或其他执行逻辑
                result = self._execute_subtask(subtask)
                subtask["status"] = "completed"
                subtask["result"] = result
                results["completed"] += 1
            except Exception as e:
                subtask["status"] = "failed"
                subtask["error"] = str(e)
                results["failed"] += 1

            results["steps"].append(subtask.copy())

        self.current_task = None
        return results

    def _execute_subtask(self, subtask: Dict) -> str:
        """执行子任务（示例）"""
        # 简化实现，实际应该更复杂
        return f"完成了: {subtask['description']}"

    def get_task_progress(self) -> Dict:
        """获取任务进度"""
        if not self.tasks:
            return {"total": 0, "completed": 0, "failed": 0, "pending": 0}

        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t["status"] == "completed")
        failed = sum(1 for t in self.tasks if t["status"] == "failed")
        pending = sum(1 for t in self.tasks if t["status"] == "pending")

        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "pending": pending,
            "progress": completed / total if total > 0 else 0
        }


class AgentRegistry:
    """Agent注册表"""

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent):
        """注册Agent"""
        self.agents[agent.id] = agent

    def get(self, agent_id: str) -> Optional[BaseAgent]:
        """获取Agent"""
        return self.agents.get(agent_id)

    def list_agents(self) -> List[Dict]:
        """列出所有Agent"""
        return [agent.get_state() for agent in self.agents.values()]

    def find_by_name(self, name: str) -> List[BaseAgent]:
        """按名称查找Agent"""
        return [agent for agent in self.agents.values() if agent.name == name]

    def remove(self, agent_id: str) -> bool:
        """移除Agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            return True
        return False


class MultiAgentOrchestrator:
    """多Agent协调器"""

    def __init__(self, registry: AgentRegistry):
        self.registry = registry
        self.collaborations: List[Dict] = []

    def create_collaboration(self, task: str, agent_ids: List[str]) -> Dict:
        """创建多Agent协作"""
        collaboration = {
            "id": str(uuid.uuid4()),
            "task": task,
            "agents": agent_ids,
            "status": "active",
            "created_at": time.time(),
            "messages": []
        }
        self.collaborations.append(collaboration)
        return collaboration

    def send_message(self, collaboration_id: str, from_agent_id: str, to_agent_id: str, message: str):
        """在协作中发送消息"""
        # 获取目标Agent
        to_agent = self.registry.get(to_agent_id)
        if not to_agent:
            raise ValueError(f"Agent {to_agent_id} not found")

        # Agent处理消息
        response = to_agent.think(message)

        # 记录消息
        collaboration = next(
            (c for c in self.collaborations if c["id"] == collaboration_id),
            None
        )
        if collaboration:
            collaboration["messages"].append({
                "from": from_agent_id,
                "to": to_agent_id,
                "message": message,
                "response": response,
                "timestamp": time.time()
            })

        return response

    def get_collaboration_status(self, collaboration_id: str) -> Optional[Dict]:
        """获取协作状态"""
        return next(
            (c for c in self.collaborations if c["id"] == collaboration_id),
            None
        )


# 预定义的工具函数
def web_search_tool(query: str) -> str:
    """网络搜索工具"""
    return f"搜索'{query}'的结果：找到5条相关网页"

def calculator_tool(expression: str) -> str:
    """计算器工具"""
    try:
        result = eval(expression)
        return f"计算结果: {result}"
    except:
        return "计算错误"

def file_writer_tool(filename: str, content: str) -> str:
    """文件写入工具"""
    return f"已写入文件 {filename}，共 {len(content)} 个字符"

def database_query_tool(table: str, query: str) -> str:
    """数据库查询工具"""
    return f"查询表 {table}: {query}，找到10条记录"

def email_sender_tool(to: str, subject: str, body: str) -> str:
    """邮件发送工具"""
    return f"已发送邮件给 {to}，主题: {subject}"

def weather_check_tool(city: str) -> str:
    """天气查询工具"""
    return f"{city}当前天气：晴天，25°C"

def data_analyzer_tool(data: str, method: str) -> str:
    """数据分析工具"""
    return f"使用 {method} 分析数据，发现3个趋势"
