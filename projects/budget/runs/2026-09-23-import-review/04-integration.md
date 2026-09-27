REPORT 2026-09-23-import-review/04
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   dotnet build HomeCharts.sln && dotnet test HomeCharts.sln --no-build && dotnet build src/HomeCharts.App/HomeCharts.App.csproj
  result:    PASS
  detail:    dotnet build HomeCharts.sln: 0 Warning(s), 0 Error(s). dotnet test HomeCharts.sln --no-build: Domain.Tests 5/5, Application.Tests 40/40, Infrastructure.Tests 11/11 — 56/56 passed, 0 failed, 0 skipped. dotnet build src/HomeCharts.App/HomeCharts.App.csproj: 0 Warning(s), 0 Error(s).

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

risks:
  - EditableRulesImportedTransactionViewModel now subscribes `PropertyChanged += OnImportedRuleTransactionChanged` once at construction (MainWindowViewModel.cs:1317), not once per page-render as before — same pattern, called less often.
  - Traced that subscription for a leak: old instances become unreachable once _rulesQueueRows/ImportedRuleTransactions are cleared on the next import, so they are collectible normally — not a leak.
  - Finding 1 from 01-recon.md (whole-queue replace across sequential imports) remains unfixed, matching this run's explicit non_goal — not a regression, just confirming scope was honored.

## Orchestrator brief
- Verdict: PASS. No change requests.
- Verified directly against the diff (`git diff -- src/HomeCharts.Presentation/Mvp/MainWindowViewModel.cs`): both 01-recon.md Finding 2 bugs are closed. `_rulesQueueRows` now holds the same `EditableRulesImportedTransactionViewModel` instances across page renders (built once in `RefreshRulesQueueAsync`, reused by `RefreshRulesQueuePage`) instead of being rebuilt per page, so edit state (`SelectedCategory`/`IsModified`) survives Prev/Next. `SaveAllPotentialRulesAsync` and `SaveAllPotentialRulesCommand`'s `CanExecute` both now read `_rulesQueueRows` (the full queue) instead of `ImportedRuleTransactions` (the displayed page only) — see § Contract/design alignment.
- Guardrail 2 (manual overrides) and guardrail 3 (no business logic in Presentation/App): both hold — see § Guardrail checks. The diff touches only display/paging bookkeeping; the actual rule-creation decision still routes through `_createCategorizationRulesBatchUseCase`/`_createCategorizationRuleUseCase` unchanged.
- Test coverage traced by hand against pre-fix behavior (not just "green") — see § Test coverage trace. All three new tests would fail on the pre-fix code for the reason stated.
- Mechanical gates: all three commands run individually, all PASS — see verification block above.
- Sections below: § Contract/design alignment, § Guardrail checks, § Reuse and consistency, § Test coverage trace.

## Contract/design alignment

No `Contracts` interface changed (both lanes reported `contract_notes: none`, confirmed — the diff is entirely within `HomeCharts.Presentation`, no `Contracts`/`Application`/`Domain`/`Infrastructure` files touched). There is no cross-lane shape to misalign here; this was a single-lane (frontend) fix plus a same-run test lane, not a backend/frontend contract change. `02-frontend.md`'s `handoff` bullets describing what the test lane should cover were followed exactly by `03-test.md`'s three test methods, one per bullet.

## Guardrail checks

- **Guardrail 2 (manual overrides never silently overwritten).** Not implicated — the "Potential New Rules" queue creates *new* categorization rules from previously-unmatched rows via `CreateCategorizationRulesBatchUseCase`/`CreateCategorizationRuleUseCase`; it has no path through `ManualRecategorizationUseCase` or any override-history table. `git diff` confirms nothing outside `MainWindowViewModel.cs`'s rules-queue methods (constructor wiring, `SaveAllPotentialRulesAsync`, `RefreshRulesQueueAsync`, `RefreshRulesQueuePage`) changed. Holds.
- **Guardrail 3 (no business logic in App/Presentation).** Spot-checked every touched method. `RefreshRulesQueueAsync` now constructs `EditableRulesImportedTransactionViewModel` once per row (moved from `RefreshRulesQueuePage`, not new) — this calls `FormatDescriptionForDisplay` (a prefix-stripping display formatter, pre-existing, unchanged) and `GetDefaultPotentialRuleCategory` (pre-existing, unchanged, pre-selects a default category for editing, not a categorization decision — nothing is persisted until the user explicitly saves). `SaveAllPotentialRulesAsync` still delegates the actual rule creation to `_createCategorizationRulesBatchUseCase.ExecuteAsync`; the view model only filters/maps `IsModified` rows into the use case's input shape (`CreateCategorizationRulesBatchItem`), which is dispatch, not decision. Holds.

## Reuse and consistency

The fix does not introduce a new pattern: `EditableRulesImportedTransactionViewModel` already existed (`TransactionsModels.cs:52-97`) and is reused unchanged; the fix's only structural move is *where* instances are constructed (once, in `RefreshRulesQueueAsync`) versus *where* they're read (`RefreshRulesQueuePage`, `SaveAllPotentialRulesAsync`, the `CanExecute` predicate) — the minimal change that closes both bugs, not a rewrite. The test file follows the existing `MainWindowViewModelTrendBarScalingTests.cs` precedent verbatim (same constructor-wiring, same in-memory fakes, same use-case-side-effect assertion style instead of mocks) — confirmed by reading both files; not an invented pattern. `tests/HomeCharts.Application.Tests/HomeCharts.Application.Tests.csproj:21` does carry a `ProjectReference` to `HomeCharts.Presentation`, confirming the test lane's claim that this cross-project test placement is an established, not ad hoc, seam.

## Test coverage trace

Traced each of the three new `[TestMethod]`s against pre-fix `MainWindowViewModel.cs` (where `RefreshRulesQueuePage` rebuilt fresh, edit-state-less view models from raw `PotentialRuleRow` on every page render, and both `SaveAllPotentialRulesAsync` and its `CanExecute` read only `ImportedRuleTransactions`, the displayed page):

- `RulesQueuePaging_EditOnDisplayedPage_SurvivesNavigatingAwayAndBack` — pre-fix, paging back to page 1 would reconstruct a fresh, unmodified view model for the same logical row, so `rowAfterRoundTrip.SelectedCategory` would be the default category, not `groceryCategory`. Would fail pre-fix.
- `SaveAllPotentialRulesAsync_ModifiedRowsOnMultiplePages_AreAllPersistedAsRules` — pre-fix, `SaveAllPotentialRulesAsync` reads only the page displayed at click time (page 2); page 1's edit lives on a discarded object never enumerated. `createdPatterns.Contains(page1Description)` would fail pre-fix.
- `SaveAllPotentialRulesCommand_CanExecute_TrueForModifiedRowOnAnotherPage` — pre-fix, `CanExecute` reads `ImportedRuleTransactions`, which after navigating to page 2 holds only page 2's freshly-built, unmodified rows. Would return `false`, failing the assertion pre-fix.

All three exercise the actual fixed code paths (`RefreshRulesQueuePage`, `SaveAllPotentialRulesAsync`, the `SaveAllPotentialRulesCommand` `CanExecute` delegate) through public API (`NextRulesQueuePageCommand`, `PreviousRulesQueuePageCommand`, `SaveAllPotentialRulesCommand`), not the private backing fields directly — coverage of behavior, not implementation.
