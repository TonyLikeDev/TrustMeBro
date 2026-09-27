---
name: roadmap-audit
description: Audit repository compliance against RoadmapFlow 3-tier context loading standards, token budgets, and layout separation. Use when the user runs /roadmap-audit, asks to audit the repository, check token budget compliance, or audit 3-tier layout structure.
---

# RoadmapFlow Repository Auditor

Audits a project repository against the 3-Tier Context Loading Model and Component Reuse standards.

## Workflow

1. **Execute Audit Engine**:
   Run the deterministic auditor:
   ```bash
   python3 src/scaffold.py audit .
   ```

2. **Check Categories**:
   - **Structure**: Existence of `PLAN.md`, `ROADMAP.md`, `.gitignore`, `.bobignore`.
   - **Tier 1 Context**: `.bob/context/architecture.md` size must be **≤ 650 tokens**.
   - **Tier 2 Context**: `.bob/context/current-phase.md` size must be **≤ 200 tokens**.
   - **Gitignore Safety**: `.gitignore` must properly exclude local session snapshot `current-phase.md`.
   - **Core Folders**: Standard directories `src/`, `tests/`, `docs/`, `scripts/`.
   - **Component Reuse Layout**: Reusable `src/db/`, `src/logic/`, `src/ui/` layout directories.

3. **Report to User**:
   - Display the itemized audit report `[PASS]` / `[FAIL]`.
   - Summarize overall status:
     - `✓ COMPLIANT`: All standards met.
     - `✗ NON-COMPLIANT`: List the exact steps to remedy failed checks.
