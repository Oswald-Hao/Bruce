# 广告投放优化器技能

智能优化广告投放策略，降低获客成本，提升ROI，帮助商家实现精准营销。

## 功能

- 多平台广告管理（百度、腾讯、巨量引擎、Google、Facebook）
- 智能出价策略（CPA/CPC/CPM优化）
- A/B测试自动化
- 受众优化（人群定向、重定向）
- 创意素材优化（图片、视频、文案）
- 实时竞价监控
- 预算自动分配
- 效果分析和报告

## 使用方法

### 优化广告投放

```bash
# 优化百度搜索广告
cd /home/lejurobot/clawd/skills/ad-spending-optimizer
python3 optimize.py \
  --platform baidu \
  --account "your_account" \
  --budget 5000 \
  --goal "conversion" \
  --max_cpa 100

# 优化腾讯信息流广告
python3 optimize.py \
  --platform tencent \
  --type "feed" \
  --budget 10000 \
  --goal "clicks" \
  --max_cpc 2.5

# 运行A/B测试
python3 ab_test.py \
  --platform tencent \
  --creative_a "ad_creative_1.jpg" \
  --creative_b "ad_creative_2.jpg" \
  --duration 7 \
  --budget 5000
```

### 分析广告效果

```bash
# 生成分析报告
python3 analyze.py \
  --platform all \
  --start_date "2026-01-01" \
  --end_date "2026-01-31" \
  --output report.html

# 实时监控
python3 monitor.py \
  --platform baidu \
  --interval 60
```

## 输出

- 优化后的投放策略
- A/B测试结果报告
- 效果分析报告（HTML/JSON/Markdown）
- 实时监控数据
- ROI提升建议

## 配置

配置文件：`config/ad_accounts.yaml`

```yaml
accounts:
  baidu:
    username: "your_username"
    password: "your_password"
    account_id: "your_account_id"
    token: "your_api_token"

  tencent:
    account_id: "your_account_id"
    app_id: "your_app_id"
    secret: "your_secret_key"

  google:
    customer_id: "your_customer_id"
    developer_token: "your_token"
    client_id: "your_client_id"
    client_secret: "your_client_secret"
```

## API支持

- 百度推广API
- 腾讯广告API
- 巨量引擎API
- Google Ads API
- Facebook Marketing API

## 注意事项

1. 首次使用需要配置各平台的API密钥
2. 部分平台需要申请广告投放资格
3. A/B测试建议至少运行7天
4. 实时监控会增加API调用次数，注意配额
5. 建议从小预算开始测试

## 赚钱价值

- 代运营服务：帮助商家优化广告，收取服务费（月5000-50000元）
- 按效果分成：按节省的广告费分成（10-30%）
- 咨询服务：提供广告投放策略咨询（时薪500-2000元）
- 工具SaaS：开发成广告优化SaaS产品（月费500-5000元）

预期收益：月10000-50000元
