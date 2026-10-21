REPORT 2026-10-21-s5-2-home-category-tree/07
status:      DONE
verdict:     PASS

changed:
  - C:\projects\investments\.agentic\projects\los-tres\runs\2026-10-21-s5-2-home-category-tree\07-ux-review.md — this UX review (no repo file edited)
  - C:\projects\investments\.agentic\projects\los-tres\runs\2026-10-21-s5-2-home-category-tree\screens\07-*.png — review screenshots (home, category, product, 404 at 390 and 1280, home at 320, focus, hover, injected-state renders)

verification:
  command:   Playwright (repo package, node scripts) against http://127.0.0.1:3010 on branch 35-home-category-tree; screenshots opened with Read; python C:\projects\investments\.agentic\scripts\check_report.py <report_to> --lane ux-review
  result:    PASS
  detail:    31 of 34 checks SATISFIED from screenshots and measured computed styles, 1 SATISFIED for the visible half only (22), 2 not checked (20, 21: no-products state not producible without destroying the demo DB). No GAP, no DRIFTED. Anchor: rendered page, real Tab presses.

contract_notes:
  - none

pack_corrections:
  - capabilities/ux.md § Producing the states — 01-ux proposed the no-products recipe `docker compose down -v` then `stack:up` without import. That destroys the demo volume the human relies on. Replace with: "home, no category has products — not producible without wiping the demo database; report not checked unless a separate empty database is available"

handoff:
  - Findings by check, evidence and the states table are in § Check results and § States below; every check cites a screenshot or measured value.
  - SHOULD_FIX: the h1 in the panel and the header link both read the site name, so "Los Tres" shows twice above the fold at 390 (screens/07-home-phone.png). Spec-defined, not blocking; consider at S6.2.
  - SHOULD_FIX: with only two demo groups the 1280 page leaves the right third empty (screens/07-home-desktop.png). This follows from the data, not from a CSS fault.
  - Test lane: the no-products render (checks 20, 21) rests on the integration test and render test only; no browser render has seen it.
  - Docs close-out: the screens in the run dir confirm the system approved in D-1 matches the build; copy 01-ux § Design system to docs/design/system.md.

skill_calls:
  - design:accessibility-review — not called, the floor was checked directly with real Tab presses and computed contrast values from the spec's tokens
  - frontend-design:frontend-design — not called, that skill is for UX mode

risks:
  - Checks 20 and 21 (no-products state) are not checked: reaching it needs a wiped or empty database. I made no attempt that touches the demo volume. Read of page.tsx shows the branch exists and renders CategoryEmpty without a link (consistency check only).
  - Checks 15, 16 and 18 were rendered by cloning DOM nodes in a throwaway browser session (extra third group, heading-only group, long and unbroken names, 12.345 count) because demo data has none. The shipped CSS is judged, not real data.
  - Check 22: the link and its text are rendered, but "from configuration" is only a consistency check (SiteHeader takes a siteName prop, page.tsx calls getSiteName()); I did not change the configured name.
  - Contrast was taken from the spec's token values (white on #0b5cad 6.9:1, #555 on white 7.5:1); computed colours on the page matched those tokens exactly; no separate contrast tool run.
  - Visited-link colour was not rendered; the CSS and spec agree but I did not click through to produce a visited state.

## Orchestrator brief

Verdict PASS. No blocking finding; no change request needed.
- 31 of 34 checks SATISFIED on screenshots plus measured computed styles at 390, 1280 and 320; check 22 satisfied for the rendered half only.
- Not checked: 20 and 21 (no-products state; needs an empty database; I would not wipe the demo volume).
- Shared header verified on home, category, product and 404: name at x=152 on desktop, x=24 on phone, 44 px link, 61 px bar, 3 px ring on first Tab on all three pages.
- Real Tab presses: header, then Automóvil, Filtros, Escobillas, Herramientas, its two children, in reading order; 3 px ring, inset on rows, unclipped.
- Category and product pages unchanged apart from the header (compared with screens/00-*).
- Two SHOULD_FIX notes in handoff, neither blocking. One pack correction (no-products recipe is destructive).
- Sections below: Check results (all 34, by number), States, Header on other pages.

---

## Check results

Screenshots are in `C:\projects\investments\.agentic\projects\los-tres\runs\2026-10-21-s5-2-home-category-tree\screens\`. "Measured" means computed style or bounding box from a Playwright script against the live page.

| # | Result | Evidence |
|---|---|---|
| 1 | SATISFIED | 07-home-phone.png, 07-home-desktop.png: panel first under header, fill rgb(11,92,173) = #0b5cad, radius 8px |
| 2 | SATISFIED | one h1 "Los Tres" inside `[data-testid=home-panel]` (h1 count 1); tagline text exact |
| 3 | SATISFIED | h1 and tagline colour rgb(255,255,255) measured; both read clearly in 07-home-phone.png |
| 4 | SATISFIED | 390: panel x=24, w=342, h=142, text left-aligned; first group top y=321, bottom 468, inside the 844 fold |
| 5 | SATISFIED | h2 "Categorías" 20px, weight 700, x=24, smaller than the 32px h1 |
| 6 | SATISFIED | each group: 1px #e2e2e2 border, 8px radius, bold blue heading row, rows divided by 1px #e2e2e2 (07-home-phone.png) |
| 7 | SATISFIED | name left, count right in 14px, weight 400, rgb(85,85,85); count and name share a baseline (y 340.4+19.6 vs 338.4+22.4) |
| 8 | SATISFIED | "1 producto" x4, "2 productos", "26 productos", "27 productos"; no "1 productos" |
| 9 | SATISFIED | heading links weight 700, rows 400; both rgb(11,92,173) |
| 10 | SATISFIED | home lists 6 links; Aceites y lubricantes absent; /categoria/aceites-y-lubricantes still 200 with its empty state |
| 11 | SATISFIED | all 6 listed links returned 200 and none showed "Aún no hay productos" |
| 12 | SATISFIED | all 6 hrefs are /categoria/<slug>; each page h1 equals the home name |
| 13 | SATISFIED | home count equals page count for all six, incl. Automóvil 27 (= 26 + 1) and Herramientas 2 |
| 14 | SATISFIED | 390: one column, groups at y=321.4 (h146.4) and y=483.8, gap 16px |
| 15 | SATISFIED | 1280: column starts x=152, track width 314.7 (three tracks, 976 wide); with a third group injected it sat at x=813, same y=297 (07-injected-desktop.png). Real data has two groups only |
| 16 | SATISFIED | injected heading-only group "Jardín": height 56.4, heading 54.4, only the border below (07-injected-phone.png) |
| 17 | SATISFIED | 390: rows a-height 44, heading rows 54.4, all >= 44 |
| 18 | SATISFIED (injected) | long name, 12.345 count, and a 76-character unbroken string wrap inside rows at 390, 1280 and 320; count stays right and first line; no overlap; scrollWidth equals clientWidth (07-injected-phone.png, -desktop, -narrow). No real long-named category exists |
| 19 | SATISFIED | scrollWidth = clientWidth at 390, 1280 and 320 on home (07-home-narrow.png); also with injected content |
| 20 | not checked | needs a database with no public products; not producible without wiping the demo volume (non-goal) |
| 21 | not checked | same reason; the populated home returns 200 |
| 22 | SATISFIED (rendered half) | header link "Los Tres" with href "/"; name comes from a siteName prop (consistency check only for config) |
| 23 | SATISFIED | link x=152 on home, category, product and 404 at 1280 (07-*-desktop.png); .page content x=152; 00-category-desktop.png had x=24 |
| 24 | SATISFIED | 390: header 61 px tall, link 44 px tall, 1px border full width |
| 25 | SATISFIED | real Tab on home, category, product: first stop is the header link, outline solid 3px rgb(11,92,173), offset 2px (07-focus-header-phone.png, -category-phone.png, -product-phone.png) |
| 26 | SATISFIED | real Tab order: header, Automóvil, Filtros, Escobillas y bombillas, Herramientas, Herramientas eléctricas, Herramientas manuales, then off the page |
| 27 | SATISFIED | row ring 3px, offset -3px, drawn inside the box, fully visible (07-focus-row-phone.png, 07-focus-grouphead-phone.png) |
| 28 | SATISFIED | at rest all 7 links have no underline; on hover and focus the name span is underlined, the count is not (header link underlines on hover) |
| 29 | SATISFIED | no cookie or consent element, 0 img, 0 input, 1 paragraph (the tagline), no featured products |
| 30 | SATISFIED | computed colours are only #1a1a1a, #fff, #0b5cad, #e2e2e2, #555; box-shadow none, transitions 0s |
| 31 | SATISFIED | 07-category-desktop.png and 07-category-phone.png match 00-category-*.png; the only difference is the header (name moved to x=152, bar 4 px taller, content shifts 4 px). Product page unchanged in layout (07-product-desktop.png). Layout beyond the header was not otherwise judged |
| 32 | SATISFIED | `lang="es-ES"` on every page; no English or key names in the body text |
| 33 | SATISFIED | Automóvil before Herramientas; Filtros before Escobillas y bombillas (alphabetical would reverse the second pair) |
| 34 | SATISFIED | the panel is the only filled block; groups are white, outlined, no shadow; no button in the panel (07-home-phone.png) |

## States

| State | Result |
|---|---|
| Home, populated | checked at 390, 1280, 320 |
| Some categories empty | checked: Aceites y lubricantes absent from home, 200 by URL |
| One category with count 1 | checked ("1 producto") |
| Heading-only group, long name, large count, unbroken string | checked by DOM injection only, labelled in checks 16 and 18 |
| No category has products | not checked (checks 20 and 21) |
| Loading, server error, JS off | not designed by the spec; page is server-rendered, links are plain anchors |

## Header on other pages

- Home, category, product and category 404 (`/categoria/no-existe`, 404) all show the same header at 390 and 1280: link at x=24 (phone) and x=152 (desktop), 44 px tall, bar 61 px, 1px #e2e2e2 border to the edges. See 07-product-phone.png and 07-notfound-*.png.
