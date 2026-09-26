#!/usr/bin/env bash
# scripts/sync_session.sh - 1-Click session start and context refresh.
# ponytail: Single bash script for instant terminal session brief; zero external tools needed.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

ROADMAP="${REPO_ROOT}/teamsource/ROADMAP.md"
if [[ ! -f "${ROADMAP}" && -f "${REPO_ROOT}/ROADMAP.md" ]]; then
    ROADMAP="${REPO_ROOT}/ROADMAP.md"
fi

SNAPSHOT="${REPO_ROOT}/.bob/context/current-phase.md"
mkdir -p "$(dirname "${SNAPSHOT}")"

ROADMAP_ENGINE="${REPO_ROOT}/src/roadmap.py"
if [[ ! -f "${ROADMAP_ENGINE}" ]]; then
    ROADMAP_ENGINE="${REPO_ROOT}/things/roadmap.py"
fi
python3 "${ROADMAP_ENGINE}" snapshot "${ROADMAP}" --output "${SNAPSHOT}"

echo ""
echo "============================================================"
echo "📍 ROADMAPFLOW SESSION BRIEF"
echo "============================================================"
cat "${SNAPSHOT}"
echo "============================================================"
echo "💡 Tier 1 (architecture.md) & Tier 2 (current-phase.md) ready."
echo "🚀 Run Bob Agent mode or execute next task directly."
