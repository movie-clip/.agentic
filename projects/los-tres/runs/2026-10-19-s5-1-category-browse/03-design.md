REPORT 2026-10-19-s5-1-category-browse/03
status:      DONE
verdict:     NONE

changed:
  - C:\projects\investments\.agentic\projects\los-tres\runs\2026-10-19-s5-1-category-browse\03-design.md — this technical plan (the only artifact)

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    The order's verification was NONE. Plan written from the code at main 8c30965 (schema, visibility, product-page, offer-target, importer, seed, demo feeds, tests/support, seams and route tests).

contract_notes:
  - New migration 0002_category_mapping: products.category_id, offers.feed_category, table feed_category_mappings; see § Contract, C-1.
  - src/server/visibility.ts visibleProductWhere gains `products.category_id is not null`; product page and /go inherit it; see § Contract, C-2.
  - New read function getPublicCategoryPage in src/server/catalogue/category-page.ts, shape fixed in § Contract, C-3.
  - SeedReport gains `categoryMappings: number`; tests/integration/seed.test.ts expectations change with it.
  - Feed CSV layout (C-15) gains the optional column `category`; ValidRow gains `feedCategory: string | null`.
  - Data-testids for the category page are fixed in § Contract, C-5; the e2e lane selects only by these.

pack_corrections:
  - none

handoff:
  - Backend: build T5.1.1-T5.1.4 to § Contract C-1..C-4, § Importer and § Demo data; files in § Lanes, lane 1.
  - Frontend: build T5.1.5 to § Contract C-3, C-5 and § Page; the read function and page-param parser are backend's, import them.
  - Test: every existing test the visibility change breaks is listed in § Affected tests; fix the shared fixture first (D-9).
  - Empty category has exactly one page: `?pagina=2` on an empty category is 404 (answers the 02-ux handoff).
  - Card price and title are never `<p>` (02-ux `.page p` specificity); price is a `<span>`, title an `<h2>`.

skill_calls:
  - none

risks:
  - Mapping is keyed per feed (feed_id, feed_category), not per network; S4.2 must map the same string once per feed. Chosen because merchant taxonomies differ within one network; see § Decisions D-1.
  - OD-F "earliest-imported assignment kept" is implemented as first-mapped-wins and never overwritten by the importer; a later admin remap (S4.2) will need its own re-assignment path.
  - Between the backend lane and the test lane, `npm test` integration is expected to fail (fixtures make unmapped, now non-public products); backend's verification is lint, typecheck and unit only.
  - Existing databases: every product is non-public after migrate until the next import-feeds run assigns categories (OD-J); the gate's e2e setup runs that import, so the gate is unaffected.
  - The guardrail-1 wording in project.md does not name the unmapped condition; owner's edit, raised by the story, not taken here.
  - categories.slug has no format CHECK; the read function validates the slug before querying, as the product page does.

## Orchestrator brief

Decisions: products.category_id (nullable FK) is the assignment; offers.feed_category stores the feed's string; feed_category_mappings keyed (feed_id, feed_category); migration `0002_category_mapping`.
Decisions: "mapped" = products.category_id is not null, added inside visibleProductWhere — no second filter; product page and /go inherit it.
Decisions: importer assigns only when category_id is null (first mapped wins, OD-F), on both new and known-offer rows (AC 5); never clears it.
Decisions: getPublicCategoryPage(slug, page) → PublicCategoryPage | null; sort lowest price asc, product id asc; 24/page; empty category = 1 page.
Lanes: 1 backend T5.1.1-T5.1.4 → 2 frontend T5.1.5 → 3 test T5.1.6 (runs the gate) → docs close-out. No blocker; nothing needs the owner.
Sections below:
- § Contract: C-1 schema+migration, C-2 visibility, C-3 read function, C-4 page-param parser, C-5 testids.
- § Importer: the exact change to validate.ts and importer/index.ts.
- § Demo data: required demo rows, mappings and the deliberate unmapped product (T5.1.4).
- § Page: route, components, metadata, 404/empty rules for frontend.
- § Decisions: D-1..D-10, the calls lanes must not make separately.
- § Lanes: files, tickets and verification per lane.
- § Affected tests: every existing test/contract the change breaks.
- § Risks detail: where this is harder than it looks.

---

## Contract

### C-1. Schema and migration (backend, T5.1.1)

Migration generated with `npm run db:generate -- --name category_mapping` → `src/db/migrations/0002_category_mapping.sql` (+ meta snapshot/journal). All in `src/db/schema/catalogue.ts` (feeds is imported there already).

| Table.column | Type | Null | Notes |
|---|---|---|---|
| `products.category_id` (`categoryId`) | integer FK → categories.id, on delete restrict | **nullable** | null = unmapped = not public. Written by the importer only (D-3). Index `products_category_id_idx`. |
| `offers.feed_category` (`feedCategory`) | text | nullable | the feed row's `category` cell, trimmed, as given; empty → null (TD-42: optional text is null, never ''). Updated on every import like price. |
| `feed_category_mappings.id` | integer identity PK | no | |
| `feed_category_mappings.feed_id` (`feedId`) | integer FK → feeds.id, restrict | no | |
| `feed_category_mappings.feed_category` (`feedCategory`) | text | no | exact string as it appears in `offers.feed_category` |
| `feed_category_mappings.category_id` (`categoryId`) | integer FK → categories.id, restrict | no | |
| `feed_category_mappings.created_at` | timestamptz default now | no | |
| unique | `feed_category_mappings_feed_id_feed_category_unique` on (feed_id, feed_category) | | one mapping per feed category ("mapped once", mvp.md) |

Export name: `feedCategoryMappings`. No money column; no flag column.

### C-2. Visibility scope (backend, T5.1.2)

`src/server/visibility.ts`, `visibleProductWhere()` becomes:

```
product public = product not hidden AND product.category_id is not null
                 AND it has at least one visible offer
```

i.e. `and(eq(products.isHidden, false), isNotNull(products.categoryId), exists(visibleOffer))`. Update the header comment to name the mapped condition. `visibleOfferWhere()` is unchanged. Nothing else restates the condition: `getPublicProductBySlug` and `getRedirectTarget` already call `visibleProductWhere()`, so the product page and `/go` return 404 for an unmapped product with no edit (AC 1, 2). The listing in C-3 calls the same two functions.

### C-3. Listing read function (backend, T5.1.3)

New file `src/server/catalogue/category-page.ts` (`import 'server-only'`), the sibling of `product-page.ts` and modelled on it.

```ts
export const CATEGORY_PAGE_SIZE = 24;

export type CategoryProductCard = {
  /** products.slug; link target /producto/<slug>. */
  slug: string;
  /** Never empty. */
  title: string;
  /** As received; null means render no brand line. */
  brand: string | null;
  /** min(visible offers.price_cents). Integer > 0, EUR, IVA included. Equals
   *  getPublicProductBySlug(slug).offers[0].priceCents for the same data. */
  lowestPriceCents: number;
  /** count(visible offers). Integer >= 1. Same number the product page shows as
   *  offers.length (Product.shopCount). */
  offerCount: number;
};

export type PublicCategoryPage = {
  slug: string;            // categories.slug
  name: string;            // categories.name
  page: number;            // 1-based, the page returned (after C-4 clamping)
  pageCount: number;       // >= 1; exactly 1 when productCount is 0
  productCount: number;    // public products in the category and every descendant
  products: CategoryProductCard[]; // length 0..24; 0 only when productCount is 0
};

/** null for: malformed slug (no query), unknown slug, or page > pageCount. */
export async function getPublicCategoryPage(
  slug: string,
  page: number,
): Promise<PublicCategoryPage | null>;
```

Rules:
- `page` is an integer >= 1 (the caller passes C-4's output); the function does not clamp, it only compares against `pageCount`.
- Subtree: the category plus all descendants at any depth (OD-A), by a recursive CTE using `UNION` (not `UNION ALL`) so a malformed cycle terminates. Embed it with drizzle's `sql` template as `inArray(products.categoryId, sql\`(with recursive …)\`)`.
- Rows: `from(offers).innerJoin(products).innerJoin(feeds).innerJoin(shops)` exactly as product-page.ts, `where(and(visibleProductWhere(), visibleOfferWhere(), <in subtree>))`, `groupBy(products.id)`. Each product appears once because it has one category_id (AC 9).
- Order: `min(offers.price_cents) asc, products.id asc` (OD-B; id is the stable tie-break).
- Aggregates are cast to int in SQL (`min(...)::int`, `count(*)::int`), because Postgres `count` is bigint and node-postgres returns it as a string.
- Queries: (1) category by slug → null if none; (2) count of distinct public products in subtree; `pageCount = max(1, ceil(productCount / 24))`; if `page > pageCount` return null before (3); (3) the page rows, `limit 24 offset (page-1)*24`.
- Slug validation before any query: extract the product page's `SLUG_FORMAT` + max length into `src/server/slug.ts` as `export function isWellFormedSlug(slug: string): boolean` (regex `^[a-z0-9]+(-[a-z0-9]+)*$`, max 120), and make product-page.ts use it too. One copy.
- Returns integer cents, never a formatted string (as C-11 for the product page).

### C-4. Page parameter parser (backend, with T5.1.3)

New pure file `src/server/catalogue/page-param.ts`:

```ts
/** `?pagina` value → page number >= 1. Never throws. */
export function parsePageParam(value: string | string[] | undefined): number;
```

- `undefined`, an array (repeated param), `''`, anything not matching `^[0-9]+$` (so `-1`, `1.5`, `abc`, ` 2`) → `1`.
- digits → `Number(value)`; `0` → `1`; above `Number.MAX_SAFE_INTEGER` → `Number.MAX_SAFE_INTEGER` (then C-3 returns null → 404). Leading zeros allowed (`02` → 2).
- No redirect: `?pagina=1` and `?pagina=abc` render page 1 at that URL (02-ux § States).

### C-5. Data-testids (frontend writes, test lane selects)

| testid | element |
|---|---|
| `category-summary` | the muted "N productos[ · Página X de Y]" line |
| `category-card` | each card `<li>` |
| `card-title` | the title `<a>` inside the card |
| `card-brand` | brand element (absent when brand is null) |
| `card-price-from` | the "Desde" label (absent when offerCount is 1) |
| `card-price` | the formatted price `<span>` |
| `card-shop-count` | the shop count |
| `pagination` | the `<nav>` (absent when pageCount is 1) |
| `pagination-prev` / `pagination-next` | the links (absent when no neighbour) |
| `pagination-indicator` | "Página X de Y" |
| `category-empty` | the empty-state container |

## Importer

T5.1.1. Files `src/server/importer/validate.ts`, `src/server/importer/index.ts`. The importer stays the only writer of products and offers.

1. `validate.ts`: add `'category'` to `OPTIONAL_COLUMNS`; `ValidRow.feedCategory: string | null` = `optional('category')` (trimmed, empty → null). No reject code: a missing or unknown category never rejects a row (AC 7).
2. `importRecords`: at the start, load this feed's mappings once into `Map<string, number>` (feed_category → category_id) inside the transaction.
3. `writeOffer`: insert `feedCategory`; on conflict `set` lists price, url, date **and feed_category** (feed data). Still never product_id, is_hidden or in_review (TD-21, TD-24); update that comment.
4. After the offer is written, on **both** paths (known offer and new/attached product): if `row.feedCategory` is non-null and maps, run `update products set category_id = $mapped where id = $productId and category_id is null`. One helper, `assignCategory(tx, productId, categoryId)`.
5. Never set category_id to null; never overwrite a non-null one (OD-F first-mapped wins, AC 6 idempotent).
6. `FeedImportReport` is unchanged: an unmapped category is not a failure and not a reject (AC 7). Counting unmapped rows is left to S4.2's queue.
7. Update the file header comment: product text is still written once (TD-23); category_id is the one product column the importer may set later, and only from null.

## Demo data

T5.1.4. Files `src/server/seed/demo-data.ts`, `src/server/seed/index.ts`, `demo/feeds/tienda-demo-uno.csv`, `demo/feeds/tienda-demo-dos.csv`.

- Both CSVs gain a `category` column. The three existing products keep their slugs, titles, EANs and prices (e2e product/go specs depend on them).
- `demo-data.ts` adds `demoCategoryMappings: { feedFile, feedCategory, categorySlug }[]`; seed inserts them after categories, `onConflictDoNothing` on (feed_id, feed_category), and reports `categoryMappings` (inserted rows).
- Required mappings (strings are the feed's own taxonomy, deliberately different per shop):
  - uno `Recambios > Filtros` → `filtros`; uno `Recambios > Iluminación` → `escobillas-y-bombillas`; uno `Bricolaje > Taladros` → `herramientas-electricas`
  - dos `Filtros de aceite` → `filtros`; dos `Herramienta manual` → `herramientas-manuales`
- Required rows / states (02-ux handoff, AC 23, 24):
  - `filtros` holds **at least 25** public products (two pages): the shared filter plus filler rows `DEMO Filtro de aire FA-1nn` (no EAN, distinct titles and prices).
  - one product with a 100-character title, in `filtros`.
  - one product with an empty brand cell (`DEMO Lámpara H7 12 V 55 W`, uno, `Recambios > Iluminación`).
  - single-offer products: the drill and wrenches already are.
  - `aceites-y-lubricantes` stays **empty** (no mapping points at it).
  - roots `automovil` and `herramientas` hold products only through children (AC 23).
  - one deliberately unmapped row: dos `Jardín > Cortacésped`, title `DEMO Cortacésped eléctrico 1200 W` → slug `demo-cortacesped-electrico-1200-w`, never public (AC 24).
  - one row with an empty category cell (dos, `DEMO Banco de trabajo plegable`) → unmapped (AC 3).
- Backend hands the test lane the final counts (products, offers, public products per category) for `tests/fixtures/demo.ts`.

## Page

T5.1.5. Build to 02-ux.md § Screens, § States, § Copy, § Tokens; this section only fixes the wiring.

- Route `src/app/(public)/categoria/[slug]/page.tsx`, `export const dynamic = 'force-dynamic'`, `searchParams: Promise<{ pagina?: string | string[] }>`.
- `const load = cache(getPublicCategoryPage)`, shared by `generateMetadata` and the page, as the product page does; page number from `parsePageParam(searchParams.pagina)`. `null` → `notFound()` (existing not-found.tsx).
- `productCount === 0` → empty state (S3), status 200, no summary/IVA/grid/nav.
- Price text via `formatEuroCents(card.lowestPriceCents)` from `@/server/money`; shop count via `t('Product.shopCount', { count: offerCount })`; "Desde" only when `offerCount >= 2`.
- Links: card → `/producto/<slug>`; pagination prev/next → `/categoria/<slug>` for page 1 (no `?pagina=1`), else `/categoria/<slug>?pagina=<n>`. Plain `<a>`/`Link`, no client component.
- Components in `src/components/`: `ProductCard.tsx` + `.module.css`, `ProductGrid.tsx` + `.module.css` (the `<ul>` grid), `Pagination.tsx` + `.module.css`, `CategoryEmpty.tsx` (+ css if needed). Components take display strings and hrefs as props (as OfferList), never read translations, config or the database.
- `messages/es-ES.json`: new `Category` namespace exactly as 02-ux § Copy. `src/app/globals.css`: the seven additive tokens of 02-ux § Tokens.
- No `/go` link on a card; no image area.

## Decisions

- **D-1.** Mapping key is (feed_id, feed_category), exact string match after trim. Not per network, not case-folded.
- **D-2.** The assignment is a column, `products.category_id`, not a read-time join through offers. It keeps the listing query and the visibility rule to one nullable column and gives OD-F a single answer.
- **D-3.** Only the importer writes `products.category_id` in this story; first mapped wins; never cleared. S4.2 owns admin re-assignment.
- **D-4.** "Mapped" lives only in `visibleProductWhere`. A second `isNotNull(categoryId)` anywhere else is a defect (seams).
- **D-5.** Shop count = number of visible offers (`offerCount`), identical to the product page's `offers.length`. Not distinct shops.
- **D-6.** Order = lowest visible price asc, then product id asc. Page size 24 as `CATEGORY_PAGE_SIZE`.
- **D-7.** Empty category has `pageCount` 1; any page > pageCount (including `?pagina=2` on an empty category) → null → 404.
- **D-8.** Invalid page values render page 1 with no redirect (C-4).
- **D-9.** Test fixture `insertProduct` defaults to a category (a lazily created test category via a new `insertCategory` helper); a test about unmapped passes `categoryId: null` explicitly. Keeps "defaults describe a fully VISIBLE state".
- **D-10.** No report change in the importer; no new CLI verb; no admin screen.

## Lanes

Order: contracts before consumers. Docs is close-out.

**Lane 1 — backend (T5.1.1, T5.1.2, T5.1.3, T5.1.4)**
- `src/db/schema/catalogue.ts`; `src/db/migrations/0002_category_mapping.sql` + `meta/*` (generated)
- `src/server/visibility.ts`
- `src/server/slug.ts` (`isWellFormedSlug`), `src/server/catalogue/product-page.ts` (use it)
- `src/server/catalogue/category-page.ts`, `src/server/catalogue/page-param.ts`
- `src/server/importer/validate.ts`, `src/server/importer/index.ts`
- `src/server/seed/demo-data.ts`, `src/server/seed/index.ts`, `demo/feeds/*.csv`
- Verification: `npm run lint && npm run typecheck && npm run test:unit` (integration breakage expected until lane 3; § Risks detail).

**Lane 2 — frontend (T5.1.5)**
- `src/app/(public)/categoria/[slug]/page.tsx`
- `src/components/ProductCard.*`, `ProductGrid.*`, `Pagination.*`, `CategoryEmpty.*`
- `messages/es-ES.json`, `src/app/globals.css`
- Verification: `npm run lint && npm run typecheck && npm run test:unit`.

**Lane 3 — test (T5.1.6)**
- `tests/support/catalogue.ts` first (D-9), then every file in § Affected tests.
- New: `tests/integration/category-page.test.ts` (C-3), `tests/integration/importer-categories.test.ts` (§ Importer, OD-F, AC 5-7), visibility additions in `tests/integration/visibility.test.ts`, `tests/unit/page-param.test.ts` (C-4), card/pagination/empty rendering in a unit component test beside `product-components.test.ts`, `tests/e2e/category.spec.ts` (phone 390 and desktop 1280 per 02-ux checks 3, 4, 14, 15, 16, 19; no cookie).
- New feed fixtures with a `category` column under `tests/fixtures/feeds/`.
- Verification: `npm run gate`.

**Close-out — docs:** `docs/decisions/` entry for D-1/D-2/D-3 (category assignment), CLAUDE.md demo steps only if the URL list changes, `docs/design/system.md` from 02-ux.

## Affected tests

Existing tests and shipped contracts the visibility change or the demo/seed change touches:

- `tests/support/catalogue.ts` `insertProduct` / `insertVisibleOffer`: products default to no category → non-public. Fix per D-9.
- `tests/integration/visibility.test.ts`, `product-page.test.ts`, `go-redirect.test.ts`, `go-counting.test.ts`, `go-privacy.test.ts` (and `tests/support/go.ts`): rely on visible fixtures; pass again once D-9 lands.
- `tests/integration/importer-preservation.test.ts`, `importer-matching.test.ts`, `importer-isolation.test.ts`, `importer-source.test.ts`, `importer-logging.test.ts`: any assertion that an imported product is public now needs a mapped category (fixture feeds lack the column); assertions that something stays hidden still hold.
- `tests/integration/importer-demo.test.ts` and `tests/fixtures/demo.ts` (`DEMO_COUNTS`, new demo constants): demo product/offer counts grow.
- `tests/integration/seed.test.ts`: `SeedReport` gains `categoryMappings`; idempotency expectation `categoryMappings: 0` on rerun.
- `tests/integration/migrations.test.ts`: add `feed_category_mappings` to the table list.
- `tests/unit/import-validate.test.ts`, `tests/unit/csv.test.ts` if it pins the header: new optional `category` column.
- `tests/unit/seams.test.ts`: add that `visibility.ts` names `categoryId` and that no other src file applies `isNotNull(products.categoryId)`.
- `tests/unit/route-classification.test.ts`: add `(public)/categoria/[slug]/page.tsx`.
- `tests/unit/messages.test.ts`: new `Category` keys and their ICU plurals.
- `tests/e2e/product.spec.ts`, `go.spec.ts`: demo products must stay public → depend on T5.1.4 mappings; no edit expected.
- Shipped contracts: C-11 (product page) gains "not public when unmapped"; C-15 (feed CSV) gains `category`; C-16 (import report) unchanged; C-18 (demo data) grows.

## Risks detail

- **Gate red between lanes.** Lane 1 makes every fixture product non-public; integration and e2e only return to green after lane 3. Lanes 1 and 2 therefore verify with lint, typecheck and unit; lane 3 runs the full gate.
- **bigint aggregates.** `count(*)` arrives as a string from node-postgres; without `::int` the card shows "NaN tiendas" or the plural breaks, and `pageCount` math silently concatenates.
- **Equality with the product page (AC 17).** Both reads must use the same visibility functions over the same join; any extra filter on one side breaks the equality.
- **Existing stacks.** After migrate, a running demo stack shows no products until `import-feeds` is re-run; the documented demo flow already includes it.
- **Recursive CTE in drizzle.** No first-class recursive builder is used; the CTE is a parameterised `sql` fragment with the category id bound, never string-concatenated.
