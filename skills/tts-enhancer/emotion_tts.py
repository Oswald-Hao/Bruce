#!/usr/bin/env python3
"""
情感语音合成工具
为文本添加情感表达，生成带情感的语音
"""

import os
import sys
import argparse
from tts import TTSEnhancer


class EmotionTTS:
    """情感TTS处理器"""

    # 情感类型及其参数
    EMOTIONS = {
        "happy": {
            "rate": 1.2,
            "pitch": 1.1,
            "volume": 1.0,
            "description": "快乐 - 语速稍快，音调稍高"
        },
        "sad": {
            "rate": 0.8,
            "pitch": 0.9,
            "volume": 0.9,
            "description": "悲伤 - 语速慢，音调低，音量小"
        },
        "angry": {
            "rate": 1.3,
            "pitch": 1.2,
            "volume": 1.0,
            "description": "愤怒 - 语速快，音调高"
        },
        "surprised": {
            "rate": 1.1,
            "pitch": 1.3,
            "volume": 1.0,
            "description": "惊讶 - 语速变化，音调起伏"
        },
        "calm": {
            "rate": 0.9,
            "pitch": 1.0,
            "volume": 0.9,
            "description": "平静 - 语速稍慢，音调正常"
        },
        "neutral": {
            "rate": 1.0,
            "pitch": 1.0,
            "volume": 1.0,
            "description": "中性 - 正常语速和音调"
        }
    }

    def __init__(self, engine="edge"):
        """
        初始化情感TTS

        Args:
            engine: TTS引擎（edge/azure支持情感）
        """
        self.enhancer = TTSEnhancer(engine=engine)
        self.engine = engine

        if engine not in ["edge", "azure"]:
            print("警告: 只有edge和azure引擎支持情感表达")

    def synthesize_with_emotion(self, text, emotion="neutral", voice=None, output=None):
        """
        带情感的语音合成

        Args:
            text: 要合成的文本
            emotion: 情感类型
            voice: 音色/语言代码
            output: 输出文件路径

        Returns:
            输出文件路径
        """
        if emotion not in self.EMOTIONS:
            raise ValueError(f"不支持的情感: {emotion}")

        emotion_params = self.EMOTIONS[emotion]

        print(f"\n情感: {emotion} - {emotion_params['description']}")

        import asyncio

        if self.engine == "edge":
            output = asyncio.run(self.enhancer.synthesize(
                text,
                voice=voice,
                rate=emotion_params["rate"],
                pitch=emotion_params["pitch"],
                volume=emotion_params["volume"],
                emotion=emotion,
                output=output
            ))
        else:
            output = self.enhancer.synthesize(
                text,
                voice=voice,
                rate=emotion_params["rate"],
                pitch=emotion_params["pitch"],
                volume=emotion_params["volume"],
                emotion=emotion,
                output=output
            )

        return output

    def batch_synthesize(self, text, emotions=None, voice=None, output_dir=None):
        """
        批量生成多种情感的语音

        Args:
            text: 文本
            emotions: 情感列表（None=全部）
            voice: 音色
            output_dir: 输出目录

        Returns:
            生成的文件列表
        """
        if emotions is None:
            emotions = list(self.EMOTIONS.keys())

        if output_dir is None:
            output_dir = tempfile.gettempdir()

        os.makedirs(output_dir, exist_ok=True)

        results = []

        for emotion in emotions:
            try:
                output = self.synthesize_with_emotion(
                    text,
                    emotion=emotion,
                    voice=voice
                )

                # 移动到指定目录
                if output:
                    final_output = os.path.join(output_dir, f"{emotion}_speech.mp3")
                    if os.path.exists(output):
                        os.rename(output, final_output)
                        results.append(final_output)

                print(f"✓ {emotion} 完成")

            except Exception as e:
                print(f"✗ {emotion} 失败: {e}")

        return results

    def list_emotions(self):
        """列出所有可用的情感"""
        print("\n可用的情感:")
        print("=" * 60)
        for name, params in self.EMOTIONS.items():
            print(f"{name:10} - {params['description']}")


def main():
    parser = argparse.ArgumentParser(description="情感语音合成工具")
    parser.add_argument("--text", required=True, help="要合成的文本")
    parser.add_argument("--emotion", default="neutral",
                       choices=["happy", "sad", "angry", "surprised", "calm", "neutral"],
                       help="情感")
    parser.add_argument("--voice", help="音色/语言代码")
    parser.add_argument("--engine", default="edge", choices=["system", "gtts", "edge", "azure"],
                       help="TTS引擎（edge/azure支持情感）")
    parser.add_argument("--output", help="输出音频文件")
    parser.add_argument("--output-dir", help="批量输出目录")
    parser.add_argument("--all-emotions", action="store_true", help="生成所有情感的语音")
    parser.add_argument("--list-emotions", action="store_true", help="列出所有情感")

    args = parser.parse_args()

    # 初始化
    emotion_tts = EmotionTTS(engine=args.engine)

    # 列出情感
    if args.list_emotions:
        emotion_tts.list_emotions()
        return

    # 批量生成所有情感
    if args.all_emotions:
        results = emotion_tts.batch_synthesize(
            args.text,
            voice=args.voice,
            output_dir=args.output_dir
        )
        print(f"\n生成了 {len(results)} 个音频文件:")
        for result in results:
            print(f"  - {result}")
        return

    # 单个情感合成
    output = emotion_tts.synthesize_with_emotion(
        args.text,
        emotion=args.emotion,
        voice=args.voice,
        output=args.output
    )

    if output:
        print(f"\n✓ 完成: {output}")


if __name__ == "__main__":
    import tempfile
    main()
