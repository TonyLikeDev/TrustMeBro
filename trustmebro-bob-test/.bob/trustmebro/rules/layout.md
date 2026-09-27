# Layout mode (TrustMeBro)

`{layout}` maps this project: folders, components, database and logic. Use it to find where a task belongs before searching the code.

1. **Keep it current.** When a change adds, moves or removes a folder, component, table, field or piece of logic, update `{layout}` in the same commit: one line per entry, with its file path, and bump "Last updated".
2. **Every new task goes on the roadmap first.** When the user starts a task that will change the project (feature, fix, refactor, docs), find where it fits in `{layout}` and what it touches, record it in `ROADMAP.md` before doing the work, and tell the user in one line what you added. If there is no roadmap yet, first create it from `{templates}/ROADMAP.md`: keep its `<!-- trustmebro -->` first line (the hooks ignore files without it), progress block, Next actions and Change log, and replace its placeholder phases with the entry. Refresh progress with `{progress_cmd}`.
   - **Feature or addition** (fits inside existing components, no database change, about a day of work): a new phase `## Feature <n>: <title>` with Build and Exit criteria items, then start.
   - **Fix or small change**: an item under `## Maintenance: fixes and small changes` (create that phase once, then reuse it), then start.
   - **Big** (a new component, a database change, several components, or several days): a phase with the item `[ ] Plan approved by the user`, a plan from the roadmap-planner skill, and no code until the user approves.
   - Already on the roadmap: work from that item instead of adding a new one. Questions, and follow-ups that continue the current task, need no entry. Not sure of the size? Ask the user.
