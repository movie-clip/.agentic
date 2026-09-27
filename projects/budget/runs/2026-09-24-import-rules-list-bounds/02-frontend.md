REPORT 2026-09-24-import-rules-list-bounds/02
status:      PARTIAL
verdict:     NONE

changed:
  - src/HomeCharts.App/MainWindow.axaml — Import tab Border gets Grid.Row="3" (the * row), bounding the Potential New Rules and Expenses ScrollViewers
  - src/HomeCharts.App/MainWindow.axaml — pager header WrapPanel: removed ItemHeight=32, added ItemSpacing=12 LineSpacing=8, dropped three now-redundant Margin="12,0,0,0"

verification:
  command:   dotnet build HomeCharts.sln ; dotnet build src/HomeCharts.App/HomeCharts.App.csproj
  result:    FAIL
  detail:    Both commands fail with MSB3021 (2 errors): bin\Debug\net9.0\HomeCharts.App.exe is locked by a running HomeCharts.App.exe (PID 45296), not by the edit. App build to a temp dir (-o) gave 0 Warning(s), 0 Error(s), so the XAML compiles.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Stop the running HomeCharts.App.exe (PID 45296) and re-run both verification commands to get a clean PASS; I did not kill a user process.
  - Visual check needed at 1200x760 and 1400x900 on Import tab with a large queue: list scrolls inside window, Expenses column scrolls, header wraps without clipping.
  - No automated layout coverage exists; test lane has nothing to add for AXAML. Paging tests untouched as page size stays 120.
  - Ledger tab Border (~:520) still lacks Grid.Row; carried finding for the human, untouched per non_goals.

skill_calls:
  - mattpocock-skills:diagnosing-bugs — not called, first fix attempt and root cause was given by recon and verified statically against the file

risks:
  - Fix is unverified visually: I did not launch the app, and an instance is already running with the old build.
  - Verified against the file that the Import Border had no Grid.Row before edit; the fix mirrors the dashboard grid Grid.Row="3" convention.
  - Rows 0-2 of the content grid are collapsed on Import but RowSpacing=16 still adds about 48px of dead space above the tab; same as Dashboard today, left as is.
  - Import Border sits in a star row with content larger than the window: the top strip is Auto and the list Border has MinHeight=280, so at 760px height the window may only just fit; visual check advised.
  - ItemSpacing/LineSpacing on WrapPanel assume Avalonia 11.3.12 (present in App csproj); compiled without warnings.
