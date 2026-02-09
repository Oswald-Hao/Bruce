# 健康管理分析系统

智能健康管理和分析工具，提供运动数据分析、饮食建议、健康监测、睡眠分析等功能。

## 功能

- 运动分析（步数、卡路里、心率、运动类型识别）
- 饮食记录和营养分析（热量、蛋白质、脂肪、碳水化合物）
- 睡眠质量分析（深睡、浅睡、REM睡眠、睡眠时长）
- 健康指标监测（体重、BMI、血压、血糖）
- 健康报告生成（日、周、月报告）
- 健康建议和提醒（运动、饮食、睡眠建议）
- 数据持久化（JSON/CSV导出）

## 使用方法

```bash
# 记录运动
python main.py log-exercise --type running --duration 30 --calories 300 --steps 5000 --heart-rate 140

# 记录饮食
python main.py log-food --name "鸡胸肉沙拉" --calories 350 --protein 30 --carbs 15 --fat 10

# 记录睡眠
python main.py log-sleep --duration 7.5 --deep 3.0 --light 3.5 --rem 1.0

# 生成健康报告
python main.py report --period week --output health_report.json

# 获取健康建议
python main.py advice --type exercise --duration 7
```

## 测试

运行测试：
```bash
python test.py
```

## 依赖

- Python 3.7+
- datetime, json, math
