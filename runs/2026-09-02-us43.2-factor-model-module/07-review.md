REPORT 2026-09-02-us43.2-factor-model-module/07
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd C:\projects\investments\portfolio && python scripts/run_all_tests.py
  result:    PASS
  detail:    run_all_tests.py exit 0, "All tests passed." — desktop vitest 359 passed, tsc --noEmit green, dead-code strict (ruff/vulture/knip) clean, backend pytest green, golden regen reported no drift. git diff --exit-code apps/desktop/src/test/dashboardGoldens.ts clean. AC1(amended)-AC6 each traced to file:line; both new pin tests pass; the two monkeypatch-retarget branch tests stay green.

contract_notes:
  - docs/finance/financial-methodology.md §Statistical Factor Model still credits risk.py for the moved factor symbols; re-point to analytics/factor_model.py — T-43.2.4, not a review blocker.
  - docs/architecture/system-architecture.md analytics module inventory has no analytics/factor_model.py row — T-43.2.4, not a review blocker.
  - Story file US-43.2 still says Status: Backlog and its Notes omit the AC1/AC3/AC5 records — T-43.2.4 close-out owns this, not a review blocker.

pack_corrections:
  - none

handoff:
  - Acceptance gate PASS — close-out proceeds to docs lane T-43.2.4, then the human runs the suite and commits.

risks:
  - AC1 graded against the amended symbol list in 02 § Cycle decision per the work order DoD; as-built matches it exactly. Human-approved at plan time — acceptable-as-built, not a deviation.
  - AC5's literal "test_analytics.py:17-18 imports updated" is a mis-statement; nothing on L17-19 moved. test_attribution.py L416/L426 also needed retargeting and got it. Substance satisfied; wording gap acceptable-as-built.
  - AC3's literal "No module imports a `_`-prefixed name from risk.py" holds only for factor-model symbols; see next bullet.
  - Pre-existing non-factor private imports from risk.py remain (_build_wealth_index, _build_drawdown_from_return_index, _portfolio_time_weighted_return_series, plus test-only imports); the other five risk.py concerns are an explicit tracked follow-up, out of this slice.
  - AC3 linalg disposition is recorded in 03-backend.md handoff and the factor_model.py docstring, not yet the story file; the DoD accepts that and T-43.2.4 folds it into Notes.

---

## Orchestrator brief

Acceptance gate over US-43.2 (extract factor-model internals from risk.py).
**Verdict: PASS** — AC1 (as amended), AC2-AC6 and test-plan delivery all
satisfied; full mechanical suite re-run (exit 0). No change requests.

- AC1 (amended, human-approved): factor_model.py defines all 12 amended symbols; risk.py imports 7 back; no factor def left in risk.py.
- AC2: ReturnBasis Literal in schemas/return_basis.py, 3 consumers re-point, pin test green.
- AC3: consumers re-pointed, linalg trio moved and exclusive to factor_model.py, no factor private leak.
- AC4: suite green, goldens byte-identical, dashboardGoldens.ts diff empty (re-ran myself).
- AC5: monkeypatches retargeted, patch-bite proven by degenerate-window tests, identity pin green.
- AC6: dead-code gate + tsc clean.
- Sections below: Findings by acceptance criterion (per-AC evidence); Amendment sign-off (per DoD).

---

## Findings by acceptance criterion

### AC1 (amended) — SATISFIED

`services/quant-engine/app/analytics/factor_model.py` exists (untracked new leaf,
imports only `{__future__, dataclasses}`) and defines, verbatim per 05's
char-diff (PASS):

| Symbol | factor_model.py |
|---|---|
| `UcitsCandidateMapping` | L21-33 |
| `FactorDefinition` | L37-50 |
| `DEFAULT_FACTOR_DEFINITIONS` (16 tuples) | L53-70 |
| `FACTOR_PROXY_MAP` / `FACTOR_KEY_MAP` | L73-74 |
| `ROLLING_RIDGE_FLOOR` `{20:1e-5,60:1e-5,252:1e-5}` | L81 |
| `ORTHOGONALIZATION_ZERO_RESIDUAL_THRESHOLD` `1e-12` | L90 |
| `orthogonalize_factors_window` | L93-133 |
| `fit_factor_model` | L136-145 |
| `_least_squares` / `_solve_linear_system` / `_dot` | L148-181 |

`risk.py:9-17` imports back 7 names (`DEFAULT_FACTOR_DEFINITIONS`,
`FACTOR_PROXY_MAP`, `FactorDefinition`, `ROLLING_RIDGE_FLOOR`,
`UcitsCandidateMapping`, `fit_factor_model`, `orthogonalize_factors_window`).
`FACTOR_KEY_MAP` is correctly not re-imported — grep confirms zero risk.py
consumers, and ruff F401 (green) would flag it. No factor-model `def` / `class`
remains in `risk.py` (grep for each symbol: only `FACTOR_BY_LABEL` at L79, which
stays and is re-derived from the imported tuple).
`selected_history_return_series` stays at `risk.py:811`, renamed public — per the
02 § Cycle decision amendment the work order instructs me to grade against.

### AC2 — SATISFIED

`schemas/return_basis.py:28` —
`ReturnBasis = Literal["portfolio_value", "market_value", "market_value_trade_neutral"]`,
placed after the Literal family with risk.py's explanatory comment ported (L18-27).
Imported from there by `risk.py:59`, `attribution.py:44`,
`services/diagnostics_engine.py:39`. `factor_model.py` does not import it (n/a per
DoD). `schemas/reconciliation.py:569` is a prose comment only. No `types.ts` /
`docs/contracts` mirror owed — it is a parameter annotation, never a serialized
field; `dashboardGoldens.ts` diff empty confirms. AC2 pin test
`test_return_basis_literal_lives_in_schemas_and_is_shared_by_reference`
(test_analytics.py:8001) asserts the three members via `typing.get_args` and
single-object identity across `risk` / `attribution` / `diagnostics_engine` —
passes.

### AC3 — SATISFIED (factor-model scope)

- `analytics/attribution.py:28-34` — factor symbols from
  `app.analytics.factor_model`; `selected_history_return_series` (public) from
  `risk.py:36`. Zero `_`-prefixed cross-seam import remains.
- `services/attribution_engine.py:21`, `services/stress_engine.py:18`,
  `services/diagnostics_engine.py:4` — `FACTOR_PROXY_MAP` from
  `app.analytics.factor_model`. `stress_engine.py:19-23` keeps `STRESS_SCENARIOS`
  / `build_statistical_factor_model` / `build_stress_scenarios` from `risk.py`
  (entry points legitimately owned there).
- Linalg trio: grep over `app/` finds `_least_squares` / `_solve_linear_system` /
  `_dot` only in `factor_model.py` — moved, no non-factor caller, not re-imported
  by `risk.py`. Disposition recorded in 03-backend.md handoff + the
  `factor_model.py` module docstring.
- Falsifying observation for "no factor-model private leak": a grep for
  `_fit_factor_model` / `_orthogonalize_factors_window` /
  `_selected_history_return_series` across `services/quant-engine` returns only
  the unrelated test-function name
  `test_orthogonalize_factors_window_reports_dropped_duplicate`. The leak is
  closed.

### AC4 — SATISFIED

Re-ran `python scripts/run_all_tests.py` myself: exit 0, final line
"All tests passed." Golden regeneration step ran and reported no drift; desktop
vitest 40 files / 359 passed; `tsc --noEmit` green; dead-code strict clean.
`git diff --exit-code apps/desktop/src/test/dashboardGoldens.ts` → exit 0, empty.
`git diff --stat` touches exactly the DoD's file set (9 tracked + the untracked
`factor_model.py`); no stray files, no US-43.1 / Epic 43 drift in the tree.

### AC5 — SATISFIED in substance

- `test_analytics.py:7915` `real_fit = risk_module.fit_factor_model`; `:7925`
  `monkeypatch.setattr(risk_module, "fit_factor_model", nan_first_fit)`; `:7993`
  `risk_module.orthogonalize_factors_window(...)` — all retargeted.
- `test_attribution.py:416` `real_fit = attr_mod.fit_factor_model`; `:426`
  `monkeypatch.setattr(attr_mod, "fit_factor_model", fake_fit)` — retargeted.
- `risk.py:1657-1658` (`_build_rolling_factor_loadings`) calls the bare imported
  names `orthogonalize_factors_window` / `fit_factor_model`, resolved against
  `risk`'s module globals at call time, so the `risk_module` patch bites.
- Falsifying observation: if the call site were module-qualified
  (`factor_model.fit_factor_model`), `test_rolling_factor_loadings_never_emit_nonfinite_values`
  would fail its `points[19].market is None` assertion (the simulated degenerate
  window). It passes — the patched path is genuinely exercised. Same logic for
  `test_attribution.py::test_nonfinite_window_skipped_and_response_is_json_safe`
  (green).
- AC5 identity pin `test_factor_model_fit_symbols_are_shared_by_reference_across_the_seam`
  (test_analytics.py:8024): `risk_module.fit_factor_model is
  factor_model.fit_factor_model`, same for `orthogonalize_factors_window`, plus
  `attribution.fit_factor_model` — passes.
- `test_analytics.py:15` moves `DEFAULT_FACTOR_DEFINITIONS` to
  `from app.analytics.factor_model import ...`, fixing its ~23 downstream use
  sites in one edit. L5298 / L7908 `monkeypatch.setattr(risk_module,
  "DEFAULT_FACTOR_DEFINITIONS", ...)` left unchanged — correct, `risk.py` holds it
  as a re-imported module global read live by `_build_rolling_factor_loadings`.

### AC6 — SATISFIED

Dead-code strict gate in the suite: ruff clean, vulture clean, knip clean,
"STRICT: no dead-code findings". `tsc --noEmit` green. No orphaned import in
`risk.py` (ruff F401 would flag `FACTOR_KEY_MAP` — deliberately not re-imported).

### Test plan delivery — SATISFIED

Two new tests exist, pin what they claim, and pass (verified by direct node-id
run): the AC2 literal-and-shared test and the AC5 identity test above. Regression
blocks — `test_attribution.py`, `test_stress_engine.py`, and the factor-model /
factor-shift / model-reliability / rolling-factor-loadings blocks of
`test_analytics.py` — pass unchanged in substance (05 and 06 both confirmed the
assertions are intact, not merely passing; re-run of the four retargeted tests +
the two new tests: 6 passed).

### Trust-state spot checks — SATISFIED

`ReturnBasis` Literal moved with all three members in original order.
`apply_return_basis_status_to_factor_model` /
`apply_return_basis_status_to_model_reliability` /
`_degrade_status_for_unverified_return_basis` unchanged and still in `risk.py`
(05 Item 5). No new market-data caller (verbatim relocation adds no FMP call). No
schema field added or nullability changed, so no badge / dash rendering is
affected.

---

## Amendment sign-off (per DoD)

AC1's amendment and AC5's wording gap are **acceptable-as-built** — both were
human-approved at plan time (02 § Cycle decision; 02 § Test edit list #6-8; the
work order DoD names AC1 "AMENDED — human-approved"). They are not deviations.
The AC1 amendment (selected_history_return_series stays in risk.py renamed
public; `UcitsCandidateMapping` + `ORTHOGONALIZATION_ZERO_RESIDUAL_THRESHOLD`
added to the move; linalg trio moved) is implemented exactly as the plan
specifies. The AC5 wording ("test_analytics.py:17-18 imports updated") describes
an edit that was correctly not made because nothing on those lines moved.
