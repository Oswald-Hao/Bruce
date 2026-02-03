# 语音识别增强技能 (STT Enhancer)

基于OpenAI Whisper的高精度语音识别系统，支持多语言、多格式、时间戳和说话人识别。

## 功能特性

- ✓ 多语言支持（99种语言）
- ✓ 多音频格式（WAV, MP3, FLAC, OGG, M4A）
- ✓ 高精度转写（5种模型大小可选）
- ✓ 自动语言检测
- ✓ 时间戳输出
- ✓ 说话人识别（简单分段）
- ✓ 批量处理
- ✓ 多种输出格式（TXT, JSON, SRT）

## 安装

```bash
pip install openai-whisper torch numpy scipy sounddevice
```

## 快速开始

### 单文件转写

```bash
# 基础转写（自动语言检测）
python stt.py --audio meeting.mp3 --output transcript.txt

# 高精度转写（带时间戳）
python stt.py --audio interview.wav --language zh --model large --output detailed.txt --timestamps

# 生成SRT字幕
python stt.py --audio video.mp4 --language en --output subtitles.srt --format srt
```

### 批量处理

```bash
# 批量转写目录中的所有音频
python batch_stt.py --input-dir ./audio --output-dir ./transcripts --language zh

# 递归处理子目录
python batch_stt.py --input-dir ./recordings --output-dir ./text --recursive

# 生成JSON格式输出
python batch_stt.py --input-dir ./podcasts --output-dir ./data --format json
```

## 模型选择

| 模型 | 大小 | 速度 | 精度 | 适用场景 |
|------|------|------|------|----------|
| tiny | 39MB | 最快 | 一般 | 快速测试、低资源 |
| base | 74MB | 快 | 良好 | 日常使用（推荐） |
| small | 244MB | 中等 | 很好 | 高精度需求 |
| medium | 769MB | 慢 | 很好 | 专业转写 |
| large | 1550MB | 最慢 | 最好 | 最高精度 |

## 输出格式

### TXT格式
纯文本格式，包含完整文本和分段详情。

### JSON格式
结构化数据，包含所有转写信息。

```json
{
  "text": "完整文本",
  "language": "zh",
  "segments": [
    {
      "id": 1,
      "start": 0.0,
      "end": 2.5,
      "text": "你好世界"
    }
  ]
}
```

### SRT格式
标准字幕格式，可直接用于视频字幕。

## 应用场景

1. **会议记录** - 自动生成会议纪要
2. **音频内容搜索** - 转写后便于搜索
3. **语音命令** - 实现语音控制
4. **访谈转录** - 节省人工整理时间
5. **播客转文本** - 便于分享和引用
6. **字幕生成** - 自动为视频生成字幕

## 核心价值

**对自我更迭的贡献：**
- 扩展语音交互能力
- 自动处理音频内容
- 提升信息处理效率

**对用户体验的提升：**
- 支持语音输入
- 自动生成字幕
- 无障碍访问

## 测试

运行完整测试套件：

```bash
python test.py
```

测试包括：
- 基础转写功能
- 多语言支持
- 时间戳功能
- 多种输出格式
- 不同模型大小
- 说话人识别

## 技术规格

- 引擎：OpenAI Whisper
- 支持语言：99种
- 音频采样率：16000Hz
- 模型大小：39MB - 1550MB
- 输出格式：TXT, JSON, SRT

## 性能参考

在CPU上（base模型）：
- 1分钟音频 ≈ 10秒转写
- 精度：约95%（清晰语音）

在GPU上（base模型）：
- 1分钟音频 ≈ 2秒转写
- 精度：约95%（清晰语音）

## 依赖项

- openai-whisper: 核心STT引擎
- torch: 深度学习框架
- numpy: 数值计算
- scipy: 音频I/O
- sounddevice: 实时录音（可选）

## 注意事项

- 首次使用会自动下载模型（约40MB-1550MB）
- 建议使用GPU加速（CUDA）
- 噪音环境会影响识别精度
- 长音频可能需要较长时间处理

## 未来增强

- [ ] 噪声抑制算法
- [ ] 实时流式转录
- [ ] 更精确的说话人分离
- [ ] 情感分析
- [ ] 语音合成集成

---

*创建于 2026-02-04*
