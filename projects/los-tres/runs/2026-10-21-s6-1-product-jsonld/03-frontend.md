REPORT 2026-10-21-s6-1-product-jsonld/03
status:      PARTIAL
verdict:     NONE

changed:
  - C:\projects\investments\los-tres\src\components\JsonLd.tsx — new server component: script type application/ld+json, data-testid product-jsonld, body is serializeJsonLd(data) only
  - C:\projects\investments\los-tres\src\app\(public)\producto\[slug]\page.tsx — builds JSON-LD once, renders JsonLd before main only when non-null; main subtree reindented under a fragment

verification:
  command:   cd C:\projects\investments\los-tres && npm run lint && npm run typecheck && npm run test:unit
  result:    PASS
  detail:    lint clean; tsc and tsc -p tsconfig.cli.json clean; vitest unit 23 files, 476 tests passed

contract_notes:
  - none

pack_corrections:
  - capabilities/frontend.md — Layout says a component never imports src/server; add the exception: JsonLd.tsx imports serializeJsonLd and type ProductJsonLd from src/server/catalogue/product-jsonld.ts (pure module, no server-only)

handoff:
  - e2e selector: script[type="application/ld+json"][data-testid="product-jsonld"] in the raw request.get HTML; the script sits before main, outside it
  - Metadata, copy, CSS and visible markup are unchanged; the main a count is unchanged because the script is outside main
  - The null branch (no script) is unreachable on the page today because the read 404s with no visible offer; cover it in the builder unit test
  - Component props: JsonLd({ data: ProductJsonLd }); it calls serializeJsonLd itself, so a test of escaping goes through the serializer, not the component

skill_calls:
  - none

risks:
  - Pack conflict: frontend.md Layout says a component never imports src/server; 01-design § Script-tag safety has JsonLd import serializeJsonLd from it. Built to the design; status PARTIAL for the human to rule
  - Alternative that satisfies both: JsonLd takes a finished json string and the page calls serializeJsonLd; not built because it deviates from the design
  - dangerouslySetInnerHTML is the first use in src; an S8.6 lint rule banning it must allow-list src/components/JsonLd.tsx
