#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书快捷指令管理器 - Feishu Shortcut Manager

用于管理飞书的快捷指令、命令别名、交互菜单等
"""

import json
from typing import Dict, List, Optional


class FeishuShortcutManager:
    """飞书快捷指令管理器类"""

    def __init__(self):
        """初始化快捷指令管理器"""
        self.shortcuts = {}
        self.shortcut_id_counter = 1

    def create_shortcut(
        self,
        name: str,
        description: str,
        trigger_type: str,
        trigger_config: Dict,
        actions: List[Dict],
        icon: Optional[str] = None,
        enabled: bool = True
    ) -> Dict:
        """
        创建快捷指令

        Args:
            name: 快捷指令名称
            description: 快捷指令描述
            trigger_type: 触发类型（keyword, card, schedule）
            trigger_config: 触发配置
            actions: 动作列表
            icon: 图标（可选）
            enabled: 是否启用

        Returns:
            快捷指令字典
        """
        shortcut = {
            "id": f"shortcut_{self.shortcut_id_counter}",
            "name": name,
            "description": description,
            "trigger_type": trigger_type,
            "trigger_config": trigger_config,
            "actions": actions,
            "icon": icon,
            "enabled": enabled,
            "created_at": self._get_current_time()
        }

        self.shortcuts[shortcut["id"]] = shortcut
        self.shortcut_id_counter += 1

        return shortcut

    def create_keyword_shortcut(
        self,
        name: str,
        description: str,
        keywords: List[str],
        action: str,
        params: Optional[Dict] = None
    ) -> Dict:
        """
        创建关键词快捷指令

        Args:
            name: 快捷指令名称
            description: 快捷指令描述
            keywords: 触发关键词列表
            action: 动作（消息、命令等）
            params: 参数（可选）

        Returns:
            快捷指令字典
        """
        shortcut = self.create_shortcut(
            name=name,
            description=description,
            trigger_type="keyword",
            trigger_config={
                "keywords": keywords
            },
            actions=[{
                "type": "action",
                "action": action,
                "params": params or {}
            }]
        )

        return shortcut

    def create_card_shortcut(
        self,
        name: str,
        description: str,
        card: Dict,
        button_actions: List[Dict]
    ) -> Dict:
        """
        创建卡片快捷指令（带按钮的卡片）

        Args:
            name: 快捷指令名称
            description: 快捷指令描述
            card: 卡片字典
            button_actions: 按钮动作列表

        Returns:
            快捷指令字典
        """
        shortcut = self.create_shortcut(
            name=name,
            description=description,
            trigger_type="card",
            trigger_config={
                "card": card
            },
            actions=button_actions
        )

        return shortcut

    def create_schedule_shortcut(
        self,
        name: str,
        description: str,
        schedule: str,
        action: str,
        params: Optional[Dict] = None
    ) -> Dict:
        """
        创建定时快捷指令

        Args:
            name: 快捷指令名称
            description: 快捷指令描述
            schedule: Cron表达式
            action: 动作
            params: 参数（可选）

        Returns:
            快捷指令字典
        """
        shortcut = self.create_shortcut(
            name=name,
            description=description,
            trigger_type="schedule",
            trigger_config={
                "schedule": schedule
            },
            actions=[{
                "type": "action",
                "action": action,
                "params": params or {}
            }]
        )

        return shortcut

    def get_shortcut(self, shortcut_id: str) -> Optional[Dict]:
        """
        获取快捷指令

        Args:
            shortcut_id: 快捷指令ID

        Returns:
            快捷指令字典，如果不存在返回None
        """
        return self.shortcuts.get(shortcut_id)

    def list_shortcuts(
        self,
        enabled_only: bool = False
    ) -> List[Dict]:
        """
        列出所有快捷指令

        Args:
            enabled_only: 是否只列出启用的快捷指令

        Returns:
            快捷指令列表
        """
        shortcuts = list(self.shortcuts.values())

        if enabled_only:
            shortcuts = [s for s in shortcuts if s.get('enabled', False)]

        return shortcuts

    def enable_shortcut(self, shortcut_id: str) -> bool:
        """
        启用快捷指令

        Args:
            shortcut_id: 快捷指令ID

        Returns:
            是否成功
        """
        shortcut = self.shortcuts.get(shortcut_id)
        if shortcut:
            shortcut['enabled'] = True
            return True
        return False

    def disable_shortcut(self, shortcut_id: str) -> bool:
        """
        禁用快捷指令

        Args:
            shortcut_id: 快捷指令ID

        Returns:
            是否成功
        """
        shortcut = self.shortcuts.get(shortcut_id)
        if shortcut:
            shortcut['enabled'] = False
            return True
        return False

    def delete_shortcut(self, shortcut_id: str) -> bool:
        """
        删除快捷指令

        Args:
            shortcut_id: 快捷指令ID

        Returns:
            是否成功
        """
        if shortcut_id in self.shortcuts:
            del self.shortcuts[shortcut_id]
            return True
        return False

    def update_shortcut(
        self,
        shortcut_id: str,
        updates: Dict
    ) -> bool:
        """
        更新快捷指令

        Args:
            shortcut_id: 快捷指令ID
            updates: 更新的字段

        Returns:
            是否成功
        """
        shortcut = self.shortcuts.get(shortcut_id)
        if shortcut:
            shortcut.update(updates)
            return True
        return False

    def trigger_shortcut(
        self,
        shortcut_id: str,
        trigger_data: Optional[Dict] = None
    ) -> List[Dict]:
        """
        触发快捷指令

        Args:
            shortcut_id: 快捷指令ID
            trigger_data: 触发数据

        Returns:
            动作列表
        """
        shortcut = self.get_shortcut(shortcut_id)

        if not shortcut:
            return []

        if not shortcut.get('enabled', False):
            return []

        actions = shortcut.get('actions', [])

        # 替换触发数据中的占位符
        if trigger_data:
            actions = self._replace_placeholders(actions, trigger_data)

        return actions

    def create_common_shortcuts(self) -> Dict[str, Dict]:
        """
        创建常用快捷指令

        Returns:
            快捷指令字典
        """
        shortcuts = {}

        # 快捷指令1：查询天气
        shortcuts['query_weather'] = self.create_keyword_shortcut(
            name="查询天气",
            description="查询指定城市的天气",
            keywords=["天气", "weather", "天气查询"],
            action="query_weather",
            params={
                "default_city": "深圳"
            }
        )

        # 快捷指令2：发送报告
        shortcuts['send_report'] = self.create_keyword_shortcut(
            name="发送报告",
            description="发送每日报告",
            keywords=["报告", "report", "日报"],
            action="send_daily_report"
        )

        # 快捷指令3：系统状态
        shortcuts['system_status'] = self.create_keyword_shortcut(
            name="系统状态",
            description="查询系统状态",
            keywords=["状态", "status", "系统状态"],
            action="query_system_status"
        )

        # 快捷指令4：帮助
        shortcuts['help'] = self.create_keyword_shortcut(
            name="帮助",
            description="显示帮助信息",
            keywords=["帮助", "help", "使用帮助"],
            action="show_help"
        )

        return shortcuts

    def _replace_placeholders(
        self,
        items: List[Dict],
        data: Dict
    ) -> List[Dict]:
        """
        替换占位符

        Args:
            items: 项目列表
            data: 数据字典

        Returns:
            替换后的项目列表
        """
        import re

        for item in items:
            for key, value in item.items():
                if isinstance(value, str):
                    # 替换 {placeholder} 格式
                    value = re.sub(r'\{(\w+)\}', lambda m: str(data.get(m.group(1), m.group(0))), value)
                    item[key] = value

        return items

    def _get_current_time(self) -> str:
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().isoformat()


def main():
    """测试飞书快捷指令管理器"""
    print("=== 飞书快捷指令管理器测试 ===\n")

    manager = FeishuShortcutManager()

    # 测试1：创建关键词快捷指令
    print("1. 创建关键词快捷指令")
    shortcut1 = manager.create_keyword_shortcut(
        name="查询天气",
        description="查询深圳天气",
        keywords=["天气", "weather"],
        action="query_weather",
        params={"city": "深圳"}
    )
    print(f"✅ 快捷指令已创建: {shortcut1['id']}")
    print(f"   名称: {shortcut1['name']}")
    print()

    # 测试2：创建卡片快捷指令
    print("2. 创建卡片快捷指令")
    card = {
        "header": {
            "title": "操作选择",
            "template": "blue"
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "plain_text",
                    "content": "请选择操作"
                }
            }
        ]
    }

    button_actions = [
        {
            "type": "action",
            "action": "send_message",
            "params": {"message": "操作1"}
        },
        {
            "type": "action",
            "action": "send_message",
            "params": {"message": "操作2"}
        }
    ]

    shortcut2 = manager.create_card_shortcut(
        name="操作选择",
        description="显示操作选择卡片",
        card=card,
        button_actions=button_actions
    )
    print(f"✅ 卡片快捷指令已创建: {shortcut2['id']}")
    print()

    # 测试3：创建定时快捷指令
    print("3. 创建定时快捷指令")
    shortcut3 = manager.create_schedule_shortcut(
        name="定时报告",
        description="每天早上9点发送报告",
        schedule="0 9 * * *",
        action="send_daily_report"
    )
    print(f"✅ 定时快捷指令已创建: {shortcut3['id']}")
    print()

    # 测试4：创建常用快捷指令
    print("4. 创建常用快捷指令")
    common_shortcuts = manager.create_common_shortcuts()
    print(f"✅ 常用快捷指令已创建: {len(common_shortcuts)}个")
    for sid, sc in common_shortcuts.items():
        print(f"   - {sid}: {sc['name']}")
    print()

    # 测试5：列出所有快捷指令
    print("5. 列出所有快捷指令")
    all_shortcuts = manager.list_shortcuts()
    print(f"✅ 共有 {len(all_shortcuts)}个快捷指令")
    for sc in all_shortcuts:
        status = "✅" if sc['enabled'] else "❌"
        print(f"   {status} {sc['id']}: {sc['name']}")
    print()

    # 测试6：禁用快捷指令
    print("6. 禁用快捷指令")
    if manager.disable_shortcut(shortcut1['id']):
        print(f"✅ 快捷指令已禁用: {shortcut1['id']}")
    else:
        print(f"❌ 禁用快捷指令失败: {shortcut1['id']}")
    print()

    # 测试7：启用快捷指令
    print("7. 启用快捷指令")
    if manager.enable_shortcut(shortcut1['id']):
        print(f"✅ 快捷指令已启用: {shortcut1['id']}")
    else:
        print(f"❌ 启用快捷指令失败: {shortcut1['id']}")
    print()

    # 测试8：触发快捷指令
    print("8. 触发快捷指令")
    actions = manager.trigger_shortcut(shortcut1['id'])
    print(f"✅ 快捷指令已触发，动作数量: {len(actions)}")
    print()

    # 测试9：删除快捷指令
    print("9. 删除快捷指令")
    if manager.delete_shortcut(shortcut3['id']):
        print(f"✅ 快捷指令已删除: {shortcut3['id']}")
    else:
        print(f"❌ 删除快捷指令失败: {shortcut3['id']}")
    print()

    # 测试10：更新快捷指令
    print("10. 更新快捷指令")
    if manager.update_shortcut(shortcut1['id'], {"description": "更新后的描述"}):
        print(f"✅ 快捷指令已更新: {shortcut1['id']}")
        updated = manager.get_shortcut(shortcut1['id'])
        print(f"   新描述: {updated['description']}")
    else:
        print(f"❌ 更新快捷指令失败: {shortcut1['id']}")
    print()

    print("=== 测试完成 ===")


if __name__ == "__main__":
    main()
