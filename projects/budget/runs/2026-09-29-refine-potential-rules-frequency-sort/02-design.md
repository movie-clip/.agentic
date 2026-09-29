REPORT 2026-09-29-refine-potential-rules-frequency-sort/02
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only design pass, verification NONE

contract_notes:
  - PotentialRuleRow drops "= 0" on OccurrenceCount (PreviewPotentialRulesUseCase.cs:99); the positional 0 at :50 and the named arg at PotentialRulesUseCaseTests.cs:61 still compile, see § contract
  - PotentialRuleRowViewModel gains public string OccurrenceText (Presentation); MainWindow.axaml row and header grids gain a column bound to it, see § contract and § layout
  - Row ORDER changes for equal-count patterns: grouped by pattern, groups by first line; docs/PROJECT_GUIDE.md:30-33 still says "keep their original parse order" and goes stale, see § lanes (docs)
  - Contracts layer, migrations and PotentialRulesViewModel paging code are untouched; paging re-slices _allRows in preview order and adds no ordering, see § contract

pack_corrections:
  - none

handoff:
  - backend: edit only PreviewPotentialRulesUseCase.cs — ordering keys plus record default removal, see § contract
  - frontend: edit only PotentialRuleRowViewModel.cs and MainWindow.axaml; may run in parallel with backend because row.OccurrenceCount already exists, see § contract and § layout
  - test: runs after backend and frontend; owns every tests/** edit named in § lanes, including the [1,2,3,4] to [1,3,2,4] change and the Assert removal
  - docs: at close-out update docs/PROJECT_GUIDE.md tie-order sentence, the row-columns sentence, and add a RELEASE_NOTES entry
  - verification gates: dotnet build HomeCharts.sln; dotnet build src/HomeCharts.App/HomeCharts.App.csproj (XAML changed); dotnet test HomeCharts.sln --no-build

skill_calls:
  - mattpocock-skills:codebase-design — called, glossary and principles only; kept the sort inside PreviewPotentialRulesUseCase (deep interface) and added no first-line field to PotentialRuleRow

risks:
  - The new column narrows the Description column by about 66px in a 1.7* panel; no screenshot verification is possible in this pass, so the frontend lane should eyeball or state it was not run
  - Design chose always-show "×1"; if the human prefers hiding count 1, that is a view-model conditional and would be a follow-up decision, not a silent change
  - Recon did not open the PotentialRulesHarness rows; the test lane must not assume harness patterns are unique beyond what UniquePatternOf gives, so the "×N" test constructs its row directly
  - Docs (PROJECT_GUIDE.md, RELEASE_NOTES.md) went unread by recon; the stale sentence at PROJECT_GUIDE.md:30-33 was found here and is routed to docs

## Orchestrator brief
- Sort in PreviewPotentialRulesUseCase: OrderByDescending(OccurrenceCount), ThenBy(first LineNumber of the pattern), ThenBy(LineNumber). Explicit keys, no reliance on stable sort.
- First-appearance = min LineNumber over rows sharing SuggestedPattern (Ordinal); LineNumber is unique physical line, so the order is total and deterministic.
- PotentialRuleRow keeps its shape; only "= 0" is dropped. No first-line field added; positional 0 at :50 stays.
- Presentation: PotentialRuleRowViewModel.OccurrenceText (string) = "×" + count, InvariantCulture; ALWAYS shown, including "×1". No conditional, so no decision lives in Presentation.
- Layout: new column "Count" at index 1, both grids become "110,56,*,110,190,96"; cells shift to columns 2-5 in header and row template.
- Lanes: backend (1 file) and frontend (2 files) parallel; then test (2 test files); docs at close-out. Each owns nothing outside its files.
- Test lane owns: rename + [1,3,2,4], two new ordering tests, FromRow Assert removal (and its stale comment), VM "×N" tests.
- Sections: contract (ordering + shapes), layout (axaml), lanes (files, order, test ownership), decisions (do-not-redecide list), risks below the block.
- Nothing blocks dispatch. Guardrails 1-5 satisfied; categorization engine, Contracts, migrations untouched.

## contract

### Ordering rule (PreviewPotentialRulesUseCase.ExecuteAsync)
- Keys, in order: (1) OccurrenceCount descending; (2) FirstLine ascending, where FirstLine is the minimum LineNumber among potentialRows whose SuggestedPattern is ordinally equal; (3) LineNumber ascending.
- Key 3 keeps rows of one pattern in file order inside their group. Because LineNumber is the physical file line (BankStatementParser.cs:40, index + 1) and is unique per row, keys 2 and 3 make the order total: no two rows tie, so no reliance on LINQ stable-sort remains.
- Two different patterns can never share a FirstLine, so groups of equal count never interleave. A group is contiguous by construction: every row of the pattern carries the same (count, FirstLine) prefix.
- Compute count and first line in the one existing GroupBy(SuggestedPattern, StringComparer.Ordinal) at :54-56: build Dictionary<string, (int Count, int FirstLine)> using group.Count() and group.Min(row => row.LineNumber). Do not add a second pass or a second dictionary.
- Use OrderByDescending(...).ThenBy(...).ThenBy(...) over a per-row lookup of the dictionary; lambdas static where they capture nothing.
- The ordering is deliberately not lexical on the pattern. Determinism (guardrail 1 spirit) comes from file position only.
- Do not touch rule matching (CategorizationEngine.Match), normalisation, prefix stripping, or RowKey. The categorization engine is not touched at all, so guardrail 1 is unaffected.

### PotentialRuleRow shape
- Only change: `int OccurrenceCount = 0` becomes `int OccurrenceCount` (PreviewPotentialRulesUseCase.cs:99). All eight fields, names and order otherwise identical.
- No FirstLine or group-index field is added: FirstLine is a sort key internal to the use case, and exposing it would widen a seam that has no second consumer.
- The production construction at :42-50 keeps its positional trailing `0` (now a required argument, overwritten by `with { OccurrenceCount = ... }` at :59). Backend may leave it or name it `OccurrenceCount: 0`; either compiles and neither is a behaviour change. Prefer leaving it untouched to keep the diff minimal.
- The `with` copy at :59 is unaffected by removing the default.
- Nullability: OccurrenceCount is a non-nullable int always >= 1 on every row returned from ExecuteAsync. There is no trust or state enum: the value is a count, not an estimate.
- Count scope stays "within the current import file" (unchanged, decided in run 2026-09-27).

### Presentation surface
- New property on PotentialRuleRowViewModel: `public string OccurrenceText { get; }`, get-only, set in the constructor next to BookingDateText/AmountText (:21-22). Name and type follow the existing *Text convention (BookingDateText, AmountText).
- Value: `"×" + row.OccurrenceCount.ToString(CultureInfo.InvariantCulture)`, e.g. "×3", "×1". Use the C# escape `×` for the multiplication sign in source so file encoding cannot corrupt it. Add `using System.Globalization;`.
- Count 1 is SHOWN as "×1". Rationale: hiding it would be a conditional display decision in Presentation and would leave a visually empty cell in a column; always-show keeps the view model a pure formatter (guardrail 3).
- No raw int property is exposed: nothing in Presentation needs to compare or branch on the count, and adding one would invite exactly that.
- The formatting lives in PotentialRuleRowViewModel because it is display text, in the same place and style as the two existing formatted strings. The count itself (a decision) is computed only in the use case; the view model does no arithmetic and no sorting.
- PotentialRulesViewModel needs no change: it already enumerates preview.PotentialRows in order at :137 and appends to _allRows, and paging (:236-242) slices without re-ordering.

## layout

- Both grids (header at MainWindow.axaml:437, row template at :465) change from `ColumnDefinitions="110,*,110,190,96"` to `ColumnDefinitions="110,56,*,110,190,96"`; ColumnSpacing stays 10.
- New column index 1, between Date and Description, so the count sits next to the date and reads as the group's leading key.
- Header: new `<TextBlock Grid.Column="1" Text="Count" Foreground="#94A3B8" FontWeight="SemiBold" HorizontalAlignment="Center" VerticalAlignment="Center"/>` (same brush and weight as :438-442).
- Row cell: new `<TextBlock Grid.Column="1" Text="{Binding OccurrenceText}" Foreground="#CBD5E1" HorizontalAlignment="Center" VerticalAlignment="Center"/>` (primary cell text #CBD5E1 as at :466 and :475).
- Existing cells shift, header and row alike: Description/TextBox 1 -> 2; Amount 2 -> 3; Expense Category/ComboBox 3 -> 4; Action/Save button 4 -> 5. Date stays column 0 (no attribute).
- The row TextBlock for Date at :466 has no Grid.Column and stays so. Every shifted element needs its Grid.Column attribute edited; a missed one lands two controls in one cell and compiles silently.
- The row DataTemplate stays x:DataType="mvp:PotentialRuleRowViewModel", so the binding is compiled: a misspelt OccurrenceText fails at build, which is why the App-project build is mandatory.
- 56px holds "×999" at default font size; no wrapping property needed.

## lanes

Order: backend and frontend in parallel (no dependency: row.OccurrenceCount exists today and the frontend reads it); then test, which depends on both; docs at close-out. Integration reviews after the test lane.

### backend
- Files: src/HomeCharts.Application/UseCases/PreviewPotentialRulesUseCase.cs only.
- Do: implement § contract ordering; drop "= 0".
- Verify: `dotnet build HomeCharts.sln`. Do not edit tests; existing tie test will fail until the test lane lands, and that is expected, not a backend defect. Report it in `risks`.

### frontend
- Files: src/HomeCharts.Presentation/Mvp/PotentialRuleRowViewModel.cs and src/HomeCharts.App/MainWindow.axaml only.
- Do: add OccurrenceText; add the column and shift the cells per § layout.
- Verify: `dotnet build HomeCharts.sln` and `dotnet build src/HomeCharts.App/HomeCharts.App.csproj`.

### test
- Files: tests/HomeCharts.Application.Tests/PotentialRulesUseCaseTests.cs and tests/HomeCharts.Application.Tests/MainWindowViewModelRulesQueuePagingTests.cs only.
- Owns the rename and expectation change: `ExecuteAsync_PatternsWithEqualOccurrenceCounts_PreserveOriginalParseOrder` (PotentialRulesUseCaseTests.cs:234) is renamed to `ExecuteAsync_PatternsWithEqualOccurrenceCounts_StayGroupedInOrderOfFirstAppearance`; expected LineNumbers [1,2,3,4] becomes [1,3,2,4]; the comment at :238-239 and the failure message at :249 are rewritten to describe grouping by first appearance (they currently assert parse order and would become false).
- Owns the FromRow cleanup: delete the Assert on row.OccurrenceCount at :68 in FromRow_StartsAtBaselineAndUnmodified, and delete the now-stale comment at :59-60 that explains the explicit OccurrenceCount arg (the argument is required after the default is dropped; leaving `OccurrenceCount: 4` in the call is fine).
- New use-case tests, in PreviewPotentialRulesUseCaseSuggestionTests, reusing CreateUseCase and the Alpha/Beta line style:
  - Tie group order is by first appearance, not lexical: lines Beta, Alpha, Beta, Alpha (both count 2) expect LineNumbers [1,3,2,4] with Beta first. The renamed test alone cannot tell first-appearance from lexical order because Alpha is both first and alphabetically first.
  - Count dominates first appearance and a singleton stays last: lines S, A, B, A, B where S is a singleton expect LineNumbers [2,4,3,5,1].
- New view-model tests, in PotentialRulesViewModelTests (same file as :296): (a) extend or add beside Row_DefaultsToSuggestedNoneCategoryAndFormatsDateAndAmount an assertion that a singleton row has OccurrenceText "×1"; (b) a test that constructs a PotentialRuleRow with OccurrenceCount 3 directly and a PotentialRuleRowViewModel over it (public constructor; use harness categories or an empty category list) and asserts OccurrenceText "×3". (b) does not depend on harness row generation.
- Verify: `dotnet build HomeCharts.sln` then `dotnet test HomeCharts.sln --no-build`.

### docs (close-out, not a build dependency)
- docs/PROJECT_GUIDE.md:30-33: replace "Rows whose pattern count ties keep their original parse order" with ties staying grouped and ordered by where the pattern first appears in the file; add the count column ("×N") to the per-row description at :34-36.
- docs/RELEASE_NOTES.md: new dated entry at the top.

## decisions

- Property name is `OccurrenceText`, type string, get-only. Not `CountText`, not `OccurrenceCountText`, not an int.
- Glyph is U+00D7 written as `×` in C#; format is glyph immediately followed by the integer, no space, invariant culture.
- Count 1 is shown ("×1"). No hide logic anywhere.
- Column header text is "Count"; column width 56; column index 1; centred; #CBD5E1 cell and #94A3B8 header.
- First appearance means min LineNumber (physical file line), not list index in potentialRows. Equivalent today, but LineNumber is the stable, observable key the test asserts on.
- Final tie-break is LineNumber ascending, so no unordered tie can ever remain. Do not add pattern-lexical ordering.
- FirstLine is not added to PotentialRuleRow or any Contracts type.
- The literal 0 at PreviewPotentialRulesUseCase.cs:50 stays as the constructor placeholder; do not restructure the row construction.
- Nothing about the dashboard's OccurrenceCount (BuildDashboardSnapshotUseCase) is planned or touched.
