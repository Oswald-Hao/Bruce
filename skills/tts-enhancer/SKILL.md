# TTS语音扩展技能

增强Bruce的语音合成（TTS）能力，提供更多音色、多语言支持和情感表达。

## 功能

- 多种TTS引擎支持（系统TTS、gTTS、Edge-TTS、Azure等）
- 多音色选择（不同声调、语速、音量）
- 多语言支持（中文、英文等）
- 情感表达（快乐、悲伤、愤怒、惊讶等）
- 实时语音合成
- 批量音频生成
- SSML标记支持
- 音频格式转换

## 工具

### tts.py
核心TTS引擎，支持多种后端。

**用法：**
```bash
python tts.py --text "你好世界" --voice zh-CN --output hello.wav
```

**选项：**
- `--text`: 要合成的文本
- `--voice`: 音色/语言代码
- `--engine`: TTS引擎（system/gtts/edge/azure）
- `--output`: 输出音频文件
- `--rate`: 语速（0.5-2.0）
- `--pitch`: 音调（0.5-2.0）
- `--volume`: 音量（0.0-1.0）
- `--emotion`: 情感（happy/sad/angry/neutral）
- `--format`: 音频格式（wav/mp3/ogg）

**示例：**
```bash
# 基础合成（系统TTS）
python tts.py --text "你好，世界" --voice zh-CN --output hello.wav

# 使用Edge-TTS（更自然）
python tts.py --text "Hello, world!" --voice en-US-JennyNeural --output hello.wav --engine edge

# 带情感的合成
python tts.py --text "太棒了！" --voice zh-CN --emotion happy --output excited.wav

# 快速朗读
python tts.py --text "快速阅读测试" --voice zh-CN --rate 1.5 --output fast.wav
```

### batch_tts.py
批量文本转语音。

**用法：**
```bash
python batch_tts.py --input-dir ./texts --output-dir ./audio --voice zh-CN
```

**选项：**
- `--input-dir`: 文本文件目录
- `--output-dir`: 音频输出目录
- `--voice`: 音色/语言代码
- `--recursive`: 递归处理子目录
- `--format`: 音频格式

### emotion_tts.py
情感语音合成。

**用法：**
```bash
python emotion_tts.py --text "我很开心" --emotion happy --voice zh-CN --output happy.wav
```

**支持的情感：**
- `happy` - 快乐（语速稍快，音调稍高）
- `sad` - 悲伤（语速慢，音调低）
- `angry` - 愤怒（语速快，音调高，音量大）
- `surprised` - 惊讶（语速变化，音调起伏）
- `calm` - 平静（正常语速和音调）
- `neutral` - 中性（默认）

## 技术规格

### 支持的引擎

1. **系统TTS** - 使用系统自带TTS（需要pyttsx3）
   - 优点：无需网络，离线可用
   - 缺点：音质一般，语言有限

2. **gTTS** - Google Translate TTS
   - 优点：多语言支持，免费
   - 缺点：需要网络，每日有限制

3. **Edge-TTS** - Microsoft Edge TTS
   - 优点：音质好，多音色，免费
   - 缺点：需要网络

4. **Azure TTS** - Microsoft Azure Cognitive Services
   - 优点：最专业，神经语音，情感丰富
   - 缺点：需要付费，需要API密钥

### 音频格式

- WAV - 无损，兼容性好
- MP3 - 压缩，体积小
- OGG - 开源，质量好

## 应用场景

- 语音助手回复
- 有声书朗读
- 视频配音
- 语音播报
- 无障碍服务
- 自动配音

## 核心价值

**对自我更迭的贡献：**
1. **语音输出：** 实现语音输出，完善语音交互
2. **情感表达：** 通过语音情感增强人机交互
3. **多语言：** 支持多语言语音输出
4. **个性化：** 多种音色选择，提供个性化体验

**应用场景：**
- 语音助手对话
- 有声内容朗读
- 多语言语音输出
- 情感化语音交互
