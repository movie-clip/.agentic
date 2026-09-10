REPORT 2026-09-09-risk-annualized-volatility/02
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   none
  result:    NOT_RUN
  detail:    Order verification field is NONE; read-only research lane. Independent estimation-error computation run under scratch Python (scipy chi-square) to ground the confidence-interval figures; not a repo command.

contract_notes:
  - financial-methodology.md section "Annualized realized volatility" (~1012-1015) needs an AMENDMENT, not a new section: record that the Risk-tab surface of this same figure requires >= 60 paired daily-return observations and withholds below it, while the Dashboard surface is unchanged and keeps no explicit floor. Docs lane writes the text at close-out; see section 4.

pack_corrections:
  - none

handoff:
  - Trust-state spec for 0 <= N < 60 is: N = 0 -> unavailable (no return series); 1 <= N < 60 -> withheld (series exists, annualized estimate not responsible). Full rationale in section 3.
  - The Risk tab's sibling engines (distribution, drawdown) expose trust literal 'synthetic' | 'unavailable' only - no 'withheld' rung. This figure needs a withheld state they do not have; tech-lead DESIGN must decide how it is represented on the wire and in the card. See section 3.
  - A new module-level constant (e.g. RISK_TAB_ANNUALIZED_VOL_MIN_OBSERVATIONS = 60) belongs in services/quant-engine/app/core/constants.py. It is NOT MIN_DAILY_OBSERVATIONS (20) and must not overload it; a bare literal 60 scattered in engine/frontend code is a duplication finding. Naming is tech-lead's.
  - Open question for the story and the post-implementation quant-audit: at N >= 60 with zero return variance (constant series), the reused house path returns 0.00%, not null. Decide explicitly whether the Risk tab publishes 0.00% or withholds. See section 3 edge-case table.
  - analytics/returns.py named in the order scope does not exist. Daily portfolio returns are produced by _paired_portfolio_and_benchmark_returns in analytics/risk.py over the daily-states chain from analytics/performance.py.
  - Metrics-inventory row for the new surfaced figure is in section 5, ready for tech-lead DESIGN and story-author.

risks:
  - The confidence-interval widths in section 2 assume i.i.d. normal daily returns (exact chi-square). Real portfolio returns cluster and are fat-tailed, so the effective sample size is smaller and the true intervals are WIDER than stated - the argument for the floor is conservative, not overstated.
  - I did not run the app or engine. That volatility_summary.portfolio_volatility_pct renders non-null for the committed IB2026 portfolio, and that build_portfolio_risk_summary applies no 20-observation floor, are read from risk.py:491-509 and :2117-2120, not observed at runtime.
  - The pack edge-case table says "variance = 0 -> null, not 0 and not 1" as a blanket rule. For a dispersion statistic (unlike a ratio such as beta/correlation) a genuinely constant series arguably has a well-defined realized volatility of exactly 0. This brief flags the tension rather than resolving it; the quant-audit lane should rule on it against the implemented behaviour.

## Orchestrator brief

- Mode RESEARCH. The dedupe decision (reuse the Dashboard code path) and the 60-day floor are HUMAN rulings carried in from 01; this brief grounds them and specifies the trust behaviour. No formula is proposed or re-derived.
- Decision recorded: the Risk-tab figure is the SAME quantity, formula and code path as the Dashboard's volatility_summary.portfolio_volatility_pct (guardrail 2). Only a presentation-layer publication floor is added.
- Decision recorded: trust states below the floor are N = 0 -> unavailable, 1 <= N < 60 -> withheld. Withheld is NOT collapsed to unavailable (guardrail 4). This differs deliberately from the sibling Risk-tab engines, which have only 'unavailable' below their 20-obs floor.
- Decision recorded: methodology needs an AMENDMENT to the existing "Annualized realized volatility" section, not a new section. Docs lane writes it at close-out; this lane does not.
- Finding surfaced: the reused Dashboard path applies NO 20-observation floor to portfolio_volatility_pct today - it is non-null from N = 2 upward (and returns 0.0 at N < 2). So the cross-surface divergence range is ~2 <= N < 60, wider than the "20-59" the order assumes.
- Lane split: none set - single downstream slice. Sequence: tech-lead DESIGN (wire representation of the withheld state + the new constant) -> story-author -> human approval -> implementation -> quant-audit.
- Sections: "1. Problem framing" (concept definition, signed meaning, pitfalls, what already ships); "2. Grounding the 60-day floor" (sampling distribution, CI widths at N=20/60/252, citations); "3. Trust-state specification" (the withheld/unavailable split, sibling-engine asymmetry, edge cases); "4. Cross-surface consequence" (guardrails 2 and 3); "5. Methodology amendment and metrics inventory" (amendment target, the inventory row).
- Blocks dispatch: none from this lane. (01's blocker about deleted planning docs is unresolved but outside quant scope.)

---

## 1. Problem framing

### 1.1 The question and the decision it enables

A researcher on the Risk tab - the product's designated pre-decision
risk-budget view - currently sees stress scenarios, drawdown analytics and a
VaR/return-distribution card. The distribution card shows `std_pct`, a
**per-period (daily), population-N** standard deviation. There is no
**annualized** portfolio volatility on the tab; that figure lives only on the
Dashboard's Risk Summary card. The story surfaces the annualized figure on the
Risk tab so a risk-budgeting decision ("is my portfolio's yearly dispersion
within tolerance?") can be made without a tab switch and a mental
population-vs-sample, daily-vs-annualized reconciliation.

### 1.2 Concept definition - the Risk-tab figure IS the Dashboard figure

**Portfolio annualized realized volatility (Risk tab)** is, by human ruling,
the *same scalar* as the Dashboard's
`volatility_summary.portfolio_volatility_pct`:

```
realized_vol_pct = stdev_sample(daily_returns) * sqrt(252) * 100
```

- `daily_returns` - the cash-flow-neutral daily portfolio return series,
  **synthetic-history basis** (current holdings valued over historical market
  prices; no trade replay), excluding cash. Same series the Dashboard uses:
  `_paired_portfolio_and_benchmark_returns(..., basis=return_basis)` in
  `analytics/risk.py`, portfolio leg only.
- `stdev_sample` - **sample (N-1)** standard deviation
  (`_sample_standard_deviation` -> `_sample_variance`, `risk.py:2131-2135`).
- `sqrt(252)` - the house square-root-of-time annualization factor;
  `VOLATILITY_ANNUALIZATION_DAYS = 252` (`risk.py:89`). Used identically for
  downside volatility, tracking error and currency-leg volatility across the
  product.
- Code path: `_calculate_annualized_volatility` (`risk.py:2117-2120`), called
  by `build_portfolio_risk_summary` (`risk.py:491-509`), consumed as
  `risk_summary.portfolio_volatility_pct` and mapped to
  `volatility_summary.portfolio_volatility_pct`
  (`schemas/diagnostics.py:94-95`; `docs/contracts/diagnostics-fields.md:216-218`).
- Methodology reference: `docs/finance/financial-methodology.md` section
  **"Annualized realized volatility"** (lines 1012-1015), under
  **"Volatility and Relative Risk"**.

**Signed meaning for this portfolio.** The statistic is a non-negative measure
of *dispersion*, not direction and not loss. A value of `0` means the daily
return was constant across the sample. A value of, say, `15%` means: under the
i.i.d. assumption the annualization relies on, a one-standard-deviation band
around the portfolio's mean annual return is roughly +/- 15 percentage points.
It says nothing about the sign of returns or the depth of a loss - pair it with
the tab's VaR and drawdown cards for tail and directional risk.

**Known pitfalls** (carry into the methodology amendment):

1. **Square-root-of-time rule assumes serial independence.** Volatility
   clustering and return autocorrelation bias `sqrt(252)` scaling; the error
   grows with the scaling horizon (Danielsson & Zigrand 2006).
2. **Synthetic-history basis.** Current weights applied to past prices are not
   what the portfolio actually held; the figure is at most `synthetic`, never
   `verified` (guardrail 3; pack "synthetic history" row).
3. **Unadjusted close prices.** No total-return adjustment; dividend drops sit
   in the price path (methodology F-9 / F-12 territory) - a small vol
   distortion, already a documented synthetic-path caveat.
4. **Point estimate with wide intervals at short N** - the entire reason for
   the floor; quantified in section 2.
5. **Non-stationarity.** A short sample drawn from one volatility regime
   annualizes to a figure that misrepresents the year.

### 1.3 What already ships, and the one gap

| Already implemented | Where |
|---|---|
| The formula, sample-(N-1), `sqrt(252)` | `risk.py:2117-2120`; methodology 1012-1015 |
| Portfolio annualized vol, synthetic basis | `build_portfolio_risk_summary`, `risk.py:491-509` |
| Surfaced on the **Dashboard** Risk Summary card | `RiskSummaryCard.tsx`; `dashboard-fields.md:37, 237` |
| A 20-obs floor (`MIN_DAILY_OBSERVATIONS`) | applies to distribution, drawdown, and **per-position** vol/beta/rho - **not** to `portfolio_volatility_pct` |

**Not covered:** the figure on the **Risk tab**, and any minimum-history floor
on this portfolio-level figure at all.

**Correction to the order's premise.** The order states the Dashboard figure is
non-null in the range "20-59 observations", implying a 20-obs floor on it.
There is none. `build_portfolio_risk_summary` computes
`portfolio_volatility_pct` whenever `portfolio_samples` is non-empty, and
`_calculate_annualized_volatility` returns `0.0` for `len < 2`. So the Dashboard
figure is:

- `None` only when the upstream diagnostics history context is absent
  (`diagnostics_engine.py` ~485-497, `observations = 0`);
- `0.00%` at N = 1;
- a computed number for **all N >= 2**.

The 20-obs floor the order and 01 attribute to this figure belongs to the
*sibling* engines, not to it. The practical consequence: the Risk tab withholds
across roughly `2 <= N < 60`, a wider divergence band than "20-59".

---

## 2. Grounding the 60-day floor

Decision (b) is settled at 60; this section supplies the estimation-error
argument and the sampling distribution, per the definition of done. It does not
relitigate 20 vs 60.

### 2.1 Why annualizing a short sample is the problem

Realized volatility is an *estimate* of an unknown parameter from a finite
sample. For returns modelled as i.i.d. normal with N observations, the sample
variance obeys

```
(N - 1) * s^2 / sigma^2  ~  chi-square(N - 1)          [Casella & Berger 2002, Thm 5.3.1]
```

so the sample standard deviation `s` has relative standard error

```
SE(s) / sigma  ~=  1 / sqrt(2 * (N - 1))               [Kenney & Keeping 1951, Sec 7.9]
```

Annualization multiplies **both** the point estimate and its standard error by
the same constant `sqrt(252) ~= 15.87`. It therefore adds **no information** -
it takes a noisy sub-quarter estimate and rescales it, plus the `sqrt(252)`
rule itself injects further error when returns are autocorrelated (Danielsson &
Zigrand 2006). The absolute uncertainty, expressed in annualized percentage
points, is inflated ~16x. Publishing that as a yearly risk figure is spurious
precision.

### 2.2 Sampling distribution of the estimate at N = 20, 60, 252

Exact 95% confidence interval for `sigma` under normality, as multiplicative
factors on the observed `s`
(`[ sqrt((N-1)/chi2_{0.975,N-1}) , sqrt((N-1)/chi2_{0.025,N-1}) ]`), and the
implied interval for a portfolio whose **true** annualized volatility is 15.0%:

| N | rel. SE of `s` | 95% CI factor on `s` | 95% CI at true vol = 15% | half-width |
|---:|---:|---|---|---:|
| 20  | 16.2% | [0.760 , 1.461] | [11.4% , 21.9%] | ~5.3 pp |
| 60  |  9.2% | [0.848 , 1.220] | [12.7% , 18.3%] | ~2.8 pp |
| 252 |  4.5% | [0.920 , 1.096] | [13.8% , 16.4%] | ~1.3 pp |

(Computed exact-chi-square with scipy in scratch; asymptotic `1/sqrt(2(N-1))`
agrees to <0.01. Real returns cluster and are fat-tailed, so treat these as
lower bounds on the true width - see risks.)

### 2.3 The estimation-error argument for the floor

At **N = 20** (~1 trading month) the 95% interval spans roughly two-thirds of
the point estimate's value (-24% / +46% multiplicatively). A researcher reading
"portfolio volatility 15%" would be equally consistent with 11% or 22% - a
different risk-budget conclusion. Scaling one month of data to a year by
`sqrt(252)` is exactly the "not enough history to compute it responsibly" case.

At **N = 60** (~3 months, ~1 quarter) the relative standard error roughly
halves (16.2% -> 9.2%) and the 95% half-width at a typical 15% vol falls to
~+/- 3 pp. That is still wide, but it is defensible for a figure that carries a
`synthetic` trust badge and an explicit disclosure. 60 is also:

- the shortest horizon over which `sqrt(252)` annualization is conventionally
  applied in practice (a quarter);
- the smallest window already used by the Risk tab's own distribution engine
  (60 / 252 / 504), so the new floor lands on an existing Risk-tab boundary
  rather than inventing a fourth number.

Standard practice corroborates a floor of at least a quarter, trending toward a
year: Figlewski (1997) shows short-sample volatility estimates are dominated by
sampling error and argues for long estimation windows; the RiskMetrics
Technical Document (1996) uses an EWMA whose effective memory is on the order of
a year of daily data; Andersen, Bollerslev, Diebold & Labys (2003) formalize
realized-volatility measurement error.

### 2.4 Citations (for the methodology amendment)

- Casella, G. & Berger, R.L. (2002). *Statistical Inference*, 2nd ed., Duxbury.
  Sec 5.3 (Thm 5.3.1) - `(n-1)s^2/sigma^2 ~ chi-square(n-1)` for normal samples.
- Kenney, J.F. & Keeping, E.S. (1951). *Mathematics of Statistics, Part 2*, 2nd
  ed., Van Nostrand. Sec 7.9 - standard error of the sample standard deviation,
  `SE(s) ~= sigma / sqrt(2n)`.
- Figlewski, S. (1997). "Forecasting Volatility." *Financial Markets,
  Institutions & Instruments* 6(1), 1-88 - short samples are dominated by
  estimation error; long windows needed for stable volatility estimates.
- Danielsson, J. & Zigrand, J.-P. (2006). "On time-scaling of risk and the
  square-root-of-time rule." *Journal of Banking & Finance* 30(10), 2701-2713 -
  `sqrt(T)` scaling misstates risk under non-i.i.d. returns, error grows with
  horizon.
- Andersen, T.G., Bollerslev, T., Diebold, F.X. & Labys, P. (2003). "Modeling
  and Forecasting Realized Volatility." *Econometrica* 71(2), 579-625.
- J.P. Morgan / Reuters (1996). *RiskMetrics - Technical Document*, 4th ed. -
  decay factor / effective sample length ~ one year of daily data.

---

## 3. Trust-state specification

### 3.1 The state, per N

Truth class throughout: **synthetic history** (current holdings x historical
prices). Trust ladder: `verified > degraded > withheld > unavailable`.

| N (paired daily returns) | Trust state | Value | Why |
|---|---|---|---|
| N = 0 (no return series: empty portfolio, or no price coverage for any holding, or diagnostics history context absent) | **unavailable** | null | We do not have the input. Matches the existing diagnostics fallback (`observations = 0`) and the pack's empty-portfolio edge case. |
| 1 <= N < 60 | **withheld** | null | We *have* the daily-return series - the sibling distribution card is already populating from it at N >= 20 - but the annualized projection over a sub-quarter sample is not trustworthy (section 2). "We have it and do not trust it" = withheld, by the pack's definition. |
| N >= 60 | **synthetic** (published) | computed % | Meets the floor. Never `verified`, never `degraded` upward - synthetic basis (guardrail 3). |

**Guardrail 4 reconciliation.** `withheld` must NOT be rendered or serialized
as `unavailable`. At N = 30 the researcher can see the VaR/distribution card
populated from the same 30-return series; telling them the annualized vol is
"unavailable" (no data) next to a populated histogram is the exact
withheld->unavailable collapse the guardrail forbids. The state must read as
"held back pending >= 60 trading days", distinct from "no history".

**No fallback value.** Below the floor the figure is null with a trust state -
never `0.0`, never the raw daily `stdev` shown as if annualized, never the
Dashboard's unfloored number passed through.

### 3.2 This differs, deliberately, from the sibling Risk-tab engines

The distribution and drawdown engines expose
`trust: Literal["synthetic", "unavailable"]` - there is **no `withheld` rung**
in their contract. Below their 20-obs floor they return `unavailable` with
`return_count = 0` and all scalars null (`risk-fields.md:240, 432`).

This figure needs a state they do not have. Two consequences for tech-lead
DESIGN (not resolved here):

1. Either the Risk-tab volatility surface carries its own trust field that
   includes `withheld`, or the card renders a `withheld` helper distinct from
   the card-level `unavailable` empty state while re-using the existing badge
   enum. The wire representation is a DESIGN decision.
2. The asymmetry ("distribution card populated at N = 30, annualized vol
   withheld at N = 30") is intentional and must be preserved - it is the
   stricter-floor ruling made visible. It should not be "fixed" by lowering
   this floor to 20 or by making this state `unavailable` to match the
   siblings. A one-line UI rationale for the asymmetry is owed (per 01's
   Option B note).

### 3.3 Edge cases (numeric behaviour, no fallback values)

| Case | Required behaviour |
|---|---|
| Empty portfolio / zero holdings | `unavailable`, null |
| No price history for any holding | `unavailable`, null |
| Single holding, N >= 60 | defined - volatility does not divide by a cross-sectional count; still subject to the 60-obs floor on its return series |
| 1 <= N < 60 (window longer than history) | `withheld`, null. Note this figure uses the **full available paired history**, not a fixed trailing window; N is the total count, and 60 is a minimum, not a window length |
| N >= 60, variance = 0 (constant return series) | **OPEN - flag for story + quant-audit.** The reused house path returns `0.00%` (std 0 -> `0.0 * sqrt(252)`). Pack edge-case rule says variance 0 -> null. For a dispersion statistic (unlike beta/rho, which are 0/0 undefined) a truly constant series has a well-defined realized volatility of 0. Decide explicitly: publish `0.00%` or withhold. Do not leave it implicit. |
| N < 2 | Cannot occur once the 60-floor gate is in front of the computation; without the gate the house path returns `0.0` (a plausible-looking zero) - another reason the gate must sit *before* `_calculate_annualized_volatility`, not after it. |

---

## 4. Cross-surface consequence

At N = 30 the Dashboard Risk Summary card shows a number; the Risk tab shows a
`withheld` state. This is acceptable and explainable. Both surfaces are the
**same truth class** (synthetic history) and, by the human's reuse ruling, the
**same formula and the same code path** - so this is not a truth-class mix
(guardrail 3) and not a traceability break (guardrail 2): there is one
documented formula and one executable path, differing only in a
presentation-layer publication threshold. When both surfaces publish (N >= 60)
the two numbers are **bit-identical**, which is strictly stronger than the
cross-surface tolerance the methodology already accepts under
"Standard-deviation denominator conventions (US-27.9 / audit F12)", where the
same metric legitimately differs by `sqrt(N/(N-1))` (~0.8% at N = 60) between
the sample-(N-1) and population-(N) modules because each is internally
consistent and the gap carries no decision-relevant content. A pure
presence/absence gate at low N carries even less: it never yields two different
numbers, only "number" versus "explicitly held back pending more history",
which is consistent with the Risk tab's stated role as the higher-bar
pre-decision risk view. The single requirement is that the withheld state name
its reason ("needs >= 60 trading days of return history; the Dashboard shows an
unfloored estimate") so a researcher cross-referencing the two tabs reads it as
a deliberate threshold, not a bug or missing data.

---

## 5. Methodology amendment and metrics inventory

### 5.1 Methodology change

**AMENDMENT to the existing section, not a new section.** Target:
`docs/finance/financial-methodology.md` section **"Annualized realized
volatility"** (lines ~1012-1015), under "Volatility and Relative Risk". The
amendment records:

- the Risk-tab surface of this figure requires `N >= 60` paired daily-return
  observations;
- below the floor: `N = 0 -> unavailable`, `1 <= N < 60 -> withheld` (not
  collapsed to unavailable);
- the Dashboard surface is unchanged and retains no explicit floor;
- the 60-obs floor is a distinct constant from the per-position
  `MIN_DAILY_OBSERVATIONS` (20) rule in the "Per-position minimum-observation
  rule" section (~1725-1755) - keep the two rules separate in the text;
- cite section 2.4 above for the estimation-error grounding.

Per the quant pack convention, a brand-new methodology *section* would be
flag-for-human; this is an amendment to an existing section whose content this
order specifies, so the docs lane writes it at close-out. This lane does not
write methodology text.

### 5.2 Computed-metrics inventory (one row for the new surfaced figure)

Wire field name, TS type and component are tech-lead DESIGN decisions;
placeholders below.

| Attribute | Value |
|---|---|
| **Field (placeholder)** | `risk_tab.annualized_volatility_pct` |
| **Backend source** | reuse `risk_summary.portfolio_volatility_pct` from `build_portfolio_risk_summary` (`analytics/risk.py:491-509`); i.e. `volatility_summary.portfolio_volatility_pct` from the diagnostics engine. No new computation. |
| **Formula** | `stdev_sample(daily_returns) * sqrt(252) * 100`; sample (N-1) std; `_calculate_annualized_volatility` (`risk.py:2117-2120`); methodology "Annualized realized volatility" (1012-1015) |
| **Return series** | cash-flow-neutral daily portfolio returns, cash excluded; full available paired history (not a fixed window); synthetic-history basis |
| **Units** | percent, already x100 (`_pct` suffix; matches the Dashboard field) |
| **Truth class** | synthetic history |
| **Trust level** | `synthetic` when published; never `verified`/`degraded` |
| **Floor** | `N >= 60` paired daily-return observations (new constant, `core/constants.py`; not `MIN_DAILY_OBSERVATIONS`) |
| **Trust / nullability rule** | `N = 0` -> `unavailable`, value null; `1 <= N < 60` -> `withheld`, value null, reason-tagged; `N >= 60` -> published `synthetic`; `N >= 60` and variance 0 -> OPEN (0.00% vs null), decide in story/audit |
| **Nullable** | Yes |
| **Gate placement** | the floor check must run BEFORE `_calculate_annualized_volatility` so a sub-floor N never reaches the `len < 2 -> 0.0` branch |

### 5.3 Tech-debt register

Checked `docs/tech-debt-register.md` - no open finding touches
`analytics/risk.py` volatility, `MIN_DAILY_OBSERVATIONS`, or annualization. The
FX-rate hardcode recorded there is in `reconciliation.py` and does not bear on
this figure.
