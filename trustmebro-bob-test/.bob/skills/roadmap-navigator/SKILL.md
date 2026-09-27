---
name: roadmap-navigator
description: Use when starting a new work session, loading project context, narrowing the context window to the current phase, checking what to work on next, or when the user says "what should I work on", "load my roadmap", "where am I in the project", or "start session".
---

# Roadmap Navigator

You solve the **context window pollution problem**: at the start of every session, instead of
loading the entire project history into context, you read only the current phase from ROADMAP.md
and surface exactly what needs to happen next. Nothing more.

## Core Principle

A large PLAN.md full of completed phases wastes context tokens and reduces Bob's accuracy on the
*current* task. This skill reads the live ROADMAP.md, identifies the active phase, loads only
that phase's tasks, and writes a Tier 2 snapshot (~200 tokens) for focused work.

## 3-Tier Model (reminder)

| Tier | File | Target size | Your job |
|------|------|-------------|----------|
| 1 | `.bob/context/architecture.md` | ≤500 tokens | Read it — do NOT rewrite unless asked |
| 2 | `.bob/context/current-phase.md` | ≤200 tokens | **Write/refresh this every session** |
| 3 | `PLAN.md` + `ROADMAP.md` | unbounded | Source of truth — read, never load fully into main context |

**Subagent rule**: If the user asks for a deep analysis of PLAN.md or ROADMAP.md, spawn a
`spawn_subagent(type: "explore")` instead of reading the full files into main context.

---

## Step 1 — Locate the Roadmap

Look for `ROADMAP.md` in the following order:
1. Project root (`./ROADMAP.md`)
2. Any path the user specifies

If `ROADMAP.md` does not exist:
- Check whether `PLAN.md` exists → if so, tell the user to run `/project-roadmap` first to
  generate the ROADMAP.md from the plan
- If neither exists → tell the user to run `/project-roadmap` with a project brief

Do not proceed without a valid `ROADMAP.md`.

---

## Step 2 — Parse the Current Phase

Read `ROADMAP.md` and identify the **current active phase**:

- The current phase is the **first phase that has at least one `[ ]` (open) item**
- If a phase has mix of `[x]` (done) and `[ ]` (open) items — it is in progress, it is current
- If all items in all phases are `[x]` → the project is complete; tell the user and stop
- If a phase has `[~]` items (written but not verified) — treat as open; they need verification

Extract from the current phase:
1. Phase name and number
2. All `[ ]` and `[~]` tasks (Build / Measure / Write / Exit criteria)
3. The "Immediate Next Actions" section from the bottom of ROADMAP.md
4. Count of completed tasks (for progress display)

---

## Step 3 — Check Tier 1

Read `.bob/context/architecture.md` if it exists. Confirm it is not stale (i.e. the project name
and stack still match). If it is missing, alert the user:
> "`.bob/context/architecture.md` not found. Run `/project-roadmap` to generate it, or create it
> manually. Tier 1 context is missing — execution will lack architectural grounding."

Do NOT rewrite architecture.md during this skill — that is `/project-roadmap`'s responsibility.

---

## Step 4 — Write Tier 2: current-phase.md (≤200 tokens)

Write `.bob/context/current-phase.md` with ONLY the current phase's open tasks.

**Token budget: 200 tokens maximum.** Count carefully:
- Do NOT list completed (`[x]`) tasks — count only
- Do NOT include future phases
- Do NOT include the change log
- Phase summary: 2 sentences max

```
# Current Phase Context

**Project**: <name from ROADMAP.md header>
**Current phase**: Phase <N> — <name>
**Phase status**: <not started | in progress | N/M tasks done>
**Last updated**: <today's date and time>

## Open Tasks

### Build
- [ ] <only open build tasks>

### Measure
- [ ] <only open measure tasks>

### Write
- [ ] <only open write tasks>

### Exit criteria
- [ ] <exit criteria not yet passed>

## Completed in this phase
<count only — e.g. "7 of 12 tasks done">

## Immediate next action
<single most important next step>

## Phase summary
<2 sentences: what this phase is about and why>
```

---

## Step 5 — Surface the Session Brief

Present a concise session brief to the user:

```
## 📍 Session Brief — <project name>

**Current phase**: Phase <N> — <name>
**Progress**: <N>/<M> tasks done  [████████░░░░░░░░░░░░] <X>%

**Open tasks this phase** (<count>):
Build:   <list open build tasks, one line each>
Measure: <list open measure tasks, one line each>
Write:   <list open write tasks, one line each>
Exit:    <exit criteria remaining>

**Context loaded**:
- Tier 1: architecture.md (~500 tokens) ✓
- Tier 2: current-phase.md (~200 tokens) ✓ (just written)
- Tier 3: PLAN.md / ROADMAP.md — NOT loaded (use subagent if needed)

**Next action**: <single most important next step>

---
Run `/dev-workflow` to start executing the current phase's tasks.
```

---

## Step 6 — Offer to Proceed

After presenting the brief, ask:
> "Ready to start? Run `/dev-workflow` to execute these tasks, or tell me which specific task to tackle first."

Do not start executing tasks automatically — wait for the user to confirm. The user may want to
adjust priorities or skip a task before starting.

---

## Notes

- This skill is designed to be run at the **start of every session** — it costs very little
  (reads 1–2 files) and pays off by keeping every subsequent tool call focused.
- The Tier 2 snapshot file (`.bob/context/current-phase.md`) is intentionally NOT committed to
  git — add it to `.gitignore` and `.bobignore`. It is a local session aid, not a project artifact.
- If the user is mid-phase from a previous session, the snapshot will already be partially correct;
  this skill just verifies and refreshes it.
- **Never spawn a subagent just to parse ROADMAP.md** — it is a small file; read it directly.
  Only use `spawn_subagent` when the user explicitly asks for deep PLAN.md analysis.
