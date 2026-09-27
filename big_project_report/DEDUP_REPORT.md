# Code dedup comparison — `odd_fixes` working tree (uncommitted)

Reconstructed directly from the current git diff/status, since duplicate files were deleted and their replacements are still untracked.

## Headline numbers

| | Lines |
|---|---|
| Deleted (old duplicate/inline code) | 4,110 |
| Added (new shared modules, in diff + untracked) | 2,790 |
| **Net removed from app code** | **−1,320** |
| *Separately: unrelated Google Sheets/Drive backup feature dropped* | *−1,895 (not dedup — a feature removal)* |

## Component/page pairs merged

| Duplicate pair (before) | Lines | → | Consolidated file (after) | Lines | Saved |
|---|---|---|---|---|---|
| `teachers/[id]/profile-form.tsx` + `teachers/ta/[id]/profile-form.tsx` | 272 + 248 = 520 | → | `teachers/profile-form.tsx` | 311 | −209 (40%) |
| `teachers/[id]/rates-panel.tsx` + `teachers/ta/[id]/rates-panel.tsx` | 256 + 254 = 510 | → | `teachers/rates-panel.tsx` | 293 | −217 (43%) |
| `teachers/new-teacher.tsx` + `teachers/new-ta.tsx` | 141 + 119 = 260 | → | `teachers/new-staff.tsx` | 184 | −76 (29%) |
| `salary/[teacherId]/salary-period-actions.tsx` + `salary/ta/[id]/salary-period-actions.tsx` | 290 + 288 = 578 | → | `components/domain/salary-period-actions.tsx` | 320 | −258 (45%) |
| Inline payroll-detail JSX in both `salary/[teacherId]/page.tsx` and `salary/ta/[id]/page.tsx` | 339 + 316 = 655 | → | `salary/payroll-detail.tsx` | 446 | −209 (32%) |
| `components/domain/month-nav.tsx` (whole component) | 88 | → | folded into `month-picker.tsx` via a `noFuture` prop | +8 | −80 (component eliminated) |

Both page pairs (`teachers/[id]` ↔ `teachers/ta/[id]`, `salary/[teacherId]` ↔ `salary/ta/[id]`) are now thin wrappers that import the shared component instead of carrying their own copy.

## Server-action / query layer

| File | Before | After | Change | Extracted to |
|---|---|---|---|---|
| `lib/actions/tas.ts` | 415 | 100 | −76% | `lib/actions/staff.ts` (394 lines, shared with `teachers.ts`) |
| `lib/actions/teachers.ts` | 493 | 116 | −76% | same `staff.ts` |
| `lib/actions/salary.ts` | 367 | 75 | −80% | `lib/actions/payroll.ts` (270 lines, shared with `ta-salary.ts`) |
| `lib/actions/ta-salary.ts` | 413 | 108 | −74% | same `payroll.ts` |
| `lib/queries/salary.ts` / `lib/queries/ta-salary.ts` | each had own `groupBy` | dropped | — | `lib/collections.ts` (10-line shared `groupBy`) |
| `lib/actions/settings.ts` | 110 | 36 | −67% | local `requireOwner()` replaced by shared `ownerOrNull`/`academicsUserOrNull`/`moneyUserOrNull`; repeated write+audit blocks collapsed into a local `commitSetting()` |

Enablers added to shared libs: `rbac.ts` (+14, the `*OrNull` helpers), `datetime.ts` (+15, `periodFromParams`), `domain/salary.ts` (+5, `isSnapshot`).

## Out of scope

The removal of `scripts/gdrive-setup.ts`, `gsheet-setup.ts`, `lib/sheets.ts`, `mirror-sheet.ts`, `reconcile-sheet.ts`, `.github/workflows/backup.yml`, and the checked-in OAuth client-secret JSON (−1,895 lines) is a separate feature deletion (Google Sheets backup/mirroring), not deduplication — kept out of the totals above.
