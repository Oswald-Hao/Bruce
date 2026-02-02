"""
工具函数
"""

import os
import yaml
import json
from typing import Dict, Any, Optional
from pathlib import Path


def load_yaml_config(config_path: str) -> Dict[str, Any]:
    """加载YAML配置文件"""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {}
    except yaml.YAMLError:
        return {}


def save_yaml_config(config: Dict[str, Any], config_path: str) -> bool:
    """保存配置到YAML文件"""
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        return True
    except Exception:
        return False


def load_json_config(config_path: str) -> Dict[str, Any]:
    """加载JSON配置文件"""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def save_json_config(config: Dict[str, Any], config_path: str) -> bool:
    """保存配置到JSON文件"""
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception:
        return False


def merge_dicts(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """合并两个字典"""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


def check_docker_installed() -> bool:
    """检查Docker是否安装"""
    try:
        import docker
        client = docker.from_env()
        client.ping()
        return True
    except Exception:
        return False


def check_kubectl_installed() -> bool:
    """检查kubectl是否安装"""
    try:
        import subprocess
        result = subprocess.run(['kubectl', 'version', '--client'],
                              capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def validate_app_structure(app_dir: str) -> bool:
    """验证应用结构"""
    required_files = ['requirements.txt', 'app.py', 'Dockerfile']
    for file in required_files:
        if not os.path.exists(os.path.join(app_dir, file)):
            return False
    return True


def get_app_name(app_dir: str) -> str:
    """从目录名获取应用名称"""
    return os.path.basename(os.path.normpath(app_dir))


def generate_dockerfile(
    app_name: str,
    python_version: str = "3.11-slim",
    port: int = 8080
) -> str:
    """生成Dockerfile"""
    return f"""FROM python:{python_version}

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE {port}

CMD ["python", "app.py"]
"""


def generate_docker_compose(
    app_name: str,
    services: Dict[str, Any]
) -> str:
    """生成docker-compose.yml"""
    compose = {
        'version': '3.8',
        'services': {
            app_name: services
        }
    }
    return yaml.dump(compose, default_flow_style=False)


def generate_k8s_deployment(
    app_name: str,
    image: str,
    replicas: int = 1,
    cpu: str = "500m",
    memory: str = "512Mi"
) -> str:
    """生成Kubernetes Deployment配置"""
    deployment = {
        'apiVersion': 'apps/v1',
        'kind': 'Deployment',
        'metadata': {
            'name': app_name,
            'labels': {
                'app': app_name
            }
        },
        'spec': {
            'replicas': replicas,
            'selector': {
                'matchLabels': {
                    'app': app_name
                }
            },
            'template': {
                'metadata': {
                    'labels': {
                        'app': app_name
                    }
                },
                'spec': {
                    'containers': [{
                        'name': app_name,
                        'image': image,
                        'ports': [{
                            'containerPort': 8080
                        }],
                        'resources': {
                            'requests': {
                                'cpu': cpu,
                                'memory': memory
                            },
                            'limits': {
                                'cpu': cpu,
                                'memory': memory
                            }
                        }
                    }]
                }
            }
        }
    }
    return yaml.dump(deployment, default_flow_style=False)


def generate_k8s_service(
    app_name: str,
    port: int = 8080,
    service_type: str = "ClusterIP"
) -> str:
    """生成Kubernetes Service配置"""
    service = {
        'apiVersion': 'v1',
        'kind': 'Service',
        'metadata': {
            'name': app_name
        },
        'spec': {
            'type': service_type,
            'selector': {
                'app': app_name
            },
            'ports': [{
                'port': port,
                'targetPort': port,
                'protocol': 'TCP'
            }]
        }
    }
    return yaml.dump(service, default_flow_style=False)


def format_size(size_bytes: int) -> str:
    """格式化字节大小"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"
