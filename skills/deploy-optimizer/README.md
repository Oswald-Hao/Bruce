# Deploy Optimizer - 跨平台部署工具

自动化跨平台部署工具，支持Docker、Kubernetes、云服务自动化部署，提高部署效率和可靠性。

## 功能特性

- **Docker管理**: 镜像构建、容器运行、容器编排
- **Kubernetes部署**: Pod、Service、Deployment管理
- **云服务集成**: AWS、阿里云、腾讯云
- **多环境支持**: 开发、测试、生产环境
- **配置生成**: 自动生成Dockerfile、K8s YAML、docker-compose.yml

## 快速开始

### 检查平台状态

```python
from deploy_optimizer import DeployOptimizer

optimizer = DeployOptimizer()
status = optimizer.get_status()

print(f"Docker可用: {status['docker']['available']}")
print(f"Kubernetes可用: {status['kubernetes']['available']}")
print(f"云服务提供商: {status['cloud']['available_providers']}")
```

### Docker部署

```python
# 构建镜像
result = optimizer.build_docker_image(
    app_dir="/path/to/app",
    image_name="myapp",
    tag="latest"
)

# 运行容器
result = optimizer.run_docker_container(
    image_name="myapp:latest",
    container_name="myapp",
    ports={8080: 80},
    env_vars={"ENV": "production"}
)
```

### Kubernetes部署

```python
# 部署到K8s
result = optimizer.deploy_to_kubernetes(
    app_name="myapp",
    image="myapp:latest",
    replicas=3,
    namespace="production",
    cpu="500m",
    memory="512Mi",
    port=8080
)

# 扩缩容
result = optimizer.scale_kubernetes_deployment(
    deployment_name="myapp",
    replicas=5,
    namespace="production"
)
```

### 云服务部署

```python
# 部署到阿里云
result = optimizer.deploy_to_cloud(
    provider="aliyun",
    service="compute",
    region="cn-hangzhou",
    instance_type="ecs.t6-c1m1.large",
    image_id="img-xxx"
)

# 列出实例
result = optimizer.get_cloud_instances(provider="aliyun")
```

### 生成部署配置

```python
# 生成Dockerfile
result = optimizer.generate_deployment_config(
    app_name="myapp",
    platform="docker",
    python_version="3.11-slim",
    port=8080
)

print(result['dockerfile'])

# 生成K8s配置
result = optimizer.generate_deployment_config(
    app_name="myapp",
    platform="kubernetes",
    image="myapp:latest",
    replicas=3
)

print(result['deployment'])
print(result['service'])
```

## 运行测试

```bash
cd /home/lejurobot/clawd/skills/deploy-optimizer/
python tests/test_all.py
```

## 测试覆盖

- ✅ 平台状态检测
- ✅ Docker操作（镜像、容器管理）
- ✅ Kubernetes操作（Pod、Deployment、Service）
- ✅ 云服务操作（阿里云、AWS、腾讯云）
- ✅ 配置文件生成
- ✅ 错误处理

## 项目结构

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
│   └── utils.py               # 工具函数
└── tests/
    └── test_all.py
```

## 核心价值

1. **统一接口**: 一个API支持多个部署平台
2. **自动化**: 自动生成配置文件，减少手动配置
3. **多云支持**: 支持主流云服务提供商
4. **容器化**: 原生支持Docker和Kubernetes
5. **灵活扩展**: 易于添加新的云服务提供商

## 依赖项

- docker (Docker SDK)
- kubernetes (K8s Python客户端，可选)
- boto3 (AWS SDK，可选)
- pyyaml (YAML处理)

## 创建时间

2026-02-03 00:20
