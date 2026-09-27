# tricklord rules

These rules apply automatically when `LAYOUT.md` or `ROADMAP.md` is present in this project.

---

## Layout mode

`LAYOUT.md` maps this project: folders, components, database and logic. Use it to find where a task belongs before searching the code.

1. **Keep it current.** When a change adds, moves or removes a folder, component, table, field or piece of logic, update `LAYOUT.md` in the same commit: one line per entry, with its file path, and bump "Last updated".
2. **Adding something** (a feature, component, integration or data change; not a bug fix or a small tweak): first find where it fits in `LAYOUT.md` and what it touches, then size it.
   - **Small** (fits inside existing components, no database change, about a day of work): add it to `ROADMAP.md` as a new phase `## Feature <n>: <title>` with Build and Exit criteria items, tell the user in one line, and start. If there is no roadmap yet, create it from `src/templates/ROADMAP.md`. Refresh progress with `python3 src/scripts/roadmap_progress.py ROADMAP.md`.
   - **Big** (a new component, a database change, several components, or several days): plan it first with the roadmap-planner skill, and wait for the user's approval before adding phases to the roadmap or writing code.
   - Not sure which? Ask the user.

---

## Roadmap mode

This project is run from a plan and a live roadmap.

- Plan: `PLAN.md`. What we intend to do. Never edited to record progress.
- Roadmap: `ROADMAP.md`. What is actually done. The source of truth for project state.

**Read `ROADMAP.md` before opening code files for a task**, and find the phase and item the task belongs to. If the roadmap and the code disagree about what is done, tell the user (or suggest running the roadmap-sync skill); don't silently trust either.

### Rules

1. **Tick in the same commit.** When an item is finished, tick it in the commit that finishes it: `[x]` done, `[~]` written but not verified, `[ ]` open. Every `[x]` names its evidence: a file path, a test, or a result.
2. **Log it.** Each tick gets a dated line under "Change log" (`- YYYY-MM-DD: what finished`) and updates "Last updated".
3. **Refresh progress** after ticking, never by hand: `python3 src/scripts/roadmap_progress.py ROADMAP.md`
4. **Keep "Next actions" ordered and current.** Anything you can't do yourself (submitting a document, collecting data, a decision, a machine you can't reach) is marked **User action** and listed first.
5. **Expand a phase when it starts**: copy its Build / Measure / Write / Exit criteria items from the plan into checkboxes under its heading. Phase headings stay `## <Phase>: <title>`, one per phase; the progress script counts the checkboxes under each.
6. **A phase closes on its exit criteria.** It isn't done while an exit criterion is open; move leftovers to Next actions.
7. **Plan changes need the user.** Dropping, adding or reordering work, or changing a decision: ask first. Once approved, add a dated line to the plan's "Deviations" section (`- YYYY-MM-DD: change, reason`), then update the roadmap. Never rewrite the plan to match what happened.
