#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Machine Controller
多机器控制能力 - 支持SSH远程执行、集群管理、并行任务
"""

import json
import os
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple
import paramiko
from pathlib import Path


class Machine:
    """单台机器配置"""

    def __init__(self, config: dict):
        self.name = config['name']
        self.host = config['host']
        self.port = config.get('port', 22)
        self.username = config['username']
        self.auth = config['auth']
        self.ssh = None
        self.sftp = None

    def connect(self) -> bool:
        """建立SSH连接"""
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if self.auth['type'] == 'key':
                key_path = os.path.expanduser(self.auth['key_path'])
                private_key = paramiko.RSAKey.from_private_key_file(key_path)
                self.ssh.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    pkey=private_key,
                    timeout=10
                )
            elif self.auth['type'] == 'password':
                self.ssh.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    password=self.auth['password'],
                    timeout=10
                )
            else:
                raise ValueError(f"不支持的认证类型: {self.auth['type']}")

            # 建立SFTP连接
            self.sftp = self.ssh.open_sftp()
            return True
        except Exception as e:
            print(f"[{self.name}] 连接失败: {e}")
            return False

    def disconnect(self):
        """断开连接"""
        if self.sftp:
            self.sftp.close()
            self.sftp = None
        if self.ssh:
            self.ssh.close()
            self.ssh = None

    def execute(self, command: str, timeout: int = 30) -> Tuple[bool, str, str]:
        """执行命令"""
        if not self.ssh:
            return False, "", "SSH连接未建立"

        try:
            stdin, stdout, stderr = self.ssh.exec_command(command, timeout=timeout)
            exit_status = stdout.channel.recv_exit_status()
            output = stdout.read().decode('utf-8', errors='ignore')
            error = stderr.read().decode('utf-8', errors='ignore')

            return exit_status == 0, output, error
        except paramiko.SSHException as e:
            return False, "", f"执行命令失败: {e}"
        except Exception as e:
            return False, "", f"未知错误: {e}"

    def upload(self, local_path: str, remote_path: str) -> Tuple[bool, str]:
        """上传文件"""
        if not self.sftp:
            return False, "SFTP连接未建立"

        try:
            self.sftp.put(local_path, remote_path)
            return True, "上传成功"
        except Exception as e:
            return False, f"上传失败: {e}"

    def download(self, remote_path: str, local_path: str) -> Tuple[bool, str]:
        """下载文件"""
        if not self.sftp:
            return False, "SFTP连接未建立"

        try:
            self.sftp.get(remote_path, local_path)
            return True, "下载成功"
        except Exception as e:
            return False, f"下载失败: {e}"

    def get_status(self) -> dict:
        """获取机器状态"""
        if not self.ssh:
            return {
                'name': self.name,
                'status': 'offline',
                'load': None,
                'disk': None
            }

        success, output, _ = self.execute('uptime && df -h / | tail -1 | awk \'{print $5}\'')
        if not success:
            return {
                'name': self.name,
                'status': 'online',
                'load': None,
                'disk': None
            }

        # 解析uptime获取负载
        lines = output.strip().split('\n')
        load = None
        disk = None

        if len(lines) > 0:
            uptime_line = lines[0]
            # 提取负载平均值（如 load average: 0.08, 0.06, 0.05）
            if 'load average:' in uptime_line:
                load_part = uptime_line.split('load average:')[-1].strip()
                load = float(load_part.split(',')[0].strip())

        if len(lines) > 1:
            disk = lines[1].strip() + ' 使用率'

        return {
            'name': self.name,
            'status': 'online',
            'load': load,
            'disk': disk
        }


class MultiMachineController:
    """多机器控制器"""

    def __init__(self, config_path: str = 'machines.json'):
        self.config_path = config_path
        self.machines: List[Machine] = []
        self.load_config()

    def load_config(self):
        """加载机器配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            self.machines = [Machine(m) for m in config.get('machines', [])]
            print(f"✓ 加载了 {len(self.machines)} 台机器配置")
        except FileNotFoundError:
            print(f"⚠ 配置文件不存在: {self.config_path}")
            self._create_sample_config()
        except json.JSONDecodeError as e:
            print(f"✗ 配置文件格式错误: {e}")

    def _create_sample_config(self):
        """创建示例配置文件"""
        sample_config = {
            "machines": [
                {
                    "name": "localhost",
                    "host": "127.0.0.1",
                    "port": 22,
                    "username": os.environ.get('USER', 'user'),
                    "auth": {
                        "type": "key",
                        "key_path": "~/.ssh/id_rsa"
                    }
                }
            ]
        }

        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(sample_config, f, indent=2, ensure_ascii=False)

        print(f"✓ 创建了示例配置文件: {self.config_path}")
        print("  请根据实际情况修改配置")

    def get_machine(self, name: str) -> Optional[Machine]:
        """根据名称获取机器"""
        for machine in self.machines:
            if machine.name == name:
                return machine
        return None

    def run_single(self, machine_name: str, command: str, timeout: int = 30) -> bool:
        """在单台机器上执行命令"""
        machine = self.get_machine(machine_name)
        if not machine:
            print(f"✗ 机器不存在: {machine_name}")
            return False

        print(f"[{machine_name}] 连接中...")
        if not machine.connect():
            print(f"[{machine_name}] ✗ 连接失败")
            return False

        print(f"[{machine_name}] 执行命令: {command}")
        success, output, error = machine.execute(command, timeout)

        if success:
            print(f"[{machine_name}] ✓ 执行成功")
            if output:
                print(f"输出:\n{output}")
        else:
            print(f"[{machine_name}] ✗ 执行失败")
            if error:
                print(f"错误: {error}")

        machine.disconnect()
        return success

    def run_parallel(self, command: str, timeout: int = 30, max_workers: int = 5):
        """在所有机器上并行执行命令"""
        results = {}

        def execute_on_machine(machine):
            if not machine.connect():
                return machine.name, False, "连接失败"

            success, output, error = machine.execute(command, timeout)
            machine.disconnect()
            return machine.name, success, output if success else error

        print(f"并行执行命令: {command}")
        print(f"目标机器: {len(self.machines)} 台")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_machine = {
                executor.submit(execute_on_machine, m): m
                for m in self.machines
            }

            for future in as_completed(future_to_machine):
                machine_name, success, result = future.result()
                results[machine_name] = {'success': success, 'output': result}

                status = "✓" if success else "✗"
                print(f"[{machine_name}] {status} {'成功' if success else '失败'}")

                if result and success:
                    print(f"  输出: {result[:200]}")  # 限制输出长度

        return results

    def status(self):
        """查看所有机器状态"""
        print("\n" + "=" * 60)
        print("集群状态")
        print("=" * 60)

        results = []
        lock = threading.Lock()

        def check_machine(machine):
            result = machine.get_status()
            with lock:
                results.append(result)

        with ThreadPoolExecutor(max_workers=10) as executor:
            list(executor.map(check_machine, self.machines))

        for r in results:
            status_icon = "●" if r['status'] == 'online' else "○"
            print(f"\n{status_icon} {r['name']}")
            print(f"  状态: {r['status']}")
            if r['load'] is not None:
                print(f"  负载: {r['load']}")
            if r['disk']:
                print(f"  磁盘: {r['disk']}")

        online = sum(1 for r in results if r['status'] == 'online')
        offline = len(results) - online

        print("\n" + "=" * 60)
        print(f"总计: {len(results)} 台 (在线: {online}, 离线: {offline})")
        print("=" * 60 + "\n")

    def upload_single(self, machine_name: str, local_path: str, remote_path: str) -> bool:
        """上传文件到单机"""
        machine = self.get_machine(machine_name)
        if not machine:
            print(f"✗ 机器不存在: {machine_name}")
            return False

        if not os.path.exists(local_path):
            print(f"✗ 本地文件不存在: {local_path}")
            return False

        print(f"[{machine_name}] 连接中...")
        if not machine.connect():
            print(f"[{machine_name}] ✗ 连接失败")
            return False

        print(f"[{machine_name}] 上传文件: {local_path} -> {remote_path}")
        success, message = machine.upload(local_path, remote_path)

        if success:
            print(f"[{machine_name}] ✓ {message}")
        else:
            print(f"[{machine_name}] ✗ {message}")

        machine.disconnect()
        return success

    def download_single(self, machine_name: str, remote_path: str, local_path: str) -> bool:
        """从单机下载文件"""
        machine = self.get_machine(machine_name)
        if not machine:
            print(f"✗ 机器不存在: {machine_name}")
            return False

        print(f"[{machine_name}] 连接中...")
        if not machine.connect():
            print(f"[{machine_name}] ✗ 连接失败")
            return False

        print(f"[{machine_name}] 下载文件: {remote_path} -> {local_path}")
        success, message = machine.download(remote_path, local_path)

        if success:
            print(f"[{machine_name}] ✓ {message}")
        else:
            print(f"[{machine_name}] ✗ {message}")

        machine.disconnect()
        return success


def print_usage():
    """打印使用说明"""
    print("""
Multi-Machine Controller - 多机器控制能力

用法:
  python3 multi-machine.py run <machine_name> "<command>"      单机执行
  python3 multi-machine.py parallel "<command>"                并行执行
  python3 multi-machine.py status                              查看状态
  python3 multi-machine.py upload <machine_name> <local> <remote>  上传文件
  python3 multi-machine.py download <machine_name> <remote> <local>  下载文件

配置:
  编辑 machines.json 配置机器列表

示例:
  python3 multi-machine.py run server1 "ls -la"
  python3 multi-machine.py parallel "uptime"
  python3 multi-machine.py status
  python3 multi-machine.py upload server1 ./test.txt /tmp/test.txt
    """)


def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    # 切换到技能目录
    skill_dir = Path(__file__).parent
    os.chdir(skill_dir)

    config_path = skill_dir / 'machines.json'
    controller = MultiMachineController(str(config_path))

    action = sys.argv[1]

    if action == 'run':
        if len(sys.argv) < 4:
            print("用法: python3 multi-machine.py run <machine_name> <command>")
            sys.exit(1)
        machine_name = sys.argv[2]
        command = ' '.join(sys.argv[3:])
        success = controller.run_single(machine_name, command)
        sys.exit(0 if success else 1)

    elif action == 'parallel':
        if len(sys.argv) < 3:
            print("用法: python3 multi-machine.py parallel <command>")
            sys.exit(1)
        command = ' '.join(sys.argv[2:])
        controller.run_parallel(command)
        sys.exit(0)

    elif action == 'status':
        controller.status()
        sys.exit(0)

    elif action == 'upload':
        if len(sys.argv) < 5:
            print("用法: python3 multi-machine.py upload <machine_name> <local> <remote>")
            sys.exit(1)
        machine_name = sys.argv[2]
        local_path = sys.argv[3]
        remote_path = sys.argv[4]
        success = controller.upload_single(machine_name, local_path, remote_path)
        sys.exit(0 if success else 1)

    elif action == 'download':
        if len(sys.argv) < 5:
            print("用法: python3 multi-machine.py download <machine_name> <remote> <local>")
            sys.exit(1)
        machine_name = sys.argv[2]
        remote_path = sys.argv[3]
        local_path = sys.argv[4]
        success = controller.download_single(machine_name, remote_path, local_path)
        sys.exit(0 if success else 1)

    else:
        print(f"未知操作: {action}")
        print_usage()
        sys.exit(1)


if __name__ == '__main__':
    main()
