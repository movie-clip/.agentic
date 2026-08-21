REPORT 2026-08-21-sector-classification-followup/08
status:      DONE
verdict:     NONE

changed:
  - docs/product/stories/US-37.2-sector-classification-followups.md — Status flipped Backlog -> Done; all 5 ACs and all 4 tickets ticked (07-review.md confirmed every one SATISFIED); Last-updated already 2026-08-21, unchanged.
  - docs/product/stories/README.md — added US-37.2 row under the existing Epic 37 section; corrected "Single-story epic" note to "Two-story epic" now that US-37.2 exists.
  - docs/product/epic-roadmap.md — added US-37.2 to Epic 37's story snapshot table (Done); corrected "All 1 story Done" to "All 2 stories Done"; corrected "Single-story epic" note to "Two-story epic"; epic header left as "Completed Epic: Epic 37" (already correct, no change needed there).

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order's verification field is NONE (doc reconciliation, no runnable command).

contract_notes:
  - none — every contract_note from lanes 03/04/05/06/07 in this mini-run reported "- none"; confirmed no schema/type/contract-doc drift to absorb.

pack_corrections:
  - none

handoff:
  - Draft slice-log line for epic-roadmap.md needs human confirmation before it is written (capability pack Step 3: docs lane drafts, does not write) — full draft text in § Handoff detail: slice-log draft below.
  - Two CARRIED findings from run.md's Open table remain genuinely open after this story and are not this docs pass's to resolve — see § Handoff detail: carried findings below.

risks:
  - current-product-state.md left unchanged (no addendum) — judged not to change the user-visible claim of the existing US-37.1 entry; see § Risk detail: no current-state addendum below.
  - Backend test-count delta (840 -> 848, +8) in the drafted slice-log line is an arithmetic derivation from the diff, not a quoted figure from any lane report — see § Risk detail: test-count derivation below.

---

## Orchestrator brief

Close-out for US-37.2 completed: story flipped to Done with all ACs/tickets ticked (per 07-review confirmation), story index and epic-roadmap updated to reflect the second Epic 37 story. No contract or schema drift to absorb. Nothing here blocks dispatch — this is a completed close-out with two informational handoffs and two informational risk notes, detailed below.

Decisions taken:
- Ticked story Done and both index docs, matching 07-review's SATISFIED verdicts exactly — no re-judgment of ACs performed here.
- Drafted (not written) a slice-log line for epic-roadmap.md, pending human confirmation per capability pack Step 3.
- Left current-product-state.md unchanged — judged no user-visible claim changed.

Named sections below:
- **Handoff detail: slice-log draft** — the full draft slice-log line text awaiting human confirmation before it's committed to epic-roadmap.md.
- **Handoff detail: carried findings** — two pre-existing CARRIED findings from run.md's Open table that remain open and out of this story's scope.
- **Risk detail: no current-state addendum** — reasoning for why current-product-state.md was left unchanged.
- **Risk detail: test-count derivation** — how the 840->848 backend test-count delta in the draft slice-log line was derived (arithmetic from diff, not a quoted lane figure).

## Handoff detail: slice-log draft

Draft slice-log line for the human to confirm before it is written into epic-roadmap.md (per capability pack Step 3 — docs lane drafts, does not write, until confirmed):

`| 2026-08-21 | US-37.2 | Taxonomy lookup in resolve_equity_sector now normalizes case/whitespace before matching (strip+casefold on both sides; narrows only what counts as unmapped, never widens what counts as mapped). MarketDataService.get_company_profile's cached diagnostic now reflects true per-symbol cache hit/miss instead of hardcoded True (pre-checks the on-disk cache via the client's own build_key/get before fetch). Three hand-duplicated FMP-profile test fakes (_FakeMarketData x2, _SpyMarketData) consolidated into app/tests/fixtures.py's shared FakeMarketData. 840 -> 848 backend (+8: 5 casing/whitespace-variant params + 1 unmapped-sector regression + 2 cache hit/miss tests), 331 frontend unchanged; tsc + dead-code gate clean; dashboardGoldens.ts untouched. |`

## Handoff detail: carried findings

Two CARRIED findings from run.md's Open table remain genuinely open after this story and are not this docs pass's to resolve:

1. The same hardcoded `cached: True` shape exists in 4 other `MarketDataService` methods (`get_quote`, `get_historical_prices`, `get_etf_holdings`, `get_etf_holdings_for_date`) — explicitly out of scope per the story.
2. 04-backend's `should_fix` — the cache pre-check re-derives `fmp.py`'s internal cache-key formula from outside that file (scope excluded touching `fmp.py`); a clean fix belongs there.

Neither is a doc gap; both are candidate future tickets for a human to size.

## Risk detail: no current-state addendum

current-product-state.md left unchanged (no addendum added). Judged: taxonomy normalization is an internal robustness fix with no change to the disclosed "Unclassified" bucket behaviour already documented under US-37.1's entry (lines 65-77); the cache-flag fix corrects only an internal diagnostic (`last_fetch_meta[...]["cached"]`) not surfaced in any UI; fixture consolidation is test-only. None of the three tickets changes the user-visible claim the existing US-37.1 entry makes, so no new bullet was warranted per the order's own framing.

## Risk detail: test-count derivation

Backend test-count delta (840 -> 848, +8) in the drafted slice-log line was computed by counting new `def test_*` functions plus parametrize cases in the diff (5 casing/whitespace params + 1 unmapped-sector test in test_equity_sector_resolution.py; 2 cache-hit/miss tests in test_market_data.py) against the prior slice-log baseline of 840 — no lane report stated the new grand total explicitly (06-test's full-suite run confirmed green but did not print the backend count), so this is an arithmetic derivation, not a quoted figure; worth a spot-check if precision matters downstream.
