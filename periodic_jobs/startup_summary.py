#!/usr/bin/env python3
"""
startup_summary.py — Print a concise project status summary at Claude startup.

Reads the latest dashboard and bridge reports (if available) and prints
a 10-line summary to stdout, intended for use in an onStart hook.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

INFRA_DIR = Path("C:/Users/admin/.claude/academic_infrastructure")
DASHBOARD_PATH = INFRA_DIR / "contexts" / "memory" / "latest_dashboard.md"
BRIDGE_PATH = INFRA_DIR / "contexts" / "memory" / "latest_bridge.md"


def read_head(path: Path, lines: int = 15) -> list[str]:
    if not path.exists():
        return []
    try:
        return path.read_text(encoding="utf-8").splitlines()[:lines]
    except Exception:
        return []


def main() -> int:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print(f"\n{'='*50}")
    print(f"  Academic Infrastructure Startup Summary")
    print(f"  {now}")
    print(f"{'='*50}")

    # Dashboard head
    dash = read_head(DASHBOARD_PATH, 12)
    if dash:
        print("\n  [Projects]")
        for line in dash:
            if line.startswith("|") and "Project" not in line and "---" not in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 3:
                    name = parts[1]
                    status = parts[2]
                    last = parts[6] if len(parts) > 6 else "?"
                    block = parts[7] if len(parts) > 7 else ""
                    flag = "⚠️ " if "blocker" in block.lower() else "  "
                    print(f"  {flag}{name:40s} {status:12s} ({last})")
    else:
        print("\n  [Projects] No dashboard found. Run: python tools/project_dashboard.py")

    # Bridge head
    bridge_lines = read_head(BRIDGE_PATH, 20)
    if bridge_lines:
        print("\n  [Top Bridge]")
        for line in bridge_lines:
            stripped = line.strip()
            if stripped.startswith("###"):
                # Extract project names and score
                print(f"  {stripped}")
            elif stripped.startswith("**Suggestion:**"):
                suggestion = stripped.replace("**Suggestion:**", "").strip()
                print(f"  → {suggestion[:120]}{'…' if len(suggestion) > 120 else ''}")
                break
    else:
        print("\n  [Bridges] No bridge report found. Run: python tools/bridge_detector.py")

    print(f"\n{'='*50}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
