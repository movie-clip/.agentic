CHANGE REQUEST 1
lane:     backend
severity: BLOCKING
round:    1
finding:  `PerformanceBenchmarkCard.tsx:95` builds the chart's data with
          `buildIndexedSeries(result.performance_series)` — the TOP-LEVEL,
          never-range-sliced `performance_series` field
          (`DashboardHistoryResult.performance_series`,
          `app/schemas/dashboard_history.py:317`). `activeRange` is used
          ONLY to pick `rangeMetrics[activeRange]` for the six summary
          scalars below the chart (`PerformanceBenchmarkCard.tsx:94,100`);
          it never touches `chartData`. Selecting `1M`/`3M`/`YTD`/`1Y`
          changes every number in the summary strip but the chart directly
          above it is IDENTICAL for every range — always the full imported
          history, indexed from day one.

          `DashboardRangeMetrics` (`app/schemas/dashboard_history.py:37-50`)
          carries no per-range series and no window boundary at all — no
          `window_start_date`, nothing a frontend could slice
          `performance_series` against even if it wanted to. The
          server-side windowing (`RANGE_WINDOWS` trading-day counts +
          `_slice_performance_series`,
          `dashboard_history_engine.py:315-321,798-806`) is not exposed in
          the contract in any form, so this cannot be fixed frontend-only
          without re-deriving that windowing logic client-side — itself a
          second copy of engine logic (architecture pack's "No duplicated
          computation").
why:      US-25.1 AC7 (`docs/product/stories/US-25.1-...md`, checked "[x]",
          Status: Done) explicitly promises the range selector "lets the
          researcher switch the summary strip **and re-anchor the chart**".
          It does not. A researcher who picks "1M" to see how the account
          moved in the last month sees a chart spanning the account's ENTIRE
          history — years, in the golden fixtures — directly above summary
          numbers that genuinely are 1-month figures. The chart and the
          numbers beneath it visually appear to describe the same window and
          do not; that is a materially misleading presentation on a
          financial-accuracy-first surface, not a cosmetic gap. No test in
          `PerformanceBenchmarkCard.test.tsx` or `DashboardPanel.test.tsx`
          exercises this: every `PerformanceBenchmarkCard` test hardcodes a
          single-range `{ All: {...} }` fixture, and
          `DashboardPanel.test.tsx`'s one range-switch test
          ("switches the summary strip when the range selector changes...",
          line 226) explicitly uses "identical values across ranges" and
          asserts only the button's `aria-pressed` state, never the chart
          or a changed number — so this gap is invisible to CI.
expected: The Exposure tab already solves the identical problem correctly:
          `IndexedReturnChart.tsx::sliceAndRebase` filters `series` by
          `date >= startDate` and rebases to 100 at that point, where
          `startDate` comes from `w.start_date` published by the DRIFT
          response's own `windows[]` (`IndexedReturnChart.tsx:20-30`) — the
          backend computes the boundary, the frontend only filters+rebases.
          Mirror that: add a window-start anchor to `DashboardRangeMetrics`
          (e.g. `window_start_date: str | None`, populated from
          `_slice_performance_series`'s own slice in
          `dashboard_history_engine.py:757` — the date already being
          computed and simply not published) so
          `PerformanceBenchmarkCard.tsx::buildIndexedSeries` can filter
          `performance_series` to `>= window_start_date` and re-base the
          already-published `portfolio_return_pct` chain to 100 at that
          point (`indexed_t = 100 * (1+pct_t/100) / (1+pct_{window_start}/100)`
          — algebra on an already-correct TWR chain, no new formula, no
          duplicated windowing logic). This is a schema addition
          (`app/schemas/dashboard_history.py`), so it starts in backend and
          must emit a contract note for `types.ts` +
          `docs/contracts/dashboard-fields.md` + the frontend consumer
          change per the schema hook. Add the range-switch chart assertion
          this CR's own tests would have caught, in the same pass or the
          following test dispatch.

CHANGE REQUEST 2
lane:     docs
severity: SHOULD_FIX
round:    1
finding:  `docs/finance/financial-methodology.md` §Indexed Return Series
          (line 2176) states the Portfolio-line formula under the heading
          "US-27.8 / audit F10" — the SAME ticket reference the CR-1 fix's
          code comment cites (`PerformanceBenchmarkCard.tsx:56`) — so the
          documented formula is and remains correct for this card. But the
          section's "Implementation:" list (line 2253-2257) names only
          `services/quant-engine/app/services/drift_engine.py` (the
          Exposure-tab drift panel). It does not name
          `app/analytics/performance.py::build_true_performance_series`
          (which actually computes the `portfolio_return_pct` chain the
          Dashboard chart consumes) or
          `PerformanceBenchmarkCard.tsx::buildIndexedSeries` (which builds
          the Dashboard chart from it).
why:      Guardrail 2 (methodology traceability) requires every UI metric
          trace to one engine formula and one code path. A future engineer
          verifying "does the Dashboard chart follow §Indexed Return
          Series" who follows this section's own "Implementation:" pointer
          lands in `drift_engine.py` — a different card, a different
          engine module, computing a window-return for the Exposure tab,
          not the Dashboard's TWR-indexed daily series. That is exactly the
          wrong-pointer trap this scout/audit run's own risk-flags warned
          about (01-scout.md § risks, 02-quant-audit.md § risks) — it did
          not cause FINDING 1's bug, but it would have made that bug harder
          to trace to the right file. `dashboard-fields.md:219`'s citation
          of this section stays correct on its own terms; this is a gap in
          the section it points to, not in the pointer itself.
expected: Add `app/analytics/performance.py::build_true_performance_series`
          (the shared TWR daily-return chain feeding
          `performance_series[].portfolio_return_pct`) and
          `PerformanceBenchmarkCard.tsx::buildIndexedSeries` (the Dashboard
          chart's consumer of it) to the "Implementation:" list, worded so
          it's clear this section governs TWO cards' indexed charts
          (Dashboard performance, Exposure drift) via two separate
          code paths that both implement the same documented formula family
          — not one shared implementation.

CHANGE REQUEST 3
lane:     backend
severity: SHOULD_FIX
round:    1
finding:  `run_dashboard_history_engine`
          (`dashboard_history_engine.py:400-419`, the non-imported `/run`
          route) has two branches — missing `history_context` vs. present
          — and BOTH unconditionally call
          `_build_unavailable_dashboard_history_result`. The function never
          computes anything regardless of input. It is live code, not dead
          code: `App.tsx:562,568` calls it whenever
          `historySource?.kind !== 'imported_replay'` (a restored
          non-ledger snapshot) or when the imported-replay path throws and
          falls back. No comment anywhere in the function explains why.
why:      Judged this an intentional, architecturally-correct fail-closed
          stub, not a defect: the Dashboard's investor-performance family
          (TWR, Modified-Dietz MWR, net contributions, monthly returns)
          genuinely requires ledger-derived cash-flow dates that a
          non-imported "positions + cash only" snapshot does not carry —
          computing anything here would mean fabricating cash-flow
          assumptions, which guardrail 4 forbids. That reasoning is sound
          but currently lives only in this reviewer's head and in
          `financial-methodology.md`'s general TWR-needs-a-ledger framing,
          not at the point of implementation. A function whose both
          branches converge on the same "unavailable" call, with zero
          comment, reads exactly like an unfinished stub to the next
          engineer who touches it — indistinguishable, at the code, from a
          defect.
expected: A short comment on `run_dashboard_history_engine` stating it is
          permanently unavailable-only because the investor-performance
          family cannot be computed without a ledger, and that this is not
          a partial implementation to be finished later. No behavior
          change.
