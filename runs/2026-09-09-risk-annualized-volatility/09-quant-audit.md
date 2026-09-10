REPORT 2026-09-09-risk-annualized-volatility/09
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd services/quant-engine && python -c "independent from-concept reimplementation of sample (N-1) stdev * sqrt(252) * 100, plus statistics.stdev cross-check, plus degenerate cases (two-point / constant / single), compared against _calculate_annualized_volatility and _build_risk_tab_annualized_volatility"
  result:    PASS
  detail:    anchor: external (independent numpy-free reimplementation + statistics.stdev + degenerate closed-form cases). Independent recompute matches engine _calculate_annualized_volatility to the bit on every N>=2 case (two-point 22.45, three-point 30.05, constant-x60 0.0). Helper classifier verified across N in {-1,0,1,30,59,60,252}: N<=0 unavailable/null, 1..59 withheld/null (incl. vol_in=0.0 at N=1 -> null, not 0.0), N>=60 synthetic with value copied through. Backend suite 1001 passed (08), full run_all_tests.py exit 0 (08).

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Methodology amendment text specified in 05 § 7 row 1 / 06 contract_notes is accurate against the shipped code and safe for the docs lane to write. Clause-by-clause check in § A4.
  - Ruling for the tech lead / docs lane: gating the floor on paired `risk_summary.observations` (not the distribution engine's unpaired `return_count`) is CORRECT, not a defect. Reasoning in § A2.

risks:
  - Zero-variance -> 0.00% at N>=60 is sound under guardrail 4 and I concur with the human ruling; the only caveat (a constant 60-day series likely means a stale price feed, which other disclosures own) is a note, not a change request. See § A3.
  - If run_diagnostics_engine ever runs on the imported-replay basis, this figure is still labelled trust="synthetic", which UNDERSTATES the basis — conservative under guardrail 4 and consistent with the rest of the Risk tab. Not a defect; noted so it is not mistaken for one.
  - AnnualizedVolatilityCard.formatPct returns '—' for null, but is only reachable in the trust==="synthetic" branch where the backend guarantees a non-null value. Harmless unreachable path; no action.
  - Pre-existing, out of scope: _calculate_annualized_volatility (risk.py:2120) uses a literal sqrt(252) while VOLATILITY_ANNUALIZATION_DAYS=252 exists in the same module. Same value; not touched by US-44.1.

## Orchestrator brief

- Verdict: PASS. All four guardrails hold. No change requests. Notes are in risks/handoff, none blocking.
- g1 (accuracy): the published scalar is the shipped Dashboard formula — sample (N-1) stdev(daily) * sqrt(252) * 100, rounded 2dp — reused, not recomputed. Independently reimplemented from the concept and matched to the bit on all N>=2 cases plus degenerate series.
- g2 (traceability): one formula, one code path (_calculate_annualized_volatility, risk.py:2117-2120). The new helper _build_risk_tab_annualized_volatility computes nothing; it classifies on observation count and copies the value. No duplicated formula introduced (grepped).
- g3 (truth-class): Synthetic History end to end. Contract literal is synthetic|withheld|unavailable — never verified/degraded. Card copy and tooltip state the synthetic basis; no broker-truth / snapshot mixing.
- g4 (trust semantics): withheld (1..59) and unavailable (0) are distinct on the wire and proven distinct by test; sub-floor value is null — never 0, never a dash, never the Dashboard passthrough. N=1's reused-path 0.0 cannot leak because the gate keys on count before value selection.
- Floor placement: server-side in the diagnostics engine, before any value is selected, keyed on risk_summary.observations — exactly where 02 § 3.2 and 05 § 4 said, on the count 02 anchored on.
- Ruling requested by the order — gate on paired N vs unpaired return_count: paired N is correct. Rationale in § A2.
- Zero-variance ruling (publish 0.00%): sound under g4. I concur; would not have ruled differently. § A3.
- Methodology amendment the plan specifies: accurate against the implementation; docs lane is clear to write it. § A4.
- Sections below: "§ A1 Formula re-derivation" (the independent recompute and numbers); "§ A2 The 60-observation floor" (placement + paired-count ruling); "§ A3 Trust semantics & edge cases" (per-N table, what each test falsifies); "§ A4 Methodology amendment check"; "§ A5 Truth-class".

---

## § A1 Formula re-derivation

**Anchor: external.** Independent from-concept reimplementation (plain Python,
no shared helper), `statistics.stdev` as a third path, and degenerate
closed-form cases. Compared against the engine's `_calculate_annualized_volatility`
(`analytics/risk.py:2117-2120`) and the new gate helper.

Formula as implemented and as documented (`financial-methodology.md` line 1015,
denominator convention line 995-996):

```
portfolio_volatility_pct = round( stdev_sample(portfolio_daily_returns) * sqrt(252) * 100 , 2 )
stdev_sample = sqrt( sum((r - mean)^2) / (N - 1) )      # risk.py:2129-2135
```

| input series | engine | independent | statistics.stdev | match |
|---|---|---|---|---|
| `[0.01, 0.03]` (N=2) | 22.45 | 22.45 | 22.45 | yes |
| `[0.01, -0.02, 0.015]` (N=3) | 30.05 | 30.05 | 30.05 | yes |
| `[0.005] * 60` (constant) | 0.0 | 0.0 | 0.0 | yes |
| `[0.02]` (N=1) | 0.0 | n/a (undefined) | n/a | see note |

Note on N=1: the reused house path returns `0.0` for `len < 2` (`risk.py:2118`).
This is a genuine defect of that path in isolation, but it is structurally
unreachable on this field: the gate classifies `N=1` as `withheld` before the
value is read, and the helper test feeds `portfolio_volatility_pct=0.0` at
`observations=1` and asserts the field stays `null` and `!= 0.0`
(`test_n_equals_one_never_publishes_a_zero_on_this_field`).

Units: `_pct`, value already `* 100`, `round(_, 2)` — matches the sibling
`volatility_summary.portfolio_volatility_pct` exactly. Annualisation factor
`sqrt(252)`, trading-day count 252 — correct for a daily series. Sign: n/a
(non-negative dispersion). No annualisation applied twice; no percent/fraction
confusion.

**Reuse, not recomputation.** `_build_risk_tab_annualized_volatility`
(`diagnostics_engine.py:439-474`) never calls `_calculate_annualized_volatility`
or anything in `analytics/`. At `N >= 60` it assigns
`annualized_volatility_pct = risk_summary.portfolio_volatility_pct` — the same
object's value. `test_published_value_is_byte_identical_to_risk_summary_scalar`
asserts `.hex()` equality; the integration test asserts `==` against both
`volatility_summary.portfolio_volatility_pct` and
`risk_summary.portfolio_volatility_pct` in one response. Guardrail 2 satisfied:
one documented formula, one executable path, the Risk-tab surface is a pure
publication gate over it.

Duplicate-formula hunt (grep `sqrt(252)` / `annualiz` / `_calculate_annualized_volatility`
across `app/`): no second implementation. US-44.1 adds none.

---

## § A2 The 60-observation floor

**Placement.** `_build_risk_tab_annualized_volatility` runs inside the
diagnostics engine on both construction paths — the populated path
(`diagnostics_engine.py:415`, after `risk_summary` is built) and
`build_unavailable_diagnostics_result` (`:539`). It classifies on
`risk_summary.observations` **before** any value is selected. This is exactly
what 02 § 3.3 and 05 § 4 require ("the gate must sit before
`_calculate_annualized_volatility`"): the `len < 2 -> 0.0` branch can never
reach this field.

**Constant.** `RISK_TAB_ANNUALIZED_VOL_MIN_OBSERVATIONS = 60` in
`core/constants.py` with a disambiguation comment separating it from
`MIN_DAILY_OBSERVATIONS` (20) and `risk.py`'s `WINDOW_MIN_OBSERVATIONS`
(`{20:25, 60:75, 252:275}`), and citing `02 § 2.4` for the value. No literal
`60` in the engine or frontend; the frontend reads `minimum_observations` off
the payload. Tests reference the constant by name; the literal is pinned in one
dedicated test (`test_floor_constant_value_is_pinned`).

**Ruling — paired `observations` vs unpaired `return_count`
(06 risk:2, 05 § 9):** gating on the paired count is **correct**, not a defect.

`build_portfolio_risk_summary` computes
`portfolio_volatility_pct = _calculate_annualized_volatility(portfolio_samples)`
where `portfolio_samples = [item[1] for item in paired_returns]` and
`observations = len(paired_returns)` (`risk.py:493, 503, 507`). The published
statistic's own sample size **is** `observations`. Applying the 60-floor to
`observations` therefore means "the estimate rests on at least 60 data points",
which is precisely the estimation-error argument in 02 § 2. Gating on the
distribution engine's `return_count` would gate on a *different* series
(unpaired, population-N standard deviation, potentially a different return
basis) than the one being published — that would be the defect. The consequent
asymmetry (VaR card populated at unpaired N>=20 while this figure withholds at
paired N<60) is the intended stricter floor, visible by design.

Benchmark pairing can only *drop* portfolio-return days (benchmark gaps), so
`observations <= raw portfolio-return count`: the floor is, if anything,
marginally more conservative than a portfolio-only count would be — safe under
guardrail 4.

---

## § A3 Trust semantics & edge cases

Verified numerically via the helper across `N in {-1, 0, 1, 30, 59, 60, 252}`
and via the two integration tests (`run_diagnostics_engine` at ~6 months and
~3 weeks of the conftest synthetic series).

| N (paired) | trust | value | correct? | falsifying observation the test produces |
|---|---|---|---|---|
| `<= 0` | `unavailable` | `null` | yes | `observations=0` with `portfolio_volatility_pct=None` -> asserts `unavailable`/`null`; also `build_unavailable_diagnostics_result` path |
| `1 .. 59` | `withheld` | `null` | yes | parametrized `[1,2,30,58,59]` **with a real 18.2 on the risk summary** -> asserts value stays `None` (a value-based gate would leak 18.2) |
| `1`, `portfolio_volatility_pct=0.0` | `withheld` | `null` | yes | explicitly feeds the reused path's `0.0` -> asserts `None` and `!= 0.0` (AC 11) |
| `>= 60` | `synthetic` | copied `%` | yes | `[60, 61, 252]` -> asserts `float`, `== risk_summary` scalar, `.hex()` identity |
| `>= 60`, variance 0 | `synthetic` | `0.0` | yes (human ruling) | constant series at floor -> asserts `synthetic` + `0.0`, no withheld branch |
| withheld vs unavailable | distinct strings | — | yes | `model_dump()` and `model_dump_json()` differ; withheld JSON contains `"withheld"`, not `"unavailable"` (AC 10, guardrail 4) |

`withheld` is never collapsed to `unavailable` — proven at the serialization
boundary, which is the level the guardrail is about. Below the floor the field
carries no number, no `0`, no `-` (frontend `EmptyState`, asserted in
`AnnualizedVolatilityCard.test.tsx` per 08 handoff). The empty portfolio /
no-history / window-longer-than-history cases all resolve to `unavailable` or
`withheld` with a null value — no plausible-looking number in any degenerate
case.

Single holding at `N >= 60`: defined and published — the statistic is the
stdev of the portfolio return series, not a cross-sectional aggregate, so there
is no divide-by-holding-count; the integration test runs a single AAPL position
and publishes at `N >= 60`.

---

## § A4 Methodology amendment check

The amendment is written by the docs lane at close-out; this gate audits that
the text 05 § 7 row 1 / 06 contract_notes describe is *correct*, so the docs
lane does not encode a wrong statement.

Every clause checks out against the code:

- "Risk-tab surface requires `N >= 60` paired daily-return observations" —
  gate is `observations < floor -> withheld`, else `synthetic`; `observations == 60`
  publishes. Correct.
- "`N = 0 -> unavailable`, `1 <= N < 60 -> withheld` (never collapsed),
  `N >= 60 -> published (synthetic)`" — matches `_build_risk_tab_annualized_volatility`
  exactly.
- "zero-variance at `N >= 60` publishes 0.00%" — no `vol == 0` branch; the
  `synthetic` path carries `0.0` through. Matches, and matches the human ruling.
- "Dashboard surface unchanged and retains no explicit floor" — `risk.py` is
  not in 06's `changed` list; `build_portfolio_risk_summary` and
  `volatility_summary.portfolio_volatility_pct` are untouched; the Dashboard
  figure is still non-null from `N >= 2` (regression asserted in the
  below-floor integration test).
- "constant distinct from `MIN_DAILY_OBSERVATIONS`" — separate constant,
  separate value (60 vs 20), disambiguation comment present.
- "cite `02 § 2.4`" — the constant's comment and the helper docstring both
  cite it.

The amendment is an edit to an existing section ("Annualized realized
volatility", line 1012) whose content this run specifies — within the docs
lane's remit, not flag-for-human.

---

## § A5 Truth-class

Synthetic History throughout: the source `daily_states` on the Risk-tab
diagnostics path are current holdings valued over historical prices (no trade
replay). The contract literal is `synthetic | withheld | unavailable` — the
model can never express `verified` or `degraded` (AC 3). The card's `synthetic`
`TrustBadge` tooltip states the basis ("current holdings applied to historical
prices"). No field on `RiskTabAnnualizedVolatility` carries a broker-truth or
snapshot-analytics value; the "Dashboard shows an unfloored estimate" line in
the withheld copy refers to the *same* synthetic scalar on the other surface,
which is a cross-reference, not a truth-class mix. Guardrail 3 holds.
