# `by-gemini/`: stress, security and skill-purpose audit

Date: 2026-09-27. Scope: `by-gemini/` at Milestone 7 (the roadmap says 94% done), measured against `PLAN.md`, `ROADMAP.md` and the tricklord skills in `src/skills/`.

---

## 1. Verdict

- **The app builds and its happy path works.** `tsc`, `next lint` and `next build` are clean (21 routes, 0 errors), and the bundled e2e script passes on an empty bookings table.
- **It is not safe to deploy.** The production build contains no authentication. 20 of 25 security probes succeeded, including cross-school writes and self-promotion to super-admin. None of the 3 critical bugs in `CODE_QUALITY_REPORT.md` (written earlier today) were fixed before Milestones 4–7 were built on top of them.
- **Two of the four roles can't book rooms.** The calendar for students and teachers calls an admin-only endpoint and gets a 403, so the room list stays empty.
- **It stops scaling at about 20k bookings.** List endpoints have no pagination. One admin opening the bookings page downloads 19 MB, and 10 admins at once stall every other user for up to 17 s.
- **The skill set met its goals on paper but not in substance.** The plan is good and the roadmap is formatted correctly, but the roadmap says more than the code does: 31 of 62 ticks name no evidence, at least 4 ticked items fail when tested, and 2 plan items were rewritten without a Deviation entry. Three of the five skills (`layout-init`, `dedup-merge`, `orchestrator`) were never used, and `roadmap-sync` can't run here because there is no git.

---

## 2. How this was tested

- Copied `by-gemini/` to a scratch directory, excluding `.next`. `node_modules` is the same symlink to `app/node_modules`. Added a second tenant (`school-beta` with an admin, a student, a room and a booking) so cross-tenant access could be tested.
- Ran `tsc --noEmit`, `next lint` and `next build`, then `next start` on port 3100 against a copy of the database. The real `by-gemini/prisma/dev.db` and `.next` were not touched.
- **Security:** 25 scripted HTTP probes against `/api/trpc`, the pages and the response headers (`sec.mjs`).
- **Load:** a Node load generator (`stress.mjs`) running races, baseline throughput at 50 concurrent requests, then the same after inserting 20k bookings and 30k notifications, plus a head-of-line blocking test.
- Ran the project's own `src/scripts/test-e2e.ts`.
- Inspected the compiled `.next/server` output to confirm what actually ships.

Machine: one Linux workstation with Node 22.22. Absolute numbers depend on the hardware; the ratios and failure shapes do not.

---

## 3. Security findings

### 3.1 Critical

| # | Finding | Proof | Where |
|---|---|---|---|
| C1 | **The production build has no authentication.** `.env.local` sets `NEXT_PUBLIC_SUPABASE_URL=http://localhost:54321`. Next.js inlines `NEXT_PUBLIC_*` values at build time, so the dev-mode check is always true and the minifier removes the real auth code. The compiled middleware is just `async function iz(e){let{pathname:t}=e.nextUrl;return eo.next()`, and `getSessionUser` has no Supabase branch. Setting the correct environment variables at runtime can't fix a build made this way. Even a clean build falls back to this mode if `DATABASE_URL` is unset. | S1: `users.list` with no cookie → 200. S25: anonymous `GET /admin` → 200. | `src/lib/auth.ts:17-23`, `src/middleware.ts:16-24`, `.next/server/src/middleware.js` |
| C2 | **Anyone can become any user by setting a cookie.** `dev_user_id` is trusted as is, and an unknown id falls back to the seeded admin. | S2: cookie = super-admin id → sees both schools. S3: made-up id → 200. | `src/lib/auth.ts:29-51` |
| C3 | **An admin can promote themselves to super-admin.** `create` blocks the `super_admin` role, but `update` doesn't. | S4: `users.update({id: self, role: "super_admin"})` → then lists users from every school. | `src/trpc/routers/users.ts:27-33, 238-247` |
| C4 | **The approval workflow can be skipped.** Any teacher can approve any booking in their school, including their own pending ones and bookings for rooms they aren't assigned to. There's no "approval authority" field anywhere in the schema. | S5: teacher2 (`bookingAuthority=pending`) books → pending → approves it → confirmed. S6: teacher1 approves a booking that isn't in their queue. | `src/trpc/routers/bookings.ts:386-426` |
| C5 | **Changing a booking's status can double-book a room.** `approve` and `reject` never check the current status, and `approve` doesn't re-run conflict detection. | S7: reject A, book B in the same slot, approve A → 2 confirmed bookings in one slot. S10: a teacher "rejects" an admin's confirmed booking. | `bookings.ts:410-413, 455-461` |

### 3.2 High

| # | Finding | Proof | Where |
|---|---|---|---|
| H1 | Staff in one school can change another school's bookings: `toggleNoShow` has no school check and doesn't even confirm the booking exists, and `cancel` lets any admin through. | S8: Alpha teacher flags a Beta booking as no-show. S9: Alpha admin cancels a Beta booking. | `bookings.ts:479-539` |
| H2 | "Create user" upserts on email, so it can move and demote an existing user from another school. | S16: Alpha admin "creates" `admin@beta.edu` → Beta's admin is now a student in Alpha. | `users.ts:191-210` |
| H3 | Suspended users keep full access, because `getSessionUser` never reads `status`. This also applies to the Supabase branch. | S13: a suspended student books a room → 200, confirmed. | `auth.ts:30-66` |
| H4 | Recurring bookings skip the booking rules: only the first occurrence is validated. | S11: `advance_days=60`, the 12-week series ends 127 days out. | `bookings.ts:275, 284-291` |
| H5 | Unparseable dates get past validation, because every comparison with `NaN` is false. Prisma then fails and the raw Prisma error, including the query shape, is sent to the client. | S12: `startAt:"garbage"` → HTTP 500 with the `prisma.booking.findFirst()` invocation in the body. | `src/lib/bookingRules.ts:40-86` |
| H6 | An admin whose `schoolId` is null sees every school, because `schoolId ?? undefined` means "no filter" to Prisma. | Static finding, same pattern as in the earlier report. | `bookings.ts:165, 208`, `users.ts:58` |

### 3.3 Medium / low

- **S14:** any student can read every booker's email for a room through `listByRoom` (`bookings.ts:116`).
- **S15:** every school admin can list every tenant through `users.schools` (`users.ts:379`).
- **S17:** no length limits on any free-text field. A 5 MB rejection reason was stored, and it is copied into the notification payload as well.
- **S23:** no CSP, `X-Frame-Options`, HSTS, `X-Content-Type-Options` or `Referrer-Policy` headers, and the response sends `x-powered-by: Next.js` (`next.config.mjs`).
- **Not a bug:** `(student)/layout.tsx` has no role check. It's harmless today, but it's inconsistent with the other three layouts.
- **No rate limiting anywhere,** including on the mutations that create notifications.

### 3.4 What held

- S18: SQL injection. Prisma parameterises every query and there's no raw SQL.
- S19 and S20: students calling admin procedures or `approve` get 403.
- S21: cross-school reads of availability get 403.
- S22: booking an inactive room gets 400.
- S24: a student opening `/admin` is redirected.
- XSS: no `dangerouslySetInnerHTML` or `eval`, and React escapes all output.

---

## 4. Stress findings

### 4.1 Booking race (check-then-insert with no transaction or constraint)

| Test | Attempts | Double bookings |
|---|---|---|
| 25 concurrent `create` calls for the same slot, 5 rounds | 125 | **0** (1 success and 24 × 409 each round) |
| 8-week series racing a single booking on week 8, offset swept 0–19 ms | 60 | **0** |
| Series whose week 4 collides | 1 | 0 rows written (conflicts are all found before any insert) |

On SQLite the race **did not reproduce**: the synchronous driver and the single writer serialise the requests. The code (`bookings.ts:294-357`) is still a textbook time-of-check/time-of-use race, with no transaction, no exclusion constraint and 8 sequential inserts. The plan targets pooled Postgres, where this would be a real race. **Not verified on Postgres.** Treat it as a static finding.

### 4.2 Throughput (50 concurrent requests)

| Endpoint | Seeded DB (~30 bookings) | 20k bookings / 30k notifications |
|---|---|---|
| `notifications.unreadCount` (polled every 15 s by every tab) | 215 req/s, p50 198 ms, p99 1.3 s | **120 req/s**, p50 363 ms, **p99 4.2 s, max 10.5 s** |
| `bookings.availability` (1 room, 1 week) | 193 req/s, p50 249 ms | 116 req/s, p50 411 ms |
| `users.list` | 240 req/s, p50 200 ms | — |
| `GET /admin` (server-rendered, 25 concurrent) | 84 req/s, p95 681 ms | — |

### 4.3 Unpaginated endpoints at 20k bookings

| Call | One request | Size |
|---|---|---|
| `bookings.listAll` (admin bookings page) | 1.97 s | **19.0 MB** |
| `bookings.listByRoom` without a date range (open to students) | 0.60 s | 9.5 MB |
| `bookings.listByUser` | 0.37 s | 7.2 MB |
| `listAll`, 10 at once | **p50 19 s, max 28 s**, 1 error | — |

### 4.4 Head-of-line blocking

While 10 `listAll` requests were running, the cheap `unreadCount` call went from p50 62 ms to **p95 17 s**. One Node process plus a synchronous SQLite driver means one heavy request stalls every user.

**What this means in practice:** 15-second polling at 120 req/s saturates at about 1,800 open tabs on this machine before anyone clicks anything. Add pagination and a date range to the three list endpoints first, then an index on `notifications(userId, readAt)`.

---

## 5. Functional break the tests missed

**Students and teachers can't book anything from the UI.** `AvailabilityCalendar` loads rooms with `trpc.rooms.list` (`src/components/calendar/AvailabilityCalendar.tsx:24`), which is an `adminProcedure` (`src/trpc/routers/rooms.ts:28`). I confirmed over HTTP that both a student and a teacher get `403 Admin privileges required`. The rooms array stays `[]`, `activeRoomId` is `""`, the availability query is disabled, and nothing can be booked. The roadmap item "availability calendar view … visible to all roles" is ticked.

## 6. The bundled e2e test

`src/scripts/test-e2e.ts` passes, with these caveats:

- **It isn't wired up.** There's no `npm test`, and it only runs with `ts-node -r tsconfig-paths/register` plus CommonJS overrides.
- **It isn't re-runnable.** Against the shipped `dev.db` it fails with a `CONFLICT` from its own earlier run, and it only passes on an empty bookings table.
- **It skips HTTP, middleware and auth,** because it calls `appRouter.createCaller` directly. That's why it missed §5 and all of §3.
- **It only tests the happy path.** There are zero negative authorisation cases, and it checks 3 recurring occurrences where the exit criterion says 8.

---

## 7. Were the skills' original purposes reached?

### 7.1 Per skill

| Skill | Purpose (from its `SKILL.md`) | What this project shows | Reached? |
|---|---|---|---|
| `roadmap-planner` | Idea → `PLAN.md`, stop for approval, then `ROADMAP.md` and the first action | `PLAN.md` is solid: a decisions table, 8 objectives, observable exit criteria and a risks table. The roadmap has the marker, one heading per phase and a generated progress block. **But** `by-gemini` (a second implementation, which is big work under the layout rule) was never planned: it has no "Plan approved" item and no Deviation, and it appears only as change log lines. | **Yes** for the initial plan. **No** for the big addition. |
| `layout-init` | A `LAYOUT.md` map, kept current | There's no `LAYOUT.md` in the root, `app/` or `by-gemini/`. This confirms the open bug BUG-007 ("planner projects never get a `LAYOUT.md`"), so the layout rules and the "new files without a layout update" reminder never fired. | **Not reached** (never run) |
| `roadmap-sync` | Catch drift between the roadmap and the code | `CODE_QUALITY_REPORT.md` recommended it, and that drift is still there: the Maintenance item says `app/prisma/dev.db` is seeded but it has 0 users; shadcn/ui is ticked but not installed; the change log still claims "verified tRPC API tests". Step 1 (`git log`) can't run, because the root isn't a git repo and `by-gemini/` is in the root `.gitignore`. | **Not reached** (can't run here) |
| `dedup-merge` | Merge copy-pasted code | Same duplication as the earlier report: 5 copies of the dev-mode check, 28 inline `FORBIDDEN` guards across the routers, 9 copies of `alert` + `setTimeout`, and 109 Tailwind v4 class names that do nothing in Tailwind 3.4. | **Not reached** (never run) |
| `orchestrator` | Pick the next skill from project state | With code and no `LAYOUT.md`, its first row says to run `layout-init`. That never happened. | **Not reached** (never run) |

### 7.2 The roadmap rules, checked one by one

| Rule | Held? | Evidence |
|---|---|---|
| 1. Tick with evidence | **No** | 31 of 62 `[x]` name no file, test or result (almost all of Milestones 4–7). Rule 1 also says to tick in the commit that finishes the item, which is impossible without git. |
| 2. Log it | Yes | Dated change log lines for each batch. |
| 3. Progress via the script | Yes | Re-running `roadmap_progress.py` reproduces the block exactly. |
| 4. Next actions, User action first | **No** | The open `[~]` user actions (migrate, seed, live-DB checks for Milestones 1–3) aren't listed. Next actions only say "run by-gemini" and "optionally deploy". |
| 5. Copy phase items from the plan | **No** | M6 "Supabase Realtime subscription" became "real-time/polling". M7 "Deploy to Vercel + Supabase" and "Smoke-test all role flows on production URL" were removed, and "tRPC router `schools`" was added. |
| 6. A phase closes on its exit criteria | **No** | M7's exit criterion "All role flows work on production URL" was rewritten to "Production build succeeds" and ticked. |
| 7. Plan changes need the user and a Deviation line | **No** | `PLAN.md` §5 Deviations is empty, even though these are all plan changes: SQLite instead of Supabase Postgres, no RLS, polling instead of Realtime, eager recurrence expansion instead of the decided "store rule, expand lazily", no deployment, and a second app. |

### 7.3 Ticked items that fail when tested

| Roadmap item (ticked) | Result |
|---|---|
| M4 "UI: availability calendar view visible to all roles" | 403 for students and teachers (§5) |
| M4 exit "School booking rules are enforced" and M7 exit "settings … respected by booking rules" | Recurring series ignore `advance_days` (S11), and invalid dates get through (S12) |
| M5 exit "Teacher without authority cannot see the approval queue" | There is no approval authority; any teacher can approve anything in their school (S5, S6) |
| M6 exit "badge count updates in real time" (plan wording) | It's 15 s polling, reworded in the roadmap instead of logged as a deviation |
| M2 exit (`[~]`) "Deactivated account cannot log in" | Suspended users keep working (S13) |
| Objective 1: tenant isolation "at DB level" | No RLS; cross-tenant writes (S8, S9, S16) |

**The "94%" counts ticks, not verified outcomes.**

### 7.4 Why the skills didn't hold (root causes)

1. **Enforcement depends on hooks that never ran.** tricklord only runs its hooks in Claude Code and IBM Bob; the README calls the rest advice (BUG-008). Judging by the name, `by-gemini` was built by a Gemini agent, which runs none of those hooks and has no rules file (no `GEMINI.md` or `AGENTS.md` equivalent of `.bob/rules/tricklord.md`). The rules reached it only as text it chose to read. It followed the mechanical ones (change log, progress script) and skipped the judgement ones (evidence, deviations).
2. **Nothing requires evidence to be runnable.** Rule 1 accepts a file path as evidence, and a file existing proves nothing about an exit criterion. `roadmap-sync` step 2 only re-runs tests "if quick", and there were none tied to items.
3. **No git.** `roadmap-sync` and "tick in the same commit" both assume git. There's no fallback and no loud failure.
4. **No `LAYOUT.md`.** `dedup-merge` and `orchestrator` both start from it, so neither had anything to act on (BUG-007).
5. **One roadmap tracks two apps.** Evidence paths point into `app/` for Milestones 1–3 and at nothing for Milestones 4–7, where the code exists only in `by-gemini/`. The roadmap can't tell you which app a tick refers to.

---

## 8. Recommendations

### 8.1 For `by-gemini` (in order, if you keep it)

1. **Before any deploy:** replace the dev-mode checks with one explicit server-only flag (`DEV_LOGIN=1`, never `NEXT_PUBLIC_*`), and fail closed when auth isn't configured. Delete `.env.local` from build contexts. (C1, C2) About 1 h.
2. Block role changes to `super_admin` unless the caller is a super-admin. (C3) A one-line guard.
3. Add an `approver` flag, or restrict approval to admins plus the teachers assigned to the room. In `approve`/`reject`, require `status === "pending"`, forbid approving your own booking, and re-check conflicts on approve. (C4, C5) About 2 h.
4. Write one `assertSameSchool(booking|user|room, ctx)` helper and use it in `cancel`, `toggleNoShow` and the 28 other guards. This is where `dedup-merge` would have paid off. (H1, H6)
5. Check `status === "active"` in `getSessionUser`. Validate dates with `z.string().datetime()` and every occurrence of a series. Add `.max()` to every free-text field. Stop upserting on email. (H2–H5)
6. Give students and teachers a read-only `rooms.listForBooking`. (§5)
7. Add pagination and a date range to `listAll`, `listByRoom` and `listByUser`, and an index on `notifications(userId, readAt)`. (§4)
8. Run the conflict check and inserts in a transaction, plus a Postgres exclusion constraint on `(roomId, tstzrange(startAt,endAt))` for active statuses. (§4.1)

### 8.2 For the skill set

1. **Evidence rule:** an exit criterion can only be `[x]` if it names a check that can be re-run (a test name or command). Otherwise it stays `[~]`.
2. **`roadmap-sync`:** add a step that diffs each roadmap phase's items against the plan's and flags rewritten or dropped items as undeclared deviations. Stop loudly when there's no git instead of silently skipping step 1.
3. **Agents without hooks:** ship `AGENTS.md` / `GEMINI.md` copies of the rules, the same way `.bob/rules/` works, and say plainly in the README that other agents get no enforcement.
4. **BUG-007:** have `roadmap-planner` stage 2 run `layout-init` once code exists, so the layout-driven skills have something to work from.
5. **Multiple apps:** support one roadmap per app folder, or require that evidence paths in a shared roadmap start with the app directory.

---

*Artifacts: the probe scripts (`sec.mjs`, `stress.mjs`, `race2.mjs`) and their JSON results are in the session scratchpad. Nothing in `by-gemini/`, `app/` or the plan and roadmap was modified.*
