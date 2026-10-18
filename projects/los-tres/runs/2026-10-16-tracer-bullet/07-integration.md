REPORT 2026-10-16-tracer-bullet/07
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd C:\projects\investments\los-tres && npm run gate; then npm run stack:down
  result:    PASS
  detail:    gate exit 0: eslint clean, tsc clean; vitest 5 files / 30 tests passed, 0 failed, 0 skipped; image build with next build typecheck ok; playwright 7 passed, 0 failed, 0 skipped (chromium, 7 workers, APP_PORT=3010). stack:down removed app, db, umami; db-data volume kept. Anchor: see § Anchors used.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - no change request raised; nothing blocks close. Close docs may apply the pack_corrections of 02, 03, 04 and 05.
  - close docs: 05-test pack_correction 2 (vitest.config.ts and playwright.config.ts must not import from tests/) is the rule that makes Open risk 1 safe; it must land in testing.md, see § Rulings on the two Open risks.
  - Open row to add (SHOULD_FIX, backend then test): Vite 'configLoader: native' warning on every Vitest run; decide package.json "type" together with the slice B module-system call, see § Rulings on the two Open risks.
  - Open row to add (SHOULD_FIX, test, slice B): scripts/init-env.mjs (no overwrite, exit 1, secrets filled, DATABASE_URL derived) and the entrypoint exit 64 have no test; init-env is where guardrail 5 secrets are made.
  - Open row to add (SHOULD_FIX, test, slice B): the TD-10 scraping-library lint ban has no regression test; I confirmed it fires on 'cheerio' in src/ and 'playwright' in scripts/ by piping a probe through eslint --stdin, nothing written.
  - Open row to add (SHOULD_FIX, test): the e2e base-URL rule is written twice, playwright.config.ts and tests/support/env.ts appBaseUrl(), by design of the coupling; slice B may read baseURL from the Playwright fixture and drop one copy.
  - slice B first task stays as 02 § Cut line says: migrate path and drizzle-kit are unproven; nothing in A exercises a table.

skill_calls:
  - none

risks:
  - Gate image build reused cached deps layers, so the Docker `npm ci` path was not re-exercised in this run; lane 03 and 05 ran it cold and nothing in package-lock.json changed since.
  - The gate was run against APP_PORT=3010 from the local .env because host port 3000 belongs to another project; the design's 3000 URL itself was not exercised. Compose and the tests read the port from one variable, so the risk is low.
  - Skill-call fidelity: all four lane reports say skill_calls none and none of them names a skill or precedent in risks; no contradiction found.
  - Pack-correction bullets in 03, 04 and 05 exceed the advisory length (05 item 1 is 847 chars); close docs applies them as text, so this is a readability matter only.
  - The Spanish copy in messages/es-ES.json is the frontend lane's own wording (Open row, CARRIED); Umami default login and the dev-only npm audit findings also stay CARRIED, unchanged by this review.
  - Guardrails 1, 3 and 4 have no seam in slice A (no tables, no admin route, no money), so the pass for them is "nothing to violate"; the route classification test is the only check, and it is a convention check not a role check.

## Orchestrator brief
- Verdict PASS, status DONE, no CR files. `npm run gate` run by me: exit 0, vitest 30/30, playwright 7/7, lint and tsc clean. Stack taken down.
- Open risk 05-test 1 (tsconfig includes root configs, .dockerignore drops tests/): ruling no action. The gate rebuilds the image so a break is loud; close docs must land testing.md rule from 05 pack_correction 2.
- Open risk 05-test 2 (Vite ESM warning): ruling SHOULD_FIX, not blocking. Warning only; decide package.json "type" with the slice B module-system call (drizzle-kit, CLI entry).
- Contract C-1..C-8 and C-10 match code field by field; C-9 (no schema) holds. No undeclared deviation from the design.
- Guardrails 2 and 5 verified in code and by probe; 1, 3, 4 have no seam in A.
- Add 3 further SHOULD_FIX Open rows from handoff (init-env and entrypoint untested; lint ban untested; base URL rule twice).
- Close docs and protocol-lint are the remaining phases; review is skipped (no story).
- Sections below: Gate run · Anchors used · Contract alignment · Design adherence · Reuse and seams · Guardrails by seam · Rulings on the two Open risks · Coverage adequacy.

## Gate run

`npm run gate` = lint, typecheck, db:up, test, stack:up, test:e2e, run by me on the branch 4-tracer-bullet-slice-a with a clean tree. Results, in order:

- `eslint .` printed nothing, exit 0. `tsc --noEmit` printed nothing, exit 0.
- `docker compose up -d --wait db` healthy; `vitest run`: Test Files 5 passed (5), Tests 30 passed (30), Duration 1.02s. Three Vite configLoader warnings printed (see ruling 2).
- `docker compose up -d --build --wait`: image built (next build ran TypeScript in the image, routes `/`, `/_not-found`, `/api/health`, all dynamic), app, db and umami reached Healthy.
- `playwright test`: 7 passed (1.2s). Afterwards `curl -I` on `/` showed 200, no Set-Cookie, no X-Powered-By; `docker compose ps` showed all three ports on 127.0.0.1 and healthy; app log held only the Next.js start banner.
- `npm run stack:down` removed the three containers and the network. `git status` clean afterwards.

## Anchors used

External anchors, not the design document alone: the real PostgreSQL 17 container and the real Umami image answered; a real chromium browser asserted no cookie and no foreign origin; the HTTP response headers came from `curl -I`; eslint was probed with a banned import through `--stdin`. The C-1..C-10 comparison below is a consistency check against 02-design and is labelled as one.

## Contract alignment

Consistency check against 02-design § Contract, field by field:

- C-1: `.env.example` lists the ten names in the design order with the design defaults; secrets blank; `scripts/init-env.mjs` fills DB_PASSWORD and UMAMI_APP_SECRET and derives DATABASE_URL; `compose.yaml` and `tests/support/env.ts` use the same names. Match.
- C-2: three services, `name: los-tres`, all ports `127.0.0.1:`, postgres:17-alpine, Umami pinned `postgresql-v2.20.2`, entrypoint verb `server`, unknown verb exit 64, non-root `node`. Match.
- C-3: `getSiteName` and `getDatabaseUrl` read per call, throw exactly `SITE_NAME is not set` and `DATABASE_URL is not set`, import `server-only`. Match. `readRequiredEnv` is an extra export, declared in 03.
- C-4: `getDb()` lazy and cached, `closeDb()` clears; importing opens nothing (next build ran with no database). Match; the idle-error listener is a declared judgment.
- C-5/C-6: health route under `(public)`, 200/503 bodies exact, `no-store`, 2 s bound, code-only log. Match; the integration test and e2e assert the same bytes.
- C-7/C-8: one `<h1>`, one `<main>`, one `<p>`, `lang="es-ES"`, title with site name, the seven message keys present, `{siteName}` in `Metadata.title` and `Home.heading`, no code name under `src/` or `messages/`. Match.
- C-9: no table anywhere. C-10: `testDatabaseUrl`, `appBaseUrl`, `loadEnv`, `assertTestDatabase`, global setup that names host and port and never the URL. Match.
- Client and server types: no frontend consumer of a backend type exists in A; the page and layout take only `getSiteName(): string`, and the header takes it as a prop. No nullability mismatch is possible.

## Design adherence

- Fences held: lane 03 left only the two declared stubs, lane 04 overwrote both, lane 05 touched only tests, the two test configs and the declared scripts, lane 06 touched only CLAUDE.md § Commands. `git status` clean, 45 files in the branch.
- Declared deviations, none wrong: `src/app/admin/` not created (git tracks no empty directory; the classification test covers it); TypeScript pinned 5.9; ESLint 9; `env:init` exits 1 when `.env` exists.
- One undeclared minor difference: the design allowed a `tests/**` override block in `eslint.config.mjs` and none was added. Lint passes without it, so nothing is wrong.
- CLAUDE.md § Commands matches `package.json` scripts one for one and states the Docker, port and chromium prerequisites. The gate exists and I ran it, so architecture.md check 1 passes.

## Reuse and seams

- Nothing existed to reuse. No second copy of any seam exists: one config reader module, one DB client, one health route, one route classifier (`tests/support/routes.ts`, used by one test). Visibility, importer, matching, money, role check and click log are all deferred to B per 02 § Seams.
- Only duplicate: the base-URL rule in `playwright.config.ts` and `tests/support/env.ts`, forced by the tsconfig coupling and declared in 05 contract_notes. Recorded as a SHOULD_FIX Open row.

## Guardrails by seam

- Guardrail 1 (admin decides): no table, no offer, no query. Nothing to violate.
- Guardrail 2 (no scraping): `no-restricted-imports` ban for `src/**` and `scripts/**` present; probe confirmed it fires for `cheerio` and `playwright`. No code fetches a shop page; the only outbound traffic is the Docker image pulls and the healthcheck to localhost.
- Guardrail 3 (roles on the server): no admin route exists; classification by directory with a unit test. Convention only, as designed.
- Guardrail 4 (money): no amount anywhere.
- Guardrail 5 (RGPD): no cookie on `/`, `/api/health` or the 404 (raw response and a real browser, `context.cookies()` empty, no foreign origin); next-intl middleware and routing are absent; `poweredByHeader` off; health logs the error code only; `.env` is untracked, `.env.example` has blank secrets, `.dockerignore` keeps `.env` out of the image, `init-env` writes mode 0600 and prints no secret; grep of tracked files for long hex strings found none. Umami tracker is not embedded.

## Rulings on the two Open risks

1. **05-test risk 1, tsconfig includes `**/*.ts`, `.dockerignore` drops `tests/`: no action.** Evidence: the image build ran `next build` with TypeScript in the gate and passed with `vitest.config.ts` and `playwright.config.ts` present and `tests/` absent. The failure mode (a root config importing `tests/`) is loud, because `npm run gate` rebuilds the image, and the lane already fixed its instance. Narrowing tsconfig would stop `npm run typecheck` checking the tests, which costs more. The rule belongs in testing.md, and 05 pack_correction 2 carries it; close docs must apply it.
2. **05-test risk 2, Vite 'configLoader: native' ESM warning: SHOULD_FIX, not blocking.** Evidence: three identical warnings per Vitest run on `vitest.config.ts:1:1` (ESM syntax in a CommonJS package). Nothing fails and Vite names it as a future default, so today's gate is sound. Do not patch it ad hoc: `"type": "module"` changes the module system of the whole repo, and `vitest.config.ts` uses `__dirname`. Settle it with the slice B backend lane, where `src/cli` entry points and drizzle-kit force the same question. Owner of the fix: backend (package.json) with test (vitest.config.ts).

## Coverage adequacy

- Tests assert the contract, not the implementation: exact C-6 bodies in both integration and e2e, per-call env reads by changing the variable between calls, error text free of sentinel secrets, raw server HTML parsed with JavaScript off, cookies and off-origin requests in a real browser, 404 in Spanish, code-name absence by file scan. Each would fail if its rule broke.
- Honest gaps, all named as SHOULD_FIX rows in handoff: `init-env.mjs`, entrypoint exit 64, lint-ban regression. None is a guardrail seam that exists in A at runtime.
- `home.spec.ts` takes the expected site name from `.env`, so it fails if `.env` is edited without `docker compose up -d`; that is the intended signal and is documented.
