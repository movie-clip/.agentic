REPORT 2026-09-23-cashflow-chart/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only recon order; no verification command was named

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - see § Map below — file:line citations for the aggregation, view-model wiring, and Avalonia rendering of the Cash Flow Trend chart
  - see § Findings — three concrete divergence candidates (is_deleted filter gap, future-booked anchor date, independent income/expense bar scaling) with file:line
  - see § Blast radius — all three findings are confined to a single layer each; none requires a Contracts interface or use-case signature change

risks:
  - the `is_deleted` filter gap in `GetByDateRangeAsync` (Infrastructure) is currently inert because no code path in this repo ever sets `IsDeleted = true` on a transaction (only `DeleteAllAsync` hard-deletes everything) — flagged as a latent inconsistency, not a live bug, and I did not exhaustively search every use case for a soft-delete write I may have missed
  - I did not find a test file specifically asserting `BuildTrend`'s month-bucket math; `tests/HomeCharts.Application.Tests/` was not opened in this recon — the orchestrator may want a lane to check whether the behavior described below is already covered before treating any finding as a gap in tests too

## Orchestrator brief
<15 lines, index only>

- Trend series computed in `BuildDashboardSnapshotUseCase.BuildTrend` (Application layer) — see § Map: Aggregation.
- Rendered as a custom bar chart (no charting library) in `MainWindow.axaml` + `MainWindowViewModel` — see § Map: View model and § Map: Rendering.
- Query boundary (`ITransactionRepository.GetByDateRangeAsync`, SQLite) is a plain inclusive date range with no `is_deleted` filter, unlike a sibling query in the same file — see § Findings, finding 1.
- Month anchor for the trend window is the max `BookingDate` among fetched transactions, not "today" — see § Findings, finding 2 (matters if any transaction is booked in the future).
- Income and expense bars are normalized to two *independent* maxima (`maxIncome`, `maxExpenses`), so bar heights are not comparable to each other across series — see § Findings, finding 3.
- No currency conversion or filtering anywhere in the aggregation — all `Amount` values are summed regardless of `Currency` — see § Findings, finding 4.
- Sections below: **Map** (Aggregation / Query / View model / Rendering), **Findings** (4 numbered items), **Blast radius**, **Sources of truth**.
- None of the findings require a `Contracts` change or use-case signature change; all are single-layer.
- No file was modified; this is a pure recon report.

## Map

### Aggregation — `HomeCharts.Application`

- `src/HomeCharts.Application/UseCases/BuildDashboardSnapshotUseCase.cs:206-241` — `BuildTrend(transactions, trendMonths, anchorMonth)` is the exact method that computes the monthly income/expense/net series shown as "Cash Flow Trend".
  - Line 209: `startMonth = anchorMonth.AddMonths(-(months - 1))` — window is `trendMonths` (12, hard-coded by the caller) months ending at `anchorMonth`.
  - Line 211-213: groups the already-fetched `transactions` collection by `(BookingDate.Year, BookingDate.Month)`, filtered to `BookingDate >= startMonth` only (no upper bound inside `BuildTrend` itself — the outer date range from the repository call is the only upper bound).
  - Line 218-219: `Income = Sum(Amount) where Amount > 0`, `Expense = Sum(Abs(Amount)) where Amount < 0`. No transaction is excluded by category, override status, or any "transfer" flag — there is no transfer concept in the domain model at all.
  - Line 222-238: for every month in the 12-month window, whether or not it had transactions, emits a `TrendPoint(month, income, expense, net)`, defaulting to zero for months with no data — so months with no activity are represented as flat zero bars, not omitted.
- `src/HomeCharts.Application/UseCases/BuildDashboardSnapshotUseCase.cs:31-36` — `anchorDate` (used as `currentMonthStart`, which becomes the `anchorMonth` passed to `BuildTrend` at line 37) is `transactions.Max(t => t.BookingDate)` when transactions exist, else today. This is the "current month" the trend window counts backward from.
- `src/HomeCharts.Application/UseCases/BuildDashboardSnapshotUseCase.cs:13-20` — the use case only ever sees the transactions the repository call at line 20 returned (`GetByDateRangeAsync(fromInclusive, toInclusive, ...)`); `BuildTrend`'s 12-month window is a *sub-window* of whatever range the caller passed in, it does not independently query further back.
- `TrendPoint` record: `src/HomeCharts.Application/UseCases/BuildDashboardSnapshotUseCase.cs:322-326` — `(DateOnly Month, decimal Income, decimal Expenses, decimal Net)`.

### Query — `HomeCharts.Infrastructure`

- `src/HomeCharts.Infrastructure/Persistence/Sqlite/SqliteTransactionRepository.cs:55-79` — `GetByDateRangeAsync(fromInclusive, toInclusive)`. SQL at line 61-67: `WHERE booking_date >= $fromDate AND booking_date <= $toDate`, both bounds inclusive, ordered by `booking_date DESC, created_utc DESC`. **No `is_deleted = 0` filter**, unlike the fingerprint-existence query in the same file (line 143-148, which does filter `WHERE is_deleted = 0`).
- Caller of this query for the dashboard: `src/HomeCharts.Presentation/Mvp/MainWindowViewModel.cs:1433-1437` (`GetDefaultRange()`) — `(today.AddYears(-5), today.AddDays(1))`, i.e. the dashboard always fetches a 5-year window regardless of the 12-month trend it displays, so the trend's 12-month sub-window is never starved by the outer fetch range.
- `src/HomeCharts.Presentation/Mvp/MainWindowViewModel.cs:1140-1143` — `RefreshDashboardAsync()` calls `_buildDashboardSnapshotUseCase.ExecuteAsync(range.From, range.To, trendMonths: 12, uncategorizedLimit: 12)`. `trendMonths: 12` is hard-coded here; there is no UI control to change the trend window.

### View model — `HomeCharts.Presentation`

- `src/HomeCharts.Presentation/Mvp/DashboardModels.cs:10-33` — `DashboardTrendBarViewModel` record: carries `Income`, `Expenses`, `Net` as decimals plus `IncomePercent`/`ExpensesPercent` (doubles, 0-100) used only for bar height, and computed `MonthLabel` (parses the `"yyyy-MM"` string back into a 3-letter month abbreviation — no year shown on the bar itself, only in the header range text).
- `src/HomeCharts.Presentation/Mvp/MainWindowViewModel.cs:1159-1192` — `RefreshDashboardAsync()` trend-bar construction:
  - Line 1172-1173: `maxIncome = snapshot.MonthlyTrend.Max(|Income|)`, `maxExpenses = snapshot.MonthlyTrend.Max(|Expenses|)` — **two independent maxima**, one per series, computed once for the whole 12-month window.
  - Line 1177-1183: each month's `IncomePercent`/`ExpensesPercent` is that month's value as a percentage of its *own series'* max, not of a shared max across both series.
  - Line 1185-1191: builds `DashboardTrendBarViewModel` per month with the raw `Income`, `Expenses`, `Net` decimals plus the two percents.
- `src/HomeCharts.Presentation/Mvp/DashboardModels.cs:29-32` — bar pixel height: `IncomeBarHeight => IncomePercent <= 0 ? 0 : Max(6, IncomePercent * 2.4)`, same formula for `ExpensesBarHeight`. Height cap is implicitly `100 * 2.4 = 240px` (container is 250px tall per the XAML, § Rendering).

### Rendering — `HomeCharts.App` (Avalonia)

- `src/HomeCharts.App/MainWindow.axaml:140-197` — "Cash Flow Trend" card. No charting library is used (no LiveCharts/OxyPlot/etc. reference); the "chart" is a hand-built `ItemsControl` bound to `TrendChartBars` (line 160), laid out with a `UniformGrid Rows="1"` (line 163), one column per month.
- Per-item template (line 167-192): each month is two `Border` rectangles inside a `Grid Height="250"` (line 170) — one for income (line 172-178, class `finance-income-swatch`), one for expenses (line 179-186, class `finance-expense-swatch`) — heights bound to `IncomeBarHeight`/`ExpensesBarHeight` from the view model, widths fixed at 16px (`IncomeBarWidth`/`ExpensesBarWidth`, `DashboardModels.cs:29,32`). Month label below (line 189, `MonthLabel`).
- Legend swatches at line 147-154 reference styles `finance-income-swatch` / `finance-expense-swatch` — colors are defined as Avalonia style classes, not inline in this file; I did not locate the style resource dictionary in this pass (likely `App.axaml` or a `Styles/` file under `HomeCharts.App`, not opened — out of the file set this order's scope named as certain, so flagged rather than guessed).
- Header row (line 142-157): title "Cash Flow Trend" (line 143), `TrendRangeText` (line 145, e.g. "Sep 2025 - Sep 2026"), and the income/expense legend swatches.
- `Net` value is carried on `DashboardTrendBarViewModel` (`NetText`, `DashboardModels.cs:20`) but is **not bound anywhere in `MainWindow.axaml`'s trend card** — only `IncomeTooltip`/`ExpensesTooltip` (hover tooltips on the two bars) are bound; no net line/bar is rendered in the current chart despite the data being computed and exposed.

## Findings

1. **`is_deleted` filter gap (Infrastructure, latent, not currently reachable).** `GetByDateRangeAsync` (`SqliteTransactionRepository.cs:55-79`) omits `WHERE is_deleted = 0`, while the sibling fingerprint-lookup query in the same class (`SqliteTransactionRepository.cs:143-148`) includes it. Today this is inert: no use case in `src/HomeCharts.Application` or `src/HomeCharts.App/CompositionRoot.cs` ever sets `Transaction.IsDeleted = true` — the only delete path is `DeleteAllAsync` (`SqliteTransactionRepository.cs:160-166`), which is a hard `DELETE FROM transactions`. If a soft-delete feature is ever added without updating this query, dashboard totals and the trend would silently include soft-deleted rows.
2. **Anchor month can be future-dated (Application).** `anchorDate` (`BuildDashboardSnapshotUseCase.cs:31-33`) is `transactions.Max(BookingDate)`, not `DateOnly.Today`. A transaction imported with a booking date in the future (bank pre-authorization/scheduled entries, or a data-entry error) would shift the entire 12-month trend window forward, so the chart's rightmost bar would not be the current calendar month and recent real months could fall outside the window.
3. **Income and expense bars are scaled independently (Presentation).** `MainWindowViewModel.cs:1172-1183` computes `maxIncome` and `maxExpenses` as two separate maxima and scales each series to its own 0-100% range. A month with €100 of expenses and a month with €10,000 of income can render bars of similar height, because "tall" means "close to that series' own historical peak," not "large in absolute euros." This is a rendering/scale property, not a data-correctness bug — the underlying `Income`/`Expenses` decimals are correct — but it means the chart cannot be read as "this month's expenses look bigger than income," which is the naive reading of a bar chart labeled "Cash Flow Trend."
4. **No currency handling anywhere in the aggregation (Application/Domain).** `Transaction.Currency` exists on the domain model but `BuildDashboardSnapshotUseCase` and `BuildTrend` sum `Amount` directly with no currency check or conversion (confirmed: no `Currency` reference anywhere in `BuildDashboardSnapshotUseCase.cs`). If the imported data ever contains more than one currency, the trend (and every other KPI) silently mixes them as if they were the same unit. `docs/TECHNICAL_DESIGN.md` and `docs/PROJECT_GUIDE.md` do not state a single-currency assumption explicitly; `BankRecipes/*.txt` sample files were not inspected in this pass to confirm whether multi-currency input is realistic for this user's data.

## Blast radius

- **Finding 1** (is_deleted filter): confined to `HomeCharts.Infrastructure` — one SQL string edit in `SqliteTransactionRepository.GetByDateRangeAsync`. No `Contracts` interface change (the interface signature is unaffected), no use-case shape change.
- **Finding 2** (future-dated anchor): confined to `HomeCharts.Application` — `BuildDashboardSnapshotUseCase.cs:31-33`, a one-line change to anchor on `DateOnly.Today` instead of `transactions.Max(BookingDate)` (or a documented decision that anchoring on the latest transaction is intentional). No cross-layer contract change.
- **Finding 3** (independent bar scaling): confined to `HomeCharts.Presentation` — `MainWindowViewModel.cs:1172-1183` and `DashboardModels.cs:29-32`; a shared-max redesign is a view-model + XAML change only, no `Application`/`Domain` change needed since `TrendPoint` already carries the raw `Income`/`Expenses`/`Net` decimals.
- **Finding 4** (currency): if this needs fixing, it is **not** confined to one layer — it would require either (a) a documented single-currency invariant enforced at import time (`HomeCharts.Application` import use case, `HomeCharts.Domain` validation), which is a use-case-shape question worth a design pass, or (b) actual multi-currency aggregation, which would need a new `Contracts`-level concept (exchange rate, display currency) and is squarely a `tech-lead` DESIGN-phase question, not a same-layer fix. Flagging this as the one finding here that could trigger the design phase per `project.md` § Delivery model ("a change that crosses more than one layer's contract").
- A chart-library swap (e.g. adopting a real charting control instead of the hand-built `ItemsControl`/`Border` bars) is confined to `HomeCharts.App`/`HomeCharts.Presentation` (frontend lane) and does not touch `Contracts` — `TrendPoint`/`DashboardTrendBarViewModel` already carry everything a real chart control would need (month, income, expenses, net).

## Sources of truth

- `docs/TECHNICAL_DESIGN.md:42-44,85-94` — the only doc description of `BuildDashboardSnapshotUseCase` and the trend panel. It is accurate as far as it goes ("Trend panel shows side-by-side monthly income/expense bars") but does not mention the anchor-month logic, the independent-scaling behavior, or any currency assumption — thin, not stale, consistent with `project.md`'s note that this profile/doc set is new and has not yet accumulated incident-driven detail.
- `docs/PROJECT_GUIDE.md` — grepped for "Trend"/"Cash Flow"/"CashFlow" and returned no matches; it does not describe the trend chart at all (user-facing flow doc is silent on this specific panel).
- No test file was found in the initial grep sweep of `src/**` for "Trend"/"CashFlow" outside the four files mapped above; `tests/HomeCharts.Application.Tests/` was not opened — flagged in `risks`, not asserted as a gap.
