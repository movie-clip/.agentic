REPORT 2026-09-07-new-epic-perf-benchmark-trust/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE (read-only recon)
  result:    NOT_RUN
  detail:    All four points confirmed against current code; file:line evidence in handoff and the sections below.

contract_notes:
  - docs/contracts/dashboard-fields.md:105 documents `benchmark_history: "unavailable"` "for a valid dashboard-history run", but the `not benchmark_rows` gate at dashboard_history_engine.py:304 makes that state unreachable when benchmark rows are fully absent — the run is forced fully unavailable instead. A P3 fix touches this doc.
  - docs/contracts/dashboard-fields.md:98-101 defines `source_status.monthly_returns` states (live/suppressed/unavailable) but nothing there records that a published monthly figure may still contain a withheld/reconciled day. A P1 fix that adds per-day withholding to monthly returns should reconcile this section.
  - No `docs/product/epic-roadmap.md` and no `docs/product/prd/**` exist in the working tree (both named in scope, CLAUDE.md, and project.md). Prior-art / roadmap tracking for this repo lives in GitHub issues (`docs/agents/issue-tracker.md`); I have no shell and could not query `gh`.

pack_corrections:
  - none

handoff:
  - P1 CONFIRMED. Monthly returns are computed by `_compute_contribution_adjusted_monthly_returns` (services/quant-engine/app/services/dashboard_history_engine.py:837-863); the daily-return line is 856: `daily_return = ((state.total_portfolio_value - state.external_cash_flow) / previous_state.total_portfolio_value) - 1`. It consults neither `state.return_is_publishable` nor `state.reconciliation_adjustment`, and subtracts only `external_cash_flow` (deposits/withdrawals) — not `unbacked_cash_flow` or `trade_flow`. See § P1.
  - P1 shared withholding rule is the `DailyPortfolioState.return_is_publishable` property at services/quant-engine/app/schemas/reconciliation.py:588-629 (returns False only for a material `unbacked_cash_flow`; a reconciled terminal day is publishable and corrected via `market_derived_terminal_value`). Its docstring names the three intended consumers: `performance.py`, `risk.py`, `attribution.py` — the monthly path is not one of them.
  - P1 main-chain contrast: `_time_weighted_daily_return` (services/quant-engine/app/analytics/performance.py:362-374) does `if not current_state.return_is_publishable: return None` (line 367) and removes the reconciliation adjustment at line 373 (`current_value = current_state.total_portfolio_value - (current_state.reconciliation_adjustment or 0.0)`). This feeds `build_true_performance_series` (performance.py:298) and, transitively, the range TWR summary. The monthly path bypasses all of it.
  - P1 only backstop today is downstream and coarse: `_monthly_returns_are_reliable` (dashboard_history_engine.py:866-875) hides the WHOLE grid when any `abs(return_pct) > 100` or any state has negative portfolio value; `monthly_returns_suppressed` (line 396) also keys on negative portfolio value only. A fabricated month at or below +100% with no negative value publishes. See § P1.
  - P2 CONFIRMED (warning direction). PerformanceBenchmarkCard.tsx:249 condition: `withheldImpact != null && withheldDates.length > 0`. `withheldImpact` = `result.run_metadata?.withheld_return_impact_pct` (line 133). Copy at lines 253-256 renders the sign (`withheldImpact > 0 ? '+' : ''` then `withheldImpact.toFixed(2)`) but the words are hardcoded: "...percentage points, so the number above understates by roughly that much." See § P2.
  - P2 sign source: `withheld_return_impact_pct` (performance.py:265-295) returns `round(_chain(honour_withholding=False) - _chain(honour_withholding=True), 2)` — (return WITH withheld days) minus (shown return). Negative when including withheld days would lower the return, i.e. the shown value overstates — exactly the case the copy mislabels. Published at dashboard_history_engine.py:465.
  - P3 CONFIRMED (benchmark outage suppresses all output). Gate 1: dashboard_history_engine.py:304 `if not benchmark_rows or not has_any_symbol_price_history(symbol_price_histories):` -> `_build_unavailable_dashboard_history_result(...)` (lines 305-311). Gate 2: build_true_performance_series (performance.py:305) `if not daily_states or not benchmark_rows: return []`, which then trips `has_replay_outputs(...)` false at dashboard_history_engine.py:386 -> same unavailable result (lines 387-393). Both key on `benchmark_rows` truthiness; holdings history / replay states are not consulted before the bail-out. See § P3.
  - P3: benchmark rows are fetched at dashboard_history_engine.py:286-297 (verified allowlist path vs `get_historical_prices`); replay/holdings inputs (`symbol_price_histories` line 298, `daily_states` line 331-344) are built AFTER the line 304 gate, so the engine already has everything needed to key the two independently.
  - P4 CONFIRMED (benchmark fixed to default). Route: services/quant-engine/app/api/routes/dashboard_history.py:19-24 — `run_imported_dashboard_history_route(snapshot: ImportedPortfolioSnapshot)`, body is the bare snapshot. `ImportedPortfolioSnapshot` (services/quant-engine/app/schemas/imports.py:93-104) has no `benchmark_symbol` field. Frontend adapter posts the snapshot unchanged: portfolioAnalysisAdapter.ts:215-231.
  - P4: the service already accepts it — `run_imported_dashboard_history(snapshot, benchmark_symbol: str | None = None, *, market_data=None)` at dashboard_history_engine.py:263-268; resolved at line 274 `resolved_benchmark_symbol = benchmark_symbol or DEFAULT_BENCHMARK_SYMBOL`. Default is `DEFAULT_BENCHMARK_SYMBOL = "SPY"` (services/quant-engine/app/core/constants.py:13). The non-imported `/run` path (`DashboardHistoryEngineRequest` -> `PortfolioEngineRequest.benchmark_symbol: str | None = None`, portfolio_engine.py:25) already carries the field but `run_dashboard_history_engine` is a stub that always returns unavailable (dashboard_history_engine.py:241-260).
  - P4: PerformanceBenchmarkCard.tsx:128 — `const benchmarkSymbol = result.run_metadata?.reproducibility?.benchmark_symbol ?? 'Benchmark'`. Display only; no selector control anywhere in the card. The symbol round-trips via `DashboardHistoryRunReproducibility.benchmark_symbol` (dashboard_history_engine.py:466-472).
  - Blast radius per point: see § Blast radius.
  - Prior-art: see § Prior art. None of the four points is tracked in any in-tree doc; `docs/tech-debt-register.md:14` has only a generic "withheld outputs are conservative" row.

risks:
  - GitHub issues are this repo's roadmap/PRD/tech-debt surface (`docs/agents/issue-tracker.md`); with no shell I could not run `gh issue list`, so "not tracked" in § Prior art means "not in any tracked doc file", not "no GitHub issue exists". A lane with `gh` should confirm before the producer assumes these are net-new.
  - P1: I confirmed the monthly path ignores `return_is_publishable`; I did not construct a runtime repro. The order states the reporter reproduced a +100% figure with a withheld state. `_monthly_returns_are_reliable`'s `> 100` guard means the exact "+100%" case is only suppressed if it exceeds 100, so the severity depends on the fabricated magnitude.
  - P3: `_withhold_benchmark_return_series` (dashboard_history_engine.py:237-238) and `_build_dashboard_benchmark_history_status` show the engine already has a "benchmark present but degraded" concept; the gap is specifically the fully-absent case at line 304. A fix must decide what `valuation_dates` (line 313, currently `sorted({row["date"] for row in benchmark_rows})`) becomes when benchmark rows are absent — the replay walk is currently anchored to benchmark dates.
  - Scope named `docs/product/epic-roadmap.md`, `docs/product/prd/**`, `docs/product/current-product-state.md`; only the last exists. Treat the roadmap/PRD scope entries as stale.

## P1 — monthly returns can publish a withheld/reconciled day

Live path is `/run-imported` -> `run_imported_dashboard_history` -> `_build_range_metrics` (dashboard_history_engine.py:561). Per range it does:

- line 604: `monthly_returns = _compute_contribution_adjusted_monthly_returns(states)` where `states` is the raw `daily_states` filtered to the visible window (line 603).
- line 629: `monthly_returns=[DashboardMonthlyReturn(...) for item in monthly_returns]` — emitted verbatim.
- line 630: `monthly_returns_reliable=_monthly_returns_are_reliable(monthly_returns, states)`.

`_compute_contribution_adjusted_monthly_returns` (lines 837-863) loop body:

```
for state in anchored_states:
    if previous_state is not None and previous_state.total_portfolio_value != 0:
        daily_return = ((state.total_portfolio_value - state.external_cash_flow) / previous_state.total_portfolio_value) - 1
        month = state.date[:7]
        growth_by_month[month] = growth_by_month.get(month, 1.0) * (1 + daily_return)
    previous_state = state
```

No reference to `return_is_publishable`, `reconciliation_adjustment`, `unbacked_cash_flow`, `trade_flow`, or `market_derived_terminal_value`. Contrast the main chain's per-day function `_time_weighted_daily_return` (performance.py:362-374), which short-circuits to `None` on `not current_state.return_is_publishable` (line 367) and nets out `reconciliation_adjustment` (line 373).

Shared withholding rule: `DailyPortfolioState.return_is_publishable` at reconciliation.py:588-629 — a `@property` on the state model. False only when `abs(unbacked_cash_flow) / abs(total_portfolio_value) > REPLAY_UNBACKED_CASH_MATERIAL_SHARE` (lines 624-629). Its docstring (lines 603-605) says it is defined on the state "so the three consumers (`performance.py`, `risk.py`, `attribution.py`) cannot drift apart" — the dashboard monthly path is a fourth consumer that was never wired in.

Backstops that exist today (both coarse, whole-grid):
- `_monthly_returns_are_reliable` (lines 866-875): returns False if `< 2` months, or any state `total_portfolio_value < 0`, or `any(abs(item["return_pct"]) > 100 ...)`.
- `monthly_returns_suppressed` (line 396): `any(state.total_portfolio_value < 0 for state in daily_states)`.

## P2 — withheld-return warning direction

PerformanceBenchmarkCard.tsx, lines 246-258:

```
{withheldImpact != null && withheldDates.length > 0 ? (
  <p className="helper" ...>
    {withheldDates.length} {withheldDates.length === 1 ? 'day is' : 'days are'} excluded from
    this return because their portfolio value moved for a reason that was not a market move.
    Including them would change the full-period figure by about{' '}
    {withheldImpact > 0 ? '+' : ''}
    {withheldImpact.toFixed(2)} percentage points, so the number above understates by roughly
    that much. See Replay Disclosures for which days and why.
  </p>
) : null}
```

- Driving value: `withheldImpact` = `result.run_metadata?.withheld_return_impact_pct ?? null` (line 133).
- Shown when: at least one withheld date AND a non-null impact. No sign branch on the "understates" clause.
- Engine sign: `withheld_return_impact_pct` (performance.py:265-295) = `_chain(honour_withholding=False) - _chain(honour_withholding=True)` = (period return counting withheld days) − (period return shown). Positive => withheld days would raise the return => "understates" is correct. Negative => withheld days would lower it => shown value **overstates**, but the copy still says "understates by roughly that much" next to a negative number.

## P3 — benchmark outage suppresses all portfolio output

`run_imported_dashboard_history` order of operations:
1. lines 286-297: fetch `benchmark_rows` (verified-allowlist direct path if `resolved_benchmark_symbol in VERIFIED_BENCHMARK_SYMBOL_ALLOWLIST`, else `market_data.get_historical_prices`).
2. line 298-302: fetch `symbol_price_histories` for current holdings.
3. **line 304**: `if not benchmark_rows or not has_any_symbol_price_history(symbol_price_histories):` -> `return _build_unavailable_dashboard_history_result(...)` (lines 305-311, with `history_start_date=None, history_end_date=None`).
4. line 313: `valuation_dates = sorted({row["date"] for row in benchmark_rows})` — the replay walk is anchored on benchmark dates.
5. lines 320-344: replay states built.
6. line 380-385: `raw_performance_series = build_true_performance_series(daily_states, benchmark_rows, ...)`.

`build_true_performance_series` (performance.py:298-359), **line 305**: `if not daily_states or not benchmark_rows: return []`. An empty series then fails `has_replay_outputs(daily_states, raw_performance_series)` at dashboard_history_engine.py:386 -> `_build_unavailable_dashboard_history_result` again (lines 387-393).

So a benchmark outage (`benchmark_rows == []`) is fatal at two independent points, and neither consults holdings history or replay state usability. The order's desired behaviour — portfolio TWR/MWR/contributions/monthly independently available with benchmark fields `unavailable` — has no code path today. Note the engine already has partial machinery for "benchmark present but weak": `_withhold_benchmark_return_series` (line 237), `_build_dashboard_benchmark_history_status` (line 395), `_allow_benchmark_return_output` (used in `_build_range_metrics`).

## P4 — benchmark selector gap

- Route (dashboard_history.py:19-24): `def run_imported_dashboard_history_route(snapshot: ImportedPortfolioSnapshot)`. Body = the snapshot only.
- `ImportedPortfolioSnapshot` (imports.py:93-104): `statement`, `statement_totals`, `instruments`, `cash_balances`, `positions`, `ledger_entries`. No benchmark field. (`benchmark_symbol` at imports.py:125 is on the unrelated `SnapshotAnalysisRequest`.)
- Service (dashboard_history_engine.py:263-268): `run_imported_dashboard_history(snapshot, benchmark_symbol: str | None = None, *, market_data=None)`. Line 274: `resolved_benchmark_symbol = benchmark_symbol or DEFAULT_BENCHMARK_SYMBOL`.
- Default: `core/constants.py:13` -> `DEFAULT_BENCHMARK_SYMBOL = "SPY"`.
- Frontend call: portfolioAnalysisAdapter.ts:215-231 `runImportedDashboardHistory(snapshot, apiUrlOptions?)` posts `JSON.stringify(snapshot)` — no symbol arg. Invoked from App.tsx:557.
- Card display: PerformanceBenchmarkCard.tsx:128 `const benchmarkSymbol = result.run_metadata?.reproducibility?.benchmark_symbol ?? 'Benchmark'`. Used only as a label (lines 147, 174, 210, 215, 229). No `<select>` / input in the file.
- The `/run` (non-imported) route already accepts `benchmark_symbol` via `DashboardHistoryEngineRequest(PortfolioEngineRequest)` (portfolio_engine.py:25, `str | None = None`) and `run_dashboard_history_engine` reads `request.benchmark_symbol` (dashboard_history_engine.py:243) — but that function is a stub: both branches (lines 245-252, 254-260) return `_build_unavailable_dashboard_history_result`. So there is no live route that honours a caller-chosen benchmark.

## Blast radius

**P1 (monthly withholding)**
- backend: `services/quant-engine/app/services/dashboard_history_engine.py` — `_compute_contribution_adjusted_monthly_returns` (837-863), possibly `_monthly_returns_are_reliable` (866-875), `monthly_returns_suppressed` (396).
- schema: none required if the fix only drops days; `services/quant-engine/app/schemas/dashboard_history.py` `DashboardMonthlyReturn` (32-34) if a per-month "partial/withheld" flag is added -> then `apps/desktop/src/features/portfolio/types.ts` + `docs/contracts/dashboard-fields.md`.
- frontend: `apps/desktop/src/features/portfolio/MonthlyReturnsGrid.tsx` consumes `range_metrics[activeRange].monthly_returns`.
- tests/goldens: `services/quant-engine/app/scripts/export_dashboard_goldens.py`, `frozen_market_data.py`; `app/tests/test_analytics.py`, `app/tests/test_ledger_replay_audit.py`; dashboard goldens regenerated by `scripts/run_all_tests.py`. Frontend: `apps/desktop/src/features/portfolio/DashboardPanel.test.tsx`, MonthlyReturnsGrid tests, `src/test/portfolioFixtures.ts`.
- methodology: `docs/finance/financial-methodology.md` monthly-returns / withholding sections (quant lane owns).
- guardrail: this is `analytics/`-adjacent trust logic -> quant lane (research before, audit after) per project.md.

**P2 (warning direction)**
- frontend only: `apps/desktop/src/features/portfolio/PerformanceBenchmarkCard.tsx:246-258`. No schema/engine change (`withheld_return_impact_pct` sign is already correct).
- tests: `PerformanceBenchmarkCard` test(s) under `apps/desktop/src/features/portfolio/`; check for a case with negative impact.
- docs: `docs/contracts/dashboard-fields.md` withheld-return disclosure row (line ~230 area) if copy semantics are documented.

**P3 (benchmark outage)**
- backend: `services/quant-engine/app/services/dashboard_history_engine.py` — line 304 gate, line 386 `has_replay_outputs` gate, `valuation_dates` derivation (313), benchmark fetch/branching (286-297), `_build_range_metrics` benchmark toggles.
- backend: `services/quant-engine/app/analytics/performance.py:305` (`build_true_performance_series` bail-out) — this is `analytics/` -> quant lane mandatory.
- schema: likely none (fields already nullable), but `DashboardHistoryRunSourceStatus.benchmark_history` / `section_trust.benchmark_path` semantics change -> `docs/contracts/dashboard-fields.md:102-107` and TS `types.ts`.
- frontend: `PerformanceBenchmarkCard.tsx` (benchmark line renders when `p.benchmark_price` present), `DashboardPanel.tsx`, `MonthlyReturnsGrid.tsx` — must tolerate portfolio-present / benchmark-absent.
- other engines keyed on benchmark rows: `drift.py`, `correlation.py`, `attribution.py`, `benchmark_service.py` (`build_benchmark_comparison`) — check whether any share the fail-closed pattern.
- tests/goldens: dashboard goldens, `export_dashboard_goldens.py`, `frozen_market_data.py` (would need a benchmark-absent fixture), `app/tests/test_analytics.py`, route tests `app/tests/` for `dashboard-history`, App.test.tsx dashboard-history mocks.
- methodology: `docs/finance/financial-methodology.md` (truth-class separation, benchmark-availability rules) — quant lane.

**P4 (benchmark selector)**
- schema: `services/quant-engine/app/schemas/imports.py` `ImportedPortfolioSnapshot` (add optional `benchmark_symbol`) OR change the route signature to take a wrapper/param — `app/schemas/` change -> NOT express-lane per project.md, schema hook fires, mirror to `types.ts` + `docs/contracts/dashboard-fields.md`.
- route: `services/quant-engine/app/api/routes/dashboard_history.py:19-24` — pass the symbol through to `run_imported_dashboard_history`. Route tests in `app/tests/`.
- frontend: `apps/desktop/src/features/portfolio/portfolioAnalysisAdapter.ts:215-231` (`runImportedDashboardHistory` signature + body), `App.tsx:551-568` (call site + where the choice is held / persisted — `app/` workspace persistence), a new selector control in `PerformanceBenchmarkCard.tsx` or `DashboardPanel.tsx`, `MonthlyReturnsGrid`/range selector sync (US-25.2 pattern, activeRange is already parent-owned).
- market data: non-allowlist symbols take the `get_historical_prices` path (dashboard_history_engine.py:292-297) and cannot be `verified_total_return` (see `_validate_verified_benchmark_slice`, lines 61-121; `VERIFIED_BENCHMARK_SYMBOL_ALLOWLIST`) -> trust/return-basis implications -> quant lane. `fmp-data` skill relevant.
- tests/goldens: dashboard goldens (benchmark symbol is in `reproducibility`), `frozen_market_data.py` must have prices for any newly-selectable symbol used in tests, App.test.tsx dashboard-history payloads, `portfolioFixtures.ts`.
- docs: `docs/product/current-product-state.md:13` ("selectable periods" — would add "selectable benchmark"), `docs/contracts/dashboard-fields.md`, `docs/architecture/system-architecture.md` route inventory.

## Prior art

Searched `docs/tech-debt-register.md`, `docs/product/current-product-state.md`, `docs/contracts/dashboard-fields.md`, `docs/finance/financial-methodology.md` (targeted grep only, per non-goals), and the `docs/` tree. There is **no `docs/product/epic-roadmap.md` and no `docs/product/prd/**`** in the working tree despite both being referenced by CLAUDE.md, project.md, and this order's scope.

- **P1 (monthly fabricated return):** not tracked. Nearest: `docs/tech-debt-register.md:14` — `| Medium | Trust semantics | Some broker-replay investor-economics and drawdown outputs remain withheld because their supporting evidence is insufficient. | ... | Do not relax publication rules without a methodology review and regression coverage. |` — this is about *over*-withholding, the opposite failure.
- **P2 (warning direction):** not tracked. `docs/contracts/dashboard-fields.md` documents the withheld-return disclosure exists but not its sign semantics.
- **P3 (benchmark outage):** not tracked. `docs/product/current-product-state.md` "Known limitations" (55-63) does not mention it. `docs/contracts/dashboard-fields.md:105` describes a `benchmark_history: "unavailable"`-within-a-valid-run state that the code does not currently produce for fully-absent rows.
- **P4 (benchmark selector):** not tracked. `docs/product/current-product-state.md:13` advertises "selectable periods" only; no mention of benchmark choice. `DEFAULT_BENCHMARK_SYMBOL` comment (`core/constants.py:11-13`) treats "SPY" as the fixed default.
- Repo-wide issue tracking is GitHub issues (`docs/agents/issue-tracker.md`); not queryable from this lane (no shell).
