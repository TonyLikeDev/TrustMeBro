---
name: roadmap-navigator
description: Narrow the context window to the active phase by extracting a minimal Tier 2 snapshot (≤200 tokens). Use when the user runs /roadmap-navigator, starts a new work session, asks what to work on next, or says "load my roadmap", "where am I in the project", or "start session".
---

# Roadmap Navigator

Extracts the current phase's tasks into a minimal Tier 2 context snapshot, solving the **context window bloat** problem across multi-session projects.

## Core Principle

Instead of loading the entire unbounded `ROADMAP.md` into context, read only the active phase, extract open tasks, and refresh `.bob/context/current-phase.md` within a strict **≤ 200 token budget**.

## Workflow

1. **Locate `ROADMAP.md`**:
   Check `./ROADMAP.md`, `teamsource/ROADMAP.md`, or `docs/ROADMAP.md`.

2. **Generate Snapshot**:
   Run the snapshot extractor:
   ```bash
   python3 src/roadmap.py snapshot <path-to-roadmap> --output .bob/context/current-phase.md
   ```

3. **Read Snapshot**:
   Read `.bob/context/current-phase.md` and display:
   - **Current Phase**: Name and overall completion status (`done/total`).
   - **Open Tasks**: Build, Measure, Write items.
   - **Exit Criteria**: Verifiable goals required to close this phase.
   - **Token Count**: Confirm snapshot remains strictly ≤ 200 tokens.

4. **Suggest Immediate Next Action**:
   Highlight the top open task and ask the user if they want to execute it with `/dev-workflow` or begin implementation.
