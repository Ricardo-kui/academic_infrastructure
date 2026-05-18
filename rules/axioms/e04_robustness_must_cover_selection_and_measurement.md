---
type: axiom
category: empirical
note_id: axiom-e04
trigger_words: ["稳健性", "robustness", "安慰剂", "placebo", "选择性偏误", "selection", "measurement error"]
source: "Edmans 2023; Beugelsdijk & Bird 2024; 用户偏好"
---

# e04: Robustness Must Cover Selection and Measurement — 稳健性检验不是装饰

## 核心原则

**稳健性检验必须系统覆盖选择性偏误（selection bias）和测量误差（measurement error）两大威胁，而不是只换控制变量。**

## 两大威胁的系统化检验

### 威胁一：选择性偏误（Selection Bias）

| 类型 | 检验方法 | 何时使用 |
|------|---------|---------|
| 样本选择 | Heckman two-step, IPW, entropy balancing | 处理组和对照组在可观察特征上不平衡 |
| 自选择 / 处理分配 | Propensity score matching, coarsened exact matching | 处理不是随机分配的 |
|  survivor bias | 包含退出/失败样本；检验 attrition 模式 | 样本是存续企业 |
|  时间选择 | 事件研究、动态效应、leads-and-lags | 处理时间可能内生 |

### 威胁二：测量误差（Measurement Error）

| 类型 | 检验方法 | 何时使用 |
|------|---------|---------|
| 代理变量误差 | 替代测量、多指标构建、验证性子样本 | 构念-测量对齐有疑问 |
|  分类误差 | 改变 cutoff、连续化、不同分类标准 | 处理或结果是二元的 |
|  时间窗口误差 | 改变窗口长度、不同 lag 结构 | 时间对齐有疑问 |
|  聚合误差 | 不同层级、disaggregation | 数据在错误层级聚合 |

## 执行规则

1. **Robustness section 必须有 threat-by-threat 的组织**：不是"我们跑了20个稳健性检验"，而是"针对选择性偏误，我们做了X；针对测量误差，我们做了Y"
2. **安慰剂检验必须设计得比主检验更不可能显著**：如果安慰剂也显著，说明识别策略有根本问题
3. **敏感性分析必须有定量标准**：Oster ratio、Rosenbaum bounds、Lee bounds 等，不是"结果仍然显著"
4. **Null/negative results 在稳健性中必须报告**：选择性报告显著结果是 p-hacking

## 反例 → 正例

- ❌ "Our results are robust to adding industry fixed effects, using alternative measures of recall timing, and excluding the financial crisis period."
- ✅ "We address two primary threats to causal interpretation. First, to mitigate selection bias from endogenous CEO-firm matching, we re-estimate using entropy-balanced samples and confirm the effect holds (Panel A). Second, to address measurement error in our text-based narcissism proxy, we reconstruct the measure using an alternative dictionary and show the coefficient remains stable (Panel B). Finally, a placebo test assigning random pseudo-CEOs to firms yields no significant effect, strengthening confidence that the pattern is not driven by unobserved firm heterogeneity."

## 关联公理

- [[e01_natural_experiment_first]] — 识别策略是稳健性的前提
- [[e03_construct_measure_alignment]] — 测量误差的根源
