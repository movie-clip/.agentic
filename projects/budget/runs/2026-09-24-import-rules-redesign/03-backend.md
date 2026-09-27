REPORT 2026-09-24-import-rules-redesign/03
status:      DONE
verdict:     NONE

changed:
  - src/HomeCharts.Domain/Categorization/DescriptionPrefixStripper.cs — new; Strip(description, prefixes) moved verbatim from VM FormatDescriptionForDisplay algorithm
  - src/HomeCharts.Domain/Model/ExpenseCategoryCatalog.cs — new; OrderedNames (18 names, VM order) and SelectAssignable<T>
  - src/HomeCharts.Application/UseCases/PreviewPotentialRulesUseCase.cs — ctor gains ICategoryRepository and IPrefixFilterRepository; PotentialRuleRow extended (RowKey, RawDescription, SuggestedPattern, SuggestedCategoryId)
  - src/HomeCharts.Application/UseCases/ApplyPotentialRulesUseCase.cs — new; PotentialRuleDraft, PotentialRuleSaveOutcome, ApplyPotentialRulesResult, ApplyPotentialRulesUseCase (SaveOneAsync, SaveModifiedAsync)

verification:
  command:   dotnet build src/HomeCharts.Application/HomeCharts.Application.csproj
  result:    PASS
  detail:    Build succeeded. 0 Warning(s), 0 Error(s)

contract_notes:
  - PotentialRuleRow.Description is renamed RawDescription and the record gained RowKey, SuggestedPattern, SuggestedCategoryId. Every consumer (VM, tests at Test1.cs:1062/:1078) lags until updated.
  - PreviewPotentialRulesUseCase ctor now takes (IRuleRepository, ICategoryRepository, IPrefixFilterRepository, BankStatementParser). CompositionRoot.cs:35 and test factories must pass the two new repositories.
  - New ApplyPotentialRulesUseCase(CreateCategorizationRuleUseCase) with SaveOneAsync(PotentialRuleDraft) and SaveModifiedAsync(IReadOnlyCollection<PotentialRuleDraft>). Frontend wires it in CompositionRoot and consumes PotentialRuleSaveOutcome and ApplyPotentialRulesResult.
  - New Domain statics DescriptionPrefixStripper.Strip and ExpenseCategoryCatalog.OrderedNames/SelectAssignable. VM ExpenseCategoryOrder and FormatDescriptionForDisplay body should delegate to them.
  - CreateCategorizationRulesBatchUseCase and its item/result records are untouched and still present; the orchestrator git rm comes after frontend and test lanes drop references.

pack_corrections:
  - none

handoff:
  - RowKey format is LineNumber|yyyy-MM-dd|Amount (invariant culture)|RawDescription; identical across runs for the same file, unique per line.
  - Draft construction for a row VM: new PotentialRuleDraft(row.SuggestedPattern, row.SuggestedCategoryId, currentText, selectedCategory?.Id), or PotentialRuleDraft.FromRow(row).
  - Test coverage needed: Strip (longest prefix, repeat, case-insensitive, trim chars, blank prefix, all-stripped returns original); SelectAssignable (order, case, dedupe, unknown skipped).
  - Test coverage needed: Preview default-category four cases (None, first non-Uncategorized assignable, first assignable, first any, null when empty), RowKey determinism, errors give empty rows.
  - Test coverage needed: Apply SaveOne outcomes incl. null category writes nothing; SaveModified filters IsApplicable, ConsideredCount, same-batch repeat is Duplicate; rule stays Contains priority 5.
  - Bash heredocs failed with an unexpected-EOF parse error in this shell; files were written with the Write tool instead. No stray files were left.

skill_calls:
  - mattpocock-skills:diagnosing-bugs — not called, no bug fix in this order and no failed fix attempt

risks:
  - Preview default-category fallback "first category of any kind" uses repository GetAllAsync order, same as the VM's Categories order today (recon Q3), assuming the VM loads them via the same repository order.
  - SaveModifiedAsync counts a non-created, non-invalid outcome as Duplicate via the default switch arm; CategoryMissing cannot occur there because IsApplicable requires a category.
