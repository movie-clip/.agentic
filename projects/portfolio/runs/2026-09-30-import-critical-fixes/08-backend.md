REPORT 2026-09-30-import-critical-fixes/08
status:      DONE
verdict:     NONE

changed:
  - services/quant-engine/app/schemas/imports.py — ImportedPosition.cost_basis and unrealized_pnl become float | None = None (C1); no per-position trust field
  - services/quant-engine/app/schemas/reconciliation.py — PortfolioOverview totals nullable, top_positions values may be None, new cost_basis_trust Literal stated|unavailable, after-validator rejects stated with a null total (C2)
  - services/quant-engine/app/schemas/reconciliation.py — EnrichedPosition removed (no caller)
  - services/quant-engine/app/analytics/overview.py — totals are None when any position value is None, cost_basis_trust derived from that, top_positions unrealized_pnl None per position
  - services/quant-engine/app/analytics/performance.py — build_enriched_positions removed, plus the now-orphaned _coerce_float helper and EnrichedPosition import
  - services/quant-engine/app/analytics/portfolio_imports.py — build_enriched_positions import and __all__ entry removed
  - services/quant-engine/app/services/statement_importer.py — _merge_terminal_positions sums cost_basis and unrealized_pnl only when both are non-null, else None
  - services/quant-engine/app/domain/ledger.py — opening-lot unit cost is estimated only when the ending position has a non-null cost_basis
  - services/quant-engine/app/services/portfolio_snapshot_builder.py — request-path positions get cost_basis=None and unrealized_pnl=None instead of market_value and 0
  - services/quant-engine/app/importers/freedom24.py — positions only: cost_basis=None, unrealized_pnl=None, trade_delta cost branch deleted; beginning-balance cell still parsed as a layout guard
  - services/quant-engine/app/services/exposure_engine.py — type annotation only: _coerce_concentration_item item widened to dict[str, float | str | None] to match top_positions; outside the fence, forced by the new schema type
  - C:\projects\investments\.agentic\projects\portfolio\runs\2026-09-30-import-critical-fixes\scratch\be3_probe.py — scratch probe for the DoD numbers and the independence checks

verification:
  command:   cd services/quant-engine && SKIP_GOLDEN_FRESHNESS_CHECK=1 python -m pytest app/tests -k "overview or importer or ledger or snapshot_builder"; python scripts/detect_deadcode.py --strict; python scratch/be3_probe.py
  result:    PASS
  detail:    108 passed, 3 failed, 910 deselected; all 3 failures are the Freedom24 reds already owned by BE-2 (none from BE-3). Dead-code strict clean. Probe: IB 62255.14/3491.53 stated; FF None/None unavailable; IB+FF None/None unavailable. see § Verification detail

contract_notes:
  - types.ts PortfolioOverview (~:56-61) lags: total_cost_basis?: number | null, total_unrealized_pnl: number | null, top_positions element unrealized_pnl: number | null, add cost_basis_trust?: 'stated' | 'unavailable' (optional, persisted overrides pre-date it)
  - types.ts ImportedPosition (:37-39) already declares cost_basis and unrealized_pnl nullable; no change, but the Python default is now None so responses can omit-or-null them
  - types.ts / any TS fixture typing top_positions unrealized_pnl as number lags (dashboardGoldens.ts overview blocks regenerate in H-1; IB gains additive cost_basis_trust: stated)
  - docs/contracts/imports-fields.md is still to be CREATED (C1 nullable fields = unavailable, C2 overview fields and validator, C5 merge sum rule); T-46.4.5
  - docs/finance/financial-methodology.md lags: E4 new section Cost Basis and Unrealized P&L after Truth Classes; also the Multi-Statement Snapshot Merge null-propagation list should name cost_basis and unrealized_pnl
  - importedExposureOverride persisted by earlier builds still holds 3018.96 / 0.00 (FF) and 62843.22 / 0.00 (request path); its cost_basis_trust defaults to stated on read; FE-2 and BE-4 re-derive per D-5
  - docs/contracts/exposure-fields.md or wherever overview fields are tabulated (check for total_cost_basis) lags on nullability and cost_basis_trust

pack_corrections:
  - none

handoff:
  - Expected red (BE-2 owned, present before BE-3): test_importer.py::test_import_freedom24_statement_returns_expected_snapshot, test_importer.py::test_freedom24_parsers_skip_malformed_records_without_raising, test_analytics.py::test_ff2026_dashboard_truth_values_match_imported_history_and_overview
  - Expected red outside the requested -k filter, full app/tests run: 6 failed 1015 passed; extra reds are test_golden_pipeline_determinism (test_render_is_deterministic, test_generated_matches_committed_goldens) awaiting H-1 and test_build_roadmap.py::test_repo_roadmap_is_current from the untracked stories
  - Tests left red by BE-3 itself: none. test_build_portfolio_overview_returns_expected_totals still passes (stated values)
  - Test lane: FF2026 VTI cost_basis and unrealized_pnl None; FF overview totals None with cost_basis_trust unavailable; top_positions VTI unrealized_pnl None; IB 62255.14 / 3491.53 stated; IB+FF None/None unavailable
  - Test lane: PortfolioOverview validator rejects stated with a null total (and accepts unavailable with null totals); no positions gives 0.0 and stated; model omits cost_basis_trust defaults to stated
  - Test lane: merge sums only when both non-null (stated+stated sums, stated+null gives None, either field independently); IB(A)+IB(B) VUAA doubles to 20162.93 / 3846.67 in my probe
  - Test lane: reconstruct_position_lots(FF2026) opening VTI lot 3.0 has unit_cost None, remaining_cost_basis None, cost_basis_is_estimated False; trade lot 6.0 @ 322.426 unchanged
  - Test lane: request-path builder yields cost_basis None and unrealized_pnl None for every position; overview over it is None/None unavailable (IB request path was 62843.22 / 0.00). A grep-style guard on portfolio_snapshot_builder.py and freedom24.py for market_value-as-cost is viable; see § Verification detail for my pattern
  - Test lane: Dashboard independence, use FrozenMarketData.from_file() for IB (the conftest mock returns an empty dashboard and proves nothing): run_imported_dashboard_history JSON is byte-identical with stated, null, and fabricated cost basis (445005 chars, 161 daily states)
  - Test lane: FF2026 dashboard independence could not be checked here because frozen data lacks the FF window until H-1; needs the same three-way check after recapture
  - Scratch probe: runs/2026-09-30-import-critical-fixes/scratch/be3_probe.py (untracked under .agentic; leave or delete by hand). Two throwaway helper scripts sit in my session scratchpad only
  - BE-4 note: legacy Freedom24 nodes hold 3018.96 / 0.00 inside the stored snapshot; nothing here touches stored data, and a stored position still validates because the fields are only widened
  - Docs lane: register rows for the ESPP and IB importers unchanged; the IB malformed-Cost-Basis drop (D-8) is untouched

skill_calls:
  - mattpocock-skills:diagnosing-bugs — not called, no fix attempt failed (one self-inflicted schema slip, cash_by_currency dropped in an edit, was caught by the first test run and fixed directly)
  - mattpocock-skills:tdd — not called, order forbids editing tests

risks:
  - The order fence did not list exposure_engine.py; I widened one type annotation there (no logic). No gate forced it (there is no python type checker in the gate); revert it if the fence is strict, behaviour is unchanged
  - Removing EnrichedPosition left _coerce_float orphaned in performance.py; removed it since the dead-code gate would fail otherwise (dashboard_history_engine.py has its own separate copy, untouched)
  - freedom24.py still calls _normalize_number on the beginning-balance cell with the result discarded, to keep the old resilience behaviour (a garbled beginning balance still skips the record). Odd to read; drop it only with a decision to change that skip semantics
  - Statement-stated Freedom24 cost basis would be lost for good: the design says never derive, so a future FF statement that does state a cost basis needs a parser change, not a flag
  - cost_basis_trust defaults to stated, so a persisted override lacking the key reads as stated even if its totals were fabricated (FF 3018.96 / 0.00); only the D-5 re-derive corrects it, not the schema
  - Exposure response snapshot echo also changes (cost_basis and unrealized_pnl serialise as null); any TS consumer that assumed numbers there sees null. Grep found no renderer of these fields in the desktop app
  - verification.result is PASS by reading the order's expected-red allowance: the targeted pytest exited non-zero on 3 failures, all Freedom24 reds owned by BE-2 and named in handoff; a strict reading would be FAIL

## Orchestrator brief
- BE-3 built to 05-design C1, C2 and the C5 merge rule: nullable ImportedPosition cost basis and P&L, PortfolioOverview with null-propagating totals and cost_basis_trust, EnrichedPosition and build_enriched_positions removed.
- Both fabrication sites are gone: freedom24.py positions and portfolio_snapshot_builder.py; ledger opening-lot estimate is guarded.
- Probe: IB2026 62255.14 / 3491.53 stated and unchanged; FF2026 None/None unavailable; IB+FF None/None unavailable; request-path IB None/None unavailable.
- Dashboard for IB2026 (frozen data) and Drawdown, Stress, Distribution over the request path are byte-identical whatever the cost basis is.
- No test is red because of BE-3; the 3 targeted reds are BE-2's Freedom24 ones. Full-suite reds also include golden determinism (H-1) and the roadmap check.
- Section Verification detail: exact counts, probe output, and how the no-fabrication check was done.

## Verification detail

Pytest, exact command `cd services/quant-engine && SKIP_GOLDEN_FRESHNESS_CHECK=1 python -m pytest app/tests -k "overview or importer or ledger or snapshot_builder"`: `3 failed, 108 passed, 910 deselected`. Failures: test_analytics.py::test_ff2026_dashboard_truth_values_match_imported_history_and_overview (first assertion start_value 2960.63 vs 3048.57, BE-2 window change), test_importer.py::test_import_freedom24_statement_returns_expected_snapshot (ledger count 8 vs 7), test_importer.py::test_freedom24_parsers_skip_malformed_records_without_raising (TypeError on dropped date argument). Identical to the set BE-1 reported for BE-2.

Full backend run with the same env var: `6 failed, 1015 passed`. The three above plus test_golden_pipeline_determinism (2) and test_build_roadmap::test_repo_roadmap_is_current.

Dead-code: `python scripts/detect_deadcode.py --strict` gives ruff, vulture and knip clean.

Probe output (be3_probe.py, market data mocked):
```
IB positions null cost basis: 0 of 18
overview IB2026: total_market_value=65746.67 total_cost_basis=62255.14 total_unrealized_pnl=3491.53 cost_basis_trust=stated
overview FF2026: total_market_value=3018.96 total_cost_basis=None total_unrealized_pnl=None cost_basis_trust=unavailable
FF VTI cost_basis None unrealized_pnl None market_value 3018.96
FF top_positions [{'symbol': 'VTI', 'market_value': 3018.96, 'weight': 1.0, 'unrealized_pnl': None}]
overview IB2026+FF2026: total_cost_basis=None total_unrealized_pnl=None cost_basis_trust=unavailable
merge stated + null VUAA (None, None)
FF VTI lot opening_balance 3.0 unit_cost None remaining_cost_basis None estimated False
FF VTI lot statement_trade 6.0 unit_cost 322.426 remaining_cost_basis 1934.56
builder: cost_basis set {None} unrealized set {None}
overview request-path IB: total_market_value=62843.22 total_cost_basis=None total_unrealized_pnl=None cost_basis_trust=unavailable
/engines/drawdown|stress|distribution/run: null-basis output == fabricated-basis output: True
/engines/exposure/run: differs only at overview and snapshot; overview now None/None/unavailable (was 62843.22/0.0/stated)
```
Independence on the Dashboard, IB2026 with `FrozenMarketData.from_file()`: `run_imported_dashboard_history` output is byte-identical for stated, null and fabricated cost basis (161 daily states, last market value 65753.77). The probe's own generic-mock Dashboard check returned an empty result for both IB and FF, so I discarded it as vacuous and used the frozen provider instead.

Fabrication check. Grep over app/ excluding tests for `cost_basis\s*=|unrealized_pnl\s*=|(cost|basis)\w*\s*=\s*[^=\n]*(market_value|close_price)|market_value\s*-\s*\w*cost`. Every hit is one of: IB importer parsing the statement's own Cost Basis / Unrealized P/L cells, ESPP importer parsing its stated cost and gain, freedom24.py and portfolio_snapshot_builder.py assigning None, the merge and ledger None-guarded sums, the overview totals, and two unrelated `return_basis="market_value"` strings. No `cost_basis = market_value`, `market_value - cost`, or `quantity * price` cost derivation remains. Limits: the grep is textual; a cost computed through a differently named variable would escape it, and I read the freedom24.py and snapshot-builder diffs by eye to cover that.
