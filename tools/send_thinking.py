#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发送 Feishu "正在思考"卡片给当前会话用户
"""

import sys
import json
from feishu_streaming import FeishuStreaming

def send_thinking():
    """发送"正在思考"卡片"""
    # 读取配置
    with open('/home/lejurobot/.moltbot/moltbot.json', 'r') as f:
        config = json.load(f)

    app_id = config['channels']['feishu']['appId']
    app_secret = config['channels']['feishu']['appSecret']

    # 创建流式输出对象
    streaming = FeishuStreaming(app_id, app_secret)

    # 获取用户ID（从命令行参数）
    if len(sys.argv) < 2:
        print("用法: python send_thinking.py <用户ID>")
        print("示例: python send_thinking.py ou_xxxxxxxxxxxxxxxx")
        print()
        print("你的用户 ID 格式：ou_xxxxxxxxxxxxxxxx")
        sys.exit(1)

    user_id = sys.argv[1]

    # 发送"正在思考"卡片
    print(f"发送'正在思考'卡片到 {user_id}")
    message_id = streaming.send_thinking_card(user_id)
    print(f"卡片已发送，消息ID: {message_id}")
    print()
    print("你现在可以使用以下命令更新消息：")
    print(f"python3 /home/lejurobot/clawd/tools/feishu-streaming.py {user_id}")

    return message_id

if __name__ == "__main__":
    send_thinking()
