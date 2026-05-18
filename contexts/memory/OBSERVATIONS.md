---
type: memory_log
note_id: infra-observations
created: 2026-05-18
status: active
---

# OBSERVATIONS.md — L1/L2 动态记忆日志

> **L1（原始观察）**：由 observer.py 每日采集，Claude 分析后写入。包含 🔴🟡🟢 优先级标记。
> **L2（周期反思）**：由 reflector.py 每周分析，将高价值观察晋升为公理或技能建议。

## 格式规范

```markdown
### Date: YYYY-MM-DD

🔴 **理论突破 / 重大决策**
- [项目标签] 内容摘要。链接到具体笔记。

🟡 **方法决策 / 写作判断**
- [项目标签] 内容摘要。

🟢 **常规进展 / 阅读记录**
- [项目标签] 内容摘要。
```

## 项目标签

| 标签 | 含义 |
|------|------|
| `#产品召回` | 产品召回专题相关 |
| `#共同所有权` | 共同所有权专题相关 |
| `#竞业协议` | 竞业协议/制度冲击专题相关 |
| `#方法论` | 识别策略、测量、模型相关 |
| `#写作` | 论文写作、段落重构、投稿相关 |
| `#理论` | 理论构建、机制推导、假设修正 |
| `#审稿` | 审稿回复、拒稿诊断、修改策略 |
| `#跨专题` | 跨专题桥接、综合发现 |

---

## Daily Observations

<!-- observer.py / Claude cron 在此追加 -->

### Date: 2026-05-12

🔴 **理论突破 / 重大决策**
- [#产品召回] 共同所有权项目的理论框架从"加速vs延迟"二元对立改为"条件化框架"——外部威胁高时spillover-internalization占优，威胁低时anticompetitive占优。参考 Kini et al. (2024)。

🟡 **方法决策 / 写作判断**
- [#共同所有权] 确定使用 MHHI delta 作为共同所有权测量，放弃 HHCO（He & Huang 2017），因为 MHHI delta 在反竞争文献中更成熟。
- [#竞业协议] anti-SLAPP 项目改用 staggered DiD + event study，放弃 simple DiD，因为州级采纳时间不同。

🟢 **常规进展 / 阅读记录**
- [#产品召回] 完成 Eilert et al. (2017) JM 召回时机文献笔记。

### Date: 2026-05-13

🔴 **理论突破 / 重大决策**
- [#CEO paranoia] CEO paranoia 和 CEO regulatory focus 两个项目共享同一套 recall timing 结果变量和 IV 方法，但理论机制完全不同——前者是心理认知路径，后者是动机聚焦路径。

🟡 **方法决策 / 写作判断**
- [#方法论] 确定所有 recall 项目统一使用 time to recall 作为核心结果，recall count 仅作扩展。

### Date: 2026-05-14

🟡 **方法决策 / 写作判断**
- [#共同所有权] FirmAwarenessDate 口径确认：以 NHTSA 首次公开披露日期为准，而非企业内部知晓日期。
- [#竞业协议] IDD × 广告支出项目确认 staggered DiD 设计，但需处理多期处理效应的异质性问题。

🟢 **常规进展 / 阅读记录**
- [#竞业协议] 阅读 Hoffmann et al. (2024) JM 关于 UD laws 与产品召回的文献。

### Date: 2026-05-15

🟡 **方法决策 / 写作判断**
- [#产品召回] 多个项目（共同所有权、anti-SLAPP、CEO paranoia）都遇到 recall timing 的 left-censoring 问题，需统一处理方案。

### Date: 2026-05-16

🔴 **理论突破 / 重大决策**
- [#跨专题] 发现产品召回专题下的四个项目（共同所有权、anti-SLAPP、CEO paranoia、CEO regulatory focus）可以共享同一套 recall 数据基础设施，包括 NHTSA 数据清洗、FirmAwarenessDate 定义、left-censoring 处理。

🟡 **方法决策 / 写作判断**
- [#方法论] 决定所有 recall 项目统一使用 Cox 比例风险模型作为 survival analysis 基准，而非简单的 OLS 对数转换。

