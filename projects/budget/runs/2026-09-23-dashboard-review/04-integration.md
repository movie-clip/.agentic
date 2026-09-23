REPORT 2026-09-23-dashboard-review/04
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   dotnet build HomeCharts.sln && dotnet build src/HomeCharts.App/HomeCharts.App.csproj && dotnet test HomeCharts.sln --no-build
  result:    PASS
  detail:    Both builds: Build succeeded, 0 Warning(s), 0 Error(s). Tests: Domain.Tests 5/5, Application.Tests 34/34, Infrastructure.Tests 10/10 passed, 0 failed. Run independently, not taken from 03-frontend.md — same result.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - docs lane: 03-frontend.md's own contract_notes (PROJECT_GUIDE.md:43, TECHNICAL_DESIGN.md:42-43) already name the two doc updates close-out needs — not duplicated here.

risks:
  - No HomeCharts.Presentation.Tests project exists in this repo at all, so FormatMonthDeltaSummary/FormatSignedAmount and ReviewUncategorizedAsync ship with no automated coverage.
  - Not raising a CR for the coverage gap above: the architecture pack's SHOULD_FIX test-coverage example names Infrastructure.Tests/Application.Tests specifically, this is pure formatting/dispatch, and the missing project is a repo-wide gap this slice didn't create and can't fix in its own scope — flagging for the ledger only.
  - The needs-attention panel's placement (right column vs. full-width row) is 03-frontend.md's own disclosed layout call against a MinHeight constraint — UI/UX placement is this gate's non_goal, so I did not evaluate it further.

## Orchestrator brief
- Verdict: PASS. All 3 slices (dead-code removal, needs-attention panel, month-comparison strip) match the approved brief (02-product.md), stay Presentation-only, and touch only the 3 files in scope — confirmed via `git status`/`git diff` against working-tree noise.
- Guardrail 3 holds: FormatMonthDeltaSummary/FormatSignedAmount format an already-computed `MonthComparison` (decimals decided in `BuildDashboardSnapshotUseCase.cs:309-314`); ReviewUncategorizedAsync sets a flag, calls existing RefreshLedgerAsync, dispatches a tab switch — no new decision in either.
- Both frontend risk flags are sound engineering judgment, correctly disclosed rather than silent deviation — see § Frontend risk flags below.
- Verification re-run independently (not trusted from 03-frontend.md): build/build/test all PASS, same counts.
- No change requests; no `cr/` files written.
- Section below: § Frontend risk flags — the reasoning behind clearing both of 03-frontend.md's flagged deviations.

## Frontend risk flags

**Flag 1 — TotalTransactionsText kept as a private field.** Consistent with Slice 1's intent, not a deviation from it. The brief ruled `TotalTransactionsText` dead because recon's grep only checked XAML bindings and missed the two C# Status-message interpolations at `MainWindowViewModel.cs:709,734`. Confirmed independently: `TotalTransactionsText` has zero XAML matches (it was never bound), so the *bindable public property* was correctly dead and is gone; the *value* had a real non-UI consumer the brief didn't know about, so keeping it as `_totalTransactionsCount` (now `int`, not a formatted `string`) is the narrower, correct fix — it removes exactly the dead surface (the public `ObservableObject` property nobody bound to) and keeps exactly the live one (the raw count two Status messages need). A verbatim delete would not have compiled.

**Flag 2 — added RefreshLedgerAsync inside ReviewUncategorizedAsync.** Correct and necessary, not scope creep. `ApplyFiltersAsync` (`MainWindowViewModel.cs:771-778`) is the existing, only precedent for "change a ledger filter field then make it visible," and it always pairs the flag change with `RefreshLedgerAsync` before setting `Status`. `ReviewUncategorizedAsync` (`:781-790`) follows that exact shape. Omitting the call would have shipped a button that changes `OnlyUncategorized` and switches tabs while the grid still shows its last unfiltered page — a broken feature, not a smaller one. This is reuse of an established pattern, not an independent decision the two engineers could have diverged on.
