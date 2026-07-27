---
type: skill_bridge
note_id: infra-skill-roots
created: 2026-05-20
status: active
---

# SKILL_ROOTS.md — Skill 实体根目录

本目录是索引和桥接层，不保存完整 skill 实现。实体 skill 存放在 Claude Code 或 Codex 的原生 skill root 中。

## 根目录

| Runtime | Root | 用途 |
|---|---|---|
| Claude Code | `C:\Users\admin\.claude\skills` | 学术 skill 的主源目录 |
| Codex | `C:\Users\admin\.codex\skills` | Codex 原生自动触发目录 |
| Academic bridge | `C:\Users\admin\.claude\academic_infrastructure\rules\skills` | 路由索引、安装状态和同步规则 |

## 规则

- `rules/skills` 只保存索引、路径、安装状态和同步政策。
- 不在 `rules/skills` 保存完整 SOP、脚本、模板或长参考材料。
- 新 skill 先创建为目录型实体 skill：`<root>\<skill-name>\SKILL.md`。
- `SKILL.md` 必须包含 `name` 和 `description` frontmatter。
- 高频且需要 Codex 自动触发的 skill，同步到 `C:\Users\admin\.codex\skills`。
- 低频或 Claude 专用 skill，可以只保留在 `C:\Users\admin\.claude\skills`，Codex 通过本索引按路径读取。

## 更新流程

1. 在实体 skill root 中创建或更新 `SKILL.md`。
2. 如需 Codex 原生触发，将该 skill 同步到 Codex root。
3. 更新 `SKILL_INDEX.md` 的触发场景、输出、Claude 状态和 Codex 状态。
4. 不把完整 skill 内容复制回 `rules/skills`。
