#!/bin/bash
# Bruce一键安装脚本
# 自动安装Moltbot、Cloudflared和配置

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "🤖 Bruce一键安装脚本"
echo "======================"
echo ""

# 检查系统要求
echo "🔍 检查系统要求..."
if ! command -v node &> /dev/null; then
    echo "❌ 未找到Node.js"
    echo "请先安装Node.js 14+："
    echo "  curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -"
    echo "  sudo apt-get install -y nodejs"
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "❌ 未找到Git"
    echo "请先安装Git：sudo apt-get install git"
    exit 1
fi

echo "✅ 系统要求检查通过"
echo ""

# 安装Moltbot
echo "📦 安装Moltbot..."
./tools/install-moltbot.sh
echo ""

# 安装Cloudflared
echo "☁️  安装Cloudflared..."
./tools/install-cloudflared.sh
echo ""

# 安装Python依赖
echo "🐍 安装Python依赖..."
if command -v pip3 &> /dev/null; then
    pip3 install requests beautifulsoup4 pillow || echo "⚠️  Python依赖安装失败，请手动安装"
else
    echo "⚠️  未找到pip3，跳过Python依赖安装"
fi
echo ""

# 配置自动推送
echo "🔄 配置自动推送..."
if [ -f ".git/hooks/post-commit" ]; then
    chmod +x .git/hooks/post-commit
    echo "✅ Git钩子已配置"
else
    echo "⚠️  Git钩子未找到"
fi
echo ""

# 启动文件监听器
echo "👀 启动文件监听器..."
if pgrep -f "file-watcher.py" > /dev/null; then
    echo "✅ 文件监听器已在运行"
else
    python3 tools/file-watcher.py "$(pwd)" 30 > /dev/null 2>&1 &
    echo "✅ 文件监听器已启动"
fi
echo ""

echo ""
echo "🎉 Bruce安装完成！"
echo ""
echo "下一步："
echo "1. 配置Moltbot：vim ~/.clawdbot/config.json"
echo "2. 启动Moltbot：moltbot gateway start"
echo "3. 配置HomeKit（可选）："
echo "   cd services/homekit-bruce"
echo "   npm install"
echo "   node index.js"
echo ""
echo "文档参考：README.md"
