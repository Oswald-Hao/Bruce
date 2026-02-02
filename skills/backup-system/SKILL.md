# Backup System - 备份恢复系统

## 技能描述

智能备份恢复系统，支持文件备份、目录备份、增量备份、自动备份策略、数据恢复等功能。

## 核心功能

- 文件备份（单文件/多文件）
- 目录备份（递归复制、排除规则）
- 增量备份（仅备份变更文件）
- 自动备份策略（定时备份、保留策略）
- 数据恢复（完整恢复、选择性恢复）
- 压缩和加密（可选）

## 使用方法

### 基本备份
```python
from backup_system import BackupSystem

# 初始化
backup = BackupSystem()

# 备份文件
backup.backup_file('/path/to/file.txt', '/backup/file.txt')

# 备份目录
backup.backup_directory('/path/to/source', '/backup/destination')

# 增量备份（仅备份变更的文件）
backup.incremental_backup('/path/to/source', '/backup/destination')
```

### 带压缩和加密的备份
```python
# 压缩备份
backup.backup_directory(
    '/path/to/source',
    '/backup/destination.zip',
    compress=True
)

# 带排除规则的备份
backup.backup_directory(
    '/path/to/source',
    '/backup/destination',
    exclude=['*.tmp', '*.log', '__pycache__']
)
```

### 恢复数据
```python
# 恢复文件
backup.restore_file('/backup/file.txt', '/restore/file.txt')

# 恢复目录
backup.restore_directory('/backup/destination', '/restore/source')
```

### 自动备份策略
```python
# 创建备份策略
backup.create_backup_strategy(
    name='daily',
    sources=['/home/user/documents'],
    destination='/backups/daily',
    schedule='0 2 * * *',  # 每天凌晨2点
    retention_days=7  # 保留7天
)
```

## 配置参数

- compress: 是否压缩（默认False）
- exclude: 排除规则列表
- retention_days: 保留天数
- encryption_key: 加密密钥（可选）

## 注意事项

1. 大文件备份建议使用压缩
2. 增量备份需要先完成一次完整备份
3. 确保目标目录有足够空间
4. 测试恢复流程以确保备份可用

## 依赖安装

```bash
pip install cryptography
```

## 文件结构

- backup_system.py - 主程序
- test_backup_system.py - 测试脚本
- SKILL.md - 技能文档
