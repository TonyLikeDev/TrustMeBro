# Project Issue Tickets & Architectural Debt Tracker

This registry documents active architectural issues, design conflicts, and component coupling bottlenecks identified in `src/`. All tickets are signed off by **tducn110**.

---

## 📋 Active Tickets

| Ticket ID | Title | Severity | Component | Status | Signed-off-by |
| :--- | :--- | :--- | :--- | :--- | :--- |
| [**ISSUE-001**](file:///home/pro/hackathon/docs/issues/ISSUE-001-duplicated-progress-engine.md) | Duplicated & Divergent Progress Calculation Engines | **HIGH** | `src/scripts/` vs `src/roadmap.py` | `OPEN` | `tducn110` |
| [**ISSUE-002**](file:///home/pro/hackathon/docs/issues/ISSUE-002-missing-tri-layout-separation.md) | Missing Tri-Layout (DB vs Logic vs UI) Component Reuse Structure | **MEDIUM** | `src/` Layout & Architecture | `OPEN` | `tducn110` |
| [**ISSUE-003**](file:///home/pro/hackathon/docs/issues/ISSUE-003-hook-lifecycle-context-drift.md) | Architectural Drift Between Claude Code Hooks & Bob 3-Tier Context Model | **HIGH** | `src/hooks/` vs `.bob/context/` | `RESOLVED` | `tducn110` |

---

## 🎯 Resolution Strategy

1. **Phase 1 (Resolve ISSUE-001)**: Refactor `src/scripts/roadmap_progress.py` to import and reuse `src/roadmap.py`.
2. **Phase 2 (Resolve ISSUE-002)**: Establish `src/db/`, `src/logic/`, and `src/ui/` sub-packages to enable real component reuse.
3. **Phase 3 (Resolve ISSUE-003)**: Align `src/hooks/roadmap_hook.py` with `.bob/context/current-phase.md` (Tier 2 loading) and support `teamsource/` discovery.
