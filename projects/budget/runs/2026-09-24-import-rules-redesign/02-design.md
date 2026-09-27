REPORT 2026-09-24-import-rules-redesign/02
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only design pass, order verification NONE

contract_notes:
  - New Domain members: DescriptionPrefixStripper.Strip and ExpenseCategoryCatalog (OrderedNames, SelectAssignable). MainWindowViewModel private ExpenseCategoryOrder and FormatDescriptionForDisplay body must adopt them. see § Contract
  - PreviewPotentialRulesUseCase ctor gains ICategoryRepository and IPrefixFilterRepository. PotentialRuleRow gains RowKey, SuggestedPattern, SuggestedCategoryId. CompositionRoot.cs:35 and 4 test factories must match. see § Contract
  - New ApplyPotentialRulesUseCase plus PotentialRuleDraft replace CreateCategorizationRulesBatchUseCase. MainWindowViewModel ctor swaps two params (single, batch) for one (apply); CompositionRoot and all test VM factories follow. see § Contract
  - docs/PROJECT_GUIDE.md:23,27-28 and a new dated RELEASE_NOTES.md entry must reflect the new list. see § Lane split

pack_corrections:
  - none

handoff:
  - backend lane first, purely additive: Domain stripper and catalog, extended Preview use case, new ApplyPotentialRulesUseCase and PotentialRuleDraft. Verify with dotnet build src/HomeCharts.App/HomeCharts.App.csproj is not possible until frontend lands, so use per-project builds. see § Lane split
  - frontend lane second: new PotentialRulesViewModel and PotentialRuleRowViewModel, delete every rules-queue member from MainWindowViewModel, replace AXAML :421-490 list block, rewire CompositionRoot. see § Removal list
  - test lane third: rewrite MainWindowViewModelRulesQueuePagingTests, Test1.cs:41/:79/:1062/:1078, ctor calls in TrendBarScalingTests, add Domain and Application tests. see § Test plan
  - no lane can delete files: orchestrator must run git rm on src/HomeCharts.Application/UseCases/CreateCategorizationRulesBatchUseCase.cs after the test lane removes its last reference. see § Removal list
  - two OPEN DECISIONS go to the human before or during frontend dispatch: edit preservation across refresh (D1) and cosmetic list polish (D2). Frontend builds parity behaviour if unanswered. see § Open decisions
  - docs lane last: PROJECT_GUIDE.md:23,27-28, new RELEASE_NOTES.md dated entry, check TECHNICAL_DESIGN.md use-case list. see § Lane split

skill_calls:
  - mattpocock-skills:codebase-design — called, used for depth and seam calls (one use case module per direction, deleting the batch pass-through, single shared stripper)

risks:
  - Solution build is red between the backend, frontend and test lanes (ctor and record changes). Each lane must verify with project-level builds, only the final state runs dotnet build HomeCharts.sln and dotnet test.
  - MainWindowViewModel.FormatDescriptionForDisplay is also used by Ledger and detail code paths (VM:676,1108,1215,1234,1243,1258,1507). Its body becomes a one-line call to the Domain stripper; behaviour must stay byte-identical for those callers.
  - Recon's ExpenseCategories claim is checked: VM:1042-1052 filters by a private name list. Left in VM it would duplicate the use case's default-category filter, so SelectAssignable moves to Domain and both call it.
  - Preview use case now reads prefix filters and categories from the repositories on every call, two extra reads per refresh. Local SQLite, acceptable; no caching added.
  - PotentialRuleRow.RowKey must be deterministic (no Guid.NewGuid) or D1 cannot work and tests cannot assert identity. It is derived from line, date, amount, raw description.
  - Extracting PotentialRulesViewModel needs busy-state and status plumbing from MainWindowViewModel (RunBusyAsync, Status). The plumbing shape is left to frontend but must not copy decisions into the child VM.
  - I read the VM only at cited ranges plus the category and prefix regions; the ImportFromSelectedFileAsync, apply-rules and merge call sites (VM:599,621,723,748,765,798,978) were not opened, only their refresh calls counted from grep.

## Orchestrator brief
- Decision: ONE list implementation = new child VM PotentialRulesViewModel + PotentialRuleRowViewModel; MainWindowViewModel keeps only a PotentialRules property and RefreshAsync calls.
- Decision: all deciding logic moves down. Prefix-stripped pattern, default category, assignable category set: Domain + PreviewPotentialRulesUseCase. IsModified and Apply-All selection: Application PotentialRuleDraft + ApplyPotentialRulesUseCase.
- Decision: batch use case deleted (git rm by orchestrator); single CreateCategorizationRuleUseCase stays as the only rule-creation path (Contains, priority 5 unchanged).
- Decision: no migration, no Contracts interface change, no new capability. Paging (120/page) kept inside the bounded region.
- Lanes: backend (additive) -> frontend -> test -> git rm -> docs. Solution build red between lanes, use project builds.
- OPEN DECISIONS for human: D1 unsaved edits across refresh, D2 cosmetic polish (modified-row highlight, Apply All count). Defaults given; neither blocks dispatch.
- § Contract: exact Domain/Application shapes, field by field.
- § Lane split: per-lane scope, order, verification commands.
- § Removal list: every member, class, AXAML block, use case, test removed or replaced.
- § Behavior decisions: refresh, saved rows, paging, errors.
- § Parity map; § UX brief; § Test plan; § Open decisions.

## Contract

Categorization engine is NOT touched (Exact > Regex > Contains, priority tie-break unchanged). No migration. No `HomeCharts.Contracts` change: existing `IRuleRepository`, `ICategoryRepository`, `IPrefixFilterRepository` are enough.

### Domain (new, backend)

```
namespace HomeCharts.Domain.Categorization
public static class DescriptionPrefixStripper
    string Strip(string description, IEnumerable<string> prefixes)
```
Exact algorithm moved from MainWindowViewModel.cs:1515-1542: ignore blank prefixes; order prefixes by length descending; repeatedly, if the value starts with a prefix (OrdinalIgnoreCase), drop it and `TrimStart(' ', '-', ':')`, restart the scan; stop when none matches; if the result is blank return the original `description`.

```
namespace HomeCharts.Domain.Model
public static class ExpenseCategoryCatalog
    IReadOnlyList<string> OrderedNames   // the 18 names of VM:13-33, same order:
        // None, Cafe, Shopping, Grocery, Education, Car, Entertainment, House, Medicine,
        // Rent, Utility, Smoke, Travel, Transport, Services, Income, Transfer, Others
    IReadOnlyList<T> SelectAssignable<T>(IEnumerable<T> categories, Func<T,string> nameOf)
        // for each name in OrderedNames: first item whose name matches (OrdinalIgnoreCase);
        // skip if an already-selected item has the same name. Mirrors VM:1042-1052.
```
Both are pure, no clock, no randomness (guardrail 1 safe).

### Application (backend)

`PreviewPotentialRulesUseCase` (same file, same name, extended):
```
ctor(IRuleRepository, ICategoryRepository, IPrefixFilterRepository, BankStatementParser)
Task<PreviewPotentialRulesResult> ExecuteAsync(string fileContent, CancellationToken ct = default)

record PotentialRuleRow(
    string  RowKey,               // non-null, deterministic, unique within one result
    int     LineNumber,
    DateOnly BookingDate,
    string  RawDescription,       // was Description; unmodified parser text, not shown by default
    decimal Amount,
    string  SuggestedPattern,     // DescriptionPrefixStripper.Strip(RawDescription, configured prefixes)
    Guid?   SuggestedCategoryId)  // null only if the category table is empty
record PreviewPotentialRulesResult(IReadOnlyList<PotentialRuleRow> PotentialRows,
    IReadOnlyList<BankStatementParseError> Errors, IReadOnlyList<BankStatementParseWarning> Warnings) // unchanged
```
Rules:
- Detection unchanged: parse errors -> empty rows plus errors; otherwise rows where `CategorizationEngine.Match(DescriptionNormalizer.Normalize(RawDescription), activeRules)` is null. Order = file order.
- `RowKey` = `$"{LineNumber}|{BookingDate:yyyy-MM-dd}|{Amount.ToString(CultureInfo.InvariantCulture)}|{RawDescription}"`. Unique because LineNumber is unique per file.
- `SuggestedCategoryId` picks, in order, exactly as VM:1559-1572: assignable category named "None" (OrdinalIgnoreCase); else first assignable not named "Uncategorized"; else first assignable; else first category of any kind; else null. "Assignable" = `ExpenseCategoryCatalog.SelectAssignable` over `ICategoryRepository.GetAllAsync`. The chooser is private to this use case.
- Prefixes come from `IPrefixFilterRepository.GetAllAsync`.

New, same folder `ApplyPotentialRulesUseCase.cs`:
```
public sealed record PotentialRuleDraft(
    string SuggestedPattern, Guid? SuggestedCategoryId,   // the baseline shown when the row was built
    string Pattern,          Guid? CategoryId)            // what the user has now
{
    public static PotentialRuleDraft FromRow(PotentialRuleRow row);   // Pattern=Suggested*, CategoryId=SuggestedCategoryId
    public bool IsModified   => !string.Equals(SuggestedPattern, Pattern, StringComparison.Ordinal) || SuggestedCategoryId != CategoryId;   // moved from TransactionsModels.cs:94-96
    public bool IsApplicable => IsModified && CategoryId is not null;                                   // moved from VM:878-881
}

public enum PotentialRuleSaveOutcome { Created, Duplicate, InvalidPattern, CategoryMissing }

public sealed record ApplyPotentialRulesResult(int ConsideredCount, int CreatedCount, int DuplicateCount, int InvalidCount);

public sealed class ApplyPotentialRulesUseCase(CreateCategorizationRuleUseCase createRule)
{
    Task<PotentialRuleSaveOutcome>   SaveOneAsync(PotentialRuleDraft draft, CancellationToken ct = default);
    Task<ApplyPotentialRulesResult>  SaveModifiedAsync(IReadOnlyCollection<PotentialRuleDraft> drafts, CancellationToken ct = default);
}
```
- `SaveOneAsync`: CategoryId null -> `CategoryMissing` (no write); otherwise delegate to `CreateCategorizationRuleUseCase.ExecuteAsync(draft.Pattern, draft.CategoryId.Value)`; invalid input -> `InvalidPattern`; IsCreated -> `Created`; else `Duplicate`. Does NOT require IsModified (parity: per-row Save works on an untouched row).
- `SaveModifiedAsync`: filter `IsApplicable`, process in input order, sequentially (each call re-reads active rules so same-batch repeats count as Duplicate, as today). `ConsideredCount` = number of applicable drafts; the VM shows "Modify at least one row..." when it is 0.
- `CreateCategorizationRuleUseCase` is unchanged: trim, duplicate = same category + Contains + OrdinalIgnoreCase pattern, `Name = "Contains ..."`, `MatchType.Contains`, `Priority = 5`, active. It stays the only rule-creation path.

### Presentation (frontend), display and dispatch only

```
public sealed class PotentialRulesViewModel : ObservableObject     // Mvp/PotentialRulesViewModel.cs
    public const int PageSize = 120;                                // display constant
    ObservableCollection<PotentialRuleRowViewModel> Rows            // current page only
    string Summary          // "Potential new rules: N"  (text kept)
    string PageInfo         // "Page n/m"               (text kept)
    ICommand RefreshCommand, NextPageCommand, PreviousPageCommand, ApplyAllCommand
    Task RefreshAsync(string? fileContent = null)                   // MainWindowViewModel calls this at its existing refresh sites

public sealed class PotentialRuleRowViewModel : ObservableObject   // replaces EditableRulesImportedTransactionViewModel
    string RowKey; string BookingDateText; string AmountText        // formatting only, "yyyy-MM-dd" and "0.00" as today
    string Description (settable) ; CategoryOptionViewModel? SelectedCategory (settable)
    IReadOnlyList<CategoryOptionViewModel> Categories               // shared reference to the parent's ExpenseCategories
    PotentialRuleDraft Draft => new(suggestedPattern, suggestedCategoryId, Description, SelectedCategory?.Id)
    bool IsModified => Draft.IsModified                              // forwards, no logic
    ICommand SaveCommand                                             // dispatches SaveOneAsync via the list VM
```
Presentation must not compare strings, choose defaults, or filter rows itself; it forwards `Draft` objects to Application and reads `IsModified` / `IsApplicable`. Row selection of the category option from `SuggestedCategoryId` is a lookup by Id in `ExpenseCategories` (mapping, not a decision); a null or missing id leaves no selection.

## Lane split

1. **backend** (first, purely additive). Scope: `src/HomeCharts.Domain/**`, `src/HomeCharts.Application/**`. Add the Domain stripper and catalog, extend `PreviewPotentialRulesUseCase`, add `ApplyPotentialRulesUseCase` and `PotentialRuleDraft`. Do NOT delete the batch use case yet and do not touch Presentation/App/tests. Reuse: `CreateCategorizationRuleUseCase` (unchanged), `CategorizationEngine.Match`, `DescriptionNormalizer.Normalize`, `IRuleRepository.GetActiveAsync`, `ICategoryRepository.GetAllAsync`, `IPrefixFilterRepository.GetAllAsync`, records style of `PreviewParsedCategoryExpensesUseCase.cs:54-59`. Verify: `dotnet build src/HomeCharts.Application/HomeCharts.Application.csproj` (warnings as errors). The full solution stays red until frontend and test land.
2. **frontend** (after backend). Scope: `src/HomeCharts.Presentation/**`, `src/HomeCharts.App/**`. Build the two new VM classes, replace the AXAML list block, rewire `CompositionRoot.cs:35,56-57,77-82`, delete everything in § Removal list, make `FormatDescriptionForDisplay` delegate to the Domain stripper, make `ReloadCategoriesAsync` use `ExpenseCategoryCatalog.SelectAssignable`. Verify: `dotnet build src/HomeCharts.App/HomeCharts.App.csproj` (also catches XAML). The new ctor breaks test projects; that is the test lane's.
3. **test** (after frontend). Scope: `tests/**`. Application-level tests can start once backend lands; VM tests need frontend. See § Test plan. Verify: `dotnet build HomeCharts.sln` then `dotnet test HomeCharts.sln --no-build`.
4. **orchestrator step**: `git rm src/HomeCharts.Application/UseCases/CreateCategorizationRulesBatchUseCase.cs` once no source or test references remain (no lane can delete). Re-run the full build and tests.
5. **docs** (last). `docs/PROJECT_GUIDE.md:23,27-28` describe the list; add a dated `docs/RELEASE_NOTES.md` entry (file already modified in the working tree); check `docs/TECHNICAL_DESIGN.md` use-case list for the batch use case and mention the new one.
6. **integration** (tech-lead) then runs against the final state; no story exists, so no reviewer.

Boundary rule for engineers: contracts before consumers. Frontend consumes only the shapes in § Contract; if it needs a different shape it stops and reports, it does not add logic in Presentation.

## Removal list

Delete or replace so that exactly one list implementation remains.

MainWindowViewModel.cs (frontend):
- Fields `_rulesQueueSummary`, `_rulesQueuePageInfo`, `_rulesQueueCurrentPage`, `_rulesQueueTotalMatchedCount`, `_rulesQueueRows` (:77-78,101-103) and const `RulesQueuePageSize` (:105): deleted, replaced by `PotentialRulesViewModel`.
- Fields `_previewPotentialRulesUseCase`, `_createCategorizationRuleUseCase`, `_createCategorizationRulesBatchUseCase` (:40,44,45) and ctor params/assignments (:118-123,142-147): the first stays only as input to the child VM; the two create ones are replaced by one `ApplyPotentialRulesUseCase` param.
- Commands and properties: `RefreshRulesQueueCommand`, `NextRulesQueuePageCommand`, `PreviousRulesQueuePageCommand`, `SavePotentialRuleCommand`, `SaveAllPotentialRulesCommand` (:169-180,231-238), `ImportedRuleTransactions` (:206), `RulesQueueSummary`, `RulesQueuePageInfo` (:305-314). Their logic lives on the child VM.
- Methods: `SavePotentialRuleAsync` (:840-872), `SaveAllPotentialRulesAsync` (:874-894), `RefreshRulesQueueAsync` (:1274-1325), `MoveNextRulesQueuePage`, `MovePreviousRulesQueuePage`, `RefreshRulesQueuePage` (:1327-1379), `GetDefaultPotentialRuleCategory` (:1559-1572), `CanMoveNextRulesQueuePage` (:1615-1623), `OnImportedRuleTransactionChanged` (:1639-1646), and the five RaiseCommands entries for them (:1584-1586,1590-1591).
- The ~12 `RefreshRulesQueueAsync` call sites (:599,621,723,748,765,798,864,890,909,932,954,978,1659) become `PotentialRules.RefreshAsync(...)`. Kept, because it is a dispatch not a decision.
- `ExpenseCategoryOrder` private array (:13-33): deleted, replaced by `ExpenseCategoryCatalog.OrderedNames`. `ExpenseCategories` collection (:200) stays (shared by the manual recategorization ComboBox).
- `FormatDescriptionForDisplay` (:1515-1542): stays as a one-line wrapper over `DescriptionPrefixStripper.Strip` because Ledger/detail paths call it; the algorithm body is deleted so there is one stripper.

TransactionsModels.cs (frontend): delete `EditableRulesImportedTransactionViewModel` (:52-97) and its IsModified rule; replaced by `PotentialRuleRowViewModel` (new file). `RulesImportedTransactionViewModel` and `RulesUnmatchedTransactionViewModel` are not part of this list; check with grep and leave untouched unless unreferenced (out of scope otherwise).

MainWindow.axaml (frontend): replace the whole card at :422-490 (header WrapPanel, column header, ScrollViewer + ItemsControl + row template). Delete the two `ReflectionBinding ... RelativeSource AncestorType=Window` bindings (:463,476): the row carries `Categories` and `SaveCommand`. Leave the Expenses card :492-505 and the top cards :390-419 untouched. Also do not touch the Ledger/Dashboard XAML.

Application (backend, then orchestrator):
- `CreateCategorizationRulesBatchUseCase`, `CreateCategorizationRulesBatchItem`, `CreateCategorizationRulesBatchResult`: deleted (git rm the file), replaced by `ApplyPotentialRulesUseCase.SaveModifiedAsync`.
- `PotentialRuleRow.Description` renamed to `RawDescription`; record shape extended.
- Kept and justified: `CreateCategorizationRuleUseCase` (the single rule-creation path; the new use case wraps it), `PreviewPotentialRulesUseCase` (detection).

App: `CompositionRoot.cs:35` (Preview ctor gets `categoryRepository`, `prefixFilterRepository`), `:56-57` (drop batch, add `new ApplyPotentialRulesUseCase(createCategorizationRuleUseCase)`), `:77-82` argument list.

Tests: see § Test plan.

Not deleted, deliberately: `MatchedImportTransactions` / `PreviewMatchedTransactionsUseCase` (different feature, Ledger tab), `PreviewParsedCategoryExpensesUseCase` and the Expenses panel (separate feature, refreshed alongside).

## Behavior decisions

Decided here because they are parity or evident from the request:
- **Saved rows leave the queue.** After a successful save the list is re-derived from the file through `PreviewPotentialRulesUseCase`; any row that now matches a rule disappears. This is intended (the queue means "not covered by a rule yet"). If the user saved a pattern that does not match the row, that row stays.
- **Per-row Save** works on an untouched row (saves the suggested pattern + default category). **Apply All** saves only rows with `IsApplicable`, across all pages. Both unchanged from today.
- **Statuses** keep today's wording for: category missing, blank pattern, duplicate, rule saved, apply-all counts, "Modify at least one row before applying all rules." (shown when `ConsideredCount == 0`). Wording is display and stays in the child VM.
- **Paging kept**, 120 rows per page, page info text "Page n/m", inside the bounded region. Reason: PROJECT_GUIDE.md:27 documents "pageable", the ItemsControl is not virtualized and 120 TextBox+ComboBox rows already are the practical ceiling, and the earlier bounds fix depends on the region being finite. Paging math is display state, not a decision, and stays in Presentation.
- **Errors** from the parser: list is empty, summary "Potential new rules: 0", page "Page 1/1", as today.
- **Page after refresh** resets to page 1 (as today).
- **Edits across page turns** survive (rows are held for all pages, as fixed on 2026-09-23). Both this and Apply All across pages must remain covered by tests.
- **Edits across refresh**: see D1. Until the human answers, frontend implements today's behaviour (rows rebuilt, edits dropped) but MUST build rows from `RowKey` so D1 is a small change.
- **Unsaved edit lost on any refresh trigger** (save of another row, prefix change, apply rules, merge, import) is today's behaviour, recon flagged it as unconfirmed; it is escalated, not decided.

## Parity map

| Capability (01 § Q2) | After the redesign |
|---|---|
| Edit description / match string | `PotentialRuleRowViewModel.Description` + TextBox in new row template |
| Category dropdown | `PotentialRuleRowViewModel.SelectedCategory` + ComboBox over row's `Categories` (= parent `ExpenseCategories`), default chosen by `PreviewPotentialRulesUseCase` (`SuggestedCategoryId`) |
| Per-row Save | `PotentialRuleRowViewModel.SaveCommand` -> `ApplyPotentialRulesUseCase.SaveOneAsync` |
| Apply All (modified rows, all pages) | `PotentialRulesViewModel.ApplyAllCommand` -> `SaveModifiedAsync(drafts of every row)`; enabled when any row `Draft.IsApplicable` |
| Refresh Queue | `PotentialRulesViewModel.RefreshCommand` / `RefreshAsync` |
| Prev / Next, page text | `PreviousPageCommand`, `NextPageCommand`, `PageInfo` |
| Summary "Potential new rules: N" | `PotentialRulesViewModel.Summary` |
| Date and amount display, read-only | `BookingDateText`, `AmountText` on the row VM |
| Modified tracking | `PotentialRuleDraft.IsModified` (Application), forwarded by the row |
| Prefix-stripped default text | `SuggestedPattern` from Domain stripper via Preview use case |
| Duplicate/invalid/created counts | `ApplyPotentialRulesResult` |
| Rule = Contains, priority 5, name "Contains ..." | unchanged in `CreateCategorizationRuleUseCase` |
| Refresh on import/merge/apply/clear/prefix/restore/package/save/initial load | same sites call `PotentialRules.RefreshAsync` |

New capabilities: none proposed as required. Match type, priority, select/reject, filter, bulk category set, undo remain out. Cosmetic polish is D2.

## UX brief

Keep one card, three stacked zones, inside the same bounded area that the earlier Grid.Row fix established (Import tab Border `Grid.Row="3"`, card `MinHeight 280`, rows scrolling inside a ScrollViewer; the card must not push the Expenses card or the tab out of the window).
- **Header** (WrapPanel is fine): title "Potential New Rules", summary, Apply All, Refresh Queue, Prev, Next, page text. Same set as today.
- **Column header** aligned with rows: Date, Description / Match String, Amount, Expense Category, Action.
- **Rows**: one card per row, same 5 columns (`110,*,110,190,96`). The Description TextBox edits inline (watermark "Type matching string..."); the ComboBox picks the category; Save is per row. Bind with compiled bindings against `PotentialRuleRowViewModel`; no window-ancestor ReflectionBinding, no `CommandParameter="{Binding .}"`.
- **Scroll**: vertical ScrollViewer inside the bounded card; horizontal disabled. Paging stays the way to move between chunks of 120.
- **Empty state**: when zero rows, show the summary "Potential new rules: 0" and an empty list; no new empty-state copy is required.
- Save is enabled only when the row has a category (display of `SelectedCategory != null`); Apply All disabled unless some row `IsApplicable`, and both disabled while busy, as today.
- Styling reuses existing classes (`finance-primary`) and the current colour literals; no new resource dictionaries.

## Test plan

Rewritten or updated (test lane):
- `tests/HomeCharts.Application.Tests/MainWindowViewModelRulesQueuePagingTests.cs`: rewritten as VM tests against `PotentialRulesViewModel` (rename file to `PotentialRulesViewModelTests.cs` via new file plus orchestrator `git rm` of the old, or overwrite in place). Keep the three behaviors: edit survives paging away and back, Apply All persists modified rows from two pages, CanExecute true when the modified row is on another page. Use `PotentialRulesViewModel.PageSize` instead of the hardcoded 120 copy. Update `Summary`/`PageInfo` assertions.
- `tests/HomeCharts.Application.Tests/Test1.cs:41` (batch use case counts): replaced by `ApplyPotentialRulesUseCase.SaveModifiedAsync` count tests; delete the batch test when the batch use case is removed.
- `Test1.cs:79` (row VM IsModified): replaced by `PotentialRuleDraft.IsModified` / `IsApplicable` matrix tests at Application level (description changed, category changed, both back to baseline, category null).
- `Test1.cs:1062`, `:1078` (Preview use case): update ctor (two new repositories) and assert on `RawDescription`; keep "returns rows with no rules" and "excludes matched rows".
- `MainWindowViewModelTrendBarScalingTests.cs:52,61,66` and the paging tests' factory: update ctor. Recommended, at test lane's discretion: one shared VM factory helper in `TestDoubles.cs` to stop duplicating the ~24-arg constructor in two files.

New tests:
- Domain (`tests/HomeCharts.Domain.Tests`): `DescriptionPrefixStripper`: longest prefix first, repeated stripping, case-insensitive, trims ' ', '-', ':', no prefixes, blank prefix ignored, everything stripped -> original returned. `ExpenseCategoryCatalog.SelectAssignable`: order follows OrderedNames, case-insensitive match, duplicates collapsed, unknown names skipped.
- Application, Preview: SuggestedPattern is prefix-stripped; SuggestedCategoryId = "None" when present, else first assignable, else first any, else null (four cases); RowKey deterministic across two runs and distinct for two rows with identical text on different lines; errors -> empty rows; rows matching an existing Exact, Regex and Contains rule are excluded (guardrail 1 evidence, no change to precedence).
- Application, Apply: SaveOne created rule has `MatchType.Contains`, `Priority 5`, trimmed pattern, name "Contains ..."; duplicate; blank -> InvalidPattern; null category -> CategoryMissing and no write. SaveModified: only applicable drafts saved, input order, same-batch repeat counts Duplicate, unmodified draft with category not saved, `ConsideredCount == 0` on nothing applicable.
- Guardrail 2: with a transaction carrying a manual override in the in-memory repositories, run `SaveModified`; assert the transaction's category and the override history are unchanged (rule creation does not re-apply rules, `ApplyPotentialRulesUseCase` has no transaction or override dependency).
- VM: page count/text for 130 rows, single save removes the row after refresh (row now matches a rule), status text for the four `PotentialRuleSaveOutcome` values, and D1 behaviour once decided.
- Not covered (no test project): AXAML layout, bindings. Frontend must run `dotnet build src/HomeCharts.App/HomeCharts.App.csproj` and report the manual check result in `risks`.

Tests to delete outright: only the batch use case test. Nothing else is redundant.

## Open decisions

- **D1. Unsaved edits when the list refreshes.** Today every refresh (save of another row, apply all, prefix change, apply rules, merge, import, Refresh Queue) rebuilds rows and drops unsaved description/category edits everywhere, not only for the saved row. Options: (a) keep today's behaviour (simple, matches history); (b) keep edits for rows whose `RowKey` still exists after refresh and reset only rows that vanished or whose suggested pattern/category baseline changed; (c) (b) only for refreshes triggered from inside the list (save, apply all, Refresh Queue) and reset on import and file change. Recommendation: (c). It fixes the worst case (edit ten rows, save one, lose nine) without carrying stale edits across a new file. Not blocking: frontend builds (a) with `RowKey` in place if unanswered.
- **D2. Cosmetic polish.** Optional display-only additions that add no capability: highlight modified rows (from `IsModified`), show the count on Apply All ("Apply All (N)"), disable Save when no category. Options: (a) none, exact visual parity; (b) all three. Recommendation: (b), low risk. Default if unanswered: (a) for highlight and count, and the Save-disabled state (already a display of an existing rule) is included.
- **D3 (informational, decided).** Paging vs continuous scroll: kept paging at 120 for the reasons in § Behavior decisions. If the human wants continuous scrolling instead, that is a UI virtualization change and a separate order.
