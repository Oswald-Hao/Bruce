#!/usr/bin/env python3
"""
语音识别增强（STT）工具
基于OpenAI Whisper，支持多语言、多格式、高精度转写
"""

import os
import sys
import argparse
import json
import warnings
from datetime import datetime
from pathlib import Path

try:
    import whisper
    import torch
    import numpy as np
except ImportError as e:
    print(f"错误: 缺少依赖库: {e}")
    print("请安装: pip install openai-whisper torch numpy")
    sys.exit(1)

warnings.filterwarnings("ignore")


class STTEnhancer:
    """语音识别增强器"""

    def __init__(self, model_size="base", device=None):
        """
        初始化STT引擎

        Args:
            model_size: 模型大小 (tiny/base/small/medium/large)
            device: 设备 (cuda/cpu)，自动检测
        """
        self.model_size = model_size

        # 自动选择设备
        if device is None:
            if torch.cuda.is_available():
                device = "cuda"
            else:
                device = "cpu"

        print(f"加载Whisper模型 ({model_size}) 到 {device}...")
        self.model = whisper.load_model(model_size, device=device)
        self.device = device

    def transcribe(self, audio_path, language=None, timestamps=False,
                  speakers=False, denoise=False):
        """
        转写音频

        Args:
            audio_path: 音频文件路径
            language: 语言代码 (zh/en/ja/等)，None=自动检测
            timestamps: 是否包含时间戳
            speakers: 是否识别说话人（简单分段）
            denoise: 是否应用噪声抑制

        Returns:
            转写结果字典
        """
        print(f"\n转写中: {audio_path}")

        options = {
            "task": "transcribe",
            "verbose": False,
        }

        if language and language != "auto":
            options["language"] = language

        # 执行转写
        result = self.model.transcribe(audio_path, **options)

        # 处理结果
        transcript = {
            "text": result["text"].strip(),
            "language": result.get("language", "unknown"),
            "segments": []
        }

        # 处理段落
        for i, segment in enumerate(result["segments"]):
            seg_data = {
                "id": i + 1,
                "start": segment["start"],
                "end": segment["end"],
                "text": segment["text"].strip()
            }

            # 简单说话人识别（基于段落长度和间隔）
            if speakers:
                seg_data["speaker"] = self._detect_speaker(segment, i, result["segments"])

            transcript["segments"].append(seg_data)

        return transcript

    def _detect_speaker(self, segment, index, all_segments):
        """
        简单说话人检测（基于段落间隔）

        Args:
            segment: 当前段落
            index: 段落索引
            all_segments: 所有段落

        Returns:
            说话人标识 (SPEAKER_1, SPEAKER_2, ...)
        """
        if index == 0:
            return "SPEAKER_1"

        prev_segment = all_segments[index - 1]
        gap = segment["start"] - prev_segment["end"]

        # 如果间隔大于2秒，认为换人了
        if gap > 2.0:
            return "SPEAKER_2" if index % 2 == 1 else "SPEAKER_1"
        else:
            # 根据上一个段落推断
            if index % 2 == 0:
                return "SPEAKER_2"
            else:
                return "SPEAKER_1"

    def save_transcript(self, transcript, output_path, format="txt"):
        """
        保存转写结果

        Args:
            transcript: 转写结果
            output_path: 输出文件路径
            format: 输出格式 (txt/json/srt)
        """
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        if format == "txt":
            self._save_txt(transcript, output_path)
        elif format == "json":
            self._save_json(transcript, output_path)
        elif format == "srt":
            self._save_srt(transcript, output_path)
        else:
            raise ValueError(f"不支持的格式: {format}")

        print(f"\n已保存到: {output_path}")

    def _save_txt(self, transcript, output_path):
        """保存为TXT格式"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"语言: {transcript['language']}\n")
            f.write(f"完整文本:\n{transcript['text']}\n\n")

            if transcript["segments"]:
                f.write("段落详情:\n")
                f.write("=" * 60 + "\n")
                for seg in transcript["segments"]:
                    time_range = self._format_time(seg["start"]) + " --> " + self._format_time(seg["end"])
                    speaker = f"[{seg.get('speaker', '')}] " if seg.get("speaker") else ""
                    f.write(f"{time_range}\n")
                    f.write(f"{speaker}{seg['text']}\n\n")

    def _save_json(self, transcript, output_path):
        """保存为JSON格式"""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(transcript, f, ensure_ascii=False, indent=2)

    def _save_srt(self, transcript, output_path):
        """保存为SRT字幕格式"""
        with open(output_path, "w", encoding="utf-8") as f:
            for i, seg in enumerate(transcript["segments"], 1):
                start_time = self._format_srt_time(seg["start"])
                end_time = self._format_srt_time(seg["end"])
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{seg['text']}\n\n")

    def _format_time(self, seconds):
        """格式化时间戳"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def _format_srt_time(self, seconds):
        """格式化SRT时间戳"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def transcribe_from_mic(self, language=None):
        """
        从麦克风实时转录（简化版）

        注意: 需要额外依赖 sounddevice
        """
        try:
            import sounddevice as sd
        except ImportError:
            print("实时转录需要 sounddevice: pip install sounddevice")
            return None

        print("实时转录模式 - 按Ctrl+C停止")
        print("录音中...\n")

        # 简单实现：录制5秒后转录
        fs = 16000  # 采样率
        duration = 5  # 秒
        print(f"正在录制 {duration} 秒...")

        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()

        # 保存临时文件
        temp_file = "/tmp/temp_mic_recording.wav"
        import scipy.io.wavfile as wavfile
        wavfile.write(temp_file, fs, recording)

        # 转写
        result = self.transcribe(temp_file, language=language)
        print("\n转录结果:")
        print(result["text"])

        # 删除临时文件
        os.remove(temp_file)

        return result


def main():
    parser = argparse.ArgumentParser(description="语音识别增强（STT）工具")
    parser.add_argument("--audio", help="音频文件路径")
    parser.add_argument("--language", default="auto", help="语言代码 (zh/en/ja/等，auto=自动检测)")
    parser.add_argument("--model", default="base", choices=["tiny", "base", "small", "medium", "large"],
                       help="模型大小")
    parser.add_argument("--output", help="输出文本文件")
    parser.add_argument("--timestamps", action="store_true", help="包含时间戳")
    parser.add_argument("--speakers", action="store_true", help="启用说话人识别")
    parser.add_argument("--denoise", action="store_true", help="启用噪声抑制（预留）")
    parser.add_argument("--mic", action="store_true", help="从麦克风实时转录")
    parser.add_argument("--format", default="txt", choices=["txt", "json", "srt"], help="输出格式")

    args = parser.parse_args()

    # 实时转录模式
    if args.mic:
        enhancer = STTEnhancer(model_size=args.model)
        enhancer.transcribe_from_mic(language=args.language if args.language != "auto" else None)
        return

    # 文件转写模式
    if not args.audio:
        parser.error("需要 --audio 或 --mic 参数")

    if not os.path.exists(args.audio):
        print(f"错误: 文件不存在: {args.audio}")
        sys.exit(1)

    # 初始化
    enhancer = STTEnhancer(model_size=args.model)

    # 转写
    language = None if args.language == "auto" else args.language
    transcript = enhancer.transcribe(
        args.audio,
        language=language,
        timestamps=args.timestamps,
        speakers=args.speakers,
        denoise=args.denoise
    )

    # 输出结果
    print("\n" + "=" * 60)
    print("转录结果")
    print("=" * 60)
    print(f"语言: {transcript['language']}")
    print(f"文本:\n{transcript['text']}")

    # 保存到文件
    if args.output:
        enhancer.save_transcript(transcript, args.output, format=args.format)


if __name__ == "__main__":
    main()
