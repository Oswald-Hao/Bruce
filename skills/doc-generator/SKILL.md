# Doc Generator - 文档自动生成器

## 功能描述

自动生成各种类型的文档，包括API文档、使用说明、技术文档、README文件等，支持从代码、注释和配置文件中提取信息。

## 安装依赖

```bash
pip install jinja2 pyyaml markdown
```

## 使用方法

### API文档生成

```python
from doc_generator import DocGenerator

# 创建文档生成器
generator = DocGenerator()

# 从Python代码生成API文档
api_doc = generator.generate_api_doc(
    code_path='./src/my_api.py',
    output_path='./docs/api.md',
    format='markdown'
)

# 从OpenAPI规范生成文档
openapi_doc = generator.generate_openapi_doc(
    spec_path='./openapi.yaml',
    output_path='./docs/openapi.md'
)
```

### README文件生成

```python
from doc_generator import DocGenerator

generator = DocGenerator()

# 生成项目README
readme = generator.generate_readme(
    project_name='MyProject',
    description='An awesome project',
    features=['Feature 1', 'Feature 2', 'Feature 3'],
    installation='pip install myproject',
    usage='from myproject import main\nmain()',
    output_path='./README.md'
)
```

### 技术文档生成

```python
from doc_generator import DocGenerator

generator = DocGenerator()

# 生成技术文档
tech_doc = generator.generate_tech_doc(
    title='Architecture Documentation',
    sections=[
        {'title': 'Overview', 'content': 'System overview...'},
        {'title': 'Components', 'content': 'Component descriptions...'},
        {'title': 'API', 'content': 'API reference...'}
    ],
    output_path='./docs/architecture.md'
)
```

### 代码注释文档生成

```python
from doc_generator import DocGenerator

generator = DocGenerator()

# 从代码注释生成文档
doc = generator.generate_from_comments(
    code_path='./src',
    output_path='./docs/code_docs.md',
    include_private=False
)
```

### 用户手册生成

```python
from doc_generator import DocGenerator

generator = DocGenerator()

# 生成用户手册
manual = generator.generate_user_manual(
    title='User Manual',
    chapters=[
        {'title': 'Getting Started', 'content': 'Installation guide...'},
        {'title': 'Basic Usage', 'content': 'How to use...'},
        {'title': 'Advanced Features', 'content': 'Advanced usage...'},
        {'title': 'Troubleshooting', 'content': 'Common issues...'}
    ],
    output_path='./docs/manual.md'
)
```

### 从配置生成文档

创建 `doc_config.yaml`:

```yaml
# 文档配置

document:
  title: "Project Documentation"
  author: "Developer"
  version: "1.0.0"

output:
  format: markdown
  path: "./docs/README.md"

sections:
  - type: title
    content: "Introduction"

  - type: description
    content: "This is a comprehensive documentation."

  - type: installation
    command: "pip install myproject"

  - type: usage
    code: |
    from myproject import main
    main()

  - type: features
    items:
      - Fast and efficient
      - Easy to use
      - Well documented

  - type: api
    path: "./src/api.py"

  - type: changelog
    versions:
      - version: "1.0.0"
        date: "2026-01-01"
        changes:
          - Initial release
```

生成文档：

```python
from doc_generator import DocGenerator

generator = DocGenerator()

# 从配置文件生成文档
doc = generator.generate_from_config(
    config_path='doc_config.yaml'
)
```

## 文档模板

### API文档模板

```python
# 自动提取API端点、参数、返回值等信息
api_doc = generator.generate_api_doc(
    code_path='./api.py',
    output_path='./docs/api.md',
    include_examples=True,
    include_auth=True
)
```

### README模板

支持多种README模板：
- Basic（基础版）
- Detailed（详细版）
- Open Source（开源项目版）
- Commercial（商业项目版）

```python
# 生成不同风格的README
readme = generator.generate_readme(
    template='open_source',  # basic, detailed, open_source, commercial
    project_name='MyProject',
    output_path='./README.md'
)
```

## 代码分析

### Python代码分析

```python
# 分析Python代码并生成文档
doc = generator.analyze_python_code(
    code_path='./src',
    output_path='./docs/python_api.md',
    include_types=True,
    include_methods=True,
    include_examples=True
)
```

### JavaScript代码分析

```python
# 分析JavaScript代码并生成文档
doc = generator.analyze_javascript_code(
    code_path='./src',
    output_path='./docs/js_api.md',
    include_types=True,
    include_examples=True
)
```

## 文档格式支持

- Markdown (.md)
- HTML (.html)
- PDF (.pdf) - 需要额外配置
- ReStructuredText (.rst)

```python
# 生成不同格式的文档
doc = generator.generate_readme(
    output_path='./README.md',
    format='markdown'  # markdown, html, rst
)

# 同时生成多种格式
docs = generator.generate_multi_format(
    config_path='doc_config.yaml',
    formats=['markdown', 'html', 'rst']
)
```

## 高级功能

### 自定义模板

```python
# 创建自定义模板
custom_template = """
# {{ title }}

{{ description }}

## Installation
{{ installation }}

## Usage
{{ usage }}
"""

# 使用自定义模板
doc = generator.generate_with_template(
    template=custom_template,
    data={
        'title': 'My Project',
        'description': 'Description here',
        'installation': 'pip install myproject',
        'usage': 'from myproject import main'
    },
    output_path='./README.md'
)
```

### 文档生成器链

```python
# 创建文档生成器链
chain = DocGenerator()

# 1. 生成API文档
chain.generate_api_doc('./src/api.py', './docs/api.md')

# 2. 生成用户手册
chain.generate_user_manual(
    title='User Manual',
    chapters=[...],
    output_path='./docs/manual.md'
)

# 3. 生成索引文档
chain.generate_index(
    docs=['api.md', 'manual.md', 'architecture.md'],
    output_path='./docs/INDEX.md'
)
```

### 自动更新

```python
# 自动更新文档
generator = DocGenerator()

# 监控代码变化并自动更新文档
generator.watch_and_update(
    code_path='./src',
    doc_path='./docs',
    interval=60  # 每60秒检查一次
)
```

## 命令行工具

```bash
# 生成README
doc-generator readme --name "MyProject" --output README.md

# 生成API文档
doc-generator api --code ./src/api.py --output ./docs/api.md

# 从配置生成
doc-generator generate --config doc_config.yaml

# 生成所有文档
doc-generator all --config doc_config.yaml

# 验证文档
doc-generator validate ./docs/
```

## 配置选项

### 全局配置

```yaml
# doc_generator_config.yaml

project:
  name: "MyProject"
  version: "1.0.0"
  author: "Developer"
  email: "dev@example.com"

documentation:
  output_dir: "./docs"
  default_format: "markdown"
  include_private: false
  include_examples: true

api_docs:
  include_types: true
  include_methods: true
  include_params: true
  include_returns: true
  include_auth: true

readme:
  template: "detailed"  # basic, detailed, open_source, commercial
  sections:
    - title
    - description
    - installation
    - usage
    - features
    - api_docs
    - contributing
    - license
```

## 使用建议

1. **保持文档更新：** 使用watch功能自动更新文档
2. **使用模板：** 利用预设模板快速生成文档
3. **配置驱动：** 使用配置文件管理文档结构
4. **多格式输出：** 同时生成多种格式以适应不同需求
5. **代码注释：** 在代码中添加详细的注释和docstring
6. **示例代码：** 在文档中包含使用示例

## 依赖说明

- jinja2: 模板引擎
- pyyaml: YAML配置解析
- markdown: Markdown格式支持

## 核心价值

**对效率提升的贡献：**
1. **自动化：** 自动从代码生成文档
2. **一致性：** 统一的文档格式和风格
3. **准确性：** 从代码中提取准确信息
4. **节省时间：** 大幅减少文档编写时间

**应用场景：**
- API文档生成
- README自动生成
- 技术文档编写
- 用户手册制作
- 代码注释文档
