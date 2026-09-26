# Layout mode (tricklord)

`{layout}` maps this project: folders, components, database and logic. Use it to find where a task belongs before searching the code.

1. **Keep it current.** When a change adds, moves or removes a folder, component, table, field or piece of logic, update `{layout}` in the same commit: one line per entry, with its file path, and bump "Last updated".
2. **Adding something** (a feature, component, integration or data change; not a bug fix or a small tweak): first find where it fits in `{layout}` and what it touches, then size it.
   - **Small** (fits inside existing components, no database change, about a day of work): add it to `ROADMAP.md` as a new phase `## Feature <n>: <title>` with Build and Exit criteria items, tell the user in one line, and start. If there is no roadmap yet, create it from `{templates}/ROADMAP.md`. Refresh progress with `{progress_cmd}`.
   - **Big** (a new component, a database change, several components, or several days): plan it first with the roadmap-planner skill, and wait for the user's approval before adding phases to the roadmap or writing code.
   - Not sure which? Ask the user.
