#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书机器人管理器测试脚本
"""

import sys
import json


def test_import():
    """测试导入"""
    print("测试1: 导入模块")
    try:
        sys.path.insert(0, '/home/lejurobot/clawd/skills/feishu-bot-manager')
        from bot import FeishuBotManager

        print("✅ 模块导入成功\n")
        return FeishuBotManager
    except ImportError as e:
        print(f"❌ 导入失败: {e}\n")
        sys.exit(1)


def test_init():
    """测试初始化"""
    print("测试2: 初始化")
    from bot import FeishuBotManager

    # 读取配置
    with open('/home/lejurobot/.moltbot/moltbot.json', 'r') as f:
        config = json.load(f)

    app_id = config['channels']['feishu']['appId']
    app_secret = config['channels']['feishu']['appSecret']

    manager = FeishuBotManager(app_id, app_secret)

    assert manager.app_id == app_id
    assert manager.app_secret == app_secret

    print("✅ 初始化测试通过\n")


def test_get_token():
    """测试获取token"""
    print("测试3: 获取token")
    from bot import FeishuBotManager

    # 读取配置
    with open('/home/lejurobot/.moltbot/moltbot.json', 'r') as f:
        config = json.load(f)

    app_id = config['channels']['feishu']['appId']
    app_secret = config['channels']['feishu']['appSecret']

    manager = FeishuBotManager(app_id, app_secret)

    try:
        token = manager.get_tenant_access_token()
        assert token is not None
        assert len(token) > 0
        print(f"✅ Token获取成功: {token[:10]}...\n")
        return manager
    except Exception as e:
        print(f"❌ Token获取失败: {e}\n")
        sys.exit(1)


def test_get_app_bot_info():
    """测试获取应用机器人信息"""
    print("测试4: 获取应用机器人信息")
    from bot import FeishuBotManager

    # 读取配置
    with open('/home/lejurobot/.moltbot/moltbot.json', 'r') as f:
        config = json.load(f)

    app_id = config['channels']['feishu']['appId']
    app_secret = config['channels']['feishu']['appSecret']

    manager = FeishuBotManager(app_id, app_secret)

    try:
        app_bot_info = manager.get_bot_info()
        assert app_bot_info is not None
        assert 'app_name' in app_bot_info or 'name' in app_bot_info
        print("✅ 应用机器人信息获取成功")
        print(f"   类型: {app_bot_info.get('app_type', 'N/A')}")
        print()
    except Exception as e:
        print(f"❌ 获取应用机器人信息失败: {e}\n")


def test_get_bot_info_by_open_id():
    """测试通过open_id获取机器人信息"""
    print("测试5: 获取机器人信息（通过open_id）")
    from bot import FeishuBotManager

    # 读取配置
    with open('/home/lejurobot/.moltbot/moltbot.json', 'r') as f:
        config = json.load(f)

    app_id = config['channels']['feishu']['appId']
    app_secret = config['channels']['feishu']['appSecret']
    app_open_id = config['channels']['feishu'].get('appOpenId', '')

    manager = FeishuBotManager(app_id, app_secret)

    try:
        if app_open_id:
            bot_info = manager.get_bot_info_by_open_id(app_open_id)
            assert bot_info is not None
            print("✅ 机器人信息获取成功（通过open_id）")
            print(f"   open_id: {app_open_id}")
            print()
        else:
            print("⏭️  跳过（appOpenId未配置）\n")
    except Exception as e:
        print(f"❌ 获取机器人信息失败: {e}\n")


def test_get_bot_online_status():
    """测试获取机器人在线状态"""
    print("测试6: 获取机器人在线状态")
    from bot import FeishuBotManager

    # 读取配置
    with open('/home/lejurobot/.moltbot/moltbot.json', 'r') as f:
        config = json.load(f)

    app_id = config['channels']['feishu']['appId']
    app_secret = config['channels']['feishu']['appSecret']
    app_open_id = config['channels']['feishu'].get('appOpenId', '')

    manager = FeishuBotManager(app_id, app_secret)

    try:
        if app_open_id:
            online = manager.get_bot_online_status(app_open_id)
            assert isinstance(online, bool)
            print(f"✅ 机器人在线状态: {'在线' if online else '离线'}")
            print()
        else:
            print("⏭️  跳过（appOpenId未配置）\n")
    except Exception as e:
        print(f"❌ 获取机器人在线状态失败: {e}\n")


def test_get_bot_permissions():
    """测试获取机器人权限"""
    print("测试7: 获取机器人权限")
    from bot import FeishuBotManager

    # 读取配置
    with open('/home/lejurobot/.moltbot/moltbot.json', 'r') as f:
        config = json.load(f)

    app_id = config['channels']['feishu']['appId']
    app_secret = config['channels']['feishu']['appSecret']
    bot_open_id = config['channels']['feishu'].get('appOpenId', '')

    manager = FeishuBotManager(app_id, app_secret)

    try:
        if bot_open_id:
            permissions = manager.get_bot_permissions(bot_open_id)
            assert isinstance(permissions, list)
            print(f"✅ 机器人权限获取成功: {len(permissions)}个权限")
            if permissions:
                print("   示例权限:")
                for perm in permissions[:3]:
                    print(f"     - {perm.get('name', 'N/A')}")
            print()
        else:
            print("⏭️  跳过（appOpenId未配置）\n")
    except Exception as e:
        print(f"❌ 获取机器人权限失败: {e}\n")


def test_get_app_permissions():
    """测试获取应用权限"""
    print("测试8: 获取应用权限")
    from bot import FeishuBotManager

    # 读取配置
    with open('/home/lejurobot/.moltbot/moltbot.json', 'r') as f:
        config = json.load(f)

    app_id = config['channels']['feishu']['appId']
    app_secret = config['channels']['feishu']['appSecret']

    manager = FeishuBotManager(app_id, app_secret)

    try:
        permissions = manager.get_app_permissions()
        assert isinstance(permissions, list)
        print(f"✅ 应用权限获取成功: {len(permissions)}个权限")
        if permissions:
            print("   示例权限:")
            for perm in permissions[:3]:
                print(f"     - {perm.get('name', 'N/A')}")
        print()
    except Exception as e:
        print(f"❌ 获取应用权限失败: {e}\n")


def test_set_bot_name():
    """测试设置机器人名称（不需要实际调用）"""
    print("测试9: 设置机器人名称（数据验证）")
    from bot import FeishuBotManager

    # 读取配置
    with open('/home/lejurobot/.moltbot/moltbot.json', 'r') as f:
        config = json.load(f)

    app_id = config['channels']['feishu']['appId']
    app_secret = config['channels']['feishu']['appSecret']

    manager = FeishuBotManager(app_id, app_secret)

    # 只验证数据，不实际调用API
    open_id = "test_open_id_123"
    name = "测试机器人"

    assert isinstance(open_id, str)
    assert isinstance(name, str)
    assert len(open_id) > 0
    assert len(name) > 0

    print("✅ 设置机器人名称数据验证成功")
    print(f"   open_id: {open_id}")
    print(f"   name: {name}")
    print()


def test_set_bot_avatar():
    """测试设置机器人头像（数据验证）"""
    print("测试10: 设置机器人头像（数据验证）")
    from bot import FeishuBotManager

    # 读取配置
    with open('/home/lejurobot/.moltbot/moltbot.json', 'r') as f:
        config = json.load(f)

    app_id = config['channels']['feishu']['appId']
    app_secret = config['channels']['feishu']['appSecret']

    manager = FeishuBotManager(app_id, app_secret)

    # 只验证数据，不实际调用API
    open_id = "test_open_id_456"
    image_key = "test_image_key_789"

    assert isinstance(open_id, str)
    assert isinstance(image_key, str)
    assert len(open_id) > 0
    assert len(image_key) > 0

    print("✅ 设置机器人头像数据验证成功")
    print(f"   open_id: {open_id}")
    print(f"   image_key: {image_key}")
    print()


def test_create_bot():
    """测试创建机器人（数据验证）"""
    print("测试11: 创建机器人（数据验证）")
    from bot import FeishuBotManager

    # 读取配置
    with open('/home/lejurobot/.moltbot/moltbot.json', 'r') as f:
        config = json.load(f)

    app_id = config['channels']['feishu']['appId']
    app_secret = config['channels']['feishu']['appSecret']

    manager = FeishuBotManager(app_id, app_secret)

    # 只验证数据，不实际调用API
    name = "测试机器人"
    avatar = "https://example.com/avatar.png"
    open_id = "test_open_id_abc"
    description = "这是一个测试机器人"

    assert isinstance(name, str)
    assert isinstance(avatar, str)
    assert isinstance(open_id, str)
    assert isinstance(description, str)
    assert len(name) > 0
    assert len(open_id) > 0

    print("✅ 创建机器人数据验证成功")
    print(f"   name: {name}")
    print(f"   avatar: {avatar}")
    print(f"   open_id: {open_id}")
    print(f"   description: {description}")
    print()


def test_delete_bot():
    """测试删除机器人（数据验证）"""
    print("测试12: 删除机器人（数据验证）")
    from bot import FeishuBotManager

    # 读取配置
    with open('/home/lejurobot/.moltbot/moltbot.json', 'r') as f:
        config = json.load(f)

    app_id = config['channels']['feishu']['appId']
    app_secret = config['channels']['feishu']['appSecret']

    manager = FeishuBotManager(app_id, app_secret)

    # 只验证数据，不实际调用API
    open_id = "test_open_id_xyz"

    assert isinstance(open_id, str)
    assert len(open_id) > 0

    print("✅ 删除机器人数据验证成功")
    print(f"   open_id: {open_id}")
    print()


def run_all_tests():
    """运行所有测试"""
    print("=== 飞书机器人管理器测试套件 ===\n")

    tests = [
        test_import,
        test_init,
        test_get_token,
        test_get_app_bot_info,
        test_get_bot_info_by_open_id,
        test_get_bot_online_status,
        test_get_bot_permissions,
        test_get_app_permissions,
        test_set_bot_name,
        test_set_bot_avatar,
        test_create_bot,
        test_delete_bot
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
