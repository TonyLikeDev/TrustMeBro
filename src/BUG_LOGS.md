# Bug log

Known flaws in the tricklord plugin. One entry per bug. When one is fixed, set its status to `fixed (<commit>)` in both the table and the entry; `wontfix (<reason>)` if it is dropped.

| ID | Severity | Title | Status |
| :--- | :--- | :--- | :--- |
| BUG-001 | Serious | Activates on any file named `PLAN.md` or `ROADMAP.md` | open |
| BUG-002 | Serious | Never tested in a real Claude Code session | open |
| BUG-003 | Serious | Session start loads too much context | open |
| BUG-004 | Medium | Stop reminder is noisy and misses committed work | open |
| BUG-005 | Medium | `LAYOUT.md` drifts from the code | open |
| BUG-006 | Medium | Small features distort the progress numbers | open |
| BUG-007 | Medium | Planner projects never get a `LAYOUT.md` | open |
| BUG-008 | Minor | Rules are advice, not enforcement | open |
| BUG-009 | Minor | Generated progress block causes merge conflicts | open |
| BUG-010 | Minor | Redundant `src/.claude-plugin/marketplace.json` | open |
| BUG-011 | Minor | Example docs publish personal information | open |

---

### BUG-001: Activates on any file named `PLAN.md` or `ROADMAP.md`

- **Severity:** serious · **Found:** 2026-09-27 · **Status:** open
- **Where:** `hooks/roadmap_hook.py`, `find()` and `start()`
- **What happens:** the hook matches on file names only. Once installed, the plugin runs in every project, so any repo with an unrelated `PLAN.md` gets *"draft plan waiting for the user's approval... Don't start building"*, and any repo with its own `ROADMAP.md` (common in open-source projects) gets the roadmap rules and tick reminders.
- **Repro:**
  ```bash
  mkdir -p /tmp/other && echo "# Migration plan" > /tmp/other/PLAN.md
  echo '{}' | CLAUDE_PROJECT_DIR=/tmp/other python3 hooks/roadmap_hook.py start
  # prints the "Don't start building" notice
  ```
- **Fix idea:** only react to files the plugin wrote, e.g. require a `<!-- tricklord -->` marker line in all three templates (or the progress markers in `ROADMAP.md`).

### BUG-002: Never tested in a real Claude Code session

- **Severity:** serious · **Found:** 2026-09-27 · **Status:** open
- **Where:** whole plugin
- **What happens:** `tests/test_plugin.py` calls the hook script directly; nothing has run inside Claude Code. Unproven:
  - the skills finding `../../templates/` and `../../scripts/` relative to their base directory;
  - `/layout-init` working without the `tricklord:` prefix;
  - the `python3 ... || python ...` hook command on Windows.
- **Fix idea:** run `claude -p` with `--plugin-dir src` against a small sample project (one run per skill, plus one session with each hook), and test once on the Windows desktop.

### BUG-003: Session start loads too much context

- **Severity:** serious · **Found:** 2026-09-27 · **Status:** open
- **Where:** `hooks/roadmap_hook.py`, `start()`
- **What happens:** layout rules + roadmap rules + progress block + next actions + up to 6,000 characters of `LAYOUT.md` are injected in every session, even for a one-line question. With the example roadmap and a layout at the limit the hook printed **11,405 characters** (about 3k tokens). Claude Code likely truncates hook output past roughly 10,000 characters (exact limit not confirmed), so the last part (next actions) may be cut. `LAYOUT_BUDGET` only limits the layout, not the total.
- **Repro:** copy `research_docs/ROADMAP.md` and a 6,000-character `LAYOUT.md` into a folder, run the `start` hook on it, and count the output with `wc -c`.
- **Fix idea:** one shared budget for everything the hook prints; load the rules and next actions, and point to the files for the rest.

### BUG-004: Stop reminder is noisy and misses committed work

- **Severity:** medium · **Found:** 2026-09-27 · **Status:** open
- **Where:** `hooks/roadmap_hook.py`, `stop()`
- **What happens:**
  - It fires on any uncommitted change: docs, config, generated files, or a tree that was already dirty when the session started (the first reply of the session triggers it, even a pure question). Each reminder costs an extra Claude reply.
  - It misses the case it exists for: code committed without ticking the roadmap leaves a clean tree, so nothing fires.
  - It runs `git status --untracked-files=all` and `git diff HEAD` after every reply, which is slow in repos with large untracked data folders.
- **Fix idea:** only count files Claude edited this turn (read the transcript, or record edits with a PostToolUse hook on Edit/Write); also check the last commit for code without a `ROADMAP.md` change.

### BUG-005: `LAYOUT.md` drifts from the code

- **Severity:** medium · **Found:** 2026-09-27 · **Status:** open
- **Where:** `hooks/roadmap_hook.py` `stop()`, `skills/roadmap-sync/SKILL.md`
- **What happens:** the layout reminder only notices files being added, removed or renamed. A new database column or a new function inside an existing file does not trigger it. Nothing checks that the paths in `LAYOUT.md` still exist, and `/roadmap-sync` ignores `LAYOUT.md`.
- **Fix idea:** a small script that checks every path and `file:function` in `LAYOUT.md` exists, run by `/roadmap-sync` (and optionally the stop hook).

### BUG-006: Small features distort the progress numbers

- **Severity:** medium · **Found:** 2026-09-27 · **Status:** open
- **Where:** `scripts/roadmap_progress.py`
- **What happens:**
  - Overall progress is the average across phases, so a one-item `Feature 7` phase counts as much as a 17-item week.
  - The label unit comes from the first phase's name, so a roadmap of weeks plus features reads "12-week plan".
  - Any `## Something: title` heading is counted as a phase.
- **Fix idea:** weight by item count (or report features separately from the plan's phases), take the unit per phase type, and only count headings that start with a known phase word or sit between the progress block and "Next actions".

### BUG-007: Planner projects never get a `LAYOUT.md`

- **Severity:** medium · **Found:** 2026-09-27 · **Status:** open
- **Where:** `skills/roadmap-planner/SKILL.md`, `rules/layout.md`
- **What happens:** the add-something flow lives in the layout rules, which only load when `LAYOUT.md` exists. Projects started with `/roadmap-planner` never create one, so additions fall back to the roadmap's plan-change rule until someone runs `/layout-init`.
- **Fix idea:** when the first phase of a planned project closes, create `LAYOUT.md` (or suggest `/layout-init`).

### BUG-008: Rules are advice, not enforcement

- **Severity:** minor · **Found:** 2026-09-27 · **Status:** open
- **Where:** `rules/`
- **What happens:** "tick in the same commit", "read the roadmap first", "update the layout" and the small-versus-big call all depend on Claude following instructions. Only the stop reminder pushes back.
- **Fix idea:** accept for now; revisit after BUG-004 if drift shows up in real use.

### BUG-009: Generated progress block causes merge conflicts

- **Severity:** minor · **Found:** 2026-09-27 · **Status:** open
- **Where:** `ROADMAP.md` progress block, `scripts/roadmap_progress.py`
- **What happens:** when two people tick items on different branches, both regenerate the progress block and git reports a conflict on every merge.
- **Fix idea:** tell the user to resolve by taking either side and rerunning the script, or regenerate the block in a post-merge step.

### BUG-010: Redundant `src/.claude-plugin/marketplace.json`

- **Severity:** minor · **Found:** 2026-09-27 · **Status:** open
- **Where:** `src/.claude-plugin/marketplace.json`
- **What happens:** the marketplace at the top of the repo (`"source": "./src"`) is the one used for installs; the copy in `src/` is left over from before the move and duplicates its descriptions.
- **Fix idea:** delete it and update the Layout section of `README.md`.

### BUG-011: Example docs publish personal information

- **Severity:** minor · **Found:** 2026-09-27 · **Status:** open
- **Where:** `research_docs/RESEARCH_PLAN.md`
- **What happens:** the public example shows a student ID, class, university and the supervisor's name.
- **Fix idea:** replace them with placeholders in the example, if they shouldn't be public.
