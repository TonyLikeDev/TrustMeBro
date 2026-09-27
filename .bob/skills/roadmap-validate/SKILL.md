---
name: roadmap-validate
description: Validate ROADMAP.md structure, phase task limits, and binary exit criteria. Use when the user runs /roadmap-validate, asks to verify exit criteria, check roadmap rules, or validate phase completion readiness.
---

# Roadmap Validator

Validates `ROADMAP.md` against RoadmapFlow integrity rules, ensuring all phases have verifiable binary exit criteria and maintainable phase sizes.

## Workflow

1. **Locate `ROADMAP.md`**:
   Check `./ROADMAP.md`, `teamsource/ROADMAP.md`, or `docs/ROADMAP.md`.

2. **Execute Validation**:
   ```bash
   python3 src/roadmap.py validate <path-to-roadmap>
   ```

3. **Report to User**:
   - If **PASS**: Report compliance and show active phase exit criteria.
   - If **FAIL**: Detail issues and propose remedies.
