REPORT 2026-09-12-rolling-factor-audit/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order verification field was NONE (read-only recon)

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - quant-audit lane's shortest path: financial-methodology.md § Statistical Factor Model → factor_model.py → risk.py::_build_rolling_factor_loadings (risk.py:1629) → test_analytics.py golden tests.
  - route feeding the chart is POST /engines/diagnostics/run(-imported) (app/api/routes/diagnostics.py), not exposure.py, despite the data surfacing through ExposureAnalysis client-side.
  - schema of record is StatisticalFactorModel in services/quant-engine/app/schemas/reconciliation.py:488, embedded in DiagnosticsResult (schemas/diagnostics.py:164).

risks:
  - Exact construction of `daily_states` / `factor_histories` / `y` (the portfolio return series regressed against factor proxies) inside `diagnostics_engine.py` was not traced line-by-line in this pass — needed for a full audit of return-basis correctness feeding the regression.
  - The full status-string enum for `StatisticalFactorModel.status` / `window.status` (all values `_degrade_status_for_unverified_return_basis` can produce) was not enumerated; only observed via test assertions (`ok`, `insufficient_history`, `unavailable`, and an implied `degraded_unverified_return_basis`-shaped string). A quant-audit lane should read `_degrade_status_for_unverified_return_basis` directly (not opened in this pass).
  - No route-level (`test_routes.py`) test was confirmed to assert on `statistical_factor_model` passthrough for `/engines/diagnostics/run`; coverage may rely entirely on the analytics-layer tests plus end-to-end desktop smoke tests not reviewed here.
  - `RollingFactorLoadingPoint` schema fields were inferred from usage (`date`, per-factor keys, `alpha`, `r_squared`, `residual_vol`) rather than read directly from its class definition in `reconciliation.py`; the exact field list/types were not opened.

## Orchestrator brief

- Chart lives in `RollingFactorLoadingsCard.tsx`, rendered on Dashboard via `DashboardPanel.tsx`; confirmed by `docs/contracts/dashboard-fields.md:248`.
- Data path: `POST /engines/diagnostics/run(-imported)` (`diagnostics.py`) → `diagnostics_engine.py` → `risk.py::build_statistical_factor_model` (calls `analytics/factor_model.py`) → merged client-side into `ExposureAnalysis` by `composeExposureView` → adapted by `buildExposureFactorModel` → `factorModel` prop.
- Formula: per-window Gram-Schmidt orthogonalized, ridge-stabilized OLS (λ=1e-5), 16 US-ETF-proxy factors, windows 20/60/252 trading days — documented verbatim in `financial-methodology.md` § Statistical Factor Model. Not Fama-French, not CAPM.
- Truth class: **Synthetic History**, explicit in methodology (`financial-methodology.md:1249-1251`).
- Trust/degrade path: `apply_return_basis_status_to_factor_model` (`risk.py:954`) degrades `status` when return-basis isn't `verified_adjusted_close`.
- Sections below, in order: **Frontend**, **Backend route and services**, **Formula**, **Schemas and contracts**, **Truth class and trust handling**, **Tests**, **Known limitations**, **Risk detail**.
- Nothing blocks dispatch; shortest audit path: `financial-methodology.md` §Statistical Factor Model → `factor_model.py` → `risk.py::_build_rolling_factor_loadings` (line 1629) → `test_analytics.py` golden tests.

---

## Frontend

- `apps/desktop/src/features/portfolio/RollingFactorLoadingsCard.tsx` (full file, 349 lines) — the chart component. Header label "Rolling Factor Analysis" at line 259. Reads `factorModel.statistical_factor_model.rolling_loadings_{20,60,252}d` via `getRollingLoadingsSeries` (lines 98-102), window toggle state (line 194, `ROLLING_WINDOW_OPTIONS = [20, 60, 252]` line 11), renders a Recharts `LineChart` with a `Brush` for zoom (lines 277-317).
- Mounted from `apps/desktop/src/features/portfolio/DashboardPanel.tsx:134` — `<RollingFactorLoadingsCard result={exposureResult} factorModel={factorModel} />`; `factorModel` prop typed `ExposureFactorModelResponse | null` (`DashboardPanel.tsx:37`).
- `factorModel` is threaded from `apps/desktop/src/app/App.tsx:493` and `:578` via `buildExposureFactorModel(exposureView)`, then `App.tsx:869` passes `dashboardSession.factorModel` into `DashboardPanel`.
- `apps/desktop/src/features/portfolio/portfolioAnalysisAdapter.ts:508` — `buildExposureFactorModel()` reshapes `ExposureAnalysis` (benchmark, factor_methodology, factor_registry, statistical_factor_model) into `ExposureFactorModelResponse`.
- `portfolioAnalysisAdapter.ts:233` — `composeExposureView(exposure, diagnostics)` — line ~259 sets `statistical_factor_model: diagnostics.statistical_factor_model`, i.e. the rolling-loadings data originates from the **diagnostics** engine response, not the exposure engine response, even though it is surfaced through `ExposureAnalysis`.
- The same underlying data (`buildExposureFactorModel`) is also consumed by `FactorDriftSummaryCard.tsx:200` (Exposure tab's "Factor Loading Drift" card) — a distinct card computing drift/summary stats over the same series; out of scope per non_goals but worth knowing it's the same source data, different presentation.
- Also worth distinguishing: `RollingCorrelationChart.tsx` (Exposure tab, benchmark/portfolio correlation) is a **different** chart/data path from this factor-loadings chart — do not conflate the two "rolling" charts.

## Backend route and services

- Route: `services/quant-engine/app/api/routes/diagnostics.py` — `POST /engines/diagnostics/run` and `/run-imported` (lines 11-24), `response_model=DiagnosticsResult`, delegating to `app/services/diagnostics_engine.py::run_diagnostics_engine` / `run_imported_diagnostics_engine`.
- `services/quant-engine/app/services/diagnostics_engine.py:341-343` — computes `statistical_factor_model = build_statistical_factor_model(daily_states, factor_histories, benchmark_symbol, return_basis=return_basis)`, then immediately degrades it via `apply_return_basis_status_to_factor_model(...)` (line 342).
- `services/quant-engine/app/analytics/risk.py` — the response-shaping layer:
  - `_build_rolling_factor_loadings` (lines 1629-1679) — the actual per-date rolling regression loop (see Formula section).
  - `build_statistical_factor_model` (around lines 1330-1381, confirmed by callers at 1356-1369) orchestrates the three window calls and `_build_current_factor_snapshot`/`_build_window_summaries`.
  - `apply_return_basis_status_to_factor_model` (lines 954-969) — trust/return-basis degrade logic.
  - `factor_model_methodology()` (line 1381) returns the methodology string surfaced to the UI/contract as `factor_methodology`.
- `services/quant-engine/app/analytics/factor_model.py` (full file, 182 lines) — factor vocabulary (`DEFAULT_FACTOR_DEFINITIONS`, 16 factors: market/growth/value/small_cap/technology/financials/health_care/energy/industrials/consumer_staples/utilities/consumer_discretionary/rates_ief/rates_tlt/credit/commodities), `ROLLING_RIDGE_FLOOR = {20: 1e-5, 60: 1e-5, 252: 1e-5}` (line 81), `orthogonalize_factors_window` (lines 93-133, per-window Gram-Schmidt with exact-collinearity drop), `fit_factor_model` (lines 136-145, ridge OLS + R²), `_least_squares`/`_solve_linear_system`/`_dot` linear-algebra primitives. Module docstring (lines 1-14) states this was extracted verbatim from `risk.py` in US-43.2 and is behaviour-neutral.

## Formula

Documented in `financial-methodology.md` § "Statistical Factor Model" / "Per-window orthogonalization", lines 1159-1254.

- Model: "Orthogonalized rolling ridge factor model using US ETF proxies for market, style, sector, and macro exposures; UCITS symbols shown separately as EU execution examples" (exact string at `financial-methodology.md:1166`, matches `risk.py:1381`).
- Not Fama-French/CAPM in the textbook sense — a custom 16-factor model with a fixed orthogonalization order (market=1, growth=2, value=3, small_cap=4, technology=5, financials=6, ... credit=15, commodities=16).
- Windows: 20, 60, 252 trading days (all three computed and shipped simultaneously; UI lets user pick which to view).
- Per date t, window w=[t−w+1,t]: (1) slice raw ETF-proxy daily returns to the window; (2) Gram-Schmidt orthogonalize within the window only (not full history) in the fixed order; (3) ridge OLS `β = (X'X + λ·D)⁻¹X'y`, `D=diag(0,1,1,...,1)`, `λ=1e-5` for all windows (`ROLLING_RIDGE_FLOOR`); (4) reported loading for factor k = β_{k+1}, interpreted as sensitivity to the orthogonalized/residual factor after controlling for higher-priority factors.
- Return basis: portfolio daily returns `y` regressed against factor proxy returns; exact source series construction is in `diagnostics_engine.py` (`daily_states`, `factor_histories`) — not fully traced in this recon pass (see Risk detail).
- Edge cases documented (`financial-methodology.md:1223-1234`): windows below `WINDOW_MIN_OBSERVATIONS[w]` → null, not partial-fill; exactly-collinear factor → coefficient null for that date, not propagated; non-finite (NaN/inf) OLS solve → null, never NaN (US-21.3); in-sample R² is diagnostic-only, not out-of-sample predictive power.
- Methodology doc also carries an explicit "Sector exposure vs. factor loading — why they can diverge" section (lines 1255-1314) specifically warning against misreading a negative sector factor loading (e.g., Technology) as a short position — directly relevant to auditing chart interpretation, not just computation.
- Academic precedent cited: Fama & French (1993), Connor & Korajczyk (1988), Bai & Ng (2002), Grinold & Kahn (2000), Barra/MSCI factor docs.

## Schemas and contracts

- `services/quant-engine/app/schemas/reconciliation.py:488-494` — `class StatisticalFactorModel(BaseModel)` carrying `rolling_loadings_20d/60d/252d: list[RollingFactorLoadingPoint]`, `windows`, `current_factor_snapshot`, `collinearity_diagnostics`, `insufficient_history`, `status`, `benchmark_symbol` (full field list not exhaustively read; the three rolling-loadings lists and `status` confirmed).
- `services/quant-engine/app/schemas/diagnostics.py:145-166` — `class DiagnosticsResult(BaseModel)` includes `factor_registry: list[FactorProxyDefinition]`, `factor_methodology: str | None`, `statistical_factor_model: StatisticalFactorModel` (line 164) — this is the top-level response schema for the `/engines/diagnostics/run` route.
- TypeScript mirror: `apps/desktop/src/features/portfolio/types.ts` — `StatisticalFactorModel` type (lines 792-887, including the three `rolling_loadings_*d` arrays with per-factor-key fields, `alpha`, `r_squared`, `residual_vol`), and `ExposureFactorModelResponse` (lines 1463-1497) — the shape actually consumed by the card.
- Contract doc: `docs/contracts/dashboard-fields.md:248` — row for "Rolling Factor Analysis" naming `RollingFactorLoadingsCard.tsx`, its inputs (`exposureResult`, `factorModel`), classifying it `engine-derived`, synthetic-history basis, and noting it is its own top-level summary card (unaffected by the Epic 25 composition-card work referenced nearby).
- Contract doc: `docs/contracts/exposure-fields.md:284` — separate row for "Rolling Factor Loadings section label" (helper copy in `ExposurePanel.tsx`), `unavailable-required` trust class, explicitly warning it "must read as historical rolling diagnostics, not current-state exposure" and that "scenario edits must not imply rerun rolling-history analytics" — this is the Exposure-tab presentation of the same underlying data, distinct from the Dashboard card in scope here.
- No entry found in `docs/contracts/factor-drift-fields.md` specific to the rolling-loadings raw series itself (that contract doc appears to cover the derived `FactorDriftSummaryCard`, out of scope).

## Truth class and trust handling

- Truth class: **Synthetic History** — explicit in `financial-methodology.md:1249-1251`: "rolling window coefficients are in-sample regression coefficients; they carry synthetic-history trust class (not verified), because they apply current holdings weights to historical price data."
- `docs/product/current-product-state.md` "Data and trust model" section (lines 34-44) defines the four truth classes and the `verified > degraded > withheld > unavailable` ladder generically; no rolling-factor-specific carve-out beyond the methodology doc's own statement above.
- Trust degrade mechanism: `risk.py::apply_return_basis_status_to_factor_model` (lines 954-969) — checks `detect_history_return_basis(benchmark_rows)` and `detect_histories_return_basis(factor_histories)`; if either is not `"verified_adjusted_close"`, degrades `model.status` and every `window.status` via `_degrade_status_for_unverified_return_basis` (not read in this pass — name only).
- Statuses observed in tests (`test_analytics.py`): `"ok"`, `"insufficient_history"`, `"unavailable"`, and a distinct degraded string asserted via `!= "degraded_unverified_return_basis"` at line 2216 (i.e., that literal string appears to be one degrade target, though the exact enum of possible status strings was not fully enumerated in this pass — see Risk detail).
- No `withheld` state observed specifically on this model in the files read; the model instead uses `ok / insufficient_history / partial / unavailable`-style strings per its TypeScript type union (`types.ts:793`: `'ok' | 'insufficient_history' | 'partial' | string`) — worth the quant-audit lane confirming this doesn't silently violate the `verified > degraded > withheld > unavailable` ladder wording, since the field's own enum doesn't use those exact tokens.

## Tests

- Backend, `services/quant-engine/app/tests/test_analytics.py` (extensive): `test_build_statistical_factor_model_populates_multi_window_rolling_loadings` (~4878), `test_statistical_factor_model_r_squared_matches_sse_over_sst_formula` (~5305), `test_rolling_loadings_null_exactly_collinear_factor_and_fit_the_rest` (~8020), `test_rolling_loadings_orthogonalize_later_factors_against_survivors_only` (~8037), `test_orthogonalize_factors_window_reports_dropped_duplicate` (~8059), `test_apply_return_basis_status_to_factor_model_degrades_status_when_adjusted_support_is_incomplete` (~5688), plus multiple status assertions (`"insufficient_history"`, `"unavailable"`) at lines 1094, 1147, 1478, 2121, 2216, 2284, 4063, 4124. A golden-master snapshot test around line 5424-5454 pins rolling-loadings output shape.
- A dedicated NaN/non-finite-handling test exists (~7985-8020, monkeypatches `fit_factor_model` to return NaN and asserts null, not NaN, propagates).
- No `test_routes.py` assertions specific to the diagnostics route's `statistical_factor_model` field were located in this pass beyond the analytics-layer tests above (route-level pass-through not separately verified — see Risk detail).
- Frontend: `apps/desktop/src/features/portfolio/RollingFactorLoadingsCard.test.tsx` (32 lines, full file read) covers **only** `sortTooltipPayloadRows` (tooltip ordering logic) — it does **not** test data selection by window, coverage-label formatting, domain/brush computation, or empty-state rendering. This is a coverage gap on the presentation layer, not the math.

## Known limitations

From `docs/product/current-product-state.md`:

- General synthetic-history limitation applies (line 63): "Synthetic-history analytics are evidence-limited by available market, FX, and dividend data" — no chart-specific limitation is separately called out.
- `docs/product/current-product-state.md` lists `exposure.py` route as covering "holdings, sector, factor, and concentration exposure" (line 87) but the rolling-loadings data actually flows through `diagnostics.py` ("portfolio diagnostics from snapshot or imported replay", line 83) merged client-side — the route inventory doc does not itself flag this cross-route composition; a reader of that doc alone would not learn the Dashboard factor chart's data comes from the diagnostics route, not the exposure route.

## Risk detail

- Exact construction of `daily_states` / `factor_histories` / `y` (the portfolio return series regressed against factor proxies) inside `diagnostics_engine.py` was not traced line-by-line in this pass — needed for a full audit of return-basis correctness feeding the regression.
- The full status-string enum for `StatisticalFactorModel.status` / `window.status` (all values `_degrade_status_for_unverified_return_basis` can produce) was not enumerated; only observed via test assertions (`ok`, `insufficient_history`, `unavailable`, and an implied `degraded_unverified_return_basis`-shaped string). A quant-audit lane should read `_degrade_status_for_unverified_return_basis` directly (not opened in this pass).
- No route-level (`test_routes.py`) test was confirmed to assert on `statistical_factor_model` passthrough for `/engines/diagnostics/run`; coverage may rely entirely on the analytics-layer tests plus end-to-end desktop smoke tests not reviewed here.
- `RollingFactorLoadingPoint` schema fields were inferred from usage (`date`, per-factor keys, `alpha`, `r_squared`, `residual_vol`) rather than read directly from its class definition in `reconciliation.py`; the exact field list/types were not opened.
