# 实时数据监控系统

实时监控各种数据源（价格、竞品、库存、新闻等），支持多源聚合、智能预警、自动响应。

## 功能

- 多数据源监控（电商、新闻、股票、社交媒体、API等）
- 实时数据采集和聚合
- 智能变化检测（价格变化、关键词出现、趋势变化）
- 多级预警机制（邮件、短信、Webhook、飞书）
- 自动响应动作（购买、告警、记录、触发脚本）
- 可视化仪表板
- 历史数据查询和分析
- 规则引擎（自定义监控规则）

## 使用方法

### 配置监控任务

```bash
cd /home/lejurobot/clawd/skills/realtime-monitor

# 添加价格监控任务
python3 monitor.py add price \
  --name "iPhone 15 Pro 价格监控" \
  --source taobao \
  --keywords "iPhone 15 Pro 256G" \
  --interval 300 \
  --threshold "price_change > 500" \
  --action "webhook:https://api.example.com/notify"

# 添加新闻监控任务
python3 monitor.py add news \
  --name "AI行业新闻监控" \
  --source toutiao \
  --keywords "人工智能,AI,大模型,ChatGPT" \
  --interval 600 \
  --action "feishu:robot_id"

# 添加竞品监控任务
python3 monitor.py add competitor \
  --name "竞品价格监控" \
  --source jd \
  --target_urls "url1,url2" \
  --interval 1800 \
  --threshold "price < our_price * 0.9"
```

### 查看监控状态

```bash
# 查看所有监控任务
python3 monitor.py list

# 查看特定任务
python3 monitor.py show --task_id task_123

# 查看监控历史
python3 monitor.py history --task_id task_123 --days 7
```

### 启动监控

```bash
# 启动所有监控任务
python3 monitor.py start

# 启动特定任务
python3 monitor.py start --task_id task_123

# 后台运行
nohup python3 monitor.py start > monitor.log 2>&1 &
```

### 查看仪表板

```bash
# 启动Web仪表板
python3 dashboard.py --port 8080

# 访问 http://localhost:8080
```

## 配置

配置文件：`config/monitor.yaml`

```yaml
# 数据源配置
sources:
  taobao:
    enabled: true
    api_key: "your_api_key"
    rate_limit: 10  # 每分钟请求次数

  jd:
    enabled: true
    api_key: "your_api_key"
    rate_limit: 10

  news:
    toutiao:
      enabled: true
      api_key: "your_api_key"

    baidu:
      enabled: true
      api_key: "your_api_key"

# 预警配置
alerts:
  email:
    enabled: true
    smtp_host: "smtp.gmail.com"
    smtp_port: 587
    username: "your_email@gmail.com"
    password: "your_password"
    recipients: ["user@example.com"]

  feishu:
    enabled: true
    webhook_url: "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"

  webhook:
    enabled: true
    default_url: "https://api.example.com/notify"

# 规则引擎
rules:
  price_drop:
    condition: "price_change < -threshold"
    priority: "high"

  keyword_match:
    condition: "keyword in content"
    priority: "medium"

  trend_change:
    condition: "trend > threshold"
    priority: "low"

# 数据存储
storage:
  type: "sqlite"  # sqlite/mysql/postgresql
  path: "data/monitor.db"
  retention_days: 90
```

## 监控规则

### 价格监控规则

```yaml
price_rules:
  - name: "降价提醒"
    condition: "new_price < old_price * 0.95"
    action: "alert"

  - name: "超低价抢购"
    condition: "new_price < target_price * 0.7"
    action: "buy"

  - name: "价格上涨"
    condition: "new_price > old_price * 1.05"
    action: "log"
```

### 新闻监控规则

```yaml
news_rules:
  - name: "关键词匹配"
    condition: "keyword in content"
    action: "notify"

  - name: "突发新闻"
    condition: "category == 'breaking'"
    action: "urgent_alert"

  - name: "趋势分析"
    condition: "keyword_count > threshold"
    action: "analyze_trend"
```

## 输出

- 实时监控数据
- 预警通知
- 变化报告
- 仪表板可视化
- 历史数据分析

## API接口

```python
# 添加监控任务
POST /api/tasks
{
  "name": "监控名称",
  "type": "price/news/competitor",
  "source": "taobao",
  "keywords": ["关键词"],
  "interval": 300,
  "threshold": "规则",
  "action": "动作"
}

# 查询监控数据
GET /api/data?task_id=xxx&start=2026-01-01&end=2026-01-31

# 获取预警
GET /api/alerts?level=warning&hours=24
```

## 注意事项

1. 注意各数据源的API调用限制
2. 监控间隔不宜过短，避免被封禁
3. 预警动作建议先测试再启用
4. 建议配置数据备份和恢复机制
5. 定期清理历史数据，避免存储空间不足

## 赚钱价值

- 代监控服务：帮助商家监控价格和竞品（月3000-20000元）
- 套利发现：发现价格差异，转卖获利（月2000-10000元）
- 数据服务：出售监控数据和分析报告（月1000-5000元）
- 工具SaaS：开发成监控工具SaaS（月费500-3000元）

预期收益：月5000-30000元
