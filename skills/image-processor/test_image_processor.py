#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image Processor 测试脚本
测试OCR、格式转换、图像编辑、批量处理等功能
"""

import sys
import os
import tempfile
import shutil
sys.path.insert(0, os.path.dirname(__file__))

from image_processor import ImageProcessor


def test_1_initialization():
    """测试1: 初始化"""
    print("测试1: 初始化")

    # 初始化处理器
    processor = ImageProcessor(quality=90, dpi=150, optimize=True)

    assert processor.quality == 90
    assert processor.dpi == 150
    assert processor.optimize == True

    print("✅ 测试1通过: 初始化正常")
    return True


def test_2_image_info():
    """测试2: 图像信息获取"""
    print("\n测试2: 图像信息获取")

    processor = ImageProcessor()

    # 创建测试图像
    from PIL import Image
    img = Image.new('RGB', (640, 480), color='red')

    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        tmp_path = tmp.name

    try:
        img.save(tmp_path)
        info = processor.get_info(tmp_path)

        assert info is not None
        assert info['width'] == 640
        assert info['height'] == 480
        assert info['format'] == 'PNG'
        assert info['mode'] == 'RGB'
        assert 'size' in info

        print("✅ 测试2通过: 图像信息获取正常")
        return True
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_3_format_conversion():
    """测试3: 格式转换"""
    print("\n测试3: 格式转换")

    processor = ImageProcessor()

    # 创建测试图像（PNG）
    from PIL import Image
    img = Image.new('RGB', (200, 200), color='blue')

    input_path = tempfile.mktemp(suffix='.png')
    output_path = tempfile.mktemp(suffix='.jpg')

    try:
        img.save(input_path)

        # PNG转JPG
        success = processor.convert(input_path, output_path, 'jpg', quality=95)
        assert success == True
        assert os.path.exists(output_path)

        # 验证输出图像
        converted_img = Image.open(output_path)
        assert converted_img.size == (200, 200)

        print("✅ 测试3通过: 格式转换正常")
        return True
    finally:
        for path in [input_path, output_path]:
            if os.path.exists(path):
                os.unlink(path)


def test_4_resize():
    """测试4: 调整大小"""
    print("\n测试4: 调整大小")

    processor = ImageProcessor()

    # 创建测试图像
    from PIL import Image
    img = Image.new('RGB', (800, 600), color='green')

    input_path = tempfile.mktemp(suffix='.jpg')
    output_path = tempfile.mktemp(suffix='.jpg')

    try:
        img.save(input_path, quality=95)

        # 调整到400x300
        success = processor.resize(input_path, output_path, width=400, height=300)
        assert success == True
        assert os.path.exists(output_path)

        # 验证尺寸
        resized_img = Image.open(output_path)
        assert resized_img.size == (400, 300)

        # 测试保持宽高比
        output_path2 = tempfile.mktemp(suffix='.jpg')
        success = processor.resize(input_path, output_path2, width=400, maintain_aspect=True)
        assert success == True

        resized_img2 = Image.open(output_path2)
        assert resized_img2.size == (400, 300)  # 800x600缩小一半

        os.unlink(output_path2)

        print("✅ 测试4通过: 调整大小正常")
        return True
    finally:
        for path in [input_path, output_path]:
            if os.path.exists(path):
                os.unlink(path)


def test_5_crop():
    """测试5: 裁剪"""
    print("\n测试5: 裁剪")

    processor = ImageProcessor()

    # 创建测试图像
    from PIL import Image
    img = Image.new('RGB', (500, 500), color='yellow')

    input_path = tempfile.mktemp(suffix='.jpg')
    output_path = tempfile.mktemp(suffix='.jpg')

    try:
        img.save(input_path, quality=95)

        # 裁剪到100,100位置，大小200x200
        success = processor.crop(input_path, output_path, x=100, y=100, width=200, height=200)
        assert success == True
        assert os.path.exists(output_path)

        # 验证尺寸
        cropped_img = Image.open(output_path)
        assert cropped_img.size == (200, 200)

        print("✅ 测试5通过: 裁剪正常")
        return True
    finally:
        for path in [input_path, output_path]:
            if os.path.exists(path):
                os.unlink(path)


def test_6_rotate():
    """测试6: 旋转"""
    print("\n测试6: 旋转")

    processor = ImageProcessor()

    # 创建测试图像
    from PIL import Image
    img = Image.new('RGB', (300, 200), color='purple')

    input_path = tempfile.mktemp(suffix='.jpg')
    output_path = tempfile.mktemp(suffix='.jpg')

    try:
        img.save(input_path, quality=95)

        # 旋转90度（expand=True扩展画布）
        success = processor.rotate(input_path, output_path, angle=90, expand=True)
        assert success == True, f"旋转失败: success={success}"
        assert os.path.exists(output_path), "输出文件不存在"

        # 验证旋转后的尺寸
        rotated_img = Image.open(output_path)
        actual_size = rotated_img.size
        expected_size = (200, 300)  # 90度旋转后尺寸互换
        assert actual_size == expected_size, f"旋转尺寸错误: 期望{expected_size}, 实际{actual_size}"

        print("✅ 测试6通过: 旋转正常")
        return True
    except Exception as e:
        print(f"❌ 测试6异常: {e}")
        raise
    finally:
        for path in [input_path, output_path]:
            if os.path.exists(path):
                os.unlink(path)


def test_7_watermark():
    """测试7: 添加水印"""
    print("\n测试7: 添加水印")

    processor = ImageProcessor()

    # 创建测试图像
    from PIL import Image
    img = Image.new('RGB', (800, 600), color='orange')

    input_path = tempfile.mktemp(suffix='.jpg')
    output_path = tempfile.mktemp(suffix='.jpg')

    try:
        img.save(input_path, quality=95)

        # 添加水印
        success = processor.add_watermark(
            input_path,
            output_path,
            watermark_text='© Test Watermark',
            position='bottom-right',
            font_size=48
        )
        assert success == True
        assert os.path.exists(output_path)

        # 验证图像存在
        watermarked_img = Image.open(output_path)
        assert watermarked_img.size == (800, 600)

        print("✅ 测试7通过: 添加水印正常")
        return True
    finally:
        for path in [input_path, output_path]:
            if os.path.exists(path):
                os.unlink(path)


def test_8_batch_convert():
    """测试8: 批量转换"""
    print("\n测试8: 批量转换")

    processor = ImageProcessor()

    # 创建测试目录和文件
    input_dir = tempfile.mkdtemp()
    output_dir = tempfile.mkdtemp()

    try:
        from PIL import Image

        # 创建多个测试文件
        for i in range(3):
            img = Image.new('RGB', (200, 200), color='rgb({},{},{})'.format(i*50, i*100, i*150))
            img.save(os.path.join(input_dir, f'img{i}.png'))

        # 批量转换
        results = processor.batch_convert(input_dir, output_dir, target_format='jpg', quality=90)

        assert len(results) == 3
        assert all(r['status'] == 'success' for r in results)

        # 验证输出文件
        output_files = os.listdir(output_dir)
        assert len(output_files) == 3
        assert all(f.endswith('.jpg') for f in output_files)

        print("✅ 测试8通过: 批量转换正常")
        return True
    finally:
        shutil.rmtree(input_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)


def test_9_batch_resize():
    """测试9: 批量调整大小"""
    print("\n测试9: 批量调整大小")

    processor = ImageProcessor()

    # 创建测试目录和文件
    input_dir = tempfile.mkdtemp()
    output_dir = tempfile.mkdtemp()

    try:
        from PIL import Image

        # 创建多个测试文件
        for i in range(3):
            img = Image.new('RGB', (800, 600), color='red')
            img.save(os.path.join(input_dir, f'img{i}.jpg'), quality=95)

        # 批量调整大小
        results = processor.batch_resize(input_dir, output_dir, width=400, maintain_aspect=True)

        assert len(results) == 3
        assert all(r['status'] == 'success' for r in results)

        # 验证输出文件尺寸
        for filename in os.listdir(output_dir):
            img = Image.open(os.path.join(output_dir, filename))
            assert img.size == (400, 300)  # 800x600保持宽高比

        print("✅ 测试9通过: 批量调整大小正常")
        return True
    finally:
        shutil.rmtree(input_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("Image Processor 测试套件")
    print("=" * 60)

    tests = [
        test_1_initialization,
        test_2_image_info,
        test_3_format_conversion,
        test_4_resize,
        test_5_crop,
        test_6_rotate,
        test_7_watermark,
        test_8_batch_convert,
        test_9_batch_resize
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"❌ 测试失败: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)

    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
