#!/usr/bin/env python3
"""
快速截图脚本
"""
from PIL import ImageGrab
import os
from datetime import datetime

# 生成文件名
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"/home/lejurobot/clawd/screenshots/screenshot_{timestamp}.png"

# 确保目录存在
os.makedirs(os.path.dirname(filename), exist_ok=True)

# 截图
screenshot = ImageGrab.grab()
screenshot.save(filename)

print(f"✅ 截图已保存: {filename}")
