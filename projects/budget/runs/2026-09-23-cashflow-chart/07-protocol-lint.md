REPORT 2026-09-23-cashflow-chart/07
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   claude plugin validate C:/projects/investments/.agentic/plugins/agentic-core; git diff on testing.md; read of tests/HomeCharts.Application.Tests/HomeCharts.Application.Tests.csproj
  result:    PASS
  detail:    plugin validate passed; diff is one 6-line paragraph in testing.md Where things live, rules 1/2/5/6/7/8 clean; anchor = bound repo csproj, which has ProjectReference to HomeCharts.Presentation.csproj

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

risks:
  - Rule 5/6: the fact sits in conditional section Where things live, whose Index condition (adding a test file) is evaluable before reading, and a lane adding a view-model test meets it
  - Rule 2: grep of projects/budget (excluding runs/) finds the fact only at testing.md:39-44, so it has exactly one home
  - Rule 7: the added paragraph names no command, so no tools: line is implicated
  - Fact anchor beyond the csproj: MainWindowViewModel is at src/HomeCharts.Presentation/Mvp/MainWindowViewModel.cs:10, and tests/HomeCharts.Application.Tests/MainWindowViewModelTrendBarScalingTests.cs already exercises it
