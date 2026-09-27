# TrustMeBro rules

These rules apply when `LAYOUT.md` or `ROADMAP.md` in this project starts with the line `<!-- trustmebro -->`. Files without that line belong to the repo, not to TrustMeBro: leave them alone.

---

## Layout mode

`LAYOUT.md` maps this project: folders, components, database and logic. Use it to find where a task belongs before searching the code.

1. **Keep it current.** When a change adds, moves or removes a folder, component, table, field or piece of logic, update `LAYOUT.md` in the same commit: one line per entry, with its file path, and bump "Last updated".
2. **Every new task goes on the roadmap first.** When the user starts a task that will change the project (feature, fix, refactor, docs), find where it fits in `LAYOUT.md` and what it touches, record it in `ROADMAP.md` before doing the work, and tell the user in one line what you added. If there is no roadmap yet, first create it from `.bob/trustmebro/templates/ROADMAP.md`: keep its `<!-- trustmebro -->` first line (TrustMeBro ignores files without it), progress block, Next actions and Change log, and replace its placeholder phases with the entry. Refresh progress with `python3 .bob/trustmebro/scripts/roadmap_progress.py ROADMAP.md`.
   - **Feature or addition** (fits inside existing components, no database change, about a day of work): a new phase `## Feature <n>: <title>` with Build and Exit criteria items, then start.
   - **Fix or small change**: an item under `## Maintenance: fixes and small changes` (create that phase once, then reuse it), then start.
   - **Big** (a new component, a database change, several components, or several days): a phase with the item `[ ] Plan approved by the user`, a plan from the roadmap-planner skill, and no code until the user approves.
   - Already on the roadmap: work from that item instead of adding a new one. Questions, and follow-ups that continue the current task, need no entry. Not sure of the size? Ask the user.

---

## Roadmap mode

This project is run from a plan and a live roadmap.

- Plan: `PLAN.md`. What we intend to do. Never edited to record progress.
- Roadmap: `ROADMAP.md`. What is actually done. The source of truth for project state.

**Read `ROADMAP.md` before opening code files for a task**, and find the phase and item the task belongs to. If the roadmap and the code disagree about what is done, tell the user (or suggest running the roadmap-sync skill); don't silently trust either.

### Rules

1. **Tick in the same commit.** When an item is finished, tick it in the commit that finishes it: `[x]` done, `[~]` written but not verified, `[ ]` open. Every `[x]` names its evidence: a file path, a test, or a result.
2. **Log it.** Each tick gets a dated line under "Change log" (`- YYYY-MM-DD: what finished`) and updates "Last updated".
3. **Refresh progress** after ticking, never by hand: `python3 .bob/trustmebro/scripts/roadmap_progress.py ROADMAP.md`
4. **Keep "Next actions" ordered and current.** Anything you can't do yourself (submitting a document, collecting data, a decision, a machine you can't reach) is marked **User action** and listed first.
5. **Expand a phase when it starts**: copy its Build / Measure / Write / Exit criteria items from the plan into checkboxes under its heading. Phase headings stay `## <Phase>: <title>`, one per phase; the progress script counts the checkboxes under each.
6. **A phase closes on its exit criteria.** It isn't done while an exit criterion is open; move leftovers to Next actions.
7. **Plan changes need the user.** Dropping, adding or reordering work, or changing a decision: ask first. Once approved, add a dated line to the plan's "Deviations" section (`- YYYY-MM-DD: change, reason`), then update the roadmap. Never rewrite the plan to match what happened.
