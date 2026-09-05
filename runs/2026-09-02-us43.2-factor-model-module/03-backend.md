REPORT 2026-09-02-us43.2-factor-model-module/03
status:      PARTIAL
verdict:     NONE

changed:
  - services/quant-engine/app/analytics/factor_model.py — NEW leaf module; verbatim UcitsCandidateMapping, FactorDefinition, DEFAULT_FACTOR_DEFINITIONS, FACTOR_PROXY_MAP, FACTOR_KEY_MAP, ROLLING_RIDGE_FLOOR, ORTHOGONALIZATION_ZERO_RESIDUAL_THRESHOLD, orthogonalize_factors_window, fit_factor_model, _least_squares, _solve_linear_system, _dot. Imports only {__future__, dataclasses}.
  - services/quant-engine/app/analytics/risk.py — deleted the 12 moved symbols; added import-back from app.analytics.factor_model (7 names, NOT FACTOR_KEY_MAP); added `from app.schemas.return_basis import ReturnBasis`; deleted local ReturnBasis Literal + its comment.
  - services/quant-engine/app/analytics/risk.py — renamed _selected_history_return_series -> selected_history_return_series at def (L871) + 4 call sites; updated _build_rolling_factor_loadings 2 call sites to un-prefixed orthogonalize_factors_window / fit_factor_model. Bodies byte-identical.
  - services/quant-engine/app/schemas/return_basis.py — added top-level `ReturnBasis = Literal["portfolio_value", "market_value", "market_value_trade_neutral"]` after the Literal family, with risk.py's explanatory comment ported verbatim.
  - services/quant-engine/app/analytics/attribution.py — split risk import: factor symbols from app.analytics.factor_model, selected_history_return_series from app.analytics.risk, ReturnBasis from app.schemas.return_basis; renamed 3 call sites (L133, L198, L205).
  - services/quant-engine/app/services/stress_engine.py — FACTOR_PROXY_MAP now imported from app.analytics.factor_model; STRESS_SCENARIOS / build_* still from app.analytics.risk.
  - services/quant-engine/app/services/attribution_engine.py — FACTOR_PROXY_MAP import repointed to app.analytics.factor_model.
  - services/quant-engine/app/services/diagnostics_engine.py — FACTOR_PROXY_MAP repointed to app.analytics.factor_model; ReturnBasis added to the existing `from app.schemas.return_basis import ...` line.

verification:
  command:   cd C:\projects\investments\portfolio && python scripts/run_all_tests.py
  result:    FAIL
  detail:    4 failed, 976 passed (backend pytest); all 4 failures are outside this lane's scope. 3 are test-lane monkeypatch retargets of the renamed factor-model symbols: test_analytics.py::test_rolling_factor_loadings_never_emit_nonfinite_values, test_analytics.py::test_orthogonalize_factors_window_reports_dropped_duplicate, test_attribution.py::test_nonfinite_window_skipped_and_response_is_json_safe. 1 is a docs table: test_docs_paths.py::test_write_story_table_covers_every_analytics_module needs a factor_model.py row in .claude/skills/write-story/SKILL.md. Dead-code gate (ruff+vulture+knip+tsc) green; git diff apps/desktop/src/test/dashboardGoldens.ts EMPTY; 59 substantive factor/attribution/stress/return-basis behaviour tests pass; live import + identity checks pass (risk.fit_factor_model is factor_model.fit_factor_model, risk.ReturnBasis is schemas.return_basis.ReturnBasis, etc.).

contract_notes:
  - schema hook fired on schemas/return_basis.py; no types.ts or docs/contracts mirror owed — ReturnBasis is a Literal param annotation, not a Pydantic model field.
  - docs/finance/financial-methodology.md §Statistical Factor Model still attributes fit_factor_model / orthogonalize_factors_window / FactorDefinition / DEFAULT_FACTOR_DEFINITIONS / FACTOR_PROXY_MAP / FACTOR_KEY_MAP / ROLLING_RIDGE_FLOOR to risk.py; they now live in analytics/factor_model.py (docs lane T-43.2.4).
  - docs/architecture/system-architecture.md analytics module inventory does not list analytics/factor_model.py (docs lane T-43.2.4).
  - .claude/skills/write-story/SKILL.md analytics-module table has no row for analytics/factor_model.py — test_docs_paths.py::test_write_story_table_covers_every_analytics_module fails until a row is added; not named in 02 § Docs edit list, so it is a scope gap for the docs lane.

pack_corrections:
  - none

handoff:
  - Test lane still owes (per 02 § Test edit list): test_analytics.py L7914/L7924 risk_module._fit_factor_model -> fit_factor_model; L7992 risk_module._orthogonalize_factors_window -> orthogonalize_factors_window; test_attribution.py L416/L426 attr_mod._fit_factor_model -> fit_factor_model; L15 move DEFAULT_FACTOR_DEFINITIONS import to app.analytics.factor_model; plus the 2 new AC2/AC5 tests.
  - risk.py imports back from factor_model: DEFAULT_FACTOR_DEFINITIONS, FACTOR_PROXY_MAP, FactorDefinition, ROLLING_RIDGE_FLOOR, UcitsCandidateMapping, fit_factor_model, orthogonalize_factors_window. FACTOR_KEY_MAP is deliberately NOT re-imported (no risk.py consumer; ruff F401 would flag it).
  - AC3 disposition: _least_squares / _solve_linear_system / _dot moved into factor_model.py, kept underscore-private, NOT re-imported by risk.py — recon-confirmed zero non-factor callers.
  - selected_history_return_series (now public) and _series_to_returns (still underscore) stay in risk.py; both bodies byte-identical to pre-move.
  - Renamed-fn monkeypatches still bind: _build_rolling_factor_loadings (in risk.py) resolves fit_factor_model / orthogonalize_factors_window against risk.py module globals at call time; identity checks confirm they are the factor_model objects.
  - factor_model.py <-> risk.py is acyclic (factor_model.py imports only stdlib); schemas/return_basis.py imports only typing+pydantic.

risks:
  - definition_of_done requires run_all_tests.py green, but non_goals forbid touching app/tests/ where 3 of the 4 failures live and the 4th needs an out-of-scope doc file. Reported PARTIAL: the source relocation is complete and behaviour-neutral; every failing test is an out-of-lane retarget the 02 plan assigns downstream.
  - Ported the ReturnBasis explanatory comment from risk.py lines 51-61 (02 said "L52-61"); L51 was the leading blank and L52-61 the comment text — the full comment moved, nothing dropped.
  - 02 § Docs edit list omits .claude/skills/write-story/SKILL.md; adding analytics/factor_model.py made test_docs_paths.py fail. The docs lane must fold this into T-43.2.4.
