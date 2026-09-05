REPORT 2026-09-02-us43.2-factor-model-module/05
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd C:\projects\investments\portfolio && python scripts/run_all_tests.py
  result:    PASS
  detail:    "All tests passed." — golden regen reported no drift; backend pytest green; desktop vitest green; tsc --noEmit green; dead-code strict (ruff+vulture+knip) clean. Targeted re-run: test_attribution.py + test_stress_engine.py 23 passed; test_analytics.py factor-model/orthogonal/reliability/rolling/return-basis/seam selection 33 passed, 0 skipped.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Integration gate may proceed — the financial gate is PASS; the relocation is proven byte-for-byte behaviour-neutral.
  - Checklist miscount (non-blocking): DoD item 1 says "all 17 tuples" for DEFAULT_FACTOR_DEFINITIONS; actual count is 16, identical in anchor and moved file.

risks:
  - anchor = git blob 6b63ae1 risk.py (HEAD). Per gates.md §2 the prior committed source blob is the correct independent reference for a verbatim-relocation audit.
  - Secondary anchor: pre-existing test_rolling_factor_loadings_matches_published_statsmodels_capm_checkpoints passes unchanged, corroborating the ridge-OLS fit math is preserved.
  - I did not re-review whether the pre-existing factor-model methodology is itself correct — out of scope per the order's non_goals; no reason arose to suspect it.

---

## Orchestrator brief

- Verdict: **PASS**. The US-43.2 factor-model relocation is byte-for-byte behaviour-neutral.
- Anchor: git blob `6b63ae1` `risk.py` (HEAD). Method: programmatic char-diff of each moved span against the anchor; `factor_model.py` is untracked so read from the working tree.
- Item 1 (verbatim char-diff): PASS. All 11 moved regions char-identical to the anchor. The ONLY deltas are the two permitted `def`-name underscore drops (`_fit_factor_model`→`fit_factor_model`, `_orthogonalize_factors_window`→`orthogonalize_factors_window`) plus the new module docstring + `from __future__` / `from dataclasses` import block. No reordered dict, no touched literal, no whitespace cleanup. Ridge floor `{20:1e-5,60:1e-5,252:1e-5}`, threshold `1e-12`, all 16 factor tuples with `orthogonalization_order` 1..16, every proxy string — identical.
- Item 6: PASS. `selected_history_return_series` (renamed from `_selected_history_return_series`) body and `_series_to_returns` body char-identical to anchor; only the one `def`-name change.
- Item 2: PASS. `run_all_tests.py` green incl. golden regen reporting no drift.
- Item 3: PASS. `git diff --exit-code apps/desktop/src/test/dashboardGoldens.ts` clean (exit 0).
- Item 4: PASS in substance. Factor-model / factor-shift / model-reliability / rolling-factor-loadings blocks + `test_orthogonalize_factors_window_reports_dropped_duplicate` + all `test_attribution.py` + all `test_stress_engine.py` pass with their assertions intact (r²=SSE/SST pin, statsmodels-CAPM checkpoint pin, collinear-drop pin, min-shared-history pin, 2 new seam-identity pins).
- Item 5 (trust honesty): PASS. `apply_return_basis_status_to_factor_model` (risk.py:954), `apply_return_basis_status_to_model_reliability` (risk.py:940), `_degrade_status_for_unverified_return_basis` (risk.py:773) unchanged and still in risk.py. `ReturnBasis` Literal = exact same three members, same order, now in `schemas/return_basis.py` with its explanatory comment ported verbatim. No rung collapsed, reclassified, or fabricated.
- RESEARCH-skip conditions (02 § RESEARCH ruling) — all three discharged, see § RESEARCH-skip discharge. RESEARCH stays correctly skipped.
- Sections below: Evidence log (per-span diff results + boundary checks); RESEARCH-skip discharge; Scope of consumer-module diffs.

---

## Evidence log

### Anchor

`git show 6b63ae1811745ae46ae8003593eb00283261e922:services/quant-engine/app/analytics/risk.py`
(2295 lines; commit `6b63ae1` "US-43.1", current HEAD). `analytics/factor_model.py` is
untracked — read from the working tree. Each moved span was sliced from the anchor by
symbol boundary (boundaries verified line-by-line) and compared character-for-character
against the corresponding block in `factor_model.py`, after applying the two permitted
`def`-name substitutions to the anchor text.

### Per-span result (Item 1)

| Moved symbol | Anchor span (risk.py) | factor_model.py | Result |
|---|---|---|---|
| `UcitsCandidateMapping` | 65–77 | 21–33 | char-identical |
| `FactorDefinition` | 97–110 | 37–50 | char-identical |
| `DEFAULT_FACTOR_DEFINITIONS` (16 tuples, order 1..16, all proxy strings) | 113–130 | 53–70 | char-identical |
| `FACTOR_PROXY_MAP` / `FACTOR_KEY_MAP` | 132–133 | 73–74 | char-identical |
| `ROLLING_RIDGE_FLOOR` `{20:1e-5,60:1e-5,252:1e-5}` + comment | 139–143 | 77–81 | char-identical |
| `ORTHOGONALIZATION_ZERO_RESIDUAL_THRESHOLD` `= 1e-12` + comment | 1689–1695 | 84–90 | char-identical |
| `orthogonalize_factors_window` (was `_orthogonalize_factors_window`) | 1698–1738 | 93–133 | char-identical modulo permitted `def`-name drop |
| `fit_factor_model` (was `_fit_factor_model`) | 1741–1750 | 136–145 | char-identical modulo permitted `def`-name drop |
| `_least_squares` | 2211–2220 | 148–157 | char-identical |
| `_solve_linear_system` | 2223–2240 | 160–177 | char-identical |
| `_dot` | 2243–2244 | 180–181 | char-identical |

No other character delta in any span. The `factor_model.py` module docstring +
`from __future__ import annotations` + `from dataclasses import dataclass` are new to
the file and are the permitted "new to the file" additions named in the DoD.

### Item 6 — the rename that stays in risk.py

`git diff risk.py` shows for `selected_history_return_series`: only the `def` line
changed (`_selected_history_return_series` → `selected_history_return_series`); the two
body lines (`series = select_history_price_series(rows)` /
`return _series_to_returns(series.points)`) are context-unchanged. Its 4 internal call
sites (build_statistical_factor_model, _benchmark_return_series,
_build_factor_risk_contributions, _build_position_risk_contributions) are renamed only.
`_series_to_returns` (anchor 2247–2255) does not appear as changed in the diff — body
char-identical.

### Items 2–4 — behaviour

- `run_all_tests.py`: "All tests passed." Golden regeneration step ran and reported no
  drift. Dead-code strict gate clean.
- `git diff --exit-code apps/desktop/src/test/dashboardGoldens.ts` → exit 0, empty.
- Targeted substance re-run: `test_attribution.py` + `test_stress_engine.py` → 23 passed;
  `test_analytics.py` factor/orthogonal/reliability/rolling/return-basis/seam selection →
  33 passed, 0 skipped, 0 xfail. Assertion-bearing tests confirmed still exercising real
  checks: `test_statistical_factor_model_r_squared_matches_sse_over_sst_formula`,
  `test_rolling_factor_loadings_matches_published_statsmodels_capm_checkpoints`
  (published-reference anchor), `test_growth_loading_is_unit_when_portfolio_matches_growth_factor_returns`
  (degenerate anchor), `test_factor_model_minimum_shared_history_is_pinned`,
  `test_orthogonalize_factors_window_reports_dropped_duplicate` (asserts
  `dropped == ["Growth"]`), plus the 2 new seam pins.

### Item 5 — trust classification

Working-tree `risk.py` still defines, unchanged (no diff hunk within these ranges):
`_degrade_status_for_unverified_return_basis` (L773),
`apply_return_basis_status_to_model_reliability` (L940),
`apply_return_basis_status_to_factor_model` (L954).
`schemas/return_basis.py` diff: adds `ReturnBasis = Literal["portfolio_value",
"market_value", "market_value_trade_neutral"]` after the Literal family, with risk.py's
L52–63 explanatory comment ported verbatim. Members and order identical to anchor L62.
New test `test_return_basis_literal_lives_in_schemas_and_is_shared_by_reference` pins
`typing.get_args(ReturnBasis) == ("portfolio_value", "market_value",
"market_value_trade_neutral")` and identity across `risk`, `attribution`,
`diagnostics_engine`. No rung collapsed / reclassified / fabricated by the move.

---

## RESEARCH-skip discharge

02 § RESEARCH ruling made the skip conditional on three things being false. Result of
the char-diff:

1. **Non-mechanical change in any moved span?** No. Every span is char-identical modulo
   the two explicitly permitted `def`-name underscore drops and the new module
   docstring/import header. Condition 1 not triggered.
2. **Any methodology-doc formula *description* would need to change?** No. Only
   implementation-location strings ("implemented in `risk.py`" → `analytics/factor_model.py`)
   are affected — that is T-43.2.4 doc re-pointing, explicitly the permitted case.
   Condition 2 not triggered.
3. **Any moved function needed a body or signature change to relocate?** No. All bodies
   byte-identical; internal references (`_least_squares`, `_dot`,
   `ORTHOGONALIZATION_ZERO_RESIDUAL_THRESHOLD`) resolve within `factor_model.py`
   unchanged. Dropping a leading underscore from two `def` names is a rename, not a
   signature or behaviour change. Condition 3 not triggered.

RESEARCH mode stays correctly skipped for this slice.

---

## Scope of consumer-module diffs

`git diff` on the four rewired consumers shows import re-pointing + call-site renames
only, no logic change:

- `analytics/attribution.py` — factor symbols now from `app.analytics.factor_model`;
  `selected_history_return_series` from `app.analytics.risk`; `ReturnBasis` from
  `app.schemas.return_basis`; 3 call sites renamed (L130, L198, L205). `FACTOR_KEY_MAP`
  still imported (from factor_model).
- `services/stress_engine.py` — `FACTOR_PROXY_MAP` from `app.analytics.factor_model`;
  `STRESS_SCENARIOS` / `build_*` still from `app.analytics.risk`.
- `services/attribution_engine.py` — `FACTOR_PROXY_MAP` import re-pointed.
- `services/diagnostics_engine.py` — `FACTOR_PROXY_MAP` re-pointed; `ReturnBasis` moved
  to the existing `from app.schemas.return_basis import ...` line.

Import-ordering aesthetics (the new `factor_model` line sits above the `risk` line in
three services, not alphabetically) are for the integration gate, not this one; the
dead-code / ruff gate is green.
