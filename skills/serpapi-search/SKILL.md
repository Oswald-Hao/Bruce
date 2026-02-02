# SerpAPI Search - 免费搜索引擎

使用SerpAPI进行网络搜索，无需信用卡，每月100次免费查询。

## 配置

API密钥：`7f2e8da583426b56dda5d8ccec53ebf4e6d5f024fe7bcd2108b886fcf142b761`

## 使用方法

通过调用这个技能进行搜索：

```python
# 搜索示例
search(query="查询内容", engine="google", num=10)
```

## 参数

- `query`: 搜索关键词
- `engine`: 搜索引擎，支持：google, bing, yahoo, duckduckgo（默认：google）
- `num`: 返回结果数量（默认：10，最大：100）

## 返回格式

返回搜索结果的JSON数据，包含：
- title: 标题
- link: 链接
- snippet: 摘要
- date: 发布时间（如果有）

## 注意事项

- 每月免费额度：100次查询
- 超出后按使用量收费
- 适合个人使用和小项目
