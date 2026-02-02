#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书卡片生成器测试脚本
"""

import sys
import json
from card import FeishuCardGenerator


def test_message_card():
    """测试基础消息卡片"""
    print("测试1: 基础消息卡片")
    gen = FeishuCardGenerator()

    card = gen.create_message_card(
        title="系统通知",
        content=[
            "欢迎使用 Bruce 智能助手",
            "我会帮你处理各种事务",
            "有问题随时告诉我！"
        ]
    )

    # 验证卡片结构
    assert "card" in json.loads(gen.to_json(card))
    assert "header" in card
    assert "elements" in card
    assert len(card["elements"]) == 3

    print("✅ 基础消息卡片测试通过\n")


def test_button_card():
    """测试按钮卡片"""
    print("测试2: 按钮卡片")
    gen = FeishuCardGenerator()

    card = gen.create_button_card(
        title="操作确认",
        content="请确认您的操作",
        buttons=[
            {"text": "确认", "url": "https://example.com/confirm"},
            {"text": "取消", "action": "cancel"},
            {"text": "帮助", "url": "https://example.com/help"}
        ]
    )

    # 验证卡片结构
    assert "header" in card
    assert "elements" in card
    # 应该有内容元素和按钮元素
    assert any(e["tag"] == "div" for e in card["elements"])
    assert any(e["tag"] == "action" for e in card["elements"])

    print("✅ 按钮卡片测试通过\n")


def test_list_card():
    """测试列表卡片"""
    print("测试3: 列表卡片")
    gen = FeishuCardGenerator()

    # 测试无序列表
    card1 = gen.create_list_card(
        title="待办事项",
        items=["任务A", "任务B", "任务C"],
        ordered=False
    )

    # 测试有序列表
    card2 = gen.create_list_card(
        title="排行榜",
        items=["第一名", "第二名", "第三名"],
        ordered=True
    )

    # 验证卡片结构
    assert "header" in card1
    assert "elements" in card1
    assert "•" in card1["elements"][0]["text"]["content"]
    assert "1." in card2["elements"][0]["text"]["content"]

    print("✅ 列表卡片测试通过\n")


def test_thinking_card():
    """测试正在思考卡片"""
    print("测试4: 正在思考卡片")
    gen = FeishuCardGenerator()

    card = gen.create_thinking_card("正在处理您的请求...")

    # 验证卡片结构
    assert "header" in card
    assert "正在思考中" in card["header"]["title"]["content"]
    assert "elements" in card

    print("✅ 正在思考卡片测试通过\n")


def test_progress_card():
    """测试进度卡片"""
    print("测试5: 进度卡片")
    gen = FeishuCardGenerator()

    card = gen.create_progress_card("任务进度", 7, 10, "处理中...")

    # 验证卡片结构
    assert "header" in card
    assert "elements" in card
    content = card["elements"][0]["text"]["content"]
    assert "7/10" in content
    assert "70%" in content

    print("✅ 进度卡片测试通过\n")


def test_result_card():
    """测试结果卡片"""
    print("测试6: 结果卡片")
    gen = FeishuCardGenerator()

    # 测试成功结果
    card1 = gen.create_result_card("任务完成", "所有任务已成功完成", success=True)
    assert card1["header"]["template"] == "green"

    # 测试失败结果
    card2 = gen.create_result_card("任务失败", "任务执行失败", success=False)
    assert card2["header"]["template"] == "red"

    print("✅ 结果卡片测试通过\n")


def test_report_card():
    """测试报告卡片"""
    print("测试7: 报告卡片")
    gen = FeishuCardGenerator()

    card = gen.create_report_card(
        title="每日报告",
        sections=[
            {"title": "任务", "content": "已完成5个任务"},
            {"title": "进度", "content": "50%"},
            {"title": "状态", "content": "正常"}
        ]
    )

    # 验证卡片结构
    assert "header" in card
    assert "elements" in card
    # 应该有标题、内容和分割线
    assert any("任务" in e.get("text", {}).get("content", "") for e in card["elements"])
    assert any(e["tag"] == "hr" for e in card["elements"])

    print("✅ 报告卡片测试通过\n")


def test_image_card():
    """测试图片卡片"""
    print("测试8: 图片卡片")
    gen = FeishuCardGenerator()

    card = gen.create_image_card(
        title="图片展示",
        image_key="test_image_key_123",
        content="这是一张测试图片"
    )

    # 验证卡片结构
    assert "header" in card
    assert "elements" in card
    assert card["elements"][0]["tag"] == "img"
    assert card["elements"][0]["img_key"] == "test_image_key_123"

    print("✅ 图片卡片测试通过\n")


def test_to_json():
    """测试JSON转换"""
    print("测试9: JSON转换")
    gen = FeishuCardGenerator()

    card = gen.create_message_card(
        title="测试",
        content=["内容1", "内容2"]
    )

    json_str = gen.to_json(card)
    json_data = json.loads(json_str)

    # 验证JSON结构
    assert "card" in json_data
    assert "header" in json_data["card"]
    assert "elements" in json_data["card"]

    print("✅ JSON转换测试通过\n")


def test_edge_cases():
    """测试边界情况"""
    print("测试10: 边界情况")
    gen = FeishuCardGenerator()

    # 测试空列表
    card1 = gen.create_list_card("空列表", [])
    assert "elements" in card1

    # 测试空按钮
    card2 = gen.create_button_card("空按钮", "无按钮", [])
    assert "elements" in card2

    # 测试进度0%
    card3 = gen.create_progress_card("测试", 0, 100)
    assert "0%" in card3["elements"][0]["text"]["content"]

    # 测试进度100%
    card4 = gen.create_progress_card("测试", 100, 100)
    assert "100%" in card4["elements"][0]["text"]["content"]

    print("✅ 边界情况测试通过\n")


def run_all_tests():
    """运行所有测试"""
    print("=== 飞书卡片生成器测试套件 ===\n")

    tests = [
        test_message_card,
        test_button_card,
        test_list_card,
        test_thinking_card,
        test_progress_card,
        test_result_card,
        test_report_card,
        test_image_card,
        test_to_json,
        test_edge_cases
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test_func.__name__} 失败: {e}\n")
            failed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} 错误: {e}\n")
            failed += 1

    print(f"\n=== 测试结果 ===")
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    print(f"总计: {passed + failed}")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
