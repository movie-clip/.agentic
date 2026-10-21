REPORT 2026-10-19-s5-1-category-browse/08
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   Playwright (repo install, chromium) against the live stack at http://127.0.0.1:3010 on branch 34-category-browse (HEAD daddce3): full-page screenshots at 390 and 1280 of every state, DOM and computed-style probes, real Tab key presses, hover, JS-off load
  result:    PASS
  detail:    28 checks on the rendered page at 390 and 1280: 25 satisfied live, 3 not fully checked live (11, 12, 14: no demo data produces them, injected DOM only). Real Tab presses used for focus.

contract_notes:
  - none

pack_corrections:
  - capabilities/ux.md § Producing the states — add rows. /categoria/filtros (26 products, 2 pages), /categoria/filtros?pagina=2 (last page, 2 cards), /categoria/escobillas-y-bombillas (one card, no brand, single page), /categoria/aceites-y-lubricantes (empty, 200), /categoria/no-existe and /categoria/filtros?pagina=3 (404).
  - capabilities/ux.md § Running the app — Playwright CLI cannot press Tab, but a short node script using the repo's playwright package can. Add: "for focus, run a node script with createRequire from the repo package.json, press Tab and screenshot; then focus is a screenshot check, not a consistency check".

handoff:
  - Verdict PASS: no blocking finding; every spec check that the live demo data can produce is satisfied at 390 and 1280, see § Check results.
  - Not checked live, injected DOM only: card title over 3 lines, unbroken 120-char word, big price with many shops, long brand. Clamp, ellipsis and containment held at 390, 320 and 1280 in 08-injected-edge-*.png.
  - Not checked live: pagination on a middle page (demo has 2 pages). Injected row at 390 fits one line with the indicator centred, 08-injected-middlepage-phone.png. Add a 3-page demo category if the gate should cover check 14.
  - SHOULD_FIX: the header site-name link shows the browser default 1px dark ring, not the 3 px --focus-ring the Accessibility floor names (08-focus-header-phone.png). File: src/components/SiteHeader.module.css or a global a:focus-visible rule in src/app/globals.css.
  - SHOULD_FIX: at 390 the page indicator touches the Siguiente border with 0 px gap on page 1 and has 7 px on a middle page (08-filtros-p1-phone.png, 08-injected-middlepage-phone.png). File: src/components/Pagination.module.css, indicator padding.
  - SHOULD_FIX: demo has no card with a title over 3 lines, so the clamp never shows on live data. Add one 160-character title to the demo feed (src/server/seed demo CSVs) so the e2e and review can see check 11 live.
  - Test lane: checks 3, 4, 14, 15, 16, 19 are satisfied here by screenshot and DOM, so e2e assertions on testids category-card, pagination-prev, pagination-next, pagination-indicator and category-empty match what renders.

skill_calls:
  - design:accessibility-review — not called, the pack's floor and the 28 checks were applied directly with real Tab presses and computed styles

risks:
  - The app container image is dated 2026-10-21 01:01; I could not confirm it was built from commit daddce3, but every spec string, testid and style matched the source, so I treated it as current.
  - The injected-DOM results use cloned live card markup with edited text. They prove the CSS rules, not that the importer or page produces those data shapes.
  - Real keyboard focus order was seen by Tab on pages 1 and 2 only; a page with both Anterior and Siguiente was not live, DOM order of both comes from Pagination.tsx (prev, indicator, next).
  - The card ring is drawn on the title link's ::after with `outline: none` on the link itself; it renders as a 3 px blue ring around the whole card (08-focus-card-phone.png), so check 25 holds, but a literal grep for outline: none matches.

## Orchestrator brief
verdict: PASS. No blocking finding, no change request needed.
Evidence: screenshots under screens/ named 08-*; 390 and 1280 for every state.
Sections below: § Check results (all 28, with screenshot), § States produced, § Accessibility and copy notes.
Not checked live (reported, not satisfied): middle-page pagination, title over 3 lines, unbroken word, big price. Injected-DOM evidence only.
Three SHOULD_FIX items in handoff (header focus ring, indicator spacing, demo row for the clamp); they become Open rows.
Two pack_corrections for capabilities/ux.md (state URLs, real Tab press).

## Check results

Screens are in `C:\projects\investments\.agentic\projects\los-tres\runs\2026-10-19-s5-1-category-browse\screens\`. Name shortened below: P = phone 390, D = desktop 1280.

| # | Result | Evidence |
|---|---|---|
| 1 | SATISFIED | 08-filtros-p1-phone.png, -desktop.png: h1 "Filtros" 32 px bold is the largest text, header name small |
| 2 | SATISFIED | same shots: "26 productos · Página 1 de 2" then "Precios con IVA incluido." both rgb(85,85,85); 08-single-page-phone.png reads "1 producto"; IVA is not inside cards |
| 3 | SATISFIED | 08-filtros-p1-phone.png: one column, cards 342 px wide at x=24; scrollWidth 390 at 390, also 320 |
| 4 | SATISFIED | 08-filtros-p1-desktop.png: 3 columns, card left 152 = h1 left 152 = product page 08-product-desktop.png; each row equal height (128 or 173), prices on one y |
| 5 | SATISFIED | title, brand, footer at card bottom in all cards; prices share one y per row (measured) |
| 6 | SATISFIED | compared 26 cards on both pages with their product pages: price text and "N tienda(s)" and "Desde" identical, 0 mismatches; format `5,55 €` with U+00A0 before the euro sign |
| 7 | SATISFIED | no envío or total in the HTML of the category page; one price per card |
| 8 | SATISFIED | 08-filtros-p1-phone.png FA-101: "5,55 €" and "1 tienda", no Desde |
| 9 | SATISFIED | 08-filtros-p1-phone.png OC 1234: "Desde 11,49 €" and "2 tiendas" |
| 10 | SATISFIED | 08-single-page-phone.png: lamp card has title then footer, no gap, no "null" |
| 11 | not checked live, injected DOM OK | demo has no title over 3 lines (the 100-char title is exactly 3 lines, 08-filtros-p1-desktop.png). Injected 160-char title: 3 lines, ellipsis, card 173 px, 08-injected-edge-phone.png and -narrow.png |
| 12 | not checked live, injected DOM OK | injected 120-char word: breaks into 3 lines with ellipsis inside the card, scrollWidth equals viewport at 390, 320, 1280 |
| 13 | SATISFIED (DOM) | 24 of 24 cards hold exactly one `<a>` with `/producto/` href; 0 `/go` links on the page |
| 14 | PARTLY, middle page not checked live | live: pagination 44 px high, indicator is a span, 08-filtros-p2-phone.png and 08-filtros-p1-desktop.png. Injected middle page at 390: prev 24-136, indicator 143-246 (centre 194.5), next 246-366 on one row |
| 15 | SATISFIED | 08-filtros-p1-phone.png: no Anterior, indicator centre 194.5 vs 195; 08-filtros-p2-desktop.png: no Siguiente, indicator at 640; no dead link rendered |
| 16 | SATISFIED | 08-single-page-phone.png and -desktop.png: no nav element and no "Página 1 de 1" text |
| 17 | SATISFIED | page 2 reads "26 productos · Página 2 de 2"; single page has no page part |
| 18 | SATISFIED (DOM) | Anterior on page 2 is `/categoria/filtros` |
| 19 | SATISFIED | 08-empty-phone.png, 08-empty-desktop.png: h1, h2 "Aún no hay productos en esta categoría" (20 px), sentence, "Volver al inicio" to `/`; no count, IVA line, ul or nav; status 200 |
| 20 | SATISFIED | `/categoria/no-existe` and `?pagina=3` both 404 with the existing screen, 08-404-slug-desktop.png and 08-404-past-phone.png; empty category `?pagina=2` also 404 |
| 21 | SATISFIED | `?pagina=0`, `abc`, `-1`, `1.5` return 200 with the same 24 titles as no query |
| 22 | SATISFIED | no img or placeholder in any category screenshot |
| 23 | SATISFIED | same system-ui stack, text rgb(26,26,26), link rgb(11,92,173), left edge 152 as 08-product-desktop.png |
| 24 | SATISFIED | hover computed: border rgb(11,92,173), title underlined, shadow none, transform none, transition 0s; 08-hover-card-desktop.png |
| 25 | SATISFIED | real Tab: 3 px solid rgb(11,92,173) ring, 2 px offset, around the whole card (08-focus-card-phone.png, -desktop.png) and on pagination links (08-focus-prev-phone.png) |
| 26 | SATISFIED | DOM order: header, 24 cards in visual order, then the pagination link; 0 positive tabindex; real Tab went header, card 123, card 124, Anterior on page 2 |
| 27 | SATISFIED | all strings in § Copy appear as written with accents and plurals; title "Filtros, página 2 \| Los Tres", description matches; html lang es-ES; no raw key seen |
| 28 | SATISFIED (DOM) | curl of the page contains the card titles; with JavaScript off, 24 cards render |

## States produced

- Populated, more than one page: /categoria/filtros (page 1, 24 cards) and ?pagina=2 (2 cards, last page partial, left-aligned at normal width, 08-filtros-p2-desktop.png).
- One page, one product, no brand: /categoria/escobillas-y-bombillas.
- Empty: /categoria/aceites-y-lubricantes. 404: unknown slug, page past the last, empty with ?pagina=2.
- Invalid page numbers: 0, abc, -1, 1.5.
- Narrow 320: pagination indicator wraps above and Anterior sits below, 08-pagination-p2-narrow320.png, no horizontal scroll.
- Loading and server error: not designed by the spec, not checked.

## Accessibility and copy notes

- Contrast: title rgb(26,26,26), muted rgb(85,85,85) on white, link rgb(11,92,173), and white on link on hover; all above the spec's ratios.
- Tap targets: pagination links 44 px high, 112 to 120 px wide; cards are the whole card.
- Focus: card, pagination and the empty-state link (08-focus-empty-phone.png, 3 px ring) match the spec; the header link uses the browser default ring, see SHOULD_FIX in handoff.
- Design quality: reads as the same product as the product page; plain, one blue, no shadow. Nothing template-like beyond the spec's own plain direction.
