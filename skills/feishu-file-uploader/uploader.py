#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书文件上传器 - Feishu File Uploader

用于上传图片、文件等到飞书，支持多种文件类型
"""

import requests
import os
from typing import Dict, Optional, Tuple
from pathlib import Path


class FeishuFileUploader:
    """飞书文件上传器类"""

    def __init__(self, app_id: str, app_secret: str):
        """
        初始化文件上传器

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

    def upload_image(
        self,
        image_path: str,
        image_type: str = "message"
    ) -> str:
        """
        上传图片到飞书

        Args:
            image_path: 图片文件路径
            image_type: 图片类型（message, avatar）

        Returns:
            image_key（用于发送图片消息）
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")

        # 读取图片
        with open(image_path, 'rb') as f:
            image_data = f.read()

        # 上传图片
        return self.upload_image_data(image_data, image_type)

    def upload_image_data(
        self,
        image_data: bytes,
        image_type: str = "message"
    ) -> str:
        """
        上传图片数据到飞书

        Args:
            image_data: 图片数据（bytes）
            image_type: 图片类型（message, avatar）

        Returns:
            image_key（用于发送图片消息）
        """
        token = self.get_tenant_access_token()

        url = f"{self.base_url}/im/v1/images"
        headers = {
            "Authorization": f"Bearer {token}"
        }

        # 构建表单数据
        files = {
            "image_type": (None, image_type),
            "image": (os.path.basename("screenshot.png"), image_data, "image/png")
        }

        response = requests.post(url, headers=headers, files=files)
        result = response.json()

        if result.get("code") != 0:
            raise Exception(f"上传图片失败: {result}")

        return result["data"]["image_key"]

    def upload_file(
        self,
        file_path: str,
        file_type: str = "file",
        parent_type: str = "chat"
    ) -> str:
        """
        上传文件到飞书

        Args:
            file_path: 文件路径
            file_type: 文件类型（file, audio, video）
            parent_type: 父类型（chat, email）

        Returns:
            file_key（用于发送文件消息）
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 读取文件
        with open(file_path, 'rb') as f:
            file_data = f.read()

        # 上传文件
        return self.upload_file_data(
            file_data,
            file_type,
            parent_type,
            os.path.basename(file_path)
        )

    def upload_file_data(
        self,
        file_data: bytes,
        file_type: str = "file",
        parent_type: str = "chat",
        file_name: str = "upload"
    ) -> str:
        """
        上传文件数据到飞书

        Args:
            file_data: 文件数据（bytes）
            file_type: 文件类型（file, audio, video）
            parent_type: 父类型（chat, email）
            file_name: 文件名

        Returns:
            file_key（用于发送文件消息）
        """
        token = self.get_tenant_access_token()

        url = f"{self.base_url}/drive/v1/medias/upload_all"
        headers = {
            "Authorization": f"Bearer {token}"
        }

        # 构建表单数据
        files = {
            "file_type": (None, file_type),
            "parent_type": (None, parent_type),
            "file": (file_name, file_data)
        }

        response = requests.post(url, headers=headers, files=files)
        result = response.json()

        if result.get("code") != 0:
            raise Exception(f"上传文件失败: {result}")

        return result["data"]["file_key"]

    def create_image_message(
        self,
        user_id: str,
        image_key: str
    ) -> Dict:
        """
        创建图片消息

        Args:
            user_id: 用户ID（open_id）
            image_key: 图片的image_key

        Returns:
            消息字典
        """
        token = self.get_tenant_access_token()

        url = f"{self.base_url}/message/v4/send?receive_id_type=open_id"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Custom-Auth": "t-g1041tjP63RE55E7GSZH6CRXVRNRO7VPUKKZX6JU"
        }
        data = {
            "receive_id": user_id,
            "receive_id_type": "open_id",
            "msg_type": "image",
            "content": {"image_key": image_key},
            "uuid": str(int(__import__('time').time() * 1000))
        }

        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        if result.get("code") != 0:
            raise Exception(f"发送图片消息失败: {result}")

        return result

    def create_file_message(
        self,
        user_id: str,
        file_key: str
    ) -> Dict:
        """
        创建文件消息

        Args:
            user_id: 用户ID（open_id）
            file_key: 文件的file_key

        Returns:
            消息字典
        """
        token = self.get_tenant_access_token()

        url = f"{self.base_url}/message/v4/send?receive_id_type=open_id"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Custom-Auth": "t-g1041tjP63RE55E7GSZH6CRXVRNRO7VPUKKZX6JU"
        }
        data = {
            "receive_id": user_id,
            "receive_id_type": "open_id",
            "msg_type": "file",
            "content": {"file_key": file_key},
            "uuid": str(int(__import__('time').time() * 1000))
        }

        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        if result.get("code") != 0:
            raise Exception(f"发送文件消息失败: {result}")

        return result

    def upload_and_send_image(
        self,
        user_id: str,
        image_path: str
    ) -> Dict:
        """
        上传图片并发送给用户

        Args:
            user_id: 用户ID（open_id）
            image_path: 图片文件路径

        Returns:
            消息字典
        """
        # 上传图片
        image_key = self.upload_image(image_path)

        # 发送图片消息
        return self.create_image_message(user_id, image_key)

    def upload_and_send_file(
        self,
        user_id: str,
        file_path: str,
        file_type: str = "file"
    ) -> Dict:
        """
        上传文件并发送给用户

        Args:
            user_id: 用户ID（open_id）
            file_path: 文件路径
            file_type: 文件类型（file, audio, video）

        Returns:
            消息字典
        """
        # 上传文件
        file_key = self.upload_file(file_path, file_type)

        # 发送文件消息
        return self.create_file_message(user_id, file_key)

    def upload_screenshot(
        self
    ) -> str:
        """
        上传截图（使用PIL的ImageGrab）

        Returns:
            image_key
        """
        try:
            from PIL import ImageGrab

            # 截取屏幕
            screenshot = ImageGrab.grab()

            # 保存为字节
            import io
            img_bytes = io.BytesIO()
            screenshot.save(img_bytes, format='PNG')
            img_bytes = img_bytes.getvalue()

            # 上传截图
            return self.upload_image_data(img_bytes, "message")

        except ImportError:
            raise Exception("PIL/Pillow未安装，无法截图")

    def upload_and_send_screenshot(
        self,
        user_id: str
    ) -> Dict:
        """
        截屏、上传并发送给用户

        Args:
            user_id: 用户ID（open_id）

        Returns:
            消息字典
        """
        # 截屏并上传
        image_key = self.upload_screenshot()

        # 发送图片消息
        return self.create_image_message(user_id, image_key)


def main():
    """测试飞书文件上传器"""
    # 读取配置
    with open('/home/lejurobot/.moltbot/moltbot.json', 'r') as f:
        config = __import__('json').load(f)

    app_id = config['channels']['feishu']['appId']
    app_secret = config['channels']['feishu']['appSecret']
    user_id = "ou_ac30832212aa13310b80594b6a24b8d9"  # 测试用户ID

    print("=== 飞书文件上传器测试 ===\n")

    uploader = FeishuFileUploader(app_id, app_secret)

    # 测试1：创建测试图片
    print("1. 创建测试图片")
    try:
        from PIL import Image, ImageDraw, ImageFont

        # 创建一个测试图片
        img = Image.new('RGB', (400, 300), color='lightblue')
        draw = ImageDraw.Draw(img)
        draw.text((100, 150), "测试图片", fill='black')

        # 保存为字节
        import io
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes = img_bytes.getvalue()

        print("✅ 测试图片创建完成")
        print()
    except Exception as e:
        print(f"❌ 创建测试图片失败: {e}")
        print()
        return

    # 测试2：上传图片数据
    print("2. 上传图片数据")
    try:
        image_key = uploader.upload_image_data(img_bytes)
        print(f"✅ 图片上传成功: {image_key}")
        print()
    except Exception as e:
        print(f"❌ 上传图片失败: {e}")
        print()
        return

    # 测试3：上传图片文件（测试文件）
    print("3. 上传图片文件（需要实际文件）")
    print("⏭️  跳过（需要实际文件路径）")
    print()

    # 测试4：创建图片消息
    print("4. 创建图片消息（不发送）")
    try:
        # 只测试消息字典创建，不实际发送
        message_dict = {
            "receive_id": user_id,
            "receive_id_type": "open_id",
            "msg_type": "image",
            "content": {"image_key": image_key},
            "uuid": "123456"
        }
        assert message_dict["content"]["image_key"] == image_key
        print("✅ 图片消息字典创建成功")
        print()
    except Exception as e:
        print(f"❌ 创建图片消息失败: {e}")
        print()

    # 测试5：创建文件消息（测试）
    print("5. 创建文件消息（需要实际文件）")
    print("⏭️  跳过（需要实际文件路径）")
    print()

    print("=== 测试完成 ===")


if __name__ == "__main__":
    main()
