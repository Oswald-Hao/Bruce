#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频剪辑与处理系统
Video Editor and Processing System

支持视频剪辑、转码、压缩、音频处理、水印添加等功能
"""

import subprocess
import os
import json
import sys
from pathlib import Path


class VideoEditor:
    """视频编辑器核心类"""

    def __init__(self, ffmpeg_path='ffmpeg'):
        self.ffmpeg_path = ffmpeg_path
        self.ffprobe_path = ffmpeg_path.replace('ffmpeg', 'ffprobe')
        self._check_ffmpeg()

    def _check_ffmpeg(self):
        """检查ffmpeg是否安装"""
        try:
            result = subprocess.run(
                [self.ffmpeg_path, '-version'],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                raise RuntimeError("ffmpeg未安装或不在PATH中")
        except FileNotFoundError:
            raise RuntimeError("ffmpeg未安装，请先安装ffmpeg")

    def _run_command(self, cmd, check=True):
        """执行shell命令"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=check
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return False, '', str(e)

    def get_video_info(self, input_path):
        """获取视频信息"""
        cmd = [
            self.ffprobe_path,
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            input_path
        ]

        success, stdout, stderr = self._run_command(cmd)
        if success:
            return json.loads(stdout)
        return None

    def clip_video(self, input_path, output_path, start_time, end_time):
        """剪辑视频片段"""
        cmd = [
            self.ffmpeg_path,
            '-i', input_path,
            '-ss', start_time,
            '-to', end_time,
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-y',
            output_path
        ]

        success, stdout, stderr = self._run_command(cmd)
        if success:
            return {'status': 'success', 'output': output_path}
        return {'status': 'error', 'message': stderr}

    def convert_format(self, input_path, output_path):
        """转换视频格式"""
        cmd = [
            self.ffmpeg_path,
            '-i', input_path,
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-movflags', '+faststart',
            '-y',
            output_path
        ]

        success, stdout, stderr = self._run_command(cmd)
        if success:
            return {'status': 'success', 'output': output_path}
        return {'status': 'error', 'message': stderr}

    def compress_video(self, input_path, output_path, quality='medium'):
        """压缩视频"""
        # quality参数：low, medium, high
        quality_map = {
            'low': '28',      # 最低质量
            'medium': '23',   # 中等质量
            'high': '18'      # 高质量
        }
        crf = quality_map.get(quality, '23')

        cmd = [
            self.ffmpeg_path,
            '-i', input_path,
            '-c:v', 'libx264',
            '-crf', crf,
            '-c:a', 'aac',
            '-b:a', '128k',
            '-y',
            output_path
        ]

        success, stdout, stderr = self._run_command(cmd)
        if success:
            return {'status': 'success', 'output': output_path}
        return {'status': 'error', 'message': stderr}

    def extract_audio(self, input_path, output_path):
        """提取音频"""
        cmd = [
            self.ffmpeg_path,
            '-i', input_path,
            '-vn',
            '-acodec', 'libmp3lame',
            '-ab', '192k',
            '-y',
            output_path
        ]

        success, stdout, stderr = self._run_command(cmd)
        if success:
            return {'status': 'success', 'output': output_path}
        return {'status': 'error', 'message': stderr}

    def replace_audio(self, input_video, input_audio, output_path):
        """替换视频音频"""
        cmd = [
            self.ffmpeg_path,
            '-i', input_video,
            '-i', input_audio,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-map', '0:v:0',
            '-map', '1:a:0',
            '-shortest',
            '-y',
            output_path
        ]

        success, stdout, stderr = self._run_command(cmd)
        if success:
            return {'status': 'success', 'output': output_path}
        return {'status': 'error', 'message': stderr}

    def add_watermark_text(self, input_path, output_path, text, position='bottom-right', opacity=0.7):
        """添加文字水印"""
        position_map = {
            'top-left': 'x=10:y=10',
            'top-right': 'x=w-tw-10:y=10',
            'bottom-left': 'x=10:y=h-th-10',
            'bottom-right': 'x=w-tw-10:y=h-th-10',
            'center': 'x=(w-tw)/2:y=(h-th)/2'
        }
        position_str = position_map.get(position, 'x=w-tw-10:y=h-th-10')

        # 设置透明度（需要先绘制半透明背景）
        cmd = [
            self.ffmpeg_path,
            '-i', input_path,
            '-vf',
            f"drawtext=text='{text}':fontsize=24:fontcolor=white@{opacity}:{position_str}",
            '-c:a', 'copy',
            '-y',
            output_path
        ]

        success, stdout, stderr = self._run_command(cmd)
        if success:
            return {'status': 'success', 'output': output_path}
        return {'status': 'error', 'message': stderr}

    def add_watermark_image(self, input_path, watermark_path, output_path, position='bottom-right', opacity=0.7):
        """添加图片水印"""
        position_map = {
            'top-left': '10:10',
            'top-right': 'W-w-10:10',
            'bottom-left': '10:H-h-10',
            'bottom-right': 'W-w-10:H-h-10',
            'center': '(W-w)/2:(H-h)/2'
        }
        position_str = position_map.get(position, 'W-w-10:H-h-10')

        cmd = [
            self.ffmpeg_path,
            '-i', input_path,
            '-i', watermark_path,
            '-filter_complex',
            f"[1]format=rgba,colorchannelmixer=aa={opacity}[wm];[0][wm]overlay={position_str}",
            '-c:a', 'copy',
            '-y',
            output_path
        ]

        success, stdout, stderr = self._run_command(cmd)
        if success:
            return {'status': 'success', 'output': output_path}
        return {'status': 'error', 'message': stderr}

    def add_subtitle(self, input_path, subtitle_path, output_path):
        """添加字幕"""
        cmd = [
            self.ffmpeg_path,
            '-i', input_path,
            '-vf',
            f"subtitles='{subtitle_path}'",
            '-c:a', 'copy',
            '-y',
            output_path
        ]

        success, stdout, stderr = self._run_command(cmd)
        if success:
            return {'status': 'success', 'output': output_path}
        return {'status': 'error', 'message': stderr}

    def merge_videos(self, input_paths, output_path):
        """合并多个视频"""
        # 创建临时文件列表
        list_file = '/tmp/video_list.txt'
        with open(list_file, 'w') as f:
            for path in input_paths:
                f.write(f"file '{os.path.abspath(path)}'\n")

        cmd = [
            self.ffmpeg_path,
            '-f', 'concat',
            '-safe', '0',
            '-i', list_file,
            '-c', 'copy',
            '-y',
            output_path
        ]

        success, stdout, stderr = self._run_command(cmd)

        # 清理临时文件
        if os.path.exists(list_file):
            os.remove(list_file)

        if success:
            return {'status': 'success', 'output': output_path}
        return {'status': 'error', 'message': stderr}

    def extract_frames(self, input_path, output_dir, fps=1, start_time=None, end_time=None):
        """提取视频帧"""
        os.makedirs(output_dir, exist_ok=True)

        cmd = [self.ffmpeg_path, '-i', input_path]

        if start_time:
            cmd.extend(['-ss', start_time])
        if end_time:
            cmd.extend(['-to', end_time])

        cmd.extend([
            '-vf', f'fps={fps}',
            os.path.join(output_dir, 'frame_%04d.jpg'),
            '-y'
        ])

        success, stdout, stderr = self._run_command(cmd)
        if success:
            return {'status': 'success', 'output_dir': output_dir, 'count': len(os.listdir(output_dir))}
        return {'status': 'error', 'message': stderr}


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description='视频剪辑与处理系统')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 剪辑命令
    clip_parser = subparsers.add_parser('clip', help='剪辑视频')
    clip_parser.add_argument('--input', required=True, help='输入视频文件')
    clip_parser.add_argument('--output', required=True, help='输出视频文件')
    clip_parser.add_argument('--start', required=True, help='开始时间 (HH:MM:SS)')
    clip_parser.add_argument('--end', required=True, help='结束时间 (HH:MM:SS)')

    # 转换命令
    convert_parser = subparsers.add_parser('convert', help='转换视频格式')
    convert_parser.add_argument('--input', required=True, help='输入视频文件')
    convert_parser.add_argument('--output', required=True, help='输出视频文件')

    # 压缩命令
    compress_parser = subparsers.add_parser('compress', help='压缩视频')
    compress_parser.add_argument('--input', required=True, help='输入视频文件')
    compress_parser.add_argument('--output', required=True, help='输出视频文件')
    compress_parser.add_argument('--quality', default='medium', choices=['low', 'medium', 'high'],
                                 help='压缩质量 (low/medium/high)')

    # 提取音频命令
    extract_audio_parser = subparsers.add_parser('extract-audio', help='提取音频')
    extract_audio_parser.add_argument('--input', required=True, help='输入视频文件')
    extract_audio_parser.add_argument('--output', required=True, help='输出音频文件')

    # 水印命令
    watermark_parser = subparsers.add_parser('watermark', help='添加水印')
    watermark_parser.add_argument('--input', required=True, help='输入视频文件')
    watermark_parser.add_argument('--output', required=True, help='输出视频文件')
    watermark_parser.add_argument('--text', help='水印文字')
    watermark_parser.add_argument('--image', help='水印图片')
    watermark_parser.add_argument('--position', default='bottom-right',
                                   choices=['top-left', 'top-right', 'bottom-left', 'bottom-right', 'center'],
                                   help='水印位置')
    watermark_parser.add_argument('--opacity', type=float, default=0.7, help='透明度 (0-1)')

    # 字幕命令
    subtitle_parser = subparsers.add_parser('subtitle', help='添加字幕')
    subtitle_parser.add_argument('--input', required=True, help='输入视频文件')
    subtitle_parser.add_argument('--output', required=True, help='输出视频文件')
    subtitle_parser.add_argument('--subtitle', required=True, help='字幕文件 (SRT)')

    # 合并命令
    merge_parser = subparsers.add_parser('merge', help='合并视频')
    merge_parser.add_argument('--inputs', required=True, nargs='+', help='输入视频文件列表')
    merge_parser.add_argument('--output', required=True, help='输出视频文件')

    # 提取帧命令
    frames_parser = subparsers.add_parser('frames', help='提取视频帧')
    frames_parser.add_argument('--input', required=True, help='输入视频文件')
    frames_parser.add_argument('--output-dir', required=True, help='输出目录')
    frames_parser.add_argument('--fps', type=int, default=1, help='每秒帧数')
    frames_parser.add_argument('--start', help='开始时间')
    frames_parser.add_argument('--end', help='结束时间')

    # 信息命令
    info_parser = subparsers.add_parser('info', help='获取视频信息')
    info_parser.add_argument('--input', required=True, help='输入视频文件')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    editor = VideoEditor()

    if args.command == 'clip':
        result = editor.clip_video(args.input, args.output, args.start, args.end)
    elif args.command == 'convert':
        result = editor.convert_format(args.input, args.output)
    elif args.command == 'compress':
        result = editor.compress_video(args.input, args.output, args.quality)
    elif args.command == 'extract-audio':
        result = editor.extract_audio(args.input, args.output)
    elif args.command == 'watermark':
        if args.text:
            result = editor.add_watermark_text(args.input, args.output, args.text, args.position, args.opacity)
        elif args.image:
            result = editor.add_watermark_image(args.input, args.image, args.output, args.position, args.opacity)
        else:
            print('错误：必须指定 --text 或 --image')
            return
    elif args.command == 'subtitle':
        result = editor.add_subtitle(args.input, args.subtitle, args.output)
    elif args.command == 'merge':
        result = editor.merge_videos(args.inputs, args.output)
    elif args.command == 'frames':
        result = editor.extract_frames(args.input, args.output_dir, args.fps, args.start, args.end)
    elif args.command == 'info':
        info = editor.get_video_info(args.input)
        if info:
            print(json.dumps(info, indent=2, ensure_ascii=False))
            return
        result = {'status': 'error', 'message': '无法获取视频信息'}

    if result['status'] == 'success':
        print(f'✓ {args.command} 成功')
        if 'output' in result:
            print(f'  输出: {result["output"]}')
    else:
        print(f'✗ {args.command} 失败: {result.get("message", "未知错误")}')


if __name__ == '__main__':
    main()
