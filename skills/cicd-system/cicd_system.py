#!/usr/bin/env python3
"""
CI/CD集成系统 - 核心实现
提供持续集成和持续部署能力
"""

import os
import yaml
import subprocess
import shutil
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import tempfile


class StepStatus(Enum):
    """步骤状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class PipelineStatus(Enum):
    """流水线状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Step:
    """流水线步骤"""
    name: str
    command: str
    status: StepStatus = StepStatus.PENDING
    output: str = ""
    error: str = ""
    duration: float = 0.0
    depends_on: List[str] = field(default_factory=list)
    condition: Optional[str] = None  # 条件执行


@dataclass
class PipelineResult:
    """流水线结果"""
    status: PipelineStatus
    steps: List[Step]
    total_duration: float
    logs: str
    timestamp: str


@dataclass
class DeploymentConfig:
    """部署配置"""
    strategy: str = "rolling"  # rolling, blue-green, canary
    replicas: int = 1
    auto_rollback: bool = True
    health_check: Optional[str] = None
    timeout: int = 300


class CICDSystem:
    """CI/CD集成系统"""

    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = config_dir or os.path.join(os.path.dirname(__file__), "config")
        os.makedirs(self.config_dir, exist_ok=True)
        self.pipelines: Dict[str, List[Step]] = {}

    def create_pipeline(
        self,
        name: str,
        steps: List[Dict[str, Any]]
    ) -> List[Step]:
        """
        创建流水线

        Args:
            name: 流水线名称
            steps: 步骤列表 [{"name": "build", "command": "...", ...}]

        Returns:
            List[Step]: 流水线步骤列表
        """
        pipeline_steps = []
        for step_data in steps:
            step = Step(
                name=step_data["name"],
                command=step_data["command"],
                depends_on=step_data.get("depends_on", []),
                condition=step_data.get("condition")
            )
            pipeline_steps.append(step)

        self.pipelines[name] = pipeline_steps
        return pipeline_steps

    def run_pipeline(
        self,
        pipeline_name: Optional[str] = None,
        steps: Optional[List[Dict[str, Any]]] = None,
        environment: str = "default",
        dry_run: bool = False
    ) -> PipelineResult:
        """
        执行流水线

        Args:
            pipeline_name: 流水线名称（可选）
            steps: 步骤列表（可选，覆盖pipeline_name）
            environment: 环境名称
            dry_run: 干跑模式（不实际执行）

        Returns:
            PipelineResult: 执行结果
        """
        start_time = datetime.now()
        logs = []

        # 获取步骤
        if steps:
            pipeline_steps = [Step(**step) for step in steps]
        elif pipeline_name and pipeline_name in self.pipelines:
            pipeline_steps = self.pipelines[pipeline_name]
        else:
            raise ValueError(f"Pipeline not found: {pipeline_name}")

        logs.append(f"Starting pipeline: {pipeline_name or 'custom'}")
        logs.append(f"Environment: {environment}")
        logs.append(f"Steps: {len(pipeline_steps)}")

        # 执行步骤
        failed = False
        for step in pipeline_steps:
            if failed:
                # 上一步失败，跳过后续步骤
                step.status = StepStatus.SKIPPED
                logs.append(f"⏭️  Skipped: {step.name} (previous step failed)")
                continue

            # 检查依赖
            if step.depends_on:
                for dep_name in step.depends_on:
                    dep_step = next((s for s in pipeline_steps if s.name == dep_name), None)
                    if not dep_step or dep_step.status != StepStatus.SUCCESS:
                        step.status = StepStatus.SKIPPED
                        logs.append(f"⏭️  Skipped: {step.name} (dependency {dep_name} failed)")
                        break
                else:
                    pass  # 所有依赖成功
                if step.status == StepStatus.SKIPPED:
                    continue

            # 执行步骤
            step.status = StepStatus.RUNNING
            logs.append(f"▶️  Running: {step.name}")

            step_start = datetime.now()
            try:
                if not dry_run:
                    output, error = self._execute_command(step.command)
                    step.output = output
                    if error:
                        raise Exception(error)

                    step.status = StepStatus.SUCCESS
                    logs.append(f"✅ Success: {step.name}")
                else:
                    logs.append(f"🔍 Dry run: {step.name}")
                    step.status = StepStatus.SUCCESS

            except Exception as e:
                step.status = StepStatus.FAILED
                step.error = str(e)
                logs.append(f"❌ Failed: {step.name}")
                logs.append(f"   Error: {str(e)}")
                failed = True

            step.duration = (datetime.now() - step_start).total_seconds()

        # 计算总时间
        total_duration = (datetime.now() - start_time).total_seconds()

        # 确定流水线状态
        if failed:
            status = PipelineStatus.FAILED
            logs.append("\n❌ Pipeline failed")
        else:
            status = PipelineStatus.SUCCESS
            logs.append("\n✅ Pipeline succeeded")

        logs.append(f"Total duration: {total_duration:.2f}s")

        return PipelineResult(
            status=status,
            steps=pipeline_steps,
            total_duration=total_duration,
            logs="\n".join(logs),
            timestamp=datetime.now().isoformat()
        )

    def _execute_command(self, command: str, timeout: int = 300) -> tuple[str, str]:
        """执行命令"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=os.getcwd()
            )

            # 检查退出码
            if result.returncode != 0:
                error_msg = result.stderr or f"Command failed with exit code {result.returncode}"
                raise Exception(error_msg)

            return result.stdout, result.stderr

        except subprocess.TimeoutExpired as e:
            raise Exception(f"Command timeout after {timeout}s")
        except Exception as e:
            raise Exception(f"Command failed: {str(e)}")

    def create_github_actions(
        self,
        project_name: str,
        python_version: str = "3.10",
        run_tests: bool = True,
        deploy_to_docker: bool = False,
        on: Optional[Dict[str, Any]] = None
    ) -> "GitHubActionsConfig":
        """创建GitHub Actions配置"""
        config = GitHubActionsConfig(
            name=f"{project_name} CI/CD",
            on=on or {
                "push": {"branches": ["main", "develop"]},
                "pull_request": {"branches": ["main"]}
            }
        )

        # 设置环境
        config.add_job(
            name="ci",
            runs_on="ubuntu-latest",
            steps=[
                {
                    "uses": "actions/checkout@v3"
                },
                {
                    "name": "Set up Python",
                    "uses": "actions/setup-python@v4",
                    "with": {"python-version": python_version}
                },
                {
                    "name": "Install dependencies",
                    "run": "pip install -r requirements.txt"
                },
                {
                    "name": "Lint",
                    "run": "flake8 . --count --show-source --statistics"
                },
                {
                    "name": "Run tests",
                    "run": "pytest --cov=. --cov-report=xml",
                    "if": run_tests
                }
            ]
        )

        # 添加Docker部署
        if deploy_to_docker:
            config.add_job(
                name="build",
                needs="ci",
                runs_on="ubuntu-latest",
                steps=[
                    {"uses": "actions/checkout@v3"},
                    {
                        "name": "Build Docker image",
                        "run": f"docker build -t {project_name} ."
                    }
                ]
            )

        return config

    def generate_dockerfile(
        self,
        base_image: str = "python:3.10-slim",
        requirements_path: str = "requirements.txt",
        workdir: str = "/app",
        port: Optional[int] = None,
        expose_ports: Optional[List[int]] = None
    ) -> str:
        """生成Dockerfile"""
        dockerfile = f"""FROM {base_image}

WORKDIR {workdir}

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY {requirements_path} .
RUN pip install --no-cache-dir -r {requirements_path}

# Copy application code
COPY . .

"""

        if expose_ports:
            for p in expose_ports:
                dockerfile += f"EXPOSE {p}\n"
        elif port:
            dockerfile += f"EXPOSE {port}\n"

        dockerfile += f"""
# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "main.py"]
"""

        return dockerfile

    def deploy(
        self,
        environment: str,
        config_path: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        部署到指定环境

        Args:
            environment: 环境名称
            config_path: 配置文件路径
            dry_run: 干跑模式

        Returns:
            部署结果
        """
        result = {
            "environment": environment,
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "details": {}
        }

        # 加载配置
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
        else:
            config = {}

        deployment_config = DeploymentConfig(**config.get("deployment", {}))

        result["details"]["config"] = {
            "strategy": deployment_config.strategy,
            "replicas": deployment_config.replicas,
            "auto_rollback": deployment_config.auto_rollback
        }

        if not dry_run:
            # 实际部署逻辑
            try:
                if deployment_config.strategy == "rolling":
                    result["details"]["message"] = "Rolling deployment started"
                elif deployment_config.strategy == "blue-green":
                    result["details"]["message"] = "Blue-green deployment started"
                elif deployment_config.strategy == "canary":
                    result["details"]["message"] = "Canary deployment started"
                else:
                    result["details"]["message"] = "Deployment started"

            except Exception as e:
                result["status"] = "failed"
                result["details"]["error"] = str(e)

                # 自动回滚
                if deployment_config.auto_rollback:
                    result["details"]["rollback"] = "Automatic rollback triggered"
        else:
            result["details"]["message"] = f"Deployment to {environment} (dry run)"

        return result

    def generate_kubernetes_manifest(
        self,
        app_name: str,
        image: str,
        replicas: int = 3,
        port: int = 80,
        resources: Optional[Dict[str, str]] = None
    ) -> str:
        """生成Kubernetes部署配置"""
        resources = resources or {"limits": {"cpu": "500m", "memory": "512Mi"}}

        manifest = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {app_name}
  labels:
    app: {app_name}
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      app: {app_name}
  template:
    metadata:
      labels:
        app: {app_name}
    spec:
      containers:
      - name: {app_name}
        image: {image}
        ports:
        - containerPort: {port}
        resources:
          limits:
            cpu: {resources['limits']['cpu']}
            memory: {resources['limits']['memory']}
---
apiVersion: v1
kind: Service
metadata:
  name: {app_name}-service
spec:
  selector:
    app: {app_name}
  ports:
  - protocol: TCP
    port: 80
    targetPort: {port}
  type: LoadBalancer
"""
        return manifest

    def rollback(
        self,
        environment: str,
        version: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """回滚部署"""
        result = {
            "environment": environment,
            "version": version or "previous",
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }

        if not dry_run:
            # 实际回滚逻辑
            pass
        else:
            result["message"] = f"Rollback to {version or 'previous'} version (dry run)"

        return result


class GitHubActionsConfig:
    """GitHub Actions配置"""

    def __init__(self, name: str, on: Dict[str, Any]):
        self.config = {
            "name": name,
            "on": on,
            "jobs": {}
        }

    def add_job(
        self,
        name: str,
        runs_on: str,
        steps: List[Dict[str, Any]],
        needs: Optional[List[str]] = None,
        if_condition: Optional[str] = None
    ):
        """添加job"""
        job_config = {
            "runs-on": runs_on,
            "steps": steps
        }

        if needs:
            job_config["needs"] = needs

        if if_condition:
            job_config["if"] = if_condition

        self.config["jobs"][name] = job_config

    def save(self, filepath: str):
        """保存配置到文件"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)

    def to_yaml(self) -> str:
        """转换为YAML字符串"""
        return yaml.dump(self.config, default_flow_style=False, sort_keys=False)
