#!/usr/bin/env python3
"""
UI自动生成器 - 根据配置或自然语言描述生成Web界面
"""

import os
import sys
import json
import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

try:
    from jinja2 import Template, Environment, FileSystemLoader
    HAS_JINJA2 = True
except ImportError:
    HAS_JINJA2 = False


# 预设主题
THEMES = {
    'modern': {
        'primary': '#667eea',
        'secondary': '#764ba2',
        'background': '#f7fafc',
        'text': '#2d3748',
        'border_radius': '8px'
    },
    'dark': {
        'primary': '#667eea',
        'secondary': '#764ba2',
        'background': '#1a202c',
        'text': '#e2e8f0',
        'border_radius': '8px'
    },
    'light': {
        'primary': '#3182ce',
        'secondary': '#2b6cb0',
        'background': '#ffffff',
        'text': '#2d3748',
        'border_radius': '4px'
    },
    'minimalist': {
        'primary': '#000000',
        'secondary': '#333333',
        'background': '#ffffff',
        'text': '#000000',
        'border_radius': '0px'
    }
}


@dataclass
class Theme:
    """主题配置"""
    primary_color: str
    secondary_color: str
    background: str
    text_color: str
    border_radius: str

    @classmethod
    def from_dict(cls, data: Dict) -> 'Theme':
        return cls(
            primary_color=data.get('primary_color', '#667eea'),
            secondary_color=data.get('secondary_color', '#764ba2'),
            background=data.get('background', '#f7fafc'),
            text_color=data.get('text_color', '#2d3748'),
            border_radius=data.get('border_radius', '8px')
        )


class Component:
    """UI组件基类"""

    def __init__(self, component_type: str, config: Dict[str, Any]):
        self.type = component_type
        self.config = config

    def render(self, theme: Theme) -> str:
        """渲染组件"""
        raise NotImplementedError


class Navbar(Component):
    """导航栏组件"""

    def render(self, theme: Theme) -> str:
        brand = self.config.get('brand', 'Brand')
        links = self.config.get('links', [])

        links_html = ''
        for link in links:
            if isinstance(link, str):
                label = link
                url = f'/{link.lower()}'
            else:
                label = link.get('label', link)
                url = link.get('link', f'/{label.lower()}')

            links_html += f'<a href="{url}" class="nav-link">{label}</a>'

        return f'''
<nav class="navbar">
    <div class="container">
        <div class="navbar-brand">{brand}</div>
        <div class="navbar-links">
            {links_html}
        </div>
    </div>
</nav>'''


class Hero(Component):
    """首页大图区域组件"""

    def render(self, theme: Theme) -> str:
        title = self.config.get('title', 'Welcome')
        subtitle = self.config.get('subtitle', '')
        background = self.config.get('background', theme.primary_color)
        button_config = self.config.get('button', {})

        button_html = ''
        if button_config:
            text = button_config.get('text', 'Learn More')
            link = button_config.get('link', '#')
            button_html = f'<a href="{link}" class="hero-button">{text}</a>'

        return f'''
<section class="hero" style="background: linear-gradient(135deg, {background}, {theme.secondary_color})">
    <div class="container">
        <h1 class="hero-title">{title}</h1>
        {f'<p class="hero-subtitle">{subtitle}</p>' if subtitle else ''}
        {button_html}
    </div>
</section>'''


class CardGrid(Component):
    """卡片网格组件"""

    def render(self, theme: Theme) -> str:
        title = self.config.get('title', '')
        cards = self.config.get('cards', [])

        cards_html = ''
        for card in cards:
            cards_html += f'''
            <div class="card">
                <h3 class="card-title">{card.get('title', '')}</h3>
                <p class="card-desc">{card.get('desc', '')}</p>
            </div>'''

        title_html = f'<h2 class="section-title">{title}</h2>' if title else ''

        return f'''
<section class="card-grid-section">
    <div class="container">
        {title_html}
        <div class="card-grid">
            {cards_html}
        </div>
    </div>
</section>'''


class Features(Component):
    """功能展示组件"""

    def render(self, theme: Theme) -> str:
        title = self.config.get('title', 'Features')
        items = self.config.get('items', [])

        items_html = ''
        for item in items:
            icon = item.get('icon', 'star')
            item_title = item.get('title', '')
            desc = item.get('desc', '')

            items_html += f'''
            <div class="feature-item">
                <div class="feature-icon">⭐</div>
                <h3 class="feature-title">{item_title}</h3>
                <p class="feature-desc">{desc}</p>
            </div>'''

        return f'''
<section class="features-section">
    <div class="container">
        <h2 class="section-title">{title}</h2>
        <div class="features-grid">
            {items_html}
        </div>
    </div>
</section>'''


class Pricing(Component):
    """定价方案组件"""

    def render(self, theme: Theme) -> str:
        title = self.config.get('title', 'Pricing')
        plans = self.config.get('plans', [])

        plans_html = ''
        for plan in plans:
            name = plan.get('name', '')
            price = plan.get('price', '')
            features = plan.get('features', [])
            popular = plan.get('popular', False)

            popular_class = 'popular' if popular else ''

            features_html = ''
            for feature in features:
                features_html += f'<li class="pricing-feature">{feature}</li>'

            plans_html += f'''
            <div class="pricing-card {popular_class}">
                {f'<div class="popular-badge">Most Popular</div>' if popular else ''}
                <h3 class="pricing-name">{name}</h3>
                <div class="pricing-price">{price}</div>
                <ul class="pricing-features">
                    {features_html}
                </ul>
                <button class="pricing-button">Choose Plan</button>
            </div>'''

        return f'''
<section class="pricing-section">
    <div class="container">
        <h2 class="section-title">{title}</h2>
        <div class="pricing-grid">
            {plans_html}
        </div>
    </div>
</section>'''


class Footer(Component):
    """页脚组件"""

    def render(self, theme: Theme) -> str:
        links = self.config.get('links', [])

        links_html = ''
        for link in links:
            if isinstance(link, str):
                label = link
                url = f'/{link.lower()}'
            else:
                label = link.get('label', link)
                url = link.get('link', f'/{label.lower()}')

            links_html += f'<a href="{url}" class="footer-link">{label}</a>'

        return f'''
<footer class="footer">
    <div class="container">
        <div class="footer-links">
            {links_html}
        </div>
        <p class="copyright">© 2026 All rights reserved</p>
    </div>
</footer>'''


class Form(Component):
    """表单组件"""

    def render(self, theme: Theme) -> str:
        title = self.config.get('title', 'Form')
        action = self.config.get('action', '#')
        method = self.config.get('method', 'POST')
        fields = self.config.get('fields', [])

        fields_html = ''
        for field in fields:
            field_type = field.get('type', 'text')
            name = field.get('name', '')
            label = field.get('label', name)
            required = field.get('required', False)

            required_html = 'required' if required else ''
            label_required = ' *' if required else ''

            if field_type == 'text':
                fields_html += f'''
                <div class="form-group">
                    <label>{label}{label_required}</label>
                    <input type="text" name="{name}" {required_html}>
                </div>'''

            elif field_type == 'email':
                fields_html += f'''
                <div class="form-group">
                    <label>{label}{label_required}</label>
                    <input type="email" name="{name}" {required_html}>
                </div>'''

            elif field_type == 'password':
                fields_html += f'''
                <div class="form-group">
                    <label>{label}{label_required}</label>
                    <input type="password" name="{name}" {required_html}>
                </div>'''

            elif field_type == 'select':
                options = field.get('options', [])
                options_html = ''
                for opt in options:
                    options_html += f'<option value="{opt}">{opt}</option>'

                fields_html += f'''
                <div class="form-group">
                    <label>{label}</label>
                    <select name="{name}">
                        {options_html}
                    </select>
                </div>'''

            elif field_type == 'textarea':
                rows = field.get('rows', 4)
                fields_html += f'''
                <div class="form-group">
                    <label>{label}</label>
                    <textarea name="{name}" rows="{rows}"></textarea>
                </div>'''

        return f'''
<section class="form-section">
    <div class="container">
        <h2 class="section-title">{title}</h2>
        <form class="ui-form" action="{action}" method="{method}">
            {fields_html}
            <button type="submit" class="form-submit">Submit</button>
        </form>
    </div>
</section>'''


class Table(Component):
    """表格组件"""

    def render(self, theme: Theme) -> str:
        title = self.config.get('title', 'Table')
        columns = self.config.get('columns', [])
        data = self.config.get('data', [])

        # 表头
        headers_html = ''.join([f'<th>{col.get("label", col)}</th>' for col in columns])

        # 表格内容
        rows_html = ''
        for row in data:
            cells_html = ''
            for col in columns:
                key = col.get('key', '')
                value = row.get(key, '')
                cells_html += f'<td>{value}</td>'

            rows_html += f'<tr>{cells_html}</tr>'

        title_html = f'<h2 class="section-title">{title}</h2>' if title else ''

        return f'''
<section class="table-section">
    <div class="container">
        {title_html}
        <table class="ui-table">
            <thead>
                <tr>{headers_html}</tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
</section>'''


class Stats(Component):
    """统计卡片组件"""

    def render(self, theme: Theme) -> str:
        metrics = self.config.get('metrics', [])

        metrics_html = ''
        for metric in metrics:
            label = metric.get('label', '')
            value = metric.get('value', '0')

            metrics_html += f'''
            <div class="stat-card">
                <div class="stat-label">{label}</div>
                <div class="stat-value">{value}</div>
            </div>'''

        return f'''
<section class="stats-section">
    <div class="container">
        <div class="stats-grid">
            {metrics_html}
        </div>
    </div>
</section>'''


# 组件注册表
COMPONENT_CLASSES = {
    'navbar': Navbar,
    'hero': Hero,
    'card_grid': CardGrid,
    'features': Features,
    'pricing': Pricing,
    'footer': Footer,
    'form': Form,
    'table': Table,
    'stats': Stats
}


class Page:
    """页面类"""

    def __init__(self, title: str = 'Page', description: str = '', theme: Theme = None):
        self.title = title
        self.description = description
        self.theme = theme or Theme.from_dict(THEMES['modern'])
        self.components = []
        self.scripts = []

    def add_component(self, config: Dict[str, Any]):
        """添加组件"""
        component_type = config.get('type')

        if component_type in COMPONENT_CLASSES:
            component_class = COMPONENT_CLASSES[component_type]
            component = component_class(component_type, config)
            self.components.append(component)
        else:
            print(f"Warning: Unknown component type: {component_type}")

    def add_script(self, script: Dict[str, Any]):
        """添加脚本"""
        self.scripts.append(script)

    def render(self) -> str:
        """渲染页面"""
        components_html = ''.join([comp.render(self.theme) for comp in self.components])

        # 生成CSS
        css = self._generate_css()

        # 生成JavaScript
        js = self._generate_js()

        return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <meta name="description" content="{self.description}">
    <style>
{css}
    </style>
</head>
<body>
    {components_html}
    <script>
{js}
    </script>
</body>
</html>'''

    def _generate_css(self) -> str:
        """生成CSS样式"""
        return f'''
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    background-color: {self.theme.background};
    color: {self.theme.text};
    line-height: 1.6;
}}

.container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}}

/* Navbar */
.navbar {{
    background: white;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    padding: 1rem 0;
}}

.navbar .container {{
    display: flex;
    justify-content: space-between;
    align-items: center;
}}

.navbar-brand {{
    font-size: 1.5rem;
    font-weight: bold;
    color: {self.theme.primary_color};
}}

.navbar-links {{
    display: flex;
    gap: 2rem;
}}

.nav-link {{
    text-decoration: none;
    color: {self.theme.text};
    transition: color 0.3s;
}}

.nav-link:hover {{
    color: {self.theme.primary_color};
}}

/* Hero */
.hero {{
    padding: 5rem 0;
    color: white;
    text-align: center;
}}

.hero-title {{
    font-size: 3rem;
    margin-bottom: 1rem;
}}

.hero-subtitle {{
    font-size: 1.5rem;
    margin-bottom: 2rem;
    opacity: 0.9;
}}

.hero-button {{
    display: inline-block;
    background: white;
    color: {self.theme.primary_color};
    padding: 1rem 2rem;
    text-decoration: none;
    border-radius: {self.theme.border_radius};
    font-weight: bold;
    transition: transform 0.3s;
}}

.hero-button:hover {{
    transform: translateY(-2px);
}}

/* Section */
.section-title {{
    text-align: center;
    font-size: 2rem;
    margin-bottom: 3rem;
    color: {self.theme.text};
}}

/* Card Grid */
.card-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin: 3rem 0;
}}

.card {{
    background: white;
    padding: 2rem;
    border-radius: {self.theme.border_radius};
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    transition: transform 0.3s;
}}

.card:hover {{
    transform: translateY(-5px);
}}

.card-title {{
    font-size: 1.25rem;
    margin-bottom: 1rem;
    color: {self.theme.primary_color};
}}

/* Features */
.features-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 2rem;
    margin: 3rem 0;
}}

.feature-item {{
    text-align: center;
    padding: 2rem;
}}

.feature-icon {{
    font-size: 3rem;
    margin-bottom: 1rem;
}}

.feature-title {{
    font-size: 1.25rem;
    margin-bottom: 0.5rem;
}}

/* Pricing */
.pricing-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin: 3rem 0;
}}

.pricing-card {{
    background: white;
    padding: 2rem;
    border-radius: {self.theme.border_radius};
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    text-align: center;
    position: relative;
}}

.pricing-card.popular {{
    border: 2px solid {self.theme.primary_color};
}}

.popular-badge {{
    position: absolute;
    top: -12px;
    left: 50%;
    transform: translateX(-50%);
    background: {self.theme.primary_color};
    color: white;
    padding: 0.25rem 1rem;
    border-radius: 20px;
    font-size: 0.875rem;
}}

.pricing-name {{
    font-size: 1.5rem;
    margin-bottom: 1rem;
}}

.pricing-price {{
    font-size: 2.5rem;
    font-weight: bold;
    color: {self.theme.primary_color};
    margin-bottom: 1.5rem;
}}

.pricing-features {{
    list-style: none;
    margin-bottom: 2rem;
    text-align: left;
}}

.pricing-feature {{
    padding: 0.5rem 0;
}}

.pricing-button {{
    background: {self.theme.primary_color};
    color: white;
    border: none;
    padding: 0.75rem 2rem;
    border-radius: {self.theme.border_radius};
    cursor: pointer;
    transition: background 0.3s;
}}

.pricing-button:hover {{
    background: {self.theme.secondary_color};
}}

/* Form */
.form-section {{
    padding: 3rem 0;
}}

.ui-form {{
    max-width: 500px;
    margin: 0 auto;
}}

.form-group {{
    margin-bottom: 1.5rem;
}}

.form-group label {{
    display: block;
    margin-bottom: 0.5rem;
    font-weight: bold;
}}

.form-group input,
.form-group select,
.form-group textarea {{
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: {self.theme.border_radius};
    font-size: 1rem;
}}

.form-submit {{
    background: {self.theme.primary_color};
    color: white;
    border: none;
    padding: 1rem 2rem;
    border-radius: {self.theme.border_radius};
    cursor: pointer;
    font-size: 1rem;
    width: 100%;
}}

/* Table */
.ui-table {{
    width: 100%;
    border-collapse: collapse;
    margin: 2rem 0;
    background: white;
}}

.ui-table th,
.ui-table td {{
    padding: 1rem;
    text-align: left;
    border-bottom: 1px solid #eee;
}}

.ui-table th {{
    background: {self.theme.primary_color};
    color: white;
    font-weight: bold;
}}

/* Stats */
.stats-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 2rem;
    margin: 3rem 0;
}}

.stat-card {{
    background: white;
    padding: 2rem;
    border-radius: {self.theme.border_radius};
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    text-align: center;
}}

.stat-label {{
    font-size: 1rem;
    color: #666;
    margin-bottom: 0.5rem;
}}

.stat-value {{
    font-size: 2.5rem;
    font-weight: bold;
    color: {self.theme.primary_color};
}}

/* Footer */
.footer {{
    background: {self.theme.text};
    color: white;
    padding: 2rem 0;
    margin-top: 3rem;
    text-align: center;
}}

.footer-links {{
    margin-bottom: 1rem;
}}

.footer-link {{
    color: white;
    text-decoration: none;
    margin: 0 1rem;
}}

.copyright {{
    opacity: 0.7;
}}

/* Responsive */
@media (max-width: 768px) {{
    .navbar .container {{
        flex-direction: column;
    }}

    .navbar-links {{
        flex-direction: column;
        gap: 1rem;
        margin-top: 1rem;
    }}

    .hero-title {{
        font-size: 2rem;
    }}

    .card-grid,
    .features-grid,
    .pricing-grid,
    .stats-grid {{
        grid-template-columns: 1fr;
    }}
}}
'''

    def _generate_js(self) -> str:
        """生成JavaScript代码"""
        js = '// Auto-generated JavaScript\n'

        for script in self.scripts:
            script_type = script.get('type', '')

            if script_type == 'toggle':
                selector = script.get('selector', '')
                trigger = script.get('trigger', '')

                js += f'''
document.querySelector('{trigger}').addEventListener('click', function() {{
    document.querySelector('{selector}').classList.toggle('active');
}});
'''

            elif script_type == 'scroll':
                js += '''
window.addEventListener('scroll', function() {
    const elements = document.querySelectorAll('.card, .feature-item');
    elements.forEach(function(element) {
        const position = element.getBoundingClientRect();
        if (position.top < window.innerHeight - 100) {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }
    });
});
'''

        return js

    def generate_html(self, output_path: str = None) -> str:
        """生成HTML并保存到文件"""
        html = self.render()

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)

        return html


class UIGenerator:
    """UI生成器"""

    def __init__(self, theme: str = 'modern' or Dict = None):
        if isinstance(theme, dict):
            self.theme = Theme.from_dict(theme)
        else:
            self.theme = Theme.from_dict(THEMES.get(theme, THEMES['modern']))

        self.template_dir = None

    def create_page(self, title: str = 'Page', description: str = '') -> Page:
        """创建页面"""
        return Page(title=title, description=description, theme=self.theme)

    def create_layout(self, type: str = 'dashboard', theme: str = None) -> Page:
        """创建布局"""
        if theme:
            self.theme = Theme.from_dict(THEMES.get(theme, THEMES['modern']))

        page = self.create_page(title=f'{type.capitalize()} Layout')

        if type == 'dashboard':
            # 添加侧边栏
            page.add_component({
                'type': 'navbar',
                'brand': 'Dashboard',
                'links': ['Home', 'Analytics', 'Users', 'Settings']
            })

        return page

    def create_form(self, title: str = 'Form', action: str = '#', method: str = 'POST') -> Page:
        """创建表单页面"""
        page = self.create_page(title=title)
        page.add_component({
            'type': 'navbar',
            'brand': 'App',
            'links': ['Home']
        })
        return page

    def create_table(self, title: str = 'Table', columns: List = None, data: List = None) -> Page:
        """创建表格页面"""
        page = self.create_page(title=title)
        page.add_component({
            'type': 'table',
            'title': title,
            'columns': columns or [],
            'data': data or []
        })
        return page

    def generate_from_config(self, config_path: str, output_path: str = None) -> str:
        """从配置文件生成UI"""
        # 读取配置
        with open(config_path, 'r', encoding='utf-8') as f:
            if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                config = yaml.safe_load(f)
            else:
                config = json.load(f)

        # 创建页面
        page_config = config.get('page', {})
        page = self.create_page(
            title=page_config.get('title', 'Page'),
            description=page_config.get('description', '')
        )

        # 添加组件
        components = config.get('components', [])
        for comp in components:
            page.add_component(comp)

        # 生成HTML
        html = page.generate_html(output_path)

        return html

    def load_template(self, template_path: str):
        """加载自定义模板"""
        self.template_dir = os.path.dirname(template_path)

    def render_template(self, data: Dict, output_path: str = None) -> str:
        """渲染模板"""
        if not HAS_JINJA2:
            raise ImportError('Jinja2 is required for template rendering')

        if not self.template_dir:
            raise ValueError('No template loaded. Call load_template() first.')

        env = Environment(loader=FileSystemLoader(self.template_dir))
        template = env.get_template(os.path.basename(self.template_dir) + '.html')

        html = template.render(data)

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)

        return html


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='UI自动生成器')
    parser.add_argument('action', choices=['generate', 'create', 'preview'])
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--output', default='output.html', help='输出文件路径')
    parser.add_argument('--type', help='创建类型')
    parser.add_argument('--fields', help='表单字段（逗号分隔）')
    parser.add_argument('--theme', default='modern', help='主题')

    args = parser.parse_args()

    generator = UIGenerator(theme=args.theme)

    if args.action == 'generate':
        if not args.config:
            print('Error: --config is required for generate action')
            sys.exit(1)

        html = generator.generate_from_config(args.config, args.output)
        print(f'Generated: {args.output}')

    elif args.action == 'create':
        if args.type == 'form' and args.fields:
            page = generator.create_form(title='Auto Form')

            fields = args.fields.split(',')
            for field in fields:
                field_type = 'text' if '@' not in field else 'email'
                page.add_component({
                    'type': 'form',
                    'fields': [{
                        'type': field_type,
                        'name': field.lower(),
                        'label': field.capitalize(),
                        'required': True
                    }]
                })

            page.generate_html(args.output)
            print(f'Created: {args.output}')

        elif args.type == 'dashboard':
            page = generator.create_layout(type='dashboard')
            page.generate_html(args.output)
            print(f'Created: {args.output}')

        else:
            print(f'Unknown type: {args.type}')

    elif args.action == 'preview':
        print(f'Open {args.output} in your browser')


if __name__ == '__main__':
    main()
