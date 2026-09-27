# Requirements Gap Analysis: Classroom Availability and Register Management

This compares the current code with the product description. The data model and APIs cover most of the spec. The main problems are three blocking UI bugs, several places where one school's data leaks to another, and weak checks when bookings are created and approved.

## Coverage by requirement

| Requirement | Status | Notes |
|---|---|---|
| **Accounts**: create, edit, deactivate, suspend, reset password | ⚠️ API done, UI broken | The API routes work. The create/edit dialog is expected to crash when it opens (blocker #1). |
| Set role, home school, contact details | ⚠️ Partial | Role is set only at creation. School is always the admin's own school, so accounts can't be moved between schools. Email can't be edited; only phone is. |
| **Rooms**: create, edit, deactivate; name, number, capacity, location, equipment | ✅ | There's no way to reactivate a room in the UI. Deactivating a room leaves its future bookings and home-room assignments in place. |
| **Home-room assignment**: assign, remove, roster, doesn't block booking | ⚠️ | Assign, remove and the roster work. "Reassign" means removing first, because only unassigned users show in the picker. The home room correctly has no effect on booking. |
| **View availability** (admin: full) | ❌ for admins | `src/app/(user)/layout.tsx:9` sends ADMIN and SUPER_ADMIN to `/admin/dashboard`, so admins can never reach `/rooms/[id]`. |
| **Book a room** (admin: any room) | ❌ for admins in UI | The API allows it, but the admin `BookingsView` gets no `rooms` prop, so the "New Booking" button never appears. |
| Per-person auto-confirm vs needs approval | ✅ | `src/app/api/bookings/route.ts:128-131` reads the setting fresh from the database. |
| Approval by admins and teachers with approval rights | ✅ | Notifications for confirmed, pending and rejected bookings are all sent. |
| Recurring weekly and one-off bookings | ⚠️ | See booking issues below. |
| Block slots already booked **or reserved for a class** | ⚠️ | Booking conflicts are checked. Nothing in the code models a class or timetable reservation. |
| Per-school booking rules | ✅ | Rules can be saved with min > max, which makes every booking impossible. |
| Cancellation confirmation, cancellation and no-show tracking | ✅ minimal | Timestamps and reasons are stored. No-shows are marked by hand only, and there's no report of either. |
| In-app notifications | ✅ | The bell checks for new ones every 30 seconds. |
| Separate data per school | ⚠️ | Several leaks (below). |
| Super admin managing every school | ❌ mostly | It can list and create schools and see all bookings. It can't manage accounts, rooms or rules for a school, and it can't deactivate a school. |
| Mobile-friendly layout | ✅ mostly | The mobile menu doesn't close after you tap a link (`src/components/layout/app-shell.tsx:37`). |

## Blocking bugs

1. **The account dialog will crash.** `src/components/admin/accounts-table.tsx:266` uses `<SelectItem value="">`. The installed Radix Select (v2.3.7) throws an error on an empty-string value, so admins can't create or edit accounts from the UI.
2. **Admins can't book or see availability** (see the table above).
3. **The super admin breaks the admin pages.** The admin layout lets SUPER_ADMIN in, but every admin route uses `user.schoolId!`, which is `undefined` for the super admin:
   - The admin pages have no school filter, so they mix every school's data together.
   - `POST /api/rooms` and `/api/admin/booking-rules` fail with a server error.
   - `POST /api/admin/accounts` creates users that belong to no school.

## Data leaking between schools

- `GET /api/rooms/[id]` has no school check. Anyone signed in can read any room, its home-room users' emails, and its upcoming bookings.
- `GET /api/rooms/[id]/availability` has no school check either.
- `PATCH` and `DELETE /api/rooms/[id]` let an admin of school A edit or deactivate school B's rooms.
- `homeRoomId` on account create and update isn't checked. It can point at another school's room or an inactive one.
- `School.isActive` is never checked, including at login.

## Sessions keep old permissions

Role, `canApprove` and status are copied into the login token once (`src/lib/auth.ts:46-52`) and never re-read. A suspended or deactivated user keeps access until the token expires, 30 days by default. Changes to approval rights don't take effect until the user logs in again.

## Booking logic issues

- **Past bookings are accepted.** A negative `advanceDays` (`src/app/api/bookings/route.ts:116`) passes validation, and the same-day rule only rejects today's date.
- **Double-booking race.** The conflict check and the insert aren't in a transaction, and the database has no overlap constraint, so two requests at the same moment can both succeed.
- **Recurring bookings:**
  - The series end date isn't checked against `maxAdvanceDays`, and the loop at `src/app/api/bookings/route.ts:143` has no cap, so an end date far in the future creates thousands of rows one at a time.
  - Weeks that clash are skipped without telling the user.
  - WEEKLY with no end date quietly becomes a one-off booking.
  - The series isn't created in a transaction.
  - Approve and cancel work on one occurrence at a time, so a 10-week series needs 10 approvals, and approvers are only notified about the first one.
- **Status changes aren't checked** (`src/app/api/bookings/[id]/route.ts:63-90`):
  - A REJECTED or CANCELLED booking can be approved, with no new conflict check, even if someone has since taken the slot.
  - A CONFIRMED booking can be rejected.
  - A future or PENDING booking can be marked as a no-show.
  - A teacher with approval rights can approve their own pending booking.
- **Timezones.** Day-level rules use the server's local time. Schools have no timezone field.
- **Calendar hides short bookings.** `src/components/bookings/room-availability-calendar.tsx:56` checks `e.getHours() > hour`, so a 10:00–10:30 booking doesn't appear at all. The grid also only shows 07:00–20:00.
- **Availability misses edge bookings.** The API only returns bookings fully inside the window (`startTime >= start && endTime <= end`), so ones crossing the window's edge are left out.

## Minor issues

- Editing a room number to one already in use causes a server error from the database's unique constraint, instead of a clean "already exists" message.
- After editing an account, the list shows the old home room.
- API errors are shown to users as raw JSON text.
- Approval requests also go to suspended or deactivated approvers.
- The "can approve" switch appears for students, although it has no effect for them.

## Recommended fix order

1. Blocker #1 (the account dialog crash).
2. The school-leak checks on `rooms/[id]` and its availability route.
3. Rejecting past bookings, and checking status before approve/reject/cancel.
4. Routing admins to availability and booking.
5. A school picker for the super admin, which it needs before any admin page works for it.
