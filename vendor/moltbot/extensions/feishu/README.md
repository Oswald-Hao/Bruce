# Feishu/Lark Channel for Moltbot

飞书/Lark 机器人集成，支持通过 Webhook 接收消息和发送消息。

## 功能特性

- ✅ 私聊消息
- ✅ 群聊消息
- ✅ 富文本消息
- ✅ 媒体文件（图片、文件）
- ✅ 消息配对（Pairing）
- ✅ 允许列表/阻止列表
- ✅ Webhook 事件接收

## 配置步骤

### 1. 创建飞书应用

1. 访问 [飞书开放平台](https://open.feishu.cn/app)
2. 创建企业自建应用
3. 获取 `App ID` 和 `App Secret`

### 2. 配置权限

在应用权限管理中，申请以下权限：

- `im:message` - 接收消息
- `im:message:send_as_bot` - 机器人发送消息
- `im:chat` - 访问聊天信息

### 3. 配置事件订阅

1. 进入应用的事件订阅页面
2. 添加请求地址：`https://your-domain.com/feishu/default`
3. 订阅事件：`im.message.receive_v1`
4. （可选）配置加密密钥（Encrypt Key）

### 4. 在 Moltbot 中配置

运行配置向导：

```bash
pnpm moltbot channels login --channel feishu
```

或手动配置 `~/.clawdbot/moltbot.json`：

```json
{
  "channels": {
    "feishu": {
      "appId": "cli_xxxxxxxxxxxxxxxx",
      "appSecret": "your_app_secret_here",
      "webhookPath": "/feishu/default",
      "dm": {
        "policy": "pairing",
        "allowFrom": []
      },
      "groupPolicy": "allowlist",
      "allowList": ["oc_xxxxxxxxxxxxxxxx"]
    }
  }
}
```

## 使用方法

### 发送消息

```bash
# 发送给用户
pnpm moltbot message send --channel feishu --target "ou_xxxxxxxxxxxxxxxx" --message "Hello!"

# 发送给群组
pnpm moltbot message send --channel feishu --target "oc_xxxxxxxxxxxxxxxx" --message "Hello group!"
```

### 启动网关

```bash
pnpm moltbot gateway
```

## 目标格式

- **用户 ID（Open ID）**: `ou_xxxxxxxxxxxxxxxx`
- **群组 ID（Chat ID）**: `oc_xxxxxxxxxxxxxxxx`
- **带前缀**: `feishu:ou_xxxxxxxxxxxxxxxx` 或 `lark:ou_xxxxxxxxxxxxxxxx`

## API 参考

### 主要函数

- `sendFeishuMessage()` - 发送消息
- `uploadFeishuMedia()` - 上传媒体文件
- `getFeishuUserInfo()` - 获取用户信息
- `getFeishuChatInfo()` - 获取群组信息
- `startFeishuMonitor()` - 启动 Webhook 监控
- `stopFeishuMonitor()` - 停止 Webhook 监控

### 消息类型

- `text` - 文本消息
- `post` - 富文本消息
- `image` - 图片消息
- `file` - 文件消息
- `audio` - 音频消息
- `video` - 视频消息

## 开发

### 目录结构

```
extensions/feishu/
├── src/
│   ├── index.ts         # 插件入口
│   ├── channel.ts       # 通道实现
│   ├── api.ts           # API 封装
│   ├── auth.ts          # 认证逻辑
│   ├── accounts.ts      # 账户管理
│   ├── targets.ts       # 目标解析
│   ├── monitor.ts       # Webhook 监控
│   ├── runtime.ts       # 运行时状态
│   ├── onboarding.ts    # 配置向导
│   ├── actions.ts       # 操作实现
│   ├── types.ts         # API 类型
│   └── types.config.ts  # 配置类型
├── package.json
└── README.md
```

### 测试

```bash
# 运行测试（需要实现）
pnpm test -- feishu

# 测试连接
pnpm moltbot doctor --channel feishu
```

## 故障排查

### Webhook 无法接收消息

1. 检查防火墙设置
2. 确认 Webhook URL 可以从外网访问
3. 检查飞书开放平台的事件订阅状态

### 消息发送失败

1. 检查 App ID 和 App Secret 是否正确
2. 确认应用权限已通过审核
3. 查看 Gateway 日志：`pnpm moltbot logs`

### Token 过期

访问令牌会自动缓存和刷新。如果遇到认证问题，重启 Gateway 即可。

## 相关链接

- [飞书开放平台文档](https://open.feishu.cn/document/)
- [飞书机器人开发指南](https://open.feishu.cn/document/ukTMukTMukTM/ucTM5YjL3ETO24yNxkjN)
- [Lark API 文档](https://open.larksuite.com/document/)

## 许可证

MIT
