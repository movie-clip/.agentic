REPORT 2026-09-27-sort-potential-rules-by-frequency/04
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   dotnet build HomeCharts.sln && dotnet test HomeCharts.sln --no-build
  result:    PASS
  detail:    Build succeeded, 0 Warning(s)/0 Error(s). Tests: HomeCharts.Domain.Tests 17 passed, HomeCharts.Application.Tests 83 passed, HomeCharts.Infrastructure.Tests 11 passed — 111 total, 0 failed, 0 skipped. Independently re-run, not taken from either lane's report.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - PROJECT_GUIDE.md doc lag already OPEN in run.md from 02-backend; confirmed accurate, no new CR needed.

skill_calls:
  - mattpocock-skills:codebase-design — called before the reuse judgment below; confirmed via § Reuse check.

risks:
  - OccurrenceCount's `= 0` default is now dead code (both call sites pass it explicitly) — cosmetic, not a CR, see § Dead default.
  - Ledger's closed "within-file, not cross-import" scope decision confirmed consistent with shipped code — not reopened.

## Orchestrator brief

- Verdict: PASS, no change requests. Verified independently, not taken on the lanes' word.
- Ran `dotnet build HomeCharts.sln` and `dotnet test HomeCharts.sln --no-build` myself: build clean, 111/111 tests pass — matches both lanes' claims.
- Read `PreviewPotentialRulesUseCase.cs` directly: groups by `SuggestedPattern`, counts, `OrderByDescending(OccurrenceCount)` — .NET's sort is stable, so tie-break is correct with no extra code.
- `git diff --stat` (source only) confirms only the two in-scope files changed — no Presentation/App touch, no migration needed (guardrails 3, 4 clean).
- `mattpocock-skills:codebase-design` called for the reuse call: § Reuse check.
- One cosmetic, non-blocking note: § Dead default.
- Test coverage confirmed to assert on `ExecuteAsync`'s actual return values, not constructor defaults: § Coverage check.

## Reuse check

`GroupBy`/`OrderByDescending` over an in-scope collection is an established Application-layer idiom already used in `BuildDashboardSnapshotUseCase.cs` (multiple call sites) and `PreviewParsedCategoryExpensesUseCase.cs`. This use case's counting/sort reuses that pattern rather than introducing a new one — no reuse/consistency finding.

## Dead default

`PotentialRuleRow.OccurrenceCount`'s `= 0` default parameter (`PreviewPotentialRulesUseCase.cs:99`) is unreachable in practice: `ExecuteAsync:42` passes `0` explicitly, and the test's line-61 constructor call now passes `OccurrenceCount: 4` explicitly (added by the test lane so the line-59 test would stop relying on the default). Neither guardrail-violating nor tool-flagged (0 warnings on build) — noted for awareness, not a change request.

## Coverage check

Read `PotentialRulesUseCaseTests.cs` in full. Three new tests exercise `ExecuteAsync` directly and assert on the returned `PotentialRuleRow`s:

- `ExecuteAsync_SingleUnmatchedRow_OccurrenceCountIsOne` — proves population, closing backend's own risk note that the line-59 test alone couldn't prove it (that test exercises `PotentialRuleDraft.FromRow`, a different member).
- `ExecuteAsync_RowsSharingSuggestedPattern_SortAheadOfSingletonsWithCorrectOccurrenceCounts` — 3 identical `MERCADONA` lines (verbatim from `BankRecipes/2023.txt`) outrank a `STARBUCKS` singleton; asserts `OccurrenceCount == 3` on the leading group and `== 1` on the trailing singleton, proving both grouping and descending order together, not just one or the other.
- `ExecuteAsync_PatternsWithEqualOccurrenceCounts_PreserveOriginalParseOrder` — two patterns (`ALPHA`/`BETA`) each occurring twice, deliberately interleaved in the input file, assert the returned `LineNumber` sequence is exactly `[1,2,3,4]`. This is the observation that would catch a "group then re-emit" implementation (which would clump `ALPHA,ALPHA,BETA,BETA`) — it exercises the tie-break as the DoD names it, not merely that the code compiles.

Confirmed `DescriptionPrefixStripper.Strip` returns the description verbatim when no prefix filters are configured (`src/HomeCharts.Domain/Categorization/DescriptionPrefixStripper.cs:5-31`, empty-prefixes loop never executes) — this is what makes the grouping test's identical raw description lines a valid way to force a shared `SuggestedPattern` deterministically, confirming the test-engineer's stated assumption rather than taking it on trust.
