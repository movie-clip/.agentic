REPORT 2026-09-11-risk-summary-audit-foldable/16
status:      DONE
verdict:     NONE

changed:
  - docs/finance/financial-methodology.md:1054-1065 — N=1 Dashboard volatility now documented as returning `null` (not `0.00%`), matching `portfolio_beta`/`portfolio_correlation`/`r_squared`'s `None`-at-N<2 convention (Fix 4 as shipped, 09-backend.md).
  - docs/finance/financial-methodology.md:1141-1149 — "Contract rule" for `information_ratio`/`active_return_pct` no longer names `investor_economics_status` as the authoritative explanation for nulls; states nulls are purely math-layer (fewer-than-2-paired-returns, tracking_error=0), matching Fix 2 as shipped.
  - docs/contracts/dashboard-fields.md:237 — Portfolio/Benchmark Volatility row: "(0.00% at N=1)" corrected to "(null at N=1 ... fixed from a prior 0.00%-at-N=1 bug)".
  - docs/contracts/dashboard-fields.md:238 — Current/Max Drawdown row: added confirmation that diagnostics drawdown publishes whenever `historical_sections_available` is True with no remaining categorical `withheld` gate, cross-referencing `risk-fields.md:548`'s "no withheld rung" policy (verified that citation still reads as described).
  - docs/contracts/dashboard-fields.md:241 — Risk contribution basis label row: Notes cell updated with the exact shipped copy from RiskSummaryCard.tsx:95, "Risk contribution basis (adjusted-close price provenance only): {trust}" (verified against 10-frontend.md and the current file).
  - docs/contracts/diagnostics-fields.md:212-215 — drawdown_summary "Refusal rule" rewritten: nulls are now math-layer only, no categorical withheld gate; `investor_economics_status` resolves `available` under the same `historical_sections_available=True` condition (US-45.1 fix, confirmed by 14-quant-audit.md).
  - docs/contracts/diagnostics-fields.md:239-241 — "Benchmark-relative refusal rule" rewritten: removed the claim that `investor_economics_status` is the authoritative explanation for `active_return_pct`/`information_ratio` nulls; states these are gated only by their own documented math-layer edge cases post-Fix-2.
  - docs/product/stories/US-45.1-dashboard-risk-summary-foldable.md:3 — `Status: Backlog` → `Status: Done` (all 8 ACs SATISFIED per 15-review.md, both integration gates PASS, quant-audit PASS).
  - projects/portfolio/capabilities/product.md — "Where the plan lives" section (table + "Navigating the roadmap" subsection) rewritten: removed references to `epic-roadmap.md`/`prd/**`/`stories/README.md`, which do not exist (deleted at `ce9c97d`, confirmed via `docs/product/` directory listing — only `current-product-state.md` and `stories/` remain); replaced with the bare `US-<n>.<m>` no-epic convention and a precedent-finding method that does not depend on a deleted roadmap.
  - projects/portfolio/project.md — "Sources of truth" table row for "Which epic is current?" rewritten: removed the false "epic-roadmap.md is the authority" claim, states the corpus was deleted at `ce9c97d` and stories use bare numbering.

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Order's verification field was NONE (docs-only lane, no Bash tool). Every edit was checked against the current on-disk source: RiskSummaryCard.tsx:95, trust_gate.py/diagnostics_engine.py gate signatures as reported in 09-backend.md, 14-quant-audit.md's independent recomputation, 15-review.md's AC table, risk-fields.md:548, and a live `docs/product/` directory listing.

contract_notes:
  - none

pack_corrections:
  - projects/portfolio/capabilities/docs.md — "Where things live" table, "Step 3 — The slice log", and "You own the roadmap and the index" sections still describe `docs/product/epic-roadmap.md` and `docs/product/stories/README.md` as live, maintained files, but both were deleted at `ce9c97d` and are staying deleted (same root cause as the two entries already in pack-corrections.md, not itself a named entry there). Replacement: strike the `epic-roadmap.md`/`stories/README.md` rows from "Where things live"; replace "Step 3 — The slice log" and the roadmap-ownership section with guidance that this project currently has no roadmap/index to maintain, following the `product.md` precedent this order just applied. Not applied here — the order named only `product.md` and `project.md`'s Sources-of-truth section, and this pack is my own operating pack, not a file this order scoped me to edit; flagging per protocol §1 rather than silently expanding scope.
  - projects/portfolio/project.md — "Layout" code block (lines 89,91) still lists `product/prd/` and `product/epic-roadmap.md` as if they exist, directly beside the "Sources of truth" table I just corrected in the same file. Replacement: delete those two lines from the fenced layout block, consistent with the Sources-of-truth fix already applied. Not applied here — the order named only the "Sources of truth" section of this file, and this is a second, distinct location in the same document; flagging rather than expanding scope unilaterally.

handoff:
  - none

risks:
  - dashboard-fields.md:242 (IR/Active Return row) and :287 (Accuracy Rule 6) were read and found already accurate post-Fix-2/Fix-1 with no "withheld-by-default" language present to remove — the order's framing assumed stale wording at those exact lines that the doc did not actually carry (the doc had been written to the intended-correct design before the code caught up); no edit made at those two spots, confirmed rather than rewritten, per the technical plan's own instruction to "confirm... unless review finds drift."
  - I extended the "Where the plan lives" correction in `product.md` beyond just the table — the "Navigating the roadmap without reading 1,700 lines" subsection was entirely instructions for grepping a file that no longer exists, so leaving it verbatim next to a corrected table would have produced an internally contradictory pack; rewrote it to a no-roadmap precedent-finding method instead of only touching the table row. This is a larger edit than "apply the replacement wording as given" strictly permits, since pack-corrections.md gave no verbatim replacement text for this entry, only the false premise — flagging the judgment call here.
  - Two further stale references to the same deleted planning corpus were found outside this order's named scope (capabilities/docs.md, project.md's Layout block) — recorded above as new `pack_corrections` rather than edited, since the order named only `product.md` and `project.md`'s Sources-of-truth section as the correction targets.

## Orchestrator brief
Applied all 5 required corrections plus both run.md Open pack_correction rows. Every OPEN row in run.md's Open table naming a docs file is now corrected: dashboard-fields.md (N=1 null, drawdown cross-ref, Fix-3 label copy), financial-methodology.md (N=1 null, IR/active-return contract rule), diagnostics-fields.md (both refusal rules), story status Done, product.md + project.md pack corrections. The MINOR HHI-duplication finding and the route-test pinned-float handoff were left untouched as instructed. Two new pack-staleness findings (capabilities/docs.md, project.md Layout block) surfaced during verification but were not in this order's named scope — reported as new `pack_corrections` bullets above for the orchestrator to append and route in a future close-out, not applied.
