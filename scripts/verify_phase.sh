#!/usr/bin/env bash
# scripts/verify_phase.sh - Binary Exit Criteria Verification Gate.
# ponytail: Single command to verify roadmap compliance, test suite, and token budget.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "🔍 [1/3] Validating ROADMAP.md structure & binary exit criteria..."
ROADMAP="${REPO_ROOT}/teamsource/ROADMAP.md"
if [[ ! -f "${ROADMAP}" && -f "${REPO_ROOT}/ROADMAP.md" ]]; then
    ROADMAP="${REPO_ROOT}/ROADMAP.md"
fi
ROADMAP_ENGINE="${REPO_ROOT}/src/roadmap.py"
TEST_SUITE="${REPO_ROOT}/src/test_tools.py"
if [[ ! -f "${ROADMAP_ENGINE}" ]]; then
    ROADMAP_ENGINE="${REPO_ROOT}/things/roadmap.py"
    TEST_SUITE="${REPO_ROOT}/things/test_tools.py"
fi
python3 "${ROADMAP_ENGINE}" validate "${ROADMAP}"

echo ""
echo "🧪 [2/3] Running automated unit test suite..."
python3 "${TEST_SUITE}" -v

echo ""
echo "📏 [3/3] Checking Tier 2 snapshot token budget (<= 200 tokens)..."
SNAPSHOT="${REPO_ROOT}/.bob/context/current-phase.md"
python3 - <<EOF
import sys
from pathlib import Path
sys.path.insert(0, "${REPO_ROOT}/src")
sys.path.insert(0, "${REPO_ROOT}/things")
from roadmap import estimate_tokens

snap = Path("${SNAPSHOT}")
if not snap.exists():
    print("✗ Snapshot not found. Run scripts/sync_session.sh first!", file=sys.stderr)
    sys.exit(1)

tokens = estimate_tokens(snap.read_text(encoding="utf-8"))
if tokens > 200:
    print(f"✗ Snapshot exceeded budget: {tokens} tokens > 200", file=sys.stderr)
    sys.exit(1)
print(f"✓ Tier 2 budget PASSED: {tokens} tokens (Budget: <= 200 tokens)")
EOF

echo ""
echo "============================================================"
echo "✅ ALL EXIT CRITERIA VERIFIED (PASS) — Phase ready to close!"
echo "============================================================"
