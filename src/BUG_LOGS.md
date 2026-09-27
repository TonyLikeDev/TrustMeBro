# Bug log

Known flaws in the tricklord plugin. One entry per bug. When one is fixed, set its status to `fixed (<version>)` in both the table and the entry and replace **Fix idea** with what was done; `wontfix (<reason>)` if it is dropped.

| ID | Severity | Title | Status |
| :--- | :--- | :--- | :--- |
| BUG-001 | Serious | Activates on any file named `PLAN.md` or `ROADMAP.md` | fixed (v0.3.0) |
| BUG-002 | Serious | Never tested in a real Claude Code session | open |
| BUG-003 | Serious | Session start loads too much context | fixed (v0.3.0) |
| BUG-004 | Medium | Stop reminder is noisy and misses committed work | fixed (v0.3.0) |
| BUG-005 | Medium | `LAYOUT.md` drifts from the code | open |
| BUG-006 | Medium | Small features distort the progress numbers | open |
| BUG-007 | Medium | Planner projects never get a `LAYOUT.md` | open |
| BUG-008 | Minor | Rules are advice, not enforcement | open |
| BUG-009 | Minor | Generated progress block causes merge conflicts | open |
| BUG-010 | Minor | Redundant `src/.claude-plugin/marketplace.json` | open |
| BUG-011 | Minor | Example docs publish personal information | open |
| BUG-012 | Medium | File changes made through shell commands are not seen | open |
| BUG-013 | Minor | Progress refresh needs a Bash permission on every tick | open |
| BUG-014 | Medium | `orchestrator` ignores the tricklord marker | fixed (v0.3.1) |
| BUG-015 | Minor | README does not document `dedup-merge` and `orchestrator` | fixed (v0.3.1) |
| BUG-016 | Minor | `dedup-merge` is written for one specific project | fixed (v0.3.1) |
| BUG-017 | Minor | `orchestrator` description triggers on any vague request | open |

---

### BUG-001: Activates on any file named `PLAN.md` or `ROADMAP.md`

- **Severity:** serious · **Found:** 2026-09-27 · **Status:** fixed (v0.3.0)
- **Where:** `hooks/roadmap_hook.py`, `find()` and `start()`
- **What happens:** the hook matches on file names only. Once installed, the plugin runs in every project, so any repo with an unrelated `PLAN.md` gets *"draft plan waiting for the user's approval... Don't start building"*, and any repo with its own `ROADMAP.md` (common in open-source projects) gets the roadmap rules and tick reminders.
- **Repro:**
  ```bash
  mkdir -p /tmp/other && echo "# Migration plan" > /tmp/other/PLAN.md
  echo '{}' | CLAUDE_PROJECT_DIR=/tmp/other python3 hooks/roadmap_hook.py start
  # prints the "Don't start building" notice
  ```
- **Fix (v0.3.0):** the three templates start with `<!-- tricklord -->`, and `find()` in `hooks/roadmap_hook.py` only accepts files containing it. `/roadmap-sync` adds the line to older files. Covered by `test_start` (an unmarked `PLAN.md` produces no output). Verified live 2026-09-27 (`claude -p --plugin-dir src`, Claude Code 2.1.283, macOS): in a project with an unmarked `PLAN.md`, the tricklord SessionStart hook printed nothing.

### BUG-002: Never tested in a real Claude Code session

- **Severity:** serious · **Found:** 2026-09-27 · **Status:** open
- **Where:** whole plugin
- **What happens:** the hooks were verified live on 2026-09-27 on macOS (see BUG-001, BUG-003, BUG-004), including the `PostToolUse` payload. Skills invoked by short name (`/orchestrator`, `/dedup-merge`) were verified live the same day (`bob_sessions/plugin_tests/2026-09-27_tricklord_live_tests.md`). Still unproven:
  - live runs of `/layout-init`, `/roadmap-planner` and `/roadmap-sync`, including the skills finding `../../templates/` and `../../scripts/` relative to their base directory;
  - the `python3 ... || python ...` hook command on Windows.
- **Fix idea:** run `claude -p` with `--plugin-dir src` against a small sample project (one run per skill, plus one session with each hook), and test once on the Windows desktop.

### BUG-003: Session start loads too much context

- **Severity:** serious · **Found:** 2026-09-27 · **Status:** fixed (v0.3.0)
- **Where:** `hooks/roadmap_hook.py`, `start()`
- **What happens:** layout rules + roadmap rules + progress block + next actions + up to 6,000 characters of `LAYOUT.md` are injected in every session, even for a one-line question. With the example roadmap and a layout at the limit the hook printed **11,405 characters** (about 3k tokens). Claude Code likely truncates hook output past roughly 10,000 characters (exact limit not confirmed), so the last part (next actions) may be cut. `LAYOUT_BUDGET` only limits the layout, not the total.
- **Repro:** copy `research_docs/ROADMAP.md` and a 6,000-character `LAYOUT.md` into a folder, run the `start` hook on it, and count the output with `wc -c`.
- **Fix (v0.3.0):** one `BUDGET` of 8,000 characters for everything `start()` prints. Rules, the progress headline (not the table) and next actions always load; `LAYOUT.md` is included only if it still fits, otherwise a pointer. Same setup as the repro now prints **4,372 characters** (was 11,405); a 1,500-character layout still loads in full (5,863). Covered by `test_start`. Verified live 2026-09-27 (`claude -p --plugin-dir src`, Claude Code 2.1.283, macOS): with the example roadmap and an 8,437-character layout, the session received 4,291 characters: both rule sets, the progress headline, all next actions, and a pointer instead of the layout.

### BUG-004: Stop reminder is noisy and misses committed work

- **Severity:** medium · **Found:** 2026-09-27 · **Status:** fixed (v0.3.0)
- **Where:** `hooks/roadmap_hook.py`, `stop()`
- **What happens:**
  - It fires on any uncommitted change: docs, config, generated files, or a tree that was already dirty when the session started (the first reply of the session triggers it, even a pure question). Each reminder costs an extra Claude reply.
  - It misses the case it exists for: code committed without ticking the roadmap leaves a clean tree, so nothing fires.
  - It runs `git status --untracked-files=all` and `git diff HEAD` after every reply, which is slow in repos with large untracked data folders.
- **Fix (v0.3.0):** a new `PostToolUse` hook on `Edit|Write|MultiEdit|NotebookEdit` records each edited path in a per-session temp file; `stop()` reads and clears it. No edits this turn means no reminder; edits without a `ROADMAP.md` edit trigger the roadmap reminder (including code committed within the turn); new untracked files without a `LAYOUT.md` edit trigger the layout reminder. The fingerprint file and the `git status` / `git diff HEAD` calls are gone. Edits outside the project are ignored. Covered by `test_stop`. Remaining gap: BUG-012. Verified live 2026-09-27 (`claude -p --plugin-dir src`, Claude Code 2.1.283, macOS): the edit hook receives `session_id` and `tool_input.file_path` as expected; a question on a dirty tree ended quietly; creating `src/util.py` (roadmap already ticked by Claude) fired only the layout reminder, which Claude acted on; editing a tracked file fired only the roadmap reminder, answered in one line; the follow-up Stop never looped and the edit log was removed.

### BUG-005: `LAYOUT.md` drifts from the code

- **Severity:** medium · **Found:** 2026-09-27 · **Status:** open
- **Where:** `hooks/roadmap_hook.py` `stop()`, `skills/roadmap-sync/SKILL.md`
- **What happens:** the layout reminder only notices new files created with Edit/Write (since v0.3.0; deletes and renames are not seen, see BUG-012). A new database column or a new function inside an existing file does not trigger it. Nothing checks that the paths in `LAYOUT.md` still exist, and `/roadmap-sync` ignores `LAYOUT.md`.
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

### BUG-012: File changes made through shell commands are not seen

- **Severity:** medium · **Found:** 2026-09-27 · **Status:** open
- **Where:** `hooks/hooks.json` (`PostToolUse` matcher), `hooks/roadmap_hook.py` `edit()` / `stop()`
- **What happens:** since the BUG-004 fix, reminders are based on the paths recorded from Edit/Write tools. Files changed through Bash (`sed -i`, `cat > file`, `mv`, `rm`, `git mv`, code generators) are not recorded, so a turn that only uses shell commands gets no roadmap or layout reminder, and deletes or renames never trigger the layout reminder. Claude uses Bash for edits often, especially in auto mode.
- **Fix idea:** also match `Bash` in `PostToolUse` and, for those calls, record the files `git status --porcelain` reports as changed since the previous call (store the last status per session), so shell-made changes, deletes and renames count as edits.

### BUG-013: Progress refresh needs a Bash permission on every tick

- **Severity:** minor · **Found:** 2026-09-27 (live test) · **Status:** open
- **Where:** `rules/roadmap.md` rule 3, the stop reminder, `scripts/roadmap_progress.py`
- **What happens:** Claude refreshes the progress block by running the script through Bash with absolute paths. Unless the user has allowed that command, every tick asks for permission; in the live test (`acceptEdits`) the call was blocked, so Claude ticked the item and logged it but the progress block stayed at 0%.
- **Fix idea:** let the stop hook run the progress script itself whenever `ROADMAP.md` was edited this turn (it already knows from the edit log), and drop the manual refresh step from the rules.

### BUG-014: `orchestrator` ignores the tricklord marker

- **Severity:** medium · **Found:** 2026-09-27 · **Status:** fixed (v0.3.1)
- **Where:** `skills/orchestrator/SKILL.md`, "State to check"
- **What happens:** the skill decided project state with "one `ls`, no reading", so any `PLAN.md` or `ROADMAP.md` counted as tricklord's, bringing BUG-001 back at the skill level: a repo's own roadmap would be routed to `roadmap-sync`, an unrelated plan to "approve this plan".
- **Fix (v0.3.1):** a file counts only if its first line is `<!-- tricklord -->` (`head -n 1`); otherwise it is treated as absent and never edited. A `ROADMAP.md` with progress markers but no tricklord marker is recognised as a pre-marker roadmap and gets `roadmap-sync` offered. Verified live (tests S1 to S3 in `bob_sessions/plugin_tests/2026-09-27_tricklord_live_tests.md`).

### BUG-015: README does not document `dedup-merge` and `orchestrator`

- **Severity:** minor · **Found:** 2026-09-27 · **Status:** fixed (v0.3.1)
- **Where:** `README.md`, Commands and Layout
- **What happens:** the two skills added in PR #2 were missing from the command list and the file tree.
- **Fix (v0.3.1):** both are listed in Commands and in the Layout tree.

### BUG-016: `dedup-merge` is written for one specific project

- **Severity:** minor · **Found:** 2026-09-27 · **Status:** fixed (v0.3.1)
- **Where:** `skills/dedup-merge/SKILL.md`
- **What happens:** examples and rules came from one web dashboard (`teachers/` vs `teachers/ta/`, a `"teacher" | "ta"` prop, `loadView`, `noFuture`, server actions, pages opened in a browser), the report step hard-coded `-- src`, and groups under ~100 shared lines were always left alone, which skips most duplicated functions outside page components.
- **Fix (v0.3.1):** generic examples; use an installed duplicate detector (`jscpd`, PMD CPD, pylint `duplicate-code`) when there is one; threshold lowered to ~20 shared lines; generated, vendored and intentionally separate code left alone; entry points kept as thin wrappers when something depends on them; the report diff scoped to the merged files; step 4 also updates the Logic list in `LAYOUT.md` (missed in the live test). Verified live (test S4): 76 → 58 lines, byte-identical output, tests passing.

### BUG-017: `orchestrator` description triggers on any vague request

- **Severity:** minor · **Found:** 2026-09-27 · **Status:** open
- **Where:** `skills/orchestrator/SKILL.md`, `description`
- **What happens:** "Use when the request is vague" matches many ordinary requests, so Claude may load the skill when it isn't needed, costing context each time.
- **Fix idea:** narrow the trigger to project-level questions ("what should I do next", "where do I start", "which skill"), and leave vague coding requests alone.
