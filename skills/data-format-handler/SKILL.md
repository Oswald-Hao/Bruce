# Data Format Handler - JSON/YAML处理工具

## 技能描述

智能数据格式处理工具，支持JSON/YAML转换、验证、格式化、批量处理、diff比较等功能。

## 核心功能

- JSON/YAML相互转换
- 格式化美化（缩进、排序）
- 数据验证（schema验证）
- 数据合并/合并
- 批量处理文件
- Diff比较

## 使用方法

### 格式转换
```python
from data_format_handler import DataFormatHandler

# 初始化
handler = DataFormatHandler()

# YAML转JSON
handler.convert('data.yaml', 'data.json', from_format='yaml', to_format='json')

# JSON转YAML
handler.convert('data.json', 'data.yaml', from_format='json', to_format='yaml')
```

### 格式化
```python
# 格式化JSON
handler.format_json('ugly.json', 'pretty.json', indent=4, sort_keys=True)

# 格式化YAML
handler.format_yaml('ugly.yaml', 'pretty.yaml', indent=2)
```

### 数据验证
```python
# JSON Schema验证
schema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'age': {'type': 'number'}
    },
    'required': ['name']
}

result = handler.validate_json('data.json', schema)
```

### 数据合并
```python
# 合并JSON文件
handler.merge_json_files(['file1.json', 'file2.json'], 'merged.json')

# 合并YAML文件
handler.merge_yaml_files(['file1.yaml', 'file2.yaml'], 'merged.yaml')
```

## 配置参数

- indent: 缩进空格数
- sort_keys: 是否排序键
- ensure_ascii: 是否转义ASCII

## 依赖安装

```bash
pip install pyyaml
```

## 文件结构

- data_format_handler.py - 主程序
- test_data_format_handler.py - 测试脚本
- SKILL.md - 技能文档
