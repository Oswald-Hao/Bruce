# TTS语音扩展技能

支持多种TTS引擎，提供多音色、多语言和情感表达能力的语音合成系统。

## 功能特性

- ✓ 多种TTS引擎（系统TTS、gTTS、Edge-TTS、Azure）
- ✓ 多音色选择
- ✓ 多语言支持
- ✓ 情感表达（快乐、悲伤、愤怒、惊讶、平静）
- ✓ 实时语音合成
- ✓ 批量音频生成
- ✓ SSML标记支持
- ✓ 语速/音调/音量调节

## 安装

```bash
# 基础安装（系统TTS）
pip install pyttsx3

# Google TTS
pip install gtts

# Edge TTS（推荐，音质好）
pip install edge-tts

# Azure TTS（专业版）
pip install azure-cognitiveservices-speech
```

## 快速开始

### 基础语音合成

```bash
# 系统TTS（离线）
python tts.py --text "你好，世界" --voice zh-CN --output hello.wav

# Edge-TTS（推荐，音质好，需要网络）
python tts.py --text "Hello, world!" --voice en-US-JennyNeural --output hello.mp3 --engine edge

# Google TTS
python tts.py --text "测试" --voice zh --output test.mp3 --engine gtts
```

### 情感语音合成

```bash
# 快乐语气
python emotion_tts.py --text "太棒了！" --emotion happy --voice zh-CN-XiaoxiaoNeural --output happy.mp3

# 悲伤语气
python emotion_tts.py --text "我很遗憾" --emotion sad --voice zh-CN-XiaoxiaoNeural --output sad.mp3

# 生成所有情感的语音
python emotion_tts.py --text "这是一段测试文本" --all-emotions --output-dir ./emotions
```

### 批量处理

```bash
# 批量转写目录中的所有文本
python batch_tts.py --input-dir ./texts --output-dir ./audio --voice zh-CN-XiaoxiaoNeural

# 使用Edge引擎
python batch_tts.py --input-dir ./articles --output-dir ./speeches --engine edge --format mp3
```

## 引擎选择

| 引擎 | 音质 | 离线 | 成本 | 适用场景 |
|------|------|------|------|----------|
| System | 一般 | ✓ | 免费 | 快速测试、离线需求 |
| gTTS | 良好 | ✗ | 免费 | 日常使用、多语言 |
| Edge-TTS | 很好 | ✗ | 免费 | **推荐**、高质量需求 |
| Azure | 最好 | ✗ | 付费 | 专业应用、商业场景 |

## 情感类型

- `happy` - 快乐（语速稍快，音调稍高）
- `sad` - 悲伤（语速慢，音调低）
- `angry` - 愤怒（语速快，音调高）
- `surprised` - 惊讶（语速变化，音调起伏）
- `calm` - 平静（语速稍慢）
- `neutral` - 中性（默认）

## 常用音色

### 中文（Edge-TTS）
- `zh-CN-XiaoxiaoNeural` - 女，年轻（推荐）
- `zh-CN-YunxiNeural` - 男，年轻
- `zh-CN-YunyangNeural` - 男，成熟
- `zh-CN-XiaoyiNeural` - 女，成熟

### 英文（Edge-TTS）
- `en-US-JennyNeural` - 女，美式（推荐）
- `en-US-GuyNeural` - 男，美式
- `en-GB-SoniaNeural` - 女，英式

### 列出所有音色
```bash
python tts.py --engine edge --list-voices
```

## 高级用法

### 调节语速和音调
```bash
python tts.py --text "快速朗读测试" --voice zh-CN-XiaoxiaoNeural --rate 1.5 --output fast.wav

python tts.py --text "慢速朗读测试" --voice zh-CN-XiaoxiaoNeural --rate 0.7 --output slow.wav
```

### 情感SSML
```bash
# 快乐 + 语速快
python tts.py --text "我好开心！" --emotion happy --rate 1.3 --voice zh-CN-XiaoxiaoNeural --output excited.wav
```

## 应用场景

1. **语音助手** - 自然对话
2. **有声书朗读** - 长文本转语音
3. **视频配音** - 自动配音
4. **语音播报** - 新闻、天气
5. **无障碍服务** - 为视障用户提供服务
6. **情感化交互** - 有情感的人机对话

## 核心价值

**对自我更迭的贡献：**
- 语音输出能力，完善语音交互
- 情感表达，增强人机交互体验
- 多语言支持，国际化应用
- 个性化音色，定制化体验

**对用户体验的提升：**
- 自然的语音对话
- 丰富的情感表达
- 多音色选择
- 灵活的参数调节

## 性能参考

**系统TTS（离线）：**
- 速度：快速
- 音质：一般

**gTTS（网络）：**
- 速度：中等
- 音质：良好
- 限制：每日调用限制

**Edge-TTS（网络，推荐）：**
- 速度：快
- 音质：很好
- 限制：无（免费）

**Azure TTS（网络，付费）：**
- 速度：很快
- 音质：最好
- 功能：最丰富

## 依赖项

- pyttsx3: 系统TTS
- gtts: Google TTS
- edge-tts: Edge TTS（推荐）
- azure-cognitiveservices-speech: Azure TTS

## 注意事项

- Edge-TTS需要网络连接
- Azure TTS需要API密钥（需付费）
- 系统TTS音质一般，建议使用Edge-TTS
- 首次使用Edge-TTS可能需要下载模型

## 未来增强

- [ ] 更多情感类型
- [ ] 自定义音色训练
- [ ] 实时语音对话
- [ ] 声音克隆
- [ ] 风格迁移
- [ ] 混合引擎支持

---

*创建于 2026-02-04*
