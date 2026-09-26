# [ISSUE-003] Architectural Drift Between Claude Code Lifecycle Hooks and Bob 2.0 3-Tier Context Model

- **Status**: RESOLVED
- **Resolution**: Fixed in `src/hooks/roadmap_hook.py` (added `teamsource/` to DIRS, auto-loads Tier 2 snapshot, verified by `src/tests/test_plugin.py`)
- **Severity**: HIGH (Workflow Integration / Context Window Pollution)
- **Component**: `src/hooks/` & `.bob/context/`
- **Reporter**: tducn110
- **Signed-off-by**: `tducn110 <duc.nguyen240205@vnuk.edu.vn>`
- **Date**: 2026-09-27

---

## 1. Description & Symptom

There is an integration drift between the Claude Code lifecycle hooks (`src/hooks/roadmap_hook.py`) and IBM Bob 2.0's **3-Tier Context Loading Model**:
1. When `SessionStart` fires, `src/hooks/roadmap_hook.py` reads and dumps the rules and the progress block into the session, but it **completely bypasses Tier 2 snapshotting** (`.bob/context/current-phase.md`), risking context window bloat if the roadmap grows large.
2. The hook searches for `ROADMAP.md` only under hardcoded paths `["", "docs", "research_docs"]`, but fails to discover demo project files under `teamsource/ROADMAP.md`.
3. When `Stop` fires after code modification, it asks the agent to run the un-reused script `src/scripts/roadmap_progress.py`, rather than integrating with the deterministic engine (`src/roadmap.py`) or updating Tier 2 snapshots.

---

## 2. Source Evidence

### Evidence A — `src/hooks/roadmap_hook.py` (Lines 16–31):
```python
PLUGIN = Path(__file__).resolve().parent.parent
DIRS = ["", "docs", "research_docs"]
def find(project, *names):
    for d in DIRS:
        for name in names:
            if (project / d / name).is_file():
                return project / d / name
    return None
```
- Missing search paths for `teamsource/` or custom paths configured in project settings.

### Evidence B — `src/hooks/roadmap_hook.py` (Lines 48–75):
- The `start()` function injects `rules.md` and raw sections of `ROADMAP.md` directly into the session prompt.
- It does not check if `.bob/context/architecture.md` (Tier 1) or `.bob/context/current-phase.md` (Tier 2) exists.
- In contrast, `.bob/skills/roadmap-navigator/SKILL.md` strictly enforces that `ROADMAP.md` must NEVER be loaded into the main context (only the ≤200 token snapshot in `current-phase.md` may be loaded).

---

## 3. Root Cause

- The Claude Code plugin was developed in isolation with a simple hook strategy (injecting the roadmap head and next actions).
- IBM Bob 2.0 was developed with a strict 3-tier token budget architecture to prevent the 160k token bloat observed in Session 001.
- These two philosophies have not yet been unified into a single coherent lifecycle contract.

---

## 4. Impact

- Running the plugin on large production projects with 10+ phases will result in continuous token waste at every session start, undermining the core value proposition of RoadmapFlow (>90% token reduction).
- Hooks will fail to detect roadmaps located in `teamsource/` during live hackathon demos.

---

## 5. Proposed Resolution

1. Update `src/hooks/roadmap_hook.py`:
   - Support `teamsource/` in search directory list `DIRS`.
   - On `SessionStart`: Check if `.bob/context/current-phase.md` exists. If present, load the ≤200 token Tier 2 snapshot instead of raw roadmap sections.
   - On `Stop`: When prompting for roadmap updates, trigger `src/roadmap.py` to update both `ROADMAP.md` and `.bob/context/current-phase.md` in one atomic step.
2. Ensure full dual-compatibility between Claude Code plugin hooks and IBM Bob 2.0 rules.

---
*Signed-off-by: tducn110*
