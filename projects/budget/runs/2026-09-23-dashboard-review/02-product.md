REPORT 2026-09-23-dashboard-review/02
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    product order, verification: NONE

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - 3 build slices proposed, all single-layer Presentation, none story- or design-earning — see § Stories, § Placement
  - dead-code ruling covers all 13 named scalar properties + 3 record types + their collections, split remove vs wire-up — see § Stories, Slice 1
  - 2 UI/UX changes proposed (needs-attention panel, month-comparison strip) — see § Stories, Slices 2-3
  - guardrail-3 judgment calls resolved: bar-percent math deleted as dead code, percent-to-pixel chart chain stays in Presentation — see § Placement
  - GetDefaultRange() ruled leave-as-is, not worth relocating now — see § Placement
  - 1 open decision for the human: bless the doc-drift resolution direction (update docs, do not resurrect the old Uncategorized KPI card) — see § Open decisions
  - docs/PROJECT_GUIDE.md:43 and docs/TECHNICAL_DESIGN.md:42-43 updates are close-out docs work once slices ship, not a separate build slice — see § Already covered

risks:
  - the order's DoD cites "10 unused properties"; recon's § Unused surface actually names 13 distinct scalar properties (7 bullets) plus 3 record types — my ruling covers all 13 by name, count mismatch is not a missing item.
  - I resolved the percent-to-pixel-height guardrail-3 call as "stays in Presentation" (§ Placement); a reviewer could reasonably read the relative-to-max ratio as Application-layer decision logic — I picked one reading with a one-line reason per the order's non_goals, not both.
  - the doc-drift ruling rests on git evidence I opened myself (`git show d4facfd`, see § Open decisions) — the commit message ("fixes") gives no stated reason for the KPI-card swap, so I inferred intent from the diff shape, not a recorded decision.

## Orchestrator brief
- verdict: new work, single-layer (Presentation-only) slice set — no epic/story tree exists in this repo (project.md § Delivery model); this brief is the specification.
- 3 build slices, all frontend-engineer, all Presentation-only:
  1. Dead-code removal (13 scalar properties / 3 record types, ruled item-by-item) — DONE-ready
  2. "Needs attention" panel (uncategorized queue + coverage, wired to existing Ledger filter) — DONE-ready
  3. "This month vs last month" comparison strip (already-computed MonthComparison) — DONE-ready
- blocks dispatch: nothing technical; one open decision for the human on doc-drift framing (§ Open decisions) — does not block starting Slice 1.
- `story` does not fire: no layer crossing, no Contracts/use-case/migration change (phases.md § "When the brief is the specification").
- `design` does not fire: no Contracts interface, use-case shape, or migration changes in any slice.
- sections below: Placement · Stories · Sequence · Open decisions · Already covered

## Placement

No epic/story tree exists for `budget` (project.md § Delivery model: "the backlog is whatever the human asks for next"). This request is the three things the human asked for — review, clean dead code, propose UI/UX — and all three land as direct extensions of the existing Dashboard tab (`MainWindow.axaml:78-294`, `MainWindowViewModel.RefreshDashboardAsync`, `DashboardModels.cs`), not a new surface. Nothing here crosses into `Domain`/`Application`/`Infrastructure`/`Contracts`: every UI/UX proposal below consumes fields `BuildDashboardSnapshotUseCase.ExecuteAsync` already returns on `DashboardSnapshot` (`UncategorizedQueue`, `Coverage`, `CurrentVsPreviousMonth` including its `IncomeDelta`/`ExpensesDelta`/`NetDelta`, confirmed at `BuildDashboardSnapshotUseCase.cs:74-106`). No new use case, no schema change, no `Contracts` change — so both `story` and `design` phase clauses (`phases.md`) stay false. This is the short-run shape: `build(frontend) → verify(integration) → close(docs)`.

**Guardrail-3 ruling 1 — `IncomeBarPercent`/`ExpensesBarPercent` share-of-total math (`MainWindowViewModel.cs:1185-1195`).** Moot: this data has no XAML consumer at all (confirmed — grepped `MainWindow.axaml` for both names, no match), so "move it to Application" would be relocating dead code, not improving architecture. Ruling: **delete**, not relocate (see § Stories, Slice 1). This resolves the judgment call by removing the question rather than picking a layer for arithmetic nobody reads.

**Guardrail-3 ruling 2 — the trend/category percent-to-pixel-height chain (`MainWindowViewModel.cs:1211-1236,1242-1255`; `DashboardModels.cs:41-44`'s `Math.Max(6d, percent * 2.4d)`).** This one is live — it drives the visible bar chart and category progress bars. Two readings exist; picking one:
- Reading A: the relative-to-max ratio is a decision (which category/month is "how big" relative to peers) and belongs in `Application` on `DashboardSnapshot`.
- Reading B: the amounts are already fully decided by `Application`; converting them to a 0-100 relative scale and then to a pixel height (`2.4d`, a hand-tuned constant for a specific 250px-tall Avalonia grid, `MainWindow.axaml:148`) is chart-layout formatting of an already-decided fact, matching guardrail 3's own wording ("format, display... they do not decide").
- **Picked: Reading B.** One-line reason: the pixel-height formula is intrinsically tied to this one widget's layout constants; moving the ratio to Application would still leave the pixel-scaling in Presentation, splitting one rendering concern across two layers for zero behavior change, and any future chart resize would then require touching Application. **Ruling: leave in Presentation — relocating it is low-value churn, not the architecture improvement worth doing here.**

**`GetDefaultRange()` (`MainWindowViewModel.cs:1484-1488`, hardcoded 5-years-back/1-day-forward).** `BuildDashboardSnapshotUseCase.ExecuteAsync` already takes `fromInclusive`/`toInclusive` as parameters — this method only chooses what to pass, shared identically across 3 call sites (dashboard refresh, post-import auto-categorize, manual apply-rules). **Ruling: leave as-is.** It is a constant, not a decision that varies by input, and moving it today fixes no bug and unblocks no story — pure premature relocation. Revisit only if a future request makes the window itself a product feature (e.g., a user-selectable date range), at which point the natural home becomes an `Application`-level default next to the use case.

**Net "architecture improvement" verdict:** the one real architecture improvement available here is the dead-code removal in Slice 1. Both guardrail-3 arithmetic locations and `GetDefaultRange()` are ruled leave/delete rather than relocate — the aggregation logic that matters (`BuildDashboardSnapshotUseCase`) is already correctly in `Application`, per recon's own finding.

## Stories

Framed as build slices, not tickets — per "What is a story here, and what is not," none of these earns a story.

### Slice 1 — Remove dead dashboard surface
outcome: the Dashboard's view-model and mapping code contain only members something actually renders — no user-visible change, this is the "clean unused methods/classes" ask.
value: none directly user-visible; the value is removing the exact ambiguity recon flagged ("a delivery brief should decide remove-vs-wire-up before any new dashboard work builds on top of them") so Slices 2-3 build on a clean base.
slice:
  - remove (no wire-up target identified): `DashboardSummary`, `TotalTransactionsText`, `AttentionSummaryText`, `IncomeBarPercent`, `ExpensesBarPercent` (`MainWindowViewModel.cs:418,430,508,514-524` + their population at `:1167-1168,1170,1183,1185-1195`)
  - remove (redundant with a bound sibling, no distinct value): `TrendRows`/`DashboardTrendRowViewModel` (duplicates `TrendChartBars`' Month/Income/Expenses/Net), `CategoryRows`/`DashboardCategoryRowViewModel` (duplicates `ExpenseCategoryBars`' Category/Amount/TransactionCount) — collections at `MainWindowViewModel.cs:204,206`, population at `:1216-1220,1248-1251`, types at `DashboardModels.cs:5-15`
  - out of slice: `UncategorizedRows`/`DashboardUncategorizedRowViewModel` and `CurrentMonth*`/`MonthDeltaSummaryText` — these move to Slices 2 and 3 (wire-up, not removal)
depends_on: none
invest: weak on Valuable — this slice has no user-visible outcome by itself; included because the user explicitly asked to "clean any unused methods/classes" and because it removes a stated blocker to building on top of dead code. Independent, Small, Testable (each removal is a mechanical delete + build-green check) otherwise hold.

### Slice 2 — "Needs attention" panel (uncategorized review queue)
outcome: from the Dashboard, the user can see the transactions still needing a category and jump straight into fixing them, instead of discovering uncategorized activity only by opening the Ledger tab and remembering to check the "Only uncategorized" box.
value: closes the exact gap `docs/PROJECT_GUIDE.md:12` already claims ("dashboard insights for ... uncategorized activity") but the shipped UI never delivered — the data (`UncategorizedRows`, `UncategorizedCountText`, `CategorizedCoverageText`, `UncategorizedAmountText`) is already computed every refresh (`MainWindowViewModel.cs:1175-1177,1298-1306`) and currently thrown away.
slice: a new panel/card on the Dashboard listing the top N uncategorized transactions (reusing `DashboardUncategorizedRowViewModel`) with count/coverage/amount, plus one action that sets `OnlyUncategorized = true` (`MainWindowViewModel.cs:333-336`, already used by the Ledger tab's existing filter at `MainWindow.axaml:492-493`) and switches to the Ledger tab. Out of slice: any new filtering/sorting inside the panel itself, any change to how the Ledger tab's own uncategorized filter works.
depends_on: none technically; soft precedence on Slice 1 only to avoid touching code mid-removal in the same method.
invest: solid on all six — independent, negotiable (only the outcome is fixed, not the exact panel layout), user-visible, small (one panel + one dispatch action, zero backend work), testable ("uncategorized transactions appear on the Dashboard and clicking the action filters the Ledger to them").

### Slice 3 — "This month vs last month" comparison strip
outcome: from the Dashboard, the user can see at a glance whether this month's income/expenses/net moved up or down from last month, without opening the trend chart and comparing bars by eye.
value: `BuildDashboardSnapshotUseCase` already computes `MonthComparison` including `IncomeDelta`/`ExpensesDelta`/`NetDelta` (`BuildDashboardSnapshotUseCase.cs:74-106`) and the view model already maps the current-month figures (`CurrentMonthLabelText`/`CurrentMonthIncomeText`/`CurrentMonthExpensesText`/`CurrentMonthNetText`, `MainWindowViewModel.cs:1178-1181`) — none of it is displayed today.
slice: a compact strip near the KPI row or trend chart showing current-month figures plus a formatted delta (replacing the currently-hardcoded-empty `MonthDeltaSummaryText`, `:1182`, with real formatting of the already-computed deltas — a Presentation-layer *format* of an Application-decided number, not a new decision). Out of slice: adding new delta metrics beyond income/expenses/net, any change to how `MonthComparison` itself is computed.
depends_on: none.
invest: solid — independent of Slice 2, user-visible, small, testable ("the strip shows last month's and this month's income/expenses/net and a signed delta").

## Sequence

No hard dependencies between the three slices — each touches a disjoint region of `RefreshDashboardAsync`/`DashboardModels.cs`/`MainWindow.axaml`. Recommended order, for diff-size reasons only:

1. **Slice 1 (removal) first.** Shrinks the surface before the other two land, and lets the close-out docs pass (§ Already covered) describe the *final* state in one edit instead of two.
2. **Slice 2 (needs-attention panel) second.** It is the more concrete "product gap" — it directly answers `docs/PROJECT_GUIDE.md:12`'s existing claim about uncategorized-activity insight — and reuses a filter (`OnlyUncategorized`) that already ships, so it is the lower-risk of the two new-UI slices.
3. **Slice 3 (month comparison) third.** Fully independent of Slice 2; ordered last only because it needs one small new piece of logic (delta formatting) that Slice 2 does not.

`integration` (build + test) runs once after each slice or once after all three — either is fine since none is story-gated; `review` does not fire (no story exists to accept against). `docs` fires at close regardless (phases.md, always) and should fold in the § Already covered doc updates once whichever slices shipped are known.

## Open decisions

### Bless the doc-drift resolution direction, not just the fact of drift
`docs/PROJECT_GUIDE.md:43` ("KPI cards: income, expenses, uncategorized") and the shipped `MainWindow.axaml` KPI row (Income/Expenses/Net/Avg Monthly Savings Rate) were written in the *same* commit (`d4facfd`) — `git show d4facfd` shows the XAML's third card was directly rewritten from "Uncategorized" (bound to `UncategorizedCountText`) to "Avg Monthly Savings Rate" in that diff, while the doc's KPI-card line was left describing the pre-change set. That commit's message ("fixes") does not say why the swap happened. Two ways to close this:
- (a) treat the swap as an intentional product decision that simply forgot to update the doc — resolve by updating `docs/PROJECT_GUIDE.md:43` to the current 4 cards, plus Slice 2's new panel, once shipped. **This is the reading this brief assumes and Slice 2 is built on.**
- (b) treat the removal of the Uncategorized KPI card as an unintended regression and restore it as a 5th card alongside Slice 2's panel.
This brief picks (a) because Slice 2 already gives uncategorized activity a stronger, more actionable home (a review queue plus a jump-to-Ledger action) than a bare count card ever did — but (a) vs (b) is a product-intent call the recorded history cannot fully settle, so it goes to the human rather than being asserted.

## Already covered

- `TrendChartBars`/`ExpenseCategoryBars` already render the same underlying data `TrendRows`/`CategoryRows` would (§ Stories, Slice 1) — confirmed by reading both the view-model records (`DashboardModels.cs:5-15,22-45`) and the bound XAML template (`MainWindow.axaml:145-172` for trend bars, `:239-263` for category bars); removal loses no information currently reachable by the user.
- The Ledger tab's "Only uncategorized" filter (`MainWindow.axaml:492-493`, `OnlyUncategorized` at `MainWindowViewModel.cs:333-336`) already exists and is the mechanism Slice 2 reuses — Slice 2 adds a Dashboard-side entry point into it, it does not duplicate or replace it.
- `docs/TECHNICAL_DESIGN.md:42-43`'s incomplete list of `DashboardSnapshot` sub-shapes (recon § Doc drift) is a close-out docs fix once Slices 2-3 ship and the shapes they consume (`MonthComparison`, uncategorized queue) actually have a UI to document — not a separate build slice.
- Recon's flagged risk that `IncomeBarPercent`/`ExpensesBarPercent` "is currently unused... so today it is dead arithmetic rather than a live decision" is accepted at face value here (I independently confirmed zero XAML matches for both names) and is the basis for the delete-not-relocate ruling in § Placement.
