#!/bin/bash
# Telegram Bot 自动重启脚本

BOT_PID=""

while true; do
    echo "🤖 启动 Telegram Bot..."
    
    python3 /home/lejurobot/clawd/tools/telegram-bot.py > /tmp/telegram-bot.log 2>&1 &
    BOT_PID=$!
    
    echo "✓ Bot PID: $BOT_PID"
    
    # 等待进程结束
    wait $BOT_PID
    EXIT_CODE=$?
    
    echo "⚠️ Bot 意外退出！退出码: $EXIT_CODE"
    echo "🔄 5秒后自动重启..."
    sleep 5
    
done
