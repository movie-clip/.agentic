REPORT 2026-09-02-us43.1-synthetic-history-module/03
status:      PARTIAL
verdict:     NONE

changed:
  - services/quant-engine/app/services/synthetic_history.py — new leaf module; module docstring + 3-import block per plan § 2; defines build_synthetic_snapshot_history_states and build_synthetic_snapshot_history_states_with_coverage, bodies verbatim from diagnostics_engine.py L761-924
  - services/quant-engine/app/services/synthetic_history.py — thin wrapper's internal self-call repointed from _build_..._with_coverage to the public build_..._with_coverage (only in-body edit)
  - services/quant-engine/app/services/diagnostics_engine.py — deleted both def _build_synthetic_snapshot_history_states* (former L761-924); added `from app.services.synthetic_history import build_synthetic_snapshot_history_states`
  - services/quant-engine/app/services/diagnostics_engine.py — L733 self-call renamed to public build_synthetic_snapshot_history_states (keyword args unchanged)
  - services/quant-engine/app/services/diagnostics_engine.py — dropped 4 now-dead imports: SYNTHETIC_COVERAGE_DE_MINIMIS_WEIGHT (core.constants), DailyPortfolioState / DailyStatePosition / SyntheticHistoryCoverage (schemas.reconciliation); dead-code gate confirms clean
  - services/quant-engine/app/services/attribution_engine.py — import + call site (L24, L98) swapped to build_synthetic_snapshot_history_states_with_coverage from app.services.synthetic_history
  - services/quant-engine/app/services/correlation_engine.py — import + call site (L35, L122) swapped to app.services.synthetic_history
  - services/quant-engine/app/services/distribution_engine.py — import + call site (L25, L117) swapped to app.services.synthetic_history
  - services/quant-engine/app/services/drawdown_engine.py — import + call site (L26, L117) swapped to app.services.synthetic_history
  - services/quant-engine/app/services/stress_engine.py — import + call site (L26, L95) swapped to app.services.synthetic_history

verification:
  command:   cd C:\projects\investments\portfolio && python scripts/run_all_tests.py
  result:    FAIL
  detail:    backend pytest 967 passed, 1 failed + 1 error, both in test-lane-owned files: ERROR test_synthetic_history_coverage.py (ImportError on old diagnostics_engine path); FAILED test_correlation_engine.py::test_portfolio_series_uses_total_market_value_not_portfolio_value (mocker.patch string L310). git diff dashboardGoldens.ts EMPTY. detect_deadcode.py --strict clean (ruff/vulture/knip). vitest+tsc not reached — run_all_tests.py halts at the pytest failure.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Test lane MUST retarget app/tests/test_synthetic_history_coverage.py: import block L21-23 to `from app.services.synthetic_history import (build_synthetic_snapshot_history_states_with_coverage,)` and rename the 6 call sites L61/89/111/124/146/177 (drop leading `_`). Suite has a live ImportError until this lands.
  - Test lane MUST update app/tests/test_correlation_engine.py L310 patch string `"app.services.correlation_engine._build_synthetic_snapshot_history_states_with_coverage"` -> `"app.services.correlation_engine.build_synthetic_snapshot_history_states_with_coverage"` (still patched on the consuming module). This is the sole cause of the 1 failed test.
  - AC2 pin test (new, test lane): assert `<engine>.build_synthetic_snapshot_history_states_with_coverage is synthetic_history.build_synthetic_snapshot_history_states_with_coverage` for attribution/correlation/distribution/drawdown/stress engines, and `not hasattr(diagnostics_engine, "_build_synthetic_snapshot_history_states")`.
  - New module public API: `build_synthetic_snapshot_history_states(snapshot, price_histories, valuation_dates) -> list[DailyPortfolioState]` and `build_synthetic_snapshot_history_states_with_coverage(...) -> tuple[list[DailyPortfolioState], SyntheticHistoryCoverage]`, both keyword-arg call convention unchanged.
  - Integration lane: verbatim char-diff condition (plan § 7) — the only in-body delta vs pre-move L761-924 is the thin wrapper's self-call `_build_..._with_coverage(` -> `build_..._with_coverage(`; the two `def` names lost their leading `_`. No other logic change.
  - After the test lane lands, `python scripts/run_all_tests.py` should be fully green — backend work here is complete and every non-test consumer is rewired.

risks:
  - Order DoD requires `run_all_tests.py` green, but non_goals forbid touching app/tests/ and the two failing files are test-lane-owned; suite-green is unreachable from this lane alone. Reported PARTIAL rather than DONE per PROTOCOL § 6. All lane-reachable checks pass (967 backend tests, dead-code gate, byte-identical goldens).
  - `DailyPortfolioState` import in diagnostics_engine.py was dropped and `detect_deadcode.py --strict` confirms it is genuinely dead — no dynamic/annotation use remained outside the moved region (recon § risk resolved).
  - New `from app.services.synthetic_history import ...` line placed immediately above the existing `from app.services.exposure_engine import ...` in diagnostics_engine.py; import block is not fully alphabetised in that file already, so no reordering was done.
  - Pre-existing uncommitted doc drift (CLAUDE.md, docs/product/epic-roadmap.md, docs/product/stories/README.md, docs/tech-debt-register.md, CONTEXT.md, Epic 43 PRD + story files) is present in the tree from run setup — not touched by this lane, flagged so integration does not attribute it here.
