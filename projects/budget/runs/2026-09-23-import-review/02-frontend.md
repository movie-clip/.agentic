REPORT 2026-09-23-import-review/02
status:      DONE
verdict:     NONE

changed:
  - src/HomeCharts.Presentation/Mvp/MainWindowViewModel.cs — `_rulesQueueRows` now stores `EditableRulesImportedTransactionViewModel` (built once in `RefreshRulesQueueAsync`) instead of raw `PotentialRuleRow`, so edit state survives paging.
  - src/HomeCharts.Presentation/Mvp/MainWindowViewModel.cs — `RefreshRulesQueuePage()` now pages by adding existing view-model instances from `_rulesQueueRows` into `ImportedRuleTransactions`, instead of constructing fresh (edit-state-less) view models per page.
  - src/HomeCharts.Presentation/Mvp/MainWindowViewModel.cs — `SaveAllPotentialRulesAsync()` now reads modified rows from `_rulesQueueRows` (the full queue, all pages) instead of `ImportedRuleTransactions` (the currently displayed page only).
  - src/HomeCharts.Presentation/Mvp/MainWindowViewModel.cs — `SaveAllPotentialRulesCommand`'s `CanExecute` predicate now checks `_rulesQueueRows` instead of `ImportedRuleTransactions`, so "Apply All" stays enabled/disabled correctly when a modified row is on a page other than the one currently displayed.

verification:
  command:   dotnet build HomeCharts.sln && dotnet build src/HomeCharts.App/HomeCharts.App.csproj
  result:    PASS
  detail:    Both builds succeeded, 0 Warning(s), 0 Error(s), on this warnings-as-errors repo.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Test lane should cover: edit `SelectedCategory` on rules-queue page 1, page to page 2 and back via `Next`/`PreviousRulesQueuePageCommand`, assert the page-1 row's `SelectedCategory`/`IsModified` are unchanged.
  - Test lane should cover: modify rows across two-plus pages of a >120-row queue (`RulesQueuePageSize = 120`), invoke `SaveAllPotentialRulesAsync`, assert the batch use case receives every modified row from every page.
  - Test lane should cover: `SaveAllPotentialRulesCommand.CanExecute` is true when a modified row exists on a page other than the one currently displayed.
  - No `tests/HomeCharts.Presentation` test project exists in this repo (confirmed by 01-recon.md), so this is new coverage, not a regression fix to an existing test file.

risks:
  - Per DoD, `RefreshRulesQueueAsync`'s whole-queue-replace on a new import/refresh was left unchanged (01-recon.md Finding 1), which is correct per the order.
  - Consequence of the above, pre-existing and out of scope: the per-row "Save" button (`SavePotentialRuleAsync`) calls `RefreshRulesQueueAsync()` on success, which still discards all other rows' pending edits by design — untouched by this fix.
  - `SaveAllPotentialRulesCommand`'s `CanExecute` predicate was changed from `ImportedRuleTransactions.Any(...)` to `_rulesQueueRows.Any(...)`, not explicitly named in `definition_of_done`.
  - That predicate change was necessary: without it, "Apply All" could show disabled while a modified row still exists on a different page — treated as part of "commits every modified row across all pages," not a separate change.
