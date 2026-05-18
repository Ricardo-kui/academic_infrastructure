---
type: skill_index
note_id: infra-skill-index
created: 2026-05-18
status: active
---

# SKILL_INDEX.md — 学术研究技能总索引

本索引 catalog 当前安装的所有 Claude Code 技能，按研究流水线组织。
遇到"怎么做X"时，先查本索引找到对应 skill，再执行。

## 论文生产流水线（前端 → 中端 → 后端 → 横向）

### 1. 选题与定位（Ideation & Positioning）

| Skill | 触发场景 | 输出 |
|-------|---------|------|
| `research-ideation` | brainstorm研究问题、选题、找角度 | 研究问题列表 + 可行性评估 |
| `dgm-research-positioning` | 已有文献笔记，需要定位gap | 候选gap、贡献声明、论文标题 |
| `research-gap-diagnosis` | 诊断现有项目的gap强度 | Gap类型、Makadok维度、Hook建议 |
| `empirical-intake` | 拿到数据但不知道怎么分析 | 研究设计简报、识别策略、变量清单 |
| `hypothesis-generation` | 有观察需要形成可检验假设 | 假设、机制、预测、实验设计 |

### 2. 文献与 intake（Literature & Intake）

| Skill | 触发场景 | 输出 |
|-------|---------|------|
| `literature-review` | 系统文献综述、找相关论文 | 结构化综述文档 + 引用 |
| `literature-notes-obsidian` | 读单篇PDF/DOI，做文献笔记 | Vault-ready 文献笔记 |
| `articlefeed` | 持续追踪新文献、管理阅读流 | 推荐列表 + 阅读进度 |
| `citation-management` | 验证引用、生成BibTeX | 标准格式引用 |
| `zotero-cli-cc` | 任何涉及Zotero的操作 | 文献检索、导出、RAG |

### 3. 理论与设计（Theory & Design）

| Skill | 触发场景 | 输出 |
|-------|---------|------|
| `write-theory` | 写/改 Theory & Hypotheses | 构念界定、机制推演、假设模板 |
| `write-theory-and-hypotheses` | Theory部分被批评under-theorized | 重写后的理论段落 |
| `causal-analysis` | 设计或审查因果推断策略 | 方法选择建议、robustness计划 |
| `did-analysis` | 现代DiD分析（R为主，概念通用） | 估计器选择、平行趋势、安慰剂 |

### 4. 实证执行（Empirical Execution）

| Skill | 触发场景 | 输出 |
|-------|---------|------|
| `stata-regression` | 跑回归、输出表格 | Stata代码 + 结果表格 |
| `stata-data-cleaning` | 数据清洗、变量构建 | 可复现的do文件 |
| `stata` | Stata语法、调试、高级功能 | 代码示例 + 解释 |
| `econometrics-agent` | 调用本地econometrics-agent CLI | 结构化回归输出、叙事总结 |
| `python-panel-data` | Python面板数据分析 | pandas/linearmodels代码 |
| `ml-analysis` | ML预测、分类、特征工程 | 模型比较、解释、稳健性 |
| `latex-tables` | 把回归结果转为LaTeX表格 | .tex表格代码 |
| `latex-econ-model` | 写理论模型的LaTeX公式 | 数学排版 |

### 5. 写作与质量控制（Writing & QC）

| Skill | 触发场景 | 输出 |
|-------|---------|------|
| `write-introduction` | 写/改 Introduction | 模块组装式引言骨架 |
| `write-methods` | 写/改 Methods | 填空式段落模板 |
| `write-results` | 写/改 Results | 假设-结果节奏模板 |
| `write-discussion` | 写/改 Discussion | 五种贡献类型的结构建议 |
| `write-discussion-and-conclusion` | Discussion被批评weak | 重写后的讨论段落 |
| `paper-review` | 全稿总控审查 | 最薄弱section诊断 + 路由 |
| `intro-review` | Introduction专项审查 | Hook/Gap/贡献预告检查 |
| `theory-review` | Theory专项审查 | 构念清晰度/why chain检查 |
| `methods-review` | Methods专项审查 | 三C标准评分 |
| `results-review` | Results专项审查 | 假设完整性/稳健性组织检查 |
| `discussion-review` | Discussion专项审查 | 贡献对齐/局限性检查 |
| `pollock-qc` | 投稿前快速健康检查 | 结构化评分表 + 修复优先级 |
| `humanizer` | 去除AI写作痕迹 | 自然化改写 |
| `proofread` | 语法、风格、清晰度校对 | 修改建议 |
| `empirical-writeup` | 把分析输出转为期刊 prose | Methods/Results/图表文字 |
| `paper-writing-stack` | 不知道先改哪个section | 修改顺序建议 + bottleneck诊断 |

### 6. 范文蒸馏（Exemplar Distillation）

| Skill | 触发场景 | 输出 |
|-------|---------|------|
| `distill-introduction-exemplar` | 分析优秀论文的Intro结构 | 功能模块拆解 + 表达DNA |
| `distill-theory-exemplar` | 分析优秀论文的Theory结构 | why-chain模式 + 论证组织方式 |
| `distill-methods-exemplar` | 分析优秀论文的Methods结构 | 段落骨架 + 可迁移范式 |
| `distill-results-exemplar` | 分析优秀论文的Results结构 | 证据组织节奏 + 说服逻辑 |

### 7. 展示与辅助（Presentation & Tools）

| Skill | 触发场景 | 输出 |
|-------|---------|------|
| `beamer-presentation` | 学术报告/会议幻灯片（LaTeX） | .tex Beamer文件 |
| `slides` | 一般幻灯片（PPTX） | .pptx文件 |
| `markitdown` | 文档转Markdown | .md文件 |
| `pdf` | PDF操作（读、创建、检查） | 渲染/提取结果 |
| `baoyu-translate` | 中英文学术翻译 | 翻译稿 |

### 8. 其他专业工具

| Skill | 触发场景 |
|-------|---------|
| `meeting-minutes` | 整理会议纪要（政府/国企风格） |
| `stata-c-plugins` | 开发Stata C/C++插件 |
| `jupyter-notebook` | 创建/编辑Jupyter笔记本 |
| `exploratory-data-analysis` | 科学数据文件的全面EDA |
| `rednote-to-obsidian` | 小红书笔记转Obsidian |
| `smart-search` | 多网站智能搜索 |
| `opencli-*` | 网站CLI交互（多种子skill） |

## 快速路由决策树

```
用户意图是...?
├── 选题/找gap/定位 → research-ideation / research-gap-diagnosis / dgm-research-positioning
├── 读文献/做笔记 → literature-notes-obsidian / zotero-cli-cc / articlefeed
├── 设计研究/识别策略 → empirical-intake / causal-analysis / did-analysis
├── 跑回归/写代码 → stata-regression / stata-data-cleaning / econometrics-agent
├── 写论文section → write-* (按section选择) / paper-writing-stack
├── 审查/修改论文 → *-review / pollock-qc / paper-review
├── 学习范文结构 → distill-*-exemplar
├── 去除AI味 → humanizer / proofread
└── 其他 → 查上表或问用户
```

## 更新规则

- 安装新skill时，按分类添加到上表
-  skill功能变更时，同步更新description
- 本索引版本号随重大变更更新
