#!/usr/bin/env python3
"""
UI生成器的测试用例
"""

import sys
import os
import tempfile
import shutil

# 添加技能目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui_generator import (
    UIGenerator,
    Page,
    Theme,
    Navbar,
    Hero,
    CardGrid,
    Features,
    Pricing,
    Footer,
    Form,
    Table,
    Stats
)


def test_basic_page_generation():
    """测试基础页面生成"""
    print("测试1: 基础页面生成...")

    generator = UIGenerator()
    page = generator.create_page(title='Test Page', description='Test Description')

    html = page.generate_html()

    assert 'Test Page' in html
    assert 'Test Description' in html
    assert '<!DOCTYPE html>' in html

    print("✅ 基础页面生成测试通过")


def test_navbar_component():
    """测试导航栏组件"""
    print("测试2: 导航栏组件...")

    navbar = Navbar('navbar', {
        'brand': 'MyBrand',
        'links': ['Home', 'About', 'Contact']
    })

    theme = Theme.from_dict({'primary_color': '#667eea', 'secondary_color': '#764ba2', 'background': '#f7fafc', 'text_color': '#2d3748', 'border_radius': '8px'})
    html = navbar.render(theme)

    assert 'MyBrand' in html
    assert 'Home' in html
    assert 'About' in html
    assert 'Contact' in html
    assert 'navbar' in html

    print("✅ 导航栏组件测试通过")


def test_hero_component():
    """测试Hero组件"""
    print("测试3: Hero组件...")

    hero = Hero('hero', {
        'title': 'Welcome to My Site',
        'subtitle': 'The best experience ever',
        'background': '#667eea',
        'button': {'text': 'Get Started', 'link': '/start'}
    })

    theme = Theme.from_dict({'primary_color': '#667eea', 'secondary_color': '#764ba2', 'background': '#f7fafc', 'text_color': '#2d3748', 'border_radius': '8px'})
    html = hero.render(theme)

    assert 'Welcome to My Site' in html
    assert 'The best experience ever' in html
    assert 'Get Started' in html
    assert 'hero' in html

    print("✅ Hero组件测试通过")


def test_card_grid_component():
    """测试卡片网格组件"""
    print("测试4: 卡片网格组件...")

    card_grid = CardGrid('card_grid', {
        'title': 'Features',
        'cards': [
            {'title': 'Feature 1', 'desc': 'Description 1'},
            {'title': 'Feature 2', 'desc': 'Description 2'},
            {'title': 'Feature 3', 'desc': 'Description 3'}
        ]
    })

    theme = Theme.from_dict({'primary_color': '#667eea', 'secondary_color': '#764ba2', 'background': '#f7fafc', 'text_color': '#2d3748', 'border_radius': '8px'})
    html = card_grid.render(theme)

    assert 'Features' in html
    assert 'Feature 1' in html
    assert 'Feature 2' in html
    assert 'Feature 3' in html
    assert 'card-grid' in html

    print("✅ 卡片网格组件测试通过")


def test_features_component():
    """测试功能展示组件"""
    print("测试5: 功能展示组件...")

    features = Features('features', {
        'title': 'Our Features',
        'items': [
            {'icon': 'star', 'title': 'Fast', 'desc': 'Very fast'},
            {'icon': 'rocket', 'title': 'Powerful', 'desc': 'Very powerful'}
        ]
    })

    theme = Theme.from_dict({'primary_color': '#667eea', 'secondary_color': '#764ba2', 'background': '#f7fafc', 'text_color': '#2d3748', 'border_radius': '8px'})
    html = features.render(theme)

    assert 'Our Features' in html
    assert 'Fast' in html
    assert 'Powerful' in html

    print("✅ 功能展示组件测试通过")


def test_pricing_component():
    """测试定价组件"""
    print("测试6: 定价组件...")

    pricing = Pricing('pricing', {
        'title': 'Pricing Plans',
        'plans': [
            {
                'name': 'Basic',
                'price': '$9',
                'features': ['Feature 1', 'Feature 2']
            },
            {
                'name': 'Pro',
                'price': '$19',
                'features': ['Feature 1', 'Feature 2', 'Feature 3'],
                'popular': True
            }
        ]
    })

    theme = Theme.from_dict({'primary_color': '#667eea', 'secondary_color': '#764ba2', 'background': '#f7fafc', 'text_color': '#2d3748', 'border_radius': '8px'})
    html = pricing.render(theme)

    assert 'Pricing Plans' in html
    assert 'Basic' in html
    assert '$9' in html
    assert 'Pro' in html
    assert '$19' in html
    assert 'Most Popular' in html

    print("✅ 定价组件测试通过")


def test_footer_component():
    """测试页脚组件"""
    print("测试7: 页脚组件...")

    footer = Footer('footer', {
        'links': ['Privacy', 'Terms', 'Contact']
    })

    theme = Theme.from_dict({'primary_color': '#667eea', 'secondary_color': '#764ba2', 'background': '#f7fafc', 'text_color': '#2d3748', 'border_radius': '8px'})
    html = footer.render(theme)

    assert 'Privacy' in html
    assert 'Terms' in html
    assert 'Contact' in html
    assert 'footer' in html

    print("✅ 页脚组件测试通过")


def test_form_component():
    """测试表单组件"""
    print("测试8: 表单组件...")

    form = Form('form', {
        'title': 'Contact Form',
        'action': '/contact',
        'method': 'POST',
        'fields': [
            {'type': 'text', 'name': 'name', 'label': 'Name', 'required': True},
            {'type': 'email', 'name': 'email', 'label': 'Email', 'required': True},
            {'type': 'textarea', 'name': 'message', 'label': 'Message', 'rows': 5}
        ]
    })

    theme = Theme.from_dict({'primary_color': '#667eea', 'secondary_color': '#764ba2', 'background': '#f7fafc', 'text_color': '#2d3748', 'border_radius': '8px'})
    html = form.render(theme)

    assert 'Contact Form' in html
    assert 'Name' in html
    assert 'Email' in html
    assert 'Message' in html
    assert '/contact' in html

    print("✅ 表单组件测试通过")


def test_table_component():
    """测试表格组件"""
    print("测试9: 表格组件...")

    table = Table('table', {
        'title': 'User List',
        'columns': [
            {'key': 'id', 'label': 'ID'},
            {'key': 'name', 'label': 'Name'},
            {'key': 'email', 'label': 'Email'}
        ],
        'data': [
            {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'},
            {'id': 2, 'name': 'Bob', 'email': 'bob@example.com'}
        ]
    })

    theme = Theme.from_dict({'primary_color': '#667eea', 'secondary_color': '#764ba2', 'background': '#f7fafc', 'text_color': '#2d3748', 'border_radius': '8px'})
    html = table.render(theme)

    assert 'User List' in html
    assert 'Alice' in html
    assert 'Bob' in html
    assert 'alice@example.com' in html

    print("✅ 表格组件测试通过")


def test_stats_component():
    """测试统计组件"""
    print("测试10: 统计组件...")

    stats = Stats('stats', {
        'metrics': [
            {'label': 'Users', 'value': '1,234'},
            {'label': 'Revenue', 'value': '$45,678'}
        ]
    })

    theme = Theme.from_dict({'primary_color': '#667eea', 'secondary_color': '#764ba2', 'background': '#f7fafc', 'text_color': '#2d3748', 'border_radius': '8px'})
    html = stats.render(theme)

    assert 'Users' in html
    assert '1,234' in html
    assert 'Revenue' in html
    assert '$45,678' in html

    print("✅ 统计组件测试通过")


def test_full_page_generation():
    """测试完整页面生成"""
    print("测试11: 完整页面生成...")

    generator = UIGenerator()
    page = generator.create_page(title='My Website', description='Awesome website')

    # 添加多个组件
    page.add_component({
        'type': 'navbar',
        'brand': 'MyBrand',
        'links': ['Home', 'About']
    })

    page.add_component({
        'type': 'hero',
        'title': 'Welcome',
        'subtitle': 'Best experience',
        'button': {'text': 'Start', 'link': '/start'}
    })

    page.add_component({
        'type': 'features',
        'title': 'Features',
        'items': [
            {'icon': 'star', 'title': 'Feature 1', 'desc': 'Desc 1'}
        ]
    })

    html = page.generate_html()

    assert 'My Website' in html
    assert 'MyBrand' in html
    assert 'Welcome' in html
    assert 'Features' in html
    assert 'Feature 1' in html

    print("✅ 完整页面生成测试通过")


def test_theme_customization():
    """测试主题定制"""
    print("测试12: 主题定制...")

    custom_theme = {
        'primary_color': '#ff0000',
        'secondary_color': '#00ff00',
        'background': '#000000',
        'text_color': '#ffffff',
        'border_radius': '10px'
    }

    generator = UIGenerator(theme=custom_theme)
    page = generator.create_page(title='Themed Page')

    html = page.generate_html()

    assert '#ff0000' in html
    assert '#00ff00' in html
    assert '#000000' in html
    assert '#ffffff' in html

    print("✅ 主题定制测试通过")


def test_file_output():
    """测试文件输出"""
    print("测试13: 文件输出...")

    # 创建临时目录
    temp_dir = tempfile.mkdtemp()

    try:
        generator = UIGenerator()
        page = generator.create_page(title='Test Output')

        output_path = os.path.join(temp_dir, 'test.html')
        page.generate_html(output_path)

        assert os.path.exists(output_path)

        with open(output_path, 'r') as f:
            content = f.read()
            assert 'Test Output' in content

        print("✅ 文件输出测试通过")

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)


def test_config_based_generation():
    """测试基于配置的生成"""
    print("测试14: 基于配置的生成...")

    # 创建临时配置文件
    temp_dir = tempfile.mkdtemp()

    try:
        config_path = os.path.join(temp_dir, 'config.yaml')

        import yaml
        config = {
            'page': {
                'title': 'Config Generated',
                'description': 'From YAML config'
            },
            'components': [
                {
                    'type': 'navbar',
                    'brand': 'ConfigBrand',
                    'links': ['Home']
                },
                {
                    'type': 'hero',
                    'title': 'From Config',
                    'subtitle': 'YAML powered'
                }
            ]
        }

        with open(config_path, 'w') as f:
            yaml.dump(config, f)

        generator = UIGenerator()
        html = generator.generate_from_config(config_path)

        assert 'Config Generated' in html
        assert 'ConfigBrand' in html
        assert 'From Config' in html

        print("✅ 基于配置的生成测试通过")

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)


def test_different_themes():
    """测试不同主题"""
    print("测试15: 不同主题...")

    themes = ['modern', 'dark', 'light', 'minimalist']

    for theme_name in themes:
        generator = UIGenerator(theme=theme_name)
        page = generator.create_page(title=f'{theme_name.title()} Theme')
        html = page.generate_html()

        assert f'{theme_name.title()} Theme' in html

    print("✅ 不同主题测试通过")


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("开始测试UI生成器")
    print("=" * 60)

    tests = [
        test_basic_page_generation,
        test_navbar_component,
        test_hero_component,
        test_card_grid_component,
        test_features_component,
        test_pricing_component,
        test_footer_component,
        test_form_component,
        test_table_component,
        test_stats_component,
        test_full_page_generation,
        test_theme_customization,
        test_file_output,
        test_config_based_generation,
        test_different_themes,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            failed += 1
            print(f"❌ 测试失败: {test.__name__}")
            print(f"   错误: {e}")
        except Exception as e:
            failed += 1
            print(f"❌ 测试异常: {test.__name__}")
            print(f"   错误: {e}")

    print("=" * 60)
    print(f"测试完成: {passed} 通过, {failed} 失败")
    print("=" * 60)

    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
