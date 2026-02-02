#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image Processor - 图像处理系统
支持OCR、格式转换、图像编辑、批量处理
"""

import os
import sys
from typing import Optional, Dict, List, Tuple, Any
from datetime import datetime


class ImageProcessor:
    """图像处理工具类"""

    def __init__(self, quality: int = 95, dpi: int = 72, optimize: bool = True):
        """
        初始化图像处理器

        Args:
            quality: JPEG质量（1-100）
            dpi: 输出DPI
            optimize: 是否优化文件大小
        """
        self.quality = max(1, min(100, quality))
        self.dpi = dpi
        self.optimize = optimize

        # 尝试导入PIL/Pillow
        try:
            from PIL import Image, ImageDraw, ImageFont
            self.PIL = True
            self.Image = Image
            self.ImageDraw = ImageDraw
            self.ImageFont = ImageFont
        except ImportError:
            self.PIL = False
            print("Warning: Pillow not installed. Install with: pip install Pillow")

        # 尝试导入pytesseract（OCR）
        try:
            import pytesseract
            self.pytesseract = pytesseract
            self.ocr_available = True
        except ImportError:
            self.ocr_available = False
            print("Warning: pytesseract not installed. Install with: pip install pytesseract")

    def _check_pil(self) -> bool:
        """检查PIL是否可用"""
        if not self.PIL:
            raise RuntimeError("Pillow not installed. Install with: pip install Pillow")
        return True

    def _check_ocr(self) -> bool:
        """检查OCR是否可用"""
        if not self.ocr_available:
            raise RuntimeError("pytesseract not installed. Install with: pip install pytesseract")
        return True

    def convert(
        self,
        input_path: str,
        output_path: str,
        target_format: str = 'jpg',
        quality: int = None,
        keep_exif: bool = False
    ) -> bool:
        """
        转换图像格式

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            target_format: 目标格式（jpg/png/webp/gif等）
            quality: JPEG质量（可选，默认使用实例设置）
            keep_exif: 是否保留EXIF数据

        Returns:
            是否成功
        """
        self._check_pil()

        try:
            img = self.Image.open(input_path)

            # 转换RGB模式（某些格式不支持RGBA）
            if target_format.lower() in ['jpg', 'jpeg'] and img.mode in ('RGBA', 'P'):
                # 创建白色背景
                background = self.Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background

            # 保存参数
            save_kwargs = {}
            if target_format.lower() in ['jpg', 'jpeg']:
                save_kwargs['quality'] = quality or self.quality
                save_kwargs['optimize'] = self.optimize
                # PIL格式名称
                pil_format = 'JPEG'
            elif target_format.lower() == 'png':
                save_kwargs['optimize'] = self.optimize
                pil_format = 'PNG'
            elif target_format.lower() == 'webp':
                save_kwargs['quality'] = quality or self.quality
                save_kwargs['method'] = 6  # 更好的压缩
                pil_format = 'WEBP'
            elif target_format.lower() == 'gif':
                pil_format = 'GIF'
            elif target_format.lower() == 'tiff' or target_format.lower() == 'tif':
                pil_format = 'TIFF'
            elif target_format.lower() == 'bmp':
                pil_format = 'BMP'
            else:
                pil_format = target_format.upper()

            # 保存图片
            img.save(output_path, format=pil_format, **save_kwargs)
            return True
        except Exception as e:
            print(f"转换失败: {str(e)}")
            return False

    def resize(
        self,
        input_path: str,
        output_path: str,
        width: int = None,
        height: int = None,
        maintain_aspect: bool = True
    ) -> bool:
        """
        调整图像大小

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            width: 目标宽度
            height: 目标高度
            maintain_aspect: 是否保持宽高比

        Returns:
            是否成功
        """
        self._check_pil()

        try:
            img = self.Image.open(input_path)
            original_width, original_height = img.size

            if not width and not height:
                width = original_width
                height = original_height

            # 保持宽高比
            if maintain_aspect:
                if width and height:
                    # 都有指定，按比例缩小到适应
                    ratio = min(width / original_width, height / original_height)
                    width = int(original_width * ratio)
                    height = int(original_height * ratio)
                elif width:
                    height = int(original_height * (width / original_width))
                elif height:
                    width = int(original_width * (height / original_height))

            # 调整大小
            resized = img.resize((width, height), self.Image.Resampling.LANCZOS)
            resized.save(output_path, optimize=self.optimize)
            return True
        except Exception as e:
            print(f"调整大小失败: {str(e)}")
            return False

    def crop(
        self,
        input_path: str,
        output_path: str,
        x: int = 0,
        y: int = 0,
        width: int = None,
        height: int = None
    ) -> bool:
        """
        裁剪图像

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            x: 左上角X坐标
            y: 左上角Y坐标
            width: 裁剪宽度
            height: 裁剪高度

        Returns:
            是否成功
        """
        self._check_pil()

        try:
            img = self.Image.open(input_path)
            img_width, img_height = img.size

            # 默认裁剪到右下角
            if width is None:
                width = img_width - x
            if height is None:
                height = img_height - y

            # 裁剪
            cropped = img.crop((x, y, x + width, y + height))
            cropped.save(output_path, optimize=self.optimize)
            return True
        except Exception as e:
            print(f"裁剪失败: {str(e)}")
            return False

    def rotate(
        self,
        input_path: str,
        output_path: str,
        angle: float,
        expand: bool = False
    ) -> bool:
        """
        旋转图像

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            angle: 旋转角度（度）
            expand: 是否扩展画布

        Returns:
            是否成功
        """
        self._check_pil()

        try:
            img = self.Image.open(input_path)
            rotated = img.rotate(angle, expand=expand, resample=self.Image.BICUBIC)
            rotated.save(output_path, optimize=self.optimize)
            return True
        except Exception as e:
            print(f"旋转失败: {str(e)}")
            return False

    def add_watermark(
        self,
        input_path: str,
        output_path: str,
        watermark_text: str,
        position: str = 'bottom-right',
        font_size: int = 36,
        opacity: int = 128,
        padding: int = 20
    ) -> bool:
        """
        添加水印文字

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            watermark_text: 水印文字
            position: 位置（top-left/top-right/bottom-left/bottom-right/center）
            font_size: 字体大小
            opacity: 透明度（0-255）
            padding: 边距

        Returns:
            是否成功
        """
        self._check_pil()

        try:
            img = self.Image.open(input_path).convert('RGBA')
            txt_layer = self.Image.new('RGBA', img.size, (255, 255, 255, 0))
            draw = self.ImageDraw.Draw(txt_layer)

            # 尝试加载字体
            try:
                font = self.ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
            except:
                font = self.ImageFont.load_default()

            # 获取文本大小
            bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # 计算位置
            img_width, img_height = img.size
            if position == 'top-left':
                x, y = padding, padding
            elif position == 'top-right':
                x, y = img_width - text_width - padding, padding
            elif position == 'bottom-left':
                x, y = padding, img_height - text_height - padding
            elif position == 'bottom-right':
                x, y = img_width - text_width - padding, img_height - text_height - padding
            elif position == 'center':
                x, y = (img_width - text_width) // 2, (img_height - text_height) // 2
            else:
                x, y = padding, padding

            # 绘制文字
            draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, opacity))

            # 合并图层
            watermarked = self.Image.alpha_composite(img, txt_layer)
            watermarked = watermarked.convert('RGB')
            watermarked.save(output_path, optimize=self.optimize)
            return True
        except Exception as e:
            print(f"添加水印失败: {str(e)}")
            return False

    def get_info(self, input_path: str) -> Optional[Dict[str, Any]]:
        """
        获取图像信息

        Args:
            input_path: 输入文件路径

        Returns:
            图像信息字典
        """
        self._check_pil()

        try:
            img = self.Image.open(input_path)
            file_size = os.path.getsize(input_path)

            return {
                'width': img.width,
                'height': img.height,
                'format': img.format,
                'mode': img.mode,
                'size': file_size,
                'size_mb': round(file_size / (1024 * 1024), 2),
                'has_transparency': img.mode in ('RGBA', 'LA', 'P')
            }
        except Exception as e:
            print(f"获取信息失败: {str(e)}")
            return None

    def get_exif(self, input_path: str) -> Optional[Dict[str, Any]]:
        """
        获取EXIF数据

        Args:
            input_path: 输入文件路径

        Returns:
            EXIF数据字典
        """
        self._check_pil()

        try:
            img = self.Image.open(input_path)
            if hasattr(img, '_getexif'):
                exif_data = img._getexif()
                if exif_data:
                    # 转换为可读格式
                    from PIL.ExifTags import TAGS
                    return {TAGS.get(tag, tag): value for tag, value in exif_data.items()}
            return None
        except Exception as e:
            print(f"获取EXIF失败: {str(e)}")
            return None

    def ocr(
        self,
        input_path: str,
        output_file: str = None,
        lang: str = 'eng'
    ) -> Optional[str]:
        """
        OCR文字识别

        Args:
            input_path: 输入图像路径
            output_file: 输出文件路径（可选）
            lang: 语言代码（eng=英语, chi_sim=简体中文）

        Returns:
            识别的文本
        """
        self._check_pil()
        self._check_ocr()

        try:
            img = self.Image.open(input_path)
            text = self.pytesseract.image_to_string(img, lang=lang)

            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(text)

            return text
        except Exception as e:
            print(f"OCR失败: {str(e)}")
            return None

    def batch_convert(
        self,
        input_dir: str,
        output_dir: str,
        target_format: str = 'jpg',
        quality: int = None,
        recursive: bool = False
    ) -> List[Dict[str, str]]:
        """
        批量转换图像格式

        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            target_format: 目标格式
            quality: JPEG质量
            recursive: 是否递归处理子目录

        Returns:
            处理结果列表
        """
        results = []

        # 支持的图片扩展名
        supported_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff', '.tif'}

        # 收集文件
        files = []
        if recursive:
            for root, dirs, filenames in os.walk(input_dir):
                for filename in filenames:
                    ext = os.path.splitext(filename)[1].lower()
                    if ext in supported_extensions:
                        files.append(os.path.join(root, filename))
        else:
            for filename in os.listdir(input_dir):
                ext = os.path.splitext(filename)[1].lower()
                if ext in supported_extensions:
                    files.append(os.path.join(input_dir, filename))

        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        # 转换文件
        for input_file in files:
            # 计算相对路径
            if recursive:
                rel_path = os.path.relpath(input_file, input_dir)
                output_file = os.path.join(output_dir, os.path.splitext(rel_path)[0] + '.' + target_format)
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
            else:
                filename = os.path.basename(input_file)
                output_file = os.path.join(output_dir, os.path.splitext(filename)[0] + '.' + target_format)

            # 转换
            success = self.convert(input_file, output_file, target_format, quality)
            results.append({
                'input': input_file,
                'output': output_file,
                'status': 'success' if success else 'failed'
            })

        return results

    def batch_resize(
        self,
        input_dir: str,
        output_dir: str,
        width: int = None,
        height: int = None,
        maintain_aspect: bool = True,
        recursive: bool = False
    ) -> List[Dict[str, str]]:
        """
        批量调整图像大小

        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            width: 目标宽度
            height: 目标高度
            maintain_aspect: 是否保持宽高比
            recursive: 是否递归处理子目录

        Returns:
            处理结果列表
        """
        results = []

        # 支持的图片扩展名
        supported_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff', '.tif'}

        # 收集文件
        files = []
        if recursive:
            for root, dirs, filenames in os.walk(input_dir):
                for filename in filenames:
                    ext = os.path.splitext(filename)[1].lower()
                    if ext in supported_extensions:
                        files.append(os.path.join(root, filename))
        else:
            for filename in os.listdir(input_dir):
                ext = os.path.splitext(filename)[1].lower()
                if ext in supported_extensions:
                    files.append(os.path.join(input_dir, filename))

        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        # 调整大小
        for input_file in files:
            if recursive:
                rel_path = os.path.relpath(input_file, input_dir)
                output_file = os.path.join(output_dir, rel_path)
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
            else:
                filename = os.path.basename(input_file)
                output_file = os.path.join(output_dir, filename)

            # 调整大小
            success = self.resize(input_file, output_file, width, height, maintain_aspect)
            results.append({
                'input': input_file,
                'output': output_file,
                'status': 'success' if success else 'failed'
            })

        return results


def main():
    """命令行示例"""
    import argparse

    parser = argparse.ArgumentParser(description='图像处理工具')
    parser.add_argument('--action', choices=['info', 'convert', 'resize'], required=True, help='操作类型')
    parser.add_argument('--input', help='输入文件路径')
    parser.add_argument('--output', help='输出文件路径')
    parser.add_argument('--format', help='目标格式')
    parser.add_argument('--width', type=int, help='目标宽度')
    parser.add_argument('--height', type=int, help='目标高度')
    args = parser.parse_args()

    processor = ImageProcessor()

    if args.action == 'info' and args.input:
        info = processor.get_info(args.input)
        if info:
            print(f"图像信息: {info}")

    elif args.action == 'convert' and args.input and args.output and args.format:
        success = processor.convert(args.input, args.output, args.format)
        print(f"转换{'成功' if success else '失败'}")

    elif args.action == 'resize' and args.input and args.output:
        success = processor.resize(args.input, args.output, args.width, args.height)
        print(f"调整大小{'成功' if success else '失败'}")


if __name__ == '__main__':
    main()
