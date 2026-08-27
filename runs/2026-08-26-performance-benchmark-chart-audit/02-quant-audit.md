REPORT 2026-08-26-performance-benchmark-chart-audit/02
status:      DONE
verdict:     FAIL

changed:
  - none

verification:
  command:   cd services/quant-engine && python -m pytest app/tests/test_analytics.py -k "dashboard_history or run_imported_dashboard" -v
  result:    PASS
  detail:    22 passed, 193 deselected in 1.55s. Suite is green; it does not exercise the chart's indexed line at all (only range_metrics scalars), which is why FINDING 1 shipped without a failing test.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - FINDING 1 (CRITICAL) is a frontend-only fix: use the already-served `portfolio_return_pct` field per point instead of `portfolio_value` — see § Findings.
  - FINDING 2 (MINOR): resolve `DashboardPanel.tsx::normalizePerformanceSeries` (dead, same wrong formula) in the same pass as FINDING 1 — see § Findings.

risks:
  - The six `range_metrics` summary scalars (TWR, MWR, Net Contributions, Portfolio Value, Benchmark Return, Excess Return) are all correct — independently recomputed and matched exactly; not blocking, listed for completeness in § Findings.
  - `dashboard-fields.md:219` and the code comment at `PerformanceBenchmarkCard.tsx:44` both assert conformance to §Indexed Return Series that the code does not have — the contract doc is not wrong, the code is; do not "fix" the doc.

## Orchestrator brief
- Verdict: FAIL. One CRITICAL (chart's portfolio line uses the wrong basis), one MINOR (dead duplicate of the same wrong formula).
- Scout's flagged discrepancy is confirmed real, not a documentation-scope question: `dashboard-fields.md:219` explicitly cites §Indexed Return Series as governing this exact chart.
- Fix is frontend-only, no backend/schema change: the correct field (`portfolio_return_pct`) is already in the API payload and TS type, just unused.
- § Findings: full FINDING 1 (CRITICAL, chart line) and FINDING 2 (MINOR, dead duplicate) blocks, with the recomputation. Route FINDING 1 to `frontend-engineer`.
- § Independently verified correct (no finding): the six summary scalars beneath the chart (TWR, MWR, Net Contributions, Portfolio Value, {Symbol} Return, Excess Return) — all recomputed and matched exactly, not in scope for a fix.

## Findings

FINDING 1
severity:   CRITICAL
where:      apps/desktop/src/features/portfolio/PerformanceBenchmarkCard.tsx:48-67 (`buildIndexedSeries`), duplicated in apps/desktop/src/features/portfolio/DashboardPanel.tsx:34-51 (dead, see FINDING 2)
claim:      Code comment (line 44) and `docs/contracts/dashboard-fields.md:219` ("base-100 rebasing per §Indexed Return Series") both assert the chart's portfolio line follows `financial-methodology.md` §Indexed Return Series (line 2176).
actual:     That section requires the portfolio line be a TWR-indexed chain (`indexed_t = indexed_{t-1} * (1 + daily_return_t)`, line 2186-2194) and explicitly bars raw market value ("Raw market value is NOT a valid portfolio line: a deposit/withdrawal/trade would draw a move against the benchmark's price line that is not performance"). `buildIndexedSeries` instead computes `(p.portfolio_value / anchorPortfolio) * 100` — a raw NAV ratio. I ported the function 1:1 to Python and ran it against the engine's real `build_true_performance_series` output (script + full output logged; two checks):
            (a) Synthetic: flat market (benchmark and holdings never move), one $50,000 deposit mid-period on a $100,000 base. True TWR = 0.0% for the whole period (deposit is not a gain) — cross-checked against a from-scratch hand implementation of the methodology's own daily-return formula, exact match with the engine (`portfolio_return_pct` = [0.0, 0.0, 0.0, 0.0]). The chart, on the SAME engine output, draws a final indexed point of 150.0 — a fabricated +50 percentage-point "gain" from a pure cash deposit.
            (b) Realistic: the repo's own `PerformanceBenchmarkCard.test.tsx` fixture (start_value=52386.10, end_value=65168.77, net_contributions=9963, true TWR=2.43%). Chart's raw-value indexed final point = 124.40 (implying +24.40%); correct TWR-indexed final point = 100*(1+2.43/100) = 102.43 (+2.43%, the number printed directly below the chart in the same card). Overstatement: 21.97 percentage points — the chart shows ~10x the true performance.
impact:     Any portfolio with a net deposit or withdrawal during the displayed window shows a chart trajectory that visually contradicts the correct Time-Weighted Return scalar printed directly beneath it in the same card — a researcher reading the chart alone would conclude the portfolio gained roughly 10x what it actually did. The "Portfolio: Replay-derived" trust label rendered directly above the chart (line 115) implies the visual reflects that return-basis pedigree; since the line is not built from any return calculation at all, the label overstates what the chart represents — this is a trust-classification problem (guardrail 4), not only an arithmetic one.
expected:   Build the portfolio line from the already-computed, already-served `portfolio_return_pct` field on each `performance_series` point: `indexed_t = 100 * (1 + portfolio_return_pct_t / 100)`, with the existing null-propagation/gap semantics preserved (§Indexed Return Series edge cases, line 2242-2250). No backend change needed — `build_true_performance_series` (`services/quant-engine/app/analytics/performance.py:298-359`) already computes this exact TWR chain and it is already in the response schema (`PerformancePoint`, `app/schemas/reconciliation.py:510-515`) and the TS type (`types.ts:544-550`); the frontend is simply reading the wrong field. The benchmark leg is unaffected — raw-price indexing (`p.benchmark_price / anchorBenchmark * 100`) IS the doc-correct formula for a price series with no cash flows, and `benchmark_return_pct` is deliberately withheld server-side (`_withhold_benchmark_return_series`, `dashboard_history_engine.py:396-397`) precisely because the chart is expected to index the raw price itself — only the portfolio leg needs to change.

FINDING 2
severity:   MINOR
where:      apps/desktop/src/features/portfolio/DashboardPanel.tsx:34-51 (`normalizePerformanceSeries`)
claim:      n/a — exported function, not asserted to be correct anywhere.
actual:     Bit-for-bit the same wrong raw-market-value formula as FINDING 1 (`point.portfolio_value / anchorPortfolioValue * 100`). Grepped the whole frontend feature dir for the anchor pattern: exactly two copies exist, this one and `PerformanceBenchmarkCard.tsx`. This one is dead — its only reference anywhere is its own test, `DashboardPanel.test.tsx:172` (confirmed by grep; not called from any render path).
impact:     No live UI impact today (confirmed unused). Drift risk: a second copy of a wrong formula is a trap for a future engineer who fixes one copy, assumes the other is a working reference, and leaves it in place or wires it up unchanged.
expected:   When fixing FINDING 1, either delete this function and its test, or apply the identical fix here and actually wire it in. Do not leave two implementations, one fixed and one not.

## Independently verified correct (no finding)

Six `range_metrics` summary scalars, each recomputed from scratch against `financial-methodology.md`'s stated formula and cross-checked against the real engine function on the same synthetic ($100,000 base, $50,000 mid-period deposit, flat benchmark) and degenerate (flat/zero-return) inputs — all matched exactly:

- Time-Weighted Return (`time_weighted_return_pct`) — `dashboard_history_engine.py::_range_time_weighted_return_pct` (line 871), re-basing via `(1+c_end)/(1+c_start)-1` per §Portfolio Return Methodology (line 503-507). Hand chain matched engine chain exactly on the synthetic case (both 0.0% throughout).
- Money-Weighted Return / Modified Dietz (`money_weighted_return_pct`) — `_compute_money_weighted_return` (line 835), matches §Money-Weighted Return (line 509-543) formula verbatim including day-weighted `w_i`; hand computation matched engine to the tested precision (0.0000% on the synthetic case, denominator/weights confirmed by formula substitution).
- Net Contributions (`net_contributions`) — plain sum of `external_cash_flow` over anchored states after the first (line 936); hand sum matched engine exactly (50000.0).
- Portfolio Value (`end_value`) — raw `daily_states[-1].total_portfolio_value`, correctly includes the terminal reconciliation per US-34.6 (the card's own reconciliation-adjustment disclosure banner, `PerformanceBenchmarkCard.tsx:204-212`, correctly explains why this then does not reconcile against Net Contributions + gain by subtraction).
- Excess Return (`excess_return_pct`) — literal `time_weighted_return_pct - benchmark_return_pct` per §Mixed-basis portfolio-vs-benchmark comparison (line 719-731); confirmed both algebraically (code) and by hand subtraction on the synthetic case (0.0 - 0.0 = 0.0).
- {Symbol} Return (`benchmark_return_pct`) — same re-basing code path as TWR (`_range_time_weighted_return_pct` parameterised on the benchmark field), correctly returns 0.0% on a flat benchmark.

Anchor used for all six: `anchor: methodology-doc` (formula re-derivation) plus `anchor: hand-computed degenerate case` (a synthetic input whose correct answer — 0% TWR/MWR/excess on a pure cash deposit with a flat market — is knowable without the code, per the pack's external-anchor rule). Both the closed-form check and the engine's real functions were run in the same script for a direct comparison, not read separately.

`normalizePerformanceSeries` dead-code question (definition_of_done item 4): confirmed no live correctness risk today — it is unused in any render path, and is a MINOR finding (FINDING 2) purely for drift risk, not a live number.
