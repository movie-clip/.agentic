REPORT 2026-09-23-cashflow-chart/04
status:      DONE
verdict:     NONE

changed:
  - tests/HomeCharts.Infrastructure.Tests/SqliteTransactionRepositoryTests.cs — new test asserting `SqliteTransactionRepository.GetByDateRangeAsync` excludes an `IsDeleted = true` row in range while still returning a sibling `IsDeleted = false` row in the same range (finding 1 coverage)
  - tests/HomeCharts.Application.Tests/BuildDashboardSnapshotUseCaseTrendAnchorTests.cs — two new tests: historical-only transactions anchor the trend window at `Max(BookingDate)`; a future-booked transaction caps the anchor at today, asserted via the last emitted `TrendPoint.Month` and that no point exceeds today's month (finding 2 coverage)
  - tests/HomeCharts.Application.Tests/MainWindowViewModelTrendBarScalingTests.cs — new test asserting `MainWindowViewModel`'s `IncomePercent`/`ExpensesPercent` for a month are computed against one shared maximum across both series (Income=100/Expenses=1000 yields ExpensesPercent≈100, IncomePercent≈10, not both ≈100) (finding 3 coverage)
  - tests/HomeCharts.Application.Tests/TestDoubles.cs — new shared file of in-memory repository/service fakes extracted for reuse across `Application.Tests`, since no shared scaffolding module existed before this run — see handoff

verification:
  command:   dotnet build HomeCharts.sln && dotnet test HomeCharts.sln --no-build
  result:    PASS
  detail:    Build succeeded, 0 Warning(s)/0 Error(s). Tests: Domain.Tests 5/5 passed, Application.Tests 37/37 passed (34 pre-existing + 3 new), Infrastructure.Tests 11/11 passed (10 pre-existing + 1 new). All passed, none skipped.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - `tests/HomeCharts.Application.Tests/TestDoubles.cs` is now the shared in-memory fake module for this project — extend it rather than re-declaring a private nested fake
  - `Phase5OperationsTests.cs` still has its own private nested fakes of the same shapes; left untouched, out of this order's named behaviors — a future cleanup pass could point it at `TestDoubles.cs`
  - `HomeCharts.Application.Tests.csproj` already project-references `HomeCharts.Presentation.csproj`, so `MainWindowViewModel` can be built with in-memory-backed use cases and driven via its public `LoadInitialStateAsync()` — this is how Presentation-layer behavior got covered without a new test project

risks:
  - `MainWindowViewModelTrendBarScalingTests` wires all 22 `MainWindowViewModel` constructor dependencies to in-memory fakes to reach `LoadInitialStateAsync` → `RefreshDashboardAsync`; heavier than a typical unit test and coupled to that constructor's parameter list, so an unrelated signature change breaks it too
  - accepted the coupling above given non_goals steered toward "a method/helper reachable from Application.Tests" over creating a new test project
  - the pack's "Where things live" section did not mention `Application.Tests` already references `HomeCharts.Presentation` — worth adding, since that reference is why Presentation view-model behavior is coverable without a `Presentation.Tests` project
