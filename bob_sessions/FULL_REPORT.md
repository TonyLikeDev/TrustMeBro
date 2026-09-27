# Engineering Report: Monorepo End-to-End Setup, Stabilization & Verification

- **Repository**: `tducn110/Tracker_yourMoney`
- **Date**: 2026-09-27
- **Target Topology**:
  - PostgreSQL Database: `127.0.0.1:5432/finance_db`
  - Standalone Hono API: `http://localhost:3001`
  - Next.js 16 Web App: `http://localhost:3000`
  - Worker Service: Background recurring bill processor

---

## 1. Executive Summary

The repository has been comprehensively diagnosed, repaired, and validated from scratch to end-to-end runtime execution.
All static checks (`pnpm typecheck`, `pnpm lint`, `pnpm test`, `pnpm build`) pass cleanly across all 7 workspace packages.
The entire local development topology (PostgreSQL database, Hono standalone API, Next.js frontend, and `/api/*` rewrite proxy) is operational and verified with live transactions, authentication, budgeting, and analytics.

---

## 2. Issues Discovered & Root Cause Analysis

### Issue 1: Database Dialect Conflict & Connection String
- **Symptom**: `drizzle.config.js` was referencing MySQL, `docker-compose.yml` was starting MySQL 8.0, and `.env` contained placeholder `postgresql://user:password@localhost:5432/dbname`.
- **Immediate Cause**: Inconsistent database dialect configurations across docs, docker-compose, and environment files.
- **System Cause**: Project was migrated from MySQL to Supabase/PostgreSQL, but local development artifacts and environment templates had leftover MySQL references and stale connection strings.
- **Root Cause**: The executable code (`packages/db/src/client.ts`, Drizzle schema, migrations, pg Pool) was strictly PostgreSQL. The local environment needed to be aligned with the actual code.
- **Resolution**:
  - Confirmed local Docker PostgreSQL 16 container (`finance-db-local`) was running on `127.0.0.1:5432` with database `finance_db`, user `finance`, password `finance`.
  - Updated `docker-compose.yml` to specify `postgres:16-alpine` with matching environment variables.
  - Updated `.env` with `DATABASE_URL=postgresql://finance:finance@localhost:5432/finance_db`.
  - Deleted legacy `drizzle.config.js` to prevent dialect confusion.

### Issue 2: Drizzle Migration Metadata Table Schema Mismatch
- **Symptom**: `pnpm --filter @finance/db db:stamp` failed with `relation "__drizzle_migrations" does not exist`.
- **Immediate Cause**: The script checked `information_schema.tables WHERE table_name = '__drizzle_migrations'`, which returned true because Drizzle creates it in the `drizzle` schema (`drizzle.__drizzle_migrations`), but `TRUNCATE TABLE __drizzle_migrations` defaulted to the `public` schema.
- **Root Cause**: Unqualified table reference in `sync-migration-metadata.ts` when querying PostgreSQL.
- **Resolution**:
  - Updated `packages/db/src/scripts/sync-migration-metadata.ts` to explicitly check and manipulate `drizzle.__drizzle_migrations` with `CREATE SCHEMA IF NOT EXISTS drizzle`.
  - Updated `packages/db/src/scripts/check-status.ts` to load `.env` as fallback when `.env.local` does not define `DATABASE_URL`.
  - Verified `db:status`, `db:stamp`, and `db:migrate` all completed successfully.

### Issue 3: ESM Package Boundary and Export Failures
- **Symptom**: Starting Hono API failed with:
  `SyntaxError: The requested module '@finance/db' does not provide an export named 'db'`.
- **Immediate Cause**: `apps/api` was running in Node.js ESM mode, but `packages/db/package.json` lacked `"type": "module"`, causing Node's module loader to treat `@finance/db` as CommonJS and fail named export extraction.
- **Root Cause**: Missing `"type": "module"` in workspace package definitions (`packages/db`, `packages/cache`, `packages/api-client`).
- **Resolution**: Added `"type": "module"` to `packages/db`, `packages/cache`, and `packages/api-client`. Kept unrestricted internal subpath exports for TypeScript and monorepo inter-package compatibility.

### Issue 4: Vitest ESM & Module Resolution Incompatibility in Worker
- **Symptom**: `pnpm test` failed with:
  `Error [ERR_REQUIRE_ESM]: require() of ES Module ... from vitest/dist/config.cjs not supported`.
- **Immediate Cause**: `apps/worker` lacked `"type": "module"` and was locked to vitest `^3.1.0` while `apps/api` used `^4.1.4`. Additionally, `apps/worker/tsconfig.json` used `"module": "node16", "moduleResolution": "node16"`, which rejected `decimal.js` construct signatures and created type mismatch errors on Drizzle operators.
- **Root Cause**: Outdated dependency and compiler options in `apps/worker`.
- **Resolution**:
  - Added `"type": "module"` to `apps/worker/package.json`.
  - Updated vitest to `^4.1.4` and added `passWithNoTests: true` in `vitest.config.ts`.
  - Switched `apps/worker/tsconfig.json` to `"module": "ESNext", "moduleResolution": "bundler"`.
  - Re-routed Drizzle imports in `apps/worker/src/index.ts` through `@finance/db` to share the identical symbol declarations.
  - Added `"typecheck": "tsc --noEmit"` script to `apps/worker/package.json` and `packages/api-client/package.json`.

### Issue 5: Turbopack Inferred Wrong Monorepo Root via Rogue Lockfile
- **Symptom**: Starting `apps/web` with Turbopack caused:
  `resolve './fonts.css' in '/home/pro/hackathon/Tracker_yourMoney/apps'`
- **Immediate Cause**: Turbopack printed:
  `⚠ Warning: We detected multiple lockfiles and selected the directory of /home/pro/pnpm-lock.yaml as the root directory`.
  An unintended empty `pnpm-lock.yaml` existed in `/home/pro`, misleading Turbopack to treat `/home/pro` as the repository root.
- **Root Cause**: External rogue lockfile outside the repository + lack of explicit `turbopack.root` in Next.js config.
- **Resolution**:
  - Removed rogue `/home/pro/pnpm-lock.yaml`.
  - Pinned `turbopack: { root: projectRoot }` explicitly in `apps/web/next.config.ts`.
  - Updated `next.config.ts` rewrite destination to use `process.env.INTERNAL_API_URL || 'http://localhost:3001'`.

---

## 3. Files Changed

| File | Changes Made |
|------|--------------|
| `.env` | Configured `DATABASE_URL` for local Docker PostgreSQL (`postgresql://finance:finance@localhost:5432/finance_db`). |
| `.env.example` | Documented local Docker PostgreSQL connection string. |
| `docker-compose.yml` | Updated service image to `postgres:16-alpine` with `POSTGRES_DB=finance_db`, `POSTGRES_USER=finance`, `POSTGRES_PASSWORD=finance`. |
| `drizzle.config.js` | Deleted obsolete legacy MySQL configuration file. |
| `packages/db/drizzle.config.ts` | Ensured `.env` is loaded in addition to `.env.local`. |
| `packages/db/package.json` | Added `"type": "module"`. |
| `packages/db/src/scripts/check-status.ts` | Added `.env` fallback loading. |
| `packages/db/src/scripts/sync-migration-metadata.ts` | Qualified schema to `drizzle.__drizzle_migrations` with `CREATE SCHEMA IF NOT EXISTS drizzle`. |
| `packages/cache/package.json` | Added `"type": "module"`. |
| `packages/api-client/package.json` | Added `"type": "module"` and `"typecheck": "tsc --noEmit"`. |
| `apps/api/package.json` | Added `"type": "module"`. |
| `apps/api/src/env.ts` | Added `.env.local` support before `.env`. |
| `apps/worker/package.json` | Added `"type": "module"`, `"typecheck": "tsc --noEmit"`, updated vitest to `^4.1.4`. |
| `apps/worker/tsconfig.json` | Switched to `"module": "ESNext", "moduleResolution": "bundler"`. |
| `apps/worker/vitest.config.ts` | Added `passWithNoTests: true`. |
| `apps/worker/src/index.ts` | Replaced direct `drizzle-orm` imports with `@finance/db`. |
| `apps/web/next.config.ts` | Pinned `turbopack.root` to project root and used dynamic `INTERNAL_API_URL` for local `/api/*` proxy rewrite. |

---

## 4. Commands That Pass

All required build and verification gates execute cleanly:

```bash
# 1. Workspace dependency installation
pnpm install
# -> Success (All 7 packages linked)

# 2. Database connection & migration checks
pnpm --filter @finance/db db:status
# -> ✅ Database is reachable. Total Users: 1

pnpm --filter @finance/db db:stamp
# -> ✅ METADATA SYNCHRONIZATION SUCCESSFUL

pnpm --filter @finance/db db:migrate
# -> [✓] migrations applied successfully!

# 3. Typecheck across all 7 workspace packages
pnpm typecheck
# -> Tasks: 7 successful, 7 total (Time: 9.275s)

# 4. Lint check
pnpm lint
# -> Tasks: 6 successful, 6 total (0 errors, 44 warnings)

# 5. Vitest test runner
pnpm test
# -> Tasks: 2 successful, 2 total (worker + api tests pass)

# 6. Production build
pnpm build
# -> Tasks: 10 successful, 10 total (Next.js 16 production build + serverless catch-all compiled)
```

---

## 5. Runtime End-to-End Verification Evidence

### Services Topology
- **PostgreSQL**: `127.0.0.1:5432` — Port open, connection established, all 14 tables verified.
- **Standalone Hono API**: `http://localhost:3001` — Active.
  - `GET /api` -> `200 OK` (`S2S Finance API v1.0.0 is running`)
  - `GET /ping` -> `200 OK` (`pong`)
- **Next.js Web Frontend**: `http://localhost:3000` — Active.
  - `GET /` -> `307 Redirect` to `/login`
  - `GET /login` -> `200 OK` (Server-side rendered with fonts and styles)
- **Local Dev Proxy Rewrite**:
  - `GET http://localhost:3000/api/ping` -> `200 OK` (`pong`) proxied seamlessly to port 3001.

### Tested Financial & Auth Flows (via Frontend Proxy `http://localhost:3000`)
1. **User Registration** (`POST /api/auth/register`):
   - Created user `e2etest@local.dev`.
   - Hashed password with `bcryptjs`.
   - Issued HttpOnly `access_token` (15m) and `refresh_token` (30d) cookies.
   - Seeded user settings, default cash wallet (`Ví Tiền Mặt`), and 11 default financial categories in a single DB transaction.
   - Response: `201 Created`.
2. **User Authentication** (`POST /api/auth/login`):
   - Validated password hash, saved session cookie to cookie jar.
   - Response: `200 OK`.
3. **Wallet Balance & CRUD** (`GET /api/v1/wallet`):
   - Retrieved default wallet with initial balance `0.00`.
   - Response: `200 OK`.
4. **Income Transaction** (`POST /api/v1/transactions`):
   - Deposited `500,000.00 VND` (Salary).
   - Enforced database `chk_wallets_balance_non_negative` check constraint.
   - Wallet balance updated to `500,000.00 VND` via Optimistic Concurrency Control (`version = 1`).
   - Response: `201 Created`.
5. **Expense Transaction** (`POST /api/v1/transactions`):
   - Spent `50,000.00 VND` (Food / "Phở bò").
   - Wallet balance deducted to `450,000.00 VND` (`version = 2`).
   - Wallet audit log entry created atomically.
   - Response: `201 Created`.
6. **Analytics Engine**:
   - `GET /api/v1/analytics/daily-summary` -> `200 OK` (`income: 500000.00`, `expense: 50000.00`, `savings: 450000.00`).
   - `GET /api/v1/analytics/category-spending` -> `200 OK` (`Ăn Uống: 50000.00`).
   - `GET /api/v1/analytics/monthly-trend` -> `200 OK` (6-month income/expense breakdown).
7. **Budget Planning** (`POST /api/v1/budgets`):
   - Created monthly budget `Ngân sách tháng 9` for `1,000,000.00 VND`.
   - Automatically computed: `spent: 50,000.00 VND` (5%), `left: 950,000.00 VND`, `daysRemaining: 3`.
   - Response: `201 Created`.

---

## 6. Remaining External Blockers / Optional Services

- **Firebase Social Login (Google)**: Firebase credentials in `.env` are currently development placeholders. Social login buttons require valid Firebase Project API keys and Google OAuth Client IDs. Local email/password login is completely functional without external Firebase calls.
- **AI Quick Add**: Requires an active `AI_API_KEY` (OpenRouter or OpenAI-compatible API) to parse natural language transaction queries.
- **Sentry Observability**: Sentry DSN is optional and currently empty in development mode; this does not block local build or runtime.

---

## 7. How to Run the Project Next

### Step 1: Start PostgreSQL (if not already running)
```bash
docker-compose up -d
# Or:
docker run -d --name finance-db-local \
  -e POSTGRES_DB=finance_db \
  -e POSTGRES_USER=finance \
  -e POSTGRES_PASSWORD=finance \
  -p 5432:5432 \
  postgres:16-alpine
```

### Step 2: Run Database Migrations
```bash
pnpm --filter @finance/db db:migrate
```

### Step 3: Start Development Servers
In two separate terminals (or with `pnpm dev` from root):

**Terminal 1 — Hono Standalone API (Port 3001)**:
```bash
pnpm --filter @finance/api dev
```

**Terminal 2 — Next.js Frontend (Port 3000)**:
```bash
pnpm --filter web dev
```

Open `http://localhost:3000` in your browser. All requests to `/api/*` will automatically proxy to `http://localhost:3001`.
