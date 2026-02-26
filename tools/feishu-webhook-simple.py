#!/usr/bin/env python3
# 简化的飞书 Webhook 处理器 - 使用 Flask

from flask import Flask, request, jsonify
import json

app = Flask(__name__)

APP_ID = "cli_a9f05a5e0378dcb0"
APP_SECRET = "KdosR8d6vhlLdM6yP9nrUdSwb2VoevJr"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """处理飞书 Webhook"""
    try:
        # 记录请求
        print(f"\n{'='*60}")
        print(f"📨 收到 {request.method} 请求")
        print(f"URL: {request.url}")
        print(f"Headers: {dict(request.headers)}")

        # GET 请求 - 健康检查
        if request.method == 'GET':
            return jsonify({
                "status": "ok",
                "service": "feishu-webhook",
                "app_id": APP_ID
            })

        # POST 请求
        try:
            raw_data = request.get_data(as_text=True)
            print(f"Raw Body: {raw_data}")
            data = json.loads(raw_data) if raw_data else {}
        except:
            data = {}
        print(f"Parsed Body: {json.dumps(data, indent=2, ensure_ascii=False)}")

        # URL 验证
        if data and data.get('type') == 'url_verification':
            challenge = data.get('challenge')
            print(f"✓ URL验证挑战")
            response = {"challenge": challenge}
            print(f"响应: {json.dumps(response, ensure_ascii=False)}")
            return jsonify(response)

        # 消息事件
        if data and data.get('header', {}).get('event_type') == 'im.message.receive_v1':
            print("✓ 收到消息事件")
            return jsonify({"code": 0, "msg": "success"})

        # 默认响应
        return jsonify({"code": 0, "msg": "ok"})

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"code": 1, "msg": str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    """首页"""
    return jsonify({
        "service": "Bruce Feishu Webhook",
        "status": "running",
        "endpoints": {
            "webhook": "/webhook (POST)",
            "health": "/ (GET)"
        }
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🤖 Bruce 飞书 Webhook 服务器")
    print("="*60)
    print(f"📡 本地: http://localhost:5000")
    print(f"📡 内网: http://10.10.10.18:5000")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=False)
