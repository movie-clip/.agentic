# Capability pack: backend — project `datoro`

For the `backend-engineer` lane. Everything about `server/**` and
`prisma/**`. Where this contradicts general Express/Prisma instincts, this
file wins.

Companion sources: `datoro/CLAUDE.md`, `datoro/AGENTS.md` (house style — this
pack does not repeat its import/naming/error-handling conventions),
`docs/operations.md`.

---

## Index

Read this block first. You are not expected to read this file end to end — read
what your order touches. Reading one extra section is cheap; acting on a
convention you never read is not.

**Always read:** **Guardrails, in code terms** · **Reuse — do not re-derive these** · **Gotchas from `AGENTS.md`** · **Definition of done for this lane**

| Section | Read it when |
|---|---|
| Layout | you are adding a file, or looking for where one lives |
| Route conventions | your order adds or changes a route |

---

## Layout

```
server/
  routes/       one file per surface — see the full list below
  middleware/   auth.ts, errorHandler.ts, asyncHandler.ts
  services/     side effects and data access — the logic belongs here
  schemas/      request/response validation
  types/        server-side types
  server.ts     entrypoint
prisma/
  schema.prisma Prisma models — CONTRACT SOURCE OF TRUTH for persisted data
  migrations/   one migration per schema change — never hand-edit the schema
                and skip a migration
```

Existing routes, for finding prior art: `adminRoutes`, `analyticsRoutes`,
`authRoutes`, `feedback`, `healthRoutes`, `macro`, `marketPerformance`,
`newsRoutes`, `searchRoutes`, `subscription.routes`, `tickerRoutes`,
`watchlist`, `watchlistItems`, `watchlists`, `webhook.routes`.

Existing services, for finding prior art: `authService`, `batchDataService`,
`cacheService`, `cacheWarmService`, `databaseService` (the Prisma client),
`emailService`, `eurostatService`, `logger`, `monitoringService`,
`quoteTtlPolicyService`, `sentryService`, `stripeService`, `watchlistService`.

## Route conventions

Per `AGENTS.md` § "Backend Patterns":

- Route handlers wrap with `server/utils/asyncHandler.ts`.
- Validate input close to the edge using the existing Joi validation middleware
  where a route already follows that pattern.
- Normalize tickers to uppercase and trimmed values before cache or API
  operations.
- Keep caching/versioning behaviour intact when touching ticker or macro
  routes.
- Route files stay focused on HTTP concerns; side effects and data access
  belong in a service module.

The main data path is the batch ticker endpoint,
`/api/ticker-data/:ticker?mode=full` — batch extraction belongs in services
like `src/services/financials/batchChartService.ts` and
`batchTableService.ts` (frontend-side; the server-side counterpart is
`server/services/batchDataService.ts`). A request that sounds like "add a field
to the ticker response" almost always means editing this path, not adding a
new route.

## Reuse — do not re-derive these

- `server/services/databaseService.ts` — the Prisma client accessor. Do not
  instantiate `PrismaClient` a second time.
- `server/services/cacheService.ts` / `cacheWarmService.ts` — caching layer.
  Do not hand-roll a second cache for market data.
- `server/services/logger.ts` — structured logging with context metadata. Never
  `console.log` in this tree (guardrail 3).
- `server/middleware/errorHandler.ts` — centralized error handling; do not leak
  stack traces to clients from a route.
- `server/middleware/auth.ts` — `authenticate()` / the `requireAuth` pattern
  (guardrail 1).
- `server/services/stripeService.ts`'s `constructWebhookEvent` — the only
  entry point that should verify a Stripe webhook signature (guardrail 2). Do
  not parse a webhook body before it has passed through this.
- `healthIndicatorService.ts` (`src/services/health/`) for health scoring —
  `AGENTS.md` names this explicitly: do not invent parallel scoring logic.

## Guardrails, in code terms

**Auth.** Every route that touches a user's own data (watchlists, sessions,
subscription state) goes through `authenticate()`. A route added without it is
a `REFUSED`-worthy defect, not a style note.

**Webhook integrity.** `webhook.routes.ts` only ever acts on an event that
`constructWebhookEvent` returned. Adding a second path that reads the raw
request body for the same purpose bypasses the guardrail even if it never
touches signature verification directly.

**Logging.** No `console.log` added to `server/**`. Use `logger.ts`, and never
pass a token, JWT, card field, or email through it in plaintext.

**Prisma only.** A raw SQL query is a guardrail violation unless an existing,
documented exception already covers the case — check `databaseService.ts` and
neighbouring services for one before writing raw SQL, and report the
justification in `risks` if you find and reuse an existing exception.

**Boundary validation.** External data (FMP responses, webhook payloads,
request bodies) is validated — Zod or the existing Joi middleware — before it
is used. A field that is missing or malformed from FMP is surfaced as missing
to the caller, not defaulted to a plausible-looking value.

## Gotchas from `AGENTS.md`

These are documented drift, not folklore — read them before assuming CI or the
default script names are authoritative:

- **The lint script is `lint:check`, not `lint`.** `.github/workflows/ci.yml`
  runs the wrong one and is `continue-on-error`, so a red lint does not fail
  that workflow. Run `npm run lint:check` yourself.
- **CI Node versions disagree.** `ci.yml` uses Node 22, `pr-checks.yml` uses
  Node 18. Prefer code that works under both unless the repo standard has since
  been unified — check before assuming one is authoritative.
- **`vitest.config.js` references `./tests/setup.js`; the file on disk is
  `tests/setup.ts`.** If test bootstrap behaves unexpectedly, verify this
  mismatch first before assuming your change caused it.
- **E2E tests expect the backend already running** (`npm run server` or
  `server:dev`), against `http://localhost:7071` unless `TEST_API_URL`
  overrides it. A backend-lane order that also needs e2e evidence must say so
  in its `verification` field — starting a server is not implicit.

## Definition of done for this lane

- [ ] New/changed routes wrapped with `asyncHandler`, validated at the edge
- [ ] Auth applied to any route touching user-scoped data
- [ ] Webhook handling only acts on a signature-verified event
- [ ] No `console.log`, no raw SQL without a documented exception
- [ ] Schema change accompanied by a Prisma migration, not a hand-edited
      `schema.prisma` with no migration
- [ ] Reused an existing service instead of re-deriving cache/logging/auth/DB
      access
- [ ] `contract_notes` names any response shape or Prisma model change that
      now needs a matching frontend or docs update
- [ ] No test files touched — that is the test lane
