REPORT 2026-08-26-performance-benchmark-chart-audit/03
status:      PARTIAL
verdict:     NONE

changed:
  - apps/desktop/src/features/portfolio/PerformanceBenchmarkCard.tsx — buildIndexedSeries portfolio leg now indexes from portfolio_return_pct (indexed_t = 100*(1+pct/100)), not portfolio_value; benchmark leg (raw-price indexing) untouched, per FINDING 1
  - apps/desktop/src/features/portfolio/DashboardPanel.tsx — deleted dead normalizePerformanceSeries (bit-for-bit the same wrong raw-value formula), per FINDING 2

verification:
  command:   cd apps/desktop && npx tsc --noEmit && npx vitest run PerformanceBenchmarkCard DashboardPanel
  result:    FAIL
  detail:    tsc --noEmit fails: DashboardPanel.test.tsx(6,26) TS2305 no exported member 'normalizePerformanceSeries' — its only reference, expected per FINDING 2 (function deleted, test not touched per non_goals). Run separately (tsc excluded): PerformanceBenchmarkCard.test.tsx 13/13 passed unmodified; DashboardPanel.test.tsx 43 passed, 1 failed (the same dead test, "normalizes all-range performance from first non-zero portfolio point").

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - DashboardPanel.test.tsx:6 imports normalizePerformanceSeries and its only test is lines 171-184 ("normalizes all-range performance from first non-zero portfolio point") — remove both; the function is deleted per FINDING 2.
  - PerformanceBenchmarkCard.test.tsx asserts no dataKey/portfolio value on the rendered chart series at all (grepped for portfolio_index/indexed/dataKey — zero matches) — it never exercised buildIndexedSeries's output, which is why FINDING 1 shipped unnoticed; add coverage for the TWR-indexed portfolio line.
  - Full verification command as specified will not pass tsc until the handoff above is done — this is the expected cross-lane split named in the order's own definition_of_done, not a regression in PerformanceBenchmarkCard.tsx.

risks:
  - status is PARTIAL, not DONE, because the order's own verification command fails on tsc (DashboardPanel.test.tsx's stale import of the now-deleted normalizePerformanceSeries) — the order explicitly anticipated this split (delete the function, leave the test to the test lane) so the failure is expected, but protocol ties DONE to an actual PASS, so I am not claiming one.
  - portfolio_return_pct on the engine's very first daily_state is always 0.0 when the basis is publishing, regardless of whether that first state's portfolio_value is itself >0 — a subtly different anchor rule than the old frontend's "first date with portfolio_value>0".
  - That anchor difference is the engine's own documented behavior (performance.py's previous_state is None branch), and is exactly the field FINDING 1 instructed the chart to consume as-is — no frontend workaround was added.
