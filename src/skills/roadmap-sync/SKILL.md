---
name: roadmap-sync
description: Check ROADMAP.md against the actual code and git history and fix the drift, such as ticked items whose evidence is gone, finished work nobody ticked, and stale next actions or progress. Use when the user runs /roadmap-sync, comes back after a break or from another machine, or asks whether the roadmap is up to date.
---

# Roadmap sync

Progress script, relative to this skill's base directory: `../../scripts/roadmap_progress.py`.

1. Read the roadmap and the plan, then `git log` since the last Change log date, plus uncommitted changes.
2. Check every `[x]` and `[~]`: does the evidence it names still exist? Run the test suite once if it is quick; a failing test turns its `[x]` back into `[~]`.
3. Find finished work nobody ticked: commits or files that complete an open item.
4. Check the format the plugin needs: a `<!-- trustmebro -->` first line in the roadmap, plan and layout (without it the hooks ignore the file; older files lack it), the `<!-- progress:start -->` / `<!-- progress:end -->` markers, and one `## <Phase>: <title>` heading per phase in the plan. Split merged headings such as "## Weeks 4 to 10" into one heading per phase.
5. Report the drift as a short list (item, what you found, proposed change). After the user confirms, apply it, add one Change log line (`- YYYY-MM-DD: synced with the code: ...`), update Next actions and "Last updated", and rerun the progress script.

Never change the plan here. Plan changes go through the deviation rule: ask the user, then log a dated line in the plan's Deviations section.
