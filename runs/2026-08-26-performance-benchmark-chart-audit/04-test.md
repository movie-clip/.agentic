REPORT 2026-08-26-performance-benchmark-chart-audit/04
status:      DONE
verdict:     NONE

changed:
  - DashboardPanel.test.tsx — removed the `normalizePerformanceSeries` import and its orphaned test (function was deleted by dispatch 03)
  - PerformanceBenchmarkCard.test.tsx — added a local recharts mock exposing `LineChart`'s `data` prop, plus a `getChartData()` helper
  - PerformanceBenchmarkCard.test.tsx — added 3 regression tests: deposit-vs-raw-value guard, unaffected benchmark leg, first-point-anchor guard

verification:
  command:   cd apps/desktop && npx tsc --noEmit && npx vitest run PerformanceBenchmarkCard DashboardPanel
  result:    PASS
  detail:    tsc --noEmit: no errors. vitest: 2 files passed, 46 tests passed (16 in PerformanceBenchmarkCard.test.tsx, 30 in DashboardPanel.test.tsx), 0 failed.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - PerformanceBenchmarkCard.test.tsx has a local `vi.mock('recharts', ...)` stubbing `LineChart` to expose its `data` prop via `data-testid="indexed-chart-data"`, read by the `getChartData()` async helper — a reusable pattern for asserting exact chart-line values without exporting the builder function from source.
  - That local mock also re-implements src/test/setup.tsx's ResponsiveContainer shim inline, since setup.tsx's global mock does not reach past a test file's own `vi.mock('recharts', ...)`.
  - If setup.tsx's ResponsiveContainer shim is ever exported as a helper, PerformanceBenchmarkCard.test.tsx's local copy should switch to reusing it — not done now since setup.tsx is outside this order's scope.

risks:
  - buildIndexedSeries is not exported from PerformanceBenchmarkCard.tsx, and non_goals forbid touching that source file, so exact chart-line values could not be asserted via a plain unit-test import of the builder.
  - The recharts-mock technique (see handoff) was used instead; it has more surface area than a pure-function test but stays entirely inside the two in-scope test files and asserts numeric values, not SVG geometry.
  - write-tests/SKILL.md's Recharts section lists only textual smoke checks (selector buttons, empty-state, selector-change) — this order's demand for exact portfolio-line values goes beyond that guidance, which is a pack gap worth flagging, not a guardrail conflict.
  - Confirmed via `git diff --stat` that DashboardPanel.tsx and PerformanceBenchmarkCard.tsx (source) carry only dispatch 03's changes; this session touched neither.
