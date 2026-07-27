#!/usr/bin/env python3
"""
agentic_reflector.py — DeepSeek-powered Agentic Reflector for academic infrastructure.

Reads OBSERVATIONS.md, extracts 🔴/🟡 entries from the last 7 days,
sends to LLM for semantic analysis, receives structured promotion suggestions
and GC plans, writes weekly reflection report.

Promotions are written as DRAFTS to contexts/thought_review/promotions/,
requiring human confirmation before applying to rules/ or native skill roots.

Usage:
    python agentic_reflector.py [YYYY-MM-DD] [--dry-run] [--force]
    python agentic_reflector.py --test  # API connectivity test

Fallback: If LLM API fails, falls back to rule-based reflector.py.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

from consolidate_observations import cleanup_observations_content
from llm_client import LLMClient

# ── Configuration ──────────────────────────────────────────────────────────

INFRA_DIR = Path("C:/Users/admin/.claude/academic_infrastructure")
OBSERVATIONS_PATH = INFRA_DIR / "contexts" / "memory" / "OBSERVATIONS.md"
REFLECTION_DIR = INFRA_DIR / "contexts" / "thought_review"
PROMOTIONS_DIR = REFLECTION_DIR / "promotions"
RULES_DIR = INFRA_DIR / "rules"
AXIOMS_DIR = RULES_DIR / "axioms"
SKILL_INDEX_PATH = RULES_DIR / "skills" / "SKILL_INDEX.md"
CLAUDE_SKILLS_ROOT = Path("C:/Users/admin/.claude/skills")
CODEX_SKILLS_ROOT = Path("C:/Users/admin/.codex/skills")

MAX_OBS_CHARS = 80_000  # ~40K tokens budget for observations

# ── Prompts ────────────────────────────────────────────────────────────────

REFLECTOR_SYSTEM_PROMPT = """你是一个学术研究基础设施的"记忆反思与晋升"专家。你的任务是将 L2（动态观察）中有价值的内容晋升为 L3（全局约束/公理/技能）。

## 晋升职责边界

| 目标文件 | 内容类型 | 示例 |
|---------|---------|------|
| `rules/axioms/` | 可执行的决策原则 | "识别策略可信度优先于系数显著性" |
| `C:\\Users\\admin\\.claude\\skills\\<skill-name>\\SKILL.md` | 原生 skill 实体 | "DiD 稳健性检验清单" |
| `C:\\Users\\admin\\.codex\\skills\\<skill-name>\\SKILL.md` | 高频或需 Codex 自动触发的 skill 同步副本 | "Stata 回归流水线" |
| `rules/skills/SKILL_INDEX.md` | skill 路由索引与 Claude/Codex 安装状态 | 只新增/更新索引行，不存完整 SOP |
| `rules/ACADEMIC_USER.md` | 用户画像更新 | 新增研究偏好、目标期刊变化 |
| `rules/ACADEMIC_COMMUNICATION.md` | 沟通风格调整 | 新增修辞禁忌、输出偏好 |
| `rules/ACADEMIC_SOUL.md` | Agent 核心价值观 | 极少数根本性身份调整 |

## 公理晋升门槛（必须同时满足）

1. **跨项目通用性**：观察中提到的原则在 2+ 个项目/专题中被验证
2. **多次验证**：至少 2 周（或 2+ 次独立场景）出现类似判断
3. **可执行性**：不是抽象建议，而是具体的决策规则（有明确 Yes/No 边界）
4. **有触发场景**：能用 3-5 个关键词描述何时调用这条公理

## 技能晋升门槛

1. 同一类技术任务反复出现 3+ 次
2. 形成可复用的步骤序列或检查清单
3. 有明确的输入-输出定义
4. target_file 必须是 Claude 原生 skill 目标：`C:\\Users\\admin\\.claude\\skills\\<kebab-skill-name>\\SKILL.md`
5. 如果该 skill 高频、跨 runtime 使用、或需要 Codex 自动触发，设置 `"codex_sync": true`；否则设置 false
6. 不要把完整 skill SOP 写入 `rules/skills/*.md`。`rules/skills` 只更新 `SKILL_INDEX.md` 路由状态

## 垃圾回收（GC）规则

- 🔴 **保留**：永远保留，但可标记为"已处理"
- 🟡 **保留 90 天**：90 天后若未晋升则删除
- 🟢 **保留 30 天**：30 天后自动删除
- **已晋升**：标记为 promoted，下次 GC 删除原文

## 输出格式

你必须输出严格的 JSON，不要 markdown 代码块标记：

{
  "weekly_analysis": "本周整体研究节奏与模式概述（200字内）",
  "promotions": [
    {
      "type": "axiom" | "skill" | "user_update" | "communication_update",
      "confidence": "high" | "medium" | "low",
      "target_file": "建议的文件路径",
      "skill_name": "仅 skill 类型需要；kebab-case",
      "codex_sync": false,
      "codex_target_file": "仅 codex_sync=true 时需要",
      "reason": "为什么值得晋升（引用具体观察）",
      "draft_content": "如果是 axiom：完整 frontmatter + 正文；如果是 skill：完整 SKILL.md，必须包含 name 和 description frontmatter；如果是 user_update：要追加的段落"
    }
  ],
  "gc_plan": {
    "entries_to_remove": [
      {"date": "YYYY-MM-DD", "summary": "条目摘要", "reason": "过期/已晋升/重复"}
    ],
    "entries_to_archive": [
      {"date": "YYYY-MM-DD", "summary": "条目摘要", "reason": "有价值但暂不晋升"}
    ]
  },
  "cross_project_insights": [
    "跨项目发现的模式或冲突（如：两个项目对同一方法的结论矛盾）"
  ]
}"""


def parse_observations(content: str) -> list[dict]:
    """Parse OBSERVATIONS.md into structured entries.

    Format expected:
        ### Date: YYYY-MM-DD

        🔴 **理论突破 / 重大决策**
        - [#标签] 内容摘要

        🟡 **方法决策 / 写作判断**
        - [#标签] 内容摘要
    """
    entries = []
    current_date = None
    current_priority = None

    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue

        date_match = re.match(r"###\s*Date:\s*(\d{4}-\d{2}-\d{2})", line)
        if date_match:
            current_date = date_match.group(1)
            current_priority = None
            continue

        # Detect priority from section header
        if line.startswith("🔴"):
            current_priority = "🔴"
            continue
        elif line.startswith("🟡"):
            current_priority = "🟡"
            continue
        elif line.startswith("🟢"):
            current_priority = "🟢"
            continue

        # Actual observation entries start with "- "
        if line.startswith("-") and current_date and current_priority:
            tag_match = re.search(r"(\[#[\w一-鿿]+\])", line)
            tag = tag_match.group(1) if tag_match else "#general"
            # Remove leading "- " and tag
            clean = re.sub(r"^-\s*", "", line).strip()
            clean = re.sub(r"\[#[\w一-鿿]+\]\s*", "", clean).strip()
            entries.append(
                {
                    "date": current_date,
                    "priority": current_priority,
                    "tag": tag,
                    "content": clean,
                    "line": line,
                }
            )

    return entries


def filter_week(entries: list[dict], end_date: str) -> list[dict]:
    end = datetime.strptime(end_date, "%Y-%m-%d")
    start = end - timedelta(days=7)
    return [
        e
        for e in entries
        if start <= datetime.strptime(e["date"], "%Y-%m-%d") <= end
    ]


def load_existing_axioms() -> str:
    """Load existing axiom titles for deduplication context."""
    if not AXIOMS_DIR.exists():
        return "（公理目录不存在）"

    lines = ["## 现有公理库（避免重复）\n"]
    for f in sorted(AXIOMS_DIR.glob("*.md")):
        if f.name == "INDEX.md":
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        # Extract title (first H1)
        m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        title = m.group(1) if m else f.name
        lines.append(f"- {f.name}: {title}")
    return "\n".join(lines)


def build_reflector_prompt(entries: list[dict], end_date: str) -> list[dict[str, str]]:
    """Construct the prompt messages for LLM."""
    # Separate by priority
    reds = [e for e in entries if e["priority"] == "🔴"]
    yellows = [e for e in entries if e["priority"] == "🟡"]
    greens = [e for e in entries if e["priority"] == "🟢"]

    obs_lines = [f"## 观察周期：{end_date} 及之前 7 天\n"]

    if reds:
        obs_lines.append("\n### [HIGH] 高优先级观察（理论突破 / 重大决策）")
        for e in reds:
            obs_lines.append(f"- [{e['date']}] {e['tag']} {e['content']}")

    if yellows:
        obs_lines.append("\n### [MED] 中优先级观察（方法决策 / 写作判断）")
        for e in yellows:
            obs_lines.append(f"- [{e['date']}] {e['tag']} {e['content']}")

    if greens:
        obs_lines.append(f"\n### [LOW] 低优先级观察（常规进展 / 阅读记录）— 共 {len(greens)} 条")
        # Only show a sample of greens to save tokens
        for e in greens[:5]:
            obs_lines.append(f"- [{e['date']}] {e['tag']} {e['content']}")
        if len(greens) > 5:
            obs_lines.append(f"- ... 还有 {len(greens) - 5} 条常规记录")

    observations_text = "\n".join(obs_lines)
    axioms_text = load_existing_axioms()

    user_prompt = f"""请分析以下本周学术观察记录，执行反思与晋升任务。

{observations_text}

{axioms_text}

## 任务

1. 分析本周 🔴/🟡 条目的共同模式
2. 判断是否有任何观察满足晋升门槛（跨项目、多次验证、可执行）
3. 如果有，输出完整的晋升草稿（axiom 请包含 frontmatter）
4. 生成 GC 计划（哪些已过期、哪些已处理完毕可删除）
5. 发现任何跨项目冲突或意外关联

请以 JSON 格式输出。"""

    # Truncate if too long
    if len(user_prompt) > MAX_OBS_CHARS * 2:
        user_prompt = user_prompt[:MAX_OBS_CHARS * 2] + "\n\n[内容过长，已截断]"

    return [
        {"role": "system", "content": REFLECTOR_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def parse_llm_json(response_text: str) -> dict:
    """Parse LLM's JSON response."""
    text = response_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            start = text.index("{")
            end = text.rindex("}") + 1
            return json.loads(text[start:end])
        except (ValueError, json.JSONDecodeError) as e:
            print(f"[!] Failed to parse JSON: {e}")
            print(f"[!] Raw response:\n{text[:1000]}")
            return {}


def normalize_promotion_targets(data: dict) -> dict:
    """Normalize promotion target paths after LLM output.

    Skill promotions now target native skill roots, not rules/skills/*.md.
    This keeps older model responses from recreating SOP files under rules/skills.
    """
    promotions = data.get("promotions", [])
    if not isinstance(promotions, list):
        data["promotions"] = []
        return data

    for promo in promotions:
        if not isinstance(promo, dict):
            continue
        if promo.get("type") == "skill":
            _normalize_skill_promotion(promo)
    return data


def _normalize_skill_promotion(promo: dict) -> None:
    skill_name = _infer_skill_name(promo)
    promo["skill_name"] = skill_name
    promo["target_file"] = str(CLAUDE_SKILLS_ROOT / skill_name / "SKILL.md")

    codex_sync = _truthy(promo.get("codex_sync"))
    if promo.get("codex_sync") is None:
        codex_sync = _default_codex_sync(promo)
    promo["codex_sync"] = codex_sync
    promo["codex_target_file"] = str(CODEX_SKILLS_ROOT / skill_name / "SKILL.md")
    promo["index_file"] = str(SKILL_INDEX_PATH)


def _infer_skill_name(promo: dict) -> str:
    for key in ("skill_name", "name"):
        raw = promo.get(key)
        if raw:
            slug = _slugify_skill_name(str(raw))
            if slug:
                return slug

    target = str(promo.get("target_file", "")).strip()
    candidate = _candidate_from_target_path(target)
    if candidate:
        slug = _slugify_skill_name(candidate)
        if slug:
            return slug

    draft = str(promo.get("draft_content", ""))
    heading = re.search(r"^#\s+(.+)$", draft, re.MULTILINE)
    if heading:
        slug = _slugify_skill_name(heading.group(1))
        if slug:
            return slug

    return "academic-workflow"


def _candidate_from_target_path(target: str) -> str:
    if not target:
        return ""
    normalized = target.replace("\\", "/").strip()
    parts = [p for p in normalized.split("/") if p]
    if not parts:
        return ""

    if parts[-1].lower() == "skill.md" and len(parts) >= 2:
        return parts[-2]

    filename = parts[-1]
    return re.sub(r"\.md$", "", filename, flags=re.IGNORECASE)


def _slugify_skill_name(value: str) -> str:
    value = value.strip()
    value = re.sub(r"\.md$", "", value, flags=re.IGNORECASE)
    value = re.sub(r"(?i)^skill:\s*", "", value)
    value = re.sub(r"(?i)^s\d+:\s*", "", value)
    value = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    value = re.sub(r"-+", "-", value)
    # Historical rules/skills files often used *_setup.md for a native skill
    # whose public name should not carry the implementation suffix.
    value = re.sub(r"-(setup|workflow|template)$", "", value)
    return value


def _truthy(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "y", "recommended", "需要", "是"}


def _default_codex_sync(promo: dict) -> bool:
    confidence = str(promo.get("confidence", "")).lower()
    text = " ".join(
        str(promo.get(k, ""))
        for k in ("reason", "draft_content", "target_file")
    ).lower()
    sync_keywords = ["codex", "自动触发", "原生", "高频", "频繁", "反复", "cross-runtime"]
    return confidence == "high" or any(k.lower() in text for k in sync_keywords)


def _yaml_quote(value: object) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def generate_report(data: dict, week_entries: list[dict], end_date: str) -> str:
    """Generate the weekly reflection markdown report."""
    start_date = (
        datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=7)
    ).strftime("%Y-%m-%d")

    analysis = data.get("weekly_analysis", "（无分析）")
    promotions = data.get("promotions", [])
    gc_plan = data.get("gc_plan", {})
    insights = data.get("cross_project_insights", [])

    lines = [
        "---",
        "type: weekly_reflection",
        "generated_by: agentic_reflector",
        f"period_start: {start_date}",
        f"period_end: {end_date}",
        f"generated_at: {datetime.now().isoformat()}",
        "---",
        "",
        f"# Weekly Reflection: {start_date} to {end_date}",
        "",
        "## AI Analysis",
        "",
        analysis,
        "",
        "## Overview",
        "",
        f"- Total observations: {len(week_entries)}",
        f"- [R] Breakthroughs: {sum(1 for e in week_entries if e['priority'] == '🔴')}",
        f"- [Y] Decisions: {sum(1 for e in week_entries if e['priority'] == '🟡')}",
        f"- [G] Routine: {sum(1 for e in week_entries if e['priority'] == '🟢')}",
        f"- Promotion suggestions: {len(promotions)}",
        "",
    ]

    # Cross-project insights
    if insights:
        lines.extend(["## Cross-Project Insights", ""])
        for insight in insights:
            lines.append(f"- {insight}")
        lines.append("")

    # Promotions
    if promotions:
        lines.extend(["## Promotion Suggestions", ""])
        for idx, promo in enumerate(promotions, 1):
            conf = promo.get("confidence", "medium")
            emoji = {"high": "[HI]", "medium": "[MED]", "low": "[LOW]"}.get(conf, "[MED]")
            lines.append(f"### {idx}. [{emoji} {conf.upper()}] {promo.get('type', 'unknown')} → `{promo.get('target_file', 'N/A')}`")
            lines.append("")
            if promo.get("type") == "skill":
                lines.append(f"**Skill name**: `{promo.get('skill_name', 'N/A')}`")
                lines.append(f"**Codex sync**: {'recommended' if promo.get('codex_sync') else 'optional'}")
                lines.append("")
            lines.append(f"**Reason**: {promo.get('reason', 'N/A')}")
            lines.append("")
            if promo.get("draft_content"):
                lines.append("**Draft content**:")
                lines.append("```markdown")
                lines.append(promo["draft_content"])
                lines.append("```")
                lines.append("")
            lines.append("---")
            lines.append("")
    else:
        lines.extend(["## Promotion Suggestions", "", "- No promotion suggestions this week.", ""])

    # GC Plan
    to_remove = gc_plan.get("entries_to_remove", [])
    to_archive = gc_plan.get("entries_to_archive", [])
    if to_remove or to_archive:
        lines.extend(["## GC Plan", ""])
        if to_remove:
            lines.append("### Entries to Remove")
            for entry in to_remove:
                lines.append(f"- [{entry.get('date', '?')}] {entry.get('summary', '')} — *{entry.get('reason', '')}*")
            lines.append("")
        if to_archive:
            lines.append("### Entries to Archive")
            for entry in to_archive:
                lines.append(f"- [{entry.get('date', '?')}] {entry.get('summary', '')} — *{entry.get('reason', '')}*")
            lines.append("")
    else:
        lines.extend(["## GC Plan", "", "- No GC actions suggested.", ""])

    # Next week focus
    lines.extend([
        "## Next Week Focus",
        "",
        "- [ ] Review promotion drafts in `contexts/thought_review/promotions/`",
        "- [ ] Confirm or reject AI-generated promotion suggestions",
        "- [ ] Apply approved axioms/user updates to `rules/`",
        "- [ ] Apply approved skills to native skill roots and update `rules/skills/SKILL_INDEX.md`",
        "- [ ] Run GC on OBSERVATIONS.md (remove entries marked for deletion)",
        "",
    ])

    return "\n".join(lines)


def write_promotion_drafts(promotions: list[dict], end_date: str) -> list[Path]:
    """Write promotion drafts to promotions/ dir for human review."""
    normalize_promotion_targets({"promotions": promotions})
    PROMOTIONS_DIR.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    for idx, promo in enumerate(promotions, 1):
        conf = promo.get("confidence", "medium")
        ptype = promo.get("type", "unknown")
        draft = promo.get("draft_content", "")
        if not draft:
            continue

        filename = f"{end_date}_promo_{idx:02d}_{ptype}_{conf}.md"
        path = PROMOTIONS_DIR / filename
        target_file = promo.get("target_file", "N/A")
        extra_frontmatter = _promotion_frontmatter_extra(promo)
        action_items = _promotion_action_items(promo)

        content = f"""---
type: promotion_draft
status: pending_review
confidence: {conf}
promotion_type: {ptype}
target_file: {_yaml_quote(target_file)}
{extra_frontmatter}generated_at: {datetime.now().isoformat()}
period_end: {end_date}
---

# Promotion Draft {idx}: {ptype} ({conf})

## Reason

{promo.get('reason', 'N/A')}

## Draft Content

{draft}

## Action Required

{action_items}
"""
        path.write_text(content, encoding="utf-8")
        written.append(path)

    return written


def _promotion_frontmatter_extra(promo: dict) -> str:
    if promo.get("type") != "skill":
        return ""
    fields = [
        ("skill_name", promo.get("skill_name", "")),
        ("codex_sync_recommended", "yes" if promo.get("codex_sync") else "no"),
        ("codex_target_file", promo.get("codex_target_file", "")),
        ("index_file", promo.get("index_file", str(SKILL_INDEX_PATH))),
    ]
    return "".join(f"{key}: {_yaml_quote(value)}\n" for key, value in fields if value)


def _promotion_action_items(promo: dict) -> str:
    if promo.get("type") != "skill":
        target = promo.get("target_file", "target file")
        return "\n".join([
            "- [ ] Review draft for accuracy and alignment",
            f"- [ ] If approved: copy/modify into `{target}`",
            "- [ ] If rejected: delete this file or move to `contexts/thought_review/rejected/`",
        ])

    target = promo.get("target_file", "target file")
    codex_target = promo.get("codex_target_file", "")
    index_file = promo.get("index_file", str(SKILL_INDEX_PATH))
    lines = [
        "- [ ] Review draft for accuracy, scope, and native skill frontmatter (`name`, `description`)",
        f"- [ ] If approved: create/update Claude native skill at `{target}`",
    ]
    if promo.get("codex_sync"):
        lines.append(f"- [ ] Sync the same skill to Codex at `{codex_target}`")
        lines.append(f"- [ ] Update `{index_file}` with Claude: yes and Codex: yes")
    else:
        lines.append(f"- [ ] If Codex native triggering is needed, sync to `{codex_target}`")
        lines.append(f"- [ ] Update `{index_file}` with Claude/Codex install status")
    lines.append("- [ ] Do not create a full SOP under `rules/skills/*.md`; keep `rules/skills` as index/bridge only")
    lines.append("- [ ] If rejected: delete this file or move to `contexts/thought_review/rejected/`")
    return "\n".join(lines)


def run_agentic_reflection(end_date: str, dry_run: bool = False, force: bool = False) -> int:
    """Run the full agentic reflection pipeline."""
    print(f"[*] Agentic Reflector for week ending {end_date}")
    print(f"[*] Reading from: {OBSERVATIONS_PATH}")

    if not OBSERVATIONS_PATH.exists():
        print(f"[error] Observations file not found: {OBSERVATIONS_PATH}")
        return 1

    content = OBSERVATIONS_PATH.read_text(encoding="utf-8")
    all_entries = parse_observations(content)
    week_entries = filter_week(all_entries, end_date)

    print(f"[*] Found {len(week_entries)} entries in the last 7 days")
    print(f"    [R] {sum(1 for e in week_entries if e['priority'] == '🔴')}")
    print(f"    [Y] {sum(1 for e in week_entries if e['priority'] == '🟡')}")
    print(f"    [G] {sum(1 for e in week_entries if e['priority'] == '🟢')}")

    if not week_entries:
        print("[*] No observations to reflect on.")
        return 0

    # Build prompt
    messages = build_reflector_prompt(week_entries, end_date)
    prompt_chars = sum(len(m["content"]) for m in messages)
    print(f"[*] Prompt size: ~{prompt_chars:,} chars (est. {prompt_chars // 2:,} tokens)")

    if dry_run:
        print("\n--- Prompt Preview (first 2000 chars) ---")
        print(messages[1]["content"][:2000])
        print("... (truncated)")
        return 0

    # Call LLM
    print("[*] Sending to LLM for reflection...")
    try:
        client = LLMClient()
        response = client.chat_completion(
            messages=messages,
            temperature=0.3,
            max_tokens=12000,
        )
    except Exception as e:
        print(f"[!] LLM API call failed: {e}")
        print("[!] Falling back to rule-based reflector.py...")
        # Fallback: call original reflector
        import subprocess
        result = subprocess.run(
            [sys.executable, str(INFRA_DIR / "periodic_jobs" / "reflector.py"), end_date],
            cwd=str(INFRA_DIR),
        )
        return result.returncode

    if hasattr(response, "content"):
        response_text = response.content
        usage_prompt = response.usage_prompt
        usage_completion = response.usage_completion
    else:
        response_text = str(response)
        usage_prompt = 0
        usage_completion = 0

    print(f"[*] LLM response received (prompt={usage_prompt}, completion={usage_completion})")
    if hasattr(response, "usage_prompt"):
        cost, currency = client.estimate_cost(response)
        print(f"[*] Est. cost: {cost:.4f} {currency}")

    # Parse JSON
    data = parse_llm_json(response_text)
    if not data:
        print("[!] Failed to parse LLM response. Writing raw response for manual inspection.")
        raw_path = REFLECTION_DIR / f"weekly_reflection_{end_date}_RAW.md"
        raw_path.write_text(response_text, encoding="utf-8")
        print(f"[write] Raw response saved to {raw_path}")
        return 1
    data = normalize_promotion_targets(data)

    # Generate report
    report = generate_report(data, week_entries, end_date)

    # Write reflection
    REFLECTION_DIR.mkdir(parents=True, exist_ok=True)
    reflection_path = REFLECTION_DIR / f"weekly_reflection_{end_date}.md"

    if reflection_path.exists() and not force:
        print(f"[skip] Reflection already exists: {reflection_path}")
        return 0

    reflection_path.write_text(report, encoding="utf-8")
    print(f"[write] {reflection_path}")

    # Write promotion drafts
    promotions = data.get("promotions", [])
    if promotions:
        drafts = write_promotion_drafts(promotions, end_date)
        print(f"[write] {len(drafts)} promotion draft(s) to {PROMOTIONS_DIR}")
        for d in drafts:
            print(f"    → {d.name}")
    else:
        print("[*] No promotion drafts generated.")

    # Execute GC on OBSERVATIONS.md
    gc_plan = data.get("gc_plan", {})
    if gc_plan.get("entries_to_remove"):
        n = execute_observations_gc(gc_plan, OBSERVATIONS_PATH)
        if n > 0:
            print(f"[gc] Removed {n} expired entries from OBSERVATIONS.md")
        else:
            print("[gc] No matching entries found for removal.")
    else:
        print("[*] No GC removals suggested.")

    hard_gc_stats = apply_hard_retention_gc(OBSERVATIONS_PATH)
    if hard_gc_stats and any(hard_gc_stats.values()):
        print(f"[gc] Applied hard retention rules: {hard_gc_stats}")
    else:
        print("[gc] No hard-retention cleanup needed.")

    # Auto-commit and push to GitHub (async, non-blocking)
    _git_auto_sync(end_date, [reflection_path, OBSERVATIONS_PATH] + [PROMOTIONS_DIR])

    print("[*] Done.")
    return 0


def execute_observations_gc(gc_plan: dict, observations_path: Path) -> int:
    """Delete entries from OBSERVATIONS.md that are marked for removal in the GC plan.

    Returns the number of entries removed.
    """
    to_remove = gc_plan.get("entries_to_remove", [])
    if not to_remove:
        return 0

    if not observations_path.exists():
        print("[!] OBSERVATIONS.md not found, skipping GC.")
        return 0

    lines = observations_path.read_text(encoding="utf-8").splitlines()
    removed = 0

    for entry in to_remove:
        entry_date = entry.get("date", "")
        summary = entry.get("summary", "")
        if not entry_date or not summary:
            continue

        # Find the matching line: must be within the correct date block
        in_target_date = False
        for i, line in enumerate(lines):
            if line is None:
                continue
            if line.strip().startswith(f"### Date: {entry_date}"):
                in_target_date = True
                continue
            if in_target_date and line.strip().startswith("### Date:"):
                in_target_date = False  # moved past this date block
                continue

            if in_target_date and line.strip().startswith("-"):
                # Check if summary is a substring of this entry (fuzzy)
                if _summary_matches(summary, line):
                    # Remove the entry line itself
                    lines[i] = None  # mark for deletion
                    # Also remove the following line if it's a continuation (starts with whitespace, not a section header or bullet)
                    j = i + 1
                    while j < len(lines) and lines[j] is not None:
                        trailing = lines[j].strip()
                        if trailing == "" or trailing.startswith("🔴") or trailing.startswith("🟡") or trailing.startswith("🟢") or trailing.startswith("###") or trailing.startswith("-"):
                            break
                        lines[j] = None
                        j += 1
                    removed += 1
                    break  # matched, move to next entry

    # Filter out None-marked lines
    cleaned = [l for l in lines if l is not None]

    # Clean up empty priority sections: if a 🔴/🟡/🟢 header has no bullet entries after it, remove the header
    result = []
    i = 0
    while i < len(cleaned):
        line = cleaned[i]
        stripped = line.strip()
        # Check if this is a priority header
        is_header = any(stripped.startswith(p) for p in ["🔴", "🟡", "🟢"])
        if is_header:
            # Look ahead: is there at least one "-" bullet before the next header or date?
            has_bullets = False
            for j in range(i + 1, len(cleaned)):
                ahead = cleaned[j].strip()
                if ahead.startswith("### Date:") or any(ahead.startswith(p) for p in ["🔴", "🟡", "🟢"]):
                    break
                if ahead.startswith("-"):
                    has_bullets = True
                    break
            if has_bullets:
                result.append(line)
            # else: skip this empty header
        else:
            result.append(line)
        i += 1

    # Collapse triple+ blank lines into double
    final = []
    blank_count = 0
    for line in result:
        if line.strip() == "":
            blank_count += 1
            if blank_count <= 2:
                final.append(line)
        else:
            blank_count = 0
            final.append(line)

    observations_path.write_text("\n".join(final) + "\n", encoding="utf-8")
    return removed


def apply_hard_retention_gc(observations_path: Path) -> dict[str, int]:
    """Apply non-negotiable retention rules independent of LLM GC suggestions."""
    if not observations_path.exists():
        return {}
    content = observations_path.read_text(encoding="utf-8")
    cleaned, stats = cleanup_observations_content(content)
    if cleaned != content:
        observations_path.write_text(cleaned, encoding="utf-8")
    return stats


def _summary_matches(summary: str, line: str) -> bool:
    """Check if a GC summary matches an observation line.

    Uses keyword overlap: if >= 60% of summary keywords appear in the line, it's a match.
    """
    # Extract meaningful keywords from summary (2+ char words, skip common words)
    stop = {"的", "了", "在", "是", "有", "和", "与", "或", "为", "等", "已", "从", "到", "将", "把",
            "a", "an", "the", "is", "are", "was", "were", "been", "be", "to", "of", "in", "for",
            "on", "with", "at", "by", "from", "as", "or", "and", "not", "but", "if", "so", "we",
            "it", "its", "they", "this", "that", "these", "those", "has", "have", "had", "do", "does"}
    keywords = [w for w in re.findall(r"[\w一-鿿]+", summary.lower())
                if len(w) >= 2 and w not in stop]
    if not keywords:
        return False
    line_lower = line.lower()
    hits = sum(1 for kw in keywords if kw in line_lower)
    return hits / len(keywords) >= 0.5


def _git_auto_sync(end_date: str, paths: list[Path]) -> None:
    """Commit and push reflector outputs to GitHub. Non-blocking, best-effort."""
    import subprocess

    repo = INFRA_DIR
    if not (repo / ".git").exists():
        print("[*] No git repo found, skipping auto-sync.")
        return

    try:
        # Stage specific paths
        for p in paths:
            if p.exists():
                subprocess.run(
                    ["git", "add", str(p.relative_to(repo))],
                    cwd=str(repo),
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
        # Check if there's anything to commit
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=str(repo),
            timeout=15,
        )
        if result.returncode == 0:
            print("[*] No changes to commit for auto-sync.")
            return

        # Commit
        msg = f"🤖 auto: weekly reflection {end_date} [agentic-reflector]"
        subprocess.run(
            ["git", "commit", "-m", msg],
            cwd=str(repo),
            capture_output=True,
            text=True,
            timeout=15,
        )
        print(f"[git] Committed: {msg}")

        # Push (async via background process so it doesn't block)
        subprocess.Popen(
            ["git", "push", "origin", "master"],
            cwd=str(repo),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print("[git] Push initiated (background).")
    except Exception as e:
        print(f"[!] Auto-sync failed (non-fatal): {e}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Agentic Reflector (LLM-powered)")
    parser.add_argument("date", nargs="?", help="End date of week (YYYY-MM-DD)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without calling API")
    parser.add_argument("--force", action="store_true", help="Overwrite existing reflection")
    parser.add_argument("--test", action="store_true", help="Quick API connectivity test")
    args = parser.parse_args()

    if args.test:
        print("[*] Testing LLM API connectivity...")
        try:
            client = LLMClient()
            resp = client.chat_completion(
                messages=[
                    {"role": "system", "content": "你是一个学术研究助手。"},
                    {"role": "user", "content": "请回复一句话确认API连接正常。"},
                ],
                temperature=0.0,
            )
            if hasattr(resp, "content"):
                print(f"[*] OK: {resp.content}")
                cost, currency = client.estimate_cost(resp)
                print(f"[*] Est. cost: {cost:.6f} {currency}")
        except Exception as e:
            print(f"[!] Test failed: {e}")
            return 1
        return 0

    if args.date:
        end_date = args.date
    else:
        end_date = datetime.now().strftime("%Y-%m-%d")

    return run_agentic_reflection(end_date, dry_run=args.dry_run, force=args.force)


if __name__ == "__main__":
    raise SystemExit(main())
