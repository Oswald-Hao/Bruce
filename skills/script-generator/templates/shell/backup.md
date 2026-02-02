#!/bin/bash
# 自动生成的Shell脚本 - 备份脚本
# 生成时间: {{timestamp}}
# 需求: {{prompt}}

set -e  # 遇到错误立即退出

# 配置变量
SOURCE_DIR="{{source_dir|/data}}"
BACKUP_DIR="{{backup_dir|/backup}}"
DAYS_TO_KEEP="{{days|7}}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 执行备份
echo "开始备份: $SOURCE_DIR -> $BACKUP_DIR"
tar -czf "$BACKUP_DIR/backup_$TIMESTAMP.tar.gz" "$SOURCE_DIR"

# 清理旧备份
echo "清理超过 $DAYS_TO_KEEP 天的旧备份..."
find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +$DAYS_TO_KEEP -delete

echo "备份完成！"
