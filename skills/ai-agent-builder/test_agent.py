#!/usr/bin/env python3
"""
AI Agent开发系统测试
"""

import sys
import os
import json
import time

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import (
    Message, Tool, Memory, BaseAgent, SimpleAgent,
    TaskAgent, AgentRegistry, MultiAgentOrchestrator,
    web_search_tool, calculator_tool, file_writer_tool,
    database_query_tool, email_sender_tool, weather_check_tool,
    data_analyzer_tool
)


def test_message():
    """测试消息"""
    print("测试 1: Message")

    msg = Message(role="user", content="你好")
    assert msg.role == "user"
    assert msg.content == "你好"
    assert "timestamp" in msg.to_dict()

    print("  ✓ 消息创建成功")
    print("  ✓ 消息转字典成功")
    print("  测试通过!\n")


def test_tool():
    """测试工具"""
    print("测试 2: Tool")

    tool = Tool(
        name="calculator",
        description="计算器",
        parameters={"expression": "str"},
        function=lambda x: "ok"
    )

    assert tool.name == "calculator"
    assert tool.description == "计算器"
    assert "parameters" in tool.to_dict()

    print("  ✓ 工具创建成功")
    print("  ✓ 工具转字典成功")
    print("  测试通过!\n")


def test_memory():
    """测试记忆系统"""
    print("测试 3: Memory")

    memory = Memory()

    # 测试添加消息
    msg1 = Message(role="user", content="消息1")
    msg2 = Message(role="assistant", content="回复1")
    memory.add_message(msg1)
    memory.add_message(msg2)

    assert len(memory.short_term) == 2

    # 测试添加事实
    memory.add_fact("Bruce是一个AI助手", "身份")
    memory.add_fact("Oswald是创造者", "关系")

    assert len(memory.facts) == 2

    # 测试搜索事实
    facts = memory.search_facts("AI")
    assert len(facts) >= 1
    assert "AI" in facts[0]["fact"]

    # 测试获取上下文
    context = memory.get_context()
    assert len(context) == 2
    assert context[0]["content"] == "消息1"

    print("  ✓ 添加消息成功")
    print("  ✓ 添加事实成功")
    print("  ✓ 搜索事实成功")
    print("  ✓ 获取上下文成功")
    print("  测试通过!\n")


def test_simple_agent():
    """测试简单Agent"""
    print("测试 4: SimpleAgent")

    agent = SimpleAgent(
        name="测试助手",
        role="助手",
        instructions="我会尽力帮助你解决问题"
    )

    # 测试基本信息
    assert agent.name == "测试助手"
    assert agent.role == "助手"
    assert agent.id is not None

    # 测试工具注册
    agent.add_tool(
        name="web_search",
        description="网络搜索",
        parameters={"query": "str"},
        function=web_search_tool
    )

    assert "web_search" in agent.tools

    # 测试思考
    response = agent.think("你好")
    assert response is not None
    assert len(response) > 0

    # 测试工具执行
    result = agent.execute_tool("web_search", {"query": "AI"})
    assert "搜索" in result

    # 测试学习
    agent.learn("今天是2026年2月14日", "日期")

    facts = agent.memory.search_facts("2026")
    assert len(facts) > 0

    # 测试状态
    state = agent.get_state()
    assert state["name"] == "测试助手"
    assert state["tools"] == ["web_search"]
    assert state["facts_count"] >= 1

    print("  ✓ Agent创建成功")
    print("  ✓ 工具注册成功")
    print("  ✓ 思考功能正常")
    print("  ✓ 工具执行成功")
    print("  ✓ 学习功能正常")
    print("  ✓ 状态获取成功")
    print("  测试通过!\n")


def test_task_agent():
    """测试任务型Agent"""
    print("测试 5: TaskAgent")

    agent = TaskAgent(
        name="任务助手",
        role="任务执行者",
        instructions="我会分解并执行任务"
    )

    # 测试任务分解
    task = "首先搜索信息，然后分析数据，最后生成报告"
    subtasks = agent.decompose_task(task)

    assert len(subtasks) == 3
    assert subtasks[0]["order"] == 1
    assert subtasks[0]["status"] == "pending"

    # 测试任务执行
    result = agent.execute_task("计算1+2，然后乘以3")

    assert "total_steps" in result
    assert result["total_steps"] >= 1
    assert "steps" in result

    # 测试任务进度
    progress = agent.get_task_progress()
    assert "total" in progress
    assert "completed" in progress
    assert "progress" in progress

    print("  ✓ 任务分解成功")
    print("  ✓ 任务执行成功")
    print("  ✓ 任务进度查询成功")
    print("  测试通过!\n")


def test_agent_registry():
    """测试Agent注册表"""
    print("测试 6: AgentRegistry")

    registry = AgentRegistry()

    # 创建并注册多个Agent
    agent1 = SimpleAgent("助手1", "助手", "帮助1")
    agent2 = SimpleAgent("助手2", "助手", "帮助2")
    agent3 = TaskAgent("任务助手", "任务执行", "执行任务")

    registry.register(agent1)
    registry.register(agent2)
    registry.register(agent3)

    # 测试列出Agent
    agents = registry.list_agents()
    assert len(agents) == 3

    # 测试获取Agent
    retrieved = registry.get(agent1.id)
    assert retrieved is not None
    assert retrieved.name == "助手1"

    # 测试按名称查找
    found = registry.find_by_name("助手1")
    assert len(found) == 1

    # 测试移除Agent
    removed = registry.remove(agent2.id)
    assert removed is True

    agents_after = registry.list_agents()
    assert len(agents_after) == 2

    print("  ✓ 注册Agent成功")
    print("  ✓ 列出Agent成功")
    print("  ✓ 获取Agent成功")
    print("  ✓ 按名称查找成功")
    print("  ✓ 移除Agent成功")
    print("  测试通过!\n")


def test_multi_agent_orchestrator():
    """测试多Agent协调器"""
    print("测试 7: MultiAgentOrchestrator")

    registry = AgentRegistry()

    # 创建Agent
    agent1 = SimpleAgent("搜索专家", "搜索", "负责搜索信息")
    agent2 = SimpleAgent("分析专家", "分析", "负责分析数据")

    registry.register(agent1)
    registry.register(agent2)

    orchestrator = MultiAgentOrchestrator(registry)

    # 测试创建协作
    collaboration = orchestrator.create_collaboration(
        task="分析市场趋势",
        agent_ids=[agent1.id, agent2.id]
    )

    assert collaboration["task"] == "分析市场趋势"
    assert len(collaboration["agents"]) == 2
    assert collaboration["status"] == "active"

    # 测试发送消息
    response = orchestrator.send_message(
        collaboration_id=collaboration["id"],
        from_agent_id=agent1.id,
        to_agent_id=agent2.id,
        message="搜索结果：AI行业增长迅速"
    )

    assert response is not None

    # 测试获取协作状态
    status = orchestrator.get_collaboration_status(collaboration["id"])
    assert status is not None
    assert len(status["messages"]) >= 1

    print("  ✓ 创建协作成功")
    print("  ✓ 发送消息成功")
    print("  ✓ 获取协作状态成功")
    print("  测试通过!\n")


def test_agent_with_multiple_tools():
    """测试Agent使用多个工具"""
    print("测试 8: Agent with Multiple Tools")

    agent = SimpleAgent(
        name="全能助手",
        role="多功能助手",
        instructions="我有多种工具可以使用"
    )

    # 注册多个工具
    agent.add_tool("calculator", "计算器", {"expression": "str"}, calculator_tool)
    agent.add_tool("file_writer", "文件写入", {"filename": "str", "content": "str"}, file_writer_tool)
    agent.add_tool("email_sender", "邮件发送", {"to": "str", "subject": "str", "body": "str"}, email_sender_tool)
    agent.add_tool("weather_check", "天气查询", {"city": "str"}, weather_check_tool)

    assert len(agent.tools) == 4

    # 测试工具调用
    calc_result = agent.execute_tool("calculator", {"expression": "2+2"})
    assert "4" in calc_result

    weather_result = agent.execute_tool("weather_check", {"city": "深圳"})
    assert "深圳" in weather_result

    # 测试状态包含所有工具
    state = agent.get_state()
    assert len(state["tools"]) == 4

    print("  ✓ 注册多个工具成功")
    print("  ✓ 计算器工具执行成功")
    print("  ✓ 天气查询工具执行成功")
    print("  ✓ 状态包含所有工具")
    print("  测试通过!\n")


def test_complex_workflow():
    """测试复杂工作流"""
    print("测试 9: Complex Workflow")

    registry = AgentRegistry()

    # 创建不同角色的Agent
    researcher = SimpleAgent("研究员", "研究", "负责信息收集和分析")
    analyst = TaskAgent("分析师", "分析", "负责深度分析和报告生成")
    reporter = SimpleAgent("报告员", "报告", "负责生成和发送报告")

    # 为每个Agent添加工具
    researcher.add_tool("web_search", "搜索", {"query": "str"}, web_search_tool)
    researcher.add_tool("database_query", "数据库查询", {"table": "str", "query": "str"}, database_query_tool)

    analyst.add_tool("data_analyzer", "数据分析", {"data": "str", "method": "str"}, data_analyzer_tool)

    reporter.add_tool("file_writer", "写文件", {"filename": "str", "content": "str"}, file_writer_tool)
    reporter.add_tool("email_sender", "发邮件", {"to": "str", "subject": "str", "body": "str"}, email_sender_tool)

    registry.register(researcher)
    registry.register(analyst)
    registry.register(reporter)

    # 创建协调器
    orchestrator = MultiAgentOrchestrator(registry)

    # 创建协作任务
    collaboration = orchestrator.create_collaboration(
        task="完成市场调研报告",
        agent_ids=[researcher.id, analyst.id, reporter.id]
    )

    # 模拟工作流
    # 1. 研究员收集信息
    research_response = orchestrator.send_message(
        collaboration["id"],
        researcher.id,
        analyst.id,
        "搜索结果：AI市场规模2025年达到500亿美元，预计2026年增长30%"
    )

    # 2. 分析师分析数据
    analyst.learn("AI市场规模持续增长", "市场")

    # 3. 报告员生成报告
    report_response = orchestrator.send_message(
        collaboration["id"],
        analyst.id,
        reporter.id,
        "分析结果：AI行业正处于快速增长期，推荐投资"
    )

    # 验证工作流
    assert len(collaboration["agents"]) == 3
    assert "messages" in collaboration

    # 验证分析师的知识
    facts = analyst.memory.search_facts("AI")
    assert len(facts) > 0

    # 验证任务分解
    task_result = analyst.execute_task("收集数据，分析趋势，生成报告")
    assert task_result["total_steps"] >= 1

    print("  ✓ 创建多Agent工作流成功")
    print("  ✓ Agent间通信成功")
    print("  ✓ 研究员收集信息成功")
    print("  ✓ 分析师学习知识成功")
    print("  ✓ 任务分解执行成功")
    print("  测试通过!\n")


def test_agent_persistence():
    """测试Agent持久化"""
    print("测试 10: Agent Persistence")

    agent = SimpleAgent(
        name="持久化测试",
        role="测试",
        instructions="测试持久化功能"
    )

    agent.add_tool("calculator", "计算器", {"expression": "str"}, calculator_tool)

    # 添加一些对话历史
    agent.think("你好")
    agent.think("2+2等于多少？")
    agent.learn("今天是测试日", "测试")

    # 转换为字典
    agent_dict = agent.to_dict()

    # 验证关键信息
    assert agent_dict["name"] == "持久化测试"
    assert "calculator" in agent_dict["tools"]
    assert len(agent_dict["memory"]["short_term"]) >= 2
    assert len(agent_dict["memory"]["facts"]) >= 1

    print("  ✓ Agent转字典成功")
    print("  ✓ 包含所有工具信息")
    print("  ✓ 保留对话历史")
    print("  ✓ 保留学习知识")
    print("  测试通过!\n")


def test_memory_capacity():
    """测试记忆容量管理"""
    print("测试 11: Memory Capacity Management")

    memory = Memory()

    # 添加大量消息
    for i in range(150):
        msg = Message(role="user", content=f"消息{i}")
        memory.add_message(msg)

    # 验证短期记忆被限制（保持在100条左右）
    assert len(memory.short_term) <= 100
    assert len(memory.short_term) > 0

    # 验证最新的消息被保留
    last_index = len(memory.short_term) - 1
    assert "消息" in memory.short_term[last_index].content

    # 添加大量事实
    for i in range(50):
        memory.add_fact(f"事实{i}: 关于{i}的信息")

    # 验证所有事实都被保留
    assert len(memory.facts) == 50

    # 测试搜索性能
    start = time.time()
    facts = memory.search_facts("信息")
    search_time = time.time() - start

    assert len(facts) > 0
    assert search_time < 1.0  # 搜索应该在1秒内完成

    print("  ✓ 短期记忆限制正常")
    print("  ✓ 最新消息被保留")
    print("  ✓ 所有事实被保留")
    print("  ✓ 搜索性能良好")
    print("  测试通过!\n")


def test_error_handling():
    """测试错误处理"""
    print("测试 12: Error Handling")

    agent = SimpleAgent("错误测试", "测试", "测试错误处理")

    # 测试执行不存在的工具
    try:
        agent.execute_tool("nonexistent_tool", {})
        assert False, "应该抛出异常"
    except ValueError as e:
        assert "not found" in str(e)

    # 测试工具执行失败
    def failing_tool():
        raise Exception("工具执行失败")

    agent.add_tool("failing", "失败工具", {}, failing_tool)

    try:
        agent.execute_tool("failing", {})
        assert False, "应该抛出异常"
    except Exception as e:
        assert "工具执行失败" in str(e)

    # 验证Agent状态变为error
    assert agent.status == "error"

    # 恢复状态
    agent.think("恢复")
    assert agent.status == "idle"

    # 测试无效的Agent ID
    registry = AgentRegistry()
    result = registry.get("invalid_id")
    assert result is None

    print("  ✓ 不存在工具抛出异常")
    print("  ✓ 工具执行失败被捕获")
    print("  ✓ Agent状态正确更新")
    print("  ✓ 无效ID返回None")
    print("  测试通过!\n")


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("AI Agent开发系统 - 测试套件")
    print("=" * 60)
    print()

    tests = [
        test_message,
        test_tool,
        test_memory,
        test_simple_agent,
        test_task_agent,
        test_agent_registry,
        test_multi_agent_orchestrator,
        test_agent_with_multiple_tools,
        test_complex_workflow,
        test_agent_persistence,
        test_memory_capacity,
        test_error_handling
    ]

    passed = 0
    failed = 0

    start_time = time.time()

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"  ✗ 测试失败: {e}\n")

    end_time = time.time()
    duration = end_time - start_time

    print("=" * 60)
    print(f"测试总结: {passed} 通过, {failed} 失败")
    print(f"用时: {duration:.2f} 秒")
    print(f"通过率: {passed/(passed+failed)*100:.1f}%")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
