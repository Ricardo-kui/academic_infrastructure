---
type: axiom
category: empirical
note_id: axiom-e03
trigger_words: ["测量", "measurement", "变量", "variable", "construct", "proxy", "代理"]
source: "Beugelsdijk & Bird 2024; 用户偏好"
---

# e03: Construct-Measure Alignment — 构念-测量对齐是方法可信度第一道门槛

## 核心原则

**变量名和构念名相近不等于对齐。**

Beugelsdijk & Bird: "Proxy measures must match theoretical constructs definitionally and empirically."

Construct-measure misalignment 是 desk reject 的 top reason 之一。

## 对齐检查清单

| 维度 | 检查问题 | 红色警报 |
|------|---------|---------|
| 定义对齐 | 构念定义和代理变量的定义是否在语义上一致？ | 理论讲"战略灵活性"，实证用"固定资产比率" |
| 层级对齐 | 构念和变量是否在同一个分析层级？ | 理论讲"团队认知多样性"，实证用"企业专利数量" |
| 时间对齐 | 构念和变量的时间窗口是否匹配因果逻辑？ | 理论讲"长期承诺"，实证用"当期R&D支出" |
| 方向对齐 | 变量的方向是否与构念的理论方向一致？ | 理论讲"主动性"，实证用"被动响应速度" |

## 执行规则

1. **Methods 必须包含 construct-measure table**：列出每个构念的理论定义、代理变量、数据来源、测量方式、已知局限
2. **禁止 distal proxy**：如果 proxy 和 construct 之间隔了两层以上，必须说明为什么更近的 proxy 不可得
3. **替代测量必须做敏感性检验**：至少一个替代测量来验证结果不是 proxy-specific
4. **构念-测量不对齐时必须使用保守语言**："we proxy X with Y" 而不是 "we measure X"

## 反例 → 正例

- ❌ "We measure CEO narcissism using the NPI-16 scale."（如果数据来自二手来源，如CEO肖像分析）
- ✅ "We proxy CEO narcissism using a text-based measure derived from shareholder letters, following Chatterjee & Hambrick (2007). While this captures grandiose self-presentation rather than clinical narcissism, it aligns with the theoretical construct of narcissism as a socially constructed trait observable in public communications. We validate this proxy against hand-coded narcissism scores for a random subsample (r = 0.72) and confirm robustness using an alternative measure based on press-release first-person singular pronouns."

## 关联公理

- [[e02_data_is_not_evidence]] — 测量质量是 evidence 的基础
- [[e04_robustness_must_cover_selection_and_measurement]] — 测量误差的稳健性
