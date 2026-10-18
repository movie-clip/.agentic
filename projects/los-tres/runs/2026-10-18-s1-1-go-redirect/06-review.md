REPORT 2026-10-18-s1-1-go-redirect/06
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   npm run test:unit; npm run test:integration
  result:    PASS
  detail:    unit 20 files, 404 passed; integration 17 files, 169 passed (Compose db up). Anchor used: the S1.1 outline in 01-product.md read against code and tests, not against 02/03/04 reports. Gate and e2e not re-run (05 ran them).

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - No change request: all eight S1.1 acceptance items are met; proceed to close docs and protocol-lint.
  - Close docs may add the optional two-sentence addendum to docs/decisions/0009 (01-design § Docs and pack corrections owed); it needs the human's yes first. See risks for why it helps.
  - S1.3 and S6.2 should reuse tests/support/go.ts (callGo, allClicks, insertGoOffer); S6.2 adds robots and X-Robots-Tag in respond() (route.ts:11).

skill_calls:
  - none

risks:
  - The stated limit is in code (counting.ts:9-11) and in docs/product/mvp.md:156-157 as "best effort; the network's report is the authority", but "an unlisted bot still counts" is explicit only in counting.ts. Decision 0009, which the outline cites, does not carry the limit.
  - The unproven point: a real HEAD request reaching the running Next server is not counted. Every e2e offer is a demo offer, so the e2e cannot tell a skipped HEAD from a skipped demo click. Integration proves it only with hand-built Requests (go-counting.test.ts HEAD and OPTIONS cases). The route exports HEAD and OPTIONS explicitly (route.ts:34-35), so likely fine.
  - The e2e click-through (go.spec.ts:53-81) asserts the browser's request to tienda-demo-dos.example and does not land on a stub page. Playwright does not route a redirect target. The contract it proves (one /go request, Referer equals product page, redirect to the cheaper shop, no cookie) is intact, and 05 already ruled it non-blocking.
  - The Referer reaching source_page through the real server (Host plus Referer on a counted row) is proven only in integration. A proxy that rewrites Host would store null on every row; S9.1 must pass Host through.
  - The crawler regex /bot\/|\bbot\b|.../ is a judgement list with known false negatives, which is the stated limit; it also scores the user agent in memory only (seams.test.ts pins it to counting.ts).
  - Outline item 2 says "in-review" offers answer 404. The test plan's in-review case is covered through the visibility scope (go-redirect.test.ts, the 'offer is in review' row), not a separate rule.

## Orchestrator brief
- Verdict PASS: every S1.1 acceptance item is met, each with code file:line and a test that would fail if the rule were removed; see § Acceptance items.
- Test plan in 01-design § Tests owed is delivered case by case; two small deviations, neither a gap against the outline; see § Test plan fidelity.
- Stated limit is written in counting.ts:9-11 and docs/product/mvp.md:156-157; see § Stated limit.
- Trust-state spot checks and repo hygiene hold; see § Trust state and hygiene.
- No finding is blocking. Nothing to route as a change request.

## Acceptance items

Source: 01-product.md § Backlog, S1.1 acceptance outline (8 items) and finding 10 / D-1 (OD2).

| # | Item | Verdict | Code | Test that would falsify it |
|---|---|---|---|---|
| 1 | Each offer row links to `/go/<offer>` with a plain anchor; the shop URL is never rendered directly | met | OfferList.tsx:45-52 plain `<a href={goHref} rel="sponsored nofollow">`, no next/link; page.tsx:63 `goHref: goPath(offer.offerId)`; go-path.ts:7-12 | product-components.test.ts (one anchor per row, href, no target/noreferrer, no button); seams.test.ts (no next/link in OfferList); e2e product.spec.ts:93-130 (href `^/go/\d+$`, HTML holds no DEMO_SHOP_HOSTS host); e2e go.spec.ts last test (no /go request on load, hover, focus) |
| 2 | Visible offer answers 302 to the stored URL; hidden, unapproved, in-review, unknown answer 404 | met | route.ts:11-21; handle-go.ts:30-50, :72; offer-target.ts:43 (visibleProductWhere + visibleOfferWhere, one query) | go-redirect.test.ts: baseline 302 with normalised Location, no-store, empty body; one-change-at-a-time 404 and zero rows for feed unapproved, shop unapproved, offer hidden, offer in review, product hidden; unknown id; 9 malformed ids; non-http stored URL; non-ASCII Location. e2e go.spec.ts 302 and 404 ids |
| 3 | One click row holds offer, shop, product, time, source page only; no IP, user agent or cookie stored, set or logged | met | clicks.ts:11-40 (exactly six columns, check on source_page); 0001_clicks.sql; record.ts:19-25 (four-field type, only writer); handle-go.ts:37, :68 (only logs, fixed text with errorCode) | clicks-schema.test.ts (exact column set from information_schema, 23514 check, RESTRICT FKs); go-privacy.test.ts (sentinel UA, Cookie, X-Forwarded-For, X-Real-Ip, Referer query: row_to_json clean, no Set-Cookie, zero console calls on counted, 404 and skipped; forced insert and lookup failure log one fixed line); seams.test.ts (one writer, UA only in counting.ts, no client-address headers, no cookie in click modules) |
| 4 | Outbound links are marked sponsored for search engines | met | OfferList.tsx:47 `rel="sponsored nofollow"` | product-components.test.ts rel regex for both words; e2e product.spec.ts rel contains sponsored and nofollow |
| 5 | Counting: a row only for a real navigation; HEAD, OPTIONS, prefetch, known crawlers, demo-feed offers are redirected but not counted | met | counting.ts:50-57 `skipReason` (method, Purpose and Sec-Purpose, CRAWLER_PATTERNS, isDemoFeed); handle-go.ts:53-70 (skip gives redirect with no insert); offer-target.ts:37 `isDemoFeed: feeds.isDemo` | click-counting.test.ts (each rule alone on an otherwise countable request; 38 crawler strings, one per family; Chrome, Safari iOS, Firefox Android, CUBOT negatives); go-counting.test.ts (counted baseline row in the same test, then HEAD, OPTIONS, Purpose prefetch, Sec-Purpose prefetch, prefetch;prerender, Googlebot, demo offer each give the same 302 and no new row; browser, missing, CUBOT, headless UAs write one row; two GETs write two rows) |
| 6 | Crawler detection reads the user agent in memory against a short pattern list in code; never stored, logged or forwarded | met | counting.ts:26-37 (five regexes in code, no dependency), :53 (read into a local, tested, dropped) | seams.test.ts (`user-agent` or `userAgent` only in counting.ts, with a non-vacuity check); go-privacy.test.ts (UA sentinel absent from row and from console) |
| 7 | Stated limit: an unlisted bot still counts; click log is best effort; network report is the authority | met | counting.ts:9-11; docs/product/mvp.md:156-157 | click-counting.test.ts: missing UA, empty UA, HeadlessChrome, curl, python-requests, Wget all count (the limit as behaviour). See § Stated limit |
| 8 | The guardrail-5 test deferred from slice B lands here | met | n/a | go-privacy.test.ts, first test asserts the request was counted (302, one row) before asserting absence, so it is not vacuous |
| D-1 | Demo clicks not counted (OD2) | met | counting.ts:55; offer-target.ts:37 | go-counting.test.ts demo case; unit demo case; go-privacy 'logs nothing on a demo offer' |

Each ticket maps: T1.1.1 (clicks.ts, 0001_clicks.sql, record.ts), T1.1.5 (counting.ts), T1.1.2 (route.ts, handle-go.ts, offer-target.ts), T1.1.3 (OfferList.tsx, page.tsx, es-ES.json goToShop), T1.1.4 (tests below). No ticket is unbuilt.

## Test plan fidelity

Checked against 01-design § Tests owed, file by file.

- tests/unit/click-counting.test.ts: delivered, with every case in the plan including lowercase method, `Purpose: preview`, one string per family, four negatives, missing and empty UA, demo.
- tests/unit/click-source-page.test.ts: delivered, with same-origin, query and fragment dropped, `/`, case-insensitive host, userinfo, the null table, and the 200-character boundary.
- tests/unit/go-path.test.ts: delivered, goPath RangeError cases and parseOfferParam accept and reject tables.
- tests/unit/seams.test.ts extended: delivered, all seven scans from the plan, each with a non-vacuity check on the file it scans.
- tests/unit/route-classification.test.ts extended: delivered (`(public)/go/[offer]/route.ts` listed and public).
- tests/support/go.ts: delivered (callGo, allClicks, insertGoOffer).
- tests/integration/clicks-schema.test.ts, go-redirect.test.ts, go-counting.test.ts, go-privacy.test.ts: delivered with every case in the plan; health.test.ts stays green (169 integration pass).
- tests/e2e/go.spec.ts and product.spec.ts rewrite: delivered. Stale case at product.spec.ts:93 rewritten, not deleted; `no /go URL` assertion added to the real-browser case.
- Deviation 1: the click-through does not land at a stubbed shop page (Playwright cannot route a redirect target); it asserts the request to the shop host instead. Judged equivalent for the outline: item 2 is proven in integration, the browser path proves one /go request, Referer and cookie-free. Not a gap.
- Deviation 2: the click-through host `tienda-demo-dos.example` is hard-coded, guarded by the fixture assertion on the preceding line. Not a gap.
- Unit tests of page-level `goHref` and `goLabel` mapping: not in the plan; covered by e2e product.spec.ts. Not a gap.
- Counts: this report ran unit 404 and integration 169, matching 04-test. The e2e was not re-run here; 05 ran it (31 passed).

## Stated limit

- counting.ts:9-11: "a bot that is not on the list still counts, a missing user agent counts, and the click log is a best-effort count. The affiliate network's own report stays the authority for commission." A reader of the counting code finds it.
- docs/product/mvp.md:156-157 (§ Outgoing clicks): "The count is best effort; the network's report is the authority for commission." A reader of the product docs finds it, without the words "unlisted bot".
- Decision 0009 does not carry it. The outline cites 0009 for the limit; the optional addendum in 01-design would close that. Recorded in risks, not a verdict item: the outline asks that the limit be stated, and it is stated twice.

## Trust state and hygiene

- Synthetic badge: the slice adds no synthetic-flagged field to a public render. Not applicable.
- Nullable fields: `source_page` is the only nullable new column; it is never rendered. Not applicable. No dash rule is touched.
- Market-data callers: the slice adds none (guardrail 2: `/go` only emits a Location, nothing fetches a shop page). No mock owed.
- Hygiene: `git status` clean; 34 files in the diff, all within the design's lane fences; package.json, lock file, compose.yaml and .env.example are not in the diff; the migration and its meta snapshot and journal are committed together. No stray files. No story file exists for S1.1 (#19 marks "Story file: no"), so no status field to reconcile.
