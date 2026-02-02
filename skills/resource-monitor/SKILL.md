# Resource Monitor - 资源监控系统

监控CPU、内存、磁盘、网络等系统资源，实时获取使用率，支持报警和历史记录。

## 安装依赖

```bash
pip3 install psutil
```

## 快速开始

```bash
# 监控所有资源
python3 monitor.py

# 检查特定资源
python3 monitor.py check --type cpu --threshold 80

# 持续监控（每5秒）
python3 monitor.py monitor --interval 5

# 查看历史数据
python3 monitor.py history
```

## 核心功能

### 1. CPU监控
- 核心数和频率
- 使用率（整体/每核心）
- 负载平均值（1/5/15分钟）
- 进程CPU使用率Top10

### 2. 内存监控
- 总内存、已用、可用、缓存
- 使用率
- 交换空间使用情况
- 进程内存使用率Top10

### 3. 磁盘监控
- 各分区使用率
- 总容量、已用、可用
- IO读写速度
- 磁盘IO进程Top10

### 4. 网络监控
- 发送/接收字节数
- 上传/下载速度
- 网络连接数（TCP/UDP）
- 网络错误统计

### 5. 报警系统
- 支持自定义阈值
- 邮件/日志报警
- 报警历史记录

## 输出格式

支持多种输出格式：
- 文本（默认）
- JSON（--format json）
- CSV（--format csv）

## 使用示例

### 实时监控
```bash
python3 monitor.py monitor --interval 3 --format text
```

### 检查资源
```bash
# 检查CPU是否超过80%
python3 monitor.py check --type cpu --threshold 80

# 检查内存是否超过90%
python3 monitor.py check --type memory --threshold 90

# 检查磁盘是否超过85%
python3 monitor.py check --type disk --threshold 85
```

### 保存历史
```bash
python3 monitor.py monitor --interval 10 --save
# 数据保存到 ~/.monitor_history.json
```

### 查看历史
```bash
python3 monitor.py history --hours 1
```

## 配置文件

配置文件位置：~/.monitor_config.json

```json
{
  "thresholds": {
    "cpu": 80,
    "memory": 85,
    "disk": 90
  },
  "alert": {
    "enabled": true,
    "email": "user@example.com"
  },
  "history": {
    "enabled": true,
    "path": "~/.monitor_history.json",
    "maxDays": 7
  }
}
```

## 注意事项

1. 需要root权限才能监控所有进程
2. 网络速度需要间隔计算（至少2秒）
3. 历史数据会自动清理（默认保留7天）
