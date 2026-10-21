# Decisions — 2026-10-21-s6-1-product-jsonld

## D-1 · build · 2026-10-21
open decision:  go on the build plan; lane split amended by the orchestrator: src/server/money.ts and src/server/catalogue/product-jsonld.ts move from frontend to a backend lane (project.md § Lane routing: backend owns server code)
raised by:      01-design.md § Lanes
ruling:         "approve" (to the 3-step version: backend, frontend, test)
by:             the human, in session
unblocks:       build; branch creation

## D-2 · build · 2026-10-21
open decision:  JsonLd.tsx imports serializeJsonLd from src/server (pure module) against frontend.md § Layout "a component never imports src/server" — A: keep and add a pack exception; B: page serialises, component imports nothing from src/server
raised by:      03-frontend.md § risks
ruling:         "A"
by:             the human, in session
unblocks:       test lane; the 03-frontend pack correction is applied at close-out
