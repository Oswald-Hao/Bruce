# 知识图谱构建系统

智能知识图谱构建和管理工具，支持实体关系抽取、知识存储、图谱查询、可视化等功能。

## 功能

- 实体抽取（从文本中识别实体）
- 关系抽取（识别实体间关系）
- 知识存储（图结构存储，JSON格式）
- 图谱查询（节点查询、关系查询、路径查询）
- 图谱可视化（节点关系可视化）
- 图谱导出（JSON/CSV格式）
- 增量更新（动态添加知识）
- 图谱分析（度中心性、连接性分析）

## 使用方法

```bash
# 添加实体
python main.py add-entity --name "Bruce" --type "AI助手" --properties '{"created_by": "Oswald"}'

# 添加关系
python main.py add-relation --source "Bruce" --target "Oswald" --type "为...而生" --properties '{"since": "2026"}'

# 查询实体
python main.py query-entity --name "Bruce"

# 查询关系
python main.py query-relation --source "Bruce"

# 查询路径
python main.py query-path --start "Bruce" --end "Oswald"

# 导出图谱
python main.py export --output knowledge_graph.json

# 分析图谱
python main.py analyze
```

## 测试

运行测试：
```bash
python test.py
```

## 依赖

- Python 3.7+
- json, re
