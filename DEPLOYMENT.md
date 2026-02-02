# Bruce部署指南

## 概述

这是一个完整的Bruce部署系统，包括：
- 🤖 Bruce核心（技能、记忆、进化系统）
- 📦 Moltbot（AI助手框架）
- ☁️ Cloudflared（隧道服务）
- 🏠 HomeKit（Siri集成）

## 一键部署（推荐）

### 快速开始

```bash
# 1. 克隆仓库
git clone git@github.com:Oswald-Hao/Bruce.git
cd Bruce

# 2. 运行一键安装
./install.sh

# 3. 配置Moltbot
vim ~/.clawdbot/config.json

# 4. 启动Moltbot
moltbot gateway start
```

### 一键安装包括

✅ 安装Moltbot到 `~/moltbot`  
✅ 安装Cloudflared到 `/usr/local/bin/cloudflared`  
✅ 安装Python依赖（requests, beautifulsoup4, pillow）  
✅ 配置Git钩子（自动推送）  
✅ 启动文件监听器（30秒检测周期）

---

## 手动部署

### 步骤1：克隆仓库

```bash
git clone git@github.com:Oswald-Hao/Bruce.git
cd Bruce
```

### 步骤2：安装Moltbot

**方式A：使用安装脚本**
```bash
./tools/install-moltbot.sh
```

**方式B：手动安装**
```bash
git clone https://github.com/moltbot/moltbot.git ~/moltbot
cd ~/moltbot
pnpm install
```

### 步骤3：安装Cloudflared

**方式A：使用安装脚本**
```bash
./tools/install-cloudflared.sh
```

**方式B：手动安装**
```bash
# 下载
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64

# 安装
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
sudo chmod +x /usr/local/bin/cloudflared

# 验证
cloudflared --version
```

### 步骤4：安装Python依赖

```bash
pip3 install requests beautifulsoup4 pillow
```

### 步骤5：配置Moltbot

```bash
# 复制配置模板
cp ~/moltbot/.env.example ~/.clawdbot/config.json

# 编辑配置
vim ~/.clawdbot/config.json
```

**配置项：**
- 飞书API配置
- 用户ID
- 技能目录路径：`/home/lejurobot/clawd/skills`
- HomeKit配置

### 步骤6：配置自动推送（可选）

**Git钩子（每次commit自动push）：**
```bash
chmod +x .git/hooks/post-commit
```

**文件监听器（自动提交并推送）：**
```bash
python3 tools/file-watcher.py /home/lejurobot/clawd 30
```

### 步骤7：启动Moltbot

```bash
cd ~/moltbot
node moltbot.mjs gateway start
```

---

## 配置Cloudflared（HomeKit使用）

### 创建隧道

```bash
# 登录Cloudflare
cloudflared tunnel login

# 创建隧道
cloudflared tunnel create bruce-homekit

# 创建配置目录
mkdir -p ~/.cloudflared

# 创建配置文件
vim ~/.cloudflared/config.yml
```

### 配置文件示例

```yaml
tunnel: <tunnel-id>
credentials-file: /home/lejurobot/.cloudflared/<tunnel-id>.json

ingress:
  - hostname: bruce.yourdomain.com
    service: http://localhost:18790
  - service: http_status:404
```

### 启动隧道

```bash
cloudflared tunnel run bruce-homekit
```

### 设置为系统服务

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

### 配置HomeKit

编辑 `services/homekit-bruce/index.js`，配置：
- PIN码（默认：123-45-678）
- 配件名称（默认：Bruce AI Assistant）
- 端口（默认：18790）

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
# 查看状态
moltbot status

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

### 测试自动推送

```bash
# 创建测试文件
echo "test" >> test.txt

# 等待30-60秒
# 检查GitHub，应该有新提交
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
│   ├── install-moltbot.sh    # Moltbot安装
│   ├── install-cloudflared.sh # Cloudflared安装
│   ├── install.sh           # 一键安装
│   ├── git-push.sh          # Git推送
│   └── file-watcher.py      # 文件监听器
├── services/                # 服务配置
│   └── homekit-bruce/       # HomeKit服务
├── vendor/                  # 第三方软件
│   └── moltbot/             # Moltbot说明
├── memory/                  # 记忆文件
├── evolution-log.md         # 进化日志
├── evolution-tasks.md       # 进化任务
├── README.md                # 主文档
├── DEPLOYMENT.md            # 本文档
└── .git/hooks/post-commit  # Git钩子

# 外部目录
~/moltbot/                   # Moltbot安装位置
~/.clawdbot/                # Moltbot配置
~/.cloudflared/             # Cloudflared配置
```

---

## 故障排查

### 问题：Moltbot无法启动

```bash
# 检查日志
journalctl -u moltbot -f

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

### 问题：自动推送不工作

```bash
# 检查Git钩子
ls -la .git/hooks/post-commit

# 检查文件监听器
ps aux | grep file-watcher

# 手动测试
./tools/git-push.sh "测试推送"
```

---

## 管理命令

### Moltbot管理

```bash
# 启动
moltbot gateway start

# 停止
moltbot gateway stop

# 重启
moltbot gateway restart

# 状态
moltbot status

# Cron任务
moltbot cron list
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

## 更新升级

### 更新Bruce

```bash
git pull origin master
```

### 更新Moltbot

```bash
cd ~/moltbot
git pull origin main
pnpm install
moltbot gateway restart
```

### 更新Cloudflared

```bash
./tools/install-cloudflared.sh
```

---

## 相关文档

- [README.md](README.md) - 主文档
- [Moltbot文档](https://docs.molt.bot)
- [Cloudflared文档](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)

---

## 支持

**仓库：** https://github.com/Oswald-Hao/Bruce.git  
**问题反馈：** 提交Issue到GitHub

---

**最后更新：** 2026-02-02
