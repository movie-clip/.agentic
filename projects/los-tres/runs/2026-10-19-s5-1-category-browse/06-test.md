REPORT 2026-10-19-s5-1-category-browse/06
status:      DONE
verdict:     NONE

changed:
  - los-tres/tests/support/catalogue.ts — D-9: insertProduct defaults categoryId to a lazily created test category; new insertCategory, defaultCategoryId, insertCategoryMapping, insertListedProduct; insertVisibleOffer takes categoryId
  - los-tres/tests/support/go.ts — insertGoOffer product option accepts categoryId
  - los-tres/tests/fixtures/demo.ts — DEMO_COUNTS now 31/32/29 public plus categoryMappings; new DEMO_NO_BRAND, DEMO_LONG_TITLE, DEMO_UNMAPPED_CATEGORY, DEMO_UNMAPPED_EMPTY, DEMO_FILLER, DEMO_CATEGORY_COUNTS, DEMO_FEED_ROWS, DEMO_CATEGORY_NAMES
  - los-tres/tests/fixtures/feeds/empty-cells.csv — gained a category column with Varios so the page is public once mapped
  - los-tres/tests/fixtures/feeds/category-mixed.csv — new: mapped, unmapped, empty, padded and wrong-case category cells
  - los-tres/tests/fixtures/feeds/category-ean-one.csv — new: EAN 2000000000046 with category Cat Uno
  - los-tres/tests/fixtures/feeds/category-ean-two.csv — new: same EAN from another shop with category Cat Dos
  - los-tres/tests/fixtures/feeds/category-ean-two-empty.csv — new: the same row with an empty category cell
  - los-tres/tests/fixtures/feeds/category-ean-three.csv — new: a different EAN with category Cat Uno, for the per-feed mapping case
  - los-tres/tests/fixtures/feeds/category-no-column.csv — new: a feed with no category column
  - los-tres/tests/unit/feed-source.test.ts — demo header pinned with the trailing category column (the extra break from 04)
  - los-tres/tests/unit/import-validate.test.ts — category added to HEADER and the base record; new describe for trimming, null, no column, never rejects
  - los-tres/tests/unit/seams.test.ts — mapped condition only in visibility.ts; category read uses the shared scope; products updated only in importer and seed
  - los-tres/tests/unit/route-classification.test.ts — (public)/categoria/[slug]/page.tsx is public
  - los-tres/tests/unit/messages.test.ts — Category namespace keys, placeholders and ICU plurals
  - los-tres/tests/unit/page-param.test.ts — new: parsePageParam table, array, cap at MAX_SAFE_INTEGER
  - los-tres/tests/unit/category-components.test.ts — new: ProductCard, ProductGrid, Pagination, CategoryEmpty branches
  - los-tres/tests/integration/visibility.test.ts — new describe: unmapped is null, becoming mapped appears, hidden/unapproved/queued stay non-public
  - los-tres/tests/integration/go-redirect.test.ts — unmapped product row added to the 404 table (guardrail 1 at /go)
  - los-tres/tests/integration/product-page.test.ts — empty-cells case maps its category so the page is public
  - los-tres/tests/integration/importer-demo.test.ts — counts, report lines (28 and 4 rows) and prices updated for the grown demo data
  - los-tres/tests/integration/migrations.test.ts — feed_category_mappings added to the table list
  - los-tres/tests/integration/seed.test.ts — categoryMappings in counts and report, 5 then 0; new describe on seeded mappings
  - los-tres/tests/integration/category-page.test.ts — new: shape, price and count equality, subtree, cycle, order, pagination, empty, unknown and malformed slugs
  - los-tres/tests/integration/importer-categories.test.ts — new: capture, assignment, idempotency, first mapped wins, never cleared, per-feed mapping, admin overrides
  - los-tres/tests/integration/demo-categories.test.ts — new: demo category counts, unmapped demo products on no page, /go 404 for an unmapped demo offer
  - los-tres/tests/e2e/category.spec.ts — new: 32 tests by C-5 testids at default, 390 and 1280 widths, JS-off HTML, 404s, empty state, no-cookie checks

verification:
  command:   npm run gate
  result:    PASS
  detail:    gate exit 0: lint and typecheck clean; vitest 42 files, 705 tests passed (unit and integration); playwright 63 passed (8.7s), 32 of them in category.spec.ts

contract_notes:
  - none

pack_corrections:
  - capabilities/testing.md — Shared scaffolding says insert helpers default to the fully VISIBLE state. Replacement: add "insertProduct defaults categoryId to a shared test category (defaultCategoryId, found by slug so it survives resetDatabase); pass categoryId: null for the unmapped state. insertCategory, insertCategoryMapping and insertListedProduct (a product with one visible offer per price) live in tests/support/catalogue.ts."
  - capabilities/testing.md — What must always be covered (1) lists category among reads. Replacement: add "A product with products.category_id null is not public: assert it on the shared scope (visibility.test.ts), the product page, /go and the category page; tests/unit/seams.test.ts keeps the isNotNull(products.categoryId) condition in src/server/visibility.ts only."
  - capabilities/testing.md — Shared scaffolding lacks the category fixtures. Replacement: add "Category feed fixtures are tests/fixtures/feeds/category-*.csv (mixed, ean-one/two/three, no-column); demo category expectations are DEMO_CATEGORY_COUNTS and friends in tests/fixtures/demo.ts, and DEMO_COUNTS carries publicProducts and categoryMappings."
  - capabilities/testing.md — Running tests says nothing on e2e selection. Replacement: add "Listing e2e select only by the data-testid values of the design contract; the category name is read by getByRole heading level 1. Category pages are server pages: parse request().get HTML with openRawHtml for JS-off checks."
  - capabilities/testing.md — Gotchas lack the heredoc rule for Python. Replacement: add "A Bash command holding several heredocs with apostrophes inside TypeScript strings failed to parse (exit 2, nothing ran): write test files with Write and run edit scripts from the scratchpad."

handoff:
  - Orchestrator: gate is green on the whole S5.1 diff, so integration, ux-review and review can run. Phone and desktop layout assertions are overflow, 44 px pagination links and the long-title card inside the viewport only; the rendered visual check stays with ux-review.
  - Docs: C-11 gains not public when unmapped, C-15 gains the category column, C-18 demo counts are 31 products, 32 offers, 29 public (pinned in tests/fixtures/demo.ts).
  - Docs: no CLAUDE.md demo-step change is implied by the tests.
  - Future S4.2 admin remap: the integration test that re-points a mapping and expects the old assignment to stay (importer-categories.test.ts, "does not overwrite an assignment") pins D-3 and will need to change with the re-assignment path.

skill_calls:
  - none

risks:
  - The order says e2e selects only by C-5 testids; two queries are not testids: getByRole heading level 1 for the category name, and page.title(). C-5 has no testid for the h1, so I used the role query.
  - category.spec.ts hard-codes the demo shape (26 filtros, 24 plus 2, FA-101 at 5,55 EUR, shared filter at 11,49 EUR on page 1); changing the demo CSVs needs matching edits in tests/fixtures/demo.ts and that spec.
  - The /go 404 for an unmapped demo offer is proven in integration (demo-categories.test.ts), not e2e, because e2e cannot read an unmapped offer id from a public page.
  - Pagination single-row fit at 390 px was reported by frontend as having about 7 px of slack on Segoe UI; the e2e asserts only that the links stay inside the viewport, and passed on this host. A Linux CI font could overflow.
  - tests/fixtures/demo.ts and the other edited files keep their original line endings (CRLF); category.spec.ts, the new integration files and the new fixtures are LF.
