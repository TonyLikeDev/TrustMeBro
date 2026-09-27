---
name: roadmap-benchmark
description: Run empirical token measurement and 10-session projection benchmark for RoadmapFlow context savings. Use when the user runs /roadmap-benchmark, asks to measure tokens, benchmark context efficiency, or check token savings in Bob.
---

# Roadmap Benchmark Runner

Executes the empirical token measurement engine and reports quantified context savings across single-session and 10-session developer workflows.

## Workflow

1. **Execute Benchmark Engine**:
   Run:
   ```bash
   python3 src/benchmark.py --json-out things/benchmark_results.json --report-out docs/BENCHMARK_REPORT.md
   ```

2. **Read Results**:
   Inspect `things/benchmark_results.json` to extract token statistics:
   - Baseline Context tokens
   - RoadmapFlow Active Context tokens
   - Tier 2 Snapshot tokens (≤200t)
   - Single-Session Savings %
   - 10-Session Cumulative Savings %

3. **Report to User**:
   Display high-density summary table showing >90% context reduction.
