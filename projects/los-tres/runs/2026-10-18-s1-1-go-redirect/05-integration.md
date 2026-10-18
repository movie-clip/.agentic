REPORT 2026-10-18-s1-1-go-redirect/05
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   npm run gate
  result:    PASS
  detail:    gate exit 0 on branch 19-go-redirect; lint and typecheck (both tsconfigs) clean; vitest 37 files, 573 tests passed; playwright 31 passed; stack rebuilt by the gate, then curl and docker logs probes clean

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - No change request is raised and no cr/ file exists; every blocking check below holds. Proceed to the review gate (acceptance) and close docs.
  - Run.md § Open row `risk | 04-test | e2e click-through deviates` is a non-blocking deviation: the orchestrator may close it as accepted, see § Severity call on the e2e click-through.
  - Close docs applies the four pack corrections already listed in 01-design, plus the extra ones in 02, 03 and 04 (backend.md demo-feed note, testing.md go.ts scaffolding, vi.mock recipe and the page.route redirect limit).
  - Open contract notes stay open for later slices: S9.1 must pass Host through, and S3.3 and S7.4/S7.5 must not hard-delete an offer, shop or product that has clicks (all three FKs are restrict).

skill_calls:
  - none

risks:
  - No test shows a counted row through the real Next server: e2e offers are all demo, so `Host` and `Referer` reaching `source_page` in the running image is proven only with hand-built Requests in integration. Fail-safe is null, so not blocking.
  - The click-through e2e hard-codes host `tienda-demo-dos.example` at tests/e2e/go.spec.ts:72 instead of indexing DEMO_SHOP_HOSTS. Line 70 asserts the fixture's first offer is Tienda Demo Dos, so a fixture change fails loudly. Not a change request.
  - No mutation run was done by the test lane (04-test risk). I read each skip test: every one asserts a counted baseline row in the same test, so removing its rule produces a second row and fails it. Judged adequate.
  - The crawler regex `bot\/` (counting.ts:28) would match a user agent holding the text `CUBOT/`; no real CUBOT string does. The plan's own list and the 02 risk already name it. Accepted, not reopened.
  - Next adds its own `vary` header to every /go response (seen with curl); it carries no data and the design's "no custom header" rule is about ours. Accepted.

## Orchestrator brief
- Verdict PASS: the combined S1.1 build holds; no change request, no CR file; `npm run gate` exit 0 (573 vitest, 31 playwright), see § Gate run.
- Contract alignment holds: /go statuses and headers, OfferRow to page mapping, Product.goToShop, and the clicks schema match 01-design; see § Contract alignment.
- The five seams hold and package.json, lock file, compose.yaml, .env.example and src/config are unchanged; see § Seams.
- Guardrails 1 and 5 were checked in code and by probing the rebuilt stack; see § Guardrails in code.
- The 04-test e2e deviation is non-blocking, severity: accepted, no CR; see § Severity call on the e2e click-through.
- § Reuse and consistency: named helpers reused, no second copy. § Coverage adequacy: tests pin the contract, skip rules fail if removed.
- Nothing blocks dispatch: next is review (acceptance), then close docs and protocol-lint.

## Gate run
- Ran `npm run gate` myself on 19-go-redirect (clean working tree, branch not edited): lint, typecheck, db:up, vitest, stack:up (image rebuilt), playwright, in that order.
- Exit 0. Vitest 37 files, 573 tests passed, none skipped; Playwright 31 passed. This matches 04-test's own report exactly.
- After the gate, with the rebuilt stack up, I probed the real server: `curl` of `/go/3` for a demo offer gave 302, `Location: https://tienda-demo-dos.example/p/DOS-100`, `cache-control: no-store`, no `Set-Cookie`, empty body; HEAD gave the same 302; `/go/999999` gave 404 with no-store; POST gave 405.
- `docker compose logs app` held none of the probe's user agent, referer query or any `.example` URL, and `select count(*) from clicks` read 0 (demo offers are never counted).

## Contract alignment
- `/go` statuses against 01-design § HTTP contract: route.ts:11-21 builds 302 with `Location` and `Cache-Control: no-store`, 503 and 404 with `Cache-Control: no-store`, all `new Response(null, ...)`, so no body and no cookie. `GET`, `HEAD`, `OPTIONS` all `= handle` (route.ts:33-35); `dynamic = 'force-dynamic'` at :6. Other methods get Next's 405 (curl-confirmed).
- handleGo order matches § Modules and reuse (handle-go.ts:30-72): `parseOfferParam`, lookup (throw gives `unavailable` plus the fixed line), `new URL` and http/https check, `skipReason`, then `sourcePageFromReferer` and `recordClick` in try/catch, then redirect with `location.href` (G-13, normalised).
- `OfferRow` (OfferList.tsx:11-14) has `goHref` and `goLabel` with the design's exact names and types; page.tsx:63-64 maps `goHref: goPath(offer.offerId)` and `goLabel: t('goToShop', { shopName: offer.shopName })`. The anchor (OfferList.tsx:45-52) is a plain `<a>` with `rel="sponsored nofollow"`, `data-testid="offer-go"`, no `target`, no `next/link`, no `noreferrer`, no `referrerPolicy`.
- `Product.goToShop` is "Ir a la tienda de {shopName}" (messages/es-ES.json:25); messages.test.ts lists the key and asserts `{shopName}`; product-components.test.ts asserts one anchor per row with href, rel, no target, no button and the label, importing `goPath` so no test writes the `/go/` literal.
- `clicks` against § Click table: clicks.ts:11-40 has exactly id (identity), offer_id, shop_id, product_id (all `not null`, `on delete restrict`), `created_at` timestamptz `defaultNow()`, `source_page` text null, the two (shop_id, created_at) and (product_id, created_at) indexes, and the `clicks_source_page_format` check with the design's regex and 200 limit. Migration 0001_clicks.sql matches and was generated (meta snapshot and journal are in the diff).
- Source-page regex is identical in clicks.ts:37 (database) and source-page.ts:8 (code), so the database check and the writer cannot disagree.
- Tests pin the contract rather than the implementation: clicks-schema.test.ts reads `information_schema` for the exact column set, tests the check with `23514` and the constraint name, reads FK delete rules, and the `23503` refusal. go-redirect.test.ts asserts status, headers and empty body from the real exported handlers.
- Deviations from the plan, all declared: the extra `..` / `%2e` rule in source-page.ts:28 (02 risk, needed so the plan's own `..` test case gives null); `CRAWLER_PATTERNS` grouped as five regexes with the plan's list verbatim; the e2e click-through (see § Severity call).

## Seams
- One visibility scope: offer-target.ts:43 uses `visibleProductWhere()` and `visibleOfferWhere()` on the same join shape as product-page.ts:48-68 and restates no flag; the existing seams test forbids `isApproved`, `isHidden`, `inReview` elsewhere and passed. visibility.ts is unchanged.
- One writer of clicks: only record.ts:20 contains `.insert(clicks)`; `src` grep found no `.update(clicks)` or `.delete(clicks)`; seams.test.ts pins it. `ClickInsert` has four fields and none about the visitor.
- One reader of the shop URL: `offers.url` is named under `src/server/clicks` only in offer-target.ts:36; seams.test.ts pins it to `src/db/`, the importer and that file.
- One reader of the user agent: `user-agent` appears in `src` only at counting.ts:53, read into a local and tested, never returned, stored, logged or passed on; seams.test.ts pins it, and `x-forwarded-for`, `x-real-ip` and the other client-address headers appear nowhere.
- One money helper and one role check: not touched by this slice. `errorCode` moved to src/server/error-code.ts with a byte-equivalent body (health/route.ts diff removes the private copy and imports it); `src/cli/shared.ts` keeps its own `describeError`, as planned; no third copy exists.
- package.json, package-lock.json, compose.yaml, .env.example and src/config show no change against origin/main (`git diff --stat` on those paths is empty; the file list has none of them). No dependency added (OD7).

## Guardrails in code
- Guardrail 1: the only path from a request to a shop URL is `getRedirectTarget`, whose single query joins offers, products, feeds and shops under both visibility conditions, so unapproved feed or shop, hidden or in-review offer and hidden product all give null and then 404 (handle-go.ts:40). The product page links only to `/go` paths built from `offerId`, so no page returns `offers.url`. The unit and integration cases change exactly one condition each from a visible baseline and assert 404 plus zero click rows.
- Guardrail 5, storage: the click row has no field for IP, user agent, cookie or referer, the writer's type has none, and the database check stops anything but a same-origin site path in `source_page`. go-privacy.test.ts sends sentinel UA, Cookie, X-Forwarded-For, X-Real-Ip and Referer query, reads `row_to_json` of the row and asserts none appear.
- Guardrail 5, logs: the only `console` calls on the path are handle-go.ts:37 and :68, both fixed text with `errorCode()` (a regex-bounded code or the word UNKNOWN, never a message). The privacy test spies on all five console methods for a counted request (zero calls), for 404 and skipped requests (zero calls), and for forced insert and lookup failures (exactly the fixed line, no URL, no UA). I confirmed the same on the live stack.
- Guardrail 5, cookie and headers: the route never touches a cookie; the redirect carries no `Set-Cookie` (integration and curl); `next.config.ts` has `poweredByHeader: false` and sets no referrer policy, matching G-9.
- Guardrail 2: nothing in the diff fetches a shop page; `/go` only emits a Location. Guardrails 3 and 4: the route sits under `(public)` and is classified public by the extended route-classification test; no float or money path was added.

## Reuse and consistency
- Reused by name: `visibleOfferWhere`, `visibleProductWhere`, `getDb`, `Executor`, the product-page join shape, `PublicOffer.offerId`, and `check`/`sql` usage as in catalogue.ts. Imports under src/server/clicks are relative, as eslint.config.mjs requires.
- The route follows the health route's shape (`dynamic`, one `respond`). Tests reuse tests/support/catalogue.ts helpers and `pgErrorOf`; the new tests/support/go.ts is the shared `/go` scaffolding the design asked for.

## Severity call on the e2e click-through
- The design asked the click-through to route the shop host to a stub with `page.route` and expect the browser at the cheaper shop's host. Playwright does not route a redirect target of a navigation, so tests/e2e/go.spec.ts:53-81 instead waits for the browser's own request to `tienda-demo-dos.example`.
- Call: NOT BLOCKING, no change request, no SHOULD_FIX file. The stub only gave the browser a page to land on; the contract under test is that following the link reaches `/go` once, carries the product page as `Referer`, is redirected to the cheaper shop, and leaves `context.cookies()` empty. All four are asserted (go.spec.ts:75-80), and `.example` never resolves so nothing leaves the machine.
- What would prove it false: if the first link pointed at the dearer shop, `waitForRequest` for `tienda-demo-dos.example` would hang and fail; if the redirect dropped the Referer, `goRequests[0].referer` would differ from `productUrl`. Both observations exist.
- Residual weakness is the hard-coded host (see risks); a fixture change fails at line 70 first, so it cannot drift silently.

## Coverage adequacy
- Skip rules are tested one at a time on an otherwise countable request, each beside a counted baseline in the same test, so removing a rule shows as a second row. Crawler coverage has one realistic string per family and four negatives including CUBOT, plus missing and empty UA, as the design required.
- The guardrail-5 test deferred from slice B exists and is not vacuous: it first asserts the request was counted (302 and one row) before asserting absence.
- Page-level mapping of `goHref` and `goLabel` has no unit test; the e2e product spec covers it (href shape, rel, no target, shop name in the link text, `main a` count). Accepted: the plan's § Tests owed did not list a unit case for it.
