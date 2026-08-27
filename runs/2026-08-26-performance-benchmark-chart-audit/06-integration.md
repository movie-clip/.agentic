REPORT 2026-08-26-performance-benchmark-chart-audit/06
status:      DONE
verdict:     CHANGES_REQUESTED

changed:
  - none

verification:
  command:   cd apps/desktop && npx tsc --noEmit && npx vitest run PerformanceBenchmarkCard DashboardPanel
  result:    PASS
  detail:    tsc --noEmit: no errors. vitest: 2 files passed, 46 tests passed (16 PerformanceBenchmarkCard, 30 DashboardPanel), 0 failed. Re-ran myself, not re-read from 05's claim.

contract_notes:
  - CR-2 #1 (BLOCKING): `DashboardRangeMetrics` (app/schemas/dashboard_history.py:37-50) needs a window-start anchor (e.g. `window_start_date`) for the frontend to correctly range-scope the chart without duplicating server-side windowing logic — see cr/CR-2.md CR 1.

pack_corrections:
  - none

handoff:
  - cr/CR-2.md written: 3 change requests (1 BLOCKING → backend, 2 SHOULD_FIX → docs and backend). Orchestrator: dispatch CR 1 to backend-engineer first (schema + engine), then frontend-engineer to consume; CR 2 to docs-engineer; CR 3 to backend-engineer (can ride with CR 1's dispatch, same lane, same file).
  - Round count for CR-2 #1 starts at 1 of 2 (ledger's Rounds table) — this is a NEW finding, not a re-open of CR-1's two (both closed PASS by 05-quant-reaudit).

risks:
  - CR-2 #1 is a pre-existing defect (present since US-25.1 shipped 2026-07-04), not introduced by the CR-1 fix dispatch (03/04) — flagged here because the order's own definition_of_done named this exact check, not because it regressed. Producer should be told AC7 was accepted "[x]" on a story whose test plan never actually tested the "re-anchor the chart" clause it promised.
  - Did not chase whether other range-gated cards (MonthlyReturnsGrid) have the same class of gap — out of scope (order names only PerformanceBenchmarkCard's chart); MonthlyReturnsGrid's monthly cells are genuinely range-scoped server-side (`range_metrics[activeRange].monthly_returns`), so it is not the same bug, just noting I did not audit it further.

## Orchestrator brief
- Verdict: CHANGES_REQUESTED. 1 BLOCKING (chart ignores the range selector entirely — real, testable, escaped detection), 2 SHOULD_FIX (doc traceability gap, missing stub comment). All three in `cr/CR-2.md`.
- CR-1's actual fix (chart line math, dead-duplicate removal) is independently confirmed sound — nothing new to add there; both prior gates (02/05 quant-audit) already closed it PASS.
- CR-2 #1 (BLOCKING, → backend then frontend): `PerformanceBenchmarkCard`'s chart reads the un-sliced top-level `performance_series`, never `activeRange`-scoped; only the summary strip below it responds to the range selector. Violates US-25.1 AC7 ("re-anchor the chart"). No test anywhere exercises this. Fix needs a schema addition (no window-boundary field exists to slice against) — not a pure frontend fix. See § Range-filter finding for full evidence.
- CR-2 #2 (SHOULD_FIX, → docs): `financial-methodology.md` §Indexed Return Series' formula is correct and matches the now-fixed code, but its "Implementation:" list only names `drift_engine.py`, not the Dashboard card's actual code path — a wrong-pointer trap, not a math error.
- CR-2 #3 (SHOULD_FIX, → backend): the non-imported `/run` route's always-unavailable behavior is judged intentional and correct (TWR needs a ledger the request-path snapshot lacks) but is undocumented at the point of implementation — one comment, no behavior change.
- Trust label ("Portfolio: Replay-derived") and contract-doc line 219 are BOTH confirmed accurate post-fix — no finding on either. See § Trust label and contract doc.
- Full evidence, the AC7 citation, and the schema/field trace are in § Range-filter finding (DoD 1), § Trust label and contract doc (DoD 2 + 3), § Methodology-doc Implementation gap (DoD 4b), and § The /run route (DoD 4a).

## Range-filter finding (DoD 1 — BLOCKING, CR-2 #1)

`DashboardPanel.tsx:118-123` mounts one `WindowSelector` above both
`PerformanceBenchmarkCard` and `MonthlyReturnsGrid`, sharing `activeRange`.
`PerformanceBenchmarkCard.tsx:94-95`:

```
const metrics: DashboardRangeMetrics = rangeMetrics[activeRange]
const chartData = buildIndexedSeries(result.performance_series)
```

`metrics` is range-scoped (drives the six summary numbers). `chartData` is
built from `result.performance_series` — the top-level
`DashboardHistoryResult.performance_series` field
(`app/schemas/dashboard_history.py:317`), which is the FULL history, never
sliced per range. `buildIndexedSeries` (line 48-67) takes no range argument
and never reads `activeRange`. Selecting `1M` re-renders the summary strip
with 1-month numbers while the chart directly above stays exactly the same
multi-year (or whatever the full import spans) line.

I checked whether the contract even carries enough information for a
frontend-only fix: `DashboardRangeMetrics` (schema, lines 37-50) has
`summary`, `max_drawdown_pct`, `monthly_returns`, `monthly_returns_reliable`,
`portfolio_return_trust` — no date, no window boundary. Server-side windowing
(`RANGE_WINDOWS` trading-day counts, `_slice_performance_series`,
`dashboard_history_engine.py:315-321,798-806`) is not exposed at all. A
frontend fix would have to re-derive that windowing (duplicated engine
logic) or the schema needs to publish the boundary.

Checked story intent, not just code-vs-code: `docs/product/stories/US-25.1-
dashboard-performance-benchmark-card.md` AC7 (checked "[x]", story Status:
Done) — "A range selector ... lets the researcher switch the summary strip
**and re-anchor the chart**." The code does the first half only. The
story's own Test Plan section, notably, only describes testing "range
selector switches the summary strip without re-fetching" — it never
mentions testing the chart re-anchoring, which is consistent with what
actually shipped: half the AC, accepted as whole.

Confirmed no test anywhere would catch this:
`PerformanceBenchmarkCard.test.tsx`'s `analysis()` fixture (line 61-106)
defines exactly one range key, `All`, and every one of its 16 tests passes
`activeRange="All"` — there is no fixture with two ranges and no assertion
that changing range changes chart data.
`DashboardPanel.test.tsx:226-237` ("switches the summary strip when the
range selector changes without any network fetch") explicitly comments
"Fixture uses identical values across ranges" and asserts only
`aria-pressed` on the clicked button plus that `fetch` was not called — it
never reads a changed number, and it never touches the chart.

Precedent for the correct shape already exists in this codebase, on the
Exposure tab: `IndexedReturnChart.tsx::sliceAndRebase` filters a series by
`date >= startDate` and rebases to 100 there, where `startDate` comes from
`windows[].start_date` PUBLISHED by the drift response
(`IndexedReturnChart.tsx:20-30`) — the backend computes the window
boundary, the frontend only filters and rebases an already-published TWR
chain. `DashboardRangeMetrics` has no equivalent field. CR-2 #1 asks for
one, named to mirror this pattern, plus the frontend consumer change.

This is a pre-existing gap (present since US-25.1 shipped 2026-07-04), not
something dispatch 03/04 introduced or touched — `git diff` on
`PerformanceBenchmarkCard.tsx` (confirmed by 05-quant-reaudit) shows only
the portfolio-leg formula and a comment changed; `chartData`'s dependency
(or non-dependency) on `activeRange` is untouched. Reported here because
the order's own definition_of_done named exactly this check ("does the
chart's indexed line also respect the selected range... this is exactly
the kind of filtering-correctness question... scout's map did not
resolve").

## Trust label and contract doc (DoD 2 + 3)

**Trust label** (`PerformanceBenchmarkCard.tsx:115-117`, "Portfolio:
Replay-derived"): `returnBasisLabel(portfolioBasis)` reads
`run_metadata.return_basis_contract.portfolio_path`. This is the SAME basis
that governs `time_weighted_return_pct` and, since the CR-1 fix, the
chart's portfolio line (`portfolio_return_pct`, the field the terminal
`time_weighted_return_pct` value is drawn from — same code path,
`performance.py::build_true_performance_series`). Before the fix the label
described a basis the chart's raw-NAV-ratio line did not actually reflect
(a fabrication concern the quant audit flagged as trust-classification,
not just arithmetic). Now that the chart is built from the same
`portfolio_return_pct` chain the basis label describes, the label is
accurate to what is actually drawn. No finding.

**Contract doc** (`docs/contracts/dashboard-fields.md:219`, "Indexed chart
... base-100 rebasing per §Indexed Return Series"): the row cites
`buildIndexedSeries(result.performance_series)` as the source — that is
still literally true post-fix (same function, same input field, corrected
formula). No doc edit needed on this line; scout and 02-quant-audit's
conclusion that "the doc was right, the code was wrong" remains true now
that the code has been fixed to match it. Confirmed by re-reading the row
verbatim against the current source, not by re-trusting the prior reports'
characterization.

## Methodology-doc Implementation gap (definition_of_done item 4b — SHOULD_FIX, CR-2 #2)

`financial-methodology.md` §Indexed Return Series (line 2176) states the
Portfolio-line formula under an "US-27.8 / audit F10" heading — the exact
ticket reference the CR-1 fix's own code comment cites
(`PerformanceBenchmarkCard.tsx:56`), so the documented FORMULA is and
remains correct for this card; nothing to fix there. But its
"Implementation:" list (line 2253-2257) names only
`services/quant-engine/app/services/drift_engine.py` — the Exposure-tab
drift panel, a different card computing a different (window-return, not
daily-TWR-series) quantity. It does not name
`app/analytics/performance.py::build_true_performance_series` (which
actually produces `performance_series[].portfolio_return_pct`, the field
the Dashboard chart consumes) or `PerformanceBenchmarkCard.tsx`. A reader
using this section to trace "where is the Dashboard chart's formula
implemented" lands in the wrong file. This is a genuine methodology-doc
gap, confirmed real — not resolved by the CR-1 fix, since the fix only
changed which field the frontend reads, not the doc's Implementation
list. SHOULD_FIX, not BLOCKING: the formula text is correct, no
number is at risk, only a traceability pointer.

## The /run route (definition_of_done item 4a — judged intentional, SHOULD_FIX comment only, CR-2 #3)

`run_dashboard_history_engine` (`dashboard_history_engine.py:400-419`)
confirmed, by direct read, to unconditionally return
`_build_unavailable_dashboard_history_result` on both branches — scout's
characterization holds. Confirmed this route is LIVE, not orphaned:
`App.tsx:562,568` calls it whenever a restored snapshot's `historySource`
is not `imported_replay`, or when the imported-replay path throws.
Judgment: intentional, architecturally-correct fail-closed stub, not a
defect. The Dashboard's investor-performance family (TWR, Modified-Dietz
MWR, net contributions, monthly returns) needs ledger-derived cash-flow
dates a non-imported "positions + cash only" snapshot cannot supply;
computing anything here would mean fabricating a cash-flow assumption,
which guardrail 4 forbids. That reasoning is sound but lives nowhere in
the code — both branches converging on the same call with no comment reads
identically to an unfinished stub. SHOULD_FIX: one comment, no behavior
change.
