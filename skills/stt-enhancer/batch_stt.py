#!/usr/bin/env python3
"""
批量语音识别工具
支持批量处理音频文件，生成转写文本
"""

import os
import sys
import argparse
import json
from pathlib import Path
from stt import STTEnhancer


class BatchSTT:
    """批量STT处理器"""

    # 支持的音频格式
    AUDIO_FORMATS = {".wav", ".mp3", ".flac", ".ogg", ".m4a", ".aac"}

    def __init__(self, model_size="base"):
        """
        初始化

        Args:
            model_size: 模型大小
        """
        print(f"初始化批量STT处理器 (模型: {model_size})...")
        self.enhancer = STTEnhancer(model_size=model_size)

    def find_audio_files(self, input_dir, recursive=False):
        """
        查找音频文件

        Args:
            input_dir: 输入目录
            recursive: 是否递归子目录

        Returns:
            音频文件列表
        """
        audio_files = []
        input_path = Path(input_dir)

        if not input_path.exists():
            raise FileNotFoundError(f"目录不存在: {input_dir}")

        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"

        for file_path in input_path.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in self.AUDIO_FORMATS:
                audio_files.append(file_path)

        audio_files.sort()
        return audio_files

    def process_batch(self, input_dir, output_dir, language=None,
                     recursive=False, format="txt", timestamps=False,
                     speakers=False):
        """
        批量处理音频文件

        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            language: 语言代码
            recursive: 是否递归子目录
            format: 输出格式
            timestamps: 是否包含时间戳
            speakers: 是否识别说话人

        Returns:
            处理统计
        """
        audio_files = self.find_audio_files(input_dir, recursive)

        if not audio_files:
            print(f"未找到音频文件: {input_dir}")
            return {
                "total": 0,
                "success": 0,
                "failed": 0,
                "results": []
            }

        print(f"\n找到 {len(audio_files)} 个音频文件\n")

        stats = {
            "total": len(audio_files),
            "success": 0,
            "failed": 0,
            "results": []
        }

        os.makedirs(output_dir, exist_ok=True)

        for i, audio_path in enumerate(audio_files, 1):
            print(f"\n[{i}/{len(audio_files)}] 处理: {audio_path.name}")

            try:
                # 转写
                transcript = self.enhancer.transcribe(
                    str(audio_path),
                    language=language,
                    timestamps=timestamps,
                    speakers=speakers
                )

                # 生成输出文件名
                output_name = audio_path.stem + f"_transcript.{format}"
                output_path = os.path.join(output_dir, output_name)

                # 保存
                self.enhancer.save_transcript(transcript, output_path, format=format)

                # 记录结果
                result = {
                    "input": str(audio_path),
                    "output": output_path,
                    "language": transcript["language"],
                    "length": len(transcript["text"]),
                    "segments": len(transcript["segments"])
                }

                stats["results"].append(result)
                stats["success"] += 1

                print(f"✓ 成功 ({transcript['language']}, {len(transcript['segments'])} 段落)")

            except Exception as e:
                print(f"✗ 失败: {e}")
                stats["failed"] += 1
                stats["results"].append({
                    "input": str(audio_path),
                    "output": None,
                    "error": str(e)
                })

        return stats

    def save_stats(self, stats, output_dir):
        """
        保存统计信息

        Args:
            stats: 统计信息
            output_dir: 输出目录
        """
        stats_path = os.path.join(output_dir, "batch_stats.json")
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)

        print(f"\n统计信息已保存: {stats_path}")

        return stats_path

    def print_summary(self, stats):
        """
        打印处理摘要

        Args:
            stats: 统计信息
        """
        print("\n" + "=" * 60)
        print("批量处理摘要")
        print("=" * 60)
        print(f"总文件数: {stats['total']}")
        print(f"成功: {stats['success']}")
        print(f"失败: {stats['failed']}")

        if stats["results"]:
            print("\n成功文件列表:")
            for result in stats["results"]:
                if result.get("output"):
                    print(f"  ✓ {result['input']} -> {result['output']}")
                else:
                    print(f"  ✗ {result['input']} (错误: {result.get('error', 'Unknown')})")


def main():
    parser = argparse.ArgumentParser(description="批量语音识别工具")
    parser.add_argument("--input-dir", required=True, help="输入音频目录")
    parser.add_argument("--output-dir", required=True, help="输出文本目录")
    parser.add_argument("--language", default=None, help="语言代码 (None=自动检测)")
    parser.add_argument("--model", default="base", choices=["tiny", "base", "small", "medium", "large"],
                       help="模型大小")
    parser.add_argument("--recursive", action="store_true", help="递归处理子目录")
    parser.add_argument("--format", default="txt", choices=["txt", "json", "srt"], help="输出格式")
    parser.add_argument("--timestamps", action="store_true", help="包含时间戳")
    parser.add_argument("--speakers", action="store_true", help="识别说话人")

    args = parser.parse_args()

    # 检查输入目录
    if not os.path.exists(args.input_dir):
        print(f"错误: 输入目录不存在: {args.input_dir}")
        sys.exit(1)

    # 初始化
    batch_stt = BatchSTT(model_size=args.model)

    # 处理
    stats = batch_stt.process_batch(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        language=args.language,
        recursive=args.recursive,
        format=args.format,
        timestamps=args.timestamps,
        speakers=args.speakers
    )

    # 保存统计
    batch_stt.save_stats(stats, args.output_dir)

    # 打印摘要
    batch_stt.print_summary(stats)


if __name__ == "__main__":
    main()
