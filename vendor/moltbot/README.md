# Moltbot - Bruce的核心框架

## 说明

这个目录用于存放Moltbot的本地副本。

**推荐使用一键安装：**
```bash
cd /home/lejurobot/clawd
./tools/install-moltbot.sh
```

或者直接克隆到home目录：
```bash
git clone https://github.com/moltbot/moltbot.git ~/moltbot
```

## Moltbot信息

**官网：** https://github.com/moltbot/moltbot  
**文档：** https://docs.molt.bot

## 安装位置

**推荐位置：** `~/moltbot`

**为什么放在home目录：**
- 避免版本冲突
- 独立更新和维护
- 配置文件在 `~/.clawdbot/`

## 相关文件

- `tools/install-moltbot.sh` - Moltbot安装脚本
- `~/.clawdbot/config.json` - Moltbot配置文件
- `~/.clawdbot/cron/jobs.json` - 定时任务配置

## 快速命令

```bash
# 启动Moltbot
moltbot gateway start

# 查看状态
moltbot status

# 重启
moltbot gateway restart

# 停止
moltbot gateway stop
```
