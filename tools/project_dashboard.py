#!/usr/bin/env python3
r"""
project_dashboard.py — Scan active research projects and generate a status dashboard.

Scans two roots:
  1. D:\OneDrive\01_研究 Research\01_活跃项目 Active   (local working dirs)
  2. D:\OneDrive\Obsidian Vault\00 工作台\项目           (Obsidian project notes)

Produces a Markdown report with project health, recent activity, blockers, and next steps.
"""

import argparse
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
ACTIVE_ROOT = Path(r"D:\OneDrive\01_研究 Research\01_活跃项目 Active")
OBSIDIAN_ROOT = Path(r"D:\OneDrive\Obsidian Vault\00 工作台\项目")

EXCLUDE_DIRS = {"_PROJECT_TEMPLATE", "备份", ".git", ".obsidian", ".smart-env",
                "_codex_tools", ".trash", "Template", "模板", "wechat", "xhs",
                "inbox", "meeting_notes", "_backup_", "文献笔记库"}

# ---------------------------------------------------------------------------
# Frontmatter helpers
# ---------------------------------------------------------------------------
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_frontmatter(text: str) -> dict[str, Any]:
    """Parse simple YAML frontmatter."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    raw = m.group(1)
    data: dict[str, Any] = {}
    key: str | None = None
    values: list[str] = []
    for line in raw.splitlines():
        stripped = line.rstrip()
        if not stripped:
            continue
        # New key
        if stripped[0].isalpha() or stripped.startswith("-"):
            # If previous key had list values, commit them
            if key is not None:
                if values:
                    data[key] = values if len(values) > 1 else values[0]
                else:
                    data[key] = ""
                key, values = None, []
        if stripped.startswith("-"):
            val = stripped[1:].strip()
            if key is not None:
                values.append(val)
            continue
        if ":" in stripped:
            k, v = stripped.split(":", 1)
            k = k.strip()
            v = v.strip()
            if key is not None:
                if values:
                    data[key] = values if len(values) > 1 else values[0]
                else:
                    data[key] = ""
            key = k
            values = [v] if v else []
    if key is not None:
        data[key] = values if len(values) > 1 else (values[0] if values else "")
    return data


# ---------------------------------------------------------------------------
# File scanning helpers
# ---------------------------------------------------------------------------
def is_excluded(path: Path) -> bool:
    for part in path.parts:
        if part in EXCLUDE_DIRS or part.startswith("_"):
            return True
    return False


def dir_mtime(path: Path) -> datetime:
    """Return the most recent mtime of any file under path (recursive)."""
    latest = datetime.min.replace(tzinfo=timezone.utc)
    for f in path.rglob("*"):
        if f.is_file() and not is_excluded(f):
            try:
                mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
                if mtime > latest:
                    latest = mtime
            except OSError:
                continue
    return latest


def count_files(path: Path, pattern: str = "*") -> int:
    return sum(1 for f in path.rglob(pattern) if f.is_file() and not is_excluded(f))


# ---------------------------------------------------------------------------
# Project extractors
# ---------------------------------------------------------------------------
def extract_local_project(active_dir: Path) -> dict[str, Any]:
    """Read README_PROJECT.md from the local active directory."""
    readme = active_dir / "README_PROJECT.md"
    data: dict[str, Any] = {"dir": active_dir, "name": active_dir.name}
    if readme.exists():
        text = readme.read_text(encoding="utf-8", errors="ignore")
        data["readme"] = text
        # Extract one-liner
        m = re.search(r"#{1,2}\s*One-line Summary\s*\n+(.+)", text, re.IGNORECASE)
        data["one_liner"] = m.group(1).strip() if m else ""
        # Extract research question
        m = re.search(r"#{1,2}\s*Research Question\s*\n+(.+?)(?=\n#{1,2}|\Z)", text, re.IGNORECASE | re.DOTALL)
        data["research_question"] = m.group(1).strip() if m else ""
        # Extract current status (first bullet only)
        m = re.search(r"#{1,2}\s*Current Status\s*\n+(.+?)(?=\n#{1,2}|\Z)", text, re.IGNORECASE | re.DOTALL)
        data["current_status"] = m.group(1).strip() if m else ""
        # Extract team
        m = re.search(r"#{1,2}\s*Team\s*\n+(.+?)(?=\n#{1,2}|\Z)", text, re.IGNORECASE | re.DOTALL)
        data["team"] = m.group(1).strip() if m else ""
        # Extract Obsidian path reference if present
        m = re.search(r"Obsidian\s*项目笔记\s*[`：:]\s*`?([^`\n]+)`?", text, re.IGNORECASE)
        if m:
            obs_path = Path(m.group(1).strip())
            data["obsidian_dir_name"] = obs_path.name
    # Local file stats
    data["local_files"] = count_files(active_dir)
    data["local_writing"] = count_files(active_dir / "writing") if (active_dir / "writing").exists() else 0
    data["local_code"] = count_files(active_dir / "code") if (active_dir / "code").exists() else 0
    data["local_data"] = count_files(active_dir / "data") if (active_dir / "data").exists() else 0
    data["last_modified"] = dir_mtime(active_dir)
    return data


def extract_obsidian_project(obsidian_dir: Path) -> dict[str, Any]:
    """Read Context Packet and project overview from Obsidian project dir."""
    data: dict[str, Any] = {"dir": obsidian_dir, "name": obsidian_dir.name}

    # Context Packet
    cp_files = list((obsidian_dir / "00 Active").glob("*Context Packet*")) if (obsidian_dir / "00 Active").exists() else []
    if cp_files:
        text = cp_files[0].read_text(encoding="utf-8", errors="ignore")
        data["context_packet"] = text
        fm = parse_frontmatter(text)
        data["frontmatter"] = fm
        data["tags"] = fm.get("tags", [])
        data["project"] = fm.get("project", obsidian_dir.name)
        # Extract known literature
        lit = []
        in_lit = False
        for line in text.splitlines():
            if re.search(r"已知文献|Known Literature|References", line, re.IGNORECASE):
                in_lit = True
                continue
            if in_lit:
                if line.startswith("##") or line.startswith("#"):
                    break
                if line.strip().startswith("-"):
                    lit.append(line.strip().lstrip("-").strip())
        data["literature"] = lit

    # Project overview
    overview_files = list((obsidian_dir / "90 AI drafts").glob("*项目概览*")) if (obsidian_dir / "90 AI drafts").exists() else []
    if overview_files:
        text = overview_files[0].read_text(encoding="utf-8", errors="ignore")
        data["overview"] = text
        fm = parse_frontmatter(text)
        data["overview_fm"] = fm
        # Extract blockers
        blockers = []
        in_blockers = False
        for line in text.splitlines():
            if re.search(r"当前阻塞|Blockers|Current Blockers", line, re.IGNORECASE):
                in_blockers = True
                continue
            if in_blockers:
                if line.startswith("##") or line.startswith("#"):
                    break
                if line.strip().startswith("-"):
                    blockers.append(line.strip().lstrip("-").strip())
        data["blockers"] = blockers
        # Extract next steps
        steps = []
        in_steps = False
        for line in text.splitlines():
            if re.search(r"下一步|Next Steps|下一步", line, re.IGNORECASE):
                in_steps = True
                continue
            if in_steps:
                if line.startswith("##") or line.startswith("#"):
                    break
                if line.strip().startswith("-"):
                    steps.append(line.strip().lstrip("-").strip())
        data["next_steps"] = steps

    # Stats
    data["file_count"] = count_files(obsidian_dir, "*.md")
    data["ai_drafts"] = count_files(obsidian_dir / "90 AI drafts", "*.md") if (obsidian_dir / "90 AI drafts").exists() else 0
    data["active_notes"] = count_files(obsidian_dir / "00 Active", "*.md") if (obsidian_dir / "00 Active").exists() else 0
    data["last_modified"] = dir_mtime(obsidian_dir)

    return data


# ---------------------------------------------------------------------------
# Dashboard generation
# ---------------------------------------------------------------------------
def format_days_ago(dt: datetime) -> str:
    if dt == datetime.min.replace(tzinfo=timezone.utc):
        return "N/A"
    delta = datetime.now(timezone.utc) - dt
    days = delta.days
    if days == 0:
        return "today"
    if days == 1:
        return "1 day ago"
    return f"{days} days ago"


def _norm_key(name: str) -> str:
    return name.lower().replace(" ", "").replace("×", "x").replace("-", "")


def pair_projects(local_projects: list[dict], obsidian_projects: list[dict]) -> tuple[list[tuple[dict, dict]], list[dict], list[dict]]:
    """Return (paired, unmatched_local, unmatched_obsidian)."""
    obs_by_name = {_norm_key(p["name"]): p for p in obsidian_projects}
    obs_by_dir_name: dict[str, dict] = {}
    for p in obsidian_projects:
        obs_by_dir_name[p["name"]] = p

    paired: list[tuple[dict, dict]] = []
    matched_obs: set[str] = set()

    for loc in local_projects:
        matched_obsidian: dict | None = None
        # 1. Explicit Obsidian dir name reference in README
        obs_dir_name = loc.get("obsidian_dir_name")
        if obs_dir_name and obs_dir_name in obs_by_dir_name:
            matched_obsidian = obs_by_dir_name[obs_dir_name]
        # 2. Fallback to normalized name match
        if matched_obsidian is None:
            matched_obsidian = obs_by_name.get(_norm_key(loc["name"]))
        if matched_obsidian is not None:
            paired.append((loc, matched_obsidian))
            matched_obs.add(matched_obsidian["name"])
        else:
            paired.append((loc, {}))

    unmatched_obs = [p for p in obsidian_projects if p["name"] not in matched_obs]
    # unmatched_local are those with empty obsidian dict
    unmatched_loc = [loc for loc, obs in paired if not obs]
    # Rebuild paired to only include those with matches
    paired = [(loc, obs) for loc, obs in paired if obs]
    return paired, unmatched_loc, unmatched_obs


def _extract_status(loc: dict) -> str:
    """Extract single-word status from Current Status section."""
    text = loc.get("current_status", "")
    if text.lower().startswith("- 当前阶段："):
        first_line = text.splitlines()[0]
        # Split on first full-width colon
        if "：" in first_line:
            return first_line.split("：", 1)[-1].strip().split()[0]
    return "active"


def generate_dashboard(local_projects: list[dict], obsidian_projects: list[dict]) -> str:
    lines: list[str] = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    lines.append(f"# Research Project Dashboard\n")
    lines.append(f"*Generated: {now} UTC*\n")

    paired, unmatched_loc, unmatched_obs = pair_projects(local_projects, obsidian_projects)

    # Combine all rows: paired first, then unmatched
    all_rows: list[tuple[dict, dict]] = []
    all_rows.extend(paired)
    for loc in unmatched_loc:
        all_rows.append((loc, {}))
    for obs in unmatched_obs:
        all_rows.append(({}, obs))

    # Summary table
    lines.append("## Overview\n")
    lines.append("| Project | Status | Local Files | Obs. Files | AI Drafts | Active | Last Activity | Blockers |")
    lines.append("|---|---|---:|---:|---:|---:|---|---|")
    for loc, obs in all_rows:
        name = obs.get("name") or loc.get("name", "Unknown")
        status = _extract_status(loc) if loc else (obs.get("frontmatter", {}).get("status", "active") if obs else "—")
        local_files = loc.get("local_files", 0) if loc else 0
        obs_files = obs.get("file_count", 0) if obs else 0
        ai = obs.get("ai_drafts", 0) if obs else 0
        active = obs.get("active_notes", 0) if obs else 0
        last_loc = loc.get("last_modified", datetime.min.replace(tzinfo=timezone.utc)) if loc else datetime.min.replace(tzinfo=timezone.utc)
        last_obs = obs.get("last_modified", datetime.min.replace(tzinfo=timezone.utc)) if obs else datetime.min.replace(tzinfo=timezone.utc)
        last = last_loc if last_loc > last_obs else last_obs
        last_str = format_days_ago(last) if last != datetime.min.replace(tzinfo=timezone.utc) else "N/A"
        blockers = len(obs.get("blockers", [])) if obs else 0
        blocker_str = f"{blockers} blocker(s)" if blockers else "—"
        lines.append(f"| {name} | {status} | {local_files} | {obs_files} | {ai} | {active} | {last_str} | {blocker_str} |")
    lines.append("")

    # Detailed cards
    lines.append("## Project Cards\n")
    for loc, obs in all_rows:
        name = obs.get("name") or loc.get("name", "Unknown")
        lines.append(f"### {name}\n")

        if loc.get("one_liner"):
            lines.append(f"**One-liner:** {loc['one_liner']}\n")
        if loc.get("research_question"):
            rq = loc["research_question"].replace("\n", " ")
            lines.append(f"**Question:** {rq[:200]}{'…' if len(rq) > 200 else ''}\n")
        if loc.get("team"):
            lines.append(f"**Team:** {loc['team'].replace(chr(10), ' ')}\n")

        if loc.get("local_files", 0):
            lf = loc["local_files"]
            lw = loc.get("local_writing", 0)
            lc = loc.get("local_code", 0)
            ld = loc.get("local_data", 0)
            lines.append(f"**Local files:** {lf} total (writing {lw}, code {lc}, data {ld})\n")

        if obs.get("tags"):
            tags = ", ".join(f"`{t}`" for t in obs["tags"] if isinstance(t, str))
            lines.append(f"**Tags:** {tags}\n")

        if obs.get("blockers"):
            lines.append("**Blockers:**")
            for b in obs["blockers"]:
                lines.append(f"- {b}")
            lines.append("")

        if obs.get("next_steps"):
            lines.append("**Next steps:**")
            for s in obs["next_steps"]:
                lines.append(f"- {s}")
            lines.append("")

        if obs.get("literature"):
            lines.append(f"**Key literature ({len(obs['literature'])} items):**")
            for lit in obs["literature"][:5]:
                lines.append(f"- {lit}")
            if len(obs["literature"]) > 5:
                lines.append(f"- … and {len(obs['literature']) - 5} more")
            lines.append("")

        if loc.get("dir"):
            lines.append(f"- Local: `{loc['dir']}`")
        if obs.get("dir"):
            lines.append(f"- Obsidian: `{obs['dir']}`")
        lines.append("")

    # Activity heatmap (last 30 days)
    lines.append("## Activity Heatmap (last 30 days)\n")
    for loc, obs in all_rows:
        name = obs.get("name") or loc.get("name", "Unknown")
        last_loc = loc.get("last_modified", datetime.min.replace(tzinfo=timezone.utc)) if loc else datetime.min.replace(tzinfo=timezone.utc)
        last_obs = obs.get("last_modified", datetime.min.replace(tzinfo=timezone.utc)) if obs else datetime.min.replace(tzinfo=timezone.utc)
        last = last_loc if last_loc > last_obs else last_obs
        delta = (datetime.now(timezone.utc) - last).days
        if delta <= 30:
            bars = max(1, 10 - delta // 3)
            bar = "█" * bars
            lines.append(f"{name:45s} {bar}  ({format_days_ago(last)})")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(description="Research project dashboard")
    parser.add_argument("--active-root", type=Path, default=ACTIVE_ROOT)
    parser.add_argument("--obsidian-root", type=Path, default=OBSIDIAN_ROOT)
    parser.add_argument("--output", "-o", type=Path, help="Write Markdown to file")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    active_root: Path = args.active_root
    obsidian_root: Path = args.obsidian_root

    # Discover local projects
    local_projects: list[dict] = []
    if active_root.exists():
        for d in active_root.iterdir():
            if d.is_dir() and d.name not in EXCLUDE_DIRS and not d.name.startswith("_"):
                local_projects.append(extract_local_project(d))

    # Discover Obsidian projects
    obsidian_projects: list[dict] = []
    if obsidian_root.exists():
        for d in obsidian_root.iterdir():
            if d.is_dir() and d.name not in EXCLUDE_DIRS and not d.name.startswith("_"):
                obsidian_projects.append(extract_obsidian_project(d))

    if args.json:
        import json
        print(json.dumps({"local": local_projects, "obsidian": obsidian_projects}, default=str, indent=2, ensure_ascii=False))
        return 0

    report = generate_dashboard(local_projects, obsidian_projects)

    if args.output:
        args.output.write_text(report, encoding="utf-8")
        print(f"[*] Dashboard written to {args.output}")
    else:
        print(report)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
