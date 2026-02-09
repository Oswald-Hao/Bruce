# 视频剪辑与处理系统

智能视频编辑和处理工具，支持视频剪辑、转码、特效添加、音频处理等功能。

## 功能

- 视频剪辑（裁剪、合并、分割）
- 格式转换（支持MP4、AVI、MOV、MKV等主流格式）
- 视频压缩（优化大小和画质）
- 音频处理（提取、替换、混音）
- 字幕添加（SRT字幕文件）
- 水印添加（文字/图片水印）
- 批量处理

## 使用方法

```bash
# 视频剪辑
python main.py clip --input video.mp4 --start 00:00:10 --end 00:00:30 --output clip.mp4

# 格式转换
python main.py convert --input video.avi --output video.mp4

# 视频压缩
python main.py compress --input video.mp4 --output compressed.mp4 --quality medium

# 提取音频
python main.py extract-audio --input video.mp4 --output audio.mp3

# 添加水印
python main.py watermark --input video.mp4 --output marked.mp4 --text "Bruce" --position bottom-right
```

## 测试

运行测试：
```bash
python test.py
```

## 依赖

- ffmpeg（系统依赖）
- Python 3.7+
- subprocess
