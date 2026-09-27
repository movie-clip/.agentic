REPORT 2026-09-24-import-rules-redesign/04
status:      DONE
verdict:     NONE

changed:
  - src/HomeCharts.Presentation/Mvp/PotentialRulesViewModel.cs — new; child VM (paging 120, Summary, PageInfo, ApplyAllText, commands, RefreshAsync) plus PotentialRulesHost delegate record
  - src/HomeCharts.Presentation/Mvp/PotentialRuleRowViewModel.cs — new; row VM over PotentialRuleRow, forwards IsModified to PotentialRuleDraft, own SaveCommand
  - src/HomeCharts.Presentation/Mvp/MainWindowViewModel.cs — removed all rules-queue state, commands, methods, ExpenseCategoryOrder; added PotentialRules property; ctor takes ApplyPotentialRulesUseCase in place of single+batch
  - src/HomeCharts.Presentation/Mvp/MainWindowViewModel.cs — FormatDescriptionForDisplay delegates to DescriptionPrefixStripper; ReloadCategoriesAsync uses ExpenseCategoryCatalog.SelectAssignable
  - src/HomeCharts.Presentation/Mvp/TransactionsModels.cs — deleted EditableRulesImportedTransactionViewModel
  - src/HomeCharts.App/MainWindow.axaml — replaced Potential New Rules card with PotentialRules-bound list; no window-ancestor bindings; modified-row style, Apply All (N)
  - src/HomeCharts.App/CompositionRoot.cs — Preview ctor gets category and prefix repositories; batch use case replaced by ApplyPotentialRulesUseCase

verification:
  command:   dotnet build src/HomeCharts.Presentation/HomeCharts.Presentation.csproj ; dotnet build src/HomeCharts.App/HomeCharts.App.csproj
  result:    PASS
  detail:    Presentation: Build succeeded, 0 Warning(s), 0 Error(s). App: Build succeeded, 0 Warning(s), 0 Error(s). No file lock encountered.

contract_notes:
  - MainWindowViewModel ctor changed: params createCategorizationRuleUseCase and createCategorizationRulesBatchUseCase replaced by one ApplyPotentialRulesUseCase at the same position. All test VM factories (paging tests, TrendBarScalingTests) must follow.
  - Removed public members on MainWindowViewModel: ImportedRuleTransactions, RulesQueueSummary, RulesQueuePageInfo, the five rules-queue commands. Replaced by PotentialRules.Rows, Summary, PageInfo, RefreshCommand, NextPageCommand, PreviousPageCommand, ApplyAllCommand and row SaveCommand.
  - CreateCategorizationRulesBatchUseCase now has no reference in src/Presentation or src/App; only tests still use it, so the orchestrator git rm can follow the test lane.
  - docs/PROJECT_GUIDE.md:23,27-28 and RELEASE_NOTES.md must mention row highlight, Apply All (N) count and edits surviving in-list refreshes (D1, D2).

pack_corrections:
  - none

handoff:
  - PotentialRulesViewModel ctor: (PreviewPotentialRulesUseCase, ApplyPotentialRulesUseCase, IReadOnlyList<CategoryOptionViewModel> categories, PotentialRulesHost). PotentialRulesHost is a record of five delegates: GetImportFilePath, GetIsBusy, RunBusyAsync, SetStatus, RefreshDependentsAsync.
  - Refresh semantics (D-1): public RefreshAsync(content) drops edits (import, merge, apply rules, prefix, restore, load). RefreshCommand, single Save and Apply All keep Description and SelectedCategory for rows whose RowKey survives and whose file path is unchanged.
  - Test: edit survives paging; Apply All saves modified rows from two pages; Apply All enabled when the only modified row is on another page; PageSize const used, not 120.
  - Test: D1 — edit two rows, save one, other edit survives; RefreshAsync(content) resets edits; ApplyAllText is Apply All (N) with N over Draft.IsApplicable.
  - Test: status text for each PotentialRuleSaveOutcome; ConsideredCount 0 status; row SaveCommand CanExecute false with no category or while busy.
  - Test: missing file, empty file and parse errors give Summary Potential new rules: 0, PageInfo Page 1/1 and no rows; a VM test with 130 rows gives Page 1/2.
  - Manual check not run: AXAML visual (bounded region, modified-row border colour, ComboBox selection binding) needs a launch of HomeCharts.App; only compile of the XAML was verified.

skill_calls:
  - mattpocock-skills:diagnosing-bugs — not called, no bug fix and no failed fix attempt

risks:
  - Behaviour change on missing or empty file: old code cleared visible rows but left hidden rows in the Apply All set; new ClearRows empties everything. Judged a latent bug, not parity.
  - Row default selection is a lookup of SuggestedCategoryId in ExpenseCategories. If the id is a non-assignable fallback category, no option is selected and the row reads as modified; only reachable with no assignable categories.
  - Unsaved edits are preserved only when RowKey matches, not when the baseline pattern or category changed; safe today since prefix changes use the resetting RefreshAsync, but not enforced.
  - RulesImportedTransactionViewModel and RulesUnmatchedTransactionViewModel are unreferenced in src but still used by tests/Test1.cs, so left in place per the order; a later cleanup order should remove them with that test.
  - Apply All count and enablement call Draft.IsApplicable per row on every change; cheap now, revisit if lists reach thousands of rows.
