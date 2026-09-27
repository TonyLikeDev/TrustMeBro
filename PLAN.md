# Plan: RoadmapFlow (IBM Bob 2.0 Hackathon)

This master plan synthesizes the requirements from `planning/PROBLEM_STATEMENT.md`, `BOB_USAGE_PLAN.md`, `JUDGING_STRATEGY.md`, and `SUBMISSION_CHECKLIST.md`. It defines the 4-phase engineering schedule for **RoadmapFlow**, a deterministic plan-first context engine and custom skill system for IBM Bob 2.0.

---

## 0. Decisions Log

| Topic | Options | Decision | Why |
| :--- | :--- | :--- | :--- |
| Core Architecture | MCP Server vs Native Python Stdlib | Native Python Stdlib (`3.10+`) | Zero dependencies, instant startup, eliminates MCP setup overhead and latency |
| Context Management | Full History vs 3-Tier Context Model | 3-Tier Context Model | Reduces LLM context token usage by >90% (Tier 1: ≤650 tok, Tier 2: ≤200 tok, Tier 3: isolated) |
| Progress Calculation | Manual vs Deterministic Engine | Deterministic Python Engine | Prevents math errors, renders ASCII progress bars, and automatically parses markdown checkboxes |
| Document Ingestion | Raw context vs Synthesized Plan | Ingest into `PLAN.md` & `LAYOUT.md` | Keeps old/init docs isolated in Tier 3 to protect context window |

---

## 1. Objectives

**General objective.** Build and ship RoadmapFlow, a 3-tier deterministic plan-first context engine and skill system for IBM Bob 2.0 that cuts context token costs by >90%.

**Specific objectives.**
1. Implement deterministic CLI engine in `src/roadmap.py` for state calculation, Tier 2 snapshot extraction, and validation.
2. Build 3-tier project scaffolder and compliance auditor in `src/scaffold.py`.
3. Create empirical token benchmark engine in `src/benchmark.py` proving 10-session token savings.
4. Package plugin hooks (`roadmap_hook.py`) and custom skills (`layout-init`, `roadmap-planner`, `roadmap-scaffold`, `roadmap-navigator`, `roadmap-sync`, `roadmap-validate`, `roadmap-audit`, `roadmap-benchmark`).

**Deliverables.**
- Production-ready Python standard library codebase (`src/`).
- Benchmark report (`docs/BENCHMARK_REPORT.md` & `things/benchmark_results.json`).
- Full unit test suite (`src/test_tools.py`, `src/tests/test_plugin.py`).
- 500-word submission statement & hackathon demo materials.

---

## 2. Technical Design

- **Architecture**: Modular monolith with zero third-party dependencies.
- **Context Boundaries**:
  - `Tier 1`: `.bob/context/architecture.md` (≤650 tok) & `LAYOUT.md` (Code map).
  - `Tier 2`: `.bob/context/current-phase.md` (≤200 tok active open tasks snapshot).
  - `Tier 3`: `PLAN.md`, `ROADMAP.md`, `planning/` (Isolated outside LLM main context window).
- **Core Engine Modules**:
  - `src/roadmap.py`: Markdown checkbox parser, progress math, snapshot extractor, validator.
  - `src/scaffold.py`: Directory tree generator and 3-Tier layout compliance auditor.
  - `src/benchmark.py`: 10-session token measurement simulation.

---

## 3. Metrics & Research Framing

| Metric | Measures | Target / Baseline | Tool |
| :--- | :--- | :--- | :--- |
| Single-session token savings | Tier 1+2 context vs baseline full history | > 90% reduction | `src/benchmark.py` |
| Tier 2 Snapshot budget | Active phase open tasks token count | ≤ 200 tokens | `src/roadmap.py` |
| Tier 1 Architecture budget | Architecture snapshot token count | ≤ 650 tokens | `src/scaffold.py audit` |
| Cumulative 10-session savings | Preserved tokens across 10 developer sessions | > 100,000 tokens saved | `src/benchmark.py` |

---

## 4. Schedule (4 Phases)

### Phase 1: Foundation & Deterministic Engine
**Build**
- [x] Create core skeleton and CLI entry points in `src/roadmap.py`, `src/scaffold.py`, `src/benchmark.py`
- [x] Implement layout mapping in `LAYOUT.md` via `layout-init` skill
- [x] Implement 3-Tier directory scaffolding (`.bob/context`, `src/db`, `src/logic`, `src/ui`) in `src/scaffold.py`

**Measure**
- [x] Unit tests in `src/test_tools.py` for token estimation, progress math, snapshot budget, and validation

**Write**
- [x] Architecture snapshot in `.bob/context/architecture.md` (≤650 tokens)

**Exit criteria**: `src/test_tools.py` unit tests pass 100% with zero regressions.

---

### Phase 2: IBM Bob Skills & Hooks Integration
**Build**
- [ ] Implement Claude/Gemini/Bob custom skills in `src/skills/`
- [ ] Implement SessionStart and Stop plugin hooks in `src/hooks/roadmap_hook.py`
- [ ] Wire `/roadmap-navigator` to auto-refresh `.bob/context/current-phase.md`

**Measure**
- [ ] Unit tests for plugin hook lifecycle in `src/tests/test_plugin.py`

**Write**
- [ ] Skill instructions for all 9 RoadmapFlow skills

**Exit criteria**: Plugin tests pass and `/roadmap-navigator` updates Tier 2 snapshot under ≤200 token budget.

---

### Phase 3: Empirical Token Benchmarking & Reporting
**Build**
- [ ] Execute 10-session token simulation via `src/benchmark.py`
- [ ] Export raw metrics to `things/benchmark_results.json`

**Measure**
- [ ] Verify single-session savings >90% and 10-session cumulative savings >100,000 tokens

**Write**
- [ ] Benchmark report in `docs/BENCHMARK_REPORT.md`

**Exit criteria**: `docs/BENCHMARK_REPORT.md` generated with verified empirical token savings.

---

### Phase 4: Hackathon Submission & Final Polish
**Build**
- [ ] Audit repository compliance via `python3 src/scaffold.py audit .`
- [ ] Verify submission checklist in `planning/SUBMISSION_CHECKLIST.md`

**Measure**
- [ ] Full test suite execution across all modules

**Write**
- [ ] Final 500-word problem statement and Bob 2.0 usage report

**Exit criteria**: `scaffold.py audit` reports 100% COMPLIANT and all deliverables ready.

---

## 5. Risks and Fallbacks

| Risk | Signal | Fallback |
| :--- | :--- | :--- |
| Context snapshot bloat | Tier 2 `current-phase.md` > 200 tokens | Truncate completed items, keep open tasks only |
| Phase scope creep | Phase has > 7 open tasks | Subdivide phase into smaller milestones |
| Git drift | Code changes committed without ticking `ROADMAP.md` | Run `python3 src/roadmap.py progress` via `/roadmap-sync` |

---

## 6. Deviations

- 2026-09-27: Initial master plan created and approved for RoadmapFlow hackathon development.
