#!/usr/bin/env python3
"""
automation_runner.py — Orchestrate the academic infrastructure pipeline.

Modes:
    daily    : agentic_observer (LLM) → rule-based fallback → consolidate → dashboard
    agentic  : agentic_observer (LLM) → rule-based fallback → consolidate → dashboard
    weekly   : agentic daily + bridge → agentic_reflector (with rule fallback)
    full     : agentic daily + bridge → agentic_reflector

Usage:
    python automation_runner.py daily [--dry-run]
    python automation_runner.py agentic [--dry-run]
    python automation_runner.py weekly [--dry-run]
    python automation_runner.py full [--dry-run]
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────────────

INFRA_DIR = Path("C:/Users/admin/.claude/academic_infrastructure")
TOOLS_DIR = INFRA_DIR / "tools"
JOBS_DIR = INFRA_DIR / "periodic_jobs"
PYTHON = sys.executable

# ── Helpers ────────────────────────────────────────────────────────────────


def run(cmd: list[str], cwd: Path | None = None, label: str = "") -> int:
    """Run a subprocess command and print status."""
    display = label or " ".join(str(c) for c in cmd)
    print(f"\n[→] {display}")
    try:
        result = subprocess.run(cmd, cwd=cwd, check=False)
        if result.returncode != 0:
            print(f"[!] {display} exited with code {result.returncode}")
        return result.returncode
    except Exception as e:
        print(f"[!] {display} failed: {e}")
        return 1


# ── Pipeline Stages ────────────────────────────────────────────────────────


def stage_observer(date_str: str | None = None, dry_run: bool = False, force: bool = False) -> int:
    cmd = [PYTHON, str(JOBS_DIR / "observer.py")]
    if date_str:
        cmd.append(date_str)
    if dry_run:
        cmd.append("--dry-run")
    if force:
        cmd.append("--force")
    return run(cmd, label="observer (rule-based)")


def stage_agentic_observer(date_str: str | None = None, dry_run: bool = False, force: bool = False) -> int:
    cmd = [PYTHON, str(JOBS_DIR / "agentic_observer.py")]
    if date_str:
        cmd.append(date_str)
    if dry_run:
        cmd.append("--dry-run")
    if force:
        cmd.append("--force")
    return run(cmd, label="agentic_observer (LLM)")


def stage_observer_default(date_str: str | None = None, dry_run: bool = False, force: bool = False) -> int:
    """Run the agentic observer first, falling back to the rule-based observer."""
    agentic_rc = stage_agentic_observer(date_str, dry_run, force)
    if agentic_rc == 0:
        return 0
    print("[!] Agentic observer failed, falling back to rule-based observer...")
    return stage_observer(date_str, dry_run, force)


def stage_consolidate(dry_run: bool = False) -> int:
    cmd = [PYTHON, str(JOBS_DIR / "consolidate_observations.py")]
    if dry_run:
        cmd.append("--dry-run")
    return run(cmd, label="consolidate")


def stage_dashboard(dry_run: bool = False) -> int:
    if dry_run:
        print("\n[skip] dashboard (dry-run: would write latest_dashboard.md)")
        return 0
    cmd = [PYTHON, str(TOOLS_DIR / "project_dashboard.py"),
           "--output", str(INFRA_DIR / "contexts" / "memory" / "latest_dashboard.md")]
    return run(cmd, label="dashboard")


def stage_bridge(dry_run: bool = False) -> int:
    if dry_run:
        print("\n[skip] bridge (dry-run: would write latest_bridge.md)")
        return 0
    cmd = [PYTHON, str(TOOLS_DIR / "bridge_detector.py"),
           "--output", str(INFRA_DIR / "contexts" / "memory" / "latest_bridge.md")]
    return run(cmd, label="bridge")


def stage_git_maintenance(dry_run: bool = False) -> int:
    """Run git gc to compact objects and reclaim space. Safe: --auto only runs when needed."""
    if dry_run:
        print("\n[skip] git maintenance (dry-run)")
        return 0
    if not (INFRA_DIR / ".git").exists():
        print("[*] No git repo, skipping git maintenance.")
        return 0
    cmd = ["git", "gc", "--auto", "--prune=30.days.ago"]
    return run(cmd, cwd=INFRA_DIR, label="git maintenance")


def stage_reflector(date_str: str | None = None, dry_run: bool = False) -> int:
    cmd = [PYTHON, str(JOBS_DIR / "reflector.py")]
    if date_str:
        cmd.append(date_str)
    if dry_run:
        cmd.append("--dry-run")
    return run(cmd, label="reflector (rule-based)")


def stage_agentic_reflector(date_str: str | None = None, dry_run: bool = False, force: bool = False) -> int:
    cmd = [PYTHON, str(JOBS_DIR / "agentic_reflector.py")]
    if date_str:
        cmd.append(date_str)
    if dry_run:
        cmd.append("--dry-run")
    if force:
        cmd.append("--force")
    return run(cmd, label="agentic_reflector (LLM)")


# ── Orchestration ──────────────────────────────────────────────────────────


def run_daily(date_str: str | None = None, dry_run: bool = False, force: bool = False) -> int:
    """Daily pipeline: agentic observer → rule-based fallback → consolidate → dashboard."""
    print("=" * 60)
    print(f"[*] Daily Pipeline — {date_str or datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 60)

    codes = []
    codes.append(stage_observer_default(date_str, dry_run, force))
    codes.append(stage_consolidate(dry_run))
    codes.append(stage_dashboard(dry_run))

    failures = [c for c in codes if c != 0]
    print(f"\n[*] Daily pipeline complete. {len(failures)} stage(s) failed.")
    return max(codes) if failures else 0


def run_agentic(date_str: str | None = None, dry_run: bool = False, force: bool = False) -> int:
    """Agentic daily pipeline: LLM observer → rule-based fallback → consolidate → dashboard."""
    print("=" * 60)
    print(f"[*] Agentic Daily Pipeline — {date_str or datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 60)

    codes = []
    codes.append(stage_observer_default(date_str, dry_run, force))
    codes.append(stage_consolidate(dry_run))
    codes.append(stage_dashboard(dry_run))

    failures = [c for c in codes if c != 0]
    print(f"\n[*] Agentic daily pipeline complete. {len(failures)} stage(s) failed.")
    return max(codes) if failures else 0


def run_weekly(date_str: str | None = None, dry_run: bool = False, force: bool = False) -> int:
    """Weekly pipeline: agentic daily + bridge + agentic_reflector (with rule fallback)."""
    print("=" * 60)
    print(f"[*] Weekly Pipeline — week ending {date_str or datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 60)

    codes = []
    codes.append(run_agentic(date_str, dry_run, force))
    codes.append(stage_bridge(dry_run))
    # Try agentic reflector first; fallback to rule-based if it fails
    agentic_rc = stage_agentic_reflector(date_str, dry_run, force)
    if agentic_rc != 0:
        print("[!] Agentic reflector failed, falling back to rule-based reflector...")
        agentic_rc = stage_reflector(date_str, dry_run)
    codes.append(agentic_rc)
    # Periodic git maintenance
    codes.append(stage_git_maintenance(dry_run))

    failures = [c for c in codes if c != 0]
    print(f"\n[*] Weekly pipeline complete. {len(failures)} stage(s) failed.")
    return max(codes) if failures else 0


def run_full(date_str: str | None = None, dry_run: bool = False, force: bool = False) -> int:
    """Full pipeline: all stages."""
    return run_weekly(date_str, dry_run, force)


# ── CLI ────────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(description="Academic infrastructure automation runner")
    parser.add_argument("mode", choices=["daily", "agentic", "weekly", "full"], help="Pipeline mode")
    parser.add_argument("date", nargs="?", help="Target date (YYYY-MM-DD)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--force", action="store_true", help="Force overwrite observer/reflection outputs")
    args = parser.parse_args()

    if args.mode == "daily":
        return run_daily(args.date, args.dry_run, args.force)
    elif args.mode == "agentic":
        return run_agentic(args.date, args.dry_run, args.force)
    elif args.mode == "weekly":
        return run_weekly(args.date, args.dry_run, args.force)
    else:
        return run_full(args.date, args.dry_run, args.force)


if __name__ == "__main__":
    raise SystemExit(main())
