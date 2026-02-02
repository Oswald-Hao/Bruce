# Bruce - AI智能助手

*为Oswald而生的高效AI管家*

---

## 📋 目录

- [Bruce是什么](#bruce是什么)
- [快速开始](#快速开始)
- [系统要求](#系统要求)
- [部署步骤](#部署步骤)
- [Moltbot集成](#moltbot集成)
- [自动推送说明](#自动推送说明)
- [技能系统](#技能系统)
- [HomeKit集成](#homekit集成)
- [定时任务](#定时任务)
- [记忆系统](#记忆系统)
- [换电脑后使用](#换电脑后使用)
- [故障排查](#故障排查)
- [相关文档](#相关文档)

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

### 克隆仓库

```bash
git clone git@github.com:Oswald-Hao/Bruce.git
cd Bruce
```

### 系统要求

**必需：**
- Linux系统（Ubuntu 20.04+推荐）
- Python 3.8+
- Node.js 14+
- Git

**推荐：**
- 4GB+ RAM
- 10GB+ 可用磁盘空间

---

## 部署步骤

### 1. 克隆仓库

```bash
git clone git@github.com:Oswald-Hao/Bruce.git
cd Bruce
```

### 2. 安装Moltbot

**Moltbot源代码已包含在vendor/moltbot/中，无需联网下载！**

```bash
cd vendor/moltbot
pnpm install
```

### 3. 配置Moltbot

```bash
# 复制配置模板到home目录
cp ../../MOLTBOT_CONFIG.example ~/.clawdbot/config.json

# 编辑配置
vim ~/.clawdbot/config.json
```

### 4. 启动Moltbot

```bash
cd vendor/moltbot
node moltbot.mjs gateway start
```

### 5. 配置自动推送（可选）

**Git钩子（每次commit自动push）：**
```bash
chmod +x .git/hooks/post-commit
```

**文件监听器（自动提交并推送）：**
```bash
python3 tools/file-watcher.py /home/lejurobot/clawd 30
```

---

## Moltbot集成

### Moltbot是什么

Moltbot是Bruce的核心框架，提供：
- 💬 多平台消息接入（飞书、Telegram、WhatsApp等）
- 🔧 技能系统（Skills）
- 📊 代理系统（Agents）
- ⏰ 定时任务（Cron）
- 🎨 Canvas渲染
- 🧠 记忆系统

### 为什么包含在仓库里？

**优点：**
- ✅ 换电脑后clone仓库即可直接使用
- ✅ 不需要联网下载Moltbot源代码
- ✅ 保证版本一致
- ✅ 完全离线可用

**说明：**
- ⚠️ vendor/moltbot/已包含完整源代码（49MB，已排除node_modules）
- ⚠️ 配置文件在~/.clawdbot/（不在仓库中，保护敏感信息）
- ⚠️ 需要运行`pnpm install`安装依赖

### 快速命令

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

---

## 自动推送说明

### 会推送的文件

**会自动推送：**
- ✅ `skills/` - 所有技能代码
- ✅ `tools/` - 工具脚本
- ✅ `services/` - 服务配置
- ✅ `memory/` - 记忆文件
- ✅ `*.md` - 所有Markdown文档
- ✅ 根目录的配置文件（SOUL.md、MEMORY.md等）

**不会推送：**
- ❌ `vendor/moltbot/node_modules/` - npm依赖
- ❌ `__pycache__/` - Python缓存
- ❌ `*.pyc` - Python编译文件
- ❌ `~/.clawdbot/` - Moltbot配置（敏感信息）
- ❌ `~/.cloudflared/` - Cloudflared配置（敏感信息）
- ❌ 临时文件

### 推送方式

#### 方式1：Git钩子（已启用）

**工作方式：** 每次`git commit`后自动`git push`

**使用方法：**
```bash
git add .
git commit -m "提交信息"
# 自动push，无需手动推送
```

#### 方式2：文件监听器（后台运行）

**工作方式：** 监听文件变化，自动提交并推送

**使用方法：**
```bash
python3 tools/file-watcher.py /home/lejurobot/clawd 30
# 监听文件变化，自动提交并推送
```

**智能Commit信息：**
- ✅ 自动识别新增、修改、删除的文件
- ✅ 生成清晰的commit信息，例如：
  - "自动更新：新增：README.md"
  - "自动更新：修改：file-watcher.py"
  - "自动更新：新增3个文件，删除1个文件"

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
cd vendor/moltbot
node moltbot.mjs cron list

# 运行特定任务
cd vendor/moltbot
node moltbot.mjs cron run <job-id>

# 禁用任务
cd vendor/moltbot
node moltbot.mjs cron update <job-id> --disable
```

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

## 换电脑后使用

### 1. 克隆仓库

```bash
git clone git@github.com:Oswald-Hao/Bruce.git
cd Bruce
```

### 2. 安装Moltbot（完全离线）

```bash
cd vendor/moltbot
pnpm install
```

### 3. 配置Moltbot

```bash
cp ../../MOLTBOT_CONFIG.example ~/.clawdbot/config.json
vim ~/.clawdbot/config.json
```

### 4. 启动Moltbot

```bash
cd vendor/moltbot
node moltbot.mjs gateway start
```

### 5. 启动文件监听器（可选）

```bash
python3 tools/file-watcher.py /home/lejurobot/clawd 30
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

### 问题：文件监听器不工作

```bash
# 检查进程
ps aux | grep file-watcher

# 手动测试
python3 tools/file-watcher.py /home/lejurobot/clawd 30
```

---

## 相关文档

- [DEPLOYMENT.md](DEPLOYMENT.md) - 完整部署指南
- [COMPLETE.md](COMPLETE.md) - 集成完成总结
- [vendor/moltbot/README.md](vendor/moltbot/README.md) - Moltbot详细说明
- [services/homekit-bruce/SETUP_GUIDE.md](services/homekit-bruce/SETUP_GUIDE.md) - HomeKit配置指南
- [tools/auto-push-guide.md](tools/auto-push-guide.md) - 自动推送详细说明

---

## GitHub仓库

**地址：** https://github.com/Oswald-Hao/Bruce.git

**状态：**
- 总技能数：63/200
- Moltbot：✅ 已包含在vendor/moltbot/
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
**当前版本：** v1.1.0
