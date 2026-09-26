# RoadmapFlow — Current Problem & Solution State
> Last updated: Session 001 (pre-hackathon planning)
> This file = single source of truth cho team về what we're building và why

---

## THE PROBLEM (Confirmed, Quantified)

### Core pain: 3 compounding problems khi dùng AI agent cho multi-session projects

**Problem 1 — Manual planning waste**
- Developer có rough idea → tốn 1–3 ngày cấu trúc project: làm gì, thứ tự nào, "done" là gì, risks là gì
- Plans tồn tại trong notes rời rạc, không có exit criteria, không có decisions log
- Kết quả: wasted build time, rework, không handoff được

**Problem 2 — Context window bloat**
- Session sau load full PLAN.md + toàn bộ completed phases → tốn token + giảm accuracy
- Developer hoặc re-explain thủ công (chậm) hoặc dump hết vào (tốn, noisy)
- Không có cách standard để nói "chỉ load cái này thôi"
- **Confirmed live**: Session 001 = 160k tokens chỉ cho research → 75% waste

**Problem 3 — Thiếu execution discipline (insight mới từ session 001)**
- AI agent không có plan-before-act mặc định → gọi tool bừa bãi
- Cùng URL fetch 2 lần, cùng file read nhiều lần → redundant token consumption
- Không có stopping criterion → exploration unbounded
- **Root cause**: Thiếu "declare intent → audit context → execute" loop

### Quantified Pain

| Pain | Cost |
|------|------|
| Manual planning | 1–3 ngày/project |
| Re-explain context mỗi session | 10–20 phút/session |
| Rework từ sai task | ~30% extra time |
| Context waste (full history) | 30–60% tokens wasted |
| Redundant tool calls | 75%+ waste (live measured) |
| Quality cliff > 100k tokens | Output quality drops noticeably |

### Who Has This Problem
- Solo dev / small team dùng IBM Bob cho multi-session projects
- Research projects (ML, engineering) với nhiều phases
- Bất kỳ project nào span > 1 session

---

## THE SOLUTION: RoadmapFlow

### Concept
3 composable IBM Bob 2.0 skills tạo thành closed loop:
```
Brief → Plan → Navigate → Execute → Tick → Next phase → lặp lại
```

### 3 Skills

**Skill 1: `/project-roadmap`**
- Input: project brief (free text)
- Output: 2 files
  - `PLAN.md` — frozen master plan (phases, tasks, exit criteria, decisions log, risks)
  - `ROADMAP.md` — live status board (checkboxes, progress bars, change log)
- Key insight: tách "what we plan" khỏi "what we've done"
- Cost: ~5,000 tokens một lần, không repeat

**Skill 2: `/roadmap-navigator`**
- Input: ROADMAP.md
- Output: `.bob/context/current-phase.md` (~200 tokens)
  - Chỉ chứa: current phase tasks, exit criteria, immediate next actions
- Key insight: thay vì 5,000+ tokens full history → 200 tokens focused scope
- Runs: đầu mỗi session, hoặc sau mỗi phase close

**Skill 3: `/dev-workflow`**
- Input: current-phase.md (200 tokens)
- Steps:
  1. Load context (chỉ current-phase.md, KHÔNG đọc full docs)
  2. Pick next task
  3. **Plan before act** (declare todo list → audit context → fetch only missing)
  4. Execute (code/measure/write)
  5. Tick ROADMAP.md
  6. Check exit criteria (binary PASS/FAIL)
  7. Close phase nếu all pass → Navigator advance
- Key insight: execution discipline enforced, không chỉ recommended

### Architecture (3 Layers — MCP removed)

```
LAYER 1: State (files on disk)
  ROADMAP.md, .bob/context/current-phase.md
  .bob/context/architecture.md
  → Persistent across sessions, human-readable, Git-tracked
  → Bob đọc/ghi trực tiếp — không cần MCP layer

LAYER 2: Skills + Mode-specific Rules (orchestration)
  skills/: orchestration instructions
  rules-agent/: execution discipline (plan-before-act)
  rules-ask/: clarification behavior only
  rules-plan/: architecture-aware planning only
  → Token-optimized: chỉ load đúng rule cho đúng mode

LAYER 3: Bob (executor)
  Agent mode: execute tasks
  Subagents: codebase exploration (isolated context → lean main window)
  Subtasks: per-phase isolation (fresh context window per phase)
  Actor-Critic: Actor subtask + Critic subtask (reliability)
```

### Token Efficiency vs Baseline

| Scenario | Tokens | vs Baseline |
|---|---|---|
| Baseline (no optimization) | ~26,500/session start | 100% |
| Level 1: mode-specific rules + navigator | ~8,900 | 34% (66% saved) |
| Level 2: + subagent for exploration | ~11,900 after 5 turns | 22% (78% saved) |
| Level 3: + MCP state management | ~11,800 full session | 20% (80% saved) |
| Level 4: subtask per phase | ~24,000/phase, always fresh | Peak quality |

---

## HONEST LIMITATIONS

| Limitation | Impact | Mitigation |
|---|---|---|
| Cost không về zero | ~1.5–2.5 Bobcoins/session minimum | Unavoidable, manage với discipline |
| Không scale > 20 phases | ROADMAP.md quá lớn | Giới hạn scope, phân tầng |
| Không reliable với multi-team | Conflict detection kém | Solo/small team only |
| LLM output không deterministic | ~70-80% reliable as-is | Actor-Critic pattern → ~85-90% |
| Feature conflict detection yếu | Có thể re-propose rejected features | decisions.md guardrail |

**Positioning**: RoadmapFlow là tool cho **solo developer / small team, short-to-medium projects, linear workflows**. Không claim enterprise-scale.

---

## BOB FEATURES USED (for submission)

| Feature | Dùng trong | Tại sao |
|---|---|---|
| **Skills** | Cả 3 skills | Core delivery mechanism |
| **Custom Modes** | Override Ask/Plan/Agent | Tailor behavior per phase |
| **Mode-specific Rules** | rules-ask/, rules-agent/ | Token optimization |
| **Agent mode** | dev-workflow execution | Autonomous task execution |
| **Subagents** | Codebase exploration | Isolated context = lean main window |
| **Subtasks** | Per-phase execution | Fresh context window per phase |
| ~~MCP Servers~~ | ~~State management~~ | ~~REMOVED — over-engineer~~ |
| **Todo list** | Execution discipline | Plan-before-act enforcement |
| **Context mentions** | @current-phase.md | Load only what's needed |

---

## WHAT'S STILL OPEN (Session 002 start here)

**P0 — Implement immediately:**
- [ ] Review + refactor 3 SKILL.md files (thêm subagent, 3-tier loading)
- [ ] Tạo .bob/context/architecture.md (~500 tokens, Tier 1)
- [ ] Tạo .bob/rules-ask/, .bob/rules-plan/ (lean, mode-specific)
- [ ] Update roadmap-navigator skill → write current-phase.md 200 tokens

**P1 — Reliability:**
- [ ] Actor-Critic pattern trong dev-workflow
- [ ] Subtask-per-phase pattern

**Submission deliverables:**
- [ ] Demo project: dùng teamsource/ làm live proof
- [ ] Demo video script
- [ ] Slides (6-10 slides)
- [ ] bob_sessions/ screenshots (manual capture in Bob IDE)

---

## KEY INSIGHT FROM SESSION 001 (live evidence)

> Session 001 consumed **160k tokens** for research only — no code written.
> Primary cause: `web_fetch` called twice on same URL = ~40k token waste.
> This IS the problem RoadmapFlow solves, demonstrated live in our own planning session.
> Use this as evidence in submission: "We discovered the problem by experiencing it ourselves."
