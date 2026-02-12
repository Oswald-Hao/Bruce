# 直播电商助手（Live Streaming E-commerce Assistant）

智能直播电商运营助手，提供直播监控、商品管理、互动分析、数据统计等功能，帮助主播和商家提升直播效果和销售转化。

## 功能

### 直播监控
- 实时观看人数监控
- 流量趋势分析
- 在线人数峰值和均值
- 观众停留时长分析
- 观众来源渠道统计

### 商品管理
- 商品上架和下架
- 商品库管理
- 价格动态调整
- 库存实时监控
- 商品点击和转化率分析
- 热门商品推荐

### 互动管理
- 弹幕实时监控和分析
- 粉丝画像分析
- 互动关键词统计
- 热门话题识别
- 自动回复设置
- 粉丝分层管理

### 数据分析
- 直播数据总览（观看人数、互动数、销售额）
- 商品销售分析（销量、销售额、转化率）
- 观众画像分析（年龄、性别、地域、兴趣）
- 转化漏斗分析（观看→点击→加购→下单）
- 历史数据对比
- 直播时段分析

### 自动化助手
- 自动回复弹幕
- 智能商品推荐
- 自动发福利/红包提醒
- 价格变动提醒
- 库存预警
- 超时未互动提醒

### 多平台支持
- 抖音直播
- 快手直播
- 淘宝直播
- 小红书直播
- 视频号直播

## 使用方法

### 启动直播监控

```bash
cd /home/lejurobot/clawd/skills/live-commerce

# 启动监控
python3 live.py start_monitor --platform douyin --room_id "123456789"

# 启动多平台监控
python3 live.py start_monitor --platform douyin,tiktok --room_id "123456789,987654321"
```

### 商品管理

```bash
# 添加商品到库
python3 live.py add_product \
  --name "智能手机" \
  --price 2999 \
  --stock 100 \
  --category "数码"

# 上架商品
python3 live.py list_product --room_id "123456789" \
  --product_id "prod_001" \
  --action "上架"

# 调整价格
python3 live.py adjust_price \
  --room_id "123456789" \
  --product_id "prod_001" \
  --new_price 2799

# 查看商品销售数据
python3 live.py product_stats --room_id "123456789" --product_id "prod_001"
```

### 数据分析

```bash
# 直播数据总览
python3 live.py live_stats --room_id "123456789"

# 观众画像分析
python3 live.py audience_profile --room_id "123456789"

# 转化漏斗分析
python3 live.py conversion_funnel --room_id "123456789"

# 历史数据对比
python3 live.py compare --room_id "123456789" --days 7

# 直播时段分析
python3 live.py time_analysis --room_id "123456789"
```

### 互动管理

```bash
# 实时弹幕监控
python3 live.py monitor_chat --room_id "123456789"

# 设置自动回复
python3 live.py set_auto_reply \
  --room_id "123456789" \
  --keyword "价格" \
  --reply "现在下单立减100元"

# 粉丝画像分析
python3 live.py follower_analysis --room_id "123456789"

# 热门话题分析
python3 live.py hot_topics --room_id "123456789"
```

### 自动化助手

```bash
# 启动自动化助手
python3 live.py start_assistant --room_id "123456789"

# 添加提醒规则
python3 live.py add_alert_rule \
  --type "stock" \
  --threshold 10 \
  --message "库存告警：商品库存不足10件"

# 添加推荐规则
python3 live.py add_recommend_rule \
  --product_id "prod_001" \
  --keywords "手机,数码,智能" \
  --reply "这款手机性价比超高，今天特价！"

# 查看提醒历史
python3 live.py alert_history --room_id "123456789"
```

## 配置

配置文件：`config/live.yaml`

```yaml
# 平台配置
platforms:
  douyin:
    enabled: true
    api_key: "your_api_key"
    api_secret: "your_api_secret"

  kuaishou:
    enabled: false
    api_key: ""

  taobao:
    enabled: false
    api_key: ""

# 监控配置
monitor:
  refresh_interval: 5  # 刷新间隔（秒）
  data_retention_days: 30  # 数据保留天数
  alert_enabled: true  # 是否启用告警

# 商品配置
products:
  default_price_discount: 0.9  # 默认折扣
  low_stock_threshold: 10  # 低库存阈值
  auto_unpublish: true  # 自动下架

# 自动回复配置
auto_reply:
  enabled: true
  max_replies_per_minute: 30  # 每分钟最大回复数
  reply_delay: 2  # 回复延迟（秒）

# 推荐配置
recommend:
  enabled: true
  max_recommendations: 5  # 最大推荐数
  min_similarity: 0.7  # 最小相似度

# 数据分析配置
analytics:
  viewer_segments:
    - name: "新观众"
      condition: "first_view_time < 24h"
    - name: "活跃粉丝"
      condition: "watch_count > 3 in 7 days"
    - name: "高价值用户"
      condition: "total_purchase > 1000"

# 通知配置
notifications:
  feishu:
    enabled: true
    webhook_url: "https://open.feishu.cn/open-apis/bot/v2/hook/..."
  email:
    enabled: false
    smtp_server: "smtp.example.com"
    smtp_port: 587
    smtp_user: "noreply@example.com"
```

## 数据结构

### 商品

```json
{
  "product_id": "prod_001",
  "name": "智能手机",
  "price": 2999,
  "original_price": 3999,
  "stock": 100,
  "category": "数码",
  "description": "高性能智能手机",
  "images": ["image1.jpg", "image2.jpg"],
  "tags": ["热销", "新品"],
  "status": "online",  # online, offline
  "created_at": "2026-02-13T00:00:00",
  "sales_count": 0,
  "click_count": 0,
  "conversion_rate": 0.0
}
```

### 直播记录

```json
{
  "live_id": "live_001",
  "room_id": "123456789",
  "platform": "douyin",
  "title": "新品发布直播",
  "start_time": "2026-02-13T20:00:00",
  "end_time": null,
  "status": "live",  # live, ended
  "max_viewers": 5000,
  "avg_viewers": 3000,
  "total_views": 10000,
  "interaction_count": 500,
  "sales_amount": 50000,
  "products": ["prod_001", "prod_002"]
}
```

### 观众数据

```json
{
  "viewer_id": "viewer_001",
  "room_id": "123456789",
  "join_time": "2026-02-13T20:05:00",
  "leave_time": "2026-02-13T20:15:00",
  "watch_duration": 600,  # 秒
  "platform": "douyin",
  "is_follower": true,
  "interactions": 5,
  "purchases": 0,
  "profile": {
    "age": "25-30",
    "gender": "male",
    "location": "北京",
    "interests": ["数码", "科技"]
  }
}
```

### 弹幕记录

```json
{
  "chat_id": "chat_001",
  "room_id": "123456789",
  "user_id": "viewer_001",
  "username": "用户A",
  "content": "这个手机多少钱？",
  "timestamp": "2026-02-13T20:10:30",
  "type": "question",  # question, comment, praise, complaint
  "replied": false,
  "sentiment": "neutral"  # positive, neutral, negative
}
```

## 数据分析指标

### 直播数据
- 观看人数：当前观看、峰值观看、总观看
- 互动数据：弹幕数、点赞数、分享数
- 销售数据：销售额、订单数、客单价
- 转化数据：观看→下单转化率、下单→支付转化率

### 商品数据
- 销量：商品销量、销量排名
- 销售额：商品销售额、销售额排名
- 点击率：商品点击率、点击转化率
- 库存：当前库存、售罄率

### 观众数据
- 观众画像：年龄分布、性别分布、地域分布
- 粉丝分层：新观众、活跃粉丝、高价值用户
- 行为数据：观看时长、互动频次、购买频次
- 留存数据：回访率、复购率

## 自动化规则

### 提醒规则
- 库存告警：库存低于阈值时提醒
- 价格变动：商品价格变动时提醒
- 超时互动：长时间未互动时提醒
- 热门商品：商品销量突增时提醒
- 异常流量：流量异常时提醒

### 推荐规则
- 关键词匹配：弹幕包含关键词时推荐商品
- 相似商品推荐：用户询问某类商品时推荐相似商品
- 热门推荐：推荐当前热销商品
- 限时推荐：在特定时间段推荐商品

## API接口

```python
# 直播管理
POST /api/live/start
POST /api/live/stop
GET /api/live/{live_id}/stats

# 商品管理
POST /api/products
GET /api/products/{product_id}
PUT /api/products/{product_id}
DELETE /api/products/{product_id}
GET /api/live/{live_id}/products

# 数据分析
GET /api/analytics/live/{live_id}
GET /api/analytics/audience/{live_id}
GET /api/analytics/conversion/{live_id}

# 互动管理
GET /api/chat/{live_id}
POST /api/chat/auto_reply
GET /api/analytics/hot_topics/{live_id}

# 自动化
POST /api/automation/alert_rules
POST /api/automation/recommend_rules
GET /api/automation/alerts/{live_id}
```

## 赚钱价值

### 代直播运营
- 为商家提供直播运营服务
- 按场收费：每场5000-20000元
- 服务10-20个商家：月50000-400000元

### 直播数据分析服务
- 提供直播数据分析报告
- 按报告收费：每个2000-10000元
- 月20-50个报告：月40000-500000元

### 直播培训
- 直播技巧培训
- 按次收费：每次5000-20000元
- 月5-10次培训：月25000-200000元

### SaaS工具订阅
- 直播运营SaaS平台
- 按用户收费：月500-2000元
- 100-500个用户：月50000-1000000元

### 选品服务
- 直播选品服务
- 按商品数收费：每个商品100-500元
- 月50-200个商品：月5000-100000元

### 预期收益
- 代直播运营：月50000-400000元
- 数据分析服务：月40000-500000元
- 直播培训：月25000-200000元
- SaaS订阅：月50000-1000000元
- 选品服务：月5000-100000元
- **总计：月170000-2300000元**

## 注意事项

1. 各平台API接口可能有限流，需要合理控制请求频率
2. 实时监控需要稳定的网络连接
3. 自动回复需要谨慎设置，避免过于频繁
4. 数据隐私保护重要，不要泄露用户信息
5. 商品定价和库存需要实时同步
6. 直播高峰期注意服务器负载
7. 需要持续优化推荐算法提升转化率
