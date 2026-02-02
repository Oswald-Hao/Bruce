#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feishu 流式输出 - 使用卡片显示"正在思考"
"""

import requests
import json
import time

class FeishuStreaming:
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.tenant_access_token = None
        self.base_url = "https://open.feishu.cn/open-apis"

    def get_tenant_access_token(self):
        """获取 tenant_access_token"""
        if self.tenant_access_token:
            return self.tenant_access_token

        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json"}
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }

        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        if result.get("code") != 0:
            raise Exception(f"获取 token 失败: {result}")

        self.tenant_access_token = result["tenant_access_token"]
        return self.tenant_access_token

    def send_thinking_card(self, receive_id):
        """发送'正在思考'卡片"""
        token = self.get_tenant_access_token()

        # 构建卡片内容
        card_content = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": "🤔 正在思考中..."
                },
                "template": "turquoise"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": "Bruce 正在处理您的请求，请稍候..."
                    }
                },
                {
                    "tag": "action",
                    "actions": []
                }
            ]
        }

        url = f"{self.base_url}/message/v4/send?receive_id_type=open_id"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        data = {
            "receive_id": receive_id,
            "msg_type": "interactive",
            "content": json.dumps({"card": card_content})
        }

        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        if result.get("code") != 0:
            raise Exception(f"发送卡片失败: {result}")

        return result.get("data", {}).get("message_id")

    def update_message_text(self, message_id, text):
        """更新消息为文本内容（替代卡片）"""
        token = self.get_tenant_access_token()

        url = f"{self.base_url}/im/v1/messages/{message_id}/update"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        data = {
            "msg_type": "text",
            "content": json.dumps({"text": text})
        }

        response = requests.put(url, headers=headers, json=data)
        result = response.json()

        if result.get("code") != 0:
            raise Exception(f"更新消息失败: {result}")

        return result

    def send_and_update(self, receive_id, final_text, delay=3):
        """发送'正在思考'卡片，然后更新为最终文本"""
        # 1. 发送卡片
        print(f"发送'正在思考'卡片到 {receive_id}")
        message_id = self.send_thinking_card(receive_id)
        print(f"卡片已发送，消息ID: {message_id}")

        # 2. 等待处理
        print(f"等待 {delay} 秒...")
        time.sleep(delay)

        # 3. 更新为最终文本
        print("更新为最终文本...")
        self.update_message_text(message_id, final_text)
        print("更新完成！")

        return message_id


def test_streaming():
    """测试流式输出"""
    # 从配置文件读取
    with open('/home/lejurobot/.moltbot/moltbot.json', 'r') as f:
        config = json.load(f)

    app_id = config['channels']['feishu']['appId']
    app_secret = config['channels']['feishu']['appSecret']

    # 创建流式输出对象
    streaming = FeishuStreaming(app_id, app_secret)

    # 目标用户ID（需要替换成实际的用户ID）
    target_user = "ou_xxxxxxxxxxxxxxxx"  # 替换成实际的 open_id

    # 测试发送和更新
    final_text = """✅ 思考完成！

这是流式输出的效果：

1. 先发送"正在思考"卡片
2. 处理完成后更新为实际内容

这样你就知道我已经收到你的消息了！"""

    streaming.send_and_update(target_user, final_text, delay=3)


if __name__ == "__main__":
    # 如果有命令行参数，使用第一个参数作为用户ID
    import sys
    if len(sys.argv) > 1:
        target_user = sys.argv[1]
    else:
        print("用法: python feishu_streaming.py <用户ID>")
        print("示例: python feishu_streaming.py ou_xxxxxxxxxxxxxxxx")
        sys.exit(1)

    # 读取配置
    with open('/home/lejurobot/.moltbot/moltbot.json', 'r') as f:
        config = json.load(f)

    app_id = config['channels']['feishu']['appId']
    app_secret = config['channels']['feishu']['appSecret']

    # 创建流式输出对象
    streaming = FeishuStreaming(app_id, app_secret)

    # 发送测试卡片
    final_text = """✅ 思考完成！

这是流式输出的效果：

1. 先发送"正在思考"卡片
2. 处理完成后更新为实际内容

这样你就知道我已经收到你的消息了！"""

    streaming.send_and_update(target_user, final_text, delay=3)
