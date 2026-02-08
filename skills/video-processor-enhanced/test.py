#!/usr/bin/env python3
"""
视频处理增强器测试
"""

import os
import sys
import unittest
import tempfile
import subprocess
from pathlib import Path

# 添加技能目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from video_processor import VideoProcessor


class TestVideoProcessor(unittest.TestCase):
    """视频处理器测试"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.vp = VideoProcessor()
        cls.temp_dir = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        import shutil
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def setUp(self):
        """每个测试前执行"""
        self.test_dir = tempfile.mkdtemp(dir=self.temp_dir)
        self.test_video = self._create_test_video()
        self.assertTrue(os.path.exists(self.test_video))

    def tearDown(self):
        """每个测试后执行"""
        import shutil
        if hasattr(self, 'test_dir') and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_test_video(self, duration=5):
        """
        创建测试视频

        Args:
            duration: 视频时长（秒）

        Returns:
            测试视频路径
        """
        test_video = os.path.join(self.temp_dir, "test_video.mp4")

        if os.path.exists(test_video):
            return test_video

        # 使用ffmpeg创建测试视频
        cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", f"color=c=blue:s=320x240:d={duration}",
            "-f", "lavfi",
            "-i", f"sine=frequency=1000:duration={duration}",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-y",
            test_video
        ]

        result = subprocess.run(cmd, capture_output=True, timeout=30)

        if result.returncode != 0:
            self.skipTest("无法创建测试视频（需要ffmpeg）")

        return test_video

    def test_01_init(self):
        """测试1: 初始化"""
        vp = VideoProcessor()
        self.assertIsNotNone(vp)
        self.assertEqual(vp.ffmpeg_path, "ffmpeg")

    def test_02_get_video_info(self):
        """测试2: 获取视频信息"""
        info = self.vp.get_video_info(self.test_video)

        self.assertIsInstance(info, dict)
        self.assertIn("duration", info)
        self.assertIn("width", info)
        self.assertIn("height", info)
        self.assertIn("codec", info)
        self.assertGreater(info["duration"], 0)
        self.assertEqual(info["width"], 320)
        self.assertEqual(info["height"], 240)

    def test_03_convert_format_mp4_to_avi(self):
        """测试3: 格式转换 MP4 -> AVI"""
        output_file = os.path.join(self.test_dir, "output.avi")

        result = self.vp.convert_format(
            self.test_video,
            output_file,
            format="avi"
        )

        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_file))

    def test_04_clip_video(self):
        """测试4: 视频剪辑"""
        output_file = os.path.join(self.test_dir, "clip.mp4")

        result = self.vp.clip_video(
            self.test_video,
            output_file,
            start="0",
            end="2"
        )

        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_file))

    def test_05_compress_video(self):
        """测试5: 视频压缩"""
        output_file = os.path.join(self.test_dir, "compressed.mp4")

        # 获取原始文件大小
        original_size = os.path.getsize(self.test_video)

        result = self.vp.compress_video(
            self.test_video,
            output_file,
            quality=70
        )

        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_file))

        # 验证压缩效果
        compressed_size = os.path.getsize(output_file)
        self.assertLess(compressed_size, original_size * 1.5)  # 允许一定浮动

    def test_06_screenshot(self):
        """测试6: 视频截图"""
        output_file = os.path.join(self.test_dir, "screenshot.jpg")

        result = self.vp.screenshot(
            self.test_video,
            output_file,
            timestamp="00:00:01"
        )

        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_file))
        self.assertGreater(os.path.getsize(output_file), 0)

    def test_07_add_text_watermark(self):
        """测试7: 添加文字水印"""
        output_file = os.path.join(self.test_dir, "watermarked.mp4")

        result = self.vp.add_watermark(
            self.test_video,
            output_file,
            text="Test Watermark",
            position="bottom-right"
        )

        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_file))

    def test_08_extract_frames(self):
        """测试8: 提取视频帧"""
        output_dir = os.path.join(self.test_dir, "frames")

        result = self.vp.extract_frames(
            self.test_video,
            output_dir,
            interval=2
        )

        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_dir))

        # 验证至少提取了一帧
        frames = [f for f in os.listdir(output_dir) if f.endswith(".jpg")]
        self.assertGreater(len(frames), 0)

    def test_09_merge_videos(self):
        """测试9: 合并视频"""
        # 创建两个短视频
        video1 = self._create_test_video(duration=2)
        video2 = self._create_test_video(duration=2)

        output_file = os.path.join(self.test_dir, "merged.mp4")

        result = self.vp.merge_videos(
            [video1, video2],
            output_file
        )

        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_file))

    def test_10_quality_settings(self):
        """测试10: 质量设置"""
        # 高质量
        output_high = os.path.join(self.test_dir, "high_quality.mp4")
        self.vp.convert_format(self.test_video, output_high, quality=95)

        # 低质量
        output_low = os.path.join(self.test_dir, "low_quality.mp4")
        self.vp.convert_format(self.test_video, output_low, quality=50)

        # 验证文件大小差异
        size_high = os.path.getsize(output_high)
        size_low = os.path.getsize(output_low)

        self.assertGreater(size_high, size_low)

    def test_11_invalid_input(self):
        """测试11: 无效输入处理"""
        with self.assertRaises((FileNotFoundError, RuntimeError)):
            self.vp.get_video_info("nonexistent.mp4")

        with self.assertRaises(FileNotFoundError):
            self.vp.convert_format("nonexistent.mp4", "output.mp4")

    def test_12_batch_process_convert(self):
        """测试12: 批量处理 - 格式转换"""
        input_dir = os.path.join(self.test_dir, "input")
        output_dir = os.path.join(self.test_dir, "output")
        os.makedirs(input_dir)

        # 复制测试视频
        test_video = self._create_test_video(duration=2)
        import shutil
        shutil.copy(test_video, os.path.join(input_dir, "video1.mp4"))
        shutil.copy(test_video, os.path.join(input_dir, "video2.mp4"))

        results = self.vp.batch_process(
            input_dir,
            output_dir,
            "convert",
            format="avi"
        )

        self.assertEqual(len(results), 2)
        for input_file, output_file, success in results:
            self.assertTrue(success)
            self.assertTrue(os.path.exists(output_file))

    def test_13_batch_process_compress(self):
        """测试13: 批量处理 - 视频压缩"""
        input_dir = os.path.join(self.test_dir, "input_compress")
        output_dir = os.path.join(self.test_dir, "output_compress")
        os.makedirs(input_dir, exist_ok=True)

        # 复制测试视频
        test_video = self._create_test_video(duration=2)
        import shutil
        shutil.copy(test_video, os.path.join(input_dir, "video1.mp4"))
        shutil.copy(test_video, os.path.join(input_dir, "video2.mp4"))

        results = self.vp.batch_process(
            input_dir,
            output_dir,
            "compress",
            quality=70
        )

        self.assertEqual(len(results), 2)
        for input_file, output_file, success in results:
            self.assertTrue(success)
            self.assertTrue(os.path.exists(output_file))


def run_tests():
    """运行测试"""
    print("=" * 60)
    print("视频处理增强器 - 测试套件")
    print("=" * 60)

    # 创建测试套件
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestVideoProcessor)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 输出测试结果摘要
    print("\n" + "=" * 60)
    print(f"测试总数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("=" * 60)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
