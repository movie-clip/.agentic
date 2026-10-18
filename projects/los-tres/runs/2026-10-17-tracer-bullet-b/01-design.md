REPORT 2026-10-17-tracer-bullet-b/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only design order, no command named

contract_notes:
  - src/db/schema/** and the first migration define the tables the importer, seed, visibility scope and read function share; column-level spec in § Schema and visibility states.
  - src/server/catalogue/product-page.ts exports `PublicProductPage` and `PublicOffer`, the one backend/frontend contract; the page and the tests import the type, see § Contract.
  - messages/es-ES.json gains a `Product` namespace; key names are fixed in § Contract and consumed by tests/unit/messages.test.ts and the e2e specs.
  - `.env.example`, `compose.yaml`, `docker-entrypoint.sh` and CLAUDE.md § Commands must agree on `SEED_DEMO_DATA` and on the verbs `migrate`, `seed`, `import-feeds`; see § Paths: migrate, seed and import-feeds.
  - The canonical feed CSV layout and the demo EANs, slugs and prices in § Contract are consumed by demo/feeds/*.csv, tests/fixtures/feeds and every importer test.
  - vitest.config.ts becomes vitest.config.mts and tsconfig.json `include` gains `**/*.mts`; the rename needs an orchestrator step, see § Handoff items from the last integration.
  - tests/support/global-setup.ts now drops, recreates and migrates the test database on every run; every integration test file depends on it, see § Paths: migrate, seed and import-feeds.

pack_corrections:
  - backend.md — layout, migrations, CLI build, relative-import rule, seams and seed rules are now concrete; exact wording in § Pack corrections owed (backend.md).
  - frontend.md — styling is CSS Modules (D-1), the `1.234,50 €` example needs `useGrouping: 'always'` and a non-breaking space, pages may import src/server; wording in § Pack corrections owed (frontend.md).
  - testing.md — global setup drops and migrates, reset helper, e2e data comes from `docker compose run import-feeds`, base URL has one source; wording in § Pack corrections owed (testing.md).
  - architecture.md — § The seams the product forces now has concrete paths for visibility, importer, matching and money; wording in § Pack corrections owed (architecture.md).

handoff:
  - Dispatch order 02 backend, 03 frontend, 04 test, 05 docs (CLAUDE.md § Commands), then integration, then close docs; fences and verification commands in § Lane split.
  - No owner question blocks dispatch. Two non-blocking questions carry my recommendation in § Owner questions; the plan is written to the recommendation.
  - Orchestrator step before the test lane: `git mv vitest.config.ts vitest.config.mts` (lanes cannot rename). Backend must have added `**/*.mts` to tsconfig include first.
  - At the human's build stop, surface one new devDependency: `drizzle-kit`. It is the migration tool of the recorded Drizzle choice (0002) and 02-design listed it for B, so it is not an owner question.
  - Existing local `.env` files predate `SEED_DEMO_DATA`; `env:init` will not overwrite them. The gate fails with a named message until the owner adds `SEED_DEMO_DATA=true` and runs `docker compose up -d`. Docs lane writes this into CLAUDE.md § Commands.
  - Open rows 3, 4, 5 and 6 from 07-integration are assigned in § Handoff items from the last integration.
  - Close docs: record decision 0011 (CSS Modules, from this run's D-1) plus a CLAUDE.md § Stack line, then apply the pack corrections in § Pack corrections owed.

skill_calls:
  - none

risks:
  - The pack's `1.234,50 €` example is wrong for plain `Intl.NumberFormat('es-ES')`: CLDR gives `1234,50 €` for four digits, and the separator before `€` is U+00A0. Verified with node 22.20. The plan forces `useGrouping: 'always'`; tests must normalise U+00A0.
  - Feed prices are assumed to include IVA. No network has been contacted and no real feed read, so this is an unverified market fact; the demo feeds are ours. The first real feed slice must check each network's field.
  - `offers.in_review` is a column nothing writes in B. I include it so the one visibility scope encodes all of guardrail 1 now. The matching-queue slice may prefer a product-level state; that would be an additive migration. A reviewer may call it speculative.
  - The CLI runs from tsc output with `--conditions=react-server` and needs relative imports in src/{cli,config,db,server}. A scratch prototype (client.ts closure, node16 CJS, outside the repo) compiled and passed `server-only`; the full closure and the image were not built. An `@/` import would only fail inside the image, so the lint rule is load-bearing.
  - flat-config `no-restricted-imports` overrides do not merge. The new relative-import override must repeat the scraping-library patterns or it silently drops the guardrail 2 ban for src/server. The lint-ban test in § Tests owed covers both.
  - Page-level hiding is not browser-tested: no admin UI exists to flip a flag and tests must not write the dev database. Visibility is proven on the read function; the page maps `null` to `notFound()`, covered by an unknown-slug e2e.
  - 0004 says demo data loads on first start so the site works locally. This plan loads categories, shops and feeds on start and leaves the first import manual, following the brief and mvp.md (imports run when someone starts them). Q-2 in § Owner questions is the owner's call.
  - `drizzle-kit` and every other version were not installed or verified in this session. The backend lane pins a release compatible with drizzle-orm 0.45.4 and confirms `generate` runs before anything else.
  - Images grow: the runner stage now carries the full production node_modules so the CLI can load drizzle's migrator and `pg`; the alternative is bundling with esbuild, a new dependency, left out.
  - Feed URLs can embed network API keys. They are stored in `feeds.url`, never printed or logged, and the report never names them. Encrypting or masking them is an admin-slice concern.
  - One shop with two feeds carrying the same product yields two offers from one shop; the shop count shown is the number of offers. Not enforced either way in B.

## Orchestrator brief
- Verdict: slice B is buildable as briefed. No owner question blocks dispatch; § Owner questions holds two non-blocking ones (CSV parser, import-on-seed), plan written to my recommendation.
- Schema and visibility states: 6 tables, explicit `is_approved` on feeds and shops, `is_hidden` on products and offers, `offers.in_review`, `feeds.is_demo`, `feeds.source_type`; product addressed by unique slug at `/producto/<slug>`.
- Contract: `getPublicProductBySlug(slug)` returns `PublicProductPage | null`, cents and Date only; the page formats with `formatEuroCents` and next-intl; message keys, feed CSV layout and demo fixture values are fixed there.
- Paths: migrate, seed and import-feeds: npm scripts `db:generate`, `db:migrate`, `db:seed`, `import-feeds`; entrypoint verbs; `server` runs migrate then `seed --if-enabled`; test DB dropped, recreated, migrated each run.
- Importer and matching rules: EAN attach or new product, conflicts rejected into the report, one transaction per feed, approved feeds only, no URL ever printed.
- Layout and seams: one file per seam (`visibility.ts`, `matching.ts`, `money.ts`, `importer/`); CLI is tsc-compiled CommonJS, relative imports only in server-side dirs.
- Decisions: TD-16 to TD-40; the big ones are stay CommonJS (config becomes .mts), tsc-compiled CLI, seed insert-only, product text first-wins, CSS Modules.
- Lane split: 02 backend, 03 frontend, 04 test, 05 docs, integration, close docs; orchestrator runs `git mv vitest.config.ts vitest.config.mts` before 04.
- Tests owed: every brief acceptance line and guardrail 1, 2, 4, 5 mapped to a named test file; guardrail 3 has no new seam.
- Handoff items from the last integration: 3 backend plus orchestrator plus test, 4 to 6 test lane; none deferred.
- Pack corrections owed: backend.md, frontend.md, testing.md, architecture.md, wording given there.
- Blocks dispatch: nothing. Surface `drizzle-kit` as a new devDependency at the human's build stop.

## Owner questions

None of these blocks dispatch. The plan is written to the recommendation; if the owner answers otherwise, only the named lines change.

- **Q-1. CSV parsing.** Node has no CSV reader. Option (a) add `csv-parse`, one new dependency. Option (b) a hand-written RFC 4180 reader in `src/server/importer/csv.ts` (quotes, doubled quotes, CRLF and LF, embedded newlines, BOM), about 60 lines, unit-tested, no dependency. Recommend **(b) for B**: the only files read are the demo feeds we author and the test fixtures; real network feeds (gzip, delimiter variants, XML) arrive in a later slice, which is the moment to adopt a library. If (a): only `csv.ts` changes, behind the same `parseCsv(text): string[][]` signature.
- **Q-2. Should `SEED_DEMO_DATA=true` also run the first import?** 0004 reads as "the site works locally on first start". The brief and mvp.md say imports run only when someone starts them. Recommend **no**: seed loads categories, shops and feeds; one extra command, `docker compose run --rm app import-feeds`, loads products. If yes: the `server` verb runs `import-feeds` after `seed --if-enabled`, one line in `docker-entrypoint.sh`, and the e2e global setup is unchanged because import is idempotent.
- **Q-3 (informational). The public URL is Spanish: `/producto/<slug>`.** An engineering default, cheap to change (one folder name and one e2e constant). Raise it only if the owner has a URL scheme in mind.

## Schema and visibility states

Settles 01-product contract_note 2. One migration, `src/db/migrations/0000_init.sql`, generated by `drizzle-kit generate --name init` from `src/db/schema/`. Explicit column names (`integer('price_cents')`), no drizzle `casing` option, so `src/db/client.ts` needs no change. Ids are `integer` identity primary keys. Every timestamp is `timestamptz not null default now()`. No `numeric`, `real`, `double precision` or `money` column anywhere (0002, guardrail 4).

### Tables

`networks`: `id`; `name text not null`; `slug text not null unique`; `created_at`.

`shops`: `id`; `name text not null`; `slug text not null unique`; `is_approved boolean not null default false`; `created_at`.

`feeds`: `id`; `shop_id int not null references shops`; `network_id int null references networks`; `source_type feed_source_type not null` (pg enum `affiliate_network | shop_upload`, 0007); `url text not null`; `is_approved boolean not null default false`; `is_demo boolean not null default false`; `created_at`. Unique `(shop_id, url)`. Check: `source_type <> 'affiliate_network' or network_id is not null`.

`categories`: `id`; `parent_id int null references categories`; `slug text not null unique`; `name text not null`; `position int not null default 0`; `created_at`. Seeded, read by nothing in B.

`products`: `id`; `slug text not null unique` (check `slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'`); `title text not null`; `brand text null`; `brand_normalised text null`; `part_number text null`; `part_number_normalised text null`; `ean text null`; `ean_normalised text null`; `description text null`; `is_hidden boolean not null default false`; `created_at`. Non-unique index on `ean_normalised`. Raw and normalised are both stored (0002); an empty feed cell is stored as `null`, never as an empty string.

`offers`: `id`; `product_id int not null references products`; `feed_id int not null references feeds`; `external_id text not null` (the feed's own row id); `price_cents integer not null` with check `price_cents > 0`; `url text not null` (the feed's affiliate link, stored for the `/go` slice, never read by a public query); `is_hidden boolean not null default false`; `in_review boolean not null default false`; `price_updated_at timestamptz not null`; `created_at`. Unique `(feed_id, external_id)`; index on `product_id`. All foreign keys `on delete restrict`. There is no `shop_id` on `offers`: the shop is reached through `feeds.shop_id`, one source of truth.

Deliberately absent, each an additive migration for its own slice: `import_runs` (the report is printed, not stored), `price_history`, `feed_categories` and any mapping, `products.category_id`, `brand_aliases`, `feeds.format` (CSV only), `shops.logo`, admin users, clicks.

### Visibility states (guardrail 1)

| State | Column | Default | Who sets it |
|---|---|---|---|
| feed approved by an admin | `feeds.is_approved` | false | admin only; seed sets it true on demo feeds only |
| shop approved by an admin | `shops.is_approved` | false | admin only; seed sets it true on demo shops only |
| product hidden | `products.is_hidden` | false | admin only |
| offer hidden | `offers.is_hidden` | false | admin only |
| offer waiting in the matching queue | `offers.in_review` | false | the matching-queue slice; nothing writes it in B |
| demo marker | `feeds.is_demo` | false | seed only |

The single rule, implemented once in `src/server/visibility.ts`:

- An offer is **visible** iff `feeds.is_approved` and `shops.is_approved` and not `offers.is_hidden` and not `offers.in_review`.
- A product is **public** iff not `products.is_hidden` and it has at least one visible offer.
- Anything else is not served: the read function returns `null`, the page returns 404.

Nothing outside `visibility.ts`, `src/db/schema/**`, the seed and the importer may mention `is_approved`, `isApproved`, `is_hidden`, `isHidden`, `in_review` or `inReview`; a unit test scans for it (§ Tests owed). The importer and the seed may mention them only to insert defaults; neither may write them on a conflict (TD-21).

## Contract

Numbering continues slice A's C-1 to C-10.

### C-11. The read function

File `src/server/catalogue/product-page.ts`, imports `server-only`. It reads the database through `getDb()` itself and takes no `db` argument, so a page never touches the database client.

```ts
export type PublicOffer = {
  offerId: number;        // offers.id; the /go slice will need it; the page must not render a link (D-1 Q4)
  shopName: string;       // shops.name
  priceCents: number;     // integer, > 0, EUR, IVA included; never a formatted string
  priceUpdatedAt: Date;   // offers.price_updated_at
};

export type PublicProductPage = {
  slug: string;
  title: string;                // never empty
  brand: string | null;         // as received
  partNumber: string | null;    // as received (raw), e.g. "OC 1234"
  ean: string | null;           // as received (raw)
  description: string | null;   // plain text; the page must render it as text, never as HTML
  offers: PublicOffer[];        // length >= 1, visible offers only, already sorted
};

export function getPublicProductBySlug(slug: string): Promise<PublicProductPage | null>;
```

- Returns `null` for every not-public reason alike: malformed slug (not `^[a-z0-9]+(-[a-z0-9]+)*$` or longer than 120 characters, rejected before any query), unknown slug, product hidden, no visible offer. The caller cannot tell which, by design.
- `offers` is ordered in SQL: `price_cents asc, shops.name asc, offers.id asc`. The client never sorts.
- There is no `shopCount` field. The page shows `offers.length`.
- The type has exactly these keys; a test uses `toEqual`, so adding `url` or an internal id breaks it on purpose. The affiliate `offers.url` is not part of any public contract in B.

### C-12. Formatting split

- Backend returns integer cents and `Date`. It never returns a formatted amount or date.
- The page (a server component under `src/app`, which may import `src/server`) formats. Components receive finished strings and never see cents or `Date`.
- Money: one helper file `src/server/money.ts` (no `server-only` import, pure) exports `parseDecimalToCents(text: string): number | null` (backend, importer) and `formatEuroCents(cents: number): string` (frontend, page). `formatEuroCents` is `new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR', useGrouping: 'always' }).format(cents / 100)`; it throws `RangeError` for a non-integer or negative argument. The single `/ 100` lives there and nowhere else. Examples: `1999` gives `19,99 €`, `123450` gives `1.234,50 €`, with U+00A0 before `€`.
- Date: next-intl, message-driven. `src/i18n/request.ts` returns `timeZone: 'Europe/Madrid'` from `getRequestConfig`; the message is `Product.priceUpdatedOn` with `{date, date, medium}` and the page passes the `Date`. Example: `18 oct 2026`.

### C-13. Route and rendered page

- Route file `src/app/(public)/producto/[slug]/page.tsx`; `export const dynamic = 'force-dynamic'`; `params` is a `Promise` in Next 16 and is awaited. `generateMetadata` and the page call one request-cached loader: `const load = cache(getPublicProductBySlug)` with `cache` from `react`, so the database is hit once per request. A `null` result calls `notFound()` from `next/navigation`, which renders the existing `src/app/not-found.tsx` with status 404.
- The product is addressed by slug (TD-30). There is no id in the URL.
- Rendered contract, asserted on the raw server HTML with JavaScript off: `<html lang="es-ES">`; one `<main>`; exactly one `<h1>` equal to `title`; `<title>` is `Product.metaTitle`; a placeholder `<div role="img" aria-label="{Product.imagePlaceholder}">` where the image goes; a `<dl>` with a `<dt>`/`<dd>` pair for each of brand, partNumber, ean that is non-null (a null one is omitted entirely); description in a `<p>` when non-null; an element `data-testid="shop-count"` whose text is `Product.shopCount` for `offers.length`; an `<h2>` `Product.offersHeading`; a `<p>` `Product.vatIncluded`; an `<ol>` with one `<li data-testid="offer-row">` per offer in order, each holding `data-testid="offer-shop"`, `data-testid="offer-price"` (the `formatEuroCents` string) and `data-testid="offer-updated"` (the `Product.priceUpdatedOn` string).
- No `<a>` inside the offers list, no `href` to any shop or affiliate URL, no `/go` link, no third-party script, no cookie. The strings `tienda-demo-uno.example` and `tienda-demo-dos.example` never appear in the HTML. Shipping is never mentioned.

### C-14. Message keys

Added under a new `Product` namespace in `messages/es-ES.json`; the wording is the frontend lane's Spanish, the key names and placeholders are fixed. No literal site name (the slice A rule).

| Key | Placeholders | Used for |
|---|---|---|
| `Product.metaTitle` | `{title}`, `{siteName}` | `<title>` |
| `Product.metaDescription` | `{title}` | meta description |
| `Product.brand`, `Product.partNumber`, `Product.ean` | none | `<dt>` labels |
| `Product.shopCount` | `{count}` ICU plural: `one {# tienda}` / `other {# tiendas}` | the shop count line |
| `Product.offersHeading` | none | the `<h2>` |
| `Product.vatIncluded` | none | the IVA note |
| `Product.priceUpdatedOn` | `{date, date, medium}` | per-offer date |
| `Product.imagePlaceholder` | none | placeholder label |

### C-15. Canonical feed CSV layout

The one layout B reads: UTF-8, optional BOM, comma-separated, first record is the header, header names matched trimmed and case-insensitively, extra columns ignored, blank lines skipped. The record number reported for a rejected row counts the header as record 1.

| Column | Required | Rule |
|---|---|---|
| `id` | yes | the feed's own row id, trimmed, non-empty; becomes `offers.external_id`; duplicates within one feed are rejected |
| `title` | yes | trimmed, non-empty |
| `price` | yes | `^\d{1,7}([.,]\d{1,2})?$` after trim, so `19.99`, `19,99`, `12`; more than two decimals, thousands separators, signs and exponents are rejected, never rounded; the value must be > 0 |
| `url` | yes | parses as an `https:` or `http:` URL |
| `brand`, `part_number`, `description` | no | empty becomes `null` |
| `ean` | no | see C-16 |
| `currency` | no | absent is EUR; present must equal `EUR` case-insensitively |

A missing required column in the header fails the whole feed (`invalid_header`), no row is read.

### C-16. Import report and CLI output

```ts
export type RejectCode =
  | 'missing_id' | 'missing_title' | 'invalid_price' | 'invalid_currency'
  | 'invalid_ean' | 'invalid_url' | 'duplicate_id'
  | 'ean_brand_conflict' | 'ambiguous_ean';
export type RejectedRow = { record: number; code: RejectCode; field?: string };

export type FeedImportReport = {
  feedId: number;
  shopName: string;
  outcome: 'imported' | 'skipped' | 'failed';
  skipReason?: 'not_approved';
  failure?: 'fetch_failed' | 'unsupported_url' | 'invalid_header' | 'database_error';
  rows: number;
  productsCreated: number;
  offersCreated: number;
  offersUpdated: number;
  rejected: RejectedRow[];
};
export type ImportReport = { startedAt: Date; feeds: FeedImportReport[] };

export class FeedNotRegisteredError extends Error {}
export function importFeeds(
  db: Database,
  options?: { feedId?: number; deps?: ImportDeps },
): Promise<ImportReport>;
export type ImportDeps = {
  readSource?: (feed: { id: number; url: string; isDemo: boolean }) => Promise<string>;
  now?: () => Date;
};
export function formatImportReport(report: ImportReport): string;
```

`formatImportReport` is the CLI's stdout, one line per feed then one per rejected row, then a total. It prints ids, shop names, counts and codes, never a URL and never a row's content:

```
feed 1 "Tienda Demo Uno": imported rows=2 products_created=2 offers_created=2 offers_updated=0 rejected=0
feed 2 "Tienda Demo Dos": imported rows=2 products_created=1 offers_created=2 offers_updated=0 rejected=0
  record 5: invalid_price (price)
total: feeds=2 imported=2 skipped=0 failed=0
```

A skipped feed prints `feed 3 "<name>": skipped not_approved`; a failed one `feed 4 "<name>": failed fetch_failed`. Exit code: 0 when no feed failed, 1 when any feed failed or `--feed <id>` names an unregistered feed, 2 for bad arguments. Rejected rows alone never make the exit code non-zero.

### C-17. Environment and Compose

- `.env.example` gains `SEED_DEMO_DATA=true`, placed after `UMAMI_PORT` and before `E2E_BASE_URL`. `scripts/init-env.mjs` already copies non-secret values.
- `compose.yaml` `app.environment` gains `SEED_DEMO_DATA: ${SEED_DEMO_DATA:-false}`. Unset means off: a VPS that forgets the variable shows no demo shops to the networks.
- `src/config/env.ts` gains `readOptionalEnv(name): string | undefined`; new `src/config/seed.ts` exports `isDemoSeedEnabled(): boolean`, read per call, true only for the trimmed, case-insensitive value `true`.

### C-18. Demo data and fixture values

The seed and the demo files are the fixtures every lane shares. Titles say DEMO, shops are fictional, hosts use the reserved `.example` TLD, EANs use the GS1 internal-use prefix 200 (valid check digits, cannot collide with a real product).

| Item | Value |
|---|---|
| network | name `Red demo`, slug `demo` |
| shop 1 | slug `tienda-demo-uno`, name `Tienda Demo Uno`, approved |
| shop 2 | slug `tienda-demo-dos`, name `Tienda Demo Dos`, approved |
| feed 1 | shop 1, `source_type affiliate_network`, url `demo-feed:tienda-demo-uno.csv`, approved, `is_demo` |
| feed 2 | shop 2, same, url `demo-feed:tienda-demo-dos.csv`, approved, `is_demo` |
| categories | two roots with children: `automovil` (Automóvil) with `aceites-y-lubricantes`, `filtros`, `escobillas-y-bombillas`; `herramientas` (Herramientas) with `herramientas-electricas`, `herramientas-manuales` |

`demo/feeds/tienda-demo-uno.csv` (seed inserts feed 1 before feed 2, so ids are 1 and 2 on a fresh database):

| id | title | brand | part_number | ean | price |
|---|---|---|---|---|---|
| UNO-001 | DEMO Filtro de aceite OC 1234 | MarcaDemo | OC 1234 | 2000000000015 | 12.99 |
| UNO-002 | DEMO Taladro percutor 650 W | HerramientasDemo | TP-650 | 2000000000022 | 49.90 |

`demo/feeds/tienda-demo-dos.csv`:

| id | title | brand | part_number | ean | price |
|---|---|---|---|---|---|
| DOS-100 | DEMO Filtro aceite OC1234 (Dos) | MarcaDemo | OC-1234 | 2000000000015 | 11.49 |
| DOS-101 | DEMO Juego de llaves fijas 12 piezas | HerramientasDemo | LF-12 | 2000000000039 | 29.99 |

Every row also carries a Spanish `description` saying the product is fictional, `currency` `EUR`, and `url` `https://tienda-demo-uno.example/p/<id>` or `https://tienda-demo-dos.example/p/<id>`.

Expected results after the first import on a fresh database: 3 products, 4 offers, 0 rejected. Slugs: `demo-filtro-de-aceite-oc-1234` (title from the Uno row, first import wins), `demo-taladro-percutor-650-w`, `demo-juego-de-llaves-fijas-12-piezas`. The shared-EAN product lists Tienda Demo Dos (1149) before Tienda Demo Uno (1299) and shows `2 tiendas`; the other two show `1 tienda`. The second run reports `products_created=0 offers_created=0 offers_updated=2` for each feed.

## Paths: migrate, seed and import-feeds

### npm scripts (backend owns them in package.json)

| Script | Command | Purpose |
|---|---|---|
| `db:generate` | `drizzle-kit generate` | writes a migration from `src/db/schema`; no database needed. Used once here with `-- --name init` |
| `cli:build` | `tsc -p tsconfig.cli.json` | compiles `src/cli/**` and its closure to `dist/` (git-ignored) |
| `db:migrate` | `npm run cli:build && node --env-file=.env --conditions=react-server dist/cli/migrate.js` | applies migrations to the database in `.env` |
| `db:seed` | same pattern with `seed.js` | always seeds the demo data, regardless of `SEED_DEMO_DATA` (an explicit act) |
| `import-feeds` | same pattern with `import-feeds.js` | `npm run import-feeds -- --feed 1` passes the flag through |
| `typecheck` | `tsc --noEmit && tsc -p tsconfig.cli.json --noEmit` | now checks both configs |

`gate` stays `lint`, `typecheck`, `db:up`, `test`, `stack:up`, `test:e2e`; it needs no migrate step because the test database migrates itself and the app container migrates on start.

### Entrypoint verbs (`docker-entrypoint.sh`, owned by backend)

- `server` (default): `node --conditions=react-server dist/cli/migrate.js`, then `node --conditions=react-server dist/cli/seed.js --if-enabled`, then `exec node server.js`. `set -eu` stays: a failing migration ends the container, `restart: unless-stopped` retries, the healthcheck never goes green, so a broken schema is loud.
- `migrate`, `seed`, `import-feeds`: `shift`, then `exec node --conditions=react-server "dist/cli/$verb.js" "$@"`. `$verb` is already matched by the `case`, so no user text reaches the path.
- Anything else: usage line, exit 64 (unchanged from slice A).
- `seed --if-enabled` exits 0 and prints `seed: SEED_DEMO_DATA is not true, skipped` when `isDemoSeedEnabled()` is false; plain `seed` always seeds.
- Compose forms: `docker compose run --rm app import-feeds [--feed <id>]`. Tests and scripts add `-T` (no TTY) and, where the stack is already up, `--no-deps`.

### Code behind the verbs

- `src/db/migrate.ts` exports `runMigrations(db: Database): Promise<void>`: drizzle's `migrate()` from `drizzle-orm/node-postgres/migrator` with `migrationsFolder: path.resolve(process.cwd(), 'src/db/migrations')`. It does not import `server-only` or the client, so test global setup can call the same function.
- `src/cli/migrate.ts`, `seed.ts`, `import-feeds.ts` are thin mains: read arguments, call `getDb()`, call one function (`runMigrations`, `seedDemoData(db)`, `importFeeds(db, ...)`), print, set `process.exitCode`, and `await closeDb()` in a `finally`. All logic lives in `src/db` and `src/server` so Vitest tests it without spawning a process.
- `seedDemoData(db): Promise<SeedReport>` in `src/server/seed/index.ts`, data constants in `src/server/seed/demo-data.ts`. Insert-only: every insert is `on conflict do nothing` on the natural key (`slug`; feeds on `(shop_id, url)`). Re-running never changes an existing row, so an admin's un-approve or hide survives a restart (TD-21).
- `SEED_DEMO_DATA`: read only by `isDemoSeedEnabled()`; local `.env.example` true, Compose default false, so the owner's laptop seeds and an unconfigured server does not (D-1 Q2).
- First run on a fresh clone: `npm ci`, `npm run env:init`, `docker compose up -d --build --wait` (migrates and seeds), `docker compose run --rm app import-feeds`, open `http://127.0.0.1:3000/producto/demo-filtro-de-aceite-oc-1234` (host port is `APP_PORT`).

### Image changes (backend owns Dockerfile and .dockerignore)

- Add a `prod-deps` stage: `npm ci --omit=dev`.
- Build stage: `npm run build`, then `npm run cli:build`.
- Runner stage: copy `prod-deps` `node_modules` to `./node_modules` first, then the standalone output over it (directories merge), then `dist`, `src/db/migrations` and `demo` (all `--chown=node:node`). Standalone alone traces only what the Next server imports and would lack drizzle's migrator.
- `.dockerignore` gains `dist`. `tsconfig.json` `exclude` gains `dist`. `eslint.config.mjs` `globalIgnores` gains `dist/**`. `.gitignore` already ignores `dist/`.

### Test database

`tests/support/global-setup.ts` (test lane) now, on every Vitest integration run: connect to the maintenance database, `drop database if exists "<DB_NAME>_test" with (force)`, `create database`, then build a `drizzle({ client: new Pool(...) })` on it and call `runMigrations` from `src/db/migrate.ts` by relative path, then end the pool. Dropping each run means the suite always proves the migrations apply from nothing and never carries a stale schema while migrations are still being regenerated on the slice branch. The failure message keeps slice A's rule: host and port and the fix, never the URL.

`tests/support/db.ts` gains `resetDatabase()`: calls `assertTestDatabase()`, then `truncate` of every table in schema `public` except drizzle's own migrations table, `restart identity cascade`. Each integration file calls it in `beforeEach`.

## Importer and matching rules

Seams: `src/server/importer/` is the only writer of `products` and `offers` from outside data; `src/server/matching.ts` is the only matcher.

### Registered source (guardrail 2)

- The importer takes feed ids, never a URL or a path. `importFeeds(db)` reads `feeds` rows where `is_approved`; with `options.feedId` it reads that one row and throws `FeedNotRegisteredError` if the row does not exist. A row that exists but is not approved is reported `skipped` with `not_approved`, and its source is not read (0007: imported only once approved).
- `src/server/importer/source.ts` is the one place in `src/` that may call `fetch` or read a file. Allowed sources: `https:` (global `fetch`, `AbortSignal.timeout(30000)`, body capped at 50 MiB, response treated as UTF-8 CSV text) and `demo-feed:<name>` only when the feed row has `is_demo`, where `<name>` must match `^[a-z0-9-]+\.csv$` and is read from `<cwd>/demo/feeds/<name>`. Anything else fails the feed with `unsupported_url`. No HTML parsing exists anywhere; the lint ban stays.
- A fetch, timeout or non-2xx failure is `fetch_failed`. The report and logs name the feed id and shop name, never the URL (it can hold a network API key).

### Per-row steps, in order

1. Parse and validate the row (C-15). A violation rejects that row with its code; the feed continues.
2. **Known offer.** If an offer exists for `(feed_id, external_id)`: update `price_cents`, `url`, `price_updated_at = report.startedAt`, nothing else, count `offers_updated`. No matching runs again.
3. **EAN** (0008 step 1). `parseEan`: absent, valid or invalid. Valid means digits only after removing spaces and hyphens, length 8 or 13, correct GS1 check digit; `ean_normalised` is that digit string, not padded. Present but invalid rejects the row `invalid_ean` (TD-26).
   - Exactly one product has the same `ean_normalised`: if both brands are non-null and their `brand_normalised` differ, reject `ean_brand_conflict` and create nothing (D-1 Q5); otherwise attach, creating only the offer. More than one product: reject `ambiguous_ean`.
   - A hidden product still gets the offer attached; it stays hidden.
4. **New product** (0008 step 3). No EAN, or no product with it: create the product with a slug (TD-30) and then the offer. Brand plus part-number matching (0008 step 2) is not implemented and has no code path; `matching.ts` leaves one place for it.
5. Product text (title, brand, part number, EAN, description) is written only when the product is created and never updated (TD-23).

Normalisers in `src/server/matching.ts`: `normalizePartNumber` removes spaces, hyphens and dots and upper-cases (empty gives `null`); `normalizeBrand` trims, collapses internal whitespace and upper-cases (empty gives `null`); `parseEan` as above. Offers are written by an upsert on `(feed_id, external_id)` whose `do update set` lists exactly `price_cents`, `url` and `price_updated_at`; it never lists `product_id`, `is_hidden` or `in_review`.

### Transactions and isolation

One database transaction per feed: a validation or conflict reject does not abort it; a database error rolls the feed back and reports `failed` with `database_error`. A failing feed never stops the others. Feeds run in `id` order. `report.startedAt` is taken once per run and is the `price_updated_at` of every row seen that run, so re-running updates the date even when the price is unchanged.

Not in B: removal of offers missing from a later import, price history, import-report persistence, XML, per-network column mapping, gzip.

## Layout and seams

New and changed paths. Server-side directories `src/cli`, `src/config`, `src/db`, `src/server` use **relative imports only** (no `@/`), enforced by lint (TD-17).

```
demo/feeds/tienda-demo-uno.csv  tienda-demo-dos.csv
drizzle.config.ts  tsconfig.cli.json
src/db/schema/index.ts (+ files per table group; imports only drizzle-orm)
src/db/migrations/0000_init.sql  meta/...
src/db/migrate.ts                runMigrations(db)
src/db/client.ts                 + export type Database, Executor (db or transaction)
src/config/env.ts                + readOptionalEnv
src/config/seed.ts               isDemoSeedEnabled
src/server/money.ts              parseDecimalToCents, formatEuroCents
src/server/slug.ts               slugify, uniqueSlug
src/server/matching.ts           parseEan, normalizePartNumber, normalizeBrand
src/server/visibility.ts         the one scope
src/server/catalogue/product-page.ts
src/server/importer/index.ts csv.ts validate.ts source.ts report.ts types.ts
src/server/seed/index.ts demo-data.ts
src/cli/migrate.ts seed.ts import-feeds.ts
src/app/(public)/producto/[slug]/page.tsx
src/components/ProductDetails.tsx OfferList.tsx ImagePlaceholder.tsx  (+ *.module.css each)
tests/...   see § Tests owed
```

| Seam | Lives in | Notes |
|---|---|---|
| Public visibility | `src/server/visibility.ts` | exports `visibleOfferWhere()` and `visibleProductWhere()` (Drizzle `SQL`, over offers joined to feeds and shops, and over products). The read function and any later public read call them; none restates a flag |
| Feed ingestion | `src/server/importer/`, CLI `src/cli/import-feeds.ts` | the only writer of products and offers; `source.ts` the only network or file read |
| Matching | `src/server/matching.ts` | EAN and normalisers now; brand + part number later |
| Money | `src/server/money.ts` | parse for the importer, format for the page |
| Role check | convention only | still the directory rule (C-5). No admin route exists; guardrail 3 has no new seam |
| Click log | later slice | `/go` is out of B |

Reuse by lane, by name:

- Backend: `getDb`, `closeDb`, `readRequiredEnv` (`src/config/env.ts`), `scripts/init-env.mjs` (unchanged), the entrypoint `case` dispatcher, slice A's `no-restricted-imports` block (extend, do not replace).
- Frontend: `getTranslations`, `getLocale`, ICU messages for dates and plurals, `SiteHeader` (site name as a prop), `src/app/not-found.tsx`, the `.page` class in `globals.css` for the `<main>` wrapper, the CSS custom properties in `globals.css`.
- Test: `assertTestDatabase`, `testDatabaseUrl`, `withDatabaseName`, `loadEnv`, `umamiBaseUrl`, `listRouteFiles`/`classifyRoute`, `server-only-stub`, and the JavaScript-off `page.setContent` pattern, no-cookie and no-foreign-origin checks from `tests/e2e/home.spec.ts` (extract them into `tests/support/page-checks.ts` rather than copying them).

## Decisions

Continues slice A's TD-1 to TD-15. These are made so no two lanes choose separately.

- **TD-16. Stay CommonJS.** No `"type": "module"` in package.json: it would force `.js` extensions on every relative import and break the tsc-compiled CLI. The Vite warning is fixed by renaming the config to `.mts` and using `import.meta.dirname` instead of `__dirname`. Verified in a scratch directory outside the repo with Vitest 5.0.5: the warning disappears.
- **TD-17. The CLI is tsc output.** `tsconfig.cli.json`: `module` and `moduleResolution` `node16`, `rootDir src`, `outDir dist`, `strict`, `esModuleInterop`, `skipLibCheck`, `types ["node"]`, `include ["src/cli/**/*.ts"]`. Run with `node --conditions=react-server` because `server-only` throws under plain Node and resolves to an empty module under that condition. tsc does not rewrite `@/` paths, so `src/{cli,config,db,server}/**` import relatively; ESLint enforces it with an override that repeats the scraping-library patterns (flat-config options do not merge). No esbuild or tsx.
- **TD-18. Image carries full production node_modules** (TD-17 needs drizzle's migrator and `pg` outside Next's trace).
- **TD-19. Migrations run on every `server` start**, before seed and before the app listens. One app container, so no migration lock is needed.
- **TD-20. Seed flag default is off in Compose, on in `.env.example`.** Only the literal `true` enables it.
- **TD-21. Seed and importer never write approval or hidden columns after the first insert.** Seed inserts are `do nothing`; the importer's offer upsert updates three named columns. A hidden or disabled demo item stays so across restarts and re-imports (guardrail 1).
- **TD-22. Import is manual.** Seed loads no products (Q-2).
- **TD-23. Product text is first-wins and immutable in B.** The admin shop ranking that decides text arrives later; until then a second feed's wording never overwrites the first.
- **TD-24. Offer identity is `(feed_id, external_id)`.** A known offer is updated and never re-matched.
- **TD-25. Rows without a valid EAN each create their own product.** Cross-shop merging for them waits for brand + part-number matching. Part number and brand are stored normalised now so that slice needs no backfill.
- **TD-26. A present but invalid EAN rejects the row**, rather than being silently treated as absent: a typo should be visible in the report, not produce a stray product.
- **TD-27. EAN conflict means** same `ean_normalised`, both `brand_normalised` non-null and different. A null brand on either side is not a disagreement.
- **TD-28. One transaction per feed;** reject codes cover row problems, `database_error` covers the rest.
- **TD-29. Only `feeds.is_approved` gates importing.** Shop approval gates visibility only.
- **TD-30. A product is addressed by its slug**, `/producto/<slug>`: generated once at creation by `slugify(title)` (NFD, strip combining marks, lower-case, runs of non `[a-z0-9]` become one `-`, trimmed, at most 80 characters, fallback `producto`), a numeric suffix `-2`, `-3` on collision, never regenerated. Slug rather than id gives readable URLs for the SEO slice, a known URL for the e2e, and a stable address across later merges (0008 redirects).
- **TD-31. The read function takes no `db` argument and returns `null` for every not-public case.**
- **TD-32. Cents and `Date` cross the boundary; the page formats** (C-12). One money helper file.
- **TD-33. Dates display in `Europe/Madrid`**, ICU `medium` style, from `getRequestConfig`.
- **TD-34. Currency format forces grouping** (`useGrouping: 'always'`) so a four-digit price reads `1.234,50 €` as the frontend pack shows.
- **TD-35. Styling is CSS Modules (this run's D-1).** New components use co-located `*.module.css`. `globals.css` keeps the variables, the reset and slice A's two classes; no new global classes; slice A's components are not migrated unless touched. No `:global`, no new dependency.
- **TD-36. Feed URLs are never logged, printed or put in a report.** The `demo-feed:` scheme, valid only for `is_demo` feeds, keeps demo data portable between host and container paths.
- **TD-37. The test database is dropped, recreated and migrated every integration run.**
- **TD-38. E2E data comes from the real path:** Playwright `globalSetup` runs `docker compose run --rm -T --no-deps app import-feeds`. Tests never write the development database. The e2e does not seed: if the report shows `feeds=0` the setup throws "no approved feed: set SEED_DEMO_DATA=true in .env and run docker compose up -d", which also proves the start-up seed path on the gate.
- **TD-39. The import report is printed, not stored.** Persisting it belongs with the admin "Import now" slice.
- **TD-40. `Database` and `Executor` types are exported from `src/db/client.ts`** so the importer, seed and migrate take a database or a transaction without each declaring its own alias. `getDb()` keeps its slice A behaviour.
- **TD-41. Price rules.** Decimal text to cents by digit handling, never a float; at most two decimals; `price_cents` fits `integer`; more than two decimals rejects rather than rounds.
- **TD-42. Empty means null** for optional text, in the schema and in the contract.

## Lane split

Order is fixed. Each fence is a write fence; reading is free. A lane that needs a file outside its fence stops and reports.

### 02 backend (first)

Fence (write): `package.json`, `package-lock.json`, `drizzle.config.ts`, `tsconfig.cli.json`, `tsconfig.json` (include `**/*.mts`, exclude `dist`), `eslint.config.mjs`, `.dockerignore`, `Dockerfile`, `docker-entrypoint.sh`, `compose.yaml`, `.env.example`, `demo/**`, `src/db/**`, `src/config/**`, `src/cli/**`, `src/server/**`. Not `src/app/**`, `src/components/**`, `src/i18n/**`, `messages/**`, `tests/**`.

Inputs: § Schema and visibility states, § Contract (C-11, C-12, C-15 to C-18), § Paths, § Importer and matching rules, § Layout and seams, § Decisions, § Handoff items from the last integration (item 3), § Pack corrections owed.

Work: install `drizzle-kit` as a devDependency (a release compatible with drizzle-orm 0.45.4; verify `generate` runs); schema and the `0000_init` migration; money, slug, matching, visibility; the read function; importer; seed; the three CLI mains; scripts; Dockerfile and entrypoint; compose and `.env.example`; lint override; demo CSVs; tsconfig changes.

Verification (all must pass, counts reported verbatim): `npm run lint && npm run typecheck && npm run build && npm test`, then `npm run db:up && npm run db:migrate && npm run db:seed && npm run import-feeds` run twice (second run reports `created=0`), then `npm run stack:up`, `docker compose run --rm -T app import-feeds` twice, `docker compose run --rm -T app bogus` exits 64, and `docker compose logs app` shows the migrate and seed lines without any URL. Report the exact `drizzle-kit` version.

### 03 frontend (second)

Fence (write): `src/app/(public)/producto/**`, `src/components/**` (including `*.module.css`), `src/i18n/request.ts` (adds `timeZone`), `messages/es-ES.json`. No new dependency, no `src/server` or `src/db` import from a component.

Inputs: § Contract (C-11 to C-14, C-18), § Decisions (TD-30 to TD-35), § Layout and seams, § Pack corrections owed.

Work: the page, three components, the `Product` messages, CSS Modules, `generateMetadata`, `cache`-wrapped loader, `notFound()` on null, Spanish copy. Components take display strings only. The description is rendered as text.

Verification: `npm run lint && npm run typecheck && npm run build`, then with the stack up and the demo imported, `curl -s http://127.0.0.1:${APP_PORT}/producto/demo-filtro-de-aceite-oc-1234` shows two offers cheapest first, `curl -sI` on it and on `/producto/no-existe` shows no `Set-Cookie`, the second returns 404.

### 04 test (third)

Fence (write): `tests/**`, `vitest.config.mts`, `playwright.config.ts` (adds `globalSetup: './tests/e2e/global-setup.ts'` as a string, never an import). It edits no `src/**`, no `package.json`.

Precondition: the orchestrator has run `git mv vitest.config.ts vitest.config.mts` and backend has added `**/*.mts` to tsconfig. The lane replaces `__dirname` with `import.meta.dirname`.

Inputs: § Tests owed, § Contract (all), § Paths, § Importer and matching rules, § Handoff items from the last integration (items 4 to 6), § Pack corrections owed.

Verification: `npm run gate` exits 0 with counts verbatim; `npm run test:unit` with the database stopped passes; the Vitest run prints no configLoader warning.

### 05 docs (fourth, build phase)

Fence (write): `CLAUDE.md` § Commands only.

Work: add `db:generate`, `cli:build`, `db:migrate`, `db:seed`, `import-feeds` with their needs; the Compose forms; `SEED_DEMO_DATA` and the note that an existing `.env` must gain `SEED_DEMO_DATA=true`; the first-run sequence in § Paths; the changed `typecheck` meaning. Nothing outside § Commands.

### Integration, then close docs

Integration (tech-lead) runs `npm run gate`, checks C-11 against the page's imports and the tests' `toEqual`, then the architecture pack list: one copy each of the visibility scope, importer write path, matcher and money helper; guardrails 1, 2, 4, 5 by seam; log output free of URLs; `dist/` and `.env` untracked; `drizzle-kit generate` reports no schema drift; the image builds cold. Close docs: decision 0011, CLAUDE.md § Stack line, pack corrections.

## Tests owed

Owned by the test lane. Each must fail if the rule it names broke. Integration tests call `resetDatabase()` in `beforeEach`; no test calls a live network (stub global `fetch` to throw in importer tests).

### Brief acceptance, one for one

| Acceptance line | Test |
|---|---|
| compose up leaves demo data present | `tests/e2e/global-setup.ts`: import report shows 2 imported feeds (fails with the TD-38 message if none) |
| `import-feeds` prints counts and rejected rows; second run duplicates nothing | `tests/integration/importer-demo.test.ts` (shipped files: 3 products, 4 offers, then unchanged counts, `offers_updated=2` per feed); `tests/unit/import-report.test.ts` (exact line format); `tests/e2e/entrypoint.spec.ts` (second `docker compose run` prints `offers_created=0`) |
| shared-EAN page lists two shops cheapest first with price, date and count | `tests/e2e/product.spec.ts` (order, `11,49 €` before `12,99 €`, `2 tiendas`, date matches the message pattern); `tests/integration/product-page.test.ts` (sort, tie-break) |
| single-shop page shows the one-shop wording | `tests/e2e/product.spec.ts` (`1 tienda`) |
| unapproved-feed, hidden-offer and hidden-product items not visible | `tests/integration/visibility.test.ts`, one test per state (below) |
| CLAUDE.md § Commands lists the gate commands | docs lane; integration checks |
| page sets no cookie; nothing logged with email, token or password | `tests/e2e/product.spec.ts` (no `Set-Cookie`, empty `context.cookies()`, no foreign origin); `tests/integration/importer-logging.test.ts` (sentinel URL key absent from report text and console) |

### Guardrail tests

- **(1) visibility**, `tests/integration/visibility.test.ts` against `getPublicProductBySlug`, fixtures by direct SQL: visible baseline returns the offer; feed unapproved, shop unapproved, offer hidden, offer `in_review`, each alone removes that offer; two offers with one removed leaves the other; all offers removed returns `null`; product hidden returns `null` even with visible offers; malformed slug returns `null` without a query. The truth table of § Schema and visibility states is the spec.
- **(1) seam**, `tests/unit/seams.test.ts` by file scan: the flag identifiers appear only in `visibility.ts`, `src/db/schema/**`, `src/server/seed/**`, `src/server/importer/**`; no file under `src/app` or `src/components` imports `@/db` (except route handlers); `fetch(` appears in `src/` only in `src/server/importer/source.ts`.
- **(1) preservation**, `tests/integration/seed.test.ts` and `importer-preservation.test.ts`: seed twice changes nothing; after setting a demo feed `is_approved=false` and a product `is_hidden=true`, a second seed and a second import leave both unchanged and the hidden product's new offers stay invisible.
- **(1) seed scope**, same file: only `is_demo` feeds and the demo shops are approved; no non-demo row is approved by the seed.
- **(2) registered source**, `tests/integration/importer-source.test.ts`: `feedId` that does not exist throws `FeedNotRegisteredError` and the reader and `fetch` are never called; an unapproved feed is `skipped` without a read; `ftp:`, `file:` and a `demo-feed:` url on a non-demo feed fail `unsupported_url`; `demo-feed:../x.csv` is refused; an `https:` feed goes through the injected reader.
- **(2) lint ban**, `tests/unit/eslint-guardrails.test.ts` using the ESLint Node API on virtual files: `cheerio`, `puppeteer`, `@playwright/test` imports are errors in `src/server/x.ts` and `scripts/x.mjs`; an `@/` import is an error in `src/server/x.ts` and `src/cli/x.ts` and allowed in `src/app/x.tsx`.
- **(3)** nothing new. The slice A route-classification test must still pass with the new route.
- **(4) money**, `tests/unit/money.test.ts`: `19.99` gives 1999, `0.29` gives 29, `1.1` gives 110, `12` gives 1200, `12,5` gives 1250, `1.005` and `1.234,50` and `1e3` and `-1` and `0` and ` ` give `null`; `formatEuroCents(1999)` and `(123450)` equal `19,99 €` and `1.234,50 €` after normalising U+00A0; non-integer throws. `tests/integration/schema.test.ts`: no column in schema `public` has type `real`, `double precision`, `numeric` or `money`; every `*_cents` column is `integer`; inserting `price_cents = 0` fails the check.
- **(5)** e2e no-cookie and logging tests above; `docker compose logs app` is not asserted.

### Matching (0008, the slice B cut)

`tests/unit/matching.test.ts`: GTIN-13 and GTIN-8 valid, bad check digit, wrong length, spaces and hyphens stripped, part number `0 986 494 123` equals `0986494123`, brand trim and case. `tests/integration/importer-matching.test.ts`, fixtures in `tests/fixtures/feeds/`: second feed with the same EAN attaches (one product, two offers, text unchanged); same EAN with a different brand is rejected `ean_brand_conflict` and creates nothing; null brand on one side attaches; no EAN creates a new product each; invalid EAN rejects; duplicate `id` in one feed rejects the second; a hidden product still receives the offer.

### Importer behaviour

`tests/unit/csv.test.ts` (quotes, doubled quotes, CRLF, embedded newline, BOM, blank lines, ragged row), `tests/unit/import-validate.test.ts` (every `RejectCode`), `tests/integration/importer-isolation.test.ts` (one feed's reader throws: it is `failed`, the other imports, exit semantics of `formatImportReport`), `tests/integration/importer-demo.test.ts` (above), `tests/integration/migrations.test.ts` (expected tables exist; `runMigrations` a second time is a no-op; every schema column exists with matching nullability), `tests/unit/slug.test.ts`, `tests/unit/seed-config.test.ts` (`isDemoSeedEnabled`: unset, `false`, `TRUE`, ` true `, `yes`), `tests/unit/messages.test.ts` extended (every key in C-14 exists; plural has `one` and `other`; no code name).

### Page, entrypoint and scripts

- `tests/integration/product-page.test.ts`: exact key set via `toEqual`, `Date` instance, integer cents, null brand/part number/EAN/description survive, empty-string cells stored as `null`, sort with a price tie.
- `tests/e2e/product.spec.ts`: raw HTML with JavaScript off (the slice A pattern, via `tests/support/page-checks.ts`) asserts C-13; no `href` off-site and none inside the offers list; the `.example` hosts absent from the HTML; unknown slug gives 404 with `NotFound.heading` and no cookie.
- `tests/e2e/entrypoint.spec.ts` (serial): `docker compose run --rm -T --no-deps app bogus` exits 64 (open row 4); `import-feeds` twice reports `offers_created=0` the second time; `import-feeds --feed 999999` exits 1.
- `tests/unit/init-env.test.ts` (open row 4): copy `scripts/init-env.mjs` and `.env.example` into a temp directory under the OS temp dir, run it with `node`: `.env` appears, `DB_PASSWORD` and `UMAMI_APP_SECRET` are 48 hex characters, `DATABASE_URL` is derived, `SEED_DEMO_DATA=true` is kept, stdout contains no secret; a second run exits 1 and the file is byte-identical.
- `tests/e2e/global-setup.ts`: runs the compose import once for the whole run, prints nothing secret, throws the TD-38 message on `feeds=0`.

## Handoff items from the last integration

Assignments for the four SHOULD_FIX rows in the ledger's `Open` table (07-integration § handoff 3 to 6). None is deferred.

- **3. Vite ESM warning and the `package.json` "type" call.** Decision: stay CommonJS (TD-16). Backend adds `**/*.mts` to tsconfig `include`. The orchestrator runs `git mv vitest.config.ts vitest.config.mts` before dispatching the test lane (no lane can rename). The test lane switches the file to `import.meta.dirname` and confirms the warning is gone. Close docs notes TD-16 in the testing pack.
- **4. `init-env.mjs` and entrypoint exit 64 untested.** Test lane: `tests/unit/init-env.test.ts` and `tests/e2e/entrypoint.spec.ts`, specified in § Tests owed. The exit-64 check runs through `docker compose run`, not `sh`, because `sh` is not reliably on the Windows host.
- **5. TD-10 scraping-library lint ban has no regression test.** Test lane: `tests/unit/eslint-guardrails.test.ts`; it also pins that the new relative-import override did not drop the ban.
- **6. E2E base-URL rule written twice.** Test lane: specs use Playwright's `baseURL` and `request` fixtures instead of `appBaseUrl()`; `appBaseUrl()` is deleted from `tests/support/env.ts` once nothing calls it. `playwright.config.ts` keeps the single copy, because a root config cannot import `tests/`. Update the comment in the config.

## Pack corrections owed

Each lane emits these in its own `pack_corrections` when it lands the convention; close docs applies them as text. Wording is the replacement.

### backend.md

- § Layout — replace the sentence "Server-only code: ..." with: "Server-only code: `src/config` (env readers, `getSiteName`, `isDemoSeedEnabled`), `src/db` (`getDb()`, `schema/`, `migrations/`, `runMigrations`), `src/server` (`visibility.ts`, `money.ts`, `matching.ts`, `slug.ts`, `catalogue/`, `importer/`, `seed/`), `src/cli` (thin mains for `migrate`, `seed`, `import-feeds`). Files in these four directories import each other relatively, never with `@/`: the CLI is compiled by `tsc -p tsconfig.cli.json` to `dist/` and run with `node --conditions=react-server`, and tsc does not rewrite aliases. ESLint enforces it."
- § Layout — add: "Migrations: `npm run db:generate -- --name <name>` writes SQL to `src/db/migrations/`; commit it. Once a migration is merged to `main` it is never edited. The app container migrates on every `server` start. Entrypoint verbs: `server`, `migrate`, `seed`, `import-feeds`; unknown verb exits 64."
- § Guardrails (1) — replace "Seeds create feeds as not approved, except the demo feed the seed marks as demo." with: "Seeds are insert-only (`on conflict do nothing`) and create nothing approved except rows marked `is_demo`; they never change an existing row. `SEED_DEMO_DATA` is true in `.env.example` and false by default in Compose."
- § Guardrails — add: "Visibility lives only in `src/server/visibility.ts`. Money parsing and formatting live only in `src/server/money.ts`. `src/server/importer/source.ts` is the only place that fetches or reads a feed. Feed URLs may hold API keys: never print or log one. Eslint's `no-restricted-imports` overrides do not merge: an override must repeat the scraping-library patterns."

### frontend.md

- Header and § Layout — replace "plain CSS with variables until the owner picks a styling system, O-4" with: "CSS Modules (owner ruling, 2026-10-17): co-located `*.module.css`; `src/app/globals.css` keeps the reset and the CSS custom properties; add no new global classes."
- § Layout — replace "A component never imports `src/db`, `src/server` or `src/config`" with: "A component never imports `src/db`, `src/server` or `src/config`, and receives finished strings. A page (`page.tsx`) is a server component and may import `src/server` read functions and `formatEuroCents`; it never imports `src/db`."
- § Spanish market conventions — replace the price example with: "Format prices with `formatEuroCents` from `src/server/money.ts`, which forces `useGrouping: 'always'` so the output is `1.234,50 €`. The space before `€` is U+00A0. Plain `Intl.NumberFormat('es-ES')` drops the thousands separator on four digits."
- § Next.js and i18n — add: "`getRequestConfig` sets `timeZone: 'Europe/Madrid'`; dates are ICU placeholders in messages, for example `{date, date, medium}`. Counts use ICU plurals. Public product pages live at `src/app/(public)/producto/[slug]/page.tsx`, call one `cache()`-wrapped read function, and call `notFound()` on `null`."

### testing.md

- § Running tests — replace the clause on the test database with: "`tests/support/global-setup.ts` drops and recreates `${DB_NAME}_test` on every integration run and migrates it with `runMigrations` from `src/db/migrate.ts`. Integration files call `resetDatabase()` (`tests/support/db.ts`) in `beforeEach`."
- § Running tests — add: "Vitest config is `vitest.config.mts` (the package stays CommonJS), using `import.meta.dirname`. E2E data comes from Playwright `globalSetup`, which runs `docker compose run --rm -T --no-deps app import-feeds`; e2e tests never write the development database. Specs use the `baseURL` and `request` fixtures; only `playwright.config.ts` computes the base URL."
- § What must always be covered — replace the matching line with: "**Matching (0008), slice B cut:** EAN attach, EAN with a different brand rejected into the report, no EAN creates a product, invalid EAN rejected. Brand + part-number matching and the queue are tested when they ship."
- § What must always be covered — add: "Assertions on es-ES prices normalise U+00A0. A file scan (`tests/unit/seams.test.ts`) keeps the visibility flags, `fetch` and the `@/db` import out of places they do not belong."

### architecture.md

- § The seams the product forces — append the paths: "Public visibility: `src/server/visibility.ts`. Feed ingestion: `src/server/importer/` with `source.ts` as the only fetch. Matching: `src/server/matching.ts`. Money: `src/server/money.ts`. Product read: `src/server/catalogue/product-page.ts`."
- § Design pass — add: "Settle how server-side CLIs run in the image (compiled, relative imports, `--conditions=react-server`) before any lane writes an entry point."
