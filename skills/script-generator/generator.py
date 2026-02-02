#!/usr/bin/env python3
"""
自动化脚本生成器
根据自然语言需求生成Shell/Python/Node脚本
"""

import os
import re
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# 模板目录
TEMPLATES_DIR = Path(__file__).parent / "templates"

# 危险命令检测
DANGEROUS_PATTERNS = [
    r"rm\s+-rf\s+/",
    r":\(\)\{\:\|:\&\};\:",
    r"dd\s+if=/dev/zero",
    r">\s+/dev/sd[a-z]",
    r"mkfs\.",
    r"chmod\s+777\s+/",
]

class ScriptGenerator:
    """脚本生成器核心类"""

    def __init__(self):
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, Dict]:
        """加载所有模板"""
        templates = {}
        if not TEMPLATES_DIR.exists():
            TEMPLATES_DIR.mkdir(parents=True)

        for lang_dir in TEMPLATES_DIR.iterdir():
            if lang_dir.is_dir():
                lang = lang_dir.name
                templates[lang] = {}
                for template_file in lang_dir.glob("*.md"):
                    name = template_file.stem
                    templates[lang][name] = self._parse_template(template_file)

        return templates

    def _parse_template(self, template_file: Path) -> Dict:
        """解析模板文件"""
        content = template_file.read_text(encoding='utf-8')

        # 提取元数据（YAML front matter或注释）
        metadata = {}
        template_body = content

        # 提取描述（支持多种格式）
        desc_patterns = [
            r'Description:\s*(.+?)(?=\n|$)',
            r'#\s*Description:\s*(.+?)(?=\n|$)',
            r'<\!--\s*Description:\s*(.+?)\s*-->',
            r'\*\s*Description:\s*(.+?)(?=\n|\*/)',
        ]

        for pattern in desc_patterns:
            desc_match = re.search(pattern, content, re.IGNORECASE)
            if desc_match:
                desc = desc_match.group(1).strip()
                # 移除多余的注释标记
                desc = desc.rstrip('-->').strip()
                # 移除星号
                desc = desc.lstrip('*').strip()
                metadata['description'] = desc
                break

        # 提取变量
        variables = re.findall(r'{{\s*(\w+)\s*}}', content)
        metadata['variables'] = list(set(variables))

        metadata['template'] = template_body
        return metadata

    def _analyze_prompt(self, prompt: str) -> Dict:
        """分析需求，提取任务类型和参数"""
        analysis = {
            'task_type': '',
            'parameters': {},
            'language_preference': None
        }

        # 检测语言偏好
        if 'shell' in prompt.lower() or 'bash' in prompt.lower() or 'sh脚本' in prompt:
            analysis['language_preference'] = 'shell'
        elif 'python' in prompt.lower() or 'py脚本' in prompt:
            analysis['language_preference'] = 'python'
        elif 'node' in prompt.lower() or 'js脚本' in prompt.lower():
            analysis['language_preference'] = 'node'

        # 检测任务类型
        task_patterns = {
            'backup': r'备份|backup|保存|save',
            'monitor': r'监控|monitor|检测|detect|告警|alert',
            'deploy': r'部署|deploy|发布|publish|上传|upload',
            'batch': r'批量|batch|循环|loop|批量处理',
            'schedule': r'定时|schedule|cron|计划|task',
            'api': r'API|接口|请求|request|爬虫|crawl',
            'file': r'文件|file|目录|folder|移动|copy|删除|delete',
        }

        for task_type, pattern in task_patterns.items():
            if re.search(pattern, prompt, re.IGNORECASE):
                analysis['task_type'] = task_type
                break

        # 提取路径参数（改进：只匹配纯路径部分）
        paths = re.findall(r'(/[\w\-./]+)(?=\s|$|[,，])', prompt)
        if paths:
            analysis['parameters']['paths'] = paths

        # 提取时间参数
        time_patterns = [
            r'(\d+)\s*点',
            r'(\d+):(\d+)',
            r'(\d+)\s*小时',
            r'(\d+)\s*分钟',
        ]
        for pattern in time_patterns:
            matches = re.findall(pattern, prompt)
            if matches:
                analysis['parameters']['times'] = matches
                break

        # 提取数字参数
        numbers = re.findall(r'\d+', prompt)
        if numbers:
            analysis['parameters']['numbers'] = [int(n) for n in numbers]

        return analysis

    def _safety_check(self, code: str) -> Tuple[bool, List[str]]:
        """安全检查"""
        warnings = []
        is_safe = True

        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, code):
                warnings.append(f"检测到潜在危险命令: {pattern}")
                is_safe = False

        return is_safe, warnings

    def _select_template(self, analysis: Dict, lang: str) -> Optional[str]:
        """选择合适的模板"""
        task_type = analysis['task_type']

        # 优先选择语言特定的模板
        if lang in self.templates and task_type in self.templates[lang]:
            return self.templates[lang][task_type]['template']

        # 其次选择通用的模板
        if lang in self.templates and 'generic' in self.templates[lang]:
            return self.templates[lang]['generic']['template']

        # 最后使用基础模板
        return self._get_base_template(lang)

    def _get_base_template(self, lang: str) -> str:
        """获取基础模板"""
        templates = {
            'shell': """#!/bin/bash
# 自动生成的Shell脚本
# 生成时间: {{timestamp}}

set -e  # 遇到错误立即退出

echo "开始执行脚本..."

# 在这里添加你的脚本逻辑
{{script_body}}

echo "脚本执行完成"
""",
            'python': """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 自动生成的Python脚本
# 生成时间: {{timestamp}}

import sys
import os
from datetime import datetime

def main():
    print("开始执行脚本...")

    # 在这里添加你的脚本逻辑
    {{script_body}}

    print("脚本执行完成")

if __name__ == "__main__":
    main()
""",
            'node': """#!/usr/bin/env node
/**
 * 自动生成的Node.js脚本
 * 生成时间: {{timestamp}}
 */

console.log("开始执行脚本...");

// 在这里添加你的脚本逻辑
{{script_body}}

console.log("脚本执行完成");
""",
        }
        return templates.get(lang, templates['python'])

    def _fill_template(self, template: str, analysis: Dict, prompt: str) -> str:
        """填充模板"""
        # 基础变量
        variables = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'prompt': prompt,
            'script_body': f"# 根据需求生成代码\n# 需求: {prompt}\n\n# TODO: 实现具体逻辑",
        }

        # 添加参数
        params = analysis.get('parameters', {})
        if 'paths' in params:
            paths_str = ', '.join([f'"{p}"' for p in params['paths']])
            variables['paths'] = paths_str
            # 为源目录和备份目录设置默认值
            if len(params['paths']) >= 1:
                variables['source_dir'] = params['paths'][0]
            if len(params['paths']) >= 2:
                variables['backup_dir'] = params['paths'][1]
        if 'numbers' in params:
            variables['numbers'] = ', '.join(map(str, params['numbers']))
            # 为天数等数字参数设置默认值
            if params['numbers']:
                variables['days'] = params['numbers'][0]

        # 替换变量（支持默认值语法 {{var|default}}）
        import re
        def replace_var(match):
            var_expr = match.group(1)  # var|default or var
            if '|' in var_expr:
                var_name, default_value = var_expr.split('|', 1)
                return str(variables.get(var_name.strip(), default_value.strip()))
            else:
                return str(variables.get(var_expr.strip(), match.group(0)))

        template = re.sub(r'{{\s*(.+?)\s*}}', replace_var, template)

        return template

    def generate(self, prompt: str, lang: str = 'python', verbose: bool = False) -> Tuple[str, bool, List[str]]:
        """生成脚本"""
        if verbose:
            print(f"分析需求: {prompt}")
            print(f"目标语言: {lang}")

        # 分析需求
        analysis = self._analyze_prompt(prompt)
        if verbose:
            print(f"任务类型: {analysis['task_type']}")
            print(f"参数: {analysis['parameters']}")

        # 选择模板
        template = self._select_template(analysis, lang)
        if verbose:
            print("使用模板: " + ("自定义" if template else "基础"))

        # 填充模板
        code = self._fill_template(template, analysis, prompt)

        # 安全检查
        is_safe, warnings = self._safety_check(code)

        if warnings:
            print("\n⚠️ 安全警告:")
            for warning in warnings:
                print(f"  - {warning}")
            print("\n建议人工审查生成的脚本！")

        return code, is_safe, warnings

    def list_templates(self) -> None:
        """列出所有可用模板"""
        print("\n可用模板:")
        print("=" * 50)

        for lang, templates in self.templates.items():
            print(f"\n📁 {lang.upper()}:")
            for name, info in templates.items():
                desc = info.get('description', '无描述')
                print(f"  - {name}: {desc}")
                if info.get('variables'):
                    print(f"    变量: {', '.join(info['variables'])}")

        print("\n" + "=" * 50)


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='自动化脚本生成器')
    parser.add_argument('--lang', '-l', choices=['shell', 'python', 'node'],
                        default='python', help='脚本语言')
    parser.add_argument('--prompt', '-p', help='自然语言需求描述')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--list-templates', action='store_true', help='列出所有模板')
    parser.add_argument('--verbose', '-v', action='store_true', help='显示详细过程')

    args = parser.parse_args()

    generator = ScriptGenerator()

    # 列出模板
    if args.list_templates:
        generator.list_templates()
        return

    # 检查prompt参数
    if not args.prompt:
        parser.error("--prompt/-p 是必需的参数")

    # 生成脚本
    code, is_safe, warnings = generator.generate(
        args.prompt,
        args.lang,
        args.verbose
    )

    # 输出
    if args.output:
        # 确保目录存在
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 写入文件
        output_path.write_text(code, encoding='utf-8')
        print(f"\n✅ 脚本已生成: {args.output}")

        # 设置执行权限
        if args.lang == 'shell':
            os.chmod(args.output, 0o755)

    else:
        # 输出到控制台
        print("\n" + "=" * 60)
        print("生成的脚本:")
        print("=" * 60)
        print(code)
        print("=" * 60)

    # 安全提示
    if not is_safe:
        print("\n⚠️ 脚本包含潜在危险操作，请人工审查后再执行！")
        sys.exit(1)


if __name__ == '__main__':
    main()
