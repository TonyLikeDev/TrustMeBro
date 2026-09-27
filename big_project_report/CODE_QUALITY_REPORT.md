# Code quality comparison: `app/` (Bob 2.0) vs `by-gemini/`

Date: 2026-09-27. Both apps target Milestones 1–3 of `PLAN.md`.

**How this was checked:**
- Read every router, lib file, layout and the main components in both apps.
- Ran `tsc --noEmit` and `next lint` on each.
- Started both dev servers and sent requests to the key routes.
- Ran a Prisma query against a copy of the SQLite database.

---

## 1. The short version

**`by-gemini/` is a fork of `app/`, not a separate implementation.** It has the same 39-file tree, and several files are identical (`providers.tsx`, `api/trpc/route.ts`). Its `node_modules` is a symlink to `app/node_modules`. So the two have the same structure. They differ in three areas: how local development works, how polished the UI is, and security.

| | `app/` (Bob 2.0) | `by-gemini/` |
|---|---|---|
| `tsc` / `next lint` | 0 errors / 0 warnings | 0 errors / 0 warnings |
| Runs locally? | **No.** Every route, including `/api/trpc`, redirects to `/login` (307), and `dev.db` has 0 rows | **Yes.** It's seeded (6 users, 3 rooms), `/admin` returns 200, and there's a role switcher |
| Security | 1 critical bug, shared with gemini | **3 critical bugs**: the shared one plus 2 of its own |
| Tests | none | none (its roadmap entry says "verified tRPC API tests", but no test files exist) |
| Self-contained | has git, a lockfile, a migration and its own `node_modules` | no lockfile, no migrations, borrowed `node_modules` |
| Source size | 82.6 KB, about 3.0k lines | 117.6 KB, about 3.4k lines (**+42% bytes**, mostly longer Tailwind class strings) |
| Verdict | less finished, fewer ways to fail | more finished, more ways to fail |

---

## 2. Bugs, ranked

### Critical

1. **Both: an admin can make themselves super-admin.** `userUpdateSchema` accepts `role: "super_admin"`. `create` blocks that role, but `update` doesn't check it (`app/src/trpc/routers/users.ts:22-28`, `:201`). An admin can edit their own account to super-admin and then see every school.
2. **Gemini: auth is skipped if `DATABASE_URL` is unset.** `isLocalDev()` returns true when `DATABASE_URL` is missing or points at a `file:` path (`by-gemini/src/lib/auth.ts:17-22`). The middleware then waves through every request (`by-gemini/src/middleware.ts:16-25`), and `getSessionUser` logs the caller in as the seeded admin. One missing environment variable in production means no authentication at all.
3. **Gemini: any user can be impersonated by setting a cookie.** In local-dev mode, `dev_user_id` is trusted without any check. I confirmed it: `curl -H 'Cookie: dev_user_id=…0001'` returned the full user list as super-admin, with no password. The role switcher in `AppShell` and the quick-login buttons on the login page are always rendered, never hidden, so they also show up in production builds.

### High

4. **Both: an admin whose `schoolId` is null sees every school.** The filter is `schoolId: ctx.user.schoolId ?? undefined`, and Prisma treats `undefined` as "no filter" (`users.ts:53`, `rooms.ts:43`).
5. **Both: suspended users keep working.** `getSessionUser` never checks `status`, so blocking a user depends entirely on the Supabase ban. **Gemini also silently swallows ban failures** in its `deactivate` handler, so the database can say "suspended" while the Auth account is still active. That breaks the Milestone 2 exit criterion ("Deactivated account cannot log in").
6. **Both: new users never get an invite email.** `auth.admin.generateLink({ type: "recovery" })` only returns a link; it doesn't send anything. Also, if the database upsert fails after the Supabase user was created, the Auth account is left orphaned.
7. **Gemini: "create user" can take over a user from another school.** The upsert looks users up by `email`. Locally, creating a user with an email that already exists overwrites that user's name, role and school.
8. **`app/`: user search crashes on SQLite.** I confirmed this against the real Prisma client: ``Unknown argument `mode` `` (`app/src/trpc/routers/users.ts:59`). The first keystroke in the search box shows "Failed to load users". Gemini removed `mode`, which means its search will be case-sensitive on Postgres.

### Medium

- **Both:** a super-admin can assign a user from school A to a room in school B (`roomAssignments.ts:59-70`).
- **`app/`:** a super-admin can't create rooms at all. The ternary has two identical branches and the result is `null`, which the handler rejects (`app/src/trpc/routers/rooms.ts:112-114`). Gemini quietly puts the room in whichever school comes first, which is a different surprise.
- **`app/`:** none of the list or detail mutations have an `onError` handler, so failures are silent. `AppShell` links to 8 pages that don't exist (`/admin/bookings`, `/super-admin/schools`, …).
- **Gemini:**
  - About 48 Tailwind v4 class names (`shadow-xs`, `outline-hidden`) in a Tailwind **3.4.19** project. They do nothing.
  - `availableUsers` (`by-gemini/src/trpc/routers/roomAssignments.ts:56`) is written but never called. The room page still loads every user in the school and filters them in the browser.
  - `(student)/layout.tsx` has no role check.
  - Error handling is `alert()`, and the success toast is copy-pasted 9 times with `setTimeout` calls that are never cleaned up.

---

## 3. Structure and duplication

The two share the same layering: route groups → client component → tRPC router → Prisma. The weakness is the same too: **there is no shared helper for "check this belongs to your school"**. The fetch → `NOT_FOUND` → `FORBIDDEN` block is repeated inline 14 times in `app/` and 15 in gemini. Gemini also queries the database directly from 3 dashboard server components, which puts the scoping logic outside tRPC.

| Duplicated piece | `app/` copies | gemini copies |
|---|---|---|
| School-access guard in routers | 14 | 15 (+3 in dashboards) |
| Local-dev detection | 2, and the middleware ignores it, which is why local dev is broken | **5, and they disagree** (the client checks the Supabase URL, the server also checks `DATABASE_URL`) |
| Hard-coded seed user IDs | 1 | 3 (`auth.ts`, `LoginForm`, `AppShell`) |
| `ROLE_HOME` / `ROLE_BADGE` maps | 3 / 2 | 3 / 2 |
| `as UserRole` enum casts | 17 | 34 (each router result is cast again) |
| Toast + `alert` + `setTimeout` per mutation | 0 | 9 |
| Files with `"super_admin"` literals | 17 files / 36 hits | 19 files / 39 hits |

---

## 4. Plan and roadmap drift (the roadmap needs fixing)

- **Maintenance** says "`app/prisma/dev.db` exists and is seeded", but it has **0 rows**.
- **M1** says "shadcn/ui installed": no shadcn or Radix package is in `package.json` in either app.
- **Next actions** still says "Start Milestone 3", but M3 is ticked.
- The **Gemini change log** entry claims tRPC API tests that don't exist.
- **Gemini** uses `db push` with no migrations, while the plan's exit criterion is `prisma migrate dev`.
- **Neither app** has Postgres RLS policies. Both are effectively on the plan's "application-layer filter" fallback, which should be logged as a Deviation once you approve it.

Running `/roadmap-sync` would reconcile these.

---

## 5. What future changes will cost

### How many places each common change touches

| Change | `app/` | gemini |
|---|---|---|
| Add a role (e.g. `staff`) | about 9 places | about 12 (plus the dev account lists) |
| Change the school-scoping or RLS rule | 14 places, or 1 after extracting a helper | 18 places, or 1 after extracting a helper |
| Change how local dev is detected | 2 (plus the middleware fix) | 5, and they have to be made to agree |
| Replace alert/toast with a real toast system | 1 | 9 |
| Switch SQLite → Postgres | new migration baseline; search already correct for Postgres | create migrations from scratch; search becomes case-sensitive |

### Time: debt to pay before Milestone 4 (focused developer-hours)

| | `app/` | gemini |
|---|---|---|
| Shared fixes (#1, #4, #5, #6, cross-school assign, a minimal `createCaller` test harness, pagination and search debounce) | 5–6 h | 5–6 h |
| App-specific fixes | 3–4 h: make local dev and the seed work, `mode`, super-admin room creation, `onError` handlers, dead links | 6–7 h: one explicit dev-mode flag replacing 5 checks, gate the switchers, email upsert, swallowed bans, Tailwind classes, wire up `availableUsers`, lockfile and migrations, one toast hook |
| **Total** | **≈ 8–10 h** | **≈ 11–13 h** |

**Milestones 4–7 (bookings, approvals, notifications, polish):** about 65–100 hours with either base, because the backend is the same. Gemini's screens take about 1.3× the lines (UserList 282 vs 204, room detail 340 vs 262), so its UI work runs about **+10–20%** unless the repeated toast/alert code is consolidated. Its working role switcher makes manual testing across four roles cheaper, which offsets part of that. `app/` is effectively untestable in a browser until local dev is fixed.

### Storage

| | `app/` | gemini |
|---|---|---|
| Source | 82.6 KB | 117.6 KB (+42%) |
| Projected source at Milestone 7 | ≈ 9–11k lines | ≈ 12–14k lines |
| `node_modules` | 849 MB | 0 MB (symlink) |

- **Hidden coupling:** deleting or reinstalling `app/` breaks gemini, and gemini has no lockfile, so its builds can't be reproduced.
- **Database:** the schema and indexes are identical, so data growth is the same. Recurring bookings will drive storage once Milestone 4 lands; the plan's "expand lazily" decision keeps that small in both.
- **`.next` dev caches:** 151 MB vs 130 MB. That's not meaningful.

### Speed

- **Measured, gemini:** `/admin` takes 2.25 s on first compile; `users.list` takes 2.5 s cold and **0.07 s warm**.
- **Measured, `app/`:** couldn't be measured past the redirect.
- **Hot spots in both:**
  - The room detail page downloads every user in the school just to fill a dropdown.
  - `users.list` has no pagination.
  - Search sends a query on every keystroke.
  - In production each request makes 2 Supabase Auth round trips (middleware plus tRPC context) and 1 database lookup.
- **Scaling:** at around 5k users per school, the room page and user list will be the first things to feel slow. Gemini's unused `availableUsers` endpoint already fixes the room page once it's wired in.

---

## 6. Recommendation

**Keep one app.** I'd continue on **`app/`**: it has git, a lockfile, a migration, its own dependencies, and fewer security holes. Then port four things from gemini, about 3–4 hours:

- the role switcher, behind an explicit `DEV_LOGIN=1` flag
- `users.schools` and the super-admin school picker
- the trimmed nav
- the `availableUsers` endpoint, actually wired in

Total ≈ 11–14 hours, about the same as fixing gemini in place, but you end up with the history and a clean supply chain. Fix #1 (the self-promotion to super-admin) first whichever base you pick; it's a one-line guard.
