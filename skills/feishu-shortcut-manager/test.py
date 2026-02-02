#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书快捷指令管理器测试脚本
"""

import sys


def test_import():
    """测试导入"""
    print("测试1: 导入模块")
    try:
        sys.path.insert(0, '/home/lejurobot/clawd/skills/feishu-shortcut-manager')
        from shortcut import FeishuShortcutManager

        print("✅ 模块导入成功\n")
        return FeishuShortcutManager
    except ImportError as e:
        print(f"❌ 导入失败: {e}\n")
        sys.exit(1)


def test_init():
    """测试初始化"""
    print("测试2: 初始化")
    from shortcut import FeishuShortcutManager

    manager = FeishuShortcutManager()

    assert manager is not None
    assert manager.shortcuts == {}
    assert manager.shortcut_id_counter == 1

    print("✅ 初始化测试通过\n")


def test_create_keyword_shortcut():
    """测试创建关键词快捷指令"""
    print("测试3: 创建关键词快捷指令")
    from shortcut import FeishuShortcutManager

    manager = FeishuShortcutManager()

    shortcut = manager.create_keyword_shortcut(
        name="查询天气",
        description="查询城市天气",
        keywords=["天气", "weather"],
        action="query_weather",
        params={"default_city": "深圳"}
    )

    assert shortcut is not None
    assert shortcut['id'] == "shortcut_1"
    assert shortcut['name'] == "查询天气"
    assert shortcut['trigger_type'] == "keyword"
    assert len(shortcut['trigger_config']['keywords']) == 2
    assert len(shortcut['actions']) == 1
    assert shortcut['enabled'] == True

    print(f"✅ 关键词快捷指令已创建: {shortcut['id']}")
    print(f"   名称: {shortcut['name']}")
    print(f"   关键词: {shortcut['trigger_config']['keywords']}")
    print()


def test_create_card_shortcut():
    """测试创建卡片快捷指令"""
    print("测试4: 创建卡片快捷指令")
    from shortcut import FeishuShortcutManager

    manager = FeishuShortcutManager()

    card = {
        "header": {"title": "操作选择", "template": "blue"},
        "elements": [
            {"tag": "div", "text": {"tag": "plain_text", "content": "请选择"}}
        ]
    }

    button_actions = [
        {"type": "action", "action": "action1", "params": {}},
        {"type": "action", "action": "action2", "params": {}}
    ]

    shortcut = manager.create_card_shortcut(
        name="操作选择",
        description="显示操作选择卡片",
        card=card,
        button_actions=button_actions
    )

    assert shortcut is not None
    assert shortcut['id'] == "shortcut_2"
    assert shortcut['trigger_type'] == "card"
    assert len(shortcut['actions']) == 2

    print(f"✅ 卡片快捷指令已创建: {shortcut['id']}")
    print(f"   名称: {shortcut['name']}")
    print()


def test_create_schedule_shortcut():
    """测试创建定时快捷指令"""
    print("测试5: 创建定时快捷指令")
    from shortcut import FeishuShortcutManager

    manager = FeishuShortcutManager()

    shortcut = manager.create_schedule_shortcut(
        name="定时报告",
        description="每天早上9点发送报告",
        schedule="0 9 * * *",
        action="send_report",
        params={"type": "daily"}
    )

    assert shortcut is not None
    assert shortcut['id'] == "shortcut_3"
    assert shortcut['trigger_type'] == "schedule"
    assert shortcut['trigger_config']['schedule'] == "0 9 * * *"

    print(f"✅ 定时快捷指令已创建: {shortcut['id']}")
    print(f"   名称: {shortcut['name']}")
    print(f"   调度: {shortcut['trigger_config']['schedule']}")
    print()


def test_get_shortcut():
    """测试获取快捷指令"""
    print("测试6: 获取快捷指令")
    from shortcut import FeishuShortcutManager

    manager = FeishuShortcutManager()

    # 先创建一个快捷指令
    created = manager.create_keyword_shortcut(
        name="测试指令",
        description="测试描述",
        keywords=["test"],
        action="test_action"
    )

    # 获取快捷指令
    shortcut = manager.get_shortcut(created['id'])

    assert shortcut is not None
    assert shortcut['id'] == created['id']
    assert shortcut['name'] == "测试指令"

    print(f"✅ 快捷指令获取成功: {shortcut['id']}")
    print()

    # 测试获取不存在的快捷指令
    not_found = manager.get_shortcut("non_existent_id")
    assert not_found is None

    print(f"✅ 不存在的快捷指令返回: {not_found}")
    print()


def test_list_shortcuts():
    """测试列出所有快捷指令"""
    print("测试7: 列出所有快捷指令")
    from shortcut import FeishuShortcutManager

    manager = FeishuShortcutManager()

    # 创建多个快捷指令
    manager.create_keyword_shortcut("指令1", "描述1", ["k1"], "a1")
    manager.create_keyword_shortcut("指令2", "描述2", ["k2"], "a2")
    manager.create_keyword_shortcut("指令3", "描述3", ["k3"], "a3")

    # 列出所有快捷指令
    all_shortcuts = manager.list_shortcuts()
    assert len(all_shortcuts) == 3

    # 列出启用的快捷指令
    enabled_shortcuts = manager.list_shortcuts(enabled_only=True)
    assert len(enabled_shortcuts) == 3  # 全部默认启用

    print(f"✅ 共有 {len(all_shortcuts)}个快捷指令")
    for sc in all_shortcuts:
        print(f"   - {sc['id']}: {sc['name']}")

    print()


def test_enable_shortcut():
    """测试启用快捷指令"""
    print("测试8: 启用/禁用快捷指令")
    from shortcut import FeishuShortcutManager

    manager = FeishuShortcutManager()

    # 创建快捷指令
    created = manager.create_keyword_shortcut("测试", "描述", ["t"], "a")

    # 禁用快捷指令
    disabled = manager.disable_shortcut(created['id'])
    assert disabled == True
    assert manager.get_shortcut(created['id'])['enabled'] == False

    # 启用快捷指令
    enabled = manager.enable_shortcut(created['id'])
    assert enabled == True
    assert manager.get_shortcut(created['id'])['enabled'] == True

    print("✅ 启用/禁用快捷指令测试通过")
    print()


def test_delete_shortcut():
    """测试删除快捷指令"""
    print("测试9: 删除快捷指令")
    from shortcut import FeishuShortcutManager

    manager = FeishuShortcutManager()

    # 创建快捷指令
    created = manager.create_keyword_shortcut("测试", "描述", ["t"], "a")

    # 删除快捷指令
    deleted = manager.delete_shortcut(created['id'])
    assert deleted == True

    # 验证已删除
    shortcut = manager.get_shortcut(created['id'])
    assert shortcut is None

    # 再次删除（应该失败）
    deleted_again = manager.delete_shortcut(created['id'])
    assert deleted_again == False

    print("✅ 删除快捷指令测试通过")
    print()


def test_update_shortcut():
    """测试更新快捷指令"""
    print("测试10: 更新快捷指令")
    from shortcut import FeishuShortcutManager

    manager = FeishuShortcutManager()

    # 创建快捷指令
    created = manager.create_keyword_shortcut("测试", "描述", ["t"], "a")

    # 更新快捷指令
    updated = manager.update_shortcut(
        created['id'],
        {"description": "更新后的描述"}
    )
    assert updated == True

    # 验证更新
    shortcut = manager.get_shortcut(created['id'])
    assert shortcut['description'] == "更新后的描述"

    print(f"✅ 快捷指令已更新: {shortcut['description']}")
    print()


def test_trigger_shortcut():
    """测试触发快捷指令"""
    print("测试11: 触发快捷指令")
    from shortcut import FeishuShortcutManager

    manager = FeishuShortcutManager()

    # 创建关键词快捷指令
    created = manager.create_keyword_shortcut(
        name="测试触发",
        description="测试触发功能",
        keywords=["{city}", "天气"],
        action="query_weather",
        params={"default_city": "深圳"}
    )

    # 触发快捷指令
    trigger_data = {"city": "北京"}
    actions = manager.trigger_shortcut(created['id'], trigger_data)

    assert len(actions) > 0
    assert actions[0]['type'] == "action"
    assert actions[0]['params']['default_city'] == "深圳"  # 不在触发数据中，保持原值

    print(f"✅ 快捷指令已触发，动作数量: {len(actions)}")
    print()


def test_create_common_shortcuts():
    """测试创建常用快捷指令"""
    print("测试12: 创建常用快捷指令")
    from shortcut import FeishuShortcutManager

    manager = FeishuShortcutManager()

    # 创建常用快捷指令
    common_shortcuts = manager.create_common_shortcuts()

    assert len(common_shortcuts) >= 4

    # 验证常用快捷指令
    expected_shortcuts = ['query_weather', 'send_report', 'system_status', 'help']
    for sc_id in expected_shortcuts:
        assert sc_id in common_shortcuts
        assert common_shortcuts[sc_id]['enabled'] == True

    print(f"✅ 常用快捷指令已创建: {len(common_shortcuts)}个")
    for sc_id, sc in common_shortcuts.items():
        print(f"   - {sc_id}: {sc['name']}")

    print()


def run_all_tests():
    """运行所有测试"""
    print("=== 飞书快捷指令管理器测试套件 ===\n")

    tests = [
        test_import,
        test_init,
        test_create_keyword_shortcut,
        test_create_card_shortcut,
        test_create_schedule_shortcut,
        test_get_shortcut,
        test_list_shortcuts,
        test_enable_shortcut,
        test_delete_shortcut,
        test_update_shortcut,
        test_trigger_shortcut,
        test_create_common_shortcuts
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
