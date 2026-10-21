REPORT 2026-10-21-s6-1-product-jsonld/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   python C:\projects\investments\.agentic\scripts\check_report.py <report_to> --lane design
  result:    PASS
  detail:    design plan written; check_report.py exit 0

contract_notes:
  - PublicProductPage (src/server/catalogue/product-page.ts) is unchanged; the JSON-LD is derived from it in full, see § Contract

pack_corrections:
  - none

handoff:
  - No backend lane: the existing getPublicProductBySlug read carries every field the JSON-LD needs, see § Data source
  - Frontend first (T6.1.1), then test (T6.1.2); files per lane, see § Lanes
  - Cents helper is centsToDecimalString(cents) in src/server/money.ts, digit slicing only, see § Cents to string
  - Script tag carries data-testid="product-jsonld" and type="application/ld+json", see § Selectors and tests

skill_calls:
  - none

risks:
  - The omit branch is unreachable today: the read returns null (404) with no visible offer; it exists for S8.4, see § Omit rule
  - EAN is stored raw; gtin is emitted only for 8, 12, 13 or 14 digits so a malformed feed value never reaches Google
  - dangerouslySetInnerHTML becomes the first use in src; an S8.6 lint rule banning it must allow-list src/components/JsonLd.tsx

## Orchestrator brief
- Decision: schema.org Product with one AggregateOffer (lowPrice, highPrice, offerCount, priceCurrency EUR); no Offer list, url, image, sku, availability or rating.
- Decision: data comes only from getPublicProductBySlug, the visible-offer read the page already renders; no backend lane, no schema change.
- Decision: builder returns null when offers is empty; the page then renders no script tag at all.
- Decision: cents to "19.99" by new centsToDecimalString in src/server/money.ts, string slicing, no division.
- Decision: serialised with JSON.stringify, then <, >, &, U+2028, U+2029 escaped as \uXXXX, in one exported function.
- Lanes: frontend T6.1.1 (money helper, builder, serializer, JsonLd component, page wiring) then test T6.1.2 (unit + e2e).
- § Contract: the exact object, field mapping, inclusion and exclusion reasons.
- § Data source: why no backend lane.
- § Cents to string: name, file, signature, examples.
- § Omit rule: the single rule and where it lives.
- § Script-tag safety: serializer and component spec.
- § Lanes: files per lane, order, verification commands.
- § Selectors and tests: testid, test cases, existing tests that break (none).
- Nothing blocks dispatch.

## Contract

Built per request from `PublicProductPage` (unchanged). Emitted object, keys in this order:

```
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": product.title,
  "description": product.description,                  only when !== null
  "brand": { "@type": "Brand", "name": product.brand }, only when !== null
  "mpn": product.partNumber,                           only when !== null, raw as stored
  "gtin": product.ean,                                 only when /^(\d{8}|\d{12,14})$/ matches
  "offers": {
    "@type": "AggregateOffer",
    "priceCurrency": "EUR",
    "lowPrice": centsToDecimalString(min priceCents),
    "highPrice": centsToDecimalString(max priceCents),
    "offerCount": offers.length (integer)
  }
}
```

TypeScript type, exported from the builder module:

```ts
export type ProductJsonLd = {
  '@context': 'https://schema.org';
  '@type': 'Product';
  name: string;
  description?: string;
  brand?: { '@type': 'Brand'; name: string };
  mpn?: string;
  gtin?: string;
  offers: {
    '@type': 'AggregateOffer';
    priceCurrency: 'EUR';
    lowPrice: string;   // "11.49"
    highPrice: string;  // "12.99"
    offerCount: number; // >= 1
  };
};
```

Absent values are omitted keys, never `null` or `""`.

Excluded, and why:
- `offers.url` / product `url`: the only offer link is `/go/<id>`, which S6.2 disallows in robots and the page marks nofollow; no absolute site URL is configured (canonical URLs are S6.2). Adding one is S6.2's call.
- Individual `Offer` items / `seller`: AggregateOffer is what the acceptance names; per-shop offers would need a url to be useful.
- `image`: the product has no image (placeholder only).
- `sku`: we have no own SKU; `mpn` is the honest field for the part number.
- `availability`, `aggregateRating`, `review`, `priceValidUntil`: the data does not support them (non-goal).
- Prices are strings with a dot and exactly two decimals: schema.org accepts Text, and a string keeps every float out of the payload (guardrail 4).
- low/high are integer min/max over `priceCents` (not first/last), so they do not depend on the read's sort order.

## Data source

- Only `getPublicProductBySlug(slug)` via the page's existing `load = cache(...)`, the same call that renders `OfferList`. No second query. It already applies `visibleProductWhere()` and `visibleOfferWhere()` (guardrail 1).
- Every field needed (title, description, brand, partNumber, ean, offers[].priceCents) is in `PublicProductPage`. No backend lane, no migration.

## Cents to string

- File: `src/server/money.ts`, the one money helper. The seams unit test forbids `/ 100` anywhere else; this helper divides nothing.
- Signature: `export function centsToDecimalString(cents: number): string`
- Throws `RangeError('cents must be a non-negative integer')` for non-integer, negative, NaN or Infinity, the same guard as `formatEuroCents`.
- Algorithm, string only: `const digits = String(cents).padStart(3, '0'); return digits.slice(0, -2) + '.' + digits.slice(-2);`
- Examples: 1999 -> "19.99"; 5 -> "0.05"; 50 -> "0.50"; 100 -> "1.00"; 100000 -> "1000.00"; 0 -> "0.00"; 4990 -> "49.90"; 999999999 -> "9999999.99". No thousands separator, always a dot.
- Docblock says it is the machine (schema.org) format; `formatEuroCents` stays the display format.

## Omit rule

- Single rule: `buildProductJsonLd(product)` returns `null` when `product.offers.length === 0`; the page renders `<JsonLd>` only when the result is non-null. No price from any other source (no last-known price).
- Today the read returns `null` (404) when there is no visible offer, so the branch is defensive; S8.4 makes it reachable and must not add a second rule.

## Script-tag safety

- Module `src/server/catalogue/product-jsonld.ts`: no `server-only`, `import type { PublicProductPage }` only, so unit tests can import it. Exports `ProductJsonLd`, `buildProductJsonLd(product: PublicProductPage): ProductJsonLd | null` and `serializeJsonLd(value: unknown): string`.
- `serializeJsonLd` = `JSON.stringify(value)`, then replace `<` with `\u003c`, `>` with `\u003e`, `&` with `\u0026`, U+2028 with `\u2028`, U+2029 with `\u2029`. The output is valid JSON that parses back to the same object and contains no `</script` or `<!--`.
- Component `src/components/JsonLd.tsx`: `export function JsonLd({ data }: { data: ProductJsonLd })` renders `<script type="application/ld+json" data-testid="product-jsonld" dangerouslySetInnerHTML={{ __html: serializeJsonLd(data) }} />`. Server component, no client JS, no CSS module (nothing visible).
- This is the only place JSON-LD is serialised.

## Lanes

1. **frontend, T6.1.1 (#129)**
   - `src/server/money.ts`: add `centsToDecimalString`.
   - `src/server/catalogue/product-jsonld.ts`: new, as in § Script-tag safety and § Contract.
   - `src/components/JsonLd.tsx`: new component.
   - `src/app/(public)/producto/[slug]/page.tsx`: `const jsonLd = buildProductJsonLd(product)`; return a fragment with `{jsonLd !== null && <JsonLd data={jsonLd} />}` before `<main>`. No change to metadata, copy or visible UI.
   - Verification: `npm run lint && npm run typecheck && npm run test:unit`.
2. **test, T6.1.2 (#130)**
   - `tests/unit/money.test.ts`: add `centsToDecimalString` cases.
   - `tests/unit/product-jsonld.test.ts`: new.
   - `tests/e2e/product.spec.ts`: add JSON-LD tests.
   - Verification: `npm run gate`.

## Selectors and tests

- Selector: `script[type="application/ld+json"][data-testid="product-jsonld"]`, read from the raw HTML of `request.get` (server-rendered, JS off), then `JSON.parse` its text.
- Unit, money: every example in § Cents to string; RangeError for -1, 1.5, NaN.
- Unit, builder: full object for a two-offer product with all fields; brand, description, partNumber null give absent keys; ean "123" gives no gtin, "2000000000015" gives gtin; unsorted offers still give the right low/high; offers [] gives null; offerCount equals offers.length.
- Unit, serializer: a title containing `</script><script>alert(1)</script>` and `<!--` gives output with no `<`, `>` or `&`, and `JSON.parse` returns the original object; U+2028 is escaped.
- e2e: DEMO_SHARED has exactly one such script: `@type` "Product", name = title, brand.name "MarcaDemo", mpn "OC 1234", gtin "2000000000015", lowPrice "11.49", highPrice "12.99", offerCount 2, priceCurrency "EUR". DEMO_DRILL: lowPrice = highPrice = "49.90", offerCount 1. Unknown slug (404): zero ld+json scripts.
- Absent-with-no-offer is covered by the builder unit test, because the page path 404s today; S8.4's T8.4.3 adds the page-level case.
- Existing tests that break: none expected. `expectLocalScriptsAndLinks` checks only `script[src]`; the `main a` count is unchanged since the script sits outside `<main>`; the seams `/ 100` test passes.
