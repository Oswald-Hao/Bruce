#!/usr/bin/env python3
"""
智能合同管理系统 (Smart Contract Manager)
合同起草、审查、模板管理、风险识别、合同跟踪
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from jinja2 import Template
except ImportError:
    Template = None


class ContractTemplate:
    """合同模板"""

    # 预定义合同模板
    TEMPLATES = {
        "销售合同": {
            "sections": [
                {"name": "基本信息", "fields": ["buyer", "seller", "contract_no", "sign_date"]},
                {"name": "商品信息", "fields": ["product_name", "quantity", "unit_price", "total_price"]},
                {"name": "交付条款", "fields": ["delivery_date", "delivery_place", "delivery_method"]},
                {"name": "付款条款", "fields": ["payment_method", "payment_time"]},
                {"name": "质量保证", "fields": ["quality_standard", "warranty_period"]},
                {"name": "违约责任", "fields": ["penalty_clause"]}
            ],
            "content": """
# 销售合同

**合同编号：** {{ contract_no }}
**签署日期：** {{ sign_date }}

## 一、合同双方

**甲方（买方）：** {{ buyer }}
**乙方（卖方）：** {{ seller }}

## 二、商品信息

| 项目 | 内容 |
|------|------|
| 商品名称 | {{ product_name }} |
| 数量 | {{ quantity }} |
| 单价 | {{ unit_price }} 元 |
| 总价 | {{ total_price }} 元 |

## 三、交付条款

**交付日期：** {{ delivery_date }}
**交付地点：** {{ delivery_place }}
**交付方式：** {{ delivery_method }}

## 四、付款条款

**付款方式：** {{ payment_method }}
**付款时间：** {{ payment_time }}

## 五、质量保证

**质量标准：** {{ quality_standard }}
**保修期：** {{ warranty_period }}

## 六、违约责任

{{ penalty_clause }}

## 七、其他条款

本合同一式两份，甲乙双方各执一份，自签字盖章之日起生效。
            """
        },
        "采购合同": {
            "sections": [
                {"name": "基本信息", "fields": ["buyer", "supplier", "contract_no", "sign_date"]},
                {"name": "采购物品", "fields": ["item_name", "quantity", "unit_price", "total_price"]},
                {"name": "交付条款", "fields": ["delivery_date", "delivery_place", "acceptance_standard"]},
                {"name": "付款条款", "fields": ["payment_method", "payment_time", "deposit_ratio"]}
            ],
            "content": """
# 采购合同

**合同编号：** {{ contract_no }}
**签署日期：** {{ sign_date }}

## 一、合同双方

**甲方（采购方）：** {{ buyer }}
**乙方（供应商）：** {{ supplier }}

## 二、采购物品

| 项目 | 内容 |
|------|------|
| 物品名称 | {{ item_name }} |
| 数量 | {{ quantity }} |
| 单价 | {{ unit_price }} 元 |
| 总价 | {{ total_price }} 元 |

## 三、交付条款

**交付日期：** {{ delivery_date }}
**交付地点：** {{ delivery_place }}
**验收标准：** {{ acceptance_standard }}

## 四、付款条款

**付款方式：** {{ payment_method }}
**付款时间：** {{ payment_time }}
**定金比例：** {{ deposit_ratio }}%

## 五、其他条款

本合同一式两份，甲乙双方各执一份，自签字盖章之日起生效。
            """
        },
        "服务合同": {
            "sections": [
                {"name": "基本信息", "fields": ["client", "provider", "contract_no", "sign_date"]},
                {"name": "服务内容", "fields": ["service_name", "service_scope", "service_period"]},
                {"name": "服务费用", "fields": ["service_fee", "payment_method", "payment_schedule"]},
                {"name": "服务质量", "fields": ["service_standard", "sla_clause"]},
                {"name": "保密条款", "fields": ["confidentiality_clause"]}
            ],
            "content": """
# 服务合同

**合同编号：** {{ contract_no }}
**签署日期：** {{ sign_date }}

## 一、合同双方

**甲方（委托方）：** {{ client }}
**乙方（服务方）：** {{ provider }}

## 二、服务内容

**服务名称：** {{ service_name }}
**服务范围：** {{ service_scope }}
**服务期限：** {{ service_period }}

## 三、服务费用

**服务费用：** {{ service_fee }} 元
**付款方式：** {{ payment_method }}
**付款计划：** {{ payment_schedule }}

## 四、服务质量

**服务标准：** {{ service_standard }}
**SLA条款：** {{ sla_clause }}

## 五、保密条款

{{ confidentiality_clause }}

## 六、其他条款

本合同一式两份，甲乙双方各执一份，自签字盖章之日起生效。
            """
        },
        "保密协议": {
            "sections": [
                {"name": "基本信息", "fields": ["discloser", "recipient", "contract_no", "sign_date"]},
                {"name": "保密信息", "fields": ["confidential_info", "usage_scope", "return_obligation"]},
                {"name": "保密期限", "fields": ["confidentiality_period", "post_termination_period"]},
                {"name": "违约责任", "fields": ["penalty_clause"]}
            ],
            "content": """
# 保密协议

**协议编号：** {{ contract_no }}
**签署日期：** {{ sign_date }}

## 一、协议双方

**甲方（披露方）：** {{ discloser }}
**乙方（接收方）：** {{ recipient }}

## 二、保密信息

**保密信息定义：** {{ confidential_info }}
**使用范围：** {{ usage_scope }}
**归还义务：** {{ return_obligation }}

## 三、保密期限

**保密期：** {{ confidentiality_period }}
**终止后保密期：** {{ post_termination_period }}

## 四、违约责任

{{ penalty_clause }}

## 五、其他条款

本协议一式两份，甲乙双方各执一份，自签字盖章之日起生效。
            """
        }
    }

    @classmethod
    def get_template_names(cls) -> List[str]:
        """获取所有模板名称"""
        return list(cls.TEMPLATES.keys())

    @classmethod
    def get_template(cls, template_name: str) -> Optional[Dict]:
        """获取指定模板"""
        return cls.TEMPLATES.get(template_name)

    @classmethod
    def get_template_fields(cls, template_name: str) -> List[str]:
        """获取模板所需字段"""
        template = cls.get_template(template_name)
        if not template:
            return []
        fields = []
        for section in template['sections']:
            fields.extend(section['fields'])
        return fields


class ContractReviewer:
    """合同审查器"""

    # 风险关键词和风险等级
    RISK_KEYWORDS = {
        "high": [
            "无限责任", "连带责任", "全部责任",
            "不可撤销", "永久", "永久有效",
            "放弃", "豁免", "不承担任何责任",
            "全部损失", "一切损失",
            "任何情况下", "无论何种情况"
        ],
        "medium": [
            "违约金", "赔偿", "罚款",
            "单方解除", "单方终止",
            "知识产权", "保密", "保密义务",
            "延期", "逾期", "推迟",
            "免责", "免除责任"
        ],
        "low": [
            "义务", "责任", "权利",
            "交付", "验收", "付款",
            "质量", "标准", "保修",
            "争议", "争议解决", "仲裁", "诉讼"
        ]
    }

    @classmethod
    def review_contract(cls, contract_text: str) -> Dict:
        """审查合同，返回风险分析"""
        risks = []
        risk_scores = {"high": 0, "medium": 0, "low": 0}

        # 检查各类风险关键词
        for level, keywords in cls.RISK_KEYWORDS.items():
            for keyword in keywords:
                count = contract_text.count(keyword)
                if count > 0:
                    risks.append({
                        "level": level,
                        "keyword": keyword,
                        "count": count,
                        "message": cls._get_risk_message(level, keyword)
                    })
                    risk_scores[level] += count

        # 计算总体风险分数
        total_score = risk_scores["high"] * 10 + risk_scores["medium"] * 5 + risk_scores["low"] * 2
        overall_risk = cls._get_overall_risk(total_score)

        # 生成审查建议
        suggestions = cls._generate_suggestions(risks)

        return {
            "overall_risk": overall_risk,
            "risk_score": total_score,
            "risk_distribution": risk_scores,
            "risks": risks,
            "suggestions": suggestions,
            "review_time": datetime.now().isoformat()
        }

    @staticmethod
    def _get_risk_message(level: str, keyword: str) -> str:
        """生成风险提示信息"""
        messages = {
            "high": f"高风险：'{keyword}' 可能带来重大法律风险",
            "medium": f"中风险：'{keyword}' 需要仔细审查",
            "low": f"低风险：'{keyword}' 属于常规条款"
        }
        return messages.get(level, f"发现关键词：'{keyword}'")

    @staticmethod
    def _get_overall_risk(score: int) -> str:
        """获取总体风险等级"""
        if score >= 50:
            return "高风险"
        elif score >= 20:
            return "中风险"
        elif score >= 5:
            return "低风险"
        else:
            return "无风险"

    @staticmethod
    def _generate_suggestions(risks: List[Dict]) -> List[str]:
        """生成审查建议"""
        suggestions = []
        high_risks = [r for r in risks if r['level'] == 'high']
        medium_risks = [r for r in risks if r['level'] == 'medium']

        if high_risks:
            suggestions.append("⚠️  合同包含高风险条款，建议咨询专业律师")
            suggestions.append("   重点关注责任条款和豁免条款")
            suggestions.append("   避免接受'无限责任'、'全部损失'等条款")

        if medium_risks:
            suggestions.append("⚡ 合同包含中风险条款，需要仔细审阅")
            suggestions.append("   核实违约金比例是否合理")
            suggestions.append("   确认保密条款的范围和期限")

        if len(suggestions) == 0:
            suggestions.append("✅ 合同审查通过，风险较低")

        return suggestions


class ContractManager:
    """合同管理器"""

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.contracts_file = self.data_dir / 'contracts.json'
        self.contracts = self._load_contracts()

    def _load_contracts(self) -> List[Dict]:
        """加载合同数据"""
        if self.contracts_file.exists():
            with open(self.contracts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_contracts(self):
        """保存合同数据"""
        with open(self.contracts_file, 'w', encoding='utf-8') as f:
            json.dump(self.contracts, f, ensure_ascii=False, indent=2)

    def create_contract(self, template_name: str, **kwargs) -> Dict:
        """基于模板创建合同"""
        template_info = ContractTemplate.get_template(template_name)
        if not template_info:
            raise ValueError(f"模板 '{template_name}' 不存在")

        # 生成合同编号
        contract_no = f"CT{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # 渲染合同内容
        contract_data = {
            "contract_no": contract_no,
            "sign_date": datetime.now().strftime('%Y-%m-%d'),
            **kwargs
        }

        if Template:
            template = Template(template_info['content'])
            contract_text = template.render(**contract_data)
        else:
            contract_text = template_info['content'].format(**contract_data)

        contract = {
            "id": len(self.contracts) + 1,
            "template_name": template_name,
            "contract_no": contract_no,
            "data": contract_data,
            "content": contract_text,
            "status": "draft",  # draft, reviewed, signed, expired
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "expiry_date": None
        }

        self.contracts.append(contract)
        self._save_contracts()
        return contract

    def get_contract(self, contract_id: int) -> Optional[Dict]:
        """获取合同"""
        for contract in self.contracts:
            if contract['id'] == contract_id:
                return contract
        return None

    def update_contract(self, contract_id: int, **kwargs) -> bool:
        """更新合同"""
        contract = self.get_contract(contract_id)
        if not contract:
            return False

        contract.update(kwargs)
        contract['updated_at'] = datetime.now().isoformat()
        self._save_contracts()
        return True

    def review_contract(self, contract_id: int) -> Optional[Dict]:
        """审查合同"""
        contract = self.get_contract(contract_id)
        if not contract:
            return None

        review_result = ContractReviewer.review_contract(contract['content'])

        # 更新合同状态
        contract['review_result'] = review_result
        contract['status'] = 'reviewed'
        contract['updated_at'] = datetime.now().isoformat()
        self._save_contracts()

        return review_result

    def set_expiry_date(self, contract_id: int, expiry_date: str) -> bool:
        """设置合同到期日期"""
        contract = self.get_contract(contract_id)
        if not contract:
            return False

        contract['expiry_date'] = expiry_date
        contract['updated_at'] = datetime.now().isoformat()
        self._save_contracts()
        return True

    def get_expiring_contracts(self, days: int = 30) -> List[Dict]:
        """获取即将到期的合同"""
        now = datetime.now()
        threshold = now + timedelta(days=days)

        expiring = []
        for contract in self.contracts:
            if contract['expiry_date']:
                expiry = datetime.fromisoformat(contract['expiry_date'])
                if now <= expiry <= threshold:
                    expiring.append(contract)

        return expiring

    def get_stats(self) -> Dict:
        """获取统计数据"""
        stats = {
            "total": len(self.contracts),
            "by_status": {},
            "by_template": {},
            "expiring_count": len(self.get_expiring_contracts(30))
        }

        for contract in self.contracts:
            status = contract['status']
            template = contract['template_name']

            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
            stats['by_template'][template] = stats['by_template'].get(template, 0) + 1

        return stats

    def export_contracts(self, format: str = 'json', output_path: str = None) -> str:
        """导出合同数据"""
        data = {
            "contracts": self.contracts,
            "exported_at": datetime.now().isoformat()
        }

        if output_path is None:
            output_path = os.path.join(
                self.data_dir,
                f'contracts_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.{format}'
            )

        if format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        elif format == 'markdown':
            with open(output_path, 'w', encoding='utf-8') as f:
                for contract in self.contracts:
                    f.write(f"# 合同 {contract['contract_no']}\n\n")
                    f.write(f"模板: {contract['template_name']}\n")
                    f.write(f"状态: {contract['status']}\n")
                    f.write(f"创建时间: {contract['created_at']}\n\n")
                    f.write(contract['content'])
                    f.write("\n\n" + "=" * 60 + "\n\n")

        return output_path


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("Usage: python contract_manager.py <command> [options]")
        print("\nCommands:")
        print("  create       - Create contract from template")
        print("  view         - View contract details")
        print("  review       - Review contract")
        print("  update       - Update contract status")
        print("  templates    - List available templates")
        print("  stats        - Show statistics")
        print("  check-expiry - Check expiring contracts")
        print("  export       - Export contracts")
        sys.exit(1)

    manager = ContractManager()
    command = sys.argv[1]

    if command == 'create':
        template = sys.argv[sys.argv.index('--template') + 1]

        # 获取模板所需字段
        fields = ContractTemplate.get_template_fields(template)

        # 收集字段值
        contract_data = {}
        for field in fields:
            if f'--{field}' in sys.argv:
                idx = sys.argv.index(f'--{field}')
                contract_data[field] = sys.argv[idx + 1]

        contract = manager.create_contract(template, **contract_data)
        print(f"✓ Contract created: {contract['contract_no']} (ID: {contract['id']})")

    elif command == 'view':
        contract_id = int(sys.argv[sys.argv.index('--id') + 1])
        contract = manager.get_contract(contract_id)

        if contract:
            print(f"\n{'=' * 60}")
            print(f"合同编号: {contract['contract_no']}")
            print(f"模板: {contract['template_name']}")
            print(f"状态: {contract['status']}")
            print(f"创建时间: {contract['created_at']}")
            print(f"{'=' * 60}\n")
            print(contract['content'])
        else:
            print(f"✗ Contract not found: {contract_id}")

    elif command == 'review':
        contract_id = int(sys.argv[sys.argv.index('--id') + 1])
        result = manager.review_contract(contract_id)

        if result:
            print(f"\n{'=' * 60}")
            print(f"合同审查结果")
            print(f"{'=' * 60}")
            print(f"总体风险: {result['overall_risk']}")
            print(f"风险分数: {result['risk_score']}")
            print(f"\n风险分布: {result['risk_distribution']}")
            print(f"\n发现风险: {len(result['risks'])} 个")
            for risk in result['risks']:
                print(f"  - {risk['message']}")
            print(f"\n审查建议:")
            for suggestion in result['suggestions']:
                print(f"  {suggestion}")
        else:
            print(f"✗ Contract not found: {contract_id}")

    elif command == 'update':
        contract_id = int(sys.argv[sys.argv.index('--id') + 1])
        status = sys.argv[sys.argv.index('--status') + 1]

        if manager.update_contract(contract_id, status=status):
            print(f"✓ Contract {contract_id} status updated to: {status}")
        else:
            print(f"✗ Failed to update contract {contract_id}")

    elif command == 'templates':
        print("\n可用合同模板:")
        for i, name in enumerate(ContractTemplate.get_template_names(), 1):
            template = ContractTemplate.get_template(name)
            print(f"  {i}. {name}")
            for section in template['sections']:
                print(f"     - {section['name']}: {', '.join(section['fields'])}")

    elif command == 'stats':
        stats = manager.get_stats()

        print(f"\n📊 合同统计:")
        print(f"  总数: {stats['total']}")
        print(f"  按状态: {stats['by_status']}")
        print(f"  按模板: {stats['by_template']}")
        print(f"  即将到期: {stats['expiring_count']} 个")

    elif command == 'check-expiry':
        days = int(sys.argv[sys.argv.index('--days') + 1]) if '--days' in sys.argv else 30
        expiring = manager.get_expiring_contracts(days)

        if expiring:
            print(f"\n⏰ 即将到期合同（{days}天内）: {len(expiring)} 个")
            for contract in expiring:
                print(f"  - {contract['contract_no']} ({contract['template_name']}) 到期: {contract['expiry_date']}")
        else:
            print(f"\n✅ 没有{days}天内到期的合同")

    elif command == 'export':
        format_type = sys.argv[sys.argv.index('--format') + 1] if '--format' in sys.argv else 'json'
        output = sys.argv[sys.argv.index('--output') + 1] if '--output' in sys.argv else None
        path = manager.export_contracts(format_type, output)
        print(f"✓ Contracts exported to: {path}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
