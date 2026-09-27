---
name: roadmap-scaffold
description: Scaffold a standard 3-tier RoadmapFlow project structure with PLAN.md, ROADMAP.md, .bob/context, and DB/Logic/UI component reuse folders. Use when the user runs /roadmap-scaffold, asks to scaffold a new project, or initialize standard 3-tier structure.
---

# RoadmapFlow Project Scaffolder

Initializes a complete, production-ready 3-tier project layout adhering to RoadmapFlow standards.

## Workflow

1. **Gather Parameters**:
   Ask or infer:
   - Target directory (e.g. `./my-project` or `.`)
   - Project Name (e.g. `MyProject`)
   - Tech Stack (e.g. `Python`, `Node.js`, `Go`)
   - Number of Phases (default: 3)

2. **Execute Scaffolder**:
   Run the scaffolder command:
   ```bash
   python3 src/scaffold.py init <dir> --name "<ProjectName>" --stack "<TechStack>" --phases <N>
   ```

3. **Verify Created Structure**:
   The scaffolder generates:
   - `PLAN.md` (Master plan with decisions log and risk matrix)
   - `ROADMAP.md` (Live status board with ASCII progress bar)
   - `.bob/context/architecture.md` (Tier 1 anchor, ≤500 tokens)
   - `.bob/context/current-phase.md` (Initial Tier 2 snapshot)
   - `src/db/`, `src/logic/`, `src/ui/` (Component reuse layouts)
   - `tests/`, `docs/`, `scripts/`, `.gitignore`, `.bobignore`

4. **Report to User**:
   Display the created tree structure and run an initial audit (`/roadmap-audit`) to confirm 100% compliance.
