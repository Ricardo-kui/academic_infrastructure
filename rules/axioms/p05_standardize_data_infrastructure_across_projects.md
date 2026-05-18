---
type: axiom
category: project_management
note_id: axiom-p05
trigger_words: ["数据基础设施", "data infrastructure", "跨项目", "cross-project", "统一口径", "变量定义", "共享数据", "清洗流程"]
source: "agentic_reflector 2026-05-18; 产品召回四个子项目实践"
---

# p05: Standardize Data Infrastructure Across Projects

## 核心原则

**当多个项目共享同一数据源或同一结果变量时，必须建立统一的数据基础设施（包括清洗流程、变量定义、模型选择），而非各自为政。**

## 触发场景

- 多个项目使用同一数据库（如 NHTSA recall data）
- 多个项目使用同一结果变量（如 time to recall）
- 多个项目面临同一数据处理问题（如 left-censoring）
- 多个项目需要同一测量方法（如 MHHI delta）

## 决策规则

1. **统一变量定义**：如 FirmAwarenessDate 以 NHTSA 首次公开披露日期为准，而非企业内部知晓日期
2. **统一模型基准**：如所有 recall 项目统一使用 Cox 比例风险模型作为 survival analysis 基准
3. **统一结果变量**：如 time to recall 作为核心结果，recall count 仅作扩展
4. **统一处理方案**：如 left-censoring 问题采用同一处理逻辑
5. **共享清洗代码**：数据清洗流程模块化，供所有项目复用

## 例外

- 项目有特殊理论需求需不同变量定义（需书面论证）
- 数据源更新导致清洗流程变更（需同步更新所有项目）

## 验证

- 检查所有共享项目是否使用同一变量口径
- 检查所有共享项目是否使用同一模型基准
- 检查数据清洗代码是否可复用

## 关联公理

- [[p01_one_paper_one_story]] — 一篇论文一个故事，但基础设施可共享
- [[e03_construct_measure_alignment]] — 统一变量定义是构念-测量对齐的前提
