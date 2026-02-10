# 智能财务管理系统 (Smart Financial Manager)

智能化财务管理工具，提供财务记账、发票管理、报表生成、财务分析、税务计算等全面财务管理解决方案。

## 功能特性

- 财务记账（收入/支出/转账记录）
- 自动分类（智能识别交易类型）
- 发票管理（发票录入、存储、查询）
- 财务报表（资产负债表、损益表、现金流量表）
- 财务分析（收支分析、趋势分析、预算管理）
- 税务计算（增值税、企业所得税计算）
- 数据导入导出
- 数据持久化
- 命令行接口

## 安装依赖

```bash
pip install openpyxl
```

## 使用方法

### 命令行接口

```bash
# 记账
python financial_manager.py record --type income --amount 10000 --category "销售收入" --description "产品销售"

# 查看账目
python financial_manager.py list --from 2026-01-01 --to 2026-02-01

# 生成报表
python financial_manager.py report --type balance --from 2026-01-01 --to 2026-01-31

# 发票管理
python financial_manager.py invoice --add --number "12345" --amount 5000

# 税务计算
python financial_manager.py tax --vat

# 财务分析
python financial_manager.py analyze --period month
```

## 核心价值

**对赚钱目标的贡献：**
1. **代理记账服务**：为企业提供代理记账服务
2. **发票管理服务**：发票开具和管理
3. **财务报表服务**：自动生成财务报表
4. **财务分析服务**：提供财务数据分析
5. **税务筹划辅助**：税务计算和申报建议

**赚钱方式：**
- 代理记账：月500-2000元/公司（月5000-30000元，10-15家公司）
- 发票管理：按票数计费，每张2-10元（月3000-15000元）
- 报表生成：月1000-5000元
- 财务分析：月3000-15000元
- 税务筹划：按服务计费，每次500-5000元（月3000-20000元）

**预期收益：** 月15000-85000元
