REPORT 2026-10-19-s5-1-category-browse/09
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   npm run test:unit
  result:    PASS
  detail:    22 files, 463 unit tests passed. Integration and e2e not re-run: 07-integration records gate exit 0 (705 vitest, 63 playwright). No external anchor applies; acceptance checked against the story text.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - No change requests: all 24 acceptance criteria are met, see § AC table.
  - Docs close-out: story status Draft to the shipped state, as the order says; not a finding.
  - Docs close-out: src/cli/seed.ts does not print SeedReport.categoryMappings (07-integration SHOULD_FIX, already an Open row).
  - Open rows from 08-ux-review stand: header focus ring, indicator spacing at 390 px, no live card showing the title clamp.

skill_calls:
  - none

risks:
  - AC 11 order within equal prices is products.id, stable but arbitrary; it satisfies OD-B but gives no meaningful order among ties.
  - AC 20 and the middle-page pagination layout were only seen on injected DOM (08-ux-review); the CSS holds, but no live data produces a title over 3 lines.
  - AC 7 and AC 5 rest on the importer reading the CSV column named category. A real affiliate feed with another column name imports unmapped and non-public until a header alias exists; out of scope here.
  - The e2e spec hard-codes the demo shape (26 filters, 24 plus 2); a change to the demo CSVs needs matching edits in tests/fixtures/demo.ts.
  - Test plan item "price formatting from cents" in the rendering group has no component test: the page formats, and e2e plus formatEuroCents's own tests cover it. Judged covered.

## Orchestrator brief

Verdict PASS. All 24 ACs met, none GAP or DRIFTED; test plan delivered in every group.
Visibility rule sits only in visibleProductWhere (src/server/visibility.ts:41); seams.test.ts pins it there.
Trust-state spot checks: no synthetic field in scope; null brand renders no line, no "null"; no new market-data caller; no cookie (e2e asserts it).
Hygiene: working tree clean, no stray files, no golden artifact touched.
Sections: § AC table (24 rows with file:line or test), § Test plan fidelity.

## AC table

Source paths are under C:\projects\investments\los-tres. Verdict: met for every row.

| AC | Status | Proof |
|---|---|---|
| 1 | SATISFIED | src/server/visibility.ts:41 isNotNull(products.categoryId); tests/integration/visibility.test.ts "returns null for an unmapped product"; go-redirect.test.ts unmapped row in the 404 table; demo-categories.test.ts /go 404 |
| 2 | SATISFIED | the condition is inside visibleProductWhere, used by product-page.ts and category-page.ts:90,108; tests/unit/seams.test.ts "tests products.category_id for null only in the visibility scope" |
| 3 | SATISFIED | src/server/importer/validate.ts:100 feedCategory null when empty; importer-categories.test.ts "stores the feed category as given (trimmed), and null for an empty cell" and "imports a feed with no category column" |
| 4 | SATISFIED | visibility.ts keeps isHidden, exists(visibleOffer) with feed/shop approved and inReview; visibility.test.ts hidden, unapproved feed, in-queue stay null; category-page.test.ts "lists none of: unmapped, hidden, unapproved-feed, in-queue, offerless" |
| 5 | SATISFIED | src/server/importer/index.ts:160 (known offers) and :180 (new) call assignCategory; importer-categories.test.ts "assigns the next import once a category gets mapped, through the known-offer path" |
| 6 | SATISFIED | importer-categories.test.ts "leaves category ids, products and offers unchanged and creates no duplicates"; assignCategory only updates where category_id is null (index.ts:207) |
| 7 | SATISFIED | offers.feed_category stored (importer/index.ts writeOffer); "does not fail or reject a run that meets an unmapped or empty category" |
| 8 | SATISFIED | src/app/(public)/categoria/[slug]/page.tsx route /categoria/[slug], ?pagina via parsePageParam, h1 is category.name; e2e category.spec.ts opens a demo category |
| 9 | SATISFIED | category-page.ts inSubtree recursive CTE, groupBy products.id; category-page.test.ts subtree group (child, grandchild, once not per path, cycle); demo "shows products in a root category only through its children" |
| 10 | SATISFIED | category-page.ts:108 applies visibleProductWhere and visibleOfferWhere; test "lists none of: unmapped, hidden, unapproved-feed, in-queue, offerless, or another category" |
| 11 | SATISFIED | category-page.ts:110 orderBy lowest price then products.id; tests "orders by lowest visible price ascending, then by product id" and "returns the same order on every request" |
| 12 | SATISFIED | CATEGORY_PAGE_SIZE 24; page.tsx:88-117 summaryPaged, Pagination with indicator, prev/next only where they exist; unit Pagination tests, e2e page 2 test |
| 13 | SATISFIED | page-param.ts and page-param.test.ts; category-page.ts:93 null past last page gives 404; tests "returns null past the last page and for an absurdly large page"; e2e "reads ?pagina=... as page 1" |
| 14 | SATISFIED | page.tsx:54 productCount 0 renders CategoryEmpty with es-ES copy, 200; category-page.test.ts "is empty, not missing, when every product in it is hidden, without offers, or lives unmapped"; e2e empty state test |
| 15 | SATISFIED | category-page.ts returns null for unknown or malformed slug, page.tsx:46 notFound(); tests "unknown and malformed slugs"; e2e 404 test |
| 16 | SATISFIED | components/ProductCard.tsx title, brand, price, shop count, single link to /producto/<slug>; unit "renders title, brand, from label, price and shop count" |
| 17 | SATISFIED | min(price_cents)::int (category-page.ts:95), formatted by formatEuroCents (page.tsx:104); product page orders asc(offers.priceCents); test "equals the first offer and the offer count of the same product page"; no shipping on the page |
| 18 | SATISFIED | count(*) over visible offers only; messages Product.shopCount ICU one/other; tests "ignores a cheaper offer that is not visible, in both the price and the count"; unit "no from label when one shop"; e2e plural count |
| 19 | SATISFIED | ProductCard.tsx:37 brand !== null; unit "renders no brand element, and no placeholder text, when the brand is null"; e2e brandless demo card; returns brand null not "" (category-page.test.ts) |
| 20 | SATISFIED | ux lane's CSS (ProductCard.module.css title clamp); 08-ux-review checks 11-12 on injected DOM; e2e no sideways scroll at 390 and 1280 with the 100-character title |
| 21 | SATISFIED | messages/es-ES.json Category namespace; components take display strings only; the only literals are aria-hidden arrows; tests/unit/messages.test.ts pins keys and plurals |
| 22 | SATISFIED | no client components; force-dynamic server page; e2e "server-renders the first page with JavaScript off and sets no cookie"; 08-ux-review check 28 |
| 23 | SATISFIED | demo CSVs carry categories; seed demoCategoryMappings; demo-categories.test.ts counts per category and root with products only through children (Automóvil, Herramientas have none of their own) |
| 24 | SATISFIED | demo CSVs: "Jardín > Cortacésped" has no mapping and DOS-103 has an empty category; demo-categories.test.ts unmapped on no page and /go 404; e2e "never lists the unmapped demo products" |

## Test plan fidelity

- Visibility (integration): unmapped excluded, mapping makes it appear, no feed category excluded, hidden/unapproved/queue stay excluded, page and /go 404 are all present (visibility.test.ts, go-redirect.test.ts, importer-categories.test.ts). The shared-scope regression is tests/unit/seams.test.ts plus category-page.test.ts using the same scope.
- Importer: capture, assignment, unmapped run succeeds, idempotent re-run, two-feed OD-F (first mapped wins, import order, never cleared) all present in importer-categories.test.ts.
- Listing read function: subtree and cycle, no duplicates, single-offer product, order and ties, page boundaries (24, 25, 26, beyond last), empty category, offerless product all present in category-page.test.ts.
- Rendering (unit): card with and without brand, one shop vs several, empty state, pagination at first and last page in category-components.test.ts (price formatting is the page's, covered by e2e).
- e2e: 32 tests in category.spec.ts cover open a category, cards with price and shop count, card to product page, subcategory product in parent, unmapped never shown, unknown slug 404, empty state, widths 390 and 1280.
- Guardrail 5: e2e asserts no cookie on the JS-off request and on a real browser visit.
- Hygiene: git status clean on the branch; no generated golden artifact in the diff; migration 0002 and its snapshot and journal are the expected generated set.
