# Feishu Streaming - 流式输出技能

为 Feishu 通道添加流式输出功能，在处理消息时显示"正在思考"卡片。

## 功能

- 消息接收时自动发送"正在思考"卡片
- 处理完成后更新为实际回复
- 提供更好的交互体验

## 安装

复制到 Moltbot skills 目录：
```bash
cp -r /home/lejurobot/clawd/skills/feishu-streaming /home/lejurobot/moltbot/skills/
```

## 配置

在 Moltbot 配置文件中启用：
```json
{
  "channels": {
    "feishu": {
      "appId": "cli_xxxxxxxxxxxxxxxx",
      "appSecret": "your_app_secret",
      "streaming": {
        "enabled": true,
        "thinkingMessage": "🤔 正在思考中..."
      }
    }
  }
}
```

## 使用

启用后，所有 Feishu 消息都会自动使用流式输出。

## 测试

```bash
python3 /home/lejurobot/clawd/tools/feishu-streaming.py ou_xxxxxxxxxxxxxxxx
```

## 注意事项

- 需要安装 `requests` 库：`pip install requests`
- Feishu 消息更新 API 限制：消息发送后 24 小时内可更新
