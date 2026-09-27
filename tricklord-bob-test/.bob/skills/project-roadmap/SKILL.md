---
name: project-roadmap
description: Use when the user wants to start a new project, generate a project plan, create a roadmap, scaffold a PLAN.md and ROADMAP.md, or turn a project brief into a structured development plan with phases, tasks, exit criteria, and a live status tracker.
---

# Project Roadmap Generator

You generate two documents for any project: a frozen master plan (`PLAN.md`) and a live status
tracker (`ROADMAP.md`). Together they solve two problems: wasted planning time at project start,
and context window pollution from stale history during development.

## Core Principle

- `PLAN.md` — the **master plan**: static, never edited to record progress. Defines objectives,
  phases, per-phase tasks (Build / Measure / Write), exit criteria, risks, and decisions.
- `ROADMAP.md` — the **live status board**: ticked as work happens. Progress bars, change log,
  immediate next actions. Never edit PLAN.md to record progress; that is ROADMAP.md's job.

## 3-Tier Context Loading Model

This skill produces artifacts consumed at three token-budget tiers:

| Tier | File | Max size | Loaded when |
|------|------|----------|-------------|
| 1 | `.bob/context/architecture.md` | ~500 tokens | Every session start — always in context |
| 2 | `.bob/context/current-phase.md` | ~200 tokens | Each session, replaces full ROADMAP.md |
| 3 | `PLAN.md` + `ROADMAP.md` | unbounded | Only when explicitly needed (planning/review) |

**Rule**: During execution (`/dev-workflow`), only Tier 1 + Tier 2 are loaded. Tier 3 is NEVER
loaded into the main context window — use `spawn_subagent` if a deep-read of PLAN.md is needed.

---

## Step 1 — Gather the Project Brief

Read the user's message for:
- **Project name and one-sentence goal**
- **Tech stack** (language, framework, platform)
- **Deliverables** (what "done" looks like — working software, report, demo, API, etc.)
- **Timeline** (days, weeks, or phases available)
- **Team size** (solo or multi-person; if multi, any machine/environment differences)

If any of these are missing and cannot be inferred, ask for them before proceeding. Do not
generate a plan for a vague brief — a narrow, specific plan is always more useful.

---

## Step 2 — Decompose into Phases

Break the project into 4–10 phases (or weeks if the user gave a weekly timeline). Each phase must:

1. Have a **single clear theme** (e.g. "Infrastructure", "Core Algorithm", "Testing", "UI", "Release")
2. List concrete **Build** tasks — specific files or modules to create
3. List **Measure** tasks — what to run, benchmark, or validate
4. List **Write** tasks — docs, reports, comments, changelogs
5. Have **Exit criteria** — a binary pass/fail statement that closes the phase

Use the following heuristics for phase sizing:
- A phase should be completable in 1–3 days of focused work (solo) or 1 week (team)
- If a phase has more than 8 Build tasks, split it
- The last phase is always "Polish, test, deliver" — never skip it

---

## Step 3 — Write PLAN.md

Create `PLAN.md` in the project root (or the path the user specified).

Structure:

```
# Project Plan: <name>

> Static master plan. Edit to refine the plan; never edit to record progress — use ROADMAP.md.

## Overview
- Goal: <one sentence>
- Stack: <language / framework / tools>
- Deliverables: <what done looks like>
- Timeline: <total duration>
- Team: <solo / members / machines>

## Decisions Log
| Topic | Option A | Option B | Decision | Reason |
(list any non-obvious architectural decisions made at planning time)

## Phase 1: <name>
### Build
- [ ] <specific file or module to create>
### Measure
- [ ] <what to run or validate>
### Write
- [ ] <doc or report to produce>
### Exit criteria
- [ ] <binary statement: tests pass / benchmark hits threshold / etc.>

## Phase 2: <name>
...

## Risks and Fallbacks
| Risk | Signal | Fallback |

## Research Questions (if applicable)
- RQ1: ...
```

Each task must be concrete enough that a developer can tick it without interpretation.

---

## Step 4 — Write ROADMAP.md

Create `ROADMAP.md` in the same directory as `PLAN.md`.

Structure:

```
# Roadmap and Status

Master plan: `PLAN.md`. This file is the live status board.
**Rule: tick items here in the same commit as the work. Never edit PLAN.md to record progress.**

Legend: `[x]` done · `[~]` written but not verified · `[ ]` open

Last updated: <today's date>

## Progress

<!-- progress:start -->
**Progress: 0% of <N>-phase plan** `[░░░░░░░░░░░░░░░░░░░░]`

| Phase | Items | Done | Progress | |
| :--- | ---: | ---: | :--- | ---: |
| Phase 1 | <N> | 0 | `[░░░░░░░░░░░░░░░░░░░░]` | not started |
...
<!-- progress:end -->

---

## Phase 1: <name>

### Build
- [ ] <copy from PLAN.md>

### Measure
- [ ] <copy from PLAN.md>

### Write
- [ ] <copy from PLAN.md>

### Exit criteria
- [ ] <copy from PLAN.md>

---

## Phase 2: <name>
(paste but leave all items [ ] — not started)

...

## Immediate Next Actions (in order)
1. <first concrete action to take right now>
2. <second action>
3. <third action>

## Change Log
- <today's date>: Plan generated by IBM Bob 2.0. Phase 1 not started.
```

---

## Step 5 — Create Tier 1: architecture.md

Create `.bob/context/architecture.md` (create `.bob/context/` if it does not exist).

This is the **always-loaded** Tier 1 anchor — loaded at the top of every session, before any
task execution. Keep it under **500 tokens**.

```
# Architecture Snapshot — <project name>

> Tier 1 context: always load this file at session start.
> Last updated: <date>

## What this project is
<2 sentences: goal + what it produces>

## Stack
- Language/runtime: <...>
- Key libraries/frameworks: <...>
- Storage/infra: <...>

## Key decisions (non-obvious ones only)
- <decision 1>: <why>
- <decision 2>: <why>

## Source layout (top-level only)
<src/
  module-a/   — <one-line purpose>
  module-b/   — <one-line purpose>>

## What NOT to re-read every session
- PLAN.md: full phase/task breakdown — use /roadmap-navigator instead
- ROADMAP.md: full status — use .bob/context/current-phase.md instead
```

---

## Step 6 — Create Tier 2: current-phase.md

Create `.bob/context/current-phase.md`.

This is the **session-scoped** Tier 2 snapshot. Keep it under **200 tokens**.

```
# Current Phase Context

**Project**: <name>
**Current phase**: Phase 1 — <name>
**Phase status**: not started
**Last updated**: <today's date>

## Open Tasks

### Build
- [ ] <Phase 1 build tasks>

### Measure
- [ ] <Phase 1 measure tasks>

### Write
- [ ] <Phase 1 write tasks>

### Exit criteria
- [ ] <exit criteria>

## Completed in this phase
0 of <N> tasks done

## Immediate next action
<first item from "Immediate Next Actions" in ROADMAP.md>

## Phase summary (for Bob's reasoning)
<2–3 sentences: what Phase 1 is about and why it comes first>
```

**Critical**: do NOT include completed phases, future phases, or the change log in this file.

---

## Step 7 — Summarise and Hand Off

After creating all files, tell the user:

1. What was created (file paths)
2. The phase breakdown (phase names and approximate size)
3. Token cost breakdown:
   - Tier 1 `architecture.md`: ~500 tokens (always loaded)
   - Tier 2 `current-phase.md`: ~200 tokens (session scope)
   - Full PLAN.md + ROADMAP.md: only loaded on demand via subagent
4. How to start working: *"Run `/roadmap-navigator` at the start of each session to refresh
   Tier 2. Run `/dev-workflow` to execute tasks."*
5. The one immediate next action from `ROADMAP.md`

Do not start executing the plan — that is the `dev-workflow` skill's job.
