# UI Generator - UI自动生成器

## 功能描述

根据自然语言描述或配置文件自动生成Web界面、移动端界面和桌面应用界面，支持快速原型设计和现代化UI框架。

## 安装依赖

```bash
pip install jinja2 pyyaml beautifulsoup4
```

## 使用方法

### 基础HTML生成

```python
from ui_generator import UIGenerator

# 创建UI生成器
generator = UIGenerator()

# 定义页面结构
page = generator.create_page(
    title='我的应用',
    description='这是一个自动生成的页面'
)

# 添加组件
page.add_component({
    'type': 'navbar',
    'brand': 'MyApp',
    'links': ['首页', '关于', '联系']
})

page.add_component({
    'type': 'hero',
    'title': '欢迎使用',
    'subtitle': '快速构建现代化界面',
    'button': '开始使用'
})

page.add_component({
    'type': 'card_grid',
    'cards': [
        {'title': '功能1', 'desc': '描述1'},
        {'title': '功能2', 'desc': '描述2'},
        {'title': '功能3', 'desc': '描述3'}
    ]
})

# 生成HTML
html = page.generate_html(output_path='index.html')
```

### 响应式布局生成

```python
from ui_generator import UIGenerator

generator = UIGenerator()

# 创建响应式布局
layout = generator.create_layout(
    type='dashboard',
    theme='modern'
)

# 添加侧边栏
layout.add_sidebar({
    'items': [
        {'icon': 'home', 'label': '首页', 'link': '/'},
        {'icon': 'users', 'label': '用户', 'link': '/users'},
        {'icon': 'settings', 'label': '设置', 'link': '/settings'}
    ]
})

# 添加主内容区
layout.add_content({
    'type': 'stats',
    'metrics': [
        {'label': '用户数', 'value': '1,234'},
        {'label': '收入', 'value': '¥45,678'},
        {'label': '订单', 'value': '89'}
    ]
})

# 生成HTML
html = layout.generate_html(output_path='dashboard.html')
```

### 表单生成

```python
from ui_generator import UIGenerator

generator = UIGenerator()

# 创建表单
form = generator.create_form(
    title='用户注册',
    action='/register',
    method='POST'
)

# 添加表单字段
form.add_field({
    'type': 'text',
    'name': 'username',
    'label': '用户名',
    'required': True
})

form.add_field({
    'type': 'email',
    'name': 'email',
    'label': '邮箱',
    'required': True
})

form.add_field({
    'type': 'password',
    'name': 'password',
    'label': '密码',
    'required': True
})

form.add_field({
    'type': 'select',
    'name': 'role',
    'label': '角色',
    'options': ['用户', '管理员', 'VIP']
})

form.add_field({
    'type': 'textarea',
    'name': 'bio',
    'label': '简介',
    'rows': 4
})

# 生成HTML
html = form.generate_html(output_path='form.html')
```

### 数据表格生成

```python
from ui_generator import UIGenerator

generator = UIGenerator()

# 创建表格
table = generator.create_table(
    title='用户列表',
    columns=[
        {'key': 'id', 'label': 'ID'},
        {'key': 'name', 'label': '姓名'},
        {'key': 'email', 'label': '邮箱'},
        {'key': 'role', 'label': '角色'}
    ],
    data=[
        {'id': 1, 'name': '张三', 'email': 'zhang@example.com', 'role': '用户'},
        {'id': 2, 'name': '李四', 'email': 'li@example.com', 'role': '管理员'},
        {'id': 3, 'name': '王五', 'email': 'wang@example.com', 'role': 'VIP'}
    ]
)

# 生成HTML
html = table.generate_html(output_path='table.html')
```

### 使用配置文件生成

创建 `ui_config.yaml`:

```yaml
# UI配置文件

page:
  title: "我的网站"
  description: "自动生成的现代化网站"
  theme: "modern"

components:
  - type: navbar
    brand: "MyBrand"
    links:
      - label: 首页
        link: /
      - label: 产品
        link: /products
      - label: 关于
        link: /about

  - type: hero
    title: "欢迎来到我们的网站"
    subtitle: "提供优质的服务和产品"
    background: "#667eea"
    button:
      text: "立即开始"
      link: /start

  - type: features
    title: "我们的特色"
    items:
      - icon: star
        title: "功能强大"
        desc: "提供丰富的功能"
      - icon: rocket
        title: "快速响应"
        desc: "优化的性能"
      - icon: shield
        title: "安全可靠"
        desc: "数据安全保障"

  - type: pricing
    title: "定价方案"
    plans:
      - name: 基础版
        price: "¥99"
        features: ["功能1", "功能2"]
      - name: 专业版
        price: "¥199"
        features: ["功能1", "功能2", "功能3"]
        popular: true
      - name: 企业版
        price: "¥399"
        features: ["所有功能", "专属支持"]

  - type: footer
    links:
      - label: 隐私政策
        link: /privacy
      - label: 服务条款
        link: /terms
```

生成UI：

```python
from ui_generator import UIGenerator

generator = UIGenerator()

# 从配置文件生成
html = generator.generate_from_config(
    config_path='ui_config.yaml',
    output_path='index.html'
)
```

### 组件库

#### 支持的组件

1. **Navbar** - 导航栏
2. **Hero** - 首页大图区域
3. **Card Grid** - 卡片网格
4. **Features** - 功能展示
5. **Pricing** - 定价方案
6. **Testimonials** - 用户评价
7. **FAQ** - 常见问题
8. **Contact** - 联系表单
9. **Footer** - 页脚
10. **Sidebar** - 侧边栏
11. **Table** - 数据表格
12. **Form** - 表单
13. **Stats** - 统计卡片
14. **Timeline** - 时间线
15. **Gallery** - 图片画廊

## 主题定制

### 预设主题

```python
# 使用预设主题
generator = UIGenerator(theme='dark')  # dark, light, modern, minimalist
```

### 自定义主题

```python
custom_theme = {
    'primary_color': '#667eea',
    'secondary_color': '#764ba2',
    'background': '#f7fafc',
    'text_color': '#2d3748',
    'border_radius': '8px'
}

generator = UIGenerator(theme=custom_theme)
```

## 交互功能

### JavaScript集成

```python
from ui_generator import UIGenerator

generator = UIGenerator()

# 添加交互功能
page.add_script({
    'type': 'toggle',
    'selector': '#mobile-menu',
    'trigger': '#menu-button'
})

page.add_script({
    'type': 'scroll',
    'animation': 'fade-in'
})

# 生成带交互的HTML
html = page.generate_html(
    output_path='index.html',
    include_js=True
)
```

## 命令行工具

```bash
# 从配置文件生成
ui-generator generate --config ui_config.yaml --output index.html

# 生成指定类型
ui-generator create --type dashboard --output dashboard.html

# 生成表单
ui-generator create-form --fields name,email,password --output form.html

# 预览生成的页面
ui-generator preview index.html
```

## 模板系统

### 使用自定义模板

```python
from ui_generator import UIGenerator

generator = UIGenerator()

# 加载自定义模板
generator.load_template('my_template.html')

# 填充模板数据
data = {
    'title': '我的页面',
    'content': '页面内容'
}

html = generator.render_template(data, output_path='output.html')
```

### 创建模板

模板使用Jinja2语法：

```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ page.title }}</title>
</head>
<body>
    <h1>{{ page.title }}</h1>
    <div class="content">
        {% for component in page.components %}
            {{ component }}
        {% endfor %}
    </div>
</body>
</html>
```

## 使用建议

1. **快速原型：** 使用配置文件快速生成页面
2. **组件组合：** 灵活组合各种组件
3. **主题定制：** 使用主题系统保持一致性
4. **响应式：** 自动生成响应式布局
5. **可扩展：** 添加自定义组件和模板

## 依赖说明

- jinja2: 模板引擎
- pyyaml: YAML配置解析
- beautifulsoup4: HTML解析和处理

## 核心价值

**对效率提升的贡献：**
1. **快速开发：** 快速生成界面原型
2. **一致风格：** 统一的设计风格
3. **响应式：** 自动适配各种设备
4. **可定制：** 灵活的主题和组件系统

**应用场景：**
- 快速原型设计
- 管理后台界面
- 落地页生成
- 文档页面
- 仪表板界面
