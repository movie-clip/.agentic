REPORT 2026-08-26-performance-benchmark-chart-audit/10
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd services/quant-engine && python -m pytest app/tests/test_analytics.py -k "dashboard_history or run_imported_dashboard" -v ; cd apps/desktop && npx vitest run PerformanceBenchmarkCard DashboardPanel
  result:    PASS
  detail:    backend: 22 passed, 193 deselected. frontend: 2 test files, 49 passed, 0 failed (18 PerformanceBenchmarkCard.test.tsx + 31 DashboardPanel.test.tsx).

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - docs/contracts/dashboard-fields.md still has no `range_metrics[*].window_start_date` entry — already tracked as outstanding in 07-backend.md/08-frontend.md contract_notes, not new; unblocked for the docs lane to pick up whenever it is next dispatched.

risks:
  - FINDING 1 (MINOR, doc gap) — the YTD anchor convention differs from the sliding-window (1M/3M/1Y) anchor convention; undocumented. Not a CR-2 defect, see § Findings.
  - `_slice_performance_series`'s "window > available history" branch silently falls back to the full series rather than `unavailable` — unchanged by CR-2, see § Pre-existing edge case for detail.

## Orchestrator brief
Verdict PASS. CR-2 #1's re-basing algebra and the two unverified assumptions
named in 07/08-frontend.md both independently re-derived and confirmed
correct against the real engine code (not just read) — detail in § Log:
- § Log/1 Re-derivation of the re-basing algebra — closed-form + synthetic
  engine cross-check, portfolio and benchmark legs match to expected rounding.
- § Log/2 window_start_date invariant — proved across 1M/3M/YTD/1Y/All plus
  single-day-history and empty-series edge cases on a real 184-point series.
- § Log/3 YTD judgment call — confirmed real, non-null, distinct-from-All.
- § Log/4 FINDING 1 (MINOR, non-blocking) — YTD's anchor-inside-window vs
  sliding windows' anchor-outside-window convention is undocumented.
- § Log/5 Pre-existing edge case — a note on a pre-CR-2 truncation behavior,
  not a finding against this fix.
Test suite re-run independently (not trusted from 09-test.md): PASS, matches.

## Log

### 1. Re-derivation of the re-basing algebra (independent, closed-form + synthetic engine run)

Built two independent synthetic datasets directly against the real engine
functions (`build_true_performance_series`, `_build_range_metrics`,
`_slice_performance_series` — no mocks), with a hand-known closed-form growth
path (portfolio compounding at a fixed daily rate, benchmark at a different
fixed daily rate), then reimplemented `buildIndexedSeries` faithfully in
Python and cross-checked against a THIRD, fully independent hand calculation
using only the raw `portfolio_return_pct`/`benchmark_price` values pulled off
the engine's own output — applying `indexed_t = 100*(1+pct_t/100)/(1+pct_windowStart/100)`
fresh, not through any shared helper.

Result on a 5-day sub-window (`window_start_date=2026-02-05`, portfolio
compounding at 1%/day, benchmark at 0.5%/day):
- Portfolio: hand calc gives indexed values 100.0, 101.000236, 102.016224,
  103.032212, 104.063952, 105.103568 (2026-02-05..2026-02-12). The
  closed-form true unrounded growth over the window
  (`portfolio_value[-1]/portfolio_value[0] - 1`) is 5.101%; the chart's
  implied growth (last indexed − 100) is 5.1036% — the ~0.003pp gap is
  exactly the accumulated 2-decimal rounding already baked into the published
  `portfolio_return_pct` field at each cumulative step (pre-existing,
  unrelated to CR-2). The re-basing algebra itself introduces zero additional
  error.
- Benchmark: hand-computed indexed values (100, 100.5, 101.0025, 101.507512,
  102.01505, 102.525125) match `1.005^n * 100` **exactly** — confirming the
  benchmark leg's date-filtered indexing is bit-for-bit the same as a fresh
  raw-price rebasing at the window's own start (DoD item 4).
- The shipped test `PerformanceBenchmarkCard.test.tsx` (`range-switch chart
  re-anchoring (CR-2 #1)`, lines 185-284) independently asserts the identical
  formula on its own fixture (`toBeCloseTo((100*1.05)/1.04, 5)` for a 1M
  window pivoting at pct=4.0 to pct=5.0) — verified by hand, matches.

Anchor used: `anchor: methodology-doc` (the doc's `indexed_t =
indexed_{t-1}*(1+daily_return_t)` compounding definition, algebraically
identical to the ratio-of-cumulative-growth-factors form CR-2 implements) —
**and** `anchor: closed-form` (the synthetic fixed-daily-rate series, whose
correct answer is known without reading any code) — the second is the
independent one; see § "Two meanings" in the quant pack.

### 2. `window_start_date` invariant (08-frontend.md's trusted-by-construction assumption)

Verified directly against `dashboard_history_engine.py::_slice_performance_series`
and `_build_range_metrics` (read, not assumed), then proved numerically on a
184-point, two-calendar-year synthetic series (2025-06-02..2026-02-12) across
every range in `RANGE_WINDOWS`:

| range | window_start_date | frontend's own `performance_series.filter(d >= window_start_date)[0].date` | match |
|---|---|---|---|
| 1M | 2026-01-14 | 2026-01-14 | yes |
| 3M | 2025-11-17 | 2025-11-17 | yes |
| YTD | 2026-01-01 | 2026-01-01 | yes |
| 1Y (window=252 > 184 available points) | 2025-06-02 | 2025-06-02 | yes |
| All | None | (unfiltered, first point 2025-06-02) | yes (null handled by both sides identically) |

The invariant holds structurally, not by luck: `performance_series` and
`daily_states` are 1:1 by date (`performance.py::build_true_performance_series`
emits exactly one `PerformancePoint` per `DailyPortfolioState`, same date, same
order), so the `prior_state.date` used to build the 1M/3M/1Y synthetic anchor
in `_slice_performance_series` is *always* a real date that also exists in the
top-level `performance_series` the frontend filters. 08-frontend.md's risk
note was right to flag this as "trusted, not verified" — it is now verified.

A second, more interesting sub-finding: the synthetic anchor's
`portfolio_return_pct` (copied from `sliced[0]`, per the code comment at
`dashboard_history_engine.py:833-839`) is a placeholder never actually used as
a return basis — `_range_time_weighted_return_pct` deliberately re-looks-up
the REAL return at that date from `source_performance_series` rather than
reading it off the synthetic anchor (its own docstring, lines 890-897, states
this explicitly: "the anchor's own copied return is never the base"). The
frontend's `buildIndexedSeries`, by filtering the real `performance_series`
rather than consuming the backend's `perf` list, independently lands on that
same real value for its own pivot (`pctAtWindowStart`) — so the chart's pivot
and the summary strip's period-return pivot are the *same number*, verified
by construction of the two independent code paths, not by one calling the
other. This is the strongest form of consistency evidence available here.

Edge cases also exercised directly against the real engine: single-day
history (window_start_date resolves to that single date for every numeric
window, no divide-by-zero, no crash), and fully-empty `performance_series`
(`window_start_date=None` uniformly, `portfolio_return_trust="unavailable"`
uniformly — no fabricated boundary on an unavailable result).

### 3. YTD judgment call (07-backend.md's risk note)

Confirmed directly from `RANGE_WINDOWS` (`window=None` for both "YTD" and
"All") and `_slice_performance_series`'s explicit `if range_name == "YTD":`
branch (filters by `point.date.startswith(latest_year)`, no synthetic anchor)
— YTD and All share `window=None` in the table but are handled by genuinely
different code paths, and `_build_range_metrics`'s
`window_start_date = perf[0].date if perf and range_name != "All" else None`
explicitly special-cases "All" out. Verified numerically on the two-year
synthetic series: YTD → `2026-01-01` (first trading day of the running year),
All → `None`. 07-backend.md's interpretation is correct.

### 4. FINDING 1 — MINOR (documentation gap, not a CR-2 defect)

```
FINDING 1
severity:   MINOR
where:      services/quant-engine/app/schemas/dashboard_history.py:51-61 (docstring);
            docs/finance/financial-methodology.md §Indexed Return Series (no mention)
claim:      window_start_date is documented as "the ISO date this range's window BEGINS" —
            true, but silently means two different things for two range kinds.
actual:     For 1M/3M/1Y, window_start_date is the LATEST daily state strictly BEFORE
            the window's own first counted trading day (`prior_state`, `dashboard_history_engine.py:822-829`)
            — a genuine "day zero" baseline, so all N window days' own returns are
            visible in the re-based chart. For YTD, window_start_date is the FIRST
            trading day WITHIN the window itself (the year's own first point,
            `_slice_performance_series:807-808`) — that day's own return (vs the prior
            year's close) is consumed establishing the baseline and is not visible in
            the re-based chart. Verified numerically: both conventions produce a point
            plotted at exactly indexed=100 at window_start_date, but a different number
            of days' worth of growth is visible behind it depending on range.
impact:     Not a wrong number — confirmed the chart and the summary strip use the
            identical convention per range (this predates CR-2: `_range_time_weighted_return_pct`,
            lines 890-914, already re-bases the same way for the summary figure). A
            future engineer extending window_start_date to a new range kind could pick
            either convention without realising two already coexist, silently
            introducing a THIRD, inconsistent one.
expected:   A one- or two-line note near the `window_start_date` docstring (or in
            financial-methodology.md's Indexed Return Series section, alongside CR-2 #2's
            already-open SHOULD_FIX naming performance.py/PerformanceBenchmarkCard.tsx as
            a second implementation of the family) stating explicitly that YTD's anchor
            is inside the window while the sliding windows' anchor is outside it.
```

This does not block. It is a defensible, internally-consistent existing
convention (YTD "start of year" reasonably read as "first trading day of the
year" rather than "last close of the prior year") — a documentation
completeness gap, not an arithmetic error, and it predates this CR.

### 5. Pre-existing edge case — window wider than available history

`_slice_performance_series` (`dashboard_history_engine.py:811-812`): when
`len(performance_series) <= window` (e.g. "1Y" selected but only 6 months of
history exist), the function returns the full `performance_series` unchanged
— no synthetic anchor, no `unavailable`. `quant.md`'s edge-case table names
this exact shape ("window longer than available history → unavailable, not
silently truncated"). This logic is untouched by CR-2 (CR-2 only added
`window_start_date` derivation on top of whatever `_slice_performance_series`
already returns) — confirmed by re-reading the function: the truncation
branch predates this change and the diff CR-2 shipped does not touch it.
Verified numerically (§2 table, "1Y" row: window=252 > 184 available points)
that `window_start_date` in this branch still correctly resolves to the
actual first available date, matching "All" — so the CR-2 invariant holds
here too; this is not a defect in the fix under audit, and re-litigating
whether the underlying truncate-vs-withhold policy is correct is outside this
order's scope (CR-2 #1 only, non_goals). Recorded for the human's awareness,
not as a finding against this fix.
