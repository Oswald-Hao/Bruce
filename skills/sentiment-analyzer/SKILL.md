# 情感分析系统 - 技能文档

## 技能名称
sentiment-analyzer

## 功能描述
基于规则和词典的情感分析系统，支持中文和英文文本的情感分析，包括正面、负面、中性判断和情感评分。

## 核心功能

### 1. 单句情感分析
- 正面/负面/中性分类
- 情感评分（-1到+1）
- 置信度评估

### 2. 批量文本分析
- 批量处理多条文本
- 统计汇总
- 情感分布分析

### 3. 多语言支持
- 中文情感词典
- 英文情感词典
- 混合文本处理

### 4. 情感词典
- 中文正面词库（500+词）
- 中文负面词库（500+词）
- 英文正面词库（1000+词）
- 英文负面词库（1000+词）
- 程序可扩展

### 5. 高级功能
- 关键词情感分析
- 情感趋势分析
- 情感强度评估
- 否定词处理
- 程度副词处理

## 安装依赖
```bash
pip install -r requirements.txt
```

## 使用示例

```python
from sentiment_analyzer import SentimentAnalyzer

# 初始化
sa = SentimentAnalyzer()

# 单句分析
result = sa.analyze("这个产品非常好用，我很满意！")
print(result)
# {'label': 'positive', 'score': 0.85, 'confidence': 0.75}

# 批量分析
texts = [
    "这个产品很棒！",
    "太糟糕了，浪费钱",
    "一般般吧"
]
results = sa.analyze_batch(texts)
print(results)

# 情感趋势
sa.analyze_trend(texts)
```

## 命令行接口

```bash
# 分析单句
python sentiment_analyzer.py analyze "这个产品非常好"

# 批量分析
python sentiment_analyzer.py batch input.txt output.json

# 情感趋势
python sentiment_analyzer.py trend input.txt

# 查看词典
python sentiment_analyzer.py dict
```

## 赚钱方式

### 1. 舆情监控服务
- 为企业监控社交媒体情感
- 品牌声誉管理
- 危机预警

### 2. 用户反馈分析
- 分析用户评论和反馈
- 产品改进建议
- 客户满意度评估

### 3. 市场调研
- 竞品情感对比
- 消费者态度分析
- 市场趋势预测

### 4. 数据服务
- 情感分析API
- 定制化情感词典
- 行业情感报告

### 预期收益：月3000-15000元
