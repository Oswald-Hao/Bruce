#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书卡片生成器 - Feishu Card Generator

支持多种飞书卡片模板，增强交互体验
"""

import json
from typing import List, Dict, Optional


class FeishuCardGenerator:
    """飞书卡片生成器类"""

    def __init__(self):
        """初始化卡片生成器"""
        self.card_config = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {},
            "elements": []
        }

    def create_message_card(
        self,
        title: str,
        content: List[str],
        template: str = "turquoise",
        markdown: bool = True
    ) -> Dict:
        """
        创建消息卡片

        Args:
            title: 卡片标题
            content: 内容列表（多段文本）
            template: 模板颜色（turquoise, blue, wathet, lark, indigo, purple, pink, red, orange, yellow, green, grey）
            markdown: 是否使用Markdown格式

        Returns:
            卡片字典
        """
        card = self.card_config.copy()

        # 设置标题
        card["header"] = {
            "title": {
                "tag": "plain_text",
                "content": title
            },
            "template": template
        }

        # 设置内容
        elements = []

        # 内容元素
        if markdown:
            for line in content:
                elements.append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": line
                    }
                })
        else:
            for line in content:
                elements.append({
                    "tag": "div",
                    "text": {
                        "tag": "plain_text",
                        "content": line
                    }
                })

        card["elements"] = elements

        return card

    def create_button_card(
        self,
        title: str,
        content: str,
        buttons: List[Dict[str, str]],
        template: str = "blue",
        markdown: bool = True
    ) -> Dict:
        """
        创建按钮卡片

        Args:
            title: 卡片标题
            content: 卡片内容
            buttons: 按钮列表，每个按钮包含 "text" 和 "url"/"action"
            template: 模板颜色
            markdown: 是否使用Markdown格式

        Returns:
            卡片字典
        """
        card = self.card_config.copy()

        # 设置标题
        card["header"] = {
            "title": {
                "tag": "plain_text",
                "content": title
            },
            "template": template
        }

        # 设置内容
        elements = []

        # 内容元素
        if markdown:
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": content
                }
            })
        else:
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "plain_text",
                    "content": content
                }
            })

        # 按钮元素
        button_elements = []

        # 将按钮分组（每行最多2个按钮）
        for i in range(0, len(buttons), 2):
            button_row = {
                "tag": "action",
                "actions": []
            }

            # 添加按钮
            for btn in buttons[i:i+2]:
                if "url" in btn:
                    button_row["actions"].append({
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": btn["text"]
                        },
                        "url": btn["url"],
                        "type": "primary" if i == 0 else "default"
                    })
                elif "action" in btn:
                    button_row["actions"].append({
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": btn["text"]
                        },
                        "type": "default"
                    })

            if button_row["actions"]:
                button_elements.append(button_row)

        elements.extend(button_elements)
        card["elements"] = elements

        return card

    def create_list_card(
        self,
        title: str,
        items: List[str],
        template: str = "wathet",
        ordered: bool = False,
        markdown: bool = True
    ) -> Dict:
        """
        创建列表卡片

        Args:
            title: 卡片标题
            items: 列表项
            template: 模板颜色
            ordered: 是否为有序列表
            markdown: 是否使用Markdown格式

        Returns:
            卡片字典
        """
        card = self.card_config.copy()

        # 设置标题
        card["header"] = {
            "title": {
                "tag": "plain_text",
                "content": title
            },
            "template": template
        }

        # 构建列表内容
        if markdown:
            if ordered:
                content = "\n".join([f"{i+1}. {item}" for i, item in enumerate(items)])
            else:
                content = "\n".join([f"• {item}" for item in items])
        else:
            if ordered:
                content = "\n".join([f"{i+1}. {item}" for i, item in enumerate(items)])
            else:
                content = "\n".join([f"- {item}" for item in items])

        # 设置内容
        elements = [{
            "tag": "div",
            "text": {
                "tag": "lark_md" if markdown else "plain_text",
                "content": content
            }
        }]

        card["elements"] = elements

        return card

    def create_image_card(
        self,
        title: str,
        image_key: str,
        content: Optional[str] = None,
        template: str = "lark"
    ) -> Dict:
        """
        创建图片卡片

        Args:
            title: 卡片标题
            image_key: 图片的image_key
            content: 可选的图片说明
            template: 模板颜色

        Returns:
            卡片字典
        """
        card = self.card_config.copy()

        # 设置标题
        card["header"] = {
            "title": {
                "tag": "plain_text",
                "content": title
            },
            "template": template
        }

        # 图片元素
        elements = [{
            "tag": "img",
            "img_key": image_key,
            "alt": {
                "tag": "plain_text",
                "content": title
            }
        }]

        # 可选的图片说明
        if content:
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "plain_text",
                    "content": content
                }
            })

        card["elements"] = elements

        return card

    def create_thinking_card(self, message: str = "正在处理您的请求...") -> Dict:
        """
        创建"正在思考"卡片

        Args:
            message: 思考提示消息

        Returns:
            卡片字典
        """
        return self.create_message_card(
            title="🤔 正在思考中...",
            content=[message],
            template="turquoise",
            markdown=True
        )

    def create_progress_card(
        self,
        title: str,
        progress: int,
        total: int,
        status: str = "处理中..."
    ) -> Dict:
        """
        创建进度卡片

        Args:
            title: 进度标题
            progress: 当前进度
            total: 总数
            status: 状态描述

        Returns:
            卡片字典
        """
        percentage = int((progress / total) * 100) if total > 0 else 0

        content = [
            f"**进度：** {progress}/{total} ({percentage}%)",
            f"**状态：** {status}",
            "",
            f"{'█' * (percentage // 5)}{'░' * (20 - percentage // 5)} {percentage}%"
        ]

        return self.create_message_card(
            title=title,
            content=content,
            template="blue",
            markdown=True
        )

    def create_result_card(
        self,
        title: str,
        result: str,
        success: bool = True,
        show_details: bool = True
    ) -> Dict:
        """
        创建结果卡片

        Args:
            title: 结果标题
            result: 结果内容
            success: 是否成功
            show_details: 是否显示详细信息

        Returns:
            卡片字典
        """
        template = "green" if success else "red"
        emoji = "✅" if success else "❌"

        content = [
            f"{emoji} {result}"
        ]

        if show_details:
            content.append("")
            content.append(f"**状态：** {'成功' if success else '失败'}")
            content.append(f"**时间：** {self._get_current_time()}")

        return self.create_message_card(
            title=title,
            content=content,
            template=template,
            markdown=True
        )

    def create_report_card(
        self,
        title: str,
        sections: List[Dict[str, str]],
        template: str = "indigo"
    ) -> Dict:
        """
        创建报告卡片

        Args:
            title: 报告标题
            sections: 报告章节列表，每个章节包含 "title" 和 "content"
            template: 模板颜色

        Returns:
            卡片字典
        """
        card = self.card_config.copy()

        # 设置标题
        card["header"] = {
            "title": {
                "tag": "plain_text",
                "content": title
            },
            "template": template
        }

        # 构建报告内容
        elements = []

        # 添加分割线
        elements.append({
            "tag": "hr"
        })

        # 添加每个章节
        for section in sections:
            section_title = section.get("title", "")
            section_content = section.get("content", "")

            # 章节标题
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**{section_title}**"
                }
            })

            # 章节内容
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": section_content
                }
            })

            # 添加分割线
            elements.append({
                "tag": "hr"
            })

        card["elements"] = elements

        return card

    def _get_current_time(self) -> str:
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_json(self, card: Dict, indent: int = 2) -> str:
        """
        将卡片转换为JSON字符串

        Args:
            card: 卡片字典
            indent: 缩进空格数

        Returns:
            JSON字符串
        """
        return json.dumps({"card": card}, ensure_ascii=False, indent=indent)


def main():
    """测试飞书卡片生成器"""
    gen = FeishuCardGenerator()

    print("=== 飞书卡片生成器测试 ===\n")

    # 测试1：基础消息卡片
    print("1. 基础消息卡片")
    card1 = gen.create_message_card(
        title="通知",
        content=["这是一条消息", "这是第二条消息"]
    )
    print(gen.to_json(card1))
    print()

    # 测试2：按钮卡片
    print("2. 按钮卡片")
    card2 = gen.create_button_card(
        title="操作确认",
        content="请选择操作",
        buttons=[
            {"text": "确认", "url": "https://example.com/confirm"},
            {"text": "取消", "action": "cancel"}
        ]
    )
    print(gen.to_json(card2))
    print()

    # 测试3：列表卡片
    print("3. 列表卡片")
    card3 = gen.create_list_card(
        title="待办事项",
        items=["任务1", "任务2", "任务3"],
        ordered=True
    )
    print(gen.to_json(card3))
    print()

    # 测试4：正在思考卡片
    print("4. 正在思考卡片")
    card4 = gen.create_thinking_card("正在处理您的请求...")
    print(gen.to_json(card4))
    print()

    # 测试5：进度卡片
    print("5. 进度卡片")
    card5 = gen.create_progress_card("任务进度", 7, 10, "处理中...")
    print(gen.to_json(card5))
    print()

    # 测试6：结果卡片
    print("6. 结果卡片")
    card6 = gen.create_result_card("任务完成", "所有任务已成功完成", success=True)
    print(gen.to_json(card6))
    print()

    # 测试7：报告卡片
    print("7. 报告卡片")
    card7 = gen.create_report_card(
        title="每日报告",
        sections=[
            {"title": "任务", "content": "已完成5个任务"},
            {"title": "进度", "content": "50%"},
            {"title": "状态", "content": "正常"}
        ]
    )
    print(gen.to_json(card7))


if __name__ == "__main__":
    main()
