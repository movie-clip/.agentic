REPORT 2026-10-18-s1-1-go-redirect/03
status:      DONE
verdict:     NONE

changed:
  - los-tres/src/components/OfferList.tsx — OfferRow gains goHref and goLabel; each row renders one plain anchor, rel "sponsored nofollow", data-testid offer-go
  - los-tres/src/components/OfferList.module.css — adds .go (inline-flex, min-height 2.75rem, existing custom properties only)
  - los-tres/src/app/(public)/producto/[slug]/page.tsx — maps goHref with goPath(offer.offerId) and goLabel with t('goToShop', { shopName })
  - los-tres/messages/es-ES.json — adds Product.goToShop "Ir a la tienda de {shopName}"
  - los-tres/tests/unit/product-components.test.ts — rewrote the no-link case to assert one sponsored anchor per row; fixtures carry goHref via goPath
  - los-tres/tests/unit/messages.test.ts — adds Product.goToShop to the key list and asserts the {shopName} placeholder

verification:
  command:   npm run lint; npm run typecheck; npm run test:unit
  result:    PASS
  detail:    lint clean; typecheck clean (tsconfig.json and tsconfig.cli.json); unit 17 files passed, 292 tests passed

contract_notes:
  - OfferRow in OfferList.tsx now requires goHref and goLabel; any other caller or fixture of OfferList must pass both
  - tests/e2e/product.spec.ts case "links nowhere in the offers and leaks no shop host, /go link or shipping text" is now stale; order 04 rewrites it

pack_corrections:
  - capabilities/frontend.md § Guardrails, in code terms (2) — replace "Until the `/go` slice ships, offer rows render no link at all (owner call Q4); the read contract still carries `offerId` for it." with "Each offer row has one plain `<a rel=\"sponsored nofollow\">` to `goPath(offerId)`; never `next/link` (it prefetches), never `target`, `noreferrer` or `referrerpolicy` (the source page comes from the Referer)."

handoff:
  - Selectors for order 04: row `[data-testid="offer-row"]`, link `a[data-testid="offer-go"]`, exactly one per row as a direct child of the li, in DOM order shop, price, link, updated
  - href is `/go/<offerId>` from goPath; rel is exactly "sponsored nofollow"; no target, no referrerpolicy, no noreferrer or noopener attribute
  - Link text is "Ir a la tienda de <shopName>" from Product.goToShop; the demo shop names appear in it, so a test of "no shop host in the HTML" must match hosts, not names
  - tests/unit/product-components.test.ts imports goPath from @/server/clicks/go-path so no test writes the literal /go/ prefix
  - Unit coverage still owed to order 04: page-level mapping of goHref and goLabel (the page is only exercised by e2e), and the next/link seam scan on OfferList.tsx

skill_calls:
  - none

risks:
  - frontend.md says a page may import src/server read functions and formatEuroCents; importing goPath from src/server/clicks/go-path follows that rule since the module is pure, but the pack does not name it
  - .go uses --color-link as a solid background with --color-bg text; contrast was not measured (link #0b5cad on white is about 6.9:1 by calculation, not by tool)
