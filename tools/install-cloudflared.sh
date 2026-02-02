#!/bin/bash
# Cloudflared安装脚本
# 自动下载和配置Cloudflared

set -e

echo "☁️  Cloudflared安装脚本"
echo "======================"

# 检查是否已经安装
if command -v cloudflared &> /dev/null; then
    VERSION=$(cloudflared --version)
    echo "✅ Cloudflared已经安装：$VERSION"
    echo "如需重新安装，请先删除：sudo rm /usr/local/bin/cloudflared"
    exit 0
fi

# 检测系统架构
ARCH=$(uname -m)
case $ARCH in
    x86_64)
        BINARY_URL="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
        ;;
    aarch64|arm64)
        BINARY_URL="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64"
        ;;
    armv7l)
        BINARY_URL="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm"
        ;;
    *)
        echo "❌ 不支持的架构：$ARCH"
        exit 1
        ;;
esac

# 下载Cloudflared
echo "📥 下载Cloudflared..."
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

wget -O cloudflared "$BINARY_URL" || curl -L -o cloudflared "$BINARY_URL"

# 安装到系统
echo "📦 安装到系统..."
sudo mv cloudflared /usr/local/bin/cloudflared
sudo chmod +x /usr/local/bin/cloudflared

# 清理临时文件
cd -
rm -rf "$TEMP_DIR"

# 验证安装
VERSION=$(cloudflared --version)
echo ""
echo "✅ Cloudflared安装成功！"
echo "版本：$VERSION"
echo ""
echo "验证安装：cloudflared --version"
echo "登录账户：cloudflared tunnel login"
echo "创建隧道：cloudflared tunnel create <name>"
