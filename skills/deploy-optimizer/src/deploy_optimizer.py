"""
Deploy Optimizer - 主类
"""

from typing import Dict, Any, Optional
import os
import importlib.util

# 动态导入模块（避免相对导入问题）
def load_module(name, file_path):
    spec = importlib.util.spec_from_file_location(name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

src_dir = os.path.dirname(os.path.abspath(__file__))
docker_manager_module = load_module("docker_manager", os.path.join(src_dir, "docker_manager.py"))
k8s_manager_module = load_module("k8s_manager", os.path.join(src_dir, "k8s_manager.py"))
cloud_manager_module = load_module("cloud_manager", os.path.join(src_dir, "cloud_manager.py"))
utils_module = load_module("utils", os.path.join(src_dir, "utils.py"))

DockerManager = docker_manager_module.DockerManager
K8sManager = k8s_manager_module.K8sManager
CloudManager = cloud_manager_module.CloudManager
load_yaml_config = utils_module.load_yaml_config
save_yaml_config = utils_module.save_yaml_config
generate_dockerfile = utils_module.generate_dockerfile
generate_k8s_deployment = utils_module.generate_k8s_deployment
generate_k8s_service = utils_module.generate_k8s_service


class DeployOptimizer:
    """跨平台部署优化器"""

    def __init__(self):
        self.docker = DockerManager()
        self.k8s = K8sManager()
        self.cloud = CloudManager()

    # Docker相关方法
    def build_docker_image(
        self,
        app_dir: str,
        image_name: Optional[str] = None,
        tag: str = "latest"
    ) -> Dict[str, Any]:
        """构建Docker镜像"""
        return self.docker.build_image(app_dir, image_name, tag)

    def run_docker_container(
        self,
        image_name: str,
        container_name: Optional[str] = None,
        ports: Optional[Dict[int, int]] = None,
        env_vars: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """运行Docker容器"""
        return self.docker.run_container(
            image_name, container_name, ports, env_vars
        )

    def stop_docker_container(self, container_id: str) -> Dict[str, Any]:
        """停止Docker容器"""
        return self.docker.stop_container(container_id)

    def list_docker_containers(self) -> Dict[str, Any]:
        """列出Docker容器"""
        containers = self.docker.list_containers()
        return {
            'success': True,
            'containers': containers
        }

    def get_docker_images(self) -> Dict[str, Any]:
        """获取Docker镜像列表"""
        images = self.docker.get_image_list()
        return {
            'success': True,
            'images': images
        }

    # Kubernetes相关方法
    def deploy_to_kubernetes(
        self,
        app_name: str,
        image: str,
        replicas: int = 1,
        namespace: str = "default",
        cpu: str = "500m",
        memory: str = "512Mi",
        port: int = 8080,
        service_type: str = "ClusterIP"
    ) -> Dict[str, Any]:
        """部署应用到Kubernetes

        Args:
            app_name: 应用名称
            image: 镜像名称
            replicas: 副本数
            namespace: 命名空间
            cpu: CPU请求
            memory: 内存请求
            port: 服务端口
            service_type: 服务类型

        Returns:
            部署结果字典
        """
        if not self.k8s.is_available():
            return {
                'success': False,
                'error': 'Kubernetes不可用'
            }

        # 创建Deployment
        deploy_result = self.k8s.create_deployment(
            app_name, image, replicas, namespace, cpu, memory, apply=True
        )

        if not deploy_result['success']:
            return deploy_result

        # 创建Service
        service_result = self.k8s.create_service(
            app_name, port, namespace, service_type, apply=True
        )

        return {
            'success': service_result['success'],
            'deployment': deploy_result,
            'service': service_result
        }

    def scale_kubernetes_deployment(
        self,
        deployment_name: str,
        replicas: int,
        namespace: str = "default"
    ) -> Dict[str, Any]:
        """扩缩容Kubernetes Deployment"""
        return self.k8s.scale_deployment(
            deployment_name, replicas, namespace
        )

    def delete_kubernetes_deployment(
        self,
        deployment_name: str,
        namespace: str = "default"
    ) -> Dict[str, Any]:
        """删除Kubernetes Deployment"""
        return self.k8s.delete_deployment(
            deployment_name, namespace
        )

    def get_kubernetes_pods(
        self,
        app_name: Optional[str] = None,
        namespace: str = "default"
    ) -> Dict[str, Any]:
        """获取Kubernetes Pod列表"""
        pods = self.k8s.get_pods(app_name, namespace)
        return {
            'success': True,
            'pods': pods
        }

    def get_kubernetes_deployments(
        self,
        namespace: str = "default"
    ) -> Dict[str, Any]:
        """获取Kubernetes Deployment列表"""
        deployments = self.k8s.get_deployments(namespace)
        return {
            'success': True,
            'deployments': deployments
        }

    def get_kubernetes_services(
        self,
        namespace: str = "default"
    ) -> Dict[str, Any]:
        """获取Kubernetes Service列表"""
        services = self.k8s.get_services(namespace)
        return {
            'success': True,
            'services': services
        }

    # 云服务相关方法
    def deploy_to_cloud(
        self,
        provider: str,
        service: str = "compute",
        region: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """部署到云服务

        Args:
            provider: 云服务提供商 (aliyun, aws, tencent)
            service: 服务类型 (compute, storage, database)
            region: 区域
            **kwargs: 其他参数

        Returns:
            部署结果字典
        """
        if not self.cloud.is_provider_available(provider):
            return {
                'success': False,
                'error': f'{provider} CLI不可用，请先安装并配置'
            }

        if provider == 'aliyun':
            if service == 'compute':
                return self.cloud.deploy_to_aliyun(
                    region=region or "cn-hangzhou",
                    **kwargs
                )
        elif provider == 'aws':
            if service == 'compute':
                return self.cloud.deploy_to_aws(
                    region=region or "us-east-1",
                    **kwargs
                )
        elif provider == 'tencent':
            if service == 'compute':
                return self.cloud.deploy_to_tencent(
                    region=region or "ap-guangzhou",
                    **kwargs
                )

        return {
            'success': False,
            'error': f'不支持的提供商或服务: {provider}/{service}'
        }

    def get_cloud_instances(
        self,
        provider: str,
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取云服务实例列表"""
        if not self.cloud.is_provider_available(provider):
            return {
                'success': False,
                'error': f'{provider} CLI不可用'
            }

        if provider == 'aliyun':
            return self.cloud.list_aliyun_instances(
                region=region or "cn-hangzhou"
            )
        elif provider == 'aws':
            return self.cloud.list_aws_instances(
                region=region or "us-east-1"
            )

        return {
            'success': False,
            'error': f'不支持的提供商: {provider}'
        }

    def start_cloud_instance(
        self,
        provider: str,
        instance_id: str,
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """启动云实例"""
        return self.cloud.start_instance(provider, instance_id, region)

    def stop_cloud_instance(
        self,
        provider: str,
        instance_id: str,
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """停止云实例"""
        return self.cloud.stop_instance(provider, instance_id, region)

    def delete_cloud_instance(
        self,
        provider: str,
        instance_id: str,
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """删除云实例"""
        return self.cloud.delete_instance(provider, instance_id, region)

    # 综合方法
    def get_status(self) -> Dict[str, Any]:
        """获取所有平台的可用状态"""
        return {
            'docker': {
                'available': self.docker.is_available()
            },
            'kubernetes': {
                'available': self.k8s.is_available()
            },
            'cloud': {
                'available_providers': self.cloud.get_available_providers()
            }
        }

    def deploy_app(
        self,
        app_name: str,
        platform: str = "docker",
        **kwargs
    ) -> Dict[str, Any]:
        """部署应用（统一入口）

        Args:
            app_name: 应用名称
            platform: 部署平台 (docker, kubernetes, cloud)
            **kwargs: 平台特定参数

        Returns:
            部署结果字典
        """
        if platform == "docker":
            app_dir = kwargs.get('app_dir', '.')
            image_name = kwargs.get('image_name', app_name)

            # 构建镜像
            build_result = self.build_docker_image(app_dir, image_name)
            if not build_result['success']:
                return build_result

            # 运行容器
            return self.run_docker_container(
                build_result['image_name'],
                **kwargs
            )

        elif platform == "kubernetes":
            return self.deploy_to_kubernetes(
                app_name,
                **kwargs
            )

        elif platform == "cloud":
            return self.deploy_to_cloud(
                **kwargs
            )

        else:
            return {
                'success': False,
                'error': f'不支持的部署平台: {platform}'
            }

    def generate_deployment_config(
        self,
        app_name: str,
        platform: str,
        **kwargs
    ) -> Dict[str, Any]:
        """生成部署配置文件

        Args:
            app_name: 应用名称
            platform: 部署平台 (docker, kubernetes)
            **kwargs: 配置参数

        Returns:
            配置内容字典
        """
        if platform == "docker":
            dockerfile = generate_dockerfile(app_name, **kwargs)
            return {
                'success': True,
                'dockerfile': dockerfile
            }

        elif platform == "kubernetes":
            # 过滤参数：deployment需要image, replicas, cpu, memory
            deploy_kwargs = {k: v for k, v in kwargs.items()
                             if k in ['image', 'replicas', 'cpu', 'memory']}
            deployment = generate_k8s_deployment(app_name, **deploy_kwargs)

            # 过滤参数：service需要port, service_type
            service_kwargs = {k: v for k, v in kwargs.items()
                              if k in ['port', 'service_type']}
            service = generate_k8s_service(app_name, **service_kwargs)

            return {
                'success': True,
                'deployment': deployment,
                'service': service
            }

        else:
            return {
                'success': False,
                'error': f'不支持的部署平台: {platform}'
            }
