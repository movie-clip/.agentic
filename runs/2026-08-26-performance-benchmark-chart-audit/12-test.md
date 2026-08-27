REPORT 2026-08-26-performance-benchmark-chart-audit/12
status:      DONE
verdict:     NONE

changed:
  - apps/desktop/src/test/portfolioFixtures.ts — createImportedDashboardFixture's range_metrics now carries a real, distinct window_start_date per range instead of the field being absent everywhere

verification:
  command:   cd apps/desktop && npx tsc --noEmit && npx vitest run PerformanceBenchmarkCard DashboardPanel ; npx vitest run
  result:    PASS
  detail:    tsc --noEmit: no errors. Narrow run: 2 files, 49 passed (18 PerformanceBenchmarkCard.test.tsx + 31 DashboardPanel.test.tsx), 0 failed. Full run: 40 files, 359 passed, 0 failed.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - `createImportedDashboardFixture`'s performance_series dates are 2025-01-02 / 2025-02-03 / 2025-03-03 — window_start_date values below are chosen against those.
  - window_start_date now: 1M='2025-03-01' (only the last point counted), 3M='2025-02-01' (last two points).
  - window_start_date now: 1Y='2025-01-01' and YTD='2025-01-02' (both include all three points, mirroring the production goldens' YTD==1Y-under-a-year pattern), All=null (unsliced).
  - A test needing the old all-null-everywhere behaviour must now override window_start_date explicitly, the same way 09-test.md's two tests already did inline.

risks:
  - none

## Orchestrator brief
- DoD met: all five range_metrics entries in `createImportedDashboardFixture` now carry a real, distinct `window_start_date` (four ISO dates + `All: null`), values chosen to be plausible against the fixture's own existing `performance_series` dates (2025-01-02/02-03/03-03), not just distinct strings — see the in-file comment added alongside the change.
- Checked every existing consumer of the fixture (`DashboardPanel.test.tsx`, `PerformanceBenchmarkCard.test.tsx` via `createImportedDashboardFixture`/`createImportedDashboardHistoryFixture`): none asserts on `window_start_date` being absent/null across all ranges — the two tests 09-test.md added already override it inline per-range, which always wins over the fixture default, so their assertions are unaffected. No BLOCKED condition found.
- Full frontend suite re-run clean after the change: `tsc --noEmit` zero errors, narrow vitest 49/49, full vitest 359/359 (40 files) — no other latent consumer of the shared fixture broke.
- Diff is isolated to the one in-scope file; `git diff --stat` confirms `portfolioFixtures.ts` is the only file this dispatch touched (other uncommitted files in the tree are prior dispatches' work, untouched here).
