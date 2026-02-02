# Bruce集成总结

## 已完成的集成

### ✅ Moltbot集成

**安装脚本：**
- `tools/install-moltbot.sh` - Moltbot自动安装脚本

**功能：**
- 自动克隆Moltbot到 `~/moltbot`
- 安装npm/pnpm依赖
- 创建配置目录 `~/.clawdbot/`
- 复制配置模板 `config.json`
- （可选）创建全局命令 `moltbot`

**文档：**
- `vendor/moltbot/README.md` - Moltbot说明文档
- `DEPLOYMENT.md` - 完整部署指南
- `README.md` - 主文档（已更新Moltbot章节）

---

### ✅ Cloudflared集成

**安装脚本：**
- `tools/install-cloudflared.sh` - Cloudflared自动安装脚本

**功能：**
- 自动检测系统架构（x86_64、arm64、armv7l）
- 下载对应架构的Cloudflared二进制文件
- 安装到 `/usr/local/bin/cloudflared`
- 验证安装

**支持架构：**
- x86_64（Intel/AMD 64位）
- arm64（ARM 64位）
- armv7l（ARM 32位）

**文档：**
- `DEPLOYMENT.md` - Cloudflared使用和配置指南
- `README.md` - 主文档（已更新Cloudflared章节）

---

### ✅ 一键安装

**一键安装脚本：**
- `install.sh` - 一键安装所有依赖

**功能：**
- 检查系统要求（Node.js、Git）
- 安装Moltbot
- 安装Cloudflared
- 安装Python依赖
- 配置Git钩子
- 启动文件监听器

**使用方法：**
```bash
git clone git@github.com:Oswald-Hao/Bruce.git
cd Bruce
./install.sh
```

---

## 目录结构

```
Bruce/
├── tools/                           # 工具脚本
│   ├── install-moltbot.sh            # Moltbot安装
│   ├── install-cloudflared.sh        # Cloudflared安装
│   ├── install.sh                    # 一键安装
│   ├── git-push.sh                   # Git推送
│   ├── file-watcher.py               # 文件监听器
│   ├── auto-push-guide.md            # 自动推送说明
│   └── auto-push.md                 # 自动推送说明
├── vendor/                          # 第三方软件
│   └── moltbot/                     # Moltbot说明
│       └── README.md
├── services/                        # 服务配置
│   └── homekit-bruce/               # HomeKit服务
├── skills/                          # 技能目录
├── memory/                          # 记忆文件
├── evolution-log.md                  # 进化日志
├── evolution-tasks.md                # 进化任务
├── README.md                        # 主文档
├── DEPLOYMENT.md                    # 部署指南
└── .git/hooks/post-commit            # Git钩子

# 外部目录
~/moltbot/                           # Moltbot安装位置
~/.clawdbot/                        # Moltbot配置
~/.cloudflared/                     # Cloudflared配置
```

---

## 安装方式对比

### 方式1：一键安装（推荐）

**优点：**
- ✅ 最简单，一条命令完成所有安装
- ✅ 自动检查系统要求
- ✅ 自动配置自动推送
- ✅ 适合新手和快速部署

**缺点：**
- ⚠️ 需要sudo权限（用于安装到系统目录）
- ⚠️ 无法自定义安装位置

**命令：**
```bash
git clone git@github.com:Oswald-Hao/Bruce.git
cd Bruce
./install.sh
```

---

### 方式2：手动安装

**优点：**
- ✅ 完全可控
- ✅ 可以自定义安装位置
- ✅ 适合高级用户

**缺点：**
- ❌ 需要多步操作
- ❌ 需要手动配置

**命令：**
```bash
# 安装Moltbot
./tools/install-moltbot.sh

# 安装Cloudflared
./tools/install-cloudflared.sh

# 手动配置
vim ~/.clawdbot/config.json

# 启动服务
moltbot gateway start
```

---

## 集成说明

### Moltbot

**安装位置：** `~/moltbot`

**为什么放在home目录：**
- 避免版本冲突
- 独立更新和维护
- 配置文件在 `~/.clawdbot/`

**配置文件：**
- `~/.clawdbot/config.json` - 主配置
- `~/.clawdbot/cron/jobs.json` - 定时任务

---

### Cloudflared

**安装位置：** `/usr/local/bin/cloudflared`

**为什么安装到系统目录：**
- 全局可用，任何目录都可调用
- 方便设置系统服务
- 符合Linux软件安装惯例

**配置文件：**
- `~/.cloudflared/config.yml` - 隧道配置
- `~/.cloudflared/<tunnel-id>.json` - 隧道凭证

---

## 使用说明

### 快速开始

```bash
# 1. 克隆仓库
git clone git@github.com:Oswald-Hao/Bruce.git
cd Bruce

# 2. 一键安装
./install.sh

# 3. 配置Moltbot
vim ~/.clawdbot/config.json

# 4. 启动Moltbot
moltbot gateway start
```

### Moltbot命令

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

### Cloudflared命令

```bash
# 查看版本
cloudflared --version

# 登录
cloudflared tunnel login

# 创建隧道
cloudflared tunnel create <name>

# 运行隧道
cloudflared tunnel run <name>

# 服务管理
sudo systemctl status cloudflared
sudo systemctl restart cloudflared
```

---

## 自动推送

### 已启用

**Git钩子：**
- 每次commit自动push
- 无需手动操作

**文件监听器：**
- 自动检测文件变化
- 30-60秒后自动提交并推送

### 推送内容

**会推送：**
- `skills/` - 所有技能
- `tools/` - 工具脚本
- `services/` - 服务配置
- `*.md` - 文档
- `vendor/` - 说明文件

**不会推送：**
- `~/moltbot/` - Moltbot代码（不在仓库中）
- `~/.clawdbot/` - Moltbot配置
- `~/.cloudflared/` - Cloudflared配置

---

## 验证安装

### 检查Moltbot

```bash
moltbot status
# 应该显示：Gateway: running, Sessions: X
```

### 检查Cloudflared

```bash
cloudflared --version
# 应该显示版本号
```

### 检查自动推送

```bash
echo "test" >> test.txt
# 等待30-60秒
# 检查GitHub，应该有新提交
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
- [DEPLOYMENT.md](DEPLOYMENT.md) - 完整部署指南
- [tools/auto-push-guide.md](tools/auto-push-guide.md) - 自动推送说明
- [vendor/moltbot/README.md](vendor/moltbot/README.md) - Moltbot说明

---

## GitHub仓库

**地址：** https://github.com/Oswald-Hao/Bruce.git

**分支：** master

**自动推送：** ✅ 已启用

---

**最后更新：** 2026-02-02
**当前版本：** v1.1.0
