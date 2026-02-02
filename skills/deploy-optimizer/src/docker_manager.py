"""
Docker管理器
"""

import docker
import os
from typing import Dict, Any, Optional, List
from .utils import (
    validate_app_structure,
    get_app_name,
    generate_dockerfile,
    format_size
)


class DockerManager:
    """Docker容器管理器"""

    def __init__(self):
        try:
            self.client = docker.from_env()
            self.enabled = True
        except Exception as e:
            print(f"警告: Docker不可用 - {e}")
            self.enabled = False
            self.client = None

    def is_available(self) -> bool:
        """检查Docker是否可用"""
        return self.enabled

    def build_image(
        self,
        app_dir: str,
        image_name: Optional[str] = None,
        tag: str = "latest",
        dockerfile: Optional[str] = None
    ) -> Dict[str, Any]:
        """构建Docker镜像

        Args:
            app_dir: 应用目录
            image_name: 镜像名称（默认使用目录名）
            tag: 镜像标签
            dockerfile: Dockerfile路径（默认使用app_dir/Dockerfile）

        Returns:
            构建结果字典
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'Docker不可用'
            }

        if not os.path.exists(app_dir):
            return {
                'success': False,
                'error': f'应用目录不存在: {app_dir}'
            }

        if image_name is None:
            image_name = get_app_name(app_dir)

        if dockerfile is None:
            dockerfile = os.path.join(app_dir, 'Dockerfile')

        if not os.path.exists(dockerfile):
            # 生成默认Dockerfile
            dockerfile_content = generate_dockerfile(image_name)
            dockerfile_path = os.path.join(app_dir, 'Dockerfile')
            with open(dockerfile_path, 'w') as f:
                f.write(dockerfile_content)

        try:
            full_image_name = f"{image_name}:{tag}"

            # 构建镜像
            image, build_logs = self.client.images.build(
                path=app_dir,
                tag=full_image_name,
                dockerfile=dockerfile,
                rm=True
            )

            # 获取镜像信息
            image_info = self.client.images.get(full_image_name)

            return {
                'success': True,
                'image_name': full_image_name,
                'image_id': image_info.id,
                'size': format_size(image_info.attrs['Size']),
                'logs': [line.get('stream', '') for line in build_logs if 'stream' in line]
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def run_container(
        self,
        image_name: str,
        container_name: Optional[str] = None,
        ports: Optional[Dict[int, int]] = None,
        env_vars: Optional[Dict[str, str]] = None,
        volumes: Optional[Dict[str, Dict[str, str]]] = None,
        detach: bool = True
    ) -> Dict[str, Any]:
        """运行Docker容器

        Args:
            image_name: 镜像名称
            container_name: 容器名称
            ports: 端口映射 {容器端口: 主机端口}
            env_vars: 环境变量
            volumes: 卷挂载 {主机路径: {'bind': 容器路径, 'mode': 'rw'}}
            detach: 是否在后台运行

        Returns:
            运行结果字典
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'Docker不可用'
            }

        try:
            container = self.client.containers.run(
                image_name,
                name=container_name,
                ports=ports,
                environment=env_vars,
                volumes=volumes,
                detach=detach
            )

            return {
                'success': True,
                'container_id': container.id,
                'container_name': container.name,
                'status': container.status
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def stop_container(self, container_id: str) -> Dict[str, Any]:
        """停止容器"""
        if not self.is_available():
            return {
                'success': False,
                'error': 'Docker不可用'
            }

        try:
            container = self.client.containers.get(container_id)
            container.stop()

            return {
                'success': True,
                'container_id': container_id,
                'status': 'stopped'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def remove_container(self, container_id: str, force: bool = False) -> Dict[str, Any]:
        """删除容器"""
        if not self.is_available():
            return {
                'success': False,
                'error': 'Docker不可用'
            }

        try:
            container = self.client.containers.get(container_id)
            container.remove(force=force)

            return {
                'success': True,
                'container_id': container_id,
                'status': 'removed'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def list_containers(self, all: bool = False) -> List[Dict[str, Any]]:
        """列出所有容器

        Args:
            all: 是否显示所有容器（包括停止的）

        Returns:
            容器列表
        """
        if not self.is_available():
            return []

        try:
            containers = self.client.containers.list(all=all)
            return [
                {
                    'id': container.id[:12],
                    'name': container.name,
                    'image': container.image.tags[0] if container.image.tags else container.image.id,
                    'status': container.status,
                    'ports': container.ports
                }
                for container in containers
            ]
        except Exception as e:
            print(f"列出容器失败: {e}")
            return []

    def get_container_logs(
        self,
        container_id: str,
        tail: int = 100
    ) -> Dict[str, Any]:
        """获取容器日志"""
        if not self.is_available():
            return {
                'success': False,
                'error': 'Docker不可用'
            }

        try:
            container = self.client.containers.get(container_id)
            logs = container.logs(tail=tail).decode('utf-8')

            return {
                'success': True,
                'logs': logs
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def inspect_container(self, container_id: str) -> Dict[str, Any]:
        """检查容器详情"""
        if not self.is_available():
            return {
                'success': False,
                'error': 'Docker不可用'
            }

        try:
            container = self.client.containers.get(container_id)
            return {
                'success': True,
                'info': container.attrs
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_image_list(self) -> List[Dict[str, Any]]:
        """获取所有镜像列表"""
        if not self.is_available():
            return []

        try:
            images = self.client.images.list()
            return [
                {
                    'id': image.id[:12],
                    'tags': image.tags,
                    'size': format_size(image.attrs['Size'])
                }
                for image in images
            ]
        except Exception as e:
            print(f"获取镜像列表失败: {e}")
            return []

    def remove_image(self, image_id: str, force: bool = False) -> Dict[str, Any]:
        """删除镜像"""
        if not self.is_available():
            return {
                'success': False,
                'error': 'Docker不可用'
            }

        try:
            image = self.client.images.get(image_id)
            image.remove(force=force)

            return {
                'success': True,
                'image_id': image_id,
                'status': 'removed'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
