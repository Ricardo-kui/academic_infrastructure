---
type: axiom
category: empirical
note_id: axiom-e01
trigger_words: ["识别策略", "identification", "因果", "causal", "内生性", "endogeneity"]
source: "Edmans 2023; Beugelsdijk & Bird 2024; 用户偏好"
---

# e01: Natural Experiment First — 识别策略可信度优先于系数显著性

## 核心原则

**没有可信识别策略的因果声称是学术欺诈。**

识别策略可信度层级：
1. **自然实验**（州级法律冲击、政策变化、断点、随机分配）
2. **工具变量 / 断点回归**
3. **固定效应 + 丰富控制 + 纵向设计**
4. **横截面 OLS**（仅限描述性/探索性，禁止因果声称）

## 执行规则

1. **优先自然实验**：当存在外生政策变化或制度冲击时，必须以自然实验为第一识别策略
2. **禁止无识别时的因果语言**：没有 DiD/IV/RD 时，不得使用 "causes" "effects" "impact" "leads to"；改用 "associated with" "linked to" "predicts"
3. **识别策略必须在 Introduction 或 Methods 前置说明**：不能让读者读到 Results 才发现"原来作者用了 FE"
4. **每个识别策略必须有威胁讨论**：说明什么内生性来源被处理了、什么还没处理、为什么未处理的威胁不大

## 反例 → 正例

- ❌ "Our results show that CEO narcissism causes faster recall timing (β = 0.35, p < 0.01)."
- ✅ "Leveraging staggered state-level adoption of director-liability laws as a quasi-exogenous shock to CEO discretion, we find that CEOs in treated firms initiate recalls 23% faster post-reform (β = 0.35, p < 0.01). This DiD design addresses endogenous matching between CEO traits and firm risk profiles, though unobserved state-level trends remain a residual threat."

## 关联公理

- [[e02_data_is_not_evidence]] — 识别的下一步
- [[e05_parallel_trends_need_graph_and_placebo]] — DiD 特殊规则
