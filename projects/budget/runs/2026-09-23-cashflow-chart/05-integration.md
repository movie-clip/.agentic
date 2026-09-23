REPORT 2026-09-23-cashflow-chart/05
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   dotnet build HomeCharts.sln && dotnet build src/HomeCharts.App/HomeCharts.App.csproj && dotnet test HomeCharts.sln --no-build
  result:    PASS
  detail:    Both builds succeeded, 0 Warning(s)/0 Error(s) each. Tests: HomeCharts.Domain.Tests 5/5 passed, HomeCharts.Application.Tests 37/37 passed, HomeCharts.Infrastructure.Tests 11/11 passed. 53/53 total, 0 failed, 0 skipped.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

risks:
  - the new `is_deleted = 0` filter on `GetByDateRangeAsync` also changes what `GetLedgerEntriesUseCase`, `ApplyCategorizationRulesUseCase`, and the export path in `BackupAndTransferUseCases.cs` see, not just the dashboard — currently inert per 01-recon.md (no write path sets `IsDeleted = true`), and correct, but the blast radius is wider than "trend chart"
  - `MainWindowViewModelTrendBarScalingTests` wires all 22 `MainWindowViewModel` constructor dependencies to reach `LoadInitialStateAsync` — 04-test.md already flagged this coupling; a real liability but not a guardrail violation, does not block this PASS
