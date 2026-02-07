# 智能客服系统

自动化客户服务，支持多渠道接入、智能问答、工单管理，提升服务效率和客户满意度。

## 功能

- 多渠道接入（微信、网站、APP、电话）
- AI智能问答（基于LLM的自动回复）
- 知识库管理（FAQ、文档、教程）
- 工单系统（创建、分配、跟踪、关闭）
- 人工转接（智能路由到客服人员）
- 客户画像（用户信息、历史记录、标签）
- 数据分析（响应时间、解决率、满意度）
- 多语言支持
- 情感分析
- 主动服务（提醒、推荐）

## 使用方法

### 配置客服渠道

```bash
cd /home/lejurobot/clawd/skills/smart-customer-service

# 添加微信渠道
python3 service.py add_channel \
  --type wechat \
  --app_id "your_app_id" \
  --app_secret "your_app_secret"

# 添加网站渠道
python3 service.py add_channel \
  --type web \
  --domain "example.com" \
  --widget_id "widget_123"
```

### 管理知识库

```bash
# 添加FAQ
python3 service.py add_faq \
  --question "如何退款？" \
  --answer "您可以登录账户，进入订单中心，选择需要退款的订单，点击申请退款。"

# 批量导入FAQ
python3 service.py import_faq --file faq.xlsx

# 搜索知识库
python3 service.py search_kb --query "退款流程"
```

### 管理工单

```bash
# 创建工单
python3 service.py create_ticket \
  --customer_id "user_123" \
  --type "退款" \
  --priority "high" \
  --title "订单退款申请"

# 分配工单
python3 service.py assign_ticket \
  --ticket_id "ticket_123" \
  --agent_id "agent_456"

# 更新工单状态
python3 service.py update_ticket \
  --ticket_id "ticket_123" \
  --status "in_progress" \
  --comment "正在处理退款申请"

# 关闭工单
python3 service.py close_ticket \
  --ticket_id "ticket_123" \
  --resolution "已成功退款"
```

### 启动客服系统

```bash
# 启动所有服务
python3 service.py start

# 启动特定服务
python3 service.py start --channels wechat,web

# 后台运行
nohup python3 service.py start > service.log 2>&1 &
```

### 查看统计

```bash
# 查看总体统计
python3 service.py stats

# 查看客服绩效
python3 service.py agent_performance --agent_id "agent_123"

# 查看满意度报告
python3 service.py satisfaction_report --days 30
```

## 配置

配置文件：`config/service.yaml`

```yaml
# 渠道配置
channels:
  wechat:
    enabled: true
    app_id: "your_app_id"
    app_secret: "your_app_secret"
    token: "your_token"

  web:
    enabled: true
    domain: "example.com"
    widget_id: "widget_123"

  phone:
    enabled: false
    provider: "alicloud"

# AI配置
ai:
  provider: "openai"  # openai/anthropic/azure
  model: "gpt-4"
  api_key: "your_api_key"
  temperature: 0.7
  max_tokens: 1000

# 知识库配置
knowledge_base:
  enabled: true
  faq_file: "data/faq.json"
  similarity_threshold: 0.8

# 工单配置
tickets:
  auto_create: true
  auto_assign: true
  sla_response_time: 3600  # 1小时内响应
  sla_resolution_time: 86400  # 24小时内解决

# 客服配置
agents:
  online_hours: "09:00-21:00"
  max_concurrent_chats: 5
  auto_away_after: 300  # 5分钟无操作后自动离开

# 通知配置
notifications:
  new_ticket: true
  urgent_ticket: true
  new_message: true
  channels: ["feishu", "email"]
```

## 知识库格式

FAQ格式（JSON）：

```json
{
  "faq": [
    {
      "id": "faq_001",
      "question": "如何退款？",
      "answer": "您可以登录账户，进入订单中心，选择需要退款的订单，点击申请退款。",
      "category": "订单",
      "tags": ["退款", "订单"]
    },
    {
      "id": "faq_002",
      "question": "发货需要多长时间？",
      "answer": "通常情况下，我们会在24小时内发货，快递需要3-5天送达。",
      "category": "物流",
      "tags": ["发货", "物流"]
    }
  ]
}
```

## 工单状态

- `open`: 已创建，待处理
- `in_progress`: 处理中
- `waiting_customer`: 等待客户回复
- `resolved`: 已解决
- `closed`: 已关闭
- `cancelled`: 已取消

## 工单优先级

- `low`: 低优先级
- `normal`: 普通优先级
- `high`: 高优先级
- `urgent`: 紧急

## AI问答

基于LLM的智能问答，支持：

- FAQ匹配（基于向量相似度）
- 上下文理解
- 多轮对话
- 情感分析
- 意图识别
- 自动转人工

## 客户画像

记录客户信息：

```json
{
  "customer_id": "user_123",
  "name": "张三",
  "email": "zhangsan@example.com",
  "phone": "13800138000",
  "tags": ["VIP", "退货率高"],
  "total_orders": 10,
  "total_spent": 5000.0,
  "last_purchase": "2026-01-15",
  "tickets_count": 3,
  "satisfaction_score": 4.5
}
```

## 数据分析

支持的指标：

- 响应时间（平均、中位数、P95）
- 解决率
- 客服处理工单数
- 客户满意度
- 渠道分布
- 问题类型分布
- 工单趋势

## API接口

```python
# 发送消息
POST /api/message
{
  "channel": "wechat",
  "customer_id": "user_123",
  "message": "我想退款"
}

# 获取工单
GET /api/tickets?status=open&priority=high

# 更新工单
PUT /api/tickets/{ticket_id}
{
  "status": "in_progress",
  "comment": "正在处理"
}

# 搜索知识库
GET /api/kb/search?q=退款

# 获取统计
GET /api/stats?period=7d
```

## 注意事项

1. AI回答需要人工审核重要问题
2. 知识库需要定期更新
3. 客服培训很重要
4. 监控服务质量
5. 保护客户隐私
6. 遵守相关法规

## 赚钱价值

- 代客服服务：为企业提供客服外包服务（月5000-20000元）
- 系统SaaS：开发成客服系统SaaS（月费1000-5000元）
- 客服培训：客服技能培训（时薪300-1000元）
- 数据服务：提供客户洞察报告（月1000-3000元）

预期收益：月10000-30000元
