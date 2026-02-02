"""
Kubernetes管理器
"""

import yaml
import subprocess
import os
from typing import Dict, Any, Optional, List
from .utils import (
    generate_k8s_deployment,
    generate_k8s_service,
    save_yaml_config
)


class K8sManager:
    """Kubernetes部署管理器"""

    def __init__(self):
        self.enabled = self._check_kubectl()

    def _check_kubectl(self) -> bool:
        """检查kubectl是否可用"""
        try:
            result = subprocess.run(
                ['kubectl', 'version', '--client'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def is_available(self) -> bool:
        """检查Kubernetes是否可用"""
        return self.enabled

    def _run_kubectl(
        self,
        command: List[str],
        capture_output: bool = True
    ) -> Dict[str, Any]:
        """运行kubectl命令"""
        try:
            result = subprocess.run(
                ['kubectl'] + command,
                capture_output=capture_output,
                text=True
            )

            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def create_deployment(
        self,
        app_name: str,
        image: str,
        replicas: int = 1,
        namespace: str = "default",
        cpu: str = "500m",
        memory: str = "512Mi",
        apply: bool = True
    ) -> Dict[str, Any]:
        """创建Deployment

        Args:
            app_name: 应用名称
            image: 镜像名称
            replicas: 副本数
            namespace: 命名空间
            cpu: CPU请求
            memory: 内存请求
            apply: 是否立即应用

        Returns:
            操作结果字典
        """
        deployment_yaml = generate_k8s_deployment(
            app_name, image, replicas, cpu, memory
        )

        if apply:
            # 应用到集群
            result = self._run_kubectl([
                'apply', '-f', '-'
            ], capture_output=False)

            # 使用stdin输入配置
            try:
                process = subprocess.Popen(
                    ['kubectl', 'apply', '-f', '-'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = process.communicate(input=deployment_yaml)

                return {
                    'success': process.returncode == 0,
                    'stdout': stdout,
                    'stderr': stderr,
                    'deployment': deployment_yaml
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'deployment': deployment_yaml
                }
        else:
            return {
                'success': True,
                'deployment': deployment_yaml
            }

    def create_service(
        self,
        app_name: str,
        port: int = 8080,
        namespace: str = "default",
        service_type: str = "ClusterIP",
        apply: bool = True
    ) -> Dict[str, Any]:
        """创建Service

        Args:
            app_name: 应用名称
            port: 服务端口
            namespace: 命名空间
            service_type: 服务类型
            apply: 是否立即应用

        Returns:
            操作结果字典
        """
        service_yaml = generate_k8s_service(
            app_name, port, service_type
        )

        if apply:
            try:
                process = subprocess.Popen(
                    ['kubectl', 'apply', '-f', '-'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = process.communicate(input=service_yaml)

                return {
                    'success': process.returncode == 0,
                    'stdout': stdout,
                    'stderr': stderr,
                    'service': service_yaml
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'service': service_yaml
                }
        else:
            return {
                'success': True,
                'service': service_yaml
            }

    def scale_deployment(
        self,
        deployment_name: str,
        replicas: int,
        namespace: str = "default"
    ) -> Dict[str, Any]:
        """扩缩容Deployment"""
        result = self._run_kubectl([
            'scale', 'deployment', deployment_name,
            f'--replicas={replicas}',
            '-n', namespace
        ])

        return result

    def delete_deployment(
        self,
        deployment_name: str,
        namespace: str = "default"
    ) -> Dict[str, Any]:
        """删除Deployment"""
        result = self._run_kubectl([
            'delete', 'deployment', deployment_name,
            '-n', namespace
        ])

        return result

    def delete_service(
        self,
        service_name: str,
        namespace: str = "default"
    ) -> Dict[str, Any]:
        """删除Service"""
        result = self._run_kubectl([
            'delete', 'service', service_name,
            '-n', namespace
        ])

        return result

    def get_pods(
        self,
        app_name: Optional[str] = None,
        namespace: str = "default"
    ) -> List[Dict[str, Any]]:
        """获取Pod列表"""
        label_filter = f'-l app={app_name}' if app_name else ''
        result = self._run_kubectl([
            'get', 'pods', label_filter,
            '-n', namespace, '-o', 'json'
        ])

        if not result['success']:
            return []

        try:
            data = yaml.safe_load(result['stdout'])
            pods = data.get('items', [])

            return [
                {
                    'name': pod['metadata']['name'],
                    'status': pod['status']['phase'],
                    'ip': pod['status'].get('podIP', 'N/A'),
                    'node': pod['spec'].get('nodeName', 'N/A')
                }
                for pod in pods
            ]
        except Exception:
            return []

    def get_deployments(
        self,
        namespace: str = "default"
    ) -> List[Dict[str, Any]]:
        """获取Deployment列表"""
        result = self._run_kubectl([
            'get', 'deployments',
            '-n', namespace, '-o', 'json'
        ])

        if not result['success']:
            return []

        try:
            data = yaml.safe_load(result['stdout'])
            deployments = data.get('items', [])

            return [
                {
                    'name': deploy['metadata']['name'],
                    'replicas': deploy['spec']['replicas'],
                    'available': deploy['status'].get('availableReplicas', 0),
                    'ready': deploy['status'].get('readyReplicas', 0)
                }
                for deploy in deployments
            ]
        except Exception:
            return []

    def get_services(
        self,
        namespace: str = "default"
    ) -> List[Dict[str, Any]]:
        """获取Service列表"""
        result = self._run_kubectl([
            'get', 'services',
            '-n', namespace, '-o', 'json'
        ])

        if not result['success']:
            return []

        try:
            data = yaml.safe_load(result['stdout'])
            services = data.get('items', [])

            return [
                {
                    'name': svc['metadata']['name'],
                    'type': svc['spec']['type'],
                    'cluster_ip': svc['spec'].get('clusterIP', 'N/A'),
                    'ports': [
                        f"{p['port']}:{p['nodePort']}"
                        for p in svc['spec'].get('ports', [])
                        if 'nodePort' in p
                    ]
                }
                for svc in services
            ]
        except Exception:
            return []

    def get_pod_logs(
        self,
        pod_name: str,
        namespace: str = "default",
        tail: int = 100
    ) -> Dict[str, Any]:
        """获取Pod日志"""
        result = self._run_kubectl([
            'logs', pod_name,
            '-n', namespace,
            f'--tail={tail}'
        ])

        return result

    def rollout_status(
        self,
        deployment_name: str,
        namespace: str = "default"
    ) -> Dict[str, Any]:
        """查看rollout状态"""
        result = self._run_kubectl([
            'rollout', 'status', 'deployment', deployment_name,
            '-n', namespace
        ])

        return result

    def rollout_undo(
        self,
        deployment_name: str,
        namespace: str = "default"
    ) -> Dict[str, Any]:
        """回滚Deployment"""
        result = self._run_kubectl([
            'rollout', 'undo', 'deployment', deployment_name,
            '-n', namespace
        ])

        return result

    def apply_manifest(
        self,
        manifest_path: str,
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """应用YAML manifest文件"""
        command = ['apply', '-f', manifest_path]
        if namespace:
            command.extend(['-n', namespace])

        result = self._run_kubectl(command)
        return result
