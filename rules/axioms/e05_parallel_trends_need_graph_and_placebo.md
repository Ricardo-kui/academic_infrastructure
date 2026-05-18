---
type: axiom
category: empirical
note_id: axiom-e05
trigger_words: ["平行趋势", "parallel trends", "DiD", "difference-in-differences", "Callaway-Sant'Anna", "Sun-Abraham"]
source: "用户偏好; did-analysis skill"
---

# e05: Parallel Trends Need Graph and Placebo — DiD 的不可协商标准

## 核心原则

**平行趋势假设必须有图形展示和安慰剂检验双重支撑；异质性处理效应必须使用 Callaway-Sant'Anna 或 Sun-Abraham。**

传统 TWFE DiD 在 staggered adoption 下已被证明有偏（Goodman-Bacon 2021）。现代 DiD 必须升级。

## 现代 DiD 五步工作流

1. **诊断 TWFE 问题**：使用 Goodman-Bacon decomposition 或 event-study 图形检查 pre-trends
2. **图形展示平行趋势**：绘制处理组和对照组的 outcome 随时间变化的轨迹，处理前必须平行
3. **安慰剂检验**：
   - 时间安慰剂：将处理时间提前 1-2 期
   - 空间安慰剂：将处理分配给未处理单元
   - 结果安慰剂：将处理应用于无关 outcome
4. **使用异质性稳健估计器**：
   - Callaway-Sant'Anna（分组-时期 ATT）
   - Sun-Abraham（交互加权估计器）
   - 避免传统 TWFE 的负权重问题
5. **HonestDiD 敏感性分析**：检验平行趋势假设的违反程度对结果的影响

## 执行规则

1. **没有 pre-trend 图形的 DiD 等于没做 DiD**
2. **staggered adoption 必须使用 CS 或 SA**：传统 TWFE 在异质性处理效应下有偏，不能使用
3. **event-study 系数图必须包含 95% CI**：视觉上的平行趋势必须有统计支撑
4. **平行趋势讨论必须诚实**："We cannot fully rule out that unobserved trends differed between treated and control groups, but the pre-trend evidence and placebo tests suggest this threat is limited."

## 反例 → 正例

- ❌ "We use a difference-in-differences design and assume parallel trends."
- ✅ "We estimate a staggered difference-in-differences design using Callaway and Sant'Anna's (2021) group-time ATT estimator to avoid bias from heterogeneous treatment effects. Figure 3a shows parallel pre-trends between treated and control firms for the 5 years preceding reform, with no significant lead coefficients (Panel A). A placebo test assigning reform dates 2 years earlier yields no significant effect (Panel B). HonestDiD sensitivity analysis shows our results remain significant under plausible violations of parallel trends up to 2× the observed pre-trend divergence."

## 关联公理

- [[e01_natural_experiment_first]] — DiD 作为自然实验的首选工具
- [[e04_robustness_must_cover_selection_and_measurement]] — 安慰剂检验的系统化
