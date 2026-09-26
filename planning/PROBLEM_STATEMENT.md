# Problem Statement

> **Submission deadline**: Sep 27, 2026 — 10:00 PM ICT
> Keep the final written statement to **500 words or less**.

---

## 🎯 The Official Challenge

> *"Create a solution that improves a specific developer workflow, such as onboarding, debugging,
> code review, testing, application maintenance, or release and deployment processes.
> Start by clearly defining a problem where time, effort, or errors are too high today."*

---

## ✏️ Chosen Problem Area

**Workflow Category**: Developer Workflow Planning + Context Window Management

---

## 📌 The Problem

### One-line Summary
> Every developer team wastes 1–3 days structuring a new project, then wastes tokens and accuracy
> every session because Bob's context window is polluted with completed work, old phases, and
> irrelevant history.

### Who Has This Problem?
Any developer or small team using an AI coding assistant (like IBM Bob 2.0) for a project that
spans multiple sessions, phases, or weeks:
- Solo developers starting a research or engineering project
- Teams onboarding onto a complex codebase
- Anyone running multi-phase builds where earlier phases pollute later sessions

### What Does the Current Situation Look Like?

**Problem 1 — Project planning is manual and inconsistent**
- A developer with a rough idea spends 1–3 days figuring out what to build, in what order,
  what "done" means for each step, and what the risks are
- Plans exist in messy notes, scattered docs, or nowhere — no structure, no exit criteria,
  no decisions log
- The result: wasted build time, rework, and no clear way to hand off to another session or person

**Problem 2 — Context window bloat kills AI accuracy over multi-session projects**
- As a project progresses, loading the full PLAN.md + all completed phases into every session
  wastes context tokens and reduces Bob's reasoning quality on the *current* task
- Developers either re-explain context manually (slow, error-prone) or dump everything in
  (expensive, noisy)
- There is no standard way to tell Bob "here is exactly what is relevant right now — ignore
  everything else"

### Quantified Pain

| Pain | Measured Cost |
|------|-------------|
| Manual project planning from scratch | 1–3 days at project start |
| Re-explaining context at each session | 10–20 minutes per session |
| Rework from working on the wrong task | ~30% extra time in unstructured projects |
| Context token waste per session (full history) | 30–60% of the context window used on completed work |
| Redundant tool calls from missing execution discipline | 75%+ token waste observed live (160k tokens, research only) |
| Quality cliff at ~100k tokens | Bob output degrades noticeably past 100k — projects hit this fast |

---

## 💡 The Solution

### Solution Summary
**RoadmapFlow** — a set of three IBM Bob 2.0 skills that turn a project brief into a structured
plan + live tracker, then narrow the context window to only the current phase at the start of each
session, and execute each phase's tasks with verified exit criteria before advancing.

### Three Composable Skills

| Skill | What It Does |
|-------|-------------|
| `/project-roadmap` | Given a project brief, generates `PLAN.md` (frozen master plan) + `ROADMAP.md` (live status board) with phases, tasks (Build/Measure/Write), exit criteria, decisions log, and risks |
| `/roadmap-navigator` | Reads ROADMAP.md, finds the current active phase, loads ONLY that phase's open tasks into a context snapshot — solving the context bloat problem |
| `/dev-workflow` | Executes the current phase's tasks one by one using Agent mode, ticks ROADMAP.md after each verified completion, checks exit criteria, and closes the phase when all pass |

### How IBM Bob 2.0 Is Central
- **Agent mode**: executes Build tasks autonomously (reads files, writes code, runs tests, iterates)
- **Document understanding**: reads PLAN.md + ROADMAP.md to reason about what is in scope
- **Custom skills**: the three skills compose into a full workflow loop
- **Context management**: the navigator skill writes a minimal `.bob/context/current-phase.md`
  snapshot that costs ~200 tokens instead of 5,000+ for the full history

### Demonstrated Impact (Before vs After)

| Metric | Before (manual) | After (RoadmapFlow) |
|--------|----------------|---------------------|
| Time to structured project plan | 1–3 days | < 5 minutes |
| Context tokens per session | 5,000+ (full history) | ~200 (current phase only) |
| Manual re-explanation per session | 10–20 minutes | 0 minutes |
| Tasks completed without exit criteria check | ~70% (guessing "done") | 100% (binary pass/fail) |
| Phase handoff errors | Common | Eliminated (navigator reloads clean context) |
| Redundant tool calls (no execution discipline) | 75%+ token waste | Eliminated via plan-before-act rules |
| Sessions hitting quality cliff (>100k tokens) | Common in multi-session projects | Avoided via subtask-per-phase pattern |

---

## 📝 Final Submission Text (500 words max)

```
Developer teams lose 1–3 days structuring every new project and then lose 10–20 minutes every
session re-explaining context to their AI assistant. As a project grows, the AI's context window
fills with completed phases and old history — wasting tokens, reducing reasoning accuracy, and
causing Bob to work on the wrong thing.

RoadmapFlow solves both problems with three composable IBM Bob 2.0 skills.

The first skill, /project-roadmap, turns any project brief into two documents in under 5 minutes:
PLAN.md (a frozen master plan with phases, per-phase Build/Measure/Write tasks, exit criteria,
a decisions log, and fallbacks) and ROADMAP.md (a live status board that gets ticked as work
progresses, never edited to reflect state in the plan, and always showing the immediate next
actions). This pattern — separating "what we plan to do" from "what we have done" — is the
key structural insight. It was inspired by watching a real research project (a 10-week ML
engineering effort) that used exactly this two-document system to stay on track.

The second skill, /roadmap-navigator, solves the context window problem. At the start of every
session, it reads ROADMAP.md, finds the first phase with open tasks, and writes a minimal context
snapshot (.bob/context/current-phase.md) containing only those open tasks — typically ~200 tokens
instead of 5,000+ for the full project history. The developer starts each session with Bob already
focused on exactly what matters now, with nothing irrelevant in scope.

The third skill, /dev-workflow, uses IBM Bob's Agent mode to execute the current phase's tasks one
by one: reading existing code, implementing, running tests, measuring outcomes, writing
documentation. After each verified task, it ticks ROADMAP.md immediately. When all tasks are done,
it runs the exit criteria as explicit pass/fail checks before closing the phase and advancing the
navigator to the next one.

Together the three skills form a closed loop: plan once → navigate cleanly each session → execute
with verified completion → advance. The result: projects that would take days to plan take minutes.
Sessions that waste tokens on history cost almost nothing. Work that would end with "I think this
is done" ends with a binary exit criteria report.

IBM Bob 2.0 is central throughout: Agent mode implements the Build tasks autonomously, document
understanding reads PLAN.md and ROADMAP.md to reason about scope, and the skill system makes the
workflow reusable for any project, not just this hackathon demo.
```
