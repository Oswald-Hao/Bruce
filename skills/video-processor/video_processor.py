#!/usr/bin/env python3
"""
Video Processor - 视频处理工具
视频格式转换、剪辑、压缩、信息提取、关键帧提取
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List


class VideoProcessor:
    """视频处理器"""

    def __init__(self):
        self.ffmpeg_cmd = self._check_ffmpeg()

    def _check_ffmpeg(self) -> Optional[str]:
        """检查ffmpeg是否安装"""
        for cmd in ['ffmpeg', 'ffmpeg.exe']:
            try:
                result = subprocess.run(
                    [cmd, '-version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return cmd
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue

        print("⚠️  ffmpeg未安装，功能受限")
        print("   安装命令: sudo apt install ffmpeg")
        return None

    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """获取视频信息"""
        if not self.ffmpeg_cmd:
            return {"error": "ffmpeg not available"}

        try:
            # 使用ffprobe获取视频信息
            result = subprocess.run(
                ['ffprobe', '-v', 'quiet', '-print_format', 'json',
                 '-show_format', '-show_streams', video_path],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return {"error": f"Failed to analyze video: {result.stderr}"}

            data = json.loads(result.stdout)

            # 提取关键信息
            video_stream = None
            audio_stream = None

            for stream in data.get('streams', []):
                if stream['codec_type'] == 'video' and not video_stream:
                    video_stream = stream
                elif stream['codec_type'] == 'audio' and not audio_stream:
                    audio_stream = stream

            format_info = data.get('format', {})

            info = {
                "filename": Path(video_path).name,
                "format_name": format_info.get('format_name', 'unknown'),
                "duration": float(format_info.get('duration', 0)),
                "size": int(format_info.get('size', 0)),
                "bit_rate": int(format_info.get('bit_rate', 0)),
                "video": {},
                "audio": {}
            }

            if video_stream:
                info["video"] = {
                    "codec": video_stream.get('codec_name', 'unknown'),
                    "width": video_stream.get('width', 0),
                    "height": video_stream.get('height', 0),
                    "fps": eval(video_stream.get('r_frame_rate', '0/1')),
                    "bit_rate": int(video_stream.get('bit_rate', 0))
                }

            if audio_stream:
                info["audio"] = {
                    "codec": audio_stream.get('codec_name', 'unknown'),
                    "sample_rate": audio_stream.get('sample_rate', 0),
                    "channels": audio_stream.get('channels', 0)
                }

            return info

        except Exception as e:
            return {"error": str(e)}

    def convert_video(self,
                     input_file: str,
                     output_file: str,
                     format: str = 'mp4',
                     codec: str = 'libx264',
                     audio_codec: str = 'aac') -> bool:
        """视频格式转换"""
        if not self.ffmpeg_cmd:
            print("❌ ffmpeg不可用，无法转换")
            return False

        try:
            cmd = [
                self.ffmpeg_cmd,
                '-i', input_file,
                '-c:v', codec,
                '-c:a', audio_codec,
                '-y',  # 覆盖输出文件
                output_file
            ]

            print(f"🔄 转换视频: {Path(input_file).name} → {format.upper()}")
            subprocess.run(cmd, check=True, timeout=300)
            print(f"✅ 转换完成: {output_file}")
            return True

        except subprocess.TimeoutExpired:
            print("❌ 转换超时")
            return False
        except subprocess.CalledProcessError as e:
            print(f"❌ 转换失败: {e}")
            return False
        except Exception as e:
            print(f"❌ 转换出错: {e}")
            return False

    def compress_video(self,
                      input_file: str,
                      output_file: str,
                      quality: str = 'medium') -> bool:
        """视频压缩"""
        if not self.ffmpeg_cmd:
            print("❌ ffmpeg不可用，无法压缩")
            return False

        # 质量参数
        quality_params = {
            'low': {'crf': '28', 'preset': 'slow'},
            'medium': {'crf': '23', 'preset': 'medium'},
            'high': {'crf': '18', 'preset': 'fast'}
        }

        params = quality_params.get(quality, quality_params['medium'])

        try:
            cmd = [
                self.ffmpeg_cmd,
                '-i', input_file,
                '-c:v', 'libx264',
                '-crf', params['crf'],
                '-preset', params['preset'],
                '-c:a', 'aac',
                '-b:a', '128k',
                '-y',
                output_file
            ]

            print(f"🗜️  压缩视频 (质量: {quality}): {Path(input_file).name}")
            subprocess.run(cmd, check=True, timeout=300)

            # 计算压缩率
            input_size = Path(input_file).stat().st_size
            output_size = Path(output_file).stat().st_size
            ratio = (1 - output_size / input_size) * 100

            print(f"✅ 压缩完成: 压缩率 {ratio:.1f}%")
            print(f"   原大小: {input_size / 1024 / 1024:.2f} MB")
            print(f"   新大小: {output_size / 1024 / 1024:.2f} MB")
            return True

        except Exception as e:
            print(f"❌ 压缩失败: {e}")
            return False

    def clip_video(self,
                   input_file: str,
                   output_file: str,
                   start_time: str,
                   end_time: str) -> bool:
        """视频剪辑（提取片段）"""
        if not self.ffmpeg_cmd:
            print("❌ ffmpeg不可用，无法剪辑")
            return False

        try:
            cmd = [
                self.ffmpeg_cmd,
                '-i', input_file,
                '-ss', start_time,
                '-to', end_time,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-y',
                output_file
            ]

            print(f"✂️  剪辑视频: {start_time} → {end_time}")
            subprocess.run(cmd, check=True, timeout=300)
            print(f"✅ 剪辑完成: {output_file}")
            return True

        except Exception as e:
            print(f"❌ 剪辑失败: {e}")
            return False

    def extract_audio(self,
                      input_file: str,
                      output_file: str,
                      format: str = 'mp3') -> bool:
        """提取音频"""
        if not self.ffmpeg_cmd:
            print("❌ ffmpeg不可用，无法提取音频")
            return False

        try:
            cmd = [
                self.ffmpeg_cmd,
                '-i', input_file,
                '-vn',  # 不处理视频
                '-acodec', 'libmp3lame' if format == 'mp3' else 'aac',
                '-y',
                output_file
            ]

            print(f"🎵 提取音频: {Path(input_file).name}")
            subprocess.run(cmd, check=True, timeout=300)
            print(f"✅ 音频已提取: {output_file}")
            return True

        except Exception as e:
            print(f"❌ 提取失败: {e}")
            return False

    def extract_frames(self,
                       input_file: str,
                       output_dir: str,
                       count: int = 10) -> bool:
        """提取关键帧"""
        if not self.ffmpeg_cmd:
            print("❌ ffmpeg不可用，无法提取帧")
            return False

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            # 获取视频时长
            info = self.get_video_info(input_file)
            if 'error' in info:
                return False

            duration = info['duration']
            interval = duration / (count + 1)

            frames = []
            for i in range(1, count + 1):
                timestamp = i * interval
                output_file = output_dir / f"frame_{i:03d}.png"
                frames.append((timestamp, output_file))

            print(f"📸 提取 {count} 个关键帧...")

            for timestamp, output_file in frames:
                cmd = [
                    self.ffmpeg_cmd,
                    '-i', input_file,
                    '-ss', str(timestamp),
                    '-vframes', '1',
                    '-y',
                    str(output_file)
                ]
                subprocess.run(cmd, check=True, timeout=30, capture_output=True)

            print(f"✅ 关键帧已提取: {output_dir}")
            return True

        except Exception as e:
            print(f"❌ 提取帧失败: {e}")
            return False

    def batch_convert(self,
                     input_dir: str,
                     output_dir: str,
                     format: str = 'mp4') -> List[bool]:
        """批量转换视频"""
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.webm']
        results = []

        for video_file in input_dir.iterdir():
            if video_file.suffix.lower() in video_extensions:
                output_file = output_dir / f"{video_file.stem}.{format}"
                result = self.convert_video(str(video_file), str(output_file), format)
                results.append(result)

        return results


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="视频处理工具")
    parser.add_argument("--info", metavar="FILE", help="获取视频信息")
    parser.add_argument("--convert", metavar="FILE", help="转换视频格式")
    parser.add_argument("--compress", metavar="FILE", help="压缩视频")
    parser.add_argument("--clip", metavar="FILE", help="剪辑视频")
    parser.add_argument("--extract-audio", metavar="FILE", help="提取音频")
    parser.add_argument("--screenshot", metavar="FILE", help="提取关键帧")
    parser.add_argument("--output", metavar="FILE", help="输出文件")
    parser.add_argument("--format", default="mp4", help="输出格式")
    parser.add_argument("--quality", default="medium", help="压缩质量")
    parser.add_argument("--start", help="开始时间 (HH:MM:SS)")
    parser.add_argument("--end", help="结束时间 (HH:MM:SS)")
    parser.add_argument("--count", type=int, default=10, help="提取帧数量")

    args = parser.parse_args()

    processor = VideoProcessor()

    if args.info:
        info = processor.get_video_info(args.info)
        print(json.dumps(info, indent=2, ensure_ascii=False))

    elif args.convert:
        if not args.output:
            output_file = Path(args.convert).stem + "." + args.format
        else:
            output_file = args.output
        processor.convert_video(args.convert, output_file, args.format)

    elif args.compress:
        if not args.output:
            output_file = Path(args.compress).stem + "_compressed.mp4"
        else:
            output_file = args.output
        processor.compress_video(args.compress, output_file, args.quality)

    elif args.clip:
        if not args.output or not args.start or not args.end:
            print("❌ 剪辑需要 --output --start --end 参数")
        else:
            processor.clip_video(args.clip, args.output, args.start, args.end)

    elif args.extract_audio:
        if not args.output:
            output_file = Path(args.extract_audio).stem + ".mp3"
        else:
            output_file = args.output
        processor.extract_audio(args.extract_audio, output_file)

    elif args.screenshot:
        if not args.output:
            args.output = Path(args.screenshot).stem + "_frames"
        processor.extract_frames(args.screenshot, args.output, args.count)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
