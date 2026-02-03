#!/bin/bash
# 安装 moltbot-syncer 服务

set -e

SERVICE_FILE="/home/lejurobot/clawd/tools/moltbot-syncer.service"
SYSTEMD_DIR="/etc/systemd/system"

echo "🚀 安装 Moltbot Syncer 服务..."
echo ""

# 复制服务文件
echo "📋 复制服务文件到 $SYSTEMD_DIR"
sudo cp "$SERVICE_FILE" "$SYSTEMD_DIR/moltbot-syncer.service"

# 重新加载 systemd
echo "🔄 重新加载 systemd 配置"
sudo systemctl daemon-reload

# 启用并启动服务
echo "▶️  启用并启动服务"
sudo systemctl enable moltbot-syncer
sudo systemctl start moltbot-syncer

# 检查状态
echo ""
echo "✅ 安装完成！"
echo ""
echo "📊 服务状态:"
sudo systemctl status moltbot-syncer --no-pager | head -15
echo ""
echo "💡 查看日志: sudo journalctl -u moltbot-syncer -f"
