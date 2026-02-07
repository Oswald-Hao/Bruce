# 内容生成引擎

AI驱动的自动化内容生成工具，支持文章、文案、视频脚本等多种内容类型。

## 功能

- 文章生成（博客、新闻、教程）
- 营销文案（广告、邮件、社交媒体）
- 视频脚本（短视频、长视频）
- 多语言支持（中文、英文等）
- 内容优化（SEO、可读性）
- 批量生成
- 模板管理
- 内容审核
- 品牌风格适配
- A/B测试生成

## 使用方法

### 生成文章

```bash
cd /home/lejurobot/clawd/skills/content-generator

# 生成博客文章
python3 generator.py generate_article \
  --topic "人工智能的发展趋势" \
  --type blog \
  --length 2000 \
  --keywords "AI,人工智能,机器学习,深度学习"

# 生成新闻稿
python3 generator.py generate_article \
  --topic "公司发布新产品" \
  --type news \
  --length 800 \
  --company_name "ABC科技"
```

### 生成营销文案

```bash
# 生成广告文案
python3 generator.py generate_ad \
  --product "智能手表" \
  --type facebook \
  --audience "年轻白领" \
  --tone "专业"

# 生成邮件营销文案
python3 generator.py generate_email \
  --product "在线课程" \
  --promotion "限时折扣" \
  --discount 0.3
```

### 生成视频脚本

```bash
# 生成短视频脚本
python3 generator.py generate_script \
  --type short_video \
  --duration 60 \
  --topic "产品介绍" \
  --style "轻松幽默"

# 生成长视频脚本
python3 generator.py generate_script \
  --type long_video \
  --duration 1800 \
  --topic "产品教程" \
  --style "专业详细"
```

### 使用模板

```bash
# 创建模板
python3 generator.py create_template \
  --name "产品介绍模板" \
  --type article \
  --structure "简介,功能,优势,购买"

# 使用模板生成
python3 generator.py use_template \
  --template_id "template_123" \
  --product "智能音箱"
```

### 批量生成

```bash
# 从列表批量生成
python3 generator.py batch_generate \
  --input topics.txt \
  --type blog \
  --output_dir ./articles

# topics.txt格式：
# 人工智能的未来
# 区块链技术解析
# 5G时代的机遇
```

## 配置

配置文件：`config/generator.yaml`

```yaml
# AI配置
ai:
  provider: "openai"  # openai/anthropic/azure
  model: "gpt-4"
  api_key: "your_api_key"
  temperature: 0.8
  max_tokens: 2000

# 品牌配置
brand:
  name: "ABC科技"
  voice: "专业且亲切"
  tone: "专业"
  language: "zh-CN"

# SEO配置
seo:
  enabled: true
  keyword_density: 0.02
  meta_description_length: 160
  title_length: 60

# 内容质量
quality:
  min_word_count: 300
  max_word_count: 3000
  readability_score: 60

# 多语言
languages:
  enabled: true
  default: "zh-CN"
  supported: ["zh-CN", "en-US", "ja-JP", "ko-KR"]

# 输出格式
output:
  format: "markdown"  # markdown/html/plain
  encoding: "utf-8"
  include_meta: true
```

## 模板系统

模板格式：

```yaml
template_id: "article_blog"
name: "博客文章模板"
type: article
structure:
  - section: "标题"
    required: true
  - section: "摘要"
    required: true
  - section: "简介"
    required: true
  - section: "正文"
    subsections:
      - "背景"
      - "分析"
      - "案例"
  - section: "结论"
    required: true
  - section: "行动号召"
    required: false
```

## 内容类型

### 文章类型
- `blog`: 博客文章
- `news`: 新闻稿
- `tutorial`: 教程
- `review`: 评测
- `opinion`: 观点文章

### 文案类型
- `ad`: 广告文案
- `email`: 邮件营销
- `social`: 社交媒体
- `product`: 产品介绍
- `landing`: 落地页

### 视频脚本类型
- `short_video`: 短视频（<1分钟）
- `medium_video`: 中视频（1-10分钟）
- `long_video`: 长视频（>10分钟）
- `tutorial_video`: 教程视频
- `promotional_video`: 宣传视频

## 内容优化

### SEO优化
- 关键词密度控制
- 标题优化
- 元描述生成
- 内链建议
- 外链机会

### 可读性优化
- 句子长度控制
- 段落结构
- 标题层级
- 过渡词使用
- 术语解释

## 输出格式

支持多种输出格式：

- **Markdown**: 用于博客、文档
- **HTML**: 用于网页
- **Plain Text**: 用于邮件、短信
- **JSON**: 用于API集成

## API接口

```python
# 生成文章
POST /api/generate/article
{
  "topic": "人工智能",
  "type": "blog",
  "length": 2000,
  "keywords": ["AI", "机器学习"]
}

# 生成文案
POST /api/generate/copy
{
  "product": "智能手表",
  "type": "ad",
  "platform": "facebook",
  "tone": "专业"
}

# 生成视频脚本
POST /api/generate/script
{
  "type": "short_video",
  "duration": 60,
  "topic": "产品介绍",
  "style": "幽默"
}

# 使用模板
POST /api/generate/template
{
  "template_id": "template_123",
  "variables": {
    "product": "智能音箱",
    "price": "299元"
  }
}
```

## 质量控制

自动质量检查：
- 重复内容检测
- 抄袭检测
- 语言错误检查
- 格式一致性
- 品牌合规性

## 注意事项

1. AI生成的内容需要人工审核
2. 注意版权和法律问题
3. 保持品牌一致性
4. 定期更新模板
5. 监控生成质量
6. 收集反馈优化

## 赚钱价值

- 代写服务：为企业代写内容（月5000-20000元）
- 内容订阅：内容包月订阅服务（月2000-10000元）
- 模板销售：优质内容模板（月1000-5000元）
- 企业解决方案：企业级内容生成系统（月10000-50000元）

预期收益：月10000-50000元
