REPORT 2026-09-24-import-rules-list-bounds/03
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   dotnet build HomeCharts.sln ; dotnet test HomeCharts.sln --no-build ; dotnet build src/HomeCharts.App/HomeCharts.App.csproj
  result:    PASS
  detail:    Solution build 0 Warning(s) 0 Error(s); tests 5 Domain + 40 Application + 11 Infrastructure = 56 passed, 0 failed; App build 0 Warning(s) 0 Error(s). Anchor: static diff vs recon root cause only, no UI run.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Human visual check still open: Import tab at 1200x760 and 1400x900 with a large queue; list scrolls inside window, Expenses column scrolls, header wraps unclipped. See § Review notes.
  - Ledger tab Border (~:520) still lacks Grid.Row; carried finding for the human at close-out, not blocking per order non_goals.

skill_calls:
  - none

risks:
  - Layout fix is judged statically only; I cannot run the UI, so scroll and wrap behaviour is unconfirmed until a human looks.
  - Rows 0-2 stay collapsed on Import but RowSpacing=16 leaves about 48px dead space above the tab; same as Dashboard today, not a regression.
  - Import Border MinHeight=280 on the list plus the Auto top strip may only just fit at 760px window height; MinHeight has no MaxHeight. Confirm visually.
  - MainWindowViewModel.cs and MainWindowViewModelRulesQueuePagingTests.cs show as modified/untracked but have 2026-09-23 mtimes, so they belong to the prior import-review run, not this lane.

## Orchestrator brief
- Verdict PASS: the diff matches the recon root cause. Import Border now has Grid.Row="3" (the * row), so the inner Auto,* grids and both ScrollViewers get finite height.
- Pager header WrapPanel drops ItemHeight=32 and uses ItemSpacing/LineSpacing, so wrapped lines no longer clip.
- Only MainWindow.axaml changed for this run; no binding, command or logic was added (guardrail 3 respected). Dashboard/Ledger blocks untouched.
- Build 0 warnings 0 errors; 56 tests pass; App build clean. The earlier MSB3021 lock is gone.
- Not blocking: Ledger Border missing Grid.Row (carried). No CR files written.
- Sections below: Review notes.

## Review notes
- Diff read via git diff: two hunks only. Hunk 1 adds Grid.Row="3" to the Import Border at :388. Hunk 2 rewrites the pager WrapPanel at :424-432.
- Root cause fit: recon Q3 named the missing Grid.Row as primary. Row 3 is the * row of the content grid at :78, so the Border gets the window remainder.
- Inner grid Auto,* at :389 and Auto,* at :423 now resolve against a finite height, so the ScrollViewers with VerticalScrollBarVisibility=Auto can scroll.
- Margin removal is safe: ItemSpacing=12 replaces the three Margin="12,0,0,0" values. The buttons had no margin before, so spacing between buttons grows from 0 to 12; cosmetic.
- Grid.Row="3" is shared with the Dashboard grid at :138 and Ledger, but all three are toggled by IsVisible, so only one occupies row 3 at a time.
- Scope check: git status filtered of bin/obj lists MainWindow.axaml (this run), the VM and a test file (both dated 2026-09-23, prior run). No other src edits by the frontend lane.
- Guardrail 3: the change is layout attributes only, no code-behind, no logic.
