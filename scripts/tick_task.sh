#!/usr/bin/env bash
# scripts/tick_task.sh - 1-Click task completion and progress recalculation.
# ponytail: Ticks a task in ROADMAP.md and recomputes progress in-place in one shot.

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 \"<task description or keyword>\"" >&2
    exit 1
fi

PATTERN="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

ROADMAP="${REPO_ROOT}/teamsource/ROADMAP.md"
if [[ ! -f "${ROADMAP}" && -f "${REPO_ROOT}/ROADMAP.md" ]]; then
    ROADMAP="${REPO_ROOT}/ROADMAP.md"
fi

python3 - <<EOF
import re
import sys
from pathlib import Path

p = Path("${ROADMAP}")
pattern = """${PATTERN}""".strip().lower()
content = p.read_text(encoding="utf-8")

lines = content.splitlines()
found = False
for i, line in enumerate(lines):
    if ("- [ ]" in line or "- [~]" in line) and pattern in line.lower():
        lines[i] = re.sub(r"-\s*\[(?: |~)\]", "- [x]", line, count=1)
        print(f"✓ Marked task done: {line.strip()} -> - [x]")
        found = True
        break

if not found:
    print(f"✗ Could not find any open task matching: '{pattern}'", file=sys.stderr)
    sys.exit(1)

p.write_text("\n".join(lines) + "\n", encoding="utf-8")
EOF

# Recalculate progress in-place
ROADMAP_ENGINE="${REPO_ROOT}/src/roadmap.py"
if [[ ! -f "${ROADMAP_ENGINE}" ]]; then
    ROADMAP_ENGINE="${REPO_ROOT}/things/roadmap.py"
fi
python3 "${ROADMAP_ENGINE}" progress "${ROADMAP}"
