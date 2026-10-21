REPORT 2026-10-21-s6-1-product-jsonld/06
status:      DONE
verdict:     NONE

changed:
  - capabilities/backend.md § Layout — added product-jsonld.ts (pure builder and serializer, no server-only) to the catalogue/ list
  - capabilities/frontend.md § Layout — the "component never imports src/server" rule now states its one exception (JsonLd.tsx, product-jsonld.ts, D-2) in the same sentence, with precedence
  - capabilities/testing.md § Running tests — added the product JSON-LD e2e method and selector
  - capabilities/testing.md § Shared scaffolding and gotchas — added the integration test for hidden and unapproved offers
  - capabilities/testing.md § Shared scaffolding and gotchas — added the \b, regex-literal and   escape gotcha (String.raw, cat -A)

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order verification was NONE

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

skill_calls:
  - none

risks:
  - No docs/** file was made false by S6.1; docs/product/mvp.md lines 69 and 83-84 already describe the JSON-LD as scoped, so nothing was edited under docs/.
  - The testing.md \b gotcha now appears in two bullets (the existing Python non-raw string one and the new extension); kept separate because the new one adds different traps, but a later pass may merge them.
  - Premises verified: src/server/catalogue/product-jsonld.ts and both test files exist in the working tree.
