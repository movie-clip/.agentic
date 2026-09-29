REPORT 2026-09-29-refine-potential-rules-frequency-sort/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only recon, verification NONE

contract_notes:
  - PotentialRuleRowViewModel (Presentation) must gain a new property for OccurrenceCount; it currently discards it, see § Path to the Import screen
  - Removing "= 0" default on PotentialRuleRow.OccurrenceCount touches only one production call site and one test call site, see § Constructor call sites

pack_corrections:
  - none

handoff:
  - Current sort is OrderByDescending on OccurrenceCount only at PreviewPotentialRulesUseCase.cs:58-61; the tie order relies on LINQ stable sort over parse order, see § Current sort
  - Every row already carries LineNumber (record param 2, populated from row.LineNumber at :44); ties can use min LineNumber per SuggestedPattern group, see § Current sort
  - PotentialRuleRowViewModel ctor (PotentialRuleRowViewModel.cs:14-33) reads row fields but never row.OccurrenceCount; need a new property there, see § Path to the Import screen
  - Row DataTemplate is MainWindow.axaml:449-496, Grid ColumnDefinitions="110,*,110,190,96", header grid duplicated at :437 with same widths; a new column must be added in both, see § Path to the Import screen
  - Presentation convention is pre-formatted string properties (BookingDateText, AmountText); no converter exists, see § Formatting conventions
  - Only two PotentialRuleRow constructions exist: PreviewPotentialRulesUseCase.cs:42-50 and PotentialRulesUseCaseTests.cs:61, see § Constructor call sites
  - Presentation row tests live in Application.Tests, not a Presentation test project, see § Tests

skill_calls:
  - none

risks:
  - Grep was limited to *.cs and *.axaml under src and tests; other file types (e.g. docs) referencing the row layout were not searched
  - Only PotentialRulesViewModel lines 100-175 were read; paging/ShowPage code (which re-slices _allRows) was not read for any ordering side effects
  - Did not open the harness (PotentialRulesHarness) in MainWindowViewModelRulesQueuePagingTests.cs beyond the cited asserts, so its generated row lines and whether they share patterns is unverified

## Orchestrator brief
- Current sort: single OrderByDescending(OccurrenceCount) at PreviewPotentialRulesUseCase.cs:58-61; ties depend on stable LINQ order (parse order).
- Rows already carry LineNumber (PotentialRuleRow param 2), so "first line where pattern appears" is computable from data in hand.
- OccurrenceCount stops at PotentialRuleRow: PotentialRuleRowViewModel ignores it; no Presentation property exists.
- Axaml row template is MainWindow.axaml:449-496 (5 columns "110,*,110,190,96"); header grid at :437 repeats the same widths.
- No converter exists; convention is pre-formatted *Text string properties; one precedent for count wording: DashboardRecurringExpenseViewModel.InsightText and axaml StringFormat '{}{0} transactions' at :520.
- Constructor call sites of PotentialRuleRow: exactly 2 (use case :42, test :61). Test already passes OccurrenceCount explicitly.
- Tests: PotentialRulesUseCaseTests.cs (use case, incl. tie-order test at :234) and MainWindowViewModelRulesQueuePagingTests.cs (VM row test at :296); no OccurrenceCount assertion at VM level.
- Existing tie test (:234-250) asserts parse order 1,2,3,4 for interleaved equal-count patterns; a count-then-first-appearance tie order would change that expected result.
- Sections below: Current sort; Path to the Import screen; Formatting conventions; Constructor call sites; Tests.
- No blockers; no contradiction with the order premise.

## Current sort
- Rows built in the loop at PreviewPotentialRulesUseCase.cs:36-52 with OccurrenceCount placeholder 0 (:50), in parse order.
- Counts computed by GroupBy(SuggestedPattern, Ordinal) at :54-56 (Dictionary pattern -> count).
- Sort at :58-61: Select(row with { OccurrenceCount = counts[pattern] }).OrderByDescending(OccurrenceCount).ToList(); no ThenBy, so ties fall to LINQ's documented stable order = parse order.
- LineNumber: PotentialRuleRow record param 2 (:93), set from row.LineNumber at :44 and also embedded in RowKey via BuildRowKey (:43, :66-71). So a per-pattern minimum LineNumber is derivable from potentialRows.
- Pattern equality is ordinal on SuggestedPattern (prefix-stripped description), :55.

## Path to the Import screen
- PotentialRulesViewModel.RefreshAsync calls _previewUseCase.ExecuteAsync at PotentialRulesViewModel.cs:123 and iterates preview.PotentialRows in that order (:137).
- Each row becomes `new PotentialRuleRowViewModel(row, _categories, SaveRowAsync, _host.GetIsBusy)` at PotentialRulesViewModel.cs:139, appended to _allRows (:147); Rows (ObservableCollection, :56) is the paged slice.
- PotentialRuleRowViewModel.cs:14-33 copies RowKey, BookingDateText (:21), AmountText (:22), SuggestedPattern, SuggestedCategoryId; row.OccurrenceCount is NOT read anywhere; the VM has no count property.
- Other VM members: RowKey, BookingDateText, AmountText, Categories, SaveCommand, Description, SelectedCategory, Draft, IsModified (:35-69).
- Axaml: list container Border at MainWindow.axaml:422 (DataContext PotentialRules); header Grid at :437 with ColumnDefinitions="110,*,110,190,96" and headers Date / Description / Match String / Amount / Expense Category / Action at :438-442 (columns 0-4).
- Row DataTemplate x:DataType="mvp:PotentialRuleRowViewModel" at :449; row Border :450-456; inner Grid at :465 with the same ColumnDefinitions="110,*,110,190,96", ColumnSpacing=10.
- Row cells: col0 TextBlock BookingDateText (:466); col1 TextBox bound to Description (:467-474); col2 TextBlock AmountText right-aligned (:475); col3 ComboBox of Categories (:476-486); col4 Save Button (:487-493).
- Row ItemsControl is at :447 inside a ScrollViewer (:446); ItemsSource="{Binding Rows}".
- Header text for the description column reads "Description / Match String".

## Formatting conventions
- Presentation uses pre-formatted read-only string properties, named *Text: PotentialRuleRowViewModel.BookingDateText/AmountText (:21-22), LedgerRowViewModel.cs:11-12, TransactionsModels.cs:27-33, DashboardModels.cs.
- Count wording precedent in code: DashboardModels.cs:116 `InsightText => $"{Occurrences} hits across {DistinctMonths} months"`.
- Count wording precedent in axaml: MainWindow.axaml:520 `Text="{Binding Transactions, StringFormat='{}{0} transactions'}"` (int bound directly with StringFormat, right-aligned, Foreground #94A3B8).
- Summary strings in PotentialRulesViewModel: `$"Potential new rules: {_allRows.Count}"` (:153).
- No IValueConverter found under src (Grep for Converter returned no hits in App/Presentation).
- Secondary/muted text colour in this panel: #94A3B8 (headers :438-442, Summary :426); primary cell text #CBD5E1 (:466, :475).

## Constructor call sites
- Production: PreviewPotentialRulesUseCase.cs:42-50, positional, passes literal 0 for OccurrenceCount as 8th arg.
- Test: PotentialRulesUseCaseTests.cs:61, passes OccurrenceCount: 4 by name, so it compiles with or without the default.
- Record declaration with default: PreviewPotentialRulesUseCase.cs:91-99 (`int OccurrenceCount = 0`).
- Other consumer (not a constructor): ApplyPotentialRulesUseCase.cs:9 PotentialRuleDraft.FromRow(PotentialRuleRow) reads the row but not OccurrenceCount.
- `with { OccurrenceCount = ... }` copy at PreviewPotentialRulesUseCase.cs:59 also relies on the property being settable via with.

## Tests
- Use-case tests: PotentialRulesUseCaseTests.cs, class PreviewPotentialRulesUseCaseSuggestionTests: OccurrenceCount singleton :204-209; sort-ahead + counts :212-231; tie-order test :234-250 asserting LineNumbers 1,2,3,4 for interleaved Alpha/Beta (Alpha at lines 1,3; Beta at 2,4) with equal count 2.
- Note: the :234 test's expected order [1,2,3,4] is parse order, which would differ from a first-appearance grouping (Alpha 1,3 then Beta 2,4) - it encodes the current behaviour.
- PotentialRulesUseCaseTests.cs:56-69 FromRow test passes OccurrenceCount: 4 explicitly.
- Presentation-level: tests\HomeCharts.Application.Tests\MainWindowViewModelRulesQueuePagingTests.cs, class PotentialRulesViewModelTests, with PotentialRulesHarness; row format test Row_DefaultsToSuggestedNoneCategoryAndFormatsDateAndAmount at :296-305 asserts BookingDateText and AmountText; helper UniquePatternOf at :455.
- No test asserts any OccurrenceCount value at the view-model level; none exists for the axaml.
- No separate Presentation test project exists; only Domain/Application/Infrastructure test projects (per CLAUDE.md).
