#!/usr/bin/env python3
# 飞书 Webhook - 完整日志版本

from flask import Flask, request, jsonify
import json
import sys
from datetime import datetime

app = Flask(__name__)

APP_ID = "cli_a9f05a5e0378dcb0"
APP_SECRET = "KdosR8d6vhlLdM6yP9nrUdSwb2VoevJr"

LOG_FILE = "/tmp/feishu-webhook-detailed.log"

def log_message(msg):
    """写入日志文件"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(msg)
    sys.stdout.flush()

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """处理飞书 Webhook"""
    try:
        log_message("="*60)
        log_message(f"📨 收到 {request.method} 请求")
        log_message(f"URL: {request.url}")
        log_message(f"Headers: {json.dumps(dict(request.headers), indent=2)}")

        # GET 请求
        if request.method == 'GET':
            return jsonify({"status": "ok", "app_id": APP_ID})

        # POST 请求
        raw_data = request.get_data(as_text=True)
        log_message(f"Raw Body: {raw_data}")

        try:
            data = json.loads(raw_data) if raw_data else {}
        except:
            data = {}

        log_message(f"Parsed Data: {json.dumps(data, indent=2, ensure_ascii=False)}")

        # URL 验证
        if data and data.get('type') == 'url_verification':
            challenge = data.get('challenge')
            log_message(f"✓ URL验证 - challenge: {challenge}")
            response = {"challenge": challenge}
            log_message(f"响应: {json.dumps(response)}")
            return jsonify(response)

        # 消息事件
        if data and data.get('header', {}).get('event_type') == 'im.message.receive_v1':
            log_message("✓ 收到消息事件")

            event = data.get('event', {})
            sender = event.get('sender', {})
            message = event.get('message', {})

            sender_id = sender.get('sender_id', {}).get('open_id', '')
            message_type = message.get('message_type', '')
            content_str = message.get('content', '{}')

            log_message(f"发送者: {sender_id}")
            log_message(f"消息类型: {message_type}")
            log_message(f"消息内容: {content_str}")

            # 解析文本消息
            if message_type == 'text':
                try:
                    content = json.loads(content_str)
                    text = content.get('text', '')
                    log_message(f"文本内容: {text}")

                    # 回复表情
                    reply_with_emoji(message.get('chat_id'), text, sender_id, data)

                except Exception as e:
                    log_message(f"解析文本失败: {e}")

            return jsonify({"code": 0, "msg": "success"})

        log_message("默认响应")
        return jsonify({"code": 0, "msg": "ok"})

    except Exception as e:
        log_message(f"❌ 错误: {e}")
        import traceback
        log_message(f"Traceback: {traceback.format_exc()}")
        return jsonify({"code": 1, "msg": str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    """首页"""
    return jsonify({"service": "Bruce Feishu Webhook", "status": "running"})

def reply_with_emoji(chat_id, text, sender_id):
    """回复表情"""
    try:
        import requests

        # 获取 token
        token_resp = requests.post(
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            json={"app_id": APP_ID, "app_secret": APP_SECRET}
        )
        tenant_token = token_resp.json()['tenant_access_token']
        log_message(f"✓ 获取 token 成功")

        # 关键词映射
        emoji_map = {
            '你好': '👋', 'hi': '👋',
            '谢谢': '🙏', 'thank': '🙏',
            '哈哈': '😂', 'haha': '😂',
            '棒': '👍', 'good': '👍',
            '666': '🔥',
            '爱你': '❤️', 'love': '❤️',
            '加油': '💪',
        }

        emoji = None
        for keyword, emo in emoji_map.items():
            if keyword in text.lower():
                emoji = emo
                log_message(f"✓ 匹配到关键词: {keyword} -> {emoji}")
                break

        if not emoji:
            emoji = '👍'
            log_message(f"✓ 默认表情: {emoji}")

        # 发送表情回复（使用 reactions API）
        message_id = webhook_data.get('event', {}).get('message', {}).get('message_id', '')

        if message_id:
            # 发送表情反应
            emoji_resp = requests.post(
                f"https://open.feishu.cn/open-apis/im/v1/messages/{message_id}/reactions",
                headers={
                    "Authorization": f"Bearer {tenant_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "emoji_type": "static",
                    "emoji_id": emoji
                }
            )

            result = emoji_resp.json()
            log_message(f"✓ 表情回复: {json.dumps(result, ensure_ascii=False)}")
        else:
            # 回退到文本消息
            message = f"{emoji}"
            send_resp = requests.post(
                "https://open.feishu.cn/open-apis/message/v4/send?receive_id_type=open_id",
                headers={
                    "Authorization": f"Bearer {tenant_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "msg_type": "text",
                    "receive_id": sender_id,
                    "open_id": sender_id,
                    "content": {"text": message}
                }
            )
            result = send_resp.json()
            log_message(f"✓ 文本回复: {json.dumps(result, ensure_ascii=False)}")

        result = send_resp.json()
        log_message(f"✓ 回复消息: {json.dumps(result, ensure_ascii=False)}")

    except Exception as e:
        log_message(f"❌ 回复失败: {e}")
        import traceback
        log_message(f"Traceback: {traceback.format_exc()}")

if __name__ == '__main__':
    log_message("="*60)
    log_message("🤖 Bruce 飞书 Webhook 服务器启动")
    log_message("="*60)
    app.run(host='0.0.0.0', port=5000, debug=False)
