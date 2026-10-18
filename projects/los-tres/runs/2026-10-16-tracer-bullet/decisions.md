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

## D-3 · design · 2026-10-16
open decision:  O-1 package manager, O-2 Node major, O-3 test database, O-4 styling system
raised by:      02-design.md § Owner questions (O-1..O-4)
ruling:         "O-1 npm. O-2 Node 22. O-3 no new service: a second database <DB_NAME>_test on the existing db service. O-4 plain globals.css with CSS variables for slice A; I'll choose a styling system before slice B."
by:             the human, in session
meaning:        all four match the design's recommendation, so the plan stands unchanged; O-4 is the owner's call before slice B and no lane picks a styling system. The human's go on the build plan is still owed.

## D-4 · build · 2026-10-16
open decision:  go on the build plan (lanes 03 backend, 04 frontend, 05 test, 06 docs; then integration and close docs; budget 8), and creating the run's public issue at Backlog
raised by:      run.md § Phases (build human stop); orchestrator build plan presented in session
ruling:         "approve, you can proceed"
by:             the human, in session
meaning:        build fires; orchestrator creates the issue, branch and draft PR per the Tracker block, then dispatches 03 backend
