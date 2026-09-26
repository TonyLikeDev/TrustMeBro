# [ISSUE-002] Missing Tri-Layout (DB vs Logic vs UI) Component Reuse Structure in `src/`

- **Status**: OPEN
- **Severity**: MEDIUM (Architecture / Component Coupling / Code Duplication)
- **Component**: `src/` (Folder Architecture & Module Boundaries)
- **Reporter**: tducn110
- **Signed-off-by**: `tducn110 <duc.nguyen240205@vnuk.edu.vn>`
- **Date**: 2026-09-27

---

## 1. Description & Symptom

Currently, the code inside `src/` is arranged in a flat, monolithic module structure. Core engine files (`roadmap.py`, `benchmark.py`, `scaffold.py`, `test_tools.py`) mix storage parsing, domain logic calculations, and UI presentation strings in single files.

There is no structural separation of reusable components into the 3 fundamental architectural layouts:
1. **DB Layout**: State schemas, markdown parsers, persistent storage contracts.
2. **Logic Layout**: Pure deterministic functions, token estimation algorithms, compliance validation.
3. **UI Layout**: ASCII graphics generators, markdown tables, prompt banners, and interactive presentation components.

---

## 2. Source Evidence

### Evidence A — `src/roadmap.py` mixes all 3 concerns in one file:
- **DB/Storage concern**: `parse_roadmap()` (reading raw disk lines and building state AST), `update_progress_in_file()` (mutating markdown file in-place).
- **Domain Logic concern**: `calculate_progress()` (weight arithmetic, ratios), `validate_roadmap()` (exit criteria rule checking), `estimate_tokens()` (token heuristics).
- **UI/Presentation concern**: `render_ascii_bar()` (drawing `[████░░░░]`), table row string formatting.

### Evidence B — `src/` folder root:
- Contains flat scripts and plugin folders without dedicated reusable module packages:
  `src/roadmap.py`, `src/benchmark.py`, `src/scaffold.py` are coupled directly with filesystem paths.

---

## 3. Root Cause

- The initial code was authored as self-contained standalone scripts ("Ponytail" dense style) without anticipating the need for modular component reuse across both IBM Bob 2.0 skills and Claude Code plugins.
- Without explicit `src/db/`, `src/logic/`, and `src/ui/` boundaries, agents cannot easily locate reusable components and end up duplicating helper logic.

---

## 4. Impact

- **Impedes Component Reuse**: An agent cannot import just the UI bar renderer without pulling in disk operations.
- **Cascading Failures**: Modifying visual layout string templates risks introducing regression bugs into core calculation logic.

---

## 5. Proposed Resolution

1. Establish explicit sub-packages or clear namespaces:
   - `src/db/` or `roadmapflow.db`: State models, AST parsing, file IO.
   - `src/logic/` or `roadmapflow.logic`: Pure functions, token calculations, rule validators.
   - `src/ui/` or `roadmapflow.ui`: ASCII renderers, markdown formatters, terminal presentation.
2. Keep public top-level imports backward-compatible (`from roadmap import calculate_progress, render_ascii_bar`).
3. Enforce the Tri-Layout Tracing rule in `dev-workflow` and `execution-discipline.md`.

---
*Signed-off-by: tducn110*
