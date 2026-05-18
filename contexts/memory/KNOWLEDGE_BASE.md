---
type: sop
note_id: infra-knowledge-base
created: 2026-05-18
status: active
---

# KNOWLEDGE_BASE.md — 记忆系统标准操作流程

## 三层记忆架构

```
L3（全局约束）: C:\Users\admin\.claude\academic_infrastructure\rules\  → 每次 session 被动加载
L1/L2（动态记忆）: contexts/memory/OBSERVATIONS.md  → agent 主动检索
L0（原始数据）: contexts/memory/daily_raw/  → observer.py 采集的原始 YAML
```

## Observer 操作手册

### 目的
每日扫描用户的学术研究活动，提取可记录的决策、发现和进展。

### 输入源（按优先级）

1. **`D:\Onedrive\Obsidian Vault\daily\`** — 每日研究日志（如果存在）
2. **`D:\Onedrive\Obsidian Vault\meeting_notes\`** — 会议/合作讨论记录
3. **`D:\Onedrive\Obsidian Vault\00 工作台\项目\`** — 项目 Context Packets（检测修改）
4. **`D:\Onedrive\Obsidian Vault\00 工作台\今日推进清单.md`** — 每日优先级变化
5. **`D:\Onedrive\Obsidian Vault\00 工作台\知识库操作日志.md`** — 知识库变更记录

### 采集逻辑（observer.py）

1. 扫描上述目录，提取当日（或指定日期）的新增/修改内容
2. 按文件类型分类：
   - `project_change`: Context Packet、作战室、章节-证据映射的修改
   - `literature_read`: 新文献笔记、原子化笔记
   - `writing_progress`: 论文段落、审稿回复的写作
   - `method_decision`: 识别策略、变量测量、模型设定的变更
   - `theory_breakthrough`: 理论框架、机制推导、假设修正
   - `routine`: 日常阅读、整理、索引更新
3. 写入 `daily_raw/YYYY-MM-DD.yaml`

### AI 分析逻辑（Claude cron 或手动触发）

读取 `daily_raw/YYYY-MM-DD.yaml`，按以下规则标记优先级：

| 优先级 | 标记 | 判断标准 |
|--------|------|---------|
| 🔴 高 | theory_breakthrough / major_decision | 改变理论框架、识别策略、或项目方向 |
| 🟡 中 | method_decision / writing_judgment | 影响实证可信度或写作质量的判断 |
| 🟢 低 | routine / reading_progress | 日常进展，无重大决策 |

### 输出格式

追加到 `OBSERVATIONS.md`：

```markdown
### Date: 2026-05-18

🔴 **理论突破**
- [#产品召回] 重新框架化 CEO regulatory focus → 召回时机机制，从"监管压力"转向"注意力分配机制"。见 [[Context Packet - CEO regulatory focus × time to recall]]

🟡 **方法决策**
- [#方法论] 决定使用 Callaway-Sant'Anna 替代传统 TWFE，处理 staggered adoption 的异质性处理效应

🟢 **常规进展**
- [#竞业协议] 完成 3 篇 Anti-SLAPP 相关文献的原子化笔记
```

## Reflector 操作手册

### 目的
每周分析 L1 观察，执行"记忆垃圾回收"和"洞察晋升"。

### 输入
`OBSERVATIONS.md` 最近 7 天的 🔴 和 🟡 条目。

### 处理流程

1. **读取**：提取上周所有 🔴 和 🟡 观察
2. **分析**：
   - 是否存在跨项目的重复模式？
   - 是否有理论判断被多次验证或修正？
   - 是否有方法决策可以被固化为最佳实践？
   - 是否有写作模式反复出现？
3. **晋升判断**：
   - **cross-project general**: 是否出现在 2+ 个项目中？
   - **multi-time verified**: 是否在 2+ 周内被验证？
   - **clear applicable scenario**: 是否有明确的触发场景？
   - 三者满足其二 → 晋升为 L3 公理或技能建议
4. **GC（垃圾回收）**：
   - 已晋升为公理的 🔴 条目 → 删除
   - 已过时或失效的 🟡 条目 → 删除
   - 🟢 条目保留 30 天后自动清理
5. **输出**：
   - 更新 `rules/axioms/`（如必要）
   - 重写 `OBSERVATIONS.md`（移除已晋升条目）
   - 写入 `contexts/thought_review/weekly_reflection_YYYY-MM-DD.md`

### 晋升阈值

| 晋升目标 | 条件 | 示例 |
|---------|------|------|
| 新公理 | 跨项目 + 多次验证 + 清晰场景 | "每次做 DiD 都必须检查平行趋势图形" |
| 技能建议 | 同一类任务反复出现 + 有优化空间 | "写 Introduction 时先填 Simsek 六 Block" |
| USER.md 更新 | 研究偏好/品味变化 | 新增目标期刊、工具链变更 |
| WORKSPACE.md 更新 | 目录结构/路由变化 | 新增项目、专题重组 |

### 反射报告格式

```markdown
# Weekly Reflection: 2026-05-11 to 2026-05-18

## 本周关键观察
- 3 条 🔴, 5 条 🟡

## 跨项目模式
- [模式名称] 描述。触发场景：[场景]。建议固化为：[公理/技能/无]

## 晋升建议
- [建议1] → 新公理 `eXX_xxx` / 更新现有公理
- [建议2] → 新技能建议

## 已执行 GC
- 移除 [N] 条已晋升/过期观察

## 下周关注
- [提醒事项]
```

## Idempotency（幂等性）

- Observer: 如果 `OBSERVATIONS.md` 中已存在 `Date: YYYY-MM-DD`，跳过该日
- Reflector: 如果 `thought_review/weekly_reflection_YYYY-MM-DD.md` 已存在，跳过该周

## Windows 兼容性

- 不使用 `fcntl`（Unix-only）
- 文件锁：使用 `portalocker` 库，或采用简单的"写入临时文件 + 原子重命名"策略
- 路径处理：使用 `pathlib.Path`，避免硬编码分隔符
