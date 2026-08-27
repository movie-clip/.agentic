REPORT 2026-08-26-performance-benchmark-chart-audit/09
status:      DONE
verdict:     NONE

changed:
  - apps/desktop/src/test/dashboardGoldens.ts — regenerated via `python -m app.scripts.export_dashboard_goldens`; diff adds only `window_start_date` per range (`ib2026` and `ff2026` fixtures), no numeric field changed
  - apps/desktop/src/features/portfolio/PerformanceBenchmarkCard.test.tsx — added a `range-switch chart re-anchoring (CR-2 #1)` describe block: two tests proving the chart's plotted dates AND re-based trajectory differ between `1M`/`3M` (distinct `window_start_date`), plus the `window_start_date: null` ("All") full-history case
  - apps/desktop/src/features/portfolio/DashboardPanel.test.tsx — added a local `vi.mock('recharts', ...)` (mirroring PerformanceBenchmarkCard.test.tsx's) and one new test asserting the chart data passed down actually changes when the range selector changes, not just `aria-pressed`

verification:
  command:   cd services/quant-engine && python -m pytest app/tests/test_analytics.py -k "dashboard_history or run_imported_dashboard" -v ; cd apps/desktop && npx tsc --noEmit && npx vitest run PerformanceBenchmarkCard DashboardPanel
  result:    PASS
  detail:    backend: 22 passed, 193 deselected. frontend: tsc clean, zero errors; vitest 2 test files, 49 passed (18 PerformanceBenchmarkCard.test.tsx + 31 DashboardPanel.test.tsx), 0 failed.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - dashboardGoldens.ts regen closes 07-backend.md's PARTIAL — the 22-test dashboard-history suite that ERRORed at golden-freshness setup now passes cleanly.
  - No new shared fixture/helper was added to `fixtures.py` or `portfolioFixtures.ts` — the golden regen only touched generated goldens (confirmed by `git diff --stat`, 20 insertions/10 deletions, all `window_start_date` additions), so `portfolioFixtures.ts` was correctly left untouched per the order's "confirm before touching" gate.
  - `DashboardPanel.test.tsx`'s new range-switch test overrides `range_metrics['1M'].window_start_date` / `['3M'].window_start_date` inline (`'2025-03-03'` / `'2025-01-02'`) against the existing `createImportedDashboardFixture()` performance_series dates, rather than editing the shared fixture — same pattern the file's other range-specific tests already use for `monthly_returns` overrides.

risks:
  - none
