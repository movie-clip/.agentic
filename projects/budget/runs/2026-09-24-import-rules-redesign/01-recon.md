REPORT 2026-09-24-import-rules-redesign/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only recon, order verification NONE

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Single implementation today: no second view model, AXAML block, use case or WPF path exists. Every hit is in MainWindowViewModel.cs, TransactionsModels.cs:52-97, MainWindow.axaml:421-490, PreviewPotentialRulesUseCase.cs, CompositionRoot.cs:35,77. see § Q1
  - Live capabilities are only: edit description, category ComboBox, per-row Save, Apply All (modified rows, all pages), Refresh Queue, Prev/Next, summary and page text. No select, reject, filter, match-type, or priority UI exists. see § Q2
  - Presentation holds decision logic that guardrail 3 would flag: default-category choice (VM:1559-1572), IsModified (TransactionsModels.cs:94-96), Apply All filter (VM:878-881), prefix-stripping FormatDescriptionForDisplay (VM:1515-1542), paging. see § Q3
  - No clearly dead code found in the list flow. The full set is live, and all of it is a replacement candidate (VM members, EditableRulesImportedTransactionViewModel, PotentialRuleRow, the two create use cases only if their signatures change). see § Q4
  - Tests to update: MainWindowViewModelRulesQueuePagingTests.cs (4 VM-shape-coupled tests), Test1.cs:79 (Editable VM), Test1.cs:1062 and :1078 (use case), and the ctor calls in TrendBarScalingTests.cs:52-66. see § Q5
  - Same capabilities need no change outside Presentation/App. Rule create/dedup/naming/priority=5/MatchType=Contains lives in Application (CreateCategorizationRuleUseCase.cs:20-47). No migration or Contracts change is evidenced. see § Q6
  - Docs to reconcile: docs/PROJECT_GUIDE.md:23,27-28 and RELEASE_NOTES.md entries at :3-11 and :29-39. TECHNICAL_DESIGN.md and OPERATIONS.md have no mention. see § Q7
  - The input recon's claim that the Import Border lacks Grid.Row is now stale: MainWindow.axaml:388 has Grid.Row="3" (uncommitted working-tree edit; git status shows MainWindow.axaml and RELEASE_NOTES.md modified).

skill_calls:
  - none

risks:
  - I read the AXAML only at :386-505 and the VM at the cited ranges, not the whole VM. There may be other references to the list in VM regions I did not open, but the grep of ImportedRuleTransactions, _rulesQueue and RulesQueue names shows none outside those cited.
  - Did not open 2026-09-23-import-review/01-recon.md, since the order said "if it exists". Not checked whether it exists.
  - I did not find legacy WPF code referencing the list. The grep covered *.cs, *.axaml, *.xaml, *.md under the repo, excluding bin and obj noise, and found none. A legacy folder not matching those extensions would be missed.
  - RulesQueueSummary and the "Potential new rules" text is set from three different places in RefreshRulesQueueAsync (VM:1282,1291,1298,1324). Not verified whether its "0" strings are asserted by tests beyond the paging test at :157.
  - Rows are re-created with Guid.NewGuid() and default category on every RefreshRulesQueueAsync (VM:1307-1319), so unsaved edits are lost after any refresh (save, prefix change, apply rules, import). This is current behaviour, not confirmed as intentional.
  - After a successful save the list is rebuilt from the file via the use case, so saved rows disappear because they now match a rule. The per-row Save has no other removal path.

## Orchestrator brief
- Q1: one implementation only. Live path: MainWindow.axaml:421-490 -> MainWindowViewModel (rules queue members) -> PreviewPotentialRulesUseCase / CreateCategorizationRule(s)BatchUseCase. No WPF, no duplicate VM, no second AXAML block found.
- Q2: capabilities are description TextBox, category ComboBox, per-row Save, Apply All, Refresh Queue, Prev/Next, summary, page info. No select/reject/filter/match-type/priority in UI.
- Q3: Presentation holds default-category choice, IsModified, Apply All filter, prefix display stripping, paging. All are guardrail 3 candidates. Domain and Application hold suggestion detection and rule creation.
- Q4: nothing clearly dead. Everything in the flow is live and a replace candidate. The `MatchedImportTransactions` flow is a separate preview (Transactions tab), not this list.
- Q5: tests are coupled to VM member names, page size 120, and "Page n/m" strings (tests listed below).
- Q6: no change outside Presentation/App evidenced for equal capability. Application/Contracts only if new capability (e.g. match type, priority) is wanted.
- Q7: PROJECT_GUIDE.md:23,27-28 and two RELEASE_NOTES sections mention it.
- Correction: the earlier bounds recon's missing Grid.Row claim is stale; :388 now has Grid.Row="3".
- Sections below: Q1 Implementations; Q2 Capabilities; Q3 Decision-logic placement; Q4 Dead vs replaceable; Q5 Tests; Q6 Blast radius outside Presentation/App; Q7 Docs.

## Q1 Implementations
- One view of the list: src/HomeCharts.App/MainWindow.axaml:421-490 (header WrapPanel :424-432, column header :436-444, ScrollViewer + ItemsControl :446-486). Import tab Border :388 has Grid.Row="3".
- One VM: src/HomeCharts.Presentation/Mvp/MainWindowViewModel.cs. Row VM: src/HomeCharts.Presentation/Mvp/TransactionsModels.cs:52-97 (EditableRulesImportedTransactionViewModel).
- One use case for detection: src/HomeCharts.Application/UseCases/PreviewPotentialRulesUseCase.cs:7-54 (records PotentialRuleRow, PreviewPotentialRulesResult). Wired at App/CompositionRoot.cs:35 and :77.
- Two use cases for persistence: CreateCategorizationRuleUseCase.cs (single) and CreateCategorizationRulesBatchUseCase.cs (batch, delegates to single). Wired at CompositionRoot.cs:56-57.
- Look-alike but a different feature: MatchedImportTransactions / PreviewMatchedTransactionsUseCase / MergeMatchedTransactionsUseCase (Ledger tab preview at MainWindow.axaml:528-536; VM:631-738). It lists rows that already match rules; it is not the suggestion list.
- Not found: no WPF/legacy path, no other AXAML or view model, no separate suggestion engine, in src, tests or docs.

## Q2 Capabilities of the live list
- Edit description/match string: Description property (TransactionsModels.cs:79-83), TextBox at MainWindow.axaml:453-460.
- Category dropdown: SelectedCategory (TransactionsModels.cs:85-89), ComboBox :462-472 bound to window-level ExpenseCategories (VM:200, filled VM:1042-1052 from ExpenseCategoryOrder).
- Per-row save: SavePotentialRuleCommand (VM:175), Save Button :473-480 (ReflectionBinding to window DataContext, CommandParameter row). Handler SavePotentialRuleAsync VM:840-872.
- Apply All: SaveAllPotentialRulesCommand (VM:178-180), Button :427, handler VM:874-894. Enabled when any row in _rulesQueueRows (all pages) IsModified with a category (VM:180).
- Refresh Queue: RefreshRulesQueueCommand (VM:169), Button :428, handler RefreshRulesQueueAsync VM:1274-1325 (re-reads file at ImportFilePath, or given content).
- Paging: NextRulesQueuePageCommand/PreviousRulesQueuePageCommand (VM:170-171), Buttons :429-430, RulesQueuePageInfo text :431. RulesQueuePageSize const 120 (VM:105). Slice in RefreshRulesQueuePage VM:1349-1379.
- Summary: RulesQueueSummary "Potential new rules: N" (VM:305-308, set VM:1324), TextBlock :426.
- Display: date (BookingDateText), amount (AmountText) read-only, TransactionsModels.cs:91-92.
- Modified tracking: IsModified compares against original description and category id (TransactionsModels.cs:94-96). OnImportedRuleTransactionChanged (VM:1639-1646) re-raises command CanExecute.
- Not present: select/checkbox, reject/dismiss, filter/search, match type, priority, sort, bulk category set, per-row removal, undo.
- Match type and priority are not user-editable: the use case hardcodes Contains and Priority 5 (CreateCategorizationRuleUseCase.cs:38-39).
- Refresh triggers: import (VM:599, 621), merge (:723), apply rules (:748), refresh (:765), clear rules (:798), prefix add/remove (:909, :932), restore (:954), package import (:978), single save (:864), apply all (:890), and VM:1659 (initial load).
- Rows are rebuilt with fresh Guid and default category on every refresh (VM:1307-1319), so unsaved edits do not survive a refresh.

## Q3 Decision-logic placement
- Domain: CategorizationEngine.Match and DescriptionNormalizer (used by PreviewPotentialRulesUseCase.cs:29-30). Correct layer.
- Application: which rows are "potential" (unmatched by any active rule) PreviewPotentialRulesUseCase.cs:24-39; rule creation, trim, duplicate check (same category, Contains, case-insensitive pattern), name, priority 5: CreateCategorizationRuleUseCase.cs:15-47; batch counts: CreateCategorizationRulesBatchUseCase.cs:7-33.
- Presentation (flag, guardrail 3): default category choice ("None", else first non-"Uncategorized", else first) at VM:1559-1572.
- Presentation (flag): IsModified rule at TransactionsModels.cs:94-96, and Apply All row selection filter at VM:878-881 (both decide what gets persisted).
- Presentation (borderline, formatting or decision): FormatDescriptionForDisplay strips configured prefixes at VM:1515-1542 and its output becomes the rule pattern the user saves (VM:1313, then :855). A pattern derived from stripped text is a rule-content decision.
- Presentation (display/dispatch, acceptable): paging math VM:1349-1379, 1615-1622; status strings; command enable state.
- App: no decision logic; the AXAML binds only. Code-behind for the tab is OnBrowseImportFileClick / OnClearAllRulesClick (MainWindow.axaml.cs:135-139), not the list.
- Guardrail 1/2 exposure: rules created here are Contains/priority 5 through Application, so precedence is unchanged. Manual overrides are not touched by this flow.

## Q4 Dead vs replaceable
- Clearly outdated/unreferenced today: none found in the list flow. Every symbol below has a live caller.
- Live, replace candidates (Presentation): VM members _rulesQueueSummary/_rulesQueuePageInfo/_rulesQueueCurrentPage/_rulesQueueTotalMatchedCount/_rulesQueueRows (VM:77-78,101-103), RulesQueuePageSize (:105), ImportedRuleTransactions (:206), 5 commands (:169-171,175-180 and props :231-238), RulesQueueSummary/PageInfo props (:305-314), SavePotentialRuleAsync, SaveAllPotentialRulesAsync, RefreshRulesQueueAsync, Move*/Refresh*RulesQueuePage, GetDefaultPotentialRuleCategory, OnImportedRuleTransactionChanged, CanMoveNextRulesQueuePage, RaiseCommands entries (:1584-1591), and ~10 call sites of RefreshRulesQueueAsync (see Q2).
- Live, replace candidates (Presentation): EditableRulesImportedTransactionViewModel (TransactionsModels.cs:52-97).
- Live, replace candidate (App): MainWindow.axaml:421-490 and the AXAML resources/bindings inside it.
- Live, may stay: PreviewPotentialRulesUseCase + records (Application) and CreateCategorizationRuleUseCase + Batch use case, both used only by this flow (only VM, CompositionRoot and tests reference them). Would become dead only if the redesign stops using them.
- Live, may stay: ExpenseCategories (VM:200) is also used at VM:1056, so not list-only.
- Dependency injection: both use cases are constructor arguments of MainWindowViewModel (VM:118-123) and are built in CompositionRoot.cs:35,56-57,77. Any signature change ripples to both test view-model factories.
- Shared and NOT part of the list: FormatDescriptionForDisplay (also used at VM:676,1108,1215,1234,1243,1258,1507), RefreshParsedCategoryExpensesAsync/ParsedCategoryExpenses (the Expenses panel at :492-505, refreshed alongside the list).

## Q5 Tests
- tests/HomeCharts.Application.Tests/MainWindowViewModelRulesQueuePagingTests.cs. Couples to VM shape: hardcoded page size 120 (:23), ImportedRuleTransactions, ExpenseCategories, NextRulesQueuePageCommand/PreviousRulesQueuePageCommand, RulesQueuePageInfo "Page n/m" (:41-44,68,97), SaveAllPotentialRulesCommand.CanExecute, RulesQueueSummary "Potential new rules: N" (:157), row.IsModified, row.SelectedCategory. Four tests: edit survives paging (:26), apply-all persists across pages (:53), CanExecute true for another page (:86), plus the setup helper (:104-184) which builds the full VM constructor.
- tests/HomeCharts.Application.Tests/Test1.cs:41 CreateCategorizationRulesBatchUseCase counts created/duplicate/invalid (use case only).
- tests/HomeCharts.Application.Tests/Test1.cs:79 EditableRulesImportedTransactionViewModel_TracksModifiedStateFromDescriptionAndCategory (row VM shape, IsModified).
- tests/HomeCharts.Application.Tests/Test1.cs:1062 and :1078 PreviewPotentialRulesUseCase returns rows with no rules / excludes matched rows (use case only, asserts PotentialRows and Description).
- tests/HomeCharts.Application.Tests/MainWindowViewModelTrendBarScalingTests.cs:52,61,66 build the VM with the two use cases; coupled only through the constructor parameter list.
- No Presentation test project, no Domain or Infrastructure tests of the list, no AXAML/UI tests.
- Layout, ComboBox binding and Save button wiring have no automated coverage.

## Q6 Blast radius outside Presentation/App
- Same capabilities: none evidenced. Detection and persistence are already in Application (Q3) and no repository method takes list-specific parameters. IRuleRepository.GetActiveAsync and UpsertAsync are the only Contracts members used (PreviewPotentialRulesUseCase.cs:24, CreateCategorizationRuleUseCase.cs:21,46).
- Moving default-category choice, modified-row selection, or prefix-stripped pattern derivation out of Presentation (Q3) would land in Application (new or extended use case) and the two test VM factories. That is a consequence of guardrail 3, not of the capability set.
- New capabilities not in the current list (match type, priority) would need CreateCategorizationRuleUseCase and batch item signature changes (CreateCategorizationRulesBatchItem(string Pattern, Guid CategoryId) at Batch.cs:37). Not required for equal capability.
- No migration, schema or Contracts change is evidenced: rules already carry Name, Pattern, MatchType, Priority, CategoryId, IsActive (CreateCategorizationRuleUseCase.cs:33-44).

## Q7 Docs
- docs/PROJECT_GUIDE.md:23 "rule suggestions are shown", :27-28 "Potential rules are listed in pageable form. Each row supports inline edit + category select + save." Needs reconciling if paging or per-row Save changes.
- docs/RELEASE_NOTES.md:3-11 (2026-09-24 bounded list, pager header no longer fixed height) and :29-39 (2026-09-23 paging/Apply-All fix). History entries; a new dated entry would be added, old ones not edited. The file is already modified in the working tree.
- docs/TECHNICAL_DESIGN.md, docs/OPERATIONS.md, docs/README.md, AGENTS.md: no mention of PotentialNewRules, RulesQueue, PreviewPotentialRules or Apply All found by grep. TECHNICAL_DESIGN.md use-case list was not read in full, so a generic mention of rule use cases may exist.
- PROJECT_GUIDE.md:20-23 says import selects a file; it does not describe the Browse-then-auto-import behaviour shown by MainWindow.axaml:396.
