REPORT 2026-08-25-leftover-findings-fold-in/12
status:      PARTIAL
verdict:     NONE

changed:
  - docs/product/epic-roadmap.md — added "Completed Epic: Epic 40" section (2 stories); updated top "Most recently shipped" line + "Epics 13 and 18-40" range; light-touch update to the "No epic is active" lead sentence
  - docs/product/current-product-state.md — Import workflow gains picker date-label + add_snapshot history-preservation bullets; Trust semantics gains the run_metadata.source_status/.confidence retirement note
  - docs/product/stories/US-40.1-snapshot-trust-signal-completeness.md — Status -> Done, all 6 ACs + 4 tickets ticked, PRD line corrected, filing note updated, Outcome note added
  - docs/product/stories/US-40.2-add-snapshot-preserves-imported-history.md — Status -> Done, all 4 ACs + 3 tickets ticked, PRD line corrected, filing note updated, Outcome note added
  - docs/product/stories/README.md — new Epic 40 index entry (2 stories) above Epic 39
  - docs/contracts/dashboard-fields.md — new "Combine Imported Snapshots (US-40.2)" section documenting POST /portfolios/import/combine-snapshots
  - docs/tech-debt-register.md — 3 new rows: dead risk.py market_data param, exposure_engine.py source_status/availability duplication, missing golden PDF fixtures no-op'ing test_importer.py
  - docs/finance/financial-methodology.md — appended Finding 3's one-sentence null-TWR-input clarification to "Multi-Statement Snapshot Merge"
  - services/quant-engine/app/tests/fixtures.py — module docstring gains the statement_totals cash_total/stock_total gotcha (08-test.md's finding)

verification:
  command:   grep -n "Epic 40" docs/product/epic-roadmap.md docs/product/current-product-state.md ; grep -rn "combine-snapshots" docs/contracts/*.md
  result:    PASS
  detail:    "Epic 40" — 3 hits in epic-roadmap.md, 3 hits in current-product-state.md. "combine-snapshots" — present in docs/contracts/dashboard-fields.md (route header + request/response table + prose). Run via the Grep tool (no Bash tool granted to this lane, per protocol §7).

contract_notes:
  - none — every contract_note raised across this run (05-technical-plan, T-40.1.3+T-40.2.2a-backend, T-40.2.2b-frontend) is now landed: exposure-fields.md sentence (already landed by T-40.1.1), dashboard-fields.md's new combine-snapshots entry (this close-out)

pack_corrections:
  - none

handoff:
  - No epic PRD file was created for Epic 40 — this close-out's scope excluded docs/product/prd/, so the retrospective-PRD convention (Epic 37/38/39 each have one) was not followed here; a human/producer call on whether to backfill one.
  - 11-integration.md's run.md ledger-bookkeeping asks (mark 3 Open-table rows ABSORBED, close the Rounds table) are outside this lane's scope (run.md is orchestrator-owned) — still open for the orchestrator to action.
  - 11-integration.md's "Unrelated uncommitted diff" (App.tsx hunk, BenchmarkPositioningCard, import_bootstrap/engine/composer.py etc., predating this run) was left untouched per this order's non_goals — still sitting uncommitted, belongs to a different closed epic.
  - This run had no dedicated acceptance-review lane (no reviewer artifact exists in run.md's Artifacts table) — AC boxes were ticked from tech-lead INTEGRATION's DoD cross-check + quant-audit's independent PASS instead, see risks.

risks:
  - docs.md capability pack says any new methodology-doc edit is flag-for-human, not auto-write; this order's DoD item 6 specified the exact sentence to append (10-quant-reaudit.md Finding 3's own `expected:` wording) — followed the order per protocol core §3's rule, flagging the conflict here, status set to PARTIAL accordingly (mirrors 09-docs.md's own precedent in this same run).
  - No acceptance-review (reviewer) lane ran in this fold-in run; I ticked both stories' ACs/tickets based on tech-lead INTEGRATION's DoD cross-check (11-integration.md, direct file:line verification against 05-technical-plan.md) plus quant-audit's independent PASS, the strongest gate evidence this run's artifact set has — not a reviewer's independent AC-by-AC trace as Epic 39's story cites.
  - Skipped creating a retrospective Epic 40 PRD file — this project's usual close-out convention (per capabilities/docs.md and Epic 37/38/39 precedent) auto-creates one for every newly-closed epic, but this order's scope explicitly excluded docs/product/prd/; flagged rather than silently either creating it (scope violation) or omitting the flag.
  - epic-roadmap.md's "No epic is active" narrative paragraph (about Epic 36/35) had gone untouched across 3 prior epic close-outs (37, 38, 39) before this one — I made a minimal lead-sentence edit rather than a full rewrite, matching that observed precedent; noting it here since it suggests the paragraph itself may be a stale convention worth a human decision, not something I resolved unilaterally.
  - current-product-state.md's top "Updated: 2026-08-19" banner has also gone untouched across 5 epics (35-39) — left it as-is to match that same precedent rather than fix it unprompted (out of this order's named DoD items).

## Orchestrator brief
- Epic 40 close-out complete: roadmap section, current-product-state, both story files (Done, all ACs/tickets ticked), story index, new contract-doc entry for the combine-snapshots route, 3 tech-debt-register rows, 1 methodology sentence, 1 fixtures docstring line — all 9 DoD items landed.
- Two flagged, non-blocking conflicts: (1) the methodology-doc edit followed the order over the pack's flag-for-human convention (status PARTIAL, see risks); (2) no reviewer lane existed in this run, so AC ticking rests on tech-lead INTEGRATION's cross-check + quant-audit PASS rather than an acceptance-reviewer trace.
- Out-of-scope items surfaced but not actioned here (by design): the Epic 40 PRD file, run.md ledger bookkeeping, and the pre-existing unrelated uncommitted diff — all named in handoff for the orchestrator/human.
- Every upstream contract_note from this run is now absorbed; none remain open.
