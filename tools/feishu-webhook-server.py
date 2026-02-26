#!/usr/bin/env python3
# 飞书 Webhook 服务器

from flask import Flask, request, jsonify
import json
import hmac
import hashlib
import base64

app = Flask(__name__)

# 飞书配置
APP_ID = "cli_a9f05a5e0378dcb0"
APP_SECRET = "KdosR8d6vhlLdM6yP9nrUdSwb2VoevJr"
VERIFICATION_TOKEN = "bruce_feishu_bot"  # 需要在飞书后台配置

@app.route('/webhook', methods=['POST'])
def webhook():
    """处理飞书 Webhook"""
    try:
        # 获取请求数据
        data = request.get_json()
        print(f"\n📨 收到 Webhook:")
        print(f"Headers: {dict(request.headers)}")
        print(f"Body: {json.dumps(data, indent=2, ensure_ascii=False)}")

        # URL 验证（首次配置时）
        if data.get('type') == 'url_verification':
            challenge = data.get('challenge')
            print(f"✓ URL验证挑战: {challenge}")
            return jsonify({
                "challenge": challenge
            })

        # 验证签名
        timestamp = request.headers.get('X-Lark-Request-Timestamp', '')
        nonce = request.headers.get('X-Lark-Request-Nonce', '')
        signature = request.headers.get('X-Lark-Signature', '')
        body = request.get_data(as_text=True)

        # 简化：暂时跳过签名验证（生产环境需要启用）
        print(f"Timestamp: {timestamp}")
        print(f"Nonce: {nonce}")
        print(f"Signature: {signature[:20]}...")

        # 处理消息事件
        if data.get('header', {}).get('event_type') == 'im.message.receive_v1':
            event = data.get('event', {})
            message = event.get('message', {})
            sender = event.get('sender', {})

            # 提取消息内容
            message_type = message.get('message_type', '')
            content_str = message.get('content', '{}')
            content = json.loads(content_str)

            text = content.get('text', '')
            sender_id = sender.get('sender_id', {}).get('open_id', '')

            print(f"\n💬 收到消息:")
            print(f"  发送者: {sender_id}")
            print(f"  类型: {message_type}")
            print(f"  内容: {text}")

            # 自动回复表情
            if text:
                reply_with_emoji(message.get('chat_id'), text)

        return jsonify({"code": 0, "msg": "success"})

    except Exception as e:
        print(f"❌ 处理 Webhook 失败: {e}")
        return jsonify({"code": 1, "msg": str(e)}), 500

def reply_with_emoji(chat_id, text):
    """根据消息内容回复表情"""
    try:
        import requests

        # 获取 token
        token_resp = requests.post(
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            json={
                "app_id": APP_ID,
                "app_secret": APP_SECRET
            }
        )
        tenant_token = token_resp.json()['tenant_access_token']

        # 简单的关键词匹配
        emoji_map = {
            '你好': '👋',
            '谢谢': '🙏',
            '哈哈': '😂',
            '棒': '👍',
            '666': '🔥',
            '爱你': '❤️',
            '加油': '💪',
        }

        emoji = None
        for keyword, emo in emoji_map.items():
            if keyword in text:
                emoji = emo
                break

        if emoji:
            # 发送表情
            emoji_resp = requests.post(
                f"https://open.feishu.cn/open-apis/im/v1/messages/{chat_id}/reactions",
                headers={
                    "Authorization": f"Bearer {tenant_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "emoji_type": "static",
                    "emoji_id": emoji
                }
            )
            print(f"✓ 回复表情: {emoji}")
        else:
            print("  未匹配到表情，发送文本回复")
            # 发送文本回复
            requests.post(
                "https://open.feishu.cn/open-apis/message/v4/send?receive_id_type=open_id",
                headers={
                    "Authorization": f"Bearer {tenant_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "msg_type": "text",
                    "receive_id": chat_id,
                    "open_id": chat_id,
                    "content": {"text": f"收到你的消息：{text}\n\n输入 /help 查看命令"}
                }
            )

    except Exception as e:
        print(f"❌ 回复失败: {e}")

if __name__ == '__main__':
    print("=" * 60)
    print("🤖 飞书 Webhook 服务器启动")
    print("=" * 60)
    print(f"📡 监听地址: http://0.0.0.0:5000/webhook")
    print(f"🌐 公网地址: https://lovely-suspected-missile-bingo.trycloudflare.com/webhook")
    print("=" * 60)
    print("\n请在飞书后台配置 Webhook URL:")
    print("https://lovely-suspected-missile-bingo.trycloudflare.com/webhook\n")

    app.run(host='0.0.0.0', port=5000)
