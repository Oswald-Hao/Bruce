#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Email Automation 测试脚本
测试批量发送、邮件分类、模板管理、自动回复等功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from email_automation import EmailAutomation
import json


def test_1_basic_send():
    """测试1: 基本邮件发送（模拟模式）"""
    print("测试1: 基本邮件发送")

    # 创建实例（不配置真实SMTP，只测试逻辑）
    email = EmailAutomation(
        smtp_server='smtp.example.com',
        username='test@example.com',
        password='test-password'
    )

    # 测试邮箱验证
    assert email.validate_email('user@example.com') == True
    assert email.validate_email('invalid-email') == False
    assert email.validate_email('user@') == False

    print("✅ 测试1通过: 邮箱格式验证正常")
    return True


def test_2_batch_send():
    """测试2: 批量邮件发送（变量替换）"""
    print("\n测试2: 批量邮件发送")

    email = EmailAutomation(
        smtp_server='smtp.example.com',
        username='test@example.com',
        password='test-password'
    )

    # 测试收件人列表
    recipients = [
        {'email': 'alice@example.com', 'name': 'Alice', 'company': 'CompanyA'},
        {'email': 'bob@example.com', 'name': 'Bob', 'company': 'CompanyB'},
        {'email': 'charlie@example.com', 'name': 'Charlie', 'company': 'CompanyC'}
    ]

    # 测试变量替换
    subject = 'Hello {name}!'
    template = 'Dear {name},\n\nWelcome to {company}!\n\nBest regards'

    # 预览邮件内容
    previews = email.preview_batch(subject, template, recipients, limit=3)

    assert len(previews) == 3
    assert 'Alice' in previews[0]['subject']
    assert 'CompanyA' in previews[0]['body']
    assert 'Bob' in previews[1]['subject']
    assert 'CompanyB' in previews[1]['body']

    print("✅ 测试2通过: 批量邮件变量替换正常")
    return True


def test_3_template_management():
    """测试3: 模板管理"""
    print("\n测试3: 模板管理")

    email = EmailAutomation(
        smtp_server='smtp.example.com',
        username='test@example.com'
    )

    # 保存模板
    template_name = 'welcome'
    template_content = 'Hello {name}!\n\nWelcome to our service.'
    assert email.save_template(template_name, template_content) == True

    # 加载模板
    loaded_content = email.load_template(template_name)
    assert loaded_content == template_content

    # 列出模板
    templates = email.list_templates()
    assert template_name in templates

    # 加载不存在的模板
    assert email.load_template('nonexistent') is None

    print("✅ 测试3通过: 模板管理正常")
    return True


def test_4_email_categorization():
    """测试4: 邮件分类"""
    print("\n测试4: 邮件分类")

    email = EmailAutomation(
        smtp_server='smtp.example.com'
    )

    # 测试邮件数据
    test_emails = [
        {
            'email': 'user1@example.com',
            'subject': 'Project meeting tomorrow',
            'body': 'Please join the project meeting at 10 AM.'
        },
        {
            'email': 'user2@example.com',
            'subject': 'Invoice #12345',
            'body': 'Your invoice is ready for payment.'
        },
        {
            'email': 'user3@example.com',
            'subject': 'Family gathering this weekend',
            'body': 'We are having a family dinner.'
        },
        {
            'email': 'user4@example.com',
            'subject': 'Help needed with installation',
            'body': 'I need help installing the software.'
        }
    ]

    # 分类规则
    rules = {
        '工作': ['meeting', 'project', 'deadline'],
        '账单': ['invoice', 'payment', 'bill'],
        '个人': ['family', 'friend', 'personal'],
        '支持': ['help', 'support', 'question']
    }

    # 执行分类
    categories = email.categorize_by_keywords(test_emails, rules)

    assert len(categories['工作']) == 1
    assert categories['工作'][0]['email'] == 'user1@example.com'
    assert len(categories['账单']) == 1
    assert categories['账单'][0]['email'] == 'user2@example.com'
    assert len(categories['个人']) == 1
    assert categories['个人'][0]['email'] == 'user3@example.com'
    assert len(categories['支持']) == 1
    assert categories['支持'][0]['email'] == 'user4@example.com'

    print("✅ 测试4通过: 邮件分类正常")
    return True


def test_5_auto_reply():
    """测试5: 自动回复规则"""
    print("\n测试5: 自动回复规则")

    email = EmailAutomation(
        smtp_server='smtp.example.com'
    )

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
        },
        {
            'trigger': 'billing',
            'response': 'For billing questions, please contact billing@example.com',
            'keywords': ['invoice', 'payment', 'bill']
        }
    ]

    email.set_auto_reply_rules(rules)

    # 测试匹配
    response1 = email.match_auto_reply('I need help', 'Can you help me?')
    assert response1 is not None, "第一条匹配失败，返回None"
    assert 'Thank you for your inquiry' in response1, f"第一条匹配内容错误: {response1}"

    response2 = email.match_auto_reply('Request for information', 'I need details')
    assert response2 is not None, "第二条匹配失败，返回None"
    assert 'visit our website' in response2, f"第二条匹配内容错误: {response2}"

    response3 = email.match_auto_reply('Invoice question', 'Payment issue')
    assert response3 is not None, "第三条匹配失败，返回None"
    assert 'billing@example.com' in response3, f"第三条匹配内容错误: {response3}"

    # 测试不匹配
    response4 = email.match_auto_reply('Hello', 'Just saying hi')
    assert response4 is None, f"第四条应该不匹配，但返回了: {response4}"

    print("✅ 测试5通过: 自动回复规则匹配正常")
    return True


def test_6_complex_batch():
    """测试6: 复杂批量发送场景"""
    print("\n测试6: 复杂批量发送场景")

    email = EmailAutomation(
        smtp_server='smtp.example.com',
        username='test@example.com'
    )

    # 复杂收件人列表
    recipients = [
        {
            'email': 'vip1@example.com',
            'name': 'VIP Customer 1',
            'company': 'BigCorp',
            'discount': '30%'
        },
        {
            'email': 'regular1@example.com',
            'name': 'Regular Customer 1',
            'company': 'SmallBiz',
            'discount': '10%'
        },
        {
            'email': 'vip2@example.com',
            'name': 'VIP Customer 2',
            'company': 'MegaCorp',
            'discount': '30%'
        }
    ]

    # 复杂模板
    subject = 'Exclusive {discount} Discount for {name} at {company}!'
    template = '''Dear {name},

As a valued customer at {company}, we are pleased to offer you an exclusive {discount} discount!

This special offer is available for a limited time only.

Best regards,
The Sales Team'''

    # 预览
    previews = email.preview_batch(subject, template, recipients, limit=3)

    assert len(previews) == 3
    assert '30%' in previews[0]['subject']
    assert 'BigCorp' in previews[0]['body']
    assert '10%' in previews[1]['subject']
    assert 'SmallBiz' in previews[1]['body']

    # 测试缺失变量
    bad_recipient = [{'email': 'test@example.com'}]  # 缺少name/company/discount
    bad_previews = email.preview_batch(subject, template, bad_recipient, limit=1)
    assert 'error' in bad_previews[0]

    print("✅ 测试6通过: 复杂批量发送场景正常")
    return True


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("Email Automation 测试套件")
    print("=" * 60)

    tests = [
        test_1_basic_send,
        test_2_batch_send,
        test_3_template_management,
        test_4_email_categorization,
        test_5_auto_reply,
        test_6_complex_batch
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"❌ 测试失败: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)

    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
