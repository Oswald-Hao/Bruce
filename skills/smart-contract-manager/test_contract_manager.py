#!/usr/bin/env python3
"""
智能合同管理系统测试
测试所有核心功能
"""

import json
import os
import sys
import tempfile
from pathlib import Path

# 添加父目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from contract_manager import (
    ContractTemplate,
    ContractReviewer,
    ContractManager
)


class TestContractTemplate:
    """合同模板测试"""

    def __init__(self):
        self.passed = 0
        self.failed = 0

    def assert_equal(self, actual, expected, test_name):
        if actual == expected:
            self.passed += 1
            print(f"  ✓ {test_name}")
        else:
            self.failed += 1
            print(f"  ✗ {test_name}: expected {expected}, got {actual}")

    def assert_not_none(self, value, test_name):
        if value is not None:
            self.passed += 1
            print(f"  ✓ {test_name}")
        else:
            self.failed += 1
            print(f"  ✗ {test_name}: value is None")

    def assert_greater(self, actual, min_val, test_name):
        if actual > min_val:
            self.passed += 1
            print(f"  ✓ {test_name}")
        else:
            self.failed += 1
            print(f"  ✗ {test_name}: expected > {min_val}, got {actual}")

    def assert_in(self, item, container, test_name):
        if item in container:
            self.passed += 1
            print(f"  ✓ {test_name}")
        else:
            self.failed += 1
            print(f"  ✗ {test_name}: {item} not in {container}")

    def test_get_template_names(self):
        """测试获取模板名称"""
        print("\n[测试] 合同模板 - 获取模板名称")

        names = ContractTemplate.get_template_names()
        self.assert_greater(len(names), 0, "模板数量 > 0")
        self.assert_in("销售合同", names, "包含销售合同模板")
        self.assert_in("采购合同", names, "包含采购合同模板")
        self.assert_in("服务合同", names, "包含服务合同模板")

    def test_get_template(self):
        """测试获取模板"""
        print("\n[测试] 合同模板 - 获取模板")

        template = ContractTemplate.get_template("销售合同")
        self.assert_not_none(template, "模板存在")
        self.assert_equal(template['sections'][0]['name'], '基本信息', "第一部分名称")
        self.assert_in('content', template, "模板包含内容")

    def test_get_template_fields(self):
        """测试获取模板字段"""
        print("\n[测试] 合同模板 - 获取模板字段")

        fields = ContractTemplate.get_template_fields("销售合同")
        self.assert_greater(len(fields), 0, "字段数量 > 0")
        self.assert_in("buyer", fields, "包含buyer字段")
        self.assert_in("seller", fields, "包含seller字段")

    def run_all(self):
        """运行所有测试"""
        print("=" * 60)
        print("合同模板测试")
        print("=" * 60)

        self.test_get_template_names()
        self.test_get_template()
        self.test_get_template_fields()

        print(f"\n结果: {self.passed} 通过, {self.failed} 失败")
        return self.failed == 0


class TestContractReviewer:
    """合同审查器测试"""

    def __init__(self):
        self.passed = 0
        self.failed = 0

    def assert_equal(self, actual, expected, test_name):
        if actual == expected:
            self.passed += 1
            print(f"  ✓ {test_name}")
        else:
            self.failed += 1
            print(f"  ✗ {test_name}: expected {expected}, got {actual}")

    def assert_not_none(self, value, test_name):
        if value is not None:
            self.passed += 1
            print(f"  ✓ {test_name}")
        else:
            self.failed += 1
            print(f"  ✗ {test_name}: value is None")

    def assert_true(self, value, test_name):
        if value:
            self.passed += 1
            print(f"  ✓ {test_name}")
        else:
            self.failed += 1
            print(f"  ✗ {test_name}: expected True, got {value}")

    def assert_greater(self, actual, min_val, test_name):
        if actual > min_val:
            self.passed += 1
            print(f"  ✓ {test_name}")
        else:
            self.failed += 1
            print(f"  ✗ {test_name}: expected > {min_val}, got {actual}")

    def assert_in(self, item, container, test_name):
        if item in container:
            self.passed += 1
            print(f"  ✓ {test_name}")
        else:
            self.failed += 1
            print(f"  ✗ {test_name}: {item} not in {container}")

    def test_review_simple_contract(self):
        """测试审查简单合同"""
        print("\n[测试] 合同审查器 - 简单合同审查")

        contract_text = """
        # 销售合同
        甲方：公司A
        乙方：公司B
        付款方式：银行转账
        交付日期：2026年3月1日
        """

        result = ContractReviewer.review_contract(contract_text)
        self.assert_not_none(result, "审查结果存在")
        self.assert_in(result['overall_risk'], ['无风险', '低风险'], "总体风险为无或低")
        self.assert_true(len(result['suggestions']) > 0, "有审查建议")

    def test_review_high_risk_contract(self):
        """测试审查高风险合同"""
        print("\n[测试] 合同审查器 - 高风险合同审查")

        contract_text = """
        # 销售合同
        甲方：公司A
        乙方：公司B
        甲方承担无限责任。
        甲方承担全部损失。
        不可撤销，永久有效。
        """

        result = ContractReviewer.review_contract(contract_text)
        self.assert_not_none(result, "审查结果存在")
        self.assert_equal(result['overall_risk'], '高风险', "总体风险为高")
        self.assert_greater(result['risk_score'], 30, "风险分数较高")
        self.assert_true(len(result['risks']) > 0, "发现风险")

    def test_review_medium_risk_contract(self):
        """测试审查中风险合同"""
        print("\n[测试] 合同审查器 - 中风险合同审查")

        contract_text = """
        # 服务合同
        客户：公司A
        服务商：公司B
        违约金：合同总额的30%
        单方解除权：甲方有权单方解除
        """

        result = ContractReviewer.review_contract(contract_text)
        self.assert_not_none(result, "审查结果存在")
        self.assert_in('中风险', result['overall_risk'], "包含中风险")
        self.assert_true('违约金' in str(result['risks']), "发现违约金风险")

    def test_suggestions_generation(self):
        """测试建议生成"""
        print("\n[测试] 合同审查器 - 建议生成")

        contract_text = "甲方承担无限责任。甲方承担全部损失。"
        result = ContractReviewer.review_contract(contract_text)

        self.assert_true(len(result['suggestions']) > 0, "有建议生成")
        self.assert_true(
            any('高风险' in s for s in result['suggestions']),
            "有高风险建议"
        )

    def run_all(self):
        """运行所有测试"""
        print("=" * 60)
        print("合同审查器测试")
        print("=" * 60)

        self.test_review_simple_contract()
        self.test_review_high_risk_contract()
        self.test_review_medium_risk_contract()
        self.test_suggestions_generation()

        print(f"\n结果: {self.passed} 通过, {self.failed} 失败")
        return self.failed == 0


class TestContractManager:
    """合同管理器测试"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.temp_dir = tempfile.mkdtemp()

    def assert_equal(self, actual, expected, test_name):
        if actual == expected:
            self.passed += 1
            print(f"  ✓ {test_name}")
        else:
            self.failed += 1
            print(f"  ✗ {test_name}: expected {expected}, got {actual}")

    def assert_not_none(self, value, test_name):
        if value is not None:
            self.passed += 1
            print(f"  ✓ {test_name}")
        else:
            self.failed += 1
            print(f"  ✗ {test_name}: value is None")

    def assert_true(self, value, test_name):
        if value:
            self.passed += 1
            print(f"  ✓ {test_name}")
        else:
            self.failed += 1
            print(f"  ✗ {test_name}: expected True, got {value}")

    def assert_greater(self, actual, min_val, test_name):
        if actual > min_val:
            self.passed += 1
            print(f"  ✓ {test_name}")
        else:
            self.failed += 1
            print(f"  ✗ {test_name}: expected > {min_val}, got {actual}")

    def test_create_contract(self):
        """测试创建合同"""
        print("\n[测试] 合同管理器 - 创建合同")

        manager = ContractManager(self.temp_dir)
        contract = manager.create_contract(
            template_name="销售合同",
            buyer="公司A",
            seller="公司B",
            product_name="笔记本电脑",
            quantity="10",
            unit_price="5000",
            total_price="50000",
            delivery_date="2026-03-01",
            delivery_place="北京",
            delivery_method="送货上门",
            payment_method="银行转账",
            payment_time="货到付款",
            quality_standard="国家标准",
            warranty_period="1年",
            penalty_clause="违约方需承担合同总额20%的违约金"
        )

        self.assert_not_none(contract, "合同创建成功")
        self.assert_equal(contract['id'], 1, "合同ID正确")
        self.assert_equal(contract['template_name'], "销售合同", "模板名称正确")
        self.assert_equal(contract['status'], 'draft', "状态为草稿")
        self.assert_true(contract['contract_no'].startswith('CT'), "合同编号格式正确")

    def test_get_contract(self):
        """测试获取合同"""
        print("\n[测试] 合同管理器 - 获取合同")

        manager = ContractManager(self.temp_dir)
        contract = manager.get_contract(1)

        self.assert_not_none(contract, "获取合同成功")
        self.assert_equal(contract['id'], 1, "合同ID正确")
        self.assert_in('销售合同', contract['content'], "内容包含模板类型")

    def test_update_contract(self):
        """测试更新合同"""
        print("\n[测试] 合同管理器 - 更新合同")

        manager = ContractManager(self.temp_dir)
        success = manager.update_contract(1, status='signed')

        self.assert_true(success, "更新成功")

        contract = manager.get_contract(1)
        self.assert_equal(contract['status'], 'signed', "状态更新正确")

    def test_review_contract(self):
        """测试审查合同"""
        print("\n[测试] 合同管理器 - 审查合同")

        manager = ContractManager(self.temp_dir)
        result = manager.review_contract(1)

        self.assert_not_none(result, "审查结果存在")
        self.assert_true('overall_risk' in result, "包含总体风险")
        self.assert_true('risks' in result, "包含风险列表")
        self.assert_true('suggestions' in result, "包含建议")

        # 检查合同状态更新
        contract = manager.get_contract(1)
        self.assert_equal(contract['status'], 'reviewed', "状态更新为已审查")

    def test_set_expiry_date(self):
        """测试设置到期日期"""
        print("\n[测试] 合同管理器 - 设置到期日期")

        manager = ContractManager(self.temp_dir)
        expiry_date = "2027-12-31"
        success = manager.set_expiry_date(1, expiry_date)

        self.assert_true(success, "设置成功")

        contract = manager.get_contract(1)
        self.assert_equal(contract['expiry_date'], expiry_date, "到期日期正确")

    def test_get_expiring_contracts(self):
        """测试获取即将到期合同"""
        print("\n[测试] 合同管理器 - 获取即将到期合同")

        manager = ContractManager(self.temp_dir)

        # 创建一个即将到期的合同
        from datetime import datetime, timedelta
        expiring_date = (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d')
        manager.create_contract(
            template_name="采购合同",
            buyer="公司C",
            supplier="公司D",
            item_name="办公用品",
            quantity="100",
            unit_price="50",
            total_price="5000",
            delivery_date="2026-03-01",
            delivery_place="上海",
            acceptance_standard="国家标准"
        )
        manager.set_expiry_date(2, expiring_date)

        # 创建一个不快到期的合同
        future_date = (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d')
        manager.create_contract(
            template_name="服务合同",
            client="公司E",
            provider="公司F",
            service_name="IT服务",
            service_scope="系统集成",
            service_period="1年",
            service_fee="100000",
            payment_method="分期付款",
            payment_schedule="每季度25%",
            service_standard="行业标准",
            sla_clause="响应时间24小时",
            confidentiality_clause="保密5年"
        )
        manager.set_expiry_date(3, future_date)

        expiring = manager.get_expiring_contracts(30)
        self.assert_true(len(expiring) >= 1, "找到即将到期合同")

    def test_get_stats(self):
        """测试获取统计数据"""
        print("\n[测试] 合同管理器 - 统计数据")

        manager = ContractManager(self.temp_dir)
        stats = manager.get_stats()

        self.assert_true(stats['total'] > 0, "总合同数 > 0")
        self.assert_true('by_status' in stats, "包含状态统计")
        self.assert_true('by_template' in stats, "包含模板统计")
        self.assert_true('expiring_count' in stats, "包含到期统计")

    def test_export_contracts(self):
        """测试导出合同"""
        print("\n[测试] 合同管理器 - 导出合同")

        manager = ContractManager(self.temp_dir)
        path = manager.export_contracts(format='json')

        self.assert_true(os.path.exists(path), "导出文件存在")

        # 验证数据
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assert_true('contracts' in data, "包含合同数据")
            self.assert_true(len(data['contracts']) > 0, "合同数量 > 0")

        os.unlink(path)

    def run_all(self):
        """运行所有测试"""
        print("=" * 60)
        print("合同管理器测试")
        print("=" * 60)

        self.test_create_contract()
        self.test_get_contract()
        self.test_update_contract()
        self.test_review_contract()
        self.test_set_expiry_date()
        self.test_get_expiring_contracts()
        self.test_get_stats()
        self.test_export_contracts()

        print(f"\n结果: {self.passed} 通过, {self.failed} 失败")
        return self.failed == 0


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("智能合同管理系统 - 完整测试套件")
    print("=" * 60)

    all_passed = True

    # 运行合同模板测试
    template_tests = TestContractTemplate()
    if not template_tests.run_all():
        all_passed = False

    # 运行合同审查器测试
    reviewer_tests = TestContractReviewer()
    if not reviewer_tests.run_all():
        all_passed = False

    # 运行合同管理器测试
    manager_tests = TestContractManager()
    if not manager_tests.run_all():
        all_passed = False

    # 清理临时目录
    import shutil
    shutil.rmtree(manager_tests.temp_dir, ignore_errors=True)

    # 总结
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有测试通过！")
        print("=" * 60)
        return 0
    else:
        print("❌ 部分测试失败")
        print("=" * 60)
        return 1


if __name__ == '__main__':
    sys.exit(main())
