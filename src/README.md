# RoadmapFlow Source Engine (`src/`)

> Deterministic core engine, project scaffolder, and empirical benchmarks for **RoadmapFlow** (IBM Bob 2.0 Hackathon).
> Zero external dependencies, pure Python standard library (`3.10+`).

---

## 📁 Source Modules

```
src/
├── __init__.py           ← Package marker
├── roadmap.py            ← Deterministic Roadmap & Context Engine (CLI + domain logic)
├── benchmark.py          ← Empirical Token Measurement & 10-session projection engine
├── scaffold.py           ← Project Scaffolder & 3-Tier standard layout compliance auditor
├── test_tools.py         ← Unit tests for the engine logic
└── README.md             ← This documentation
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
# Run unit test suite
python3 -m unittest discover tests -v
# OR run directly
python3 src/test_tools.py -v
```

---

## 🤖 IBM Bob 2.0 Integration

| Module | Bob Feature Used | How Bob Uses It |
|---|---|---|
| `roadmap.py` | Document Understanding & Skills (`/roadmap-navigator`) | Extracts Tier 2 snapshots so Bob avoids 160k token context pollution |
| `scaffold.py` | Agent Mode & Project Initialization (`/project-roadmap`) | Generates standard project layout and rules for Bob sessions |
| `benchmark.py` | Agent Mode & Reporting | Verifies and validates empirical token savings achieved by Bob |
