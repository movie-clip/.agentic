REPORT 2026-10-18-s1-1-go-redirect/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only design order, no command named

contract_notes:
  - New table `clicks` (src/db/schema/clicks.ts, migration 0001) is the one shape S1.3 will read; columns and the source_page check are fixed in § Click table and migration.
  - `/go/<offer>` is a new public HTTP contract (statuses, headers, empty bodies); the frontend link, the e2e specs and S6.2's robots rule depend on it, see § HTTP contract of the redirect.
  - `OfferRow` in src/components/OfferList.tsx gains `goHref` and `goLabel`; the product page maps them and the unit test `renders no link and no button` becomes false on purpose, see § Offer link.
  - messages/es-ES.json gains `Product.goToShop` with a `{shopName}` placeholder; tests/unit/messages.test.ts must list it, see § Offer link.
  - The comment on `PublicOffer.offerId` (product-page.ts:13) says the page must not render a link; it is now stale. The type itself does not change.
  - S3.3 must not hard-delete an offer that has clicks: `clicks.offer_id` is `on delete restrict`. The 'stop being public' wording in the brief already allows a flag; S3.3's design must keep it that way.
  - S9.1's reverse proxy must pass the original `Host` header through, or every source page is stored as null, see § Source page.

pack_corrections:
  - backend.md — Layout lacks `src/server/clicks/` and the guardrail 5 bullet lacks the click-row rule; exact wording in § Docs and pack corrections owed.
  - frontend.md — guardrail 2 says offer rows render no link until /go ships; that is now false; wording in § Docs and pack corrections owed.
  - testing.md — the guardrail 5 bullet and scaffolding list lack the `/go` helpers and the console-spy rule; wording in § Docs and pack corrections owed.
  - architecture.md — the Click log seam names no file; wording in § Docs and pack corrections owed.

handoff:
  - Dispatch 02 backend (T1.1.1, T1.1.5, T1.1.2 as one order, in the order written in § Lane split), then 03 frontend (T1.1.3), then 04 test (T1.1.4). Inputs for each: this file's named sections.
  - No owner question blocks dispatch. The plan adds no dependency (OD7), changes no CLAUDE.md § Stack line, and needs no new decision record.
  - Frontend needs only `goPath()` from the backend lane, so it could run in parallel; the protocol order is backend first and the plan keeps it.
  - Test lane verification is `npm run gate`; the stack must be rebuilt from the backend and frontend work first (`npm run stack:up` is part of the gate).
  - Close docs (existing run request) also applies the four pack corrections here; the optional 0009 addendum in § Docs and pack corrections owed needs the human's yes first.

skill_calls:
  - none

risks:
  - Reading the user agent in memory to skip crawlers is the owner's reading of guardrail 5 (stored or logged is forbidden, read is not). The brief flagged it; the plan stores and logs nothing and a source scan pins that. Umami's own browser detection is a separate question (S1.2).
  - Source page comes from the `Referer` header. A visitor or extension that blocks it gets `null`; behind a proxy that rewrites `Host` every row gets `null`. Both fail safe (nothing stored) but would blind S1.3's per-page view, which the brief does not promise.
  - OPTIONS is exported and redirects, as the brief says ('redirected as usual'). Next's default would be 204 with Allow. A CORS preflight to /go would fail on a redirect; nothing in the product makes one.
  - A 404 from /go has an empty body, so a visitor on a stale link sees the browser's bare error page, not the Spanish not-found page. Acceptable for the MVP; a producer call if it matters.
  - The crawler list is a judgement call that will have false negatives (stated limit) and, if written carelessly, false positives (a bare `bot` substring matches CUBOT phones). The plan forbids the bare substring and requires a negative test.
  - `headlesschrome` and `playwright` are left off the crawler list on purpose, so test browsers are counted like visitors. A headless bot therefore counts; the network report stays the authority.
  - Counting is provable only in the integration project. The e2e can write nothing to the development database and every e2e offer is a demo offer, so the e2e proves redirect, markup and absence of prefetch and cookies, never a counted row.
  - Whether `request.method` is `HEAD` when Next dispatches a HEAD to a handler is unverified here. The plan exports `HEAD` explicitly and requires a direct-call integration test plus an e2e `request.head`.
  - Next 16.4.2's automatic HEAD uses the GET handler (read in node_modules/next/dist/server/route-modules/app-route/helpers/auto-implement-methods.js); nothing else about route-handler behaviour was run in this session.
  - Every counted GET writes a row; a refresh or double click counts twice. Deduping needs an identifier the guardrail forbids storing.
  - S8.4 will rewrite `visibleProductWhere`. `/go` keeps working only if the product-hidden condition survives that rewrite; the hidden-product test in § Tests owed is the tripwire.

## Orchestrator brief
- Verdict: S1.1 is buildable as briefed; no owner question blocks dispatch; no dependency (OD7: none) and no decision record.
- Lanes: 02 backend (T1.1.1, T1.1.5, T1.1.2), 03 frontend (T1.1.3), 04 test (T1.1.4); files and verification per lane in § Lane split.
- § HTTP contract of the redirect: route `src/app/(public)/go/[offer]/route.ts`, numeric offer id, 302 / 404 / 503, GET+HEAD+OPTIONS, no-store, no cookie.
- § Click table and migration: `clicks` has id, offer_id, shop_id, product_id, created_at, source_page; migration 0001; DB check on source_page.
- § Visibility and demo detection: reuse `visibleOfferWhere` + `visibleProductWhere` (visibility.ts:20, :30); demo is `feeds.is_demo` (sources.ts:44), no schema change.
- § Counting rules: one pure `skipReason()` in counting.ts covers method, prefetch, crawler, demo; user agent never leaves that function.
- § Source page: same-origin `Referer`, path only, strict regex, else null.
- § Offer link: plain `<a>` with `rel="sponsored nofollow"`, key `Product.goToShop`, href from `goPath()`.
- § Modules and reuse and § Decisions for engineers: file map and G-1 to G-14 so lanes decide nothing alone.
- § Tests owed: every T1.1.4 case, including the guardrail-5 test deferred from slice B.
- § Docs and pack corrections owed: four pack edits, one optional 0009 addendum, stale tests to rewrite.

## HTTP contract of the redirect

Route file: `src/app/(public)/go/[offer]/route.ts`. It lives under `(public)`, so `classifyRoute` (tests/support/routes.ts) already reads it as public (guardrail 3); no role check applies to a redirect that anyone may follow. `export const dynamic = 'force-dynamic'`. It exports `GET`, `HEAD` and `OPTIONS`, all the same function, each `(request: Request, ctx: { params: Promise<{ offer: string }> }) => Promise<Response>`; `params` is a `Promise` in Next 16. Any other method gets Next's own 405.

`<offer>` is `offers.id`, the integer already exposed as `PublicOffer.offerId` (product-page.ts:14), not a slug.

| Case | Status | Headers | Body |
|---|---|---|---|
| id is valid, offer is visible (counted or not) | 302 | `Location: <new URL(offers.url).href>`, `Cache-Control: no-store` | none |
| id malformed, unknown, or offer not visible (unapproved feed or shop, offer hidden, in review, product hidden) | 404 | `Cache-Control: no-store` | none |
| stored URL does not parse or is not `http:`/`https:` | 404 | as above | none |
| the visibility lookup throws | 503 | `Cache-Control: no-store` | none |

- No `Set-Cookie`, no custom header, no body, on any row. The route never reads or writes a cookie.
- `Location` is the normalised `new URL(stored).href`, never the raw string: `Headers` throws on a non-ASCII byte, and `URL` percent-encodes it.
- Excluded requests (HEAD, OPTIONS, prefetch, crawler, demo) get exactly the same 302 as a counted one. Only the row differs.
- The click insert failing does not change the response: the visitor is still redirected (G-8).
- All responses are built by one function in route.ts (`respond(result)`), so S6.2 can add a header such as `X-Robots-Tag` in one place. Nothing in S1.1 adds one.
- The module that decides is `handleGo` (§ Modules and reuse). route.ts only adapts `Request` to `GoRequest` and `GoResult` to `Response`.

## Click table and migration

File `src/db/schema/clicks.ts`, re-exported from `src/db/schema/index.ts`. It imports only `drizzle-orm` and sibling schema files (that directory's rule). The table is the guardrail 5 contract: these columns and no others.

| Column | Type | Null | Notes |
|---|---|---|---|
| `id` | `integer` identity (`generatedByDefaultAsIdentity`) | no | primary key, same as every other table |
| `offer_id` | `integer` | no | references `offers.id`, `on delete restrict` |
| `shop_id` | `integer` | no | references `shops.id`, `on delete restrict`; `feeds.shop_id` of the offer **at click time** |
| `product_id` | `integer` | no | references `products.id`, `on delete restrict`; `offers.product_id` **at click time** |
| `created_at` | `timestamptz` | no | `default now()`, the database clock; the code never passes a time |
| `source_page` | `text` | yes | a site path or `null`, see § Source page |

- `shop_id` and `product_id` are snapshots, not derived by join later. A later merge or split (S7.4, S7.5) must not rewrite history.
- Check `clicks_source_page_format`: `source_page is null or (length(source_page) <= 200 and source_page ~ '^/([a-z0-9_-]+(/[a-z0-9_-]+)*/?)?$')`. A scheme, host, `?`, `#`, `:` or `%` cannot be stored even by a buggy writer.
- Indexes `clicks_shop_id_created_at_idx (shop_id, created_at)` and `clicks_product_id_created_at_idx (product_id, created_at)`, for S1.3's per-shop and per-product range counts. No index on `offer_id`; S1.3 can add one.
- Deliberately absent: `ip`, `user_agent`, `cookie`, `referer`, `session`, `visitor`, `hash`, `is_bot`, `is_demo`, `counted`. Uncounted requests have no row at all (S1.3 depends on that), so no flag is needed.
- Migration: `npm run db:generate -- --name clicks` writes `src/db/migrations/0001_clicks.sql` and the meta snapshot; commit them. After generating, running it a second time must produce nothing. Never hand-edit; the app container applies it on start. The check constraint uses `sql` from `drizzle-orm` as `catalogue.ts:46` does.
- Update `tests/integration/migrations.test.ts` expected-table list to include `clicks`. `resetDatabase()` truncates every `public` table, so no change there.

## Visibility and demo detection

- The visibility rule exists. `visibleOfferWhere()` is `src/server/visibility.ts:20`: feed approved, shop approved, offer not hidden, offer not in review. `visibleProductWhere()` is `visibility.ts:30`: product not hidden and it has a visible offer. The product page uses both at `src/server/catalogue/product-page.ts:67`.
- `/go` reuses both, on the same join (`offers` → `products`, `feeds`, `shops`), in one query in `src/server/clicks/offer-target.ts`. It restates no flag: the existing source scan in tests/unit/seams.test.ts forbids `isApproved`, `isHidden` and `inReview` outside `visibility.ts`, `src/db/`, the seed and the importer.
- A visible offer on a hidden product answers 404, as the product page does. That is the guardrail 1 reading of 'a hidden item is never public'.
- Demo detection needs no schema change. `feeds.is_demo` already exists (`src/db/schema/sources.ts:44`), defaults false, and only the seed sets it true (`src/server/seed/index.ts:58`). An offer is a demo offer when its feed's `isDemo` is true; the offer reaches its feed through `offers.feedId` (`src/db/schema/catalogue.ts:57`).
- `isDemo` is selected in the same query as the redirect target and returned as `isDemoFeed`. It is not a visibility flag, so naming it outside `visibility.ts` is allowed.
- The shop URL is `offers.url` (`catalogue.ts:65`). Only `offer-target.ts` (plus the schema and the importer) may name it; a new source scan pins that (§ Tests owed).

## Counting rules

One pure function owns all four rules, in `src/server/clicks/counting.ts`. No `server-only` import (it must unit-test with no database), no I/O, no `console`.

```ts
export type SkipReason = 'method' | 'prefetch' | 'crawler' | 'demo';
export type CountingInput = {
  method: string;
  headers: Pick<Headers, 'get'>;
  isDemoFeed: boolean;
};
/** null means: write a click row. Any reason means: redirect, write nothing. */
export function skipReason(input: CountingInput): SkipReason | null;
export const CRAWLER_PATTERNS: readonly RegExp[];
```

| Rule | Check | Lives in |
|---|---|---|
| HEAD, OPTIONS | `method.toUpperCase() !== 'GET'` gives `'method'` | `skipReason` |
| Prefetch | `Purpose` or `Sec-Purpose` header, trimmed and lowercased, contains `prefetch`, `prerender` or `preview` (covers `prefetch;prerender` and Safari's `Purpose: preview`) gives `'prefetch'` | `skipReason` |
| Known crawler | the `User-Agent` header is tested against `CRAWLER_PATTERNS`, case-insensitive, gives `'crawler'` | `skipReason` |
| Demo offer | `isDemoFeed` true gives `'demo'` | `skipReason`; the flag comes from `offer-target.ts` |

- The user agent is read inside `skipReason` into a local variable and tested. It is not returned, put in an object, passed to any other function, logged or stored. A source scan pins that the string `user-agent` appears in `src/` only in `counting.ts` (§ Tests owed).
- Missing or empty `User-Agent` is **not** a crawler. It counts. The brief says 'known crawlers' and states that an unlisted bot counts.
- `CRAWLER_PATTERNS` is a short list in our own code, no dependency. Starting point; the backend lane may adjust it, but not use a bare `bot` substring (it matches CUBOT phones) and not add `headlesschrome`, `playwright`, `curl`, `wget` or `python-requests` (G-6):
  - generic: `/bot\/|\bbot\b|spider|crawl|slurp/i`
  - search and SEO engines: `googlebot`, `google-inspectiontool`, `adsbot-google`, `mediapartners-google`, `bingpreview`, `msnbot`, `yandex`, `baiduspider`, `duckduckbot`, `applebot`, `petalbot`, `semrush`, `ahrefs`, `mj12bot`, `dotbot`, `bytespider`
  - AI crawlers: `gptbot`, `claudebot`, `ccbot`, `amazonbot`, `perplexitybot`
  - link-preview fetchers: `facebookexternalhit`, `facebot`, `twitterbot`, `linkedinbot`, `slackbot`, `discordbot`, `telegrambot`, `whatsapp`, `skypeuripreview`
  - monitors: `uptimerobot`, `pingdom`, `lighthouse`
  - Each family above must have one positive unit case with a realistic user agent string, and at least three mainstream browser strings (Chrome on Windows, Safari on iOS, Firefox on Android) plus one CUBOT string must be negative.
- The stated limit goes in the file's header comment: an unlisted bot still counts, the click log is best effort, and the network's report stays the authority for commission (decision 0009).
- Prefetch headers matter in the browser only for speculative loads; the link itself must also never trigger one (§ Offer link).

## Source page

- The value is a **site path, not a URL**: `/producto/demo-filtro-de-aceite-oc-1234`, `/`, or `null`. No scheme, no host, no query, no fragment.
- It is derived in memory from the `Referer` header by `sourcePageFromReferer(referer: string | null, host: string | null): string | null` in `src/server/clicks/source-page.ts` (pure, no `server-only`). `host` is the request's `Host` header.
- Rules, in order; any failure returns `null`:
  1. `referer` and `host` are both non-empty.
  2. `new URL(referer)` parses (a throw is `null`), protocol is `http:` or `https:`.
  3. The referer's `host` (hostname and port) equals `host`, compared case-insensitively. A foreign origin gives `null`: a foreign page's path can carry a person's data and is not our page.
  4. The query string and fragment are dropped, never stored.
  5. The `pathname` is at most 200 characters and matches `^/([a-z0-9_-]+(/[a-z0-9_-]+)*/?)?$`. Percent signs, uppercase, dots, `@`, `//` all give `null`. Every route we own is lowercase kebab, so this loses nothing.
- No `?from=` parameter, no extra markup, no second header. `Referer` is already sent by the browser on a same-origin navigation under the default policy (`strict-origin-when-cross-origin`), and the browser sends the shop only our origin after the redirect.
- Therefore the link must not carry `rel="noreferrer"`, `referrerpolicy` or `target`, and no `Referrer-Policy` header is added anywhere (G-9). An e2e test pins that the browser's `/go` request does carry the product page as referer.
- The Referer header is read in the handler, passed to this function, and the header string goes no further. It is never logged.
- If the project ever puts `/go` behind a proxy that rewrites `Host`, rule 3 fails and every `source_page` becomes `null`. That is a fail-safe, and S9.1 must pass `Host` through.

## Offer link

- Component: `src/components/OfferList.tsx`. `OfferRow` gains two finished strings; the component stays a server component (no `'use client'`, no event handler, no state) and imports neither `next/link` nor `src/server`.

```ts
export type OfferRow = {
  key: string;
  shopName: string;
  price: string;
  updated: string;
  /** Relative path /go/<id>, from goPath(). Never a shop URL. */
  goHref: string;
  /** Link text, already translated: Product.goToShop with the shop name. */
  goLabel: string;
};
```

- Markup, one per offer row, inside `<li data-testid="offer-row">`:
  `<a href={goHref} rel="sponsored nofollow" data-testid="offer-go" className={styles.go}>{goLabel}</a>`
- A plain `<a>`: **not** `next/link` (it prefetches in production), no `target`, no `referrerPolicy`, no `rel` value `noreferrer` or `noopener` (no `target`, so `noopener` has no job, and `noreferrer` would blank the source page). `sponsored nofollow` marks it as a paid link for search engines; `sponsored` is the current value and `nofollow` the legacy fallback.
- Exactly one anchor per row, as a direct child of the `<li>`, and no other `<a>` or `<button>` in the offer list.
- `goPath(offerId: number): string` returns `/go/<id>`; it lives in `src/server/clicks/go-path.ts` (pure, no `server-only`) beside `parseOfferParam`. It throws `RangeError` for a non-integer or non-positive id, as `formatEuroCents` does for bad cents. `page.tsx` maps `goHref: goPath(offer.offerId)`; no component or test writes the literal `/go/` prefix except `go-path.ts`'s own test and the route folder name.
- Message key `Product.goToShop`, placeholder `{shopName}`, in `messages/es-ES.json`. Wording is the frontend lane's Spanish (for example 'Ir a la tienda de {shopName}'), no price, no mention of shipping (tests/unit/messages.test.ts already forbids both), no literal site name. The page calls `t('goToShop', { shopName: offer.shopName })`.
- Style: a class in `OfferList.module.css` using only the custom properties already in `globals.css`; the link is at least 44 px tall; the row layout is the frontend lane's. No new global class (decision 0011).
- The anchor's accessible name is its text, which already names the shop, so no `aria-label`.

## Modules and reuse

New files, all under `src/server/clicks/` (imports relative, never `@/`, per `eslint.config.mjs`):

| File | Exports | Notes |
|---|---|---|
| `go-path.ts` | `goPath(offerId)`, `parseOfferParam(raw): number \| null` | pure. `parseOfferParam` accepts only `^[1-9][0-9]{0,8}$`, so no overflow of the `integer` id and no leading zeros |
| `counting.ts` | `skipReason`, `CRAWLER_PATTERNS`, types | pure, § Counting rules |
| `source-page.ts` | `sourcePageFromReferer` | pure, § Source page |
| `offer-target.ts` | `getRedirectTarget(offerId): Promise<RedirectTarget \| null>` | `server-only`; the one query; `RedirectTarget = { offerId; shopId; productId; url; isDemoFeed }` |
| `record.ts` | `recordClick(db: Executor, click: ClickInsert): Promise<void>` | `server-only`; the **only** writer of `clicks`; `ClickInsert = { offerId; shopId; productId; sourcePage: string \| null }`; takes `Executor` from `src/db/client.ts:16` like the importer and matcher |
| `handle-go.ts` | `handleGo(req: GoRequest): Promise<GoResult>` | `server-only`; orchestrates |

```ts
export type GoRequest = { method: string; offerParam: string; headers: Pick<Headers, 'get'> };
export type GoResult =
  | { kind: 'redirect'; location: string }
  | { kind: 'not_found' }
  | { kind: 'unavailable' };
```

`handleGo` order: `parseOfferParam` (null gives `not_found`, no query) → `getRedirectTarget` (null gives `not_found`; a throw gives `unavailable` and `console.error('go: lookup failed (<code>)')`) → `new URL(target.url)` (throw or non-http gives `not_found`) → `skipReason(...)` → when null, `sourcePageFromReferer(headers.get('referer'), headers.get('host'))` and `await recordClick(getDb(), {...})` inside try/catch (`console.error('go: click not recorded (<code>)')` and continue) → `redirect` with `url.href`.

Also:
- `src/server/error-code.ts` exports `errorCode(error: unknown): string`, the body of the private function in `src/app/(public)/api/health/route.ts:15`. The health route imports it; its behaviour and `tests/integration/health.test.ts` do not change. `src/cli/shared.ts` keeps its own `describeError` (different contract). Do not add a third copy.
- Reuse by name: `visibleOfferWhere`, `visibleProductWhere` (`src/server/visibility.ts`), `getDb` and `Executor` (`src/db/client.ts`), the join shape of `getPublicProductBySlug` (`product-page.ts:48-68`), `PublicOffer.offerId`.
- Seams: **one writer of clicks** is `record.ts`; **one visibility scope** is unchanged; **one place that reads the shop URL** is `offer-target.ts`; **one place that reads the user agent** is `counting.ts`.
- `package.json` and `package-lock.json` are untouched. `src/config/env.ts`, `.env.example` and `compose.yaml` are untouched: the redirect needs no setting.

## Decisions for engineers

- G-1. The offer in the path is `offers.id`, an integer of 1 to 9 digits with no leading zero. Anything else is 404 before any query.
- G-2. A visible offer of a hidden product is 404. The lookup uses both `visibleProductWhere()` and `visibleOfferWhere()`.
- G-3. `shop_id` and `product_id` on the click are the values at click time and are never updated.
- G-4. Counted means: `GET`, no `Purpose`/`Sec-Purpose` of prefetch, prerender or preview, no crawler pattern, feed not demo. A missing user agent counts.
- G-5. Only `skipReason` looks at the method, the prefetch headers and the user agent. The handler and the route do not repeat any of those checks.
- G-6. `headlesschrome`, `playwright`, `curl`, `wget`, `python-requests` stay off the crawler list; test browsers and scripts are counted as visitors.
- G-7. The source page is the same-origin `Referer` path matching the strict regex, else `null`; it is a path, never a URL.
- G-8. A failed click insert is logged as a fixed line with an error code and the visitor is still redirected. A failed lookup is a 503.
- G-9. No `Referrer-Policy` header, no `referrerpolicy` attribute, no `rel="noreferrer"` anywhere on or around the link.
- G-10. The only log lines in the `/go` path are the two fixed failure lines in § Modules and reuse. Nothing logs a request header, an offer URL, a Referer or an id from a request. A success and a 404 log nothing.
- G-11. The anchor is `rel="sponsored nofollow"`, no `target`, no `next/link`; text from `Product.goToShop`.
- G-12. HEAD and OPTIONS are exported explicitly and redirect like GET; they are not counted.
- G-13. `Location` is `new URL(offers.url).href`. The stored URL is never returned from any public read function and never appears in a log, an error code or a test failure message.
- G-14. Tests live with the test lane. The backend lane writes no test file; the frontend lane edits only the two test files named in § Lane split. No lane edits an already-merged migration.

## Lane split

Order: 02 backend, 03 frontend, 04 test. Each lane's fence is its file list; anything else is a stop-and-report.

**02 backend** (T1.1.1, T1.1.5, T1.1.2; build in that order inside the one order: schema and write path, then counting and source page, then lookup, handler and route).
- Create: `src/db/schema/clicks.ts`, `src/db/migrations/0001_clicks.sql`, its meta files (generated), `src/server/clicks/{go-path,counting,source-page,offer-target,record,handle-go}.ts`, `src/server/error-code.ts`, `src/app/(public)/go/[offer]/route.ts`.
- Edit: `src/db/schema/index.ts` (export), `src/app/(public)/api/health/route.ts` (import `errorCode`), `src/server/catalogue/product-page.ts:13` (comment only: the page now links through `/go`), `tests/integration/migrations.test.ts` (add `clicks` to the expected tables; one line).
- Verify: `npm run lint`; `npm run typecheck`; `npm run db:up` then `npm run db:generate -- --name clicks` (a second run produces no new file) and `npm run test:integration`; `npm run test:unit`. Then `npm run stack:up`, `docker compose run --rm app import-feeds`, and `curl -i -o /dev/null http://127.0.0.1:${APP_PORT}/go/<id>` for a demo offer id read from the product page: 302 with `Location` on a `.example` host and no `Set-Cookie`. `docker compose logs app` shows no offer URL, no user agent, no referer.
- Report a contract note for every changed shape above and a `pack_corrections` entry for `backend.md`.

**03 frontend** (T1.1.3).
- Edit: `src/components/OfferList.tsx`, `src/components/OfferList.module.css`, `src/app/(public)/producto/[slug]/page.tsx` (map `goHref`, `goLabel`; import `goPath` from `@/server/clicks/go-path`), `messages/es-ES.json` (`Product.goToShop`).
- Edit these two tests only because the change falsifies them: `tests/unit/product-components.test.ts` (the case `renders no link and no button in the offers (no /go slice yet)` becomes: one anchor per row, href is the given `goHref`, rel contains `sponsored` and `nofollow`, no `target`, no `<button`, text is the given `goLabel`) and `tests/unit/messages.test.ts` (add `Product.goToShop` to the key list and assert it takes `{shopName}`).
- Verify: `npm run lint`; `npm run typecheck`; `npm run test:unit`.
- Report a `pack_corrections` entry for `frontend.md` (guardrail 2 sentence).

**04 test** (T1.1.4): all other tests, § Tests owed. Verify: `npm run gate` exits 0.

After 04: the integration gate checks contract alignment (route statuses against `respond`, `OfferRow` against the page, `Product.goToShop` against the unit test), the five seams, and that `package.json` did not change.

## Tests owed

Every case is table-driven where it can be, asserts the contract (status, header, stored row), not the implementation, and would fail if the rule it names were removed. Rules are tested **one at a time on an otherwise countable request**: a demo test uses a browser user agent and GET; a crawler test uses a non-demo feed; otherwise another rule masks the one under test.

Unit (no database):
- `tests/unit/click-counting.test.ts`: `skipReason` for GET with browser UA gives `null`; `HEAD` and `OPTIONS` give `'method'` (also lowercase method); `Purpose: prefetch`, `Sec-Purpose: prefetch`, `Sec-Purpose: prefetch;prerender`, `Purpose: preview` give `'prefetch'`; one realistic user agent per family in § Counting rules gives `'crawler'`; Chrome Windows, Safari iOS, Firefox Android and a CUBOT string give `null`; missing and empty UA give `null`; `isDemoFeed: true` gives `'demo'`.
- `tests/unit/click-source-page.test.ts`: same-origin product URL gives `/producto/x`; `?q=secret#frag` is dropped; `/` gives `/`; different host, different port, `null` referer, `null` host, `not a url`, `ftp:`, `//evil`, uppercase path, `%41`, `@` in path, `..`, a 201-character path all give `null`; host comparison is case-insensitive; userinfo in the referer is never in the result.
- `tests/unit/go-path.test.ts`: `goPath(12)` is `/go/12`; `goPath(0)`, `goPath(1.5)`, `goPath(-1)` throw `RangeError`; `parseOfferParam` accepts `1` and `999999999`, rejects `0`, `01`, `-1`, `1.5`, `1e3`, ` 1`, `1 `, `abc`, `''`, `1000000000`, `0x10`.
- `tests/unit/seams.test.ts` (extend): the string `user-agent` (case-insensitive, comments stripped) appears in `src/` only in `src/server/clicks/counting.ts`; `x-forwarded-for`, `x-real-ip`, `cf-connecting-ip`, `true-client-ip` appear nowhere in `src/`; `.insert(clicks)` appears only in `src/server/clicks/record.ts` and no `.update(clicks)` or `.delete(clicks)` appears anywhere; `offers.url` is named only under `src/db/`, `src/server/importer/` and `src/server/clicks/offer-target.ts`; `next/link` is imported nowhere in `src/components/OfferList.tsx`; no `src/` file under `src/app/(public)/go` or `src/server/clicks` mentions `cookie` or `set-cookie`.
- `tests/unit/route-classification.test.ts` (extend): `(public)/go/[offer]/route.ts` is in the route list and classified `public`.
- Frontend lane owns the `OfferList` and messages edits named in § Lane split.

Integration (real PostgreSQL, `assertTestDatabase`, `resetDatabase` in `beforeEach`, helpers from `tests/support/catalogue.ts`, whose defaults are the visible state). Add `tests/support/go.ts` with a `callGo(offerId, { method, headers })` that calls the exported `GET`/`HEAD`/`OPTIONS` of `@/app/(public)/go/[offer]/route` with `new Request(...)` and `{ params: Promise.resolve({ offer }) }`, and `allClicks()`.
- `tests/integration/clicks-schema.test.ts`: the `clicks` columns, read from `information_schema`, equal exactly `id, offer_id, shop_id, product_id, created_at, source_page` with the types in § Click table (a new column fails it on purpose); `source_page` rejects `https://x.example/a`, `/a?b=1`, `/A`, `//a`, and a 201-character path with `23514` / `clicks_source_page_format`; accepts `null`, `/`, `/producto/x`; deleting an offer, shop or product that has a click is refused (`23503`).
- `tests/integration/go-redirect.test.ts` (guardrail 1): baseline visible offer gives 302, `Location` equals the normalised stored URL, `Cache-Control: no-store`, empty body; then, changing exactly one thing each, 404 and **zero** `clicks` rows for: feed unapproved, shop unapproved, offer hidden, offer in review, product hidden, unknown id, and each malformed id (`abc`, `0`, `01`, `-1`, `1.5`, `1e3`, a 10-digit number); a stored URL with scheme `javascript:` gives 404; a stored URL with a non-ASCII character gives a 302 whose `Location` is ASCII; the 404 body never contains the stored URL; `GET`, `HEAD` and `OPTIONS` all give the same 302.
- `tests/integration/go-counting.test.ts` (counting): the baseline GET writes exactly one row with the right `offer_id`, `shop_id`, `product_id` and a `created_at` within the test's window; then `HEAD`, `OPTIONS`, `Purpose: prefetch`, `Sec-Purpose: prefetch`, a `Googlebot` UA, and a demo-feed offer each give the same 302 as the baseline and **zero** rows; a browser UA, a missing UA, and a CUBOT UA each write one row; a same-origin `Referer` writes `source_page`, a cross-origin one and a missing one write `null`, a same-origin one with `?q=secret` writes the bare path; two GETs write two rows.
- `tests/integration/go-privacy.test.ts` (guardrail 5, the test deferred from slice B): send one counted GET carrying a unique `User-Agent`, `Cookie`, `X-Forwarded-For`, `X-Real-Ip` and a `Referer` with a unique query value; then (a) `select row_to_json(c)::text from clicks c` contains none of those values; (b) the response has no `Set-Cookie`; (c) spies on `console.log/info/warn/error/debug` recorded no call during the request, and none of them contain any of the values or the offer URL; (d) force the insert to fail (a `vi.mock` of `record.ts` that throws an error whose message holds the offer URL and the UA): the response is still the 302, and the only logged text is the fixed line with a code, without the URL or the UA; (e) force the lookup to fail: 503 and the same fixed-line rule.
- `tests/integration/health.test.ts` must stay green after `errorCode` moves.

End-to-end (Playwright, against the Compose stack; writes nothing to the development database; offer ids are read from the product page, never hard-coded):
- `tests/e2e/go.spec.ts`: `request.get('/go/<id>', { maxRedirects: 0 })` for a demo offer gives 302, `Location` host is one of `DEMO_SHOP_HOSTS`, no `Set-Cookie`, `Cache-Control: no-store`; `request.head` and `request.fetch` with method `OPTIONS` also 302; `/go/999999`, `/go/abc` give 404 and no cookie; real click-through: open the shared product page, route the demo shop host to a stub with `page.route`, click the first `offer-go` link, expect the browser at the cheaper shop's host, the `/go` request's `referer` header equal to the product page URL, and `context.cookies()` empty; no request to `/go` happens on load, on hover or on focus of the links (no prefetch), after `networkidle`.
- `tests/e2e/product.spec.ts` (rewrite the stale case `links nowhere in the offers and leaks no shop host, /go link or shipping text`): each `offer-row` holds exactly one `a[data-testid="offer-go"]`, `href` matches `^/go/\d+$`, `rel` contains `sponsored` and `nofollow`, no `target`; `main a` count equals the row count; the HTML contains no `DEMO_SHOP_HOSTS` host and no shipping text; the existing `expectLocalScriptsAndLinks` still passes. Extend `a real browser visit sets no cookie and contacts no other origin` with 'and requests no /go URL'.

The e2e cannot show a counted row, because every e2e offer is a demo offer and e2e writes only through `import-feeds`. The counting rules are proven in the integration project; `docs` and this section say so.

## Docs and pack corrections owed

- `docs/product/mvp.md` § Outgoing clicks already states the counting rules and the limit; nothing to change. `CLAUDE.md` § Commands is unchanged (no new command, no new variable).
- Optional, needs the human's yes before a docs lane touches it: append to `docs/decisions/0009-click-log-and-analytics.md` under Consequences two sentences: 'The source page is a same-origin site path taken in memory from the Referer header; a query, a fragment or a foreign origin is never stored. Prefetch and HEAD requests, known crawlers (the user agent is read in memory against a short list and never stored or logged) and demo offers are redirected but not counted.' This records an interpretation of the record's 'source page' and 'no user agent'.
- backend.md, § Layout: after the `src/server` list add `clicks/` (`go-path.ts`, `counting.ts`, `source-page.ts`, `offer-target.ts`, `record.ts`, `handle-go.ts`) and `error-code.ts`; add that the public route `src/app/(public)/go/[offer]/route.ts` exports `GET`, `HEAD`, `OPTIONS` and builds every response in one `respond()`.
- backend.md, § Guardrails (5): replace 'The click row has no IP, user agent or cookie field.' with 'The click row (`src/db/schema/clicks.ts`) has no IP, user agent, cookie or referer field; `source_page` is a same-origin site path validated in code and by a database check. Only `src/server/clicks/counting.ts` reads the user agent, in memory. Only `src/server/clicks/record.ts` writes `clicks`.'
- frontend.md, § Guardrails (2): replace 'Until the `/go` slice ships, offer rows render no link at all (owner call Q4); the read contract still carries `offerId` for it.' with 'Each offer row has one plain `<a rel="sponsored nofollow">` to `goPath(offerId)`; never `next/link` (it prefetches), never `target`, `noreferrer` or `referrerpolicy` (the source page comes from the Referer).'
- testing.md, § What must always be covered (5): add 'Counting rules are proven in the integration project one rule at a time on an otherwise countable request; the e2e cannot show a counted row because every e2e offer is a demo offer. The privacy test spies on `console.*` and reads `row_to_json` of the click row.' and, under scaffolding, 'tests/support/go.ts: `callGo`, `allClicks`.'
- architecture.md, § The seams the product forces, Click log: replace the bullet with 'Click log (`src/server/clicks/record.ts` is the only writer; `src/server/clicks/counting.ts` the only reader of the user agent; `src/server/clicks/offer-target.ts` the only reader of `offers.url`; handler `src/server/clicks/handle-go.ts`, route `src/app/(public)/go/[offer]/route.ts`). Its row shape has no field for IP, user agent, cookie or referer (guardrail 5).'
- Stale tests the build must rewrite (not delete): `tests/unit/product-components.test.ts` case `renders no link and no button in the offers (no /go slice yet)` (frontend lane) and `tests/e2e/product.spec.ts` case at line 93 (test lane).
- S1.3, S6.2, S9.1 seams, nothing more: S1.3 reads only `clicks` with the two indexes above; S6.2 adds its header in `respond()` and a robots rule for `/go`; S9.1's proxy keeps the `Host` header and logs no client address.
