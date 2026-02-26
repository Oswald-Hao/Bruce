#!/usr/bin/env python3
# 飞书消息发送工具 - Bruce

import requests
import sys
import json

# Feishu应用配置
APP_ID = "cli_a9f05a5e0378dcb0"
APP_SECRET = "KdosR8d6vhlLdM6yP9nrUdSwb2VoevJr"
OPEN_ID = "ou_ac30832212aa13310b80594b6a24b8d9"  # Oswald的open_id

def get_tenant_access_token():
    """获取tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    data = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    if result["code"] != 0:
        raise Exception(f"获取token失败: {result['msg']}")

    return result["tenant_access_token"]

def send_message(text):
    """发送文本消息到飞书"""
    try:
        # 获取token
        token = get_tenant_access_token()

        # 发送消息
        url = "https://open.feishu.cn/open-apis/message/v4/send?receive_id_type=open_id"
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {token}"
        }
        data = {
            "msg_type": "text",
            "receive_id": OPEN_ID
        }

        # content必须是JSON对象
        data["content"] = {"text": text}

        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        if result["code"] == 0:
            msg_id = result.get('data', {}).get('msg_id', 'N/A')
            print(f"✅ 消息发送成功! Message ID: {msg_id}")
            return True
        else:
            print(f"❌ 消息发送失败: {result.get('msg', 'Unknown error')}")
            print(f"完整响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return False

    except Exception as e:
        print(f"❌ 发送消息时出错: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 send-feishu.py \"消息内容\"")
        print("\n示例:")
        print("  python3 send-feishu.py \"你好，Bruce！\"")
        sys.exit(1)

    message = sys.argv[1]
    send_message(message)
