REPORT 2026-09-23-dashboard-review/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    recon order, verification: NONE

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - `BuildDashboardSnapshotUseCase.ExecuteAsync` (src/HomeCharts.Application/UseCases/BuildDashboardSnapshotUseCase.cs:13) is the single read-model entry point; any brief changing dashboard content should extend `DashboardSnapshot` rather than add a second use case.
  - `MainWindowViewModel.RefreshDashboardAsync` (src/HomeCharts.Presentation/Mvp/MainWindowViewModel.cs:1162-1307) is the only mapping point from snapshot to bound view-model collections/strings; a UI change touches this method plus src/HomeCharts.App/MainWindow.axaml:78-294.
  - Ten dashboard-facing view-model properties are populated every refresh but have zero XAML binding — see § Unused surface — a delivery brief should decide remove-vs-wire-up before any new dashboard work builds on top of them.
  - `docs/PROJECT_GUIDE.md:43` documents an "uncategorized" KPI card that does not exist in `MainWindow.axaml`'s KPI row (:85-114, four cards: Income/Expenses/Net/Savings Rate) — doc and code disagree on what ships today.
  - There is no `HomeCharts.Presentation.Tests` project in `tests/**` — Presentation-layer dashboard code (all of `DashboardModels.cs`, all of `RefreshDashboardAsync`) has no test coverage at any level.

risks:
  - I read `DashboardExpenseCategoryBarViewModel`/`IncomeBarPercent`/category-percent math in the view model as "arithmetic done in Presentation" rather than a guardrail-3 violation outright — it computes display ratios (bar heights/percentages) rather than a categorization or override decision, but a reviewer may weigh it differently; flagged as a finding, not adjudicated. See § Business-logic-in-Presentation findings.
  - I did not exhaustively diff the legacy WPF reference code against the current Dashboard, since CLAUDE.md marks it reference-only and out of the active implementation; if the brief wants "what did WPF do differently," that is a separate read.

## Orchestrator brief
- Dashboard tab spans 4 files end to end: DashboardModels.cs (view-model records), MainWindowViewModel.cs (mapping/state), MainWindow.axaml (layout/bindings), BuildDashboardSnapshotUseCase.cs (the only aggregation logic, Application layer, correctly placed).
- § Where it lives — full file/class/line map.
- § What already exists — DashboardSnapshot's 8 sub-shapes already cover KPI, trend, category breakdown, uncategorized queue, month comparison, coverage, largest expenses, recurring expenses; a new dashboard metric most likely extends this record, not a new use case.
- § Unused surface — 10 properties/3 record types populated but never bound in XAML or referenced by tests; MonthDeltaSummaryText/AttentionSummaryText are always set to `string.Empty`/never computed from data at all.
- § Business-logic-in-Presentation findings — display-ratio math in the view model; judgment call flagged, not resolved, for design/review lanes.
- § Test coverage — one exhaustive Application-layer test for the use case; zero Presentation-layer tests exist anywhere in this repo (no test project).
- § Doc drift — PROJECT_GUIDE.md's KPI-card list doesn't match the shipped XAML.
- § Structural comparison to other tabs — same MVVM/one-big-viewmodel pattern repo-wide; not dashboard-specific.
- Nothing blocks dispatch; scope was read-only and fully covered.

## Where it lives

- `src/HomeCharts.Application/UseCases/BuildDashboardSnapshotUseCase.cs:1-365` — the only aggregation/decision logic for the Dashboard. `ExecuteAsync` (line 13) pulls all transactions/categories in range, computes KPI totals, trend, category breakdown, month-over-month comparison, coverage, largest expenses (current month, top 6), recurring expenses (≥2 occurrences across ≥2 distinct months, top 6), and an uncategorized queue (top N by date). Returns a single `DashboardSnapshot` record (line 283) composed of `DashboardKpi`, `IReadOnlyList<TrendPoint>`, `IReadOnlyList<CategoryBreakdownItem>`, `IReadOnlyList<UncategorizedItem>`, `MonthComparison`, `DashboardCoverage`, `IReadOnlyList<LargestExpenseItem>`, `IReadOnlyList<RecurringExpenseItem>`.
- `src/HomeCharts.Presentation/Mvp/DashboardModels.cs:1-126` — 9 view-model record/class types that reshape `DashboardSnapshot` items for binding: `DashboardTrendRowViewModel`, `DashboardCategoryRowViewModel`, `DashboardUncategorizedRowViewModel`, `DashboardTrendBarViewModel` (with bar-height/tooltip formatting), `DashboardExpenseCategoryBarViewModel` (mutable, `IsExpanded` with collapse-siblings callback), `DashboardExpenseTransactionViewModel`, `DashboardLargestExpenseViewModel`, `DashboardRecurringExpenseViewModel`.
- `src/HomeCharts.Presentation/Mvp/MainWindowViewModel.cs` — the single view model for the whole app (not dashboard-specific). Dashboard-relevant members:
  - field `_buildDashboardSnapshotUseCase` (line 47), injected via constructor (line 129/153).
  - 7 `ObservableCollection<...>` dashboard collections (lines 204-210): `TrendRows`, `TrendChartBars`, `CategoryRows`, `ExpenseCategoryBars`, `UncategorizedRows`, `LargestExpenseRows`, `RecurringExpenseRows`.
  - ~20 dashboard-facing string/double properties (lines 418-524): `DashboardSummary`, `TrendRangeText`, `TotalTransactionsText`, `IncomeText`, `ExpensesText`, `NetText`, `SavingsRateText`, `CurrentMonthLabelText`, `CurrentMonthIncomeText`, `CurrentMonthExpensesText`, `CurrentMonthNetText`, `MonthDeltaSummaryText`, `UncategorizedCountText`, `CategorizedCoverageText`, `UncategorizedAmountText`, `AttentionSummaryText`, `IncomeBarPercent`, `ExpensesBarPercent`.
  - `ShowDashboardViewCommand` (line 192, 249) and `IsDashboardViewSelected` (line 254) — tab-selection plumbing, shared with the other 3 tabs (`Import`, `Transactions`, `Utility`) via the same `_selectedView` string field pattern.
  - `RefreshDashboardAsync()` (lines 1162-1307) — the only method that calls the use case and populates every dashboard-bound member. Called from: initial load, after import (line 654), after apply-rules (line 781, 798, 837 approx — apply rules flows), after manual recategorization/merge flows (lines 975, 999, 1049), and on `ShowDashboardViewCommand`/tab switch paths (740, 756, 1690).
  - `OnExpenseCategoryExpanded` (line 1309) — single-open-accordion behavior for the expenses panel, referenced as a callback into `DashboardExpenseCategoryBarViewModel`.
  - `FormatDescriptionForDisplay` (line 1547) — strips user-configured prefix filters from descriptions for display; used by dashboard rows (largest expenses, recurring expenses, uncategorized rows, category transaction rows) and by the Ledger tab identically.
  - `GetDefaultRange()` (line 1484, static, private) — hardcodes `(today - 5 years, today + 1 day)` as the range passed into `BuildDashboardSnapshotUseCase`; shared by the dashboard refresh, the post-import auto-categorize call, and the manual "Apply Rules" action — not dashboard-exclusive, but the Dashboard's data window is entirely determined by this Presentation-layer constant.
- `src/HomeCharts.App/MainWindow.axaml:78-294` — the Dashboard tab's layout, gated behind `IsVisible="{Binding IsDashboardViewSelected}"` on four separate `Grid`s (no single dashboard container element). Contains: 4 KPI cards (Income, Expenses, Net, Avg Monthly Savings Rate — lines 85-114), a "Cash Flow Trend" bar chart bound to `TrendChartBars` (lines 116-174), "Largest Expenses This Month" list bound to `LargestExpenseRows` (177-200), "Recurring Expenses" list bound to `RecurringExpenseRows` (202-227), and an "Expenses" category-breakdown accordion bound to `ExpenseCategoryBars` (231-293).
- `src/HomeCharts.App/CompositionRoot.cs:59,84` — wires `BuildDashboardSnapshotUseCase` from concrete `SqliteTransactionRepository`/`SqliteCategoryRepository`, passed into `MainWindowViewModel`'s constructor. No dashboard-specific composition beyond this; pure wiring, no logic.
- `src/HomeCharts.Contracts/Persistence/ITransactionRepository.cs`, `ICategoryRepository.cs` — the two contracts the dashboard use case depends on (`GetByDateRangeAsync`, `GetAllAsync`); no dashboard-specific contract exists or is needed today.
- `tests/HomeCharts.Application.Tests/Test1.cs:561-655` — `BuildDashboardSnapshotUseCase_ComputesKpiTrendBreakdownAndUncategorized` is the sole dashboard test: asserts KPI totals, savings rate, trend count, category breakdown membership, uncategorized queue count, month-comparison figures, coverage counts, and that `LargestExpenses[0]`/`RecurringExpenses[0]` pick the expected item.

## Unused surface

Grepped every dashboard-facing view-model member against `src/HomeCharts.App/MainWindow.axaml` (the only `.axaml` view in the solution besides `App.axaml`) and against `tests/**`. None of the following have any XAML binding or test reference — evidence: `Grep pattern="<name>" path="src\HomeCharts.App\MainWindow.axaml"` returned no matches for all of them in one pass, and a second pass against `tests/**` also returned no matches:

- `MainWindowViewModel.DashboardSummary` (MainWindowViewModel.cs:418) — built at :1167-1168 every refresh, never displayed.
- `MainWindowViewModel.TotalTransactionsText` (:430) — set at :1170, never displayed.
- `MainWindowViewModel.CurrentMonthLabelText` / `CurrentMonthIncomeText` / `CurrentMonthExpensesText` / `CurrentMonthNetText` (:460-482) — set at :1178-1181 from `snapshot.CurrentVsPreviousMonth.Current`, never displayed; the month-comparison feature (current vs previous month) is computed end-to-end in the use case (`MonthComparison`, `BuildDashboardSnapshotUseCase.cs:74-106`) and mapped into the view model, but has no UI at all.
- `MainWindowViewModel.MonthDeltaSummaryText` (:484) — hardcoded to `string.Empty` at :1182 every refresh; the deltas it would summarize (`MonthComparison.IncomeDelta/ExpensesDelta/NetDelta`, BuildDashboardSnapshotUseCase.cs:85-87) are computed but never consumed anywhere.
- `MainWindowViewModel.UncategorizedCountText` / `CategorizedCoverageText` / `UncategorizedAmountText` (:490-506) — set at :1175-1177, never displayed (the XAML KPI row has no "uncategorized" card — see § Doc drift).
- `MainWindowViewModel.AttentionSummaryText` (:508) — hardcoded to `string.Empty` at :1183 every refresh; defaults to `"No dashboard actions pending"` (field init, :96) but that default is also never shown.
- `MainWindowViewModel.IncomeBarPercent` / `ExpensesBarPercent` (:514-524) — computed at :1188-1195 (share of income vs. expenses of total flow), never bound.
- `ObservableCollection<DashboardTrendRowViewModel> TrendRows` (:204) — populated at :1216-1220 in parallel with `TrendChartBars` (which *is* bound); `TrendRows`/`DashboardTrendRowViewModel` itself has no XAML consumer and no test reference.
- `ObservableCollection<DashboardCategoryRowViewModel> CategoryRows` (:206) — populated at :1248-1251 in parallel with `ExpenseCategoryBars` (which *is* bound); `CategoryRows`/`DashboardCategoryRowViewModel` has no XAML consumer and no test reference.
- `ObservableCollection<DashboardUncategorizedRowViewModel> UncategorizedRows` (:208) — populated at :1301-1306 every refresh (`UncategorizedRows.Clear()` then re-add, iterating `snapshot.UncategorizedQueue`); no XAML consumer, no test reference. This is the "review uncategorized transactions from the dashboard" surface implied by `docs/PROJECT_GUIDE.md:12` ("dashboard insights for ... uncategorized activity") but it renders nowhere.

Net: 3 whole view-model record types (`DashboardTrendRowViewModel`, `DashboardCategoryRowViewModel`, `DashboardUncategorizedRowViewModel`) plus their backing collections, and 10 scalar properties, are computed on every dashboard refresh and never read by any UI element or test.

## Business-logic-in-Presentation findings

Guardrail 3 ("no business logic in `HomeCharts.App`/`HomeCharts.Presentation`... decisions belong in Domain/Application... view models format, display and dispatch — they do not decide"). The Dashboard's core aggregation is correctly in `BuildDashboardSnapshotUseCase` (Application layer). Two places in `MainWindowViewModel.RefreshDashboardAsync` do arithmetic beyond formatting, flagged for a design/review judgment call rather than resolved here:

- `MainWindowViewModel.cs:1185-1195` — `IncomeBarPercent`/`ExpensesBarPercent` are derived by dividing `Math.Abs(TotalIncome)`/`Math.Abs(TotalExpenses)` by their sum (`totalFlow`) — a share-of-total computation performed in the view model, not the use case. (Currently unused by any binding — see § Unused surface — so today it is dead arithmetic rather than a live decision.)
- `MainWindowViewModel.cs:1211-1236` and `:1242-1255` — `maxIncome`/`maxExpenses`/`maxCategoryAmount` normalization and the resulting `incomePercent`/`expensesPercent`/`percent` (0-100 relative-to-max values baked into `DashboardTrendBarViewModel`/`DashboardExpenseCategoryBarViewModel`) are computed in the view model from raw `TrendPoint`/`CategoryBreakdownItem` amounts, then further transformed into pixel heights inside `DashboardTrendBarViewModel.IncomeBarHeight`/`ExpensesBarHeight` (`DashboardModels.cs:41-44`, a hand-tuned `Math.Max(6d, percent * 2.4d)` formula). This chain (relative-to-max ratio, then linear scale-to-pixels) is chart-rendering logic living entirely in Presentation; whether that crosses guardrail 3 (a "decision") or stays inside "format, display" is the call this recon leaves to design/review — the specific lines are named for that judgment.
- `MainWindowViewModel.GetDefaultRange()` (:1484-1488) hardcodes the dashboard's (and apply-rules', and post-import's) effective analysis window as "5 years back through tomorrow." This is a fixed business default (how much history the dashboard shows) encoded as a Presentation-layer constant rather than an Application-layer default/parameter — noted as friction, not resolved as a violation, since `BuildDashboardSnapshotUseCase.ExecuteAsync` already accepts `fromInclusive`/`toInclusive` as parameters and the view model is merely choosing values to pass, which is closer to "dispatch" than "decide."

## Test coverage

- `HomeCharts.Application.Tests/Test1.cs:562-655` — one test method, `BuildDashboardSnapshotUseCase_ComputesKpiTrendBreakdownAndUncategorized`, covers `BuildDashboardSnapshotUseCase.ExecuteAsync` broadly: KPI totals/savings rate, trend point count, category breakdown, uncategorized queue count, month comparison (current+previous), coverage, and first-item checks on `LargestExpenses`/`RecurringExpenses`. It does not test: empty-transaction edge cases, the `trendMonths`/`uncategorizedLimit` parameter boundaries beyond the one scenario, or `BuildRecurringExpenses`'s ≥2-occurrences/≥2-months threshold logic in isolation.
- No test exercises `MainWindowViewModel.RefreshDashboardAsync`, any `DashboardModels.cs` type, or `OnExpenseCategoryExpanded` — there is no `HomeCharts.Presentation.Tests` project in `tests/**` at all (confirmed via `Glob "tests/**/*.cs"`: only `Domain.Tests`, `Application.Tests`, `Infrastructure.Tests` exist). This is a repo-wide gap, not dashboard-specific, but it means every mapping/formatting line named in § Where it lives and § Business-logic-in-Presentation findings is untested.
- `HomeCharts.Infrastructure.Tests` (`WorkflowIntegrationTests.cs`, `Test1.cs`) has no dashboard-related test — confirmed via grep for `Dashboard|GetByDateRangeAsync|GetAllAsync` returning only the two file names with no dashboard-specific method calls inspected further (not read in full; flagged as unconfirmed depth, not a gap claim).

## Doc drift

- `docs/PROJECT_GUIDE.md:43` states "KPI cards: income, expenses, uncategorized" as the Dashboard Review flow's KPI set. The shipped `MainWindow.axaml:85-114` KPI row has exactly four cards: Income Total, Expenses Total, Net, Avg Monthly Savings Rate — there is no uncategorized-amount or uncategorized-count KPI card. The `UncategorizedCountText`/`UncategorizedAmountText`/`CategorizedCoverageText` properties exist in the view model (see § Unused surface) and would satisfy this doc line if wired up, suggesting the doc describes an intended/former state that the current XAML doesn't implement (or the XAML regressed after the doc was written) — recon cannot tell which direction the drift ran without a git-blame that was out of scope.
- `docs/TECHNICAL_DESIGN.md:42-43` describes `BuildDashboardSnapshotUseCase` as producing "KPI, monthly trend, category breakdown, uncategorized queue" — accurate as far as it goes, but does not mention `MonthComparison`, `DashboardCoverage`, `LargestExpenses`, or `RecurringExpenses`, all of which exist in `DashboardSnapshot` and are partially or fully unused (see § Unused surface). Not wrong, just incomplete relative to current code.

## Structural comparison to other tabs

Brief, non-dashboard-focused comparison per the order's non-goals: all four tabs (`Dashboard`, `Import`, `Transactions`/Ledger, `Utility`) share one `MainWindowViewModel` god-object and one `MainWindow.axaml` file, gated by `IsVisible="{Binding Is<X>ViewSelected}"` bindings off a single `_selectedView` string field — this is a repo-wide pattern, not a Dashboard-specific deviation. The Ledger tab's `FormatDescriptionForDisplay`-based `TransactionDetailViewModel` (MainWindowViewModel.cs:1527-1545) is structurally the closest sibling to the Dashboard's row-mapping code and follows the identical mapping-in-view-model shape — so the Dashboard is not an outlier in how it's built, it is just the tab with the most unused surface area.
