REPORT 2026-09-11-risk-summary-audit-foldable/12
status:      DONE
verdict:     NONE

changed:
  - services/quant-engine/app/tests/test_analytics.py — 2 of 7 pinned drawdown/investor_economics assertions were already fixed by a prior terminated attempt (test_run_diagnostics_engine_uses_history_context_for_snapshot_requests, test_run_imported_diagnostics_engine_populates_history_derived_summary_fields); confirmed unchanged.
  - services/quant-engine/app/tests/test_analytics.py — test_run_imported_diagnostics_engine_marks_verified_adjusted_close_when_all_history_rows_have_adjusted_fields: drawdown-null assertions replaced with real values (0.0/0.0) and relative_risk.active_return_pct with 0.1; this fixture is the verified-basis fixture the technical plan's risks section flagged as missing (see risks).
  - services/quant-engine/app/tests/test_analytics.py — test_run_imported_diagnostics_engine_keeps_unverified_status_when_any_factor_history_lacks_adjusted_fields: same pinned-null assertions replaced with real values (0.0/0.0, active_return_pct 0.1) under its degraded section_trust.
  - services/quant-engine/app/tests/test_analytics.py — test_run_imported_diagnostics_engine_refuses_drawdown_family_even_when_history_is_available renamed to test_run_imported_diagnostics_engine_publishes_drawdown_family_when_history_is_available; all drawdown/relative-risk/rolling-series null assertions rewritten to real values (-4.55/-4.55, active_return_pct 1.0, information_ratio 1.84).
  - services/quant-engine/app/tests/test_analytics.py — added test_build_portfolio_risk_summary_volatility_is_none_not_zero_at_n_equals_one (Fix 4 N=1 regression).
  - services/quant-engine/app/tests/test_analytics.py — added test_allow_diagnostics_relative_return_outputs_passes_through_its_argument (direct unit coverage of the Fix 2 gate), plus the corresponding private-import line.
  - services/quant-engine/app/tests/test_routes.py — test_diagnostics_engine_route_uses_history_context_when_present: investor_economics_status assertion fixed (available/None) and drawdown/relative_risk assertions fixed to real values (drawdown compared to volatility_regime.snapshot; active_return_pct 0.8, information_ratio 10.15).
  - services/quant-engine/app/tests/test_routes.py — test_imported_diagnostics_engine_route_accepts_imported_snapshot_payload: investor_economics_status assertion fixed (available/None); drawdown/relative_risk None assertions kept as-is with a comment, confirmed via TestClient probe to be the genuine N<2 math-layer case, not the reversed gate.
  - services/quant-engine/app/tests/test_trust_gate.py — added test_allow_diagnostics_drawdown_outputs_passes_through_its_argument (direct unit coverage of the Fix 1 gate).

verification:
  command:   cd services/quant-engine && pytest && cd ../../apps/desktop && npx vitest run
  result:    PASS
  detail:    Backend: 1004 passed, 0 failed, 50 warnings (all pytest-socket live-network guard warnings, pre-existing/unrelated) in ~95s. Frontend: 42 test files passed (42), 380 tests passed (380) in ~6s. mcp__project__check_gates confirms deadcode clean, tsc clean, goldens not drifted.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Frontend's RiskSummaryCard.test.tsx and DashboardPanel.test.tsx stale-copy assertions (work order items 10-11) were already corrected to the new copy by a prior terminated attempt on this same working tree before this dispatch started — verified via grep and a passing vitest run, no edit needed from this lane.
  - test_run_imported_diagnostics_engine_marks_verified_adjusted_close_when_all_history_rows_have_adjusted_fields is confirmed to be the "verified_adjusted_close end-to-end" fixture the technical plan's risks section said was missing.
  - That fixture already carried a fully verified section_trust before this order; only its drawdown/relative-risk assertions needed updating, no new fixture was built — future audits can cite this test name instead of treating the fixture gap as still open.
  - Route-test pinned floats (active_return_pct 0.8, information_ratio 10.15) diverge from a standalone-script probe run outside pytest (0.7/0.88) for the same payload.
  - Always derive route-test pinned values from an actual pytest run of that exact test, not a bare TestClient script — conftest.py's autouse fixtures change what MarketDataService returns relative to a script run outside the pytest session.

risks:
  - Backend production code (trust_gate.py, diagnostics_engine.py, risk.py) and two frontend files (RiskSummaryCard.tsx, DashboardPanel.test.tsx) were already modified by a prior terminated dispatch of this order before this session started.
  - This lane only touched test_analytics.py, test_routes.py, and test_trust_gate.py, confirmed via `git status` before and after — no production file was edited by this lane.
  - test_imported_diagnostics_engine_route_accepts_imported_snapshot_payload's drawdown/relative-risk fields remain None post-fix — confirmed via a direct TestClient probe that this is the genuine N<2 insufficient-history math-layer case (historical_sections_available=True, fields still None), not a leftover pinned-null bug.
  - Pinned floats in the route/analytics tests (0.8, 10.15, -4.55, 1.84, etc.) are exact per an actual pytest run against deterministic conftest.py-mocked data, but are magic numbers with no hand-derivable provenance, unlike the US-27.1 hand-computed IR fixture elsewhere in this file.
  - A future contributor changing the underlying mocked fixture data will need to re-derive these pinned floats the same way this lane did: run the test, read the AssertionError, pin the real value.
