---
name: roadmap-audit
description: Audit repository compliance against RoadmapFlow 3-tier context loading standards, token budgets, and layout separation. Use when the user runs /roadmap-audit, asks to audit the repository, check token budget compliance, or audit 3-tier layout structure.
---

# RoadmapFlow Repository Auditor

Audits a project repository against the 3-Tier Context Loading Model and Component Reuse standards.

## Workflow

1. **Execute Audit Engine**:
   ```bash
   python3 src/scaffold.py audit .
   ```

2. **Verify Standards**:
   - Check `PLAN.md`, `ROADMAP.md`, `.gitignore`, `.bobignore`.
   - Tier 1 anchor ≤ 650 tokens.
   - Tier 2 snapshot ≤ 200 tokens.
   - Component reuse layouts: `src/db/`, `src/logic/`, `src/ui/`.

3. **Report to User**:
   Display itemized pass/fail results.
