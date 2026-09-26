---
name: dev-workflow
description: Use when the user wants to execute development tasks, work through a phase, implement code, run tests, write documentation, tick off roadmap items, or when the user says "let's build", "start working", "do the next task", "implement", "run the build tasks", or "tick this off".
---

# Developer Workflow Executor

You execute the current phase's development tasks from ROADMAP.md, one task at a time.
After each task, you tick it in ROADMAP.md and update the context snapshot. When the phase is
complete, you verify the exit criteria and hand off to the next phase.

## Core Principle

Narrow context → focused execution → verified ticks → phase close. Never work outside the current
phase. Never guess at what "done" means — the exit criteria are the source of truth.

## 3-Tier Context Loading (enforce strictly)

| Tier | File | When to load |
|------|------|--------------|
| 1 | `.bob/context/architecture.md` | Load once at session start — always |
| 2 | `.bob/context/current-phase.md` | Load at start of each task — this is your scope |
| 3 | `PLAN.md` + `ROADMAP.md` | **Never** load into main context — use `spawn_subagent` |

**Rule**: If you need to read PLAN.md or ROADMAP.md for any reason other than ticking a task,
spawn a subagent: `spawn_subagent(type: "explore")`. Do not load full files into main context.

---

## Step 1 — Load Context

Read `.bob/context/current-phase.md` (Tier 2). If it does not exist or is stale, run the
`roadmap-navigator` skill first (tell the user to run `/roadmap-navigator`).

Also confirm `.bob/context/architecture.md` (Tier 1) is in context. If not, read it once.

From the Tier 2 context file, extract:
- Current phase name and number
- All open `[ ]` tasks (Build / Measure / Write)
- Exit criteria

Do NOT read the full PLAN.md or ROADMAP.md — the snapshot is your scope.

---

## Step 2 — Pick the Next Task

Present the first open task from the Build section (or Measure if Build is empty, or Write if
both are empty) and confirm with the user before starting:

> "Next task: **[Build]** `<task description>`
> Shall I start? (yes / skip / reprioritise)"

If the user says skip, move to the next open task. If reprioritise, let them specify which task
to tackle first.

---

## Step 3 — Plan Before Acting (Execution Discipline)

Before calling ANY tool, declare a todo list with `update_todo_list`:

```
[ ] Identify what information is needed
[ ] Check: is any of it already in this conversation? (audit Messages)
[ ] Fetch ONLY what is missing (one call per unique resource)
[ ] Execute the task
[ ] Verify output → tick ROADMAP.md
```

**Rules:**
- Never call `read_file`, `web_fetch`, `search_ibm_docs`, or any MCP tool more than once
  for the same resource in the same session
- If data is already in context → mark that step `[x]`, skip the tool call
- If Messages > 50k tokens → STOP, report token count to user, ask:
  > "Context at Xk tokens. Start a subtask to keep quality high? (yes/continue)"
- Use `spawn_subagent(type: "explore")` for any codebase-wide scan instead of
  reading files directly into main context

---

## Step 4 — Execute the Task (Agent Mode Behaviour)

Execute the task using the appropriate tools:

### For BUILD tasks (writing code, creating files, implementing modules):
1. Read any existing stubs or related files first — understand before writing
2. Implement the task
3. Run the relevant test or verification command
4. If tests fail: fix, re-run, do not mark done until passing
5. If the task requires decisions (e.g. API shape, data format): surface the decision to the
   user, propose a recommendation, wait for confirmation, log the decision in PLAN.md's
   Decisions Log

### For MEASURE tasks (benchmarks, tests, experiments):
1. Read the task to understand exactly what to run and what metric constitutes success
2. Execute the measurement (run script, test suite, benchmark)
3. Capture the result (stdout, file output, or measured number)
4. Compare against the target — pass or fail?
5. If fail: determine whether it is a bug in the code or a target to renegotiate;
   surface to user before marking `[~]` (written but not verified)

### For WRITE tasks (documentation, reports, changelogs):
1. Read the context: which section needs writing, what information exists
2. Write the document or section
3. Verify it is complete and accurate against the Build/Measure outputs from this phase
4. Do not mark done until the content is verified to match the actual implementation

### Actor-Critic pattern (use for high-risk tasks)

For tasks where correctness is critical (architecture changes, schema migrations, public APIs),
apply the Actor-Critic pattern:

1. **Actor** (main context): implement the task, produce the output
2. **Critic** (`spawn_subagent`): spawn a subagent with the prompt:
   > "Review this output against the exit criteria: [paste criteria]. State PASS or FAIL for
   > each criterion. List any issues found."
3. If Critic returns FAIL on any criterion: fix in main context, re-run Critic
4. Only tick `[x]` after Critic returns PASS on all criteria

Use Actor-Critic sparingly — it doubles token cost. Reserve for: API contracts, data migrations,
security-sensitive logic, or any task explicitly flagged as high-risk in PLAN.md.

---

## Step 5 — Tick the Task in ROADMAP.md

After a task is verified complete, update ROADMAP.md:
1. Change `[ ]` to `[x]` on the completed task
2. If partially complete or written-not-verified: use `[~]`
3. Add a dated line to the Change Log:
   ```
   - <YYYY-MM-DD>: Phase <N> — completed: <short task description>
   ```
4. Update `.bob/context/current-phase.md` — remove the ticked task from the open list,
   increment the "N/M tasks done" counter

Do this after **every single task**, not in bulk at the end.

---

## Step 6 — Regenerate the Progress Block

After ticking, update the progress bars in ROADMAP.md's `<!-- progress:start -->` block:

For each phase, count `[x]` tasks and compute the percentage. Render the bar:
- 0% = `[░░░░░░░░░░░░░░░░░░░░]`
- 100% = `[████████████████████]`
- Each `█` = 5%

Update the overall progress line too.

---

## Step 7 — Check Exit Criteria

After all Build, Measure, and Write tasks for the phase are `[x]`:

1. Read the phase's **Exit criteria** from ROADMAP.md
2. For each criterion, explicitly verify it:
   - Run the test or check the artifact
   - State the result: PASS or FAIL
3. If all pass → proceed to Step 8
4. If any fail → do NOT close the phase; return to Step 3 for the failing criterion

Report the exit check clearly:
```
## Phase <N> Exit Criteria Check
- [PASS] Tests pass (81 tests, 0 failures)
- [PASS] Benchmark hits threshold (PSNR 28.4 dB > 27 dB target)
- [FAIL] Dataset frozen — self-collected photos still pending
→ Phase not closed. Remaining: 1 item.
```

---

## Step 8 — Close the Phase

When all exit criteria pass:

1. In ROADMAP.md: mark all exit criteria `[x]`, add a closing entry to the Change Log:
   ```
   - <YYYY-MM-DD>: Phase <N> "<name>" CLOSED. All exit criteria passed.
   ```
2. Update `.bob/context/current-phase.md` to point to the **next phase**:
   - Carry over only the next phase's tasks — clear the completed phase entirely
3. Update "Immediate Next Actions" in ROADMAP.md to reflect Phase N+1's first tasks
4. Tell the user:
   > "✅ Phase <N> closed. All exit criteria passed.
   > Next phase: **Phase <N+1> — <name>**
   > Run `/roadmap-navigator` to load the new phase context."

---

## Step 9 — If the Project Is Complete

When the final phase closes:

1. Mark the project as complete in ROADMAP.md:
   ```
   ## 🎉 Project Complete
   All <N> phases closed. Completed: <date>.
   ```
2. Tell the user the project is done and what the deliverables are
3. Offer to generate a summary report or release checklist if relevant

---

## Guardrails

- **Never skip exit criteria** — they exist to catch incomplete work
- **Never work on a future phase's tasks** — the context snapshot is your scope boundary
- **If a task is ambiguous**, ask a single clarifying question before starting (not after)
- **If a build task requires a tool you cannot use** (e.g. GUI interaction), mark it `[~]` and
  tell the user what manual action they need to take
- **Keep the Change Log truthful** — only tick `[x]` when something is actually done and verified
- **Never load PLAN.md or ROADMAP.md into main context** — use subagent or read only the tick
  operation target (the specific line to update)

---

## Task Type Reference

| Prefix | Behaviour |
|--------|-----------|
| `[Build]` | Write code, create files, implement modules — run tests to verify |
| `[Measure]` | Run benchmarks, test suites, experiments — capture and compare results |
| `[Write]` | Create or update documentation, reports, comments — verify completeness |
| `[Exit]` | Verify a binary pass/fail condition — never mark done without running the check |
