---
type: workspace
note_id: infra-academic-workspace
created: 2026-05-18
updated: 2026-07-27
status: active
---

# ACADEMIC_WORKSPACE.md — 学术工作区目录路由

## 职责边界

本文件只回答"去哪里找、去哪里放"。不解释研究主题，不记录项目阶段，不维护资产数量。

## 双层架构

- **全局层**：`C:\Users\admin\.claude\academic_infrastructure\` — 跨项目规则、公理、记忆、周期任务和工具。
- **知识库层**：`D:\Onedrive\Obsidian Vault\` — 文献、概念、论证卡、项目材料、证据包和日常研究记录。

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

## Agent 协作原则

给子任务或工具（Agent、Workflow、Skill、Bash）下达任务时，提供目标、上下文和质量标准，让执行者自行读取所需材料。不把 agent 当作简单 API，也不在 prompt 中塞入大量预处理上下文来替代它自己的检索和判断。

关注最终学术质量，而不是固定步骤是否被机械执行。若信息缺失，继续向下查原始笔记、PDF extract、数据字典或代码，不停在二手总结。
