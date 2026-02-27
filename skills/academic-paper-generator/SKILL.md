# Academic Paper Generator - 学术论文生成器

## 功能描述

这是一个全自动学术论文生成系统，可以根据项目代码或研究主题自主生成符合arXiv标准的完整论文，包括：

- 自动分析代码库和研究内容
- 生成LaTeX格式的学术论文（符合arXiv标准）
- 自动创建高质量图表（架构图、结果图、对比图等）
- 自动生成摘要、引言、方法、实验、结论等完整章节
- 支持引用管理（BibTeX）
- 支持公式、算法、表格
- 可生成PDF最终版本

## 使用方式

### 基本用法

```bash
# 从代码库生成论文
python paper_generator.py --source /path/to/project --title "研究标题"

# 从主题生成论文
python paper_generator.py --topic "深度学习在图像识别中的应用" --type review

# 从项目描述生成
python paper_generator.py --describe "项目描述" --data results.csv
```

### 高级用法

```bash
# 完整定制
python paper_generator.py \
  --source /path/to/project \
  --title "论文标题" \
  --authors "作者1,作者2" \
  --type conference \
  --venue "NeurIPS 2026" \
  --results /path/to/results \
  --figures \
  --bibliography refs.bib \
  --output paper.pdf
```

## 输入参数

| 参数 | 说明 | 必填 |
|------|------|------|
| --source | 项目代码路径 | 否 |
| --topic | 研究主题 | 否 |
| --title | 论文标题 | 是 |
| --authors | 作者列表（逗号分隔） | 否 |
| --abstract | 摘要内容 | 否 |
| --type | 论文类型（conference/journal/review/tech） | 否 |
| --venue | 发表场所 | 否 |
| --results | 实验结果数据路径 | 否 |
| --figures | 是否自动生成图表 | 否 |
| --bibliography | 参考文献文件 | 否 |
| --output | 输出PDF路径 | 否 |
| --template | LaTeX模板路径 | 否 |

## 输出内容

1. **main.tex** - 主论文文件（LaTeX格式）
2. **figures/** - 自动生成的图表目录
   - architecture.pdf - 系统架构图
   - results.pdf - 实验结果图
   - comparison.pdf - 对比分析图
3. **references.bib** - 参考文献文件
4. **paper.pdf** - 最终PDF论文
5. **metadata.json** - 论文元数据

## 支持的论文类型

- **conference** - 会议论文（NeurIPS, ICML, ICLR等）
- **journal** - 期刊论文（Nature, Science, JMLR等）
- **review** - 综述论文
- **tech** - 技术报告
- **workshop** - 研讨会论文

## 自动生成的章节

1. **Title Page** - 标题页（标题、作者、单位、日期）
2. **Abstract** - 摘要（自动总结研究内容）
3. **Introduction** - 引言（研究背景、动机、贡献）
4. **Related Work** - 相关工作（自动检索相关文献）
5. **Methodology** - 方法论（系统架构、算法设计）
6. **Experiments** - 实验（实验设计、数据集、设置）
7. **Results** - 结果（实验结果、图表分析）
8. **Discussion** - 讨论（结果解读、局限性）
9. **Conclusion** - 结论（总结、未来工作）
10. **References** - 参考文献

## 图表生成能力

### 架构图
- 系统架构图
- 模块关系图
- 数据流图
- 类图/流程图

### 结果图
- 折线图（性能曲线）
- 柱状图（对比分析）
- 散点图（相关性分析）
- 热力图（混淆矩阵）
- 箱线图（统计分布）

### 表格
- 实验结果表
- 对比分析表
- 参数配置表
- 消融实验表

## LaTeX模板

支持多种模板：
- ACL会议模板
- NeurIPS模板
- ICML模板
- IEEE模板
- 自定义模板

## 依赖项

- Python 3.8+
- LaTeX (TeX Live / MacTeX)
- Python包：
  - matplotlib（图表生成）
  - networkx（架构图）
  - pandas（数据处理）
  - plotly（交互式图表）
  - jinja2（模板渲染）
  - pygments（代码高亮）

## 工作流程

1. **分析阶段**
   - 扫描项目代码结构
   - 识别核心功能和算法
   - 提取关键信息和数据

2. **内容生成**
   - 生成论文各章节内容
   - 分析代码生成方法论
   - 整合研究结果

3. **图表生成**
   - 绘制系统架构图
   - 生成实验结果图表
   - 创建对比分析图

4. **文献检索**
   - 搜索相关研究领域
   - 生成BibTeX引用
   - 整合相关工作

5. **LaTeX编译**
   - 生成完整LaTeX源码
   - 编译生成PDF
   - 质量检查和优化

## 示例输出

```latex
\documentclass{article}
\title{Deep Learning for Image Recognition: A Novel Approach}
\author{Your Name}
\date{\today}

\begin{document}
\maketitle

\begin{abstract}
This paper presents...
\end{abstract}

\section{Introduction}
...
\end{document}
```

## 质量保证

- 自动检查LaTeX语法
- 图表分辨率优化（300+ DPI）
- 引用格式验证
- PDF编译错误处理
- 内容逻辑性检查

## 使用场景

1. **从代码库生成论文** - 给我一个项目路径，自动生成完整论文
2. **从实验数据生成** - 给我结果数据，自动分析和可视化
3. **从研究主题生成** - 给我一个主题，自动撰写综述
4. **论文草稿生成** - 快速生成初稿，然后人工修改

## 高级功能

- **多版本生成** - 同时生成会议版、期刊版、技术报告版
- **自动翻译** - 生成中英文双语版本
- **版本对比** - 生成版本差异报告
- **提交准备** - 生成arXiv提交包

## 注意事项

1. 生成的论文是初稿，需要人工审核和修改
2. 图表需要根据实际调整样式和颜色
3. 参考文献需要补充完整和验证
4. 学术诚信：确保内容原创性，正确引用
5. 建议在使用前进行同行评议

## 扩展性

可以集成：
- 自动化实验结果收集
- Git历史分析（展示开发历程）
- 性能基准测试
- 代码覆盖率分析
- 文档生成整合

## 许可和引用

使用本技能生成的论文，请适当引用工具。

## 技术栈

- Python 3.8+
- LaTeX (XeLaTeX/LuaLaTeX)
- Matplotlib/Seaborn（可视化）
- Networkx（架构图）
- Pandas（数据处理）
- Jinja2（模板引擎）
