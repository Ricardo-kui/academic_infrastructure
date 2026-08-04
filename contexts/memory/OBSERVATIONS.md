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
### Date: 2026-08-04

🔴 **理论突破 / 重大决策**
- [#共同所有权] 既有结果失效声明：Table 1-7基于旧数据，须在复现包上重跑。 (核心结果作废并需重跑，是项目关键转折点。) [[00 工作台/项目/共同所有权 × 产品召回/90 AI drafts/实证分析设计 - H2 time-to-recall - 共同所有权 × 产品召回.md]]

🟡 **方法决策 / 写作判断**
- [#共同所有权] H2实证设计修订：Lewbel IV降为补充识别，并购DiD现实校正，变量规格修正。 (识别策略优先级重排及关键变量规格修正，直接影响主回归有效性。) [[00 工作台/项目/共同所有权 × 产品召回/90 AI drafts/实证分析设计 - H2 time-to-recall - 共同所有权 × 产品召回.md]]
- [#共同所有权] 机制数据可得性受限：units_recalled等不在最终数据集，AE匹配内生性检验设为强制前置。 (机制分析可行性受限，需回补数据并新增前置检验。) [[00 工作台/项目/共同所有权 × 产品召回/90 AI drafts/实证分析设计 - H2 time-to-recall - 共同所有权 × 产品召回.md]]
- [#共同所有权] Medicaid覆盖率口径更正：无条件仅14.0%，H1暴露控制须按条件子样本+旗标设计。 (关键控制变量口径修正，影响H1暴露控制设计。) [[00 工作台/项目/共同所有权 × 产品召回/90 AI drafts/实证分析设计 - H2 time-to-recall - 共同所有权 × 产品召回.md]]

### Date: 2026-08-03

🟢 **常规进展 / 阅读记录**
- [#理论] 新增Vidal & Mitchell (2015)论文，探讨绩效反馈与资产剥离的资源重构关系。 (引入新锚文，扩展绩效反馈理论在资产剥离中的应用，对理论框架有实质推进。) [[00 工作台/叙述模板训练集/_parsed_texts/mvp30/EBSCO-FullText-08_03_2026.md]]

### Date: 2026-07-21

🔴 **理论突破 / 重大决策**
- [#产品召回] 药品FAERS ASCII全量下载完成，nb15 notebook执行通过 (M5药品端关键数据底座建成，项目里程碑) [[00 工作台\项目\共同所有权 × 产品召回\00 Active\Plan - nb15 FAERS 药品不良事件匹配 - 2026-07-21.md]]

🟡 **方法决策 / 写作判断**
- [#产品召回] 药品FAERS匹配方案从API反查改为全量ASCII下载+药名匹配 (核心方法口径变更，绕过API配额硬约束，影响后续所有药品端分析) [[00 工作台\项目\共同所有权 × 产品召回\00 Active\Plan - nb15 FAERS 药品不良事件匹配 - 2026-07-21.md]]
- [#产品召回] 药品匹配键从NDC精确匹配降级为generic/brand级，精度降级需声明 (核心变量测量方案变更，影响与Wowak可比性和论文声明) [[00 工作台\项目\共同所有权 × 产品召回\00 Active\Plan - nb15 FAERS 药品不良事件匹配 - 2026-07-21.md]]
- [#产品召回] FAERS ASCII字段映射与Wowak筛选口径对齐完成 (核心假设验证（API不可行）后新方案落地，方法学推进) [[00 工作台\项目\共同所有权 × 产品召回\00 Active\Plan - nb15 FAERS 药品不良事件匹配 - 2026-07-21.md]]

### Date: 2026-07-07

🟢 **常规进展 / 阅读记录**
- [#方法论] Batch 13 完成 Lashley & Pollock 2020 定性过程研究解构，扩展方法论覆盖范围 (新增定性过程研究方法论模板，补全了定量方法之外的证据层) [[00 工作台/叙述模板训练集/narrative_analysis/methods_results/mvp30/fine_grained/batch_13_lashley_pollock2020/lashley_pollock2020_waiting_to_inhale_fine_methods_results.md]]
- [#方法论] 更新了全部22篇语料库和运行时桥接文件，整合Batch 13内容 (常规语料库整合与ID桥接更新，无实质性理论或方法判断变化) [[00 工作台/叙述模板训练集/narrative_analysis/methods_results/mvp30/fine_grained/_all_22_expression_corpus_methods_results.md]]

### Date: 2026-06-23

🟡 **方法决策 / 写作判断**
- [#产品召回] [[项目作战室 - 共同所有权 × 产品召回]] [[00 工作台\项目\共同所有权 × 产品召回\90 AI drafts\Introduction front-end 草稿 - 共同所有权 × 产品召回.md]]

### Date: 2026-06-20

🟡 **方法决策 / 写作判断**
- [#general] Rising income inequality has intensified scrutiny of how corporations distribute wealth, yet we understand little about how executives’ formative life experiences shape these strategic choices. We focus on the military—a “total institution” that presents a unique theoretical puzzle. Military service [[00 工作台\项目\从军经验 × 薪酬差距\Manuscript - Military Experience × Pay Gap.md]]

### Date: 2026-06-02

🟡 **方法决策 / 写作判断**
- [#产品召回] Introduction Packet 修正文献定位，明确Darby和Wowak为锚文 (文献定位修正影响Gap表述和理论贡献声明，属于写作关键修改) [[00 工作台\项目\CEO regulatory focus × time to recall\00 Active\Introduction Packet - CEO regulatory focus × time to recall.md]]

### Date: 2026-05-29

🔴 **理论突破 / 重大决策**
- [#产品召回] CEO regulatory focus × time to recall 项目完成初稿 (项目里程碑：完成初稿，进入投稿准备阶段) [[00 工作台\项目\CEO regulatory focus × time to recall\EN\Manuscript - CEO regulatory focus × time to recall.md]]

### Date: 2026-05-26

🔴 **理论突破 / 重大决策**
- [#产品召回] CEO regulatory focus × recall 论文初稿完成 (项目里程碑：基准回归跑通，初稿完成) [[00 工作台\项目\CEO regulatory focus × time to recall\EN\Manuscript - CEO regulatory focus × time to recall.md]]
- [#方法论] 叙述模板训练集新增三篇论文的精细理论/引言分析 (方法论训练集实质性推进，识别新理论架构类型) [[00 工作台\叙述模板训练集\narrative_analysis\theory\mvp30\fine_grained\batch_2026-05-26\han_pollock_paruchuri_smj_distilled_theory.md]]

### Date: 2026-05-27

🔴 **理论突破 / 重大决策**
- [#产品召回] 放弃omission/commission映射，改用新术语体系 (核心理论映射被推翻，术语体系变更，影响H1/H2方向) [[00 工作台\项目\CEO regulatory focus × time to recall\深度阅读笔记 - Crowe & Higgins (1997) regulatory focus 战略倾向.md]]

### Date: 2026-05-18

🔴 **理论突破 / 重大决策**
- [#产品召回] 项目锁定 count-primary / timing-conditional 结果架构 (核心结果架构从并列改为优先级顺序，是项目里程碑) [[00 工作台\项目\anti-SLAPP laws × product recall count and timing\00 Active\文献证据包 - anti-SLAPP laws × product recall count and timing.md]]
- [#产品召回] 机制口径锁定：ability/external revelation 为主线，incentive 为副线 (理论机制从双路径并列改为有主次的框架) [[00 工作台\项目\anti-SLAPP laws × product recall count and timing\90 AI drafts\机制编译笔记 - anti-SLAPP 如何影响召回数量与时机.md]]

### Date: 2026-05-19

🔴 **理论突破 / 重大决策**
- [#共同所有权] 共同所有权理论链收口：条件化框架取代单向主效应 (理论主张从平均效应转向威胁强度条件化，是核心理论框架的实质性推进) [[00 工作台\项目\共同所有权 × 产品召回\00 Active\Theory Evidence Chain - 共同所有权 × 产品召回.md]]

### Date: 2026-05-20

🔴 **理论突破 / 重大决策**
- [#产品召回] 确定paranoia项目叙事骨架：contingency而非主效应 (明确项目核心叙事为severity×paranoia交互，非主效应，属理论框架重大修正) [[00 工作台\项目\CEO paranoia × time to recall\00 Active\文献证据包 - CEO paranoia × time to recall.md]]

### Date: 2026-05-22

🔴 **理论突破 / 重大决策**
- [#共同所有权] Context Packet更新：理论框架明确为条件化框架，核心是action-threshold reweighting (理论框架从单向效应转向条件化框架是重大修正) [[00 工作台\项目\共同所有权 × 产品召回\00 Active\Context Packet - 共同所有权 × 产品召回.md]]

### Date: 2026-05-23

🟡 **方法决策 / 写作判断**
- [#方法论] Slot-aligned verification demo展示真空输出与注入事实的精度差异，暴露Darby2023设计细节 (方法验证：揭示模板幻觉风险，明确需处理recurrent-event和GLM) [[00 工作台/项目/CEO regulatory focus × time to recall/EN/90 AI drafts/EN/slot_aligned_verification.md]]

### Date: 2026-05-24

🔴 **理论突破 / 重大决策**
- [#产品召回] Literature Dialogue 补全完成，进入 full manuscript consistency pass (项目里程碑：文献对话补全后进入手稿一致性检查阶段) [[00 工作台\项目\CEO regulatory focus × time to recall\00 Active\项目作战室 - CEO regulatory focus × time to recall.md]]

### Date: 2026-05-19

🔴 **理论突破 / 重大决策**
- [#CEO paranoia] Theory Packet 新增 Darby et al. (2026) 作为外部治理对照锚 (引入外部治理对照锚，强化内部认知路径的理论区分) [[00 工作台\项目\CEO paranoia × time to recall\00 Active\Theory Packet - CEO paranoia × time to recall.md]]

🟡 **方法决策 / 写作判断**
- [#CEO regulatory focus] Methods Packet 新增 Darby et al. (2026) 作为外部治理基准锚 (引入新锚文校准测量、方法和效应量，提升方法可信度) [[00 工作台\项目\CEO regulatory focus × time to recall\00 Active\Methods and Results Packet - CEO regulatory focus × time to recall.md]]

### Date: 2026-05-20

🟡 **方法决策 / 写作判断**
- [#产品召回] 建立paranoia与overconfidence/regulatory focus的构念区分笔记 (明确构念区分路径，支撑discriminant validity论证) [[00 工作台\项目\CEO paranoia × time to recall\90 AI drafts\关联文献地图 - CEO paranoia × time to recall.md]]

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

### Date: 2026-05-23

🔴 **理论突破 / 重大决策**
- [#产品召回] Qian et al. (2024) 确认regulatory focus可稳健进入安全决策，为recall timing提供近邻证据 (核心假设验证：regulatory focus→harm-reducing action迁移成立) [[00 工作台/项目/CEO regulatory focus × time to recall/深度阅读笔记 - Qian et al (2024) JOM workplace safety.md]]

🟡 **方法决策 / 写作判断**
- [#产品召回] Introduction outline完成，绑定narrative slots到具体文献和模板，明确gap类型为Incompleteness (项目里程碑：写作框架确定，gap定位和贡献声明已绑定) [[00 工作台/项目/CEO regulatory focus × time to recall/EN/Section Outlines/introduction_outline.md]]
- [#产品召回] Discussion、Methods、Results、Theory四个outline创建为占位符，约束条件已写入 (写作框架扩展，但内容尚未填充) [[00 工作台/项目/CEO regulatory focus × time to recall/EN/Section Outlines/discussion_outline.md]]

### Date: 2026-05-24

🔴 **理论突破 / 重大决策**
- [#general] Literature Dialogue 新增 Shi et al. (2026) 和 Wu et al. (2026) 两篇锚文 (新增关键文献，扩展了理论对话（语言机制和绩效反馈）) [[00 工作台\项目\CEO regulatory focus × time to recall\EN\Literature Dialogue.md]]
- [#产品召回] Claim Cards EN 完成4个核心主张的英文表述和机制描述 (核心主张的正式英文表述，支撑理论写作) [[00 工作台\项目\CEO regulatory focus × time to recall\EN\Claim Cards EN.md]]

🟡 **方法决策 / 写作判断**
- [#产品召回] Context Packet EN 完成术语锁定和核心主张定义 (术语锁定和核心主张定义是写作的关键基础) [[00 工作台\项目\CEO regulatory focus × time to recall\EN\Context Packet EN.md]]

### Date: 2026-05-12

🔴 **理论突破 / 重大决策**
- [#产品召回] 共同所有权项目的理论框架从"加速vs延迟"二元对立改为"条件化框架"——外部威胁高时spillover-internalization占优，威胁低时anticompetitive占优。参考 Kini et al. (2024)。

🟡 **方法决策 / 写作判断**
- [#共同所有权] 确定使用 MHHI delta 作为共同所有权测量，放弃 HHCO（He & Huang 2017），因为 MHHI delta 在反竞争文献中更成熟。
- [#竞业协议] anti-SLAPP 项目改用 staggered DiD + event study，放弃 simple DiD，因为州级采纳时间不同。

### Date: 2026-05-13

🔴 **理论突破 / 重大决策**
- [#CEO paranoia] CEO paranoia 和 CEO regulatory focus 两个项目共享同一套 recall timing 结果变量和 IV 方法，但理论机制完全不同——前者是心理认知路径，后者是动机聚焦路径。

🟡 **方法决策 / 写作判断**
- [#方法论] 确定所有 recall 项目统一使用 time to recall 作为核心结果，recall count 仅作扩展。

### Date: 2026-05-14

🟡 **方法决策 / 写作判断**
- [#共同所有权] FirmAwarenessDate 口径确认：以 NHTSA 首次公开披露日期为准，而非企业内部知晓日期。
- [#竞业协议] IDD × 广告支出项目确认 staggered DiD 设计，但需处理多期处理效应的异质性问题。

### Date: 2026-05-15

🟡 **方法决策 / 写作判断**
- [#产品召回] 多个项目（共同所有权、anti-SLAPP、CEO paranoia）都遇到 recall timing 的 left-censoring 问题，需统一处理方案。

### Date: 2026-05-16

🔴 **理论突破 / 重大决策**
- [#跨专题] 发现产品召回专题下的四个项目（共同所有权、anti-SLAPP、CEO paranoia、CEO regulatory focus）可以共享同一套 recall 数据基础设施，包括 NHTSA 数据清洗、FirmAwarenessDate 定义、left-censoring 处理。

🟡 **方法决策 / 写作判断**
- [#方法论] 决定所有 recall 项目统一使用 Cox 比例风险模型作为 survival analysis 基准，而非简单的 OLS 对数转换。
