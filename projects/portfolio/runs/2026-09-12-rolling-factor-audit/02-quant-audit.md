REPORT 2026-09-12-rolling-factor-audit/02
status:      DONE
verdict:     FAIL

changed:
  - none

verification:
  command:   cd services/quant-engine && pytest app/tests/test_analytics.py -k "factor_model or rolling_loadings or orthogonalize or return_basis" -v
  result:    PASS
  detail:    15 passed, 205 deselected in 7.10s. anchor: external - (a) independent numpy ridge-OLS + Gram-Schmidt implementation, agrees to 7.2e-16 on coefficients and 1.1e-16 on R^2; (b) degenerate closed-form case (pure-noise y, true beta=0, true R^2=0) run through _build_rolling_factor_loadings at all three windows; (c) closed-form OLS bias E[R^2|null]=K/(n-1) and residual-variance factor (n-K-1)/(n-1). The suite passing is not evidence for the verdict - see section 'Why the suite passes anyway'.

contract_notes:
  - `statistical_factor_model.status` and `windows[].status` have no row in docs/contracts/dashboard-fields.md:248; the card consumes neither. see § FINDING 1
  - `RollingFactorLoadingPoint.alpha` (reconciliation.py) and its types.ts mirror are always null by construction; the vitest fixture fabricates `alpha: 0.0002`. see § FINDING 7
  - `residual_vol` returns percent (risk.py:1669 ×100) with no `_pct` suffix, against the repo's unit-suffix contract. see § FINDING 8
  - types.ts marks technology / consumer_staples / utilities / consumer_discretionary optional (`?`); the other 12 factor keys are required. Pydantic makes all 16 `float | None = None`.
  - No methodology section defines `residual_vol`; guardrail 2 (one documented formula per displayed metric) is unmet for that field.

pack_corrections:
  - none

handoff:
  - FINDING 1 (CRITICAL) and FINDING 2 (CRITICAL) both block. 1 is a frontend fix, 2 is an owner/methodology decision — not an engineer's.
  - FINDING 4 and 6 are documentation/test-comment defects sharing one root error: the belief that the 20d regression uses 25 observations. It uses 20.
  - Reproduction scripts are inline in the sections below; all run offline against `app/analytics` with `random.seed` fixed.
  - The core linear algebra is correct and needs no rework — see § What verified clean.

risks:
  - gates.md § 2: the [−2, +4] market-loading assertion cannot fail — pure noise produced max |market| = 0.46. See § Why the suite passes anyway.
  - FINDING 2 is a methodology-design judgment, not an arithmetic slip. Per pack it goes to the human with the anchor, not to a CR against the implementer.
  - Not re-verified, out of scope: `_build_current_factor_snapshot`, `build_stress_scenarios`, `build_risk_contribution_breakdown` — all inherit FINDING 2 and 3.
  - FINDING 5's numerical impact on loadings measured small (β 1.175 both with and without a 1.5% dividend yield); it is a labelling defect, not an arithmetic one. Do not route it as a math fix.

---

## Orchestrator brief

- **Verdict: FAIL.** The formula is implemented correctly; the chart is not honestly labelled, and its 20-day window publishes noise as exposure.
- Decision: the *arithmetic* is clean — independent numpy re-implementation agrees to 7e-16. Do not re-dispatch the linear algebra.
- Decision: FINDING 1 (status never rendered) is the narrowest blocker and is a pure **frontend** fix.
- Decision: FINDING 2 (16 factors, 20 observations, 3 residual dof) is an **owner/methodology** decision, not a lane's. Escalate; do not open a CR.
- Decision: FINDING 3 (residual_vol bias), 4 and 6 (doc/test say 25 obs, code uses 20) are **docs + backend**; 7–10 are contract cleanup.
- Lane split if dispatched: frontend → F1; owner → F2; backend → F3; docs → F4, F6; backend+frontend+docs → F7–F10.
- Sections below: **Findings** (F1–F10, each with the numbers), **What verified clean**, **Why the suite passes anyway**, **Reproductions**.
- Nothing blocks dispatch of F1. F2 blocks close-out until the owner rules.

---

## Findings

```
FINDING 1
severity:   CRITICAL
where:      apps/desktop/src/features/portfolio/RollingFactorLoadingsCard.tsx (whole file)
claim:      risk.py:954-969 degrades model.status and every windows[].status to
            "degraded_unverified_return_basis" when the benchmark or factor return
            basis is not verified_adjusted_close.
actual:     `grep -n "status" RollingFactorLoadingsCard.tsx` returns nothing. The card
            reads rolling_loadings_*d, windows[].observations, start/end dates — never
            `status`. A degraded model renders pixel-identical to an `ok` one.
impact:     The researcher reads a degraded number as verified. The engine's entire
            return-basis degrade path is computed and discarded at the last hop.
expected:   The card surfaces the degrade level, and dashboard-fields.md carries a row
            for statistical_factor_model.status. Guardrail 4.
```

```
FINDING 2
severity:   CRITICAL
where:      factor_model.py:53-70 (16 factors) + risk.py:83 WINDOW_MIN_OBSERVATIONS
            + risk.py:1650-1658; surfaced by RollingFactorLoadingsCard.tsx:265 ("20d")
claim:      methodology §Per-window orthogonalization presents the 20/60/252 windows as
            three equivalent views; the only stated R² caveat is "in-sample ... must not
            be used to claim out-of-sample explanatory power".
actual:     The 20d regression fits K=16 factors + intercept = 17 parameters on exactly
            20 observations → 3 residual degrees of freedom. Fed pure noise (y
            independent of every factor, so true β=0 and true R²=0 for all dates):

              window=20   mean R² = 0.850   max 0.997   max |market| = 0.463
              window=60   mean R² = 0.288   max 0.448   max |market| = 0.280
              window=252  mean R² = 0.059   max 0.091   max |market| = 0.086

            These match the closed form E[R²|null] = K/(n−1) = 0.842 / 0.271 / 0.064.
            A single 20d point from noise returned r_squared=0.9006 with loadings up to
            ±0.5762 and residual_vol 3.87% against a true 15.56%.
impact:     On the 20d window ~84% of the displayed R² is an arithmetic artifact of the
            parameter count, and the loadings are largely sampling noise plotted as
            time-varying factor exposure. A researcher reads "R² 0.90" as "the model
            explains 90% of my returns" and reads a ±0.5 line as a real tilt. The 60d
            default still carries ~0.27 of artifact R².
expected:   Either the 20d window is withdrawn / gated, or the published R² is
            degrees-of-freedom adjusted (R²_adj = 1 − (1−R²)(n−1)/(n−K−1)), or the
            methodology documents E[R²|null] per window and the UI states it. This is an
            owner decision on the model's design, not an implementation fix.
```

```
FINDING 3
severity:   MATERIAL
where:      factor_model.py:140-145 (residuals) → risk.py:1668-1670 (residual_vol)
claim:      residual_vol is the annualized volatility of the regression residual, i.e.
            the portfolio's specific (non-factor) risk.
actual:     _calculate_annualized_volatility divides RSS by (n−1), the sample-stdev
            denominator, not by (n−K−1). With K=16 the OLS residual variance is
            biased low by (n−K−1)/(n−1). Monte-Carlo against a known true 15.87%:

              window=20   reported 5.81%   ratio 0.366   theory √(3/19)  = 0.397
              window=60   reported 13.75%  ratio 0.866   theory √(43/59) = 0.854
              window=252  reported 15.73%  ratio 0.991   theory √(235/251)=0.968

impact:     Specific risk is understated by ~63% on the 20d window and ~13% on the 60d.
            Anything downstream that partitions total variance into factor + specific
            (risk.py:1841 specific_risk_share) inherits the bias in the same direction.
expected:   Divide by (n − K − 1), or document residual_vol as an uncorrected in-sample
            residual dispersion. Note this card does not render the field, but it ships
            in the same payload and FactorDriftSummaryCard.test.tsx:14 names it.
```

```
FINDING 4
severity:   MATERIAL
where:      docs/finance/financial-methodology.md §Per-window orthogonalization,
            "Edge cases" bullet 1 — vs risk.py:1644-1652
claim:      "Window has fewer than WINDOW_MIN_OBSERVATIONS[w] dates: return null for all
            factors on that date" — implying the w=20 regression window holds ≥25 dates.
actual:     The gate is on elapsed history, not window content:
              if index + 1 < min_observations: emit a date-only null point
              start = index - window + 1   →  y[start : index+1], length == window
            The regression window always holds exactly w dates (20 / 60 / 252). The
            first 20d estimate lands at index 24 and uses y[5:25] — 20 observations.
            app/core/constants.py:33 describes it correctly as "a per-window OLS
            estimation buffer"; the methodology doc does not.
impact:     A reader of the specification concludes the 20d fit has 25−17 = 8 residual
            dof. It has 3. This wrong reading is the direct upstream cause of FINDING 2
            being invisible, and it is reproduced verbatim in the tests (FINDING 6).
expected:   The doc states that WINDOW_MIN_OBSERVATIONS is a history prerequisite and
            that the estimation window is exactly w observations against K+1 parameters.
```

```
FINDING 5
severity:   MATERIAL
where:      services/synthetic_history.py:66 vs risk.py:779-808 vs risk.py:954-969
claim:      The rolling regression is a like-for-like fit of portfolio returns on factor
            returns, and status "ok" means the return basis is verified.
actual:     The dependent variable y is built from synthetic states priced on
            row['price'] — raw close, price-return only. The regressors and the
            benchmark go through select_history_price_series, which returns
            "verified_adjusted_close" and uses adjClose (total return) whenever present.
            apply_return_basis_status_to_factor_model inspects only benchmark_rows and
            factor_histories; it never inspects the portfolio leg — which
            diagnostics_engine.py:274-283 itself declares
            verification_status="unverified", economic_basis="price_return_only".
            End-to-end run with adjClose-bearing factors and a price-return portfolio:
              model status BEFORE degrade: ok   AFTER: ok
              windows: [(20,'ok',399), (60,'ok',399), (252,'ok',399)]
impact:     status "ok" is published for a model whose dependent variable the same
            service has already classified as unverified. Truth-class separation
            (guardrail 3) and trust semantics (guardrail 4) both bend here.
expected:   The degrade gate includes the portfolio return basis, or the doc states that
            the model deliberately regresses price returns on total returns and that
            "ok" scopes only to the regressor legs. Measured loading impact is small
            (see § Reproductions) — this is a labelling defect, not an arithmetic one.
```

```
FINDING 6
severity:   MATERIAL
where:      app/tests/test_analytics.py:7848 and :7905-7907 (docstrings)
claim:      ":7848 — '20d window (25 obs, 17 params → 8 df)'; ':7905 — the pre-fix
            condition number was dangerous and λ=1e-5 provided no real regularisation.
            The window-proportional ridge floor (λ=0.01 for the 20d window) must cap
            every coefficient'."
actual:     The shipped ROLLING_RIDGE_FLOOR (factor_model.py:81) is {20: 1e-5, 60: 1e-5,
            252: 1e-5} — λ=0.01 was reverted, and factor_model.py:78-81 records why
            (">80% shrinkage — unacceptable bias"). The 20d window is 20 obs / 3 df, not
            25 obs / 8 df. Both docstrings describe a mechanism that is not shipped.
impact:     The two stability tests appear to guarantee a safeguard that does not exist.
            An engineer changing the ridge floor would read the wrong contract.
expected:   Docstrings state the shipped λ=1e-5 and that stability comes from per-window
            Gram-Schmidt alone; observation/df counts corrected to 20 / 3.
```

```
FINDING 7
severity:   MINOR
where:      schemas/reconciliation.py RollingFactorLoadingPoint.alpha;
            types.ts:~840 alpha; src/test/portfolioFixtures.ts:958-959
claim:      RollingFactorLoadingPoint carries an `alpha` estimate per date.
actual:     _build_rolling_factor_loadings never sets alpha — it passes only date,
            r_squared, residual_vol and **values_map. The field is null by construction.
            risk.py:1352-1354 records the deliberate decision: "methodology forbids
            labelling the OLS intercept 'alpha'". The vitest fixture nonetheless sets
            alpha: 0.0002 — a value the engine cannot produce.
impact:     A field that looks available in the contract and the TS type is permanently
            null; the fixture makes it look populated to anyone reading the test data.
expected:   Remove alpha from the schema/type/fixture, or document it as reserved-null.
```

```
FINDING 8
severity:   MINOR
where:      risk.py:1668-1670; schemas/reconciliation.py RollingFactorLoadingPoint
claim:      Field name `residual_vol` carries no unit suffix.
actual:     The value is `_calculate_annualized_volatility(residuals) * 100` — percent.
impact:     The repo's contract is that the suffix names the unit (_pct / _pp /
            fraction). A consumer can reasonably read `residual_vol` as a fraction and
            multiply by 100 again.
expected:   `residual_vol_pct`, or a documented exception.
```

```
FINDING 9
severity:   MINOR
where:      apps/desktop/src/features/portfolio/types.ts:819-887
claim:      The TS rolling_loadings_*d element mirrors RollingFactorLoadingPoint.
actual:     technology, consumer_staples, utilities and consumer_discretionary are
            declared optional (`?: number | null`); the other twelve factor keys are
            required. The Pydantic model declares all sixteen `float | None = None`.
impact:     Optionality diverges from the schema for four of sixteen factors — harmless
            today because the engine always emits every key, but it is a contract drift
            the schema hook exists to catch.
expected:   All sixteen keys declared identically.
```

```
FINDING 10
severity:   MINOR
where:      RollingFactorLoadingsCard.tsx:315
claim:      Empty state reads "Available observations: {selectedWindowSummary.observations}".
actual:     WindowSummary.observations is len(common_dates) — total shared history, not
            the per-estimate observation count and not the number of estimable dates.
            My 400-day run reported 399 for all three windows.
impact:     Under a heading about the selected window having "enough observations", the
            number shown is not the selected window's.
expected:   Label it as available history, or show the estimable-point count.
```

---

## What verified clean

These reproduce exactly and need no rework.

- **The ridge-OLS and Gram-Schmidt arithmetic is correct.** An independent numpy
  implementation written from the concept (classical Gram-Schmidt with an intercept
  column, then `solve(XᵀX + λD, Xᵀy)` with `D = diag(0,1,…,1)`, λ=1e-5) agrees with
  `fit_factor_model` to **7.2e-16** on every coefficient and **1.1e-16** on R².
  `anchor: independent implementation (numpy)`.
- **The doc's formula and the code agree**, step for step: window slice → per-window
  Gram-Schmidt in `orthogonalization_order` → ridge on factor columns only → reported
  loading = β_{k+1}. The one exception is FINDING 4's edge-case wording.
- **R² = 1 − SSE/SST is exactly as documented** (factor_model.py:141-144), computed on
  in-sample fitted values. `ss_total == 0` → `None`, correct: a constant return series
  yields null R², not 0 and not 1.
- **No duplicated formula.** `_least_squares`, `_solve_linear_system`,
  `orthogonalize_factors_window` and `fit_factor_model` exist once, in
  `factor_model.py`; `risk.py` and `attribution.py` both import them, and
  test_analytics.py:8102-8104 pins identity. Guardrail 2 holds for the formula itself.
- **Edge cases behave as documented**, checked numerically, not read:
  - history shorter than `WINDOW_MIN_OBSERVATIONS` → every point date-only null, no
    partial-window value;
  - empty dates → `[]`;
  - `growth` an exact duplicate of `market` → `growth` is dropped from the design
    matrix and its loading is `None`, `market` still fits (−0.298), later factors
    orthogonalized against survivors only;
  - the NaN guard at risk.py:1663-1675 is real — `isfinite` is checked on each
    coefficient, on r_squared and on residual_vol independently.
- **Annualisation is right**: sample stdev × √252, trading-day count 252 (the
  *denominator* is the FINDING 3 issue, not the factor).
- **The estimator recovers a known loading when signal dominates.** With a synthetic
  portfolio built as 1.2 × SPY returns + noise (true β = 1.2):
  20d mean 1.174, 60d 1.186, 252d 1.190. The ~1% downward bias is the expected
  attenuation from noise in y. The estimator is not broken — FINDING 2 is about what it
  does when signal does *not* dominate, which is the ordinary case.

---

## Why the suite passes anyway

`verification.result: PASS` is recorded because the order named that command and it
ran green (15 passed, 205 deselected). It is not evidence for the verdict, and the
reason is worth stating because it is the failure gates.md § 2 describes.

`test_rolling_factor_loadings_market_beta_in_range` asserts the 20d market loading stays
within [−2, +4]. I fed the same function pure noise — sixteen independent factor series
and a y independent of all of them — and the largest |market| produced at w=20 was
**0.463**. The assertion band is roughly four times wider than anything the estimator
emits, so no input distinguishes a working model from a degenerate one under this test.
The test was written against a historical blowup (loadings near −4.60) that per-window
Gram-Schmidt genuinely fixed; it does not, and cannot, detect the *remaining* defect,
which is not blowup but inflated R² and noise-driven loadings within a plausible band.

Similarly, no test asserts anything about `statistical_factor_model.status` reaching the
UI, which is why FINDING 1 survived: the engine-side degrade is tested
(`test_apply_return_basis_status_to_factor_model_degrades_status_...`), the rendering of
it is not, and `RollingFactorLoadingsCard.test.tsx` covers only tooltip row ordering.

---

## Reproductions

All offline, `random.seed` fixed, run from `services/quant-engine`.

**F2 — noise through the shipped rolling function.**

```python
import random
from app.analytics.factor_model import DEFAULT_FACTOR_DEFINITIONS
from app.analytics.risk import _build_rolling_factor_loadings
for window, N in ((20,120),(60,200),(252,600)):
    random.seed(11)
    dates  = [f"d{i:04d}" for i in range(N)]
    factors= [(d.label,d.us_proxy,[random.gauss(0,0.01) for _ in range(N)])
              for d in DEFAULT_FACTOR_DEFINITIONS]
    y      = [random.gauss(0,0.01) for _ in range(N)]     # true beta 0, true R2 0
    pts    = _build_rolling_factor_loadings(dates, y, factors, window=window)
    rs     = [p.r_squared for p in pts if p.r_squared is not None]
    print(window, sum(rs)/len(rs), max(rs), 16/(window-1))
```

Output: `20 0.850 0.997 0.842` / `60 0.288 0.448 0.271` / `252 0.059 0.091 0.064`.

**F3 — residual_vol against a known true 15.87%.** Same construction, reading
`p.residual_vol`; means 5.81 / 13.75 / 15.73 against theory √((n−K−1)/(n−1)) =
0.397 / 0.854 / 0.968 of true.

**F5 — status stays "ok" on a mixed return basis.** Build `price` as a raw close with
quarterly dividend drops and `adjClose` as the total-return series, feed the holdings to
`build_synthetic_snapshot_history_states` and the proxies to
`build_statistical_factor_model(..., return_basis="market_value")`, then apply
`apply_return_basis_status_to_factor_model`. Status is `ok` before and after; all three
windows `ok`. Loading impact measured separately at true β=1.2: **1.175 with a 1.5%
dividend yield, 1.175 without** — the mislabelling matters, the arithmetic barely does.

**F1 — trivially reproducible:** `grep -n "status"
apps/desktop/src/features/portfolio/RollingFactorLoadingsCard.tsx` returns no lines.
