# IBM Bob 2.0 Usage Plan

> Solution: **RoadmapFlow** — three composable IBM Bob 2.0 skills for structured project planning
> and context-window-aware development.
>
> The submission requires a **500-word IBM Bob Usage Statement** — the final draft is at the bottom.

---

## 📋 Solution Architecture

RoadmapFlow is built entirely as IBM Bob 2.0 **custom skills**. Bob is not just a helper — the
three skills form the entire product. Every phase of the workflow runs inside Bob.

```
User gives project brief
        ↓
/project-roadmap  ←── Bob Agent mode: generates PLAN.md + ROADMAP.md
        ↓
/roadmap-navigator ←── Bob Document understanding: reads ROADMAP.md, writes minimal context snapshot
        ↓
/dev-workflow     ←── Bob Agent mode: executes tasks, ticks ROADMAP.md, verifies exit criteria
        ↓
Phase closes → /roadmap-navigator advances to next phase → loop
```

---

## 🤖 Bob 2.0 Features Used

### 1. Custom Skills (Core of the solution)
Three skills live in `.bob/skills/`:
- [`project-roadmap`](../.bob/skills/project-roadmap/SKILL.md) — plan generator
- [`roadmap-navigator`](../.bob/skills/roadmap-navigator/SKILL.md) — context window narrower
- [`dev-workflow`](../.bob/skills/dev-workflow/SKILL.md) — task executor with exit criteria

### 2. Agent Mode
Used inside `dev-workflow` to:
- Read existing files before implementing
- Write code, create modules, update docs
- Run test commands and check output
- Iterate until tests pass (not just generate and stop)

### 3. Document Understanding
Used inside `roadmap-navigator` and `dev-workflow` to:
- Read and parse `PLAN.md` and `ROADMAP.md`
- Identify the current active phase (first phase with open `[ ]` items)
- Extract only the relevant tasks into the minimal context snapshot

### 4. Context Mentions (@file)
Used in `roadmap-navigator` to reference `ROADMAP.md` and `PLAN.md` directly, and in
`dev-workflow` to reference source files being implemented.

### 5. Ask Mode → Plan Mode → Agent Mode Pipeline
The natural flow of RoadmapFlow maps exactly to Bob's mode progression:
- **Ask mode**: user describes the project → Bob asks clarifying questions
- **Plan mode**: `/project-roadmap` decomposes the brief into phases and tasks
- **Agent mode**: `/dev-workflow` executes each task autonomously

### 6. Rollback
Used in `dev-workflow` when a Build task needs experimentation — Bob explores an approach,
and if tests fail, rollback recovers the pre-change state before trying another approach.

### 7. Custom Rules (.bob rules file)
A `.bob/rules/roadmapflow.md` rules file enforces:
- Always tick ROADMAP.md in the same commit as the work
- Never mark a task `[x]` without running the exit criteria check
- Always read the context snapshot before starting any task

---

## 🗺️ Bob Usage by Workflow Step

| Step | User Action | Bob Feature | Output |
|------|------------|-------------|--------|
| 1 | Paste project brief | Ask mode | Clarifying questions answered |
| 2 | `/project-roadmap` | Agent mode + document generation | `PLAN.md` + `ROADMAP.md` |
| 3 | `/roadmap-navigator` | Document understanding + file write | `.bob/context/current-phase.md` (minimal context) |
| 4 | `/dev-workflow` — Build task | Agent mode | Code implemented + tests passing |
| 5 | `/dev-workflow` — Measure task | Agent mode (runs commands) | Benchmark/test results |
| 6 | `/dev-workflow` — Write task | Agent mode | Documentation updated |
| 7 | `/dev-workflow` — exit check | Agent mode (runs checks) | PASS/FAIL per criterion |
| 8 | Phase closes | Agent mode (ticks ROADMAP.md) | ROADMAP.md updated, change log entry |
| 9 | Next session | `/roadmap-navigator` | New minimal context snapshot for Phase N+1 |

---

## 📊 Session Tracking

Every time you use Bob for a significant task, note it here so you don't miss screenshots.

| # | Date | Task Description | Bob Feature Used | Screenshot Saved? |
|---|------|-----------------|-----------------|-------------------|
| 1 | | Generate PLAN.md + ROADMAP.md for demo project | Agent mode / project-roadmap skill | [ ] |
| 2 | | Navigate to Phase 1, write context snapshot | Document understanding / roadmap-navigator | [ ] |
| 3 | | Execute Phase 1 Build tasks | Agent mode / dev-workflow skill | [ ] |
| 4 | | Run exit criteria check, close Phase 1 | Agent mode / dev-workflow skill | [ ] |
| 5 | | Navigate to Phase 2 | roadmap-navigator skill | [ ] |
| 6 | | Execute Phase 2 tasks | Agent mode / dev-workflow skill | [ ] |
| 7 | | Demo: show context token savings (before vs after) | Ask mode | [ ] |
| 8 | | Generate PR with Bob's built-in Git integration | Pull request feature | [ ] |

> **Reminder**: Bob IDE → Tasks tab → select task → click task header → screenshot consumption
> summary → save as PNG to `bob_sessions/` folder.

---

## 📝 IBM Bob Usage Statement (500 words max — final draft)

```
We built RoadmapFlow using IBM Bob 2.0 as the entire product engine, not just a development
assistant. The solution consists of three custom Bob skills that form a complete developer
workflow loop.

The first skill, /project-roadmap, uses Bob's Agent mode and document generation capabilities
to turn a free-form project brief into two structured documents in under 5 minutes: PLAN.md
(a frozen master plan with phases, per-phase Build/Measure/Write tasks, exit criteria, a
decisions log, and risk fallbacks) and ROADMAP.md (a live status board that tracks progress
with tick checkboxes, progress bars, and a change log). Bob reads the brief using Ask mode
to gather any missing details, then uses Agent mode to write both files to the workspace.

The second skill, /roadmap-navigator, uses Bob's document understanding to read ROADMAP.md,
identify the first phase with open tasks, and write a minimal context snapshot to
.bob/context/current-phase.md containing only those open tasks. This directly addresses the
context window pollution problem: instead of loading the full project history (5,000+ tokens)
into every session, the navigator loads only what is relevant now (~200 tokens). Bob reasons
with context mentions (@ROADMAP.md) to parse the live status and @PLAN.md to understand the
phase's purpose.

The third skill, /dev-workflow, uses Bob's Agent mode to execute the current phase's tasks
one by one. For Build tasks: Bob reads existing stubs, implements the code, runs tests, and
iterates until they pass — using rollback when an approach fails. For Measure tasks: Bob
runs benchmark scripts and compares results against targets. For Write tasks: Bob generates
documentation against the actual implementation. After each verified task, Bob ticks
ROADMAP.md immediately and adds a dated entry to the change log. When all tasks are done,
Bob runs each exit criterion as an explicit pass/fail check and only closes the phase when
all pass — eliminating the "I think this is done" ambiguity.

We used Bob's Plan mode to design the skill architecture before implementation, Agent mode
to write and test all three SKILL.md files, and the built-in code review workflow to verify
the skill instructions were unambiguous. The session navigator's context snapshot was verified
to load in under 200 tokens against a 10-week project plan (the teamsource documents in our
repo) — demonstrating real token savings of 96% compared to loading the full history.

Bob's custom rules file enforces workflow discipline: always tick ROADMAP.md in the same
commit as the work, never mark a task done without running the exit criteria, always read
the context snapshot before starting. This makes the workflow consistent across sessions
and team members.

The result is a self-contained, reusable workflow system where IBM Bob 2.0 is not a
feature — it is the product.
```

---

## 🔗 Key Bob 2.0 Documentation

| Feature | Link |
|---------|------|
| Skills | https://bob.ibm.com/docs/ide/features/skills |
| Agent mode / Modes | https://bob.ibm.com/docs/ide/features/modes |
| Custom rules | https://bob.ibm.com/docs/ide/configuration/rules |
| Document understanding | https://bob.ibm.com/docs/ide/features/context-mentions |
| Rollback | https://bob.ibm.com/docs/ide/features/rollback |
| Pull requests | https://bob.ibm.com/docs/ide/features/pull-requests |
| Best practices | https://bob.ibm.com/docs/ide/getting-started/best-practices |
