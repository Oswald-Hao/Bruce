#!/usr/bin/env python3
"""
批量文本转语音工具
支持批量处理文本文件，生成音频
"""

import os
import sys
import argparse
from pathlib import Path


class BatchTTS:
    """批量TTS处理器"""

    # 支持的文本格式
    TEXT_FORMATS = {".txt", ".md", ".text"}

    def __init__(self, engine="system"):
        """
        初始化

        Args:
            engine: TTS引擎
        """
        from tts import TTSEnhancer
        print(f"初始化批量TTS处理器 (引擎: {engine})...")
        self.enhancer = TTSEnhancer(engine=engine)
        self.engine = engine

    def find_text_files(self, input_dir, recursive=False):
        """
        查找文本文件

        Args:
            input_dir: 输入目录
            recursive: 是否递归子目录

        Returns:
            文本文件列表
        """
        text_files = []
        input_path = Path(input_dir)

        if not input_path.exists():
            raise FileNotFoundError(f"目录不存在: {input_dir}")

        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"

        for file_path in input_path.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in self.TEXT_FORMATS:
                text_files.append(file_path)

        text_files.sort()
        return text_files

    def process_batch(self, input_dir, output_dir, voice=None,
                     recursive=False, format="wav", rate=1.0,
                     emotion="neutral"):
        """
        批量处理文本文件

        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            voice: 音色/语言代码
            recursive: 是否递归子目录
            format: 音频格式
            rate: 语速
            emotion: 情感

        Returns:
            处理统计
        """
        text_files = self.find_text_files(input_dir, recursive)

        if not text_files:
            print(f"未找到文本文件: {input_dir}")
            return {
                "total": 0,
                "success": 0,
                "failed": 0,
                "results": []
            }

        print(f"\n找到 {len(text_files)} 个文本文件\n")

        stats = {
            "total": len(text_files),
            "success": 0,
            "failed": 0,
            "results": []
        }

        os.makedirs(output_dir, exist_ok=True)

        import asyncio

        for i, text_path in enumerate(text_files, 1):
            print(f"\n[{i}/{len(text_files)}] 处理: {text_path.name}")

            try:
                # 读取文本
                with open(text_path, "r", encoding="utf-8") as f:
                    text = f.read().strip()

                if not text:
                    print("  跳过（空文件）")
                    continue

                # 生成输出文件名
                output_name = text_path.stem + f".{format}"
                output_path = os.path.join(output_dir, output_name)

                # 合成
                import asyncio

                if self.engine == "edge":
                    output = asyncio.run(self.enhancer.synthesize(
                        text,
                        voice=voice,
                        rate=rate,
                        emotion=emotion,
                        output=output_path
                    ))
                else:
                    output = self.enhancer.synthesize(
                        text,
                        voice=voice,
                        rate=rate,
                        emotion=emotion,
                        output=output_path
                    )

                # 记录结果
                result = {
                    "input": str(text_path),
                    "output": output_path,
                    "length": len(text),
                    "format": format
                }

                stats["results"].append(result)
                stats["success"] += 1

                print(f"✓ 成功 ({len(text)} 字符)")

            except Exception as e:
                print(f"✗ 失败: {e}")
                stats["failed"] += 1
                stats["results"].append({
                    "input": str(text_path),
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
        import json
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
    parser = argparse.ArgumentParser(description="批量文本转语音工具")
    parser.add_argument("--input-dir", required=True, help="输入文本目录")
    parser.add_argument("--output-dir", required=True, help="输出音频目录")
    parser.add_argument("--voice", help="音色/语言代码")
    parser.add_argument("--engine", default="system", choices=["system", "gtts", "edge", "azure"],
                       help="TTS引擎")
    parser.add_argument("--recursive", action="store_true", help="递归处理子目录")
    parser.add_argument("--format", default="wav", choices=["wav", "mp3", "ogg"], help="音频格式")
    parser.add_argument("--rate", type=float, default=1.0, help="语速（0.5-2.0）")
    parser.add_argument("--emotion", default="neutral",
                       choices=["happy", "sad", "angry", "surprised", "calm", "neutral"],
                       help="情感")

    args = parser.parse_args()

    # 检查输入目录
    if not os.path.exists(args.input_dir):
        print(f"错误: 输入目录不存在: {args.input_dir}")
        sys.exit(1)

    # 初始化
    batch_tts = BatchTTS(engine=args.engine)

    # 处理
    stats = batch_tts.process_batch(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        voice=args.voice,
        recursive=args.recursive,
        format=args.format,
        rate=args.rate,
        emotion=args.emotion
    )

    # 保存统计
    batch_tts.save_stats(stats, args.output_dir)

    # 打印摘要
    batch_tts.print_summary(stats)


if __name__ == "__main__":
    main()
