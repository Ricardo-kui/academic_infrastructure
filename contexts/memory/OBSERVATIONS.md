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
### Date: 2026-05-17

🟢 **常规进展 / 阅读记录**
- [#产品召回] 梳理了CEO调节焦点与召回时机项目的核心文献簇与阅读顺序 (文献地图明确了理论锚点和阅读路径，属于文献综述实质性推进) [[00 工作台\项目\CEO regulatory focus × time to recall\90 AI drafts\关联文献地图 - CEO regulatory focus × time to recall.md]]

### Date: 2026-05-18

🟢 **常规进展 / 阅读记录**
- [#产品召回] Hoffmann et al. (2024) 被定位为 conceptual cousin 而非模板 (明确 closest-paper 的差异化定位，影响写作策略) [[00 工作台\项目\anti-SLAPP laws × product recall count and timing\90 AI drafts\背景文献笔记 - Hoffmann et al (2024) JM UD laws and product recalls.md]]
- [#产品召回] 现实案例搜索和网络案例素材被标记为 controlled_defer (案例搜索被推迟，不影响当前核心进展) [[00 工作台\项目\anti-SLAPP laws × product recall count and timing\90 AI drafts\现实案例搜索 - anti-SLAPP laws × product recall count and timing.md]]

### Date: 2026-05-19

🔴 **理论突破 / 重大决策**
- [#CEO paranoia] Theory Packet 新增 Darby et al. (2026) 作为外部治理对照锚 (引入外部治理对照锚，强化内部认知路径的理论区分) [[00 工作台\项目\CEO paranoia × time to recall\00 Active\Theory Packet - CEO paranoia × time to recall.md]]

🟡 **方法决策 / 写作判断**
- [#CEO regulatory focus] Methods Packet 新增 Darby et al. (2026) 作为外部治理基准锚 (引入新锚文校准测量、方法和效应量，提升方法可信度) [[00 工作台\项目\CEO regulatory focus × time to recall\00 Active\Methods and Results Packet - CEO regulatory focus × time to recall.md]]

🟢 **常规进展 / 阅读记录**
- [#CEO regulatory focus] Context Packet 和 Theory Packet 常规更新，无实质性理论或方法变动 (文件内容为已有信息的整理和重申，无新判断或突破) [[00 工作台\项目\CEO regulatory focus × time to recall\00 Active\Context Packet - CEO regulatory focus × time to recall.md]]
- [#CEO paranoia] Context Packet 常规更新，无实质性理论或方法变动 (文件内容为已有信息的整理和重申，无新判断或突破) [[00 工作台\项目\CEO paranoia × time to recall\00 Active\Context Packet - CEO paranoia × time to recall.md]]

### Date: 2026-05-20

🟡 **方法决策 / 写作判断**
- [#产品召回] 建立paranoia与overconfidence/regulatory focus的构念区分笔记 (明确构念区分路径，支撑discriminant validity论证) [[00 工作台\项目\CEO paranoia × time to recall\90 AI drafts\关联文献地图 - CEO paranoia × time to recall.md]]

🟢 **常规进展 / 阅读记录**
- [#产品召回] 锚定Wu et al (2025) SMJ作为叙事结构先例与discriminant validity方法先例 (新锚文献提供顶刊验证的contingency叙事骨架和区分效度方法先例) [[00 工作台\项目\CEO paranoia × time to recall\90 AI drafts\深度阅读笔记 - Wu et al (2025) SMJ anti-SLAPP 与预防性CSP.md]]
- [#产品召回] 更新文献证据包，调整Recall正式层默认路由 (常规文献整理与路由优化，无实质性理论判断) [[00 工作台\项目\CEO paranoia × time to recall\00 Active\文献证据包 - CEO paranoia × time to recall.md]]

### Date: 2026-05-21

🔴 **理论突破 / 重大决策**
- [#产品召回] 明确Theory与Introduction的接力关系及核心机制 (确定了理论机制为CEO regulatory focus改变召回启动阈值，属核心假设推进) [[00 工作台\项目\CEO regulatory focus × time to recall\90 AI drafts\Theory and Hypotheses 重写稿 - CEO regulatory focus × time to recall.md]]

🟡 **方法决策 / 写作判断**
- [#方法论] 确定数据来源为Artfinder平台，明确爬取变量 (数据源和变量测量方案确定，属方法口径重要进展) [[00 工作台\项目\身份修辞 × 买家购买经验.md]]

### Date: 2026-05-22

🔴 **理论突破 / 重大决策**
- [#共同所有权] 共同所有权项目文献证据包完成24篇文献formalize，主结果固定为time to recall (主结果变量锁定是项目核心里程碑) [[00 工作台\项目\共同所有权 × 产品召回\00 Active\文献证据包 - 共同所有权 × 产品召回.md]]
- [#CEO regulatory focus × time to recall] 机制编译笔记将CEO regulatory focus机制压缩为action-threshold reweighting链条 (机制链条整理是常规理论推进，无突破性判断) [[00 工作台\项目\CEO regulatory focus × time to recall\90 AI drafts\机制编译笔记 - CEO regulatory focus 如何影响召回时机.md]]

🟡 **方法决策 / 写作判断**
- [#CEO regulatory focus × time to recall] 假设推导解构笔记诊断H1/H2支撑偏薄、引文尾注化、缺少收尾句 (写作诊断指向假设段落的实质性修改方向) [[00 工作台\项目\CEO regulatory focus × time to recall\90 AI drafts\原文假设推导解构与对照 - CEO regulatory focus × time to recall.md]]

🟢 **常规进展 / 阅读记录**
- [#共同所有权] 文献证据包新增Batch 8C回流，建立稳定证据链与使用纪律 (证据链结构化是文献综述实质性推进) [[00 工作台\项目\共同所有权 × 产品召回\00 Active\文献证据包 - 共同所有权 × 产品召回.md]]

### Date: 2026-05-23

🔴 **理论突破 / 重大决策**
- [#产品召回] Qian et al. (2024) 确认regulatory focus可稳健进入安全决策，为recall timing提供近邻证据 (核心假设验证：regulatory focus→harm-reducing action迁移成立) [[00 工作台/项目/CEO regulatory focus × time to recall/深度阅读笔记 - Qian et al (2024) JOM workplace safety.md]]

🟡 **方法决策 / 写作判断**
- [#产品召回] Introduction outline完成，绑定narrative slots到具体文献和模板，明确gap类型为Incompleteness (项目里程碑：写作框架确定，gap定位和贡献声明已绑定) [[00 工作台/项目/CEO regulatory focus × time to recall/EN/Section Outlines/introduction_outline.md]]
- [#产品召回] Discussion、Methods、Results、Theory四个outline创建为占位符，约束条件已写入 (写作框架扩展，但内容尚未填充) [[00 工作台/项目/CEO regulatory focus × time to recall/EN/Section Outlines/discussion_outline.md]]

🟢 **常规进展 / 阅读记录**
- [#跨专题] 知识库运维：关闭Copilot autosave、清理工作台归档、执行RAG激活计划 (常规运维，无学术判断变更) [[00 工作台/知识库操作日志.md]]
- [#跨专题] 回流Chung, Low, & Rust (2023) JAMS至canonical层并更新MOC (文献整理，已有原子层笔记，无新发现) [[00 工作台/知识库操作日志.md]]

### Date: 2026-05-24

🔴 **理论突破 / 重大决策**
- [#general] Literature Dialogue 新增 Shi et al. (2026) 和 Wu et al. (2026) 两篇锚文 (新增关键文献，扩展了理论对话（语言机制和绩效反馈）) [[00 工作台\项目\CEO regulatory focus × time to recall\EN\Literature Dialogue.md]]
- [#产品召回] Claim Cards EN 完成4个核心主张的英文表述和机制描述 (核心主张的正式英文表述，支撑理论写作) [[00 工作台\项目\CEO regulatory focus × time to recall\EN\Claim Cards EN.md]]

🟡 **方法决策 / 写作判断**
- [#产品召回] Context Packet EN 完成术语锁定和核心主张定义 (术语锁定和核心主张定义是写作的关键基础) [[00 工作台\项目\CEO regulatory focus × time to recall\EN\Context Packet EN.md]]

🟢 **常规进展 / 阅读记录**
- [#产品召回] Evidence Matrix 新增 Shi et al. (2026) 和 Wu et al. (2026) 的证据绑定 (新文献绑定到证据矩阵，支撑理论对话) [[00 工作台\项目\CEO regulatory focus × time to recall\EN\Evidence Matrix.md]]
- [#产品召回] Concept Map EN 和 Evidence Matrix 完成英文版本创建 (常规文件翻译和整理，无实质性学术判断变化) [[00 工作台\项目\CEO regulatory focus × time to recall\EN\Concept Map EN.md]]

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
