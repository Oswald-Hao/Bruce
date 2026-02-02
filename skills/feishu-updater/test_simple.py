#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书消息更新器测试脚本（简化版 - 只测试更新）
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
        gen.create_progress_card("测试进度",5, 10),
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


def test_json_serialization():
    """测试JSON序列化"""
    print("测试5: JSON序列化")
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
    print("测试6: 卡片模板")
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


def test_card_title_conversion():
    """测试卡片标题转换"""
    print("测试7: 卡片标题转换")
    import copy
    from card import FeishuCardGenerator

    gen = FeishuCardGenerator()
    card = gen.create_thinking_card("测试")

    # 深度复制卡片
    card_copy = copy.deepcopy(card)

    # 转换header.title为字符串格式
    if 'header' in card_copy and 'title' in card_copy['header']:
        title_obj = card_copy['header']['title']
        if isinstance(title_obj, dict) and 'content' in title_obj:
            card_copy['header']['title'] = title_obj['content']

    assert card_copy['header']['title'] == "🤔 正在思考中..."
    assert isinstance(card_copy['header']['title'], str)

    print("✅ 卡片标题转换测试通过\n")


def test_update_card_structure():
    """测试更新卡片的数据结构"""
    print("测试8: 更新卡片的数据结构")
    from card import FeishuCardGenerator

    gen = FeishuCardGenerator()
    card = gen.create_progress_card("测试进度", 7, 10, "测试状态")

    # 验证卡片结构
    assert "header" in card
    assert "elements" in card
    assert "config" in card

    # 验证header结构
    assert "title" in card["header"]
    assert "template" in card["header"]

    # 验证elements结构
    assert len(card["elements"]) > 0
    assert "tag" in card["elements"][0]

    print("✅ 更新卡片的数据结构测试通过\n")


def test_edge_cases():
    """测试边界情况"""
    print("测试9: 边界情况")
    from card import FeishuCardGenerator

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


def test_card_serialization_for_api():
    """测试卡片序列化以供API使用"""
    print("测试10: 卡片序列化以供API使用")
    from card import FeishuCardGenerator
    import copy

    gen = FeishuCardGenerator()
    card = gen.create_thinking_card("测试消息")

    # 模拟API使用：深度复制并转换title
    card_for_api = copy.deepcopy(card)

    if 'header' in card_for_api and 'title' in card_for_api['header']:
        title_obj = card_for_api['header']['title']
        if isinstance(title_obj, dict) and 'content' in title_obj:
            card_for_api['header']['title'] = title_obj['content']

    # 验证转换后的格式
    assert isinstance(card_for_api['header']['title'], str)
    assert card_for_api['header']['title'] == "🤔 正在思考中..."

    # 验证可以序列化为JSON
    try:
        json_str = json.dumps({"card": card_for_api}, ensure_ascii=False)
        parsed = json.loads(json_str)
        assert "card" in parsed
        print("✅ 卡片序列化以供API使用测试通过\n")
    except Exception as e:
        print(f"❌ 序列化失败: {e}\n")
        raise


def run_all_tests():
    """运行所有测试"""
    print("=== 飞书消息更新器测试套件（简化版）===\n")

    tests = [
        test_import,
        test_card_generator,
        test_updater_init,
        test_get_token,
        test_json_serialization,
        test_card_templates,
        test_card_title_conversion,
        test_update_card_structure,
        test_edge_cases,
        test_card_serialization_for_api
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
