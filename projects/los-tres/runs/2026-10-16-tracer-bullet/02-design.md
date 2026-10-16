REPORT 2026-10-16-tracer-bullet/02
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only design order, no command named

contract_notes:
  - CLAUDE.md § Commands needs the nine commands in § Commands below before integration runs; architecture.md makes an empty list BLOCKING, so a build-phase docs order precedes integration (budget 7 -> 8).
  - 01-product § Slice boundary put migration, seed, importer and product page in this slice; they move to slice B. Acceptance "docker compose up from a fresh clone" now needs `npm run env:init` first (guardrail 5), see § Cut line.
  - `.env.example`, `compose.yaml` and `tests/support/env.ts` must carry the same variable names, see § Contract C-1.
  - `src/config/site.ts` getSiteName() is consumed by the frontend page and metadata; signature in § Contract C-3.
  - GET /api/health body and statuses are consumed by the Compose healthcheck and by tests; shape in § Contract C-6.
  - messages/es-ES.json key names are consumed by tests/unit/messages.test.ts and e2e; keys fixed in § Contract C-8.
  - run.md `plan` and `budget` lines lag: slice A is 4 build dispatches (backend, frontend, test, docs) not 3.

pack_corrections:
  - backend.md — § Before the stack is recorded, § Layout and guardrail (5) "no value" are stale; exact replacement wording in § Pack corrections owed (backend.md).
  - frontend.md — § Before the stack is recorded and § Layout are stale, and the i18n and cookie conventions are unset; exact replacement wording in § Pack corrections owed (frontend.md).
  - testing.md — § Running tests reads "Not yet established"; runner, projects, DB and e2e reach are now fixed; exact replacement wording in § Pack corrections owed (testing.md).

handoff:
  - dispatch is blocked on owner answers O-1 (package manager) and O-2 (Node major); recommended npm and Node 22, plan is written to those, see § Owner questions
  - test lane dispatch is blocked on O-3 (test database); recommended: second database on the existing db service, see § Owner questions
  - dispatch order: 03 backend, 04 frontend, 05 test, 06 docs (CLAUDE.md § Commands only), then integration, then close docs; file fences in § Lane split
  - backend verification command is `npm run lint && npm run typecheck && npm run build && docker compose up -d --build --wait`, then `curl` of /api/health, see § Lane split
  - test and integration verification command is `npm run gate`, see § Commands
  - slice B starts from the preconditions A leaves and the inputs listed in § Cut line (B inputs)

skill_calls:
  - none

risks:
  - Tool and image versions (Next, next-intl, Vitest, Playwright, Umami tag) were not verified from this session; engineers pin what they install and record versions in pack_corrections. Postgres is fixed at major 17 here.
  - Drizzle migration tooling (drizzle-kit, migrate in the image) is unproven until slice B because A creates no table; the cost of keeping the schema out of A. B's first task is the migrate path.
  - Umami ships with a well-known default admin login. Loopback-only publish makes it safe locally; the VPS slice must change it and must not publish the port.
  - `docker/db-init` runs only on an empty db volume, so an existing volume lacks the `umami` database; recovery is `docker compose down -v`. Acceptable pre-launch.
  - The owner is on Windows: a CRLF checkout of docker-entrypoint.sh breaks the container. `.gitattributes` forcing LF on *.sh is part of backend scope.
  - `npm run gate` builds the image and runs the e2e against Compose on every run, so it takes minutes. Deliberate: the Compose path is this slice's whole risk.
  - Guardrail 5 trap: next-intl middleware or i18n routing sets a NEXT_LOCALE cookie. Decision TD-4 forbids both; the e2e no-Set-Cookie test is the proof.
  - Scope note for the producer: 01-product's three-line "fresh clone, docker compose up" acceptance gains one command (`npm run env:init`); no secret may be committed, so a default password was rejected.
  - No guardrail is touched by a seam in A except 5 (no cookie, no PII in logs) and 2 (lint ban on HTML scraping libraries). Guardrails 1, 3 and 4 have no seam in A; their tests wait for B or the admin slice.

## Orchestrator brief
- Cut: slice A = skeleton + Compose (app, db, umami) + gate + one SSR page `/` + `/api/health`. NO tables. Migration and seed go to B: their only consumers (importer, visibility scope, product page) are in B.
- Decisions: one Next.js app at repo root; npm; Node 22; messages/es-ES.json; SITE_NAME env read at request time in src/config/site.ts; no next-intl middleware (cookie).
- Decisions: Vitest `unit` + `integration` projects; integration uses a second database `<DB_NAME>_test` on the same `db` service; Playwright targets the Compose app, no webServer.
- Decisions: secrets are never committed; `npm run env:init` generates .env; .env.example has blank secrets and local defaults for the rest.
- BLOCKS DISPATCH: O-1 package manager, O-2 Node major (recommend npm, 22), O-3 test database (recommend same db service). Owner answers needed before 03 backend (O-1, O-2) and 05 test (O-3).
- Lane split: 03 backend -> 04 frontend -> 05 test -> 06 docs (CLAUDE.md § Commands only, before integration) -> integration -> close docs. Budget 7 -> 8.
- Sections: Owner questions · Cut line (A, B, B inputs, acceptance) · Layout · Commands · Contract (C-1..C-10) · Decisions (TD-1..) · Seams · Lane split · Pack corrections owed · reuse is "none exists", stated in Seams.
- Frontend lane is real but thin (layout, page, i18n, 404, CSS). Backend writes stub layout/page only so `docker compose up` is verifiable; frontend overwrites them.

## Owner questions

Stack-adjacent choices the recorded stack does not settle. No lane decides these (`project.md` § Building before the stack exists). The plan is written to the recommendation; if the owner answers otherwise only the named lines change.

- **O-1. Package manager.** Not in CLAUDE.md § Stack. Recommend **npm**: it ships with Node, the owner's machine has npm 11.12 and no pnpm, and Dockerfile uses `npm ci`. Lockfile `package-lock.json`. If pnpm: every `npm run` below is `pnpm`, the Dockerfile install line and the lockfile change.
- **O-2. Node major.** Not in CLAUDE.md § Stack. Recommend **22** (the owner's machine runs v22.20.0, so host tests and the container run the same major). Pinned in `.nvmrc`, `package.json` `engines`, and the Dockerfile base image. If 24: those three lines.
- **O-3. Test database.** The order allows raising a test-only Compose service but not adding one. Recommend **no new service**: Vitest global setup creates a second database `<DB_NAME>_test` on the existing `db` service and runs only against it. The alternative (a `db-test` service) means a fourth service in Compose and a second port.
- **O-4. Styling system for the UI (non-blocking for A).** Not in the stack. Slice A uses one plain `src/app/globals.css` with CSS custom properties and adds no dependency. The owner may want to choose Tailwind or CSS Modules before slice B grows the UI; not needed to build A.

## Cut line

**Slice A (this run) contains:**
1. Repo skeleton at the repo root: Next.js App Router, TypeScript strict, ESLint flat config, npm scripts (§ Commands).
2. Configuration: `SITE_NAME` read at request time; the whole env contract (C-1); `.env.example`; `npm run env:init` that generates `.env` (no secret in git).
3. Spanish copy path: next-intl without routing, `messages/es-ES.json`, one `<html lang="es-ES">`.
4. The database path, with no table: `pg` + Drizzle client, created lazily, proven by `GET /api/health` and by an integration test on a real PostgreSQL.
5. `Dockerfile` (multi-stage, standalone output, non-root), an entrypoint dispatcher that knows one verb (`server`), and `compose.yaml` with exactly `app`, `db`, `umami`.
6. One server-rendered page `/` (site name, one-line tagline, no listing) and a Spanish 404.
7. The gate: ESLint (with the guardrail 2 import ban), `tsc --noEmit`, Vitest `unit` + `integration`, Playwright against the Compose app, and `npm run gate`.
8. Tests listed in § Lane split lane 3. `CLAUDE.md` § Commands filled by a build-phase docs order.

**Moves to slice B (next run), not planned here:** first Drizzle migration and every table; seed and `SEED_DEMO_DATA` (D-1 Q2); `drizzle-kit`; entrypoint verbs `migrate`, `seed`, `import-feeds` and the CLI that backs them; importer and EAN matching; money helper; the visibility scope; the product page and its route; guardrail 1, 2 (runtime), 4 tests; the product e2e flow.

**First migration and seed belong in B.** The one reason: a schema has no reader or writer in A, so its columns would be guessed and rewritten once the importer, the visibility scope and the product page (all slice B) shape them, whereas A proves the database path with a connectivity test that needs no table.

**B inputs already recorded (not B's design):** guardrail 1 states must be explicit columns (feed approved, product hidden, offer hidden), money as `*_cents` integer (0002), EAN and part number stored raw and normalised (0002), a feed source type `affiliate_network | shop_upload` (0007), the D-1 rulings Q1 to Q5 and Q7. 01-product `contract_notes` 2 (states beyond the six nouns) is B's design pass to settle.

**Preconditions A leaves for B:** `src/db/client.ts`; test database creation in Vitest global setup (B adds "run migrations on it"); the entrypoint dispatcher (B adds verbs); `docker/db-init`; the route classification convention (TD-6).

**Acceptance of slice A, observable:**
- On a fresh clone: `npm ci`, `npm run env:init`, `docker compose up -d --build --wait` leaves `app`, `db`, `umami` running and `app` healthy, with no account and no network access to any shop.
- `GET http://127.0.0.1:3000/` returns 200 HTML (view-source shows it, no JS needed) with one `<h1>` equal to `SITE_NAME`, `lang="es-ES"`, and no `Set-Cookie`.
- Changing `SITE_NAME` in `.env` and `docker compose up -d` (no `--build`) changes the `<h1>`.
- `GET /api/health` returns 200 `{status:"ok",db:"up"}`; with `db` stopped it returns 503 `{status:"degraded",db:"down"}`.
- Umami answers on `http://127.0.0.1:3001/`.
- `npm run gate` exits 0.

## Layout

All inside the recorded stack. Names are given once; every lane uses these.

- **Package manager:** npm (O-1). **Node:** 22 (O-2). One `package.json` at the repo root, no workspaces.
- **Es-ES messages:** `messages/es-ES.json` (one namespaced file; keys in C-8). Wired from `src/i18n/request.ts`.
- **Site name:** environment variable `SITE_NAME`, read only by `src/config/site.ts` (`getSiteName()`). It is not in any message file or markup literal.
- **Locale:** fixed `es-ES`, constant in `src/i18n/locale.ts`. No locale in URLs.

```
.                          repo root = the Next.js app
  package.json  package-lock.json  .nvmrc  tsconfig.json  next.config.ts
  eslint.config.mjs  vitest.config.ts  playwright.config.ts
  Dockerfile  docker-entrypoint.sh  compose.yaml  .dockerignore
  .env.example  .gitattributes  .gitignore
  messages/es-ES.json
  public/                   (empty, .gitkeep; standalone image copies it)
  docker/db-init/01-umami.sql
  scripts/init-env.mjs      (the only plain-JS file)
  src/
    app/
      layout.tsx  globals.css  not-found.tsx
      (public)/             every PUBLIC page and route handler lives here
        page.tsx            /
        api/health/route.ts /api/health
      admin/                every ADMIN page and action lives here (empty in A and B)
    config/                 env.ts (generic readers), site.ts (getSiteName)
    db/                     client.ts (A); schema/, migrations/ arrive in B
    i18n/                   request.ts, locale.ts
    server/                 server-only domain code (B: visibility, money, importer, matching, auth)
    cli/                    command entry points (B: import-feeds)
    components/             React components (UI only, no DB imports)
  tests/
    unit/  integration/  e2e/  fixtures/  support/
```

Rules: `src/config`, `src/db`, `src/server`, `src/cli` import `server-only` (or are never imported from a `'use client'` file); `src/components` never imports from them. Tests live in `tests/`, never beside source, so the test lane's fence is one directory.

## Commands

Prerequisites on the host: Node 22, Docker with Compose, a free port 3000, 3001, 5433. First run on a fresh clone: `npm ci`, `npm run env:init`, `npm run test:e2e:install`.

| Purpose | Command | Needs |
|---|---|---|
| lint | `npm run lint` = `eslint .` | nothing |
| types | `npm run typecheck` = `tsc --noEmit` | nothing |
| unit tests | `npm run test:unit` = `vitest run --project unit` | nothing |
| integration tests | `npm run test:integration` = `vitest run --project integration` | `npm run db:up` |
| unit + integration | `npm test` = `vitest run` | `npm run db:up` |
| e2e | `npm run test:e2e` = `playwright test` | `npm run stack:up` |
| full gate | `npm run gate` | Docker running; runs everything above in order |

Helper scripts (also listed in CLAUDE.md § Commands): `npm run env:init` (create `.env` once, refuses to overwrite), `npm run db:up` = `docker compose up -d --wait db`, `npm run stack:up` = `docker compose up -d --build --wait`, `npm run stack:down` = `docker compose down`, `npm run test:e2e:install` = `playwright install chromium`, `npm run dev`, `npm run build`.

`npm run gate` is exactly: `npm run lint && npm run typecheck && npm run db:up && npm test && npm run stack:up && npm run test:e2e`. No shell-specific syntax (the owner runs Windows; `npm run` uses cmd).

**How the runners reach the services**

| Runner | PostgreSQL | The app |
|---|---|---|
| Vitest `unit` | none | imports modules directly; no network |
| Vitest `integration` | host to `127.0.0.1:${DB_HOST_PORT}`, database `${DB_NAME}_test`, URL derived from `DATABASE_URL` by `tests/support/env.ts` | imports the route handler and calls it as a function; no HTTP |
| Playwright | none directly | HTTP to the Compose `app` at `E2E_BASE_URL`, default `http://127.0.0.1:${APP_PORT}`; Umami at `${UMAMI_PORT}`. No `webServer` block: the Compose stack is the server under test |

Vitest and Playwright load `.env` with `process.loadEnvFile('.env')` when the file exists (Node 22, no dotenv dependency). Vitest config: `test.projects` with `unit` (`tests/unit/**/*.test.ts`) and `integration` (`tests/integration/**/*.test.ts`, `fileParallelism: false`, `globalSetup: tests/support/global-setup.ts`, `env.DATABASE_URL` set to the test URL, `server-only` aliased to an empty stub in `tests/support/server-only-stub.ts`). Playwright: chromium only, `testDir: tests/e2e`.

## Contract

Everything slice A creates that another lane consumes. A has no schema (see § Cut line).

**C-1. Environment variables** (`.env.example` lists exactly these, in this order, with these defaults; secrets blank)

| Name | Secret | `.env.example` value | Read by |
|---|---|---|---|
| `SITE_NAME` | no | `Los Tres` | `compose.yaml` (to `app`), `npm run dev`, `src/config/site.ts`, e2e |
| `APP_PORT` | no | `3000` | `compose.yaml` host publish, Playwright baseURL |
| `DB_USER` | no | `lostres` | `compose.yaml` (db, app, umami), `env:init` |
| `DB_PASSWORD` | yes | blank | `compose.yaml`; generated by `env:init` |
| `DB_NAME` | no | `lostres` | `compose.yaml` (`POSTGRES_DB`), `env:init` |
| `DB_HOST_PORT` | no | `5433` | `compose.yaml` host publish, `env:init` |
| `DATABASE_URL` | yes (holds the password) | blank | host-side only: `npm run dev`, `src/db/client.ts`, Vitest, B's drizzle-kit. `env:init` derives `postgres://DB_USER:DB_PASSWORD@127.0.0.1:DB_HOST_PORT/DB_NAME`. Inside Compose the `app` service gets its own value pointing at host `db`, port 5432 |
| `UMAMI_APP_SECRET` | yes | blank | `compose.yaml` (umami) |
| `UMAMI_PORT` | no | `3001` | `compose.yaml` host publish, e2e |
| `E2E_BASE_URL` | no | blank (means `http://127.0.0.1:${APP_PORT}`) | Playwright only |

`NEXT_PUBLIC_*` variables are not used. The test database name is always `${DB_NAME}_test`, derived, with no variable of its own. `compose.yaml` uses `${DB_PASSWORD:?run npm run env:init}`-style required interpolation for `DB_PASSWORD`, `UMAMI_APP_SECRET`, `SITE_NAME`, and plain `${VAR:-default}` for ports, user and name. `env:init` writes `.env` with the `wx` flag (never overwrites), fills each blank secret with `crypto.randomBytes(24).toString('hex')`, derives `DATABASE_URL`, and prints no secret.

**C-2. Compose** (`compose.yaml`, top-level `name: los-tres`; these three services and no other)

| Service | Image / build | Host port (always `127.0.0.1:`) | Container port | Notes |
|---|---|---|---|---|
| `app` | build `.` (Dockerfile) | `${APP_PORT:-3000}` | 3000 | env: `SITE_NAME`, `DATABASE_URL` (to `db:5432`), `PORT=3000`, `HOSTNAME=0.0.0.0`, `NODE_ENV=production`. `depends_on: db: service_healthy`. Healthcheck `wget -qO- http://127.0.0.1:3000/api/health` |
| `db` | `postgres:17-alpine` | `${DB_HOST_PORT:-5433}` | 5432 | named volume `db-data` at `/var/lib/postgresql/data`; `POSTGRES_USER/PASSWORD/DB` from `DB_*`; healthcheck `pg_isready`; `docker/db-init` mounted read-only at `/docker-entrypoint-initdb.d` |
| `umami` | official Umami image, tag pinned by the engineer to a verified current release | `${UMAMI_PORT:-3001}` | 3000 | own database `umami` on `db`; `DATABASE_URL` to it; `APP_SECRET=${UMAMI_APP_SECRET}`; `depends_on: db: service_healthy`; tracker is not embedded anywhere (D-1 Q7) |

`docker/db-init/01-umami.sql` is the single statement `CREATE DATABASE umami;`. No other published port. `app` image entrypoint is `./docker-entrypoint.sh`, default command `server`; an unknown verb exits 64 with a usage line. The image runs as the non-root `node` user.

**C-3. Config module** — `src/config/env.ts` and `src/config/site.ts`
- `getSiteName(): string` reads `process.env.SITE_NAME` on every call (never at module load), trims it, and throws `Error("SITE_NAME is not set")` when missing or blank. Returns a non-empty string. The error text never includes other environment values.
- `getDatabaseUrl(): string` reads `process.env.DATABASE_URL` on every call; throws `Error("DATABASE_URL is not set")` when missing or blank. Both are server-only.

**C-4. Database client** — `src/db/client.ts`
- `getDb()` returns a Drizzle instance (`drizzle-orm/node-postgres` over a `pg` Pool), created on first call from `getDatabaseUrl()` and cached. Importing the module opens no connection (so `next build` needs no database).
- `closeDb(): Promise<void>` ends the pool and clears the cache; tests call it in `afterAll`.
- Nothing logs the URL, the password or the driver error message.

**C-5. Route classification** — directory is the declaration. Public pages and handlers: `src/app/(public)/**`. Admin pages, handlers and server actions: `src/app/admin/**` (nothing there yet). Root files `layout.tsx`, `not-found.tsx`, `globals.css` are neither. No `page.tsx` or `route.ts` may sit anywhere else.

**C-6. `GET /api/health`** — file `src/app/(public)/api/health/route.ts`, `export const dynamic = 'force-dynamic'`, header `Cache-Control: no-store`, body `application/json`, no cookie.

| Case | Status | Body |
|---|---|---|
| database answers `select 1` | 200 | `{"status":"ok","db":"up"}` |
| any database error or timeout | 503 | `{"status":"degraded","db":"down"}` |

Exactly those two keys, both strings, always present. The 503 path logs only the error `code` string, never a message or URL. A bounded wait of 2 seconds on the check so an unreachable database cannot hang the Compose healthcheck.

**C-7. `GET /` rendered contract** (what tests may assert)
- 200, `text/html`, no `Set-Cookie` header, rendered on the server per request (raw HTML contains the `<h1>`).
- `<html lang="es-ES">`; exactly one `<h1>` whose text equals `getSiteName()`; one `<main>`; one `<p>` whose text equals `Home.tagline` from `messages/es-ES.json`; `<title>` contains the site name.
- No third-party script, no Umami tracker, no `<a>` pointing off-site.
- The page reads the site name at request time: `export const dynamic = 'force-dynamic'` on the page and layout chain so a changed `SITE_NAME` needs a container restart, not a rebuild.

**C-8. Message keys** — `messages/es-ES.json`, namespaced, ICU placeholders. Keys the tests rely on are fixed here; wording is the frontend lane's Spanish.

| Key | Placeholders | Used for |
|---|---|---|
| `Metadata.title` | `{siteName}` | `<title>` |
| `Metadata.description` | none | meta description |
| `Home.heading` | `{siteName}` | the `<h1>` |
| `Home.tagline` | none | the `<p>` |
| `NotFound.heading`, `NotFound.body`, `NotFound.backHome` | none | `not-found.tsx` |

The literal text "Los Tres" (any case) appears nowhere under `src/` or in `messages/`.

**C-9. Schema.** None. The only database objects in A are the databases `${DB_NAME}` (created by Postgres), `umami` (db-init) and `${DB_NAME}_test` (Vitest global setup). No table of ours exists until B.

**C-10. Test infrastructure** (consumed by lane 3 and, in B, by every integration test)
- `tests/support/env.ts` exports `loadEnv()`, `testDatabaseUrl()` (DATABASE_URL with the database name replaced by `${name}_test`) and `appBaseUrl()`.
- `tests/support/global-setup.ts` connects to the maintenance database `postgres` with the `.env` credentials, creates `${DB_NAME}_test` if missing, and on failure throws a message naming host and port and the fix (`npm run db:up`), never the URL.
- Any helper that mutates the database calls `assertTestDatabase()` first, which fails unless `current_database()` ends in `_test`.

## Decisions

- **TD-1. One app, root layout, `src/`, `tests/`.** Chosen so the test lane's fence is `tests/**` and the build lanes' fences are disjoint.
- **TD-2. Drizzle over `pg` (node-postgres).** The stack names Drizzle only; the driver is chosen here once so B does not choose again.
- **TD-3. Built as `output: 'standalone'`, runtime `HOSTNAME=0.0.0.0`.** The standalone server binds the container hostname otherwise and the healthcheck fails.
- **TD-4. No next-intl middleware, no i18n routing, no locale cookie.** Locale is the constant `es-ES` in `getRequestConfig`. This is the guardrail 5 line for this slice.
- **TD-5. Everything dynamic reads env at call time.** No `process.env` read at module load in `src/`, so one image serves any `SITE_NAME` and `next build` needs no database.
- **TD-6. Route classification by directory (C-5).** Gives guardrail 3 something checkable before the first admin route exists. A unit test enforces it.
- **TD-7. Secrets: generated, never committed.** `env:init` over a committed default password, because the same Compose runs on the VPS (0004) and a default password there is a published secret.
- **TD-8. Ports bind to 127.0.0.1 only.** The VPS exposes only a reverse proxy, later; nothing in A is reachable from another machine.
- **TD-9. Postgres 17.** Pinned major; the data mount path is `/var/lib/postgresql/data`.
- **TD-10. ESLint bans HTML-scraping libraries in `src/` and `scripts/`.** `no-restricted-imports` for `cheerio`, `jsdom`, `linkedom`, `parse5`, `node-html-parser`, `htmlparser2`, `puppeteer*`, `playwright*`. Guardrail 2 enforced by the gate, not by review. XML parsing for feeds is not on the list.
- **TD-11. Vitest integration files run serially** (`fileParallelism: false`) because they share one database.
- **TD-12. Playwright runs against Compose, not `next start`.** The Compose path is the slice's riskiest unknown; a gate that bypasses it proves nothing about it.
- **TD-13. Errors are generic outward.** Health, config and DB client never print a connection string, password or driver message.
- **TD-14. No Prettier, no CI file, no git hooks.** None is in the stack or the gate; the owner may add them later.
- **TD-15. Styling is one `globals.css` with CSS variables** until O-4 is answered.

## Seams

No code exists, so there is nothing to reuse and nothing to duplicate; the patterns set below are what B follows. "Touches" means A creates the module or the convention.

| Seam (architecture.md) | In A | Where it lives |
|---|---|---|
| Public visibility | deferred to B | `src/server/visibility.ts` (one scope, every public read calls it) |
| Feed ingestion | deferred to B | `src/server/importer/`, CLI `src/cli/import-feeds.ts`, entrypoint verb `import-feeds` |
| Matching | deferred to B | `src/server/matching.ts` |
| Role check | **convention only** | classification by directory (C-5): `src/app/(public)/**` public, `src/app/admin/**` admin. The check itself, `src/server/auth/`, waits for the first admin route |
| Money | deferred to B | `src/server/money.ts` (integer cents; the es-ES formatter takes cents) |
| Click log | deferred (later than B) | `src/app/(public)/go/[offer]/route.ts` |

Entry points in A, both public: `src/app/(public)/page.tsx` and `src/app/(public)/api/health/route.ts`. The database client `src/db/client.ts` and the config modules are infrastructure the later seams build on.

## Lane split

Order is fixed: backend, frontend, test, docs, then integration. Each lane's fence is a write fence; reading anything in the repo is allowed.

### 03 · backend (first)

Owns the skeleton, the delivery files, the config and the database path.

Fence (write):
`package.json`, `package-lock.json`, `.nvmrc`, `tsconfig.json`, `next.config.ts` (create), `eslint.config.mjs` (create, including TD-10), `Dockerfile`, `docker-entrypoint.sh`, `compose.yaml`, `.dockerignore`, `.gitattributes` (`*.sh text eol=lf`), `.gitignore` (append `.next/`, `next-env.d.ts`, `*.tsbuildinfo`, `playwright-report/`, `test-results/`), `.env.example`, `docker/**`, `scripts/**`, `public/.gitkeep`, `src/config/**`, `src/db/**`, `src/app/(public)/api/health/route.ts`, and two **stubs** it must write only so the image can build: `src/app/layout.tsx` and `src/app/(public)/page.tsx` (bare: layout wraps children in `<html lang="es-ES"><body>`; page renders one `<h1>` with `getSiteName()`; no i18n, no CSS). Lane 04 overwrites both.

Work:
1. Create the app and install dependencies: runtime `next`, `react`, `react-dom`, `next-intl`, `drizzle-orm`, `pg`, `server-only`; dev `typescript`, `@types/node`, `@types/react`, `@types/react-dom`, `@types/pg`, `eslint`, `eslint-config-next`. Pin `engines`. Lockfile committed. Do not install `vitest`, `@playwright/test` or `drizzle-kit`.
2. Scripts it owns in `package.json`: `dev`, `build`, `lint`, `typecheck`, `env:init`, `db:up`, `stack:up`, `stack:down`.
3. `src/config/*` and `src/db/client.ts` per C-3 and C-4; the health route per C-6.
4. `Dockerfile`, entrypoint, `compose.yaml`, `docker/db-init`, `.env.example`, `scripts/init-env.mjs` per C-1 and C-2.
5. Do not touch `src/app/(public)/` other than the files above, `messages/`, `src/i18n/`, or `tests/`.

Verification (all must pass): `npm ci && npm run lint && npm run typecheck && npm run build`, then `npm run env:init && docker compose up -d --build --wait`, then `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3000/api/health` prints 200 and the body matches C-6, then `docker compose stop db` makes it 503, then `docker compose down`. Report `changed`, `contract_notes` for every name in C-1 to C-6, and the pack_corrections in § Pack corrections owed.

### 04 · frontend (second)

Owns Spanish copy, the layout and the page.

Fence (write): `src/app/layout.tsx`, `src/app/globals.css`, `src/app/not-found.tsx`, `src/app/(public)/page.tsx` (overwrites the stubs), `src/i18n/**`, `messages/es-ES.json`, `src/components/**`, and in `next.config.ts` only the next-intl plugin wrapper (`createNextIntlPlugin('./src/i18n/request.ts')`). It adds no dependency.

Work: C-7 and C-8 exactly; `getRequestConfig` returns the fixed locale and the messages file (TD-4: no middleware, no `routing`); `generateMetadata` uses `Metadata.*`; page and layout export `dynamic = 'force-dynamic'`; `<main>` landmark, one skip-free simple header showing the site name via `getSiteName()` (not hard-coded); Spanish `not-found.tsx`; plain CSS only (TD-15). No `'use client'` unless needed. No import from `src/db` or `src/server`.

Verification: `npm run lint && npm run typecheck && npm run build`, then `docker compose up -d --build --wait` and a `curl -s http://127.0.0.1:3000/` whose HTML contains the `<h1>`, `lang="es-ES"`, and no `Set-Cookie` (`curl -sI`). Then set a different `SITE_NAME` in `.env`, run `docker compose up -d` (no `--build`), and confirm the `<h1>` changed. Types of `getSiteName()` mirror C-3.

### 05 · test (third)

Owns every test file and the test infrastructure.

Fence (write): `tests/**`, `vitest.config.ts`, `playwright.config.ts`, in `package.json` only the `devDependencies` `vitest` and `@playwright/test` and the scripts `test`, `test:unit`, `test:integration`, `test:e2e`, `test:e2e:install`, `gate`, and in `eslint.config.mjs` only a `tests/**` override block. It does not edit `src/`.

Tests to write (each must fail if the rule it names broke):
- `tests/unit/site-config.test.ts`: `getSiteName()` returns the trimmed value; reads the env at each call (change it between calls); throws on unset and on blank; the thrown message does not contain other env values.
- `tests/unit/messages.test.ts`: every key in C-8 exists; `Home.heading` and `Metadata.title` contain `{siteName}`; no message and no file under `src/` contains "Los Tres" in any case.
- `tests/unit/route-classification.test.ts`: every `page.tsx` and `route.ts` under `src/app` is below `(public)` or `admin` (TD-6); the two A entry points are below `(public)`.
- `tests/integration/db-client.test.ts`: `getDb()` runs `select 1`; `current_database()` ends in `_test`; `closeDb()` then `getDb()` reconnects. `afterAll` closes.
- `tests/integration/health.test.ts`: the `GET` handler returns 200 and the exact C-6 body against the real test database; with `DATABASE_URL` pointing at an unused port it returns 503 and the exact degraded body within 5 seconds, and the response text contains neither the host nor a password.
- `tests/e2e/home.spec.ts`: raw HTML of `/` (Playwright `request`, no JS) has one `<h1>` equal to `SITE_NAME` from `.env`, `lang="es-ES"`, a `<p>` equal to `Home.tagline`; the response has no `set-cookie`; after a browser visit `context.cookies()` is empty; no request leaves the app origin.
- `tests/e2e/stack.spec.ts`: `/api/health` returns 200 and the C-6 body through Compose; Umami answers 200 at `UMAMI_PORT`; an unknown path returns 404 with the Spanish `NotFound.heading`.

Guardrail tests in A: guardrail 5 (no cookie) only. Guardrails 1, 2 (runtime), 3, 4 have no seam in A; the test pack's "owes the matching test" is satisfied by the seam table, and their tests are not written here.

Verification: `npm run gate` exits 0, with the counts reported verbatim. Also run `npm run test:unit` with the database stopped to confirm unit tests need no database.

### 06 · docs (fourth, build-phase order before integration)

Fence (write): `CLAUDE.md` § Commands only (replace "None yet" with the table and the helper list from § Commands above, prerequisites included). Not `docs/**` beyond that, not the packs. A separate close-phase docs order later applies `pack_corrections`.

### Integration (after 06) and close docs

Integration runs `npm run gate` and the checks in architecture.md § Integration review that apply to A (gate exists; guardrails 2 and 5; no second copy of anything yet). Close docs applies the pack corrections below.

## Pack corrections owed

Each lane emits these as `pack_corrections` when it lands the convention. Wording is the replacement text.

**backend.md**
- § Before the stack is recorded — replace the section body with: "The stack is recorded in `CLAUDE.md` § Stack. Report `BLOCKED` only if the tech-lead plan names no directory or file for what you are asked to build."
- § Layout — replace "*Not yet established.*" with: "One Next.js app at the repo root, npm, Node 22 (confirm O-1 and O-2 answers). Server-only code: `src/config` (env readers, `getSiteName`), `src/db` (`getDb()`, schema, migrations), `src/server` (visibility, money, importer, matching, auth), `src/cli`. Delivery files at the root: `Dockerfile`, `docker-entrypoint.sh` (verb dispatcher), `compose.yaml`, `docker/db-init`. Every public route is under `src/app/(public)/`, every admin route under `src/app/admin/`."
- § Guardrails (5) "add each new variable to `.env.example` with no value" — replace with: "add each new variable to `.env.example`: secrets blank and generated by `npm run env:init`, non-secret settings with their local default. Never read `process.env` at module load; read it in a function."
- § Guardrails — add: "Importing a `src/db` or `src/config` module must not open a connection or throw; `next build` runs with no database."
- § Layout — add: "Compose binds every published port to `127.0.0.1`. The `app` image runs `HOSTNAME=0.0.0.0`. `.gitattributes` keeps `*.sh` LF."

**frontend.md**
- § Before the stack is recorded — same replacement as backend.md's.
- § Layout — replace "*Not yet established.*" with: "UI under `src/app` (pages), `src/components`, `src/i18n`, `messages/es-ES.json`, `src/app/globals.css` (plain CSS with variables until the owner picks a styling system, O-4). Public pages under `src/app/(public)/`, admin under `src/app/admin/`. Never import `src/db` or `src/server` from a component."
- § Spanish market conventions — add: "next-intl runs without middleware and without i18n routing: locale is the constant `es-ES`, because next-intl's middleware sets a locale cookie (guardrail 5). Messages are namespaced in one file; the site name enters a message only as the `{siteName}` placeholder filled from `getSiteName()`. No literal site name anywhere in `src/` or `messages/`."
- § Spanish market conventions — add: "Pages that show configuration or data export `dynamic = 'force-dynamic'`; never read `SITE_NAME` or any env at module load."

**testing.md**
- § Running tests — replace "*Not yet established.*" with: "Vitest with two projects: `unit` (`tests/unit`) and `integration` (`tests/integration`, serial, real PostgreSQL, database `${DB_NAME}_test` on the Compose `db` service, created by `tests/support/global-setup.ts`, needs `npm run db:up`). Playwright in `tests/e2e`, chromium, against the Compose `app` at `E2E_BASE_URL` (default `http://127.0.0.1:${APP_PORT}`), needs `npm run stack:up`. `npm run gate` runs lint, tsc, tests and e2e in that order. Env comes from `.env` via `process.loadEnvFile`. Fixtures in `tests/fixtures`."
- § What must always be covered — add: "Any helper that writes to the database calls `assertTestDatabase()` first; a test must never run against the development database. No test calls a live network."
- § What must always be covered — add: "Every public response is asserted to have no `Set-Cookie`."
