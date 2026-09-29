REPORT 2026-09-27-sort-potential-rules-by-frequency/02
status:      DONE
verdict:     NONE

changed:
  - src/HomeCharts.Application/UseCases/PreviewPotentialRulesUseCase.cs — added `OccurrenceCount` to `PotentialRuleRow`, computed per `SuggestedPattern` within the current parse batch, and sorted `PotentialRows` descending by that count (stable secondary order = original parse order).

verification:
  command:   dotnet build HomeCharts.sln
  result:    PASS
  detail:    Build succeeded. 0 Warning(s), 0 Error(s).

contract_notes:
  - `PotentialRuleRow` (src/HomeCharts.Application/UseCases/PreviewPotentialRulesUseCase.cs:91-99) gained a new `OccurrenceCount` field, defaulted to 0.
  - The default value on `OccurrenceCount` exists solely to keep the existing positional test constructor call at tests/HomeCharts.Application.Tests/PotentialRulesUseCaseTests.cs:59 compiling without a test-file edit, which is out of this order's scope.
  - `PotentialRulesViewModel`/`PotentialRuleRowViewModel` in HomeCharts.Presentation do not surface `OccurrenceCount` to the UI — a Presentation-lane change if the count itself (not just the resulting order) needs to be shown.
  - `docs/PROJECT_GUIDE.md` § "Rule Management" documents no sort order today (per recon § Docs) and now lags behind the shipped "most-repeated-first" default ordering.

pack_corrections:
  - none

handoff:
  - `PreviewPotentialRulesResult.PotentialRows` is now pre-sorted: highest `OccurrenceCount` first, ties broken by original parse/file order via a stable `OrderByDescending`.
  - `PotentialRulesViewModel.LoadAsync`/`ShowPage` already consume `PotentialRows` in return order with no sort call, so no Presentation change was needed or made — confirmed by reading the current file, unchanged from recon's description.
  - Test coverage to add (test lane): multiple unmatched rows sharing a `SuggestedPattern` should sort ahead of singletons.
  - Test coverage to add (test lane): ties (equal counts) should preserve original parse order.
  - The existing single-row test at tests/HomeCharts.Application.Tests/PotentialRulesUseCaseTests.cs:59 compiles only because `OccurrenceCount` defaults to 0 — worth an explicit assertion that the use case actually populates it, not just the constructor default.

skill_calls:
  - none

risks:
  - Gave `PotentialRuleRow.OccurrenceCount` a default value of `0` on the record's positional parameter so the existing test file's 7-arg constructor call keeps compiling under `dotnet build HomeCharts.sln`.
  - That default was chosen because editing tests/** is forbidden by this order's non_goals; it is a minimal, additive signature change and guardrail 5 (warnings-as-errors) still holds, but the test lane should confirm the default doesn't mask a case where the field should have been required.
