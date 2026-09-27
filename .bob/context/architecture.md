# Architecture Snapshot — RoadmapFlow

> Tier 1 context: always load this file at session start. Target size: ≤ 650 tokens.
> Last updated: 2026-09-27 (Session 003)

## What this project is
RoadmapFlow is a plan-first context engine and skill system for multi-session projects. Produces `PLAN.md` (master plan), `ROADMAP.md` (status board), `LAYOUT.md` (code map), and `.bob/context/` snapshots for >90% token reduction.

## Stack
- Engine: Python 3.10+ standard library (`src/roadmap.py`, `src/scaffold.py`, `src/benchmark.py`)
- Storage: Markdown files — Git-tracked, human-readable
- Integrations: Claude Code / Gemini CLI / IBM Bob 2.0 Plugin Hooks & Skills

## Key decisions
- **3-Tier Context Model**: Tier 1 (`architecture.md`, `LAYOUT.md`) → Tier 2 (`current-phase.md` ≤200 tok) → Tier 3 (`PLAN.md`, `ROADMAP.md`, init/research docs — outside main context).
- **Document Ingestion**: Existing/init docs (`planning/`, `research_docs/`) ingested during `/roadmap-planner` into `PLAN.md` Decisions Log, then isolated in Tier 3.
- **Deterministic State Engine**: Pure Python CLI handles progress math, validation, and snapshotting with zero external dependencies.
- **Git Drift Detection**: `/roadmap-sync` verifies code/doc changes against status checkboxes and logs traceable deviations.

## Source Layout
- `src/`: Core Python engine modules (`roadmap.py`, `scaffold.py`, `benchmark.py`)
- `src/db/`, `src/logic/`, `src/ui/`: Reusable component architecture layouts
- `src/hooks/`: Plugin SessionStart & Stop hooks (`roadmap_hook.py`)
- `src/rules/`: Dynamic system rules loaded into LLM sessions (`layout.md`, `roadmap.md`)
- `src/templates/`: Document templates (`LAYOUT.md`, `PLAN.md`, `ROADMAP.md`)
- `planning/`: Raw requirements, problem statement, and judging guidelines
- `.bob/context/`: Tier 1 (`architecture.md`) and Tier 2 (`current-phase.md`)

## What NOT to re-read every session
- Raw init/research docs (`planning/*.md`, `research_docs/`): Summarized in `PLAN.md` & `LAYOUT.md`.
- Historical `PLAN.md` & `ROADMAP.md` completed phases: Query via subagent or CLI snapshot.
