# Code quality comparison: this repo (NoSkill) vs `ClassManagement/app` (Bob 2.0), Milestones 1–3

Date: 2026-09-27. Scope is Milestones 1–3 of `ClassManagement/PLAN.md` (scaffold and auth, account management, rooms and home-room assignment). NoSkill was built without a plan and also contains first versions of Milestones 4–7; those are covered only in section 5 (cost), where they matter.

**How this was checked:**

- Read every route handler, lib file, layout and the main components in both apps.
- Ran `tsc --noEmit` and `next lint` on each.
- Ran both apps from isolated copies in a scratch directory, so neither working tree was touched. NoSkill ran against a throwaway Postgres database (`migrate deploy` + seed, dropped afterwards). Bob ran on a copy of its SQLite file.
- NoSkill: logged in as each role over HTTP and ran the Milestone 2–3 flows plus cross-school tests with a second school.
- Bob: HTTP stops at the login redirect, so its tRPC routers were called directly with `createCaller` against the seeded copy.
- Checked each claim the earlier Bob-vs-Gemini report makes about Bob (section 4b).

The existing NoSkill dev server on port 3001 was hung (5.4 GB of memory, every request timed out) and was left alone.

---

## 1. The short version

**These are two independent implementations with different stacks.** Bob follows the plan's stack: tRPC, Supabase Auth, and SQLite locally (Supabase Postgres planned). NoSkill uses REST route handlers, NextAuth credentials with bcrypt, and Postgres in Docker. NoSkill has no Postgres RLS; neither does Bob.

|                             | NoSkill                                                                                                                               | Bob `app/`                                                                                                                                                                                     |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tsc` / `next lint`         | 0 errors / 0 warnings                                                                                                                 | 0 errors / 0 warnings                                                                                                                                                                          |
| Runs locally?               | **Yes.** `migrate deploy` and the seed work; all 5 seeded roles log in and land on the right home page                                | **No.** Every route, including `/api/trpc`, redirects to `/login` (307). The login form posts to a Supabase stub that isn't running, and `dev.db` has 0 rows. The seed works when run by hand. |
| Milestone 1–3 exit criteria | M1 ✅, M2 ⚠️ (a deactivated user's open session keeps working), M3 ✅                                                                 | Can't be run end to end. At the router level, M3 passes and M2 needs a live Supabase for create and deactivate.                                                                                |
| Critical security bugs      | **1**: school-A rooms can be read and edited by school-B admins                                                                       | **1**: an admin can promote themselves to super-admin                                                                                                                                          |
| Other high-severity bugs    | 4                                                                                                                                     | 4                                                                                                                                                                                              |
| Tests                       | none                                                                                                                                  | none                                                                                                                                                                                           |
| Self-contained              | lockfile ✅, migration ✅, own `node_modules` ✅; **git repo with 0 commits**                                                         | git ✅ (2 commits), lockfile ✅, migration ✅, own `node_modules` ✅                                                                                                                           |
| Source size (M1–3)          | ~71 KB / 1,959 lines, plus a 30 KB / 827-line shadcn-style UI kit                                                                     | 82.6 KB / 2,628 lines (no UI kit; long inline Tailwind strings)                                                                                                                                |
| Follows `PLAN.md` decisions | **No**: NextAuth instead of Supabase Auth, REST instead of tRPC, no RLS, recurring bookings stored as expanded rows instead of a rule | Yes, except RLS (neither has it)                                                                                                                                                               |
| Verdict                     | works today, with tenant-isolation holes                                                                                              | matches the plan, but can't be used yet                                                                                                                                                        |

---

## 2. Bugs, ranked

"Confirmed" means reproduced at runtime. "By reading" means found in the code but not executed.

### Critical

1. **NoSkill: an admin from another school can read and edit your rooms.** Confirmed with a second school: its admin got 200 from `GET /api/rooms/{schoolA-room}` and 200 from `GET …/availability`, and `PATCH` changed school A's room (`equipmentNotes` became "edited by school B"). `DELETE` has the same missing check. (`src/app/api/rooms/[id]/route.ts`, `…/availability/route.ts`). Bob gets this right: all 4 cross-school router calls returned FORBIDDEN.
2. **Bob: an admin can make themselves super-admin.** Confirmed: `users.update({ id: self, role: "super_admin" })` succeeded (`app/src/trpc/routers/users.ts:22-28`, `:201`). An admin can also promote a teacher to admin. NoSkill's update schema has no `role` field; a `role: "SUPER_ADMIN"` PATCH was ignored (confirmed).

### High

3. **NoSkill: account endpoints return password hashes.** Confirmed: the responses to `POST /api/admin/accounts` and `PATCH /api/admin/accounts/[id]` include `passwordHash` (bcrypt), because the create and update calls have no `select`. The hash then sits in the accounts table's client state.
4. **NoSkill: a school-B admin can put their user on a school-A roster.** Confirmed: creating a user with `homeRoomId` set to a school-A room returned 201, and that user now appears on school A's roster. `homeRoomId` is never checked for school or active status.
5. **Both: blocked users keep working.**
   - NoSkill, confirmed: after deactivation, a new login gets 401, but the user's existing session still reads rooms (200) and **created a booking (201)**. Role, `canApprove` and status are copied into the login token once (`src/lib/auth.ts:46-52`), and the token lasts 30 days by default.
   - Bob, by reading: `getSessionUser` never checks `status`. **Bob also ignores ban failures**, which the earlier report said only Gemini did. Confirmed: with Supabase unreachable, `users.deactivate` still returned `status: "suspended"`. `updateUserById` returns an error instead of throwing, and nobody checks it.
6. **Both: a super-admin on admin surfaces misbehaves.**
   - NoSkill, confirmed: `POST /api/rooms` → 500, `GET /api/admin/booking-rules` → 500, `POST /api/admin/accounts` → 201 with `schoolId: null`. The `/admin/*` pages load with no school filter.
   - Bob, confirmed: `rooms.create` → BAD_REQUEST, because both branches of the ternary are identical. An admin with a null `schoolId` sees all 8 users across schools.
7. **Bob: user search crashes on SQLite.** Confirmed: ``Unknown argument `mode` `` (`users.ts:59`). NoSkill's account search runs in the browser and works, but it has no role filter, which M2 asks for.

### Medium

- **NoSkill:**
  - Changing a room number to one that already exists returns 500 instead of 409 (confirmed).
  - There's no reactivate-room button, although the API supports it (confirmed via `PATCH status`).
  - There's no super-admin users page, although the API returns all schools' users (confirmed: 6).
  - Nothing stops an admin from deactivating themselves or editing another admin in their school (by reading).
  - Admins can't reach `/rooms`, so they can't see availability (confirmed: 307 to `/admin/dashboard`).
  - `npm run db:seed` calls `tsx`, which isn't in `devDependencies`, so it fails on a fresh clone (only `npx tsx` works).
- **Bob:**
  - A super-admin can assign a school-A user to a school-B room (confirmed).
  - Users can be assigned to an **inactive** room (confirmed).
  - A user can have several home rooms (confirmed: the same teacher assigned to 2 rooms), while the spec says "a default/home room".
  - Rooms have **no room number field**, which the spec requires, and duplicate names are accepted (confirmed).
  - Only 4 of 13 mutations have `onError`, so the others fail silently.
  - `AppShell` links to **6** pages that don't exist (the report said 8).
  - `generateLink` doesn't send an invite email (by reading).

---

## 3. Structure and duplication

Both use the same shape: layouts guard pages, and each handler checks school access inline. **Neither has a shared "load this record and confirm it belongs to your school" helper.** Bob's copies are consistent. NoSkill's are missing from the room routes, which is where its critical bug comes from.

| Duplicated piece                          | NoSkill                                                                                                  | Bob                                                  |
| ----------------------------------------- | -------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| School-access guard written inline        | 5 in API routes, **missing in 4 room handlers**; plus 19 `user.schoolId!` assertions in pages and routes | 13 in routers, all present                           |
| `getSessionUser()` + null check           | 20 route handlers                                                                                        | 1 (`protectedProcedure` middleware)                  |
| Role-home redirect maps                   | 1 (`app/page.tsx` switch)                                                                                | 3 (`ROLE_HOME` ×3)                                   |
| `as any` / enum casts                     | 19 `as any`                                                                                              | 5 `as UserRole`                                      |
| Booking-rules default upsert              | 3 copies                                                                                                 | n/a (settings JSON, not built)                       |
| Files / hits with the super-admin literal | 9 / 15                                                                                                   | 17 / 42                                              |
| Toast + error pattern                     | one `useToast` hook; 2 `window.confirm`                                                                  | `alert()` for reset; `confirm()` ×5; no shared toast |

NoSkill's server pages call Prisma directly with `user.schoolId!` (admin dashboard, accounts, rooms, assignments, settings, bookings). That puts school scoping in the pages as well as the API, which is why a super-admin with no school breaks them.

---

## 4a. Plan conformance (Milestones 1–3)

| Plan item                                                                           | NoSkill                                                                                       | Bob                                                                                                                           |
| ----------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Next.js 14 + TS + Tailwind                                                          | ✅                                                                                            | ✅                                                                                                                            |
| Prisma + Supabase + tRPC + shadcn/ui                                                | Prisma ✅, **no Supabase, no tRPC**, shadcn-style Radix components ✅                         | Prisma ✅, Supabase ✅, tRPC ✅, **no shadcn/Radix**                                                                          |
| Schema with all core tables                                                         | ✅ Postgres enums, `canApprove`, `BookingRules` table, `homeRoomId` (one home room)           | ✅ strings-as-enums on SQLite, `RoomAssignment` (many home rooms), settings as a JSON string, **no per-person approval flag** |
| Migration succeeds                                                                  | ✅ `migrate deploy` on a fresh DB                                                             | ✅ migration file; SQLite only                                                                                                |
| Session guard middleware                                                            | ❌ no `middleware.ts`; guards live in layouts and handlers (they work: anonymous → 307 / 401) | ✅ `middleware.ts`, but it blocks everything locally                                                                          |
| Role layouts: super-admin, admin, teacher, student                                  | ⚠️ teacher and student share one `(user)` layout                                              | ✅ four layouts                                                                                                               |
| Seed: 1 school, 1 SA, 1 admin, 2 teachers, **2 students**, 3 rooms                  | ⚠️ 1 student                                                                                  | ✅                                                                                                                            |
| **M1 exit**: login → role home; anonymous → `/login`                                | ✅ confirmed for all roles                                                                    | ❌ can't log in locally                                                                                                       |
| M2: list with search **and role filter**                                            | ⚠️ search only                                                                                | ✅ (search crashes)                                                                                                           |
| M2: reset credentials by **email**                                                  | ⚠️ admin sets a new password directly                                                         | ✅ by reading (needs Supabase)                                                                                                |
| M2: super-admin sees all schools' users                                             | ⚠️ API yes, no page                                                                           | ✅ page + router                                                                                                              |
| **M2 exit**: deactivated user can't log in                                          | ⚠️ new logins blocked; existing sessions continue                                             | untestable; code doesn't check status                                                                                         |
| M3: rooms CRUD + deactivate/**reactivate**                                          | ⚠️ no reactivate button                                                                       | ✅                                                                                                                            |
| M3: room detail page with roster                                                    | ⚠️ roster is on a separate Assignments page                                                   | ✅                                                                                                                            |
| **M3 exit**: create room, assign, roster, unassign, deactivate; hidden from booking | ✅ all confirmed; a deactivated room returns 404 on booking                                   | ✅ at router level (no booking calendar yet)                                                                                  |

## 4b. The earlier report's claims about Bob, checked

| Claim                                                                | Result                                                                                               |
| -------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| Every route redirects to `/login`; `dev.db` has 0 rows               | **Confirmed**                                                                                        |
| #1 admin can self-promote to super-admin                             | **Confirmed** (and admin can promote teacher → admin)                                                |
| #4 admin with null `schoolId` sees every school                      | **Confirmed** (8 users)                                                                              |
| #5 suspended users keep working; "Gemini also swallows ban failures" | **Confirmed for Bob, and Bob swallows ban failures too.** The report attributed that only to Gemini. |
| #6 `generateLink` sends nothing; orphaned Auth user                  | Agrees with the code (not run)                                                                       |
| #8 search crashes on SQLite (`mode`)                                 | **Confirmed**                                                                                        |
| Super-admin can't create rooms                                       | **Confirmed**                                                                                        |
| Cross-school assignment by super-admin                               | **Confirmed**                                                                                        |
| `AppShell` links to 8 missing pages                                  | **Corrected: 6**                                                                                     |
| 14 inline guard copies                                               | 13 by my count                                                                                       |
| 17 `as UserRole` casts                                               | 5 by my count of `as UserRole` (the report may have counted all enum casts)                          |
| 82.6 KB source; 849 MB `node_modules`                                | **Confirmed**                                                                                        |

## 4c. Drift in NoSkill

- There's no plan or roadmap, so nothing drifts, but nothing records the stack deviations either.
- The git repo has **0 commits**. Everything is untracked, including this report.
- `ACCOUNTS.md` lists seed passwords. It's fine for dev, but check before the repo goes anywhere shared.

---

## 5. What future changes will cost

### How many places each common change touches

| Change                                                     | NoSkill                                                                                           | Bob                                |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | ---------------------------------- |
| Add a role (e.g. `staff`)                                  | about 8: Prisma enum, 2 zod enums, sidebar, root redirect, layouts, session helpers, account form | about 9                            |
| Change the school-scoping rule                             | about 25 (20 handlers + server pages), or 1 after extracting a helper                             | 13, or 1 after extracting a helper |
| Make local dev work                                        | 0; it already works                                                                               | 2 checks plus the middleware       |
| Consistent error toasts                                    | 0 (already has `useToast`)                                                                        | ~13 mutations                      |
| Move to Postgres                                           | done                                                                                              | new migration baseline; fix `mode` |
| **Align with the plan's stack** (Supabase Auth, tRPC, RLS) | large: rewrite auth, move 20 handlers into routers, add RLS                                       | done, apart from RLS               |

### Time: debt to pay before Milestone 4 (focused developer-hours, estimates)

|                                           | NoSkill                                                                                                                                               | Bob                                                                                                                                                    |
| ----------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Security and tenancy                      | 2–3 h: school helper applied to room routes, `homeRoomId` check, strip `passwordHash`, re-check status/role per request, self and admin-target guards | 5–6 h (from the report): role guard, null-school guard, status check, invite email, ban errors, cross-school assign                                    |
| Milestone 1–3 gaps                        | 2–3 h: reactivate button, role filter, super-admin users page, 409 on duplicate room number, declare `tsx`, second seeded student                     | 3–4 h: local dev + seed, `mode`, super-admin room creation, `onError`, dead links; add a room-number field and decide on one-vs-many home rooms (+1 h) |
| Super-admin school picker for admin pages | 2–3 h (or 0.5 h to block super-admin from `/admin`)                                                                                                   | included above                                                                                                                                         |
| Minimal test harness                      | 1–2 h (route handlers + a test database)                                                                                                              | 1 h (`createCaller` already works)                                                                                                                     |
| **Total**                                 | **≈ 7–11 h**                                                                                                                                          | **≈ 10–13 h**                                                                                                                                          |

**Milestones 4–7:** NoSkill already has first versions of bookings (one-off and weekly), conflict checks, approvals, notifications and booking-rule settings. What's left there is fixing the issues in `NO-SKILL-REPORT.md`:

- past bookings are accepted
- the double-booking race
- recurring series have no cap and are handled one occurrence at a time
- status changes aren't validated
- the calendar hides bookings under an hour
- admins have no booking UI

That's roughly **20–35 h** plus deployment. Bob is at **65–100 h** (the report's estimate), since none of it exists yet.

If the plan's stack decisions are binding, add roughly **25–40 h** to NoSkill to move it onto Supabase Auth, tRPC and RLS, which erases most of that lead.

### Storage

|                    | NoSkill                                                                                                | Bob                                                        |
| ------------------ | ------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------- |
| Source             | 151.7 KB / 4,222 lines in total (71 KB for M1–3, 50 KB for M4–7, 30 KB UI kit)                         | 82.6 KB / 2,628 lines                                      |
| `node_modules`     | 655 MB                                                                                                 | 849 MB                                                     |
| Recurring bookings | stored as one row per occurrence, with no cap: an end date far in the future creates thousands of rows | a rule stored in JSON (plan: expand lazily); not built yet |

### Speed

- **Measured, NoSkill** (dev mode):
  - Login takes 0.65–0.9 s (bcrypt cost 12).
  - `GET /api/admin/accounts` takes 38 ms cold and **22 ms warm**.
  - The `/admin/accounts` page takes 1.13 s on first compile and 47–68 ms warm.
- **Measured, Bob:** `users.list` plus `rooms.list` in-process take 2.5 ms warm. That excludes HTTP and Supabase, and HTTP can't be measured past the redirect.
- **Per-request auth:** NoSkill decodes a JWT with no database or network call, which is the cheapest option but is also what causes stale permissions. Bob makes 2 Supabase round trips plus 1 database lookup.
- **Hot spots:**
  - NoSkill has no pagination on accounts or bookings lists (fixed `take` of 50/100/200), and the notification bell polls every 30 s per tab. Recurring bookings are inserted one query at a time, with a conflict query per week.
  - Bob's room page loads every user in the school to fill a dropdown, and search sends a query on every keystroke.

---

## 6. Recommendation

The choice depends on one decision: **are the `PLAN.md` stack decisions binding?**

- **If yes** (Supabase Auth, tRPC, RLS are requirements): continue on **Bob `app/`**. Its tenancy checks are consistent and it matches the plan. Pay down its ≈ 10–13 h of debt first, starting with the self-promotion guard, which is a one-line fix. Use NoSkill as a reference for Milestones 4–7: its booking, approval, notification and booking-rules code maps directly onto Bob's schema.
- **If no** (the spec is what matters, not the plan's stack): continue on **NoSkill**. It runs today, and most of Milestones 4–7 already exist in first-draft form. Fix the room-route school checks and the `passwordHash` leak first (under an hour together). Then commit to git, and record the stack deviations in a plan so they're deliberate.

Whichever base you pick, both need the same two things: a single "belongs to your school" helper, and re-checking account status on every request.

Note that the given token from the Hackathon has been used an run out before the project finished, that's why the analysis suggest that continuing on the Non-skill used version is more convenient
