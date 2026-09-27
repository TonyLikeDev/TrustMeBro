# tricklord / RoadmapFlow

> A Claude Code plugin & deterministic engine for plan-first projects: map the code in `LAYOUT.md`, plan the work in `PLAN.md`, track it in `ROADMAP.md`, and have Claude keep them current as work lands.
> Includes deterministic core engine, project scaffolder, and empirical benchmarks for **RoadmapFlow** (IBM Bob 2.0 Hackathon).
> Zero external dependencies, pure Python standard library (`3.10+`).

---

## Commands

- `/roadmap-planner`: an idea or source documents become `PLAN.md`. It stops for your review; once you approve, it creates `ROADMAP.md` and does the first action.
- `/layout-init`: an existing codebase becomes `LAYOUT.md`: folder tree, components, database schema, and business logic mapping.
- `/roadmap-navigator`: narrows context to the active phase by extracting a minimal Tier 2 snapshot (`≤ 200 tokens`).
- `/roadmap-sync`: checks the roadmap against code and git history and fixes the drift.
- `/roadmap-benchmark`: runs empirical token measurement and calculates context savings (>90%).
- `/roadmap-validate`: validates exit criteria and phase integrity rules.
- `/roadmap-audit`: audits repository compliance against RoadmapFlow 3-tier loading standards.
- `/roadmap-scaffold`: scaffolds a standard 3-tier project structure with DB, Logic, and UI layout folders.

(Also reachable as `/tricklord:roadmap-planner` and so on.)

**Adding something** to a project with `LAYOUT.md`: just ask. Claude finds where it fits in the layout, then sizes it. A small addition becomes a new phase in `ROADMAP.md` and work starts; a big one (new component, database change, several days) is planned first and waits for your approval.

## What happens automatically

- **Session start, `LAYOUT.md` present**: Claude gets the layout rules from `rules/layout.md` and the layout itself (or a pointer to it if it's over 6,000 characters).
- **Session start, `ROADMAP.md` present** (project root, `docs/` or `research_docs/`): Claude gets the roadmap rules from `rules/roadmap.md`, the progress block and the next actions, and reads the roadmap before the code.
- **Session start, plan but no roadmap**: Claude is told the plan is an unapproved draft and not to start building.
- **End of a reply that changed code but not the roadmap**, or added / removed / renamed files but not the layout: Claude is asked once to update them.

Edit `rules/` to change how Claude maintains the layout and roadmap, and `templates/` to change the document format.

---

## 📁 Layout

```
src/
├── .claude-plugin/
│   ├── plugin.json              plugin manifest (name, version, description)
│   └── marketplace.json         lets /plugin marketplace add install it
├── skills/
│   ├── roadmap-planner/SKILL.md /roadmap-planner: idea or documents → PLAN.md, approve → ROADMAP.md
│   ├── layout-init/SKILL.md     /layout-init: existing code → LAYOUT.md (tree, components, database, logic)
│   └── roadmap-sync/SKILL.md    /roadmap-sync: fix drift between roadmap and code
├── hooks/
│   ├── hooks.json               registers the SessionStart and Stop hooks
│   └── roadmap_hook.py          start: load layout + roadmap rules and state; stop: update reminder
├── rules/
│   ├── layout.md                loaded when LAYOUT.md exists: keep it current, how to add something
│   └── roadmap.md               loaded when ROADMAP.md exists: tick, log, progress, deviations
├── templates/
│   ├── LAYOUT.md                layout format: overview, folder tree, components, database, logic
│   ├── PLAN.md                  plan format: decisions, objectives, design, schedule, risks, deviations
│   └── ROADMAP.md               status board format: progress block, phases, next actions, change log
├── scripts/
│   └── roadmap_progress.py      regenerates the progress block from the checkboxes
├── tests/
│   └── test_plugin.py           checks the progress math and both hooks
├── BUG_LOGS.md                  known flaws, their status and fix ideas
├── research_docs/               example plan and roadmap from a real project
├── __init__.py                  package marker
├── roadmap.py                   Deterministic Roadmap & Context Engine (CLI + domain logic)
├── benchmark.py                 Empirical Token Measurement & 10-session projection engine
├── scaffold.py                  Project Scaffolder & 3-Tier standard layout compliance auditor
├── test_tools.py                Unit tests for the engine logic
└── README.md                    This documentation
```

---

## 🚀 Getting Started

### Prerequisites

```bash
# Claude Code
# git
# python >= 3.10 (as python3 or python)
```

### Installation

```bash
# Try it without installing
claude --plugin-dir /path/to/tricklord/src

# Install for good (run inside Claude Code)
/plugin marketplace add TonyLikeDev/tricklord      # or a local path: /path/to/tricklord
/plugin install tricklord@tricklord
```

---

## 🛠️ CLI & Module Usage

### 1. `roadmap.py` — Deterministic Roadmap Engine
Handles state calculation, Tier 2 context snapshot extraction, and compliance validation:

```bash
# Recalculate progress in-place from checkboxes (- [x], - [~], - [ ])
python3 src/roadmap.py progress teamsource/ROADMAP.md

# Extract active phase open tasks into minimal context snapshot (strictly ≤ 200 tokens)
python3 src/roadmap.py snapshot teamsource/ROADMAP.md --output .bob/context/current-phase.md

# Validate roadmap integrity and binary exit criteria
python3 src/roadmap.py validate teamsource/ROADMAP.md
```

### 2. `benchmark.py` — Empirical Token Measurement
Simulates and measures actual files in `teamsource/` and `.bob/context/` across 10 developer sessions:

```bash
python3 src/benchmark.py --json-out things/benchmark_results.json --report-out docs/BENCHMARK_REPORT.md
```

**Measured Results:**
- Baseline Full Context: **9,124 tokens**
- RoadmapFlow Tier 1+2 Context: **797 tokens** (**91.26% single-session reduction**)
- Tier 2 Snapshot alone: **156 tokens** (under ≤200 token budget)
- 10-Session Cumulative Savings: **93.3%** (**110,270 tokens preserved**)

### 3. `scaffold.py` — Project Scaffolder & Layout Auditor
Scaffolds standard 3-tier folder structures and audits repository compliance:

```bash
# Scaffold a new project with 3-tier context management
python3 src/scaffold.py init my-app --name "MyApp" --stack "Node.js" --phases 4

# Audit compliance of current repository
python3 src/scaffold.py audit .
```

---

## 🧪 Running Tests

```bash
# Run engine unit tests
python3 -m unittest discover tests -v
# OR run directly
python3 src/test_tools.py -v

# Run Claude Code plugin tests
python3 src/tests/test_plugin.py
```

---

## 🤖 IBM Bob 2.0 Integration

| Module | Bob Feature Used | How Bob Uses It |
|---|---|---|
| `roadmap.py` | Document Understanding & Skills (`/roadmap-navigator`) | Extracts Tier 2 snapshots so Bob avoids 160k token context pollution |
| `scaffold.py` | Agent Mode & Project Initialization (`/project-roadmap`) | Generates standard project layout and rules for Bob sessions |
| `benchmark.py` | Agent Mode & Reporting | Verifies and validates empirical token savings achieved by Bob |

---

## ⚠️ Credential Safety

- **Never hardcode API keys, passwords, or secrets** in any file in this directory
- Use environment variables: `process.env.API_KEY` or `os.environ['API_KEY']`
- All secrets belong in `.env` (which is in `.gitignore` and `.bobignore`)
- IBM Cloud credential exposure = account suspension

### Required `.gitignore` entries:

```
.env
.env.*
credentials.json
ibm-credentials.env
*.key
*.pem
```

### Required `.bobignore` entries:

```
.env
.env.*
credentials.json
ibm-credentials.env
```
