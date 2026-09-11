REPORT 2026-09-11-risk-summary-audit-foldable/09
status:      PARTIAL
verdict:     NONE

changed:
  - services/quant-engine/app/services/trust_gate.py — `allow_diagnostics_drawdown_outputs` now takes `historical_sections_available: bool` keyword-only and returns it, with a dated rationale comment (Fix 1).
  - services/quant-engine/app/services/diagnostics_engine.py — `_allow_diagnostics_relative_return_outputs` now takes `historical_sections_available: bool` keyword-only and returns it, with a dated rationale comment (Fix 2).
  - services/quant-engine/app/services/diagnostics_engine.py — both gate call sites (lines formerly 326, 339) updated to pass `historical_sections_available=True`.
  - services/quant-engine/app/analytics/risk.py — `build_portfolio_risk_summary`'s volatility guards changed from `if portfolio_samples`/`if benchmark_samples` to `if len(portfolio_samples) >= 2`/`if len(benchmark_samples) >= 2` (Fix 4).

verification:
  command:   cd services/quant-engine && pytest
  result:    FAIL
  detail:    994 passed, 7 failed. All 7 failures are the expected pinned-null/pinned-status regressions from unwithholding the Fix 1/Fix 2 gates (see risks); no other test regressed. `_calculate_annualized_volatility`'s internal N<2 branch (risk.py:2117-2120) left untouched per plan § Decisions.

contract_notes:
  - No schema file touched; the reachable-value-space changes on the six fields in the technical plan's § Contract table are exactly as that plan described — the doc corrections it lists (dashboard-fields.md:238,242,287; financial-methodology.md:1054-1058,1141-1149) are the docs lane's work per the plan, not new notes here.
  - Unenumerated by the plan's § Contract table: `run_metadata.investor_economics_status` now resolves to `available` instead of always `withheld`, because `build_diagnostics_investor_economics_status` (trust_gate.py:301-313) derives its result from `allow_drawdown_outputs and allow_relative_return_outputs` — both now `True` under the same condition this order flips. See § Risks.

pack_corrections:
  - none

handoff:
  - Test lane: `test_run_diagnostics_engine_uses_history_context_for_snapshot_requests` (test_analytics.py) now fails on a pinned `drawdown_summary.current_drawdown_pct is None` assertion; real value is now `0.0` in this fixture — needs updating to assert the real value (or confirm the fixture is a genuine N<2 case, which it is not per the failure output).
  - Test lane: `test_run_imported_diagnostics_engine_populates_history_derived_summary_fields` (test_analytics.py) now fails on a pinned `investor_economics_status == {"status": "withheld", ...}` assertion; actual is now `{"status": "available", "reason": None}`.
  - Test lane: `test_run_imported_diagnostics_engine_marks_verified_adjusted_close_when_all_history_rows_have_adjusted_fields` (test_analytics.py) fails on a pinned drawdown-null assertion; its fixture already carries a fully `verified_adjusted_close` section_trust, so it may seed the new verified-basis fixture the plan's risks section says is missing.
  - Test lane: `test_run_imported_diagnostics_engine_keeps_unverified_status_when_any_factor_history_lacks_adjusted_fields` (test_analytics.py) now fails on the same pinned drawdown-null assertion, under a degraded (not verified) section_trust.
  - Test lane: `test_run_imported_diagnostics_engine_refuses_drawdown_family_even_when_history_is_available` (test_analytics.py) now fails — its own name states the policy this fix reverses; it needs a rewrite (rename + reassert real values), not a relaxed assertion.
  - Test lane: `test_diagnostics_engine_route_uses_history_context_when_present` (test_routes.py:1077, drawdown assertions at :1088-1089) now fails first on the `investor_economics_status` pinned-withheld assertion before reaching the drawdown lines the plan cited.
  - Test lane: `test_imported_diagnostics_engine_route_accepts_imported_snapshot_payload` (test_routes.py:2533, drawdown at :2546-2547, relative_risk at :2550-2551) fails the same way — `investor_economics_status` pinned-withheld assertion fails first, ahead of the drawdown/relative-return lines the plan named.
  - Test lane: no existing test pinned the old `portfolio_volatility_pct`/`benchmark_volatility_pct` N=1 `0.0` value, so Fix 4 produced zero test regressions — the new N=1-returns-None regression test (test_analytics.py, per plan § Fix 4) is purely additive.

risks:
  - `investor_economics_status` flipping to `available` is a mechanical side effect of trust_gate.py:301-313 consuming the same two booleans this order flips, not a deliberate extra change — the plan's § Contract table did not name this field, so docs close-out should give it the same "becomes accurate" confirmation pass already planned for drawdown/relative-return.
  - Two now-failing route tests fail at their `investor_economics_status` assertion before pytest reaches the drawdown-null lines the plan cited (test_routes.py:1088-1089, :2546-2547) — those lines are still wrong under the new behavior, just not yet reported; fix both assertions per test, not only the first one pytest shows.
  - `status: PARTIAL` here reflects protocol § 6 (verification.result is FAIL, so DONE is unavailable), not incomplete work — all three fixes are implemented exactly per the plan and every DoD bullet is met; the 7 failures are the order's own anticipated, named exception (pinned-null tests the test lane owns), not a defect in this change.
