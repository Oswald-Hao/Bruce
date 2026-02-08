#!/usr/bin/env python3
"""
版本控制增强器
Git版本控制增强工具
"""

import os
import subprocess
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from collections import Counter


class VersionControl:
    """版本控制器"""

    def __init__(self, repo_path: str = "."):
        """
        初始化版本控制器

        Args:
            repo_path: Git仓库路径
        """
        self.repo_path = repo_path
        self._check_git()

    def _check_git(self):
        """检查git是否安装和是否在git仓库中"""
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=self.repo_path
            )
            if result.returncode != 0:
                raise RuntimeError("git未安装")
        except FileNotFoundError:
            raise RuntimeError("git未安装")

        # 检查是否在git仓库中
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=self.repo_path
        )
        if result.returncode != 0:
            raise RuntimeError("不在Git仓库中")

    def _run_git(self, args: List[str], timeout: int = 30) -> Tuple[bool, str]:
        """
        执行git命令

        Args:
            args: git命令参数
            timeout: 超时时间（秒）

        Returns:
            (是否成功, 输出或错误信息)
        """
        try:
            result = subprocess.run(
                ["git"] + args,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.repo_path
            )
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr
        except subprocess.TimeoutExpired:
            return False, f"命令执行超时（{timeout}秒）"
        except Exception as e:
            return False, str(e)

    def status(self) -> Dict:
        """
        获取Git状态

        Returns:
            状态信息字典
        """
        success, output = self._run_git(["status", "--porcelain"])
        if not success:
            return {"error": output}

        # 解析状态输出
        modified = []
        added = []
        deleted = []
        untracked = []

        for line in output.strip().split('\n'):
            if not line:
                continue

            status = line[:2]
            file_path = line[3:]

            if 'M' in status:
                modified.append(file_path)
            if 'A' in status:
                added.append(file_path)
            if 'D' in status:
                deleted.append(file_path)
            if '??' in status:
                untracked.append(file_path)

        return {
            "modified": modified,
            "added": added,
            "deleted": deleted,
            "untracked": untracked,
            "has_changes": bool(modified or added or deleted or untracked)
        }

    def smart_commit(self, message: Optional[str] = None, add_all: bool = True) -> bool:
        """
        智能提交

        Args:
            message: 提交信息（为空则自动生成）
            add_all: 是否添加所有变更

        Returns:
            是否成功
        """
        # 获取状态
        status = self.status()

        if not status.get("has_changes", False):
            print("没有变更需要提交")
            return True

        # 自动生成提交信息
        if not message:
            message = self._generate_commit_message(status)

        # 添加文件
        if add_all:
            success, output = self._run_git(["add", "."])
            if not success:
                raise RuntimeError(f"添加文件失败: {output}")

        # 提交
        success, output = self._run_git(["commit", "-m", message])
        if not success:
            raise RuntimeError(f"提交失败: {output}")

        print(f"✓ 提交成功: {message}")
        return True

    def _generate_commit_message(self, status: Dict) -> str:
        """
        生成提交信息

        Args:
            status: Git状态

        Returns:
            提交信息
        """
        modified = status.get("modified", [])
        added = status.get("added", [])
        deleted = status.get("deleted", [])
        untracked = status.get("untracked", [])

        parts = []

        if added:
            parts.append(f"添加 {len(added)} 个文件")
        if modified:
            parts.append(f"修改 {len(modified)} 个文件")
        if deleted:
            parts.append(f"删除 {len(deleted)} 个文件")
        if untracked:
            parts.append(f"新增 {len(untracked)} 个文件")

        if parts:
            message = "、".join(parts)
        else:
            message = "更新代码"

        return message

    def create_branch(self, branch_name: str, checkout: bool = True) -> bool:
        """
        创建分支

        Args:
            branch_name: 分支名称
            checkout: 是否切换到新分支

        Returns:
            是否成功
        """
        args = ["branch", branch_name]
        if checkout:
            args.insert(1, "-b")

        success, output = self._run_git(args)
        if not success:
            raise RuntimeError(f"创建分支失败: {output}")

        action = "创建并切换" if checkout else "创建"
        print(f"✓ {action}分支: {branch_name}")
        return True

    def switch_branch(self, branch_name: str) -> bool:
        """
        切换分支

        Args:
            branch_name: 分支名称

        Returns:
            是否成功
        """
        success, output = self._run_git(["checkout", branch_name])
        if not success:
            raise RuntimeError(f"切换分支失败: {output}")

        print(f"✓ 切换到分支: {branch_name}")
        return True

    def list_branches(self) -> Dict:
        """
        列出所有分支

        Returns:
            分支列表
        """
        success, output = self._run_git(["branch", "-a"])
        if not success:
            raise RuntimeError(f"获取分支列表失败: {output}")

        branches = []
        current = None

        for line in output.strip().split('\n'):
            if not line:
                continue

            if line.startswith('*'):
                line = line[1:].strip()
                current = line
            else:
                line = line.strip()

            if line.startswith('remotes/'):
                continue

            branch_name = line.split('/')[-1]
            branches.append(branch_name)

        return {
            "branches": branches,
            "current": current
        }

    def analyze_history(self, count: int = 10) -> Dict:
        """
        分析提交历史

        Args:
            count: 提交数量

        Returns:
            历史统计
        """
        success, output = self._run_git(["log", f"-{count}", "--pretty=format:%an|%ae|%s", "--date=format:%Y-%m-%d"])
        if not success:
            return {"error": output}

        commits = []
        authors = []

        for line in output.strip().split('\n'):
            if not line:
                continue

            parts = line.split('|')
            if len(parts) >= 3:
                author = parts[0]
                date = parts[1]
                subject = parts[2]

                commits.append({
                    "author": author,
                    "date": date,
                    "message": subject
                })

                if author:
                    authors.append(author)

        # 统计
        author_count = Counter(authors)
        total_commits = len(commits)

        return {
            "total_commits": total_commits,
            "commits": commits,
            "authors": dict(author_count),
            "top_author": author_count.most_common(1)[0] if author_count else None
        }

    def get_diff(self, file_path: Optional[str] = None) -> str:
        """
        获取差异

        Args:
            file_path: 文件路径（为空则显示所有差异）

        Returns:
            差异文本
        """
        args = ["diff"]
        if file_path:
            args.append("--")
            args.append(file_path)

        success, output = self._run_git(args)
        if not success:
            raise RuntimeError(f"获取差异失败: {output}")

        return output

    def push(self, branch: Optional[str] = None) -> bool:
        """
        推送到远程仓库

        Args:
            branch: 分支名称（为空则推送当前分支）

        Returns:
            是否成功
        """
        args = ["push"]
        if branch:
            args.append(f"origin/{branch}")

        success, output = self._run_git(args, timeout=120)
        if not success:
            raise RuntimeError(f"推送失败: {output}")

        print(f"✓ 推送成功")
        return True

    def pull(self) -> bool:
        """
        从远程仓库拉取

        Returns:
            是否成功
        """
        success, output = self._run_git(["pull"], timeout=120)
        if not success:
            raise RuntimeError(f"拉取失败: {output}")

        print(f"✓ 拉取成功")
        return True


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="版本控制增强器")
    subparsers = parser.add_subparsers(dest="command", help="命令")

    # status命令
    subparsers.add_parser("status", help="查看状态")

    # commit命令
    commit_parser = subparsers.add_parser("commit", help="智能提交")
    commit_parser.add_argument("message", nargs="?", help="提交信息")

    # branch命令
    branch_parser = subparsers.add_parser("branch", help="分支管理")
    branch_subparsers = branch_parser.add_subparsers(dest="action", help="操作")
    branch_create = branch_subparsers.add_parser("create", help="创建分支")
    branch_create.add_argument("name", help="分支名称")
    branch_create.add_argument("--no-checkout", action="store_false", dest="checkout", default=True)
    branch_switch = branch_subparsers.add_parser("switch", help="切换分支")
    branch_switch.add_argument("name", help="分支名称")
    branch_subparsers.add_parser("list", help="列出分支")

    # stats命令
    stats_parser = subparsers.add_parser("stats", help="历史统计")
    stats_parser.add_argument("--count", type=int, default=10, help="提交数量")

    # diff命令
    diff_parser = subparsers.add_parser("diff", help="查看差异")
    diff_parser.add_argument("file", nargs="?", help="文件路径")

    # push命令
    subparsers.add_parser("push", help="推送")

    # pull命令
    subparsers.add_parser("pull", help="拉取")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    vc = VersionControl()

    try:
        if args.command == "status":
            status = vc.status()
            print(json.dumps(status, indent=2, ensure_ascii=False))

        elif args.command == "commit":
            vc.smart_commit(args.message)

        elif args.command == "branch":
            if args.action == "create":
                vc.create_branch(args.name, args.checkout)
            elif args.action == "switch":
                vc.switch_branch(args.name)
            elif args.action == "list":
                branches = vc.list_branches()
                print(json.dumps(branches, indent=2, ensure_ascii=False))

        elif args.command == "stats":
            stats = vc.analyze_history(args.count)
            print(json.dumps(stats, indent=2, ensure_ascii=False))

        elif args.command == "diff":
            diff = vc.get_diff(args.file)
            print(diff)

        elif args.command == "push":
            vc.push()

        elif args.command == "pull":
            vc.pull()

    except Exception as e:
        print(f"✗ 错误: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
