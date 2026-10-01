# Decisions — 2026-09-15-fix-systemic-stress-dashboard

## D-1 · specification · 2026-10-01
open decision:  FINDING 3's composite LEVEL jump (80.0 -> 66.0 at bar 272) — display the
                basis, or withhold the composite until every non-zero-weight component is
                available?
raised by:      01-quant.md § FINDING 3
ruling:         "display the basis" — keep exclude-and-renormalise exactly as it is, add a
                Basis table row naming the components in the composite, and take
                `table.new(..., 2, 6, ...)` at :113-115 to `2, 7`.
by:             the orchestrator, adopting 01-quant.md § FINDING 3's stated recommendation.
                The human has not ruled. Recorded this way so the run can resume instead of
                stalling a third week; it is reversible until `backend` ships, and the
                reasoning is the quant's, not a paraphrase: withholding would blank the panel
                for the first 272 bars of every chart and permanently for any user without
                COR1M, reversing the deliberate design choice the header at :20-24 states, in
                order to fix a 20-bar warm-up artefact.
