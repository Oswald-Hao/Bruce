#!/bin/bash
# Feishu通知工具
# 用途：在技能测试完成后发送通知到主会话

if [ $# -lt 2 ]; then
    echo "用法: $0 \"[消息内容]\" [技能进度]"
    echo "示例: $0 \"Data Collector 已完成并测试通过\" \"54/200\""
    exit 1
fi

MESSAGE="$1"
PROGRESS="$2"

# 格式化通知消息
NOTIFICATION="✅ $MESSAGE - 进度: $PROGRESS"

# 通过moltbot发送到主会话
node /home/lejurobot/moltbot/moltbot.mjs agent \
  --message "$NOTIFICATION" \
  --to "ou_ac30832212aa13310b80594b6a24b8d9" \
  --channel feishu \
  --deliver

if [ $? -eq 0 ]; then
    echo "✅ Feishu通知已发送: $NOTIFICATION"
else
    echo "❌ Feishu通知发送失败"
    exit 1
fi
