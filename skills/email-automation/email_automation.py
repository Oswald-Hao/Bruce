#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Email Automation - 邮件自动化系统
支持批量发送、自动回复、邮件分类、模板管理
"""

import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr, parseaddr
from email.header import decode_header
import time
import re
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple


class EmailAutomation:
    """邮件自动化工具类"""

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int = 587,
        username: str = None,
        password: str = None,
        use_tls: bool = True,
        default_from: str = None
    ):
        """
        初始化邮件自动化工具

        Args:
            smtp_server: SMTP服务器地址
            smtp_port: SMTP端口
            username: 邮箱用户名
            password: 邮箱密码
            use_tls: 是否使用TLS加密
            default_from: 默认发件人
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username or ''
        self.password = password or ''
        self.use_tls = use_tls
        self.default_from = default_from or username
        self.auto_reply_rules = []

        # 创建模板目录
        self.template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        os.makedirs(self.template_dir, exist_ok=True)

    def _connect_smtp(self) -> smtplib.SMTP:
        """连接SMTP服务器"""
        try:
            smtp = smtplib.SMTP(self.smtp_server, self.smtp_port)
            if self.use_tls:
                smtp.starttls()
            if self.username and self.password:
                smtp.login(self.username, self.password)
            return smtp
        except Exception as e:
            raise Exception(f"SMTP连接失败: {str(e)}")

    def _send_single(
        self,
        smtp: smtplib.SMTP,
        to_email: str,
        subject: str,
        body: str,
        from_name: str = None,
        from_email: str = None,
        html: bool = False
    ) -> Tuple[bool, str]:
        """
        发送单封邮件

        Args:
            smtp: SMTP连接对象
            to_email: 收件人邮箱
            subject: 邮件主题
            body: 邮件内容
            from_name: 发件人名称
            from_email: 发件人邮箱
            html: 是否为HTML格式

        Returns:
            (是否成功, 错误信息)
        """
        try:
            # 构建邮件
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = formataddr((from_name or '', from_email or self.default_from))
            msg['To'] = to_email

            # 添加正文
            if html:
                msg.attach(MIMEText(body, 'html', 'utf-8'))
            else:
                msg.attach(MIMEText(body, 'plain', 'utf-8'))

            # 发送
            smtp.send_message(msg)
            return True, ''
        except Exception as e:
            return False, str(e)

    def send_batch(
        self,
        subject: str,
        template: str,
        recipients: List[Dict[str, str]],
        from_name: str = None,
        from_email: str = None,
        delay: float = 1.0,
        html: bool = False
    ) -> Dict[str, Any]:
        """
        批量发送邮件（支持变量替换）

        Args:
            subject: 邮件主题（支持{variable}变量）
            template: 邮件模板（支持{variable}变量）
            recipients: 收件人列表，每个元素为包含email和变量的字典
            from_name: 发件人名称
            from_email: 发件人邮箱
            delay: 发送间隔（秒）
            html: 是否为HTML格式

        Returns:
            发送结果统计
        """
        result = {
            'sent': 0,
            'failed': 0,
            'details': []
        }

        smtp = self._connect_smtp()

        try:
            for recipient in recipients:
                to_email = recipient.get('email')
                if not to_email:
                    result['failed'] += 1
                    result['details'].append({
                        'email': to_email,
                        'status': 'failed',
                        'error': 'Missing email address'
                    })
                    continue

                # 变量替换
                try:
                    personalized_subject = subject.format(**recipient)
                    personalized_body = template.format(**recipient)
                except KeyError as e:
                    result['failed'] += 1
                    result['details'].append({
                        'email': to_email,
                        'status': 'failed',
                        'error': f'Missing variable: {str(e)}'
                    })
                    continue

                # 发送邮件
                success, error = self._send_single(
                    smtp, to_email, personalized_subject, personalized_body,
                    from_name, from_email, html
                )

                if success:
                    result['sent'] += 1
                    result['details'].append({
                        'email': to_email,
                        'status': 'sent',
                        'error': ''
                    })
                else:
                    result['failed'] += 1
                    result['details'].append({
                        'email': to_email,
                        'status': 'failed',
                        'error': error
                    })

                # 延迟
                if delay > 0 and recipient != recipients[-1]:
                    time.sleep(delay)

        finally:
            smtp.quit()

        return result

    def send(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_name: str = None,
        from_email: str = None,
        html: bool = False
    ) -> Tuple[bool, str]:
        """
        发送单封邮件

        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            body: 邮件内容
            from_name: 发件人名称
            from_email: 发件人邮箱
            html: 是否为HTML格式

        Returns:
            (是否成功, 错误信息)
        """
        smtp = self._connect_smtp()

        try:
            success, error = self._send_single(
                smtp, to_email, subject, body, from_name, from_email, html
            )
            return success, error
        finally:
            smtp.quit()

    def categorize_by_keywords(
        self,
        emails: List[Dict[str, str]],
        rules: Dict[str, List[str]]
    ) -> Dict[str, List[Dict[str, str]]]:
        """
        根据关键词分类邮件（本地数据）

        Args:
            emails: 邮件列表，每个邮件包含subject/body等字段
            rules: 分类规则，格式为 {'分类名': ['关键词1', '关键词2']}

        Returns:
            分类后的邮件字典
        """
        categories = {name: [] for name in rules.keys()}
        categories['未分类'] = []

        for email_item in emails:
            # 合并主题和正文进行匹配
            text = (email_item.get('subject', '') + ' ' + email_item.get('body', '')).lower()
            matched = False

            for category, keywords in rules.items():
                if any(keyword.lower() in text for keyword in keywords):
                    categories[category].append(email_item)
                    matched = True
                    break

            if not matched:
                categories['未分类'].append(email_item)

        return categories

    def save_template(self, name: str, content: str) -> bool:
        """
        保存邮件模板

        Args:
            name: 模板名称
            content: 模板内容（支持{variable}变量）

        Returns:
            是否成功
        """
        try:
            template_path = os.path.join(self.template_dir, f'{name}.txt')
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception:
            return False

    def load_template(self, name: str) -> Optional[str]:
        """
        加载邮件模板

        Args:
            name: 模板名称

        Returns:
            模板内容，不存在返回None
        """
        try:
            template_path = os.path.join(self.template_dir, f'{name}.txt')
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None

    def list_templates(self) -> List[str]:
        """列出所有模板名称"""
        templates = []
        try:
            for filename in os.listdir(self.template_dir):
                if filename.endswith('.txt'):
                    templates.append(filename[:-4])  # 移除.txt后缀
        except Exception:
            pass
        return templates

    def set_auto_reply_rules(self, rules: List[Dict[str, Any]]) -> None:
        """
        设置自动回复规则

        Args:
            rules: 规则列表，每个规则包含：
                - trigger: 触发器名称
                - response: 回复内容（支持{variable}）
                - keywords: 关键词列表
        """
        self.auto_reply_rules = rules

    def match_auto_reply(self, subject: str, body: str) -> Optional[str]:
        """
        匹配自动回复规则（选择最佳匹配）

        Args:
            subject: 邮件主题
            body: 邮件正文

        Returns:
            匹配到的回复内容，未匹配返回None
        """
        text = (subject + ' ' + body).lower()

        best_match = None
        max_count = 0

        for rule in self.auto_reply_rules:
            keywords = rule.get('keywords', [])
            # 统计该规则匹配的关键词数量
            match_count = sum(1 for keyword in keywords if keyword.lower() in text)

            # 选择匹配数量最多的规则
            if match_count > 0 and match_count > max_count:
                max_count = match_count
                best_match = rule.get('response', '')

        return best_match

    def validate_email(self, email_addr: str) -> bool:
        """
        验证邮箱地址格式

        Args:
            email_addr: 邮箱地址

        Returns:
            是否有效
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email_addr) is not None

    def preview_batch(
        self,
        subject: str,
        template: str,
        recipients: List[Dict[str, str]],
        limit: int = 5
    ) -> List[Dict[str, str]]:
        """
        预览批量邮件内容（不实际发送）

        Args:
            subject: 邮件主题
            template: 邮件模板
            recipients: 收件人列表
            limit: 最多预览数量

        Returns:
            预览列表
        """
        previews = []

        for i, recipient in enumerate(recipients[:limit]):
            try:
                personalized_subject = subject.format(**recipient)
                personalized_body = template.format(**recipient)
                previews.append({
                    'email': recipient.get('email'),
                    'subject': personalized_subject,
                    'body': personalized_body[:200] + '...' if len(personalized_body) > 200 else personalized_body
                })
            except KeyError as e:
                previews.append({
                    'email': recipient.get('email'),
                    'error': f'Missing variable: {str(e)}'
                })

        return previews


def main():
    """命令行示例"""
    import argparse

    parser = argparse.ArgumentParser(description='邮件自动化工具')
    parser.add_argument('--action', choices=['send', 'batch', 'template'], required=True, help='操作类型')
    parser.add_argument('--to', help='收件人邮箱')
    parser.add_argument('--subject', help='邮件主题')
    parser.add_argument('--body', help='邮件内容')
    parser.add_argument('--template', help='模板名称')
    args = parser.parse_args()

    # 示例配置（实际使用时替换为真实配置）
    email = EmailAutomation(
        smtp_server='smtp.gmail.com',
        smtp_port=587,
        username='your@email.com',
        password='your-password'
    )

    if args.action == 'send':
        if args.to and args.subject and args.body:
            success, error = email.send(args.to, args.subject, args.body)
            print(f'发送{"成功" if success else "失败"}: {error}')
        else:
            print('缺少必要参数: --to, --subject, --body')

    elif args.action == 'template':
        if args.template:
            content = email.load_template(args.template)
            if content:
                print(f'模板内容:\n{content}')
            else:
                print(f'模板 {args.template} 不存在')


if __name__ == '__main__':
    main()
