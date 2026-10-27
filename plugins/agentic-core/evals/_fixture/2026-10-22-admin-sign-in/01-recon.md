REPORT 2026-10-22-admin-sign-in/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only recon; the order's verification was NONE

contract_notes:
  - src/db/schema/index.ts:5-7 re-exports three schema files; a users/admin table needs a new file plus a line there, a generated migration 0003 and a _journal.json entry (src/db/migrations/meta/_journal.json:19-25).
  - messages/es-ES.json:92-93 (Privacy.adminsHeading / adminsBody) already tells visitors the admin area "usa una cookie de sesión"; the privacy page text is already written for a session cookie and may need a wording check against whatever S2.1 builds.
  - docker-entrypoint.sh:13-29 hard-codes the verb list (server|migrate|seed|import-feeds) in both the case arm and the usage text; a create-admin verb needs both edited, and the usage string at :26 is asserted by tests/e2e/entrypoint.spec.ts:22 (only the prefix `usage: docker-entrypoint.sh`).
  - tests/support/routes.ts:23-28 and tests/unit/route-classification.test.ts:42 already define `admin/` as the one top-level dir under src/app that classifies a route as admin; an admin route outside `src/app/admin/` or `src/app/(public)/` fails the unit test.

pack_corrections:
  - none

handoff:
  - see § Auth, session, role: nothing exists. Every admin-related item is greenfield except the route-classification convention and the Privacy copy.
  - see § CLI verb pattern: copy the shape of src/cli/seed.ts and src/cli/migrate.ts for a create-admin verb.
  - see § Schema and migrations: schema conventions to follow.
  - see § Root layout, middleware, headers, cookies: the single root layout wraps every route including a future src/app/admin.
  - see § Tests: existing guardrail-3/5 coverage, what is absent, and the Vitest/Playwright layout.

skill_calls:
  - none

risks:
  - agenticRoot resolves to C:\projects\investments\.agentic (outside the repo); PROTOCOL.md read there. I did not read capabilities/recon.md (the order did not name it and the Lane routing table gives scout no pack).
  - I did not open every file under src/server or every test; claims about "no X exists" rest on grep over src, tests, scripts, messages, docs for admin|session|cookie|password|TOTP|noindex|robots|middleware|proxy and on the file listings. A hit missed by the regex is possible.
  - Decision files 0003 and 0005 do not exist in docs/decisions (listing shows 0001,0002,0004,0006,0007,0008,0009,0010,0011); I did not establish whether the gap is intentional.
  - Decisions 0002/0004/0007/0008/0011 were listed but not read in full; 0004 admin mentions were found only by grep.
  - Whether Next 16.4.2 uses `proxy.ts` instead of `middleware.ts` was not verified from node_modules; no such file exists either way, and cookie/server-action API details were not verified.

## Orchestrator brief
- Admin/auth/session/cookie/role code: ABSENT. No src/app/admin, no users table, no middleware/proxy file, no hashing/auth dependency, no create-admin verb.
- Only admin scaffolding that exists: route classification (`admin/` vs `(public)/`) in tests/support/routes.ts:23-28, mvp.md § Admin area (:128-141), decision 0001 (:36-38), 0006 test promise (:35), 0009 session-cookie note (:34-35), and live Privacy copy (messages/es-ES.json:92-93).
- mvp.md:130-133 fixes: accounts for the three members created by a command, no sign-up, login = email + password + TOTP. The order says "email+password"; whether TOTP is in S2.1 is a scope question the code cannot settle.
- One root layout (src/app/layout.tsx) renders public SiteHeader + SiteFooter around ALL routes; there is no (public) layout, so src/app/admin/** inherits them unless restructured.
- "No cookie" is asserted broadly on public pages (set-cookie absent, empty context.cookies) in 8+ test files; an admin login sets a cookie, so those assertions must stay scoped to public routes.
- noindex exists only as a promise for demo products (mvp.md:178-179); no robots/noindex/headers code exists in src.
- Guardrail-3 test promised by 0006:35 ("admin routes reject anonymous requests") has NO test yet; only the route-classification unit test touches `admin`.
- CLI: verbs are src/cli/{migrate,seed,import-feeds}.ts via runCli (src/cli/shared.ts:8), compiled by tsconfig.cli.json, dispatched in docker-entrypoint.sh (exit 64 at :28); exit codes 0/1/2.
- Schema: 3 files plus index; 3 migrations; integration tests auto-iterate every exported table; DB reset truncates all public tables per test.
- Sections below: Auth, session, role; CLI verb pattern; Schema and migrations; Root layout, middleware, headers, cookies; i18n and messages; Logging and guardrail 5; Tests; Dependencies and config; Sources of truth; Open questions.

## Auth, session, role
- No auth, session, cookie-setting, password, hashing, TOTP or role code exists in src: grep for `admin|session|cookie|password|TOTP|noindex|robots|middleware|proxy` over src returns only comments, i18n copy, and DB password handling (src/config/env.ts:17, src/db/client.ts:23, src/app/(public)/api/health/route.ts:27).
- No `src/app/admin/` directory exists; the only app routes are under `(public)`: page.tsx, api/health, go/[offer], categoria/[slug], producto/[slug], aviso-legal, privacidad, como-nos-financiamos (file listing of src/app); plus src/app/not-found.tsx.
- Route classification convention: first dir under src/app must be `(public)` or `admin` (tests/support/routes.ts:22-28); unit test asserts every page/route is classified (tests/unit/route-classification.test.ts:16-19) and that `admin/feeds/page.tsx` would be `admin` (:42).
- mvp.md § Admin area: "Accounts for the three team members only, created by a command. There is no sign-up." (docs/product/mvp.md:130-131); "Login is email + password + authenticator-app code (TOTP). Every admin route and action checks the role on the server." (:132-133).
- mvp.md:33 "No public accounts. Visitors never log in."
- Decision 0001: two roles only; the admin role check runs "in server code: route handlers, server actions and data access. Never in components alone." (docs/decisions/0001-typescript-nextjs.md:36-38).
- Decision 0009: "The admin login uses a session cookie for admins only. It is strictly necessary, so it needs no consent." (docs/decisions/0009-click-log-and-analytics.md:34-35).
- Decision 0006 lists a required guardrail test: "admin routes reject anonymous requests on the server" (docs/decisions/0006-quality-gate.md:35) and e2e flows that begin with an admin (:17-18). None exist yet (grep of tests/ finds no admin-route test).
- Guardrail 3 text: agentic/project.md:58-61 and CLAUDE.md "Roles are enforced on the server".
- mvp.md:112-114: feed URLs "encrypted at rest before the first real feed is added" and "the admin area shows them masked" are adjacent future work, not S2.1 code; no encryption code exists.

## CLI verb pattern
- Each verb is a file in src/cli that calls `void runCli('<name>', async () => number)`: seed (src/cli/seed.ts:9-26), migrate (src/cli/migrate.ts:7-15), import-feeds (src/cli/import-feeds.ts:13-35).
- runCli (src/cli/shared.ts:8-17) sets process.exitCode from the main's return, always closes the pool via closeDb, and on a throw prints `<name>: failed (<code>)` with only a driver/system code or an "X is not set" notice (describeError, :20-27). Messages are never printed (guardrail 5). Unit-tested: tests/unit/cli-shared.test.ts:29-61 (sentinels for a URL and an email in an error message).
- Exit-code convention: 0 ok, 1 failure/not registered (import-feeds.ts:31), 2 usage error (seed.ts:14, migrate.ts:9-10, import-feeds.ts:19); 64 only from the entrypoint for an unknown verb (docker-entrypoint.sh:28).
- Usage-error idiom: `console.error('usage: <verb> ...')` then `return 2` (seed.ts:13-14).
- Entrypoint dispatcher: `case "$verb"` arms `server` (:14-20) and `migrate|seed|import-feeds` (:21-24, `exec node --conditions=react-server "dist/cli/$verb.js" "$@"`); default arm prints usage + unknown command and exits 64 (:25-29). A new verb must be added to the `migrate|seed|import-feeds` arm and the usage line at :26.
- CLIs run with `--conditions=react-server` so `import 'server-only'` resolves empty (docker-entrypoint.sh:7-8; package.json:19-21).
- npm script pattern per verb: `npm run cli:build && node --env-file=.env --conditions=react-server dist/cli/<name>.js` (package.json:19-21). `cli:build` = `tsc -p tsconfig.cli.json` (package.json:18).
- tsconfig.cli.json includes only `src/cli/**/*.ts` (tsconfig.cli.json:14), module node16, rootDir src, outDir dist; imported files are compiled transitively. Relative imports are required: ESLint forbids `@/` in src/{cli,config,db,server} (eslint.config.mjs:57-76; tests/unit/eslint-guardrails.test.ts:52-61). Existing relative specifiers carry no `.js` extension (src/cli/seed.ts:1-4).
- Dockerfile copies dist/ and src/db/migrations into the runner (Dockerfile:39-40) and installs full production node_modules (:35); a new runtime dependency must be under `dependencies` to reach the image (`npm ci --omit=dev`, :16).
- CLAUDE.md § Commands documents only migrate/seed/import-feeds as verbs and says "Any other verb exits 64"; a new verb makes that doc and the entrypoint usage text lag. CLAUDE.md § Commands belongs to the docs lane (agentic/project.md:124).
- Entrypoint e2e: tests/e2e/entrypoint.spec.ts:19-23 (unknown verb -> 64, stderr contains `usage: docker-entrypoint.sh`), :25-59 other verbs via `docker compose run --rm -T --no-deps app ...`; helper composeRun at :10-16.
- `seed --if-enabled` is the precedent for flag arguments and env-gated behaviour: src/cli/seed.ts:11-19, src/config/seed.ts (isDemoSeedEnabled; file exists, not opened).
- Server-side DB access seam: `getDb()` / `closeDb()` in src/db/client.ts:26-48, `Executor` type at :16 for tx-or-db injection; src/server/<area>/ holds logic and the CLI stays thin (seed calls src/server/seed/index.ts).

## Schema and migrations
- Schema files: src/db/schema/catalogue.ts, sources.ts, clicks.ts, re-exported from src/db/schema/index.ts:5-7. Header comment: imports only drizzle-orm so drizzle-kit loads it with no environment; optional text is null, never an empty string (index.ts:1-4).
- Table style: `id: integer('id').primaryKey().generatedByDefaultAsIdentity()`, `createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow()`, snake_case column names, camelCase TS fields (src/db/schema/sources.ts:15-20, 22-29).
- Slugs `text().notNull().unique()`; booleans `.notNull().default(false)` (sources.ts:18, 27); unique constraint and CHECK via the table callback (sources.ts:47-53); `sql` template check in clicks.ts:35-38; pgEnum for closed sets (sources.ts:13).
- Foreign keys use `onDelete: 'restrict'` (sources.ts:37-38; clicks.ts:15-25).
- No user, account or credential table exists. migrations.test.ts:19-35 lists expected tables: networks, shops, feeds, categories, products, offers, clicks, feed_category_mappings.
- Migration generation: `npm run db:generate -- --name <name>` (package.json:17; drizzle.config.ts:6-10, schema ./src/db/schema/index.ts, out ./src/db/migrations). Existing: 0000_init, 0001_clicks, 0002_category_mapping (src/db/migrations/meta/_journal.json:5-25). Next would be 0003. Migrations are applied by src/db/migrate.ts, never drizzle-kit (drizzle.config.ts:4-5).
- Migration tests auto-cover any exported table: every table in `schema` must exist in the DB and every column match nullability (tests/integration/migrations.test.ts:16, 38-68); journal count must equal applied count (:82-91).
- tests/integration/schema.test.ts:19,30 inspects information_schema columns, including all `%_cents` columns (not opened beyond the grep line).
- Test DB reset truncates every table in `public` with `restart identity cascade` (tests/support/db.ts:24-33), so a seeded admin row is wiped per test unless the test inserts its own.
- Test DB is `${DB_NAME}_test`, dropped/recreated/migrated per integration run (vitest.config.mts:29-33; CLAUDE.md § Commands); integration files run serially (`fileParallelism: false`, vitest.config.mts:28).
- Seams test requires `is_approved|isApproved|is_hidden|isHidden|in_review|inReview` only in visibility.ts, src/db/, seed, importer (tests/unit/seams.test.ts:57-68); a user-table column with such a name would be affected.
- Seed behaviour: demo seed is idempotent and preserves admin decisions (src/server/seed/index.ts:23 comment; tests/integration/seed.test.ts:122,154); it loads networks, shops, feeds, categories only (src/cli/seed.ts:6-8).

## Root layout, middleware, headers, cookies
- No middleware or proxy file exists: file listing of src and repo root shows none; src/i18n/request.ts:5-6 states "no middleware and no routing: next-intl's middleware sets a locale cookie, which guardrail 5 forbids for public visitors (TD-4)".
- Single root layout: src/app/layout.tsx:21-39 renders `<html lang>` > `<body>` > SiteHeader + {children} + SiteFooter (footer links to the 3 legal pages, :24-29) for every route. No `(public)/layout.tsx` and no `admin/layout.tsx` exist. A route at src/app/admin/** would inherit header, footer and the root `export const dynamic = 'force-dynamic'` (:11).
- Root metadata is `generateMetadata` returning title + description only (layout.tsx:13-19): no `robots` metadata anywhere.
- SiteHeader takes only `siteName` and renders a link home (src/components/SiteHeader.tsx:6-16); no auth state, no logout.
- next.config.ts:6-11: `output: 'standalone'`, `poweredByHeader: false`; no `headers()` config, no redirects.
- No noindex/robots/sitemap code in src (grep returns nothing). mvp.md:178-179 says demo products are noindex and left out of the sitemap, so that behaviour is promised but not implemented.
- Cookies set today: none. The health route is `force-dynamic` (health/route.ts:6) and answers `Cache-Control: no-store` (:8).
- /go sets no cookie and tests assert so: tests/integration/go-redirect.test.ts:27,54; go-privacy.test.ts:84-104,137,170; tests/e2e/go.spec.ts:21-49.
- Public-page cookie assertions that target public URLs today: `expectNoSetCookie` (tests/support/page-checks.ts:20-23) used in tests/e2e/go.spec.ts, product.spec.ts, legal.spec.ts, category.spec.ts, home.spec.ts; `context.cookies()` toEqual([]) in home.spec.ts:64, product.spec.ts:144,157, category.spec.ts:223,237,287, legal.spec.ts:228, stack.spec.ts:38.
- Static scan: no cookie mention in src/app/(public)/go/ or src/server/clicks/ (tests/unit/seams.test.ts:211-219). A session helper elsewhere does not trip it. Reading the user agent is limited to src/server/clicks/counting.ts (seams.test.ts:176-179); no client-address headers anywhere in src (:181-183), so an IP-keyed login rate limiter would trip that scan.
- Seams test forbids importing `@/db/` from any page or component under src/app or src/components except route.ts/route.js files (tests/unit/seams.test.ts:96-104). A login page that touches the DB must go through src/server/ or a route handler.
- Seams test forbids `fetch(` outside src/server/importer/source.ts and any http client import in src (seams.test.ts:77-85).
- Compose: app binds to 127.0.0.1 only (compose.yaml:9-10); app environment lists exactly SITE_NAME, DATABASE_URL, SEED_DEMO_DATA, OWNER_*, CONTACT_EMAIL, PORT, HOSTNAME, NODE_ENV (compose.yaml:11-24); there is no session-secret variable. A new env var must be added to compose.yaml, .env.example:1-20 and possibly scripts/init-env.mjs (generates DB_PASSWORD and UMAMI_APP_SECRET, init-env.mjs:21-26; tests/unit/init-env.test.ts:54-68 pins its output).
- Env access seam: readRequiredEnv/readOptionalEnv read at call time, never at module load, and never put values in errors (src/config/env.ts:9-15, 26-29, comment TD-5/TD-13).

## i18n and messages
- Single catalogue messages/es-ES.json (109 lines), top-level namespaces: Metadata, Home, NotFound, Category, Product, Footer, DemoNotice, LegalNotice, Privacy, Funding (es-ES.json:2,6,14,19,33,46,51,54,76,101). No Admin or Login namespace.
- Loading: src/i18n/request.ts:7-11 (fixed locale from src/i18n/locale.ts, `timeZone: 'Europe/Madrid'`, dynamic import of the JSON); plugin wired in next.config.ts:4; pages call `getTranslations('<Namespace>')` (layout.tsx:14,23).
- Copy conventions: ICU plurals `{count, plural, one {#...} other {#...}}` (es-ES.json:10,23,39); `{siteName}` placeholder; the code name must not appear in any message or file under src/ (tests/unit/messages.test.ts:66-76); rich-text tags like `<email>` / `<b>` (es-ES.json:61,84).
- Message tests: tests/unit/messages.test.ts pins specific keys per namespace (:37-49 Home/Metadata/NotFound, :80-93 Product, :187-190 Privacy keys); it does not require keys for new namespaces. Support helper tests/support/messages.ts and tests/unit/message-helpers.test.ts exist (not opened).
- Existing relevant copy: Privacy.adminsHeading = "Administradores", adminsBody = "El área de administración usa una cookie de sesión, estrictamente necesaria para iniciar sesión. Solo la reciben los administradores del sitio; los visitantes nunca la reciben." (es-ES.json:92-93), rendered at src/app/(public)/privacidad/content.tsx:49-50; heading asserted by tests/unit/legal-pages.test.ts:122.
- Privacy.cookiesBody says the site installs no cookies for visitors (es-ES.json:81-82), consistent with an admin-only cookie.
- Design system: docs/design/system.md (Header table at :49, focus ring and 44 px tap targets at :67). Grep found no form-control, input, button or error-message spec in it; I did not read the full file.
- CSS convention: co-located `*.module.css`, globals.css holds variables/reset (CLAUDE.md § Stack, decision 0011). No form or input component exists in src/components (listing).

## Logging and guardrail 5
- No logging library. Only console.log/console.error, at: src/server/clicks/handle-go.ts:37,68; src/cli/migrate.ts:9,13; src/cli/import-feeds.ts:18,26,30; src/cli/seed.ts:13,17,21; src/cli/shared.ts:12; src/app/(public)/api/health/route.ts:28.
- Pattern: log a fixed string plus `errorCode(error)`, never the error message (src/server/error-code.ts:6-14: returns `code` if matching `/^[A-Za-z0-9_]{1,32}$/` else 'UNKNOWN'). Used at handle-go.ts:37,68 and health/route.ts:28.
- Tests that pin no-leak behaviour with sentinels: tests/integration/health.test.ts:8,29-48 (password sentinel absent from body and log output); tests/integration/go-privacy.test.ts:84-104,159-170 (cookie/header sentinels, "logs nothing"); tests/integration/importer-logging.test.ts (not opened); tests/unit/cli-shared.test.ts:29-61 (URL and email sentinels).
- tests/e2e/entrypoint.spec.ts:59 checks seed output contains no `postgres://` or `DB_PASSWORD`.
- Click table schema comment lists columns that deliberately do not exist (ip, user agent, cookie, referer, session, visitor, hash, flag) (src/db/schema/clicks.ts:7-10; tests/integration/clicks-schema.test.ts:25 inspects its columns). A sessions table elsewhere would not collide with it.
- Guardrail 5 text: agentic/project.md:65-69 "Never log tokens, passwords or emails in plaintext"; CLAUDE.md says "Never log tokens, passwords or emails" without "in plaintext".

## Tests
- Vitest config vitest.config.mts:13-37: two projects. `unit` = tests/unit/**/*.test.ts (no DB); `integration` = tests/integration/**/*.test.ts, serial, with globalSetup tests/support/global-setup.ts and setupFiles tests/support/test-database-env.ts. Aliases `@` -> src and `server-only` -> tests/support/server-only-stub.ts (:8-11). The config comment forbids importing from tests/ (:5-6).
- Playwright config playwright.config.ts:15-25: testDir tests/e2e, globalSetup ./tests/e2e/global-setup.ts (runs the Compose import), `fullyParallel: true`, `forbidOnly`, one chromium project, no webServer (Compose stack is the server under test, :14). baseURL from E2E_BASE_URL or APP_PORT (:10-12).
- E2E runs against the built image in Compose: a login e2e needs an admin account in the Compose `db`, i.e. created by a new verb via `docker compose run --rm -T --no-deps app <verb>` (pattern: tests/e2e/entrypoint.spec.ts:10-16) or by seed. The comment at playwright.config.ts:17-18 says tests never write the dev DB, though entrypoint.spec.ts runs import-feeds against it.
- Support helpers: tests/support/{db.ts, env.ts, feeds.ts, go.ts, catalogue.ts, messages.ts, net.ts, network-off.ts, pg-error.ts, routes.ts, page-checks.ts}; fixtures in tests/fixtures/.
- Guardrail-3 tests present: only classification, tests/unit/route-classification.test.ts:9-44 and tests/support/routes.ts:22-28. No test requests an admin URL or checks a role. The comment at route-classification.test.ts:21 ("two slice A entry points") is slice-A history, not a deferral.
- Guardrail-5 tests present: seams (tests/unit/seams.test.ts:161-220), go-privacy, health, cli-shared, entrypoint, and the "no cookie" assertions listed under Root layout. None addresses an admin cookie, password logging, or admin e-mail logging.
- Deferral to admin found only as comments: "an admin edit (S4.2) is not built yet" (tests/integration/importer-categories.test.ts:201); US-5.1 defers admin screens to S4.1/S4.2 (docs/product/stories/US-5.1-category-browse.md:33). I did not grep for `it.todo`/`test.skip`.
- Tests that mention admin but concern hidden-by-admin visibility (not role checks): tests/integration/category-tree.test.ts:156, category-page.test.ts:162, go-redirect.test.ts:59, seed.test.ts:122,154,168, importer-preservation.test.ts:28-31, importer-categories.test.ts:243,271.
- ESLint guardrail tests lint virtual files against the real config: tests/unit/eslint-guardrails.test.ts; a new auth dependency imported in src/{cli,config,db,server} must still use relative imports.
- Gate: `npm run gate` = lint, typecheck (tsconfig.json + tsconfig.cli.json), db:up, `npm test`, stack:up, `test:e2e` (package.json:27).
- Story-file format example: docs/product/stories/US-5.1-category-browse.md:1-23 header (Status, Epic/Slice/Priority/Size, Issue/Tickets, Depends on, Source), then `## Open decisions`, `## Story`, `## Scope` (In / Out), `## Acceptance criteria` (numbered, grouped by subheading, :35-58). Only the first 60 lines were read.
- Story IDs referenced in the repo: S1.1 click log (seams.test.ts:161), S4.1/S4.2 tree and mapping admin screens, S5.1, S8.1 image upload, S9.3 legal pages. I did not grep for S2.1 or #22 by name.

## Dependencies and config
- Runtime dependencies (package.json:29-37): drizzle-orm ^0.45.4, next ^16.4.2, next-intl ^4.14.9, pg ^8.23.1, react ^19.3.1, react-dom ^19.3.1, server-only ^0.0.1. Nothing for password hashing, TOTP, session, JWT, validation or cookies is installed.
- Dev dependencies (package.json:38-49): @playwright/test, @types/*, drizzle-kit, eslint (+ eslint-config-next), typescript ^5.9.3, vitest ^5.0.5.
- Node `>=22 <23` (package.json:5-7), `.nvmrc` present; I did not grep for `node:crypto` use.
- Native-binding packages must build on `node:22-alpine` (Dockerfile:3); not verified for any candidate.
- Guardrail 2 lint ban list covers scrapers/browsers only (eslint.config.mjs:8-20); an auth library is unaffected.
- `.claude/settings.json` and `.mcp.json` exist; not opened.
- CLAUDE.md § Stack says a change to a stack line is the owner's call (agentic/project.md:96-99); no recorded decision covers authentication, hashing or sessions (only 0001:36-38, 0006:35, 0009:34-35 touch the admin).

## Sources of truth
- docs/product/mvp.md (approved 2026-10-16, amended 2026-10-18; mvp.md:3-7) governs scope; § Admin area at :128-141 governs S2.1. Looks current and consistent with CLAUDE.md and project.md.
- docs/decisions/: 0001 (roles, server checks), 0006 (gate tests), 0009 (admin session cookie), 0004 (delivery; admin lines found only by grep at :22, :24). No numbered decision on auth mechanics.
- agentic/project.md § Hard guardrails (:46-73) is the only numbered copy of guardrails 1-5; guardrail 3 at :58-61, guardrail 5 at :65-69.
- CLAUDE.md § Commands lists verbs and states "Any other verb exits 64"; it will lag a new verb.
- docs/design/system.md is the UX reference (grep only); no admin or form patterns found.
- GitHub Project 3 and issue #22 were not read, per the order.

## Open questions
- TOTP: mvp.md:132 requires password plus authenticator code; the order says "email+password" for S2.1. Is TOTP in S2.1 or a later story? The repo does not say.
- Which mechanism for password hashing and session storage (library vs node:crypto, DB-backed session vs signed cookie)? No decision exists; the order excludes recommending one (OD1).
- Where does an admin session get checked, given there is no middleware/proxy file and the seams test blocks `@/db/` imports from pages and components (seams.test.ts:96-104)? The map cannot settle the intended seam.
- Does `src/app/admin/**` get its own root layout or route group (the root layout at layout.tsx:21-39 wraps public chrome around every route)? Not decided anywhere in the repo.
- Where do the create-admin verb's arguments come from (flags, prompt, generated)? No src/cli verb takes an interactive prompt; all use flags. Passwords and emails must stay out of logs (guardrail 5).
- Session cookie secret: no env var exists (compose.yaml:11-24, .env.example); whether `env:init` should generate it is undecided.
- Does the demo/noindex handling (mvp.md:178-179) cover admin and login pages? No robots or noindex code exists at all, so any such requirement is new code.
- What does an anonymous request to an admin URL return (redirect to login, 401, 404), and may that response set a cookie? Not specified in docs; relevant to the e2e "no cookie" family.
- Rate limiting or lockout on login: no precedent; the seams test bans client-IP headers in src (seams.test.ts:181-183), constraining the key choice.
- Decision numbers 0003 and 0005 are missing from docs/decisions; unknown whether intentional or whether one covers auth.
- Whether Next 16.4.2 here uses `middleware.ts` or `proxy.ts` as the interception filename was not verified.
