#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书Webhook处理器测试脚本
"""

import sys
import json
import base64


def test_import():
    """测试导入"""
    print("测试1: 导入模块")
    try:
        sys.path.insert(0, '/home/lejurobot/clawd/skills/feishu-webhook-handler')
        from webhook import FeishuWebhookHandler

        print("✅ 模块导入成功\n")
        return FeishuWebhookHandler
    except ImportError as e:
        print(f"❌ 导入失败: {e}\n")
        sys.exit(1)


def test_init():
    """测试初始化"""
    print("测试2: 初始化")
    from webhook import FeishuWebhookHandler

    app_secret = "test_secret"

    handler = FeishuWebhookHandler(app_secret)

    assert handler.app_secret == app_secret

    print("✅ 初始化测试通过\n")


def test_parse_webhook_event():
    """测试解析Webhook事件"""
    print("测试3: 解析Webhook事件")
    from webhook import FeishuWebhookHandler

    handler = FeishuWebhookHandler("test_secret")

    test_event = {
        "header": {
            "event_id": "test_event_id",
            "event_type": "im.message.receive_v1",
            "create_time": "1234567890",
            "token": "test_token"
        },
        "event": {}
    }

    event = handler.parse_webhook_event(json.dumps(test_event))

    assert event is not None
    assert event['event_type'] == 'im.message.receive_v1'
    assert event['event_id'] == 'test_event_id'
    assert 'raw_event' in event

    print("✅ 解析Webhook事件测试通过\n")


def test_extract_message_content():
    """测试提取消息内容"""
    print("测试4: 提取消息内容")
    from webhook import FeishuWebhookHandler

    handler = FeishuWebhookHandler("test_secret")

    test_event = {
        'event_type': 'im.message.receive_v1',
        'event_id': 'test_event_id',
        'timestamp': '1234567890',
        'token': 'test_token',
        'raw_event': {
            'event': {
                'sender': {
                    'sender_id': {'open_id': 'test_user_id'},
                    'sender_type': 'user'
                },
                'message': {
                    'message_id': 'test_message_id',
                    'chat_type': 'p2p',
                    'message_type': 'text',
                    'content': '{"text": "测试消息"}'
                }
            }
        }
    }

    content = handler.extract_message_content(test_event)

    assert content is not None
    assert content['message_id'] == 'test_message_id'
    assert content['sender_id'] == 'test_user_id'
    assert content['message_type'] == 'text'
    assert content['text'] == '测试消息'

    print("✅ 提取消息内容测试通过\n")


def test_extract_image_content():
    """测试提取图片消息内容"""
    print("测试5: 提取图片消息内容")
    from webhook import FeishuWebhookHandler

    handler = FeishuWebhookHandler("test_secret")

    test_event = {
        'event_type': 'im.message.receive_v1',
        'event_id': 'test_event_id',
        'timestamp': '1234567890',
        'token': 'test_token',
        'raw_event': {
            'event': {
                'sender': {
                    'sender_id': {'open_id': 'test_user_id'},
                    'sender_type': 'user'
                },
                'message': {
                    'message_id': 'test_message_id',
                    'chat_type': 'p2p',
                    'message_type': 'image',
                    'content': '{"image_key": "test_image_key"}'
                }
            }
        }
    }

    content = handler.extract_message_content(test_event)

    assert content is not None
    assert content['message_type'] == 'image'
    assert content['image_key'] == 'test_image_key'

    print("✅ 提取图片消息内容测试通过\n")


def test_is_message_event():
    """测试判断消息事件"""
    print("测试6: 判断消息事件")
    from webhook import FeishuWebhookHandler

    handler = FeishuWebhookHandler("test_secret")

    # 测试消息事件
    event1 = {
        'event_type': 'im.message.receive_v1',
        'raw_event': {}
    }

    assert handler.is_message_event(event1) == True
    print("  - 消息事件: ✅")

    # 测试非消息事件
    event2 = {
        'event_type': 'some_other_event',
        'raw_event': {}
    }

    assert handler.is_message_event(event2) == False
    print("  - 非消息事件: ✅")

    print("✅ 判断消息事件测试通过\n")


def test_is_private_chat():
    """测试判断私聊"""
    print("测试7: 判断私聊")
    from webhook import FeishuWebhookHandler

    handler = FeishuWebhookHandler("test_secret")

    # 测试私聊
    content1 = {
        'chat_type': 'p2p',
        'message_id': 'test',
        'sender_id': 'test'
    }

    assert handler.is_private_chat(content1) == True
    print("  - 私聊: ✅")

    # 测试群聊
    content2 = {
        'chat_type': 'group',
        'message_id': 'test',
        'sender_id': 'test'
    }

    assert handler.is_private_chat(content2) == False
    print("  - 群聊: ✅")

    print("✅ 判断私聊测试通过\n")


def test_is_group_chat():
    """测试判断群聊"""
    print("测试8: 判断群聊")
    from webhook import FeishuWebhookHandler

    handler = FeishuWebhookHandler("test_secret")

    # 测试群聊
    content1 = {
        'chat_type': 'group',
        'message_id': 'test',
        'sender_id': 'test'
    }

    assert handler.is_group_chat(content1) == True
    print("  - 群聊: ✅")

    # 测试私聊
    content2 = {
        'chat_type': 'p2p',
        'message_id': 'test',
        'sender_id': 'test'
    }

    assert handler.is_group_chat(content2) == False
    print("  - 私聊: ✅")

    print("✅ 判断群聊测试通过\n")


def test_create_challenge_response():
    """测试创建挑战响应"""
    print("测试9: 创建挑战响应")
    from webhook import FeishuWebhookHandler

    handler = FeishuWebhookHandler("test_secret")

    challenge = "test_challenge"
    response = handler.create_challenge_response(challenge)

    assert 'challenge' in response
    assert 'token' in response
    assert response['challenge'] == challenge

    print("✅ 创建挑战响应测试通过\n")


def test_handle_message():
    """测试处理消息"""
    print("测试10: 处理消息")
    from webhook import FeishuWebhookHandler

    handler = FeishuWebhookHandler("test_secret")

    # 测试处理函数
    test_handled = []

    def test_handler(content):
        test_handled.append(content)
        return True

    content = {
        'message_id': 'test',
        'text': '测试消息'
    }

    result = handler.handle_message(content, test_handler)

    assert result == True
    assert len(test_handled) == 1
    assert test_handled[0]['text'] == '测试消息'

    print("✅ 处理消息测试通过\n")


def run_all_tests():
    """运行所有测试"""
    print("=== 飞书Webhook处理器测试套件 ===\n")

    tests = [
        test_import,
        test_init,
        test_parse_webhook_event,
        test_extract_message_content,
        test_extract_image_content,
        test_is_message_event,
        test_is_private_chat,
        test_is_group_chat,
        test_create_challenge_response,
        test_handle_message
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
