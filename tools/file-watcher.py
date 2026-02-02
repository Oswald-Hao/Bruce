#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件监听和自动推送工具
监听文件的变化，自动提交并推送到GitHub
使用AI分析更改内容，生成智能的commit信息
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path

# Moltbot配置
MOLTBOT_DIR = "/home/lejurobot/moltbot"

class GitAutoPusher:
    def __init__(self, watch_path="/home/lejurobot/clawd/skills"):
        self.watch_path = Path(watch_path)
        self.last_push = 0
        self.push_cooldown = 60  # 推送冷却时间（秒）

    def get_changes_summary(self):
        """获取更改的文件列表和类型"""
        try:
            # 获取git状态
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd="/home/lejurobot/clawd"
            )

            if not result.stdout.strip():
                return None

            # 解析git状态
            added = []
            modified = []
            deleted = []

            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                status, file = line[:2], line[3:]
                if 'A' in status:
                    added.append(file)
                elif 'M' in status or 'R' in status:
                    modified.append(file)
                elif 'D' in status:
                    deleted.append(file)

            return {
                'added': added,
                'modified': modified,
                'deleted': deleted
            }
        except Exception as e:
            print(f"检查Git状态失败：{e}")
            return None

    def get_diff_content(self, files):
        """获取文件的具体更改内容"""
        try:
            # 获取git diff
            result = subprocess.run(
                ["git", "diff", "HEAD~1", "--"] + files,
                capture_output=True,
                text=True,
                cwd="/home/lejurobot/clawd"
            )
            return result.stdout
        except Exception as e:
            print(f"获取Git diff失败：{e}")
            return ""

    def analyze_changes(self, changes):
        """分析文件更改，返回摘要"""
        summary = {
            'skills': [],
            'docs': [],
            'configs': [],
            'tools': [],
            'services': [],
            'memory': [],
            'evolution': []
        }

        # 分类所有更改的文件
        all_files = changes.get('added', []) + changes.get('modified', [])
        for file in all_files:
            if 'skills/' in file or 'kills/' in file:
                # 提取技能名称
                skill_name = file.split('/')[-2] if '/' in file else file
                summary['skills'].append(skill_name)
            elif any(doc in file for doc in ['README', 'DEPLOYMENT', 'COMPLETE', 'INTEGRATION']):
                summary['docs'].append(file.split('/')[-1])
            elif 'MEMORY.md' in file:
                summary['memory'].append('长期记忆')
            elif 'evolution-log.md' in file or 'evolution-tasks.md' in file:
                summary['evolution'].append('进化系统')
            elif 'tools/' in file:
                summary['tools'].append(file.split('/')[-1])
            elif 'services/' in file:
                summary['services'].append(file.split('/')[-2] if '/' in file else file)
            elif file.endswith('.md'):
                summary['configs'].append(file.split('/')[-1])
            elif file.endswith('.py'):
                summary['tools'].append(file.split('/')[-1])

        return summary

    def generate_ai_commit_message(self, changes, summary):
        """生成智能的commit信息（基于规则分析）"""
        parts = []

        # 优先级1：技能更新
        if summary['skills']:
            skill_names = list(set(summary['skills']))  # 去重
            if len(skill_names) == 1:
                parts.append(f"完成{skill_names[0]}技能")
            elif len(skill_names) <= 3:
                parts.append(f"完成{len(skill_names)}个技能")
            else:
                parts.append(f"完成多个技能")

        # 优先级2：进化系统
        if summary['evolution']:
            parts.append("更新进化系统")

        # 优先级3：工具脚本
        if summary['tools'] and not summary['skills']:
            tool_names = list(set(summary['tools'][:3]))
            if len(tool_names) == 1:
                parts.append(f"更新{tool_names[0]}")
            elif len(tool_names) <= 3:
                parts.append(f"更新{len(tool_names)}个工具")
            else:
                parts.append(f"更新多个工具")

        # 优先级4：文档更新
        if summary['docs']:
            doc_names = list(set(summary['docs'][:3]))
            if len(doc_names) == 1:
                parts.append(f"更新{doc_names[0]}文档")
            else:
                parts.append("更新多个文档")

        # 优先级5：记忆更新
        if summary['memory']:
            parts.append("更新记忆系统")

        # 优先级6：配置文件
        if summary['configs']:
            parts.append("更新配置文件")

        # 优先级7：服务配置
        if summary['services']:
            parts.append("更新服务配置")

        # 优先级8：删除文件
        if changes.get('deleted'):
            deleted_count = len(changes['deleted'])
            if deleted_count == 1:
                parts.append(f"删除{changes['deleted'][0].split('/')[-1]}")
            else:
                parts.append(f"清理{deleted_count}个文件")

        # 优先级9：新增文件
        if changes.get('added'):
            added_count = len(changes['added'])
            if added_count <= 3 and not parts:  # 如果前面没有生成内容
                parts.append(f"新增{added_count}个文件")

        # 如果没有识别出有意义的更改
        if not parts:
            return "自动更新：文件变化"

        # 组合最终的commit信息
        return "自动更新：" + "，".join(parts)

    def try_moltbot_ai_commit(self, changes, summary):
        """尝试使用Moltbot AI生成commit信息"""
        try:
            # 检查Moltbot是否安装
            if not Path(f"{MOLTBOT_DIR}/moltbot.mjs").exists():
                return None

            # 准备prompt
            prompt = f"""分析以下Git更改，生成一个简洁的commit信息（10-20个字）。

更改的文件：
新增：{', '.join(changes.get('added', []))}
修改：{', '.join(changes.get('modified', []))}
删除：{', '.join(changes.get('deleted', []))}

识别的更改类型：
技能：{', '.join(summary.get('skills', []))}
文档：{', '.join(summary.get('docs', []))}
工具：{', '.join(summary.get('tools', []))}
进化：{', '.join(summary.get('evolution', []))}
记忆：{', '.join(summary.get('memory', []))}
服务：{', '.join(summary.get('services', []))}
配置：{', '.join(summary.get('configs', []))}

要求：
1. 只返回commit信息，不要其他内容
2. 信息要简洁，10-20个字
3. 优先描述最重要的更改（技能 > 进化 > 工具 > 文档）
4. 例如："完成SerpAPI技能"、"更新进化系统"、"新增3个技能"
5. 如果无法确定，使用"自动更新：文件变化"
"""

            # 调用Moltbot（通过消息发送）
            # 注意：这里需要Moltbot支持，目前先返回None
            # 可以考虑通过webhook或者消息系统调用Moltbot

            return None

        except Exception as e:
            print(f"Moltbot AI调用失败：{e}")
            return None

    def generate_commit_message(self, changes):
        """生成智能的commit信息"""
        # 基于规则分析
        summary = self.analyze_changes(changes)

        # 尝试使用Moltbot AI
        ai_message = self.try_moltbot_ai_commit(changes, summary)
        if ai_message:
            return ai_message

        # 回退到规则分析
        return self.generate_ai_commit_message(changes, summary)

    def git_add_and_commit(self, message="自动更新：文件变化"):
        """添加更改并提交"""
        try:
            # 添加所有更改
            subprocess.run(
                ["git", "add", "."],
                cwd="/home/lejurobot/clawd",
                check=True
            )

            # 提交
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd="/home/lejurobot/clawd",
                check=True
            )

            print(f"✅ 已提交：{message}")
            return True
        except subprocess.CalledProcessError as e:
            # 可能没有需要提交的更改
            print(f"⚠️  没有需要提交的更改")
            return False
        except Exception as e:
            print(f"❌ 提交失败：{e}")
            return False

    def start_watching(self, interval=30):
        """开始监听文件变化"""
        print(f"👀 开始监听文件变化：{self.watch_path}")
        print(f"🔄 检查间隔：{interval}秒")
        print(f"🤖 AI分析：已启用（基于规则+Moltbot）")
        print("按Ctrl+C停止监听\n")

        try:
            while True:
                # 检查是否有更改
                changes = self.get_changes_summary()
                if changes:
                    current_time = time.time()

                    # 检查冷却时间
                    if current_time - self.last_push >= self.push_cooldown:
                        # 生成智能commit信息
                        message = self.generate_commit_message(changes)

                        # 提交更改（会自动触发Git钩子推送）
                        if self.git_add_and_commit(message):
                            self.last_push = current_time
                    else:
                        remaining = int(self.push_cooldown - (current_time - self.last_push))
                        print(f"⏳ 冷却中，{remaining}秒后可推送...")

                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n👋 停止监听")

if __name__ == "__main__":
    import sys

    # 支持命令行参数指定监听路径
    watch_path = sys.argv[1] if len(sys.argv) > 1 else "/home/lejurobot/clawd"

    pusher = GitAutoPusher(watch_path)

    # 默认检查间隔30秒
    interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30

    pusher.start_watching(interval)
