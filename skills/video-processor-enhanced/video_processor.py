#!/usr/bin/env python3
"""
视频处理增强器
基于ffmpeg的全面视频处理工具
"""

import os
import subprocess
import json
import re
from pathlib import Path
from typing import Dict, Optional, Tuple
import tempfile


class VideoProcessor:
    """视频处理器"""

    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        """
        初始化视频处理器

        Args:
            ffmpeg_path: ffmpeg可执行文件路径
        """
        self.ffmpeg_path = ffmpeg_path
        self.ffprobe_path = ffmpeg_path.replace("ffmpeg", "ffprobe")
        self._check_ffmpeg()

    def _check_ffmpeg(self):
        """检查ffmpeg是否安装"""
        try:
            result = subprocess.run(
                [self.ffmpeg_path, "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                raise RuntimeError("ffmpeg未安装或不在PATH中")
        except FileNotFoundError:
            raise RuntimeError("ffmpeg未安装，请使用: sudo apt-get install ffmpeg")

    def _run_command(self, cmd: list, timeout: int = 3600) -> Tuple[bool, str]:
        """
        执行命令

        Args:
            cmd: 命令列表
            timeout: 超时时间（秒）

        Returns:
            (是否成功, 输出或错误信息)
        """
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr
        except subprocess.TimeoutExpired:
            return False, f"命令执行超时（{timeout}秒）"
        except Exception as e:
            return False, str(e)

    def get_video_info(self, input_file: str) -> Dict:
        """
        获取视频信息

        Args:
            input_file: 输入视频文件路径

        Returns:
            视频信息字典
        """
        cmd = [
            self.ffprobe_path,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            input_file
        ]

        success, output = self._run_command(cmd, timeout=30)

        if not success:
            raise RuntimeError(f"获取视频信息失败: {output}")

        data = json.loads(output)

        # 提取视频流信息
        video_stream = None
        audio_stream = None

        for stream in data.get("streams", []):
            if stream["codec_type"] == "video" and video_stream is None:
                video_stream = stream
            elif stream["codec_type"] == "audio" and audio_stream is None:
                audio_stream = stream

        format_info = data.get("format", {})

        info = {
            "filename": format_info.get("filename", input_file),
            "format": format_info.get("format_name", "unknown"),
            "duration": float(format_info.get("duration", 0)),
            "size": int(format_info.get("size", 0)),
            "bit_rate": int(format_info.get("bit_rate", 0)),
        }

        if video_stream:
            info.update({
                "width": video_stream.get("width"),
                "height": video_stream.get("height"),
                "codec": video_stream.get("codec_name"),
                "fps": eval(video_stream.get("r_frame_rate", "0/1")),
                "pixel_format": video_stream.get("pix_fmt"),
            })

        if audio_stream:
            info.update({
                "audio_codec": audio_stream.get("codec_name"),
                "sample_rate": audio_stream.get("sample_rate"),
                "channels": audio_stream.get("channels"),
            })

        return info

    def convert_format(
        self,
        input_file: str,
        output_file: str,
        format: str = "mp4",
        quality: int = 90,
        video_codec: Optional[str] = None,
        audio_codec: Optional[str] = None,
        overwrite: bool = True
    ) -> bool:
        """
        转换视频格式

        Args:
            input_file: 输入文件
            output_file: 输出文件
            format: 目标格式（mp4, avi, mov, mkv等）
            quality: 质量（1-100）
            video_codec: 视频编码器（自动选择）
            audio_codec: 音频编码器（自动选择）
            overwrite: 是否覆盖已存在文件

        Returns:
            是否成功
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"输入文件不存在: {input_file}")

        # 自动选择编码器
        if video_codec is None:
            codec_map = {
                "mp4": "libx264",
                "avi": "mpeg4",
                "mov": "libx264",
                "mkv": "libx264",
                "flv": "flv",
                "webm": "libvpx-vp9",
            }
            video_codec = codec_map.get(format.lower(), "libx264")

        if audio_codec is None:
            audio_codec = "aac"

        cmd = [self.ffmpeg_path]

        if overwrite:
            cmd.append("-y")

        cmd.extend(["-i", input_file])

        # 视频编码参数
        crf = (100 - quality) // 2  # 质量转CRF值（0-51）
        cmd.extend([
            "-c:v", video_codec,
            "-crf", str(crf),
            "-preset", "medium",
            "-c:a", audio_codec,
            "-b:a", "192k",
        ])

        cmd.append(output_file)

        success, output = self._run_command(cmd, timeout=3600)

        if not success:
            raise RuntimeError(f"格式转换失败: {output}")

        return True

    def clip_video(
        self,
        input_file: str,
        output_file: str,
        start: str,
        end: str,
        overwrite: bool = True
    ) -> bool:
        """
        剪辑视频片段

        Args:
            input_file: 输入文件
            output_file: 输出文件
            start: 开始时间（HH:MM:SS或秒数）
            end: 结束时间（HH:MM:SS或秒数）
            overwrite: 是否覆盖已存在文件

        Returns:
            是否成功
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"输入文件不存在: {input_file}")

        cmd = [self.ffmpeg_path]

        if overwrite:
            cmd.append("-y")

        cmd.extend([
            "-ss", str(start),
            "-to", str(end),
            "-i", input_file,
            "-c", "copy",  # 无损剪辑
            output_file
        ])

        success, output = self._run_command(cmd, timeout=3600)

        if not success:
            raise RuntimeError(f"视频剪辑失败: {output}")

        return True

    def compress_video(
        self,
        input_file: str,
        output_file: str,
        quality: int = 80,
        resolution: Optional[str] = None,
        overwrite: bool = True
    ) -> bool:
        """
        压缩视频

        Args:
            input_file: 输入文件
            output_file: 输出文件
            quality: 质量（1-100，80为平衡质量）
            resolution: 分辨率（如1280x720）
            overwrite: 是否覆盖已存在文件

        Returns:
            是否成功
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"输入文件不存在: {input_file}")

        cmd = [self.ffmpeg_path]

        if overwrite:
            cmd.append("-y")

        cmd.extend(["-i", input_file])

        # 质量参数
        crf = (100 - quality) // 2
        cmd.extend([
            "-c:v", "libx264",
            "-crf", str(crf),
            "-preset", "medium",
            "-c:a", "aac",
            "-b:a", "128k",
        ])

        # 分辨率调整
        if resolution:
            cmd.extend(["-vf", f"scale={resolution}"])

        cmd.append(output_file)

        success, output = self._run_command(cmd, timeout=3600)

        if not success:
            raise RuntimeError(f"视频压缩失败: {output}")

        return True

    def extract_frames(
        self,
        input_file: str,
        output_dir: str,
        interval: int = 5,
        format: str = "jpg",
        quality: int = 90,
        overwrite: bool = True
    ) -> bool:
        """
        提取视频帧

        Args:
            input_file: 输入文件
            output_dir: 输出目录
            interval: 提取间隔（秒）
            format: 输出格式（jpg, png）
            quality: 图片质量（1-100）
            overwrite: 是否覆盖已存在文件

        Returns:
            是否成功
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"输入文件不存在: {input_file}")

        os.makedirs(output_dir, exist_ok=True)

        cmd = [self.ffmpeg_path]

        if overwrite:
            cmd.append("-y")

        cmd.extend([
            "-i", input_file,
            "-vf", f"fps=1/{interval}",
            "-q:v", str((100 - quality) // 2),
            os.path.join(output_dir, f"frame_%04d.{format}")
        ])

        success, output = self._run_command(cmd, timeout=3600)

        if not success:
            raise RuntimeError(f"提取帧失败: {output}")

        return True

    def screenshot(
        self,
        input_file: str,
        output_file: str,
        timestamp: str = "00:00:05",
        width: Optional[int] = None,
        overwrite: bool = True
    ) -> bool:
        """
        截取视频截图

        Args:
            input_file: 输入文件
            output_file: 输出文件
            timestamp: 截图时间点（HH:MM:SS）
            width: 截图宽度（自动计算高度）
            overwrite: 是否覆盖已存在文件

        Returns:
            是否成功
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"输入文件不存在: {input_file}")

        cmd = [self.ffmpeg_path]

        if overwrite:
            cmd.append("-y")

        cmd.extend([
            "-ss", timestamp,
            "-i", input_file,
            "-vframes", "1",
        ])

        if width:
            cmd.extend(["-vf", f"scale={width}:-1"])

        cmd.append(output_file)

        success, output = self._run_command(cmd, timeout=30)

        if not success:
            raise RuntimeError(f"截图失败: {output}")

        return True

    def add_watermark(
        self,
        input_file: str,
        output_file: str,
        text: Optional[str] = None,
        image: Optional[str] = None,
        position: str = "bottom-right",
        opacity: float = 0.7,
        fontsize: int = 24,
        overwrite: bool = True
    ) -> bool:
        """
        添加水印

        Args:
            input_file: 输入文件
            output_file: 输出文件
            text: 文字水印内容
            image: 图片水印路径
            position: 水印位置（top-left, top-right, bottom-left, bottom-right, center）
            opacity: 不透明度（0-1）
            fontsize: 字体大小
            overwrite: 是否覆盖已存在文件

        Returns:
            是否成功
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"输入文件不存在: {input_file}")

        if not text and not image:
            raise ValueError("必须提供文字水印或图片水印")

        if text and image:
            raise ValueError("只能使用一种水印类型（文字或图片）")

        cmd = [self.ffmpeg_path]

        if overwrite:
            cmd.append("-y")

        cmd.extend(["-i", input_file])

        if text:
            # 文字水印
            position_map = {
                "top-left": "(x=w-tw-10:y=h-th-10)",
                "top-right": "(x=w-tw-10:y=10)",
                "bottom-left": "(x=10:y=h-th-10)",
                "bottom-right": "(x=w-tw-10:y=h-th-10)",
                "center": "(x=(w-tw)/2:y=(h-th)/2)",
            }

            pos = position_map.get(position, position_map["bottom-right"])
            drawtext = (
                f"drawtext=text='{text}':fontsize={fontsize}:"
                f"fontcolor=white@{opacity}:{pos}"
            )

            cmd.extend(["-vf", drawtext])

        elif image:
            # 图片水印
            if not os.path.exists(image):
                raise FileNotFoundError(f"水印图片不存在: {image}")

            cmd.extend(["-i", image])

            position_map = {
                "top-left": "10:10",
                "top-right": "W-w-10:10",
                "bottom-left": "10:H-h-10",
                "bottom-right": "W-w-10:H-h-10",
                "center": "(W-w)/2:(H-h)/2",
            }

            pos = position_map.get(position, position_map["bottom-right"])
            overlay = f"overlay={pos}"

            cmd.extend([
                "-filter_complex",
                f"[1:v]format=rgba,colorchannelmixer=aa={opacity}[watermark];[0:v][watermark]{overlay}"
            ])

        cmd.extend([
            "-c:a", "copy",
            output_file
        ])

        success, output = self._run_command(cmd, timeout=3600)

        if not success:
            raise RuntimeError(f"添加水印失败: {output}")

        return True

    def merge_videos(
        self,
        input_files: list,
        output_file: str,
        overwrite: bool = True
    ) -> bool:
        """
        合并视频

        Args:
            input_files: 输入文件列表
            output_file: 输出文件
            overwrite: 是否覆盖已存在文件

        Returns:
            是否成功
        """
        for f in input_files:
            if not os.path.exists(f):
                raise FileNotFoundError(f"输入文件不存在: {f}")

        # 创建文件列表
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tf:
            for f in input_files:
                tf.write(f"file '{os.path.abspath(f)}'\n")
            list_file = tf.name

        try:
            cmd = [self.ffmpeg_path]

            if overwrite:
                cmd.append("-y")

            cmd.extend([
                "-f", "concat",
                "-safe", "0",
                "-i", list_file,
                "-c", "copy",
                output_file
            ])

            success, output = self._run_command(cmd, timeout=3600)

            if not success:
                raise RuntimeError(f"合并视频失败: {output}")

            return True

        finally:
            os.remove(list_file)

    def batch_process(
        self,
        input_dir: str,
        output_dir: str,
        operation: str,
        **kwargs
    ) -> list:
        """
        批量处理视频

        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            operation: 操作类型（convert, compress, extract_frames）
            **kwargs: 操作参数

        Returns:
            处理结果列表
        """
        os.makedirs(output_dir, exist_ok=True)

        video_extensions = [".mp4", ".avi", ".mov", ".mkv", ".flv", ".webm"]
        video_files = []

        for file in os.listdir(input_dir):
            if any(file.lower().endswith(ext) for ext in video_extensions):
                video_files.append(os.path.join(input_dir, file))

        results = []

        for video_file in video_files:
            filename = os.path.basename(video_file)
            name, ext = os.path.splitext(filename)

            try:
                if operation == "convert":
                    output_format = kwargs.get("format", "mp4")
                    output_file = os.path.join(output_dir, f"{name}.{output_format}")
                    self.convert_format(video_file, output_file, **kwargs)
                    results.append((video_file, output_file, True))

                elif operation == "compress":
                    output_file = os.path.join(output_dir, f"{name}_compressed{ext}")
                    self.compress_video(video_file, output_file, **kwargs)
                    results.append((video_file, output_file, True))

                elif operation == "extract_frames":
                    frame_dir = os.path.join(output_dir, name)
                    self.extract_frames(video_file, frame_dir, **kwargs)
                    results.append((video_file, frame_dir, True))

                else:
                    results.append((video_file, None, False))

            except Exception as e:
                results.append((video_file, str(e), False))

        return results


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="视频处理增强器")
    subparsers = parser.add_subparsers(dest="command", help="命令")

    # info命令
    info_parser = subparsers.add_parser("info", help="获取视频信息")
    info_parser.add_argument("input", help="输入视频文件")

    # convert命令
    convert_parser = subparsers.add_parser("convert", help="转换视频格式")
    convert_parser.add_argument("input", help="输入视频文件")
    convert_parser.add_argument("output", help="输出视频文件")
    convert_parser.add_argument("--format", default="mp4", help="目标格式")
    convert_parser.add_argument("--quality", type=int, default=90, help="质量（1-100）")

    # clip命令
    clip_parser = subparsers.add_parser("clip", help="剪辑视频")
    clip_parser.add_argument("input", help="输入视频文件")
    clip_parser.add_argument("output", help="输出视频文件")
    clip_parser.add_argument("start", help="开始时间（秒或HH:MM:SS）")
    clip_parser.add_argument("end", help="结束时间（秒或HH:MM:SS）")

    # compress命令
    compress_parser = subparsers.add_parser("compress", help="压缩视频")
    compress_parser.add_argument("input", help="输入视频文件")
    compress_parser.add_argument("output", help="输出视频文件")
    compress_parser.add_argument("--quality", type=int, default=80, help="质量（1-100）")
    compress_parser.add_argument("--resolution", help="分辨率（如1280x720）")

    # screenshot命令
    screenshot_parser = subparsers.add_parser("screenshot", help="截取视频截图")
    screenshot_parser.add_argument("input", help="输入视频文件")
    screenshot_parser.add_argument("output", help="输出图片文件")
    screenshot_parser.add_argument("--timestamp", default="00:00:05", help="截图时间点")

    # extract命令
    extract_parser = subparsers.add_parser("extract", help="提取视频帧")
    extract_parser.add_argument("input", help="输入视频文件")
    extract_parser.add_argument("output_dir", help="输出目录")
    extract_parser.add_argument("--interval", type=int, default=5, help="提取间隔（秒）")

    # watermark命令
    watermark_parser = subparsers.add_parser("watermark", help="添加水印")
    watermark_parser.add_argument("input", help="输入视频文件")
    watermark_parser.add_argument("output", help="输出视频文件")
    watermark_parser.add_argument("--text", help="文字水印")
    watermark_parser.add_argument("--image", help="图片水印")
    watermark_parser.add_argument("--position", default="bottom-right", help="水印位置")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    vp = VideoProcessor()

    try:
        if args.command == "info":
            info = vp.get_video_info(args.input)
            print(json.dumps(info, indent=2, ensure_ascii=False))

        elif args.command == "convert":
            vp.convert_format(
                args.input, args.output,
                format=args.format,
                quality=args.quality
            )
            print(f"✓ 格式转换成功: {args.output}")

        elif args.command == "clip":
            vp.clip_video(args.input, args.output, args.start, args.end)
            print(f"✓ 视频剪辑成功: {args.output}")

        elif args.command == "compress":
            vp.compress_video(
                args.input, args.output,
                quality=args.quality,
                resolution=args.resolution
            )
            print(f"✓ 视频压缩成功: {args.output}")

        elif args.command == "screenshot":
            vp.screenshot(args.input, args.output, timestamp=args.timestamp)
            print(f"✓ 截图成功: {args.output}")

        elif args.command == "extract":
            vp.extract_frames(args.input, args.output_dir, interval=args.interval)
            print(f"✓ 帧提取成功: {args.output_dir}")

        elif args.command == "watermark":
            vp.add_watermark(
                args.input, args.output,
                text=args.text,
                image=args.image,
                position=args.position
            )
            print(f"✓ 添加水印成功: {args.output}")

    except Exception as e:
        print(f"✗ 错误: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
