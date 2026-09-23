REPORT 2026-09-23-cashflow-chart/06
status:      DONE
verdict:     NONE

changed:
  - docs/TECHNICAL_DESIGN.md — `BuildDashboardSnapshotUseCase` bullet now states the trend window anchors at `Min(DateOnly.Today, Max(BookingDate))`, capping a future-booked transaction from pulling the window forward
  - docs/TECHNICAL_DESIGN.md — `transactions` data-model bullet now notes the `is_deleted` soft-delete flag and that dashboard date-range reads filter it out
  - docs/TECHNICAL_DESIGN.md — § 6 UI Design Notes trend-panel line now describes shared-max bar scaling across both series and the per-month signed net indicator, replacing the one-line "side-by-side bars" description
  - docs/RELEASE_NOTES.md — appended a new `## 2026-09-23` entry (Data Accuracy: is_deleted filter + capped trend anchor; Product/UX: shared-max bar scaling + chart redesign; Validation: the three commands and 53-passing count from 05-integration.md)
  - C:\projects\investments\.agentic\projects\budget\capabilities\testing.md — added a note to § "Where things live" that `HomeCharts.Application.Tests.csproj` already references `HomeCharts.Presentation.csproj`, so Presentation view-model behavior (e.g. `MainWindowViewModel`) is coverable from `Application.Tests` without a separate `Presentation.Tests` project (pack correction from 04-test.md § risks)

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    docs-only order, no verification command named; no Bash tool available to this lane

contract_notes:
  - none

pack_corrections:
  - capabilities/testing.md — false/incomplete premise: the pack's "Where things live" section did not mention that `HomeCharts.Application.Tests` already references `HomeCharts.Presentation`. Applied exact fact from 04-test.md § risks: "`HomeCharts.Application.Tests.csproj` already project-references `HomeCharts.Presentation.csproj`. That means `Presentation` view-model behavior (e.g. `MainWindowViewModel`) is already coverable from `Application.Tests` — by wiring its constructor dependencies to in-memory fakes and driving it through its public methods — without a separate `HomeCharts.Presentation.Tests` project."

handoff:
  - none

risks:
  - `docs/PROJECT_GUIDE.md` left untouched by design: 01-recon.md confirmed it does not mention "Trend"/"Cash Flow" anywhere, and per this order's scope it should only be touched if it already described the trend panel to users — it does not, so adding new user-facing documentation here would be a side effect this order was told not to introduce
  - did not document finding 4 (currency handling) anywhere — it was explicitly dismissed this run as unreachable given the current single-currency import format, and non_goals forbade inventing that caveat
  - the `is_deleted` filter's wider blast radius (also affects `GetLedgerEntriesUseCase`, `ApplyCategorizationRulesUseCase`, and the export path per 05-integration.md § risks) was not called out as a separate doc note beyond the one `transactions` data-model bullet — judged in-scope-enough to leave as a single shared fact rather than repeating it per use case, since `docs.md`'s "one fact, one section" framing argues against duplicating it across § 3 use-case bullets
