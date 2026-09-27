# tricklord plugin: live test log (2026-09-27)

> **These are Claude Code test runs, not IBM Bob sessions.** They test the tricklord Claude Code plugin in `src/`. The IBM Bob task session screenshots required for the submission go in `bob_sessions/` itself.

- **Tool:** Claude Code 2.1.283, `claude -p` (non-interactive) with `--plugin-dir src`, on macOS
- **Plugin version:** 0.3.0 for the hook tests, 0.3.1 (working tree) for the skill tests
- **Projects:** throwaway git repos built for each test, deleted afterwards
- **Models:** Haiku 4.5 for the hook tests, Sonnet 5 for the skill tests
- **Cost:** about $0.25 for the hook tests and $0.65 for the skill tests

## Summary

| # | Test | What it checks | Result |
| :--- | :--- | :--- | :--- |
| H1 | Unrelated `PLAN.md` | BUG-001: hooks ignore files without `<!-- tricklord -->` | ✅ pass |
| H2 | Large roadmap + 8.4k layout | BUG-003: session start stays within budget | ✅ pass |
| H3 | Question on a dirty tree | BUG-004: no edits, no reminder | ✅ pass |
| H4 | Create a new file | BUG-004: edit hook payload, layout reminder, no loop | ✅ pass |
| H5 | Edit a tracked file | BUG-004: roadmap reminder only | ✅ pass |
| S1 | `/orchestrator`, repo-owned `PLAN.md` / `ROADMAP.md` | Marker check: repo files are treated as absent | ✅ pass |
| S2 | `/orchestrator`, pre-marker tricklord roadmap | Legacy roadmap gets `roadmap-sync` offered | ✅ pass |
| S3 | `/orchestrator`, marked `PLAN.md`, no roadmap | Draft plan: asks for approval before stage 2 | ✅ pass |
| S4 | `/dedup-merge merge them` on a duplicate pair | Merge, verify, update `LAYOUT.md`, report numbers | ✅ pass, 2 minor misses |

## Hook tests (H1 to H5)

Run with `--output-format stream-json --verbose --include-hook-events`, reading each tricklord hook's exact output.

- **H1.** Project with `PLAN.md` = "# Migration plan" (no marker). Prompt: "Reply with just OK." The tricklord SessionStart hook printed nothing.
- **H2.** The example 10-week roadmap (marker added) next to an 8,437-character `LAYOUT.md`. The session received 4,291 characters: layout rules, roadmap rules, the one-line progress headline, all four next actions, and a pointer instead of the layout (was 11,405 characters before the fix).
- **H3.** Marked roadmap and layout, an untracked `notes.txt`, prompt "What is 2+2?". The Stop hook printed nothing.
- **H4.** Prompt: "Create a new file src/util.py containing a function add(a, b)". The edit hook received `session_id` and `tool_input.file_path`. Claude ticked the roadmap on its own from the session-start rules, so the Stop hook fired only the layout reminder; Claude updated `LAYOUT.md`; the follow-up Stop was quiet and the edit log was removed.
- **H5.** Prompt: "Add a one-line docstring to the greet function in src/app.py." Tracked file, so only the roadmap reminder fired; Claude answered "This change doesn't advance a roadmap item" and stopped.

Finding: the progress block stayed at 0% in H4 because running the progress script needs a Bash permission (logged as BUG-013).

## Skill tests (S1 to S4)

Each skill was invoked by its short name (`/orchestrator`, `/dedup-merge`), which resolved in `claude -p`.

**S1 to S3: `/orchestrator What should I run next in this project?`** Tools allowed: read-only (`head`, `ls`, `find`, `git log`, `git status`, Read). No file changed in any run.

| Project state | Answer |
| :--- | :--- |
| S1: `app.py`, repo-owned `PLAN.md` and `ROADMAP.md` (no marker) | "neither starts with `<!-- tricklord -->` (plain repo files, not tricklord's) ... count as absent." Recommends `layout-init`, asks before running it. |
| S2: `app.py`, `ROADMAP.md` with `<!-- progress:start -->` but no marker | "a tricklord roadmap predating the marker convention." Recommends `layout-init` first, then `roadmap-sync` to add the marker. |
| S3: marked `PLAN.md`, no roadmap, no code | "draft plan awaiting approval ... Do you approve this plan?" Stage 2 only after a yes. |

**S4: `/dedup-merge merge them`** on a Python project with `reports/sales_report.py` and `reports/inventory_report.py` (38 lines each, 71% identical), a non-duplicate `utils/fmt.py`, a test script, and a marked `LAYOUT.md`. Permission mode `acceptEdits`, Bash limited to `diff`, `wc`, `git`, `python3`, `ls`, `rm`, `cat`, `head`, `find`.

- Created a shared `reports/report.py` and kept the two old files as 12-line wrappers, because the tests import their names (the skill's rule for entry points).
- 76 → 58 lines (−24%); reported as a table with an explanation of why the saving is below half.
- Tests pass. Independent check: old and new code give byte-identical output on empty input, duplicate and blank names, sorting, large values and the negative-value errors.
- `utils/fmt.py` untouched; nothing committed.

Minor misses, observed in S1 and S4:
- `LAYOUT.md`: the folder tree was updated, but the Logic list was not pointed at the new `report.py:build_report`. The skill's step 4 now says to update both.
- The report skipped the skill's note that counts added lines separately from the net saving.
- In S1 the orchestrator read the repo's `PLAN.md` and `ROADMAP.md` in full although the skill says to check first lines only. Harmless here, but it costs tokens on large files.

## Not covered

- `/layout-init`, `/roadmap-planner` and `/roadmap-sync` live runs.
- Windows (the `python3 || python` hook command).
- Interactive sessions (all runs used `claude -p`).
