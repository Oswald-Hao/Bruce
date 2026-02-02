# 自动化推送说明

## 推送方式

### 1. 手动推送
```bash
./tools/git-push.sh "提交信息"
```

### 2. 自动推送（推荐）

#### 每天自动推送
创建cron任务，每天凌晨2:00自动推送：
```bash
0 2 * * * /home/lejurobot/clawd/tools/git-push.sh "每日自动更新：$(date +\%Y-\%m-\%d)"
```

#### 每次进化后推送
在进化系统中，每完成一个技能后自动推送：
```bash
/home/lejurobot/clawd/tools/git-push.sh "新增技能：[技能名称] - [进度X/200]"
```

## 已配置

- ✅ GitHub仓库：https://github.com/Oswald-Hao/Bruce.git
- ✅ SSH认证：已配置
- ✅ 自动推送脚本：tools/git-push.sh
- ✅ 首次推送：2026-02-02 10:20

## 当前状态

- 首次提交：Bruce工作空间初始提交（1688个文件，153896行代码）
- 第二次提交：添加自动化推送脚本（2个文件，43行代码）
- 总提交数：2
- 分支：master

## 推送建议

每次完成技能进化后，使用以下格式推送：
```bash
./tools/git-push.sh "完成[技能名称] - [进度X/200]"
```

例如：
```bash
./tools/git-push.sh "完成Data Collector - 54/200"
```

这样可以清晰地追踪每次更新的内容。
