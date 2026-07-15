---
type: skill_index
note_id: infra-skill-index
created: 2026-05-18
status: active
---

# SKILL_INDEX.md — 学术 Skill 索引与桥接表

本文件只做路由：遇到学术任务时，先用这里确定该读哪个实体 skill。

实体 skill 不存放在本目录。根目录见 `SKILL_ROOTS.md`：

- Claude Code 主源：`C:\Users\admin\.claude\skills`
- Codex 原生目录：`C:\Users\admin\.codex\skills`

状态含义：

- **Claude: yes**：存在 `C:\Users\admin\.claude\skills\<skill>\SKILL.md`
- **Codex: yes**：存在 `C:\Users\admin\.codex\skills\<skill>\SKILL.md`，可作为 Codex 原生 skill 触发
- **Codex: bridge**：Codex 未原生安装，但可按 Claude 路径读取

## 快速路由

| 用户意图 | 首选 skill |
|---|---|
| 选题、找 gap、定位贡献 | `research-ideation` / `research-gap-diagnosis` / `dgm-research-positioning` |
| 读文献、做 Obsidian 笔记 | `literature-notes-obsidian` / `literature-review` / `articlefeed` |
| 引用、BibTeX、Zotero | `citation-management` / `zotero-cli-cc` |
| 理论构建、假设发展 | `write-theory` / `write-theory-and-hypotheses` / `hypothesis-generation` |
| 研究设计、因果识别 | `empirical-intake` / `causal-analysis` / `did-analysis` |
| 产品召回数据基础设施 | `s01-recall-data-infrastructure` |
| Stata 清洗、回归、表格 | `stata` / `stata-data-cleaning` / `stata-regression` |
| 实证执行流水线(现代交错 DiD + 稳健性箱 + 机制 + 召回时机) | `empirical-pipeline-stata` |
| 规格搜索/口径变换(既定问题下试到稳健或显著,纪律版) | `xianzhu-skill` |
| 写论文 section | `write-introduction` / `write-methods` / `write-results` / `write-discussion` |
| 审查论文质量 | `paper-review` / `pollock-qc` / `*-review` |
| 审稿回复/R&R(解析意见→修改路线图→回复信;或回复体检) | `revision-coach` |
| 投稿 AI 使用声明(按期刊政策) | `ai-disclosure` |
| 去除 AI 味、润色 | `humanizer` / `proofread` |
| 幻灯片、PDF、文档转换 | `slides` / `beamer-presentation` / `pdf` / `markitdown` |

## 论文生产流水线

### 1. 选题与定位

| Skill | 触发场景 | 输出 | Claude | Codex |
|---|---|---|---|---|
| `research-ideation` | brainstorm 研究问题、选题、找角度 | 研究问题列表 + 可行性评估 | yes | bridge |
| `dgm-research-positioning` | 已有文献笔记，需要定位 gap | 候选 gap、贡献声明、论文标题 | yes | yes |
| `research-gap-diagnosis` | 诊断现有项目的 gap 强度 | Gap 类型、Makadok 维度、Hook 建议 | yes | bridge |
| `empirical-intake` | 拿到数据但不知道怎么分析 | 研究设计简报、识别策略、变量清单 | yes | yes |
| `hypothesis-generation` | 有观察需要形成可检验假设 | 假设、机制、预测、实验设计 | yes | yes |

### 2. 文献与引用

| Skill | 触发场景 | 输出 | Claude | Codex |
|---|---|---|---|---|
| `literature-review` | 系统文献综述、找相关论文 | 结构化综述文档 + 引用 | yes | yes |
| `literature-notes-obsidian` | 读单篇 PDF/DOI，做文献笔记 | Vault-ready 文献笔记 | yes | yes |
| `articlefeed` | 持续追踪新文献、管理阅读流 | 推荐列表 + 阅读进度 | yes | yes |
| `citation-management` | 验证引用、生成 BibTeX | 标准格式引用 | yes | yes |
| `zotero-cli-cc` | 任何涉及 Zotero 的操作 | 文献检索、导出、RAG | yes | bridge |

### 3. 理论与研究设计

| Skill | 触发场景 | 输出 | Claude | Codex |
|---|---|---|---|---|
| `write-theory` | 写或修改 Theory & Hypotheses | 构念界定、机制推演、假设模板 | yes | bridge |
| `write-theory-and-hypotheses` | Theory 部分被批评 under-theorized | 重写后的理论段落 | bridge | yes |
| `causal-analysis` | 设计或审查因果推断策略 | 方法选择建议、robustness 计划 | yes | yes |
| `did-analysis` | 现代 DID 分析 | 估计器选择、平行趋势、安慰剂 | yes | bridge |

### 4. 实证执行

| Skill | 触发场景 | 输出 | Claude | Codex |
|---|---|---|---|---|
| `s01-recall-data-infrastructure` | 产品召回项目数据基础设施搭建 | recall timing 数据骨架 + 变量定义 | yes | yes |
| `stata-regression` | 跑回归、输出表格 | Stata 代码 + 结果表格 | yes | bridge |
| `stata-data-cleaning` | 数据清洗、变量构建 | 可复现 do-file | yes | bridge |
| `stata` | Stata 语法、调试、高级功能 | 代码示例 + 解释 | yes | bridge |
| `econometrics-agent` | 调用本地 econometrics-agent CLI | 结构化回归输出、叙事总结 | yes | yes |
| `python-panel-data` | Python 面板数据分析 | pandas/linearmodels 代码 | yes | bridge |
| `ml-analysis` | ML 预测、分类、特征工程 | 模型比较、解释、稳健性 | yes | yes |
| `latex-tables` | 回归结果转 LaTeX 表格 | `.tex` 表格代码 | yes | bridge |
| `latex-econ-model` | 写理论模型的 LaTeX 公式 | 数学排版 | yes | bridge |

### 5. 写作与质量控制

| Skill | 触发场景 | 输出 | Claude | Codex |
|---|---|---|---|---|
| `write-introduction` | 写或改 Introduction | 引言模块和段落草稿 | yes | bridge |
| `write-methods` | 写或改 Methods | 方法段落模板和 prose | yes | bridge |
| `write-results` | 写或改 Results | 假设-结果节奏模板 | yes | bridge |
| `write-discussion` | 写或改 Discussion | 贡献类型和讨论结构 | yes | bridge |
| `write-discussion-and-conclusion` | Discussion 或 conclusion 被批评 weak | 重写后的讨论/结论段落 | bridge | yes |
| `paper-review` | 全稿总控审查 | 最薄弱 section 诊断 + 路由 | yes | bridge |
| `intro-review` | Introduction 专项审查 | Hook/Gap/贡献预告检查 | yes | bridge |
| `theory-review` | Theory 专项审查 | 构念清晰度/why-chain 检查 | yes | bridge |
| `methods-review` | Methods 专项审查 | 三 C 标准评分 | yes | bridge |
| `results-review` | Results 专项审查 | 假设完整性/稳健性组织检查 | yes | bridge |
| `discussion-review` | Discussion 专项审查 | 贡献对齐/局限性检查 | yes | bridge |
| `pollock-qc` | 投稿前快速健康检查 | 结构化评分表 + 修复优先级 | yes | bridge |
| `humanizer` | 去除 AI 写作痕迹 | 自然化改写 | yes | yes |
| `proofread` | 语法、风格、清晰度校对 | 修改建议 | yes | bridge |
| `empirical-writeup` | 分析输出转为期刊 prose | Methods/Results/图表文字 | yes | yes |
| `paper-writing-stack` | 不知道先改哪个 section | 修改顺序建议 + bottleneck 诊断 | yes | yes |

### 6. 范文蒸馏

| Skill | 触发场景 | 输出 | Claude | Codex |
|---|---|---|---|---|
| `distill-introduction-exemplar` | 分析优秀论文的 Intro 结构 | 功能模块拆解 + 表达 DNA | yes | bridge |
| `distill-theory-exemplar` | 分析优秀论文的 Theory 结构 | why-chain 模式 + 组织方式 | yes | bridge |
| `distill-methods-exemplar` | 分析优秀论文的 Methods 结构 | 段落骨架 + 可迁移范式 | yes | bridge |
| `distill-results-exemplar` | 分析优秀论文的 Results 结构 | 证据组织节奏 + 说服逻辑 | yes | bridge |

### 7. 展示与辅助

| Skill | 触发场景 | 输出 | Claude | Codex |
|---|---|---|---|---|
| `beamer-presentation` | 学术报告/会议幻灯片 | `.tex` Beamer 文件 | yes | bridge |
| `slides` | 一般幻灯片或 PPTX | `.pptx` 文件 | yes | yes |
| `markitdown` | 文档转 Markdown | `.md` 文件 | yes | yes |
| `pdf` | PDF 操作、读取、检查 | 渲染/提取结果 | yes | yes |
| `baoyu-translate` | 中英文学术翻译 | 翻译稿 | yes | bridge |

### 8. 其他专业工具

| Skill | 触发场景 | Claude | Codex |
|---|---|---|---|
| `meeting-minutes` | 整理会议纪要 | yes | bridge |
| `stata-c-plugins` | 开发 Stata C/C++ 插件 | yes | bridge |
| `jupyter-notebook` | 创建/编辑 Jupyter notebook | yes | yes |
| `exploratory-data-analysis` | 科学数据文件 EDA | yes | yes |
| `rednote-to-obsidian` | 小红书/RedNote 转 Obsidian | yes | yes |
| `smart-search` | 多网站智能搜索 | yes | bridge |

## 桥接读取规则

当 Codex 状态是 `bridge` 时，按以下方式处理：

1. 优先检查当前会话的 Codex skill 列表是否已有同名或等价 skill。
2. 如果没有，直接读取 `C:\Users\admin\.claude\skills\<skill>\SKILL.md`。
3. 只读取完成任务所需的 reference/script，不批量展开整个 skill 目录。
4. 若该 skill 会频繁用于 Codex 会话，再同步到 `C:\Users\admin\.codex\skills` 并把状态改为 `yes`。

## 维护规则

- 本目录不保存完整 skill 内容。
- 新增或重写 skill 时，先改实体 skill，再更新本索引。
- Claude 和 Codex 行只记录安装状态，不代表两个版本内容完全一致。
- 定期用目录扫描检查本索引是否与两个 skill root 一致。
