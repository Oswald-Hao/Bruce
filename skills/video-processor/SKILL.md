# Video Processing Skill

视频处理技能 - 视频剪辑、转码、分析、压缩

## 功能说明

- 视频格式转换（MP4/AVI/MOV/WebP等）
- 视频剪辑（裁剪、拼接、提取片段）
- 视频压缩（减小文件大小，保持质量）
- 视频信息提取（分辨率、时长、编码等）
- 音频提取（从视频中提取音频）
- 视频截图（提取关键帧）
- 批量处理

## 使用方式

```bash
# 视频格式转换
cd /home/lejurobot/clawd/skills/video-processor
python3 video_processor.py --convert <input_file> --output <output_file> --format <format>

# 视频压缩
python3 video_processor.py --compress <input_file> --output <output_file> --quality <level>

# 视频剪辑
python3 video_processor.py --clip <input_file> --output <output_file> --start <time> --end <time>

# 提取关键帧
python3 video_processor.py --screenshot <input_file> --output <output_dir> --count <number>
```

## 测试用例

```bash
# 运行测试
cd /home/lejurobot/clawd/skills/video-processor
python3 test_video_processor.py
```

## 实现方式

Python 3 + ffmpeg（通过subprocess调用） + moviepy（可选，简化API）
