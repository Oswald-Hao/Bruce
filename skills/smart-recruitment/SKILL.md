# 智能招聘系统 (Smart Recruitment System)

智能化的招聘管理系统，提供简历筛选、面试安排、人才匹配、招聘流程管理等全流程招聘解决方案。

## 功能特性

- 简历解析和入库（PDF/Word/文本）
- 智能简历筛选（关键词、技能匹配、经验匹配）
- 候选人评分和排名
- 自动面试安排（时间协调、日历集成）
- 面试反馈管理
- 人才库管理（标签、分类、搜索）
- 招聘数据分析（漏斗分析、渠道分析、效率分析）
- 招聘流程跟踪
- 数据持久化
- 命令行接口

## 安装依赖

```bash
pip install PyPDF2 python-docx openpyxl
```

## 使用方法

### 命令行接口

```bash
# 添加候选人
python smart_recruitment.py add-candidate --name "张三" --resume "/path/to/resume.pdf" --position "Python开发工程师"

# 搜索候选人
python smart_recruitment.py search --keyword "Python" --min-experience 3

# 面试评分
python smart_recruitment.py rate --id 1 --round "技术面" --score 85 --feedback "技术基础扎实"

# 招聘数据统计
python smart_recruitment.py stats --period month

# 管理面试安排
python smart_recruitment.py schedule --id 1 --datetime "2026-02-15 14:00" --round "HR面" --interviewer "李四"

# 查看人才库
python smart_recruitment.py talent-pool --tag "Python"
```

## 核心价值

**对赚钱目标的贡献：**
1. **代招聘服务**：为企业筛选简历、安排面试，按成功入职收费
2. **招聘SaaS平台**：提供智能招聘管理系统订阅服务
3. **人才库服务**：为企业建立和维护人才库
4. **猎头服务**：高端人才推荐和猎头服务

**赚钱方式：**
- 代招聘服务：按成功入职计费，月薪的20-30%（月10000-50000元）
- 招聘SaaS订阅：月5000-20000元（50-200个企业用户）
- 人才库服务：月3000-15000元
- 猎头服务：月薪的25-35%（月15000-60000元）

**预期收益：** 月33000-145000元
