#!/bin/bash
# Moltbot安装脚本
# 自动下载和配置Moltbot

set -e

MOLTBOT_DIR="/home/lejurobot/moltbot"
MOLTBOT_REPO="https://github.com/moltbot/moltbot.git"
VENDOR_DIR="$(dirname "$0")/vendor/moltbot"

echo "📦 Moltbot安装脚本"
echo "==================="

# 检查是否已经安装
if [ -d "$MOLTBOT_DIR" ]; then
    echo "✅ Moltbot已经安装在：$MOLTBOT_DIR"
    echo "如需重新安装，请先删除：sudo rm -rf $MOLTBOT_DIR"
    exit 0
fi

# 下载Moltbot
echo "📥 下载Moltbot..."
git clone "$MOLTBOT_REPO" "$MOLTBOT_DIR"

# 安装依赖
echo "🔧 安装依赖..."
cd "$MOLTBOT_DIR"

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 未找到Node.js，请先安装Node.js 14+"
    exit 1
fi

# 安装npm依赖（如果使用pnpm，使用pnpm）
if command -v pnpm &> /dev/null; then
    pnpm install
else
    npm install
fi

# 创建配置目录
echo "📁 创建配置目录..."
mkdir -p ~/.clawdbot

# 复制配置模板
if [ -f "$MOLTBOT_DIR/.env.example" ]; then
    cp "$MOLTBOT_DIR/.env.example" ~/.clawdbot/config.json
    echo "✅ 配置文件已创建：~/.clawdbot/config.json"
else
    echo "⚠️  未找到.env.example，请手动创建配置文件"
fi

# 创建链接（可选）
echo "🔗 创建快捷命令..."
if [ ! -L /usr/local/bin/moltbot ]; then
    sudo ln -s "$MOLTBOT_DIR/moltbot.mjs" /usr/local/bin/moltbot 2>/dev/null || echo "⚠️  无法创建全局命令（需要sudo权限）"
fi

echo ""
echo "✅ Moltbot安装完成！"
echo ""
echo "下一步："
echo "1. 编辑配置文件：vim ~/.clawdbot/config.json"
echo "2. 启动Moltbot：moltbot gateway start"
echo ""
echo "更多信息：https://github.com/moltbot/moltbot"
