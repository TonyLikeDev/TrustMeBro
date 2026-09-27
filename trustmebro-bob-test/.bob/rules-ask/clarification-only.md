# Ask Mode Rules — RoadmapFlow

## Purpose
Ask mode is for **clarification and explanation only**. It does NOT plan, design, or execute.

## Rules

### Rule 1: No Planning
Do not generate PLAN.md, ROADMAP.md, or architecture decisions in Ask mode.
If the user asks to start planning → redirect: *"Switch to Plan mode for that."*

### Rule 2: No Execution
Do not write code, create files, or call build tools in Ask mode.
If the user asks to implement something → redirect: *"Switch to Agent mode for that."*

### Rule 3: Answer from context first
Before fetching any resource:
1. Scan the current conversation for the answer
2. Check if `.bob/context/architecture.md` is already in context — it likely has the answer
3. Only fetch if the answer is genuinely absent

### Rule 4: One question, one answer
If clarification is needed, ask a **single** focused question — not a list.
If the user's question is ambiguous, state your interpretation before answering.

### Rule 5: Token discipline
Do not load PLAN.md, ROADMAP.md, or completed phase history into Ask mode context.
If the user asks about project status → read `.bob/context/current-phase.md` only.
