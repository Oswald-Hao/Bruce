# 📄 PDF论文生成器 - 直接生成PDF

## ✨ 特点

- ✅ **直接生成PDF** - 不需要LaTeX
- ✅ **自动生成图表** - 高质量PNG图表
- ✅ **完整论文结构** - 符合学术标准
- ✅ **简单易用** - 一条命令搞定

## 🚀 快速开始

### 最简单的用法

```bash
python3 /home/lejurobot/clawd/skills/academic-paper-generator/pdf_generator.py \
    --title "你的论文标题" \
    --authors "作者名字"
```

### 完整示例

```bash
python3 /home/lejurobot/clawd/skills/academic-paper-generator/pdf_generator.py \
    --title "Deep Learning for Image Recognition" \
    --authors "AI Research Lab, University" \
    --figures \
    --output-dir ./my_paper
```

## 📝 输出内容

生成后会得到：

```
my_paper/
├── paper.pdf          # 📄 完整的PDF论文（直接可用）
└── figures/           # 📊 高质量图表（PNG格式）
    ├── results.png
    └── comparison.png
```

## 📋 PDF论文结构

生成的PDF包含：

1. ✅ 标题页（标题、作者、日期）
2. ✅ 摘要
3. ✅ 引言（研究背景、主要贡献）
4. ✅ 相关工作
5. ✅ 方法论
6. ✅ 实验（设置、基线）
7. ✅ 结果（表格 + 图表）
8. ✅ 讨论
9. ✅ 结论
10. ✅ 参考文献

## 🎨 自动生成的图表

- 📊 **results.png** - 实验结果曲线图
- 📊 **comparison.png** - 性能对比柱状图

所有图表都是300 DPI高分辨率。

## 💡 使用场景

### 场景1: 快速生成论文

```bash
python3 /home/lejurobot/clawd/skills/academic-paper-generator/pdf_generator.py \
    --title "My Research Paper" \
    --authors "Your Name"
```

**得到：** 完整的PDF论文，可以直接打印或提交！

### 场景2: 生成带图表的论文

```bash
python3 /home/lejurobot/clawd/skills/academic-paper-generator/pdf_generator.py \
    --title "Experimental Analysis" \
    --authors "Research Team" \
    --figures
```

**得到：** 包含2个高质量图表的PDF论文

### 场景3: 自定义输出目录

```bash
python3 /home/lejurobot/clawd/skills/academic-paper-generator/pdf_generator.py \
    --title "Custom Paper" \
    --authors "Author" \
    --output-dir ~/Documents/papers/my_paper
```

## 📊 实际效果

刚刚测试生成了：

**文件大小：** 353.4 KB
**页数：** 约7-8页
**格式：** PDF（使用ReportLab生成）
**图表：** 2个高质量PNG图表

## 🔧 参数说明

| 参数 | 说明 | 必填 | 默认值 |
|------|------|------|--------|
| --title | 论文标题 | ✅ 是 | 无 |
| --authors | 作者列表 | ❌ 否 | Unknown Author |
| --type | 论文类型 | ❌ 否 | conference |
| --figures | 生成图表 | ❌ 否 | True |
| --output-dir | 输出目录 | ❌ 否 | paper_output |

## ⚙️ 技术细节

**PDF生成库：** ReportLab
**图表生成：** Matplotlib
**无需安装：** LaTeX（TeX Live等）
**依赖项：** Python 3 + reportlab + matplotlib + pandas

## 🆚 对比：LaTeX vs PDF生成器

| 功能 | LaTeX版本 | PDF生成器 |
|------|-----------|-----------|
| 输出格式 | .tex源码 | ✅ .pdf直接 |
| 需要LaTeX | ✅ 是 | ✅ 否 |
| 生成PDF | 需要编译 | ✅ 直接得到 |
| 图表格式 | PDF | PNG |
| 学术标准 | IEEE/arXiv | 通用格式 |
| 易用性 | 需要学习 | ✅ 超简单 |

## 🎯 适合谁使用

### 适合使用PDF生成器：
- ✅ 快速需要PDF论文
- ✅ 不想安装LaTeX
- ✅ 不需要投稿会议/期刊
- ✅ 简单作业/报告

### 适合使用LaTeX版本：
- ❌ 投稿顶级会议（NeurIPS等）
- ❌ 提交arXiv
- ❌ 需要精确格式控制
- ❌ 需要复杂公式

## 📖 完整示例

### 示例1: 基本论文

```bash
python3 /home/lejurobot/clawd/skills/academic-paper-generator/pdf_generator.py \
    --title "A Simple Paper" \
    --authors "John Doe"
```

### 示例2: 完整论文

```bash
python3 /home/lejurobot/clawd/skills/academic-paper-generator/pdf_generator.py \
    --title "Deep Learning in Computer Vision" \
    --authors "AI Research Lab, University of Science" \
    --type journal \
    --figures \
    --output-dir ~/Documents/papers/dl_paper
```

### 示例3: 团队论文

```bash
python3 /home/lejurobot/clawd/skills/academic-paper-generator/pdf_generator.py \
    --title "Team Research Results" \
    --authors "Alice, Bob, Charlie" \
    --figures \
    --output-dir ./team_paper
```

## 📞 使用帮助

有问题？

1. **查看PDF：** 用任何PDF阅读器打开
2. **修改内容：** 编辑.py源码中的文本
3. **自定义样式：** 修改样式设置

## 🎉 开始使用

```bash
python3 /home/lejurobot/clawd/skills/academic-paper-generator/pdf_generator.py \
    --title "你的论文标题" \
    --authors "你的名字"
```

就这么简单！🎊

---

**两种版本：**
1. **LaTeX版本** (`paper_generator.py`) - 用于学术投稿
2. **PDF生成器** (`pdf_generator.py`) - 快速生成PDF ✅

选择你需要的版本！
