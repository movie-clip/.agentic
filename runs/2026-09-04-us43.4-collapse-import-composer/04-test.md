REPORT 2026-09-04-us43.4-collapse-import-composer/04
status:      DONE
verdict:     NONE

changed:
  - services/quant-engine/app/tests/test_analytics.py — added test_import_engine_composer_module_no_longer_exists, pinning that `import app.services.import_engine_composer` raises ModuleNotFoundError, placed immediately after test_build_import_bootstrap_from_snapshot_falls_back_to_ledger_and_position_dates_when_statement_period_missing.

verification:
  command:   python scripts/run_all_tests.py
  result:    PASS
  detail:    backend 985 passed, 50 warnings in 25.61s; frontend 40 test files / 359 tests passed; tsc --noEmit clean; dead-code gate (ruff+vulture+knip) clean; "All tests passed."

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

risks:
  - none

## Orchestrator brief

- Added the single AC1/AC4 pin test per the DoD, matching the ModuleNotFoundError pattern at test_mcp_tools.py:361-367.
- Confirmed via `git status --porcelain` that the human's `git rm` of import_engine_composer.py already landed (staged D), so the pin test exercises the real post-deletion state, not a future one.
- Full canonical suite (`run_all_tests.py`) is green: backend 985 passed (984 from dispatch 03 + 1 new), frontend 359 passed, tsc clean, dead-code gate clean, `dashboardGoldens.ts` diff confirmed empty via `git diff --stat`.
- No file outside `services/quant-engine/app/tests/test_analytics.py` was edited by this lane.
