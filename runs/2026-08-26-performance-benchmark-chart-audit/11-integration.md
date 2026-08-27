REPORT 2026-08-26-performance-benchmark-chart-audit/11
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd services/quant-engine && python -m pytest app/tests/test_analytics.py -k "dashboard_history or run_imported_dashboard" -v ; cd apps/desktop && npx tsc --noEmit && npx vitest run PerformanceBenchmarkCard DashboardPanel
  result:    PASS
  detail:    backend: 22 passed, 193 deselected. tsc --noEmit: no errors. vitest: 2 files, 49 passed (18 PerformanceBenchmarkCard.test.tsx + 31 DashboardPanel.test.tsx), 0 failed. All re-run myself this dispatch, not trusted from 07/08/09/10's claims. Also ran `python scripts/detect_deadcode.py --strict`: ruff/vulture/knip all clean.

contract_notes:
  - docs/contracts/dashboard-fields.md still has no `range_metrics[*].window_start_date` entry — confirmed still absent by direct grep, not new (07/08/10 already flagged it), unblocked for docs lane.

pack_corrections:
  - none

handoff:
  - docs-engineer: add the `range_metrics[*].window_start_date` entry to dashboard-fields.md — SHOULD_FIX, route to Open, not a new CR.
  - SHOULD_FIX (Open, not a CR): tighten `types.ts` `window_start_date?: string | null` to the strict `string | null` the backend contract note asked for — see § Typing judgment (DoD 2).
  - SHOULD_FIX (Open, not a CR): give `portfolioFixtures.ts`'s `createImportedDashboardFixture` real distinct per-range `window_start_date` values — see § Fixture coverage footgun.
  - SHOULD_FIX (Open, not a CR): document 10-quant-audit.md FINDING 1 (YTD vs sliding-window anchor convention) near the `window_start_date` docstring or in financial-methodology.md.

risks:
  - none

## Orchestrator brief
- Verdict: PASS. CR-2 #1 (chart ignoring range selector, my own prior BLOCKING) is genuinely resolved — re-read `PerformanceBenchmarkCard.tsx` myself; chart now filters+re-bases on `window_start_date`. No new BLOCKING. No new CR file. Full evidence in § Range-filter re-check (DoD 1).
- Full suite re-run by me, not trusted from prior heads: backend 22 passed, tsc clean, vitest 49/49, dead-code gate clean (see `verification` block above).
- DoD's typing question (`window_start_date?:` optional vs strict) judged SHOULD_FIX, not BLOCKING, with a related coverage risk — see § Typing judgment (DoD 2) and § Fixture coverage footgun.
- goldens/fixtures spot-checked, internally consistent, no full re-audit performed (10-quant-audit.md already proved the numbers) — see § Goldens/fixtures spot check (DoD 3).
- Diff scope confirmed clean end to end (only the card's own files + two backend files changed, no orphaned refs) — see § Diff scope sanity.
- Three SHOULD_FIX items surfaced, all routed to Open in `handoff`, none to a CR: docs-fields entry, typing/fixture tightening, quant FINDING 1 doc note.
- CR-2 #2/#3 (already routed to tech-debt-register by human decision per this order's non_goals) — untouched, not re-litigated.

## Range-filter re-check (DoD 1)
`PerformanceBenchmarkCard.tsx:94-95` now reads:
```
const metrics: DashboardRangeMetrics = rangeMetrics[activeRange]
const chartData = buildIndexedSeries(result.performance_series, metrics.window_start_date ?? null)
```
`buildIndexedSeries` (lines 46-92) filters `perf` to `>= windowStartDate` when non-null, and re-bases the portfolio leg's already-published `portfolio_return_pct` chain to 100 at the sliced first point (`pctAtWindowStart`), and the benchmark leg to its own sliced anchor price — both algebraically distinct from the CR-1 day-one formula, confirmed by reading the branch, not by trusting the reports. `window_start_date=null` (e.g. "All") runs the original CR-1 day-one path unchanged.

New test coverage genuinely exercises this, not just presence of the field: `PerformanceBenchmarkCard.test.tsx`'s `range-switch chart re-anchoring (CR-2 #1)` block (lines 185-283) gives 1M and 3M distinct `window_start_date`s on the same underlying series and asserts both the plotted date list AND the re-based trajectory differ (`oneMonth[0].portfolio` vs `threeMonth[1].portfolio`, same calendar date, different indexed value because each range re-bases to its own pivot) — this is the exact class of assertion CR-2 #1's `why` said was missing. `DashboardPanel.test.tsx`'s new test (lines 275-296) confirms the same at the integration level: clicking the "3M window" button changes the array `LineChart` actually receives, intercepted via a `vi.mock('recharts', ...)`, not SVG geometry. Both read myself; both pass.

## Typing judgment (DoD 2)
`types.ts:553` ships `window_start_date?: string | null` where 07-backend.md's contract note asked for the strict `window_start_date: string | null`. Judged **SHOULD_FIX, not BLOCKING**, for three reasons:
1. **No runtime defect.** `PerformanceBenchmarkCard.tsx:118` reads `metrics.window_start_date ?? null` — `undefined` and `null` are normalized identically before `buildIndexedSeries` ever sees them. There is no code path where the optional key being absent produces a different outcome than it being present-and-null.
2. **Matches this exact type's own precedent.** `portfolio_return_trust?: 'verified' | 'degraded' | 'unavailable'` (the sibling field two lines above) is the same shape — optional in TS, always-serialized-with-a-default on the backend. This is an established convention in `DashboardRangeMetrics`, not a new inconsistency `window_start_date` introduces.
3. **Wrong-direction mismatch is the BLOCKING one.** The architecture pack's own example ("a field the backend made optional and the frontend typed as required... fails on the first import with short history") is backend-lenient/frontend-strict. Here it is the reverse: backend-strict (always present) / frontend-lenient (optionally present) — the safe direction, since a frontend that tolerates absence can never crash on a field that always arrives.

Still genuinely worth fixing: tightening the type to match the contract note is free precision, and doing so would force `portfolioFixtures.ts` to supply real values — see next section for why that matters more than the type itself.

## Fixture coverage footgun
`portfolioFixtures.ts`'s `createImportedDashboardFixture` (the shared fixture `DashboardPanel.test.tsx` and most of `PerformanceBenchmarkCard.test.tsx` build on) has **no** `window_start_date` in any of its five `range_metrics` entries (1M/3M/YTD/1Y/All) — confirmed by direct read (lines 1296-1330-ish) and by grep (zero matches for `window_start_date` in the file). Because the field is optional, this still type-checks; because `?? null` normalizes, it still renders correctly — every range gets `null`, i.e. the full-history, unfiltered chart. That is functionally fine today, but it means: any *future* test that renders `PerformanceBenchmarkCard`/`DashboardPanel` off the shared fixture without explicitly overriding `window_start_date` per range (the way 09-test.md's two new tests correctly do, inline) would silently exercise the exact "chart ignores the range selector" shape CR-2 #1 fixed, and pass, because the fixture itself never gives two ranges different anchors. Not a defect in what shipped — the two tests that matter right now both override correctly — but a latent gap: the *default* path back into this bug is one un-overridden fixture use away. SHOULD_FIX: give `createImportedDashboardFixture`'s `range_metrics` real, distinct `window_start_date` values per range so the shared fixture itself cannot regress-mask this bug.

## Goldens/fixtures spot check (DoD 3)
`dashboardGoldens.ts` (IB2026, lines 31450-31659): 1M → `2026-07-13`, 3M → `2026-05-11`, YTD → `2026-01-08`, 1Y → `2026-01-08` (same as YTD — consistent with 10-quant-audit.md's confirmed "window > available history falls back to full series" behavior, since this account has under a year of history), All → `null`. Internally coherent, matches the invariant table 10-quant-audit.md already proved numerically on a synthetic series — spot-checked against the real golden, not re-derived. `portfolioFixtures.ts` correctly carries no `window_start_date` at all (see § Fixture coverage footgun) — absence is consistent with the optional type, not a contradiction.

## Diff scope sanity
`git diff --stat` shows 8 files changed, including `DashboardPanel.tsx` (-19 lines, no additions) — this is CR-1's `normalizePerformanceSeries` dead-code removal (the raw-NAV-ratio duplicate), already reviewed and passed clean by dispatch 06; nothing new landed there this round. Nothing uncommitted outside the Performance & Benchmark card's own files and its two schema/service backend files. `detect_deadcode.py --strict` confirms no orphaned reference to the removed function.
