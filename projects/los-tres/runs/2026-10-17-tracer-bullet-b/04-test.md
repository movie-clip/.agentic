REPORT 2026-10-17-tracer-bullet-b/04
status:      DONE
verdict:     NONE

changed:
  - vitest.config.mts — __dirname replaced by import.meta.dirname; comment on global setup updated; no configLoader/CJS warning in the gate or unit run
  - playwright.config.ts — globalSetup './tests/e2e/global-setup.ts' added as a string; base-URL comment now says this file is the one copy
  - tests/support/global-setup.ts — drops, recreates and migrates ${DB_NAME}_test on every integration run through runMigrations; failure messages never carry the URL
  - tests/support/db.ts — resetDatabase() added (assertTestDatabase, then truncate all public tables, restart identity cascade)
  - tests/support/env.ts — appBaseUrl() deleted (nothing calls it); the base URL now has one source, playwright.config.ts
  - tests/support/catalogue.ts — new; direct-insert fixtures (insertShop/Feed/Product/Offer, insertVisibleOffer, insertFixtureFeed, allProducts/allOffers)
  - tests/support/feeds.ts — new; readFeedFixture, fixtureDeps (feed url = fixture file name), textDeps(byFeedId)
  - tests/support/network-off.ts — new; stubNetworkOff() makes global fetch throw
  - tests/support/net.ts — new; unusedPort(), moved out of health.test.ts
  - tests/support/pg-error.ts — new; pgErrorOf() unwraps code and constraint from a Drizzle rejection
  - tests/support/messages.ts — new; normaliseSpaces, icuPlural, dateMessagePattern, so e2e assert copy through messages/es-ES.json
  - tests/support/page-checks.ts — new; openRawHtml (JS-off setContent), expectNoSetCookie, expectLocalScriptsAndLinks, expectNoForeignOrigin, extracted from home.spec.ts
  - tests/fixtures/demo.ts — new; expected demo slugs, titles, shop names, prices, counts
  - tests/fixtures/feeds/*.csv — new; 9 local feed fixtures (ean-first, ean-second, ean-brand-conflict, ean-null-brand, no-ean, rejects, price-edge, invalid-header, empty-cells, changed-text)
  - tests/integration/health.test.ts — unusedPort imported from tests/support/net.ts
  - tests/e2e/home.spec.ts — uses baseURL fixture and page-checks helpers; no appBaseUrl
  - tests/e2e/global-setup.ts — new; runs docker compose run --rm -T --no-deps app import-feeds once, throws the TD-38 message on feeds=0
  - tests/e2e/product.spec.ts — new; C-13 on raw HTML with JS off, order, count, one-shop wording, no links, no cookie, 404 cases
  - tests/e2e/entrypoint.spec.ts — new; serial; bogus verb exits 64, import twice creates nothing, --feed 999999 exits 1, bad argument exits 2
  - tests/unit/money.test.ts — new; float-trap prices, rejects, formatEuroCents with U+00A0 normalised
  - tests/unit/matching.test.ts — new; GTIN-8/13, check digits, normalisers
  - tests/unit/slug.test.ts, csv.test.ts, import-validate.test.ts, import-report.test.ts, seed-config.test.ts — new unit tests for the pure importer, slug and config modules
  - tests/unit/feed-source.test.ts — new; the real reader with fetch stubbed: demo-feed scheme and traversal, non-https refusal, size cap, no URL in errors
  - tests/unit/cli-shared.test.ts — new; runCli prints an error code only
  - tests/unit/eslint-guardrails.test.ts — new; ESLint Node API on virtual files for the scraping ban and the relative-import rule
  - tests/unit/seams.test.ts — new; file scans for visibility flags, fetch, fs, @/db, /100, parseFloat and float columns in the migration SQL
  - tests/unit/init-env.test.ts — new; init-env.mjs in a temp tree, never touches the real .env
  - tests/unit/messages.test.ts — extended with the Product namespace (keys, placeholders, plural branches)
  - tests/unit/message-helpers.test.ts, product-components.test.ts — new; pins the message helpers and the ProductDetails/OfferList branches
  - tests/integration/migrations.test.ts, schema.test.ts, seed.test.ts — new; tables and columns vs Drizzle, money columns, check constraints, default-deny, seed scope
  - tests/integration/visibility.test.ts, product-page.test.ts — new; guardrail 1 truth table on getPublicProductBySlug, exact contract shape, ordering with ties
  - tests/integration/importer-demo.test.ts, importer-matching.test.ts, importer-source.test.ts — new; shipped demo data, EAN matching and every reject code, registered-source rules
  - tests/integration/importer-preservation.test.ts, importer-isolation.test.ts, importer-logging.test.ts — new; admin decisions survive seed and import, per-feed transactions, no URL key or row content in any output

verification:
  command:   npm run gate; docker compose stop db && npm run test:unit; docker compose start db; git status --porcelain
  result:    PASS
  detail:    gate exit 0: lint and typecheck clean; Test Files 30 passed (30), Tests 396 passed (396), 0 skipped (unit 17 files, integration 13 files, 105 tests); e2e 23 passed, 0 skipped. test:unit with db stopped: 17 files, 291 tests passed. No configLoader warning in either output.

contract_notes:
  - tests/unit/seams.test.ts pins that fetch( appears only in src/server/importer/source.ts and node:fs only in source.ts and src/db/migrate.ts; a later slice needing either must extend the allow-list there.
  - tests/integration/product-page.test.ts pins PublicProductPage and PublicOffer with toEqual; adding any key (url, shopCount, an internal id) fails it on purpose.
  - tests/e2e/global-setup.ts parses the line total: feeds=N imported=N skipped=N failed=N from import-feeds stdout; a change to that C-16 line breaks e2e setup.
  - Feed fixtures use the C-15 header names; a change to the canonical CSV layout needs tests/fixtures/feeds/*.csv updated with it.
  - tests/e2e product spec expects the Spanish copy only through messages/es-ES.json, and the demo values from tests/fixtures/demo.ts, which must stay equal to demo/feeds/*.csv.

pack_corrections:
  - testing.md — § Running tests: replace the clause on the test database with "`tests/support/global-setup.ts` drops and recreates `${DB_NAME}_test` on every integration run (`drop database ... with (force)`) and migrates it with `runMigrations` from `src/db/migrate.ts`. Integration files call `resetDatabase()` (`tests/support/db.ts`) in `beforeEach` and `closeDb()` in `afterAll`."
  - testing.md — § Running tests: replace "`vitest.config.ts`" and "Vitest 5 with two projects in `vitest.config.ts`" with `vitest.config.mts` (the package stays CommonJS), which uses `import.meta.dirname`; and add "`vitest.config.mts` and `playwright.config.ts` must not import from `tests/`".
  - testing.md — § Running tests: add "E2E data comes from Playwright `globalSetup` (`tests/e2e/global-setup.ts`), which runs `docker compose run --rm -T --no-deps app import-feeds` and throws the TD-38 message on `feeds=0`; e2e tests never write the development database themselves. Specs use the `baseURL` and `request` fixtures; only `playwright.config.ts` computes the base URL (`appBaseUrl()` is gone)."
  - testing.md — § What must always be covered: replace the Matching line with "**Matching (0008), slice B cut:** EAN attach, EAN with a different brand rejected into the report (`ean_brand_conflict`), null brand on either side attaches, no EAN creates a product, invalid EAN rejected. Brand + part-number matching and the queue are tested when they ship."
  - testing.md — § What must always be covered: add "Assertions on es-ES prices normalise U+00A0 (`normaliseSpaces`, `tests/support/messages.ts`). `tests/unit/seams.test.ts` scans the source so the visibility flags, `fetch(`, `node:fs`, `@/db` in pages and `/ 100` stay out of places they do not belong."
  - testing.md — add a § Shared test scaffolding: "`tests/support/catalogue.ts` (insert helpers whose defaults are the fully VISIBLE state: a test sets only the one flag it is about), `feeds.ts` (`fixtureDeps`: a feed row's `url` is the fixture file name; `textDeps`), `network-off.ts` (`stubNetworkOff`, every importer test stubs fetch to throw), `pg-error.ts`, `page-checks.ts`, `messages.ts`. Local feed files live in `tests/fixtures/feeds/`; shipped-demo expectations in `tests/fixtures/demo.ts`."
  - testing.md — add "The ESLint Node API runs in Vitest (`new ESLint({cwd})`, `lintText(code, {filePath})` on virtual paths under `src/`); the first call loads eslint-config-next and takes seconds, so those tests pass a 60 s timeout."
  - testing.md — add "A malformed-slug test proves 'no query' black-box: stop the pool, point DATABASE_URL at an unused port, call the read function; malformed slugs return null, a well-formed slug rejects."
  - testing.md — add "`vi.stubEnv` plus `closeDb()` re-points `getDb()`: `getDb` caches its pool, so close it before and after changing DATABASE_URL."
  - testing.md — add "React components render in the unit project with `renderToStaticMarkup` from `react-dom/server` and `createElement`; `.module.css` imports resolve without configuration."
  - testing.md — add "On Windows (autocrlf) existing files are CRLF: a multi-line Edit old_string fails, so use single-line edits or rewrite the file with Write. A Python script that opens a file with open(p,'wb') before it has built the content truncates the file if the build raises; read, build, then write. Python's default encoding is cp1252: pass encoding='utf-8'. A long Bash heredoc containing apostrophes failed to parse; use Write for files."

handoff:
  - Docs/integration: run `npm run gate` with SEED_DEMO_DATA=true in .env; the e2e global setup fails with the TD-38 message if the app container has no approved feed.
  - Counts to cite: unit 17 files 291 tests, integration 13 files 105 tests, e2e 23 tests, 0 skipped anywhere.
  - Next lane writing integration tests: call resetDatabase() in beforeEach and closeDb() in afterAll, build rows with tests/support/catalogue.ts, and call stubNetworkOff() in beforeEach with vi.unstubAllGlobals() in afterEach.
  - Next lane adding a feed fixture: put the CSV in tests/fixtures/feeds/, register a feed whose url is the file name (insertFixtureFeed), and import with deps: fixtureDeps; never the real reader for a fixture.
  - Next e2e spec on a public page: use openRawHtml, expectNoSetCookie, expectLocalScriptsAndLinks, expectNoForeignOrigin from tests/support/page-checks.ts, the baseURL fixture, and messages.ts helpers for plural and date copy.
  - Admin slice: the visibility truth table is in tests/integration/visibility.test.ts; an admin action that flips a flag should reuse insertVisibleOffer and assert through getPublicProductBySlug.
  - /go slice: guardrail 5 click-row test (no IP, user agent or cookie) is not written; no /go route exists yet. The seams scan already bans fetch( and HTTP clients outside source.ts.
  - Brand + part-number matching slice: matching.ts keeps one gap for it; add cases to tests/integration/importer-matching.test.ts next to the EAN ones, with a new fixture CSV.

skill_calls:
  - none

risks:
  - No mutation check was made: I could not edit src/**, so I did not prove each new test fails when its rule is broken. The suites passed on first run, which is evidence of agreement with the code, not of sensitivity.
  - tests/e2e/global-setup.ts failure branches (feeds=0 gives the TD-38 message, a failed import throws) were not exercised; only the success path ran in the gate.
  - The e2e import writes price_updated_at on the development database on every run; the design mandates it (TD-38) and nothing else in e2e writes. Tests that need unapproved or hidden rows run only on the _test database.
  - Page-level hiding is not browser-tested, as designed: visibility is proven on getPublicProductBySlug and the unknown-slug 404; a hidden product reaching notFound() relies on the page's null-to-notFound mapping.
  - seams.test.ts strips comments with a line-based regex and matches imports with a regex; a flag name inside a string, or a multi-line import, could slip past. It is a tripwire, not a parser.
  - dateMessagePattern accepts any 3 to 5 letter month token; it pins the shape of the ICU medium date, not the exact Madrid date or month name.
  - The first unit run spent about 23 s mostly in the ESLint tests (config load); later runs finished in under 2 s. If it grows, move eslint-guardrails.test.ts behind its own timeout or file.
  - Guardrail 5 on /go (click row, no cookie) has no test because the route does not exist; the home and product specs cover no-cookie and no foreign origin for the public pages that do.
  - global-setup swallows the migration error text and prints a fixed message (the driver message can carry the URL); a broken migration shows no cause, so run `npm run db:generate` or read the migration SQL to find it.
  - No production defect found: nothing in src/** was edited or needed to be.
