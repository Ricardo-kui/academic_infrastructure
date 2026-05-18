#!/usr/bin/env python3
"""
bridge_detector.py — Detect cross-theme bridges across research projects.

Reads all project Context Packets from the Obsidian project workspace,
extracts tags, citations, and keywords, then surfaces:
  - Shared literature citations
  - Shared thematic tags
  - Shared outcome / mechanism keywords
  - Suggested bridge opportunities
"""

import argparse
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from project_dashboard import parse_frontmatter, EXCLUDE_DIRS, OBSIDIAN_ROOT

# ---------------------------------------------------------------------------
# Keywords to scan for bridge signals
# ---------------------------------------------------------------------------
MECHANISM_KEYWORDS = {
    "product recall", "recall timing", "time to recall", "recall count",
    "common ownership", "institutional ownership", "mhhi", "hhco",
    "ceo paranoia", "regulatory focus", "anti-slapp", "idd",
    "spillover", "vertical spillover", "horizontal spillover",
    "did", "difference-in-differences", "iv", "instrumental variable",
    "matching", "psm", "rdd", "event study", "survival", "hazard",
    "csr", "corporate social responsibility",
    "advertising", "ad spending", "buyer experience",
}

OUTCOME_KEYWORDS = {
    "time to recall", "recall count", "recall timing", "recall decision",
    "product quality", "defect disclosure", "voluntary recall",
}

THEME_ALIASES: dict[str, list[str]] = {
    "product recall": ["recall", "product recall", "recall timing", "time to recall", "recall count"],
    "common ownership": ["common ownership", "institutional ownership", "mhhi", "hhco", "mhhi delta"],
    "ceo paranoia": ["ceo paranoia", "paranoia"],
    "regulatory focus": ["regulatory focus", "promotion focus", "prevention focus"],
    "anti-slapp": ["anti-slapp", "slapp"],
    "idd": ["idd", "insider trading"],
    "csr": ["csr", "corporate social responsibility"],
    "advertising": ["advertising", "ad spending", "advertising expenditure"],
}

# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------
CITEKEY_RE = re.compile(r"\[\[(?:[^\]|]*\s)?([A-Z][a-zA-Z]+(?:et\.?\s*al\.?)?[^\]]*\(\d{4}\)[^\]]*)\]\]")
ALT_CITE_RE = re.compile(r"`([A-Z][a-zA-Z]+(?:EtAl)?\d{4})`")


def extract_citations(text: str) -> set[str]:
    cites: set[str] = set()
    for m in CITEKEY_RE.finditer(text):
        cites.add(m.group(1).strip())
    for m in ALT_CITE_RE.finditer(text):
        cites.add(m.group(1).strip())
    return cites


def extract_keywords(text: str, keyword_set: set[str]) -> set[str]:
    text_lower = text.lower()
    found: set[str] = set()
    for kw in keyword_set:
        if kw in text_lower:
            found.add(kw)
    return found


def canonical_themes(tags: list[str], text: str) -> set[str]:
    """Map raw tags + text to canonical theme names."""
    all_text = " ".join(tags).lower() + " " + text.lower()
    themes: set[str] = set()
    for theme, aliases in THEME_ALIASES.items():
        for alias in aliases:
            if alias in all_text:
                themes.add(theme)
                break
    return themes


# ---------------------------------------------------------------------------
# Project reader
# ---------------------------------------------------------------------------
def read_projects(root: Path) -> list[dict[str, Any]]:
    projects: list[dict[str, Any]] = []
    if not root.exists():
        return projects
    for d in root.iterdir():
        if not d.is_dir() or d.name in EXCLUDE_DIRS or d.name.startswith("_"):
            continue
        active_dir = d / "00 Active"
        cp_files = list(active_dir.glob("*Context Packet*")) if active_dir.exists() else []
        if not cp_files:
            continue
        text = cp_files[0].read_text(encoding="utf-8", errors="ignore")
        fm = parse_frontmatter(text)
        tags = fm.get("tags", []) if isinstance(fm.get("tags"), list) else []
        projects.append({
            "name": d.name,
            "dir": d,
            "tags": tags,
            "text": text,
            "citations": extract_citations(text),
            "mechanisms": extract_keywords(text, MECHANISM_KEYWORDS),
            "outcomes": extract_keywords(text, OUTCOME_KEYWORDS),
            "themes": canonical_themes(tags, text),
        })
    return projects


# ---------------------------------------------------------------------------
# Bridge scoring
# ---------------------------------------------------------------------------
def score_bridge(p1: dict, p2: dict) -> tuple[float, dict[str, Any]]:
    """Return (score, details) for a project pair."""
    details: dict[str, Any] = {}
    score = 0.0

    # Shared citations (strong signal)
    shared_cites = p1["citations"] & p2["citations"]
    if shared_cites:
        score += len(shared_cites) * 3.0
        details["shared_citations"] = sorted(shared_cites)

    # Shared themes
    shared_themes = p1["themes"] & p2["themes"]
    if shared_themes:
        score += len(shared_themes) * 2.0
        details["shared_themes"] = sorted(shared_themes)

    # Shared mechanisms
    shared_mech = p1["mechanisms"] & p2["mechanisms"]
    if shared_mech:
        score += len(shared_mech) * 1.5
        details["shared_mechanisms"] = sorted(shared_mech)

    # Shared outcomes
    shared_out = p1["outcomes"] & p2["outcomes"]
    if shared_out:
        score += len(shared_out) * 1.5
        details["shared_outcomes"] = sorted(shared_out)

    # Tag overlap
    shared_tags = set(p1["tags"]) & set(p2["tags"])
    if shared_tags:
        score += len(shared_tags) * 1.0
        details["shared_tags"] = sorted(shared_tags)

    return score, details


def generate_bridge_report(projects: list[dict[str, Any]], min_score: float = 2.0) -> str:
    lines: list[str] = []
    lines.append("# Cross-Theme Bridge Detection Report\n")
    lines.append(f"*Projects scanned: {len(projects)}*\n")

    # Build pairwise scores
    bridges: list[tuple[float, dict, dict, dict]] = []
    n = len(projects)
    for i in range(n):
        for j in range(i + 1, n):
            score, details = score_bridge(projects[i], projects[j])
            if score >= min_score:
                bridges.append((score, projects[i], projects[j], details))

    bridges.sort(key=lambda x: x[0], reverse=True)

    if not bridges:
        lines.append("No significant bridges detected above the threshold.\n")
        return "\n".join(lines)

    lines.append(f"## Top Bridges (score ≥ {min_score})\n")
    for idx, (score, p1, p2, det) in enumerate(bridges, 1):
        lines.append(f"### {idx}. {p1['name']} <-> {p2['name']}  (score: {score:.1f})\n")

        if "shared_themes" in det:
            lines.append(f"**Shared themes:** {', '.join(f'`{t}`' for t in det['shared_themes'])}\n")
        if "shared_outcomes" in det:
            lines.append(f"**Shared outcomes:** {', '.join(f'`{o}`' for o in det['shared_outcomes'])}\n")
        if "shared_mechanisms" in det:
            lines.append(f"**Shared mechanisms:** {', '.join(f'`{m}`' for m in det['shared_mechanisms'])}\n")
        if "shared_citations" in det:
            lines.append(f"**Shared citations ({len(det['shared_citations'])}):**")
            for c in det["shared_citations"][:8]:
                lines.append(f"- {c}")
            if len(det["shared_citations"]) > 8:
                lines.append(f"- … and {len(det['shared_citations']) - 8} more")
            lines.append("")
        if "shared_tags" in det:
            lines.append(f"**Shared tags:** {', '.join(f'`{t}`' for t in det['shared_tags'])}\n")

        # Generate suggestion
        suggestion = generate_suggestion(p1, p2, det)
        lines.append(f"**Suggestion:** {suggestion}\n")

    # Theme incidence table
    lines.append("## Theme Incidence Across Projects\n")
    theme_projects: dict[str, list[str]] = defaultdict(list)
    for p in projects:
        for t in p["themes"]:
            theme_projects[t].append(p["name"])
    for theme, names in sorted(theme_projects.items(), key=lambda x: -len(x[1])):
        lines.append(f"- `{theme}`: {len(names)} project(s) — {', '.join(names)}")
    lines.append("")

    # Citation frequency
    cite_projects: dict[str, list[str]] = defaultdict(list)
    for p in projects:
        for c in p["citations"]:
            cite_projects[c].append(p["name"])
    multi_cites = {c: names for c, names in cite_projects.items() if len(names) > 1}
    if multi_cites:
        lines.append("## Citations Shared by Multiple Projects\n")
        for c, names in sorted(multi_cites.items(), key=lambda x: -len(x[1])):
            lines.append(f"- {c}: {', '.join(names)}")
        lines.append("")

    return "\n".join(lines)


def generate_suggestion(p1: dict, p2: dict, det: dict) -> str:
    """Generate a natural-language bridge suggestion."""
    themes = det.get("shared_themes", [])
    outcomes = det.get("shared_outcomes", [])
    mechanisms = det.get("shared_mechanisms", [])
    citations = det.get("shared_citations", [])

    parts: list[str] = []
    if "product recall" in themes:
        parts.append("both engage with product recall")
    if outcomes:
        parts.append(f"share the outcome dimension `{next(iter(outcomes))}`")
    if mechanisms:
        m = next(iter(mechanisms))
        parts.append(f"both employ `{m}` as a mechanism or method")
    if citations:
        parts.append(f"draw on shared literature (e.g., {citations[0]})")

    if not parts:
        return "Consider comparing theoretical framings for complementary insights."

    suggestion = f"These projects {' and '.join(parts)}."
    if "product recall" in themes and len(themes) > 1:
        suggestion += " You may be able to cross-test mechanisms or pool robustness checks."
    elif "did" in mechanisms or "difference-in-differences" in mechanisms:
        suggestion += " A shared empirical design may allow cross-project methodological validation."
    else:
        suggestion += " Explore whether theoretical mechanisms from one project can inform the other."
    return suggestion


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(description="Cross-theme bridge detector")
    parser.add_argument("--obsidian-root", type=Path, default=OBSIDIAN_ROOT)
    parser.add_argument("--min-score", type=float, default=2.0)
    parser.add_argument("--output", "-o", type=Path, help="Write Markdown to file")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    projects = read_projects(args.obsidian_root)

    if args.json:
        import json
        payload = []
        n = len(projects)
        for i in range(n):
            for j in range(i + 1, n):
                score, details = score_bridge(projects[i], projects[j])
                if score >= args.min_score:
                    payload.append({
                        "project_a": projects[i]["name"],
                        "project_b": projects[j]["name"],
                        "score": score,
                        "details": details,
                        "suggestion": generate_suggestion(projects[i], projects[j], details),
                    })
        payload.sort(key=lambda x: x["score"], reverse=True)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    report = generate_bridge_report(projects, min_score=args.min_score)

    if args.output:
        args.output.write_text(report, encoding="utf-8")
        print(f"[*] Bridge report written to {args.output}")
    else:
        print(report)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
