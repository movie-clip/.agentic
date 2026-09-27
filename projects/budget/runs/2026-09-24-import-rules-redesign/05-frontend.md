REPORT 2026-09-24-import-rules-redesign/05
status:      DONE
verdict:     NONE

changed:
  - src/HomeCharts.Presentation/Mvp/TransactionsModels.cs — deleted RulesUnmatchedTransactionViewModel and RulesImportedTransactionViewModel records

verification:
  command:   dotnet build src/HomeCharts.Presentation/HomeCharts.Presentation.csproj ; dotnet build src/HomeCharts.App/HomeCharts.App.csproj
  result:    PASS
  detail:    Both builds succeeded, 0 warnings, 0 errors (warnings-as-errors project settings untouched)

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - tests/HomeCharts.Application.Tests/Test1.cs:79 and :83 reference EditableRulesImportedTransactionViewModel (already removed by order 04, not by this order); test lane must rewrite or delete
  - tests/HomeCharts.Application.Tests/MainWindowViewModelRulesQueuePagingTests.cs uses ImportedRuleTransactions, RulesQueuePageInfo, RulesQueueSummary, SaveAllPotentialRulesCommand, NextRulesQueuePageCommand (lines 30-184); test lane must rewrite against PotentialRulesViewModel
  - No test references the two types deleted here (grep of tests/** found none)
  - Grep evidence: RulesImportedTransactionViewModel|RulesUnmatchedTransactionViewModel over repo excluding bin/obj matched only their own definitions in TransactionsModels.cs
  - Grep evidence: RulesQueue|ImportedRuleTransactions|EditableRules|SavePotentialRule|SaveAllPotentialRules|GetDefaultPotentialRuleCategory|OnImportedRuleTransactionChanged in src/** (non-bin/obj) has zero matches; nothing else left from the old flow in Presentation or App
  - App axaml/cs "Rule" grep shows only new-flow bindings (PotentialRules, potential-rule-row styles), Clear All Rules and CompositionRoot wiring; no stale resource or style found
  - TransactionsModels.cs using HomeCharts.Application.UseCases is still needed by DatePresetOptionViewModel (LedgerDatePreset), so kept

skill_calls:
  - none

risks:
  - The two deleted records' removal left no other newly-unreferenced type; DashboardUncategorizedRowViewModel and other dashboard models were not audited because they are outside the old rules-queue flow
