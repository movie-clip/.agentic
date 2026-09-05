REPORT 2026-09-02-us43.1-synthetic-history-module/04
status:      DONE
verdict:     NONE

changed:
  - services/quant-engine/app/tests/test_synthetic_history_coverage.py — import block retargeted from `app.services.diagnostics_engine._build_synthetic_snapshot_history_states_with_coverage` to `app.services.synthetic_history.build_synthetic_snapshot_history_states_with_coverage`
  - services/quant-engine/app/tests/test_synthetic_history_coverage.py — 6 call sites (L61/89/111/124/146/177) renamed to drop the leading underscore; explicit rename, no `as` alias
  - services/quant-engine/app/tests/test_synthetic_history_coverage.py — new AC2 pin test `test_all_engine_consumers_bind_to_the_shared_synthetic_history_symbol` appended
  - services/quant-engine/app/tests/test_correlation_engine.py — L310 patch string `_build_synthetic_snapshot_history_states_with_coverage` -> `build_synthetic_snapshot_history_states_with_coverage` on `app.services.correlation_engine`

verification:
  command:   cd C:\projects\investments\portfolio && python scripts/run_all_tests.py
  result:    PASS
  detail:    All tests passed. Backend pytest 980 passed; frontend vitest 359 passed (40 files); tsc --noEmit clean; dead-code gate clean (ruff/vulture/knip). git diff apps/desktop/src/test/dashboardGoldens.ts EMPTY.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - AC2 pin test name is `test_all_engine_consumers_bind_to_the_shared_synthetic_history_symbol` in test_synthetic_history_coverage.py; asserts object identity of `build_synthetic_snapshot_history_states_with_coverage` across attribution/correlation/distribution/drawdown/stress engines vs `app.services.synthetic_history`, plus `not hasattr` for both old private diagnostics_engine names
  - grep for `_build_synthetic` in app/tests/ now returns clean; coverage-matrix test file has 12 `def test_` functions (11 pre-existing unchanged in substance + 1 new)
  - No shared fixture added; existing `imported_snapshot` / `position` from app/tests/fixtures reused unchanged

risks:
  - Coverage-matrix cases and fixtures were edited only for the imported symbol name (underscore drop); no assertion, expected value, or fixture body changed — behaviour-neutrality proof (AC4) intact
  - AC2 pin test asserts `not hasattr(diagnostics_engine, "_build_synthetic_snapshot_history_states_with_coverage")` in addition to the non-coverage name, per DoD; both hold against the backend lane's gutted module
