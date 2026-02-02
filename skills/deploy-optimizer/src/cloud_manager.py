"""
云服务管理器
"""

import subprocess
from typing import Dict, Any, Optional, List


class CloudManager:
    """云服务管理器"""

    def __init__(self):
        self.providers = {
            'aliyun': {
                'enabled': False,
                'cli': 'aliyun'
            },
            'aws': {
                'enabled': False,
                'cli': 'aws'
            },
            'tencent': {
                'enabled': False,
                'cli': 'tencentcli'
            }
        }

        # 检查各个云服务的CLI是否可用
        for provider, info in self.providers.items():
            info['enabled'] = self._check_cli(info['cli'])

    def _check_cli(self, cli_name: str) -> bool:
        """检查CLI工具是否可用"""
        try:
            result = subprocess.run(
                [cli_name, 'version'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def is_provider_available(self, provider: str) -> bool:
        """检查云服务提供商是否可用"""
        return self.providers.get(provider, {}).get('enabled', False)

    def get_available_providers(self) -> List[str]:
        """获取可用的云服务提供商列表"""
        return [
            provider
            for provider, info in self.providers.items()
            if info['enabled']
        ]

    def deploy_to_aliyun(
        self,
        region: str = "cn-hangzhou",
        instance_type: str = "ecs.t6-c1m1.large",
        image_id: str = "ubuntu_20_04_x64_20G_alibase_20230628.vhd",
        vswitch_id: Optional[str] = None,
        security_group_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """部署到阿里云ECS"""
        if not self.is_provider_available('aliyun'):
            return {
                'success': False,
                'error': '阿里云CLI不可用，请先安装并配置aliyun CLI'
            }

        command = [
            'ecs', 'CreateInstance',
            '--RegionId', region,
            '--InstanceType', instance_type,
            '--ImageId', image_id,
            '--IoOptimized', 'optimized'
        ]

        if vswitch_id:
            command.extend(['--VSwitchId', vswitch_id])
        if security_group_id:
            command.extend(['--SecurityGroupId', security_group_id])

        try:
            result = subprocess.run(
                ['aliyun'] + command,
                capture_output=True,
                text=True
            )

            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def deploy_to_aws(
        self,
        region: str = "us-east-1",
        instance_type: str = "t2.micro",
        image_id: str = "ami-0c55b159cbfafe1f0",
        key_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """部署到AWS EC2"""
        if not self.is_provider_available('aws'):
            return {
                'success': False,
                'error': 'AWS CLI不可用，请先安装并配置aws CLI'
            }

        command = [
            'ec2', 'run-instances',
            '--region', region,
            '--image-id', image_id,
            '--instance-type', instance_type,
            '--count', '1'
        ]

        if key_name:
            command.extend(['--key-name', key_name])

        try:
            result = subprocess.run(
                ['aws'] + command,
                capture_output=True,
                text=True
            )

            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def deploy_to_tencent(
        self,
        region: str = "ap-guangzhou",
        instance_type: str = "S2.MEDIUM2",
        image_id: str = "img-xxx"
    ) -> Dict[str, Any]:
        """部署到腾讯云CVM"""
        if not self.is_provider_available('tencent'):
            return {
                'success': False,
                'error': '腾讯云CLI不可用，请先安装并配置tencentcli'
            }

        command = [
            'cvm', 'RunInstances',
            '--Region', region,
            '--InstanceType', instance_type,
            '--ImageId', image_id,
            '--InstanceCount', '1'
        ]

        try:
            result = subprocess.run(
                ['tencentcli'] + command,
                capture_output=True,
                text=True
            )

            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def list_aliyun_instances(self, region: str = "cn-hangzhou") -> Dict[str, Any]:
        """列出阿里云ECS实例"""
        if not self.is_provider_available('aliyun'):
            return {
                'success': False,
                'error': '阿里云CLI不可用'
            }

        result = subprocess.run(
            ['aliyun', 'ecs', 'DescribeInstances', '--RegionId', region],
            capture_output=True,
            text=True
        )

        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr
        }

    def list_aws_instances(self, region: str = "us-east-1") -> Dict[str, Any]:
        """列出AWS EC2实例"""
        if not self.is_provider_available('aws'):
            return {
                'success': False,
                'error': 'AWS CLI不可用'
            }

        result = subprocess.run(
            ['aws', 'ec2', 'describe-instances', '--region', region],
            capture_output=True,
            text=True
        )

        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr
        }

    def start_instance(
        self,
        provider: str,
        instance_id: str,
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """启动云实例"""
        if provider == 'aliyun':
            command = ['ecs', 'StartInstance', '--InstanceId', instance_id]
            if region:
                command.extend(['--RegionId', region])
            cli = 'aliyun'
        elif provider == 'aws':
            command = ['ec2', 'start-instances', '--instance-ids', instance_id]
            if region:
                command.extend(['--region', region])
            cli = 'aws'
        else:
            return {
                'success': False,
                'error': f'不支持的提供商: {provider}'
            }

        result = subprocess.run(
            [cli] + command,
            capture_output=True,
            text=True
        )

        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr
        }

    def stop_instance(
        self,
        provider: str,
        instance_id: str,
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """停止云实例"""
        if provider == 'aliyun':
            command = ['ecs', 'StopInstance', '--InstanceId', instance_id]
            if region:
                command.extend(['--RegionId', region])
            cli = 'aliyun'
        elif provider == 'aws':
            command = ['ec2', 'stop-instances', '--instance-ids', instance_id]
            if region:
                command.extend(['--region', region])
            cli = 'aws'
        else:
            return {
                'success': False,
                'error': f'不支持的提供商: {provider}'
            }

        result = subprocess.run(
            [cli] + command,
            capture_output=True,
            text=True
        )

        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr
        }

    def delete_instance(
        self,
        provider: str,
        instance_id: str,
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """删除云实例"""
        if provider == 'aliyun':
            command = ['ecs', 'DeleteInstance', '--InstanceId', instance_id]
            if region:
                command.extend(['--RegionId', region])
            cli = 'aliyun'
        elif provider == 'aws':
            command = ['ec2', 'terminate-instances', '--instance-ids', instance_id]
            if region:
                command.extend(['--region', region])
            cli = 'aws'
        else:
            return {
                'success': False,
                'error': f'不支持的提供商: {provider}'
            }

        result = subprocess.run(
            [cli] + command,
            capture_output=True,
            text=True
        )

        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
