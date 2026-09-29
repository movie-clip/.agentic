REPORT 2026-09-29-refine-potential-rules-frequency-sort/03
status:      DONE
verdict:     NONE

changed:
  - budget/src/HomeCharts.Application/UseCases/PreviewPotentialRulesUseCase.cs — order by OccurrenceCount desc, pattern first LineNumber asc, LineNumber asc; drop "= 0" on OccurrenceCount

verification:
  command:   dotnet build HomeCharts.sln && dotnet test HomeCharts.sln --no-build
  result:    PASS
  detail:    build 0 warnings 0 errors; tests Domain 17/17, Infrastructure 11/11, Application 82 of 83 passed, the one failure being the expected ExecuteAsync_PatternsWithEqualOccurrenceCounts_PreserveOriginalParseOrder

contract_notes:
  - PotentialRuleRow.OccurrenceCount is now a required constructor parameter; the positional 0 at PreviewPotentialRulesUseCase.cs:50 and named arg in PotentialRulesUseCaseTests.cs:61 still compile
  - Row order changes for equal-count patterns (grouped by pattern, groups by first line); docs/PROJECT_GUIDE.md:30-33 now stale, docs lane at close-out

pack_corrections:
  - none

handoff:
  - test lane: ExecuteAsync_PatternsWithEqualOccurrenceCounts_PreserveOriginalParseOrder fails now (expects [1,2,3,4], gets [1,3,2,4]); rename and update per 02-design § lanes, not edited here
  - test lane: implementation is one GroupBy into Dictionary<string,(int Count,int FirstLine)> then OrderByDescending(Count).ThenBy(FirstLine).ThenBy(LineNumber); FirstLine is internal, no new field on PotentialRuleRow
  - test lane: the FromRow_StartsAtBaselineAndUnmodified Assert on OccurrenceCount is untouched and still passes today; removal is still owed per design

skill_calls:
  - none

risks:
  - The ThenBy(FirstLine) lambda captures the patternStats dictionary so it is not static; design said static where nothing is captured, so this follows it
  - Application.Tests reports 1 failure by design of the user's requested behaviour change; not a backend defect
