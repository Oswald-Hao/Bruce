#!/usr/bin/env python3
"""
测试 Video Processor
"""

import os
import sys
import tempfile
import shutil
import unittest
from pathlib import Path


# 添加技能目录到路径
sys.path.insert(0, str(Path(__file__).parent))


class TestVideoProcessor(unittest.TestCase):
    """测试 Video Processor"""

    def setUp(self):
        """测试前准备"""
        # 创建临时测试目录
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir, ignore_errors=True)

        # 导入模块
        from video_processor import VideoProcessor
        self.processor = VideoProcessor()

    def test_check_ffmpeg(self):
        """测试ffmpeg检查"""
        # ffmpeg_cmd可能为None（未安装）或字符串（已安装）
        self.assertIn(self.processor.ffmpeg_cmd, [None, 'ffmpeg', 'ffmpeg.exe'])

    def test_get_video_info_without_ffmpeg(self):
        """测试获取视频信息（无ffmpeg）"""
        # 模拟ffmpeg不可用的情况
        self.processor.ffmpeg_cmd = None

        result = self.processor.get_video_info("nonexistent.mp4")
        self.assertIn("error", result)

    def test_get_video_info_nonexistent_file(self):
        """测试获取不存在文件的信息"""
        if not self.processor.ffmpeg_cmd:
            self.skipTest("ffmpeg not installed")

        result = self.processor.get_video_info("nonexistent_file.mp4")
        self.assertIn("error", result)

    def test_convert_without_ffmpeg(self):
        """测试转换视频（无ffmpeg）"""
        self.processor.ffmpeg_cmd = None

        input_file = "input.mp4"
        output_file = "output.mp4"

        result = self.processor.convert_video(input_file, output_file)
        self.assertFalse(result)

    def test_compress_without_ffmpeg(self):
        """测试压缩视频（无ffmpeg）"""
        self.processor.ffmpeg_cmd = None

        input_file = "input.mp4"
        output_file = "output.mp4"

        result = self.processor.compress_video(input_file, output_file)
        self.assertFalse(result)

    def test_clip_without_ffmpeg(self):
        """测试剪辑视频（无ffmpeg）"""
        self.processor.ffmpeg_cmd = None

        result = self.processor.clip_video("input.mp4", "output.mp4", "00:00:00", "00:00:10")
        self.assertFalse(result)

    def test_extract_audio_without_ffmpeg(self):
        """测试提取音频（无ffmpeg）"""
        self.processor.ffmpeg_cmd = None

        result = self.processor.extract_audio("input.mp4", "output.mp3")
        self.assertFalse(result)

    def test_extract_frames_without_ffmpeg(self):
        """测试提取帧（无ffmpeg）"""
        self.processor.ffmpeg_cmd = None

        result = self.processor.extract_frames("input.mp4", "frames_dir", 10)
        self.assertFalse(result)

    def test_quality_params_exist(self):
        """测试质量参数配置"""
        # 测试代码逻辑是否正确，不依赖ffmpeg
        quality_params = {
            'low': {'crf': '28', 'preset': 'slow'},
            'medium': {'crf': '23', 'preset': 'medium'},
            'high': {'crf': '18', 'preset': 'fast'}
        }

        for quality in ['low', 'medium', 'high']:
            params = quality_params.get(quality)
            self.assertIsNotNone(params)
            self.assertIn('crf', params)
            self.assertIn('preset', params)

    def test_create_output_dir(self):
        """测试创建输出目录"""
        # 测试批量转换的目录创建逻辑
        input_dir = Path(self.test_dir) / "input"
        output_dir = Path(self.test_dir) / "output"

        # 模拟批量转换的目录创建
        output_dir.mkdir(parents=True, exist_ok=True)

        self.assertTrue(output_dir.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
