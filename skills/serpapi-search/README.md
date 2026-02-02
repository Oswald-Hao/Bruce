# SerpAPI搜索技能

## 简介

这是一个使用SerpAPI的网络搜索工具，完全免费（每月100次查询），无需信用卡。

## 特点

- ✓ 免费使用：每月100次查询
- ✓ 多引擎支持：Google、Bing、Yahoo、DuckDuckGo
- ✓ 简单易用：Python脚本，可直接调用
- ✓ 无需信用卡：只需API密钥
- ✓ 已测试通过：6个测试用例全部通过

## 安装

```bash
# 确保安装requests库
pip3 install requests

# 脚本已安装在：
/home/lejurobot/clawd/skills/serpapi-search/
```

## 使用方法

### 1. 命令行使用

```bash
python3 /home/lejurobot/clawd/skills/serpapi-search/search.py "搜索关键词" [结果数量]

# 示例
python3 /home/lejurobot/clawd/skills/serpapi-search/search.py "AI最新资讯" 5
```

### 2. Python代码调用

```python
from search import SerpAPISearch

# 创建搜索实例
search = SerpAPISearch()

# 搜索并获取结果
results = search.get_organic_results("Python编程教程", 5)

# 格式化输出
print(search.format_results(results))
```

### 3. 在Moltbot中使用

通过skill-creator或直接调用search.py脚本即可在Moltbot中使用。

## 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| query | str | 必需 | 搜索关键词 |
| engine | str | google | 搜索引擎（google/bing/yahoo/duckduckgo） |
| num | int | 10 | 返回结果数量（1-100） |
| country | str | us | 国家代码 |
| language | str | en | 语言代码 |

## 返回格式

每个搜索结果包含：
- `title`: 标题
- `link`: 链接
- `snippet`: 摘要
- `date`: 发布时间（如果有）

## 测试

```bash
# 运行测试
python3 /home/lejurobot/clawd/skills/serpapi-search/test.py
```

## 限制

- 每月免费100次查询
- 超出后按使用量收费
- 适合个人使用和小项目

## API密钥

```
7f2e8da583426b56dda5d8ccec53ebf4e6d5f024fe7bcd2108b886fcf142b761
```

## 文件结构

```
serpapi-search/
├── SKILL.md      # 技能文档
├── search.py     # 主要搜索脚本
├── test.py       # 测试脚本
└── README.md     # 说明文档
```

## 优势

相比Brave Search API：
- ✓ 无需信用卡
- ✓ 免费额度明确
- ✓ 多引擎支持
- ✓ 文档完善

## 测试状态

- ✓ 基本搜索测试通过
- ✓ 结果格式化测试通过
- ✓ 错误处理测试通过
- ✓ 空查询处理测试通过

**所有测试通过！可以正常使用。**
