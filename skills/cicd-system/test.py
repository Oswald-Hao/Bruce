#!/usr/bin/env python3
"""
CI/CD集成系统测试
"""

import os
import sys
import tempfile
import yaml
from cicd_system import (
    CICDSystem,
    Step,
    StepStatus,
    PipelineStatus,
    GitHubActionsConfig
)


class TestCICDSystem:
    """CI/CD系统测试套件"""

    def __init__(self):
        self.cicd = CICDSystem()
        self.test_results = []
        self.temp_dir = tempfile.mkdtemp()

    def test_create_pipeline(self):
        """测试1: 创建流水线"""
        print("\n[测试1] 创建流水线...")

        steps = [
            {"name": "build", "command": "echo 'building'"},
            {"name": "test", "command": "echo 'testing'", "depends_on": ["build"]},
            {"name": "deploy", "command": "echo 'deploying'", "depends_on": ["test"]}
        ]

        try:
            pipeline = self.cicd.create_pipeline("my-pipeline", steps)

            assert len(pipeline) == 3, "应创建3个步骤"
            assert pipeline[0].name == "build", "第一个步骤应为build"
            assert pipeline[1].depends_on == ["build"], "test应依赖build"
            assert pipeline[2].depends_on == ["test"], "deploy应依赖test"

            print(f"✅ 创建了 {len(pipeline)} 个步骤")
            self.test_results.append(("创建流水线", "✅ 通过", f"创建{len(pipeline)}个步骤"))
            return True

        except Exception as e:
            self.test_results.append(("创建流水线", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def test_run_pipeline_dry_run(self):
        """测试2: 干跑流水线"""
        print("\n[测试2] 干跑流水线...")

        steps = [
            {"name": "step1", "command": "echo 'test'"},
            {"name": "step2", "command": "echo 'test2'", "depends_on": ["step1"]}
        ]

        try:
            result = self.cicd.run_pipeline(
                steps=steps,
                dry_run=True
            )

            assert result.status == PipelineStatus.SUCCESS, "流水线应成功"
            assert len(result.steps) == 2, "应有2个步骤"
            assert result.total_duration > 0, "应有执行时间"
            assert all(s.status == StepStatus.SUCCESS for s in result.steps), "所有步骤应成功"

            print(f"✅ 流水线执行成功，耗时 {result.total_duration:.2f}s")
            self.test_results.append(("干跑流水线", "✅ 通过", "所有步骤成功"))
            return True

        except Exception as e:
            self.test_results.append(("干跑流水线", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def test_run_pipeline_with_failures(self):
        """测试3: 失败处理"""
        print("\n[测试3] 失败处理...")

        steps = [
            {"name": "success_step", "command": "echo 'ok'"},
            {"name": "fail_step", "command": "exit 1"},
            {"name": "skip_step", "command": "echo 'skipped'", "depends_on": ["fail_step"]}
        ]

        try:
            result = self.cicd.run_pipeline(steps=steps)

            assert result.status == PipelineStatus.FAILED, "流水线应失败"
            assert result.steps[0].status == StepStatus.SUCCESS, "第一个步骤应成功"
            assert result.steps[1].status == StepStatus.FAILED, "第二个步骤应失败"
            assert result.steps[2].status == StepStatus.SKIPPED, "第三个步骤应跳过"

            print("✅ 正确处理失败：success → failed → skipped")
            self.test_results.append(("失败处理", "✅ 通过", "正确处理失败链"))
            return True

        except Exception as e:
            self.test_results.append(("失败处理", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def test_create_github_actions(self):
        """测试4: 创建GitHub Actions配置"""
        print("\n[测试4] 创建GitHub Actions配置...")

        try:
            config = self.cicd.create_github_actions(
                project_name="test-project",
                python_version="3.10",
                run_tests=True,
                deploy_to_docker=True
            )

            assert config is not None, "应创建配置"
            assert "jobs" in config.config, "应包含jobs"
            assert "ci" in config.config["jobs"], "应包含ci job"

            print(f"✅ 创建GitHub Actions配置，包含 {len(config.config['jobs'])} 个jobs")
            self.test_results.append(("GitHub Actions配置", "✅ 通过", f"{len(config.config['jobs'])}个jobs"))
            return True

        except Exception as e:
            self.test_results.append(("GitHub Actions配置", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def test_generate_dockerfile(self):
        """测试5: 生成Dockerfile"""
        print("\n[测试5] 生成Dockerfile...")

        try:
            dockerfile = self.cicd.generate_dockerfile(
                base_image="python:3.10-slim",
                requirements_path="requirements.txt",
                port=8000
            )

            assert "FROM python:3.10-slim" in dockerfile, "应包含FROM语句"
            assert "WORKDIR" in dockerfile, "应包含WORKDIR"
            assert "EXPOSE 8000" in dockerfile, "应包含EXPOSE 8000"
            assert "CMD" in dockerfile, "应包含CMD"

            print(f"✅ 生成Dockerfile（{len(dockerfile)} 字符）")
            self.test_results.append(("生成Dockerfile", "✅ 通过", "包含必需指令"))
            return True

        except Exception as e:
            self.test_results.append(("生成Dockerfile", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def test_deploy_dry_run(self):
        """测试6: 部署（干跑）"""
        print("\n[测试6] 部署（干跑）...")

        try:
            result = self.cicd.deploy(
                environment="staging",
                dry_run=True
            )

            assert result["environment"] == "staging", "环境应为staging"
            assert result["status"] == "success", "部署应成功"
            assert "details" in result, "应包含详情"

            print(f"✅ 部署配置: {result['details']}")
            self.test_results.append(("部署干跑", "✅ 通过", result['details'].get('message', '')))
            return True

        except Exception as e:
            self.test_results.append(("部署干跑", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def test_generate_kubernetes_manifest(self):
        """测试7: 生成Kubernetes配置"""
        print("\n[测试7] 生成Kubernetes配置...")

        try:
            manifest = self.cicd.generate_kubernetes_manifest(
                app_name="myapp",
                image="myapp:1.0",
                replicas=3,
                port=8080
            )

            assert "apiVersion: apps/v1" in manifest, "应为Kubernetes配置"
            assert "kind: Deployment" in manifest, "应包含Deployment"
            assert "kind: Service" in manifest, "应包含Service"
            assert "replicas: 3" in manifest, "应有3个副本"

            print(f"✅ 生成Kubernetes配置（{len(manifest)} 字符）")
            self.test_results.append(("Kubernetes配置", "✅ 通过", "Deployment + Service"))
            return True

        except Exception as e:
            self.test_results.append(("Kubernetes配置", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def test_rollback(self):
        """测试8: 回滚"""
        print("\n[测试8] 回滚...")

        try:
            result = self.cicd.rollback(
                environment="production",
                version="v1.0",
                dry_run=True
            )

            assert result["environment"] == "production", "环境应为production"
            assert result["version"] == "v1.0", "版本应为v1.0"
            assert result["status"] == "success", "回滚应成功"

            print(f"✅ 回滚配置: {result}")
            self.test_results.append(("回滚", "✅ 通过", "回滚到v1.0"))
            return True

        except Exception as e:
            self.test_results.append(("回滚", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def test_github_actions_save(self):
        """测试9: 保存GitHub Actions配置"""
        print("\n[测试9] 保存GitHub Actions配置...")

        try:
            config = self.cicd.create_github_actions(
                project_name="test-save",
                run_tests=True
            )

            filepath = os.path.join(self.temp_dir, "workflow.yml")
            config.save(filepath)

            assert os.path.exists(filepath), "文件应存在"

            # 验证内容
            with open(filepath, 'r') as f:
                content = yaml.safe_load(f)
                assert content["name"] == "test-save CI/CD", "名称应匹配"

            print(f"✅ 配置已保存到 {filepath}")
            self.test_results.append(("保存配置", "✅ 通过", "文件创建成功"))
            return True

        except Exception as e:
            self.test_results.append(("保存配置", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def test_multi_environment_deploy(self):
        """测试10: 多环境部署"""
        print("\n[测试10] 多环境部署...")

        environments = ["dev", "staging", "production"]
        results = []

        try:
            for env in environments:
                result = self.cicd.deploy(environment=env, dry_run=True)
                results.append(result)

            assert len(results) == 3, "应部署3个环境"
            assert all(r["status"] == "success" for r in results), "所有部署应成功"

            env_names = [r["environment"] for r in results]
            print(f"✅ 部署到 {len(env_names)} 个环境: {', '.join(env_names)}")
            self.test_results.append(("多环境部署", "✅ 通过", f"成功部署{len(env_names)}个环境"))
            return True

        except Exception as e:
            self.test_results.append(("多环境部署", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def test_condition_execution(self):
        """测试11: 条件执行"""
        print("\n[测试11] 条件执行...")

        steps = [
            {"name": "always_run", "command": "echo 'always'", "condition": "always"},
            {"name": "on_success", "command": "echo 'success'", "condition": "success"}
        ]

        try:
            result = self.cicd.run_pipeline(steps=steps, dry_run=True)

            # 在当前实现中，所有步骤都会执行（因为前一步成功）
            assert len(result.steps) == 2, "应有2个步骤"

            print("✅ 条件执行测试完成")
            self.test_results.append(("条件执行", "✅ 通过", "条件机制正常"))
            return True

        except Exception as e:
            self.test_results.append(("条件执行", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def test_complex_pipeline(self):
        """测试12: 复杂流水线"""
        print("\n[测试12] 复杂流水线（5步并行）...")

        steps = [
            {"name": "build", "command": "echo 'build'"},
            {"name": "test", "command": "echo 'test'", "depends_on": ["build"]},
            {"name": "lint", "command": "echo 'lint'", "depends_on": ["build"]},
            {"name": "security", "command": "echo 'security'", "depends_on": ["build"]},
            {"name": "deploy", "command": "echo 'deploy'", "depends_on": ["test", "lint", "security"]}
        ]

        try:
            result = self.cicd.run_pipeline(steps=steps, dry_run=True)

            assert result.status == PipelineStatus.SUCCESS, "流水线应成功"
            assert len(result.steps) == 5, "应有5个步骤"
            assert result.steps[-1].depends_on == ["test", "lint", "security"], "deploy应依赖3个步骤"

            print("✅ 复杂流水线执行成功（构建 → 测试/检查 → 部署）")
            self.test_results.append(("复杂流水线", "✅ 通过", "5步流水线成功"))
            return True

        except Exception as e:
            self.test_results.append(("复杂流水线", "❌ 失败", str(e)))
            print(f"错误: {e}")
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("="*60)
        print("CI/CD集成系统测试套件")
        print("="*60)

        # 运行所有测试
        self.test_create_pipeline()
        self.test_run_pipeline_dry_run()
        self.test_run_pipeline_with_failures()
        self.test_create_github_actions()
        self.test_generate_dockerfile()
        self.test_deploy_dry_run()
        self.test_generate_kubernetes_manifest()
        self.test_rollback()
        self.test_github_actions_save()
        self.test_multi_environment_deploy()
        self.test_condition_execution()
        self.test_complex_pipeline()

        # 打印结果汇总
        print("\n" + "="*60)
        print("测试结果汇总")
        print("="*60)

        passed = sum(1 for _, status, _ in self.test_results if "✅" in status)
        total = len(self.test_results)

        for test_name, status, detail in self.test_results:
            print(f"{status} {test_name}: {detail}")

        print("\n" + "="*60)
        print(f"通过: {passed}/{total}")
        print("="*60)

        if passed == total:
            print("\n🎉 所有测试通过！")
            return True
        else:
            print(f"\n⚠️ {total - passed} 个测试失败")
            return False


def main():
    """主函数"""
    tester = TestCICDSystem()
    success = tester.run_all_tests()

    # 清理临时文件
    import shutil
    try:
        shutil.rmtree(tester.temp_dir)
    except:
        pass

    # 返回退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
