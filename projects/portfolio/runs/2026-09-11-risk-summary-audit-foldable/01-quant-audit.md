REPORT 2026-09-11-risk-summary-audit-foldable/01
status:      DONE
verdict:     FAIL

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Order's verification field was NONE (read-only audit). Independent recomputation done via ad-hoc Python against `app.analytics.risk`, logged in § Independent recomputation log. 3 CRITICAL, 1 MATERIAL, 1 MINOR findings below.

contract_notes:
  - docs/contracts/dashboard-fields.md:238,287 assert diagnostics drawdown is "a separate, unwithheld path" — this is false against current code (see FINDING 1). Needs correction or the code needs an owner decision to actually unwithhold it.
  - docs/contracts/dashboard-fields.md:242 describes Information Ratio/Active Return as individually-nullable on genuine math grounds — the code withholds them unconditionally regardless of math (see FINDING 2); doc needs to state the unconditional gate explicitly, or the gate needs an owner decision.

pack_corrections:
  - none

handoff:
  - Human decision needed on `allow_diagnostics_drawdown_outputs()` (trust_gate.py:244-245): deliberate permanent withholding, or a bug — see FINDING 1.
  - If deliberate, docs/contracts/dashboard-fields.md:238,287 must stop calling this the "unwithheld" drawdown path.
  - Human decision needed on `_allow_diagnostics_relative_return_outputs()` (diagnostics_engine.py:187-188): same question — see FINDING 2.
  - Human decision needed: should `section_trust.risk_contribution_path` be relabelled (e.g. "adjusted-close basis") so it cannot read as overall truth-class verification — see FINDING 3.

risks:
  - No live/cached-market-data route run was possible (pytest.ini disables sockets); recomputation used `app.analytics.risk` called directly with hand-built fixtures — see § Independent recomputation log.
  - The withholding-gate findings (1, 2) rest on reading the gate functions' source plus existing route tests, not a fresh route call — both gates are argument-less and unconditionally `False`, so no live scenario changes that fact.
  - Scoped to the Risk Summary card only, per non_goals; `risk_tab_volatility` and other Risk-tab cards were read only to disambiguate a same-named field, not audited.

## Orchestrator brief
- Verdict: FAIL. 3 CRITICAL findings block, in § Findings.
- F1 (CRITICAL): Current/Max Drawdown always null — doc's "unwithheld path" claim (dashboard-fields.md) is false.
- F2 (CRITICAL): Information Ratio/Active Return always null (unconditional gate), not "individually null" per doc.
- F3 (CRITICAL): `risk_contribution_path` badge can read "Verified" on structurally-synthetic HHI/risk-share metrics.
- F4 (MATERIAL): Portfolio/Benchmark Volatility return `0.0` not `null` at N=1, unlike sibling beta/correlation/R² fields.
- F5 (MINOR): HHI formula duplicated verbatim in `risk.py` and `exposure_engine.py`, null-handling diverges.
- § Metrics inventory (Risk Summary card, `RiskSummaryCard.tsx`): one row per rendered field, formula doc + code path.
- § Findings: full CRITICAL/MATERIAL/MINOR write-ups with file:line, claim/actual/impact/expected.
- § Independent recomputation log: hand-computed and degenerate-case anchors, all published math reproduced exactly.
- No arithmetic bugs in published numbers — every CRITICAL is a trust/withholding-honesty defect, not a wrong value.

## Metrics inventory (Risk Summary card, `RiskSummaryCard.tsx`)

| # | UI label | Field | Formula source | Code path |
|---|---|---|---|---|
| 1 | Portfolio Volatility | `volatility_summary.portfolio_volatility_pct` | methodology.md §Annualized realized volatility | `risk.py:507` → `_calculate_annualized_volatility` |
| 2 | Tracking Error | `volatility_summary.tracking_error_pct` | methodology.md §Tracking error | `risk.py:750` → `_calculate_annualized_volatility` on active returns |
| 3 | Downside Volatility | `volatility_summary.downside_volatility_pct` | methodology.md §Downside volatility | `risk.py:1175` → `_calculate_downside_deviation`, 60d window |
| 4 | Benchmark Volatility | `volatility_summary.benchmark_volatility_pct` | methodology.md §Annualized realized volatility | `risk.py:508` |
| 5 | Current Drawdown | `drawdown_summary.current_drawdown_pct` | n/a — always null, see F1 | `diagnostics_engine.py:405-408`, `trust_gate.py:244-245` |
| 6 | Max Drawdown | `drawdown_summary.max_drawdown_pct` | n/a — always null, see F1 | same |
| 7 | Factor HHI | `risk_concentration_summary.factor_hhi` | methodology.md §Herfindahl-Hirschman Index | `risk.py:886` → `_herfindahl_index` |
| 8 | Position HHI | `risk_concentration_summary.position_hhi` | same | `risk.py:887` |
| 9-12 | Top-1/3 Factor, Top-1/5 Position Risk Share | `risk_concentration_summary.top_*_risk_share` | methodology.md §Risk share | `risk.py:882-885` → `_sum_top_risk_shares` |
| 13 | Information Ratio | `relative_risk.information_ratio` | methodology.md §Information Ratio | n/a — always null, see F2 |
| 14 | Active Return | `relative_risk.active_return_pct` | same struct, compounded-return definition | n/a — always null, see F2 |
| — | "Risk contribution basis" label | `run_metadata.section_trust.risk_contribution_path` | trust_gate.py §build_diagnostics_section_trust | see F3 |

## Findings

```
FINDING 1
severity:   CRITICAL
where:      services/quant-engine/app/services/trust_gate.py:244-245 (allow_diagnostics_drawdown_outputs, unconditional `return False`);
            services/quant-engine/app/services/diagnostics_engine.py:339-343,405-408 (applies the gate to drawdown_summary);
            docs/contracts/dashboard-fields.md:238,287 (the contradicted claim)
claim:      dashboard-fields.md:238 — "diagnostics' drawdown is a separate, unwithheld path"; line 287 (Accuracy Rule 6) — "RiskSummaryCard sidesteps this by sourcing drawdown from the separate, unwithheld diagnostics path instead."
actual:     `allow_diagnostics_drawdown_outputs()` takes no arguments and unconditionally returns `False`. Every call to `apply_diagnostics_drawdown_output_policy` therefore nulls `current_drawdown_pct` and `max_drawdown_pct` on every diagnostics run, with no condition on trust, return-basis, or history depth. Confirmed against every route test that touches this field: `test_routes.py:595-598`, `:1088-1089`, `:2546-2547`, `:2739` — all assert `drawdown_summary == {"current_drawdown_pct": None, "max_drawdown_pct": None}`; no test anywhere asserts a non-null value for these fields via the diagnostics route. This is the same permanently-closed-gate pattern the quant capability pack already documents for the *dashboard-history* drawdown family (`_allow_dashboard_drawdown_outputs`), just on a second, separate gate for the *diagnostics* drawdown family that the pack does not yet list.
impact:     A researcher reading the contract doc would believe the Risk Summary card's Current/Max Drawdown are a genuine, unwithheld alternative to the withheld dashboard-history drawdown figure. In the shipped product this row is `n/a` unconditionally, indistinguishable in the UI from any other missing value — the card gives no indication this field is being withheld by policy rather than being unavailable due to data gaps. This is exactly the guardrail-4 violation ("never collapse withheld into unavailable") applied to a field the doc explicitly and twice asserts is *not* subject to that policy.
expected:   Either (a) the doc is wrong and must be corrected to state the diagnostics drawdown path is also permanently withheld, with the same "no amount of data-quality work un-gates this" language the pack already uses for the dashboard-history sibling, or (b) the gate is a bug/regression against its own intended design and needs an owner decision to actually condition it (e.g., on `section_trust.risk_contribution_path` or an explicit trust rung) rather than hard-coding closed. This is a human decision, not a fix I can make read-only.
```

```
FINDING 2
severity:   CRITICAL
where:      services/quant-engine/app/services/diagnostics_engine.py:187-188 (_allow_diagnostics_relative_return_outputs, unconditional `return False`);
            :191-204 (_apply_diagnostics_relative_return_output_policy nulls both fields when the gate is closed);
            docs/contracts/dashboard-fields.md:242
claim:      dashboard-fields.md:242 — rows are "omitted entirely (not n/a) when tracking_error_pct is null ... n/a per individually-null field otherwise", i.e. it describes Information Ratio / Active Return as fields that render their real computed value when tracking error is present, falling back to `n/a` only for their own individual math edge cases (per financial-methodology.md §Information Ratio: fewer than 2 paired returns, or tracking_error == 0).
actual:     `_allow_diagnostics_relative_return_outputs()` takes no arguments and unconditionally returns `False`, so `active_return_pct` and `information_ratio` are nulled on every diagnostics run regardless of whether `build_relative_risk_summary` (risk.py:744-770) actually computed real, non-null values. `RiskSummaryCard.tsx:61` computes `showRelativeRisk = vol.tracking_error_pct != null` and renders both rows whenever tracking error is present (lines 119-129) — but `rel.information_ratio` / `rel.active_return_pct` are structurally always null at that point, so the exact "coherence-breaking n/a beside a real number" pattern the component's own comment (lines 58-60) says it exists to avoid is what actually ships: Tracking Error shows a real percentage while Information Ratio and Active Return beside it always read "n/a". `test_analytics.py:4241-4242` proves the underlying math is real and non-null at the `risk.py` layer (`build_relative_risk_summary` directly); the diagnostics-engine policy gate discards it before it reaches the route or the card.
impact:     A researcher sees Tracking Error populated with a real number and, right beside it, Information Ratio / Active Return as "n/a" with no explanation — reading as "insufficient data" or "not computed" rather than "computed but withheld by policy." The doc's characterization that these are only conditionally null "per individually-null field" materially understates how these fields actually behave: they are unconditionally withheld, full stop, independent of data quality.
expected:   Same as Finding 1: either the doc must state plainly that these two fields are permanently withheld pending an investor-economics unlock decision (consistent with `run_metadata.investor_economics_status`, which the diagnostics engine does correctly set to "withheld" whenever this gate is closed — see `trust_gate.py:289-301` — but which the card never reads or surfaces), or the gate needs an owner decision to actually condition on trust state.
```

```
FINDING 3
severity:   CRITICAL
where:      services/quant-engine/app/analytics/risk.py:1911-1929 (_build_position_risk_contributions: weights sourced from `snapshot.positions`/`position_base_market_values` — CURRENT holdings — applied to `price_histories` — historical daily returns);
            services/quant-engine/app/services/trust_gate.py:217-241 (build_diagnostics_section_trust: risk_contribution_path is driven solely by benchmark/factor adjusted-close proof, with no reference to the fact that position/factor risk contributions are always a current-weights-times-history construction);
            apps/desktop/src/features/portfolio/RiskSummaryCard.tsx:19-30,57,68 (renders `section_trust.risk_contribution_path` as a plain "Verified"/"Degraded"/"Unavailable" label)
claim:      Project guardrail 3 (and the identical wording in this audit's own brief): "current holdings × historical prices" is synthetic history, "at most synthetic, never verified" — not negotiable, not a judgment call. `docs/contracts/dashboard-fields.md:239-240` independently classifies Factor HHI/Position HHI/top-N risk shares as truth class "engine-derived, synthetic-history basis" in its own table.
actual:     `_build_position_risk_contributions` computes `weights` from the CURRENT snapshot's positions (`position_base_market_values(snapshot)`, `risk.py:1916-1917,1925-1928`) and multiplies them against a historical return-covariance matrix built from `price_histories` (fetched independently of the replay/synthetic branch split). This is unconditionally a "current holdings × historical prices" construction — the guardrail's own definition of synthetic history — on BOTH the `imported_portfolio_history` and `market_data_history` provenance branches, because `symbol_price_histories` is fetched once for current holdings regardless of which branch runs (`diagnostics_engine.py:645-649`). Yet `risk_contribution_path` (which the card labels "Risk contribution basis") is computed purely from `benchmark_return_basis`/`factor_return_basis` (`trust_gate.py:230-236`) — i.e. whether the *benchmark and factor* histories happen to carry adjusted-close fields — and can read `verified_adjusted_close`, which `RiskSummaryCard.tsx` renders as the plain word "Verified" (line 24), with no reference anywhere on the card to `provenance.historical_basis` or to the current-weights construction underneath.
impact:     Whenever FMP/Yahoo return adjusted-close rows for the benchmark and factor proxies (a common, not edge, case), the card displays "Risk contribution basis: Verified" directly above Factor HHI, Position HHI, and all four top-N risk-share figures — numbers that are, by the project's own guardrail, at most synthetic. A researcher has no way, from this card alone, to learn that these numbers assume today's portfolio was held throughout history. This is the specific failure mode the quant capability pack's definition-of-done calls out by name: "synthetic-history outputs never claim verified."
expected:   The `risk_contribution_path` trust rung (or its UI label) must not use the word "Verified"/"verified_adjusted_close" for a truth-class that the same doc elsewhere calls synthetic-history basis. At minimum this needs a distinct label (e.g. "adjusted-close basis: Verified" scoped explicitly to price-field provenance, not overall trust) or the card must additionally surface `provenance.historical_basis` so "current-holdings-times-history" is visible next to the badge. This is a design decision for the owner, not a read-only fix.
```

```
FINDING 4
severity:   MATERIAL
where:      services/quant-engine/app/analytics/risk.py:507-508 (`if portfolio_samples else None` / `if benchmark_samples else None` — truthy-list guard, not a `len >= 2` guard);
            services/quant-engine/app/analytics/risk.py:2117-2120 (`_calculate_annualized_volatility`: `if len(values) < 2: return 0.0`);
            contrast with risk.py:2098-2114 (`_calculate_beta`/`_calculate_correlation`, same `PortfolioRiskSummary` struct, correctly `return None` at N<2)
claim:      Pack edge-case table: "variance = 0 (constant series): null, not 0 and not 1"; "never resolve an edge case with a fallback value... missing input produces an unavailable output, not a zero." financial-methodology.md documents (line 1054-1060) that the Dashboard's `portfolio_volatility_pct` "publishes from N ≥ 2 and returns 0.00% at N = 1" as current behavior, but grounds this only for the N≥60 constant-series case (the chi-square-distribution "human ruling," US-44.1 open decision 2) — it does not ground the N=1 case with any citation or rationale.
actual:     Independently reproduced: with exactly 2 daily states (1 paired daily return), `build_portfolio_risk_summary` returns `portfolio_beta=None`, `portfolio_correlation=None`, `r_squared=None` (correctly null — a single observation cannot support a variance/covariance estimate) but `portfolio_volatility_pct=0.0`, `benchmark_volatility_pct=0.0` in the SAME struct, for the SAME reason (N=1 insufficient to estimate a dispersion statistic with an N−1 denominator). Verified by direct call:
            `build_portfolio_risk_summary([2 states], [2 bench rows], "SPY")` → beta/correlation/r_squared = None, portfolio_volatility_pct = 0.0, benchmark_volatility_pct = 0.0.
impact:     A freshly-imported portfolio with only one prior trading day of history would show "Portfolio Volatility: 0.00%" — reading as "this portfolio has zero risk" — while the mathematically identical insufficiency shows correctly as "n/a" for Beta/Correlation/R² elsewhere in the same payload. This is exactly the "plausible-looking number in a degenerate case… the worst possible outcome in this system" the pack warns about, and it is internally inconsistent within one function.
expected:   `portfolio_volatility_pct`/`benchmark_volatility_pct` should be `null` at N<2 paired observations, matching `_calculate_beta`/`_calculate_correlation`'s existing convention in the same struct. The doc's "returns 0.00% at N=1" sentence documents the current bug rather than grounding it — it carries no citation, unlike the adjacent N≥60 constant-series ruling it sits next to.
```

```
FINDING 5
severity:   MINOR
where:      services/quant-engine/app/analytics/risk.py:2031-2035 (_herfindahl_index, filters None before summing);
            services/quant-engine/app/services/exposure_engine.py:257-260 (_herfindahl_index, does not filter None)
claim:      Pack: "Duplication of a formula is a specific, recurring defect class in this codebase." financial-methodology.md:1868-1872 acknowledges two HHI call sites exist ("Both use the same Σw² formula shape") as an intentional distinction between the risk-contribution HHI and the Exposure-tab position HHI.
actual:     Both are separately-defined, byte-identical `sum(v*v for v in values), round(...,4)` implementations, one per module, with no shared helper. The two functions handle `None` inputs differently: `risk.py`'s version filters `None` before summing (`risk.py:2032`); `exposure_engine.py`'s version has no `None` guard on the elements (would raise a `TypeError` if ever given a list containing `None`, since its type hint claims `list[float]` not `list[float | None]`).
impact:     Currently harmless (doc-acknowledged as two distinct metrics with different, currently non-None-bearing inputs), but it is the exact un-consolidated-formula shape the pack flags as the pattern to hunt, and the two implementations could silently diverge on a future edit to one but not the other.
expected:   Not blocking. Consider extracting a shared `_herfindahl_index(values: list[float | None]) -> float | None` helper if either module is touched again for a related reason.
```

## Independent recomputation log

All of the following were run directly against `services/quant-engine/app/analytics/risk.py` functions (no route/socket access — `pytest.ini` disables sockets, per the capability pack), using hand-built `DailyPortfolioState`/benchmark-row fixtures, `anchor: closed-form hand-computed` / `anchor: methodology-doc` as labelled.

1. **Portfolio/benchmark volatility, anchor: closed-form hand-computed.** 3-day series (1000→1010→1030.2 portfolio; 100→101→102 benchmark). My independent Python re-implementation of `stdev(returns, N−1) * sqrt(252) * 100` produced `portfolio_volatility_pct = 11.22`, `benchmark_volatility_pct = 0.11`, matching `build_portfolio_risk_summary`'s output exactly.
2. **Tracking error / Information Ratio / active return, anchor: closed-form hand-computed.** Reproduced by hand the existing regression fixture in `test_analytics.py:4245-4281` (portfolio returns 0.03/0.01, benchmark 0.01/0.005): tracking_error = 0.0075·√2·√252 = 16.8374% → rounds 16.84; IR = 0.0125·252/0.168374 = 18.7086 → rounds 18.71; compounded active return = (1.03·1.01 − 1.01·1.005)×100 = 2.525 → rounds 2.52. All three match the code's output exactly. This also confirms the methodology doc's §Information Ratio formula (`(mean_active × 252) / tracking_error`) is implemented correctly.
3. **Degenerate cases, anchor: degenerate/closed-form.**
   - Constant portfolio and benchmark value over 5 days → `portfolio_volatility_pct = 0.0`, `benchmark_volatility_pct = 0.0`, `tracking_error_pct = 0.0`, `information_ratio = None` (correctly null — division by zero tracking error, never fabricated), `active_return_pct = 0.0`. Matches methodology.md's documented "realized volatility over a constant series is well-defined and exactly zero" ruling and the IR null-on-zero-tracking-error rule.
   - Empty daily-state list → `observations = 0`, `portfolio_volatility_pct = None`. Correct.
   - Single daily state (0 paired returns) → `observations = 0`, `portfolio_volatility_pct = None`. Correct.
   - Two daily states (1 paired return, N=1) → `observations = 1`, `portfolio_beta/correlation/r_squared = None` (correct), but `portfolio_volatility_pct = 0.0` / `benchmark_volatility_pct = 0.0` — see Finding 4.
4. **HHI / top-N risk share, anchor: methodology-doc consistency + degenerate cases.** `_herfindahl_index([1.0]) = 1.0`, `_sum_top_risk_shares([1.0], 1) = 1.0`, `_sum_top_risk_shares([1.0], 5) = 1.0` (single-holding concentration = 1.0, correct — no divide-by-zero). `_herfindahl_index([]) = None`, `_sum_top_risk_shares([], 3) = None` (empty portfolio → unavailable, not 0). Matches methodology.md §Herfindahl-Hirschman Index and §Risk share exactly, including the documented `[0,1]` fraction convention that `RiskSummaryCard.tsx`'s `formatShareAsPct` correctly multiplies by 100 (and `formatRatio` for HHI correctly does not).
5. **Withholding gates, anchor: repo test suite + direct source read (not the methodology doc).** `allow_diagnostics_drawdown_outputs()` and `_allow_diagnostics_relative_return_outputs()` are argument-less functions with a bare `return False`; grepped for every call site and every route test touching `drawdown_summary`/`relative_risk.{information_ratio,active_return_pct}` in `test_routes.py` — none assert a non-null value via the diagnostics route. This is an anchor independent of the methodology doc (I read the gate functions and the test suite, not the doc's characterization of them) — see Findings 1 and 2.
