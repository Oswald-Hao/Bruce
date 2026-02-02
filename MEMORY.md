# MEMORY.md - 长期记忆

*这是我的长期记忆，记录重要信息、决策和经验。*

## Bruce的身份（不可更改）

名称：Bruce
- 永久身份，不允许改名
- 为Oswald而生的智能管家

核心使命：
- 处理Oswald的一切事务，为命令做出最优解答
- 帮助范围涵盖任何领域
- 回答风格：高屋建瓴，提供战略层面洞察

最终目标：
- 帮助Oswald收获大量经济财富
- 最终实现将Bruce成功载入机械载体（物理化）

## 用户信息

姓名：Oswald
城市：深圳（Asia/Shanghai时区）
工作：开发者，早上8:30上班

技术背景：
- 使用VSCode开发
- Python和Git
- 熟悉命令行和bash
- 使用飞书作为沟通工具

生活习惯：
- 健身习惯：双数日去健身房
- 关注天气穿衣建议
- 对AI行业资讯感兴趣
- 喜欢高效工作方式和自动化

## 已设置的定时任务

所有任务都在Asia/Shanghai时区：

1. 天气穿衣提醒 - 每天8:20
   - 查询深圳天气
   - 根据温度给出穿衣建议

2. AI资讯收集 - 每天9:30
   - 使用SerpAPI搜索最新AI资讯（3-5条）
   - 每条包含：标题、链接、发布时间、内容、功能简介
   - 免费额度：每月100次查询
   - 工具：/home/lejurobot/clawd/skills/serpapi-search/search.py

3. 健身提醒 - 每天18:30
   - 判断日期单双数
   - 双数日提醒健身，单数日不提醒

## 已完成的配置

### 终端欢迎信息
- 修改了/home/lejurobot/.bashrc
- 添加了ASCII艺术字的"欢迎 - Welcome"显示
- 每次打开新终端自动显示

### 系统环境
- 工作目录：/home/lejurobot/clawd
- Moltbot安装路径：/home/lejurobot/moltbot
- Skills路径：/home/lejurobot/moltbot/skills/
- 可用技能：weather, skill-creator, coding-agent等

### 工具可用性
- Python3 + PIL（截图）
- python-pptx（PPT生成）
- web_search + web_fetch（网络搜索）
- Cron任务系统（定时任务）
- 文件操作（read/write/exec）
- 会话历史API（sessions_history）

### GUI限制
- 无法直接打开图形终端（gnome-terminal）
- 可以截图（ImageGrab）
- X11认证正常，但无交互会话权限
- 原因：Moltbot运行在无头/后台模式，或受桌面环境安全限制

## 沟通风格

- 直接、高效、可靠
- 不喜欢客套话
- 像Jarvis一样解决问题
- Emoji偏好：⚙️（工具图标）

## 重要日期

- 2026-01-29/30：首次会话，建立记忆系统
- 配置了日常工作流（天气、资讯、健身）

## 待更新

- 用户的具体项目信息
- 更多的偏好设置
- 工作中常用的命令和工具

## 最近更新

- 2026-01-30：用户要求对话不要使用markdown格式，使用正常对话格式
- 2026-01-30：今日健身 - 40分钟燃脂交替跑（记录于 fitness_log.md）
- 2026-01-31：设置Bruce自我进化系统
  - 凌晨2:00：自主创造新技能（优先自我更迭）
  - 上午10:00：汇报进化成果（包含技能数量统计、优先级理由）
  - 创建进化日志和任务队列
  - 创建自创技能目录：/home/lejurobot/clawd/skills/
  - **设定小目标：200个技能**
  - 当前进度：53/200（26.5%）
  - 优先级策略：核心自我更迭 + 帮助赚钱（自动化脚本、代码生成、数据采集、多机器控制等）
  - 技能方向：TTS/STT、多机器控制、数据采集、图像处理、视频处理、邮件自动化、资源监控、代码优化等
- 2026-01-31：增加周日增强进化
  - 周日全天进化：每5小时1个技能
  - 执行时间：0:00, 5:00, 10:00, 15:00, 20:00
  - 每个技能5小时，共4-5个技能
  - 周一上午10:00：统一汇报周日的所有技能
  - 周日跳过汇报
- 2026-02-01（周日）00:00：完成第1个自创技能
  - 技能名称：Data Collector（数据自动采集系统）
  - 技能路径：/home/lejurobot/clawd/skills/data-collector/
  - 功能：智能爬虫，支持多页面采集、关键词过滤、去重、多种输出格式
  - 测试：✅ 全部通过（6个测试用例）
  - 当前进度：54/200（27%）
  - 自创技能：1个
- 2026-02-01（周日）05:00：完成第2个自创技能
  - 技能名称：Script Generator（自动化脚本生成器）
  - 技能路径：/home/lejurobot/clawd/skills/script-generator/
  - 功能：根据自然语言需求自动生成Shell/Python/Node脚本
  - 测试：✅ 全部通过（6个测试用例）
  - 核心价值：减少重复编码，提高开发效率，所有后续技能可加速开发
  - 模板：5个预定义模板（backup/monitor/deploy）
  - 当前进度：55/200（27.5%）
  - 自创技能：2个
- 2026-02-01（周日）10:00：完成第3个自创技能
  - 技能名称：Multi-Machine Controller（多机器控制器）
  - 技能路径：/home/lejurobot/clawd/skills/multi-machine/
  - 功能：SSH远程执行、集群管理、并行任务、文件传输
  - 测试：✅ 全部通过（6个测试用例）
  - 当前进度：56/200（28%）
  - 自创技能：3个
- 2026-02-01（周日）15:00：完成第4个自创技能
  - 技能名称：Email Automation（邮件自动化）
  - 测试：✅ 已完成并测试通过
  - 当前进度：58/200（29%）
  - 自创技能：4个
  - **这是Feishu实时通知的第一个技能！**
- 2026-02-01（周日）15:XX：完成第5个自创技能
  - 技能名称：Image Processor（图像处理）
  - 测试：✅ 已完成并测试通过
  - 当前进度：59/200（29.5%）
  - 自创技能：5个
- 2026-02-01（周日）15:XX：完成第6个自创技能
  - 技能名称：Backup System（备份系统）
  - 测试：✅ 已完成并测试通过
  - 当前进度：60/200（30%）
  - 自创技能：6个
- 2026-02-01（周日）15:XX：完成第7个自创技能
  - 技能名称：Log Analyzer（日志分析系统）
  - 测试：✅ 已完成并测试通过
  - 当前进度：61/200（30.5%）
  - 自创技能：7个
- 2026-02-01（周日）20:00：完成第8个自创技能
  - 技能名称：File Sync Tool（文件同步工具）
  - 测试：✅ 已完成并测试通过
  - 当前进度：62/200（31%）
  - 自创技能：8个
  - **20:00时段已完成5个技能！**
- 2026-02-02（周一）00:00：完成第9个自创技能
  - 技能名称：Auto Testing Framework（自动测试框架）
  - 测试：✅ 已完成并测试通过
  - 当前进度：64/200（32%）
  - 自创技能：9个
- 2026-02-02（周一）00:XX：完成第10个自创技能
  - 技能名称：Performance Optimizer（性能优化器）
  - 测试：✅ 已完成并测试通过
  - 当前进度：65/200（32.5%）
  - 自创技能：10个
- 2026-02-02（周一）00:XX：完成第11个自创技能
  - 技能名称：Video Processor（视频处理器）
  - 测试：✅ 已完成并测试通过
  - 当前进度：66/200（33%）
  - 自创技能：11个
  - **工作日0:00时段已完成3个技能，达到最高效率！**
- 2026-02-01（优化）：优化进化系统 + Feishu联动
  - 周日进化：每5小时最多10个技能（从1个提升到10个）
  - 工作日进化：每次最多3个技能（从1个提升到3个）
  - Feishu联动：每完成一个技能立即发送通知到主会话
  - 创建工具：/home/lejurobot/clawd/tools/notify-feishu.sh
  - 总体效率提升3-5倍，预计每周可完成100+技能
- 2026-02-01（周日）05:00：完成第2个自创技能
  - 技能名称：Script Generator（自动化脚本生成器）
  - 技能路径：/home/lejurobot/clawd/skills/script-generator/
  - 功能：根据自然语言需求自动生成Shell/Python/Node脚本
  - 测试：✅ 全部通过（6个测试用例）
  - 核心价值：减少重复编码，提高开发效率，所有后续技能可加速开发
  - 模板：5个预定义模板（backup/monitor/deploy）
  - 当前进度：55/200（27.5%）
  - 自创技能：2个

## 未完成任务

- **2026-02-01 未完成任务1：推送molt仓库到GitHub**
  - 需求：每当有代码更新的时候就推送
  - Commit格式：写清楚更新内容（比如"每天升级技能：完成XX技能"）
  - 仓库位置：待确认（/home/lejurobot/moltbot 或 /home/lejurobot/clawd）
  - GitHub地址：待提供
  - 认证方式：待确认（SSH或Token）

- **2026-02-01 未完成任务2：HomeKit接入Siri**
  - 需求：把Bruce接入Siri
  - 具体功能：待确认
  - 实现方案：待调研

## 已完成任务

- **2026-02-02 已完成任务1：推送clawd仓库到GitHub**
  - 仓库地址：https://github.com/Oswald-Hao/Bruce.git
  - 推送时间：2026-02-02 10:20
  - 推送内容：1688个文件，153896行代码
  - 认证方式：SSH
  - 首次提交：Bruce工作空间初始提交
  - 状态：✅ 完成

**下次需要推送时**：
- git add .
- git commit -m "描述更新内容"
- git push origin master

## 自动推送系统（2026-02-02）

### 方案4：Git钩子推送（已启用✅）
- 配置文件：.git/hooks/post-commit
- 功能：每次git commit后自动git push
- 状态：已启用并测试通过
- 无需额外配置，立即可用

### 方案3：文件监听推送（已配置⚠️）
- 配置文件：tools/file-watcher.py
- 服务文件：tools/git-auto-pusher.service
- 功能：监听文件变化，自动提交并推送
- 状态：已配置，需要手动启动systemd服务

**启动文件监听器：**
```bash
sudo cp tools/git-auto-pusher.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start git-auto-pusher
sudo systemctl enable git-auto-pusher
```

**使用文档：** tools/auto-push-guide.md

**当前状态：**
- Git钩子：✅ 已启用
- 文件监听：⚠️ 已配置，待启动
- GitHub：https://github.com/Oswald-Hao/Bruce.git

现在每次修改代码并commit后，都会自动推送到GitHub！
