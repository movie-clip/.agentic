REPORT 2026-09-14-tech-debt-f6-ridge-docstrings/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only recon order; no verification command named

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - shipped ridge penalty: `ROLLING_RIDGE_FLOOR = {20: 1e-5, 60: 1e-5, 252: 1e-5}` at `services/quant-engine/app/analytics/factor_model.py:81` — uniform 1e-5 across all three windows, not window-proportional.
  - shipped minimum-observation threshold: `WINDOW_MIN_OBSERVATIONS = {20: 25, 60: 75, 252: 275}` at `services/quant-engine/app/analytics/risk.py:83` — this is a history-length gate, not the regression's observation count.
  - shipped regression window size: `services/quant-engine/app/analytics/risk.py:1650-1658` (`_build_rolling_factor_loadings`) slices exactly `window` observations (`start = index - window + 1`, `y_window = y[start:index+1]`) once `index + 1 >= min_observations`; for the 20d window this is always 20 observations, never 25.
  - shipped residual degrees of freedom for the 20d window: 20 observations fit against 17 parameters (16 factors + intercept, `factor_model.py:53-70` defines the 16, `factor_model.py:136-138 fit_factor_model`/`_least_squares` build the design matrix `[1, F*_1..F*_K]`) → 3 residual df. No code computes or stores a `df` value directly; this is arithmetic over the two cited quantities, not a shipped field.
  - `test_analytics.py:7844-7849` docstring (`test_rolling_factor_loadings_market_beta_in_range`) — full text: "Pre-fix, global Gram-Schmidt + ridge_lambda=1e-5 produced Market loadings as extreme as -4.60 on the 20d window (25 obs, 17 params → 8 df, near-singular). Per-window Gram-Schmidt + ridge floor λ=0.01 must prevent this blowup." — the "25 obs...8 df" claim is at line 7847, the "ridge floor λ=0.01" claim is at line 7848.
  - `test_analytics.py:7900-7907` docstring (`test_rolling_factor_loadings_20d_no_blowup`) — full text: "With 25 min-observations and 16 factors, the pre-fix OLS condition number was dangerously high (n/K ≈ 1.56) and ridge_lambda=1e-5 provided no real regularisation. The window-proportional ridge floor (λ=0.01 for the 20d window) must cap every coefficient within a plausible range." — the "window-proportional ridge floor (λ=0.01...)" claim spans lines 7905-7906; line 7907 is the closing `"""` only.
  - the order's citation of `test_analytics.py:7848` for the first docstring is one line short of the full claim — the "25 obs, 17 params → 8 df" wording is at line 7847, immediately above; both lines belong to the same docstring and both need correction.
  - the order's citation of `test_analytics.py:7905-7907` for the second docstring is correct as a containing range; the load-bearing sentence itself is lines 7905-7906.
  - F6 claim "docstrings describe a 20d window (25 obs, 17 params → 8 df)" — CONFIRMED verbatim at `test_analytics.py:7847`.
  - F6 claim "and a window-proportional ridge floor (λ=0.01 for the 20d window) that were never shipped" — CONFIRMED: shipped `ROLLING_RIDGE_FLOOR` is uniform 1e-5, not window-proportional and not 0.01 anywhere in `factor_model.py:81`.
  - F6 claim "ROLLING_RIDGE_FLOOR (factor_model.py:81) is 1e-5 for every window" — CONFIRMED exactly at that line.
  - F6 claim "the 20d window is 20 obs / 3 df" — CONFIRMED: the regression always fits exactly `window` (20) observations against 17 params, per `risk.py:1650-1658`; 20 − 17 = 3.
  - other file repeating the same misleading language: `services/quant-engine/app/analytics/risk.py:1636` docstring for `_build_rolling_factor_loadings` reads "Fits ridge OLS with a window-proportional floor (see ROLLING_RIDGE_FLOOR)" — this is source-code prose, in scope (`analytics/**`), that repeats the "window-proportional" characterization the shipped uniform-1e-5 value contradicts; it names no numeric λ so does not repeat the 0.01 figure specifically.
  - `test_analytics.py:8032` inline comment "ridge floor shrinks ~0.5%" (in `test_rolling_loadings_null_exactly_collinear_factor_and_fit_the_rest`) makes no explicit λ or window-size claim and is not contradicted by the shipped code; not in scope of F6's three claim types (penalty value, observation threshold, degrees of freedom) but flagged since it is ridge-floor-adjacent prose in the same file.
  - `docs/finance/financial-methodology.md:1207-1231` §Per-window orthogonalization already states the corrected facts: "Ridge floor: λ = 1e-5 for all windows" (line 1212), and an explicit "Edge cases" note (lines 1223-1231) stating the estimation window always holds exactly `w` observations, that for w=20 this is "20 observations against 17 parameters, i.e. 3 residual degrees of freedom, not the 25-observations/8-df reading an earlier draft implied" — this confirms the register's statement that this run's methodology-doc correction already landed; the test docstrings are the one remaining uncorrected location for the same two claims.

risks:
  - `services/quant-engine/app/analytics/risk.py:1636` was not named in the work order's scope of docstrings-to-correct but repeats the same "window-proportional floor" mischaracterization found in the two test docstrings; flagged in `handoff` for the orchestrator to route to a later build order if it decides the fix should extend there.
  - no other file under the three scoped paths (`docs/**`, `services/quant-engine/app/analytics/**`, `test_analytics.py`) was found stating the 25-obs/17-params/8-df figure, the λ=0.01 figure, or a residual-df figure for the 20d window, beyond the locations listed above; absence confirmed by exact-string and figure grep across the scoped paths.
