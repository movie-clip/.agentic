REPORT 2026-09-24-import-rules-redesign/06
status:      DONE
verdict:     NONE

changed:
  - tests/HomeCharts.Application.Tests/MainWindowViewModelRulesQueuePagingTests.cs — overwritten in place; now PotentialRulesViewModelTests (paging, Apply All, D1, ApplyAllText, statuses, errors) plus PotentialRulesHarness
  - tests/HomeCharts.Application.Tests/PotentialRulesUseCaseTests.cs — new; PotentialRuleDraft matrix, Preview suggestions and RowKey, Apply use case, manual-override guardrail test
  - tests/HomeCharts.Domain.Tests/PotentialRulesDomainTests.cs — new; DescriptionPrefixStripper and ExpenseCategoryCatalog tests
  - tests/HomeCharts.Application.Tests/Test1.cs — removed batch use case and row VM tests; Preview tests use the new ctor and RawDescription
  - tests/HomeCharts.Application.Tests/TestDoubles.cs — added TestRepositories and TestViewModelFactory (single MainWindowViewModel ctor call)
  - tests/HomeCharts.Application.Tests/MainWindowViewModelTrendBarScalingTests.cs — uses TestViewModelFactory instead of inline ctor

verification:
  command:   dotnet build HomeCharts.sln ; dotnet test HomeCharts.sln --no-build
  result:    PASS
  detail:    Build 0 warnings 0 errors. Domain 17 passed, Application 80 passed, Infrastructure 11 passed; 0 failed, 0 skipped. Application project re-run 3 times, stable. Debug only, Release not run.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - No tests/** file references CreateCategorizationRulesBatchUseCase or its records; orchestrator can git rm src/HomeCharts.Application/UseCases/CreateCategorizationRulesBatchUseCase.cs and rebuild
  - The old paging file was overwritten in place, so no orphan file; its filename is now stale for class PotentialRulesViewModelTests, optional: git mv it to PotentialRulesViewModelTests.cs
  - New shared helpers in TestDoubles.cs: TestRepositories (all in-memory repos) and TestViewModelFactory.Create(repos) for the MainWindowViewModel ctor
  - New PotentialRulesHarness (in the paging test file) builds PotentialRulesViewModel with a controllable host; LastRun awaits fire-and-forget commands that go through RunBusyAsync
  - Tests using RefreshCommand poll with PotentialRulesHarness.WaitUntilAsync because that command is not routed through RunBusyAsync and cannot be awaited
  - Covered per 02-design Test plan: D-1 (edit two rows, save one, other survives; RefreshAsync(content) and changed file reset), Apply All (N), Contains priority 5 rules, manual override unchanged after SaveModified
  - Not covered: CategoryMissing status text via the VM, since row Save is disabled without a category; covered at use-case level only

skill_calls:
  - mattpocock-skills:tdd — not called, real in-memory repositories used throughout so no mock-versus-real tradeoff arose
  - mattpocock-skills:diagnosing-bugs — not called, no test failed or flaked

risks:
  - Release configuration (CI gate) was not run, only Debug
  - PotentialRulesViewModel.LoadAsync reads the file only when content is null; edits-kept tests depend on the host path staying a real file until the test ends, which the harness guarantees
  - VM tests rely on the row-instance identity changing to detect refresh completion; if a future refactor reuses row instances, WaitUntilAsync would time out
  - Default category name lookups rely on ExpenseCategoryCatalog naming; harness seeds only None, Grocery and Car
