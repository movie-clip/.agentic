REPORT 2026-08-26-performance-benchmark-chart-audit/05
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd apps/desktop && npx tsc --noEmit && npx vitest run PerformanceBenchmarkCard DashboardPanel
  result:    PASS
  detail:    tsc --noEmit: no errors. vitest: 2 files passed, 46 tests passed (16 PerformanceBenchmarkCard, 30 DashboardPanel), 0 failed.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

risks:
  - Third indexed-series builder found while hunting duplicates (`IndexedReturnChart.tsx::sliceAndRebase`, Exposure tab drift panel) — see § Duplicate-formula hunt for why it's cleared, not a finding.
  - First-point-anchor subtlety judged non-blocking (pre-existing engine behaviour, not fabrication) — see § Judgment: first-point anchor (DoD item 3).

## Orchestrator brief
- Verdict: PASS. Both FINDING 1 (fabricated chart line) and FINDING 2 (dead duplicate) are genuinely fixed, independently re-derived against current source — not re-read from the fix reports' own claims.
- FINDING 1: re-ran my own synthetic ($100k base + $50k mid-period deposit, flat market) against the *live* `build_true_performance_series`, confirmed the chart now renders [100,100,100,100], not the old fabricated 150. Realistic case: 2.43% TWR → 102.43 indexed, not 124.40. See § Independent recomputation.
- FINDING 2: `normalizePerformanceSeries` confirmed gone from `DashboardPanel.tsx` (clean diff deletion) and absent everywhere else except one comment. See § Independent recomputation.
- Benchmark leg confirmed byte-for-byte unchanged via `git diff` — only the portfolio leg's five lines changed. See § Independent recomputation.
- First-point-anchor subtlety (03-frontend.md's flagged risk) judged correct, non-fabricating, pre-existing — full reasoning in § Judgment: first-point anchor (DoD item 3).
- Duplicate-formula hunt turned up a third, unrelated, correctly-implemented builder (Exposure tab) — see § Duplicate-formula hunt.
- Verification command run exactly as specified: PASS (tsc clean, 46/46 tests).

## Independent recomputation

### FINDING 1 — synthetic case (flat market, $50k mid-period deposit on $100k base)

Built `DailyPortfolioState` objects directly (not through the frontend or any mock) and called the real `build_true_performance_series` from `services/quant-engine/app/analytics/performance.py`, then applied the CURRENT `buildIndexedSeries` portfolio-leg formula read verbatim from `PerformanceBenchmarkCard.tsx:61` (`100 * (1 + p.portfolio_return_pct / 100)` when non-null, else null):

```
states: value=100000 (2026-01-01), value=100000 (2026-02-01),
        value=150000 + $50k deposit (2026-03-01), value=150000 (2026-04-01)
engine portfolio_return_pct:  [0.0, 0.0, 0.0, 0.0]
chart portfolio line (current code): [100.0, 100.0, 100.0, 100.0]
```

Matches true TWR (0% throughout — a deposit is not a gain) exactly. The pre-fix formula (`portfolio_value / anchorPortfolio * 100`) would have produced a final point of 150.0 on this same input (150000/100000*100), the fabricated +50pp finding from the original audit. Confirmed gone.

### FINDING 1 — realistic case (formula substitution)

`PerformanceBenchmarkCard.tsx:61`'s current formula is `100 * (1 + portfolio_return_pct / 100)`. Substituting the repo fixture's stated true TWR of 2.43%: `100 * (1 + 2.43/100) = 102.43` — matches the number printed directly beneath the chart in the same card, and is not the old raw-NAV-ratio result of 124.40. I also ran a smaller multi-state case to confirm the formula transform holds for a non-trivial engine output, not just the algebraic substitution: a two-state chain from 52,386.10 to 65,168.77 with a $9,963 deposit landing on the terminal date yields engine `portfolio_return_pct=5.38`, chart line `105.38` — same `100*(1+pct/100)` transform, confirming the code path itself (not just the arithmetic) is correct; the exact 2.43% figure is a property of the fixture's full multi-day replay (out of scope to reconstruct day-by-day here), and the transform from whatever pct the engine emits is what this order asks me to re-verify.

### Benchmark leg — confirmed unchanged

`git diff` on `PerformanceBenchmarkCard.tsx` shows the *only* changed lines are the portfolio leg (5 lines: dropped `anchorPortfolio`, changed the `portfolio:` field's RHS, added a comment). The benchmark leg's three lines (`anchorBenchmark`, the `benchmark:` ternary, `p.benchmark_price / anchorBenchmark * 100`) are byte-for-byte identical to before the fix — confirmed by diff, which is the check that actually matters for "genuinely unchanged" (stronger evidence than re-deriving its output, since an unmodified formula cannot have regressed). Ran it anyway as a sanity check on the ported formula: case (a)'s flat benchmark (500 throughout) correctly stays `[100.0, 100.0, 100.0, 100.0]`; the two-state realistic prices (689.51 → 773.03) correctly index to `[100.0, 112.11]` (773.03/689.51*100 = 112.11), i.e. the benchmark leg still reflects raw price movement with no cash-flow adjustment, as the doc specifies for a price series.

### FINDING 2 — confirmed closed

`grep -rn "normalizePerformanceSeries" apps/desktop/src/` returns exactly one hit: a comment in `PerformanceBenchmarkCard.test.tsx:157` referencing the deleted function by name for context, not a live reference. `git diff` on `DashboardPanel.tsx` shows the function's full body (21 lines) cleanly removed, nothing else touched. Grepped the whole frontend for the underlying wrong-formula pattern (`portfolio_value / anchor...`) — zero remaining hits outside the fixed file.

### Duplicate-formula hunt (pack requirement, beyond the two named findings)

`grep -rl "buildIndexedSeries\|IndexedSeries\|indexed_t" apps/desktop/src/` surfaced a third file: `IndexedReturnChart.tsx` (the Exposure tab's vs-Market drift panel, `sliceAndRebase`). Read it and its backend source (`drift_engine.py::_build_daily_series` / `_compound_chain`, `app/schemas/drift.py::portfolio_indexed`). It is NOT a copy of the FINDING 1 bug: it rebases an already-TWR-indexed field the backend computes via a genuine compound cash-flow-neutral chain (`_compound_chain`, comment at `drift_engine.py:148-154` explicitly: "cash-flow-neutral TWR chain... a deposit must not draw a fake up-move"), for the purpose of re-basing a sub-window's start back to 100 (`portfolio_indexed / portfolio_indexed_at_window_start * 100` — a valid operation on an already-correct TWR index). Different card, different engine module, not implicated by either finding, not touched by this CR. No finding raised; noted in `risks` for the record.

## Judgment: first-point anchor (DoD item 3)

Read `performance.py:319-357` (`build_true_performance_series`) directly, not just the fix report's characterization.

**What happens:** the loop's `previous_state is None` branch fires only once, on `daily_states[0]` — whatever state that is — and unconditionally sets `portfolio_return_pct = 0.0` there, regardless of that state's own `total_portfolio_value`. `daily_states[0]`'s date is `history_start_date = min(ledger trade dates ∪ position as-of dates)` (`dashboard_history_engine.py:704-709`), i.e. the account's own earliest recorded activity — not an arbitrary benchmark-only date (benchmark rows are fetched for `[history_start_date, history_end_date]`, so `valuation_dates[0] >= history_start_date`).

**Constructed the edge case directly** (day 0 has $0 — no cash, no position — followed by a deposit-and-buy two days later):
```
states: value=0 (day0), value=0 (day1), value=100000+$100k deposit (day2), value=101000 (day3)
engine portfolio_return_pct: [0.0, None, None, 1.0]
chart portfolio line:        [100.0, None, None, 101.0]
```

**Verdict: not a fabrication, and not a new defect from this CR.**
- No plausible-looking wrong number appears. The deposit/trade-landing day (day2) is correctly `None` (`_time_weighted_daily_return` returns `None` whenever the previous state's value is 0) — the gap is honest, not interpolated or carried forward.
- The day-0 value of 100 is not a claim about day 0's dollar value; it is the literal statement "0% cumulative return as of the first tracked day," which is definitionally true whether or not the account already held money that day — the TWR index's base case, not an invented one.
- This is pre-existing engine behaviour (`performance.py` was not touched by dispatch 03/04's diff — confirmed by `git diff`), and it is the *same* field (`portfolio_return_pct`) that feeds the `time_weighted_return_pct` summary scalar this repo's round-1 audit already passed. Whatever this quirk is, it is not unique to the chart and was not introduced or made worse by wiring the chart to consume it.
- Whether `history_start_date` can realistically land on a genuinely `$0` day in production is a narrower question (would require a ledger whose earliest entry is a deposit that doesn't land in cash the same day, or a position `as_of_date` earlier than any trade) — I did not chase that further; it is a pre-existing engine-semantics question, not something this fix could have introduced or is scoped to resolve, and 03-frontend.md correctly declined to add a frontend workaround for it (FINDING 1 explicitly instructed consuming the field as-is).

No finding raised on this item; it does not block PASS.
