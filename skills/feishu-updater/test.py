#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书消息更新器测试脚本
"""

import sys
import json
import os
import time


def test_import():
    """测试导入"""
    print("测试1: 导入模块")
    try:
        sys.path.insert(0, '/home/lejurobot/clawd/skills/feishu-card-generator')
        from card import FeishuCardGenerator
        sys.path.insert(0, '/home/lejurobot/clawd/skills/feishu-updater')
        from updater import FeishuMessageUpdater

        print("✅ 模块导入成功\n")
        return FeishuCardGenerator, FeishuMessageUpdater
    except ImportError as e:
        print(f"❌ 导入失败: {e}\n")
        sys.exit(1)


def test_card_generator():
    """测试卡片生成器"""
    print("测试2: 卡片生成器")
    from card import FeishuCardGenerator

    gen = FeishuCardGenerator()

    # 测试各种卡片创建
    cards = [
        gen.create_thinking_card("测试消息"),
        gen.create_progress_card("测试进度", 5, 10),
        gen.create_result_card("测试结果", "测试成功", True),
        gen.create_message_card("测试标题", ["内容1", "内容2"])
    ]

    for i, card in enumerate(cards):
        assert "header" in card
        assert "elements" in card
        print(f"  - 卡片 {i+1}: ✅")

    print("✅ 卡片生成器测试通过\n")


def test_updater_init():
    """测试更新器初始化"""
    print("测试3: 更新器初始化")
    from updater import FeishuMessageUpdater

    # 读取配置
    with open('/home/lejurobot/.moltbot/moltbot.json', 'r') as f:
        config = json.load(f)

    app_id = config['channels']['feishu']['appId']
    app_secret = config['channels']['feishu']['appSecret']

    updater = FeishuMessageUpdater(app_id, app_secret)

    assert updater.app_id == app_id
    assert updater.app_secret == app_secret
    assert updater.card_gen is not None

    print("✅ 更新器初始化测试通过\n")


def test_get_token():
    """测试获取token"""
    print("测试4: 获取token")
    from updater import FeishuMessageUpdater

    # 读取配置
    with open('/home/lejurobot/.moltbot/moltbot.json', 'r') as f:
        config = json.load(f)

    app_id = config['channels']['feishu']['appId']
    app_secret = config['channels']['feishu']['appSecret']

    updater = FeishuMessageUpdater(app_id, app_secret)

    try:
        token = updater.get_tenant_access_token()
        assert token is not None
        assert len(token) > 0
        print(f"✅ Token获取成功: {token[:10]}...\n")
        return updater
    except Exception as e:
        print(f"❌ Token获取失败: {e}\n")
        sys.exit(1)


def test_send_thinking_card(updater):
    """测试发送'正在思考'卡片"""
    print("测试5: 发送'正在思考'卡片")

    user_id = "ou_ac30832212aa13310b80594b6a24b8d9"  # 测试用户ID

    try:
        message_id = updater.send_thinking_card(
            user_id,
            "正在处理您的请求，请稍候..."
        )
        assert message_id is not None
        print(f"✅ 卡片已发送，消息ID: {message_id}")
        print()
        return message_id
    except Exception as e:
        print(f"❌ 发送失败: {e}\n")
        sys.exit(1)


def test_update_progress(updater, message_id):
    """测试更新进度卡片"""
    print("测试6: 更新进度卡片")

    try:
        updater.update_progress(
            message_id,
            "任务进度",
            7,
            10,
            "处理中..."
        )
        print("✅ 进度卡片已更新")
        print()
    except Exception as e:
        print(f"❌ 更新失败: {e}\n")
        sys.exit(1)


def test_update_to_result(updater, message_id):
    """测试更新为结果卡片"""
    print("测试7: 更新为结果卡片")

    try:
        updater.update_to_result(
            message_id,
            "测试完成",
            "所有测试已成功完成",
            success=True
        )
        print("✅ 结果卡片已更新")
        print()
    except Exception as e:
        print(f"❌ 更新失败: {e}\n")
        sys.exit(1)


def test_send_text_message(updater):
    """测试发送文本消息"""
    print("测试8: 发送文本消息")

    user_id = "ou_ac30832212aa13310b80594b6a24b8d9"  # 测试用户ID

    try:
        message_id = updater.send_text_message(
            user_id,
            "这是一条测试消息"
        )
        assert message_id is not None
        print(f"✅ 文本消息已发送，消息ID: {message_id}")
        print()
    except Exception as e:
        print(f"❌ 发送失败: {e}\n")
        sys.exit(1)


def test_json_serialization():
    """测试JSON序列化"""
    print("测试9: JSON序列化")
    from card import FeishuCardGenerator

    gen = FeishuCardGenerator()

    card = gen.create_thinking_card("测试")
    json_str = gen.to_json(card)

    json_data = json.loads(json_str)

    assert "card" in json_data
    assert "header" in json_data["card"]
    assert "elements" in json_data["card"]

    print("✅ JSON序列化测试通过\n")


def test_card_templates():
    """测试卡片模板"""
    print("测试10: 卡片模板")
    from card import FeishuCardGenerator

    gen = FeishuCardGenerator()

    templates = [
        "turquoise", "blue", "wathet", "lark",
        "indigo", "purple", "pink", "red",
        "orange", "yellow", "green", "grey"
    ]

    for template in templates:
        card = gen.create_message_card(
            "测试标题",
            ["测试内容"],
            template=template
        )
        assert card["header"]["template"] == template
        print(f"  - 模板 {template}: ✅")

    print("✅ 卡片模板测试通过\n")


def run_all_tests():
    """运行所有测试"""
    print("=== 飞书消息更新器测试套件 ===\n")

    # 测试1：导入
    FeishuCardGenerator, FeishuMessageUpdater = test_import()

    # 测试2：卡片生成器
    test_card_generator()

    # 测试3：更新器初始化
    test_updater_init()

    # 测试4：获取token
    updater = test_get_token()

    # 测试9：JSON序列化（不需要连接飞书）
    test_json_serialization()

    # 测试10：卡片模板（不需要连接飞书）
    test_card_templates()

    # 测试5-8：需要连接飞书的测试
    print("开始飞书API测试（需要网络连接）\n")

    message_id = test_send_thinking_card(updater)

    time.sleep(2)  # 等待2秒

    test_update_progress(updater, message_id)

    time.sleep(2)  # 等待2秒

    test_update_to_result(updater, message_id)

    test_send_text_message(updater)

    print("=== 所有测试通过 ===")


if __name__ == "__main__":
    try:
        run_all_tests()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 测试套件失败: {e}")
        sys.exit(1)
