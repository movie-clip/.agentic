REPORT 2026-09-23-cashflow-chart/02
status:      DONE
verdict:     NONE

changed:
  - src/HomeCharts.Infrastructure/Persistence/Sqlite/SqliteTransactionRepository.cs — `GetByDateRangeAsync` SQL now filters `AND is_deleted = 0`, matching the sibling fingerprint-existence query in the same file (finding 1)
  - src/HomeCharts.Application/UseCases/BuildDashboardSnapshotUseCase.cs — trend anchor date is now `Min(today, Max(BookingDate among transactions))` instead of an unbounded `Max(BookingDate)`, capping a future-booked transaction from pulling the 12-month trend window forward (finding 2)

verification:
  command:   dotnet build HomeCharts.sln
  result:    PASS
  detail:    Build succeeded. 0 Warning(s), 0 Error(s)

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - no existing test asserts `GetByDateRangeAsync` excludes a row with `is_deleted = 1` from its returned range (01-recon.md § risks flagged the test-coverage gap generally) — test lane should add one
  - no existing test asserts `BuildDashboardSnapshotUseCase` anchors the trend window at today when a transaction has a `BookingDate` after `DateOnly.Today`, while still anchoring at `Max(BookingDate)` for the normal historical case — test lane should add coverage for both branches

risks:
  - none
