# Image Processor - 图像处理系统

## 技能描述

多功能图像处理工具，支持OCR文字识别、图像格式转换、图像编辑、批量处理等功能。

## 核心功能

- OCR文字识别（提取图片中的文字）
- 图像格式转换（JPG/PNG/WebP/GIF互相转换）
- 图像编辑（调整大小、裁剪、旋转、添加水印）
- 批量处理（批量转换、批量调整大小）
- 图像信息提取（尺寸、格式、EXIF数据）

## 使用方法

### OCR文字识别
```python
from image_processor import ImageProcessor

# 初始化
processor = ImageProcessor()

# 识别图片文字
text = processor.ocr('image.png')
print(text)

# 识别并保存结果
processor.ocr('image.png', output_file='output.txt')
```

### 图像格式转换
```python
# 单张转换
processor.convert('image.png', 'output.jpg', quality=95)

# 批量转换
results = processor.batch_convert(
    input_dir='images/',
    output_dir='converted/',
    target_format='jpg',
    quality=90
)
```

### 图像编辑
```python
# 调整大小
processor.resize('image.jpg', 'resized.jpg', width=800, height=600)

# 裁剪
processor.crop('image.jpg', 'cropped.jpg', x=100, y=100, width=500, height=500)

# 旋转
processor.rotate('image.jpg', 'rotated.jpg', angle=90)

# 添加水印
processor.add_watermark(
    'image.jpg',
    'watermarked.jpg',
    watermark_text='© Copyright',
    position='bottom-right'
)
```

### 图像信息
```python
# 获取图像信息
info = processor.get_info('image.jpg')
print(info)
# {'width': 1920, 'height': 1080, 'format': 'JPEG', 'size': 1234567}

# 获取EXIF数据
exif = processor.get_exif('image.jpg')
print(exif)
```

## 配置参数

- quality: JPEG质量（1-100，默认95）
- dpi: 输出DPI（默认72）
- optimize: 是否优化文件大小（默认True）

## 依赖安装

```bash
pip install Pillow pytesseract
```

**注意：** OCR功能需要安装Tesseract OCR引擎：
- Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
- macOS: `brew install tesseract`
- Windows: 从 https://github.com/UB-Mannheim/tesseract/wiki 下载安装

## 文件结构

- image_processor.py - 主程序
- test_image_processor.py - 测试脚本
- SKILL.md - 技能文档

## 支持的格式

输入格式：BMP, EPS, GIF, ICO, JPEG, PNG, TIFF, WebP等
输出格式：JPEG, PNG, WebP, GIF, TIFF等
