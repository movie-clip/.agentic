REPORT 2026-10-17-tracer-bullet-b/06
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd C:\projects\investments\los-tres && npm run gate; drizzle-kit generate drift probe on a copy; docker compose build --no-cache app; docker compose run --rm -T --no-deps app import-feeds / bogus; git status --porcelain
  result:    PASS
  detail:    gate exit 0: eslint clean, tsc clean (both configs); vitest Test Files 30 passed (30), Tests 396 passed (396), 0 failed, 0 skipped, no configLoader warning; playwright 23 passed, 0 failed, 0 skipped. Drift probe: "No schema changes, nothing to migrate". Cold build: Image los-tres-app Built, exit 0. git status empty. Anchors: see § Anchors used.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - no change request raised; nothing blocks close. Close docs may apply the pack_corrections of 01, 02, 03 and 04, and record decision 0011 and the CLAUDE.md § Stack CSS Modules line.
  - Open row to add (SHOULD_FIX, backend): src/server/importer/source.ts calls fetch without a redirect policy, so an https feed can redirect to http or another host; set redirect to error or re-check the final URL, and add a case to tests/unit/feed-source.test.ts (test lane), see § Findings.
  - Open row to add (SHOULD_FIX, docs): CLAUDE.md § Commands quotes the e2e failure text as "no approved feed: set SEED_DEMO_DATA=true in .env and run docker compose up -d", but tests/e2e/global-setup.ts throws "e2e setup: the import found no approved feed. Set SEED_DEMO_DATA=true in .env and run: docker compose up -d".
  - Open row to add (SHOULD_FIX, test): the failure branches of tests/e2e/global-setup.ts (feeds=0, failed import) and the sensitivity of the new suites to a broken rule were never exercised; 04-test says so itself. I confirmed by reading that the guardrail tests assert on one flag at a time.
  - Open row to add (human, informational): acceptance line 1 reads "demo data is present" after compose up; under owner ruling D-2 Q-2 the seed loads shops, feeds and categories but no products, so a product page 404s until import-feeds runs. CLAUDE.md says so.
  - Open row to add (carried, dev-only): npm audit reports 9 advisories (4 moderate, 5 high) that arrive through drizzle-kit and @esbuild-kit; npm audit --omit=dev reports 0 vulnerabilities, so the image is unaffected.
  - Review phase is not triggered (no story); the human checks the acceptance lines in § Acceptance lines, slice B.

skill_calls:
  - none

risks:
  - Skill-call fidelity: reports 01, 02, 03, 04 and 05 all state skill_calls none, and none names a skill or an existing pattern as precedent in risks or contract_notes; no contradiction found.
  - The gate's stack:up reused Docker layer cache, so I ran the cold build as a separate command (docker compose build --no-cache app, exit 0, only the base image and WORKDIR cached). The cold image was built but not started; the running stack is the gate's image from the same sources.
  - Host port 3000 belongs to another project; the gate, curl and e2e ran against APP_PORT=3010 from .env. The 3000 URL printed in CLAUDE.md was not exercised, and the code reads one variable for both.
  - I did not rebuild a fresh database volume. Migrating from nothing is covered by tests/support/global-setup.ts (drop, create, migrate on every integration run) and by 02-backend's own reset run; the gate ran against the existing dev volume.
  - The gate's e2e global setup writes offers.price_updated_at on the development database each run, by design TD-38; the dev database holds only demo rows (3 products, 4 offers, 2 feeds).
  - Postgres server logs (db service) print the full failing row on a check violation, which includes the offer url; this appeared only for the schema test's deliberate price_cents 0 and -1 inserts on the _test database. The importer validates price before insert, so a feed row cannot reach it.
  - The importer's loadFeeds names feeds.isApproved to choose which feeds to read. This is the second place a feed approval is read, but it gates importing (TD-29), not what the public sees, and the design allows the importer to name the flag. Not a second visibility scope.
  - The page does not import the PublicProductPage type by name; it consumes the function's inferred return type, which is the same contract. Checked structurally, see § Contract alignment.
  - Producer-side note: acceptance line 1 and 0004 ("demo data loads on first start") read slightly differently from the owner's ruling D-2 Q-2. The ruling stands; nothing to re-scope here.

## Orchestrator brief
- Verdict PASS, status DONE, no CR files, no BLOCKING finding. `npm run gate` run by me: exit 0, vitest 30 files / 396 tests passed, playwright 23 passed, lint and both tsc configs clean.
- Drift probe: `drizzle-kit generate` on a copy reports "No schema changes, nothing to migrate"; the cold `docker compose build --no-cache app` exits 0; `dist/` and `.env` are untracked; tree clean at the end.
- C-11 matches code, page and tests field by field (toEqual + `satisfies PublicProductPage`); C-12 to C-18 match; no undeclared deviation from 01-design.
- One copy each of visibility scope, importer write path, matcher, money helper, confirmed by grep and by tests/unit/seams.test.ts.
- Guardrails 1, 2, 4, 5 hold by seam; guardrail 3 has no new seam (no admin route). Importer output, container logs and page HTML carry no feed URL.
- Slice B acceptance: all 7 lines met; line 1 is met as the owner ruled it (D-2 Q-2, seed loads no products).
- Three SHOULD_FIX rows to add: redirect policy in source.ts (backend), CLAUDE.md failure-text drift (docs), untested global-setup failure branches (test).
- Informational Open rows: acceptance line 1 wording vs D-2 Q-2 (human); dev-only npm audit via drizzle-kit (carried).
- Close docs and protocol-lint are the remaining phases; review is not triggered.
- Sections below: Gate run · Anchors used · Contract alignment · Design adherence · Reuse and seams · Guardrails by seam · Checks from 01-design · Acceptance lines, slice B · Findings · Coverage adequacy.

## Gate run

`npm run gate` on branch 6-tracer-bullet-slice-b, clean tree, `.env` with APP_PORT=3010 and SEED_DEMO_DATA=true. Results, in order:

- `eslint .` printed nothing, exit 0. `tsc --noEmit && tsc -p tsconfig.cli.json --noEmit` printed nothing, exit 0.
- `docker compose up -d --wait db` healthy. `vitest run`: Test Files 30 passed (30), Tests 396 passed (396), Duration 11.42s. No configLoader warning.
- `docker compose up -d --build --wait`: app, db and umami Healthy.
- `playwright test`: 23 passed (6.8s), global setup ran the compose import first.
- Final line `EXIT=0`.

Extra commands: `docker compose build --no-cache app` exit 0 (Image los-tres-app Built). `docker compose run --rm -T --no-deps app import-feeds` printed `feed 1 ... offers_updated=2 rejected=0`, `feed 2 ... offers_updated=2 rejected=0`, `total: feeds=2 imported=2 skipped=0 failed=0`, exit 0, no URL in the output. `app bogus` exit 64.

## Anchors used

External anchors, not the design document alone: a real PostgreSQL container ran the migrations, the schema and visibility tests and the importer tests; a real chromium browser asserted no cookie and no foreign origin; `curl -D -` read the live page and the headers (200, no Set-Cookie, one anchor in the HTML which is the header link to `/`, 404 for an unknown slug); `drizzle-kit generate` regenerated from the schema as an independent check on the committed migration; `docker compose logs` and `docker compose run` output were grepped for URLs. The C-11 to C-18 comparison below is a consistency check against 01-design and is labelled as one.

## Contract alignment

Consistency check against 01-design § Contract, field by field:

- C-11 `PublicOffer`: offerId, shopName, priceCents, priceUpdatedAt. `PublicProductPage`: slug, title, brand, partNumber, ean, description, offers. Code in src/server/catalogue/product-page.ts has exactly these keys and nullability (the four text fields `string | null`, title non-null). tests/integration/product-page.test.ts pins them with `toEqual` and `satisfies PublicProductPage`, and a second test asserts the affiliate url never appears in the JSON.
- The page src/app/(public)/producto/[slug]/page.tsx reads only those fields: title, brand, partNumber, ean (nulls left out of the dl), description (text node), offers.length, offerId (React key only), shopName, priceCents through `formatEuroCents`, priceUpdatedAt as a `Date` to next-intl. No field is used that the type lacks, and no nullable field is used as required.
- Sort: SQL `order by price_cents asc, shops.name asc, offers.id asc`; the components never sort. Null for every non-public reason, malformed slug rejected before a query (test stops the pool and proves it).
- C-12: `/ 100` appears only in src/server/money.ts:38 (seams test). `parseDecimalToCents` is by digits, no float. `formatEuroCents` forces `useGrouping: 'always'`, throws RangeError on a non-integer or negative.
- C-13: raw HTML checked live and by e2e: one h1, role=img placeholder, dl of non-null details, shop-count, h2, IVA note, ol of li with the three test ids, no link in the list, no `.example` host, no `/go`.
- C-14: ten `Product` keys in messages/es-ES.json with the fixed names and placeholders; `shopCount` is an ICU plural with one and other; `priceUpdatedOn` uses `{date, date, medium}`; `timeZone: 'Europe/Madrid'` set in src/i18n/request.ts.
- C-15 and C-16: header names, price regex, currency rule, reject codes and the report line format match src/server/importer/validate.ts and report.ts; the e2e setup parses the `total:` line, so a change to it breaks the gate loudly.
- C-17 and C-18: `.env.example`, compose.yaml and docker-entrypoint.sh agree on SEED_DEMO_DATA (example true, Compose default false) and on the verbs; demo CSVs and tests/fixtures/demo.ts agree (3 products, 4 offers, 11,49 € before 12,99 € for the shared-EAN product).

## Design adherence

- Fences held: git shows backend files only in the backend fence, frontend only under src/app/(public)/producto, src/components, src/i18n/request.ts and messages; tests/** and the two test configs for the test lane; CLAUDE.md § Commands for docs. The `git mv vitest.config.ts vitest.config.mts` shows as a rename.
- Declared deviations, none wrong: `lib: ["ES2023"]` in tsconfig.cli.json (needed for `useGrouping: 'always'`), `matchProduct` exported from matching.ts, ids generated by default rather than always, ean raw value stored trimmed with its hyphens, the shop-count `p` placed in the offers section.
- No undeclared deviation found. package-lock.json: 85 packages added, none removed, none changed in version; the large diff is reordering.
- `drizzle-kit` ^0.31.11 is the one new devDependency, surfaced by 01-design for the human's build stop.

## Reuse and seams

One copy each, by grep over src/ and by tests/unit/seams.test.ts:

- Visibility scope: src/server/visibility.ts only. The flags `isApproved`, `isHidden`, `inReview` appear in src/db/schema, visibility.ts, src/server/seed and src/server/importer and nowhere else; the product read function calls `visibleProductWhere()` and `visibleOfferWhere()` and restates no flag.
- Importer write path: src/server/importer/index.ts is the only writer of products and offers from outside data; the seed writes no products and no offers.
- Matcher: src/server/matching.ts (`parseEan`, `normalizePartNumber`, `normalizeBrand`, `matchProduct`); the importer calls it, nothing else normalises.
- Money: src/server/money.ts; `grep` for parseFloat, toFixed, Math.round, `* 100` and `/ 100` finds only the two lines in that file.
- Fetch and file reads: src/server/importer/source.ts is the only `fetch(`; `node:fs` appears only there and in src/db/migrate.ts. No HTTP client import in src/.
- Reuse of slice A: getDb, closeDb, readRequiredEnv, the entrypoint `case`, and the existing `no-restricted-imports` block (the new override repeats the scraping patterns, pinned by tests/unit/eslint-guardrails.test.ts).

## Guardrails by seam

- Guardrail 1 (admin decides): feeds and shops default to not approved; products and offers default to not hidden. The public read applies the one scope. tests/integration/visibility.test.ts removes an offer by each of feed unapproved, shop unapproved, offer hidden and offer in review, alone and with a second offer present; hidden product, no offers and unknown slug return null. The seed is insert-only and approves only the demo shops and `is_demo` feeds it creates; tests/integration/seed.test.ts and importer-preservation.test.ts prove an admin's un-approve or hide survives a second seed and import, and that a hidden product's new offers stay invisible. The importer's offer upsert lists exactly price_cents, url and price_updated_at. An unapproved feed is reported skipped and its source is not read.
- Guardrail 2 (no scraping): the importer takes feed ids and rows, never a free URL or path; `demo-feed:` works only for `is_demo` rows and a `^[a-z0-9-]+\.csv$` name read from demo/feeds; other schemes fail `unsupported_url`; no HTML parser exists in src/; the lint ban is regression-tested for src/server and scripts, and the override that disables `@/` repeats it. One SHOULD_FIX on redirects, see § Findings.
- Guardrail 3 (roles): no new route, no admin surface; the route classification test from slice A still passes with `/producto/[slug]` under `(public)`. Nothing new to violate.
- Guardrail 4 (money): `price_cents integer` with a `> 0` check; no real, double, numeric or money column in 0000_init.sql (seams test and schema test); parse by digit handling, more than two decimals rejected not rounded; IVA included is an assumption of the demo feeds that the first real feed slice must check (01-design risk).
- Guardrail 5 (RGPD): the page and the 404 carry no Set-Cookie (curl, e2e, real browser); no foreign origin; CLI mains print only counts, ids, shop names, codes, and on failure only an error code (src/cli/shared.ts); the app container log holds the migrate and seed lines and Next's own localhost lines; the importer output and `app seed --if-enabled` print no URL (tests/integration/importer-logging.test.ts, tests/e2e/entrypoint.spec.ts, my run). No click log exists yet.

## Checks from 01-design

- C-11 against the page's imports and the tests' toEqual: pass, see § Contract alignment.
- One copy each of visibility, importer write path, matcher, money helper: pass, see § Reuse and seams.
- Guardrails 1, 2, 4, 5 by seam: pass, see § Guardrails by seam.
- Log output free of URLs: pass. `docker compose logs app` shows only `http://localhost:3000` and `http://0.0.0.0:3000` from Next's start-up banner, which are not feed, database or shop URLs; import-feeds output grepped for `https?:`, `demo-feed`, `.example`, `postgres`: none.
- `dist/` and `.env` untracked: pass. `git ls-files` lists only `.env.example`; `git check-ignore -v` names `.gitignore` lines 8 and 2.
- `drizzle-kit generate` reports no schema drift: pass. Run against a copy of src/db/migrations outside src/ (path removed afterwards): "No schema changes, nothing to migrate", and the copy was identical to the committed directory.
- Image builds cold: pass. `docker compose build --no-cache app` exit 0, the `npm ci`, `npm ci --omit=dev`, `next build` and `tsc -p tsconfig.cli.json` steps all ran.
- `npm run gate` run by me: pass, exit 0.

## Acceptance lines, slice B

From 2026-10-16-tracer-bullet/01-product.md § Slice boundary, "Acceptance as observable behaviour":

- 1. Compose up starts app, db and umami with demo data and no network access: MET as ruled by the owner (D-2 Q-2). Evidence: stack:up Healthy for the three services; app log `migrate: up to date` then `seed: networks=0 shops=0 feeds=0 categories=0` on a re-start; the importer reads demo/feeds from the image with no fetch (tests stub fetch to throw). Products appear after `import-feeds`; CLAUDE.md § Commands says so.
- 2. `import-feeds` prints counts and rejected rows; a second run leaves the same products and offers: MET. Evidence: my run printed `offers_updated=2` per feed, `products_created=0`; tests/integration/importer-demo.test.ts (3 products, 4 offers, then unchanged), tests/unit/import-report.test.ts, tests/e2e/entrypoint.spec.ts; rejected rows are printed as `record N: code (field)`.
- 3. Shared-EAN page lists at least two shops cheapest first with price, updated date and shop count: MET. Evidence: curl of /producto/demo-filtro-de-aceite-oc-1234 returned 200; tests/e2e/product.spec.ts asserts `11,49 €` before `12,99 €`, `2 tiendas` and the date shape; tests/integration/product-page.test.ts asserts the order and the tie-break.
- 4. Single-shop product shows the one-shop wording: MET. Evidence: e2e asserts `1 tienda` for the other two demo slugs; the ICU plural has `one` and `other`.
- 5. An offer from an unapproved feed, a hidden offer or a hidden product is not visible on any public page; a test covers each: MET. Evidence: tests/integration/visibility.test.ts, one test per state, plus shop unapproved and in-review. The page-level mapping from null to 404 is covered by the unknown-slug and malformed-slug e2e, not by a hidden-product browser test (no admin exists to flip a flag).
- 6. CLAUDE.md § Commands lists the gate commands and all of them pass: MET. Evidence: every script name in the table exists in package.json; the gate exits 0. One wording drift, see § Findings F-2.
- 7. The page sets no cookie and nothing is logged with an email, token or password: MET. Evidence: curl shows no Set-Cookie on 200 and 404; e2e `expectNoSetCookie` and an empty `context.cookies()`; importer-logging test and cli-shared test show codes only.

## Findings

No BLOCKING finding.

- F-1 SHOULD_FIX, lane backend, src/server/importer/source.ts (the `fetch(parsed, { signal })` call): no `redirect` option, so the default follows redirects; an `https:` feed URL can redirect to `http:` or to another host and the https-only rule of C-16 and 0007 is then not enforced on the final target. 02-backend's risks say "a redirect target is still https only", which is not what `fetch` does. Satisfied by `redirect: 'error'` (a redirecting feed fails as `fetch_failed`) or by re-checking `response.url` for https, plus one case in tests/unit/feed-source.test.ts (test lane).
- F-2 SHOULD_FIX, lane docs, CLAUDE.md § Commands (first-run paragraph on SEED_DEMO_DATA): the quoted message "no approved feed: set SEED_DEMO_DATA=true in .env and run docker compose up -d" is not the text tests/e2e/global-setup.ts throws ("e2e setup: the import found no approved feed. Set SEED_DEMO_DATA=true in .env and run: docker compose up -d"). 05-docs flagged that it had not opened the file. A reader grepping the quoted text finds nothing. Satisfied by quoting the shipped sentence.
- F-3 SHOULD_FIX, lane test, tests/e2e/global-setup.ts: only the success path ran in the gate; the `feeds=0` branch that proves the start-up seed path, and the failed-import branch, are unexercised, and 04-test made no mutation check of the new suites. Not wrong, thin. Satisfied by a unit test that runs the setup with a stubbed `spawnSync` result, or by saying in the testing pack that these branches are manual.

## Coverage adequacy

- The guardrail 1 tests change one flag on an otherwise visible row and assert on the difference, so a scope that dropped any one condition fails a named test; they would not pass after the requirement changed.
- The contract test uses `toEqual` on the whole value, so adding `url` or an id breaks it; a separate test pins that the affiliate URL is never in the JSON.
- The money tests include the float traps (`1.005`, `0.29`, `1.1`) and the U+00A0 normalisation; the schema test queries `information_schema` for column types rather than reading source.
- The seams test is a source scan and its own comment calls it a tripwire; it states that a flag inside a string or a multi-line import could slip past. Accepted: the database-level and function-level tests carry the behaviour.
- Page-level hiding is proven on the read function, the 404 mapping on unknown and malformed slugs; a hidden-product browser test needs the admin slice.
- Guardrail 5 on `/go` has no test because no route exists; correctly deferred.
