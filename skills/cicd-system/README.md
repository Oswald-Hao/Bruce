# CI/CD集成系统

提供全面的持续集成和持续部署能力，支持自动化构建、测试、部署流程。

## 功能

- 自动化构建（Docker镜像、代码编译、依赖安装）
- 自动化测试（单元测试、集成测试、性能测试）
- 自动化部署（单机部署、集群部署、滚动更新）
- 代码质量检查（代码规范、安全扫描、依赖检查）
- 通知集成（邮件、Slack、飞书）
- 多环境管理（开发、测试、预发、生产）
- 回滚机制（版本回退、快速恢复）

## 支持的平台

- GitHub Actions
- GitLab CI
- Jenkins
- 自建流水线

## 快速开始

### 1. 创建GitHub Actions配置

```python
from cicd_system import CICDSystem

cicd = CICDSystem()
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
result = cicd.run_pipeline(
    steps=[
        {"name": "build", "command": "make build"},
        {"name": "test", "command": "pytest", "depends_on": ["build"]},
        {"name": "deploy", "command": "kubectl apply -f k8s/", "depends_on": ["test"]}
    ],
    environment="staging"
)

print(result.status)
print(result.logs)
```

### 3. 生成Dockerfile

```python
dockerfile = cicd.generate_dockerfile(
    base_image="python:3.10-slim",
    requirements_path="requirements.txt",
    port=8000
)
```

### 4. 生成Kubernetes配置

```python
manifest = cicd.generate_kubernetes_manifest(
    app_name="myapp",
    image="myapp:1.0",
    replicas=3,
    port=8080
)
```

## 测试

```bash
python test.py
```

## 输出示例

```
Starting pipeline: my-pipeline
Environment: staging
Steps: 5

▶️  Running: build
✅ Success: build
▶️  Running: test
✅ Success: test
▶️  Running: lint
✅ Success: lint
▶️  Running: security
✅ Success: security
▶️  Running: deploy
✅ Success: deploy

✅ Pipeline succeeded
Total duration: 45.23s
```

## 技术栈

- Python 3.x
- Docker
- Kubernetes
- GitHub Actions
- YAML
