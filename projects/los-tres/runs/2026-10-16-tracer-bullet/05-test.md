REPORT 2026-10-16-tracer-bullet/05
status:      DONE
verdict:     NONE

changed:
  - package.json, package-lock.json — devDependencies vitest ^5.0.5 and @playwright/test ^1.64.1; scripts test, test:unit, test:integration, test:e2e, test:e2e:install, gate
  - vitest.config.ts — projects unit and integration (serial, globalSetup, setupFiles), `@` and `server-only` aliases; imports nothing from tests/
  - playwright.config.ts — chromium only, testDir tests/e2e, no webServer, baseURL from E2E_BASE_URL or APP_PORT; imports nothing from tests/
  - tests/support/env.ts, global-setup.ts, test-database-env.ts, db.ts, routes.ts, server-only-stub.ts — C-10 helpers, assertTestDatabase, route walker
  - tests/unit/site-config.test.ts, messages.test.ts, route-classification.test.ts — config, C-8 keys and no code name, C-5 classification
  - tests/integration/db-client.test.ts, health.test.ts — select 1, _test database, reconnect; health 200 and 503 bodies, 5 s bound, no host or password leak
  - tests/e2e/home.spec.ts, stack.spec.ts — C-7 raw HTML, no cookie, no foreign origin; health, Umami (heartbeat and followed redirect), Spanish 404
  - tests/fixtures/.gitkeep — empty fixtures directory

verification:
  command:   npm ci && npm run test:e2e:install && npm run gate; docker compose stop db && npm run test:unit && docker compose start db; docker compose down
  result:    PASS
  detail:    gate exit 0: lint and tsc clean; vitest 5 files / 30 tests passed, 0 failed, 0 skipped (unit 3 files / 25, integration 2 files / 5); playwright 7 passed, 0 failed, 0 skipped. test:unit with db stopped: 3 files / 25 passed.

contract_notes:
  - tsconfig.json includes **/*.ts, so `next build` in the image typechecks root vitest.config.ts and playwright.config.ts; .dockerignore drops tests/, so those two configs must never import from tests/.
  - tests/support/env.ts appBaseUrl() and the baseURL block in playwright.config.ts hold the same rule twice (E2E_BASE_URL, else APP_PORT); change both together.
  - CLAUDE.md § Commands (lane 06) can list test, test:unit, test:integration, test:e2e, test:e2e:install and gate exactly as added to package.json.
  - Vitest 5.0.5 and Playwright 1.64.x are installed; the Playwright browser is chromium only, installed by `npm run test:e2e:install`.

pack_corrections:
  - testing.md — § Running tests: replace "*Not yet established.*" with "Vitest 5 with two projects in `vitest.config.ts`: `unit` (`tests/unit`, no database, no network) and `integration` (`tests/integration`, serial, real PostgreSQL, database `${DB_NAME}_test` on the Compose `db` service, created by `tests/support/global-setup.ts`, pointed at by `tests/support/test-database-env.ts`, needs `npm run db:up`). Playwright in `tests/e2e`, chromium only, against the Compose `app` at `E2E_BASE_URL` (default `http://127.0.0.1:${APP_PORT}`), no webServer, needs `npm run stack:up`. Commands: `npm run test:unit`, `test:integration`, `test` (both), `test:e2e`, `test:e2e:install`, and `npm run gate` = lint, tsc, db:up, test, stack:up, test:e2e. Env comes from `.env` via `process.loadEnvFile`. Helpers in `tests/support`, fixtures in `tests/fixtures`."
  - testing.md — § Running tests, add: "`vitest.config.ts` and `playwright.config.ts` must not import from `tests/`: tsconfig includes them, `next build` typechecks them in the image, and `.dockerignore` removes `tests/`. Put shared logic behind `setupFiles` or `globalSetup` instead."
  - testing.md — § What must always be covered, add: "Any helper that writes to the database calls `assertTestDatabase()` (`tests/support/db.ts`) first; a test never runs against the development database. No test calls a live network."
  - testing.md — § What must always be covered, add: "Every public response is asserted to have no `Set-Cookie`; a browser visit also asserts `context.cookies()` is empty and no request leaves the app origin."
  - testing.md — § Running tests, add: "Umami answers 307 at `/`. Assert 200 on `/api/heartbeat`, and on `/` only through a client that follows redirects. Host port 3000 may be taken, so the e2e base URL comes from the local `.env` `APP_PORT`, never a literal."
  - testing.md — § Running tests, add: "Expected site name and copy come from `SITE_NAME` in `.env` and `messages/es-ES.json`, never a literal. Raw server HTML is parsed by `page.setContent` in a context with `javaScriptEnabled: false`, not by an HTML parser dependency."

handoff:
  - fixtures and helpers in tests/support: loadEnv, withDatabaseName, testDatabaseUrl, appBaseUrl, umamiBaseUrl (env.ts); assertTestDatabase (db.ts); listRouteFiles and classifyRoute (routes.ts); server-only-stub.ts.
  - slice B integration tests: put migrations in tests/support/global-setup.ts after the CREATE DATABASE, and call assertTestDatabase() in any writing helper.
  - guardrail 5 (no Set-Cookie) is asserted on /, /api/health (e2e and integration) and the 404; guardrails 1 to 4 have no seam in slice A and no test.
  - not tested, by choice: scripts/init-env.mjs and the entrypoint exit code 64 on an unknown verb; the first needs filesystem isolation and the second a container run, neither cheap inside the fence.
  - integration tests need `npm run db:up` first; `npm run gate` does it, and global setup fails with host, port and "Run: npm run db:up" when the database is down.
  - the e2e stack stays up after `npm run gate`; the verification ended with `docker compose down`, the db-data volume remains.

skill_calls:
  - none

risks:
  - First gate run failed in the image build: root vitest.config.ts and playwright.config.ts imported ./tests/support/env, which .dockerignore removes, so `next build` failed typechecking. Fixed inside my fence by not importing from tests/; the underlying coupling (tsconfig includes, .dockerignore excludes) is the backend lane's files and is unchanged.
  - Vite prints a "configLoader native" warning for vitest.config.ts and tests/support/env.ts (ESM syntax in a CommonJS package). It is advisory and does not fail anything; a package.json "type": "module" is outside my fence.
  - `npm run gate` leaves the Compose stack running and rebuilds the image, so it takes minutes; this is the design's stated cost.
  - The home e2e reads SITE_NAME from the local .env, so it passes only when the running app was started with the same value; a .env edited without `docker compose up -d` fails it, which is the intended signal.
  - Host port 3000 is held by another project; the e2e ran against APP_PORT=3010 from the local .env, and I stopped no other container.
  - The 503 health integration test waits about 2 s for the bounded check, so the integration project is slower than its test count suggests.
  - npm audit reports 5 high findings, all in the dev-only lint chain (see 03-backend risks); the new devDependencies add none that I checked.
