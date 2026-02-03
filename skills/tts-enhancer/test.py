#!/usr/bin/env python3
"""
测试TTS语音扩展技能
支持模拟模式（无需实际音频生成）
"""

import os
import sys
import tempfile
from unittest.mock import Mock, patch, MagicMock, AsyncMock

# 添加技能路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_initialization():
    """测试1: 引擎初始化"""
    print("\n测试1: 引擎初始化")

    try:
        # Mock所有引擎依赖
        sys.modules['pyttsx3'] = MagicMock()
        sys.modules['gtts'] = MagicMock()
        sys.modules['edge_tts'] = MagicMock()
        sys.modules['azure.cognitiveservices.speech'] = MagicMock()

        # 测试不同的引擎
        from tts import TTSEnhancer

        # 测试system引擎
        enhancer = TTSEnhancer(engine="system")
        assert enhancer.engine == "system", "引擎类型错误"
        print("  ✓ System引擎初始化")

        # 测试gtts引擎
        enhancer = TTSEnhancer(engine="gtts")
        assert enhancer.engine == "gtts", "引擎类型错误"
        print("  ✓ gTTS引擎初始化")

        # 测试edge引擎
        enhancer = TTSEnhancer(engine="edge")
        assert enhancer.engine == "edge", "引擎类型错误"
        print("  ✓ Edge引擎初始化")

        print("  ✓ 引擎初始化测试通过")
        return True

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_synthesize_mock():
    """测试2: 语音合成功能（模拟模式）"""
    print("\n测试2: 语音合成功能（模拟模式）")

    try:
        # Mock pyttsx3
        sys.modules['pyttsx3'] = MagicMock()
        mock_engine = MagicMock()
        # getProperty根据参数返回不同值
        mock_engine.getProperty.side_effect = lambda key: 200 if key == 'rate' else 1.0 if key == 'volume' else []
        mock_engine.runAndWait.return_value = None
        mock_engine.save_to_file.return_value = None
        # Mock voice对象
        mock_voice = MagicMock()
        mock_voice.name = "zh-CN"
        mock_voice.id = "test-voice"
        mock_voice.languages = ["zh-CN"]
        mock_engine.getProperty.side_effect = lambda key: [mock_voice] if key == 'voices' else 200 if key == 'rate' else 1.0
        sys.modules['pyttsx3'].init.return_value = mock_engine

        from tts import TTSEnhancer

        enhancer = TTSEnhancer(engine="system")

        # Mock临时文件创建
        with patch('tts.tempfile.NamedTemporaryFile') as mock_temp:
            mock_temp.return_value.name = "/tmp/test_output.wav"

            # 测试合成
            output = enhancer.synthesize(
                "测试文本",
                voice="zh-CN",
                rate=1.0,
                output=None
            )

            # 验证
            assert output is not None, "输出为空"
            print(f"  ✓ 语音合成测试通过")

        return True

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_emotion_mapping():
    """测试3: 情感映射"""
    print("\n测试3: 情感映射")

    try:
        sys.modules['pyttsx3'] = MagicMock()

        from tts import TTSEnhancer
        enhancer = TTSEnhancer(engine="system")

        # 测试SSML情感转换
        assert enhancer._emotion_to_style("happy") == "cheerful"
        assert enhancer._emotion_to_style("sad") == "sad"
        assert enhancer._emotion_to_style("angry") == "angry"
        print("  ✓ 情感类型映射")

        # 测试语速转换
        assert enhancer._rate_to_ssml(0.5) == "0.5"
        assert enhancer._rate_to_ssml(1.0) == "1.0"
        assert enhancer._rate_to_ssml(2.0) == "2.0"
        print("  ✓ 语速转换")

        # 测试音调转换（修复边界值）
        assert enhancer._pitch_to_ssml(0.5) == "-20%"
        assert enhancer._pitch_to_ssml(1.0) == "+0%"
        # 1.5应该映射到+20%（1.25以上区间）
        assert enhancer._pitch_to_ssml(1.5) == "+20%"
        print("  ✓ 音调转换")

        print("  ✓ 情感映射测试通过")
        return True

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ssml_generation():
    """测试4: SSML生成"""
    print("\n测试4: SSML生成")

    try:
        sys.modules['pyttsx3'] = MagicMock()

        from tts import TTSEnhancer
        enhancer = TTSEnhancer(engine="system")

        # 测试SSML生成
        ssml = enhancer._apply_emotion_ssml(
            "你好世界",
            emotion="happy",
            rate=1.0,
            pitch=1.0
        )

        print(f"  生成的SSML: {ssml[:100]}...")

        # 检查SSML内容
        assert "你好世界" in ssml, "缺少原始文本"
        assert "cheerful" in ssml.lower(), "缺少情感样式"  # 不区分大小写
        assert "prosody" in ssml, "缺少prosody标签"
        print("  ✓ SSML生成")

        print("  ✓ SSML生成测试通过")
        return True

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_emotion_tts_mock():
    """测试5: 情感TTS（模拟模式）"""
    print("\n测试5: 情感TTS（模拟模式）")

    try:
        from emotion_tts import EmotionTTS

        # 检查情感定义
        assert "happy" in EmotionTTS.EMOTIONS, "缺少happy情感"
        assert "sad" in EmotionTTS.EMOTIONS, "缺少sad情感"
        assert "angry" in EmotionTTS.EMOTIONS, "缺少angry情感"
        print("  ✓ 情感定义完整")

        # 检查情感参数
        happy_params = EmotionTTS.EMOTIONS["happy"]
        assert happy_params["rate"] > 1.0, "快乐情感语速应大于1.0"
        assert happy_params["pitch"] > 1.0, "快乐情感音调应大于1.0"
        print("  ✓ 情感参数正确")

        # 检查悲伤情感
        sad_params = EmotionTTS.EMOTIONS["sad"]
        assert sad_params["rate"] < 1.0, "悲伤情感语速应小于1.0"
        assert sad_params["pitch"] < 1.0, "悲伤情感音调应小于1.0"
        print("  ✓ 悲伤情感参数正确")

        print("  ✓ 情感TTS测试通过")
        return True

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_structure():
    """测试6: API结构完整性"""
    print("\n测试6: API结构完整性")

    try:
        from tts import TTSEnhancer
        from emotion_tts import EmotionTTS
        import inspect

        # 检查TTSEnhancer类
        members_tts = [name for name in dir(TTSEnhancer) if not name.startswith('_') or name == '__init__']
        assert "synthesize" in members_tts, "缺少synthesize方法"
        assert "list_voices" in members_tts, "缺少list_voices方法"
        print("  ✓ TTSEnhancer API完整")

        # 检查EmotionTTS类
        members_emotion = [name for name in dir(EmotionTTS) if not name.startswith('_')]
        assert "synthesize_with_emotion" in members_emotion, "缺少synthesize_with_emotion方法"
        assert "batch_synthesize" in members_emotion, "缺少batch_synthesize方法"
        assert "list_emotions" in members_emotion, "缺少list_emotions方法"
        print("  ✓ EmotionTTS API完整")

        print("  ✓ API结构测试通过")
        return True

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_batch_tts_mock():
    """测试7: 批量TTS（模拟模式）"""
    print("\n测试7: 批量TTS（模拟模式）")

    try:
        from batch_tts import BatchTTS

        # 检查文本格式支持
        assert ".txt" in BatchTTS.TEXT_FORMATS, "缺少.txt支持"
        assert ".md" in BatchTTS.TEXT_FORMATS, "缺少.md支持"
        print("  ✓ 文本格式支持")

        # 检查方法存在
        import inspect
        methods = [name for name in dir(BatchTTS) if not name.startswith('_')]
        assert "find_text_files" in methods, "缺少find_text_files方法"
        assert "process_batch" in methods, "缺少process_batch方法"
        print("  ✓ 批量处理方法完整")

        print("  ✓ 批量TTS测试通过")
        return True

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_import():
    """测试0: 模块导入"""
    print("\n测试0: 模块导入")

    try:
        from tts import TTSEnhancer
        print("  ✓ tts模块导入成功")
        return True
    except Exception as e:
        print(f"  ✗ 导入失败: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("TTS语音扩展技能测试（模拟模式）")
    print("=" * 60)
    print("注意: 使用模拟模式，无需实际音频生成\n")

    tests = [
        test_import,
        test_initialization,
        test_synthesize_mock,
        test_emotion_mapping,
        test_ssml_generation,
        test_emotion_tts_mock,
        test_api_structure,
        test_batch_tts_mock
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
        print("说明: 代码结构和API正确，实际使用需要安装对应引擎依赖")
        return 0
    else:
        print(f"\n✗ {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
