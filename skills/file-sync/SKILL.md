# File Sync Tool - 文件同步工具

## 技能描述

智能文件同步工具，支持双向同步、单向同步、增量同步、文件冲突解决、排除规则等功能。

## 核心功能

- 双向同步（保持两个目录一致）
- 单向同步（源到目标或目标到源）
- 增量同步（仅同步变更文件）
- 冲突检测和处理（保留最新、保留两侧、手动选择）
- 排除规则（忽略特定文件/目录）
- 同步日志和统计

## 使用方法

### 基本同步
```python
from file_sync import FileSync

# 初始化
sync = FileSync()

# 单向同步（源 → 目标）
result = sync.sync_one_way('source/', 'destination/')

# 双向同步
result = sync.sync_two_way('dir1/', 'dir2/')
```

### 增量同步
```python
# 仅同步变更的文件
result = sync.sync_incremental('source/', 'destination/', exclude=['*.tmp', '.git'])
```

### 冲突处理
```python
# 冲突策略：newest（保留最新）、source（保留源）、target（保留目标）、both（保留两侧）
result = sync.sync_with_conflict_policy(
    'dir1/',
    'dir2/',
    conflict_policy='newest'
)
```

### 同步统计
```python
# 获取同步统计
stats = sync.get_sync_stats('source/', 'destination/')
print(stats)
# {'files_to_sync': 10, 'conflicts': 2, 'total_size': 1024000}
```

## 配置参数

- exclude: 排除规则列表（如['*.tmp', '.git', '*.log']）
- conflict_policy: 冲突策略
- dry_run: 预演模式（不实际同步）
- verbose: 详细输出

## 注意事项

1. 双向同步前建议先备份
2. 大文件同步建议使用增量模式
3. 使用dry_run先预览同步计划
4. 冲突处理要谨慎选择策略

## 依赖安装

```bash
# 无额外依赖，使用Python标准库
```

## 文件结构

- file_sync.py - 主程序
- test_file_sync.py - 测试脚本
- SKILL.md - 技能文档
