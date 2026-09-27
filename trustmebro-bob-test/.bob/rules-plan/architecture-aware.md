# Plan Mode Rules — RoadmapFlow

## Purpose
Plan mode is for **architecture-aware planning only**. It proposes designs and structures;
it does NOT execute, write code, or tick ROADMAP.md.

## Rules

### Rule 1: Read architecture.md before proposing
Before proposing any architectural change, design, or phase structure:
1. Read `.bob/context/architecture.md` (Tier 1) — confirm stack, key decisions, source layout
2. Proposals must be consistent with existing decisions in architecture.md
3. If a proposal contradicts a prior decision → flag it explicitly and ask for confirmation

### Rule 2: No execution
Do not write production code, create implementation files, or call build tools in Plan mode.
Pseudocode and file structure sketches are fine.
If the user asks to implement → redirect: *"Switch to Agent mode for that."*

### Rule 3: Decisions must be logged
Any non-obvious architectural decision reached during planning must be written to
`PLAN.md`'s Decisions Log before ending the planning session.
Format:
```
| Topic | Option A | Option B | Decision | Reason |
```

### Rule 4: Phase sizing guardrails
When proposing or refining phases:
- Max 8 Build tasks per phase — split if exceeded
- Every phase needs binary Exit criteria (not fuzzy goals)
- Last phase is always "Polish, test, deliver"

### Rule 5: Token discipline
Do not load full ROADMAP.md history into Plan mode.
Read `.bob/context/current-phase.md` for current state; read PLAN.md only if explicitly asked
to review the full plan.
