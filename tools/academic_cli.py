#!/usr/bin/env python3
"""
academic_cli.py — Unified CLI for academic infrastructure tools.

Commands:
    observe [date]     Run daily research activity observer
    reflect [date]     Run weekly reflection
    search QUERY       Semantic search across Vault
    index PROFILE      Build semantic index for a profile
    dashboard          Generate project status dashboard
    bridge             Detect cross-theme bridges
"""

import argparse
import subprocess
import sys
from pathlib import Path

INFRA_DIR = Path(__file__).parent.parent
SEMANTIC_DIR = INFRA_DIR / "tools" / "semantic_search"
JOBS_DIR = INFRA_DIR / "periodic_jobs"


def cmd_observe(args: argparse.Namespace) -> int:
    cmd = [sys.executable, str(JOBS_DIR / "observer.py")]
    if args.date:
        cmd.append(args.date)
    if args.dry_run:
        cmd.append("--dry-run")
    if args.force:
        cmd.append("--force")
    return subprocess.call(cmd)


def cmd_reflect(args: argparse.Namespace) -> int:
    cmd = [sys.executable, str(JOBS_DIR / "reflector.py")]
    if args.date:
        cmd.append(args.date)
    if args.dry_run:
        cmd.append("--dry-run")
    if args.force:
        cmd.append("--force")
    return subprocess.call(cmd)


def cmd_search(args: argparse.Namespace) -> int:
    cmd = [
        sys.executable, "-m", "search.cli", "search",
        args.query,
        "--profile", args.profile,
        "--top-k", str(args.top_k),
    ]
    if args.json:
        cmd.append("--json")
    return subprocess.call(cmd, cwd=str(SEMANTIC_DIR))


def cmd_index(args: argparse.Namespace) -> int:
    cmd = [
        sys.executable, "-m", "search.cli", "index",
        "--profile", args.profile,
    ]
    return subprocess.call(cmd, cwd=str(SEMANTIC_DIR))


def cmd_dashboard(args: argparse.Namespace) -> int:
    cmd = [sys.executable, str(INFRA_DIR / "tools" / "project_dashboard.py")]
    if args.output:
        cmd.extend(["--output", args.output])
    if args.json:
        cmd.append("--json")
    return subprocess.call(cmd)


def cmd_bridge(args: argparse.Namespace) -> int:
    cmd = [sys.executable, str(INFRA_DIR / "tools" / "bridge_detector.py")]
    if args.output:
        cmd.extend(["--output", args.output])
    if args.json:
        cmd.append("--json")
    if args.min_score:
        cmd.extend(["--min-score", str(args.min_score)])
    return subprocess.call(cmd)


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="academic",
        description="Academic infrastructure CLI",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # observe
    obs = sub.add_parser("observe", help="Run daily observer")
    obs.add_argument("date", nargs="?", help="Target date (YYYY-MM-DD)")
    obs.add_argument("--dry-run", action="store_true")
    obs.add_argument("--force", action="store_true")

    # reflect
    refl = sub.add_parser("reflect", help="Run weekly reflector")
    refl.add_argument("date", nargs="?", help="Week end date (YYYY-MM-DD)")
    refl.add_argument("--dry-run", action="store_true")
    refl.add_argument("--force", action="store_true")

    # search
    srch = sub.add_parser("search", help="Semantic search")
    srch.add_argument("query", help="Search query")
    srch.add_argument("--profile", default="literature-index")
    srch.add_argument("--top-k", type=int, default=10)
    srch.add_argument("--json", action="store_true")

    # index
    idx = sub.add_parser("index", help="Build semantic index")
    idx.add_argument("--profile", default="literature-index")

    # dashboard
    dash = sub.add_parser("dashboard", help="Project status dashboard")
    dash.add_argument("--output", "-o", help="Output Markdown file")
    dash.add_argument("--json", action="store_true", help="Output JSON")

    # bridge
    bridge = sub.add_parser("bridge", help="Cross-theme bridge detection")
    bridge.add_argument("--output", "-o", help="Output Markdown file")
    bridge.add_argument("--json", action="store_true", help="Output JSON")
    bridge.add_argument("--min-score", type=float, default=2.0, help="Minimum bridge score threshold")

    args = parser.parse_args()

    commands = {
        "observe": cmd_observe,
        "reflect": cmd_reflect,
        "search": cmd_search,
        "index": cmd_index,
        "dashboard": cmd_dashboard,
        "bridge": cmd_bridge,
    }
    return commands[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
