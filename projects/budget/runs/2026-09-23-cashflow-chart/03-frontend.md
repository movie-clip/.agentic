REPORT 2026-09-23-cashflow-chart/03
status:      DONE
verdict:     NONE

changed:
  - src/HomeCharts.Presentation/Mvp/MainWindowViewModel.cs — `RefreshDashboardAsync` now computes one `sharedMax` across both `Income` and `Expenses` for the whole 12-month window, replacing two independent `maxIncome`/`maxExpenses` maxima (finding 3 fix)
  - src/HomeCharts.Presentation/Mvp/MainWindowViewModel.cs — `IncomePercent`/`ExpensesPercent` are now both scaled against that single `sharedMax`, so bar heights are comparable across series, not just within one series
  - src/HomeCharts.Presentation/Mvp/DashboardModels.cs — added `NetIsPositive`, `NetSignedText`, `NetTooltip` to `DashboardTrendBarViewModel` to back the new per-month net indicator in the redesigned chart
  - src/HomeCharts.Presentation/Mvp/DashboardModels.cs — `IncomeBarWidth`/`ExpensesBarWidth` widened from 16d to 18d as part of the visual redesign
  - src/HomeCharts.App/App.axaml — `Border.finance-income-swatch` restyled from a flat fill to a vertical green `LinearGradientBrush`
  - src/HomeCharts.App/App.axaml — `Border.finance-expense-swatch` restyled from a flat fill to a vertical red `LinearGradientBrush`
  - src/HomeCharts.App/App.axaml — `finance-accent-swatch` and every `TextBlock.finance-*` class left unchanged, since those are shared with other dashboard cards
  - src/HomeCharts.App/MainWindow.axaml — Cash Flow Trend header gets a subtitle line, a pill-styled range text, and a third "Net" legend swatch (reusing existing `finance-accent-swatch`)
  - src/HomeCharts.App/MainWindow.axaml — each month cell now has a hover highlight via `Border#TrendCell:pointerover`, matching the existing `Border#ExpenseHeader`/`Border#ExpenseTxRow` pattern used elsewhere in this file
  - src/HomeCharts.App/MainWindow.axaml — a signed net value is now rendered between the bars and the month label, green (`finance-income`) when `NetIsPositive`, red (`finance-expense`) otherwise, toggled via `IsVisible` — see § Net design decision

verification:
  command:   dotnet build HomeCharts.sln && dotnet build src/HomeCharts.App/HomeCharts.App.csproj
  result:    PASS
  detail:    Both builds succeeded, 0 Warning(s), 0 Error(s) each (solution build and the App-project XAML-specific build both ran and passed independently)

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - test lane: no existing test asserts the trend chart's bar-scaling behavior — see § Test coverage gap
  - see § Net design decision for why net is a signed inline value, not a line/marker overlay
  - see § Theme note for why "light and dark" reduces to "dark only" in this app today

risks:
  - `finance-income-swatch`/`finance-expense-swatch` (the two classes restyled with gradients) are used only inside the Cash Flow Trend card per a repo-wide grep — no risk of regressing the KPI cards or the expenses-by-category panel
  - every `TextBlock.finance-*` class (used broadly across other dashboard cards) was left at its original flat color specifically to avoid any risk of regressing those cards
  - the order asked the redesign to read well "in both light and dark theme if it has one" — see § Theme note; I did not invent light-theme-specific styling since there is no code path that would ever exercise it

## Orchestrator brief
Finding 3 (independent bar scaling) fixed in `MainWindowViewModel.cs`; chart redesigned in `MainWindow.axaml`/`App.axaml` with a new per-month signed net indicator. Both required builds pass. Sections below: **Test coverage gap** (what the test lane should add), **Net design decision** (what was chosen and why), **Theme note** (app is dark-only, confirmed via grep).

## Test coverage gap
No existing test asserts the trend chart's bar-scaling behavior. Worth covering: `IncomePercent`/`ExpensesPercent` in `MainWindowViewModel.RefreshDashboardAsync` (around line 1172) are now derived from one shared maximum across both series — e.g. a month with Income=100, Expenses=1000 should yield `ExpensesPercent=100` and `IncomePercent=10`, not two independent 100s. `01-recon.md` already noted no test file covers `BuildTrend`'s consumers.

## Net design decision
Chose a compact signed value (`+123.45` / `-45.00`) rendered between the two bars and the month label, colored green/red via the existing `finance-income`/`finance-expense` TextBlock classes and toggled with `IsVisible` — not a line/marker overlay. A Polyline-based net line was considered and rejected: it would need pixel-position geometry derived from the same shared scale, which is more surface area and risk for a styling-only pass than this order's scope justifies. The KPI-level "Net" summary card above the chart (`MainWindow.axaml`, around line 102) already existed and is unchanged.

## Theme note
`App.axaml` line 4 hardcodes `RequestedThemeVariant="Dark"`. A repo-wide grep for `ThemeVariant`/`RequestedTheme`/`ActualThemeVariant` under `src/` returns only that one line — there is no light-theme code path anywhere in this app. So "reads well in light and dark theme if it has one" reduces to "reads well in the one theme that exists." Flagged rather than silently assumed, and rather than building unreachable light-theme styling.
