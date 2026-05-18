---
type: workspace
note_id: infra-academic-workspace
created: 2026-05-18
status: active
---

# ACADEMIC_WORKSPACE.md — 学术工作区目录路由

目标：让AI每轮session都能快速知道"去哪里找/放什么"。**找任何文件前先查这里。**

## 双层级架构

本工作区采用**双层架构**：
- **全局层**（`C:\Users\admin\.claude\academic_infrastructure\`）：AI身份、记忆、工具、公理 —— 跨项目通用
- **知识库层**（`D:\Onedrive\Obsidian Vault\`）：文献、概念、项目、证据 —— 内容资产

## 全局层路由

| 内容类型 | 位置 | 说明 |
|---------|------|------|
| AI身份与行为 | `rules/ACADEMIC_SOUL.md` | 核心真理、agent原则、思考框架 |
| 用户画像 | `rules/ACADEMIC_USER.md` | 研究风格、工具链、项目列表 |
| 写作风格 | `rules/ACADEMIC_COMMUNICATION.md` | 中英文学术 prose QC |
| 学术公理 | `rules/axioms/` | 理论与方法决策原则 |
| 技能索引 | `rules/skills/SKILL_INDEX.md` | 66个Claude Code技能路由 |
| 动态记忆 | `contexts/memory/OBSERVATIONS.md` | L1/L2观察日志 |
| 周期反思 | `contexts/thought_review/` | 每周反思报告 |
| 观察脚本 | `periodic_jobs/observer.py` | 每日研究活动采集 |
| 反思脚本 | `periodic_jobs/reflector.py` | 每周洞察蒸馏 |
| 语义搜索 | `tools/semantic_search/` | Vault语义索引与检索 |
| 项目仪表板 | `tools/project_dashboard.py` | 活跃项目状态总览 |
| 桥接检测 | `tools/bridge_detector.py` | 跨专题理论桥接发现 |
| CLI入口 | `tools/academic_cli.py` | 统一命令行工具 |

## 知识库层路由（Obsidian Vault）

### 导航入口
- **全局索引**：`D:\Onedrive\Obsidian Vault\index.md`
- **读取协议**：`D:\Onedrive\Obsidian Vault\00 工作台\Claude 读取协议.md`
- **三层语料协议**：`D:\Onedrive\Obsidian Vault\三层语料协议与默认检索顺序.md`

### 专题底座
| 专题 | 根目录 | 文献地图 | 研究框架 |
|------|--------|----------|----------|
| 产品召回 | `产品召回/` | `产品召回 文献地图` | `产品召回 研究框架` |
| 共同所有权 | `共同所有权/` | `共同所有权 文献地图` | `共同所有权 研究框架` |
| 竞业协议 | `竞业协议/` | `竞业协议 文献地图` | `竞业协议 研究框架` |

### 核心资产目录
- **`literature/`**：343篇结构化文献笔记（citation_ready 290篇）
- **`概念库/`**：161篇概念页（全局概念 + 专题概念）
- **`论证卡库/`**：93篇论证卡（实体卡64张）
- **`00 工作台/项目/`**：5个活跃项目的Context Packet、作战室、证据包
- **`文献笔记库/02 原子化/`**：894篇单篇深读笔记（Tier 2证据层）
- **`PDF evidence extracts/`**：42篇页码级原文摘录

### 项目路由（活跃项目）
每个项目固定结构：
```
00 工作台/项目/
├── Context Packet - <项目名>.md        ← 项目总览与理论资产
├── 项目作战室 - <项目名>.md             ← 执行状态与待办
├── 章节-证据映射 - <项目名>.md          ← 写作结构与证据对应
├── Evidence Audit - <项目名>.md        ← 证据链审计
└── （各类Packet：Intro/Theory/Methods）
```

### 周期记录
- **`daily/`**：每日研究日志（当前为空，待启用）
- **`meeting_notes/`**：会议/合作讨论记录
- **`00 工作台/今日推进清单.md`**：当前优先级
- **`00 工作台/知识库操作日志.md`**：知识库变更记录
- **`00 工作台/问答归档/`**：3+篇文献综合的问答沉淀

## 命名规则

- Vault内文件名：中文为主，保留现有前缀约定（`全局概念 - `、`产品召回 主题 - `等）
- frontmatter必须包含：`type`, `note_id`, `created`
- 全局层文件名：英文snake_case
- 索引文件：`INDEX.md`（公理）、`SKILL_INDEX.md`（技能）

## 快速查询

| 我想要... | 先去 |
|-----------|------|
| 了解用户当前项目状态 | `ACADEMIC_USER.md` → `index.md` → 活跃项目表 |
| 查某理论构念的定义 | `index.md` → 概念库节 → `全局概念 - <概念>` |
| 找某变量的测量方式 | `index.md` → 二手数据变量测度 / 概念页测量节 |
| 推进某个具体项目 | `index.md` → 活跃项目 → Context Packet |
| 跨专题理论桥接 | `tools/bridge_detector.py` 或 `跨专题桥接假设.md` |
| 跑回归/写Stata | 调用 `stata-regression` / `econometrics-agent` skill |
| 写论文某section | 调用对应 `write-` skill，按 `paper-writing-stack` 路由 |
| 审查论文质量 | 调用 `pollock-qc` 或对应 `*-review` skill |
| 查新文献/管理引用 | 调用 `zotero-cli-cc` / `citation-management` skill |
| 将PDF转为文献笔记 | 调用 `literature-notes-obsidian` skill |
