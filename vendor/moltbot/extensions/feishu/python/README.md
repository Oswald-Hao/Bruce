# 飞书扩展功能集合

## 概述

这个Python模块提供了飞书扩展的增强功能，包括：

1. **卡片生成器 (FeishuCardGenerator)**
   - 正在思考卡片
   - 进度卡片（带进度条）
   - 结果卡片（成功/失败）
   - 按钮卡片

2. **消息更新器 (FeishuMessageUpdater)**
   - 发送卡片消息
   - 更新消息内容
   - 流式输出支持

3. **机器人管理器 (FeishuBotManager)**
   - 获取机器人信息
   - 检查机器人在线状态

4. **扩展功能集合 (FeishuExtended)**
   - 统一的API接口
   - 简化使用流程

## 使用方法

### 基本使用

```python
from feishu_extended import create_feishu_extended

# 创建实例
app_id = "your_app_id"
app_secret = "your_app_secret"
feishu = create_feishu_extended(app_id, app_secret)

# 发送正在思考卡片
message_id = feishu.send_thinking_card(
    "user_open_id",
    "正在处理您的请求..."
)
print(f"消息ID: {message_id}")

# 更新进度
feishu.update_progress(
    message_id,
    "任务进度",
    5,
    10,
    "处理中..."
)

# 更新为结果
feishu.update_to_result(
    message_id,
    "任务完成",
    "所有任务已成功完成",
    success=True
)
```

### 获取机器人信息

```python
# 获取机器人信息
bot_info = feishu.get_bot_info()
print(f"机器人名称: {bot_info.get('app_name')}")

# 检查机器人在线状态
online = feishu.get_bot_online_status("bot_open_id")
print(f"机器人在线: {online}")
```

### 创建自定义卡片

```python
from feishu_extended import FeishuCardGenerator

# 创建卡片生成器
gen = FeishuCardGenerator()

# 创建结果卡片
result_card = gen.create_result_card(
    title="任务完成",
    result="所有任务已成功完成",
    success=True
)

# 使用消息更新器发送
from feishu_extended import FeishuMessageUpdater
updater = FeishuMessageUpdater(app_id, app_secret)
message_id = updater.send_card("user_open_id", result_card)
```

## 卡片模板颜色

支持以下模板颜色：
- `turquoise` - 青色
- `blue` - 蓝色
- `wathet` - 淡蓝色
- `lark` - 飞书蓝
- `indigo` - 靛蓝色
- `purple` - 紫色
- `pink` - 粉色
- `red` - 红色
- `orange` - 橙色
- `yellow` - 黄色
- `green` - 绿色
- `grey` - 灰色

## 与Moltbot集成

在飞书扩展中调用Python模块：

```typescript
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

async function sendThinkingCard(userId: string, message: string): Promise<string> {
  const script = `
    import sys
    sys.path.insert(0, '/home/lejurobot/moltbot/extensions/feishu/python')
    from feishu_extended import create_feishu_extended

    app_id = "${process.env.FEISHU_APP_ID}"
    app_secret = "${process.env.FEISHU_APP_SECRET}"
    feishu = create_feishu_extended(app_id, app_secret)

    message_id = feishu.send_thinking_card("${userId}", "${message}")
    print(message_id)
  `;

  const { stdout } = await execAsync(`python3 -c "${script}"`);
  return stdout.trim();
}
```

## 依赖

- Python 3.x
- requests (`pip install requests`)

## 测试

```bash
cd /home/lejurobot/moltbot/extensions/feishu/python
python3 feishu_extended.py
```

## API参考

### FeishuExtended

#### 发送卡片

- `send_thinking_card(user_id, message)` - 发送正在思考卡片
- `send_progress_card(user_id, title, progress, total, status)` - 发送进度卡片

#### 更新消息

- `update_progress(message_id, title, progress, total, status)` - 更新进度卡片
- `update_to_result(message_id, title, result, success)` - 更新为结果卡片
- `update_to_thinking(message_id, message)` - 更新为正在思考卡片

#### 机器人管理

- `get_bot_info(bot_id)` - 获取机器人信息
- `get_bot_online_status(bot_open_id)` - 获取机器人在线状态

## 注意事项

1. Token缓存时间：5分钟（提前5分钟刷新）
2. API请求超时：10秒
3. 消息更新限制：发送后24小时内可更新
4. Token过期后自动刷新

## 错误处理

所有方法都会抛出异常，调用时需要捕获：

```python
try:
    message_id = feishu.send_thinking_card("user_open_id")
except Exception as e:
    print(f"发送失败: {e}")
```

## 性能

- 发送消息：< 500ms
- 更新消息：< 300ms
- Token获取：< 500ms
- 机器人信息查询：< 500ms
