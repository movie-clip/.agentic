REPORT 2026-09-27-sort-potential-rules-by-frequency/03
status:      DONE
verdict:     NONE

changed:
  - tests/HomeCharts.Application.Tests/PotentialRulesUseCaseTests.cs — added coverage for OccurrenceCount population and the most-repeated-first sort, plus its stable tie-break; updated the line-59 test to stop relying on the field's default.

verification:
  command:   dotnet build HomeCharts.sln && dotnet test HomeCharts.sln --no-build
  result:    PASS
  detail:    Build succeeded, 0 Warning(s)/0 Error(s). Tests: HomeCharts.Domain.Tests 17 passed, HomeCharts.Application.Tests 83 passed, HomeCharts.Infrastructure.Tests 11 passed — 111 total, 0 failed, 0 skipped.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - New test `ExecuteAsync_RowsSharingSuggestedPattern_SortAheadOfSingletonsWithCorrectOccurrenceCounts` (PotentialRulesUseCaseTests.cs) covers the grouping/sort DoD item: 3 identical-description rows outrank a 1-off singleton, with OccurrenceCount asserted (3 vs 1) on the returned rows, not the constructor default.
  - New test `ExecuteAsync_PatternsWithEqualOccurrenceCounts_PreserveOriginalParseOrder` covers the tie-break DoD item: two patterns each occurring twice, interleaved in the file, assert `LineNumber` sequence `[1,2,3,4]` is preserved through the sort.
  - New test `ExecuteAsync_SingleUnmatchedRow_OccurrenceCountIsOne` gives the use case's OccurrenceCount population an explicit, direct assertion (the substantive gap behind backend-engineer's risk note) alongside the existing single-row suggestion tests.
  - `FromRow_StartsAtBaselineAndUnmodified` (line 59) now passes `OccurrenceCount: 4` explicitly to the `PotentialRuleRow` constructor instead of relying on the record's default, and asserts `row.OccurrenceCount == 4` directly — it no longer masks the field behind an unexercised default.
  - That line-59 test exercises `PotentialRuleDraft.FromRow`, not `ExecuteAsync`, so it cannot itself prove use-case population; that proof lives in the three new tests above — see § Risks for why.
  - No new shared fixture was needed — all new tests reuse the existing `TestRepositories` fake and follow the existing `CreateUseCase`/`OpenAiLine`-style constant pattern already in this file.
  - Realistic `BankRecipes`-style rows were used for the grouping test (verbatim MERCADONA/STARBUCKS lines pulled from `BankRecipes/2023.txt`); the tie-break test uses two clearly-synthetic ALPHA/BETA lines since the point there is the interleaving pattern, not realism of the merchant text.

skill_calls:
  - mattpocock-skills:tdd — not called, no mocking-vs-real-dependency or test/production coupling tradeoff arose; all new tests reuse the existing `TestRepositories` in-memory fake and `BankStatementParser` real instance already established by the surrounding tests in this file.

risks:
  - Confirmed via `DescriptionPrefixStripper.Strip` (src/HomeCharts.Domain/Categorization/DescriptionPrefixStripper.cs) that with no prefix filters configured, `SuggestedPattern` equals the raw description verbatim — this is what lets the grouping test use identical `BankRecipes` description lines to force a shared pattern deterministically, rather than needing prefix-filter setup.
  - The DoD's line-59-test bullet is only partially satisfiable by editing that test itself: `FromRow_StartsAtBaselineAndUnmodified` exercises `PotentialRuleDraft.FromRow`, not `PreviewPotentialRulesUseCase.ExecuteAsync`, so it was never going to be able to prove the use case populates the field.
  - I made the line-59 test stop relying on the default (explicit value + assertion) and put the actual "use case populates OccurrenceCount" proof in a new, separate `ExecuteAsync`-based test — that is what 02-backend.md's risk note was actually asking to be closed.
