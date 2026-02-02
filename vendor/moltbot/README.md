# Moltbot - Bruce的核心框架

## 说明

Moltbot源代码已包含在此目录中（vendor/moltbot/），不需要联网下载安装。

## 快速开始

```bash
# 1. 进入Moltbot目录
cd vendor/moltbot

# 2. 安装依赖（只执行一次）
pnpm install

# 3. 启动Moltbot
node moltbot.mjs gateway start
```

## Moltbot信息

**官网：** https://github.com/moltbot/moltbot  
**文档：** https://docs.molt.bot

## 为什么包含在仓库里？

**优点：**
- ✅ 换电脑后clone仓库即可直接使用
- ✅ 不需要联网下载Moltbot源代码
- ✅ 保证版本一致
- ✅ 完全离线可用

**缺点：**
- ⚠️ 仓库体积增大（约49MB，已排除node_modules）
- ⚠️ 更新Moltbot需要手动合并

## 配置文件

Moltbot配置文件不在仓库中（保护敏感信息），需要手动创建：

```bash
# 复制配置模板到home目录
cp ../../MOLTBOT_CONFIG.example ~/.clawdbot/config.json

# 编辑配置
vim ~/.clawdbot/config.json
```

## 目录说明

**源代码：** `vendor/moltbot/`（在仓库中）  
**配置文件：** `~/.clawdbot/`（不在仓库中）  
**定时任务：** `~/.clawdbot/cron/jobs.json`

## 快速命令

```bash
# 进入Moltbot目录
cd vendor/moltbot

# 启动Moltbot
node moltbot.mjs gateway start

# 查看状态
node moltbot.mjs status

# 重启
node moltbot.mjs gateway restart

# 停止
node moltbot.mjs gateway stop
```

## 更新Moltbot

```bash
# 进入Moltbot目录
cd vendor/moltbot

# 拉取最新代码
git pull origin main

# 重新安装依赖
pnpm install

# 重启Moltbot
node moltbot.mjs gateway restart
```

## 排除的文件

以下文件已通过.gitignore排除，不会提交到仓库：
- `node_modules/` - npm依赖包（太大）
- `dist/` - 构建输出
- `.git/` - Git历史
- `*.log` - 日志文件
- `*.moltbot` - Moltbot日志
