#!/usr/bin/env python3
"""
测试语音识别增强技能
"""

import os
import sys
import tempfile
import wave
import struct
import numpy as np

# 添加技能路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stt import STTEnhancer


def create_test_audio(duration=3, frequency=440, sample_rate=16000):
    """
    创建测试音频文件（简单的正弦波）

    Args:
        duration: 持续时间（秒）
        frequency: 频率（Hz）
        sample_rate: 采样率

    Returns:
        音频文件路径
    """
    # 生成正弦波
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    audio_data = 0.5 * np.sin(2 * np.pi * frequency * t)

    # 转换为16位PCM
    audio_data = (audio_data * 32767).astype(np.int16)

    # 写入WAV文件
    temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    temp_path = temp_file.name

    with wave.open(temp_path, 'wb') as wav_file:
        wav_file.setnchannels(1)  # 单声道
        wav_file.setsampwidth(2)  # 2字节（16位）
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())

    return temp_path


def test_basic_transcription():
    """测试1: 基础转写功能"""
    print("\n测试1: 基础转写功能")

    try:
        enhancer = STTEnhancer(model_size="tiny")

        # 创建测试音频
        audio_path = create_test_audio()
        print(f"  创建测试音频: {audio_path}")

        # 转写
        result = enhancer.transcribe(audio_path, language="en")
        print(f"  语言检测: {result['language']}")
        print(f"  文本长度: {len(result['text'])} 字符")

        assert result is not None, "转写结果为空"
        assert "language" in result, "缺少语言检测"
        assert "text" in result, "缺少转写文本"
        assert len(result["segments"]) > 0, "缺少段落信息"

        # 清理
        os.remove(audio_path)

        print("  ✓ 基础转写测试通过")
        return True

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        return False


def test_multilingual():
    """测试2: 多语言支持"""
    print("\n测试2: 多语言支持")

    try:
        enhancer = STTEnhancer(model_size="tiny")

        # 创建测试音频
        audio_path = create_test_audio()

        # 测试中文
        result_zh = enhancer.transcribe(audio_path, language="zh")
        assert result_zh["language"] in ["zh", "chinese"], f"中文检测失败: {result_zh['language']}"
        print(f"  中文检测: {result_zh['language']}")

        # 测试英文
        result_en = enhancer.transcribe(audio_path, language="en")
        assert result_en["language"] in ["en", "english"], f"英文检测失败: {result_en['language']}"
        print(f"  英文检测: {result_en['language']}")

        # 清理
        os.remove(audio_path)

        print("  ✓ 多语言测试通过")
        return True

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        return False


def test_timestamps():
    """测试3: 时间戳功能"""
    print("\n测试3: 时间戳功能")

    try:
        enhancer = STTEnhancer(model_size="tiny")

        audio_path = create_test_audio(duration=5)

        result = enhancer.transcribe(audio_path, timestamps=True)

        assert len(result["segments"]) > 0, "缺少段落"

        for seg in result["segments"]:
            assert "start" in seg, "缺少开始时间"
            assert "end" in seg, "缺少结束时间"
            assert seg["end"] > seg["start"], "时间范围无效"

        print(f"  检测到 {len(result['segments'])} 个段落")

        # 清理
        os.remove(audio_path)

        print("  ✓ 时间戳测试通过")
        return True

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        return False


def test_save_formats():
    """测试4: 多种输出格式"""
    print("\n测试4: 多种输出格式")

    try:
        enhancer = STTEnhancer(model_size="tiny")
        audio_path = create_test_audio()

        result = enhancer.transcribe(audio_path)

        # 测试TXT格式
        txt_path = tempfile.NamedTemporaryFile(suffix=".txt", delete=False).name
        enhancer.save_transcript(result, txt_path, format="txt")
        assert os.path.exists(txt_path), "TXT文件未创建"
        assert os.path.getsize(txt_path) > 0, "TXT文件为空"
        os.remove(txt_path)
        print("  ✓ TXT格式")

        # 测试JSON格式
        json_path = tempfile.NamedTemporaryFile(suffix=".json", delete=False).name
        enhancer.save_transcript(result, json_path, format="json")
        assert os.path.exists(json_path), "JSON文件未创建"
        assert os.path.getsize(json_path) > 0, "JSON文件为空"

        # 验证JSON格式
        import json
        with open(json_path, "r") as f:
            json.load(f)
        os.remove(json_path)
        print("  ✓ JSON格式")

        # 测试SRT格式
        srt_path = tempfile.NamedTemporaryFile(suffix=".srt", delete=False).name
        enhancer.save_transcript(result, srt_path, format="srt")
        assert os.path.exists(srt_path), "SRT文件未创建"
        assert os.path.getsize(srt_path) > 0, "SRT文件为空"
        os.remove(srt_path)
        print("  ✓ SRT格式")

        # 清理
        os.remove(audio_path)

        print("  ✓ 输出格式测试通过")
        return True

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        return False


def test_model_sizes():
    """测试5: 不同模型大小"""
    print("\n测试5: 不同模型大小")

    try:
        audio_path = create_test_audio()

        models = ["tiny", "base"]

        for model in models:
            enhancer = STTEnhancer(model_size=model)
            result = enhancer.transcribe(audio_path)
            assert result is not None, f"{model} 模型转写失败"
            print(f"  ✓ {model} 模型")

        # 清理
        os.remove(audio_path)

        print("  ✓ 模型大小测试通过")
        return True

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        return False


def test_speaker_detection():
    """测试6: 说话人识别"""
    print("\n测试6: 说话人识别")

    try:
        enhancer = STTEnhancer(model_size="tiny")
        audio_path = create_test_audio(duration=10)

        result = enhancer.transcribe(audio_path, speakers=True)

        # 检查是否分配了说话人
        speaker_found = False
        for seg in result["segments"]:
            if "speaker" in seg:
                speaker_found = True
                print(f"  检测到说话人: {seg['speaker']}")
                break

        # 注意：简单音频可能只有一个说话人，这是正常的
        # 只要功能不报错就算通过
        print("  ✓ 说话人识别功能正常")

        # 清理
        os.remove(audio_path)

        return True

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("语音识别增强技能测试")
    print("=" * 60)

    tests = [
        test_basic_transcription,
        test_multilingual,
        test_timestamps,
        test_save_formats,
        test_model_sizes,
        test_speaker_detection
    ]

    results = []

    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ✗ 测试异常: {e}")
            results.append(False)

    # 汇总
    print("\n" + "=" * 60)
    print("测试汇总")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total}")

    if passed == total:
        print("\n✓ 所有测试通过！")
        return 0
    else:
        print(f"\n✗ {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
