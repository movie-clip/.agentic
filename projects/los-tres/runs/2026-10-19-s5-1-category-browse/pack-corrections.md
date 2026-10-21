# Pack corrections — 2026-10-19-s5-1-category-browse

## from 04-backend
  - capabilities/backend.md — Layout lists src/server/catalogue/ without its files. Replacement: "catalogue/ (product-page.ts, category-page.ts, page-param.ts)", and add isWellFormedSlug to the slug.ts mention.
  - capabilities/backend.md — Guardrails (1) says the scope is "approved feed, not hidden, not in the matching queue". Replacement: add "and product mapped to a category (products.category_id is not null)".
  - capabilities/backend.md — Guardrails (1) says seeds create nothing approved except is_demo and demo shops. Replacement: add "and insert the demo feed_category_mappings (on conflict do nothing); a mapping decides category only, never visibility of a feed".
  - capabilities/backend.md — Guardrails: add the importer rule "products.category_id is the one product column the importer sets after creation, only from null (first mapped wins), never cleared".


## from 05-frontend
  - capabilities/frontend.md — Layout lists no listing components. Replacement: add "Listing components: ProductCard, ProductGrid, Pagination, CategoryEmpty in src/components (display strings only); page-level styles in a page.module.css beside the page.tsx".
  - capabilities/frontend.md — Guardrails (2) names only offer rows. Replacement: add "A product card has one link, to /producto/<slug>, stretched over the card with a ::after pseudo-element on the title anchor; it never carries a /go link".
  - capabilities/frontend.md — Layout says nothing on the `.page p` rule. Replacement: add "`.page p { color: var(--color-muted) }` (specificity 0,1,1) beats a single-class module rule on any <p> inside .page; use a span or h2 for text that must not be muted, and p only for muted prose".
  - capabilities/frontend.md — Next.js and i18n lacks the listing conventions. Replacement: add "Listing pages read ?pagina through parsePageParam, call notFound() on a null read, link page 1 as the clean path with no ?pagina=1, and use plain <a> (not next/link) for card and pagination links".


## from 06-test
  - capabilities/testing.md — Shared scaffolding says insert helpers default to the fully VISIBLE state. Replacement: add "insertProduct defaults categoryId to a shared test category (defaultCategoryId, found by slug so it survives resetDatabase); pass categoryId: null for the unmapped state. insertCategory, insertCategoryMapping and insertListedProduct (a product with one visible offer per price) live in tests/support/catalogue.ts."
  - capabilities/testing.md — What must always be covered (1) lists category among reads. Replacement: add "A product with products.category_id null is not public: assert it on the shared scope (visibility.test.ts), the product page, /go and the category page; tests/unit/seams.test.ts keeps the isNotNull(products.categoryId) condition in src/server/visibility.ts only."
  - capabilities/testing.md — Shared scaffolding lacks the category fixtures. Replacement: add "Category feed fixtures are tests/fixtures/feeds/category-*.csv (mixed, ean-one/two/three, no-column); demo category expectations are DEMO_CATEGORY_COUNTS and friends in tests/fixtures/demo.ts, and DEMO_COUNTS carries publicProducts and categoryMappings."
  - capabilities/testing.md — Running tests says nothing on e2e selection. Replacement: add "Listing e2e select only by the data-testid values of the design contract; the category name is read by getByRole heading level 1. Category pages are server pages: parse request().get HTML with openRawHtml for JS-off checks."
  - capabilities/testing.md — Gotchas lack the heredoc rule for Python. Replacement: add "A Bash command holding several heredocs with apostrophes inside TypeScript strings failed to parse (exit 2, nothing ran): write test files with Write and run edit scripts from the scratchpad."


## from 08-ux-review
  - capabilities/ux.md § Producing the states — add rows. /categoria/filtros (26 products, 2 pages), /categoria/filtros?pagina=2 (last page, 2 cards), /categoria/escobillas-y-bombillas (one card, no brand, single page), /categoria/aceites-y-lubricantes (empty, 200), /categoria/no-existe and /categoria/filtros?pagina=3 (404).
  - capabilities/ux.md § Running the app — Playwright CLI cannot press Tab, but a short node script using the repo's playwright package can. Add: "for focus, run a node script with createRequire from the repo package.json, press Tab and screenshot; then focus is a screenshot check, not a consistency check".

