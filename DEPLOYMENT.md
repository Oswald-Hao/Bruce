# Bruce部署指南

## 概述

这是一个完整的Bruce部署系统，包括：
- 🤖 Bruce核心（技能、记忆、进化系统）
- 📦 Moltbot（AI助手框架，源代码已包含在vendor/moltbot/）
- ☁️ Cloudflared（隧道服务，需手动下载安装）
- 🏠 HomeKit（Siri集成）

---

## 快速开始

### 克隆仓库

```bash
git clone git@github.com:Oswald-Hao/Bruce.git
cd Bruce
```

### 安装Moltbot

**Moltbot源代码已包含在vendor/moltbot/中，无需下载！**

```bash
cd vendor/moltbot
pnpm install
```

**配置Moltbot：**
```bash
# 复制配置模板到home目录
cp ../../MOLTBOT_CONFIG.example ~/.clawdbot/config.json

# 编辑配置
vim ~/.clawdbot/config.json
```

**启动Moltbot：**
```bash
cd vendor/moltbot
node moltbot.mjs gateway start
```

---

## Cloudflared安装（HomeKit使用）

### 下载并安装

```bash
# 下载最新版本
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64

# 安装到系统
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
sudo chmod +x /usr/local/bin/cloudflared

# 验证安装
cloudflared --version
```

### 配置Cloudflared

**登录Cloudflare：**
```bash
cloudflared tunnel login
```

**创建隧道：**
```bash
cloudflared tunnel create bruce-homekit
```

**配置隧道：**
```bash
# 创建配置目录
mkdir -p ~/.cloudflared

# 创建配置文件
vim ~/.cloudflared/config.yml
```

**配置示例：**
```yaml
tunnel: <tunnel-id>
credentials-file: /home/lejurobot/.cloudflared/<tunnel-id>.json

ingress:
  - hostname: bruce.yourdomain.com
    service: http://localhost:18790
  - service: http_status:404
```

**运行隧道：**
```bash
cloudflared tunnel run bruce-homekit
```

**设置为系统服务：**
```bash
sudo cloudflared service install
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

---

## 配置HomeKit服务

### 安装依赖

```bash
cd services/homekit-bruce
npm install
```

### 启动HomeKit服务

```bash
node services/homekit-bruce/index.js
```

### 创建systemd服务（可选）

```bash
sudo cp services/homekit-bruce/homekit-bruce.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start homekit-bruce
sudo systemctl enable homekit-bruce
```

---

## 验证部署

### 检查Moltbot

```bash
cd vendor/moltbot
node moltbot.mjs status

# 应该显示：
# Gateway: running
# Sessions: X
```

### 检查Cloudflared

```bash
# 查看版本
cloudflared --version

# 查看隧道状态
sudo systemctl status cloudflared
```

### 检查HomeKit

```bash
# 检查端口监听
sudo netstat -tulpn | grep 18790

# 查看服务日志
sudo journalctl -u homekit-bruce -f
```

---

## 目录结构

```
Bruce/
├── skills/                  # 技能目录
│   ├── data-collector/
│   ├── script-generator/
│   └── ...
├── tools/                   # 工具脚本
│   ├── git-push.sh          # Git推送
│   ├── file-watcher.py      # 文件监听器
│   ├── auto-push-guide.md   # 自动推送说明
│   └── auto-push.md         # 自动推送说明
├── services/                # 服务配置
│   └── homekit-bruce/       # HomeKit服务
├── vendor/                  # 第三方软件
│   └── moltbot/             # Moltbot源代码（已包含）
│       ├── src/             # 源代码
│       ├── extensions/       # 扩展
│       ├── skills/          # 技能
│       ├── package.json      # 依赖配置
│       └── pnpm-lock.yaml   # 锁文件
├── memory/                  # 记忆文件
├── evolution-log.md          # 进化日志
├── evolution-tasks.md        # 进化任务
├── README.md                # 主文档
├── DEPLOYMENT.md            # 本文档
├── MOLTBOT_CONFIG.example   # Moltbot配置模板
└── .git/hooks/post-commit   # Git钩子

# 外部目录
~/.clawdbot/                # Moltbot配置
~/.cloudflared/             # Cloudflared配置
```

---

## 故障排查

### 问题：Moltbot无法启动

```bash
# 检查日志
cd vendor/moltbot
node moltbot.mjs status

# 检查配置
cat ~/.clawdbot/config.json

# 检查端口占用
sudo netstat -tulpn | grep <port>
```

### 问题：Cloudflared无法连接

```bash
# 检查隧道状态
cloudflared tunnel list

# 检查配置
cat ~/.cloudflared/config.yml

# 查看日志
sudo journalctl -u cloudflared -f
```

### 问题：HomeKit无法配对

```bash
# 检查服务状态
sudo systemctl status homekit-bruce

# 检查端口
sudo netstat -tulpn | grep 18790

# 查看日志
sudo journalctl -u homekit-bruce -n 50

# 确保防火墙允许端口
sudo ufw allow 18790
```

---

## 管理命令

### Moltbot管理

```bash
# 进入Moltbot目录
cd vendor/moltbot

# 启动
node moltbot.mjs gateway start

# 停止
node moltbot.mjs gateway stop

# 重启
node moltbot.mjs gateway restart

# 状态
node moltbot.mjs status

# Cron任务
node moltbot.mjs cron list
```

### Cloudflared管理

```bash
# 查看隧道
cloudflared tunnel list

# 运行隧道
cloudflared tunnel run <tunnel-name>

# 服务状态
sudo systemctl status cloudflared

# 重启服务
sudo systemctl restart cloudflared
```

### HomeKit管理

```bash
# 服务状态
sudo systemctl status homekit-bruce

# 重启服务
sudo systemctl restart homekit-bruce

# 查看日志
sudo journalctl -u homekit-bruce -f
```

---

## 换电脑后使用

### 1. 克隆仓库

```bash
git clone git@github.com:Oswald-Hao/Bruce.git
cd Bruce
```

### 2. 安装Moltbot

```bash
cd vendor/moltbot
pnpm install
```

### 3. 配置Moltbot

```bash
cp ../../MOLTBOT_CONFIG.example ~/.clawdbot/config.json
vim ~/.clawdbot/config.json
```

### 4. 安装Cloudflared

```bash
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
sudo chmod +x /usr/local/bin/cloudflared
```

### 5. 启动Moltbot

```bash
cd vendor/moltbot
node moltbot.mjs gateway start
```

---

## 相关文档

- [README.md](README.md) - 主文档
- [Moltbot文档](https://docs.molt.bot)
- [Cloudflared文档](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [vendor/moltbot/README.md](vendor/moltbot/README.md) - Moltbot详细说明

---

## 支持

**仓库：** https://github.com/Oswald-Hao/Bruce.git  
**问题反馈：** 提交Issue到GitHub

---

**最后更新：** 2026-02-02
