---
type: skill
category: data_infrastructure
note_id: skill-s01
trigger_words: ["recall数据", "召回数据", "NHTSA", "FirmAwarenessDate", "left-censoring", "time to recall", "Cox模型", "recall infrastructure"]
source: "agentic_reflector 2026-05-18; 产品召回四个子项目共享基础设施"
---

# s01: Product Recall Data Infrastructure Setup

## 目的

为产品召回专题下的多个项目建立统一、可复用的数据基础设施，确保变量定义、清洗流程、模型选择的一致性。

## 输入

- 原始 NHTSA 召回数据（含召回日期、企业信息、产品类别等）
- 企业财务数据（Compustat、CRSP）
- 行业分类数据（SIC/NAICS）

## 输出

- 清洗后的 recall timing 数据集（含 FirmAwarenessDate、time to recall、left-censoring 标志）
- 可复用的数据清洗代码（Python/Stata）
- 变量定义文档

## 步骤

### 步骤 1：数据获取与初步清洗

- 从 NHTSA 下载原始召回数据
- 去除重复记录（按 recall ID 去重）
- 处理缺失值（如缺失 FirmAwarenessDate 的样本标记）

### 步骤 2：变量定义

- **FirmAwarenessDate**：以 NHTSA 首次公开披露日期为准
- **Recall Date**：企业实际召回开始日期
- **Time to Recall**：FirmAwarenessDate 到 Recall Date 的天数
- **Left-censoring**：如果 FirmAwarenessDate 在样本期开始之前，标记为 left-censored

### 步骤 3：数据合并

- 将召回数据与企业财务数据按 firm-year 匹配
- 处理多对多匹配（同一企业多年多次召回）

### 步骤 4：模型基准

- 使用 Cox 比例风险模型作为 survival analysis 基准
- 结果变量：time to recall
- 扩展分析：recall count（Poisson/Negative Binomial）

### 步骤 5：稳健性检验

- 替换 FirmAwarenessDate 定义（如企业内部知晓日期）
- 替换模型（如 OLS 对数转换）
- 处理 left-censoring（如剔除或使用 Tobit 模型）

## 注意事项

- 所有项目必须使用同一变量口径
- 数据清洗代码需模块化，供所有项目复用
- 变量定义变更需同步更新所有项目

## 关联

- [[p05_standardize_data_infrastructure_across_projects]] — 本 skill 是该公理的执行实现
- [[stata-data-cleaning]] — 数据清洗的 Stata 实现
- [[stata-regression]] — Cox 模型的 Stata 实现
