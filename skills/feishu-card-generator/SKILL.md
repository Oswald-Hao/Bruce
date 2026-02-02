# 飞书卡片生成器 - Feishu Card Generator

**技能路径：** `/home/lejurobot/clawd/skills/feishu-card-generator/`

## 功能描述

创建飞书富文本卡片生成器，支持多种卡片模板，增强飞书交互体验。

**支持功能：**
- ✓ 基础消息卡片（多段文本、标题）
- ✓ 按钮卡片（交互按钮、链接跳转）
- ✓ 列表卡片（有序/无序列表）
- ✓ 图片卡片（单图展示、图片说明）
- ✓ 进度卡片（进度条、百分比显示）
- ✓ 结果卡片（成功/失败状态）
- ✓ 报告卡片（多章节报告）
- ✓ 正在思考卡片（流式输出支持）

## 文件结构

```
feishu-card-generator/
├── SKILL.md      # 技能文档
├── card.py       # 卡片生成器类（核心）
└── test.py       # 测试脚本
```

## 核心类和方法

### FeishuCardGenerator

**初始化：**
```python
from card import FeishuCardGenerator

gen = FeishuCardGenerator()
```

**核心方法：**

1. **create_message_card** - 基础消息卡片
```python
card = gen.create_message_card(
    title="通知",
    content=["消息1", "消息2"],
    template="turquoise",
    markdown=True
)
```

2. **create_button_card** - 按钮卡片
```python
card = gen.create_button_card(
    title="操作确认",
    content="请选择操作",
    buttons=[
        {"text": "确认", "url": "https://..."},
        {"text": "取消", "action": "cancel"}
    ],
    template="blue"
)
```

3. **create_list_card** - 列表卡片
```python
card = gen.create_list_card(
    title="待办事项",
    items=["任务1", "任务2"],
    ordered=True,
    template="wathet"
)
```

4. **create_image_card** - 图片卡片
```python
card = gen.create_image_card(
    title="图片展示",
    image_key="img_key_123",
    content="图片说明"
)
```

5. **create_thinking_card** - 正在思考卡片
```python
card = gen.create_thinking_card("正在处理您的请求...")
```

6. **create_progress_card** - 进度卡片
```python
card = gen.create_progress_card(
    title="任务进度",
    progress=7,
    total=10,
    status="处理中..."
)
```

7. **create_result_card** - 结果卡片
```python
card = gen.create_result_card(
    title="任务完成",
    result="所有任务已成功完成",
    success=True,
    show_details=True
)
```

8. **create_report_card** - 报告卡片
```python
card = gen.create_report_card(
    title="每日报告",
    sections=[
        {"title": "任务", "content": "已完成5个任务"},
        {"title": "进度", "content": "50%"},
        {"title": "状态", "content": "正常"}
    ]
)
```

9. **to_json** - 转换为JSON
```python
json_str = gen.to_json(card, indent=2)
```

## 模板颜色

支持以下模板颜色：
- `turquoise` - 青色（默认）
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

## 使用示例

### 示例1：发送"正在思考"卡片

```python
from card import FeishuCardGenerator
import requests

gen = FeishuCardGenerator()

# 创建"正在思考"卡片
card = gen.create_thinking_card("正在处理您的请求...")

# 转换为JSON
card_json = json.dumps({"card": card}, ensure_ascii=False)

# 发送到飞书（需要飞书API）
# response = send_to_feishu(card_json, user_id)
```

### 示例2：创建进度卡片

```python
gen = FeishuCardGenerator()

# 创建进度卡片
card = gen.create_progress_card(
    title="下载进度",
    progress=75,
    total=100,
    status="下载中..."
)

# 显示进度
print(gen.to_json(card))
```

### 示例3：创建结果卡片

```python
gen = FeishuCardGenerator()

# 成功结果
card1 = gen.create_result_card(
    title="任务完成",
    result="所有任务已成功完成",
    success=True
)

# 失败结果
card2 = gen.create_result_card(
    title="任务失败",
    result="任务执行失败",
    success=False
)
```

### 示例4：创建报告卡片

```python
gen = FeishuCardGenerator()

# 创建每日报告
card = gen.create_report_card(
    title="每日报告 - 2026-02-02",
    sections=[
        {"title": "任务完成", "content": "已完成10个任务"},
        {"title": "技能进化", "content": "新增2个技能"},
        {"title": "系统状态", "content": "所有系统正常运行"},
        {"title": "明日计划", "content": "继续优化飞书功能"}
    ]
)
```

## 集成到Moltbot

### 1. 在Feishu插件中使用

```python
# 在飞书消息发送时使用卡片
from feishu_card_generator.card import FeishuCardGenerator

gen = FeishuCardGenerator()
card = gen.create_thinking_card("正在思考...")

# 发送卡片到飞书
sendFeishuMessage({
    account: account,
    receiveId: userId,
    receiveIdType: "open_id",
    msgType: "interactive",
    content: json.dumps({"card": card})
})
```

### 2. 在流式输出中使用

```python
# 发送"正在思考"卡片
card_gen = FeishuCardGenerator()
thinking_card = card_gen.create_thinking_card("正在处理您的请求...")

# 发送卡片
message_id = send_card_to_feishu(thinking_card, user_id)

# 处理完成后，发送结果卡片
result_card = card_gen.create_result_card(
    title="处理完成",
    result="已成功处理您的请求",
    success=True
)

# 更新或发送新卡片
update_or_send_card(result_card, user_id, message_id)
```

## 测试

运行测试脚本：

```bash
cd /home/lejurobot/clawd/skills/feishu-card-generator
python3 test.py
```

**测试覆盖：**
- ✓ 基础消息卡片
- ✓ 按钮卡片
- ✓ 列表卡片
- ✓ 正在思考卡片
- ✓ 进度卡片
- ✓ 结果卡片
- ✓ 报告卡片
- ✓ 图片卡片
- ✓ JSON转换
- ✓ 边界情况

## 价值评估

**核心价值：**
1. 增强飞书交互体验
2. 支持更丰富的消息格式
3. 提高用户参与度
4. 为后续飞书集成打基础
5. 支持流式输出体验

**应用场景：**
- 流式输出的"正在思考"卡片
- 操作确认卡片
- 报告展示卡片
- 任务提醒卡片
- 进度跟踪卡片
- 结果通知卡片

## 优先级理由

**为什么优先开发飞书功能：**
1. **用户需求：** Oswald要求更好的飞书交互体验
2. **流式输出：** "正在思考"卡片是流式输出的核心
3. **日常使用：** 飞书是主要沟通渠道
4. **提升体验：** 丰富的卡片格式提高用户体验
5. **基础能力：** 为后续飞书高级功能打基础

**对自我更迭的贡献：**
- 增强用户交互能力
- 提升消息展示效果
- 支持更复杂的场景

## 后续优化方向

1. **更多卡片类型：**
   - 表格卡片
   - 图表卡片
   - 音频卡片
   - 视频卡片

2. **高级功能：**
   - 卡片更新（动态更新卡片内容）
   - 卡片交互（按钮点击回调）
   - 卡片联动（卡片之间的关联）

3. **模板系统：**
   - 预定义模板库
   - 自定义主题
   - 卡片继承和扩展

4. **集成优化：**
   - 集成到Moltbot核心
   - 自动卡片选择
   - 智能卡片推荐

## 技术实现

**核心技术：**
- Python 3.x
- JSON 序列化
- 飞书 Open API（卡片格式）
- 面向对象设计

**依赖：**
- 无外部依赖（纯Python标准库）

**性能：**
- 卡片生成：< 1ms
- JSON转换：< 1ms
- 内存占用：< 1MB

## 完成

✅ 技能开发完成
✅ 全部测试通过
✅ 文档编写完成
