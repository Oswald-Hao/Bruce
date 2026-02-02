# Data Collector - 数据自动采集系统

*智能爬虫，自动采集网页数据，支持多种输出格式*

## 功能描述

自动从网页采集数据，支持：
- 结构化数据提取（表格、列表等）
- 关键词搜索和过滤
- 多页面批量采集
- 多种输出格式（JSON、CSV、TXT）
- 自动去重和数据清洗

## 使用方式

### 基本用法

采集单个页面：
```
data-collector --url "https://example.com" --selector "div.product"
```

采集多个页面：
```
data-collector --urls "urls.txt" --selector "h2.title" --format json
```

按关键词过滤：
```
data-collector --url "https://example.com" --filter "AI" --format csv
```

### 参数说明

- `--url`: 单个URL（与--urls互斥）
- `--urls`: 包含URL列表的文件路径（每行一个）
- `--selector`: CSS选择器，用于提取元素
- `--filter`: 关键词过滤（仅提取包含该关键词的内容）
- `--format`: 输出格式（json/csv/txt，默认txt）
- `--output`: 输出文件路径（默认输出到控制台）
- `--limit`: 每页最多提取数量（默认100）
- `--delay`: 请求间隔秒数（默认1，避免被封）
- `--timeout`: 请求超时秒数（默认30）
- `--dedupe`: 启用去重（默认启用）
- `--clean`: 启用数据清洗（去除空格、换行等，默认启用）

### 依赖

- Python 3.7+
- pip安装：
```bash
pip install beautifulsoup4 requests lxml
```

或一键安装：
```bash
data-collector --install
```

## 输出格式

### JSON
```json
[
  {"text": "内容1", "url": "https://example.com/page1"},
  {"text": "内容2", "url": "https://example.com/page2"}
]
```

### CSV
```csv
text,url
内容1,https://example.com/page1
内容2,https://example.com/page2
```

### TXT
```
内容1
  来源: https://example.com/page1

内容2
  来源: https://example.com/page2
```

## 实战案例

### 案例1：采集新闻标题
```bash
data-collector --url "https://news.example.com" --selector "h2.news-title" --format json --output news.json
```

### 案例2：采集产品价格
```bash
data-collector --url "https://shop.example.com" --selector "div.product" --format csv --output prices.csv --filter "discount"
```

### 案例3：批量采集博客文章
```bash
data-collector --urls blog_urls.txt --selector "article.post-content" --format txt --output articles.txt --delay 2
```

## 注意事项

1. 遵守robots.txt规则
2. 控制请求频率，避免对服务器造成压力
3. 某些网站需要处理JavaScript渲染，本技能不支持（可用selenium等工具）
4. 复杂的登录/验证码场景需要额外处理

## 技术实现

- 使用requests发送HTTP请求
- 使用BeautifulSoup4解析HTML
- CSS选择器提取数据
- 支持去重和清洗
- 可配置延迟和超时
