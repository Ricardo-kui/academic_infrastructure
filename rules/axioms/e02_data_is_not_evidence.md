---
type: axiom
category: empirical
note_id: axiom-e02
trigger_words: ["data", "evidence", "显著", "significant", "p-value", "系数"]
source: "Edmans 2023; Beugelsdijk & Bird 2024"
---

# e02: Data Is Not Evidence — 显著系数≠可信发现

## 核心原则

**Data are facts; evidence supports a specific interpretation and rules out plausible alternatives.（Edmans）**

显著系数只是数据的一种描述，不是对理论主张的证据。真正的证据必须：
1. 支持作者想让读者相信的**具体解释**
2. 排除**合理的替代解释**

## 执行规则

1. **每个显著结果必须有理论解释**：不是"X is positively related to Y"，而是"X increases Y because [mechanism], which is consistent with [theory]"
2. **必须主动排除替代解释**：
   - 反向因果？→ 用时间滞后、工具变量、理论论证
   - 遗漏变量？→ 用固定效应、敏感性分析（Altonji/Oster）
   - 样本选择？→ 用 Heckman、逆概率加权、样本外验证
   - 测量误差？→ 用替代测量、结构方程、信度检验
3. **禁止 HARKing**：假设必须在看到数据前注册或明确陈述；事后发现的显著关系必须标注为"exploratory"
4. **Null results 也是证据**：不显著的结果如果 theoretically important，必须报告并解释

## 反例 → 正例

- ❌ "The coefficient on CEO narcissism is positive and significant (β = 0.35, p < 0.01), supporting our hypothesis."
- ✅ "The positive coefficient on CEO narcissism (β = 0.35, p < 0.01) is consistent with our attention-allocation mechanism: narcissistic CEOs prioritize image-threatening signals, accelerating recall initiation. This interpretation is strengthened by three pieces of evidence: (1) the effect is concentrated in high-media-coverage periods, (2) an alternative explanation through risk-seeking is rejected because narcissism does not correlate with recall scope, and (3) an Oster sensitivity test shows the effect survives omitted-variable bias up to 2.5× the explanatory power of observed controls."

## 关联公理

- [[e01_natural_experiment_first]] — 识别策略是 evidence 的前提
- [[e04_robustness_must_cover_selection_and_measurement]] — 替代解释排除的系统化
