REPORT 2026-08-21-epic38-followups-and-etf/15
status:      DONE
verdict:     NONE

changed:
  - docs/product/prd/epic-38-sector-classification-follow-through.md — new PRD, mirrors Epic 37's structure (Status/Created/Closed/Seeded-by, Problem, Goal, Non-goals, Story snapshot, Slice log)
  - docs/product/epic-roadmap.md — top summary now names Epic 38 as most recently shipped; new "Completed Epic: Epic 38" section inserted before Epic 37's
  - docs/product/current-product-state.md — Exposure-tab sector-classification entry now covers ETF look-through (US-38.1), replacing the "does not cover" line
  - docs/product/stories/README.md — new Epic 38 index section (US-38.1/US-38.2 rows, Done) inserted before Epic 37's section
  - docs/product/stories/US-38.1-etf-lookthrough-sector-classification.md — Status Backlog to Done; all 9 ACs and 4 tickets ticked (reviewer confirmed all SATISFIED)
  - docs/product/stories/US-38.2-market-data-cache-diagnostic-accuracy.md — Status Backlog to Done; all 8 ACs and 3 tickets ticked (reviewer confirmed all SATISFIED)
  - docs/contracts/exposure-fields.md — "Sector labels" row (~line 207) source citation corrected: no frontend consumer exists for lookthrough_sector_exposure, per reviewer's grep-verified finding

verification:
  command:   NONE (no Bash tool granted to this lane)
  result:    NOT_RUN
  detail:    docs-only reconciliation pass; orchestrator/human should run `grep -rn "topLookthroughSectors" apps/desktop/src` (expect zero hits) to confirm the exposure-fields.md fix and re-run the mechanical report checker on this artifact

contract_notes:
  - none — this order absorbed every open contract note from the run (exposure-fields.md/tech-debt-register.md prose were already applied by the prior 10-docs dispatch; this order's own scope was the epic close-out layer)

pack_corrections:
  - none

handoff:
  - tech-debt-register.md: judged no new row needed for findings 1/2 (5-method cache-flag bug, fmp.py cache-key duplication) — both existed only as narrative mentions in US-37.2, never had a register row, and are now fully fixed in this same run by T-38.2.1/T-38.2.2, so there is no lingering gap to catalogue; see risks
  - epic-roadmap.md's "Open items" list (lines 12-50) already contained no F-B / "cached: True" bullets to remove — checked in full, nothing needed there

risks:
  - my own judgment call, per the order's explicit discretion, not to add a tech-debt-register row for findings 1/2 since both are closed within this same run with no open remainder — flagging in case the human wants a historical-traceability row anyway
  - current-product-state.md's US-37.2/get_company_profile cache-diagnostic fix has no precedent entry in that doc at all (grepped, zero hits) — read as this doc not tracking internal/diagnostic-only detail at that granularity, so I did not add a US-38.2 entry either; flagging the absence of precedent rather than guessing
