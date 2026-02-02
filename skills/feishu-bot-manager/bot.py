#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书机器人管理器 - Feishu Bot Manager

用于管理飞书机器人，包括机器人信息、权限设置等
"""

import requests
from typing import Dict, Optional, List


class FeishuBotManager:
    """飞书机器人管理器类"""

    def __init__(self, app_id: str, app_secret: str):
        """
        初始化机器人管理器

        Args:
            app_id: 飞书应用ID
            app_secret: 飞书应用Secret
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = "https://open.feishu.cn/open-apis"
        self.token_cache = None

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

    def get_bot_info(
        self,
        bot_id: Optional[str] = None,
        bot_type: str = "app"
    ) -> Dict:
        """
        获取机器人信息

        Args:
            bot_id: 机器人ID（open_id，如果为空则使用当前app）
            bot_type: 机器人类型（app, user）

        Returns:
            机器人信息
        """
        token = self.get_tenant_access_token()

        # 如果没有指定bot_id，使用当前app_id
        if bot_id is None:
            url = f"{self.base_url}/application/v6/applications"
        else:
            url = f"{self.base_url}/bot/v3/info?bot_type={bot_type}&bot_id={bot_id}"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Custom-Auth": "t-g1041tjP63RE55E7GSZH6CRXVRNRO7VPUKKZX6JU"
        }

        response = requests.get(url, headers=headers)
        result = response.json()

        if result.get("code") != 0:
            raise Exception(f"获取机器人信息失败: {result}")

        if bot_id is None:
            return result.get("data", {})
        else:
            return result

    def get_bot_info_by_open_id(self, open_id: str) -> Dict:
        """
        通过open_id获取机器人信息

        Args:
            open_id: 机器人的open_id

        Returns:
            机器人信息
        """
        return self.get_bot_info(open_id, "user")

    def set_bot_name(self, open_id: str, name: str) -> bool:
        """
        设置机器人名称

        Args:
            open_id: 机器人的open_id
            name: 新的名称

        Returns:
            是否成功
        """
        token = self.get_tenant_access_token()

        url = f"{self.base_url}/bot/v3/name"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Custom-Auth": "t-g1041tjP63RE55E7GSZH6CRXVRNRO7VPUKKZX6JU"
        }
        data = {
            "open_id": open_id,
            "name": name
        }

        response = requests.put(url, headers=headers, json=data)
        result = response.json()

        if result.get("code") != 0:
            raise Exception(f"设置机器人名称失败: {result}")

        return True

    def set_bot_avatar(self, open_id: str, image_key: str) -> bool:
        """
        设置机器人头像

        Args:
            open_id: 机器人的open_id
            image_key: 头像图片的image_key

        Returns:
            是否成功
        """
        token = self.get_tenant_access_token()

        url = f"{self.base_url}/bot/v3/avatar"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Custom-Auth": "t-g1041tjP63RE55E7GSZH6CRXVRNRO7VPUKKZX6JU"
        }
        data = {
            "open_id": open_id,
            "avatar": image_key
        }

        response = requests.put(url, headers=headers, json=data)
        result = response.json()

        if result.get("code") != 0:
            raise Exception(f"设置机器人头像失败: {result}")

        return True

    def get_bot_permissions(self, open_id: str) -> List[Dict]:
        """
        获取机器人权限

        Args:
            open_id: 机器人的open_id

        Returns:
            权限列表
        """
        token = self.get_tenant_access_token()

        url = f"{self.base_url}/bot/v3/permissions?bot_id={open_id}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Custom-Auth": "t-g1041tjP63RE55E7GSZH6CRXVRNRO7VPUKKZX6JU"
        }

        response = requests.get(url, headers=headers)
        result = response.json()

        if result.get("code") != 0:
            raise Exception(f"获取机器人权限失败: {result}")

        return result.get("data", {}).get("permissions", [])

    def get_app_permissions(self) -> List[Dict]:
        """
        获取应用权限

        Returns:
            权限列表
        """
        token = self.get_tenant_access_token()

        url = f"{self.base_url}/application/v6/applications/{self.app_id}/permissions"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)
        result = response.json()

        if result.get("code") != 0:
            raise Exception(f"获取应用权限失败: {result}")

        return result.get("data", {}).get("permissions", [])

    def create_bot(
        self,
        name: str,
        avatar: str,
        open_id: str,
        description: Optional[str] = ""
    ) -> Dict:
        """
        创建机器人

        Args:
            name: 机器人名称
            avatar: 头像URL
            open_id: 机器人的open_id
            description: 机器人描述

        Returns:
            机器人信息
        """
        token = self.get_tenant_access_token()

        url = f"{self.base_url}/bot/v3/create"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Custom-Auth": "t-g1041tjP63RE55E7GSZH6CRXVRNRO7VPUKKZX6JU"
        }
        data = {
            "name": name,
            "avatar": avatar,
            "open_id": open_id,
            "description": description
        }

        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        if result.get("code") != 0:
            raise Exception(f"创建机器人失败: {result}")

        return result.get("data", {})

    def delete_bot(self, open_id: str) -> bool:
        """
        删除机器人

        Args:
            open_id: 机器人的open_id

        Returns:
            是否成功
        """
        token = self.get_tenant_access_token()

        url = f"{self.base_url}/bot/v3/delete"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Custom-Auth": "t-g1041tjP63RE55E7GSZH6CRXVRNRO7VPUKKZX6JU"
        }
        data = {
            "open_id": open_id
        }

        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        if result.get("code") != 0:
            raise Exception(f"删除机器人失败: {result}")

        return True

    def get_bot_online_status(self, open_id: str) -> bool:
        """
        获取机器人在线状态

        Args:
            open_id: 机器人的open_id

        Returns:
            是否在线
        """
        try:
            bot_info = self.get_bot_info_by_open_id(open_id)
            return bot_info.get("online", False)
        except Exception:
            return False


def main():
    """测试飞书机器人管理器"""
    import json

    # 读取配置
    with open('/home/lejurobot/.moltbot/moltbot.json', 'r') as f:
        config = json.load(f)

    app_id = config['channels']['feishu']['appId']
    app_secret = config['channels']['feishu']['appSecret']

    print("=== 飞书机器人管理器测试 ===\n")

    manager = FeishuBotManager(app_id, app_secret)

    # 测试1：获取应用机器人信息
    print("1. 获取应用机器人信息")
    try:
        app_bot_info = manager.get_bot_info()
        print(f"✅ 应用名称: {app_bot_info.get('app_name', 'N/A')}")
        print(f"✅ 应用描述: {app_bot_info.get('description', 'N/A')}")
        print(f"✅ 应用类型: {app_bot_info.get('app_type', 'N/A')}")
        print()
    except Exception as e:
        print(f"❌ 获取应用机器人信息失败: {e}")
        print()

    # 测试2：获取应用权限
    print("2. 获取应用权限")
    try:
        permissions = manager.get_app_permissions()
        print(f"✅ 权限数量: {len(permissions)}")
        if permissions:
            print("✅ 权限示例:")
            for perm in permissions[:3]:
                print(f"   - {perm.get('name', 'N/A')}")
        print()
    except Exception as e:
        print(f"❌ 获取应用权限失败: {e}")
        print()

    # 测试3：获取机器人在线状态
    print("3. 获取机器人在线状态")
    try:
        online = manager.get_bot_online_status(app_bot_info.get('open_id', ''))
        print(f"✅ 在线状态: {'在线' if online else '离线'}")
        print()
    except Exception as e:
        print(f"❌ 获取在线状态失败: {e}")
        print()

    print("=== 测试完成 ===")


if __name__ == "__main__":
    main()
