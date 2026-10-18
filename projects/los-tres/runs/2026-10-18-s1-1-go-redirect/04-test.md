REPORT 2026-10-18-s1-1-go-redirect/04
status:      DONE
verdict:     NONE

changed:
  - los-tres/tests/unit/click-counting.test.ts — new: skipReason one rule at a time, 38 crawler families, 4 negatives incl. CUBOT, missing and empty UA, demo
  - los-tres/tests/unit/click-source-page.test.ts — new: sourcePageFromReferer positives, query and fragment dropped, 16 null cases, 200-character boundary
  - los-tres/tests/unit/go-path.test.ts — new: goPath RangeError cases, parseOfferParam accept and reject tables
  - los-tres/tests/unit/seams.test.ts — extended: user agent only in counting.ts, no client-address header, one clicks writer, offers.url, no next/link in OfferList, no cookie in /go
  - los-tres/tests/unit/route-classification.test.ts — extended: (public)/go/[offer]/route.ts is listed and public
  - los-tres/tests/support/go.ts — new shared helper: callGo, allClicks, insertGoOffer, GO_HOST
  - los-tres/tests/integration/clicks-schema.test.ts — new: exact columns, source_page check 23514, FK delete rule RESTRICT, 23503 on offer delete
  - los-tres/tests/integration/go-redirect.test.ts — new: guardrail 1, 302 contract, five hidden causes, unknown and malformed ids, bad stored URLs, non-ASCII Location
  - los-tres/tests/integration/go-counting.test.ts — new: counted row fields, HEAD, OPTIONS, both prefetch headers, Googlebot and demo each skipped on an otherwise countable request, source page cases
  - los-tres/tests/integration/go-privacy.test.ts — new: guardrail 5 deferred test, row_to_json, no Set-Cookie, console spies, forced insert and lookup failure
  - los-tres/tests/e2e/go.spec.ts — new: 302 contract, HEAD and OPTIONS, 404 ids, real click-through with referer, no prefetch on load, hover or focus
  - los-tres/tests/e2e/product.spec.ts — stale case rewritten (one sponsored /go anchor per row), no-/go-on-load assertion added to the real-browser case

verification:
  command:   npm run gate
  result:    PASS
  detail:    gate exit 0; lint and typecheck clean; vitest 37 files, 573 passed, 0 skipped (unit 20 files 404 passed, integration 17 files 169 passed); playwright 31 passed, 0 skipped

contract_notes:
  - Pack testing.md needs the go.ts scaffolding and the counting-rules note, as 01-design § Docs and pack corrections owed lists; see pack_corrections.

pack_corrections:
  - capabilities/testing.md § What must always be covered (5) — add: "Counting rules are proven in the integration project one rule at a time on an otherwise countable request; the e2e cannot show a counted row because every e2e offer is a demo offer. The privacy test spies on `console.*` and reads `row_to_json` of the click row."
  - capabilities/testing.md § Shared scaffolding and gotchas — add: "`tests/support/go.ts`: `callGo(offer, {method, headers})` calls the route's GET/HEAD/OPTIONS with a countable default request (Host `shop.test`, browser UA; a header set to null is removed), `allClicks()`, `insertGoOffer({shop, feed, product, offer})` (visible by default, `feed.isDemo` for demo)."
  - capabilities/testing.md § Shared scaffolding and gotchas — add: "Force a failure in the real route by `vi.mock` of `@/server/clicks/record` or `@/server/clicks/offer-target` with `importOriginal` and a `vi.hoisted` switch; a `\b` in a Python non-raw string written into a test file becomes a backspace character, so write regexes with Write or a raw string."
  - capabilities/testing.md § Running tests — add: "Playwright `page.route` does not intercept the redirect target of a navigation (`/go` 302 to a shop host): the click-through asserts the browser's request to the `.example` host with `page.waitForRequest`, and the page ends on a chrome-error page."

handoff:
  - New shared helper tests/support/go.ts (callGo, allClicks, insertGoOffer, GO_HOST); S1.3 and S6.2 tests should reuse it.
  - Seam scans in tests/unit/seams.test.ts now pin: user agent only in counting.ts, offers.url only under src/db, importer and offer-target.ts, one writer of clicks.
  - Page-level mapping of goHref and goLabel is covered only by e2e (product.spec.ts), no unit test; the frontend handoff offered it as owed, the plan's § Tests owed did not list it.
  - Docs lane: the pack corrections above plus those in 02-backend.md and 03-frontend.md apply at close-out.

skill_calls:
  - none

risks:
  - The e2e click-through does not load a stubbed shop page: Playwright did not route the redirect target, so it asserts the browser requested tienda-demo-dos.example and ends on an error page. That is a deviation from 01-design § Tests owed ("expect the browser at the cheaper shop's host").
  - The e2e cannot show a counted row, since every e2e offer is a demo offer; counting is proven in integration only, as the design says.
  - The click-through test asserts the cheaper shop by the name order in tests/fixtures/demo.ts and a hard-coded host tienda-demo-dos.example, not read from DEMO_SHOP_HOSTS by index.
  - go-counting uses a plus or minus 60 s window for created_at, because the database clock is the Docker host's and the test clock is Node's.
  - Next sends its own vary header on /go (backend risk); no test pins header sets, so it does not matter.
  - No mutation run was done to confirm each skip test fails when its rule is removed; each skip test asserts a counted baseline row in the same test so a rule removal would show as a second row.
