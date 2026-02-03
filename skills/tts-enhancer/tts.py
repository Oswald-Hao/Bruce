#!/usr/bin/env python3
"""
TTS语音扩展工具
支持多种TTS引擎，提供多音色、多语言和情感表达
"""

import os
import sys
import argparse
import tempfile
import subprocess


class TTSEnhancer:
    """TTS语音合成增强器"""

    def __init__(self, engine="system"):
        """
        初始化TTS引擎

        Args:
            engine: TTS引擎 (system/gtts/edge/azure)
        """
        self.engine = engine
        self._initialize_engine()

    def _initialize_engine(self):
        """初始化指定的TTS引擎"""
        if self.engine == "system":
            self._init_system_tts()
        elif self.engine == "gtts":
            self._init_gtts()
        elif self.engine == "edge":
            self._init_edge_tts()
        elif self.engine == "azure":
            self._init_azure_tts()
        else:
            raise ValueError(f"不支持的引擎: {self.engine}")

    def _init_system_tts(self):
        """初始化系统TTS（pyttsx3）"""
        try:
            import pyttsx3
            self.pyttsx3 = pyttsx3
            self.engine_name = "System TTS (pyttsx3)"
        except ImportError:
            raise ImportError("pyttsx3未安装，请运行: pip install pyttsx3")

    def _init_gtts(self):
        """初始化gTTS"""
        try:
            from gtts import gTTS
            self.gTTS = gTTS
            self.engine_name = "Google TTS"
        except ImportError:
            raise ImportError("gtts未安装，请运行: pip install gtts")

    def _init_edge_tts(self):
        """初始化Edge-TTS"""
        try:
            import edge_tts
            self.edge_tts = edge_tts
            self.engine_name = "Edge TTS"
        except ImportError:
            raise ImportError("edge-tts未安装，请运行: pip install edge-tts")

    def _init_azure_tts(self):
        """初始化Azure TTS"""
        try:
            import azure.cognitiveservices.speech as speechsdk
            self.azure_speech = speechsdk
            self.engine_name = "Azure TTS"
        except ImportError:
            raise ImportError("azure-cognitiveservices-speech未安装，请运行: pip install azure-cognitiveservices-speech")

    def synthesize(self, text, voice=None, rate=1.0, pitch=1.0,
                  volume=1.0, emotion="neutral", output=None):
        """
        合成语音

        Args:
            text: 要合成的文本
            voice: 音色/语言代码
            rate: 语速（0.5-2.0）
            pitch: 音调（0.5-2.0）
            volume: 音量（0.0-1.0）
            emotion: 情感（happy/sad/angry/surprised/calm/neutral）
            output: 输出文件路径

        Returns:
            输出文件路径
        """
        if self.engine == "system":
            return self._synthesize_system(text, voice, rate, pitch, volume, emotion, output)
        elif self.engine == "gtts":
            return self._synthesize_gtts(text, voice, rate, output)
        elif self.engine == "edge":
            return self._synthesize_edge(text, voice, rate, pitch, emotion, output)
        elif self.engine == "azure":
            return self._synthesize_azure(text, voice, rate, pitch, emotion, output)

    def _synthesize_system(self, text, voice, rate, pitch, volume, emotion, output):
        """使用系统TTS合成"""
        engine = self.pyttsx3.init()

        # 设置音色
        if voice:
            voices = engine.getProperty('voices')
            for v in voices:
                if voice in v.name or voice in v.languages:
                    engine.setProperty('voice', v.id)
                    break

        # 设置语速
        rate_value = engine.getProperty('rate') * rate
        engine.setProperty('rate', rate_value)

        # 设置音量
        engine.setProperty('volume', volume)

        # 输出到文件
        if output is None:
            output = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name

        engine.save_to_file(text, output)
        engine.runAndWait()

        print(f"已保存到: {output}")
        return output

    def _synthesize_gtts(self, text, voice, rate, output):
        """使用gTTS合成"""
        if voice is None:
            voice = "zh"

        tts = self.gTTS(text=text, lang=voice, slow=(rate < 0.8))

        if output is None:
            output = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False).name

        tts.save(output)
        print(f"已保存到: {output}")
        return output

    async def _synthesize_edge(self, text, voice, rate, pitch, emotion, output):
        """使用Edge-TTS合成"""
        if voice is None:
            voice = "zh-CN-XiaoxiaoNeural"

        # 设置语音参数
        communicate = self.edge_tts.Communicate(text, voice)

        # 应用情感（通过SSML）
        if emotion != "neutral":
            text = self._apply_emotion_ssml(text, emotion, rate, pitch)
            communicate = self.edge_tts.Communicate(text, voice)

        if output is None:
            output = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False).name

        await communicate.save(output)
        print(f"已保存到: {output}")
        return output

    def _synthesize_azure(self, text, voice, rate, pitch, emotion, output):
        """使用Azure TTS合成"""
        # 需要设置API密钥
        speech_key = os.environ.get("AZURE_SPEECH_KEY")
        speech_region = os.environ.get("AZURE_SPEECH_REGION", "eastasia")

        if not speech_key:
            raise ValueError("请设置AZURE_SPEECH_KEY环境变量")

        # 创建语音配置
        config = self.azure_speech.SpeechConfig(
            subscription=speech_key,
            region=speech_region
        )

        if voice:
            config.speech_synthesis_voice_name = voice

        # 创建音频配置
        if output is None:
            output = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name

        audio_config = self.azure_speech.audio.AudioOutputConfig(filename=output)

        # 创建合成器
        synthesizer = self.azure_speech.SpeechSynthesizer(speech_config=config, audio_config=audio_config)

        # 应用情感（SSML）
        if emotion != "neutral":
            text = self._apply_emotion_ssml(text, emotion, rate, pitch)

        # 执行合成
        result = synthesizer.speak_text_async(text).get()

        if result.reason == self.azure_speech.ResultReason.SynthesizingAudioCompleted:
            print(f"已保存到: {output}")
            return output
        else:
            raise RuntimeError(f"合成失败: {result.reason}")

    def _apply_emotion_ssml(self, text, emotion, rate, pitch):
        """
        应用情感SSML标记

        Args:
            text: 原始文本
            emotion: 情感类型
            rate: 语速
            pitch: 音调

        Returns:
            SSML格式的文本
        """
        # SSML参数
        rate_str = self._rate_to_ssml(rate)
        pitch_str = self._pitch_to_ssml(pitch)
        emotion_style = self._emotion_to_style(emotion)

        # 构建SSML
        ssml = f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-CN">'
        ssml += f'<voice name="zh-CN-XiaoxiaoNeural">'
        ssml += f'<mstts:express-as style="{emotion_style}">'
        ssml += f'<prosody rate="{rate_str}" pitch="{pitch_str}">'
        ssml += text
        ssml += '</prosody></mstts:express-as></voice></speak>'

        return ssml

    def _rate_to_ssml(self, rate):
        """将语速转换为SSML格式"""
        if rate <= 0.5:
            return "0.5"
        elif rate <= 0.75:
            return "0.8"
        elif rate <= 1.0:
            return "1.0"
        elif rate <= 1.25:
            return "1.2"
        elif rate <= 1.5:
            return "1.5"
        else:
            return "2.0"

    def _pitch_to_ssml(self, pitch):
        """将音调转换为SSML格式"""
        if pitch <= 0.5:
            return "-20%"
        elif pitch <= 0.75:
            return "-10%"
        elif pitch <= 1.0:
            return "+0%"
        elif pitch <= 1.25:
            return "+10%"
        else:
            return "+20%"

    def _emotion_to_style(self, emotion):
        """将情感转换为Azure TTS样式"""
        emotion_map = {
            "happy": "cheerful",
            "sad": "sad",
            "angry": "angry",
            "surprised": "excited",
            "calm": "calm",
            "neutral": "neutral"
        }
        return emotion_map.get(emotion, "neutral")

    def list_voices(self):
        """列出可用音色"""
        if self.engine == "system":
            return self._list_system_voices()
        elif self.engine == "edge":
            return self._list_edge_voices()
        else:
            print(f"引擎 {self.engine} 不支持列出音色")
            return []

    def _list_system_voices(self):
        """列出系统TTS音色"""
        engine = self.pyttsx3.init()
        voices = engine.getProperty('voices')

        print("\n可用音色:")
        for i, voice in enumerate(voices, 1):
            print(f"{i}. {voice.name}")
            print(f"   ID: {voice.id}")
            print(f"   语言: {voice.languages}")
            print()

        return voices

    async def _list_edge_voices(self):
        """列出Edge-TTS音色"""
        voices = await self.edge_tts.list_voices()

        print("\n可用音色:")
        for voice in voices:
            if "zh-CN" in voice["Locale"]:
                print(f"- {voice['Name']} ({voice['Locale']}, {voice['Gender']})")

        return voices


def main():
    parser = argparse.ArgumentParser(description="TTS语音扩展工具")
    parser.add_argument("--text", required=True, help="要合成的文本")
    parser.add_argument("--voice", help="音色/语言代码")
    parser.add_argument("--engine", default="system", choices=["system", "gtts", "edge", "azure"],
                       help="TTS引擎")
    parser.add_argument("--output", help="输出音频文件")
    parser.add_argument("--rate", type=float, default=1.0, help="语速（0.5-2.0）")
    parser.add_argument("--pitch", type=float, default=1.0, help="音调（0.5-2.0）")
    parser.add_argument("--volume", type=float, default=1.0, help="音量（0.0-1.0）")
    parser.add_argument("--emotion", default="neutral",
                       choices=["happy", "sad", "angry", "surprised", "calm", "neutral"],
                       help="情感")
    parser.add_argument("--list-voices", action="store_true", help="列出可用音色")
    parser.add_argument("--format", default="wav", choices=["wav", "mp3", "ogg"], help="音频格式")

    args = parser.parse_args()

    # 初始化
    enhancer = TTSEnhancer(engine=args.engine)

    # 列出音色
    if args.list_voices:
        if args.engine == "edge":
            import asyncio
            asyncio.run(enhancer.list_voices())
        else:
            enhancer.list_voices()
        return

    # 合成语音
    import asyncio

    if args.engine == "edge":
        output = asyncio.run(enhancer.synthesize(
            args.text,
            voice=args.voice,
            rate=args.rate,
            pitch=args.pitch,
            volume=args.volume,
            emotion=args.emotion,
            output=args.output
        ))
    else:
        output = enhancer.synthesize(
            args.text,
            voice=args.voice,
            rate=args.rate,
            pitch=args.pitch,
            volume=args.volume,
            emotion=args.emotion,
            output=args.output
        )

    # 格式转换（如果需要）
    if output and args.format != "wav":
        if output.endswith(".wav"):
            new_output = output.replace(".wav", f".{args.format}")
            try:
                subprocess.run(["ffmpeg", "-i", output, new_output], check=True)
                os.remove(output)
                output = new_output
                print(f"已转换为 {args.format} 格式: {output}")
            except:
                print(f"格式转换失败，保留WAV格式: {output}")


if __name__ == "__main__":
    main()
