# 语音识别增强技能

增强Bruce的语音识别（STT）能力，支持多语言、多音频格式，提供高精度转写。

## 功能

- 多语言支持（中文、英文等）
- 多音频格式支持（WAV、MP3、FLAC、OGG）
- 高精度转写
- 自动语言检测
- 噪声抑制
- 说话人识别（多说话人场景）
- 时间戳输出
- 实时转录（可选）

## 工具

### stt.py
核心STT引擎，基于OpenAI Whisper。

**用法：**
```bash
python stt.py --audio input.wav --language zh --output output.txt
```

**选项：**
- `--audio`: 音频文件路径
- `--language`: 语言代码（zh/en/ja/等，auto=自动检测）
- `--model`: 模型大小（tiny/base/small/medium/large）
- `--output`: 输出文本文件
- `--timestamps`: 包含时间戳
- `--speakers`: 启用说话人识别
- `--denoise`: 启用噪声抑制

**示例：**
```bash
# 基础转录（自动语言检测）
python stt.py --audio meeting.mp3 --language auto --output transcript.txt

# 高精度转录（带时间戳和说话人识别）
python stt.py --audio interview.wav --language zh --model large --output detailed.txt --timestamps --speakers

# 英文转录
python stt.py --audio speech.mp3 --language en --output en.txt

# 实时转录（从麦克风）
python stt.py --mic --language zh
```

### batch_stt.py
批量音频文件转写。

**用法：**
```bash
python batch_stt.py --input-dir ./audio --output-dir ./transcripts --language zh
```

**选项：**
- `--input-dir`: 音频文件目录
- `--output-dir`: 输出文本目录
- `--language`: 语言代码
- `--recursive`: 递归处理子目录
- `--format`: 输出格式（txt/json/srt）

## 技术规格

- 引擎：OpenAI Whisper
- 支持语言：99种语言
- 音频格式：WAV, MP3, FLAC, OGG, M4A
- 模型大小：
  - tiny: 39MB, 快速
  - base: 74MB, 平衡
  - small: 244MB, 较好
  - medium: 769MB, 好
  - large: 1550MB, 最好

## 应用场景

- 会议记录自动生成
- 音频内容搜索
- 语音命令识别
- 访谈转录
- 播客转文本
- 字幕生成

## 核心价值

**对自我更迭的贡献：**
1. **语音交互：** 实现语音输入，扩展交互方式
2. **内容处理：** 自动处理音频内容，提升信息处理能力
3. **无障碍：** 为有听力障碍的用户提供服务
4. **自动化：** 自动转写音频，节省人工成本

**应用场景：**
- 语音命令
- 会议记录
- 音频内容分析
- 自动字幕生成
