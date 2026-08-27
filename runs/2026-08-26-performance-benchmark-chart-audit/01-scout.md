REPORT 2026-08-26-performance-benchmark-chart-audit/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only recon order; no verification command was named

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Component: `apps/desktop/src/features/portfolio/PerformanceBenchmarkCard.tsx` (229 lines) is the "Performance & Benchmark" chart — confirmed by `aria-label="Performance & Benchmark"` at line 83/109 and by `docs/contracts/dashboard-fields.md`'s own "### Performance & Benchmark card (Epic 25 / US-25.1)" section (line 215).
  - Mounted by `apps/desktop/src/features/portfolio/DashboardPanel.tsx:142` as `<PerformanceBenchmarkCard result={result} activeRange={activeRange} />`, alongside `MonthlyReturnsGrid` sharing the same `activeRange` state (lines 88-90).
  - Chart line data: `buildIndexedSeries()` (PerformanceBenchmarkCard.tsx:48-67) rebases `result.performance_series` (raw `portfolio_value` and `benchmark_price`) to base 100 at the first point with `portfolio_value > 0`, client-side, in TypeScript — this math runs in the browser, not the engine.
  - Summary numbers below the chart (Portfolio Value, Time-Weighted Return, Money-Weighted Return, Net Contributions, `{Symbol} Return`, Excess Return) come from `result.range_metrics[activeRange].summary` (types.ts:519-542), a server-computed object, distinct code path from the chart line above it.
  - Range filter: `WindowSelector` in DashboardPanel.tsx:136-138, prop `value=activeRange`, handler `onChange={setSelectedRange}`; options are the keys of `result.range_metrics` (`1M, 3M, YTD, 1Y, All` per backend `RANGE_WINDOWS`, dashboard_history_engine.py:315-321).
  - No benchmark-symbol selector exists on this chart or anywhere in `DashboardPanel`/`App.tsx` for the Dashboard tab — the benchmark symbol is hardcoded `'SPY'` at import time (`apps/desktop/src/app/App.tsx:150`, `buildImportFormData`) and threaded through as `historyContext.benchmarkSymbol`; the Exposure tab's "vs Market drift panel" has its own separate selectable-benchmark mechanism, unrelated to this chart.
  - Backend route: `POST /api/engines/dashboard-history/run-imported` (`services/quant-engine/app/api/routes/dashboard_history.py:19-24`) → `run_imported_dashboard_history()` in `services/quant-engine/app/services/dashboard_history_engine.py:422-648`; the non-imported `/run` endpoint (line 400) is effectively an always-`unavailable` stub for imported-only flows.
  - Frontend adapter calling that route: `runImportedDashboardHistory()` / `runDashboardHistoryEngine()` in `apps/desktop/src/features/portfolio/portfolioAnalysisAdapter.ts:191-231`.
  - Schema/contract source of truth for the response: `services/quant-engine/app/schemas/dashboard_history.py` (`DashboardHistoryResult`, `DashboardHistoryRunMetadata`, `DashboardRangeMetrics`), mirrored on the TS side by `apps/desktop/src/features/portfolio/types.ts:442-550` (`DashboardHistoryRunMetadata`, `DashboardRangeMetrics`, `PerformanceSeriesPoint`).
  - Formula for the summary Time-Weighted Return / range re-basing: `docs/finance/financial-methodology.md` §"Portfolio Return Methodology" (line 456) — cash-flow-neutral daily return chained in `app/analytics/risk.py::_portfolio_time_weighted_return_series`, range values re-based via `(1+c_end)/(1+c_start)-1` in `dashboard_history_engine.py::_range_time_weighted_return_pct` (line 871).
  - Formula for Money-Weighted Return: `docs/finance/financial-methodology.md` §"Money-Weighted Return (Modified Dietz)" (line 509), implemented in `dashboard_history_engine.py::_compute_money_weighted_return` (line 835).
  - Formula for `{Symbol} Return` / `Excess Return`: `docs/finance/financial-methodology.md` §"Benchmark and Factor Return Methodology" → "### Mixed-basis portfolio-vs-benchmark comparison (US-34.5)" (line 719) — excess is a literal subtraction of the two already-published scalars, never independently derived (`dashboard_history_engine.py:974-978`).
  - Backend test coverage: `services/quant-engine/app/tests/test_analytics.py` — ~30 tests matching `test_run_imported_dashboard_history_*`, `test_run_dashboard_history_engine_*`, `test_every_range_publishes_its_own_time_weighted_return` (line 8699), `test_performance_summary_reports_twr_mwr_and_excess_return` (line 7717), `test_publishing_the_benchmark_return_does_not_promote_its_basis` (line 9144), plus ~9 golden/consistency tests for the IB2026/FF2026 real statements (lines 7408-7466).
  - Frontend test coverage: `apps/desktop/src/features/portfolio/PerformanceBenchmarkCard.test.tsx` (component rendering, trust-marker text) and `apps/desktop/src/features/portfolio/DashboardPanel.test.tsx` (range selector, `normalizePerformanceSeries` helper) and `apps/desktop/src/features/portfolio/portfolioAnalysisAdapter.test.ts:72-73` (adapter fetch-shape tests for both dashboard-history routes).
  - Contract doc: `docs/contracts/dashboard-fields.md`, section "### Performance & Benchmark card (Epic 25 / US-25.1)" (line 215-225) plus the long "Investor-economics withholding rule" block (lines 96-147) governing which `range_metrics` scalars may be non-null. Doc reads current — actively revised through US-34.9/CR-1 (2026-08-25) per its own inline dating.

risks:
  - `docs/contracts/dashboard-fields.md:219` states the chart's indexed line follows "base-100 rebasing per §Indexed Return Series" (`financial-methodology.md` line 2176), but that methodology section explicitly specifies the portfolio line must be a **TWR-indexed chain** ("Raw market value is NOT a valid portfolio line: a deposit/withdrawal/trade would draw a move against the benchmark's price line that is not performance") and names its sole implementation as `services/quant-engine/app/services/drift_engine.py` (line 2253-2257) — the Exposure tab's drift panel, not this chart. `PerformanceBenchmarkCard.tsx::buildIndexedSeries` (line 48-67) instead indexes raw `portfolio_value` (total market value, not TWR-chained) client-side. Flagging the discrepancy only — not concluding which side is wrong.
  - `apps/desktop/src/features/portfolio/DashboardPanel.tsx::normalizePerformanceSeries` (line 34-51) implements the identical raw-market-value base-100 rebasing math as `PerformanceBenchmarkCard.tsx::buildIndexedSeries`, but is not called anywhere in `DashboardPanel`'s render tree — its only consumer found is `DashboardPanel.test.tsx:172`. Two parallel implementations of the same math is a drift risk regardless of which (if either) is correct; not flagging correctness.
  - Did not locate a dedicated methodology section describing the Dashboard chart's own client-side indexing formula (as opposed to the range-metrics scalar formulas, which are well-documented) — either it is intentionally covered by §Indexed Return Series (and the implementation has drifted from that doc) or the doc has a gap; this scout could not determine which without judging correctness.
  - The non-imported `/api/engines/dashboard-history/run` route (`dashboard_history_engine.py:400-419`) currently always returns the unavailable result regardless of input — confirmed by reading the function body (both branches call `_build_unavailable_dashboard_history_result`). Noted as an observation, not a verdict on whether that route is meant to be reachable in the current product state.
