---
type: axiom
category: project
note_id: axiom-p02
trigger_words: ["审稿回复", "reviewer response", "R&R", "revise", "回复审稿人", "response letter"]
source: "Pollock 2025 Ch12; Edmans 2023"
---

# p02: Reviewer Response Is Part of Writing — 审稿回复是写作的一部分

## 核心原则

**审稿回复不是防御战，而是加深论证的机会。每条回复都应该让论文比原来更好。**

Edmans: "Rejection reflects contribution strength, fit, feasibility of revision, and editor/referee judgment."
Pollock Ch12: "Revision is not correction; it is deepening."

## 回复质量的三个层级

| 层级 | 特征 | 效果 |
|------|------|------|
| **防御性** | "Reviewer misunderstood our paper." | 激怒审稿人 |
| **合规性** | "We have added control variables as suggested." | 勉强过关 |
| **深化性** | "This comment exposes a subtle threat to our mechanism that we had not fully articulated. We now clarify..." | 赢得尊重 |

## 执行规则

1. **永远假设审稿人是善意的、聪明的、忙碌的**：他们不可能是"完全误解"，最多是"我们没有讲清楚"
2. **每条回复必须有三种成分**：
   - **Acknowledge**：感谢指出问题（即使不同意）
   - **Respond**：明确说明做了什么修改（或为什么不做）
   - **Locate**：指出修改在稿子的哪一页、哪一段、哪张表
3. **不做修改时必须提供理论依据**："We appreciate the suggestion to add industry × year FE. However, because our identification relies on within-firm variation over time, industry × year FE would absorb our treatment effect. We instead add state × year FE to address regional trends (p. 15, Table 4)."
4. **重大修改必须在 cover letter 中总结**：让 editor 一眼看到论文如何改进

## 反例 → 正例

- ❌ "Reviewer 2 claims our instrument is weak. This is incorrect because our F-statistic is 12.5, which exceeds the Stock-Yogo threshold."
- ✅ "We thank Reviewer 2 for pushing us to strengthen the instrument discussion. Upon reflection, we realized our initial presentation understated the first-stage relationship. We have now: (1) added a dedicated first-stage table (Table A3, p. 32) showing the F-statistic of 12.5 exceeds the Stock-Yogo 10% maximal IV size threshold; (2) added a discussion of why the instrument satisfies the exclusion restriction based on [theoretical argument] (p. 18, para. 3); and (3) conducted a sensitivity analysis using Anderson-Rubin confidence intervals, which are robust to weak instruments (p. 33, Table A4)."

## 关联公理

- [[p04_rejection_is_information_not_failure]] — 拒稿心态
- [[e04_robustness_must_cover_selection_and_measurement]] — 回复中常用的稳健性补充
