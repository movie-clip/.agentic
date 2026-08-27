REPORT 2026-08-26-performance-benchmark-chart-audit/07
status:      PARTIAL
verdict:     NONE

changed:
  - services/quant-engine/app/schemas/dashboard_history.py — added `window_start_date: str | None` to `DashboardRangeMetrics` (docstring documents ISO-date semantics and the "All" null case)
  - services/quant-engine/app/services/dashboard_history_engine.py — `_build_range_metrics` now reads `window_start_date` off the existing `_slice_performance_series(...)` slice's first point (no new computation), wired into both the populated and the empty-series construction branches

verification:
  command:   cd services/quant-engine && python -m pytest app/tests/test_analytics.py -k "dashboard_history or run_imported_dashboard" -v
  result:    FAIL
  detail:    22 selected tests all ERROR at setup — the session-scoped dashboard-goldens freshness fixture (`app/tests/conftest.py`) fails because backend output now includes `window_start_date`, not yet reflected in `apps/desktop/src/test/dashboardGoldens.ts`. Diagnostic-only rerun with `SKIP_GOLDEN_FRESHNESS_CHECK=1` (env var only, no file edits) shows all 22 pass on their actual assertions — confirming this is golden staleness, not a logic regression. `python scripts/detect_deadcode.py --strict` is clean (ruff/vulture/knip all pass).

contract_notes:
  - apps/desktop/src/features/portfolio/types.ts `DashboardRangeMetrics` (line 519) needs a mirrored `window_start_date: string | null` field.
  - docs/contracts/dashboard-fields.md needs a new entry for `range_metrics[*].window_start_date` (near the existing `portfolio_return_trust` entry at line 322) documenting the source (`_slice_performance_series`'s own slice) and the "All" → null semantics.

pack_corrections:
  - none

handoff:
  - apps/desktop/src/test/dashboardGoldens.ts is stale and blocks the full `test_analytics.py` dashboard-history suite (22 tests) at setup; regenerate via `python -m app.scripts.export_dashboard_goldens` (run from `services/quant-engine`), review the diff, commit.
  - No test in `test_analytics.py` asserts the full `DashboardRangeMetrics` shape directly — every existing assertion is per-field (e.g. `result.range_metrics["All"].summary.time_weighted_return_pct`) — so only the golden fixture needs updating for this field, not `test_analytics.py` itself.
  - `PerformanceBenchmarkCard.tsx::buildIndexedSeries` (frontend-engineer's next dispatch) can now read `rangeMetrics[activeRange].window_start_date` to filter `performance_series` to `>= window_start_date` and re-base, per CR-2 #1's `expected` section — `null` means no filtering (full history, e.g. "All").
  - Add the range-switch chart assertion CR-2 #1 names (that changing `activeRange` changes the chart's plotted date range, not just the summary strip) — this is a `test` lane item once the frontend consumer lands.

risks:
  - Interpreted "`None` when the range has no lower bound, e.g. `All`" as applying only to "All" among the two `RANGE_WINDOWS` entries with `window=None` — "All" returns the full unsliced series so `window_start_date=None`.
  - "YTD" also has `window=None` in `RANGE_WINDOWS` but is year-filtered by its own branch in `_slice_performance_series`, so it gets a real (non-null) `window_start_date` — this split was not spelled out explicitly in the CR; worth a quick confirm from tech-lead/frontend-engineer that it matches intent.
