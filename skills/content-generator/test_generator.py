#!/usr/bin/env python3
"""
内容生成引擎测试用例
"""

import unittest
import os
import tempfile
import shutil

from generator import (
    ContentGenerator,
    ContentTemplate,
    GeneratedContent,
    ContentType
)


class TestContentGenerator(unittest.TestCase):
    """测试内容生成器"""

    def setUp(self):
        """设置测试环境"""
        self.test_dir = tempfile.mkdtemp()
        self.generator = ContentGenerator(config_file="config/generator.yaml")

    def tearDown(self):
        """清理测试环境"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        if os.path.exists("data"):
            shutil.rmtree("data")

    def test_init(self):
        """测试初始化"""
        self.assertIsInstance(self.generator.templates, list)
        self.assertIsInstance(self.generator.generated_contents, list)

    def test_create_template(self):
        """测试创建模板"""
        template = self.generator.create_template(
            name="测试模板",
            type="blog",
            structure=["标题", "摘要", "正文", "结论"],
            required_sections=["标题", "正文"]
        )

        self.assertIsInstance(template, ContentTemplate)
        self.assertEqual(template.name, "测试模板")
        self.assertEqual(template.type, ContentType.ARTICLE_BLOG)
        self.assertEqual(len(template.structure), 4)

    def test_generate_article(self):
        """测试生成文章"""
        content = self.generator.generate_article(
            topic="人工智能",
            type="blog",
            length=1000,
            keywords=["AI", "机器学习"]
        )

        self.assertIsInstance(content, GeneratedContent)
        self.assertEqual(content.topic, "人工智能")
        self.assertEqual(content.type, ContentType.ARTICLE_BLOG)
        self.assertIsNotNone(content.title)
        self.assertGreater(len(content.body), 0)
        self.assertIn("人工智能", content.body)

    def test_generate_ad(self):
        """测试生成广告文案"""
        content = self.generator.generate_ad(
            product="智能手表",
            platform="facebook",
            tone="专业",
            audience="年轻白领"
        )

        self.assertIsInstance(content, GeneratedContent)
        self.assertEqual(content.topic, "智能手表")
        self.assertEqual(content.type, ContentType.COPY_AD)
        self.assertIsNotNone(content.title)
        self.assertIn("智能手表", content.body)

    def test_generate_script(self):
        """测试生成视频脚本"""
        content = self.generator.generate_script(
            type="short_video",
            duration=60,
            topic="产品介绍",
            style="专业"
        )

        self.assertIsInstance(content, GeneratedContent)
        self.assertEqual(content.topic, "产品介绍")
        self.assertEqual(content.type, ContentType.SCRIPT_SHORT_VIDEO)
        self.assertIn("开场", content.body)
        self.assertIn("结尾", content.body)

    def test_use_template(self):
        """测试使用模板"""
        # 先创建模板
        template = self.generator.create_template(
            name="测试模板",
            type="blog",
            structure=["标题", "摘要", "正文", "结论"],
            required_sections=["标题", "正文"]
        )

        # 使用模板
        content = self.generator.use_template(
            template_id=template.template_id,
            variables={
                "title": "示例标题",
                "摘要": "这是摘要",
                "正文": "这是正文内容",
                "结论": "这是结论"
            }
        )

        self.assertIsInstance(content, GeneratedContent)
        self.assertEqual(content.title, "示例标题")
        self.assertIn("摘要", content.body)
        self.assertIn("正文", content.body)

    def test_get_content(self):
        """测试获取内容"""
        content = self.generator.generate_article(
            topic="测试主题",
            type="blog",
            length=500
        )

        retrieved = self.generator.get_content(content.content_id)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["content_id"], content.content_id)
        self.assertEqual(retrieved["title"], content.title)

    def test_list_contents(self):
        """测试列出内容"""
        # 生成多个内容
        self.generator.generate_article(topic="主题1", type="blog", length=500)
        self.generator.generate_article(topic="主题2", type="blog", length=500)
        self.generator.generate_ad(product="产品1", platform="facebook")

        # 列出所有内容
        all_contents = self.generator.list_contents()
        self.assertEqual(len(all_contents), 3)

        # 列出文章
        articles = self.generator.list_contents(type="blog")
        self.assertEqual(len(articles), 2)

    def test_export_content_markdown(self):
        """测试导出为Markdown"""
        content = self.generator.generate_article(
            topic="测试",
            type="blog",
            length=500
        )

        exported = self.generator.export_content(
            content_id=content.content_id,
            format="markdown"
        )

        self.assertIsNotNone(exported)
        self.assertIn("#", exported)  # Markdown标题标记

    def test_export_content_html(self):
        """测试导出为HTML"""
        content = self.generator.generate_article(
            topic="测试",
            type="blog",
            length=500
        )

        exported = self.generator.export_content(
            content_id=content.content_id,
            format="html"
        )

        self.assertIsNotNone(exported)
        self.assertIn("<h2>", exported)  # HTML标题标记

    def test_export_content_plain(self):
        """测试导出为纯文本"""
        content = self.generator.generate_article(
            topic="测试",
            type="blog",
            length=500
        )

        exported = self.generator.export_content(
            content_id=content.content_id,
            format="plain"
        )

        self.assertIsNotNone(exported)
        self.assertNotIn("#", exported)  # 不应该有Markdown标记


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestContentGenerator))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 返回测试结果
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
