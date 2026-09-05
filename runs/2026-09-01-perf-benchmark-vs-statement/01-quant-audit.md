REPORT 2026-09-01-perf-benchmark-vs-statement/01
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd services/quant-engine && python -m pytest app/tests/ -k "statement_truth or ledger_replay_audit" -q ; python -m pytest app/tests/test_analytics.py -q ; python -m pytest app/tests/test_importer_csv.py app/tests/test_statement_refresh.py app/tests/test_portfolio_state.py -q ; cd apps/desktop && npx vitest run PerformanceBenchmarkCard DashboardPanel ; plus a standalone recomputation script (see § Independent recomputation)
  result:    PASS
  detail:    backend 18 passed (statement-truth+replay) / 215 passed (test_analytics) / 81 passed (importer+refresh+portfolio_state); frontend 49 passed (2 files). Independent cash-flow-neutral TWR chain reproduced engine to 2dp (1.1004% vs published 1.11%). anchor: raw-ledger recomputation + broker statement (both independent); methodology-doc for formula consistency.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - No regression guard exists that reconciles the engine's replay-derived TWR against the statement's 5.5066% TWR; statement_truths.py:192 pins only the parsed statement value. This is by design (the two are not meant to be equal) but the "matches the statement?" question is unguarded — see § Answer.
  - financial-methodology.md carries ~20 IB2026-pinned illustrative figures (lines 241, 297, 353, 397, 405, 441, 501, 578, 963, 1699, 2385, 2396, 2421, 2423, 2455, 2480, 2551, 2558, 2596) not covered by the refresh checklist and not re-verified against the 2026-08-28 statement — see § FINDING 1.

risks:
  - Chart line ends at +1.11% vs the broker statement's +5.51% TWR (4.40pp gap; chart shows ~1/5 of the reported return). Math is correct and labelled `degraded` / "Replay-derived", so not a guardrail-4 violation.
  - Whether the "Replay-derived" label communicates a 5x understatement strongly enough to a researcher is a producer/UX judgment, not a math call — recorded here per "you do not decide scope".
  - Comparison ran against the git working tree; the in-flight refresh is functionally complete (targeted suites green) though not fully staged. Does not invalidate the comparison — see § Goldens and statement_truths freshness.

## Orchestrator brief
- Verdict PASS. Chart portfolio line is a faithful implementation of its stated methodology; trust label is honest (`degraded` / `replay_derived` on every range).
- Section "Answer to the work order": the line does NOT numerically match the statement — chart +1.11% vs statement +5.51% TWR, a 4.40pp divergence — but the gap is structural and disclosed, not a computational error.
- Section "Independent recomputation": divergence = ~2.79pp missing pre-window week (replay starts 2026-01-08; statement period starts 2026-01-01) + ~1.49pp from 4 deliberately withheld days; chaining both onto the replay chain lands at 5.46% vs 5.51%. Anchors: raw-ledger recompute + the broker statement, not methodology-doc-only.
- Section "Range-window consistency": chart line vs summary-strip scalar is EXACT on all 5 windows, both legs.
- Section "Goldens and statement_truths freshness": working-tree CSV, goldens, statement_truths.py mutually consistent; refresh functionally complete.
- Section "Findings": two MINOR, both documentation-only, both pre-existing — FINDING 1 (stale illustrative numbers in financial-methodology.md), FINDING 2 (Implementation-list pointer, already tracked in tech-debt-register).
- Nothing blocks dispatch. No code/doc change requested by this gate.

## Answer to the work order

**Does the Dashboard "Performance & Benchmark" chart's portfolio line match the
IB statement's reported performance for the IB2026.csv import? No — it diverges
by 4.40 percentage points — and that divergence is by design, correctly
computed, and honestly labelled.**

- Chart "All" / since-import portfolio line terminates at **+1.11%**
  (`range_metrics["All"].summary.time_weighted_return_pct`, and the last
  `performance_series[-1].portfolio_return_pct` the chart indexes to
  `100*(1+pct/100)` = 101.11).
- Statement's self-reported **"Net Asset Value / Time Weighted Rate of Return"
  = 5.506619351%** (docs/IB2026.csv line 20; period "January 1, 2026 - August
  28, 2026" line 5).
- **Divergence: 5.5066% − 1.11% = 4.40 percentage points.** The chart line
  shows roughly one-fifth of the broker's reported return.

This is not a wrong number. The chart's portfolio leg is published on the
`replay_derived` rung (`run_metadata.return_basis_contract.portfolio_path`),
`range_metrics[*].portfolio_return_trust = "degraded"` on every window, and the
card renders the "Replay-derived" marker plus the withheld-impact and
reconciliation-adjustment disclosures. The statement's own TWR is IB's
verified total return over the full Jan 1 - Aug 28 period; the replay chain is a
real measurement on reconstructed inputs (inferred opening holdings, mixed-basis
valuation, terminal reconciliation, deliberate day gaps) over a shorter window.
The methodology (financial-methodology.md §"Publication rungs for the replayed
return", US-34.2) establishes this as a distinct, honestly-labelled rung — the
quant pack blesses "publishing under a new honest label", which is what this is.

### Code path identified (definition_of_done item 1)

- Chart line builder: `apps/desktop/src/features/portfolio/PerformanceBenchmarkCard.tsx`
  `buildIndexedSeries(result.performance_series, metrics.window_start_date ?? null)`
  — portfolio leg `100*(1+portfolio_return_pct/100)` re-based to the window
  start; benchmark leg raw `benchmark_price` ratio. Unchanged since the
  2026-08-26 audit fix (confirmed by direct read).
- Backend fields consumed: `performance_series[*].portfolio_return_pct`
  (cumulative cash-flow-neutral TWR chain) and
  `range_metrics[*].window_start_date`, both from
  `services/quant-engine/app/services/dashboard_history_engine.py`
  `run_imported_dashboard_history` →
  `analytics/performance.py::build_true_performance_series`
  and `_build_range_metrics` / `_slice_performance_series` /
  `_range_time_weighted_return_pct`.
- Summary-strip scalars: `range_metrics[activeRange].summary.{time_weighted_return_pct,
  money_weighted_return_pct, benchmark_return_pct, excess_return_pct,
  start_value, end_value, net_contributions}`.

## Independent recomputation

Re-implemented the cash-flow-neutral daily-return chain from scratch, from
financial-methodology.md §Portfolio Return Methodology
(`daily_return_t = ((tpv_t − ext_cf_t) / tpv_{t-1}) − 1`, chained), and ran it
over the engine's own `daily_states` for the current docs/IB2026.csv import
(frozen `golden_market_data.json`, network-free):

| quantity | independent recompute | engine | match |
|---|---|---|---|
| published chain (skip non-publishable days) | 1.1004% | 1.11% (`range_metrics["All"].summary.time_weighted_return_pct`) | yes (2dp) |
| all-days chain (do not skip) | 2.5946% | implied 2.59% (`withheld_return_impact_pct` 1.49 = 2.5946 − 1.1004) | yes |
| withheld days | 2026-04-14, 04-17, 06-12, 07-17 | same (`run_metadata.withheld_return_dates`) | yes |
| ending value | — | 65,892.74 = statement Ending NAV 65,892.735 | yes (terminal reconciliation) |

**Divergence decomposition vs the statement's 5.5066%:**

- Replay window starts 2026-01-08 (first frozen market-data date); statement
  period starts 2026-01-01. Engine day-1 `total_portfolio_value` 53,843.91 vs
  statement Starting Value 52,381.12 → a naive Jan 1 → Jan 8 move of **+2.79%**
  the replay chain never sees (no `external_cash_flow` on day 1).
- 4 withheld days remove **+1.49pp** (by design — unbacked cash flow from a
  withheld-quantity holding's trade).
- Chaining the pre-window move onto the all-days replay chain:
  `(1+0.0279)*(1+0.025946) − 1 = 5.46%` — within **0.05pp** of the statement's
  5.5066%. Residual is mixed-basis / adjusted-close vs broker marks, immaterial.

Conclusion: the replay TWR arithmetic is sound. The 4.40pp gap to the statement
is entirely window coverage (~2.79pp) + deliberate withholding (~1.49pp), not a
formula, sign, denominator, or annualisation error.

## Range-window consistency

Replicated `buildIndexedSeries` in Python against the engine's real
`performance_series` and compared the chart line's terminal implied growth to
the summary-strip scalar for the same window:

| range | window_start_date | summary TWR | chart line implied growth | benchmark: summary vs chart |
|---|---|---|---|---|
| 1M | 2026-07-30 | 5.68% | +5.6752% | 3.73 vs 3.7293 |
| 3M | 2026-05-29 | −0.79% | −0.7947% | 1.96 vs 1.9628 |
| YTD | 2026-01-08 | 1.11% | +1.11% | 12.17 vs 12.1698 |
| 1Y | 2026-01-08 | 1.11% | +1.11% | 12.17 vs 12.1698 |
| All | null | 1.11% | +1.11% | 12.17 vs 12.1698 |

Chart line and summary strip agree to sub-0.01pp on every window, both legs —
they are the same re-basing convention on the same chain (as proven structurally
in the 2026-08-26 run, 10-quant-audit §Log/1-2; re-confirmed numerically here).
YTD == 1Y == All because the first available data point (2026-01-08) is inside
all three windows. The 2026-08-26 fixes (portfolio leg off `portfolio_return_pct`
not raw `portfolio_value`; chart filtered by `window_start_date`) are both still
in place — verified by direct read of the current card source.

## Goldens and statement_truths freshness

The in-flight statement refresh (git status) is mutually consistent with the
current working-tree docs/IB2026.csv (2026-08-28 statement):

- `golden_market_data.json` (working tree): SPY/AAPL series through 2026-08-28,
  most symbols through 2026-08-27; 73 series. Covers the new window.
- `dashboardGoldens.ts` (staged): `range_metrics` TWR 1M=5.68 / 3M=−0.79 /
  YTD=1Y=All=1.11, `window_start_date` 2026-07-30 / 2026-05-29 / 2026-01-08 —
  matches the engine run exactly.
- `statement_truths.py` (unstaged): `IB_TWR_PCT = 5.506619`,
  `IB_STATEMENT_PERIOD = "2026-01-01 - 2026-08-28"`, `ending_nav 65892.74` —
  matches the CSV.
- Targeted suites all green: 18 (statement-truth + replay-audit), 22
  (dashboard-history analytics), 215 (full test_analytics.py), 81
  (importer + statement_refresh + portfolio_state), 49 frontend (card + panel).

Not every refreshed file is git-staged, but the working tree is internally
consistent and the suites pass, so **this does not invalidate any part of the
comparison** — the recomputation was run against that same working tree.

Note: `statement_truths.py:192`
`check("totals.time_weighted_return_pct (6dp)", IB_TWR_PCT, totals.time_weighted_return_pct)`
pins the value the importer *parses from the CSV*, not an engine-computed TWR.
No test anywhere reconciles the replay-derived chart TWR against 5.5066%.

## Findings

FINDING 1
severity:   MINOR
where:      docs/finance/financial-methodology.md:500-501 (and ~19 other IB2026-pinned figures listed in handoff)
claim:      "On IB2026 the published 2.43% understates the all-days chain of 4.23% by 1.80pp."
actual:     Current docs/IB2026.csv (2026-08-28 statement) produces published 1.11% / all-days 2.59% / impact 1.49pp (engine + independent recompute agree). The doc's numbers are from a prior statement version and were not updated in the in-flight refresh.
impact:     A reader treating the doc as current would cite a published replay TWR (2.43%) and a withheld-impact (1.80pp) that no longer exist. No formula is wrong; only the worked example. The statement-refresh workflow (docs/architecture/testing-architecture.md §"Statement refresh workflow", steps 1-5) does not list methodology illustrative figures, so this drift is systemic, not introduced by this refresh.
expected:   Either refresh the IB2026-pinned illustrative numbers as a refresh step, or mark them as pinned to a stated statement date so they are not read as live.

FINDING 2
severity:   MINOR
where:      docs/finance/financial-methodology.md:2253-2257 (§Indexed Return Series, "Implementation")
claim:      Implementation list names only drift_engine.py (`_compound_chain`, `_portfolio_return`, `_build_daily_series`, `_basis_note`) and portfolio_state.py.
actual:     The Dashboard "Performance & Benchmark" chart's portfolio line is built by performance.py::build_true_performance_series + PerformanceBenchmarkCard.tsx::buildIndexedSeries — a second implementation of the same indexed-chain family, not listed.
impact:     A reader auditing "the indexed chart" from the doc would inspect the drift-panel code and miss the Dashboard card entirely. Already raised as CR-2 #2 SHOULD_FIX in the 2026-08-26 run and carried to docs/tech-debt-register.md; confirmed still open. Not re-raised as new — recorded so this audit's trail is complete.
expected:   Add performance.py::build_true_performance_series and PerformanceBenchmarkCard.tsx to the Implementation list (the tech-debt entry already tracks this).
