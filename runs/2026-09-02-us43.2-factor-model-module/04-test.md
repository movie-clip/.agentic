REPORT 2026-09-02-us43.2-factor-model-module/04
status:      DONE
verdict:     NONE

changed:
  - services/quant-engine/app/tests/test_analytics.py — L15 split: DEFAULT_FACTOR_DEFINITIONS now imported `from app.analytics.factor_model`, remaining names stay on the risk import; fixes the ~23 downstream use sites in one edit.
  - services/quant-engine/app/tests/test_analytics.py — L7914 `risk_module._fit_factor_model` -> `risk_module.fit_factor_model`; L7924 monkeypatch target `"_fit_factor_model"` -> `"fit_factor_model"`; L7992 `risk_module._orthogonalize_factors_window` -> `risk_module.orthogonalize_factors_window`. L5298 / L7907 / L17-18 left unchanged per 02.
  - services/quant-engine/app/tests/test_analytics.py — 2 new tests after `test_orthogonalize_factors_window_reports_dropped_duplicate`: `test_return_basis_literal_lives_in_schemas_and_is_shared_by_reference` (AC2 pin) and `test_factor_model_fit_symbols_are_shared_by_reference_across_the_seam` (AC5 identity).
  - services/quant-engine/app/tests/test_attribution.py — L416 `attr_mod._fit_factor_model` -> `attr_mod.fit_factor_model`; L426 monkeypatch target `"_fit_factor_model"` -> `"fit_factor_model"`.
  - .claude/skills/write-story/SKILL.md — one new analytics-module table row for `services/quant-engine/app/analytics/factor_model.py`, placed after the risk.py row; clears `test_docs_paths.py::test_write_story_table_covers_every_analytics_module`.

verification:
  command:   cd C:\projects\investments\portfolio && python scripts/run_all_tests.py
  result:    PASS
  detail:    run_all_tests.py "All tests passed." — backend 982 passed (was 976+4-failed pre-lane; 4 retargeted failures fixed + 2 new pin tests), desktop vitest green, tsc --noEmit green, dead-code strict (ruff+vulture+knip) clean. git diff apps/desktop/src/test/dashboardGoldens.ts EMPTY (exit 0). Factor-model / factor-shift / model-reliability / rolling-factor-loadings blocks + all of test_attribution.py + all test_stress*.py pass unchanged in substance.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - New test `test_return_basis_literal_lives_in_schemas_and_is_shared_by_reference` (test_analytics.py) pins `typing.get_args(ReturnBasis) == ("portfolio_value","market_value","market_value_trade_neutral")` and asserts `risk`, `attribution`, `diagnostics_engine` all bind the same object from `app.schemas.return_basis`.
  - New test `test_factor_model_fit_symbols_are_shared_by_reference_across_the_seam` (test_analytics.py) pins `risk_module.fit_factor_model is factor_model.fit_factor_model`, same for `orthogonalize_factors_window`, plus `attribution.fit_factor_model is factor_model.fit_factor_model`.
  - No shared fixture added; both new tests use local imports only, matching the file's existing in-test import style.
  - No `from app.analytics.risk import _<factor-symbol>` remains in app/tests/ — verified by grep (only the test-function name `test_orthogonalize_factors_window_reports_dropped_duplicate` still contains the substring).
  - Docs lane T-43.2.4 still owns confirming the SKILL.md row wording and the methodology / architecture / tech-debt-register doc re-points listed in 03 contract_notes.

risks:
  - The SKILL.md row is in this lane's scope by the work order but its wording is provisional; T-43.2.4 is expected to finalise it. If the docs lane rewrites it, the only guard is `test_docs_paths.py` which just needs the `app/analytics/factor_model.py` path token present anywhere in the row.
  - AC5's own wording ("test_analytics.py:17-18 private-symbol imports are updated") is a mis-statement — nothing on L17-18 moved, so those lines are correctly left untouched (per 02 § Test edit list #6). Flagged for the reviewer.
  - test_attribution.py L416/L426 retarget is an AC5 gap the story's AC5 text did not name (only 02 § Test edit list #7-8 caught it); done here, reviewer should note AC5 wording is under-inclusive.
