REPORT 2026-10-21-s6-1-product-jsonld/02
status:      DONE
verdict:     NONE

changed:
  - C:\projects\investments\los-tres\src\server\money.ts — added centsToDecimalString(cents), digit slicing, RangeError guard like formatEuroCents
  - C:\projects\investments\los-tres\src\server\catalogue\product-jsonld.ts — new: ProductJsonLd type, buildProductJsonLd, serializeJsonLd

verification:
  command:   cd C:\projects\investments\los-tres && npm run lint && npm run typecheck && npm run test:unit
  result:    PASS
  detail:    lint clean; tsc and tsc -p tsconfig.cli.json clean; vitest unit 23 files, 476 tests passed

contract_notes:
  - Frontend imports buildProductJsonLd, serializeJsonLd and type ProductJsonLd from src/server/catalogue/product-jsonld.ts (relative to the component, via the @/ alias)
  - Test lane imports centsToDecimalString from src/server/money.ts and the three product-jsonld exports; no server-only, so unit tests import them directly
  - PublicProductPage, schema and migrations are unchanged; no contract doc lags

pack_corrections:
  - capabilities/backend.md — Layout lists catalogue/ as product-page.ts, category-page.ts, category-tree.ts, page-param.ts; add product-jsonld.ts (pure builder and serializer, no server-only)

handoff:
  - Test cases for money: every example in 01-design § Cents to string (1999, 5, 50, 100, 100000, 0, 4990, 999999999) and RangeError for -1, 1.5, NaN, Infinity
  - Test cases for builder: two-offer full object; null brand, description, partNumber give absent keys; ean "123" gives no gtin; "2000000000015" gives gtin; unsorted offers give right low/high; offers [] gives null; offerCount equals offers.length
  - Test cases for serializer: title with script-closing text and comment opener gives no <, > or &; JSON.parse returns the original; U+2028 and U+2029 escaped
  - Key order in the emitted object is @context, @type, name, description, brand, mpn, gtin, offers; the offers object has a fixed key order too
  - Builder returns null only for empty offers; an empty string brand or description is emitted as is (design says only null is omitted)

skill_calls:
  - none

risks:
  - The Write tool turned the U+2028 and U+2029 escapes in the two regex literals into raw characters, which broke the parse; fixed to escape text. A later tool that rewrites the file could repeat it, so check git diff.
  - offers[0] uses a non-null assertion after the length check; lint accepts it, but a future stricter rule would flag it.
