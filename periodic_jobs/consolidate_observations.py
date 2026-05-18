#!/usr/bin/env python3
"""
consolidate_observations.py — Merge daily_raw/*.yaml into OBSERVATIONS.md.

Scans daily_raw/ for unmerged YAML files, converts them into the standard
🔴🟡🟢 markdown format, and appends them to OBSERVATIONS.md under the
"Daily Observations" section.

Usage:
    python consolidate_observations.py [--dry-run] [--force]
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml

# ── Configuration ──────────────────────────────────────────────────────────

INFRA_DIR = Path("C:/Users/admin/.claude/academic_infrastructure")
RAW_DIR = INFRA_DIR / "contexts" / "memory" / "daily_raw"
OBSERVATIONS_PATH = INFRA_DIR / "contexts" / "memory" / "OBSERVATIONS.md"

# Activity type → priority marker
PRIORITY_MAP = {
    "theory_breakthrough": "🔴",
    "project_milestone": "🔴",
    "method_decision": "🟡",
    "writing_progress": "🟡",
    "literature_read": "🟢",
    "routine": "🟢",
}

# Activity type → category label (Chinese)
CATEGORY_LABEL = {
    "theory_breakthrough": "理论突破",
    "project_milestone": "项目里程碑",
    "method_decision": "方法决策",
    "writing_progress": "写作进展",
    "literature_read": "文献阅读",
    "routine": "常规进展",
}

# ── Helpers ────────────────────────────────────────────────────────────────


def load_yaml_raw(path: Path) -> dict | None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"[warn] Failed to load {path}: {e}")
        return None


def extract_date_from_filename(path: Path) -> str | None:
    m = re.match(r"(\d{4}-\d{2}-\d{2})\.yaml", path.name)
    return m.group(1) if m else None


def activity_to_markdown(activity: dict) -> str:
    """Convert a single activity dict to an OBSERVATIONS.md line."""
    act_type = activity.get("type", "routine")
    priority = PRIORITY_MAP.get(act_type, "🟢")
    tag = activity.get("project_tag", "#general")
    summary = activity.get("summary", "[no summary]")
    rel_path = activity.get("path", "")

    # Build link if path exists
    link = f" [[{rel_path}]]" if rel_path else ""
    return f"- [{tag}] {summary}{link}"


def group_activities_by_priority(activities: list[dict]) -> dict[str, list[str]]:
    """Group markdown lines by priority marker."""
    groups: dict[str, list[str]] = {"🔴": [], "🟡": [], "🟢": []}
    for act in activities:
        act_type = act.get("type", "routine")
        priority = PRIORITY_MAP.get(act_type, "🟢")
        md = activity_to_markdown(act)
        groups[priority].append(md)
    return groups


def render_date_block(date_str: str, activities: list[dict]) -> str:
    """Render a full ### Date: YYYY-MM-DD block."""
    lines = [f"### Date: {date_str}", ""]
    groups = group_activities_by_priority(activities)

    for priority, label_base in [("🔴", "理论突破 / 重大决策"),
                                  ("🟡", "方法决策 / 写作判断"),
                                  ("🟢", "常规进展 / 阅读记录")]:
        if groups[priority]:
            lines.append(f"{priority} **{label_base}**")
            for md in groups[priority]:
                lines.append(md)
            lines.append("")

    return "\n".join(lines)


def find_unmerged_raw_files() -> list[Path]:
    """Find raw YAML files that haven't been merged yet.

    Heuristic: a file is unmerged if its date is not already present
    as a '### Date: YYYY-MM-DD' header in OBSERVATIONS.md.
    """
    if not OBSERVATIONS_PATH.exists():
        return sorted(RAW_DIR.glob("*.yaml"))

    obs_content = OBSERVATIONS_PATH.read_text(encoding="utf-8")
    merged_dates = set(re.findall(r"###\s*Date:\s*(\d{4}-\d{2}-\d{2})", obs_content))

    unmerged = []
    for path in sorted(RAW_DIR.glob("*.yaml")):
        date_str = extract_date_from_filename(path)
        if date_str and date_str not in merged_dates:
            unmerged.append(path)
    return unmerged


def append_to_observations(blocks: list[str], dry_run: bool = False) -> bool:
    """Append rendered blocks to OBSERVATIONS.md before the closing section."""
    if not OBSERVATIONS_PATH.exists():
        print(f"[error] OBSERVATIONS.md not found: {OBSERVATIONS_PATH}")
        return False

    content = OBSERVATIONS_PATH.read_text(encoding="utf-8")

    # Find insertion point: after "<!-- observer.py / Claude cron 在此追加 -->"
    marker = "<!-- observer.py / Claude cron 在此追加 -->"
    if marker not in content:
        print(f"[error] Marker not found in OBSERVATIONS.md: {marker}")
        return False

    insertion = "\n\n".join(blocks) + "\n"

    if dry_run:
        print("--- Preview ---")
        print(insertion[:1500])
        print("... (truncated)")
        return True

    new_content = content.replace(marker, marker + "\n" + insertion)
    OBSERVATIONS_PATH.write_text(new_content, encoding="utf-8")
    print(f"[write] Appended {len(blocks)} day(s) to {OBSERVATIONS_PATH}")
    return True


# ── CLI ────────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(description="Consolidate daily observations")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--force", action="store_true", help="Re-process already merged dates")
    args = parser.parse_args()

    if args.force:
        raw_files = sorted(RAW_DIR.glob("*.yaml"))
    else:
        raw_files = find_unmerged_raw_files()

    if not raw_files:
        print("[*] No new raw files to consolidate.")
        return 0

    print(f"[*] Found {len(raw_files)} unmerged raw file(s)")

    # Load and group by date
    by_date: dict[str, list[dict]] = {}
    for path in raw_files:
        data = load_yaml_raw(path)
        if not data:
            continue
        date_str = data.get("date") or extract_date_from_filename(path)
        if not date_str:
            continue
        by_date.setdefault(date_str, []).extend(data.get("activities", []))

    if not by_date:
        print("[*] No valid activities found.")
        return 0

    # Render blocks
    blocks = []
    for date_str in sorted(by_date):
        block = render_date_block(date_str, by_date[date_str])
        blocks.append(block)
        print(f"  → {date_str}: {len(by_date[date_str])} activities")

    # Append
    ok = append_to_observations(blocks, dry_run=args.dry_run)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
