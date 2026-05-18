---
type: axiom_index
note_id: infra-axiom-index
created: 2026-05-18
status: active
---

# Axiom Index — 学术公理库索引

> 这些公理从用户的写作指导笔记（`Vault/文献笔记库/02 原子化/写作指导`）和已配置 skills 的设计哲学中提炼而来。它们不是抽象哲学，而是可执行的决策原则。

## 分类体系

| 前缀 | 类别 | 来源 | 触发场景 |
|------|------|------|----------|
| `t*` | Theory & Contribution | Makadok et al. 2018; Zuckerman 2015; Sandberg & Alvesson 2010 | 理论构建、贡献定位、gap诊断 |
| `e*` | Empirical & Identification | Edmans 2023; Beugelsdijk & Bird 2024; skills因果推断体系 | 研究设计、识别策略、稳健性检验 |
| `w*` | Writing & Rhetoric | Simsek & Li 2022; Pollock 2025; 写作指导体系 | 论文写作、段落诊断、AI味去除 |
| `p*` | Project Management | Edmans 2023; 写作指导导航 | 项目推进、投稿策略、审稿回复 |

## 公理列表

### t* — Theory & Contribution

- **t01_gap_must_be_genuine.md** — 贡献必须落在Makadok八维度的至少一个，且必须具体说明改变了什么
- **t02_problematization_not_gap_spotting.md** — Gap-spotting不是贡献，problematization才是
- **t03_so_what_who_cares.md** — 如果不改变读者的prior，就不是贡献
- **t04_mechanism_must_penetrates_blackbox.md** — 机制解释必须穿透黑箱
- **t05_boundary_conditions_are_not_afterthoughts.md** — 边界条件是理论精确化的核心工具
- **t06_conditionalize_theoretical_frameworks.md** — 二元对立框架应转化为条件化框架 [provisional]

### e* — Empirical & Identification

- **e01_natural_experiment_first.md** — 识别策略可信度优先于系数显著性
- **e02_data_is_not_evidence.md** — Data ≠ Evidence；显著系数≠可信发现
- **e03_construct_measure_alignment.md** — 构念-测量对齐是方法可信度第一道门槛
- **e04_robustness_must_cover_selection_and_measurement.md** — 稳健性检验必须覆盖两大威胁
- **e05_parallel_trends_need_graph_and_placebo.md** — 平行趋势需要图形+安慰剂双重支撑

### w* — Writing & Rhetoric

- **w01_introduction_is_jobs_to_be_done.md** — 引言是Jobs to Be Done，不是文献空白展示
- **w02_one_paragraph_one_function.md** — 每个段落必须有且仅有一个功能
- **w03_tables_must_be_self_contained.md** — 表格必须自解释
- **w04_intro_promises_must_be_cashed_in_discussion.md** — Introduction承诺必须在Discussion中兑现
- **w05_avoid_ai_vocabulary_at_all_costs.md** — AI味写作是学术credibility poison
- **w06_paragraph_triad_structure.md** — 每个段落必须是完整的论证单元（主题句→支持句→结尾句）
- **w07_topic_sentence_precision.md** — 主题句必须兼具话题指向和核心观点
- **w08_supporting_sentences_chain.md** — 支持句必须是环环相扣的论证链

### p* — Project Management

- **p01_one_paper_one_story.md** — 一篇论文一个故事
- **p02_reviewer_response_is_part_of_writing.md** — 审稿回复是写作的一部分
- **p03_deadline_drives_scope_not_quality.md** — Deadline驱动scope，不驱动quality
- **p04_rejection_is_information_not_failure.md** — Rejection是信息，不是失败
- **p05_standardize_data_infrastructure_across_projects.md** — 多项目共享数据源时必须统一基础设施

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

- observer.py 每日扫描研究活动中的决策模式
- reflector.py 每周分析 🔴/🟡 条目，将跨项目验证的原则晋升为公理
- 新公理的创建标准：cross-project general + multi-time verified + clear applicable scenario
