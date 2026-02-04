# Auto Test Framework - 自动化测试框架增强

## 功能描述

提供全面的自动化测试能力，包括单元测试、集成测试、性能测试和UI测试，帮助提升代码质量和开发效率。

## 安装依赖

```bash
pip install pytest pytest-cov pytest-asyncio pytest-mock requests httpx selenium playwright
```

## 使用方法

### 单元测试

```python
from auto_test_framework import UnitTest

# 创建单元测试
test = UnitTest()

# 添加测试用例
test.add_test({
    'name': 'test_addition',
    'code': '''
def test_addition():
    assert 2 + 2 == 4
    assert 1 + 1 != 3
''',
    'type': 'function'
})

# 运行测试
result = test.run()
print(result)
```

### 集成测试

```python
from auto_test_framework import IntegrationTest

# 创建集成测试
test = IntegrationTest(base_url='http://localhost:8000')

# 添加测试用例
test.add_test({
    'name': 'test_api_endpoint',
    'endpoint': '/api/users',
    'method': 'GET',
    'expected_status': 200,
    'expected_fields': ['users', 'count']
})

# 运行测试
result = test.run()
print(result)
```

### 性能测试

```python
from auto_test_framework import PerformanceTest

# 创建性能测试
test = PerformanceTest()

# 添加性能测试
test.add_test({
    'name': 'test_response_time',
    'function': lambda: time.sleep(0.1),
    'max_duration': 0.15,  # 最大响应时间
    'iterations': 100
})

# 运行测试
result = test.run()
print(result)
```

### UI测试（基于Playwright）

```python
from auto_test_framework import UITest

# 创建UI测试
test = UITest()

# 添加UI测试
test.add_test({
    'name': 'test_login',
    'url': 'http://localhost:3000/login',
    'actions': [
        {'type': 'fill', 'selector': '#username', 'value': 'testuser'},
        {'type': 'fill', 'selector': '#password', 'value': 'password123'},
        {'type': 'click', 'selector': '#login-button'},
        {'type': 'wait_for_url', 'pattern': '/dashboard'}
    ]
})

# 运行测试（需要浏览器）
result = test.run(headless=True)
print(result)
```

### 测试覆盖率分析

```python
from auto_test_framework import CoverageAnalyzer

# 分析测试覆盖率
analyzer = CoverageAnalyzer(module_path='./src')

# 运行分析
report = analyzer.analyze()
print(f"Coverage: {report['percentage']}%")
print(f"Missing lines: {report['missing_lines']}")
```

### 测试报告生成

```python
from auto_test_framework import TestReporter

# 生成测试报告
reporter = TestReporter()

# 添加测试结果
reporter.add_result(test_result)

# 生成HTML报告
reporter.generate_html(output_path='test-report.html')

# 生成JSON报告
reporter.generate_json(output_path='test-report.json')

# 生成Markdown报告
reporter.generate_markdown(output_path='test-report.md')
```

## 核心特性

### 1. 单元测试
- ✓ 基于pytest的单元测试框架
- ✓ 支持同步和异步测试
- ✓ 支持测试夹具（fixtures）
- ✓ 支持参数化测试
- ✓ 支持测试标记（marks）

### 2. 集成测试
- ✓ HTTP/HTTPS API测试
- ✓ 数据库集成测试
- ✓ 消息队列集成测试
- ✓ 微服务集成测试
- ✓ 支持测试环境隔离

### 3. 性能测试
- ✓ 响应时间测试
- ✓ 吞吐量测试
- ✓ 并发测试
- ✓ 压力测试
- ✓ 性能基准测试

### 4. UI测试
- ✓ 基于Playwright的UI测试
- ✓ 支持Chrome、Firefox、Safari
- ✓ 支持无头模式
- ✓ 支持截图和录屏
- ✓ 支持等待和断言

### 5. 测试覆盖率
- ✓ 代码覆盖率分析
- ✓ 分支覆盖率
- ✓ 行覆盖率
- ✓ 缺失代码报告
- ✓ 覆盖率趋势分析

### 6. 测试报告
- ✓ HTML报告
- ✓ JSON报告
- ✓ Markdown报告
- ✓ 测试趋势图表
- ✓ 失败截图和日志

## 配置文件

在项目根目录创建 `auto_test_config.yaml`：

```yaml
# 自动化测试配置

test:
  # 测试目录
  test_dir: './tests'

  # 测试文件匹配模式
  test_patterns:
    - 'test_*.py'
    - '*_test.py'

  # 测试标记
  markers:
    unit: 单元测试
    integration: 集成测试
    performance: 性能测试
    ui: UI测试

  # 测试超时
  timeout: 30  # 秒

coverage:
  # 覆盖率目标
  target: 80  # 百分比

  # 要包含的目录
  include:
    - './src'

  # 要排除的目录
  exclude:
    - './tests'
    - './venv'

report:
  # 报告输出目录
  output_dir: './test-reports'

  # 报告格式
  formats:
    - html
    - json
    - markdown

ui:
  # UI测试配置
  headless: true
  screenshot_on_failure: true
  video: false
```

## 命令行工具

```bash
# 运行所有测试
auto-test run

# 运行特定测试
auto-test run tests/test_example.py

# 运行带标记的测试
auto-test run -m unit

# 生成覆盖率报告
auto-test coverage

# 生成测试报告
auto-test report

# 清理测试环境
auto-test clean
```

## 测试用例示例

### 1. 单元测试示例

```python
# tests/test_calculator.py
import pytest
from src.calculator import Calculator

def test_addition():
    calc = Calculator()
    assert calc.add(2, 3) == 5

def test_subtraction():
    calc = Calculator()
    assert calc.subtract(5, 3) == 2

@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 2),
    (3, 4, 12),
    (0, 5, 0),
])
def test_multiplication(a, b, expected):
    calc = Calculator()
    assert calc.multiply(a, b) == expected
```

### 2. 集成测试示例

```python
# tests/test_api.py
import pytest
from auto_test_framework import IntegrationTest

def test_user_api():
    test = IntegrationTest(base_url='http://localhost:8000')

    # 测试创建用户
    response = test.post('/api/users', json={
        'name': 'Test User',
        'email': 'test@example.com'
    })
    assert response.status_code == 201
    assert 'id' in response.json()

    # 测试获取用户
    user_id = response.json()['id']
    response = test.get(f'/api/users/{user_id}')
    assert response.status_code == 200
    assert response.json()['name'] == 'Test User'

    # 测试删除用户
    response = test.delete(f'/api/users/{user_id}')
    assert response.status_code == 204
```

### 3. 性能测试示例

```python
# tests/test_performance.py
from auto_test_framework import PerformanceTest
import time

def test_api_performance():
    test = PerformanceTest()

    # 测试API响应时间
    test.add_test({
        'name': 'test_api_response_time',
        'function': lambda: requests.get('http://localhost:8000/api/data'),
        'max_duration': 0.5,
        'iterations': 100
    })

    result = test.run()
    assert result['passed'], f"性能测试失败: {result}"
```

### 4. UI测试示例

```python
# tests/test_ui.py
from auto_test_framework import UITest

def test_login_page():
    test = UITest()

    test.add_test({
        'name': 'test_login',
        'url': 'http://localhost:3000/login',
        'actions': [
            {'type': 'fill', 'selector': '#username', 'value': 'testuser'},
            {'type': 'fill', 'selector': '#password', 'value': 'password123'},
            {'type': 'click', 'selector': '#login-button'},
            {'type': 'assert_text', 'selector': 'h1', 'text': 'Welcome'}
        ]
    })

    result = test.run(headless=True)
    assert result['passed'], f"UI测试失败: {result}"
```

## 使用建议

1. **单元测试：** 为每个函数和方法编写单元测试
2. **集成测试：** 测试模块和组件之间的交互
3. **性能测试：** 在性能关键路径上添加性能测试
4. **UI测试：** 测试用户界面的重要流程
5. **覆盖率目标：** 保持在80%以上
6. **持续集成：** 将测试集成到CI/CD流程
7. **定期运行：** 定期运行全部测试，及时发现问题

## 依赖说明

- pytest: 测试框架
- pytest-cov: 测试覆盖率
- pytest-asyncio: 异步测试支持
- pytest-mock: Mock支持
- requests: HTTP客户端
- httpx: 异步HTTP客户端
- selenium: Web自动化（可选）
- playwright: 现代Web自动化（推荐）

## 核心价值

**对自我更迭的贡献：**
1. **质量保证：** 自动化测试保证代码质量
2. **快速反馈：** 快速发现和修复问题
3. **重构信心：** 重构时有测试作为安全网
4. **文档作用：** 测试用例作为功能文档

**应用场景：**
- 新功能开发
- 代码重构
- Bug修复
- 性能优化
- 持续集成
