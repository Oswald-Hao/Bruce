# CI/CD集成系统 - SKILL.md

## 技能描述

提供全面的持续集成和持续部署能力，支持自动化构建、测试、部署流程，提升开发效率和代码质量。

## 核心功能

- 自动化构建（Docker镜像、代码编译、依赖安装）
- 自动化测试（单元测试、集成测试、性能测试）
- 自动化部署（单机部署、集群部署、滚动更新）
- 代码质量检查（代码规范、安全扫描、依赖检查）
- 通知集成（邮件、Slack、飞书）
- 多环境管理（开发、测试、预发、生产）
- 回滚机制（版本回退、快速恢复）
- 流水线可视化

## 支持的CI/CD平台

- GitHub Actions
- GitLab CI
- Jenkins
- 自建流水线（本地执行）

## 安装依赖

```bash
pip install docker jinja2 pyyaml
```

## 使用方法

### 1. 创建CI/CD配置

```python
from cicd_system import CICDSystem

cicd = CICDSystem()

# 创建GitHub Actions配置
config = cicd.create_github_actions(
    project_name="my-project",
    python_version="3.10",
    run_tests=True,
    deploy_to_docker=True
)

config.save(".github/workflows/ci.yml")
```

### 2. 执行流水线

```python
# 执行本地流水线
result = cicd.run_pipeline(
    steps=[
        "build",
        "test",
        "lint",
        "security_scan",
        "deploy"
    ],
    environment="staging"
)

print(result.status)  # "success" | "failed"
print(result.logs)    # 执行日志
```

### 3. 生成Dockerfile

```python
dockerfile = cicd.generate_dockerfile(
    base_image="python:3.10-slim",
    requirements_path="requirements.txt",
    workdir="/app",
    port=8000
)
```

### 4. 多环境部署

```python
# 部署到不同环境
for env in ["dev", "staging", "production"]:
    result = cicd.deploy(
        environment=env,
        config_path=f"config/{env}.yaml",
        auto_rollback=True
    )
```

## 命令行工具

```bash
# 初始化CI/CD配置
python skills/cicd-system/init.py

# 执行流水线
python skills/cicd-system/run.py --steps build,test,deploy

# 生成配置
python skills/cicd-system/generate.py --platform github-actions

# 查看流水线状态
python skills/cicd-system/status.py
```

## 配置示例

### GitHub Actions配置

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest
      - name: Build Docker
        run: docker build -t myapp .
```

## 核心价值

- **自动化：** 自动化构建测试部署，减少人工操作
- **快速反馈：** 快速发现和修复问题
- **质量保证：** 自动化质量检查和安全扫描
- **高效部署：** 一键部署到多个环境
- **稳定可靠：** 自动回滚机制保证稳定性

## 测试

```bash
# 运行所有测试
python skills/cicd-system/test.py

# 运行特定测试
python skills/cicd-system/test.py --test pipeline
python skills/cicd-system/test.py --test docker
python skills/cicd-system/test.py --test deploy
```

## 注意事项

- 部署前请确保有足够的资源
- 生产环境部署建议使用灰度发布
- 保留多个版本以便快速回滚
- 定期检查和更新依赖包
