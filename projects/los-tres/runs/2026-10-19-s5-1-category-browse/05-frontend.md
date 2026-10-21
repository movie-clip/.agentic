REPORT 2026-10-19-s5-1-category-browse/05
status:      PARTIAL
verdict:     NONE

changed:
  - los-tres/src/app/(public)/categoria/[slug]/page.tsx — new server route: cache()-wrapped getPublicCategoryPage, generateMetadata, notFound on null, empty state, summary, grid, pagination
  - los-tres/src/app/(public)/categoria/[slug]/page.module.css — new: header block, h1 (--text-xl) and the two muted note lines
  - los-tres/src/components/ProductCard.tsx — new: one li, h2 holding the single stretched title link, optional brand, footer with Desde, price span and shop count; C-5 testids
  - los-tres/src/components/ProductCard.module.css — new: outlined card, 3-line title clamp, stretched link, hover border, focus ring on the card, footer pinned to the bottom
  - los-tres/src/components/ProductGrid.tsx — new: ul of ProductCard from a cards array (key per item), never sorts
  - los-tres/src/components/ProductGrid.module.css — new: repeat(auto-fill, minmax(min(16rem, 100%), 1fr)) grid, no media query
  - los-tres/src/components/Pagination.tsx — new: nav with plain anchors (previous, indicator, next); absent neighbour is not rendered; arrows aria-hidden
  - los-tres/src/components/Pagination.module.css — new: three-column grid keeping the indicator centred, 44 px links, wrap below 24rem
  - los-tres/src/components/CategoryEmpty.tsx — new: empty-state section (h2, body, Volver al inicio link to /)
  - los-tres/src/components/CategoryEmpty.module.css — new: h2 at --text-lg, spacing, focus ring on the home link
  - los-tres/messages/es-ES.json — new Category namespace, 12 keys exactly as 02-ux § Copy
  - los-tres/src/app/globals.css — the seven additive tokens (--radius, --tap-target, --focus-ring, --text-sm/md/lg/xl); no existing value changed

verification:
  command:   npm run lint && npm run typecheck && npm run test:unit
  result:    FAIL
  detail:    lint and typecheck pass; test:unit 403 passed, 1 failed: tests/unit/feed-source.test.ts:29 (the known red, owned by the test lane, expects the old CSV header without ,category). Nothing from this lane fails.

contract_notes:
  - messages/es-ES.json gains the Category namespace; tests/unit/messages.test.ts should add its keys and the ICU plurals (Category.summary, Category.summaryPaged).
  - src/app/globals.css gains seven tokens; docs/design/system.md (docs close-out) should record them as additive.
  - New route (public)/categoria/[slug]/page.tsx must be added to tests/unit/route-classification.test.ts as a public, dynamic page.
  - No type or contract drift against backend: the page imports getPublicCategoryPage and parsePageParam and reads only slug, name, page, pageCount, productCount, products as 04-backend fixed them.

pack_corrections:
  - capabilities/frontend.md — Layout lists no listing components. Replacement: add "Listing components: ProductCard, ProductGrid, Pagination, CategoryEmpty in src/components (display strings only); page-level styles in a page.module.css beside the page.tsx".
  - capabilities/frontend.md — Guardrails (2) names only offer rows. Replacement: add "A product card has one link, to /producto/<slug>, stretched over the card with a ::after pseudo-element on the title anchor; it never carries a /go link".
  - capabilities/frontend.md — Layout says nothing on the `.page p` rule. Replacement: add "`.page p { color: var(--color-muted) }` (specificity 0,1,1) beats a single-class module rule on any <p> inside .page; use a span or h2 for text that must not be muted, and p only for muted prose".
  - capabilities/frontend.md — Next.js and i18n lacks the listing conventions. Replacement: add "Listing pages read ?pagina through parsePageParam, call notFound() on a null read, link page 1 as the clean path with no ?pagina=1, and use plain <a> (not next/link) for card and pagination links".

handoff:
  - Route: /categoria/<slug>[?pagina=<n>]; page 1 links are /categoria/<slug> with no query; the card link is /producto/<slug>; the empty state links to /.
  - Testids per C-5, all as specified: category-summary (the p), category-card (li), card-title (the title a), card-brand, card-price-from, card-price, card-shop-count, pagination (nav), pagination-prev, pagination-next, pagination-indicator, category-empty (section; it holds h2, body and the home link, not the h1).
  - The pagination links contain an aria-hidden arrow span, so textContent is "← Anterior" and "Siguiente →"; use toContainText or the accessible name, not an exact textContent match.
  - Pagination links carry rel="prev" and rel="next"; the card and pagination links are plain anchors with no target and no rel other than that.
  - Summary text: pageCount above 1 gives "N productos · Página X de Y" (Category.summaryPaged), else "N productos" or "1 producto"; the IVA line is a second p with no testid, text "Precios con IVA incluido.".
  - Pagination is absent from the DOM when pageCount is 1 and for an empty category; an empty category renders h1 plus category-empty, no summary, no IVA line, no grid; ?pagina=2 on it is 404 by the backend.
  - Document title: "{category} | {siteName}" on page 1, "{category}, página {n} | {siteName}" from page 2; description is Category.metaDescription.
  - Demo facts for e2e (04-backend): filtros has 26 products, 24 then 2; page 1 starts at FA-101 (5,55 €); the shared filter card reads "Desde 11,49 €" and "2 tiendas"; aceites-y-lubricantes is empty.
  - Unit component test beside product-components.test.ts should cover: brand null renders no card-brand, priceFrom null renders no card-price-from, previous or next null renders no link, the card holds exactly one anchor and no /go href.
  - Checks 3, 4, 14, 15, 16 and 19 of 02-ux § Checks are the e2e ones; at 390 the pagination row is a single line on the Windows font (measured: links 112 and 120 px wide, indicator 104 px, all within 24 to 366 px).

skill_calls:
  - none

risks:
  - Pagination at 390 px is a single row only because the grid columns shrink to the links; it has about 7 px of slack with Segoe UI and the indicator sits roughly 8 px left of true centre, closer to Anterior than Siguiente. A wider system font (for example DejaVu on a Linux browser) would overflow before the 24rem wrap breakpoint; raise that breakpoint if it shows.
  - To make the row fit I removed the column gap and halved the arrow gap with calc(var(--space-1) / 2) and gave the indicator the same half-space padding; 02-ux S2 does not set these, and no new token was added for them.
  - 02-ux § Accessibility floor asks for the focus ring on the header link and "Volver al inicio" too; only the empty-state link got a module rule. The header link is in SiteHeader and a global a:focus-visible rule is outside this order's scope (seven tokens only in globals.css), so the browser default ring stays there.
  - The card title link uses outline: none on :focus-visible and draws the ring on its ::after pseudo-element instead (02-ux check 25 says no bare outline: none; this one has the replacement on the same rule family). A literal grep for "outline: none" will match it.
  - Card focus ring relies on the title having overflow hidden but not position, so the stretched ::after is not clipped by the clamp; this was seen in a static Chromium render only, not in the running app (no stack was started for this order).
  - I checked layout by rendering the module CSS and equivalent markup in a scratch HTML page in Chromium at 390, 320 and 1280; the real route was not rendered, so UX-REVIEW still owns the rendered check.
  - Existing code keeps hard-coded 2.75rem, 1.25rem and 0.875rem in OfferList.module.css; the order forbade touching it, so the new tokens are used by the new files only.
  - Price formatting uses formatEuroCents from the server, as the pack says; no arithmetic in components.
