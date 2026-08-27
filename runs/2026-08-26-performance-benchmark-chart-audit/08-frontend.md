REPORT 2026-08-26-performance-benchmark-chart-audit/08
status:      DONE
verdict:     NONE

changed:
  - apps/desktop/src/features/portfolio/types.ts — `DashboardRangeMetrics` gains `window_start_date?: string | null`, mirroring the backend schema field 07-backend.md added
  - apps/desktop/src/features/portfolio/PerformanceBenchmarkCard.tsx — `buildIndexedSeries` now filters `performance_series` to `>= window_start_date` and re-bases the portfolio leg to 100 at the window's first point; benchmark leg gets the same date filter, unchanged rebasing formula

verification:
  command:   cd apps/desktop && npx tsc --noEmit && npx vitest run PerformanceBenchmarkCard DashboardPanel
  result:    PASS
  detail:    tsc clean, zero errors; vitest 2 test files, 46 passed (16 PerformanceBenchmarkCard.test.tsx + 30 DashboardPanel.test.tsx), 0 failed

contract_notes:
  - docs/contracts/dashboard-fields.md still needs the `range_metrics[*].window_start_date` entry 07-backend.md's contract_notes named — out of this order's scope (types.ts + PerformanceBenchmarkCard.tsx only), still outstanding for the docs lane

pack_corrections:
  - none

handoff:
  - add a range-switch chart assertion to PerformanceBenchmarkCard.test.tsx / DashboardPanel.test.tsx per CR-2 #1's expected section — no existing test exercises `window_start_date`-driven filtering or re-basing; current 46 green tests all predate this behavior
  - src/test/dashboardGoldens.ts and src/test/portfolioFixtures.ts predate `window_start_date` and only type-check because the field was added optional — the pending golden regen (`python -m app.scripts.export_dashboard_goldens`, named in 07-backend.md's handoff) should populate real per-range values there so a range-switch test has real dates to assert against
  - manual trace of `dashboard_history_engine.py:764` confirms `window_start_date` is non-null whenever `range_name != "All"` and the slice is non-empty, so this fix is not a no-op for real multi-range data — the BLOCKED escape hatch in this order's definition_of_done was not triggered

risks:
  - typed `window_start_date` as optional (`?:`) rather than the plain `string | null` 07-backend.md's contract note names verbatim, to avoid a same-pass edit to dashboardGoldens.ts/portfolioFixtures.ts (both out of this order's scope)
  - the optional typing matches the existing convention for `portfolio_return_trust`, a sibling field with a backend default that is also typed optional in this same type — flag in case the tech lead wants `window_start_date` strict instead
  - the portfolio re-basing pivot (`pctAtWindowStart`) is read from `sliced[0].portfolio_return_pct` without independently re-deriving that `sliced[0].date` equals `window_start_date` — trusted by construction per the backend's own comment that `window_start_date` IS `perf[0].date` of the identical slice, so the two cannot diverge without a backend bug
