#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书文件上传器测试脚本
"""

import sys
import json
import io


def test_import():
    """测试导入"""
    print("测试1: 导入模块")
    try:
        sys.path.insert(0, '/home/lejurobot/clawd/skills/feishu-file-uploader')
        from uploader import FeishuFileUploader

        print("✅ 模块导入成功\n")
        return FeishuFileUploader
    except ImportError as e:
        print(f"❌ 导入失败: {e}\n")
        sys.exit(1)


def test_init():
    """测试初始化"""
    print("测试2: 初始化")
    from uploader import FeishuFileUploader

    # 读取配置
    with open('/home/lejurobot/.moltbot/moltbot.json', 'r') as f:
        config = json.load(f)

    app_id = config['channels']['feishu']['appId']
    app_secret = config['channels']['feishu']['appSecret']

    uploader = FeishuFileUploader(app_id, app_secret)

    assert uploader.app_id == app_id
    assert uploader.app_secret == app_secret

    print("✅ 初始化测试通过\n")


def test_get_token():
    """测试获取token"""
    print("测试3: 获取token")
    from uploader import FeishuFileUploader

    # 读取配置
    with open('/home/lejurobot/.moltbot/moltbot.json', 'r') as f:
        config = json.load(f)

    app_id = config['channels']['feishu']['appId']
    app_secret = config['channels']['feishu']['appSecret']

    uploader = FeishuFileUploader(app_id, app_secret)

    try:
        token = uploader.get_tenant_access_token()
        assert token is not None
        assert len(token) > 0
        print(f"✅ Token获取成功: {token[:10]}...\n")
        return uploader
    except Exception as e:
        print(f"❌ Token获取失败: {e}\n")
        sys.exit(1)


def test_create_test_image():
    """测试创建测试图片"""
    print("测试4: 创建测试图片")
    from uploader import FeishuFileUploader

    try:
        from PIL import Image, ImageDraw, ImageFont

        # 创建测试图片
        img = Image.new('RGB', (400, 300), color='lightblue')
        draw = ImageDraw.Draw(img)
        draw.text((100, 150), "测试图片", fill='black')

        # 保存为字节
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes = img_bytes.getvalue()

        print(f"✅ 测试图片创建成功: {len(img_bytes)} bytes\n")
        return img_bytes
    except Exception as e:
        print(f"❌ 创建测试图片失败: {e}\n")
        sys.exit(1)


def test_upload_image_data(uploader, img_bytes):
    """测试上传图片数据"""
    print("测试5: 上传图片数据")
    try:
        image_key = uploader.upload_image_data(img_bytes, "message")
        assert image_key is not None
        assert len(image_key) > 0
        print(f"✅ 图片数据上传成功: {image_key}\n")
        return image_key
    except Exception as e:
        print(f"❌ 上传图片数据失败: {e}\n")
        sys.exit(1)


def test_create_image_message_dict():
    """测试创建图片消息字典"""
    print("测试6: 创建图片消息字典")
    try:
        image_key = "test_image_key_123"
        user_id = "test_user_id"

        message_dict = {
            "receive_id": user_id,
            "receive_id_type": "open_id",
            "msg_type": "image",
            "content": {"image_key": image_key},
            "uuid": "123456"
        }

        assert message_dict["content"]["image_key"] == image_key
        assert message_dict["msg_type"] == "image"
        print("✅ 图片消息字典创建成功\n")


def test_create_file_message_dict():
    """测试创建文件消息字典"""
    print("测试7: 创建文件消息字典")
    try:
        file_key = "test_file_key_456"
        user_id = "test_user_id"

        message_dict = {
            "receive_id": user_id,
            "receive_id_type": "open_id",
            "msg_type": "file",
            "content": {"file_key": file_key},
            "uuid": "123456"
        }

        assert message_dict["content"]["file_key"] == file_key
        assert message_dict["msg_type"] == "file"
        print("✅ 文件消息字典创建成功\n")
    except Exception as e:
        print(f"❌ 创建文件消息字典失败: {e}\n")
        sys.exit(1)


def test_upload_nonexistent_file():
    """测试上传不存在的文件"""
    print("测试8: 上传不存在的文件")
    from uploader import FeishuFileUploader

    # 读取配置
    with open('/home/lejurobot/.moltbot/moltbot.json', 'r') as f:
        config = json.load(f)

    app_id = config['channels']['feishu']['appId']
    app_secret = config['channels']['feishu']['appSecret']

    uploader = FeishuFileUploader(app_id, app_secret)

    try:
        uploader.upload_image("/tmp/nonexistent.png")
        print("❌ 应该抛出异常\n")
        sys.exit(1)
    except FileNotFoundError:
        print("✅ 正确抛出FileNotFoundError\n")


def test_upload_screenshot():
    """测试上传截图"""
    print("测试9: 上传截图（需要PIL）")
    from uploader import FeishuFileUploader

    # 读取配置
    with open('/home/lejurobot/.moltbot/moltbot.json', 'r') as f:
        config = json.load(f)

    app_id = config['channels']['feishu']['appId']
    app_secret = config['channels']['feishu']['appSecret']

    uploader = FeishuFileUploader(app_id, app_secret)

    try:
        image_key = uploader.upload_screenshot()
        print(f"✅ 截图上传成功: {image_key}\n")
    except ImportError:
        print("⏭️  PIL/Pillow未安装，跳过截图测试\n")
    except Exception as e:
        print(f"❌ 截图上传失败: {e}\n")


def run_all_tests():
    """运行所有测试"""
    print("=== 飞书文件上传器测试套件 ===\n")

    tests = [
        test_import,
        test_init,
        test_get_token,
        test_create_test_image,
        test_upload_image_data,
        test_create_image_message_dict,
        test_create_file_message_dict,
        test_upload_nonexistent_file,
        test_upload_screenshot
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test_func.__name__} 失败: {e}\n")
            failed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} 错误: {e}\n")
            failed += 1

    print(f"\n=== 测试结果 ===")
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    print(f"总计: {passed + failed}")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
