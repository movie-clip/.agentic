CHANGE REQUEST CR-2 — 2026-09-12-rolling-factor-f1-f7
raised by:  05-quant-audit.md § Findings, FINDING 3 (MATERIAL) — and coverage owed for CR-1's fix to FINDING 1
round:      1 of 2
scope fence: apps/desktop/src/features/portfolio/RollingFactorLoadingsCard.test.tsx only

Two things, both read from their sources before editing:

1. Read `05-quant-audit.md` § Findings, the `FINDING 3` block, in full. `RollingFactorLoadingsCard.test.tsx:57-61` asserts a `windows[].status == "partial"` fixture case that the real engine can never produce (proven in that block). Relabel or restructure that test so it is honest about testing a defensive branch, not a reachable engine state — do not delete the branch it's testing, only correct what the test claims about it.
2. Read `06-frontend.md` § handoff (the CR-1 fix report) for what the new model-level `'partial'` branch and its tooltip logic (`modelPartialTooltip`) need covered: the missing-factors-named case and the generic-fallback case. Add render-level test cases for both, reusing the existing adapter-chain fixture pattern already used in this file (do not hand-build a parallel response literal).
