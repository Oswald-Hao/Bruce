#!/usr/bin/env python3
"""
智能财务管理系统 (Smart Financial Manager)
财务记账、发票管理、报表生成、财务分析、税务计算
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from decimal import Decimal, getcontext

# 设置精度
getcontext().prec = 2


class Transaction:
    """交易记录"""

    def __init__(self, transaction_type: str, amount: float, category: str,
                 description: str = "", tags: List[str] = None):
        self.id = None  # 将在添加时分配
        self.type = transaction_type  # income, expense, transfer
        self.amount = Decimal(str(amount))
        self.category = category
        self.description = description
        self.tags = tags or []
        self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'id': self.id,
            'type': self.type,
            'amount': float(self.amount),
            'category': self.category,
            'description': self.description,
            'tags': self.tags,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Transaction':
        """从字典创建"""
        transaction = cls(
            transaction_type=data['type'],
            amount=data['amount'],
            category=data['category'],
            description=data.get('description', ''),
            tags=data.get('tags', [])
        )
        transaction.id = data.get('id')
        transaction.created_at = data.get('created_at', datetime.now().isoformat())
        return transaction


class Invoice:
    """发票"""

    def __init__(self, invoice_number: str, amount: float, invoice_type: str,
                 date: str = None, buyer: str = "", seller: str = ""):
        self.id = None
        self.invoice_number = invoice_number
        self.amount = Decimal(str(amount))
        self.type = invoice_type  # purchase, sales
        self.date = date or datetime.now().strftime('%Y-%m-%d')
        self.buyer = buyer
        self.seller = seller
        self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'amount': float(self.amount),
            'type': self.type,
            'date': self.date,
            'buyer': self.buyer,
            'seller': self.seller,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Invoice':
        """从字典创建"""
        invoice = cls(
            invoice_number=data['invoice_number'],
            amount=data['amount'],
            invoice_type=data['type'],
            date=data.get('date'),
            buyer=data.get('buyer', ''),
            seller=data.get('seller', '')
        )
        invoice.id = data.get('id')
        invoice.created_at = data.get('created_at', datetime.now().isoformat())
        return invoice


class FinancialManager:
    """财务管理器"""

    # 交易分类
    INCOME_CATEGORIES = ['销售收入', '服务收入', '投资收益', '其他收入']
    EXPENSE_CATEGORIES = ['采购成本', '运营费用', '工资福利', '房租水电', '其他支出']

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.transactions_file = self.data_dir / 'transactions.json'
        self.invoices_file = self.data_dir / 'invoices.json'
        self.transactions = self._load_transactions()
        self.invoices = self._load_invoices()

    def _load_transactions(self) -> List[Transaction]:
        """加载交易数据"""
        if self.transactions_file.exists():
            with open(self.transactions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [Transaction.from_dict(t) for t in data]
        return []

    def _save_transactions(self):
        """保存交易数据"""
        with open(self.transactions_file, 'w', encoding='utf-8') as f:
            json.dump([t.to_dict() for t in self.transactions], f, ensure_ascii=False, indent=2)

    def _load_invoices(self) -> List[Invoice]:
        """加载发票数据"""
        if self.invoices_file.exists():
            with open(self.invoices_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [Invoice.from_dict(i) for i in data]
        return []

    def _save_invoices(self):
        """保存发票数据"""
        with open(self.invoices_file, 'w', encoding='utf-8') as f:
            json.dump([i.to_dict() for i in self.invoices], f, ensure_ascii=False, indent=2)

    def record_transaction(self, transaction_type: str, amount: float,
                          category: str, description: str = "",
                          tags: List[str] = None) -> Transaction:
        """记录交易"""
        transaction = Transaction(
            transaction_type=transaction_type,
            amount=amount,
            category=category,
            description=description,
            tags=tags
        )
        transaction.id = len(self.transactions) + 1
        self.transactions.append(transaction)
        self._save_transactions()
        return transaction

    def get_transactions(self, start_date: str = None, end_date: str = None,
                         transaction_type: str = None) -> List[Transaction]:
        """获取交易列表"""
        transactions = self.transactions

        # 按日期筛选
        if start_date:
            start = datetime.fromisoformat(start_date)
            transactions = [t for t in transactions
                          if datetime.fromisoformat(t.created_at) >= start]

        if end_date:
            end = datetime.fromisoformat(end_date + ' 23:59:59')
            transactions = [t for t in transactions
                          if datetime.fromisoformat(t.created_at) <= end]

        # 按类型筛选
        if transaction_type:
            transactions = [t for t in transactions if t.type == transaction_type]

        return transactions

    def get_balance(self, as_of: str = None) -> Dict:
        """获取余额"""
        transactions = self.get_transactions(end_date=as_of)

        income = sum(t.amount for t in transactions if t.type == 'income')
        expense = sum(t.amount for t in transactions if t.type == 'expense')
        balance = income - expense

        return {
            'income': float(income),
            'expense': float(expense),
            'balance': float(balance)
        }

    def add_invoice(self, invoice_number: str, amount: float, invoice_type: str,
                   date: str = None, buyer: str = "", seller: str = "") -> Invoice:
        """添加发票"""
        invoice = Invoice(
            invoice_number=invoice_number,
            amount=amount,
            invoice_type=invoice_type,
            date=date,
            buyer=buyer,
            seller=seller
        )
        invoice.id = len(self.invoices) + 1
        self.invoices.append(invoice)
        self._save_invoices()
        return invoice

    def get_invoices(self, invoice_type: str = None) -> List[Invoice]:
        """获取发票列表"""
        if invoice_type:
            return [i for i in self.invoices if i.type == invoice_type]
        return self.invoices

    def generate_balance_sheet(self, as_of: str = None) -> Dict:
        """生成资产负债表"""
        balance = self.get_balance(as_of)
        transactions = self.get_transactions(end_date=as_of)

        # 按分类汇总
        income_by_category = {}
        expense_by_category = {}

        for t in transactions:
            if t.type == 'income':
                income_by_category[t.category] = income_by_category.get(t.category, 0) + float(t.amount)
            elif t.type == 'expense':
                expense_by_category[t.category] = expense_by_category.get(t.category, 0) + float(t.amount)

        return {
            'as_of': as_of or datetime.now().strftime('%Y-%m-%d'),
            'assets': {
                'total': balance['income'],
                'by_category': income_by_category
            },
            'liabilities': {
                'total': balance['expense'],
                'by_category': expense_by_category
            },
            'equity': balance['balance']
        }

    def generate_income_statement(self, start_date: str, end_date: str) -> Dict:
        """生成损益表"""
        transactions = self.get_transactions(start_date, end_date)

        income = sum(t.amount for t in transactions if t.type == 'income')
        expense = sum(t.amount for t in transactions if t.type == 'expense')
        profit = income - expense

        # 按分类汇总
        income_by_category = {}
        expense_by_category = {}

        for t in transactions:
            if t.type == 'income':
                income_by_category[t.category] = income_by_category.get(t.category, 0) + float(t.amount)
            elif t.type == 'expense':
                expense_by_category[t.category] = expense_by_category.get(t.category, 0) + float(t.amount)

        return {
            'period': f"{start_date} to {end_date}",
            'revenue': {
                'total': float(income),
                'by_category': income_by_category
            },
            'expenses': {
                'total': float(expense),
                'by_category': expense_by_category
            },
            'net_income': float(profit)
        }

    def generate_cash_flow_statement(self, start_date: str, end_date: str) -> Dict:
        """生成现金流量表"""
        transactions = self.get_transactions(start_date, end_date)

        operating_inflow = sum(t.amount for t in transactions
                              if t.type == 'income' and t.category in ['销售收入', '服务收入'])
        operating_outflow = sum(t.amount for t in transactions
                               if t.type == 'expense' and t.category in ['运营费用', '工资福利'])
        net_operating = operating_inflow - operating_outflow

        return {
            'period': f"{start_date} to {end_date}",
            'operating': {
                'inflow': float(operating_inflow),
                'outflow': float(operating_outflow),
                'net': float(net_operating)
            }
        }

    def calculate_tax(self, tax_type: str = 'vat', period: str = 'month') -> Dict:
        """计算税务"""
        now = datetime.now()
        if period == 'month':
            start_date = (now.replace(day=1)).strftime('%Y-%m-%d')
            end_date = now.strftime('%Y-%m-%d')
        elif period == 'quarter':
            quarter = (now.month - 1) // 3 + 1
            start_date = datetime(now.year, (quarter - 1) * 3 + 1, 1).strftime('%Y-%m-%d')
            end_date = now.strftime('%Y-%m-%d')
        elif period == 'year':
            start_date = datetime(now.year, 1, 1).strftime('%Y-%m-%d')
            end_date = now.strftime('%Y-%m-%d')
        else:
            return {}

        transactions = self.get_transactions(start_date, end_date)
        income = sum(t.amount for t in transactions if t.type == 'income')
        expense = sum(t.amount for t in transactions if t.type == 'expense')

        if tax_type == 'vat':
            # 增值税（简化计算）
            vat_rate = 0.13  # 13%
            output_tax = float(income) * vat_rate
            input_tax = float(expense) * vat_rate
            vat_payable = max(0, output_tax - input_tax)

            return {
                'type': '增值税',
                'period': f"{start_date} to {end_date}",
                'income': float(income),
                'expense': float(expense),
                'output_tax': output_tax,
                'input_tax': input_tax,
                'vat_payable': vat_payable,
                'rate': vat_rate
            }

        elif tax_type == 'income_tax':
            # 企业所得税（简化计算）
            profit = float(income) - float(expense)
            income_tax = max(0, profit * 0.25)  # 25%税率

            return {
                'type': '企业所得税',
                'period': f"{start_date} to {end_date}",
                'revenue': float(income),
                'expenses': float(expense),
                'profit': profit,
                'income_tax': income_tax,
                'rate': 0.25
            }

        return {}

    def analyze_financials(self, period: str = 'month') -> Dict:
        """财务分析"""
        now = datetime.now()
        if period == 'month':
            start_date = (now.replace(day=1)).strftime('%Y-%m-%d')
            end_date = now.strftime('%Y-%m-%d')
        elif period == 'year':
            start_date = datetime(now.year, 1, 1).strftime('%Y-%m-%d')
            end_date = now.strftime('%Y-%m-%d')
        else:
            return {}

        transactions = self.get_transactions(start_date, end_date)

        # 收支趋势
        daily_data = {}
        for t in transactions:
            date = datetime.fromisoformat(t.created_at).strftime('%Y-%m-%d')
            if date not in daily_data:
                daily_data[date] = {'income': 0, 'expense': 0}
            if t.type == 'income':
                daily_data[date]['income'] += float(t.amount)
            elif t.type == 'expense':
                daily_data[date]['expense'] += float(t.amount)

        # 按分类统计
        category_stats = {}
        for t in transactions:
            key = f"{t.type}_{t.category}"
            if key not in category_stats:
                category_stats[key] = {'count': 0, 'amount': 0}
            category_stats[key]['count'] += 1
            category_stats[key]['amount'] += float(t.amount)

        return {
            'period': f"{start_date} to {end_date}",
            'total_transactions': len(transactions),
            'daily_trend': daily_data,
            'category_analysis': category_stats,
            'balance': self.get_balance(end_date)
        }

    def get_summary(self) -> Dict:
        """获取财务摘要"""
        balance = self.get_balance()
        total_transactions = len(self.transactions)
        total_invoices = len(self.invoices)

        # 本月数据
        now = datetime.now()
        month_start = now.replace(day=1).strftime('%Y-%m-%d')
        month_transactions = self.get_transactions(start_date=month_start)
        month_income = sum(t.amount for t in month_transactions if t.type == 'income')
        month_expense = sum(t.amount for t in month_transactions if t.type == 'expense')

        return {
            'balance': balance,
            'total_transactions': total_transactions,
            'total_invoices': total_invoices,
            'this_month': {
                'income': float(month_income),
                'expense': float(month_expense),
                'net': float(month_income - month_expense)
            }
        }

    def export_data(self, format: str = 'json', output_path: str = None) -> str:
        """导出数据"""
        data = {
            'transactions': [t.to_dict() for t in self.transactions],
            'invoices': [i.to_dict() for i in self.invoices],
            'exported_at': datetime.now().isoformat()
        }

        if output_path is None:
            output_path = os.path.join(
                self.data_dir,
                f'financial_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.{format}'
            )

        if format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        elif format == 'csv':
            import csv
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'id', 'type', 'amount', 'category', 'description', 'created_at'
                ])
                writer.writeheader()
                writer.writerows([t.to_dict() for t in self.transactions])

        return output_path


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("Usage: python financial_manager.py <command> [options]")
        print("\nCommands:")
        print("  record    - Record transaction")
        print("  list      - List transactions")
        print("  balance   - Show balance")
        print("  report    - Generate financial report")
        print("  invoice   - Manage invoices")
        print("  tax       - Calculate tax")
        print("  analyze   - Financial analysis")
        print("  summary   - Show financial summary")
        print("  export    - Export data")
        sys.exit(1)

    manager = FinancialManager()
    command = sys.argv[1]

    if command == 'record':
        transaction_type = sys.argv[sys.argv.index('--type') + 1]
        amount = float(sys.argv[sys.argv.index('--amount') + 1])
        category = sys.argv[sys.argv.index('--category') + 1]
        description = sys.argv[sys.argv.index('--description') + 1] if '--description' in sys.argv else ""
        tags = sys.argv[sys.argv.index('--tags') + 1].split(',') if '--tags' in sys.argv else None

        transaction = manager.record_transaction(transaction_type, amount, category, description, tags)
        print(f"✓ Transaction recorded: {transaction.type} {transaction.amount} - {transaction.category}")

    elif command == 'list':
        start_date = sys.argv[sys.argv.index('--from') + 1] if '--from' in sys.argv else None
        end_date = sys.argv[sys.argv.index('--to') + 1] if '--to' in sys.argv else None
        trans_type = sys.argv[sys.argv.index('--type') + 1] if '--type' in sys.argv else None

        transactions = manager.get_transactions(start_date, end_date, trans_type)
        print(f"\n📋 Transactions ({len(transactions)}):")
        for t in transactions:
            print(f"  {t.id}. {t.created_at[:10]} | {t.type:8} | {str(t.amount):10} | {t.category:15} | {t.description}")

    elif command == 'balance':
        as_of = sys.argv[sys.argv.index('--as-of') + 1] if '--as-of' in sys.argv else None
        balance = manager.get_balance(as_of)

        print(f"\n💰 Balance (as of {as_of or 'now'}):")
        print(f"  Income:    {balance['income']:10.2f}")
        print(f"  Expense:   {balance['expense']:10.2f}")
        print(f"  Balance:   {balance['balance']:10.2f}")

    elif command == 'report':
        report_type = sys.argv[sys.argv.index('--type') + 1]
        start_date = sys.argv[sys.argv.index('--from') + 1]
        end_date = sys.argv[sys.argv.index('--to') + 1]

        if report_type == 'balance':
            report = manager.generate_balance_sheet(end_date)
            print(f"\n📊 Balance Sheet (as of {report['as_of']}):")
            print(f"  Assets:   {report['assets']['total']:.2f}")
            print(f"  Liabilities: {report['liabilities']['total']:.2f}")
            print(f"  Equity:   {report['equity']:.2f}")
        elif report_type == 'income':
            report = manager.generate_income_statement(start_date, end_date)
            print(f"\n📊 Income Statement ({report['period']}):")
            print(f"  Revenue:  {report['revenue']['total']:.2f}")
            print(f"  Expenses: {report['expenses']['total']:.2f}")
            print(f"  Net Income: {report['net_income']:.2f}")
        elif report_type == 'cashflow':
            report = manager.generate_cash_flow_statement(start_date, end_date)
            print(f"\n📊 Cash Flow Statement ({report['period']}):")
            print(f"  Operating Inflow:  {report['operating']['inflow']:.2f}")
            print(f"  Operating Outflow: {report['operating']['outflow']:.2f}")
            print(f"  Net Operating:     {report['operating']['net']:.2f}")

    elif command == 'invoice':
        if '--add' in sys.argv:
            number = sys.argv[sys.argv.index('--number') + 1]
            amount = float(sys.argv[sys.argv.index('--amount') + 1])
            inv_type = sys.argv[sys.argv.index('--type') + 1]
            date = sys.argv[sys.argv.index('--date') + 1] if '--date' in sys.argv else None
            buyer = sys.argv[sys.argv.index('--buyer') + 1] if '--buyer' in sys.argv else ""
            seller = sys.argv[sys.argv.index('--seller') + 1] if '--seller' in sys.argv else ""

            invoice = manager.add_invoice(number, amount, inv_type, date, buyer, seller)
            print(f"✓ Invoice added: {invoice.invoice_number} - {invoice.amount}")
        else:
            inv_type = sys.argv[sys.argv.index('--type') + 1] if '--type' in sys.argv else None
            invoices = manager.get_invoices(inv_type)
            print(f"\n📄 Invoices ({len(invoices)}):")
            for i in invoices:
                print(f"  {i.invoice_number} | {i.type:7} | {str(i.amount):10} | {i.date}")

    elif command == 'tax':
        tax_type = sys.argv[sys.argv.index('--vat') + 1] if '--vat' in sys.argv else 'vat'
        period = sys.argv[sys.argv.index('--period') + 1] if '--period' in sys.argv else 'month'
        tax = manager.calculate_tax(tax_type, period)

        print(f"\n💰 Tax Calculation ({tax['type']}):")
        print(f"  Period: {tax['period']}")
        if tax_type == 'vat':
            print(f"  Income:    {tax['income']:.2f}")
            print(f"  Expense:   {tax['expense']:.2f}")
            print(f"  Output Tax: {tax['output_tax']:.2f}")
            print(f"  Input Tax:  {tax['input_tax']:.2f}")
            print(f"  VAT Payable: {tax['vat_payable']:.2f}")
        elif tax_type == 'income_tax':
            print(f"  Revenue:   {tax['revenue']:.2f}")
            print(f"  Expenses:  {tax['expenses']:.2f}")
            print(f"  Profit:    {tax['profit']:.2f}")
            print(f"  Income Tax: {tax['income_tax']:.2f}")

    elif command == 'analyze':
        period = sys.argv[sys.argv.index('--period') + 1] if '--period' in sys.argv else 'month'
        analysis = manager.analyze_financials(period)

        print(f"\n📈 Financial Analysis ({analysis['period']}):")
        print(f"  Total Transactions: {analysis['total_transactions']}")
        print(f"  Current Balance: {analysis['balance']['balance']:.2f}")
        print(f"\n  Category Analysis:")
        for key, stats in analysis['category_analysis'].items():
            print(f"    {key}: {stats['amount']:.2f} ({stats['count']} transactions)")

    elif command == 'summary':
        summary = manager.get_summary()

        print(f"\n📊 Financial Summary:")
        print(f"  Current Balance: {summary['balance']['balance']:.2f}")
        print(f"  Total Transactions: {summary['total_transactions']}")
        print(f"  Total Invoices: {summary['total_invoices']}")
        print(f"\n  This Month:")
        print(f"    Income:  {summary['this_month']['income']:.2f}")
        print(f"    Expense: {summary['this_month']['expense']:.2f}")
        print(f"    Net:     {summary['this_month']['net']:.2f}")

    elif command == 'export':
        format_type = sys.argv[sys.argv.index('--format') + 1] if '--format' in sys.argv else 'json'
        output = sys.argv[sys.argv.index('--output') + 1] if '--output' in sys.argv else None
        path = manager.export_data(format_type, output)
        print(f"✓ Data exported to: {path}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
