REPORT 2026-09-24-import-rules-redesign/07
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   dotnet build HomeCharts.sln ; dotnet test HomeCharts.sln --no-build ; dotnet build src/HomeCharts.App/HomeCharts.App.csproj
  result:    PASS
  detail:    Solution build 0 Warning(s) 0 Error(s). Tests: Domain 17 passed, Application 80 passed, Infrastructure 11 passed, 0 failed, 0 skipped (108 total). App-project build 0 Warning(s) 0 Error(s). CreateCategorizationRulesBatchUseCase.cs confirmed deleted (git status: D); grep for CreateCategorizationRulesBatch over src/** and tests/** returns zero matches.

contract_notes:
  - Backend's contract_notes (PreviewPotentialRulesUseCase ctor, PotentialRuleRow shape, ApplyPotentialRulesUseCase/PotentialRuleDraft) and frontend's consumption in PotentialRulesViewModel/PotentialRuleRowViewModel/CompositionRoot.cs agree field for field, verified by reading both source files directly rather than trusting the two reports alone.

pack_corrections:
  - none

handoff:
  - No change requests raised; run is clear to proceed to the docs lane per run.md's phase table.

skill_calls:
  - mattpocock-skills:codebase-design — called (SKILL.md glossary/principles only) before writing the reuse finding in § Findings — engineering.

risks:
  - decisions.md records D1 and D2 rulings only as literal text "option 1" each, with no numbered list preserved anywhere in the run; 02-design.md lists D1 as (a)/(b)/(c) and D2 as (a)/(b), so "option 1" reads most naturally as the first-listed option (a) each time.
  - Shipped behavior instead matches 02-design recommendations, not option (a): D1 preserves edits by RowKey on RefreshCommand/Save/Apply All (design (c)); D2 adds modified-row highlight and "Apply All (N)" (design (b)). Ask the human to confirm this matches what "option 1" meant.
  - 05-frontend's own risks note that DashboardUncategorizedRowViewModel and other dashboard models were not audited for further unreferenced types after removing the two row VMs; out of this run's scope, flagged for a future cleanup order, not a defect in this one.

## Orchestrator brief
- Verdict: PASS. All three verification commands green; DoD's five confirmations (one implementation, no business logic in Presentation/App, guardrails 1/2 unaffected, no schema/migration touched, no warning silenced) each independently checked against source, not just the lane reports.
- No change requests. `cr/` was not created.
- § Findings — engineering: detail behind each DoD bullet, contract alignment, and the reuse judgment (codebase-design call).
- Non-blocking: `risks` bullets 1-2 are a decisions.md ambiguity ("option 1" vs. lettered options in 02-design) the human should confirm before docs lane writes RELEASE_NOTES — not an engineering defect, so not a CR.
- Next: dispatch docs lane per run.md; no reviewer (no story).

## Findings — engineering

**Exactly one implementation.** Grep for every old symbol (`RulesQueue*`, `ImportedRuleTransactions`, `EditableRulesImportedTransactionViewModel`, `SavePotentialRuleCommand`, `SaveAllPotentialRulesCommand`, `GetDefaultPotentialRuleCategory`, `RulesImportedTransactionViewModel`, `RulesUnmatchedTransactionViewModel`) over `src/**` and `tests/**` returns zero matches. `CreateCategorizationRulesBatchUseCase.cs` is deleted and unreferenced. `MainWindow.axaml:422-503` is a single card bound to `PotentialRulesViewModel`, compiled bindings only, no `AncestorType=Window` reflection binding.

**No business logic in Presentation/App.** Read `PotentialRulesViewModel.cs` and `PotentialRuleRowViewModel.cs` in full: no string comparison, no default-category choice, no filtering decision — `SaveOneAsync`/`SaveModifiedAsync` are called with `Draft` objects built by simple field copies, `IsModified`/`IsApplicable` are forwarded properties reading `PotentialRuleDraft` in `HomeCharts.Application`. `MainWindowViewModel.FormatDescriptionForDisplay` (line 1298-1299) is now a one-line call to `DescriptionPrefixStripper.Strip`; `ReloadCategoriesAsync` (line 939) uses `ExpenseCategoryCatalog.SelectAssignable` instead of the old private array. `CompositionRoot.cs` diff confirms `ApplyPotentialRulesUseCase(createCategorizationRuleUseCase)` replaces the batch use case at the single wiring site.

**Guardrail 1 (deterministic categorization) and guardrail 2 (manual overrides).** `git status`/`git diff` show zero changes under `src/HomeCharts.Domain/Categorization` other than the new, unrelated `DescriptionPrefixStripper.cs` file — `CategorizationEngine.cs` is untouched. `PotentialRulesUseCaseTests.cs:343-375` (`SaveModifiedAsync_ManualOverrideOnTransaction_IsUnchanged`) is a real guardrail-2 test: it seeds a transaction with a manual override, runs `SaveModifiedAsync` with a draft that would match the transaction, then asserts the transaction's `CategoryId` and the override row are both unchanged — not merely that the code compiles.

**Guardrail 4 (migrations) and guardrail 5 (warnings).** `git status` on `src/HomeCharts.Infrastructure/Persistence/Sqlite/Migrations` shows no changes. All three verification builds report 0 warnings; grep for `pragma warning disable`, `SuppressMessage`, `NoWarn` across the touched source projects returns nothing.

**Coverage adequacy.** `PotentialRulesUseCaseTests.cs` and `PotentialRulesDomainTests.cs` test the contract, not the implementation: `PotentialRuleDraft.IsModified`/`IsApplicable` matrix, `RowKey` determinism, the four-case default-category chooser, `DescriptionPrefixStripper` (longest-prefix, repeat, case-insensitive, trim chars, blank prefix, all-stripped), `ExpenseCategoryCatalog.SelectAssignable` ordering/dedupe. The VM-level tests (rewritten `MainWindowViewModelRulesQueuePagingTests.cs`) cover D1's edit-survival semantics (edit two rows, save one, other survives; `RefreshAsync(content)` resets) and paging/Apply-All across pages. Each of these would fail if the underlying requirement regressed, not just if the code were refactored differently.

**Reuse judgment (codebase-design).** `ApplyPotentialRulesUseCase` wraps `CreateCategorizationRuleUseCase` as the single rule-creation seam — deleting it would reintroduce rule-creation logic at each caller, so it earns its keep rather than being a pass-through. `DescriptionPrefixStripper` and `ExpenseCategoryCatalog` are each a single Domain-level implementation with one seam; Presentation forwards (`FormatDescriptionForDisplay`, `ReloadCategoriesAsync`, row `Draft`/`IsModified`) rather than recomputing. No parallel/duplicate implementation found.
