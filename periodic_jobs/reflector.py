#!/usr/bin/env python3
"""
Academic Reflector — Weekly memory garbage collection and insight promotion.

Reads OBSERVATIONS.md, analyzes the last 7 days of 🔴/🟡 observations,
suggests promotions to axioms/skills, GCs expired entries, and writes
a weekly reflection report.

Usage:
    python reflector.py [YYYY-MM-DD]    # End date of the week (default: today)
    python reflector.py --dry-run       # Preview without writing
    python reflector.py --force         # Overwrite existing reflection
"""

import argparse
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────────────

INFRA_DIR = Path("C:/Users/admin/.claude/academic_infrastructure")
OBSERVATIONS_PATH = INFRA_DIR / "contexts" / "memory" / "OBSERVATIONS.md"
REFLECTION_DIR = INFRA_DIR / "contexts" / "thought_review"
AXIOMS_DIR = INFRA_DIR / "rules" / "axioms"

# Promotion thresholds
PROMOTION_RULES = {
    "axiom": {
        "min_projects": 2,      # Appears in 2+ project tags
        "min_weeks": 2,         # Verified across 2+ weeks
        "min_severity": "🔴",   # At least one 🔴 observation
    },
    "skill_suggestion": {
        "min_occurrences": 3,   # Same task type appears 3+ times
        "min_severity": "🟡",   # At least 🟡
    },
    "user_update": {
        "triggers": ["目标期刊", "工具链", "研究方法偏好", "合作者"],
    },
}

# GC rules
GC_RULES = {
    "promoted": "remove",           # Already promoted → delete
    "🔴": "keep",                   # Always keep 🔴
    "🟡": "keep_90d",               # Keep 🟡 for 90 days
    "🟢": "keep_30d",               # Keep 🟢 for 30 days
}

# ── Helpers ────────────────────────────────────────────────────────────────


def parse_observations(content: str) -> list[dict]:
    """Parse OBSERVATIONS.md into structured entries."""
    entries = []
    current_date = None

    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue

        # Detect date headers: "### Date: YYYY-MM-DD"
        date_match = re.match(r"###\s*Date:\s*(\d{4}-\d{2}-\d{2})", line)
        if date_match:
            current_date = date_match.group(1)
            continue

        # Detect priority markers
        priority = None
        if line.startswith("🔴"):
            priority = "🔴"
        elif line.startswith("🟡"):
            priority = "🟡"
        elif line.startswith("🟢"):
            priority = "🟢"

        if priority and current_date:
            # Extract tag and content
            tag_match = re.search(r"(\[#[\w一-鿿]+\])", line)
            tag = tag_match.group(1) if tag_match else "#general"

            # Clean line
            clean = re.sub(r"^[🔴🟡🟢]\s*\*?", "", line).strip()
            clean = re.sub(r"\[#[\w一-鿿]+\]\s*", "", clean).strip()

            entries.append(
                {
                    "date": current_date,
                    "priority": priority,
                    "tag": tag,
                    "content": clean,
                    "line": line,
                }
            )

    return entries


def filter_week(entries: list[dict], end_date: str) -> list[dict]:
    """Filter entries within 7 days before end_date."""
    end = datetime.strptime(end_date, "%Y-%m-%d")
    start = end - timedelta(days=7)

    return [
        e
        for e in entries
        if start <= datetime.strptime(e["date"], "%Y-%m-%d") <= end
    ]


def analyze_patterns(entries: list[dict]) -> dict:
    """Analyze cross-project and multi-time patterns."""
    patterns = {
        "by_tag": {},
        "by_type": {},
        "cross_project": [],
        "recurring": [],
    }

    for e in entries:
        tag = e["tag"]
        p = e["priority"]

        # Count by tag
        if tag not in patterns["by_tag"]:
            patterns["by_tag"][tag] = {"🔴": 0, "🟡": 0, "🟢": 0}
        patterns["by_tag"][tag][p] += 1

        # Detect activity type from content
        activity_type = "general"
        if any(k in e["content"] for k in ["理论", "机制", "假设", "theory", "mechanism", "hypothesis"]):
            activity_type = "theory"
        elif any(k in e["content"] for k in ["DiD", "IV", "识别", "稳健性", "变量", "identification", "robustness"]):
            activity_type = "methods"
        elif any(k in e["content"] for k in ["引言", "写作", "段落", "投稿", "审稿", "introduction", "writing", "submission"]):
            activity_type = "writing"

        if activity_type not in patterns["by_type"]:
            patterns["by_type"][activity_type] = []
        patterns["by_type"][activity_type].append(e)

    # Cross-project patterns: same activity type across 2+ tags
    for act_type, act_entries in patterns["by_type"].items():
        tags_involved = set(e["tag"] for e in act_entries)
        if len(tags_involved) >= 2 and len(act_entries) >= 3:
            patterns["cross_project"].append(
                {
                    "type": act_type,
                    "tags": sorted(tags_involved),
                    "count": len(act_entries),
                    "sample": act_entries[0]["content"][:120],
                }
            )

    # Recurring patterns: same keyword in 2+ entries
    keyword_counts: dict[str, list] = {}
    for e in entries:
        words = re.findall(r"[一-鿿]{2,6}|[a-zA-Z]{5,}", e["content"])
        for w in words:
            w = w.lower()
            if w not in keyword_counts:
                keyword_counts[w] = []
            keyword_counts[w].append(e)

    for kw, occ in keyword_counts.items():
        if len(occ) >= 3 and len(set(e["tag"] for e in occ)) >= 1:
            patterns["recurring"].append(
                {
                    "keyword": kw,
                    "count": len(occ),
                    "tags": sorted(set(e["tag"] for e in occ)),
                    "sample": occ[0]["content"][:120],
                }
            )

    # Sort recurring by count
    patterns["recurring"] = sorted(
        patterns["recurring"], key=lambda x: x["count"], reverse=True
    )[:10]

    return patterns


def generate_promotions(entries: list[dict], patterns: dict) -> list[dict]:
    """Generate promotion suggestions based on patterns."""
    promotions = []

    # Check cross-project patterns for axiom promotion
    for cp in patterns["cross_project"]:
        has_red = any(
            e["priority"] == "🔴" for e in patterns["by_type"].get(cp["type"], [])
        )
        if has_red:
            promotions.append(
                {
                    "type": "axiom_candidate",
                    "reason": f"Cross-project pattern: {cp['type']} observed in {', '.join(cp['tags'])} ({cp['count']} times)",
                    "suggested_id": f"auto_{cp['type']}_{datetime.now().strftime('%m%d')}",
                    "sample": cp["sample"],
                }
            )

    # Check recurring keywords for skill suggestions
    for rec in patterns["recurring"]:
        if rec["count"] >= 3:
            promotions.append(
                {
                    "type": "skill_suggestion",
                    "reason": f"Recurring activity '{rec['keyword']}' ({rec['count']} times) in {', '.join(rec['tags'])}",
                    "suggested_action": f"Consider creating a reusable workflow for '{rec['keyword']}'",
                    "sample": rec["sample"],
                }
            )

    return promotions


def generate_reflection_report(
    week_entries: list[dict], patterns: dict, promotions: list[dict], end_date: str
) -> str:
    """Generate the weekly reflection markdown report."""
    start_date = (
        datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=7)
    ).strftime("%Y-%m-%d")

    lines = [
        f"---",
        f"type: weekly_reflection",
        f"period_start: {start_date}",
        f"period_end: {end_date}",
        f"generated_at: {datetime.now().isoformat()}",
        f"---",
        f"",
        f"# Weekly Reflection: {start_date} to {end_date}",
        f"",
        f"## Overview",
        f"",
        f"- Total observations: {len(week_entries)}",
        f"- 🔴 Breakthroughs: {sum(1 for e in week_entries if e['priority'] == '🔴')}",
        f"- 🟡 Decisions: {sum(1 for e in week_entries if e['priority'] == '🟡')}",
        f"- 🟢 Routine: {sum(1 for e in week_entries if e['priority'] == '🟢')}",
        f"- Projects touched: {len(set(e['tag'] for e in week_entries))}",
        f"",
        f"## Activity by Project",
        f"",
    ]

    for tag, counts in sorted(patterns["by_tag"].items()):
        total = sum(counts.values())
        lines.append(f"- {tag}: {total} entries (🔴{counts['🔴']} 🟡{counts['🟡']} 🟢{counts['🟢']})")

    lines.extend(["", "## Cross-Project Patterns", ""])
    if patterns["cross_project"]:
        for cp in patterns["cross_project"]:
            lines.append(f"- **{cp['type']}** observed across {', '.join(cp['tags'])} ({cp['count']} times)")
            lines.append(f"  - Example: _{cp['sample']}_")
            lines.append("")
    else:
        lines.append("- No cross-project patterns detected this week.")

    lines.extend(["", "## Promotion Suggestions", ""])
    if promotions:
        for promo in promotions:
            lines.append(f"### [{promo['type']}] {promo.get('suggested_id', promo.get('suggested_action', ''))}")
            lines.append(f"- **Reason**: {promo['reason']}")
            lines.append(f"- **Sample**: _{promo['sample']}_")
            lines.append("")
            if promo["type"] == "axiom_candidate":
                lines.append("- **Action**: Consider formalizing into `rules/axioms/` if verified again next week.")
            elif promo["type"] == "skill_suggestion":
                lines.append("- **Action**: Consider adding to `rules/skills/SKILL_INDEX.md` or creating a reusable template.")
            lines.append("")
    else:
        lines.append("- No promotion suggestions this week.")

    lines.extend(["", "## Key Observations", ""])
    reds = [e for e in week_entries if e["priority"] == "🔴"]
    if reds:
        lines.append("### 🔴 Breakthroughs")
        for e in reds:
            lines.append(f"- **{e['date']}** [{e['tag']}] {e['content']}")
        lines.append("")

    yellows = [e for e in week_entries if e["priority"] == "🟡"]
    if yellows:
        lines.append("### 🟡 Key Decisions")
        for e in yellows[:5]:  # Limit to top 5
            lines.append(f"- **{e['date']}** [{e['tag']}] {e['content']}")
        lines.append("")

    lines.extend(["", "## Next Week Focus", "", "- [ ] Review promotion suggestions", "- [ ] Archive outdated 🟢 observations", "- [ ] Verify any pending 🔴 breakthroughs", ""])

    return "\n".join(lines)


def gc_observations(content: str, entries: list[dict]) -> str:
    """Perform garbage collection on OBSERVATIONS.md."""
    # For MVP, this is a simple mark-and-report
    # Full GC requires tracking which entries have been promoted
    now = datetime.now()
    lines = content.splitlines()
    result_lines = []
    removed_count = 0

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("🟢"):
            # Check if we can find a date for this line
            # Simple heuristic: keep all 🟢 for now, report would-be GC
            pass
        result_lines.append(line)

    return "\n".join(result_lines)


# ── CLI ────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Academic Reflector")
    parser.add_argument("date", nargs="?", help="End date of week (YYYY-MM-DD)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--force", action="store_true", help="Overwrite existing reflection")
    args = parser.parse_args()

    # Parse end date
    if args.date:
        end_date = args.date
    else:
        end_date = datetime.now().strftime("%Y-%m-%d")

    start_date = (
        datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=7)
    ).strftime("%Y-%m-%d")

    print(f"[*] Reflecting on week {start_date} to {end_date}...")

    # Read observations
    if not OBSERVATIONS_PATH.exists():
        print(f"[error] Observations file not found: {OBSERVATIONS_PATH}")
        sys.exit(1)

    content = OBSERVATIONS_PATH.read_text(encoding="utf-8")
    all_entries = parse_observations(content)
    week_entries = filter_week(all_entries, end_date)

    print(f"[*] Found {len(week_entries)} entries in the last 7 days")
    print(f"    🔴 {sum(1 for e in week_entries if e['priority'] == '🔴')}")
    print(f"    🟡 {sum(1 for e in week_entries if e['priority'] == '🟡')}")
    print(f"    🟢 {sum(1 for e in week_entries if e['priority'] == '🟢')}")

    # Analyze patterns
    patterns = analyze_patterns(week_entries)
    promotions = generate_promotions(week_entries, patterns)

    # Generate report
    report = generate_reflection_report(week_entries, patterns, promotions, end_date)

    if args.dry_run:
        print("\n--- Preview ---")
        print(report[:2000])
        print("... (truncated)")
        return

    # Write reflection
    REFLECTION_DIR.mkdir(parents=True, exist_ok=True)
    reflection_path = REFLECTION_DIR / f"weekly_reflection_{end_date}.md"

    if reflection_path.exists() and not args.force:
        print(f"[skip] Reflection already exists: {reflection_path}")
        return

    reflection_path.write_text(report, encoding="utf-8")
    print(f"[write] {reflection_path}")

    # GC observations (MVP: report only)
    print(f"[*] GC: Currently in report-only mode. Run with --apply-gc to remove promoted entries.")

    print(f"[*] Done.")


if __name__ == "__main__":
    main()
