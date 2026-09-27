Given TEST_PLAN.md and TEST_ROADMAP.md, Bob ran with all skills enabled until it ran out of tokens.
The run stopped at Milestone 3 when Bob's tokens ran out, so the challenge ends with an analysis of the first 3 milestones only.

## What was compared

| Build | How it was made | Where it got to |
|---|---|---|
| **Bob `app/`** | Bob 2.0 with the tricklord skills (plan → roadmap → build) | M1–M3 built; exit criteria left as `[~]` "User action" |
| **`by-gemini/`** | A fork of Bob's `app/`, finished by Gemini | M1–M3, runnable locally |
| **NoSkill** | Built on its own, with no plan and no skills | M1–M3, plus first drafts of M4–M7 |

Sources: `CODE_QUALITY_REPORT.md` (Bob vs Gemini), `NO-SKILL-VS-BOB-M1-3.md` (NoSkill vs Bob), `NO-SKILL-REPORT.md` (NoSkill vs the product spec). `DEDUP_REPORT.md` covers a different codebase and is discussed separately at the end.

## In general the reports suggest

### 1. Skills bought plan conformance, not a working product
- Bob is the only build that follows `PLAN.md`: tRPC, Supabase Auth, four role layouts, a seed that matches the spec, and a recurrence rule rather than expanded rows. The one exception is RLS, which no build has.
- NoSkill quietly swapped the stack (NextAuth, REST, one stored row per recurrence) and left no record of doing so.
- Bob's app still **does not run locally**. Every route redirects to `/login`, and `dev.db` has 0 rows. NoSkill runs, and all 5 roles log in. Gemini runs too, but only through a dev-mode auth bypass.

### 2. Under a fixed token budget, the skilled run delivered less
- Bob finished 3 of 7 milestones. NoSkill has first drafts of all 7.
- Estimated remaining work:

  | | Debt before M4 | M4–M7 | Total |
  |---|---|---|---|
  | Bob | 10–13 h | 65–100 h | ≈ 75–113 h |
  | NoSkill | 7–11 h | 20–35 h | ≈ 27–46 h |
  | NoSkill, if the plan's stack is binding | | +25–40 h | ≈ 52–86 h |

- Planning and roadmap bookkeeping use tokens that would otherwise go to features. That overhead only pays off when the plan's decisions are binding. With the budget gone, continuing on NoSkill is the cheaper path, and the last report says so.

### 3. The roadmap overstated progress
- Build items were ticked on "tsc + ESLint zero errors" evidence. Type-checking is not verification.
- Every exit criterion was pushed back to the user as `[~] User action`, so no milestone was ever proven end to end by the agent.
- The reviews found drift:
  - "dev.db exists and is seeded" (it has 0 rows)
  - "shadcn/ui installed" (it is not)
  - a stale "Start Milestone 3" next action
  - Gemini's "verified tRPC API tests" (no tests exist)
- **No build has any tests.** A `createCaller` test for Bob would take about 1 hour and would have caught the self-promotion bug and the SQLite search crash.

### 4. Structure: Bob was more consistent, but every build has the same gap
- Bob's school-access guards are consistent: 13 copies, all present, behind a single `protectedProcedure`. NoSkill is missing the guard in 4 room handlers, and that is its critical bug. Gemini inherited Bob's guards and added 3 critical bugs of its own.
- No build has a shared "load this record and check it belongs to your school" helper or a status check on every request. Both reports list these as the first fixes, whichever base is kept.
- Size for M1–M3: Bob 82.6 KB, NoSkill 71 KB plus a 30 KB UI kit, Gemini 117.6 KB (+42% over Bob).

### 5. Every build has at least one critical security bug

| Build | Critical bugs |
|---|---|
| Bob | An admin can promote themselves to super-admin (a one-line fix) |
| NoSkill | Admins from another school can read and edit rooms; account endpoints return `passwordHash` |
| Gemini | The shared self-promotion bug; auth is skipped when `DATABASE_URL` is unset; any user can be impersonated with a cookie |

A structured workflow did not stop security bugs. It made them more consistent: Bob's bugs are in its shared paths, not scattered across handlers.

## What this means for the skills

1. **Verify at runtime before ticking.** An M1 exit criterion like "the app runs locally and login works" should be checked by the agent, not handed to the user. That alone would have caught Bob's biggest gap.
2. **Run `/roadmap-sync` at each milestone boundary.** It is built to find exactly the drift listed above.
3. **Keep the planning overhead proportional to the budget.** On a token-limited run, a lighter plan, or a planning pass that stops sooner, leaves more budget for building.
4. **Add early nudges** toward a shared tenancy guard and one smoke test per router. Every build needed both and none had them.

## The dedup report (separate codebase)

`DEDUP_REPORT.md` measures the dedup skill on another project:
- It removed **1,320 lines net** (4,110 deleted, 2,790 added).
- Merged file pairs shrank by 29–45%.
- The duplicated action layers shrank by 74–80%.

That is the kind of clean-up both classroom apps now need: the school guard is repeated 13–25 times, depending on the build.

## Caveats
- Each approach was run once, on one project.
- Gemini is a fork of Bob's code, not an independent build.
- The hour figures are the reviewer's estimates, not measurements.
