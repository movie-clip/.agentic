REPORT 2026-09-30-import-critical-fixes/10
status:      PARTIAL
verdict:     NONE

changed:
  - services/quant-engine/app/tests/test_import_combined.py — NEW: merge idempotence, chained/doubled refusals, analyze-combined route, admission roll-up, offsetting-delta pair, path independence (US-46.1, US-46.3)
  - services/quant-engine/app/tests/test_freedom24_ledger.py — NEW: trade date vs settlement, single commission, cash roll-forward 52.04, unparseable-date synthetic fixture, no-fallback guard (US-46.2)
  - services/quant-engine/app/tests/test_cost_basis_unavailable.py — NEW: FF2026 nulls, overview totals and trust, request path, merge, lots, fabrication guards, IB dashboard independence (US-46.4)
  - services/quant-engine/app/tests/test_importer.py — known-red pins updated: ledger count 8 to 7 (:287), date set now {2026-03-31, 2026-04-01, 2026-04-07} (:288), _parse_transactions call drops the date arg (:332)
  - services/quant-engine/app/tests/fixtures.py — added account_snapshot() shared builder for single-account synthetic statements
  - services/quant-engine/app/tests/test_fixtures.py — two tests validating account_snapshot against the real schema and its admission knobs
  - services/quant-engine/app/tests/statement_truths.py — added IB_TOTAL_COST_BASIS_2DP and IB_TOTAL_UNREALIZED_PNL_2DP (62255.14 / 3491.53)

verification:
  command:   cd services/quant-engine && SKIP_GOLDEN_FRESHNESS_CHECK=1 python -m pytest app/tests -q (via run_tests scope=backend, which sets the env var); ruff on touched files; python scripts/detect_deadcode.py --strict
  result:    FAIL
  detail:    4 failed, 1103 passed. Reds: test_analytics.py::test_ff2026_dashboard_truth_values_match_imported_history_and_overview (T-2, new FF window), test_golden_pipeline_determinism x2 (H-1 recapture), test_build_roadmap::test_repo_roadmap_is_current (stale ROADMAP.md). None caused by this lane. Dead-code strict clean. see § Verification detail

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - New shared builder fixtures.account_snapshot(account_id, *, positions, cash, stock_total, with_totals, as_of_date, base_currency, source_name) returns a payload dict; untouched it is admitted/verified. stock_total makes a position-value delta; with_totals=False makes it degraded; account_id=None removes identity
  - Statement pins IB_TOTAL_COST_BASIS_2DP and IB_TOTAL_UNREALIZED_PNL_2DP live in statement_truths.py and are read only by test_cost_basis_unavailable.py; update them on a statement refresh
  - T-2 owns test_analytics.py::test_ff2026_dashboard_truth_values_match_imported_history_and_overview (first failing assertion is the old window start value 2960.63 vs 3048.57); it pins the 2025-12-01 window with mocked prices and must be rewritten to the AC 6-13 values
  - T-2 owns the FF dashboard independence check (stated vs null vs fabricated basis) which needs the recaptured frozen FF window; only IB independence is pinned here, using FrozenMarketData.from_file()
  - H-1 clears test_golden_pipeline_determinism (2 tests); the ROADMAP.md staleness (test_build_roadmap) clears with python scripts/build_roadmap.py, which is the human's or docs lane's step, not a test edit
  - Risk-tab engines (stress, drawdown, distribution) take request-path payloads that carry no cost basis, so their independence is structural; no per-engine before/after test was written
  - Scratch files created by this lane: none in the repo; mutation scripts sit in the session scratchpad only
  - Mutation evidence: recompute-only, last-file-only, account-blind merge and fabricated-date mutants each turn the named tests red (see § Verification detail)

skill_calls:
  - mattpocock-skills:tdd — not called, no mock-or-real choice beyond the conftest autouse market-data mocks the pack prescribes; real statements and TestClient throughout
  - mattpocock-skills:diagnosing-bugs — not called, the one red I hit (a wrong premise in my own test) was diagnosed by reading the merge code

risks:
  - Combining a clean statement with a totals-less one yields the combined recompute withheld, not degraded: merged stock_total sums only the available totals against all positions. Pre-existing merge behaviour in statement_importer.py _merge_statement_totals; conservative, not a defect of this slice, but it makes a degraded-plus-clean distinct-account pair unreachable in tests
  - Guard 1 in statement_importer.py refuses two identical combined inputs (A+B and A+B), which key equality would have replaced correctly; BE-1 reported it; I did not pin it either way
  - test_the_two_fabrication_sites_construct_positions_with_literal_none is an AST check that couples to the ImportedPosition call sites in freedom24.py and portfolio_snapshot_builder.py; a refactor that builds positions via a helper needs the guard updated, its failure message says so
  - The regex fabrication guard omits a quantity-times-price pattern on purpose because ledger lot arithmetic legitimately multiplies a stated trade price by a quantity; a cost derived through a differently named variable at a new site would escape the regex and only the two-site AST check would cover it
  - Expected-red note: the order's verification command is not fully green, so verification is FAIL and status PARTIAL; every red is named and attributed above and none is a genuine defect in this slice's behaviour
  - Not covered by design (frontend or later lanes): US-46.1 AC 7-8, 10-12 UI paths, US-46.3 AC 12-15, US-46.4 AC 9 and 11 are persistence or rendering behaviour for T-3; AC 14 Other statements unchanged for IB/ESPP dashboards is covered for IB only

## Orchestrator brief
- T-1 delivered: 88 net new passing tests across three new files plus 2 fixture tests; known-red pins at test_importer.py:287/:288/:332 updated, not deleted.
- Offsetting-delta pair (U1 +10, U2 -10 on distinct accounts) exists; recompute alone gives admitted/verified, the D-3 rule gives withheld/withheld. Recompute-only mutant turns it red.
- Suite: 4 failed, 1103 passed. Reds are T-2 (FF dashboard test), H-1 (2 golden determinism), and stale ROADMAP.md; none from this lane.
- FF dashboard independence check and FF AC 6-13 replay values are left for T-2.
- Section "Coverage map (05-design § Lane split T-1 "Must include")": AC to test table for the T-1 Must-include list. Section "Verification detail": counts and mutation results.

## Coverage map (05-design § Lane split T-1 "Must include")

| Must include | Test (file::name) | AC |
|---|---|---|
| combine(S,S) = S on IB2026 | test_import_combined::test_combine_of_a_statement_with_itself_is_idempotent_on_positions_and_cash | 46.1 AC 1-4 |
| analyze-combined on real IB2026.csv | test_import_combined::test_analyze_combined_ib_twice_matches_ib_alone_on_real_statement, ::test_analyze_combined_carries_the_snapshot_the_merge_produced | 46.1 AC 1-4, 6 |
| flat [IB, ESPP, IB] equals [IB, ESPP] | ::test_flat_combine_of_ib_espp_ib_leaves_ib_unchanged | 46.1 AC 1-4 |
| chained-input refusal | ::test_chained_combine_of_a_combined_input_with_a_shared_account_is_refused, ::test_analyze_combined_chained_input_is_a_400_with_the_guard_message, ::test_stored_snapshot_with_repeated_account_part_is_refused_even_alone, ::test_analyze_combined_legacy_doubled_account_is_a_400_even_as_the_only_input | 46.1 AC 12 (fail-closed) |
| five fixture pairs' labels | ::test_fixture_pairs_are_degraded_and_keep_each_constituent_label (5 params), ::test_last_file_only_label_is_gone_for_ib_plus_espp | 46.3 AC 1-4, 9 |
| single statements unchanged | ::test_single_statements_keep_their_own_label_and_have_no_rollup, ::test_single_input_seam_equals_the_single_snapshot_bootstrap | 46.3 AC 10; 46.1 AC 9 |
| offsetting-delta pair, distinct accounts | ::test_offsetting_deltas_across_two_accounts_cannot_lift_the_combined_label, ::test_offsetting_deltas_hold_through_the_route_and_in_either_order | 46.3 AC 6 |
| superseded same-account case | ::test_superseded_statement_still_contributes_its_own_label (2 params) | 46.3 AC 7 |
| constituent evidence kept | ::test_constituents_follow_input_order_and_keep_their_checks, ::test_rollup_rule_name_is_the_published_contract_string | 46.3 AC 8 |
| upload and add path agree | ::test_multi_file_upload_and_analyze_combined_give_the_same_label_and_constituents, ::test_multi_file_path_returns_constituents_but_analyze_combined_does_not | 46.3 AC 5 |
| refused combine 400 and no summary | ::test_refused_combine_is_a_400_with_no_combined_admission_or_portfolio (2 params), ::test_refused_combine_raises_before_any_admission_is_built | 46.1 AC 7; 46.3 AC 11 |
| carried evidence (D-11) and ladder | ::test_carried_admission_from_a_saved_node_lowers_the_label, ::test_carried_admissions_travel_through_the_route, ::test_withheld_and_unavailable_stay_distinct_rungs_in_the_rollup | 46.3 AC 13-14 (engine half) |
| distinct accounts still sum; replace same account | ::test_distinct_accounts_still_sum_a_shared_symbol_and_cash, ::test_same_account_later_statement_replaces_rather_than_sums | 46.1 AC 5 |
| missing account / currency mismatch refusal | ::test_combine_refuses_a_missing_account_identity_and_a_base_currency_mismatch | 46.1 AC 7-8 |
| Freedom24: trade date not settlement, dates set | test_freedom24_ledger::test_trades_are_dated_by_trade_date_not_settlement, ::test_no_ledger_entry_carries_a_date_the_statement_does_not_state; test_importer::test_import_freedom24_statement_returns_expected_snapshot (:287/:288) | 46.2 AC 1-2 |
| Freedom24: commission once, 6.76, per trade | ::test_each_commission_sits_on_its_trade_row_dated_to_the_trade, ::test_no_period_fee_row_exists_so_total_commission_is_6_76_not_13_52 | 46.2 AC 4 |
| Freedom24: cash 52.04 | ::test_ledger_cash_rolls_forward_to_the_statement_ending_cash | 46.2 AC 5 |
| Freedom24: unparseable date synthetic fixture | ::test_record_with_an_unparseable_trade_date_is_dropped_and_the_rest_imports (5 params), ::test_a_page_of_only_bad_dates_yields_no_entries_rather_than_synthetic_ones; test_importer::test_freedom24_parsers_skip_malformed_records_without_raising (:332) | 46.2 AC 3 |
| Freedom24: no fallback machinery | ::test_no_synthetic_date_or_period_commission_machinery_remains | 46.2 AC 2-4 |
| FF2026 VTI cost null, schema accepts absence | test_cost_basis_unavailable::test_freedom24_vti_has_no_cost_basis_and_no_unrealized_pnl, ::test_position_schema_accepts_absent_cost_basis_and_pnl_and_defaults_them_to_none | 46.4 AC 1 |
| trust unavailable, not withheld/degraded | ::test_ff_overview_totals_are_unavailable_with_trust_unavailable, ::test_overview_schema_rejects_stated_over_a_null_total_and_rejects_other_trust_words | 46.4 AC 2 |
| overview totals null, top position null | ::test_ff_overview_totals_are_unavailable_with_trust_unavailable, ::test_ff_top_positions_report_vti_pnl_as_unavailable_not_zero, ::test_ff_bootstrap_overview_is_unavailable_end_to_end | 46.4 AC 3-4 |
| IB unchanged | ::test_ib_overview_totals_are_the_statement_stated_values, ::test_ib_and_espp_still_state_cost_basis_for_every_position, ::test_ib_plus_espp_totals_stay_stated_and_are_the_sum_of_the_stated_parts | 46.4 AC 6 |
| IB+FF null | ::test_ib_plus_freedom24_totals_are_unavailable_not_a_silent_ib_only_sum | 46.4 AC 5 |
| request-path builder null + grep-style guard | ::test_request_path_builder_yields_unavailable_cost_basis_for_every_position, ::test_request_path_overview_is_unavailable_not_market_value_and_zero, ::test_exposure_engine_route_serialises_cost_basis_as_null_not_zero, ::test_analyze_snapshot_route_added_node_path_is_unavailable, ::test_no_production_module_derives_cost_basis_or_zero_fills_pnl, ::test_the_fabrication_guard_catches_each_known_fabrication_shape, ::test_the_two_fabrication_sites_construct_positions_with_literal_none | 46.4 AC 7 |
| merge sums only when both non-null | ::test_merge_sums_cost_basis_and_pnl_when_both_inputs_state_them, ::test_merge_of_a_null_with_anything_is_none_never_the_stated_side_alone (3 params), ::test_merge_treats_cost_basis_and_pnl_independently | 46.4 AC 8 |
| no opening-lot estimate on null | ::test_ff_opening_vti_lot_carries_no_estimated_unit_cost | 46.4 AC 10 |
| Dashboard outputs unchanged for IB | ::test_ib_dashboard_history_is_independent_of_cost_basis_and_pnl | 46.4 AC 12 (IB half) |
| EnrichedPosition removed | ::test_enriched_position_and_its_builder_are_removed | 46.4 design |

Not in this lane: 46.2 AC 6-14 (dashboard replay values, T-2 after H-1); 46.4 AC 12 FF half (T-2); 46.1 AC 10-12, 46.3 AC 12-15 UI and persistence, 46.4 AC 9 and 11 (T-3).

## Verification detail

- Full backend, exact command `cd services/quant-engine && SKIP_GOLDEN_FRESHNESS_CHECK=1 python -m pytest app/tests -q` (through run_tests scope=backend): `4 failed, 1103 passed, 49 warnings`. Baseline before this lane: `6 failed, 1015 passed`. The two Freedom24 importer reds are fixed; 88 tests added.
- Remaining reds and attribution:
  - test_analytics.py::test_ff2026_dashboard_truth_values_match_imported_history_and_overview — depends on the new FF window (T-2). Left untouched per the order.
  - test_golden_pipeline_determinism.py::test_render_is_deterministic and ::test_generated_matches_committed_goldens — H-1 recapture pending (FrozenMarketDataMiss for the FF window).
  - test_build_roadmap.py::test_repo_roadmap_is_current — untracked US-46.x stories make ROADMAP.md stale; regenerate with python scripts/build_roadmap.py (not a test change).
- New files alone: test_import_combined.py 37 passed, test_freedom24_ledger.py 13 passed, test_cost_basis_unavailable.py 34 passed, test_fixtures.py 5 passed, test_importer.py 28 passed.
- ruff on touched files: clean. detect_deadcode.py --strict: ruff, vulture, knip clean.
- Falsifier runs (monkeypatch mutants from a scratchpad script, no repo file edited or reverted):
  - Recompute-only admission: 11 of 18 selected admission tests fail, including the offsetting-delta test. With the roll-up structure kept but the top-level label set to the combined recompute, the offsetting test still fails on `assert (decision, trust_level) == ("withheld", "withheld")` while its premise asserts the recompute alone is admitted/verified.
  - Last-file-only admission: the 5 pair tests and test_last_file_only_label_is_gone_for_ib_plus_espp fail.
  - Account-blind merge (all snapshots sum): 4 merge tests fail, including the IB-twice route test (VUAA 160).
  - Fabricated trade date (always 2025-12-01): 11 Freedom24 tests fail, including the two updated test_importer pins.
