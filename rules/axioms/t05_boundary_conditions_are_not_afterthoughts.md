---
type: axiom
category: theory
note_id: axiom-t05
trigger_words: ["边界条件", "boundary condition", "scope", "适用范围", "局限性"]
source: "Makadok et al. 2018"
---

# t05: Boundary Conditions Are Not Afterthoughts — 边界条件是理论精确化的核心工具

## 核心原则

**边界条件不是论文的"道歉段落"，而是理论精确化的核心工具。**

Makadok: "Careful exploration of boundary conditions can make a valuable theoretical contribution by identifying logical inconsistencies, restricting or relaxing scope conditions, and deriving more specific predictions."

## 边界条件的四种贡献

| 类型 | 操作 | 理论效果 |
|------|------|---------|
| 收紧边界 | 增加 scope conditions | 提高预测精度，可能降低普适性 |
| 放松边界 | 减少 scope conditions | 扩大理论适用范围，可能降低预测精度 |
| 澄清边界 | 明确 implicit assumptions | 暴露理论的逻辑结构，便于检验 |
| 挑战边界 | 发现 boundary inconsistencies | 可能推翻或重大修正理论 |

## 执行规则

1. **边界条件必须前置到理论推导**：在提出假设时说明"该关系在Z条件下更强/更弱/反向"，而不是在 Discussion 才补充
2. **禁止 trivial boundary**："未来研究应在其他行业验证"不是边界条件，是废话
3. **边界条件必须有理论依据**：不能只是"我们样本来自美国制造业"，而是"该机制依赖于美国特定的监管结构，因此在制度差异大的情境下可能失效"
4. **Discussion 的 limitations 必须回到理论**：每个 limitation 都应说明"这意味着理论的适用范围是 X 而非 Y"

## 反例 → 正例

- ❌ "Our findings are limited to the U.S. context, and future research should examine other countries."
- ✅ "The recall-timing mechanism we identify depends on the U.S. regulatory structure that allows firms discretion over when to report safety defects. In jurisdictions with mandatory immediate-reporting laws (e.g., EU's RAPEX), the CEO trait effect we document may be attenuated because managerial discretion is compressed. This boundary condition sharpens the theory: CEO personality matters most where institutional ambiguity creates decision space."

## 关联公理

- [[t01_gap_must_be_genuine]] — boundary conditions lever
- [[t04_mechanism_must_penetrates_blackbox]] — 机制的条件化
