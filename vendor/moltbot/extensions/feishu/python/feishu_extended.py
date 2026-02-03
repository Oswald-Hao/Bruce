#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书扩展功能集合
整合卡片生成、消息更新、机器人管理等功能
"""

import json
import requests
import hashlib
import hmac
from datetime import datetime
from typing import Dict, List, Optional, Union


class FeishuCardGenerator:
    """飞书卡片生成器"""

    def __init__(self):
        self.templates = {
            "turquoise": "#00d6b9",
            "blue": "#3370ff",
            "wathet": "#7bc4ff",
            "lark": "#3370ff",
            "indigo": "#626fff",
            "purple": "#a762ff",
            "pink": "#ff64a3",
            "red": "#ff4d4f",
            "orange": "#ff9c6e",
            "yellow": "#ffc300",
            "green": "#3ac487",
            "grey": "#8f959e"
        }

    def create_thinking_card(self, message: str, template: str = "blue") -> Dict:
        """创建正在思考卡片"""
        color = self.templates.get(template, self.templates["blue"])
        return {
            "header": {
                "title": {"content": "🤔 正在思考...", "tag": "plain_text"},
                "template": template
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "plain_text",
                        "content": message
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": "_请稍候，正在处理您的请求..._"
                    }
                }
            ]
        }

    def create_progress_card(self, title: str, progress: int, total: int, status: str = "", template: str = "wathet") -> Dict:
        """创建进度卡片"""
        percentage = int((progress / total) * 100) if total > 0 else 0
        progress_bar = self._create_progress_bar(percentage)

        elements = [
            {
                "tag": "div",
                "text": {
                    "tag": "plain_text",
                    "content": f"{title}\n\n进度：{progress}/{total} ({percentage}%)"
                }
            },
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": progress_bar
                }
            }
        ]

        if status:
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "plain_text",
                    "content": f"\n状态：{status}"
                }
            })

        return {
            "header": {
                "title": {"content": title, "tag": "plain_text"},
                "template": template
            },
            "elements": elements
        }

    def create_result_card(self, title: str, result: str, success: bool = True, show_details: bool = True) -> Dict:
        """创建结果卡片"""
        icon = "✅" if success else "❌"
        template = "green" if success else "red"

        elements = [
            {
                "tag": "div",
                "text": {
                    "tag": "plain_text",
                    "content": f"{icon} {title}"
                }
            }
        ]

        if show_details:
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"\n**结果：**\n{result}"
                }
            })

        return {
            "header": {
                "title": {"content": title, "tag": "plain_text"},
                "template": template
            },
            "elements": elements
        }

    def create_button_card(self, title: str, content: str, buttons: List[Dict], template: str = "blue") -> Dict:
        """创建按钮卡片"""
        elements = [
            {
                "tag": "div",
                "text": {
                    "tag": "plain_text",
                    "content": content
                }
            },
            {
                "tag": "action"
            }
        ]

        # 添加按钮
        for btn in buttons:
            elements.append({
                "tag": "action",
                "actions": [{
                    "tag": "button",
                    "text": {"tag": "plain_text", "content": btn["text"]},
                    "type": "primary",
                    "url": btn.get("url", "")
                }]
            })

        return {
            "header": {
                "title": {"content": title, "tag": "plain_text"},
                "template": template
            },
            "elements": elements
        }

    def _create_progress_bar(self, percentage: int) -> str:
        """创建进度条"""
        filled = "█" * (percentage // 10)
        empty = "░" * (10 - (percentage // 10))
        return f"{filled}{empty} {percentage}%"


class FeishuMessageUpdater:
    """飞书消息更新器"""

    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.token_cache = None
        self.token_expire = 0
        self.api_base = "https://open.feishu.cn/open-apis"

        self.card_generator = FeishuCardGenerator()

    def _get_tenant_access_token(self) -> str:
        """获取租户访问令牌"""
        if self.token_cache and datetime.now().timestamp() < self.token_expire:
            return self.token_cache

        url = f"{self.api_base}/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json"}
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }

        response = requests.post(url, headers=headers, json=data, timeout=10)
        result = response.json()

        if result.get("code") != 0:
            raise Exception(f"获取token失败: {result}")

        self.token_cache = result["tenant_access_token"]
        self.token_expire = datetime.now().timestamp() + result["expire"] - 300
        return self.token_cache

    def send_card(self, user_id: str, card: Dict) -> str:
        """发送卡片消息"""
        token = self._get_tenant_access_token()
        url = f"{self.api_base}/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        data = {
            "receive_id": user_id,
            "msg_type": "interactive",
            "content": json.dumps({"card": card})
        }

        response = requests.post(url, headers=headers, json=data, timeout=10)
        result = response.json()

        if result.get("code") != 0:
            raise Exception(f"发送卡片失败: {result}")

        return result["data"]["message_id"]

    def update_message(self, message_id: str, content: Union[str, Dict]) -> bool:
        """更新消息"""
        token = self._get_tenant_access_token()
        url = f"{self.api_base}/im/v1/messages/{message_id}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        data = {}

        if isinstance(content, str):
            data["content"] = json.dumps({"text": content})
        else:
            data["content"] = json.dumps({"card": content})

        response = requests.request("PATCH", url, headers=headers, json=data, timeout=10)
        result = response.json()

        return result.get("code") == 0

    def send_thinking_card(self, user_id: str, message: str = "正在处理您的请求...") -> str:
        """发送正在思考卡片"""
        card = self.card_generator.create_thinking_card(message)
        return self.send_card(user_id, card)

    def send_progress_card(self, user_id: str, title: str, progress: int, total: int, status: str = "") -> str:
        """发送进度卡片"""
        card = self.card_generator.create_progress_card(title, progress, total, status)
        return self.send_card(user_id, card)

    def update_progress(self, message_id: str, title: str, progress: int, total: int, status: str = "") -> bool:
        """更新进度卡片"""
        card = self.card_generator.create_progress_card(title, progress, total, status)
        return self.update_message(message_id, card)

    def update_to_result(self, message_id: str, title: str, result: str, success: bool = True) -> bool:
        """更新为结果卡片"""
        card = self.card_generator.create_result_card(title, result, success)
        return self.update_message(message_id, card)

    def update_to_thinking(self, message_id: str, message: str = "继续处理...") -> bool:
        """更新为正在思考卡片"""
        card = self.card_generator.create_thinking_card(message)
        return self.update_message(message_id, card)


class FeishuBotManager:
    """飞书机器人管理器"""

    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.api_base = "https://open.feishu.cn/open-apis"
        self.token_cache = None
        self.token_expire = 0

    def _get_tenant_access_token(self) -> str:
        """获取租户访问令牌"""
        if self.token_cache and datetime.now().timestamp() < self.token_expire:
            return self.token_cache

        url = f"{self.api_base}/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json"}
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }

        response = requests.post(url, headers=headers, json=data, timeout=10)
        result = response.json()

        if result.get("code") != 0:
            raise Exception(f"获取token失败: {result}")

        self.token_cache = result["tenant_access_token"]
        self.token_expire = datetime.now().timestamp() + result["expire"] - 300
        return self.token_cache

    def get_bot_info(self, bot_id: Optional[str] = None) -> Dict:
        """获取机器人信息"""
        token = self._get_tenant_access_token()
        url = f"{self.api_base}/bot/v3/info"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        params = {}
        if bot_id:
            params["bot_id"] = bot_id

        response = requests.get(url, headers=headers, params=params, timeout=10)
        result = response.json()

        if result.get("code") != 0:
            raise Exception(f"获取机器人信息失败: {result}")

        return result["data"]["bot"]

    def get_bot_online_status(self, bot_open_id: str) -> bool:
        """获取机器人在线状态"""
        token = self._get_tenant_access_token()
        url = f"{self.api_base}/bot/v3/online_status"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        data = {"bot_open_id": bot_open_id}

        response = requests.post(url, headers=headers, json=data, timeout=10)
        result = response.json()

        if result.get("code") != 0:
            return False

        return result["data"].get("online", False)


class FeishuExtended:
    """飞书扩展功能集合"""

    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.updater = FeishuMessageUpdater(app_id, app_secret)
        self.bot_manager = FeishuBotManager(app_id, app_secret)

    # 消息更新功能
    def send_thinking_card(self, user_id: str, message: str = "正在处理您的请求...") -> str:
        """发送正在思考卡片"""
        return self.updater.send_thinking_card(user_id, message)

    def send_progress_card(self, user_id: str, title: str, progress: int, total: int, status: str = "") -> str:
        """发送进度卡片"""
        return self.updater.send_progress_card(user_id, title, progress, total, status)

    def update_progress(self, message_id: str, title: str, progress: int, total: int, status: str = "") -> bool:
        """更新进度卡片"""
        return self.updater.update_progress(message_id, title, progress, total, status)

    def update_to_result(self, message_id: str, title: str, result: str, success: bool = True) -> bool:
        """更新为结果卡片"""
        return self.updater.update_to_result(message_id, title, result, success)

    def update_to_thinking(self, message_id: str, message: str = "继续处理...") -> bool:
        """更新为正在思考卡片"""
        return self.updater.update_to_thinking(message_id, message)

    # 机器人管理功能
    def get_bot_info(self, bot_id: Optional[str] = None) -> Dict:
        """获取机器人信息"""
        return self.bot_manager.get_bot_info(bot_id)

    def get_bot_online_status(self, bot_open_id: str) -> bool:
        """获取机器人在线状态"""
        return self.bot_manager.get_bot_online_status(bot_open_id)


def create_feishu_extended(app_id: str, app_secret: str) -> FeishuExtended:
    """创建飞书扩展实例"""
    return FeishuExtended(app_id, app_secret)


# 测试
if __name__ == "__main__":
    # 示例使用
    app_id = "your_app_id"
    app_secret = "your_app_secret"

    feishu = create_feishu_extended(app_id, app_secret)

    # 发送正在思考卡片
    # message_id = feishu.send_thinking_card("user_open_id", "正在处理您的请求...")
    # print(f"发送消息ID: {message_id}")

    # 更新进度
    # feishu.update_progress(message_id, "任务进度", 3, 10, "处理中...")

    # 更新为结果
    # feishu.update_to_result(message_id, "任务完成", "所有任务已成功完成", success=True)
