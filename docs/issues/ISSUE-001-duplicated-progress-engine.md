# [ISSUE-001] Duplicated and Divergent Roadmap Progress Calculation Engines

- **Status**: OPEN
- **Severity**: HIGH (Architecture / Maintainability / Logic Conflict)
- **Component**: `src/` (Core Logic & Scripts)
- **Reporter**: tducn110
- **Signed-off-by**: `tducn110 <duc.nguyen240205@vnuk.edu.vn>`
- **Date**: 2026-09-27

---

## 1. Description & Symptom

There are currently **two competing and divergent implementations** of the roadmap progress calculation and ASCII progress bar rendering inside `src/`:
1. `src/scripts/roadmap_progress.py` (introduced in Tony's commit `3b92012`).
2. `src/roadmap.py` (introduced in Duc's commit `5c818cf` and bridged via root `scripts/roadmap_progress.py`).

Both scripts perform the exact same domain operation (reading checkboxes, calculating progress fractions, and generating ASCII progress bars), but they use different parsing logic, different formatting rules, and completely disjoint code paths.

---

## 2. Source Evidence

### Evidence A — `src/scripts/roadmap_progress.py` (Lines 17–56)
- Implements ad-hoc regex parsing: `re.match(r"\s*[-*] \[([ xX~])\]", line)`
- Custom ASCII bar generator: `bar(frac)` using round arithmetic
- Only checks headings matching `## <Phase>: <title>`
- Does not validate exit criteria or calculate token budgets

### Evidence B — `src/roadmap.py` (Lines 40–180)
- Implements comprehensive AST-style parser: `parse_roadmap()`
- Calculates progress weights (`[~]` = 0.5, `[x]` = 1.0)
- Implements `render_ascii_bar(ratio, width=20)`
- Integrates binary exit criteria validation (`validate_roadmap()`)
- Integrates Tier 2 context snapshot extraction (`extract_tier2_snapshot()`)
- Updates files in-place with atomic verification (`update_progress_in_file()`)

### Evidence C — Root `scripts/roadmap_progress.py`
- Root `scripts/roadmap_progress.py` delegates directly to `src/roadmap.py`, while `src/hooks/roadmap_hook.py` delegates to `src/scripts/roadmap_progress.py`.

---

## 3. Root Cause

Lack of a single source of truth for deterministic roadmap calculations:
- `src/scripts/roadmap_progress.py` was introduced as a standalone script for the Claude Code plugin without reusing the existing `src/roadmap.py` engine.
- This directly violates the **Component Reuse** principle and creates split-brain state calculations across the repository.

---

## 4. Impact

- **Risk of state drift**: If a developer or hook runs `src/scripts/roadmap_progress.py`, it may generate a table layout incompatible with `src/roadmap.py` or fail on non-standard phase headings.
- **Maintenance overhead**: Any change to progress weighting or formatting requires patching two separate files.

---

## 5. Proposed Resolution

1. Make `src/roadmap.py` the authoritative domain engine for all progress and snapshot calculations.
2. Refactor `src/scripts/roadmap_progress.py` to be a lightweight CLI wrapper that imports and calls `update_progress_in_file()` from `src/roadmap.py`.
3. Unify test coverage under `tests/test_tools.py` and `src/tests/test_plugin.py`.

---
*Signed-off-by: tducn110*
