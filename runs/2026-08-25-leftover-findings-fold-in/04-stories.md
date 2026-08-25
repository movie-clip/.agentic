REPORT 2026-08-25-leftover-findings-fold-in/04
status:      DONE
verdict:     NONE

changed:
  - docs/product/stories/US-40.1-snapshot-trust-signal-completeness.md — new story, drafted
  - docs/product/stories/US-40.2-add-snapshot-preserves-imported-history.md — new story, drafted

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only drafting order; no verification command applies. Both stories are drafts for human review, not approved.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - US-40.1 (Backlog): freeze-date picker label (a) + retire run_metadata.source_status/.confidence as a trust source (b), 4 tickets (T-40.1.1..4), 6 ACs — docs/product/stories/US-40.1-snapshot-trust-signal-completeness.md
  - US-40.2 (Backlog): add_snapshot preserves imported history, 3 tickets (T-40.2.1..3), 4 ACs, first ticket is explicitly tech-lead DESIGN — docs/product/stories/US-40.2-add-snapshot-preserves-imported-history.md
  - No blocking open decisions remain — the order's definition_of_done already carries the human's resolutions (epic title, 2-story split, both extra leftovers folded in, item 4 and the pre-existing backlog excluded)
  - One non-blocking design-pass note left in US-40.1: whether to ticket the quant research's _build_exposure_source_status/_build_exposure_availability duplication finding as a simplification, or leave it as a noted opportunity, is tech-lead DESIGN's call
  - Both extra leftovers (RecordingMarketData gap, dead market_data param) were folded into US-40.1 as a non-AC-traced Housekeeping ticket (T-40.1.3) — reasoning given in that story's § Notes / decisions
  - Item 4 (risk.py:612/1483 market_data kwarg) is named in both stories' Out of scope, recommending a docs/tech-debt-register.md entry for docs-engineer at close-out, per the delivery brief's own recommendation

risks:
  - I resolved the "which story gets the two extra leftovers" judgment call by putting both under US-40.1 rather than splitting one to each — US-40.2 is frontend-only with no adjacency to either backend/test-infra item, so a forced split seemed worse than a stated single placement; flagging in case the human disagrees
  - US-40.1's AC1/AC2 (freeze-date picker label) deliberately do not name which underlying date field to surface (client-persisted PortfolioSnapshot.importedMeta.importedAt vs. the engine's ExposureRunReproducibilityMetadata) — the delivery brief pointed at the engine field specifically, but the picker enumerates all workspace nodes client-side and the engine field is only populated for the currently-active exposure result, so the exact data source is a design question I left to tech-lead DESIGN rather than assuming the brief's pointer resolves cleanly
  - I independently re-read exposure_engine.py, variantLabels.ts, App.tsx (both override call sites and both import-mode branches), portfolioWorkspaceStorage.ts, workspaceTypes.ts, docs/contracts/exposure-fields.md, frozen_market_data.py, and risk.py's dead-param site — all line citations in both stories were confirmed against current code, not relayed from the prior artifacts unchecked
  - US-40.2's test plan assumes App.tsx's add_snapshot branch is exercised somewhere in the existing frontend suite today (naming App.test.tsx as a likely location) — I did not open the current test file to confirm exact existing coverage, since the story's test plan intentionally leaves exact file/location to the test lane

## Orchestrator brief
- Epic 40 "Snapshot Trust & Fidelity Follow-Through" — 2 stories drafted, both Status: Backlog, per the human-resolved definition_of_done (no open decisions block ticketing)
- US-40.1 bundles items 1+2 (UI freeze-date label + retiring run_metadata.source_status/.confidence as a trust source, per quant research's fix direction (b): doc note + regression test, no schema change) plus both extra leftovers as a non-AC Housekeeping ticket
- US-40.2 covers item 3 alone (add_snapshot data-loss); its first ticket (T-40.2.1) is explicitly a tech-lead DESIGN ticket for the client-side recombination logic — not pre-specified here
- Item 4 (risk.py market_data kwarg) is NOT ticketed in either story — named in both § Out of scope, recommended for tech-debt-register.md at docs-engineer close-out
- Both stories are drafts for human review — neither is approved, ticketed-for-dispatch, or Next phase
- Sections below: none — this report has no sections beyond the block; the two story files carry the substance
