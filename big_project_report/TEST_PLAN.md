<!-- tricklord -->
# Plan: Classroom Availability and Register Management

A multi-tenant web app for schools/branches to manage teacher and student accounts, classroom inventory, and room bookings. This plan was derived from the product description provided by the team. It is organized into seven milestone-based phases; milestones replace fixed weeks because the team controls its own deadline. The plan says what we intend to build; ROADMAP.md (created after approval) tracks what is actually done.

---

## 0. Decisions

| Topic | Options | Decision | Why |
| :--- | :--- | :--- | :--- |
| Frontend framework | React, Vue, Next.js, SvelteKit | **Next.js (App Router)** | SSR for fast mobile loads; built-in API routes reduce backend boilerplate; strong ecosystem |
| Backend / API | Separate Express/FastAPI vs Next.js API routes | **Next.js API routes (tRPC)** | Single repo, type-safe end-to-end, no separate deployment |
| Database | PostgreSQL, MySQL, SQLite | **PostgreSQL via Supabase** | Multi-tenancy, row-level security per school, hosted auth, realtime subscriptions for notifications |
| Auth | Custom JWT, NextAuth, Supabase Auth | **Supabase Auth** | Already in stack; supports role-based claims; session management out of the box |
| Styling | Tailwind CSS vs CSS modules | **Tailwind CSS + shadcn/ui** | Rapid responsive UI, mobile-first, accessible components out of the box |
| ORM | Prisma vs Drizzle vs raw SQL | **Prisma** | Type-safe schema, migration tooling, works well with PostgreSQL |
| Multi-tenancy isolation | Row-level isolation vs separate DB per school | **Row-level isolation with school_id FK + Postgres RLS** | Cost-effective; Supabase RLS enforces tenant boundary at DB level |
| Booking recurrence | Store expanded slots vs rule + generator | **Store a recurrence rule; expand lazily on read** | Avoids slot explosion for long-running recurring bookings |
| Notification delivery | Email, in-app, push | **In-app only for MVP; email as stretch goal** | Keeps scope tight; Supabase Realtime covers in-app |
| Deployment | Vercel, Railway, self-hosted | **Vercel (frontend) + Supabase (managed DB/auth)** | Zero-config deployment for Next.js; matches Supabase's native integration |

---

## 1. Objectives

**General objective.** Build and deploy a production-ready multi-tenant web application that lets school admins manage rooms and accounts, and lets teachers and students view availability and book rooms, with role-based approval workflows.

**Specific objectives.**
1. Implement multi-tenant data isolation (school_id, Postgres RLS) with super-admin and school-admin tiers.
2. Build account management CRUD for teachers and students (Admin only).
3. Build room management CRUD and home-room assignment (Admin only).
4. Implement a live availability calendar with conflict detection.
5. Implement one-off and recurring room bookings with per-account authority settings (auto-confirm / needs-approval).
6. Implement an approval workflow (Pending → Approved / Rejected) for bookings requiring sign-off.
7. Deliver in-app notifications for confirmations, approvals, and rejections.
8. Ship a responsive UI (mobile + desktop) for all three roles.

**Deliverables.**
- Deployed web application (Vercel + Supabase)
- Source code in repository with migrations and seed data
- PLAN.md + ROADMAP.md tracking all work
- Bob session screenshots in `bob_sessions/`

---

## 2. Technical Design

### Stack

| Layer | Technology |
| :--- | :--- |
| Framework | Next.js 14 (App Router) |
| Language | TypeScript |
| Styling | Tailwind CSS + shadcn/ui |
| API layer | tRPC (server actions fallback) |
| ORM | Prisma |
| Database | PostgreSQL (Supabase) |
| Auth | Supabase Auth (JWT with custom claims for role + school_id) |
| Realtime / Notifications | Supabase Realtime |
| Deployment | Vercel + Supabase |

### Directory layout

```
src/
  app/               # Next.js App Router pages & layouts
    (auth)/          # login, password reset
    (super-admin)/   # cross-school views
    (admin)/         # school-scoped admin views
    (teacher)/       # teacher views
    (student)/       # student views
    api/             # tRPC + webhook endpoints
  components/        # shared UI components
  lib/
    db.ts            # Prisma client
    supabase.ts      # Supabase client helpers
    auth.ts          # session utilities
  trpc/              # tRPC routers
  types/             # shared TypeScript types
prisma/
  schema.prisma
  migrations/
  seed.ts
```

### Core database tables

| Table | Key columns |
| :--- | :--- |
| `schools` | id, name, settings (JSONB: booking rules) |
| `users` | id, school_id, role (super_admin\|admin\|teacher\|student), email, name, status, booking_authority (auto\|pending) |
| `rooms` | id, school_id, name, capacity, location, equipment_notes, is_active |
| `room_assignments` | id, user_id, room_id, assigned_at (home-room assignment) |
| `bookings` | id, school_id, room_id, user_id, start_at, end_at, status (pending\|confirmed\|rejected\|cancelled), recurrence_rule (JSONB), is_recurring, cancellation_reason, no_show (bool) |
| `notifications` | id, user_id, type, payload (JSONB), read_at |

### Multi-tenancy rules
- Every query includes a `school_id` filter.
- Postgres RLS policies on each table verify `auth.jwt()->>'school_id' = school_id` for school-scoped roles.
- Super-admin bypasses RLS via a service-role key used only in server-side tRPC procedures.

### Booking conflict detection
- A booking conflicts with any existing confirmed/pending booking on the same room whose `[start_at, end_at)` range overlaps the requested range.
- For recurring bookings, check every expanded occurrence before inserting.

---

## 3. Schedule (milestones)

Each milestone has **Build**, **Measure**, and **Exit criteria**. "Write" appears only where docs are a real output.

---

### Milestone 1: Project scaffold and auth

**Build**
- [ ] Initialize Next.js 14 project with TypeScript and Tailwind
- [ ] Install and configure Prisma, Supabase client, tRPC, shadcn/ui
- [ ] Write initial `schema.prisma` with all core tables and enums
- [ ] Run first migration against Supabase dev DB
- [ ] Set up Supabase Auth with custom JWT claims (role, school_id)
- [ ] Implement login / logout flow (email+password)
- [ ] Implement server-side session guard middleware (redirect if unauthenticated)
- [ ] Create role-based layout wrappers: super-admin, admin, teacher, student
- [ ] Write seed script: 1 school, 1 super-admin, 1 admin, 2 teachers, 2 students, 3 rooms

**Exit criteria**: `prisma migrate dev` succeeds; seed runs without error; login redirects to the correct role dashboard; unauthenticated requests redirect to `/login`.

---

### Milestone 2: Account management (Admin)

**Build**
- [ ] tRPC router `users`: list, create, update, deactivate (soft-delete via status field)
- [ ] Admin UI: user list page with search and role filter
- [ ] Admin UI: create/edit user form (role, school_id, booking_authority, contact details)
- [ ] Admin UI: deactivate / reactivate account action
- [ ] Admin UI: reset-credentials action (trigger Supabase password-reset email)
- [ ] Enforce school_id scoping — admin can only see/edit users in their own school
- [ ] Super-admin can see users across all schools (bypass RLS via service role)

**Exit criteria**: Admin can create a teacher and student, edit their details, deactivate them, and the deactivated account cannot log in; super-admin list shows users from all schools.

---

### Milestone 3: Room management and home-room assignment (Admin)

**Build**
- [ ] tRPC router `rooms`: list, create, update, deactivate
- [ ] Admin UI: room list page
- [ ] Admin UI: create/edit room form (name, capacity, location, equipment_notes)
- [ ] Admin UI: deactivate / reactivate room action
- [ ] tRPC router `roomAssignments`: assign user to room, remove assignment, list by room
- [ ] Admin UI: room detail page with assigned-user roster
- [ ] Admin UI: assign/unassign teacher or student to a room

**Exit criteria**: Admin can create a room, assign a teacher to it, see them on the roster, unassign them, and deactivate the room; deactivated rooms do not appear in the booking calendar.

---

### Milestone 4: Availability calendar and room booking

**Build**
- [ ] Availability query: given a room and date range, return booked slots (confirmed + pending) and free slots respecting school booking rules (min/max slot length, advance booking window, same-day flag)
- [ ] tRPC router `bookings`: create (one-off), create (recurring), cancel, list by room, list by user
- [ ] Booking conflict detection (server-side, also validated client-side for UX)
- [ ] Auto-confirm path: if user's `booking_authority = auto`, booking is inserted as `confirmed`
- [ ] Needs-approval path: if `booking_authority = pending`, booking is inserted as `pending`
- [ ] UI: availability calendar view (week view, per room) visible to all roles
- [ ] UI: book a slot modal (select date/time, one-off vs recurring, submit)
- [ ] UI: my bookings list for teacher and student
- [ ] UI: all bookings list for admin

**Exit criteria**: A user with auto-confirm gets a confirmed booking instantly; a user needing approval gets a pending booking; overlapping slots are rejected; recurring booking creates entries for the next 8 weeks; booking rules are enforced.

---

### Milestone 5: Approval workflow

**Build**
- [ ] tRPC router `bookings`: approve, reject (available to admin; available to teacher if `booking_authority` includes approval rights)
- [ ] Admin/Teacher UI: pending-bookings queue with approve / reject actions
- [ ] Rejection requires a reason string (stored in booking record)
- [ ] Cancellation confirmation modal; cancellation records reason; no-show flag settable by admin/teacher

**Exit criteria**: Admin can approve or reject a pending booking; a teacher with approval authority can do the same; a teacher without authority cannot see the approval queue; cancellation stores reason; no-show can be toggled.

---

### Milestone 6: Notifications

**Build**
- [ ] Insert a `notifications` row whenever a booking is confirmed, approved, rejected, or cancelled
- [ ] Supabase Realtime subscription in the client: update notification badge count live
- [ ] Notification bell UI: dropdown list of unread notifications with timestamps
- [ ] Mark-as-read action (single + mark-all-read)

**Exit criteria**: Booking an auto-confirm slot triggers a notification for the booker; approving a pending booking triggers a notification for the booker; the badge count updates in real time without a page refresh.

---

### Milestone 7: Polish, settings, and deployment

**Build**
- [ ] Admin UI: school settings page (min/max slot length, advance booking window, same-day booking toggle)
- [ ] Mobile-responsive pass: test and fix layout on 375 px (iPhone SE) and 768 px (tablet)
- [ ] Accessibility pass: keyboard navigation, ARIA labels on interactive elements
- [ ] Write `README.md`: local setup, env vars, migration and seed commands, deployment notes
- [ ] Deploy to Vercel + Supabase production environment
- [ ] Smoke-test all role flows on production URL

**Exit criteria**: All role flows work on production URL; school settings are persisted and respected by booking rules; UI is usable on a 375 px screen; README covers setup end-to-end.

---

## 4. Risks and fallbacks

| Risk | Signal | Fallback |
| :--- | :--- | :--- |
| Supabase RLS policy complexity causes bugs or performance issues | Queries fail or return wrong school's data | Fallback to application-layer `school_id` filter on all queries; remove RLS policies and rely on tRPC auth guards |
| Recurring booking expansion is slow for large date ranges | Calendar query takes > 500 ms | Cap recurring bookings at 52 occurrences; add a DB index on `(room_id, start_at)` |
| tRPC adds too much ceremony for simple pages | Boilerplate slows milestone delivery | Replace with Next.js server actions for straightforward mutations |
| Supabase Realtime is unreliable in the target region | Notifications don't arrive live | Fall back to polling every 30 s on the notifications endpoint |
| Scope creep on admin features delays booking milestone | Milestones 2–3 take more than expected | Ship minimal CRUD for accounts and rooms; defer equipment notes and roster UI to Milestone 7 polish |

---

## 5. Deviations

<!-- Dated, user-approved changes: `- YYYY-MM-DD: change, reason` -->
