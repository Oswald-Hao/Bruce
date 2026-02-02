# Email Automation - 邮件自动化系统

## 技能描述

智能邮件自动化工具，支持批量邮件发送、自动回复、邮件分类、模板管理等功能。

## 核心功能

- 批量邮件发送（收件人列表、个性化内容、进度跟踪）
- 自动回复（基于规则、关键词匹配、智能回复）
- 邮件分类（主题分类、发件人分类、自动标签）
- 模板管理（保存/加载模板、变量替换）
- 邮件分析（打开率、回复率统计）

## 使用方法

### 批量发送邮件
```python
from email_automation import EmailAutomation

# 初始化
email = EmailAutomation(
    smtp_server='smtp.gmail.com',
    smtp_port=587,
    username='your@email.com',
    password='your-password'
)

# 批量发送
recipients = [
    {'email': 'user1@example.com', 'name': 'Alice', 'company': 'CompanyA'},
    {'email': 'user2@example.com', 'name': 'Bob', 'company': 'CompanyB'}
]

result = email.send_batch(
    subject='Hello {name}!',
    template='Dear {name},\n\nWelcome to {company}!',
    recipients=recipients,
    delay=2  # 发送间隔（秒）
)

print(result)  # {'sent': 2, 'failed': 0, 'details': [...]}
```

### 邮件分类
```python
# 按主题分类
categories = email.categorize_by_subject(
    inbox_folder='INBOX',
    rules={
        '工作': ['meeting', 'project', 'deadline'],
        '个人': ['family', 'friend', 'personal'],
        '账单': ['invoice', 'payment', 'bill']
    }
)

# 按发件人分类
categories = email.categorize_by_sender(
    inbox_folder='INBOX',
    sender_map={
        '同事': ['@company.com'],
        '朋友': ['@gmail.com'],
        '系统': ['noreply@', 'support@']
    }
)
```

### 自动回复
```python
# 设置自动回复规则
rules = [
    {
        'trigger': 'help',
        'response': 'Thank you for your inquiry. Our team will reply within 24 hours.',
        'keywords': ['help', 'support', 'question']
    },
    {
        'trigger': 'info',
        'response': 'For more information, visit our website: https://example.com',
        'keywords': ['info', 'information', 'details']
    }
]

email.set_auto_reply_rules(rules)
```

## 配置参数

- smtp_server: SMTP服务器地址
- smtp_port: SMTP端口（默认587）
- username: 邮箱用户名
- password: 邮箱密码/应用密码
- use_tls: 是否使用TLS（默认True）
- default_from: 默认发件人

## 注意事项

1. 需要启用邮箱的"应用专用密码"或"不够安全的应用访问"
2. 批量发送建议设置延迟，避免被标记为垃圾邮件
3. 大量发送前先测试小批量
4. 自动回复规则要谨慎设置，避免无限循环

## 依赖安装

```bash
pip install secure-smtplib email-validator
```

## 文件结构

- email_automation.py - 主程序
- test_email_automation.py - 测试脚本
- templates/ - 邮件模板目录
- SKILL.md - 技能文档
