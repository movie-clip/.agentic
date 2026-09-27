REPORT 2026-09-24-import-rules-list-bounds/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only recon, order verification NONE

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Root cause is the Import tab Border at MainWindow.axaml:388 having no Grid.Row, so it lands in row 0 (Auto) of the content grid declared at :78 (RowDefinitions="Auto,Auto,Auto,*"). Fix there is a layout change in App only.
  - Same defect exists for the Ledger tab Border at MainWindow.axaml:520 (no Grid.Row). Same fix applies, but the order scopes Import only, so decide whether to include it.
  - The nested "*" rows at :389, :423, :435 and the ScrollViewer at :446 are correct in shape but never receive a finite height, because the ancestor row is Auto.
  - Page size is const 120 at MainWindowViewModel.cs:105, fixed and independent of space. With ~60-70px rows that is ~7000px of content, so paging cannot keep the list within the window on its own.
  - Header WrapPanel at :424 mixes title, summary, Apply All, Refresh, Prev, Next, page info with ItemHeight=32. At 1200px min window in a 1.7* column it can wrap, and ItemHeight clips any second-line height mismatch.
  - Convention to mirror: dashboard grid uses explicit Grid.Row="3" (:138) so its * row bounds children; capped lists use ScrollViewer MaxHeight (:305 MaxHeight=220, :328 MaxHeight=700, :358 MaxHeight=180, :534 Border MaxHeight=260).
  - Pager convention to mirror: Ledger pager at :593-595 (Prev, Next, PageInfo) inside a WrapPanel; VM uses PreviousPageCommand/NextPageCommand/PageInfo.
  - Tests: only MainWindowViewModelRulesQueuePagingTests.cs covers the queue paging. If the fix changes RulesQueuePageSize (const at VM:105), that test file duplicates the value at line 23 and must change with it.
  - No Domain/Application/Contracts change is needed. Paging is VM-side slicing of an in-memory list (VM:1349-1379), and layout is pure AXAML.

risks:
  - Not verified visually or by running the app. The overflow explanation is from static reading of Avalonia layout rules (Auto row measures child with infinite height, so ScrollViewer never scrolls).
  - I did not read the AXAML between :1-77 (sidebar) or :580-end (ledger footer) in full. Nothing in a grep of ScrollViewer/RowDefinitions suggests an outer ScrollViewer around the content grid, but I did not open every line.
  - Prior recon (2026-09-23-import-review/01-recon.md) was not opened. Its 02-frontend.md was read and its claims about _rulesQueueRows and page size 120 were confirmed against VM:105 and VM:1349-1379.
  - Whether the user's "only pages, no scroll" observation also involves the inner ScrollViewer being present but inert is inferred; the ScrollViewer exists at :446 with VerticalScrollBarVisibility=Auto and just never becomes constrained.

skill_calls:
  - none

## Orchestrator brief
- Root cause found statically: Import tab Border (MainWindow.axaml:388) has no Grid.Row, so it sits in Auto row 0 of the grid at :78 (Auto,Auto,Auto,*). Auto row = unbounded height, so inner "*" rows and ScrollViewer (:446) never get bounded and the list grows past the window.
- Ledger tab Border (:520) has the same missing Grid.Row. Dashboard (:138) sets Grid.Row="3" explicitly and is bounded.
- Page size is a fixed const 120 (VM:105), not derived from space. Rows are variable/fixed by content ~one TextBox/ComboBox/Button line plus 12 padding and 8 margin.
- Change is App AXAML (and optionally page size const in Presentation VM). No Domain/Application/Contracts work.
- Existing test file for paging: tests/HomeCharts.Application.Tests/MainWindowViewModelRulesQueuePagingTests.cs, hardcodes page size 120.
- Sections below: Q1 Layout tree; Q2 Page size and rows; Q3 Root cause; Q4 Sibling regions; Q5 Tests; Q6 Layer blast radius; Q7 Conventions.

## Q1 Layout tree
All in C:\projects\investments\budget\src\HomeCharts.App\MainWindow.axaml.
- Window: Width 1400, Height 900, MinWidth 1200, MinHeight 760 (:13-16).
- Root Grid ColumnDefinitions="220,*" RowDefinitions="*" (:21). Column 0 sidebar; column 1 content.
- Content Grid Grid.Column=1 RowDefinitions="Auto,Auto,Auto,*" Margin=20 RowSpacing=16 (:78). No ScrollViewer wraps it.
- Import tab Border (:388), IsVisible=IsImportFiltersViewSelected, NO Grid.Row, so row 0 (Auto).
- Inside: Grid RowDefinitions="Auto,*" RowSpacing=14 (:389).
  - Row 0 (:390): Grid cols 1.15*,1.15*,0.7* with Import & Search, Import Status, Rules Actions cards.
  - Row 1 (:421): Grid cols 1.7*,1*.
    - Col 0 Border (:422) > Grid Auto,* (:423): row 0 header WrapPanel ItemHeight=32 (:424-432) holding title, RulesQueueSummary, Apply All, Refresh Queue, Prev, Next, RulesQueuePageInfo.
    - Row 1 Border (:434) MinHeight=280, no MaxHeight > Grid Auto,* (:435): column header Border (:436-444), then ScrollViewer VerticalScrollBarVisibility=Auto, Horizontal=Disabled (:446) > ItemsControl ImportedRuleTransactions (:447).
    - Item template (:449-483): Border Padding 12 Margin 0,0,0,8 > Grid cols 110,*,110,190,96 with date, TextBox, amount, ComboBox, Save button.
    - Col 1 Border (:492): Expenses summary, Grid Auto,* with own ScrollViewer (:499) over ParsedCategoryExpenses.
- No DataGrid is used anywhere in this tab. Pager buttons are plain Buttons bound to PreviousRulesQueuePageCommand / NextRulesQueuePageCommand (:429-430).
- ViewModel: src/HomeCharts.Presentation/Mvp/MainWindowViewModel.cs.

## Q2 Page size and rows
- RulesQueuePageSize = 120, private const, MainWindowViewModel.cs:105. Fixed; not derived from viewport.
- Paging slice: RefreshRulesQueuePage (VM:1349-1379) does Skip((page-1)*120).Take(120) over _rulesQueueRows, adds view models to ImportedRuleTransactions, sets RulesQueuePageInfo "Page n/m" (VM:1377).
- Next enabled when page*120 < _rulesQueueTotalMatchedCount (VM:1615-1622); Previous when page > 1 (VM:171).
- Row height is content-driven, not fixed: no Height on item Border; single-line controls (TextBox, ComboBox, Button) with Padding 12 and Margin bottom 8 (:450-451). Approx 60-70px per row (estimate from control defaults; not measured). 120 rows is thousands of px.
- Column header row and item rows share widths 110,*,110,190,96 (:437, :451) so they align.

## Q3 Root cause
- Primary: Import Border at :388 has no Grid.Row, therefore Grid.Row=0, which is Auto in :78. Avalonia measures Auto rows with infinite available height, so the whole Import subtree measures to its content height. Inner "*" rows (:389, :423, :435) then equal content height, and the ScrollViewer at :446 (VerticalScrollBarVisibility=Auto) is given infinite height, never overflows, never shows a scrollbar. Result matches the user's report: no scroll, list extends past window.
- Contributing: page size 120 is large relative to a 760-900px window, so each page is still far taller than the window.
- Contributing: MinHeight=280 on :434 has no matching MaxHeight; only lower-bounds it.
- Minor: header WrapPanel (:424) has ItemHeight=32 and 7 children including a title at 18pt; may wrap or clip at narrow widths ("UI looks off").
- Statically determined, not confirmed by running the app. Nothing in the file contradicts it.
- Same defect at Ledger Border :520 (no Grid.Row), though its inner grid (:521) has a MaxHeight=260 on the matched list (:534), which partly masks it.

## Q4 Sibling regions
- Import tab, top strip (:390-419): Import & Search (path TextBox, Browse, help text), Import Status (three wrapped TextBlocks LastImportSummary/Details/WarningBreakdown, variable height), Rules Actions (Clear All Rules). All Auto height inside row 0 of :389.
- Lower strip (:421): Potential New Rules list (col 0, 1.7*) and Expenses summary (col 1, 1*), both in the "*" row of :389 which is currently not bounded.
- Sidebar (:21-76, column 0) is separate and fixed at 220px.
- Competition: intended design is top strip Auto plus lower strip "*"; because the ancestor is Auto, "*" has nothing to divide, and the tab as a whole is not scrollable.
- Other tabs' regions share the content grid but are toggled with IsVisible (dashboard :79-138, ledger :520). Rows 0-2 hold dashboard header, KPI cards, and trend banner (:79, :85, :116), all collapsed when not dashboard; RowSpacing=16 still applies between rows, but collapsed rows measure 0.

## Q5 Tests
- tests/HomeCharts.Application.Tests/MainWindowViewModelRulesQueuePagingTests.cs: page size 120 hardcoded at :23; asserts page 1 full (:28-30), page info "Page 2/2" / "Page 1/2" (:41-44, :68, :97), edit state survives paging, Apply All across pages.
- tests/HomeCharts.Application.Tests/MainWindowViewModelTrendBarScalingTests.cs: dashboard trend only, unrelated.
- No Presentation test project exists; VM tests live in Application.Tests. No AXAML/layout or headless UI tests were found.
- Layout (AXAML) fix has no automated coverage.

## Q6 Layer blast radius
- App: MainWindow.axaml only for the layout root cause (Grid.Row on :388, possibly :520).
- Presentation: only if page size or pager labels change (MainWindowViewModel.cs:105, :1349-1379, :1615-1622).
- Tests: MainWindowViewModelRulesQueuePagingTests.cs :23 mirrors page size 120; update only if the const changes.
- Domain/Application/Contracts: no. Paging is in-memory slicing in the VM; no repository/use case takes page parameters for the rules queue (the grep for RulesQueuePageSize/_rulesQueueCurrentPage hits only the VM and the test). Guardrail 3 is not implicated by view-only layout and page-size changes.

## Q7 Conventions
- Bounded scroll lists elsewhere: Dashboard uses ScrollViewer inside fixed-height Grids (Height=380 :231, Height=372 :255) with "Auto,*" rows; also ScrollViewer MaxHeight=220 (:305), MaxHeight=700 (:328), MaxHeight=180 (:358), Border MaxHeight=260 wrapping ScrollViewer (:534).
- Dashboard grid pins itself via Grid.Row="3" (:138), the pattern the Import Border lacks.
- Pager: Ledger uses Prev/Next buttons and PageInfo text (:593-595), the same button styling (Background #0F172A, BorderBrush #334155, Foreground #E2E8F0) as the queue pager (:429-431).
- Scroll settings: ScrollViewer VerticalScrollBarVisibility=Auto, HorizontalScrollBarVisibility=Disabled is used consistently.
