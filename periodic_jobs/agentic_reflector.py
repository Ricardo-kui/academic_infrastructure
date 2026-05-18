#!/usr/bin/env python3
"""
agentic_reflector.py — DeepSeek-powered Agentic Reflector for academic infrastructure.

Reads OBSERVATIONS.md, extracts 🔴/🟡 entries from the last 7 days,
sends to LLM for semantic analysis, receives structured promotion suggestions
and GC plans, writes weekly reflection report.

Promotions are written as DRAFTS to contexts/thought_review/promotions/,
requiring human confirmation before moving to rules/.

Usage:
    python agentic_reflector.py [YYYY-MM-DD] [--dry-run] [--force]
    python agentic_reflector.py --test  # API connectivity test

Fallback: If LLM API fails, falls back to rule-based reflector.py.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

from llm_client import LLMClient

# ── Configuration ──────────────────────────────────────────────────────────

INFRA_DIR = Path("C:/Users/admin/.claude/academic_infrastructure")
OBSERVATIONS_PATH = INFRA_DIR / "contexts" / "memory" / "OBSERVATIONS.md"
REFLECTION_DIR = INFRA_DIR / "contexts" / "thought_review"
PROMOTIONS_DIR = REFLECTION_DIR / "promotions"
RULES_DIR = INFRA_DIR / "rules"
AXIOMS_DIR = RULES_DIR / "axioms"
SKILLS_DIR = RULES_DIR / "skills"

MAX_OBS_CHARS = 80_000  # ~40K tokens budget for observations

# ── Prompts ────────────────────────────────────────────────────────────────

REFLECTOR_SYSTEM_PROMPT = """你是一个学术研究基础设施的"记忆反思与晋升"专家。你的任务是将 L2（动态观察）中有价值的内容晋升为 L3（全局约束/公理/技能）。

## 晋升职责边界

| 目标文件 | 内容类型 | 示例 |
|---------|---------|------|
| `rules/axioms/` | 可执行的决策原则 | "识别策略可信度优先于系数显著性" |
| `rules/skills/` | 技术方法论/工作流模板 | "DiD 稳健性检验清单" |
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
      "reason": "为什么值得晋升（引用具体观察）",
      "draft_content": "如果是 axiom：完整 frontmatter + 正文；如果是 user_update：要追加的段落"
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
        "- [ ] Apply approved promotions to `rules/`",
        "- [ ] Run GC on OBSERVATIONS.md (remove entries marked for deletion)",
        "",
    ])

    return "\n".join(lines)


def write_promotion_drafts(promotions: list[dict], end_date: str) -> list[Path]:
    """Write promotion drafts to promotions/ dir for human review."""
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

        content = f"""---
type: promotion_draft
status: pending_review
confidence: {conf}
promotion_type: {ptype}
target_file: {promo.get('target_file', 'N/A')}
generated_at: {datetime.now().isoformat()}
period_end: {end_date}
---

# Promotion Draft {idx}: {ptype} ({conf})

## Reason

{promo.get('reason', 'N/A')}

## Draft Content

{draft}

## Action Required

- [ ] Review draft for accuracy and alignment
- [ ] If approved: copy/modify into `{promo.get('target_file', 'target file')}`
- [ ] If rejected: delete this file or move to `contexts/thought_review/rejected/`
"""
        path.write_text(content, encoding="utf-8")
        written.append(path)

    return written


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

    print("[*] Done.")
    return 0


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
