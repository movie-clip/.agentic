REPORT 2026-10-17-mvp-backlog/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only recon order, no command named

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Shipped surface is exactly: one product page, the importer (CSV, EAN-only matching), demo seed, Compose, gate. Everything else in mvp.md is ABSENT; see § Capability map.
  - Data model already done: networks, shops, feeds, categories, products, offers. Everything else (clicks, price history, import runs, category mapping, admin users, images, alias, ranking) is absent; see § Schema inventory.
  - Slice B design pre-declared the absent tables as "each an additive migration for its own slice": 01-design.md § Schema and visibility states, "Deliberately absent".
  - Prior artifacts' unbuilt-slice mentions are collected in § Proposed but not built.
  - The 17 CARRIED/OPEN ledger rows from both runs are listed one per bullet in § Open ledger rows.
  - Only one migration exists (src/db/migrations/0000_init.sql); a merged migration is never edited (backend pack rule quoted in 01-design.md § Pack corrections owed).

skill_calls:
  - none

risks:
  - I did not open src/components/*.tsx, messages/es-ES.json, Dockerfile, docker-entrypoint.sh, eslint.config.mjs or any tests/ file; test coverage claims rest on filenames plus 01-design.md § Tests owed and 06-integration.md.
  - I did not read the 2026-10-17-mvp-backlog run.md or tracker.md, nor GitHub issues or Project 3; whether tickets already exist for any ABSENT item is not established here.
  - Whether a 0000_init.sql column list matches schema/*.ts exactly was not diffed; I read the schema TS and the design's description, and 06-integration reports drizzle-kit generate with no drift.
  - Nothing in src/ names Umami; I could not confirm from src whether the page includes a tracker. The brief (Q7) says it is not embedded; grep of src for "umami" returned zero matches.
  - The Open table of the 2026-10-16 run still lists rows (e.g. Vite ESM warning, init-env test) that the 2026-10-17 run's Closed table says were absorbed; I list them under § Open ledger rows with that note, not as live.
  - Feed prices are assumed IVA-inclusive in all current code; no real feed has ever been read (01-design.md risks 2).

## Orchestrator brief
- Premise check: the repo is a slice-A+B tracer bullet. Ships: skeleton, Compose (app/db/umami), gate, 6-table schema, demo seed, `import-feeds` CLI (CSV only, EAN matching only), one product page `/producto/<slug>`. Nothing else is public.
- Public routes today: `/` (stub heading), `/producto/[slug]`, `/api/health`, not-found. No search, category page, listing, sitemap, robots, JSON-LD.
- No admin of any kind exists: no auth, TOTP, accounts, admin routes, or UI to approve, hide, map, import. `src/server/auth/` does not exist. Approval and hide flags exist only as columns that nothing but the demo seed writes.
- No `/go` redirect, no clicks table, no buy link on the page (offers.url stored, deliberately never read publicly).
- Matching: only EAN attach and new-product; brand+part-number, alias table, review queue, merge, split are ABSENT. `offers.in_review` column exists but nothing writes it.
- Importer gaps vs mvp.md: no removal of offers missing from latest import, no import report storage, no XML or gzip, no per-network mapping, no redirect policy.
- Product has no `category_id`; no feed-category mapping; no image storage or upload; no price history; no "no offers right now" state (product with no visible offer returns 404); no shop ranking.
- Delivery: Compose runs locally only; no VPS, domain, TLS, reverse proxy, backups, or production Umami hardening exists.
- Sections below: Capability map (per mvp.md heading: SHIPPED/PARTIAL/ABSENT with evidence) · Schema inventory · Proposed but not built · Open ledger rows · Sources of truth
- Blocks dispatch: nothing. Note for the planner: mvp.md headline target (3 approved feeds, 10k indexed products) needs real feeds, which no code has ever read; that is a data fact, not a code fact.

## Capability map

Paths are under C:\projects\investments\los-tres. Status key: SHIPPED, PARTIAL, ABSENT.

| mvp.md heading | Status | Evidence and what is missing |
|---|---|---|
| Name (site name is config) | SHIPPED | src/config/site.ts:10-12 `getSiteName()` reads `SITE_NAME`; compose.yaml:12 requires it; used in src/app/(public)/page.tsx:11 and product page metadata (page.tsx:25). |
| Audience and language (es-ES, messages files, no public accounts) | SHIPPED | messages/es-ES.json; src/i18n/request.ts (timeZone Europe/Madrid); src/app/(public)/page.tsx:8 uses `getTranslations`. No login for public exists. Only Spanish. |
| Catalogue scope: categories (fixed tree, admin-defined, feed category mapped once, unmapped queue) | PARTIAL | `categories` table with parent_id, slug, name, position: src/db/schema/catalogue.ts:16-25. Demo tree of 2 roots / 5 children seeded: src/server/seed/index.ts:65-91, data in src/server/seed/demo-data.ts. Missing: `products.category_id` (absent from catalogue.ts:27-48), feed-category mapping table, unmapped queue, admin editing, any read of categories (01-design.md says "read by nothing in B"), the real ~30-node tree. |
| No vehicle fitment | SHIPPED (by absence) | no fitment code or column. |
| Product and offers: one product many offers, sorted by price, shop/price/"updated on" | SHIPPED | src/server/catalogue/product-page.ts:47-86 (ORDER BY price_cents, shop name, offer id at :68); page src/app/(public)/producto/[slug]/page.tsx:30-66; components OfferList/ProductDetails/ImagePlaceholder. |
| Product: single-offer shown, "1 shop" wording | SHIPPED | page.tsx:55 `shopCount` ICU plural (`one {# tienda}`) per 01-design.md C-14. |
| Product: price is cents EUR IVA included, no shipping | SHIPPED | offers.price_cents integer + check > 0: catalogue.ts:63,76; src/server/money.ts (parseDecimalToCents, formatEuroCents); page.tsx:60. IVA inclusion in real feeds unverified. |
| Product: text from feeds, admin shop ranking decides winner | PARTIAL | Text is first-wins, immutable: importer index.ts:189 `createProduct`, TD-23. Missing: shop ranking column or table, text-merge logic, any admin control. |
| Product: images uploaded by admin, category placeholder until set | PARTIAL | Single generic placeholder: src/components/ImagePlaceholder.tsx, page.tsx:49 imageLabel. Missing: image column/table, upload route, storage volume (0004 says a Docker volume behind a storage interface; compose.yaml has only `db-data`), per-category placeholders. |
| Price history (one point per day, lowest offer, chart) | ABSENT | no table (01-design.md "Deliberately absent: price_history"), no job, no chart component. |
| Product with no offers keeps page, "No offers right now" with last known lowest price | ABSENT | product-page.ts:70-71 returns null (404) when no visible offer; visibility.ts:37 defines a product as public only with a visible offer. Needs last-known-price storage (no column) and a changed public rule. mvp.md vs current visibility.ts contract disagree on this point. |
| Matching: EAN first | SHIPPED | src/server/matching.ts:22-38 `parseEan` (GS1 check digit), :64-85 `matchProduct`; ean_normalised index catalogue.ts:45. |
| Matching: brand + part number | PARTIAL | Normalisers exist (matching.ts:41-50) and both normalised columns are stored (catalogue.ts:34,36), written at importer index.ts:209-211. No lookup: matching.ts:8-10 says step 2 "has no code path yet". TD-25: rows without valid EAN each create their own product. No index on (brand_normalised, part_number_normalised). |
| Matching: EAN/brand conflict to review queue | PARTIAL | Conflict detected (matching.ts:77-83) but the row is rejected into the import report (index.ts:162-165), not queued; nothing is created. `offers.in_review` (catalogue.ts:69) exists and is honoured by visibility.ts:25, but nothing writes it. No queue table or UI. The other 0008 conflict (EAN→one product, brand+part→another) is absent. |
| Matching: admin merge and split; decisions stored and re-applied; old URL redirects | ABSENT | no merge/split code, no decision table, no redirect route. Slug stability was designed for it (TD-30). |
| Matching: brand alias table | ABSENT | 0008 step 2 requires it; "brand_aliases" listed as deliberately absent in 01-design.md. |
| Search (full text incl. EAN and part number) | ABSENT | no search route, query, tsvector or trigram index; only ean_normalised btree index. |
| Category pages with brand/price/shop filters | ABSENT | no category route; products have no category link. |
| Browsing: home / product listing | ABSENT | src/app/(public)/page.tsx is a heading and tagline only. |
| SEO: server-rendered product page | SHIPPED | page.tsx is a server component, `force-dynamic`; generateMetadata at :19-28 (title, description). |
| SEO: schema.org Product / AggregateOffer JSON-LD | ABSENT | grep for ld+json, schema.org, AggregateOffer in src returned no matches. |
| SEO: sitemap, robots, canonical, indexing | ABSENT | no sitemap/robots route or file; deferred in 01-product.md § Slice boundary ("structured data, sitemaps and indexing work"). |
| Data sources: affiliate feeds only, no scraping | SHIPPED (guardrail) | src/server/importer/source.ts is the only fetch/file reader (:3-8 comment, :34-60); lint ban + tests/unit/eslint-guardrails.test.ts and seams.test.ts. Real network feeds never exercised. |
| Data sources: first shops (Awin, Kwanko, Effinity programmes) | ABSENT | only fictional demo network "Red demo" and two demo shops (01-design.md C-18). No network applications, no real rows. Per-network CSV/XML column mapping absent (design "Not in B"). |
| Data sources: shops upload own feed later, model must allow | SHIPPED (model) | pgEnum feed_source_type ('affiliate_network', 'shop_upload'): sources.ts:13, feeds.source_type :39. No upload feature. |
| Shops and feeds are data: networks, shops, feeds, link patterns as rows | PARTIAL | tables networks/shops/feeds exist: sources.ts:15-54; seeded by src/server/seed/index.ts. Missing: shop logo (design: absent), affiliate link pattern column (offers.url stores the feed's own link only), feeds.format, any admin screen to enter them. Feed URL may embed API key (sources.ts:40-41, TD-36). |
| Feed import: `import-feeds` command reads each approved feed, validates every row | PARTIAL | src/cli/import-feeds.ts:13-35 (`--feed <id>`); importer index.ts:44-62; validate.ts, csv.ts. CSV only (hand-written parser, Q-1); XML and gzip absent; real https fetch exists (source.ts:51-56) but untested against any network. |
| Feed import: import report the admin can read | PARTIAL | Printed to stdout only: src/server/importer/report.ts, types.ts RejectCode. TD-39: not stored. No import_runs table, no admin view. |
| Feed import: "Import now" button (per feed or all) running the same code | ABSENT | no admin route, no server action. importFeeds(db, {feedId}) is the reusable function. |
| Feed import: one broken feed never stops others; never takes site down | SHIPPED | one transaction per feed, failures caught per feed: index.ts:58-60, :119-124; tests/integration/importer-isolation.test.ts. |
| Feed import: offer missing from latest successful import is removed | ABSENT | importer only upserts (index.ts:224-245); no delete or mark pass. 01-design.md "Not in B: removal of offers missing from a later import". |
| Feed import: re-run idempotent, prices and dates updated | SHIPPED | upsert on (feed_id, external_id) updates price_cents, url, price_updated_at only: index.ts:241-244. |
| Admin: accounts for three members created by a command, no sign-up | ABSENT | no users table, no CLI verb (entrypoint verbs are only server, migrate, seed, import-feeds; anything else exits 64). |
| Admin: email + password + TOTP login, server-side role check | ABSENT | grep for login/totp/session/password in src finds only comments. Role check is "convention only": directory classification src/app/(public)/** vs src/app/admin/** (tests/support/routes.ts, tests/unit/route-classification.test.ts); no src/app/admin directory and no src/server/auth. Guardrail 3 tests were deferred "to the slice that adds the first admin route" (01-product.md § Slice boundary). ADR 0009 notes admin session cookie is allowed. |
| Admin: approve/disable shops and feeds | ABSENT | columns exist (shops.is_approved sources.ts:27, feeds.is_approved :43) honoured by visibility.ts:20-27 and importer (index.ts:76,103); only the demo seed sets them (seed/index.ts:44,57). No UI/action. |
| Admin: run imports, read reports | ABSENT | see "Import now" and report rows above. |
| Admin: maintain category tree, map feed categories | ABSENT | table only; no mapping table. |
| Admin: upload product images | ABSENT | no storage. |
| Admin: resolve matching review queue, merge, split | ABSENT | see Matching rows. |
| Admin: hide any product or offer | PARTIAL | columns products.is_hidden (catalogue.ts:41) and offers.is_hidden (:67) enforced by the one scope visibility.ts:20-38 and tested (tests/integration/visibility.test.ts, importer-preservation.test.ts). No UI or action sets them. |
| Admin: rank shops for text precedence | ABSENT | no column/table. |
| Visibility (guardrail 1) | SHIPPED (read side) | src/server/visibility.ts is the single scope: offer visible = feed approved AND shop approved AND not hidden AND not in_review (:20-27); product public = not hidden AND has a visible offer (:30-38). seams.test.ts pins that flags are named only in permitted files. Write side is admin-only and no admin exists. Note: mvp.md says products from approved feeds publish automatically (satisfied); the 'waiting in matching queue' product state in project.md guardrail 1 is implemented at offer level only. |
| Outgoing clicks `/go/<offer>` and click log | ABSENT | no route (design reserved src/app/(public)/go/[offer]/route.ts, 02-design.md of run 1 line 267), no clicks table; offers.url stored "for the /go slice" (catalogue.ts:64) and PublicOffer.offerId carries the id (product-page.ts:12-14); page renders no link by design (D-1 Q4). 06-integration.md line 147: guardrail-5 /go test "correctly deferred". |
| Analytics: self-hosted Umami, cookieless | PARTIAL | umami service in compose.yaml:48-65 (image postgresql-v2.20.2, loopback port, db `umami` created by docker/db-init/01-umami.sql). Tracker script not embedded in any page (D-1 Q7, 01-product.md Q7); needs a site id from Umami UI. Default admin login unchanged (open row, run 1 risk). |
| Revenue / no ads | SHIPPED (by absence) | no ad code. |
| Delivery: Docker Compose locally | SHIPPED | compose.yaml (app, db, umami; loopback ports; healthchecks), Dockerfile, docker-entrypoint.sh (verbs server/migrate/seed/import-feeds, exit 64 otherwise), `npm run stack:up`; `npm run gate` passing per 2026-10-17 06-integration. |
| Delivery: EU VPS with domain, live site for network review | ABSENT | nothing in repo: no prod compose overrides, reverse proxy/TLS, domain config, backup, deploy docs, or CI (no .github). 0004 says provider/domain chosen by owner later. Compose binds 127.0.0.1 only (compose.yaml:3,10,33,52). |
| Delivery: gate (ESLint, tsc, Vitest, Playwright) | SHIPPED | `npm run gate` per CLAUDE.md § Commands; ADR 0006; 54 test files under tests/ (unit, integration, e2e, support). No CI workflow in repo (.github absent). |

Out-of-MVP items (ads, public accounts, shipping, fitment, tyres, Amazon, Icecat, scheduling, other languages): none implemented, consistent with mvp.md § Out of MVP.

Route inventory in src/app: `(public)/page.tsx` (stub home), `(public)/producto/[slug]/page.tsx`, `(public)/api/health/route.ts`, `not-found.tsx`, `layout.tsx`, `globals.css`. Components: SiteHeader, ImagePlaceholder, ProductDetails, OfferList.

## Schema inventory

Source: src/db/schema/index.ts re-exports catalogue.ts and sources.ts. One migration: src/db/migrations/0000_init.sql (+ meta/_journal.json, 0000_snapshot.json). All timestamps timestamptz default now(); all FKs on delete restrict.

- `networks` (sources.ts:15): id, name, slug unique, created_at.
- `shops` (sources.ts:22): id, name, slug unique, is_approved bool default false, created_at. No logo, no ranking, no link pattern.
- `feeds` (sources.ts:31): id, shop_id FK, network_id FK nullable, source_type enum (affiliate_network | shop_upload), url, is_approved default false, is_demo default false, created_at. Unique (shop_id, url); check affiliate_network requires network_id. No format, no last-import timestamp, no status, no link pattern.
- `categories` (catalogue.ts:16): id, parent_id self-FK, slug unique, name, position, created_at.
- `products` (catalogue.ts:27): id, slug unique with format check, title, brand, brand_normalised, part_number, part_number_normalised, ean, ean_normalised (indexed), description, is_hidden, created_at. No category_id, image, status, merged_into.
- `offers` (catalogue.ts:50): id, product_id FK, feed_id FK, external_id, price_cents integer > 0, url, is_hidden, in_review, price_updated_at, created_at. Unique (feed_id, external_id); index on product_id. No shop_id (shop reached via feeds.shop_id), no last_seen_at / removed marker.
- Pg enum: `feed_source_type`.
- Not present as tables or columns (each named by 01-design.md as deliberately absent, or simply not mentioned): import_runs, price_history, feed_categories / category mapping, products.category_id, brand_aliases, feeds.format, shops.logo, admin users, clicks, image storage, shop ranking, review-queue/merge/split decision store, last-known-price, search index/tsvector.

## Proposed but not built

- 2026-10-16-tracer-bullet/01-product.md § Slice boundary "Out of this slice": admin area (login, TOTP, feed approval, Import now, report UI, category mapping and unmapped queue, image upload, hide controls, shop ranking).
- Same § : matching queue, brand + part number matching, brand alias table, merge and split.
- Same § : `/go/<offer>` redirect and click log, and any outbound link.
- Same § : price history and chart.
- Same § : "No offers right now" state and removal of offers missing from the latest import.
- Same § : search, category pages and filters, home page and any listing.
- Same § : schema.org Product/AggregateOffer, sitemaps and indexing work.
- Same § : per-category image placeholders.
- Same § : embedding the Umami tracker.
- Same § : real affiliate feeds, real shops, network applications, VPS, domain and deployment.
- 2026-10-16-tracer-bullet/01-product.md § Sequence "Candidate later slices, for the human to order": (1) /go redirect and click log; (2) admin login and feed approval; (3) matching queue, import report in admin, Import now; (4) search and category pages, then structured data; (5) VPS deployment.
- 2026-10-16-tracer-bullet/02-design.md § Seams (line 262-267): visibility, importer, matching, money were "deferred to B" (now built); Role check "convention only, src/server/auth/ waits for the first admin route"; click log "deferred (later than B)" at src/app/(public)/go/[offer]/route.ts.
- 2026-10-17-tracer-bullet-b/01-design.md § Schema and visibility states "Deliberately absent, each an additive migration for its own slice": import_runs, price_history, feed_categories and any mapping, products.category_id, brand_aliases, feeds.format (CSV only), shops.logo, admin users, clicks.
- 2026-10-17-tracer-bullet-b/01-design.md § Importer and matching rules "Not in B": removal of offers missing from a later import, price history, import-report persistence, XML, per-network column mapping, gzip.
- 2026-10-17-tracer-bullet-b/01-design.md TD-25 and TD-23: cross-shop merging of no-EAN rows waits for brand + part-number matching; shop ranking deciding text wins arrives later.
- 2026-10-17-tracer-bullet-b/01-design.md TD-39: persisting the import report "belongs with the admin Import now slice".
- 2026-10-17-tracer-bullet-b/01-design.md § risks: encrypting or masking feed URLs holding API keys is "an admin-slice concern"; `offers.in_review` may be replaced by a product-level state in the matching-queue slice (additive migration); first real feed slice must check each network's IVA field.
- 2026-10-17-tracer-bullet-b/02-backend.md (line 93): strict redirect handling for https feed fetch is "a later feed-slice choice".
- 2026-10-17-tracer-bullet-b/04-test.md (line 46): seams.test.ts allow-list for `fetch(` and `node:fs` must be extended by any slice needing either.
- 2026-10-17-tracer-bullet-b/06-integration.md (line 147): guardrail 5 test for /go deferred until the route exists.
- 2026-10-16-tracer-bullet/decisions.md D-1 Q7: Umami runs, tracker not embedded; D-1 Q4: no outbound link until /go exists.
- docs/decisions/0004 Decision: admin-uploaded images stored on a Docker volume behind a storage interface (not yet in compose.yaml).
- docs/decisions numbering gap: 0003 and 0005 do not exist in docs/decisions/ (files present: 0001, 0002, 0004, 0006-0011); I did not find why.

## Open ledger rows

Ledger 2026-10-17-tracer-bullet-b/run.md § Open (all CARRIED; run CLOSED):

- should_fix, 06-integration.md § handoff F-1: importer https fetch has no redirect policy (https to http or other host).
- should_fix, 06-integration.md § handoff F-3: tests/e2e/global-setup.ts failure branches (feeds=0, failed import) unexercised; no mutation check of the new suites.
- risk, 06-integration.md § risks: npm audit shows 9 dev-only advisories via drizzle-kit; `--omit=dev` shows 0.
- should_fix, 08-protocol-lint.md § handoff SHOULD_FIX: 8 pack style items (5 carried from last run, 3 new).
- risk, 08-protocol-lint.md § risks: CRLF tips disagree (backend/frontend packs say use Edit; testing.md says multi-line Edit fails).

Ledger 2026-10-16-tracer-bullet/run.md § Open (all marked CARRIED there; the 2026-10-17 run's Closed table records the "absorbed" ones):

- risk, 03-backend.md § risks 5: Umami default admin login must be changed before the VPS slice. Still live (not in the 10-17 Closed table).
- risk, 03-backend.md § risks 4: npm audit, 5 high in dev-only lint chain, fix is breaking. Succeeded in practice by the 10-17 audit row above (9 dev-only via drizzle-kit); status unclear.
- risk, 04-frontend.md § risks 2: Spanish copy is the lane's own wording; owner to review. Still live; slice B added more Spanish copy (Product namespace).
- should_fix, 07-integration.md § handoff 3: Vite ESM warning / package.json type. Closed by 10-17 (vitest.config.mts, TD-16).
- should_fix, 07-integration.md § handoff 4: init-env.mjs and entrypoint exit 64 untested. Closed by 10-17 (init-env.test.ts, entrypoint.spec.ts).
- should_fix, 07-integration.md § handoff 5: TD-10 scraping-lib lint ban has no regression test. Closed by 10-17 (eslint-guardrails.test.ts).
- should_fix, 07-integration.md § handoff 6: e2e base-URL rule written twice. Closed by 10-17.
- contract_note, 08-docs.md § contract_notes 1: CLAUDE.md § Stack omits npm/Node 22; owner may add (0010 records them). CLAUDE.md § Commands now says "npm and Node 22" at its head; the Stack list itself still carries no npm/Node line. Not recorded as Closed in the 10-17 ledger.
- decision, 08-docs.md § handoff 2: owner to pick a styling system before slice B. Closed by 10-17 D-1 (CSS Modules, decision 0011).
- should_fix, 09-protocol-lint.md § handoff SHOULD_FIX 1-2: testing.md 900-char paragraph; base-URL rule twice. Not in the 10-17 Closed table; the 10-17 row "8 pack style items (5 carried from last run)" appears to subsume them.
- should_fix, 09-protocol-lint.md § handoff SHOULD_FIX 3-4: frontend.md long multi-fact bullets; site-name rule twice. Same note.
- should_fix, 09-protocol-lint.md § handoff SHOULD_FIX 5: backend.md § Layout multi-fact paragraphs; pins as a table. Same note.

## Sources of truth

- docs/product/mvp.md: approved scope, dated 2026-10-16; current, and the checklist this map follows. Contradiction to note: mvp.md "page stays when a product loses all offers" vs src/server/visibility.ts:30-38 and product-page.ts:70-71 (404 when none visible), the latter documented as TD-31 in 2026-10-17-tracer-bullet-b/01-design.md.
- docs/decisions/: 0001 Next.js/TS, 0002 PostgreSQL/Drizzle, 0004 Compose (revised 2026-10-16 for VPS), 0006 gate, 0007 feeds/no scraping, 0008 matching (queue, merge, split, alias table), 0009 click log and Umami, 0010 slice A tooling calls, 0011 CSS Modules. 0003 and 0005 absent. All look current for what they cover; 0008 and 0009 describe features not built.
- CLAUDE.md: current for commands and first-run (updated in the last commits, 0220ea8 and 4e20a47). § Stack omits npm/Node line (see open row).
- Run artifacts: 2026-10-16-tracer-bullet/01-product.md (slice boundary, sequence), 02-design.md (seams), 2026-10-17-tracer-bullet-b/01-design.md (schema, contracts C-11 to C-18, TD-16 to TD-42, tests owed), 06-integration.md (gate PASS evidence). The ledgers' § Open tables are as quoted above.
- Tracker: GitHub Project 3 is named canonical in CLAUDE.md but I did not read it.
- Git state at read: branch 6-tracer-bullet-slice-b, clean; last commit 0220ea8 "#6 Record CSS Modules as decision 0011". Slice B work is on this branch; whether PR for #6 is merged I did not check (the run ledger says run CLOSED).
