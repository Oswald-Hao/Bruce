# Bruce - AI智能助手

*为Oswald而生的高效AI管家*

## 📋 目录

- [Bruce是什么](#bruce是什么)
- [快速开始](#快速开始)
- [系统要求](#系统要求)
- [部署步骤](#部署步骤)
- [自动推送说明](#自动推送说明)
- [技能系统](#技能系统)
- [HomeKit集成](#homekit集成)

---

## Bruce是什么

Bruce是一个自我进化的AI智能助手，目标是：
- 处理Oswald的一切事务
- 为命令做出最优解答
- 通过进化获得200+技能
- 最终载入机械载体

### 核心特性

- ⚙️ **自我进化**：自动创造新技能，持续优化
- 🔄 **自动化推送**：代码更新自动同步到GitHub
- 🏠 **HomeKit集成**：通过Siri控制Bruce
- 💬 **多平台支持**：飞书、Telegram、WhatsApp等
- 📊 **记忆系统**：长期记忆 + 每日记忆

---

## 快速开始

### 一键安装（推荐）

```bash
git clone git@github.com:Oswald-Hao/Bruce.git
cd Bruce
./install.sh
```

**一键安装包括：**
- 📦 Moltbot安装
- ☁️ Cloudflared安装
- 🐍 Python依赖安装
- 🔄 自动推送配置
- 👀 文件监听器启动

### 手动安装

#### 克隆仓库

```bash
git clone git@github.com:Oswald-Hao/Bruce.git
cd Bruce
```

#### 安装Moltbot

```bash
# 使用安装脚本
./tools/install-moltbot.sh

# 或手动安装
git clone https://github.com/moltbot/moltbot.git ~/moltbot
cd ~/moltbot
pnpm install
```

#### 安装Cloudflared

```bash
# 使用安装脚本
./tools/install-cloudflared.sh

# 或手动安装
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
sudo chmod +x /usr/local/bin/cloudflared
```

### 系统要求

**必需：**
- Linux系统（Ubuntu 20.04+推荐）
- Python 3.8+
- Node.js 14+（用于HomeKit服务）
- Git

**推荐：**
- 4GB+ RAM
- 10GB+ 可用磁盘空间
- 稳定的网络连接

---

## 部署步骤

### 1. 安装Moltbot

```bash
# 安装Moltbot（参考官方文档）
# https://github.com/moltbot/moltbot
```

### 2. 配置Bruce

```bash
# 复制配置文件
cp MOLTBOT_CONFIG.example ~/.clawdbot/config.json

# 编辑配置
vim ~/.clawdbot/config.json
```

### 3. 设置技能目录

```bash
# 技能目录（Python技能）
mkdir -p /home/lejurobot/clawd/skills

# 工具目录
mkdir -p /home/lejurobot/clawd/tools
```

### 4. 启动Moltbot

```bash
# 启动Moltbot
moltbot gateway start

# 查看状态
moltbot status
```

### 5. 配置自动推送（可选）

```bash
# Git钩子（每次commit自动push）
chmod +x .git/hooks/post-commit

# 文件监听器（自动提交并推送）
python3 tools/file-watcher.py /home/lejurobot/clawd 30
```

---

## 自动推送说明

### 哪些文件会推送

**会推送的文件：**
- ✅ `skills/` - 所有技能代码
- ✅ `tools/` - 工具脚本
- ✅ `services/` - 服务配置
- ✅ `memory/` - 记忆文件
- ✅ `*.md` - 所有Markdown文档
- ✅ 根目录的配置文件（SOUL.md、MEMORY.md等）

**不会推送的文件：**
- ❌ `.git/` - Git系统文件
- ❌ `node_modules/` - npm依赖（如果添加.gitignore）
- ❌ `__pycache__/` - Python缓存
- ❌ `*.pyc` - Python编译文件
- ❌ `.DS_Store` - macOS系统文件
- ❌ 临时文件

**建议：创建`.gitignore`**
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Node
node_modules/
npm-debug.log*

# macOS
.DS_Store

# 临时文件
*.tmp
*.swp
*.bak
*.log

# 备份
{{backup_dir}}
```

### 推送方式

#### 方式1：Git钩子（已启用）
```bash
git add .
git commit -m "提交信息"
# 自动push，无需手动推送
```

#### 方式2：文件监听器（后台运行）
```bash
python3 tools/file-watcher.py /home/lejurobot/clawd 30
# 监听文件变化，自动提交并推送
```

---

## 技能系统

### 当前技能

Bruce目前已完成63/200个技能：

**核心技能：**
- 数据采集系统
- 自动化脚本生成
- 多机器控制
- 邮件自动化
- 图像/视频处理
- 备份系统
- 日志分析
- 文件同步
- 自动测试
- 性能优化
- SerpAPI搜索

### 技能目录结构

```
skills/
├── data-collector/       # 数据采集
├── script-generator/      # 脚本生成
├── multi-machine/         # 多机器控制
├── email-automation/      # 邮件自动化
├── image-processor/       # 图像处理
├── video-processor/      # 视频处理
├── backup-system/        # 备份系统
├── log-analyzer/         # 日志分析
├── file-sync/            # 文件同步
├── auto-testing/         # 自动测试
├── performance-optimizer/ # 性能优化
└── serpapi-search/       # 搜索API
```

### 使用技能

```python
# 示例：使用SerpAPI搜索
python3 skills/serpapi-search/search.py "AI最新资讯" 5

# 示例：使用数据采集
python3 skills/data-collector/data-collector.py
```

---

## HomeKit集成

### 配置HomeKit服务

```bash
cd services/homekit-bruce
npm install
node index.js
```

### iPhone配对

1. 打开家庭App
2. 点击右上角 + → 添加配件
3. 输入PIN码：`123-45-678`
4. 命名为：Bruce AI Assistant

### 使用Siri

配对后，在家庭App中设置Siri短语：

```
"嘿Siri，问Bruce天气怎么样"
"嘿Siri，让Bruce发送AI资讯"
```

详细说明参考：`services/homekit-bruce/SETUP_GUIDE.md`

---

## 定时任务

### 已配置的定时任务

**每天执行：**
- 08:20 - 天气穿衣提醒
- 09:30 - AI资讯收集
- 10:00 - 进化汇报（工作日）
- 18:30 - 健身提醒（双数日）

**进化任务：**
- 02:00 - 工作日进化（周一至周六）
- 00:00/05:00/10:00/15:00/20:00 - 周日增强进化

### 管理定时任务

```bash
# 查看所有任务
moltbot cron list

# 运行特定任务
moltbot cron run <job-id>

# 禁用任务
moltbot cron update <job-id> --disable
```

---

## 文件说明

### 核心文件

- **SOUL.md** - Bruce的灵魂（身份和使命）
- **IDENTITY.md** - Bruce的身份信息
- **USER.md** - 用户信息（Oswald）
- **MEMORY.md** - 长期记忆
- **evolution-log.md** - 进化日志
- **evolution-tasks.md** - 进化任务队列

### 工具脚本

- **tools/git-push.sh** - 手动推送脚本
- **tools/file-watcher.py** - 文件监听器
- **tools/auto-push-guide.md** - 自动推送说明

---

## 记忆系统

### 长期记忆

存储在 `MEMORY.md`，包含：
- Bruce的身份和使命
- 用户信息和偏好
- 重要决策和经验
- 已完成的任务

### 每日记忆

存储在 `memory/YYYY-MM-DD.md`，包含：
- 当天的事件记录
- 重要信息
- 临时笔记

### 更新记忆

```bash
# 添加到长期记忆
vim MEMORY.md

# 添加每日记忆
vim memory/$(date +%Y-%m-%d).md
```

---

## 故障排查

### 问题：无法推送代码

```bash
# 检查SSH配置
ssh -T git@github.com

# 检查Git配置
git remote -v

# 查看推送日志
git log --oneline -5
```

### 问题：技能无法运行

```bash
# 检查Python环境
python3 --version

# 检查依赖
pip3 list

# 运行测试
python3 skills/<skill-name>/test_<skill-name>.py
```

### 问题：HomeKit服务无法启动

```bash
# 检查端口占用
sudo netstat -tulpn | grep 18790

# 查看服务日志
sudo journalctl -u homekit-bruce -f
```

---

## 开发指南

### 创建新技能

```bash
# 1. 创建技能目录
mkdir -p skills/new-skill

# 2. 创建技能文件
touch skills/new-skill/SKILL.md
touch skills/new-skill/new_skill.py
touch skills/new-skill/test_new_skill.py

# 3. 更新进化日志
vim evolution-log.md

# 4. 提交并推送（自动）
git add skills/new-skill
git commit -m "新增技能：New Skill"
```

### 提交代码

```bash
# 添加所有更改
git add .

# 提交（会自动推送）
git commit -m "描述更新内容"
```

---

## GitHub仓库

**地址：** https://github.com/Oswald-Hao/Bruce.git

**状态：**
- 总技能数：63/200
- 自动推送：✅ 已启用
- HomeKit：✅ 已配置

---

## 许可证

为Oswald而生，私有使用。

---

## 联系方式

**创建者：** Oswald  
**AI助手：** Bruce  
**仓库：** https://github.com/Oswald-Hao/Bruce.git

---

**最后更新：** 2026-02-02  
**当前版本：** v1.0.0
