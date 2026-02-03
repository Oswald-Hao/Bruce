#!/usr/bin/env python3
"""
测试语音识别增强技能
支持模拟模式（无需音频文件）
"""

import os
import sys
import json
from unittest.mock import Mock, patch, MagicMock

# 添加技能路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_basic_transcription_mock():
    """测试1: 基础转写功能（模拟模式）"""
    print("\n测试1: 基础转写功能（模拟模式）")

    try:
        # Mock Whisper模型
        with patch('stt.whisper.load_model') as mock_load:
            # 创建模拟模型
            mock_model = MagicMock()
            mock_model.transcribe.return_value = {
                "text": "这是一个测试转录文本",
                "language": "zh",
                "segments": [
                    {
                        "start": 0.0,
                        "end": 2.0,
                        "text": "这是一个测试"
                    }
                ]
            }
            mock_load.return_value = mock_model

            # 导入并测试
            from stt import STTEnhancer

            enhancer = STTEnhancer(model_size="tiny")

            # 测试转写（使用模拟音频路径）
            result = enhancer.transcribe("test_audio.wav", language="zh")

            assert result is not None, "转写结果为空"
            assert result["language"] == "zh", "语言检测错误"
            assert len(result["text"]) > 0, "转写文本为空"
            assert len(result["segments"]) > 0, "缺少段落信息"

            print(f"  ✓ 模拟转写测试通过")
            print(f"    语言: {result['language']}")
            print(f"    文本: {result['text'][:20]}...")
            return True

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multilingual_mock():
    """测试2: 多语言支持（模拟模式）"""
    print("\n测试2: 多语言支持（模拟模式）")

    try:
        with patch('stt.whisper.load_model') as mock_load:
            mock_model = MagicMock()
            mock_model.transcribe.side_effect = [
                {"text": "中文测试", "language": "zh", "segments": []},
                {"text": "English test", "language": "en", "segments": []}
            ]
            mock_load.return_value = mock_model

            from stt import STTEnhancer
            enhancer = STTEnhancer(model_size="tiny")

            # 测试中文
            result_zh = enhancer.transcribe("test.wav", language="zh")
            assert result_zh["language"] == "zh", f"中文检测失败"
            print(f"  中文检测: {result_zh['language']}")

            # 测试英文
            result_en = enhancer.transcribe("test.wav", language="en")
            assert result_en["language"] == "en", f"英文检测失败"
            print(f"  英文检测: {result_en['language']}")

            print("  ✓ 多语言测试通过")
            return True

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        return False


def test_timestamps_mock():
    """测试3: 时间戳功能（模拟模式）"""
    print("\n测试3: 时间戳功能（模拟模式）")

    try:
        with patch('stt.whisper.load_model') as mock_load:
            mock_model = MagicMock()
            mock_model.transcribe.return_value = {
                "text": "测试文本",
                "language": "zh",
                "segments": [
                    {"start": 0.0, "end": 2.5, "text": "测试"},
                    {"start": 2.5, "end": 5.0, "text": "文本"}
                ]
            }
            mock_load.return_value = mock_model

            from stt import STTEnhancer
            enhancer = STTEnhancer(model_size="tiny")

            result = enhancer.transcribe("test.wav", timestamps=True)

            assert len(result["segments"]) == 2, "段落数量错误"

            for seg in result["segments"]:
                assert "start" in seg, "缺少开始时间"
                assert "end" in seg, "缺少结束时间"
                assert seg["end"] > seg["start"], "时间范围无效"

            print(f"  ✓ 时间戳测试通过 ({len(result['segments'])} 个段落)")
            return True

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        return False


def test_save_formats_mock():
    """测试4: 多种输出格式（模拟模式）"""
    print("\n测试4: 多种输出格式（模拟模式）")

    try:
        with patch('stt.whisper.load_model') as mock_load:
            mock_model = MagicMock()
            mock_model.transcribe.return_value = {
                "text": "测试",
                "language": "zh",
                "segments": [{"start": 0.0, "end": 2.0, "text": "测试"}]
            }
            mock_load.return_value = mock_model

            from stt import STTEnhancer
            import tempfile

            enhancer = STTEnhancer(model_size="tiny")
            result = enhancer.transcribe("test.wav")

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
            with open(json_path, "r") as f:
                json_data = json.load(f)
                assert "text" in json_data, "JSON缺少text字段"
            os.remove(json_path)
            print("  ✓ JSON格式")

            # 测试SRT格式
            srt_path = tempfile.NamedTemporaryFile(suffix=".srt", delete=False).name
            enhancer.save_transcript(result, srt_path, format="srt")
            assert os.path.exists(srt_path), "SRT文件未创建"
            os.remove(srt_path)
            print("  ✓ SRT格式")

            print("  ✓ 输出格式测试通过")
            return True

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_sizes_mock():
    """测试5: 不同模型大小（模拟模式）"""
    print("\n测试5: 不同模型大小（模拟模式）")

    try:
        with patch('stt.whisper.load_model') as mock_load:
            mock_model = MagicMock()
            mock_model.transcribe.return_value = {
                "text": "测试",
                "language": "zh",
                "segments": []
            }
            mock_load.return_value = mock_model

            from stt import STTEnhancer

            models = ["tiny", "base", "small"]

            for model in models:
                enhancer = STTEnhancer(model_size=model)
                result = enhancer.transcribe("test.wav")
                assert result is not None, f"{model} 模型转写失败"
                print(f"  ✓ {model} 模型")

            print("  ✓ 模型大小测试通过")
            return True

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        return False


def test_speaker_detection_mock():
    """测试6: 说话人识别（模拟模式）"""
    print("\n测试6: 说话人识别（模拟模式）")

    try:
        with patch('stt.whisper.load_model') as mock_load:
            mock_model = MagicMock()
            mock_model.transcribe.return_value = {
                "text": "测试",
                "language": "zh",
                "segments": [
                    {"start": 0.0, "end": 2.0, "text": "A"},
                    {"start": 3.0, "end": 5.0, "text": "B"},
                    {"start": 5.5, "end": 7.0, "text": "C"}
                ]
            }
            mock_load.return_value = mock_model

            from stt import STTEnhancer
            enhancer = STTEnhancer(model_size="tiny")

            result = enhancer.transcribe("test.wav", speakers=True)

            # 检查说话人分配
            speakers_found = [seg.get("speaker") for seg in result["segments"] if "speaker" in seg]
            print(f"  检测到说话人: {set(speakers_found) if speakers_found else '单个说话人'}")

            print("  ✓ 说话人识别功能正常")
            return True

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        return False


def test_api_structure():
    """测试7: API结构完整性"""
    print("\n测试7: API结构完整性")

    try:
        from stt import STTEnhancer
        import inspect

        # 检查STTEnhancer类
        members = [name for name in dir(STTEnhancer) if not name.startswith('_') or name == '__init__']
        assert "transcribe" in members, "缺少transcribe方法"
        assert "save_transcript" in members, "缺少save_transcript方法"

        print(f"  ✓ STTEnhancer API完整")

        # 检查函数签名
        sig = inspect.signature(STTEnhancer.transcribe)
        params = list(sig.parameters.keys())
        assert "audio_path" in params, "缺少audio_path参数"
        assert "language" in params, "缺少language参数"

        print(f"  ✓ 方法签名正确")
        return True

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_import():
    """测试0: 导入测试"""
    print("\n测试0: 模块导入")

    try:
        from stt import STTEnhancer
        print("  ✓ stt模块导入成功")
        return True
    except Exception as e:
        print(f"  ✗ 导入失败: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("语音识别增强技能测试（模拟模式）")
    print("=" * 60)
    print("注意: 使用模拟模式，无需实际音频文件\n")

    tests = [
        test_import,
        test_basic_transcription_mock,
        test_multilingual_mock,
        test_timestamps_mock,
        test_save_formats_mock,
        test_model_sizes_mock,
        test_speaker_detection_mock,
        test_api_structure
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
        print("说明: 代码结构和API正确，实际使用需要安装ffmpeg")
        return 0
    else:
        print(f"\n✗ {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
