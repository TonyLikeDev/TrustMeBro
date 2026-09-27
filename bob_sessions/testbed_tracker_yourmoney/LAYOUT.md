# LAYOUT.md — Finance Tracker V3
Last updated: 2026-05-20

---

## Folder Tree

```
Tracker_yourMoney/
├── apps/
│   ├── api/                  Hono REST API (Node.js serverless on Vercel)
│   │   └── src/
│   │       ├── index.ts      App bootstrap: CORS, rate-limit, route mounting, error handler
│   │       ├── instrument.ts Sentry Node SDK init
│   │       ├── env.ts        Env validation (dotenv-safe)
│   │       ├── server.ts     Local dev HTTP server entry
│   │       ├── lib/          Shared utilities
│   │       │   ├── errors.ts       AppError hierarchy (NotFoundError, ValidationError…)
│   │       │   ├── firebase-auth.ts Firebase Admin SDK – verifyFirebaseIdToken()
│   │       │   ├── jwt.ts          signAccessToken / signRefreshToken / verifyToken
│   │       │   ├── logger.ts       Pino structured logger
│   │       │   ├── response.ts     Standard JSON envelope helpers
│   │       │   ├── validator.ts    Zod+Hono helper wrappers
│   │       │   ├── crypto-utils.ts SHA-256 token hashing
│   │       │   └── event-bus.ts    In-process event emitter
│   │       ├── middleware/
│   │       │   ├── auth-guard.ts   JWT session cookie → userId in context
│   │       │   ├── audit.ts        Writes mutation events to audit_logs
│   │       │   ├── rate-limit.ts   Sliding-window in-memory rate limiter
│   │       │   ├── error.ts        Global error boundary middleware
│   │       │   └── security-headers.ts HSTS / CSP headers
│   │       ├── routes/             One file per domain (all mount under /api/v1/*)
│   │       │   ├── auth.ts         /auth – social login, refresh, logout, /me
│   │       │   ├── transactions.ts /transactions – CRUD + quick-add NLP
│   │       │   ├── wallet.ts       /wallet – multi-wallet CRUD + cash shortcut
│   │       │   ├── budgets.ts      /budgets – budget CRUD + summary
│   │       │   ├── bills.ts        /bills – recurring bill CRUD + pay
│   │       │   ├── goals.ts        /goals – savings goal CRUD + contribute
│   │       │   ├── categories.ts   /categories – CRUD
│   │       │   ├── analytics.ts    /analytics – category spending, daily summary, trend
│   │       │   ├── notifications.ts /notifications – list, mark read
│   │       │   ├── user.ts         /user – profile, settings, onboarding
│   │       │   ├── ai.ts           /ai – Gemini NLP pass-through endpoint
│   │       │   └── internal.ts     /internal – test-only helpers
│   │       └── services/           Business logic layer
│   │           ├── container.ts        DI container; exports service singletons
│   │           ├── auth-service.ts     Firebase sync, JWT issuance, refresh
│   │           ├── transaction-service.ts CRUD, idempotency, quick-add dispatch
│   │           ├── budget-service.ts   Budget CRUD + SQL-level spent aggregation
│   │           ├── analytics-service.ts Category spending, daily summary, monthly trend
│   │           ├── bill-service.ts     Recurring bills + payment + ledger
│   │           ├── goal-service.ts     Goals + contribution + ledger
│   │           ├── wallet-service.ts   Multi-wallet CRUD, OCC balance updates
│   │           ├── category-service.ts Category CRUD + auto-seed defaults
│   │           ├── ai-service.ts       AI category/wallet auto-creation (OpenRouter)
│   │           ├── idempotency.ts      Idempotency key check + store
│   │           └── adapters/
│   │               ├── nlp-adapter.ts        Regex NLP fallback (INLPAdapter interface)
│   │               └── gemini-nlp-adapter.ts Gemini/OpenRouter primary NLP parser
│   │
│   ├── web/                  Next.js 16 App Router frontend (deployed on Vercel)
│   │   └── src/
│   │       ├── app/
│   │       │   ├── layout.tsx        Root HTML shell, providers
│   │       │   ├── page.tsx          Root redirect (→ /dashboard)
│   │       │   ├── providers.tsx     TanStack Query + theme providers
│   │       │   ├── (auth)/
│   │       │   │   ├── login/        Google social login page
│   │       │   │   └── onboarding/   4-step onboarding wizard
│   │       │   ├── (dashboard)/      Protected layout with sidebar
│   │       │   │   ├── layout.tsx    Dashboard shell (sidebar, nav, AuthGuard)
│   │       │   │   ├── dashboard/    Budget-First overview page
│   │       │   │   ├── transactions/ Transaction list, search, filter, CRUD
│   │       │   │   ├── wallets/      Multi-wallet management
│   │       │   │   ├── budgets/      Category budget setup & tracking
│   │       │   │   ├── bills/        Recurring bills + pay
│   │       │   │   ├── goals/        Savings goals + contribute
│   │       │   │   ├── analytics/    Income/expense charts
│   │       │   │   └── settings/     Category manager, profile, preferences
│   │       │   ├── api/[[...route]]/ Next.js catch-all → Hono bridge (Vercel only)
│   │       │   └── context/
│   │       │       ├── AuthProvider.tsx  Firebase auth state, race-condition guard
│   │       │       └── WalletContext.tsx  Active wallet selection context
│   │       ├── components/
│   │       │   ├── CategoryManager.tsx   Category CRUD panel (Tran Vo Ba Vuong)
│   │       │   ├── EmptyState.tsx        Generic empty-list placeholder
│   │       │   ├── ErrorBoundary.tsx     React error boundary
│   │       │   ├── GoogleAnalytics.tsx   GA4 script injector
│   │       │   ├── budgets/              Budget card + form components
│   │       │   ├── dashboard/            Summary strip, ring chart, wallet card
│   │       │   ├── layout/               Sidebar, top nav, mobile nav
│   │       │   ├── onboarding/           OnboardingWizard (4 steps)
│   │       │   ├── quick-add/            QuickAddModal + SimpleQuickInput
│   │       │   ├── ui/                   shadcn/ui primitives
│   │       │   └── wallet/               CashWalletWidget, AddWalletModal
│   │       ├── _lib/
│   │       │   ├── firebase.ts           Firebase client SDK init
│   │       │   ├── google-oauth.ts       Google OAuth helpers
│   │       │   ├── hooks/
│   │       │   │   ├── finance.tsx       All TanStack Query hooks (useTransactions, useBudgets…)
│   │       │   │   ├── use-budgets.ts    Budget-specific hooks
│   │       │   │   └── use-mounted.ts    Client-side SSR hydration guard
│   │       │   └── utils/
│   │       │       ├── currency-input.ts Input formatting helpers
│   │       │       └── finance.ts        Safe-to-Spend calculation helpers
│   │       ├── locales/vi.json           Vietnamese i18n strings
│   │       └── sentry.*.config.ts        Sentry client/server/edge configs
│   │
│   └── worker/               Recurring bills background processor (tsx)
│       └── src/
│           └── index.ts      Cron-style loop: query due bills → create transactions + notifications
│
├── packages/
│   ├── db/                   Drizzle ORM, schema, repositories (@finance/db)
│   │   └── src/
│   │       ├── client.ts     PostgreSQL pool (pg) + Drizzle instance
│   │       ├── schema/       Table definitions (see Database section)
│   │       ├── repositories/ BaseRepository + domain repos (transaction, bill, goal, budget, analytics, category)
│   │       ├── queries/      Reusable typed query helpers (summary, transactions)
│   │       └── scripts/      DB seed, status-check, migration-sync CLI tools
│   │
│   ├── shared-schemas/       Zod validation schemas shared by API and Web (@finance/shared-schemas)
│   │   └── src/              bill, budget, category, goal, transaction, user, wallet schemas + finance.ts
│   │
│   ├── api-client/           Typed Axios API client (@finance/api-client)
│   │   └── src/
│   │       ├── client.ts         Axios instance, camelCase interceptors, cookie auth
│   │       ├── endpoints.ts      Typed functions: authAPI, budgetAPI, transactionsAPI, walletAPI…
│   │       ├── types.ts          TS interfaces for all API response shapes
│   │       ├── presenters/
│   │       │   └── currencyPresenter.ts  formatCurrency / formatVND / toDecimal
│   │       └── guards/amountGuard.ts     Runtime amount validation
│   │
│   └── cache/                In-memory cache layer (@finance/cache)
│
├── drizzle.config.ts         Root drizzle-kit config (points to packages/db schema)
├── docker-compose.yml        Local PostgreSQL (dev)
├── turbo.json                Turborepo pipeline config
└── pnpm-workspace.yaml       pnpm workspace manifest
```

---

## Components

| Component | Path | Responsibility | Depends On |
|-----------|------|----------------|------------|
| API (Hono) | `apps/api/src/index.ts` | REST API, auth, business logic | `@finance/db`, `@finance/shared-schemas`, `@finance/cache` |
| Web (Next.js) | `apps/web/src/app/` | Dashboard UI, TanStack Query, shadcn/ui | `@finance/api-client`, `@finance/shared-schemas` |
| Worker | `apps/worker/src/index.ts` | Process due recurring bills | `@finance/db`, `@finance/cache` |
| DB package | `packages/db/src/` | Schema, migrations, repositories | PostgreSQL via `pg` |
| Shared Schemas | `packages/shared-schemas/src/` | Zod validation, shared types | — |
| API Client | `packages/api-client/src/` | Typed HTTP client, currency formatting | Axios |
| Cache | `packages/cache/` | In-memory response cache | — |

### Main Flows

**Auth:** `AuthProvider` → `authAPI.login` → `apps/api/src/routes/auth.ts` → `auth-service` (Firebase verify → JWT issue → cookie)

**Transaction CRUD:** `finance.tsx:useTransactions` → `transactionsAPI` → `routes/transactions.ts` → `TransactionService` → `TransactionRepository` → PostgreSQL

**Quick Add (AI):** `QuickAddModal` → `transactionsAPI.quickAdd` → `routes/transactions.ts:/quick` → `TransactionService.quickAdd` → `GeminiNLPAdapter.parseAsync` (fallback: `RegexNLPAdapter`) → insert transaction

**Budget Engine:** `useBudgets` → `budgetAPI.list` → `routes/budgets.ts` → `BudgetService.getBudgets` → SQL JOIN with aggregated SUM(transactions) per budget period

**Analytics Dashboard:** `analyticsAPI` → `routes/analytics.ts` → `AnalyticsService` (category spending, monthly trend, daily summary)

**Recurring Bills Worker:** `apps/worker/src/index.ts` → queries due bills → `BillRepository` + `TransactionRepository` → insert bill_payments + transactions + notifications

---

## Database

All tables defined in `packages/db/src/schema/`. 15 tables total.

| Table | Key Fields | Defined In |
|-------|------------|------------|
| `users` | `id` (bigint PK), `firebase_uid`, `email`, `full_name`, `has_onboarded` | `schema/users.ts` |
| `user_settings` | `user_id` (PK FK), `monthly_budget`, `currency`, `language`, `theme` | `schema/auth.ts` |
| `refresh_tokens` | `id`, `user_id`, `token_hash`, `expires_at` | `schema/auth.ts` |
| `wallets` | `id`, `user_id`, `name`, `type` (enum), `balance`, `version` (OCC), `deleted_at` | `schema/wallet.ts` |
| `wallet_logs` | `id`, `wallet_id`, `balance_before`, `balance_after`, `idempotency_key` | `schema/wallet.ts` |
| `categories` | `id`, `user_id`, `name`, `type` (income/expense), `icon`, `color` | `schema/categories.ts` |
| `transactions` | `id`, `user_id`, `wallet_id`, `category_id`, `amount` (DECIMAL 15,2), `type`, `display_date`, `source`, `idempotency_key` | `schema/transactions.ts` |
| `budgets` | `id`, `user_id`, `name`, `target_amount`, `period_type`, `start_date`, `end_date`, `is_all_categories`, `status` | `schema/budgets.ts` |
| `budget_categories` | `id`, `budget_id`, `category_id`, `allocated_amount` | `schema/budgets.ts` |
| `bills` | `id`, `user_id`, `name`, `amount`, `frequency`, `due_date`, `deleted_at` | `schema/bills.ts` |
| `bill_payments` | `id`, `bill_id`, `amount`, `paid_at` | `schema/bills.ts` |
| `goals` | `id`, `user_id`, `name`, `target_amount`, `current_amount`, `deadline`, `deleted_at` | `schema/goals.ts` |
| `notifications` | `id`, `user_id`, `type` (enum), `title`, `body`, `is_read` | `schema/extensions.ts` |
| `audit_logs` | `id`, `user_id`, `action`, `resource`, `resource_id`, `old_values`, `new_values` | `schema/extensions.ts` |
| `idempotency_keys` | `key` (UNIQUE), `user_id`, `created_at` | `schema/transactions.ts` (via UNIQUE constraint) |

Relations: `wallets` → `users`; `transactions` → `users`, `wallets`, `categories`, `goals`; `budget_categories` → `budgets`, `categories`; `bill_payments` → `bills`

---

## Business Logic

| Rule | Where |
|------|-------|
| Firebase ID token → JWT session cookie (14-day TTL) | `apps/api/src/services/auth-service.ts` |
| JWT sign/verify with secret rotation | `apps/api/src/lib/jwt.ts:signAccessToken`, `verifyToken` |
| All money stored as DECIMAL(15,2), transported as strings, computed with Decimal.js | `apps/api/src/services/*`, `packages/api-client/src/presenters/currencyPresenter.ts` |
| Idempotency: UNIQUE `idempotency_key` on transactions; duplicate → 409 | `apps/api/src/services/idempotency.ts`, `apps/api/src/index.ts:onError` |
| Soft delete: `deleted_at` timestamp on wallets, bills, goals; queries filter `isNull(deletedAt)` | `packages/db/src/repositories/*.ts` |
| Transactions are immutable (no UPDATE, only soft-delete) | `apps/api/src/services/transaction-service.ts` |
| OCC: wallet balance uses `version` column + rowCount check to prevent double-spend | `apps/api/src/services/wallet-service.ts` |
| Budget spent = SQL-aggregated SUM of transactions within period (no N+1) | `apps/api/src/services/budget-service.ts:getBudgets` |
| Safe-to-Spend engine: monthly budget − committed expenses − emergency buffer | `apps/web/src/_lib/utils/finance.ts` |
| AI Quick Add: NLP text → Gemini parseAsync → `{amount, category, date}` (fallback: regex) | `apps/api/src/services/adapters/gemini-nlp-adapter.ts:parseAsync`, `nlp-adapter.ts` |
| Auto-seed default categories on first login | `apps/api/src/services/category-service.ts` |
| AI auto-creates categories/wallets when no match exists | `apps/api/src/services/ai-service.ts:resolveOrCreateCategory` |
| Recurring bill processing: query due bills → insert payment + ledger transaction | `apps/worker/src/index.ts` |
| Bill contribute / goal contribute: wrapped in `db.transaction()` for atomic insert | `apps/api/src/services/bill-service.ts`, `goal-service.ts` |
| Rate limiting: 100 req/min global, 30 req/min auth, 10 req/min quick-add | `apps/api/src/middleware/rate-limit.ts` |
| Audit logging: all non-GET mutations written to `audit_logs` | `apps/api/src/middleware/audit.ts` |
| Onboarding: 4-step wizard (profile → wallet → budget → first tx); gates dashboard | `apps/web/src/components/onboarding/`, `apps/api/src/routes/user.ts:/onboarding` |
| AuthGuard: redirects unauthenticated users to `/login` | `apps/web/src/app/(dashboard)/layout.tsx`, `components/ErrorBoundary.tsx` |
| TanStack Query cache invalidation after mutations | `apps/web/src/_lib/hooks/finance.tsx` |
