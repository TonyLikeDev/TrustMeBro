#!/usr/bin/env python3
"""
Bridge script matching teamsource/ROADMAP.md reference.
# ponytail: Simple delegate runner forwarding to things/roadmap.py.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "things"))

from roadmap import update_progress_in_file

if __name__ == "__main__":
    target = REPO_ROOT / "teamsource/ROADMAP.md"
    dry_run = "--dry-run" in sys.argv
    success, msg = update_progress_in_file(target, dry_run=dry_run)
    if success:
        print(f"✓ Progress block updated in {target}")
    else:
        print(f"✗ Failed: {msg}", file=sys.stderr)
        sys.exit(1)
