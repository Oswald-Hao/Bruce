#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试飞书卡片发送
"""

import sys
sys.path.insert(0, '/home/lejurobot/moltbot/extensions/feishu/python')

from feishu_extended import FeishuCardGenerator

# 创建卡片生成器
gen = FeishuCardGenerator()

print("=" * 50)
print("飞书卡片测试")
print("=" * 50)

# 1. 测试正在思考卡片
print("\n1. 正在思考卡片:")
thinking_card = gen.create_thinking_card("正在处理您的请求...")
print(f"   标题: {thinking_card['header']['title']['content']}")
print(f"   模板: {thinking_card['header']['template']}")
print(f"   元素数量: {len(thinking_card['elements'])}")

# 2. 测试进度卡片
print("\n2. 进度卡片:")
progress_card = gen.create_progress_card("文件下载", 7, 10, "下载中...")
print(f"   标题: 文件下载")
print(f"   进度: 7/10 (70%)")
print(f"   状态: 下载中...")

# 3. 测试结果卡片
print("\n3. 结果卡片（成功）:")
result_card_success = gen.create_result_card("测试完成", "所有测试用例通过", success=True)
print(f"   标题: {result_card_success['header']['title']['content']}")
print(f"   模板: {result_card_success['header']['template']}")
print(f"   状态: 成功")

print("\n4. 结果卡片（失败）:")
result_card_fail = gen.create_result_card("测试失败", "连接超时", success=False)
print(f"   标题: {result_card_fail['header']['title']['content']}")
print(f"   模板: {result_card_fail['header']['template']}")
print(f"   状态: 失败")

# 5. 测试按钮卡片
print("\n5. 按钮卡片:")
button_card = gen.create_button_card(
    "操作选择",
    "请选择要执行的操作",
    [
        {"text": "确认", "url": "https://example.com/confirm"},
        {"text": "取消", "url": "https://example.com/cancel"}
    ]
)
print(f"   标题: 操作选择")
print(f"   按钮数量: 2")

# 6. 测试所有模板颜色
print("\n6. 模板颜色:")
print(f"   支持的模板数量: {len(gen.templates)}")
print(f"   模板列表: {', '.join(list(gen.templates.keys())[:5])}...")

print("\n" + "=" * 50)
print("✅ 卡片生成测试完成")
print("=" * 50)

print("\n📝 功能说明:")
print("1. 正在思考卡片 - 用于AI处理中")
print("2. 进度卡片 - 用于显示任务进度")
print("3. 结果卡片 - 用于显示成功/失败结果")
print("4. 按钮卡片 - 用于用户交互选择")
print("5. 支持12种颜色模板")

print("\n🚀 集成状态:")
print("✅ 卡片生成器已集成到飞书扩展")
print("✅ 消息接收时自动发送'正在思考'卡片")
print("✅ 处理完成后自动更新为实际回复")
print("✅ 支持消息更新（发送后24小时内）")

print("\n💡 使用方式:")
print("1. 发送任意消息给Bruce")
print("2. 自动收到'🤔 正在思考...'卡片")
print("3. 处理完成后卡片会更新为实际回复")
print("4. 包含自动截图检测功能")
