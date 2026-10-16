# Decisions — 2026-10-16-tracer-bullet

## D-1 · framing · 2026-10-16
open decision:  Q1–Q7, the owner's open calls
raised by:      01-product.md § Open decisions (Q1–Q7), with the orchestrator's recommendation per question relayed in session
ruling:         "all recommended"
by:             the human, in session
meaning:        Q1 seed marks only the demo feed approved (backend.md § Guardrails (1)); Q2 seeding behind a config flag, on locally, off on the VPS; Q3 fictional shop names and clearly demo product titles; Q4 no outbound link on offer rows until /go exists; Q5 matching cut accepted (EAN attach + new product; EAN/brand conflict rejected into the import report); Q6 no ticketed story, 01-product.md is the specification; Q7 Umami runs, tracker not embedded

## D-2 · framing · 2026-10-16
open decision:  split the tracer bullet into more than one slice?
raised by:      01-product.md § Stories (invest: "Small is also weak … proposed split is skeleton + Compose + gate on an empty page, then import + product page")
ruling:         "it is good idea to split into multiple slices"
by:             the human, in session
meaning:        this run builds slice A only (skeleton + Compose + gate, ending on a page that renders); import + product page is the next run. The design lane draws the exact cut line.
