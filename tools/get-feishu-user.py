#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取当前会话的 Feishu 用户 ID
"""

import json
import requests

def get_user_info():
    """读取 Moltbot 配置，获取当前会话的用户ID"""
    # 这里需要从 Moltbot 的会话信息中获取
    # 目前先提供手动查询的方法

    with open('/home/lejurobot/.moltbot/moltbot.json', 'r') as f:
        config = json.load(f)

    app_id = config['channels']['feishu']['appId']
    app_secret = config['channels']['feishu']['appSecret']

    print("Feishu 配置信息:")
    print(f"App ID: {app_id}")
    print(f"App Secret: {app_secret[:10]}...")
    print()
    print("要测试流式输出，请告诉我你的 Feishu 用户 ID (open_id)")
    print("格式：ou_xxxxxxxxxxxxxxxx")

if __name__ == "__main__":
    get_user_info()
