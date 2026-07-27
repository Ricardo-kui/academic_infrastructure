---
type: workspace
note_id: infra-academic-workspace
created: 2026-05-18
status: active
---

# ACADEMIC_WORKSPACE.md — 学术工作区目录路由

## 职责边界

本文件只回答“去哪里找、去哪里放”。它不解释研究主题，不保存用户画像，不记录项目阶段，也不维护资产数量。

找任何学术文件前先查这里；如果这里只能定位到入口，再按 Vault 的读取协议继续向下查。

## 双层架构

- **全局层**：`C:\Users\admin\.claude\academic_infrastructure\`
  存放跨项目规则、技能、公理、记忆、周期任务和工具。
- **知识库层**：`D:\Onedrive\Obsidian Vault\`
  存放文献、概念、论证卡、项目材料、证据包和日常研究记录。

## 全局层路由

| 内容 | 路径 |
|---|---|
| AI 身份与行动边界 | `rules/ACADEMIC_SOUL.md` |
| 用户长期画像 | `rules/ACADEMIC_USER.md` |
| 沟通与默认 prose 风格 | `rules/ACADEMIC_COMMUNICATION.md` |
| 学术公理索引 | `rules/axioms/INDEX.md` |
| 学术技能路由 | `AGENTS.md` Skill Dispatch 表（项目上下文） |
| 动态观察记忆 | `contexts/memory/OBSERVATIONS.md` |
| 记忆系统说明 | `contexts/memory/KNOWLEDGE_BASE.md` |
| 周期反思 | `contexts/thought_review/` |
| 周期脚本 | `periodic_jobs/` |
| 语义搜索工具 | `tools/semantic_search/` |
| 项目仪表板 | `tools/project_dashboard.py` |
| 跨专题桥接检测 | `tools/bridge_detector.py` |
| 统一 CLI | `tools/academic_cli.py` |

## Vault 入口

| 用途 | 路径 |
|---|---|
| 全局索引 | `D:\Onedrive\Obsidian Vault\index.md` |
| 读取协议 | `D:\Onedrive\Obsidian Vault\00 工作台\Claude 读取协议.md` |
| 三层语料协议 | `D:\Onedrive\Obsidian Vault\三层语料协议与默认检索顺序.md` |
| 项目材料根目录 | `D:\Onedrive\Obsidian Vault\00 工作台\项目\` |
| 结构化文献笔记 | `D:\Onedrive\Obsidian Vault\literature\` |
| 概念库 | `D:\Onedrive\Obsidian Vault\概念库\` |
| 论证卡库 | `D:\Onedrive\Obsidian Vault\论证卡库\` |
| 原子化深读笔记 | `D:\Onedrive\Obsidian Vault\文献笔记库\02 原子化\` |
| PDF 证据摘录 | `D:\Onedrive\Obsidian Vault\PDF evidence extracts\` |

## 专题入口

| 专题 | Vault 根目录 |
|---|---|
| 产品召回 | `D:\Onedrive\Obsidian Vault\产品召回\` |
| 共同所有权 | `D:\Onedrive\Obsidian Vault\共同所有权\` |
| 竞业协议 | `D:\Onedrive\Obsidian Vault\竞业协议\` |

## 项目材料约定

项目材料默认存放在 `00 工作台\项目\`。常见文件包括：

- `Context Packet - <项目名>.md`
- `项目作战室 - <项目名>.md`
- `章节-证据映射 - <项目名>.md`
- `Evidence Audit - <项目名>.md`
- `Intro/Theory/Methods/Results` 等专项 packet

推进具体项目时，优先读取该项目的 Context Packet 和项目作战室，再读取章节证据映射、Evidence Audit 和相关专题材料。

## 快速查询

| 我想要... | 先去 |
|---|---|
| 了解当前项目状态 | Vault `index.md` → `00 工作台\项目\` → 项目 Context Packet |
| 查理论构念定义 | Vault `index.md` → `概念库\` |
| 查变量测量 | 概念页 → 原子化笔记 → PDF evidence extracts |
| 找用户过往判断 | `contexts/memory/OBSERVATIONS.md` → Vault 问答归档/项目作战室 |
| 做文献检索或引用 | `AGENTS.md` Skill Dispatch → 文献/引用相关 skill |
| 设计识别策略 | `rules/axioms/INDEX.md` 的 e* 公理 → causal/DID/stata 相关 skill |
| 写或审论文 section | `AGENTS.md` Skill Dispatch → write/review/pollock 相关 skill |
| 跨专题找连接 | `tools/bridge_detector.py` → 对应专题入口 |

## 命名规则

- 全局层规则文件：英文大写或 snake_case，保持现有约定。
- Vault 文件名：保留中文命名和现有前缀。
- 新增结构化笔记 frontmatter 至少包含 `type`、`note_id`、`created`。
- 不把临时项目状态写进 L3 规则文件；项目状态应留在 Vault 项目材料、dashboard 或动态记忆中。
