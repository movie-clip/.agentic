REPORT 2026-08-21-dynamic-sector-classification/08
status:      DONE
verdict:     NONE

changed:
  - docs/finance/financial-methodology.md — new "## Sector/Industry Classification — Source and Resolution (US-37.1)" section
  - financial-methodology.md new section covers: resolution order, opt-in wiring, identity gate rationale, full 11-entry taxonomy table, classification_source semantics, Unclassified bucket, caching TTL, explicit F-B (ETF look-through) exclusion
  - docs/contracts/exposure-fields.md — "Current-state concentration math" gains an Unclassified-bucket bullet + overview.py implementation pointer
  - docs/contracts/exposure-fields.md — top_sectors / top_sector_weight / sector_hhi rows' Notes columns updated to name the Unclassified bucket
  - docs/contracts/exposure-fields.md — new "Sector classification provenance (classification_source)" subsection stating it is backend-internal, not a contract row

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    docs-only change, no runnable verification named by the order

contract_notes:
  - none — this lane is the terminus for the pending docs notes from 02/05/06/07; nothing further downstream needs to change

pack_corrections:
  - none

handoff:
  - Both doc edits were checked against the actual shipped code (equity_sector_resolution.py, registry.py, overview.py, instruments.py), not retyped from the plan
  - Confirmed no drift between 05-technical-plan.md's design and what T-37.1.1/T-37.1.2 actually shipped — code matches plan exactly
  - Taxonomy table's 11 rows were copied verbatim from the live SECTOR_TAXONOMY_MAP dict in equity_sector_resolution.py, not retyped from the research brief
  - Not touched, per non_goals: epic-roadmap.md, current-product-state.md, and the story file still show US-37.1 as not-yet-closed-out — separate future dispatch

risks:
  - capabilities/docs.md § Auto-update vs flag-for-human says a brand-new methodology section is normally flag-for-human, not auto-written
  - This order's own definition_of_done explicitly directed writing the new methodology section directly with fully specified content — followed the order as the more specific instruction
  - Flagging per protocol: recommend a human review the new financial-methodology.md section content before treating it as final, per the pack's usual caution
  - 02-quant-research.md's contract_note (exposure-fields.md sector rows lack per-instrument provenance) is dismissed as landed, not a gap
  - Reason: classification_source now exists internally but is deliberately not exposed at the contract/UI level — documented explicitly in the new subsection
  - Aggregate-level truth-class labels (top_sectors/sector_hhi = current-state-truth) are correctly unchanged since the aggregate itself remains snapshot analytics
  - AC9's "distinct unclassified state" is satisfied purely on the backend per 05-technical-plan.md § Frontend confirmation (ExposurePanel.tsx already renders generically)
  - I did not re-verify ExposurePanel.tsx myself — out of this docs-only order's scope — inherited trust from the tech lead's full read, not independently re-checked here
