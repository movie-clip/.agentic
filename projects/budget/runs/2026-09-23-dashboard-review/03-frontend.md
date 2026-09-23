REPORT 2026-09-23-dashboard-review/03
status:      DONE
verdict:     NONE

changed:
  - src/HomeCharts.Presentation/Mvp/MainWindowViewModel.cs — Slice 1: deleted DashboardSummary, TotalTransactionsText, AttentionSummaryText, IncomeBarPercent, ExpensesBarPercent properties/fields and their population code.
  - src/HomeCharts.Presentation/Mvp/MainWindowViewModel.cs — Slice 1: deleted TrendRows/CategoryRows collections and their population inside RefreshDashboardAsync, kept TrendChartBars/ExpenseCategoryBars which remain bound.
  - src/HomeCharts.Presentation/Mvp/MainWindowViewModel.cs — Slice 1: two Merge-flow Status messages that actually read TotalTransactionsText now read a private int field (_totalTransactionsCount) instead — see risks.
  - src/HomeCharts.Presentation/Mvp/MainWindowViewModel.cs — Slice 2: added ReviewUncategorizedCommand/ReviewUncategorizedAsync — sets OnlyUncategorized=true, refreshes the ledger, and switches to the Ledger tab.
  - src/HomeCharts.Presentation/Mvp/MainWindowViewModel.cs — Slice 3: MonthDeltaSummaryText now formats snapshot.CurrentVsPreviousMonth's IncomeDelta/ExpensesDelta/NetDelta via new FormatMonthDeltaSummary/FormatSignedAmount formatting-only helpers.
  - src/HomeCharts.Presentation/Mvp/DashboardModels.cs — Slice 1: deleted DashboardTrendRowViewModel and DashboardCategoryRowViewModel record types.
  - src/HomeCharts.App/MainWindow.axaml — Slice 3: added a "this month vs last month" strip bound to CurrentMonthLabelText/CurrentMonthIncomeText/CurrentMonthExpensesText/CurrentMonthNetText/MonthDeltaSummaryText, between the KPI row and the trend/category grid.
  - src/HomeCharts.App/MainWindow.axaml — Slice 2: added a "Needs Attention" panel above the existing Expenses-breakdown card, bound to UncategorizedRows/UncategorizedCountText/CategorizedCoverageText/UncategorizedAmountText, with a "Review in Ledger" button bound to ReviewUncategorizedCommand.

verification:
  command:   dotnet build HomeCharts.sln && dotnet build src/HomeCharts.App/HomeCharts.App.csproj && dotnet test HomeCharts.sln --no-build
  result:    PASS
  detail:    Both builds: Build succeeded, 0 Warning(s), 0 Error(s). Tests: Domain.Tests 5/5, Application.Tests 34/34, Infrastructure.Tests 10/10 passed, 0 failed.

contract_notes:
  - docs/PROJECT_GUIDE.md:43's KPI-card description (per D-2's ruling) should now also mention the new "Needs Attention" panel and "vs last month" strip as shipped Dashboard surfaces, not only the 4 KPI cards.
  - docs/TECHNICAL_DESIGN.md:42-43's DashboardSnapshot description should note MonthComparison and UncategorizedQueue are now consumed by the UI (Slices 2-3), not merely computed.

pack_corrections:
  - none

handoff:
  - No HomeCharts.Presentation.Tests project exists (per non_goals, none added); name for the test lane if one is created: FormatMonthDeltaSummary/FormatSignedAmount and ReviewUncategorizedAsync.
  - docs lane: apply D-2's ruling to docs/PROJECT_GUIDE.md:43 now that the needs-attention panel and month-comparison strip are shipped (see contract_notes).
  - docs lane: update docs/TECHNICAL_DESIGN.md:42-43 per recon's Doc drift finding now that MonthComparison/UncategorizedQueue are UI-consumed (see contract_notes).

risks:
  - Recon's "TotalTransactionsText never displayed" claim missed 2 C# call sites reading it in Status messages; deleting it verbatim would break the build, so I kept its value as a private int field instead and pointed those 2 call sites at it.
  - Recon's grep only checked XAML bindings and test references, not interpolated C# string usage, which is why it missed TotalTransactionsText's 2 real consumers in MergeMatchedTransactionsAsync's Status messages.
  - The order phrases Slice 2's action as only "sets OnlyUncategorized = true and switches to the Ledger tab"; I judged that reusing the filter mechanism means reusing it working, so I also call RefreshLedgerAsync.
  - Without RefreshLedgerAsync, the new button would flip the OnlyUncategorized flag and switch tabs but leave the grid showing its previous unfiltered page until the user also clicked "Apply Filters" themselves.
  - I placed the needs-attention panel above the Expenses-breakdown card in the right column rather than as a new page-width row, to avoid exceeding the window's MinHeight=760 given the trend chart's fixed Height=250 — my own layout call, not the brief's.
