---
name: roadmap-init
description: Build ROADMAP.md for a project that already has code, by reading the codebase, git history and docs to work out what is done, what is half done and what is left. Use when the user runs /roadmap-init or asks to add a roadmap or status board to an existing project.
---

# Roadmap init

Reconstruct the true state of an existing project as `ROADMAP.md`. Every status comes from evidence in the repo, not from guesses.

If a `ROADMAP.md` already exists, stop and suggest `/roadmap-sync` instead.

Plugin files, relative to this skill's base directory: template at `../../templates/ROADMAP.md`, progress script at `../../scripts/roadmap_progress.py`.

## 1. Read, in this order

1. `PLAN.md` or any plan, spec or proposal, the README, `CLAUDE.md` / `AGENTS.md`.
2. `git log --oneline` (last ~100 commits) and the directory tree: what was built, and in what order.
3. The code: entry points, modules, config, and stubs (`TODO`, `FIXME`, `NotImplementedError`, functions that only `pass`, empty files).
4. Tests: run the suite once if there is a standard command and it finishes in a couple of minutes. Passing tests are the strongest evidence.

## 2. Ask what the code can't tell you (one batch)

- What "finished" means for this project: deliverables and deadline.
- Weeks or milestones for the remaining work.
- Anything done outside the repo (documents submitted, data collected, decisions made).

## 3. Classify

- `[x]` done: exists and is verified (a test passes, it runs, a result is recorded). Name the evidence.
- `[~]` written but not verified: the code exists but nothing proves it works.
- `[ ]` open: planned, stubbed, or missing.

Group finished work into completed phases (git history gives the order), then lay out the remaining phases with Build / Measure / Write / Exit criteria. Without a plan file, write every remaining phase's items straight into the roadmap, since there is no plan to expand them from later.

## 4. Confirm, then write

Show a short summary: phases, item counts per state, and anything surprising (for example a feature the README claims but the code lacks). After the user confirms:

1. Write `ROADMAP.md` in the project root from the template, one `## <Phase>: <title>` heading per phase. Link the plan if one exists; otherwise the header says the roadmap was built from the code.
2. Next actions: the remaining work in order, **User action** items first.
3. Change log: `- YYYY-MM-DD: roadmap created from existing code.`
4. Run `python3 <base dir>/../../scripts/roadmap_progress.py ROADMAP.md` (`python` where `python3` is missing).

Don't create `PLAN.md` unless the user asks for one.
