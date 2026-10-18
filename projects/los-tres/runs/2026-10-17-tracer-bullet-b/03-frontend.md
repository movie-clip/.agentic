REPORT 2026-10-17-tracer-bullet-b/03
status:      DONE
verdict:     NONE

changed:
  - src/app/(public)/producto/[slug]/page.tsx — new; force-dynamic server page, cache(getPublicProductBySlug) loader, generateMetadata, notFound() on null, formatEuroCents and next-intl date
  - src/components/ProductDetails.tsx — new; h1, dl of present details, description as a text node, takes display strings only
  - src/components/ProductDetails.module.css — new; co-located styles using globals.css variables
  - src/components/OfferList.tsx — new; h2, shop-count, IVA note and ol of offer rows with no link or button
  - src/components/OfferList.module.css — new; co-located styles using globals.css variables
  - src/components/ImagePlaceholder.tsx — new; one generic div role=img placeholder
  - src/components/ImagePlaceholder.module.css — new; co-located placeholder box
  - src/i18n/request.ts — getRequestConfig now also returns timeZone 'Europe/Madrid'
  - messages/es-ES.json — new Product namespace with the ten C-14 keys

verification:
  command:   npm run lint; npm run typecheck; npm run build; SEED_DEMO_DATA=true npm run stack:up; docker compose run --rm -T app import-feeds; curl against http://127.0.0.1:3010 (see § Verification output); git status --porcelain
  result:    PASS
  detail:    lint exit 0, typecheck exit 0 (both tsconfigs), next build ok with /producto/[slug] dynamic; page shows 2 offers 11,49 € then 12,99 €; 200 and 404 responses both carry 0 Set-Cookie

contract_notes:
  - messages/es-ES.json Product namespace is live with the exact C-14 key names; tests/unit/messages.test.ts and the e2e specs can rely on them.
  - The rendered page matches C-13: test ids shop-count, offer-row, offer-shop, offer-price, offer-updated; one h1; role=img placeholder with aria-label from Product.imagePlaceholder.
  - The shop-count element is a p inside the offers section, after the h2 and before the IVA p, not inside the product details block.
  - src/i18n/request.ts now sets timeZone 'Europe/Madrid'; every next-intl date in the app uses it, so the e2e date assertion must expect Madrid dates.
  - Spanish wording is mine; the e2e should assert it through the message file, not literals, to stay in step with C-14.

pack_corrections:
  - frontend.md — Header and § Layout: replace "plain CSS with variables until the owner picks a styling system, O-4" with "CSS Modules (owner ruling, 2026-10-17): co-located `*.module.css`; `src/app/globals.css` keeps the reset and the CSS custom properties; add no new global classes."
  - frontend.md — § Layout: replace "A component never imports `src/db`, `src/server` or `src/config`" with "A component never imports `src/db`, `src/server` or `src/config`, and receives finished strings. A page (`page.tsx`) is a server component and may import `src/server` read functions and `formatEuroCents`; it never imports `src/db`."
  - frontend.md — § Spanish market conventions: replace the price example with "Format prices with `formatEuroCents` from `src/server/money.ts`, which forces `useGrouping: 'always'` so the output is `1.234,50 €`. The space before `€` is U+00A0. Plain `Intl.NumberFormat('es-ES')` drops the thousands separator on four digits."
  - frontend.md — § Next.js and i18n: add "`getRequestConfig` sets `timeZone: 'Europe/Madrid'`; dates are ICU placeholders in messages, for example `{date, date, medium}`. Counts use ICU plurals. Public product pages live at `src/app/(public)/producto/[slug]/page.tsx`, call one `cache()`-wrapped read function, and call `notFound()` on `null`."
  - frontend.md — § Guardrails (2): the "always /go/<offer>" rule has a slice B exception; add "Until the /go slice ships, offer rows render no link at all (owner call Q4); the read contract still carries `offerId` for it."
  - frontend.md — § Layout: add "A CSS Module file next to a component is imported as `styles` and typed by Next's `*.module.css` declaration; class names are hashed in the HTML, so tests select by `data-testid` or role, never by class."
  - frontend.md — § Layout: add "Working-copy files are CRLF on Windows (autocrlf): edit existing files with the Edit tool, and write new ones with Write; a heredoc containing an apostrophe inside a long Bash command failed to parse in Git Bash here."

handoff:
  - Test lane, route: /producto/demo-filtro-de-aceite-oc-1234 shows Tienda Demo Dos 11,49 € then Tienda Demo Uno 12,99 €, brand MarcaDemo, part number OC 1234, EAN 2000000000015, shop-count "2 tiendas"; the other demo slugs show "1 tienda".
  - Test lane, dates: priceUpdatedOn renders "Precio actualizado el 17 oct 2026" (ICU medium, Europe/Madrid); assert the shape with a regex or via the message, since the date changes per run.
  - Test lane, 404: an unknown slug and a malformed slug (Bad_Slug) both return 404 with the slice A not-found page and no Set-Cookie; the title there is the root Metadata title.
  - Test lane, no-link: the HTML contains no href inside main, no /go, and no .example host; the only anchor on the page is the site-header link to /.
  - Test lane, unit: ProductDetails and OfferList are pure display components; ProductDetails omits the dl when no detail exists and omits the description p when description is null, so a render test can cover those two branches.
  - Test lane, hashed classes: CSS Module class names are hashed in the HTML, so select by data-testid, role or tag.
  - Docs lane: nothing for CLAUDE.md; the frontend adds no command or env variable.

skill_calls:
  - none

risks:
  - An empty-string brand, part number or EAN would render an empty dd: the contract says empty means null (TD-42) so I rely on the backend and did not add a client-side guard.
  - The generateMetadata null branch returns an empty object and the page then calls notFound(); the 404 page shows the root layout title, which is acceptable but is not a product-specific title.
  - The page imports getSiteName from src/config, which the pack forbids for components only; this is the page, as the root layout does, so I read it as allowed.
  - The shop-count line sits in the offers section; C-13 lists it first but does not fix its parent, so I chose the section it describes.
  - The Spanish copy is mine and unreviewed by a native copywriter; "Referencia" labels the part number and "Dónde comprarlo" heads the offers.
  - The running Compose stack now holds my rebuilt app image with SEED_DEMO_DATA=true exported only in my shell; a later docker compose up -d from a shell without it falls back to the .env value, which is true.

## Orchestrator brief
- The product page at /producto/<slug> is built to C-11 to C-14; three components, CSS Modules, no new dependency, nothing outside the fence.
- Verified live on the rebuilt Compose stack: two offers cheapest first, 404 for unknown and malformed slugs, no Set-Cookie on either response.
- No offer row has a link; no .example host or /go string in the HTML.
- No contract gap found; seven pack_corrections for frontend.md, the first four verbatim from 01-design.
- § Verification output holds the command outputs and the git status.

## Verification output

```
> npm run lint        -> exit 0, no output from eslint
> npm run typecheck   -> tsc --noEmit && tsc -p tsconfig.cli.json --noEmit, no output
> npm run build       -> Next.js 16.4.2 (Turbopack), Compiled successfully, routes: ƒ /  ƒ /_not-found  ƒ /api/health  ƒ /producto/[slug]
> SEED_DEMO_DATA=true npm run stack:up    -> app, db, umami healthy
> docker compose run --rm -T app import-feeds
feed 1 "Tienda Demo Uno": imported rows=2 products_created=0 offers_created=0 offers_updated=2 rejected=0
feed 2 "Tienda Demo Dos": imported rows=2 products_created=0 offers_created=0 offers_updated=2 rejected=0
total: feeds=2 imported=2 skipped=0 failed=0
```

(The demo data was already imported by the backend lane, so created counts are 0.)

curl -s http://127.0.0.1:3010/producto/demo-filtro-de-aceite-oc-1234 (main element, reformatted one tag per line):

```
<html lang="es-ES"> ... <title>DEMO Filtro de aceite OC 1234 | Los Tres</title>
<h1>DEMO Filtro de aceite OC 1234</h1>
<dt>Marca</dt><dd>MarcaDemo</dd>  <dt>Referencia</dt><dd>OC 1234</dd>  <dt>EAN</dt><dd>2000000000015</dd>
<h2>Dónde comprarlo</h2>
<p data-testid="shop-count">2 tiendas</p>
<p>Precios con IVA incluido.</p>
<li data-testid="offer-row"> offer-shop "Tienda Demo Dos"  offer-price "11,49 €"  offer-updated "Precio actualizado el 17 oct 2026"
<li data-testid="offer-row"> offer-shop "Tienda Demo Uno"  offer-price "12,99 €"  offer-updated "Precio actualizado el 17 oct 2026"
```

Checks on the raw HTML and headers:

```
GET  /producto/demo-filtro-de-aceite-oc-1234  -> HTTP/1.1 200 OK, 0 Set-Cookie
GET  /producto/no-existe                       -> HTTP/1.1 404 Not Found, 0 Set-Cookie, body "Página no encontrada"
GET  /producto/Bad_Slug                        -> 404
grep -c example = 0 ; grep -c /go = 0 ; <a> inside <main> = 0 ; foreign script src = 0
GET  /producto/demo-taladro-percutor-650-w     -> shop-count "1 tienda"
```

git status --porcelain:

```
 M messages/es-ES.json
 M src/i18n/request.ts
?? src/app/(public)/producto/
?? src/components/ImagePlaceholder.module.css
?? src/components/ImagePlaceholder.tsx
?? src/components/OfferList.module.css
?? src/components/OfferList.tsx
?? src/components/ProductDetails.module.css
?? src/components/ProductDetails.tsx
```
