# CRM系统（客户关系管理系统）

专业的客户关系管理系统，帮助企业全方位管理客户信息、销售流程、商机跟踪，提升销售效率和客户满意度。

## 功能

### 客户管理
- 客户信息管理（基本信息、行业、规模、标签）
- 客户搜索和筛选（多条件查询）
- 客户分群（基于RFM模型、行为、属性）
- 客户画像（购买行为、沟通记录、价值评分）
- 客户生命周期管理（潜在客户、新客户、活跃客户、流失客户）

### 联系人管理
- 联系人信息（姓名、职位、邮箱、电话、微信）
- 多联系人关联（一个客户多个联系人）
- 联系人关系（决策人、影响人、使用人）
- 沟通记录（电话、邮件、会议、拜访）

### 销售线索管理
- 线索收集（表单、导入、API）
- 线索评分（基于行为、属性）
- 线索质量判断（高价值、中价值、低价值）
- 线索转化（转化为客户）

### 销售机会（商机）管理
- 商机创建和跟踪
- 销售阶段管理（初步接触、需求确认、方案提交、谈判、成交）
- 成交金额和概率
- 预计成交时间
- 竞品分析

### 任务和日程
- 待办任务管理
- 任务分配（分配给销售）
- 任务提醒（邮件、消息）
- 日历视图
- 任务完成跟踪

### 数据分析
- 销售漏斗分析（各阶段转化率）
- 客户价值分析（CLV、ARPU）
- 销售业绩分析（按销售、按时间段）
- 转化率分析（线索→客户、商机→成交）
- 客户流失分析
- 客户分布分析（行业、地区、规模）

### 自动化工作流
- 自动跟进提醒
- 自动任务分配
- 自动发送邮件
- 客户生命周期自动触发
- 周期性任务自动创建

### 数据管理
- 数据导入导出（Excel、CSV、JSON）
- 数据备份和恢复
- 数据去重
- 字段自定义
- 权限管理

## 使用方法

### 管理客户

```bash
cd /home/lejurobot/clawd/skills/crm-system

# 添加客户
python3 crm.py add_customer \
  --name "科技有限公司" \
  --industry "软件" \
  --scale "中型" \
  --phone "0755-12345678" \
  --email "contact@company.com" \
  --address "深圳市南山区"

# 搜索客户
python3 crm.py search_customers \
  --name "科技" \
  --industry "软件"

# 更新客户
python3 crm.py update_customer \
  --customer_id "cust_001" \
  --scale "大型"

# 删除客户
python3 crm.py delete_customer --customer_id "cust_001"

# 添加客户标签
python3 crm.py add_tag \
  --customer_id "cust_001" \
  --tag "VIP"
```

### 管理联系人

```bash
# 添加联系人
python3 crm.py add_contact \
  --customer_id "cust_001" \
  --name "张三" \
  --position "CTO" \
  --phone "13800138000" \
  --email "zhangsan@company.com"

# 添加沟通记录
python3 crm.py add_interaction \
  --contact_id "contact_001" \
  --type "phone" \
  --content "讨论产品方案"

# 查看客户的所有联系人和沟通记录
python3 crm.py list_contacts --customer_id "cust_001"
```

### 管理销售线索

```bash
# 添加线索
python3 crm.py add_lead \
  --name "李四" \
  --company "新公司" \
  --phone "13900139000" \
  --email "lisi@newcompany.com" \
  --source "网站" \
  --interest "CRM系统"

# 线索评分
python3 crm.py score_lead --lead_id "lead_001"

# 转化线索为客户
python3 crm.py convert_lead --lead_id "lead_001" \
  --customer_name "新公司"

# 批量导入线索
python3 crm.py import_leads --file leads.xlsx
```

### 管理销售机会

```bash
# 创建商机
python3 crm.py create_opportunity \
  --customer_id "cust_001" \
  --title "CRM系统采购" \
  --amount 100000 \
  --stage "初步接触" \
  --probability 20 \
  --expected_close_date "2026-03-15"

# 更新商机阶段
python3 crm.py update_opportunity \
  --opportunity_id "opp_001" \
  --stage "方案提交" \
  --probability 50

# 查看商机列表
python3 crm.py list_opportunities --stage "方案提交"

# 商机成交
python3 crm.py close_opportunity \
  --opportunity_id "opp_001" \
  --status "won" \
  --actual_amount 95000
```

### 管理任务

```bash
# 创建任务
python3 crm.py create_task \
  --type "followup" \
  --customer_id "cust_001" \
  --title "回访客户" \
  --description "确认产品使用情况" \
  --due_date "2026-02-15" \
  --assignee "sales_001"

# 完成任务
python3 crm.py complete_task --task_id "task_001"

# 查看待办任务
python3 crm.py list_tasks --status "pending" \
  --assignee "sales_001"
```

### 客户分析

```bash
# 销售漏斗分析
python3 crm.py sales_funnel

# 客户价值分析
python3 crm.py customer_value

# RFM分析
python3 crm.py rfm_analysis

# 销售业绩分析
python3 crm.py sales_performance \
  --period "2026-01" \
  --sales_rep "sales_001"

# 客户分群
python3 crm.py segment_customers
```

### 数据管理

```bash
# 导出客户数据
python3 crm.py export_customers \
  --format csv \
  --output customers.csv

# 导入客户数据
python3 crm.py import_customers --file customers.csv

# 数据备份
python3 crm.py backup --backup_dir backups/

# 恢复数据
python3 crm.py restore --backup_file backup_20260213.json
```

### 启动自动化

```bash
# 启动自动化服务
python3 crm.py start_automation

# 查看自动化规则
python3 crm.py list_automation_rules

# 添加自动化规则
python3 crm.py add_automation_rule \
  --trigger "lead_created" \
  --action "send_email" \
  --template "welcome_email"
```

## 配置

配置文件：`config/crm.yaml`

```yaml
# 客户配置
customers:
  required_fields: ["name", "phone"]
  custom_fields:
    - name: "行业"
      type: "select"
      options: ["软件", "互联网", "金融", "制造", "其他"]
    - name: "规模"
      type: "select"
      options: ["小型", "中型", "大型"]
  duplicate_check: true

# 线索配置
leads:
  auto_score: true
  score_threshold: 60
  auto_convert_threshold: 80

# 商机配置
opportunities:
  stages:
    - name: "初步接触"
      probability: 10
    - name: "需求确认"
      probability: 30
    - name: "方案提交"
      probability: 50
    - name: "商务谈判"
      probability: 70
    - name: "成交"
      probability: 100
  default_expected_days: 30

# 任务配置
tasks:
  auto_create_reminder: true
  reminder_days: [1, 3, 7]
  default_assignee: "sales_001"

# 自动化配置
automation:
  enabled: true
  rules:
    - trigger: "lead_created"
      action: "send_welcome_email"
    - trigger: "opportunity_stage_changed"
      action: "notify_manager"
    - trigger: "task_due_soon"
      action: "send_reminder"

# 通知配置
notifications:
  email:
    enabled: true
    smtp_server: "smtp.example.com"
    smtp_port: 587
    smtp_user: "noreply@example.com"
    smtp_password: "password"

  feishu:
    enabled: true
    webhook_url: "https://open.feishu.cn/open-apis/bot/v2/hook/..."

# 数据配置
data:
  backup_interval: 86400  # 每天备份一次
  backup_retention_days: 30
  export_formats: ["csv", "xlsx", "json"]
```

## 数据结构

### 客户

```json
{
  "customer_id": "cust_001",
  "name": "科技有限公司",
  "industry": "软件",
  "scale": "中型",
  "phone": "0755-12345678",
  "email": "contact@company.com",
  "address": "深圳市南山区",
  "tags": ["VIP", "高价值"],
  "created_at": "2026-01-15",
  "updated_at": "2026-02-10",
  "status": "active",
  "rfm_score": {"recency": 5, "frequency": 4, "monetary": 5, "total": 14}
}
```

### 联系人

```json
{
  "contact_id": "contact_001",
  "customer_id": "cust_001",
  "name": "张三",
  "position": "CTO",
  "phone": "13800138000",
  "email": "zhangsan@company.com",
  "wechat": "zhangsan_wx",
  "role": "决策人",
  "interactions": [
    {
      "date": "2026-02-10",
      "type": "phone",
      "content": "讨论产品方案"
    }
  ]
}
```

### 销售线索

```json
{
  "lead_id": "lead_001",
  "name": "李四",
  "company": "新公司",
  "phone": "13900139000",
  "email": "lisi@newcompany.com",
  "position": "采购经理",
  "source": "网站",
  "interest": "CRM系统",
  "score": 75,
  "status": "new",
  "created_at": "2026-02-10",
  "assigned_to": "sales_001"
}
```

### 商机

```json
{
  "opportunity_id": "opp_001",
  "customer_id": "cust_001",
  "title": "CRM系统采购",
  "amount": 100000,
  "stage": "方案提交",
  "probability": 50,
  "expected_close_date": "2026-03-15",
  "created_at": "2026-02-01",
  "updated_at": "2026-02-10",
  "assigned_to": "sales_001",
  "competitors": ["Salesforce", "钉钉CRM"],
  "status": "open"
}
```

### 任务

```json
{
  "task_id": "task_001",
  "type": "followup",
  "customer_id": "cust_001",
  "contact_id": "contact_001",
  "opportunity_id": "opp_001",
  "title": "回访客户",
  "description": "确认产品使用情况",
  "due_date": "2026-02-15",
  "priority": "normal",
  "status": "pending",
  "assignee": "sales_001",
  "created_at": "2026-02-10"
}
```

## RFM分析

RFM模型：
- **Recency（最近购买）**：最近一次购买时间，分值越高越好
- **Frequency（购买频率）**：购买次数，分值越高越好
- **Monetary（购买金额）**：购买金额，分值越高越好

客户分群：
- **VIP客户**：R高、F高、M高
- **重要发展客户**：R高、F低、M高
- **重要保持客户**：R低、F高、M高
- **重要挽留客户**：R低、F高、M低
- **一般发展客户**：R高、F低、M低
- **一般保持客户**：R低、F低、M低

## 销售漏斗

```
初步接触 → 需求确认 → 方案提交 → 商务谈判 → 成交
   100%      80%         50%         30%       20%
```

## API接口

```python
# 客户管理
POST /api/customers
GET /api/customers/{customer_id}
PUT /api/customers/{customer_id}
DELETE /api/customers/{customer_id}
GET /api/customers/search

# 联系人管理
POST /api/contacts
GET /api/contacts?customer_id={customer_id}

# 线索管理
POST /api/leads
GET /api/leads/{lead_id}
PUT /api/leads/{lead_id}/convert

# 商机管理
POST /api/opportunities
GET /api/opportunities
PUT /api/opportunities/{opportunity_id}
PUT /api/opportunities/{opportunity_id}/close

# 任务管理
POST /api/tasks
GET /api/tasks
PUT /api/tasks/{task_id}/complete

# 数据分析
GET /api/analytics/sales_funnel
GET /api/analytics/customer_value
GET /api/analytics/rfm
```

## 赚钱价值

### 代运营服务
- 为中小企业提供CRM系统搭建和数据录入服务
- 按企业规模收费：月5000-30000元
- 服务10-20家企业：月50000-600000元

### CRM SaaS订阅
- 提供CRM系统云服务订阅
- 按用户数收费：月200-500元/用户
- 100-500个企业用户：月20000-250000元

### 定制开发
- 为大中型企业定制CRM系统
- 按项目收费：每个项目100000-500000元
- 每月2-5个项目：月200000-2500000元

### 数据服务
- 销售数据分析报告
- 客户洞察报告
- 按报告收费：每个5000-20000元

### 培训和咨询
- CRM使用培训
- 销售流程优化咨询
- 按次收费：每次10000-50000元

### 预期收益
- 代运营：月50000-600000元
- SaaS订阅：月20000-250000元
- 定制开发：月200000-2500000元
- 数据服务：月10000-100000元
- 培训咨询：月20000-200000元
- **总计：月300000-3650000元**

## 注意事项

1. 数据安全非常重要，需要加密存储敏感信息
2. 权限管理要严格，不同角色有不同权限
3. 定期备份客户数据
4. 遵守数据保护法规（如GDPR）
5. 确保数据质量，定期清理无效数据
6. 用户体验要友好，销售愿意使用
7. 移动端支持很重要
8. 与其他系统集成（邮件、日历、ERP等）
