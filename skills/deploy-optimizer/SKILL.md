# Deploy Optimizer - 跨平台部署工具

## 功能描述

自动化跨平台部署工具，支持Docker、Kubernetes、云服务自动化部署，提高部署效率和可靠性。

## 核心功能

- Docker容器管理（镜像构建、容器运行、容器编排）
- Kubernetes部署管理（Pod、Service、Deployment、ConfigMap）
- 云服务集成（AWS、阿里云、腾讯云）
- 部署自动化（CI/CD集成、自动回滚、健康检查）
- 多环境支持（开发、测试、生产）
- 配置管理（环境变量、密钥管理）

## 安装依赖

```bash
pip install docker kubernetes boto3
pip install pyyaml jinja2
```

## 使用方法

### Docker部署
```python
from deploy_optimizer import DeployOptimizer

optimizer = DeployOptimizer()

# 构建Docker镜像
result = optimizer.build_docker_image(
    app_dir="/path/to/app",
    image_name="myapp",
    tag="latest"
)

# 运行容器
result = optimizer.run_container(
    image_name="myapp:latest",
    container_name="myapp",
    ports={8080: 80},
    env_vars={"ENV": "production"}
)
```

### Kubernetes部署
```python
# 部署到Kubernetes
result = optimizer.deploy_to_kubernetes(
    app_name="myapp",
    image="myapp:latest",
    replicas=3,
    namespace="production",
    cpu="500m",
    memory="512Mi"
)
```

### 云服务部署
```python
# 部署到阿里云
result = optimizer.deploy_to_cloud(
    provider="aliyun",
    service="ecs",
    region="cn-hangzhou",
    instance_type="ecs.t6-c1m1.large",
    image_id="img-xxx"
)
```

## 工具结构

```
skills/deploy-optimizer/
├── SKILL.md
├── README.md
├── src/
│   ├── __init__.py
│   ├── deploy_optimizer.py    # 主类
│   ├── docker_manager.py       # Docker管理
│   ├── k8s_manager.py         # Kubernetes管理
│   ├── cloud_manager.py       # 云服务管理
│   ├── config_manager.py      # 配置管理
│   └── utils.py               # 工具函数
├── templates/
│   ├── docker/
│   │   ├── Dockerfile.j2
│   │   └── docker-compose.yml.j2
│   └── kubernetes/
│       ├── deployment.yml.j2
│       ├── service.yml.j2
│       └── configmap.yml.j2
└── tests/
    ├── test_deploy_optimizer.py
    ├── test_docker_manager.py
    ├── test_k8s_manager.py
    ├── test_cloud_manager.py
    └── test_config_manager.py
```

## 测试

运行测试：
```bash
cd /home/lejurobot/clawd/skills/deploy-optimizer/
python -m pytest tests/ -v
```

## 创建时间

2026-02-03 00:20
