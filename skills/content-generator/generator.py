#!/usr/bin/env python3
"""
内容生成引擎
AI驱动的自动化内容生成工具
"""

import json
import yaml
import logging
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ContentType(Enum):
    """内容类型"""
    ARTICLE_BLOG = "blog"
    ARTICLE_NEWS = "news"
    ARTICLE_TUTORIAL = "tutorial"
    COPY_AD = "ad"
    COPY_EMAIL = "email"
    COPY_SOCIAL = "social"
    SCRIPT_SHORT_VIDEO = "short_video"
    SCRIPT_LONG_VIDEO = "long_video"


@dataclass
class ContentTemplate:
    """内容模板"""
    template_id: str
    name: str
    type: ContentType
    structure: List[str]
    required_sections: List[str]


@dataclass
class GeneratedContent:
    """生成的内容"""
    content_id: str
    type: ContentType
    topic: str
    title: str
    body: str
    meta: Dict[str, Any]
    created_at: datetime


class ContentGenerator:
    """内容生成器"""

    def __init__(self, config_file: str = "config/generator.yaml"):
        """
        初始化内容生成器

        Args:
            config_file: 配置文件路径
        """
        self.config = self._load_config(config_file)
        self.templates: List[ContentTemplate] = []
        self.generated_contents: List[GeneratedContent] = []
        self.db_conn = self._init_db()

    def _load_config(self, config_file: str) -> Dict:
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return {}

    def _init_db(self) -> sqlite3.Connection:
        """初始化数据库"""
        import os
        os.makedirs("data", exist_ok=True)

        conn = sqlite3.connect("data/generator.db", check_same_thread=False)
        cursor = conn.cursor()

        # 创建模板表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS templates (
                template_id TEXT PRIMARY KEY,
                name TEXT,
                type TEXT,
                structure TEXT,
                required_sections TEXT
            )
        """)

        # 创建内容表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contents (
                content_id TEXT PRIMARY KEY,
                type TEXT,
                topic TEXT,
                title TEXT,
                body TEXT,
                meta TEXT,
                created_at TEXT
            )
        """)

        conn.commit()
        return conn

    def create_template(
        self,
        name: str,
        type: str,
        structure: List[str],
        required_sections: List[str] = None
    ) -> ContentTemplate:
        """
        创建模板

        Args:
            name: 模板名称
            type: 内容类型
            structure: 结构
            required_sections: 必需章节

        Returns:
            模板
        """
        import uuid

        template_id = f"template_{uuid.uuid4().hex[:8]}"

        template = ContentTemplate(
            template_id=template_id,
            name=name,
            type=ContentType(type),
            structure=structure,
            required_sections=required_sections or []
        )

        self.templates.append(template)
        self._save_template(template)

        logger.info(f"创建模板: {name} ({template_id})")
        return template

    def _save_template(self, template: ContentTemplate):
        """保存模板到数据库"""
        cursor = self.db_conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO templates
            (template_id, name, type, structure, required_sections)
            VALUES (?, ?, ?, ?, ?)
        """, (
            template.template_id,
            template.name,
            template.type.value,
            json.dumps(template.structure),
            json.dumps(template.required_sections)
        ))

        self.db_conn.commit()

    def generate_article(
        self,
        topic: str,
        type: str = "blog",
        length: int = 1000,
        keywords: List[str] = None
    ) -> GeneratedContent:
        """
        生成文章

        Args:
            topic: 主题
            type: 文章类型
            length: 长度（字数）
            keywords: 关键词

        Returns:
            生成的内容
        """
        import uuid

        content_id = f"content_{uuid.uuid4().hex[:8]}"

        # 模拟AI生成文章
        title = self._generate_title(topic, type)
        body = self._generate_article_body(topic, type, length, keywords or [])

        content = GeneratedContent(
            content_id=content_id,
            type=ContentType.ARTICLE_BLOG if type == "blog" else ContentType.ARTICLE_NEWS if type == "news" else ContentType.ARTICLE_TUTORIAL,
            topic=topic,
            title=title,
            body=body,
            meta={
                "word_count": len(body),
                "keywords": keywords or [],
                "type": type
            },
            created_at=datetime.now()
        )

        self.generated_contents.append(content)
        self._save_content(content)

        logger.info(f"生成文章: {title} ({len(body)}字)")
        return content

    def _generate_title(self, topic: str, type: str) -> str:
        """生成标题"""
        templates = [
            f"{topic}：全面解析",
            f"深度解读{topic}",
            f"{topic}：从入门到精通",
            f"关于{topic}，你需要知道的5件事",
            f"{topic}：为什么它如此重要？"
        ]

        return random.choice(templates)

    def _generate_article_body(
        self,
        topic: str,
        type: str,
        length: int,
        keywords: List[str]
    ) -> str:
        """生成文章正文"""
        # 简化的文章生成
        intro = f"# {topic}\n\n"
        intro += f"{topic}是当前最热门的话题之一。在这篇文章中，我们将深入探讨{topic}的各个方面，帮助您更好地理解这一重要主题。\n\n"

        body_intro = "## 背景\n\n"
        body_intro += f"在过去的几年里，{topic}经历了快速发展。越来越多的人开始关注这一领域，因为它对我们生活和工作产生了深远影响。\n\n"

        main_body = "## 主体\n\n"
        main_body += f"{topic}的核心在于其创新性和实用性。它不仅改变了传统的工作方式，还为我们带来了全新的可能性和机遇。\n\n"

        # 插入关键词
        if keywords:
            main_body += f"特别是关于{keywords[0]}和{keywords[1] if len(keywords) > 1 else ''}的讨论，已经成为当前研究的重点。\n\n"

        conclusion = "## 结论\n\n"
        conclusion += f"总而言之，{topic}是一个充满潜力的领域。随着技术的不断进步，我们相信{topic}将在未来发挥更加重要的作用。\n\n"
        conclusion += "如果您对{topic}有任何疑问或想法，欢迎在评论区留言交流！"

        content = intro + body_intro + main_body + conclusion

        # 调整长度
        current_length = len(content)
        if current_length < length:
            # 扩充内容
            content += "\n\n## 补充\n\n" + "这里可以添加更多关于" + topic + "的详细内容。" * ((length - current_length) // 20)
        elif current_length > length:
            # 精简内容
            content = content[:length]

        return content

    def generate_ad(
        self,
        product: str,
        platform: str = "facebook",
        tone: str = "专业",
        audience: str = "一般"
    ) -> GeneratedContent:
        """
        生成广告文案

        Args:
            product: 产品
            platform: 平台
            tone: 语调
            audience: 目标受众

        Returns:
            生成的内容
        """
        import uuid

        content_id = f"content_{uuid.uuid4().hex[:8]}"

        # 生成标题
        if tone == "专业":
            title = f"{product} - 专业品质，值得信赖"
        elif tone == "轻松":
            title = f"发现{product}的无限可能！"
        else:
            title = f"{product}，您的不二之选"

        # 生成正文
        body = f"## {title}\n\n"
        body += f"✨ **{product}** ✨\n\n"
        body += f"专为{audience}打造的{product}，带给您前所未有的体验！\n\n"

        if platform == "facebook":
            body += "📱 点击了解更多详情\n"
            body += "👍 点赞 · 💬 评论 · 📤 分享\n"
        elif platform == "instagram":
            body += "📷 用{product}记录美好时刻\n"
            body += "#{product} #生活 #品质\n"
        elif platform == "linkedin":
            body += "💼 专业之选，品质保证\n"
            body += "🔗 点击了解商务合作\n"

        content = GeneratedContent(
            content_id=content_id,
            type=ContentType.COPY_AD,
            topic=product,
            title=title,
            body=body,
            meta={
                "platform": platform,
                "tone": tone,
                "audience": audience,
                "type": "ad"
            },
            created_at=datetime.now()
        )

        self.generated_contents.append(content)
        self._save_content(content)

        logger.info(f"生成广告: {title}")
        return content

    def generate_script(
        self,
        type: str = "short_video",
        duration: int = 60,
        topic: str = "产品介绍",
        style: str = "专业"
    ) -> GeneratedContent:
        """
        生成视频脚本

        Args:
            type: 视频类型
            duration: 时长（秒）
            topic: 主题
            style: 风格

        Returns:
            生成的内容
        """
        import uuid

        content_id = f"content_{uuid.uuid4().hex[:8]}"

        # 估算字数（每秒约3个字）
        word_count = duration * 3

        # 生成标题
        title = f"{topic} - {duration}秒视频脚本"

        # 生成脚本
        body = f"## {title}\n\n"
        body += f"**时长**: {duration}秒\n"
        body += f"**风格**: {style}\n\n"
        body += "---\n\n"

        # 开场（5秒）
        body += "**[0-5秒] 开场**\n"
        body += "（音乐起，画面展示产品）\n"
        body += f"旁白：今天给大家介绍{topic}...\n\n"

        # 主体
        if style == "专业":
            body += "**[5-45秒] 主体**\n"
            body += f"（展示产品核心功能和优势）\n"
            body += f"旁白：{topic}采用了先进的技术，为您提供最优质的体验。它具有以下特点：\n"
            body += "1. 高效便捷\n"
            body += "2. 安全可靠\n"
            body += "3. 物超所值\n\n"
        else:
            body += "**[5-45秒] 主体**\n"
            body += f"（轻松幽默地展示产品）\n"
            body += f"旁白：你还在为{topic}发愁吗？看看这个！简直是神器啊！\n\n"

        # 结尾
        body += "**[45-60秒] 结尾**\n"
        body += "（展示购买链接和优惠信息）\n"
        body += "旁白：赶快点击下方链接购买吧！限时优惠，不容错过！\n"

        content = GeneratedContent(
            content_id=content_id,
            type=ContentType.SCRIPT_SHORT_VIDEO if type == "short_video" else ContentType.SCRIPT_LONG_VIDEO if type == "long_video" else ContentType.SCRIPT_SHORT_VIDEO,
            topic=topic,
            title=title,
            body=body,
            meta={
                "duration": duration,
                "style": style,
                "type": "script",
                "word_count": word_count
            },
            created_at=datetime.now()
        )

        self.generated_contents.append(content)
        self._save_content(content)

        logger.info(f"生成脚本: {title}")
        return content

    def use_template(
        self,
        template_id: str,
        variables: Dict[str, str]
    ) -> GeneratedContent:
        """
        使用模板生成内容

        Args:
            template_id: 模板ID
            variables: 变量

        Returns:
            生成的内容
        """
        import uuid

        template = self._get_template(template_id)
        if not template:
            logger.error(f"未找到模板: {template_id}")
            return None

        content_id = f"content_{uuid.uuid4().hex[:8]}"

        # 生成内容
        body = ""
        for section in template.structure:
            section_content = variables.get(section, f"[{section}]")
            body += f"## {section}\n\n{section_content}\n\n"

        title = variables.get("title", f"基于{template.name}")

        content = GeneratedContent(
            content_id=content_id,
            type=template.type,
            topic="template_generation",
            title=title,
            body=body,
            meta={
                "template_id": template_id,
                "variables": variables
            },
            created_at=datetime.now()
        )

        self.generated_contents.append(content)
        self._save_content(content)

        logger.info(f"使用模板生成: {title}")
        return content

    def _get_template(self, template_id: str) -> Optional[ContentTemplate]:
        """获取模板"""
        for template in self.templates:
            if template.template_id == template_id:
                return template
        return None

    def _save_content(self, content: GeneratedContent):
        """保存内容到数据库"""
        cursor = self.db_conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO contents
            (content_id, type, topic, title, body, meta, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            content.content_id,
            content.type.value,
            content.topic,
            content.title,
            content.body,
            json.dumps(content.meta),
            content.created_at.isoformat()
        ))

        self.db_conn.commit()

    def get_content(self, content_id: str) -> Optional[Dict]:
        """
        获取内容

        Args:
            content_id: 内容ID

        Returns:
            内容信息
        """
        for content in self.generated_contents:
            if content.content_id == content_id:
                return asdict(content)
        return None

    def list_contents(self, type: Optional[str] = None) -> List[Dict]:
        """
        列出内容

        Args:
            type: 内容类型

        Returns:
            内容列表
        """
        contents = self.generated_contents
        if type:
            contents = [c for c in contents if c.type.value == type]

        return [asdict(content) for content in contents]

    def export_content(self, content_id: str, format: str = "markdown") -> str:
        """
        导出内容

        Args:
            content_id: 内容ID
            format: 格式

        Returns:
            导出的内容
        """
        content_dict = self.get_content(content_id)
        if not content_dict:
            return None

        if format == "markdown":
            return content_dict["body"]
        elif format == "html":
            # 简化的Markdown到HTML转换
            html = content_dict["body"]
            html = html.replace("## ", "<h2>").replace("\n\n", "</h2>")
            html = html.replace("**", "<strong>")
            html = html.replace("* ", "</strong>")
            return html
        elif format == "plain":
            # 移除Markdown标记
            plain = content_dict["body"]
            plain = plain.replace("#", "").replace("**", "").replace("*", "")
            return plain
        else:
            return content_dict["body"]


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="内容生成引擎")
    parser.add_argument("command", choices=["generate_article", "generate_ad", "generate_script", "create_template", "use_template", "list", "export"],
                        help="命令")
    parser.add_argument("--topic", help="主题")
    parser.add_argument("--type", help="类型")
    parser.add_argument("--length", type=int, help="长度")
    parser.add_argument("--keywords", nargs="+", help="关键词")
    parser.add_argument("--product", help="产品")
    parser.add_argument("--platform", help="平台")
    parser.add_argument("--tone", help="语调")
    parser.add_argument("--audience", help="受众")
    parser.add_argument("--duration", type=int, help="时长")
    parser.add_argument("--style", help="风格")
    parser.add_argument("--name", help="名称")
    parser.add_argument("--template_id", help="模板ID")
    parser.add_argument("--content_id", help="内容ID")
    parser.add_argument("--format", help="格式")
    parser.add_argument("--output", help="输出文件")

    args = parser.parse_args()

    # 创建内容生成器
    generator = ContentGenerator()

    if args.command == "generate_article":
        content = generator.generate_article(
            topic=args.topic,
            type=args.type or "blog",
            length=args.length or 1000,
            keywords=args.keywords or []
        )
        print(content.body)

    elif args.command == "generate_ad":
        content = generator.generate_ad(
            product=args.product,
            platform=args.platform or "facebook",
            tone=args.tone or "专业",
            audience=args.audience or "一般"
        )
        print(content.body)

    elif args.command == "generate_script":
        content = generator.generate_script(
            type=args.type or "short_video",
            duration=args.duration or 60,
            topic=args.topic or "产品介绍",
            style=args.style or "专业"
        )
        print(content.body)

    elif args.command == "create_template":
        template = generator.create_template(
            name=args.name,
            type=args.type,
            structure=["标题", "摘要", "正文", "结论"],
            required_sections=["标题", "正文"]
        )
        print(f"模板创建成功: {template.template_id}")

    elif args.command == "use_template":
        # 简化处理，假设variables是JSON
        import json
        variables = {"title": args.topic or "示例标题"}
        content = generator.use_template(
            template_id=args.template_id,
            variables=variables
        )
        if content:
            print(content.body)

    elif args.command == "list":
        contents = generator.list_contents(type=args.type)
        print(f"共有 {len(contents)} 个内容:")
        for content in contents:
            print(f"  - {content['content_id']}: {content['title']}")

    elif args.command == "export":
        exported = generator.export_content(
            content_id=args.content_id,
            format=args.format or "markdown"
        )
        if exported:
            print(exported)


if __name__ == "__main__":
    main()
