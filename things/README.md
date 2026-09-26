# RoadmapFlow Tooling Engine (`things/`)

> Deterministic tools and empirical benchmarks for **RoadmapFlow** (IBM Bob 2.0 Hackathon).
> Built under **Ponytail** engineering principles: zero external dependencies, pure Python standard library, maximum density.

---

## 🛠️ Tools Included

### 1. `roadmap.py` — Deterministic Roadmap Engine
Handles all state operations without polluting LLM reasoning:
- **`progress`**: Computes completion percentages from checkboxes (`[x]`, `[~]`, `[ ]`) and updates the ASCII progress bar and summary table in `ROADMAP.md` in-place.
- **`snapshot`**: Implements the core logic of `/roadmap-navigator`. Extracts open tasks of the active phase into `.bob/context/current-phase.md` adhering strictly to the **≤ 200 token budget**.
- **`validate`**: Validates binary pass/fail exit criteria and phase limits.

```bash
# Update progress table
python3 things/roadmap.py progress teamsource/ROADMAP.md

# Generate Tier 2 context snapshot
python3 things/roadmap.py snapshot teamsource/ROADMAP.md --output .bob/context/current-phase.md

# Validate roadmap integrity
python3 things/roadmap.py validate teamsource/ROADMAP.md
```

---

### 2. `benchmark.py` — Empirical Token Measurement
Measures real files in `teamsource/` and `.bob/context/`, simulating 10 multi-session developer workflows.
- Generates `things/benchmark_results.json`
- Generates `docs/BENCHMARK_REPORT.md`

```bash
python3 things/benchmark.py
```

**Measured Findings:**
- **Baseline Context (Research Plan + Roadmap)**: **9,124 tokens**
- **RoadmapFlow Active Context (Tier 1 + Tier 2)**: **797 tokens**
- **Tier 2 Context Snapshot**: **156 tokens** (under ≤200 token budget)
- **Single-Session Token Reduction**: **91.26%**
- **10-Session Cumulative Savings**: **93.3%** (**110,270 tokens saved**)

---

### 3. `scaffold.py` — Project Scaffolder & Standard Layout Auditor
Generates and audits standard 3-tier folder structures for any project using RoadmapFlow:
- **`init`**: Scaffolds `src/`, `tests/`, `docs/`, `scripts/`, `.bob/context/`, `PLAN.md`, `ROADMAP.md`, `.gitignore`, `.bobignore`, and initial Tier 2 snapshot.
- **`audit`**: Validates whether a repository complies with all RoadmapFlow standards (binary exit criteria, Tier 1/2 token budgets, gitignore rules).

```bash
# Scaffold a new project
python3 things/scaffold.py init my-app --name "MyApp" --stack "Node.js" --phases 4

# Audit compliance of a repository
python3 things/scaffold.py audit .
```

---

### 4. `test_tools.py` — Automated Verification Harness
Full unit test coverage using Python standard library `unittest`.

```bash
python3 -m unittest things/test_tools.py -v
```

---

## 🔗 Bridge Integration

- `scripts/roadmap_progress.py` delegates directly to `things/roadmap.py progress`, satisfying the reference in `teamsource/ROADMAP.md:31`.
