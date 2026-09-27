# Bob test: every new task goes on the roadmap

**Result: ✅ pass.** IBM Bob, with tricklord's `.bob/` folder copied into a project, recorded a new task on the roadmap before writing any code.

- **Date:** 2026-09-27
- **Agent:** IBM Bob Shell 2.0.5, headless (`bob run`), Agent mode
- **tricklord:** `.bob/` from the repo working tree, hooks `SessionStart` + `UserPromptSubmit`
- **Task ID:** `22fdf4fa00395fcc3ecaf7472b82d4b9` · 35.2 s · 12 tool calls · total cost 0.458
- **Evidence:** full output in [`bob-run.log`](bob-run.log); screenshot in `bob_sessions/Screenshot 2026-09-27 at 15.03.44.png` (left window)

## Setup

A throwaway project with one function and a tricklord `LAYOUT.md`, but no roadmap:

```
app.py      def add(a, b): return a + b
LAYOUT.md   <!-- tricklord --> ... - **add**: adds two numbers -> `app.py:add`
.bob/       copied from the tricklord repo
```

```bash
bob run --workspace . --trust --max-cost 3 --max-turns 25 \
  "Add a function multiply(a, b) to app.py that returns a * b."
```

## What Bob did

| Step | Time | Action |
| :--- | :--- | :--- |
| before 1 | | `UserPromptSubmit` hook created `ROADMAP.md` from the template (Bob never wrote it; it already existed at step 2) |
| 1 | +4.1 s | Todo list: **1. Add multiply task to ROADMAP.md**, 2. implement, 3. update `LAYOUT.md`, 4. refresh progress |
| 2–3 | +6.5 s | Read `ROADMAP.md` and `app.py` |
| 4–5 | +13.0 s | Added `## Feature 1: multiply function` to `ROADMAP.md` (first attempt failed, retry succeeded) |
| 7 | +17.8 s | Added `multiply` to `app.py`, **after** the roadmap entry |
| 8 | +21.2 s | Added `multiply` to `LAYOUT.md`'s logic list |
| 9 | +25.5 s | Ticked both items with evidence (`app.py:multiply`, exit criterion `multiply(2, 3)` returns `6`) and added a change-log line |
| 11 | +30.9 s | Ran the progress script with the exact command from the `SessionStart` rules: roadmap at 100% |
| end | +34.1 s | "Added Feature 1: multiply function to ROADMAP.md before starting work." |

## Checks

| Check | Result |
| :--- | :--- |
| `ROADMAP.md` created by the hook, starting with `<!-- tricklord -->` | ✅ |
| Roadmap entry before the code change | ✅ step 5 before step 7 |
| Item ticked with evidence, change-log line added | ✅ |
| `LAYOUT.md` updated | ✅ |
| Progress block refreshed | ✅ 100% |
| User told in one line | ✅ |
| `SessionStart` output reached Bob | ✅ Bob used the quoted interpreter-and-script command that only those rules contain |

## Notes

- Cosmetic: Bob wrote "Exit criteria:" as plain text instead of a `### Exit criteria` heading and left out `### Build`; the progress script still counted both items. The roadmap header says "Plan: `PLAN.md`" although the project has no plan.
- Not run: the check that a question ("What does add() do?") adds no roadmap entry.
- The files in this folder are the state after the run: [`app.py`](app.py), [`LAYOUT.md`](LAYOUT.md), [`ROADMAP.md`](ROADMAP.md).
