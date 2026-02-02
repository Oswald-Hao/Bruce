#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书消息更新器 - Feishu Message Updater

用于流式输出，实时更新飞书消息（特别是卡片）
"""

import requests
import json
import time
from typing import Dict, Optional
from card import FeishuCardGenerator


class FeishuMessageUpdater:
    """飞书消息更新器类"""

    def __init__(self, app_id: str, app_secret: str):
        """
        初始化消息更新器

        Args:
            app_id: 飞书应用ID
            app_secret: 飞书应用Secret
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = "https://open.feishu.cn/open-apis"
        self.token_cache = None
        self.card_gen = FeishuCardGenerator()

    def get_tenant_access_token(self) -> str:
        """获取租户访问令牌"""
        if self.token_cache:
            return self.token_cache

        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json"}
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }

        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        if result.get("code") != 0:
            raise Exception(f"获取token失败: {result}")

        self.token_cache = result["tenant_access_token"]
        return self.token_cache

    def send_thinking_card(
        self,
        user_id: str,
        message: str = "正在处理您的请求...",
        template: str = "turquoise"
    ) -> str:
        """
        发送"正在思考"卡片

        Args:
            user_id: 用户ID（open_id）
            message: 思考提示消息
            template: 卡片模板颜色

        Returns:
            消息ID
        """
        # 创建"正在思考"卡片
        card = self.card_gen.create_thinking_card(message)
        card["header"]["template"] = template

        # 发送卡片
        return self.send_interactive_message(user_id, card)

    def send_progress_card(
        self,
        user_id: str,
        title: str,
        progress: int,
        total: int,
        status: str = "处理中...",
        template: str = "blue"
    ) -> str:
        """
        发送进度卡片

        Args:
            user_id: 用户ID
            title: 进度标题
            progress: 当前进度
            total: 总数
            status: 状态描述
            template: 卡片模板颜色

        Returns:
            消息ID
        """
        # 创建进度卡片
        card = self.card_gen.create_progress_card(title, progress, total, status)
        card["header"]["template"] = template

        # 发送卡片
        return self.send_interactive_message(user_id, card)

    def send_interactive_message(
        self,
        user_id: str,
        card: Dict
    ) -> str:
        """
        发送交互式消息（卡片）

        Args:
            user_id: 用户ID（open_id）
            card: 卡片字典

        Returns:
            消息ID
        """
        # 深度复制卡片，避免修改原始数据
        card_copy = json.loads(json.dumps(card))

        # 转换header.title为字符串格式
        if 'header' in card_copy and 'title' in card_copy['header']:
            title_obj = card_copy['header']['title']
            if isinstance(title_obj, dict) and 'content' in title_obj:
                card_copy['header']['title'] = title_obj['content']

        token = self.get_tenant_access_token()

        url = f"{self.base_url}/message/v4/send?receive_id_type=open_id"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Custom-Auth": "t-g1041tjP63RE55E7GSZH6CRXVRNRO7VPUKKZX6JU"  # 自定义认证头
        }
        data = {
            "receive_id": user_id,
            "receive_id_type": "open_id",
            "msg_type": "interactive",
            "content": {"card": card_copy},  # 使用对象，不是字符串
            "uuid": str(int(time.time() * 1000))
        }

        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        if result.get("code") != 0:
            raise Exception(f"发送消息失败: {result}")

        return result.get("data", {}).get("message_id")

    def update_card(
        self,
        message_id: str,
        card: Dict
    ) -> bool:
        """
        更新卡片

        Args:
            message_id: 消息ID
            card: 新的卡片内容

        Returns:
            是否成功
        """
        # 深度复制卡片，避免修改原始数据
        card_copy = json.loads(json.dumps(card))

        # 转换header.title为字符串格式
        if 'header' in card_copy and 'title' in card_copy['header']:
            title_obj = card_copy['header']['title']
            if isinstance(title_obj, dict) and 'content' in title_obj:
                card_copy['header']['title'] = title_obj['content']

        token = self.get_tenant_access_token()

        url = f"{self.base_url}/im/v1/messages/{message_id}/update"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Custom-Auth": "t-g1041tjP63RE55E7GSZH6CRXVRNRO7VPUKKZX6JU"  # 自定义认证头
        }
        data = {
            "msg_type": "interactive",
            "content": {"card": card_copy}  # 使用对象，不是字符串
        }

        response = requests.put(url, headers=headers, json=data)
        result = response.json()

        if result.get("code") != 0:
            raise Exception(f"更新消息失败: {result}")

        return True

    def update_progress(
        self,
        message_id: str,
        title: str,
        progress: int,
        total: int,
        status: str = "处理中...",
        template: str = "blue"
    ) -> bool:
        """
        更新进度卡片

        Args:
            message_id: 消息ID
            title: 进度标题
            progress: 当前进度
            total: 总数
            status: 状态描述
            template: 卡片模板颜色

        Returns:
            是否成功
        """
        # 创建新的进度卡片
        card = self.card_gen.create_progress_card(title, progress, total, status)
        card["header"]["template"] = template

        # 更新卡片
        return self.update_card(message_id, card)

    def update_to_result(
        self,
        message_id: str,
        title: str,
        result: str,
        success: bool = True,
        show_details: bool = True
    ) -> bool:
        """
        将"正在思考"卡片更新为结果卡片

        Args:
            message_id: 消息ID
            title: 结果标题
            result: 结果内容
            success: 是否成功
            show_details: 是否显示详细信息

        Returns:
            是否成功
        """
        # 创建结果卡片
        card = self.card_gen.create_result_card(title, result, success, show_details)

        # 更新卡片
        return self.update_card(message_id, card)

    def update_to_thinking(
        self,
        message_id: str,
        message: str = "正在处理您的请求...",
        template: str = "turquoise"
    ) -> bool:
        """
        将卡片更新为"正在思考"卡片

        Args:
            message_id: 消息ID
            message: 思考提示消息
            template: 卡片模板颜色

        Returns:
            是否成功
        """
        # 创建"正在思考"卡片
        card = self.card_gen.create_thinking_card(message)
        card["header"]["template"] = template

        # 更新卡片
        return self.update_card(message_id, card)

    def send_text_message(
        self,
        user_id: str,
        text: str
    ) -> str:
        """
        发送文本消息

        Args:
            user_id: 用户ID（open_id）
            text: 文本内容

        Returns:
            消息ID
        """
        token = self.get_tenant_access_token()

        url = f"{self.base_url}/message/v4/send?receive_id_type=open_id"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        data = {
            "receive_id": user_id,
            "receive_id_type": "open_id",
            "msg_type": "text",
            "content": {"text": text},  # 使用对象而不是字符串
            "uuid": str(int(time.time() * 1000))
        }

        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        if result.get("code") != 0:
            raise Exception(f"发送消息失败: {result}")

        return result.get("data", {}).get("message_id")


def main():
    """测试飞书消息更新器"""
    # 读取配置
    with open('/home/lejurobot/.moltbot/moltbot.json', 'r') as f:
        config = json.load(f)

    app_id = config['channels']['feishu']['appId']
    app_secret = config['channels']['feishu']['appSecret']
    user_id = "ou_ac30832212aa13310b80594b6a24b8d9"  # 测试用户ID

    print("=== 飞书消息更新器测试 ===\n")

    updater = FeishuMessageUpdater(app_id, app_secret)

    # 测试1：发送"正在思考"卡片
    print("1. 发送'正在思考'卡片")
    try:
        message_id = updater.send_thinking_card(
            user_id,
            "正在处理您的请求，请稍候..."
        )
        print(f"✅ 卡片已发送，消息ID: {message_id}")
        print()
    except Exception as e:
        print(f"❌ 发送失败: {e}")
        print()
        return

    # 等待3秒
    print("等待3秒...")
    time.sleep(3)

    # 测试2：更新为进度卡片
    print("2. 更新为进度卡片")
    try:
        updater.update_progress(
            message_id,
            "任务进度",
            5,
            10,
            "处理中..."
        )
        print("✅ 进度卡片已更新")
        print()
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        print()

    # 等待3秒
    print("等待3秒...")
    time.sleep(3)

    # 测试3：更新为结果卡片
    print("3. 更新为结果卡片")
    try:
        updater.update_to_result(
            message_id,
            "任务完成",
            "所有任务已成功完成",
            success=True
        )
        print("✅ 结果卡片已更新")
        print()
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        print()

    print("=== 测试完成 ===")


if __name__ == "__main__":
    main()
