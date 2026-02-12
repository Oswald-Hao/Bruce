# 智能广告投放优化系统（Smart Ad Optimizer）

智能化的广告投放管理系统，提供多平台广告管理、智能出价优化、A/B测试、ROI分析等功能，帮助企业提升广告效果和投资回报率。

## 功能

### 多平台广告管理
- 支持Google Ads、Facebook Ads、抖音广告、快手广告
- 统一管理多个广告账户和活动
- 批量操作广告系列和广告组
- 实时同步广告数据

### 智能出价优化
- 自动出价策略（CPC、CPM、CPA、ROAS目标）
- 基于ROI的动态出价调整
- 预算智能分配
- 竞价预测和优化建议

### A/B测试系统
- 广告创意A/B测试
- 受众A/B测试
- 出价A/B测试
- 多变量测试支持
- 统计显著性分析

### ROI分析
- 实时ROI计算
- 广告系列ROI分析
- 转化路径分析
- 归因模型支持
- 预测性分析

### 自动化优化
- 自动暂停低效广告
- 自动增加高ROI广告预算
- 自动调整出价
- 自动生成优化报告
- 规则引擎支持

### 竞品分析
- 竞品广告监控
- 竞品关键词分析
- 市场份额追踪
- 竞争策略建议

## 使用方法

### 添加广告平台账户

```bash
cd /home/lejurobot/clawd/skills/ad-optimizer

# 添加Google Ads账户
python3 ad.py add_account \
  --platform "google" \
  --account_id "123-456-7890" \
  --client_id "client_id" \
  --client_secret "client_secret"

# 添加Facebook Ads账户
python3 ad.py add_account \
  --platform "facebook" \
  --account_id "act_123456" \
  --access_token "your_token"

# 添加抖音广告账户
python3 ad.py add_account \
  --platform "douyin" \
  --account_id "123456" \
  --app_id "app_id" \
  --app_secret "app_secret"
```

### 创建广告系列

```bash
# 创建广告系列
python3 ad.py create_campaign \
  --platform "google" \
  --account_id "123-456-7890" \
  --name "测试广告系列" \
  --budget 10000 \
  --bidding_strategy "MAXIMIZE_CONVERSIONS" \
  --start_date "2026-02-14"

# 设置出价
python3 ad.py set_bidding \
  --campaign_id "camp_001" \
  --strategy "TARGET_ROAS" \
  --target_roas 3.0
```

### A/B测试

```bash
# 创建A/B测试
python3 ad.py create_ab_test \
  --test_name "创意测试" \
  --campaign_id "camp_001" \
  --variable "creative" \
  --variants "A,B,C" \
  --duration 7

# 查看测试结果
python3 ad.py ab_test_results --test_id "test_001"

# 结束测试并应用胜出方案
python3 ad.py conclude_ab_test --test_id "test_001" --apply_winner
```

### ROI分析

```bash
# 广告系列ROI分析
python3 ad.py roi_analysis --campaign_id "camp_001"

# 整体ROI报告
python3 ad.py roi_report \
  --platform "google" \
  --start_date "2026-02-01" \
  --end_date "2026-02-13"

# 转化路径分析
python3 ad.py conversion_path --campaign_id "camp_001"
```

### 自动化优化

```bash
# 启动自动化优化
python3 ad.py start_auto_optimize --platform "google"

# 添加优化规则
python3 ad.py add_optimization_rule \
  --type "pause_low_roi" \
  --condition "roi < 0.5" \
  --action "pause"

# 查看优化建议
python3 ad.py optimization_suggestions --campaign_id "camp_001"

# 应用优化建议
python3 ad.py apply_suggestions --campaign_id "camp_001"
```

### 竞品分析

```bash
# 添加竞品监控
python3 ad.py add_competitor \
  --name "竞争对手A" \
  --platform "google" \
  --keywords ["关键词1", "关键词2"]

# 查看竞品分析报告
python3 ad.py competitor_report --competitor_id "comp_001"

# 竞品关键词分析
python3 ad.py competitor_keywords --competitor_id "comp_001"
```

## 配置

配置文件：`config/ad.yaml`

```yaml
# 平台配置
platforms:
  google:
    enabled: true
    developer_token: "your_token"
    client_id: "your_client_id"
    client_secret: "your_client_secret"

  facebook:
    enabled: false
    app_id: ""
    app_secret: ""

  douyin:
    enabled: false
    app_id: ""
    app_secret: ""

# 优化配置
optimization:
  auto_optimize: true
  check_interval: 3600  # 每小时检查一次
  roi_threshold: 1.0  # ROI低于1.0暂停
  max_daily_budget: 100000  # 每日最大预算

# A/B测试配置
ab_testing:
  min_sample_size: 100  # 最小样本量
  significance_level: 0.05  # 显著性水平
  min_duration_days: 3  # 最短测试天数

# 出价配置
bidding:
  default_strategy: "MAXIMIZE_CONVERSIONS"
  target_roas: 3.0
  max_cpc: 10.0
  min_cpc: 0.5

# 报告配置
reports:
  auto_generate: true
  email_reports: true
  report_schedule: "daily"  # daily, weekly, monthly
  recipients: ["manager@company.com"]
```

## 数据结构

### 广告账户

```json
{
  "account_id": "123-456-7890",
  "platform": "google",
  "name": "主账户",
  "currency": "CNY",
  "status": "active",
  "created_at": "2026-02-13",
  "api_config": {
    "client_id": "xxx",
    "client_secret": "xxx"
  }
}
```

### 广告系列

```json
{
  "campaign_id": "camp_001",
  "account_id": "123-456-7890",
  "name": "测试广告系列",
  "status": "active",
  "budget": 10000,
  "bidding_strategy": "MAXIMIZE_CONVERSIONS",
  "target_roas": 3.0,
  "start_date": "2026-02-14",
  "end_date": null,
  "metrics": {
    "impressions": 10000,
    "clicks": 500,
    "conversions": 25,
    "cost": 1000,
    "revenue": 3000,
    "roi": 2.0
  }
}
```

### A/B测试

```json
{
  "test_id": "test_001",
  "name": "创意测试",
  "campaign_id": "camp_001",
  "variable": "creative",
  "variants": ["A", "B", "C"],
  "start_date": "2026-02-13",
  "end_date": null,
  "status": "running",
  "results": {
    "A": {"impressions": 5000, "clicks": 250, "conversions": 12, "ctr": 0.05, "conversion_rate": 0.048},
    "B": {"impressions": 5000, "clicks": 280, "conversions": 15, "ctr": 0.056, "conversion_rate": 0.054},
    "C": {"impressions": 5000, "clicks": 230, "conversions": 10, "ctr": 0.046, "conversion_rate": 0.043}
  },
  "winner": "B",
  "significance": 0.03
}
```

### 优化规则

```json
{
  "rule_id": "rule_001",
  "type": "pause_low_roi",
  "name": "低ROI自动暂停",
  "condition": "roi < 0.5",
  "action": "pause",
  "enabled": true,
  "created_at": "2026-02-13"
}
```

## 优化策略

### ROI优化
1. **预算分配**：将更多预算分配给高ROI广告系列
2. **出价调整**：根据ROI动态调整出价
3. **关键词优化**：暂停低效关键词，增加高效关键词预算
4. **受众优化**：优化受众定位，提高转化率

### A/B测试
1. **创意测试**：测试不同广告素材
2. **受众测试**：测试不同受众群体
3. **出价测试**：测试不同出价策略
4. **标题测试**：测试不同广告标题

### 自动化
1. **自动暂停**：自动暂停低ROI广告
2. **自动加预算**：自动增加高ROI广告预算
3. **自动调整出价**：根据表现自动调整出价
4. **自动生成报告**：自动发送优化报告

## 赚钱价值

### 代运营服务
- 为企业提供广告投放代运营服务
- 按广告消耗收费（3-5%佣金）+ 基础服务费
- 月服务费：5000-20000元/客户
- 服务10-30个客户：月50000-600000元

### 效果分成
- 按ROI提升比例收费
- 提升ROI的20-30%作为服务费
- 每客户月收益：10000-100000元

### 培训和咨询
- 广告投放培训和咨询
- 按次收费：每次5000-20000元
- 月5-10次培训：月25000-200000元

### SaaS工具订阅
- 提供广告优化SaaS工具
- 按用户收费：月500-2000元/用户
- 100-500个用户：月50000-1000000元

### 预期收益
- 代运营服务：月50000-600000元
- 效果分成：月50000-500000元
- 培训咨询：月25000-200000元
- SaaS订阅：月50000-1000000元
- **总计：月175000-2300000元**

## 注意事项

1. 各平台API有调用限制，需要合理控制请求频率
2. 广告优化需要一定的数据积累，新账户效果可能不稳定
3. A/B测试需要足够的样本量和时间才能得到显著结果
4. ROI计算需要准确的转化追踪数据
5. 自动化优化需要设置合理的阈值，避免过度优化
6. 需要定期监控和调整优化策略
7. 遵守各平台的广告政策和规定
