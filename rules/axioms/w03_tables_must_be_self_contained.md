---
type: axiom
category: writing
note_id: axiom-w03
trigger_words: ["表格", "table", "figure", "图", "自解释", "self-contained"]
source: "Pollock 2025 Ch07; 写作指导体系"
---

# w03: Tables Must Be Self-Contained — 表格不看正文也能读懂

## 核心原则

**读者应该能在不读正文的情况下，从表格中读懂：研究了什么、用了什么方法、发现了什么、结果有多稳健。**

## 自解释表格的五个要素

| 要素 | 要求 | 反例 |
|------|------|------|
| **标题** | 说明表格内容、样本、方法 | "Table 2" → "Table 2. Main Results: CEO Narcissism and Recall Timing, 2000-2020" |
| **列标题** | 清晰标识每个模型/变量 | "(1)" "(2)" → "(1) OLS" "(2) FE" "(3) DiD" |
| **行标签** | 变量名 + 理论含义 | "Narcissism" → "CEO Narcissism (text-based)" |
| **统计信息** | 样本量、R²、固定效应、标准误类型 | 缺失 → 必须标注 "Robust SE clustered at firm level" |
| **注释** | 显著性水平、特殊处理、数据来源 | 无注释 → *** p<0.01, ** p<0.05, * p<0.1; SEs clustered at firm level |

## 执行规则

1. **表格标题必须包含 outcome、sample period 和 method**：不能只写"Main Results"
2. **每个系数必须有明确的标准误类型**：OLS? Clustered? Bootstrap? 不能假设读者知道
3. **固定效应必须在表格底部明确标注**："Firm FE" "Year FE" "Industry × Year FE"
4. **稳健性检验表格必须有"检验了什么威胁"的标注**："Panel B: Alternative narcissism measure" 而不是 "Panel B: Robustness"
5. **图形必须有清晰的坐标轴标签和图例**："Effect of X on Y" 而不是 "Coefficient"

## 反例 → 正例

- ❌ 表格标题："Table 2. Regression Results"
- ✅ 表格标题："Table 2. CEO Narcissism and Time to Product Recall: Main Results and Identification Checks, 2000-2020"
- ❌ 列标题："(1)" "(2)" "(3)"
- ✅ 列标题："(1) OLS" "(2) Firm FE" "(3) Callaway-Sant'Anna DiD"
- ❌ 行标签："Narcissism" "Controls" "Obs"
- ✅ 行标签："CEO Narcissism (text-based, std.)" "Firm Size (log assets)" "Firm Age" "Leverage" "Constant" "Observations" "R-squared" "Firm FE" "Year FE" "Industry × Year FE"

## 关联公理

- [[e04_robustness_must_cover_selection_and_measurement]] — 稳健性表格的组织
- [[w02_one_paragraph_one_function]] — Results 段落的表格导航
