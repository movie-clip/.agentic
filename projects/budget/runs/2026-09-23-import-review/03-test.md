REPORT 2026-09-23-import-review/03
status:      DONE
verdict:     NONE

changed:
  - tests/HomeCharts.Application.Tests/MainWindowViewModelRulesQueuePagingTests.cs — new file, three regression tests for the "Potential New Rules" paging fix.

verification:
  command:   dotnet build HomeCharts.sln && dotnet test HomeCharts.sln --no-build
  result:    PASS
  detail:    Build: 0 Warning(s), 0 Error(s). Tests: Domain.Tests 5/5 passed, Application.Tests 40/40 passed (incl. the 3 new tests), Infrastructure.Tests 11/11 passed. 0 failed, 0 skipped across the solution.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - New test file `MainWindowViewModelRulesQueuePagingTests.cs` covers edit-survives-paging (DoD bullet 1) — see § New test file below.
  - Same file covers Apply-All-covers-all-pages (DoD bullet 2), asserted via `_createCategorizationRulesBatchUseCase`'s effect on `InMemoryRuleRepository` — see § New test file.
  - Same file covers `SaveAllPotentialRulesCommand.CanExecute` true for an off-page modified row (DoD bullet 3) — see § New test file.
  - No new shared fixture was needed — reused the `TestDoubles.cs` in-memory repositories and the constructor-wiring pattern from `MainWindowViewModelTrendBarScalingTests.cs` verbatim.
  - Tests drive the real import path end-to-end via the public `ImportFromSelectedFileAsync`, not the private `RefreshRulesQueueAsync`/`_rulesQueueRows` — see § New test file for the temp-file approach.
  - Added a `WaitUntilIdleAsync(viewModel)` local helper (polls the public `IsBusy` property) to safely await a fire-and-forget command's async body; reuse it for any future fire-and-forget command assertion.

risks:
  - "Apply All reaches the batch use case" is asserted indirectly through `InMemoryRuleRepository.GetActiveAsync()` rather than a mock, because `CreateCategorizationRulesBatchUseCase` has no interception seam of its own.
  - That indirection matches the tradeoff `MainWindowViewModelTrendBarScalingTests.cs` already makes (use-case side effects, not mocks) — not a new pattern for this file.
  - `RulesQueuePageSize = 120` is a private constant on `MainWindowViewModel`; the new test file re-declares it locally with a comment pointing at the source, since it cannot be referenced directly.
  - If that private constant ever changes, the test file's local copy must be updated alongside it — nothing catches that mechanically.
  - `mattpocock-skills:tdd` was not invoked: this order adds tests against already-merged production code (the frontend fix landed before this order started), so there is no red-green cycle here.
  - The only mocking-vs-real tradeoff in this file is the one already named above (asserting via repository side effects), so the tdd call collapses to that single, already-precedented decision.

## Orchestrator brief
- New regression test file added under `tests/HomeCharts.Application.Tests/`, no `src/**` touched, no new test project created.
- All three `definition_of_done` cases from the order are covered by one file, three test methods — see § New test file for which method covers which case.
- `dotnet build HomeCharts.sln && dotnet test HomeCharts.sln --no-build` passes in full: 56 tests, 0 failed.
- No pack corrections, no contract notes — the fix from `02-frontend.md` matched the pack's documented `Application.Tests`-covers-`Presentation` seam exactly.

## New test file

`tests/HomeCharts.Application.Tests/MainWindowViewModelRulesQueuePagingTests.cs` — three `[TestMethod]`s, one per DoD bullet:

- `RulesQueuePaging_EditOnDisplayedPage_SurvivesNavigatingAwayAndBack` — sets `SelectedCategory` on page 1's first row, calls `NextRulesQueuePageCommand`/`PreviousRulesQueuePageCommand`, asserts the row's `SelectedCategory`/`IsModified` are unchanged on return.
- `SaveAllPotentialRulesAsync_ModifiedRowsOnMultiplePages_AreAllPersistedAsRules` — modifies one row on each of two pages, invokes `SaveAllPotentialRulesCommand`, asserts both rows' descriptions became rule patterns in `InMemoryRuleRepository`.
- `SaveAllPotentialRulesCommand_CanExecute_TrueForModifiedRowOnAnotherPage` — modifies a row on page 1, navigates to page 2, asserts `CanExecute(null)` is still `true`.

All three share `CreateViewModelWithPotentialRulesAsync(rowCount)`: builds the same in-memory-fake-wired `MainWindowViewModel` as `MainWindowViewModelTrendBarScalingTests`, calls `LoadInitialStateAsync()`, writes a temp `BankRecipes`-style file with `rowCount` unique unmatched rows (default `RulesQueuePageSize + 10` = 130, forcing exactly 2 pages), and imports it via `ImportFromSelectedFileAsync`.
