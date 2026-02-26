#!/usr/bin/env python3
# Telegram 消息发送工具 - Bruce

import requests
import sys
import os

# Telegram 配置
BOT_TOKEN = "8744492015:AAHejYg5eCEaaQSmI4hT4OnlRX_12kyIcTk"
CHAT_ID = "8125507347"
PROXY = "http://127.0.0.1:7897"

def send_message(text, parse_mode=None):
    """发送消息到 Telegram"""
    try:
        proxies = {
            "http": PROXY,
            "https": PROXY
        }

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": CHAT_ID,
            "text": text
        }

        if parse_mode:
            data["parse_mode"] = parse_mode

        response = requests.post(url, json=data, proxies=proxies, timeout=10)
        result = response.json()

        if result.get("ok"):
            print(f"✅ 消息发送成功!")
            return True
        else:
            print(f"❌ 发送失败: {result.get('description')}")
            return False

    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 send-telegram.py \"消息内容\"")
        sys.exit(1)

    message = sys.argv[1]
    send_message(message)
