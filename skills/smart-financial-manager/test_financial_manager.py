#!/usr/bin/env python3
"""
智能财务管理系统测试
测试所有核心功能
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

# 添加父目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from financial_manager import (
    Transaction,
    Invoice,
    FinancialManager
)


class TestTransaction:
    """交易记录测试"""

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

    def test_create_transaction(self):
        """测试创建交易"""
        print("\n[测试] 交易记录 - 创建交易")

        transaction = Transaction(
            transaction_type='income',
            amount=10000.0,
            category='销售收入',
            description='产品销售',
            tags=['销售', '电子产品']
        )

        self.assert_not_none(transaction, "交易创建成功")
        self.assert_equal(transaction.type, 'income', "交易类型正确")
        self.assert_equal(float(transaction.amount), 10000.0, "金额正确")
        self.assert_equal(transaction.category, '销售收入', "分类正确")

    def test_transaction_to_dict(self):
        """测试交易转字典"""
        print("\n[测试] 交易记录 - 转字典")

        transaction = Transaction('expense', 500.0, '运营费用')
        transaction.id = 1
        data = transaction.to_dict()

        self.assert_equal(data['id'], 1, "ID正确")
        self.assert_equal(data['type'], 'expense', "类型正确")
        self.assert_equal(data['amount'], 500.0, "金额正确")

    def test_transaction_from_dict(self):
        """测试从字典创建交易"""
        print("\n[测试] 交易记录 - 从字典创建")

        data = {
            'id': 1,
            'type': 'income',
            'amount': 2000.0,
            'category': '服务收入',
            'description': '',
            'tags': []
        }
        transaction = Transaction.from_dict(data)

        self.assert_equal(transaction.id, 1, "ID正确")
        self.assert_equal(transaction.type, 'income', "类型正确")

    def run_all(self):
        """运行所有测试"""
        print("=" * 60)
        print("交易记录测试")
        print("=" * 60)

        self.test_create_transaction()
        self.test_transaction_to_dict()
        self.test_transaction_from_dict()

        print(f"\n结果: {self.passed} 通过, {self.failed} 失败")
        return self.failed == 0


class TestInvoice:
    """发票测试"""

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

    def test_create_invoice(self):
        """测试创建发票"""
        print("\n[测试] 发票 - 创建发票")

        invoice = Invoice(
            invoice_number='INV-001',
            amount=5000.0,
            invoice_type='sales',
            date='2026-02-01',
            buyer='公司A',
            seller='公司B'
        )

        self.assert_not_none(invoice, "发票创建成功")
        self.assert_equal(invoice.invoice_number, 'INV-001', "发票号正确")
        self.assert_equal(invoice.type, 'sales', "类型正确")

    def test_invoice_to_dict(self):
        """测试发票转字典"""
        print("\n[测试] 发票 - 转字典")

        invoice = Invoice('INV-002', 3000.0, 'purchase')
        invoice.id = 1
        data = invoice.to_dict()

        self.assert_equal(data['id'], 1, "ID正确")
        self.assert_equal(data['invoice_number'], 'INV-002', "发票号正确")

    def run_all(self):
        """运行所有测试"""
        print("=" * 60)
        print("发票测试")
        print("=" * 60)

        self.test_create_invoice()
        self.test_invoice_to_dict()

        print(f"\n结果: {self.passed} 通过, {self.failed} 失败")
        return self.failed == 0


class TestFinancialManager:
    """财务管理器测试"""

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

    def test_record_transaction(self):
        """测试记录交易"""
        print("\n[测试] 财务管理器 - 记录交易")

        manager = FinancialManager(self.temp_dir)
        transaction = manager.record_transaction(
            transaction_type='income',
            amount=10000.0,
            category='销售收入',
            description='产品销售'
        )

        self.assert_not_none(transaction, "交易记录成功")
        self.assert_equal(transaction.id, 1, "ID正确")
        self.assert_equal(transaction.type, 'income', "类型正确")

    def test_get_transactions(self):
        """测试获取交易列表"""
        print("\n[测试] 财务管理器 - 获取交易列表")

        manager = FinancialManager(self.temp_dir)

        # 添加更多交易
        manager.record_transaction('expense', 500.0, '运营费用')
        manager.record_transaction('income', 2000.0, '服务收入')

        transactions = manager.get_transactions()
        self.assert_greater(len(transactions), 0, "交易数量 > 0")

        # 测试类型筛选
        income_transactions = manager.get_transactions(transaction_type='income')
        self.assert_true(len(income_transactions) >= 2, "收入交易 >= 2")

    def test_get_balance(self):
        """测试获取余额"""
        print("\n[测试] 财务管理器 - 获取余额")

        manager = FinancialManager(self.temp_dir)
        balance = manager.get_balance()

        self.assert_not_none(balance, "余额存在")
        self.assert_true('income' in balance, "包含收入")
        self.assert_true('expense' in balance, "包含支出")
        self.assert_true('balance' in balance, "包含净余额")

    def test_add_invoice(self):
        """测试添加发票"""
        print("\n[测试] 财务管理器 - 添加发票")

        manager = FinancialManager(self.temp_dir)
        invoice = manager.add_invoice(
            invoice_number='INV-001',
            amount=5000.0,
            invoice_type='sales',
            buyer='公司A',
            seller='公司B'
        )

        self.assert_not_none(invoice, "发票添加成功")
        self.assert_equal(invoice.id, 1, "ID正确")
        self.assert_equal(invoice.invoice_number, 'INV-001', "发票号正确")

    def test_get_invoices(self):
        """测试获取发票列表"""
        print("\n[测试] 财务管理器 - 获取发票列表")

        manager = FinancialManager(self.temp_dir)
        manager.add_invoice('INV-002', 3000.0, 'purchase')
        manager.add_invoice('INV-003', 4000.0, 'sales')

        invoices = manager.get_invoices()
        self.assert_true(len(invoices) >= 3, "发票数量 >= 3")

        # 测试类型筛选
        sales_invoices = manager.get_invoices(invoice_type='sales')
        self.assert_true(len(sales_invoices) >= 2, "销售发票 >= 2")

    def test_generate_balance_sheet(self):
        """测试生成资产负债表"""
        print("\n[测试] 财务管理器 - 生成资产负债表")

        manager = FinancialManager(self.temp_dir)
        report = manager.generate_balance_sheet()

        self.assert_not_none(report, "报表存在")
        self.assert_true('assets' in report, "包含资产")
        self.assert_true('liabilities' in report, "包含负债")
        self.assert_true('equity' in report, "包含所有者权益")

    def test_generate_income_statement(self):
        """测试生成损益表"""
        print("\n[测试] 财务管理器 - 生成损益表")

        manager = FinancialManager(self.temp_dir)
        now = datetime.now()
        start_date = (now - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = now.strftime('%Y-%m-%d')

        report = manager.generate_income_statement(start_date, end_date)

        self.assert_not_none(report, "报表存在")
        self.assert_true('revenue' in report, "包含收入")
        self.assert_true('expenses' in report, "包含支出")
        self.assert_true('net_income' in report, "包含净利润")

    def test_generate_cash_flow_statement(self):
        """测试生成现金流量表"""
        print("\n[测试] 财务管理器 - 生成现金流量表")

        manager = FinancialManager(self.temp_dir)
        now = datetime.now()
        start_date = (now - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = now.strftime('%Y-%m-%d')

        report = manager.generate_cash_flow_statement(start_date, end_date)

        self.assert_not_none(report, "报表存在")
        self.assert_true('operating' in report, "包含经营活动")

    def test_calculate_tax(self):
        """测试税务计算"""
        print("\n[测试] 财务管理器 - 税务计算")

        manager = FinancialManager(self.temp_dir)
        vat = manager.calculate_tax('vat', 'month')

        self.assert_not_none(vat, "税务计算结果存在")
        self.assert_equal(vat['type'], '增值税', "类型正确")
        self.assert_true('vat_payable' in vat, "包含应纳税额")

        # 测试企业所得税
        income_tax = manager.calculate_tax('income_tax', 'month')
        self.assert_not_none(income_tax, "所得税计算结果存在")
        self.assert_equal(income_tax['type'], '企业所得税', "类型正确")

    def test_analyze_financials(self):
        """测试财务分析"""
        print("\n[测试] 财务管理器 - 财务分析")

        manager = FinancialManager(self.temp_dir)
        analysis = manager.analyze_financials('month')

        self.assert_not_none(analysis, "分析结果存在")
        self.assert_true('total_transactions' in analysis, "包含总交易数")
        self.assert_true('category_analysis' in analysis, "包含分类分析")
        self.assert_true('balance' in analysis, "包含余额")

    def test_get_summary(self):
        """测试获取财务摘要"""
        print("\n[测试] 财务管理器 - 财务摘要")

        manager = FinancialManager(self.temp_dir)
        summary = manager.get_summary()

        self.assert_not_none(summary, "摘要存在")
        self.assert_true('balance' in summary, "包含余额")
        self.assert_true('total_transactions' in summary, "包含总交易数")
        self.assert_true('this_month' in summary, "包含本月数据")

    def test_export_data(self):
        """测试导出数据"""
        print("\n[测试] 财务管理器 - 导出数据")

        manager = FinancialManager(self.temp_dir)
        path = manager.export_data(format='json')

        self.assert_true(os.path.exists(path), "导出文件存在")

        # 验证数据
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assert_true('transactions' in data, "包含交易数据")
            self.assert_true('invoices' in data, "包含发票数据")

        os.unlink(path)

    def run_all(self):
        """运行所有测试"""
        print("=" * 60)
        print("财务管理器测试")
        print("=" * 60)

        self.test_record_transaction()
        self.test_get_transactions()
        self.test_get_balance()
        self.test_add_invoice()
        self.test_get_invoices()
        self.test_generate_balance_sheet()
        self.test_generate_income_statement()
        self.test_generate_cash_flow_statement()
        self.test_calculate_tax()
        self.test_analyze_financials()
        self.test_get_summary()
        self.test_export_data()

        print(f"\n结果: {self.passed} 通过, {self.failed} 失败")
        return self.failed == 0


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("智能财务管理系统 - 完整测试套件")
    print("=" * 60)

    all_passed = True

    # 运行交易记录测试
    transaction_tests = TestTransaction()
    if not transaction_tests.run_all():
        all_passed = False

    # 运行发票测试
    invoice_tests = TestInvoice()
    if not invoice_tests.run_all():
        all_passed = False

    # 运行财务管理器测试
    manager_tests = TestFinancialManager()
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
