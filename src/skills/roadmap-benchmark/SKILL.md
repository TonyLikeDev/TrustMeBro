---
name: roadmap-benchmark
description: Run empirical token measurement and 10-session projection benchmark for RoadmapFlow context savings. Use when the user runs /roadmap-benchmark, asks to measure tokens, benchmark context efficiency, or check token savings.
---

# Roadmap Benchmark Runner

Executes the empirical token measurement engine and reports quantified context savings across single-session and 10-session developer workflows.

## Workflow

1. **Execute Benchmark Engine**:
   Run the deterministic benchmark script:
   ```bash
   python3 src/benchmark.py --json-out things/benchmark_results.json --report-out docs/BENCHMARK_REPORT.md
   ```

2. **Read Results**:
   Inspect `things/benchmark_results.json` to extract:
   - **Baseline Context**: Full plan + roadmap token count.
   - **RoadmapFlow Active Context**: Tier 1 + Tier 2 token count.
   - **Tier 2 Snapshot**: Target ≤ 200 tokens.
   - **Single-Session Savings %**: Typically > 90%.
   - **10-Session Cumulative Savings**: Total tokens saved and % reduction.

3. **Report to User**:
   Present a clear, high-density summary table:

   ```markdown
   ### 📊 RoadmapFlow Token Benchmark Results

   | Metric | Baseline | RoadmapFlow | Savings |
   | :--- | :--- | :--- | :--- |
   | **Active Context per Turn** | ~9,124 tokens | ~797 tokens | **91.3%** |
   | **Tier 2 Session Snapshot** | Full Roadmap | 156 tokens (≤200t budget) | **98.3%** |
   | **10-Session Cumulative** | 118,240 tokens | 7,970 tokens | **93.3%** (110k tokens saved) |
   ```

   Confirm that the full report has been updated in `docs/BENCHMARK_REPORT.md`.
