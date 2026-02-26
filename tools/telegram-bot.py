#!/usr/bin/env python3
# Telegram Bot 监听服务 - Bruce

import requests
import time
import subprocess
import json
import sys
from datetime import datetime

# 强制刷新输出
sys.stdout.reconfigure(line_buffering=True)

# Telegram 配置
BOT_TOKEN = "8744492015:AAHejYg5eCEaaQSmI4hT4OnlRX_12kyIcTk"
CHAT_ID = "8125507347"
PROXY = "http://127.0.0.1:7897"

def send_message(text):
    """发送消息到 Telegram"""
    try:
        proxies = {"http": PROXY, "https": PROXY}
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": text}
        resp = requests.post(url, json=data, proxies=proxies, timeout=10)
        print(f"✓ 发送消息: {text[:50]}... | 状态: {resp.status_code}")
        if resp.status_code != 200:
            print(f"  响应: {resp.text}")
    except Exception as e:
        print(f"✗ 发送失败: {e}")

def handle_message(message_text):
    """处理收到的消息"""
    message_text = message_text.strip().lower()
    
    # 帮助命令
    if message_text in ['/start', '/help', '帮助']:
        return """🤖 Bruce Bot 命令列表：

/status - 查看系统状态
/time - 查看当前时间
/weather - 查看深圳天气
/fitness - 健身提醒
/progress - 进化进度
/ai - AI资讯

或者直接跟我对话！"""

    # 状态查询
    elif message_text in ['/status', '状态']:
        try:
            result = subprocess.run(['uptime'], capture_output=True, text=True)
            return f"📊 系统状态：\n{result.stdout}"
        except:
            return "❌ 无法获取系统状态"

    # 时间查询
    elif message_text in ['/time', '时间']:
        now = datetime.now()
        return f"🕐 当前时间：\n{now.strftime('%Y-%m-%d %H:%M:%S')}"

    # 进度查询
    elif message_text in ['/progress', '进度']:
        return """📈 进化进度：64/200 (32%)

最近完成的技能：
- AI Agent开发系统
- 智能推荐系统
- 跨境电商系统

继续努力！⚙️"""

    # 默认回复
    else:
        return f"收到你的消息：{message_text}\n\n输入 /help 查看可用命令"

def main():
    """主循环"""
    print("🤖 Bruce Bot 启动...")
    print(f"📱 监听 Telegram: @{CHAT_ID}")
    send_message("🟢 Bruce Bot 已启动！输入 /help 查看命令")

    last_update_id = 0

    while True:
        try:
            proxies = {"http": PROXY, "https": PROXY}
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

            # 第一次不使用 offset，获取所有未读消息
            if last_update_id == 0:
                params = {"timeout": 10}
            else:
                params = {"offset": last_update_id + 1, "timeout": 30}

            response = requests.get(url, params=params, proxies=proxies, timeout=35)
            result = response.json()

            if result.get("ok"):
                for update in result.get("result", []):
                    last_update_id = update["update_id"]

                    if "message" in update:
                        message = update["message"]
                        text = message.get("text")

                        if text and text != "/start":
                            print(f"📨 收到消息: {text}")
                            reply = handle_message(text)
                            send_message(reply)
                            
        except KeyboardInterrupt:
            print("\n👋 Bot 已停止")
            send_message("🔴 Bruce Bot 已停止")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")
            time.sleep(5)
            
if __name__ == "__main__":
    main()
