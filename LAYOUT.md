# Project layout

Map of the code: where things are, what they do, how they connect. **Rule: when a change adds, moves or removes a folder, component, table or piece of logic, update this file in the same commit.** One line per entry; point to files, don't paste code.

Last updated: 2026-09-27.

## Overview

RoadmapFlow is a deterministic plan-first context engine and Claude/Gemini plugin. It reduces LLM context window token usage by >90% by enforcing a 3-tier layout (`PLAN.md`, `ROADMAP.md`, `.bob/context/current-phase.md`) and providing automated state calculation, validation, and benchmarking scripts.

## Folder tree

```
/home/pro/hackathon/
├── src/                         Core Python engine modules, skills, rules, templates, and hooks
│   ├── roadmap.py               Deterministic Roadmap Engine (progress math, Tier 2 snapshot extraction, validation)
│   ├── scaffold.py              Project Scaffolder & 3-Tier layout compliance auditor
│   ├── benchmark.py            Empirical Token Measurement & 10-session projection engine
│   ├── test_tools.py           Unit tests for engine logic
│   ├── hooks/                  Plugin hooks for session start/stop lifecycle
│   │   ├── hooks.json          Hook registrations
│   │   └── roadmap_hook.py     SessionStart context injector and Stop update reminder
│   ├── rules/                  System prompt rules loaded into LLM sessions
│   │   ├── layout.md           Rules active when LAYOUT.md exists
│   │   └── roadmap.md          Rules active when ROADMAP.md exists
│   ├── templates/              Markdown document templates
│   │   ├── LAYOUT.md           System architecture layout template
│   │   ├── PLAN.md             Static master plan template
│   │   └── ROADMAP.md          Live status board template
│   ├── scripts/                Progress recalculation & session extraction helpers
│   │   ├── roadmap_progress.py Recalculates progress block from checkboxes
│   │   └── export_bob_sessions.py Extracts all sessions directly from ~/.bob/db/bob.db
│   └── skills/                 Skill definitions for AI agents
├── big_project_report/          Testing reports and benchmark dossiers (baseline vs RoadmapFlow)
├── bob_sessions/                Empirical IBM Bob session transcripts, raw JSON database export, and testbed artifacts
│   ├── FULL_REPORT.md           Full engineering stabilization report on Tracker_yourMoney
│   ├── all_bob_sessions.json    Complete raw session export from Bob SQLite database
│   ├── session_logs/            12 structured session transcripts and SUMMARY.md
│   └── testbed_tracker_yourmoney/ Supporting testbed evaluation artifacts
├── envidence/                   Visual verification screenshots and execution evidence (aliased as evidence/)
├── planning/                    Hackathon strategy, guidelines, problem statement, and checklist docs
├── docs/                        Benchmark reports and hackathon guide summaries
│   ├── BENCHMARK_REPORT.md     Measured token reduction benchmark output
│   └── HACKATHON_GUIDE_SUMMARY.md Hackathon strategy summary
├── teamsource/                  Reference dataset (sample research plan & roadmap for benchmarking)
│   ├── RESEARCH_PLAN.md        Reference master plan
│   └── ROADMAP.md              Reference status board
├── slides/                      Presentation decks and hackathon pitch slides
├── scripts/                     Shell and python utility scripts for task ticking and phase verification
├── tests/                       Unit test suite for plugin and engine verification
└── things/                      Output directory for generated JSON benchmarks
```

## Components

| Component | Path | Does | Depends on |
| :--- | :--- | :--- | :--- |
| Roadmap Engine | `src/roadmap.py` | State calculation, snapshot extraction, roadmap validation | stdlib (`argparse`, `re`, `pathlib`) |
| Scaffolder & Auditor | `src/scaffold.py` | 3-Tier project structure generator and layout auditor | `src/roadmap.py` |
| Token Benchmark Engine | `src/benchmark.py` | Simulates 10 developer sessions and measures token savings | `src/roadmap.py` |
| Lifecycle Hooks | `src/hooks/roadmap_hook.py` | Session start context injection and stop reminder | `src/roadmap.py` |
| Progress Calculator | `src/scripts/roadmap_progress.py` | Recalculates checkbox progress bars in-place | `src/roadmap.py` |
| Bob Session Extractor | `src/scripts/export_bob_sessions.py` | Parses and extracts raw session logs, token spend, and messages from Bob SQLite database | `sqlite3`, stdlib |

**Flows**
- Session Start Flow: `roadmap_hook.py` → reads `LAYOUT.md` & `.bob/context/current-phase.md` → injects minimal context to LLM session.
- Progress Sync Flow: Developer ticks `[x]` → `roadmap_progress.py` / `roadmap.py progress` → updates progress bar & Change Log in `ROADMAP.md`.
- Benchmark Flow: `benchmark.py` → reads `teamsource/ROADMAP.md` → measures Tier 1/2 vs Baseline tokens → outputs `docs/BENCHMARK_REPORT.md`.
- Evaluation Flow: `export_bob_sessions.py` → queries `~/.bob/db/bob.db` → extracts Markdown transcripts to `bob_sessions/session_logs/` and JSON to `bob_sessions/all_bob_sessions.json`.

## Database

- **Core Engine**: Zero runtime database dependencies (pure file-based Markdown and deterministic Python CLI).
- **Evaluation & Analytics**: Integrates with IBM Bob's internal SQLite database (`~/.bob/db/bob.db`) for empirical benchmarking, auditing conversation turns, API costs, error cycles, and token usage.

## Logic

- **Progress Math & Bar Rendering**: Parses checkboxes (`[x]`, `[~]`, `[ ]`) and computes phase progress → `src/roadmap.py:calculate_progress`
- **Tier 2 Snapshot Extraction**: Extracts active phase open tasks into budget-constrained markdown ($\le 200$ tokens) → `src/roadmap.py:extract_phase_snapshot`
- **Roadmap Integrity Validation**: Checks phase task limits and verifies binary exit criteria → `src/roadmap.py:validate_roadmap`
- **3-Tier Compliance Audit**: Audits structure, Tier 1 token size ($\le 650$ tokens), and ignore files → `src/scaffold.py:audit_repository`
- **Empirical Token Benchmarking**: Simulates 10 sessions and computes single/cumulative token savings → `src/benchmark.py:run_benchmark`
