#!/usr/bin/env python3
"""
startup_summary.py — Print a concise project status summary at Claude startup.

Reads the latest dashboard and bridge reports (if available) and prints
a 10-line summary to stdout, intended for use in an onStart hook.

Exit code is always 0 so that hook failures never block the session.
"""

from __future__ import annotations

import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
INFRA_DIR = Path(os.environ.get("CLAUDE_ACADEMIC_INFRA", "C:/Users/admin/.claude/academic_infrastructure"))
DASHBOARD_PATH = INFRA_DIR / "contexts" / "memory" / "latest_dashboard.md"
BRIDGE_PATH = INFRA_DIR / "contexts" / "memory" / "latest_bridge.md"
PROMOTIONS_DIR = INFRA_DIR / "contexts" / "thought_review" / "promotions"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def read_head(path: Path, lines: int = 15) -> list[str]:
    """Safely read the first *lines* of a text file."""
    if not path.exists():
        return []
    try:
        return path.read_text(encoding="utf-8").splitlines()[:lines]
    except Exception:
        return []


def find_pending_promotions(promo_dir: Path) -> list[Path]:
    """Return promotion drafts that haven't been reviewed (not in applied/ or rejected/)."""
    if not promo_dir.exists():
        return []
    pending = []
    for f in promo_dir.glob("*.md"):
        pending.append(f)
    return sorted(pending)


def print_error(msg: str) -> None:
    """Send diagnostics to stderr so stdout stays clean for the summary."""
    print(f"[startup_summary] {msg}", file=sys.stderr)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    try:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        print(f"\n{'='*50}")
        print(f"  Academic Infrastructure Startup Summary")
        print(f"  {now}")
        print(f"{'='*50}")

        # --- Dashboard -------------------------------------------------------
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

        # --- Bridge ----------------------------------------------------------
        bridge_lines = read_head(BRIDGE_PATH, 20)
        if bridge_lines:
            print("\n  [Top Bridge]")
            for line in bridge_lines:
                stripped = line.strip()
                if stripped.startswith("###"):
                    print(f"  {stripped}")
                elif stripped.startswith("**Suggestion:**"):
                    suggestion = stripped.replace("**Suggestion:**", "").strip()
                    print(f"  → {suggestion[:120]}{'…' if len(suggestion) > 120 else ''}")
                    break
        else:
            print("\n  [Bridges] No bridge report found. Run: python tools/bridge_detector.py")

        # --- Pending Promotions -----------------------------------------------
        pending = find_pending_promotions(PROMOTIONS_DIR)
        if pending:
            count = len(pending)
            print(f"\n  [!] {count} PENDING PROMOTION DRAFT(S) — review required:")
            for f in pending:
                # Read first heading for a one-line summary
                try:
                    for line in f.read_text(encoding="utf-8").splitlines():
                        if line.startswith("# Promotion Draft"):
                            print(f"      → {f.name}: {line.strip('# ')}")
                            break
                except Exception:
                    print(f"      → {f.name}")
            print(f"  [!] Action: review drafts, then move to applied/ or rejected/")

        print(f"\n{'='*50}\n")
        return 0

    except Exception as exc:
        print_error(f"Unexpected error: {exc}")
        traceback.print_exc(file=sys.stderr)
        return 0  # Always succeed so the hook never blocks the session


if __name__ == "__main__":
    raise SystemExit(main())
