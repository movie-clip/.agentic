REPORT 2026-10-21-s5-2-home-category-tree/04
status:      DONE
verdict:     NONE

changed:
  - C:\projects\investments\los-tres\messages\es-ES.json — Home gains categoriesHeading, productCount, emptyHeading, emptyBody
  - C:\projects\investments\los-tres\src\components\CategoryEmpty.tsx — homeLabel optional; link paragraph omitted when undefined
  - C:\projects\investments\los-tres\src\components\CategoryTree.tsx — new: groups ul, h3 heading link, nested rows, plain anchors, testids per design
  - C:\projects\investments\los-tres\src\components\CategoryTree.module.css — new: 18rem group grid, outlined group, 44px rows, inset 3px focus ring
  - C:\projects\investments\los-tres\src\app\(public)\page.tsx — home: brand panel, h2 plus CategoryTree from getPublicCategoryTree(), or CategoryEmpty without link
  - C:\projects\investments\los-tres\src\app\(public)\page.module.css — new: panel fill, white tagline (.panel .tagline beats .page p), section title
  - C:\projects\investments\los-tres\src\components\SiteHeader.tsx — inner column div, CSS module classes, data-testid site-header-link
  - C:\projects\investments\los-tres\src\components\SiteHeader.module.css — new: edge-to-edge border, content-width column, 44px link, 3px ring at 2px offset
  - C:\projects\investments\los-tres\src\app\globals.css — removed .site-header and .site-header__name only; no token added

verification:
  command:   cd C:\projects\investments\los-tres && npm run lint && npm run typecheck && npm run test:unit
  result:    PASS
  detail:    lint clean, tsc (app and CLI) clean, unit 22 files / 464 tests passed.

contract_notes:
  - tests/e2e/home.spec.ts is now stale: h1 is inside home-panel, plus h2, h3 and links; populated home still has exactly one p (the tagline).
  - tests/unit/messages.test.ts must list the four new Home keys.
  - docs/design/system.md still describes the old header and has no brand panel or group grid; docs close-out replaces it (D-1 approved).
  - New props: CategoryTreeProps { groups: CategoryTreeGroupItem[] } where item = { key, href, name, count, children: CategoryTreeRow[] } (finished strings).

pack_corrections:
  - capabilities/frontend.md § Layout — lists ProductCard, ProductGrid, Pagination, CategoryEmpty. Replace with: "ProductCard, ProductGrid, Pagination, CategoryEmpty (homeLabel optional: no link when omitted), CategoryTree (home groups), SiteHeader (styles in SiteHeader.module.css)".
  - capabilities/frontend.md § Layout — add: "A single-class module rule loses to .page p; override it with a two-class selector under the container (.panel .tagline), never !important."

handoff:
  - Testids as 02-design § Testids: home-panel, category-tree, category-group, category-group-link, category-group-count, category-row, category-row-link, category-row-count, category-empty, site-header-link.
  - Home empty state is CategoryEmpty without homeLabel: 200, testid category-empty, no link, no categoriesHeading h2; panel still rendered. Page has two p there (tagline, body).
  - Group and row links are plain anchors to /categoria/<slug>; the count is a span inside the link, so link text reads "Filtros 26 productos".
  - Header link is the next/link at / with testid site-header-link; height is min 44px (tap-target) so the e2e can assert boundingBox height >= 44.
  - Test lane render tests: heading-only group has no nested ul; CategoryEmpty without homeLabel has no anchor.
  - UX-REVIEW: check 25 and 27 (focus rings) need a node Tab script; the 320px no-overflow check and long-name wrap were not rendered by me.

skill_calls:
  - none

risks:
  - Link rows use display: grid (columns 1fr auto, align-items baseline, align-content center) instead of the spec's flex: flex cannot centre content in a min-height row while baseline-aligning; visible result matches 01-ux § Screens C.
  - Not rendered in a browser by me; only lint, tsc and unit ran, so layout checks (1280 x=152 alignment, 3 columns, panel colours) are unverified until UX-REVIEW.
  - Header edit moves the site name on category and product pages at 1280 (x=24 to 152), as 01-ux risks said.
  - Group heading is rendered as a styled .headingLink with padding space-2 (about 56px high); child rows are 44px min.
