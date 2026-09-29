REPORT 2026-09-29-refine-potential-rules-frequency-sort/04
status:      PARTIAL
verdict:     NONE

changed:
  - budget/src/HomeCharts.Presentation/Mvp/PotentialRuleRowViewModel.cs — add using System.Globalization; add get-only OccurrenceText = "×" + OccurrenceCount (InvariantCulture), set in ctor after AmountText
  - budget/src/HomeCharts.App/MainWindow.axaml — header and row grids now "110,56,*,110,190,96"; new Count header and OccurrenceText cell at column 1; Description/Amount/Category/Action cells shifted to columns 2-5

verification:
  command:   dotnet build HomeCharts.sln && dotnet build src/HomeCharts.App/HomeCharts.App.csproj && dotnet test HomeCharts.sln --no-build
  result:    FAIL
  detail:    both builds 0 warnings 0 errors; tests Domain 17/17, Infrastructure 11/11, Application 82 of 83, the one failure being ExecuteAsync_PatternsWithEqualOccurrenceCounts_PreserveOriginalParseOrder, expected from backend lane and owned by test lane

contract_notes:
  - PotentialRuleRowViewModel gains public string OccurrenceText; test lane asserts "×1" and "×3" against it, see § Edits as shipped
  - docs/PROJECT_GUIDE.md per-row description (:34-36) now lacks the Count column; docs lane owns it at close-out

pack_corrections:
  - none

handoff:
  - test lane: OccurrenceText for OccurrenceCount 3 is "×3" (U+00D7 immediately followed by the integer, no space); construct PotentialRuleRow directly per 02-design § lanes
  - test lane: the failing test ExecuteAsync_PatternsWithEqualOccurrenceCounts_PreserveOriginalParseOrder is the sole red and clears when renamed with expectation [1,3,2,4] per 02-design § lanes

skill_calls:
  - mattpocock-skills:diagnosing-bugs — not called, no bug and no failed fix attempt

risks:
  - verification is FAIL only because of the one pre-declared test failure from the backend ordering change; both DoD builds passed, so treat status PARTIAL as a verification-wording matter, not a frontend defect
  - Layout was not visually checked and the app was not launched; the Description column narrows by about 66px (56 + 10 spacing) in a 1.7* panel, so eyeball it when the app is next run
  - The two builds finished in 2.29s and 0.75s, so they were likely incremental; the compiled OccurrenceText binding is proven only insofar as MSBuild compiled MainWindow.axaml in the first build
  - Both edits followed 02-design § contract and § layout exactly; no deviation from the design

## Orchestrator brief
- OccurrenceText added to PotentialRuleRowViewModel; Count column added at index 1 in the header and row grids of MainWindow.axaml, per 02-design.
- Both DoD builds pass with 0 warnings; the only red test is the pre-declared backend-driven tie-order test for the test lane.
- Layout not visually checked. Section: Edits as shipped lists the final column map.

## Edits as shipped

- PotentialRuleRowViewModel.cs: OccurrenceText declared beside AmountText, assigned in the constructor beside AmountText; no conditional, no arithmetic, so "×1" is shown (D-1).
- MainWindow.axaml header grid: Date (col 0, no attribute), Count (1, centred, #94A3B8 SemiBold), Description / Match String (2), Amount (3), Expense Category (4), Action (5).
- MainWindow.axaml row grid: Date TextBlock (0, no attribute), OccurrenceText TextBlock (1, centred, #CBD5E1), TextBox (2), Amount TextBlock (3), ComboBox (4), Save Button (5).
- Every previously attributed Grid.Column was incremented by one in both grids; no two controls share a column.
