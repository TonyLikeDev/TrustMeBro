# Architecture Snapshot — RoadmapFlow

> Tier 1 context: always load this file at session start.
> Last updated: 2025-01 (Session 002)

## What this project is
RoadmapFlow is a set of 3 composable IBM Bob 2.0 skills that close the plan → execute → track loop
for solo developers and small teams doing multi-session AI-assisted projects. It produces
`PLAN.md` (frozen master plan), `ROADMAP.md` (live status board), and `.bob/context/` snapshots
that keep each session's token cost minimal.

## Stack
- Platform: IBM Bob 2.0 (Skills + Custom Modes + Rules)
- Storage: files on disk (Markdown) — Git-tracked, human-readable
- No MCP servers, no external APIs, no database

## Key decisions
- **3-tier context loading**: architecture.md (Tier 1, ≤500 tok) → current-phase.md (Tier 2,
  ≤200 tok) → PLAN.md + ROADMAP.md (Tier 3, never in main context). Rationale: 75% token waste
  observed in Session 001 (160k tokens, no code written).
- **No MCP layer**: removed as over-engineering. Bob reads/writes files directly via native tools.
- **Mode-specific rules**: rules-agent/ enforces plan-before-act; rules-ask/ and rules-plan/ are
  lean, mode-targeted. Reduces irrelevant rule noise per mode.
- **Actor-Critic via subagents**: high-risk tasks spawn a Critic subagent for review.
  Boosts reliability from ~75% to ~85-90% without unbounded context growth.

## Source layout
```
.bob/
  skills/
    project-roadmap/SKILL.md   — generates PLAN.md + ROADMAP.md + context files
    roadmap-navigator/SKILL.md — refreshes Tier 2 snapshot at session start
    dev-workflow/SKILL.md      — executes tasks, ticks ROADMAP.md, closes phases
  rules-agent/
    execution-discipline.md    — plan-before-act, no redundant calls, token budget
  rules-ask/
    clarification-only.md      — Ask mode: no planning, no execution
  rules-plan/
    architecture-aware.md      — Plan mode: read architecture.md before proposing
  context/
    architecture.md            — THIS FILE (Tier 1, always loaded)
    current-phase.md           — Tier 2 snapshot (session-local, not committed)
planning/
  CURRENT_STATE.md             — problem statement, solution design, open items
docs/                          — submission docs, demo scripts
slides/                        — hackathon presentation
teamsource/                    — live demo project (proof of RoadmapFlow working)
```

## What NOT to re-read every session
- `planning/CURRENT_STATE.md`: historical context — use this file + current-phase.md instead
- `PLAN.md` / `ROADMAP.md` of demo project: load via subagent only
- Any completed-phase content: already ticked, not relevant to current work
