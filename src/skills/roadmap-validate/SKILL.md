---
name: roadmap-validate
description: Validate ROADMAP.md structure, phase task limits, and binary exit criteria. Use when the user runs /roadmap-validate, asks to verify exit criteria, check roadmap rules, or validate phase completion readiness.
---

# Roadmap Validator

Validates `ROADMAP.md` against RoadmapFlow integrity rules, ensuring all phases have verifiable binary exit criteria and maintainable phase sizes.

## Workflow

1. **Locate `ROADMAP.md`**:
   Check in order: `./ROADMAP.md`, `teamsource/ROADMAP.md`, `docs/ROADMAP.md`, `research_docs/ROADMAP.md`.

2. **Execute Validation**:
   Run the deterministic validation engine:
   ```bash
   python3 src/roadmap.py validate <path-to-roadmap>
   ```

3. **Evaluate Rules**:
   The engine verifies:
   - Presence of standard `## Week X` or `## Phase X` sections.
   - Task count per phase (recommends ≤ 12 tasks to prevent token bloat).
   - Mandatory presence of `### Exit criteria` in every phase.
   - Binary verifiable checklist items (`[ ]`, `[~]`, `[x]`).

4. **Report to User**:
   - If **PASS**: Report `✓ ROADMAP.md is fully compliant with RoadmapFlow standards!`, list the active phase, and show its exit criteria.
   - If **FAIL**: List each violation with phase name, exact failure reason, and the command/edit needed to fix it.
