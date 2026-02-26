#!/usr/bin/env python3
# Telegram Bot - 简化版，避免所有问题

import requests
import time
import subprocess
from datetime import datetime
import signal
import sys

# Telegram 配置
BOT_TOKEN = "8744492015:AAHejYg5eCEaaQSmI4hT4OnlRX_12kyIcTk"
CHAT_ID = "8125507347"
PROXY = "http://127.0.0.1:7897"

# 全局变量
running = True

def signal_handler(signum, frame):
    """处理退出信号"""
    global running
    print("\n🛑 收到停止信号，正在退出...")
    running = False

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def send_message(text):
    """发送消息"""
    try:
        proxies = {"http": PROXY, "https": PROXY}
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": text}
        resp = requests.post(url, json=data, proxies=proxies, timeout=10)
        result = resp.json()
        if result.get("ok"):
            print(f"✓ 已回复")
        else:
            print(f"✗ 发送失败: {result.get('description')}")
        return result.get("ok")
    except Exception as e:
        print(f"✗ 发送异常: {e}")
        return False

def handle_message(text):
    """处理消息"""
    text = text.strip().lower()
    
    if text in ['/start', '/help', '帮助']:
        return """🤖 Bruce Bot 命令：

/status - 系统状态
/time - 当前时间
/progress - 进化进度

或者直接聊天！"""
    
    elif text in ['/status', '状态']:
        try:
            result = subprocess.run(['uptime'], capture_output=True, text=True)
            return f"📊 系统运行时间：\n{result.stdout.strip()}"
        except:
            return "无法获取状态"
    
    elif text in ['/time', '时间']:
        now = datetime.now()
        return f"🕐 {now.strftime('%Y-%m-%d %H:%M:%S')}"
    
    elif text in ['/progress', '进度']:
        return "📈 进化进度：64/200 (32%)\n\n最近技能：AI Agent开发系统"
    
    else:
        return f"🤖 收到：{text}\n\n输入 /help 查看命令"

def main():
    """主循环"""
    print("=" * 50)
    print("🤖 Bruce Bot 启动")
    print("=" * 50)
    
    # 发送启动通知
    send_message("🟢 Bruce Bot 在线！输入 /help 开始")
    
    last_update_id = 0
    error_count = 0
    max_errors = 10
    
    while running and error_count < max_errors:
        try:
            proxies = {"http": PROXY, "https": PROXY}
            
            # 获取更新
            if last_update_id == 0:
                params = {"timeout": 10}
            else:
                params = {"offset": last_update_id + 1, "timeout": 30}
            
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            resp = requests.get(url, params=params, proxies=proxies, timeout=40)
            
            if resp.status_code != 200:
                print(f"✗ API 错误: {resp.status_code}")
                error_count += 1
                time.sleep(5)
                continue
            
            result = resp.json()
            
            if not result.get("ok"):
                print(f"✗ 响应错误: {result.get('description')}")
                error_count += 1
                time.sleep(5)
                continue
            
            # 重置错误计数
            error_count = 0
            
            # 处理消息
            for update in result.get("result", []):
                last_update_id = update["update_id"]
                
                if "message" in update:
                    msg = update["message"]
                    text = msg.get("text")
                    
                    if text and text != "/start":
                        print(f"\n📨 收到: {text}")
                        reply = handle_message(text)
                        send_message(reply)
            
        except requests.exceptions.Timeout:
            print("⏱️ 超时，继续...")
            continue
        except Exception as e:
            print(f"✗ 错误: {e}")
            error_count += 1
            time.sleep(3)
    
    if error_count >= max_errors:
        print(f"\n❌ 错误过多，停止运行")
        send_message("🔴 Bot 因错误停止")
    
    print("\n👋 Bot 已停止")

if __name__ == "__main__":
    main()
