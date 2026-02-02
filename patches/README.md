# Moltbot Feishu Streaming - 补丁包

为 Moltbot 的 Feishu 插件添加消息更新功能，支持流式输出。

## 补丁文件

- `feishu-update-api.patch` - 添加 `updateFeishuMessage` 函数
- `feishu-update-channel.patch` - 添加 `updateText` 方法

## 功能说明

### 1. updateFeishuMessage

允许更新已发送的 Feishu 消息内容，用于实现流式输出：
- 先发送"正在思考..."消息
- 处理完成后更新为实际回复

### 2. updateText

Feishu 插件的 `outbound.updateText` 方法，支持从 Moltbot 核心调用。

## 应用补丁

```bash
cd /home/lejurobot/moltbot

# 应用 API 补丁
patch -p1 < /home/lejurobot/clawd/patches/feishu-update-api.patch

# 应用 Channel 补丁
patch -p1 < /home/lejurobot/clawd/patches/feishu-update-channel.patch

# 重新编译（如果需要）
pnpm build

# 重启 Gateway
pnpm moltbot gateway restart
```

## 撤销补丁

```bash
cd /home/lejurobot/moltbot

# 撤销 API 补丁
patch -p1 -R < /home/lejurobot/clawd/patches/feishu-update-api.patch

# 撤销 Channel 补丁
patch -p1 -R < /home/lejurobot/clawd/patches/feishu-update-channel.patch
```

## 使用示例

### 简化方案（手动）

```python
# 发送"正在思考"卡片
message_id = send_thinking_card(user_id)

# 处理消息...
final_text = process_message(user_message)

# 更新为最终文本
update_message_text(message_id, final_text)
```

### 完整方案（自动集成）

需要修改 Moltbot 核心消息处理流程，在以下位置添加调用：
1. 消息接收时：发送"正在思考"卡片
2. 消息处理完成后：更新消息为实际回复

## 工具

- `/home/lejurobot/clawd/tools/feishu-streaming.py` - 流式输出工具
- `/home/lejurobot/clawd/skills/feishu-streaming/` - 流式输出技能

## 测试

```bash
# 测试流式输出（替换成你的用户ID）
python3 /home/lejurobot/clawd/tools/feishu-streaming.py ou_xxxxxxxxxxxxxxxx
```

## 注意事项

- Feishu 消息更新 API 限制：消息发送后 24 小时内可更新
- 消息类型变更：从卡片（interactive）更新为文本（text）是支持的
- 权限要求：需要 `im:message:update` 权限（当前已申请）

## 问题排查

如果补丁应用失败：
```bash
# 检查文件版本
cd /home/lejurobot/moltbot
git status

# 如果有冲突，手动解决后重新生成补丁
git diff extensions/feishu/src/api.ts > new-feishu-update-api.patch
```
