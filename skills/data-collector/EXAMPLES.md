# Data Collector 使用示例

## 快速开始

### 1. 采集单个页面
```bash
cd /home/lejurobot/clawd/skills/data-collector
python3 data-collector.py --url "https://example.com" --selector "h1"
```

### 2. 采集并保存为JSON
```bash
python3 data-collector.py \
  --url "https://news.example.com" \
  --selector "h2.title" \
  --format json \
  --output news.json
```

### 3. 批量采集多个页面
```bash
# 创建URL列表文件
cat > urls.txt << EOF
https://example.com/page1
https://example.com/page2
https://example.com/page3
EOF

# 批量采集
python3 data-collector.py \
  --urls urls.txt \
  --selector "article.content" \
  --format csv \
  --output results.csv \
  --delay 2
```

### 4. 按关键词过滤
```bash
python3 data-collector.py \
  --url "https://shop.example.com" \
  --selector "div.product" \
  --filter "discount" \
  --format json \
  --output discount_products.json
```

## 实战场景

### 场景1：采集竞品价格
```bash
# 采集电商产品价格
python3 data-collector.py \
  --urls competitor_urls.txt \
  --selector "div.product-item" \
  --format csv \
  --output competitor_prices.csv \
  --delay 1.5
```

### 场景2：监控新闻标题
```bash
# 采集科技新闻标题
python3 data-collector.py \
  --url "https://news.example.com/tech" \
  --selector "h2.news-title" \
  --format json \
  --output tech_news.json \
  --limit 50
```

### 场景3：抓取博客文章
```bash
# 批量抓取博客文章内容
python3 data-collector.py \
  --urls blog_urls.txt \
  --selector "article.post-content" \
  --format txt \
  --output articles.txt \
  --delay 3
```

## CSS选择器指南

- `h1` - 标题
- `h2.news-title` - 类名为news-title的h2标题
- `div.product` - 类名为product的div
- `p.description` - 类名为description的段落
- `a.link` - 类名为link的链接
- `#main-content` - id为main-content的元素
- `.item.active` - 同时有item和active类的元素

更多选择器请参考：https://www.w3schools.com/cssref/css_selectors.asp

## 常见问题

**Q: 如何查看网页的CSS选择器？**
A: 在浏览器中右键点击元素 → 检查，在开发者工具中右键元素 → Copy → Copy selector

**Q: 采集速度慢怎么办？**
A: 调整--delay参数（默认1秒），但不要太快以免被封

**Q: 某些网站采集不到数据？**
A: 可能是动态渲染的JavaScript网站，需要用其他工具（如selenium）

**Q: 如何处理登录？**
A: 本技能不支持登录，可以使用带session cookie的requests高级用法
