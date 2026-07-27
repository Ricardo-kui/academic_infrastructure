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
import hashlib
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

import yaml

# ── Configuration ──────────────────────────────────────────────────────────

INFRA_DIR = Path("C:/Users/admin/.claude/academic_infrastructure")
RAW_DIR = INFRA_DIR / "contexts" / "memory" / "daily_raw"
OBSERVATIONS_PATH = INFRA_DIR / "contexts" / "memory" / "OBSERVATIONS.md"

YELLOW_RETENTION_DAYS = 90
GREEN_RETENTION_DAYS = 30

# Activity type → priority marker
# Supports both rule-based observer (legacy) and agentic observer (new) type names
PRIORITY_MAP = {
    # Agentic observer types
    "theory": "🔴",
    "milestone": "🔴",
    "methods": "🟡",
    "writing": "🟡",
    "literature": "🟢",
    "routine": "🟢",
    # Rule-based observer legacy types
    "theory_breakthrough": "🔴",
    "project_milestone": "🔴",
    "method_decision": "🟡",
    "writing_progress": "🟡",
    "literature_read": "🟢",
}

# Activity type → category label (Chinese)
CATEGORY_LABEL = {
    "theory": "理论突破",
    "milestone": "项目里程碑",
    "methods": "方法决策",
    "writing": "写作进展",
    "literature": "文献阅读",
    "routine": "常规进展",
    "theory_breakthrough": "理论突破",
    "project_milestone": "项目里程碑",
    "method_decision": "方法决策",
    "writing_progress": "写作进展",
    "literature_read": "文献阅读",
}

# ── Helpers ────────────────────────────────────────────────────────────────


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip().lower()


def _fingerprint(path: str, summary: str) -> str:
    payload = f"{_normalize_text(path)}\n{_normalize_text(summary)}"
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()


def _activity_fingerprint(activity: dict) -> str:
    return _fingerprint(str(activity.get("path", "")), str(activity.get("summary", "")))


def _markdown_line_fingerprint(line: str) -> str | None:
    stripped = line.strip()
    if not stripped.startswith("-"):
        return None

    body = re.sub(r"^-\s*", "", stripped)
    body = re.sub(r"^\[#[^\]]+\]\s*", "", body)

    path = ""
    links = re.findall(r"\[\[([^\]]+)\]\]", body)
    if links:
        path = links[-1]
        body = re.sub(r"\s*\[\[[^\]]+\]\]\s*$", "", body).strip()

    if not body:
        return None
    return _fingerprint(path, body)


def observation_fingerprints(content: str) -> set[str]:
    keys: set[str] = set()
    for line in content.splitlines():
        key = _markdown_line_fingerprint(line)
        if key:
            keys.add(key)
    return keys


def parse_date(value: str) -> datetime | None:
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return None


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


def filter_recordable_activities(activities: list[dict], seen_keys: set[str]) -> tuple[list[dict], int]:
    """Drop empty summaries and duplicates using path + summary fingerprints."""
    kept: list[dict] = []
    skipped = 0

    for activity in activities:
        summary = str(activity.get("summary", "")).strip()
        if not summary or summary in {"[no summary]", "[no extractable summary]", "[unreadable]"}:
            skipped += 1
            continue

        key = _activity_fingerprint(activity)
        if key in seen_keys:
            skipped += 1
            continue

        seen_keys.add(key)
        kept.append(activity)

    return kept, skipped


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


def cleanup_observations_content(content: str, reference_date: datetime | None = None) -> tuple[str, dict[str, int]]:
    """Apply hard OBSERVATIONS.md retention rules.

    Rules:
    - Drop empty date blocks.
    - Drop duplicate observation lines, keeping the newest/topmost occurrence.
    - Keep 🔴 until explicitly removed by promotion/GC.
    - Drop 🟡 entries older than 90 days.
    - Drop 🟢 entries older than 30 days.
    """
    reference = reference_date or datetime.now()
    lines = content.splitlines()
    result: list[str] = []
    seen: set[str] = set()
    stats = {
        "empty_dates_removed": 0,
        "duplicates_removed": 0,
        "expired_yellow_removed": 0,
        "expired_green_removed": 0,
    }

    i = 0
    while i < len(lines):
        line = lines[i]
        date_match = re.match(r"^###\s*Date:\s*(\d{4}-\d{2}-\d{2})\s*$", line.strip())
        if not date_match:
            result.append(line)
            i += 1
            continue

        date_str = date_match.group(1)
        block: list[str] = [line]
        i += 1
        while i < len(lines) and not re.match(r"^###\s*Date:\s*\d{4}-\d{2}-\d{2}\s*$", lines[i].strip()):
            block.append(lines[i])
            i += 1

        cleaned_block, block_stats = _cleanup_date_block(block, date_str, reference, seen)
        for key, value in block_stats.items():
            stats[key] += value

        if cleaned_block:
            result.extend(cleaned_block)
        else:
            stats["empty_dates_removed"] += 1

    cleaned = _collapse_blank_lines(result)
    return cleaned.rstrip() + "\n", stats


def _cleanup_date_block(
    block: list[str],
    date_str: str,
    reference_date: datetime,
    seen_keys: set[str],
) -> tuple[list[str], dict[str, int]]:
    block_date = parse_date(date_str)
    stats = {
        "empty_dates_removed": 0,
        "duplicates_removed": 0,
        "expired_yellow_removed": 0,
        "expired_green_removed": 0,
    }

    kept_entries: dict[str, list[str]] = {"🔴": [], "🟡": [], "🟢": []}
    current_priority: str | None = None

    for raw_line in block[1:]:
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped.startswith("🔴"):
            current_priority = "🔴"
            continue
        if stripped.startswith("🟡"):
            current_priority = "🟡"
            continue
        if stripped.startswith("🟢"):
            current_priority = "🟢"
            continue
        if not stripped.startswith("-") or current_priority is None:
            continue

        if _is_expired(current_priority, block_date, reference_date):
            if current_priority == "🟡":
                stats["expired_yellow_removed"] += 1
            elif current_priority == "🟢":
                stats["expired_green_removed"] += 1
            continue

        key = _markdown_line_fingerprint(raw_line)
        if key and key in seen_keys:
            stats["duplicates_removed"] += 1
            continue
        if key:
            seen_keys.add(key)
        kept_entries[current_priority].append(raw_line)

    if not any(kept_entries.values()):
        return [], stats

    output = [block[0], ""]
    for priority, label in [
        ("🔴", "理论突破 / 重大决策"),
        ("🟡", "方法决策 / 写作判断"),
        ("🟢", "常规进展 / 阅读记录"),
    ]:
        if kept_entries[priority]:
            output.append(f"{priority} **{label}**")
            output.extend(kept_entries[priority])
            output.append("")

    return output, stats


def _is_expired(priority: str, block_date: datetime | None, reference_date: datetime) -> bool:
    if priority == "🔴" or block_date is None:
        return False
    age = reference_date.date() - block_date.date()
    if priority == "🟡":
        return age > timedelta(days=YELLOW_RETENTION_DAYS)
    if priority == "🟢":
        return age > timedelta(days=GREEN_RETENTION_DAYS)
    return False


def _collapse_blank_lines(lines: list[str]) -> str:
    output: list[str] = []
    blank_count = 0
    for line in lines:
        if line.strip() == "":
            blank_count += 1
            if blank_count <= 2:
                output.append(line)
        else:
            blank_count = 0
            output.append(line)
    return "\n".join(output)


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


def append_to_observations(blocks: list[str], dry_run: bool = False, reference_date: datetime | None = None) -> bool:
    """Append rendered blocks to OBSERVATIONS.md before the closing section."""
    if not OBSERVATIONS_PATH.exists():
        print(f"[error] OBSERVATIONS.md not found: {OBSERVATIONS_PATH}")
        return False

    original_content = OBSERVATIONS_PATH.read_text(encoding="utf-8")
    content, cleanup_stats = cleanup_observations_content(original_content, reference_date=reference_date)

    # Find insertion point: after "<!-- observer.py / Claude cron 在此追加 -->"
    marker = "<!-- observer.py / Claude cron 在此追加 -->"
    if marker not in content:
        print(f"[error] Marker not found in OBSERVATIONS.md: {marker}")
        return False

    insertion = "\n\n".join(blocks).strip()

    if dry_run:
        print("--- Cleanup Preview ---")
        print(cleanup_stats)
        print("--- Preview ---")
        if insertion:
            print(insertion[:1500])
            print("... (truncated)")
        else:
            print("[no new observation blocks]")
        return True

    if insertion:
        new_content = content.replace(marker, marker + "\n" + insertion + "\n")
    else:
        new_content = content
    if new_content != original_content:
        OBSERVATIONS_PATH.write_text(new_content, encoding="utf-8")
        print(f"[write] Appended {len(blocks)} day(s) to {OBSERVATIONS_PATH}")
    else:
        print("[*] OBSERVATIONS.md already satisfies consolidation and cleanup rules.")
    print(f"[cleanup] {cleanup_stats}")
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
        ok = append_to_observations([], dry_run=args.dry_run)
        return 0 if ok else 1

    print(f"[*] Found {len(raw_files)} unmerged raw file(s)")

    # Load and group by date
    by_date: dict[str, list[dict]] = {}
    for path in raw_files:
        data = load_yaml_raw(path)
        if not data:
            continue
        activities = data.get("activities", [])
        if not activities:
            if args.dry_run:
                print(f"[cleanup] Would remove empty raw cache: {path.name}")
            else:
                path.unlink(missing_ok=True)
                print(f"[cleanup] Removed empty raw cache: {path.name}")
            continue
        date_str = data.get("date") or extract_date_from_filename(path)
        if not date_str:
            continue
        by_date.setdefault(date_str, []).extend(activities)

    if not by_date:
        print("[*] No valid activities found.")
        ok = append_to_observations([], dry_run=args.dry_run)
        return 0 if ok else 1

    # Render blocks
    blocks = []
    content = OBSERVATIONS_PATH.read_text(encoding="utf-8") if OBSERVATIONS_PATH.exists() else ""
    cleaned_content, _cleanup_stats = cleanup_observations_content(content)
    seen_keys = observation_fingerprints(cleaned_content)
    skipped_total = 0
    for date_str in sorted(by_date):
        activities, skipped = filter_recordable_activities(by_date[date_str], seen_keys)
        skipped_total += skipped
        if not activities:
            print(f"  -> {date_str}: 0 recordable activities ({skipped} skipped)")
            continue
        block = render_date_block(date_str, activities)
        blocks.append(block)
        print(f"  -> {date_str}: {len(activities)} activities ({skipped} skipped)")

    if not blocks:
        print(f"[*] No new non-duplicate activities to append ({skipped_total} skipped).")
        ok = append_to_observations([], dry_run=args.dry_run)
        return 0 if ok else 1

    # Append
    ok = append_to_observations(blocks, dry_run=args.dry_run)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
