#!/usr/bin/env python3
"""
Academic Observer — Daily research activity collector.

Scans the Obsidian Vault and related directories for research activity,
classifies observations by type and priority, and writes structured YAML
for downstream AI analysis.

Usage:
    python observer.py [YYYY-MM-DD]    # Collect for specific date (default: today)
    python observer.py --dry-run       # Preview without writing
    python observer.py --force         # Overwrite existing raw file
"""

import argparse
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

import yaml

# ── Configuration ──────────────────────────────────────────────────────────

VAULT_ROOT = Path("D:/Onedrive/Obsidian Vault")
INFRA_DIR = Path("C:/Users/admin/.claude/academic_infrastructure")
RAW_DIR = INFRA_DIR / "contexts" / "memory" / "daily_raw"

# Directories to scan, in priority order
SCAN_TARGETS = [
    (VAULT_ROOT / "daily", "daily_log"),
    (VAULT_ROOT / "meeting_notes", "meeting"),
    (VAULT_ROOT / "00 工作台/项目", "project"),
    (VAULT_ROOT / "00 工作台/叙述模板训练集", "narrative_training"),
    (VAULT_ROOT / "文献笔记库/02 原子化", "atomic_notes"),
    (VAULT_ROOT / "概念库", "concepts"),
    (VAULT_ROOT / "论证卡库", "argument_cards"),
]

# Files to check for modifications
TRACKED_FILES = [
    (VAULT_ROOT / "00 工作台/今日推进清单.md", "priority"),
    (VAULT_ROOT / "00 工作台/知识库操作日志.md", "knowledge_op"),
]

# Regex patterns for content classification
PATTERNS = {
    "theory_breakthrough": re.compile(
        r"理论框架|机制推导|假设修正|重构|refram|mechanism|theory|hypothesis|gap|problematiz",
        re.IGNORECASE,
    ),
    "method_decision": re.compile(
        r"识别策略|DiD|IV|RDD|匹配|稳健性|变量测量|模型设定|identification|robustness|measurement|specification",
        re.IGNORECASE,
    ),
    "writing_progress": re.compile(
        r"引言|理论|方法|结果|讨论|写作|重写|段落|投稿|审稿|introduction|theory|methods|results|discussion|writing|submission|review",
        re.IGNORECASE,
    ),
    "literature_read": re.compile(
        r"文献|阅读|笔记|原子化|literature|reading|note|paper",
        re.IGNORECASE,
    ),
    "project_milestone": re.compile(
        r"完成|提交|通过|拒绝|修改|里程碑|milestone|complete|submit|reject|revise|accept",
        re.IGNORECASE,
    ),
}

PROJECT_TAGS = {
    "产品召回": "#产品召回",
    "共同所有权": "#共同所有权",
    "竞业协议": "#竞业协议",
    "CEO regulatory focus": "#产品召回",
    "CEO paranoia": "#产品召回",
    "anti-SLAPP": "#竞业协议",
    "IDD": "#竞业协议",
}

# ── Helpers ────────────────────────────────────────────────────────────────


def detect_project_tag(text: str) -> str:
    """Infer project tag from text content."""
    text_lower = text.lower()
    for keyword, tag in PROJECT_TAGS.items():
        if keyword.lower() in text_lower:
            return tag
    return "#general"


def classify_activity(text: str) -> str:
    """Classify activity type from text content."""
    scores = {key: len(pat.findall(text)) for key, pat in PATTERNS.items()}
    if not any(scores.values()):
        return "routine"
    return max(scores, key=scores.get)


def get_file_mtime(path: Path) -> datetime | None:
    """Get file modification time as timezone-naive datetime."""
    try:
        return datetime.fromtimestamp(path.stat().st_mtime)
    except OSError:
        return None


def find_modified_files(
    root: Path, target_date: datetime, file_pattern: str = "*.md"
) -> list[Path]:
    """Find files modified on target_date under root."""
    if not root.exists():
        return []

    modified = []
    start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)

    for path in root.rglob(file_pattern):
        mtime = get_file_mtime(path)
        if mtime and start <= mtime < end:
            modified.append(path)

    return modified


def extract_summary(path: Path, max_chars: int = 300) -> str:
    """Extract a brief summary from a markdown file."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return "[unreadable]"

    # Remove YAML frontmatter
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            text = parts[2]

    # Take first non-empty line that isn't a heading
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("-"):
            return line[:max_chars]

    return "[no extractable summary]"


# ── Core Logic ─────────────────────────────────────────────────────────────


def collect_observations(target_date: datetime) -> dict:
    """Collect raw research activity for target_date."""
    date_str = target_date.strftime("%Y-%m-%d")
    observations = {
        "date": date_str,
        "collected_at": datetime.now().isoformat(),
        "sources": {},
        "activities": [],
    }

    # Scan directory targets
    for scan_dir, source_type in SCAN_TARGETS:
        modified = find_modified_files(scan_dir, target_date)
        if modified:
            observations["sources"][source_type] = [
                {
                    "path": str(p.relative_to(VAULT_ROOT)),
                    "summary": extract_summary(p),
                }
                for p in modified[:10]  # Limit to avoid overflow
            ]

            for p in modified[:10]:
                text = p.read_text(encoding="utf-8")[:2000]
                activity = {
                    "source": source_type,
                    "path": str(p.relative_to(VAULT_ROOT)),
                    "type": classify_activity(text),
                    "project_tag": detect_project_tag(text),
                    "summary": extract_summary(p),
                }
                observations["activities"].append(activity)

    # Check tracked files
    for tracked_file, source_type in TRACKED_FILES:
        if tracked_file.exists():
            mtime = get_file_mtime(tracked_file)
            if mtime and mtime.date() == target_date.date():
                text = tracked_file.read_text(encoding="utf-8")[:2000]
                observations["sources"][source_type] = [
                    {
                        "path": str(tracked_file.relative_to(VAULT_ROOT)),
                        "summary": extract_summary(tracked_file),
                    }
                ]
                observations["activities"].append(
                    {
                        "source": source_type,
                        "path": str(tracked_file.relative_to(VAULT_ROOT)),
                        "type": classify_activity(text),
                        "project_tag": detect_project_tag(text),
                        "summary": extract_summary(tracked_file),
                    }
                )

    # Add metadata
    observations["activity_counts"] = {
        key: sum(1 for a in observations["activities"] if a["type"] == key)
        for key in list(PATTERNS.keys()) + ["routine"]
    }

    return observations


def write_raw_yaml(observations: dict, force: bool = False) -> Path | None:
    """Write observations to daily_raw/YYYY-MM-DD.yaml."""
    date_str = observations["date"]
    raw_path = RAW_DIR / f"{date_str}.yaml"

    if not observations.get("activities"):
        print("[skip] No activities with recording value; raw file not written.")
        return None

    if raw_path.exists() and not force:
        print(f"[skip] Raw file already exists: {raw_path}")
        return None

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # Atomic write: temp file then rename
    temp_path = raw_path.with_suffix(".tmp")
    with open(temp_path, "w", encoding="utf-8") as f:
        yaml.dump(observations, f, allow_unicode=True, sort_keys=False)
    temp_path.replace(raw_path)

    print(f"[write] {raw_path}")
    return raw_path


# ── CLI ────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Academic Observer")
    parser.add_argument("date", nargs="?", help="Target date (YYYY-MM-DD)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--force", action="store_true", help="Overwrite existing raw file")
    args = parser.parse_args()

    # Parse target date
    if args.date:
        target_date = datetime.strptime(args.date, "%Y-%m-%d")
    else:
        target_date = datetime.now()

    print(f"[*] Collecting observations for {target_date.strftime('%Y-%m-%d')}...")

    observations = collect_observations(target_date)

    activity_total = len(observations["activities"])
    print(f"[*] Found {activity_total} activities from {len(observations['sources'])} sources")

    if args.dry_run:
        print("\n--- Preview ---")
        print(yaml.dump(observations, allow_unicode=True, sort_keys=False)[:1500])
        print("... (truncated)")
        return

    raw_path = write_raw_yaml(observations, force=args.force)
    if raw_path:
        print(f"[*] Done. Raw data written to: {raw_path}")
        print(f"[*] Next step: Run Claude analysis to append to OBSERVATIONS.md")
    else:
        print("[*] Nothing written (file exists). Use --force to overwrite.")


if __name__ == "__main__":
    main()
