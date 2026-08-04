---
type: axiom_index
note_id: infra-axiom-index
created: 2026-05-18
status: active
---

# Axiom Index — 学术公理库索引

> **两类公理，两种角色：**
> - 🏛 **教科书护栏**（`source: textbook`）：来自 Makadok、Edmans、Pollock 等方法论文献——任何合格管理学研究者都应遵循。作用是防止 AI 犯低级错误。
> - 🧠 **数据蒸馏**（`source: distilled`）：从用户真实的跨项目决策中提取——只有这个研究者才会这么做的原则。作用是将个人研究风格编码为可执行的规则。
>
> 两类都有价值。前者保证下限，后者提高上限。商学论文决策低频高 stakes，蒸馏速度天然慢（目标：每年 5-10 条新增），**这是正常的，不是系统故障。**

## 分类体系

| 前缀 | 类别 | 触发场景 |
|------|------|----------|
| `t*` | Theory & Contribution | 理论构建、贡献定位、gap诊断 |
| `e*` | Empirical & Identification | 研究设计、识别策略、稳健性检验 |
| `w*` | Writing & Rhetoric | 论文写作、段落诊断、AI味去除 |
| `p*` | Project Management | 项目推进、投稿策略、审稿回复 |

## 公理列表

### t* — Theory & Contribution

- 🏛 **t01_gap_must_be_genuine.md** — 贡献必须落在Makadok八维度的至少一个，且必须具体说明改变了什么
- 🏛 **t02_problematization_not_gap_spotting.md** — Gap-spotting不是贡献，problematization才是
- 🏛 **t03_so_what_who_cares.md** — 如果不改变读者的prior，就不是贡献
- 🏛 **t04_mechanism_must_penetrates_blackbox.md** — 机制解释必须穿透黑箱
- 🏛 **t05_boundary_conditions_are_not_afterthoughts.md** — 边界条件是理论精确化的核心工具
- 🏛 **t06_conditionalize_theoretical_frameworks.md** — 二元对立框架应转化为条件化框架 [provisional]
- 🧠 **t07_conditionalize_before_main_effect.md** — 条件化框架优先于单向主效应 [distilled: 四项目交叉验证, 2026-05-25]

### e* — Empirical & Identification

- 🏛 **e01_natural_experiment_first.md** — 识别策略可信度优先于系数显著性
- 🏛 **e02_data_is_not_evidence.md** — Data ≠ Evidence；显著系数≠可信发现
- 🏛 **e03_construct_measure_alignment.md** — 构念-测量对齐是方法可信度第一道门槛
- 🏛 **e04_robustness_must_cover_selection_and_measurement.md** — 稳健性检验必须覆盖两大威胁
- 🏛 **e05_parallel_trends_need_graph_and_placebo.md** — 平行趋势需要图形+安慰剂双重支撑
- 🧠 **e06_data_infrastructure_decision_tradeoff.md** — 精度降级必须声明 [distilled: FAERS/MAUDE 真实决策, 2026-07-27]

### w* — Writing & Rhetoric

- 🏛 **w01_introduction_is_jobs_to_be_done.md** — 引言是Jobs to Be Done，不是文献空白展示
- 🏛 **w02_one_paragraph_one_function.md** — 每个段落必须有且仅有一个功能
- 🏛 **w03_tables_must_be_self_contained.md** — 表格必须自解释
- 🏛 **w04_intro_promises_must_be_cashed_in_discussion.md** — Introduction承诺必须在Discussion中兑现
- 🏛 **w05_avoid_ai_vocabulary_at_all_costs.md** — AI味写作是学术credibility poison
- 🏛 **w06_paragraph_triad_structure.md** — 每个段落必须是完整的论证单元
- 🏛 **w07_topic_sentence_precision.md** — 主题句必须兼具话题指向和核心观点
- 🏛 **w08_supporting_sentences_chain.md** — 支持句必须是环环相扣的论证链

### p* — Project Management

- 🏛 **p01_one_paper_one_story.md** — 一篇论文一个故事
- 🏛 **p02_reviewer_response_is_part_of_writing.md** — 审稿回复是写作的一部分
- 🏛 **p03_deadline_drives_scope_not_quality.md** — Deadline驱动scope，不驱动quality
- 🏛 **p04_rejection_is_information_not_failure.md** — Rejection是信息，不是失败
- 🏛 **p05_standardize_data_infrastructure_across_projects.md** — 多项目共享数据源时必须统一基础设施

## 公理 → Skill 映射

> 动态演化不创建新 skill。公理通过约束已有 skill 来影响写作质量。

| 使用 Skill 时 | 应检查的公理 |
|---|---|
| `write-introduction` | t01, t02, t03, w01, w04 |
| `write-theory` | t04, t05, t06, t07 |
| `write-methods` | e01, e02, e03, e04, e05, e06 |
| `write-results` | e02, w03 |
| `write-discussion` | w04, p01 |
| `humanizer` / `proofread` | w05, w06, w07, w08 |
| `revision-coach` | p02, p04 |
| `causal-analysis` / `did-analysis` | e01, e04, e05 |
| `research-gap-diagnosis` | t01, t02, t03 |

当公理与 skill 语料库中的范例冲突时（如 t07 要求条件化但语料范例是主效应），优先遵循公理——公理是更稳定的决策原则，skill 语料库需要据此更新。

## 使用指南

### 何时调用公理

1. **理论判断时**（t*）：当用户问"这算不算贡献""gap够不够强""理论框架缺什么"
2. **方法决策时**（e*）：当用户问"这个识别策略可信吗""稳健性够不够""变量怎么测"
3. **写作诊断时**（w*）：当用户要求重写段落、审查论文、准备投稿
4. **项目推进时**（p*）：当用户问"该投哪个期刊""怎么回复审稿人""优先级怎么排"

### 公理 ≠ 教条

- 公理是**启发式原则**，不是不可违背的法律
- 当公理之间冲突时（如t01要求具体贡献 vs. 项目早期贡献尚模糊），优先**沟通冲突**而非盲目执行
- 用户明确 override 某条公理时，记录原因并考虑未来更新该公理

### 积累与演化

- **每周一 9:07 AM**：observer.py 采集近期研究活动（cron job，7 天自动过期需重建）
- **每 2-4 周**：reflector.py 分析观察记录，跨项目验证的模式晋升为 promotion draft
- **新公理创建标准**：cross-project general + multi-time verified + clear applicable scenario
- **现实预期**：商学论文决策低频高 stakes，每年新增 5-10 条数据蒸馏公理是正常速度。大多数公理是教科书护栏（🏛）——它们的作用是保证下限，不是独特洞见。
