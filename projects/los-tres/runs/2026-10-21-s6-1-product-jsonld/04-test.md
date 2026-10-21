REPORT 2026-10-21-s6-1-product-jsonld/04
status:      DONE
verdict:     NONE

changed:
  - C:\projects\investments\los-tres\tests\unit\money.test.ts — centsToDecimalString examples, RangeError cases, parser round-trip
  - C:\projects\investments\los-tres\tests\unit\product-jsonld.test.ts — new: builder (full object, absent keys, gtin length rule, min/max, offerCount, null) and serializer (escapes, round-trip)
  - C:\projects\investments\los-tres\tests\integration\product-jsonld.test.ts — new: hidden and unapproved-feed offers do not move low, high or offerCount (guardrail 1)
  - C:\projects\investments\los-tres\tests\e2e\product.spec.ts — three JSON-LD tests: shared-EAN page, single-shop page, 404 page

verification:
  command:   cd C:\projects\investments\los-tres && npm run gate
  result:    PASS
  detail:    gate exit 0; vitest 46 files, 770 tests passed; playwright 70 passed

contract_notes:
  - none

pack_corrections:
  - capabilities/testing.md — Running tests: add "Product JSON-LD e2e reads the raw request.get HTML with a regex over script tags (one match) and JSON.parse, then openRawHtml for selector and visible-price comparison; selector script[type=application/ld+json][data-testid=product-jsonld]"
  - capabilities/testing.md — Shared scaffolding: add "tests/integration/product-jsonld.test.ts feeds getPublicProductBySlug into buildProductJsonLd to prove hidden and unapproved offers cannot reach the JSON-LD"
  - capabilities/testing.md — Gotchas: the \b backspace trap also hits a Python heredoc and regex literals in e2e specs, and "\u2028"-style escapes typed in a test string literal may arrive as the raw character; use String.raw for expected escape text and check with cat -A

handoff:
  - No shared fixture or helper added; the e2e uses DEMO_SHARED, DEMO_DRILL and DEMO_SHOP_HOSTS from tests/fixtures/demo.ts
  - Page-level omit (no script with no offer) is not reachable today because the page 404s; the builder unit test covers null, S8.4 T8.4.3 adds the page case
  - Hidden/unapproved check lives in the integration project because e2e fixtures cannot hide an offer (e2e writes only via import-feeds)

skill_calls:
  - none

risks:
  - A regex with \b written through a tool became a backspace character (the pack warned); caught by the first e2e run failing with zero matches, fixed.
  - The e2e script regex requires a space before type=, so a change of attribute order in React output would still match but a change to single quotes would not.
  - No product defect found; the frontend/pack-conflict about components importing src/server is the frontend lane's PARTIAL and is untouched here.
