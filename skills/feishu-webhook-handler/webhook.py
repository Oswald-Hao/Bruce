#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书Webhook处理器 - Feishu Webhook Handler

用于处理飞书的Webhook事件，支持消息接收、事件处理等
"""

import json
import hmac
import hashlib
from typing import Dict, Optional, Callable
from datetime import datetime


class FeishuWebhookHandler:
    """飞书Webhook处理器类"""

    def __init__(self, app_secret: str):
        """
        初始化Webhook处理器

        Args:
            app_secret: 飞书应用Secret（用于验证Webhook签名）
        """
        self.app_secret = app_secret

    def verify_webhook_signature(
        self,
        timestamp: str,
        nonce: str,
        body: str,
        signature: str
    ) -> bool:
        """
        验证Webhook签名

        Args:
            timestamp: 时间戳
            nonce: 随机数
            body: 请求体
            signature: 签名

        Returns:
            是否验证通过
        """
        # 拼接字符串
        content = f"{timestamp}{nonce}{body}"

        # 计算签名
        computed_signature = hmac.new(
            self.app_secret.encode('utf-8'),
            content.encode('utf-8'),
            hashlib.sha256
        ).digest()

        # Base64编码
        computed_signature_b64 = base64.b64encode(computed_signature).decode('utf-8')

        # 比较签名
        return computed_signature_b64 == signature

    def parse_webhook_event(
        self,
        body: str
    ) -> Optional[Dict]:
        """
        解析Webhook事件

        Args:
            body: 请求体（JSON字符串）

        Returns:
            事件字典，如果解析失败返回None
        """
        try:
            event = json.loads(body)

            # 验证事件结构
            if 'header' not in event or 'event' not in event:
                return None

            # 提取事件信息
            event_type = event.get('header', {}).get('event_type', '')
            event_id = event.get('header', {}).get('event_id', '')
            timestamp = event.get('header', {}).get('create_time', '')
            token = event.get('header', {}).get('token', '')

            return {
                'event_type': event_type,
                'event_id': event_id,
                'timestamp': timestamp,
                'token': token,
                'raw_event': event
            }

        except Exception as e:
            print(f"解析Webhook事件失败: {e}")
            return None

    def extract_message_content(
        self,
        event: Dict
    ) -> Optional[Dict]:
        """
        从事件中提取消息内容

        Args:
            event: 事件字典

        Returns:
            消息内容字典，如果不是消息事件返回None
        """
        try:
            event_type = event.get('event_type', '')
            raw_event = event.get('raw_event', {})

            # 只处理消息接收事件
            if event_type != 'im.message.receive_v1':
                return None

            message = raw_event.get('event', {}).get('message', {})
            sender = raw_event.get('event', {}).get('sender', {})

            # 提取消息ID
            message_id = message.get('message_id', '')

            # 提取消息类型
            message_type = message.get('message_type', '')

            # 提取聊天类型
            chat_type = message.get('chat_type', '')
            chat_id = message.get('chat_id', '')

            # 提取发送者信息
            sender_id = sender.get('sender_id', {}).get('open_id', '')
            sender_type = sender.get('sender_type', '')

            # 提取消息内容
            content = message.get('content', '')

            # 根据消息类型解析内容
            if message_type == 'text':
                # 文本消息
                content_obj = json.loads(content)
                text = content_obj.get('text', '')

                return {
                    'message_id': message_id,
                    'message_type': 'text',
                    'chat_type': chat_type,
                    'chat_id': chat_id,
                    'sender_id': sender_id,
                    'sender_type': sender_type,
                    'text': text,
                    'raw_content': content
                }

            elif message_type == 'image':
                # 图片消息
                content_obj = json.loads(content)
                image_key = content_obj.get('image_key', '')

                return {
                    'message_id': message_id,
                    'message_type': 'image',
                    'chat_type': chat_type,
                    'chat_id': chat_id,
                    'sender_id': sender_id,
                    'sender_type': sender_type,
                    'image_key': image_key,
                    'raw_content': content
                }

            else:
                # 其他类型消息
                return {
                    'message_id': message_id,
                    'message_type': message_type,
                    'chat_type': chat_type,
                    'chat_id': chat_id,
                    'sender_id': sender_id,
                    'sender_type': sender_type,
                    'raw_content': content
                }

        except Exception as e:
            print(f"提取消息内容失败: {e}")
            return None

    def handle_message(
        self,
        content: Dict,
        handler: Callable
    ) -> bool:
        """
        处理消息

        Args:
            content: 消息内容
            handler: 处理函数

        Returns:
            是否处理成功
        """
        try:
            return handler(content)
        except Exception as e:
            print(f"处理消息失败: {e}")
            return False

    def create_challenge_response(
        self,
        challenge: str
    ) -> Dict:
        """
        创建挑战响应（用于URL验证）

        Args:
            challenge: 挑战字符串

        Returns:
            响应字典
        """
        # 计算挑战响应
        challenge_response = self._calculate_challenge(challenge)

        return {
            "challenge": challenge,
            "token": challenge_response
        }

    def _calculate_challenge(self, challenge: str) -> str:
        """
        计算挑战响应

        Args:
            challenge: 挑战字符串

        Returns:
            挑战响应
        """
        # 使用app_secret对challenge进行加密
        # 这里简化处理，实际应该使用飞书指定的加密方式
        return hmac.new(
            self.app_secret.encode('utf-8'),
            challenge.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def is_message_event(self, event: Dict) -> bool:
        """
        判断是否为消息事件

        Args:
            event: 事件字典

        Returns:
            是否为消息事件
        """
        return event.get('event_type') == 'im.message.receive_v1'

    def is_private_chat(self, content: Dict) -> bool:
        """
        判断是否为私聊

        Args:
            content: 消息内容

        Returns:
            是否为私聊
        """
        return content.get('chat_type') == 'p2p'

    def is_group_chat(self, content: Dict) -> bool:
        """
        判断是否为群聊

        Args:
            content: 消息内容

        Returns:
            是否为群聊
        """
        return content.get('chat_type') == 'group'


def main():
    """测试飞书Webhook处理器"""
    import base64

    print("=== 飞书Webhook处理器测试 ===\n")

    # 读取配置
    with open('/home/lejurobot/.moltbot/moltbot.json', 'r') as f:
        config = json.load(f)

    app_secret = config['channels']['feishu']['appSecret']

    handler = FeishuWebhookHandler(app_secret)

    # 测试1：解析Webhook事件
    print("1. 解析Webhook事件")
    test_event = {
        "header": {
            "event_id": "test_event_id",
            "event_type": "im.message.receive_v1",
            "create_time": "1234567890",
            "token": "test_token"
        },
        "event": {
            "sender": {
                "sender_id": {
                    "open_id": "test_open_id"
                },
                "sender_type": "user"
            },
            "message": {
                "message_id": "test_message_id",
                "chat_type": "p2p",
                "message_type": "text",
                "content": '{"text": "测试消息"}'
            }
        }
    }

    event = handler.parse_webhook_event(json.dumps(test_event))
    if event:
        print(f"✅ 事件解析成功: {event['event_type']}")
    else:
        print("❌ 事件解析失败")
    print()

    # 测试2：提取消息内容
    print("2. 提取消息内容")
    if event:
        content = handler.extract_message_content(event)
        if content:
            print(f"✅ 消息提取成功: {content['text']}")
            print(f"   发送者: {content['sender_id']}")
            print(f"   消息类型: {content['message_type']}")
        else:
            print("❌ 消息提取失败")
    print()

    # 测试3：判断消息事件
    print("3. 判断消息事件")
    if event:
        if handler.is_message_event(event):
            print("✅ 是消息事件")
        else:
            print("❌ 不是消息事件")
    print()

    # 测试4：判断私聊
    print("4. 判断私聊")
    if event:
        content = handler.extract_message_content(event)
        if content and handler.is_private_chat(content):
            print("✅ 是私聊")
        else:
            print("❌ 不是私聊")
    print()

    print("=== 测试完成 ===")


if __name__ == "__main__":
    main()
