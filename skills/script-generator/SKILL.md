# Script Generator - 自动化脚本生成器

*智能生成Shell/Python/Node自动化脚本，减少重复编码*

## 功能概述

根据自然语言需求自动生成可执行的自动化脚本，支持三种语言：
- Shell脚本（Bash）
- Python脚本
- Node.js脚本

## 核心功能

1. **智能解析需求**：理解自然语言需求，提取任务类型、参数、操作
2. **模板驱动生成**：基于预定义模板生成代码
3. **多语言支持**：Shell/Python/Node三种脚本语言
4. **安全检查**：生成前检查危险命令
5. **自动注释**：生成的代码包含详细注释
6. **参数化配置**：支持变量和配置项

## 使用方法

```bash
# 生成Shell脚本
python3 script_generator.py \
  --lang shell \
  --prompt "创建一个定时备份脚本，每天凌晨2点备份/data目录到/backup，保留最近7天的备份" \
  --output backup.sh

# 生成Python脚本
python3 script_generator.py \
  --lang python \
  --prompt "监控指定进程的CPU和内存使用率，超过阈值时发送邮件告警" \
  --output monitor.py

# 生成Node.js脚本
python3 script_generator.py \
  --lang node \
  --prompt "监听指定目录的文件变化，自动部署到远程服务器" \
  --output deploy.js

# 查看支持的模板
python3 script_generator.py --list-templates
```

## 参数说明

- `--lang`: 脚本语言（shell/python/node）
- `--prompt`: 自然语言需求描述
- `--output`: 输出文件路径
- `--list-templates`: 列出所有可用模板
- `--verbose`: 显示详细生成过程

## 安全特性

- 检测危险命令（rm -rf /、:(){:|:&};:等）
- 过滤敏感路径操作
- 添加用户确认提示
- 包含安全注释

## 测试

运行测试：
```bash
python3 test_generator.py
```

测试覆盖：
- 模板加载
- 需求解析
- 代码生成
- 安全检查
- 输出验证

## 扩展

添加新模板：
1. 在 `templates/` 目录创建新模板文件
2. 在 `generator.py` 中注册模板
3. 添加测试用例
