# Script Generator 使用示例

*展示如何使用自动化脚本生成器*

## 1. 列出所有可用模板

```bash
python3 generator.py --list-templates
```

输出：
```
可用模板:
==================================================

📁 PYTHON:
  - backup: 定时备份指定目录到目标位置，支持保留指定天数的备份
  - monitor: 监控指定进程的CPU和内存使用率，超过阈值时记录日志

📁 NODE:
  - deploy: 监听指定目录的文件变化，自动执行部署命令

📁 SHELL:
  - backup: 定时备份指定目录到目标位置，支持保留指定天数的备份
  - monitor: 监控指定进程的CPU和内存使用率，超过阈值时记录日志
```

## 2. 生成Shell备份脚本

```bash
python3 generator.py \
  --lang shell \
  --prompt "备份 /data 目录到 /backup，保留7天" \
  --output backup.sh
```

生成的脚本会自动：
- 设置源目录为 `/data`
- 设置备份目录为 `/backup`
- 设置保留天数为 `7`
- 添加执行权限

## 3. 生成Python监控脚本

```bash
python3 generator.py \
  --lang python \
  --prompt "监控 python 进程的CPU和内存使用率，阈值90%" \
  --output monitor.py
```

## 4. 生成Node.js部署脚本

```bash
python3 generator.py \
  --lang node \
  --prompt "监听 ./src 目录，自动部署到远程服务器" \
  --output deploy.js
```

## 5. 使用verbose模式查看详细信息

```bash
python3 generator.py \
  --lang python \
  --prompt "创建一个备份脚本" \
  --verbose
```

会显示：
- 需求分析结果
- 选择的模板
- 生成的代码

## 6. 测试安全检查

```bash
# 危险命令会被检测到
python3 generator.py \
  --lang shell \
  --prompt "执行 rm -rf / 清理系统" \
  --output dangerous.sh
```

输出：
```
⚠️ 安全警告:
  - 检测到潜在危险命令: rm\s+-rf\s+/
⚠️ 脚本包含潜在危险操作，请人工审查后再执行！
```

## 7. 运行测试

```bash
python3 test_generator.py
```

## 8. 执行生成的脚本

```bash
# Shell脚本
chmod +x backup.sh
./backup.sh

# Python脚本
python3 monitor.py --process nginx --cpu-threshold 90

# Node脚本
node deploy.js ./src /var/www "npm run build"
```

## 支持的自然语言格式

- "创建一个bash脚本备份目录"
- "写一个python脚本监控CPU"
- "使用node.js创建部署脚本"
- "定时备份文件"
- "监控服务器状态"
- "监听文件变化自动部署"

系统会自动识别：
- 语言偏好（bash/python/node）
- 任务类型（backup/monitor/deploy等）
- 参数（路径、数字、时间）
