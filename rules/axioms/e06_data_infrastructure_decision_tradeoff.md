---
id: e06
name: Data Infrastructure Decision Tradeoff
created: 2026-07-27
updated: 2026-07-27
status: active
category: empirical
promoted_from: "contexts/thought_review/promotions/2026-07-27_promo_01_axiom_high.md"
---

# e06: Data Infrastructure Decision Tradeoff — 精度降级必须声明

## 原则
当数据基础设施约束（API配额、下载限制、计算资源等）迫使测量精度降级时，研究者必须：
1. 记录原始方案与降级方案的差异
2. 量化精度损失的影响（如匹配率、误分类率）
3. 在论文中明确声明降级及其对结论稳健性的潜在影响

## 触发场景
- API配额不足导致数据获取方案变更
- 数据下载限制迫使使用替代数据源
- 计算资源不足导致变量聚合或简化
- 匹配键从精确匹配降级为模糊匹配

## 决策边界
- **Yes**: 精度降级后仍能支持核心假设检验，且降级影响可量化
- **No**: 精度降级导致核心构念无法有效测量，或影响不可量化

## 相关公理
- [[e03_construct_measure_alignment]] — 精度降级直接影响构念-测量对齐
- [[e04_robustness_must_cover_selection_and_measurement]] — 降级后的稳健性检验需覆盖测量误差

## 示例
- 药品FAERS匹配：从NDC精确匹配降级为generic/brand级匹配，需声明匹配率变化和对Wowak可比性的影响
