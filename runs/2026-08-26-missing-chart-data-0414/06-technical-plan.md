REPORT 2026-08-26-missing-chart-data-0414/06
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only DESIGN order, no verification command named

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - The story's T-41.1.1 text bundles the `types.ts` mirror and `docs/contracts/dashboard-fields.md` edit into the "Backend" ticket — `backend.md`'s "Contract notes you must emit" section forbids backend-engineer from touching `apps/desktop/**` or `docs/**`. Dispatch per § Lane split below, not per the ticket's literal wording.
  - T-41.1.1 (backend-engineer): implement exactly § Contract + § Decision — delete the branch. Verification: `cd services/quant-engine && python -m pytest app/tests/test_analytics.py -k "withheld or publishable or disclosure"`.
  - T-41.1.2 (frontend-engineer): implement § Frontend visual treatment, consuming backend's contract_notes for the exact TS field/location. Do not introduce `CardShell`/`TrustBadge`/`WindowSelector` — this file is an intentionally-unmigrated Dashboard card (ui-polish § Migration notes); only extend the `ChartShell`/`chartDefaults` usage already present.
  - T-41.1.3 (test-engineer): § Test-plan resolution below settles how the frontend half is actually testable given the file's existing full-`LineChart` mock — read it before writing the vitest additions.
  - T-41.1.4 (docs-engineer): fold the `dashboard-fields.md` contract-row addition (sourced from backend's `contract_notes`) into the same dispatch as the methodology two-granularities note — both are docs-lane, both are small, no reason to split.

risks:
  - Recharts `ReferenceDot`'s `shape` render-prop type (confirmed from `node_modules/recharts/types/cartesian/ReferenceDot.d.ts`, installed v3.8.1) accepts a function receiving `DotProps` including `cx`/`cy` — confirmed from typings, not from a live render. Frontend engineer should sanity-check the actual prop shape against installed 3.8.1 at implementation time.
  - `PerformanceBenchmarkCard.test.tsx` mocks `LineChart` down to a `<div>` dumping only its `data` prop — the marker component never mounts through that mock today. § Test-plan resolution names the two-tier fix (extend the data dump + test the marker component in isolation), but I have not written or run either test; test-engineer owns confirming it actually closes the AC1/AC6 gap.
  - I did not confirm SVG `tabIndex` + `onFocus` actually receives keyboard focus in jsdom (vitest's environment) versus only in a real browser — a plausible but unverified assumption behind "keyboard-reachable." Flagging for test-engineer, not resolved here.
  - If jsdom does not deliver focus events to an SVG `<g>`, the accessible-name path (`aria-label`, read by a screen reader on focus) still holds regardless — but the visible-caption test may need `fireEvent.focus` rather than a literal Tab-key simulation.

## Orchestrator brief
- Contract settled: `PerformancePoint.withheld_reason: str | None` (backend, no default — see § Contract), mirrored as `PerformanceSeriesPoint.withheld_reason?: string | null` (TS, optional key — matches the `window_start_date?:` precedent exactly, so existing fixture literals keep type-checking). See § Contract.
- Decision: `_withheld_return_cause(state) -> str | None` is a new module-level helper in `performance.py`, single source for both the per-point field and `replay_disclosures()`.
- Decision (the open question): DELETE `replay_disclosures()`'s `reconciliation_adjustment` branch (`performance.py:225-229`), not leave-with-comment. This is compelled by AC4, not a style call — see § Decision: delete the dead branch.
- Decision: frontend marker is a `ReferenceDot` at `(x=date, y=100)` with a custom diamond `shape`, `--color-status-warn` token, keyboard-focusable, revealing a caption paragraph (reusing this file's existing `<p className="helper">` pattern) — not a Recharts built-in `Tooltip` (those are hover-only in this codebase's existing usage). See § Frontend visual treatment.
- Lane split resolves a real conflict between the story's ticket-owner labels and the backend/frontend pack boundaries — see `handoff`, § Lane split and order.
- AC traceability: all 6 ACs covered, no orphan — see § AC traceability.
- Sections below: § Contract · § Decision: delete the dead branch · § Frontend visual treatment · § Test-plan resolution · § Lane split and order · § AC traceability

## Contract

**Backend — `services/quant-engine/app/schemas/reconciliation.py:510-515`:**

```python
class PerformancePoint(BaseModel):
    date: str
    portfolio_value: float
    benchmark_price: float | None
    portfolio_return_pct: float | None
    benchmark_return_pct: float | None
    # US-41.1: the one reason THIS date's portfolio_return_pct is withheld, or
    # None when it is publishable. Populated iff `not state.return_is_publishable`
    # — NEVER for the other two null-portfolio_return_pct causes (whole-series
    # basis suppression, zero-prior-value gap; see performance.py
    # build_true_performance_series). Sourced from the one function
    # replay_disclosures() also reads, so the two surfaces cannot drift
    # (03-quant-research.md § Field proposal).
    withheld_reason: str | None
```

No default value — matches every sibling field on this model (all required keys, nullable values), and forces the one call site (`build_true_performance_series`'s `PerformancePoint(...)` construction, `performance.py:348-356`) to pass it explicitly rather than silently defaulting to `None` if a future field is added to the constructor call and this one is forgotten.

**Classifier — new module-level helper in `performance.py`, placed above `replay_disclosures` (~line 205):**

```python
def _withheld_return_cause(state: DailyPortfolioState) -> str | None:
    """The one reason THIS state's return is withheld, or None if it is
    publishable. Single source for replay_disclosures()'s run-level summary
    and build_true_performance_series()'s per-point field (US-41.1) — read
    one classification, not two independently maintained ones.
    """
    if state.return_is_publishable:
        return None
    return (
        "a holding whose reconstructed quantity was withheld traded that day, "
        "moving cash with no position behind it in market value"
    )
```

Text copied verbatim from the existing `unbacked_cash_flow` sentence at `performance.py:231-233` — AC6 requires the same register, and this makes it literally the same string, not a re-wording.

**Wiring into `build_true_performance_series`** (`performance.py:298-359`): one line inside the existing per-state loop (line ~320), passed into the `PerformancePoint(...)` constructor call:

```python
withheld_reason=_withheld_return_cause(state),
```

`state` is already in scope there — no new plumbing, matches 03-quant-research.md's finding exactly.

**Frontend — `apps/desktop/src/features/portfolio/types.ts`, in `PerformanceSeriesPoint` (line 556-562):**

```ts
export type PerformanceSeriesPoint = {
  date: string
  portfolio_value: number
  benchmark_price: number | null
  portfolio_return_pct: number | null
  benchmark_return_pct: number | null
  /** US-41.1: the one reason this date's portfolio_return_pct is withheld, or
   *  absent/null when publishable. Optional key (like the sibling
   *  `window_start_date?:` on DashboardRangeMetrics, types.ts:553) so existing
   *  PerformanceSeriesPoint fixture literals predating this field keep
   *  type-checking; the backend always serializes it. */
  withheld_reason?: string | null
}
```

**Contract doc — `docs/contracts/dashboard-fields.md`:** new row alongside the existing `performance_series`/`window_start_date` entries (the file's own established format, see line 324's `window_start_date` entry for the template), naming: backend source (`PerformancePoint.withheld_reason`, `_withheld_return_cause` classifier), TS mirror location, consuming UI (`PerformanceBenchmarkCard.tsx`'s marker), and the "null iff publishable, never a placeholder string" nullability rule. Docs-engineer owns writing the actual row; backend's `contract_notes` on its own report is what feeds this.

## Decision: delete the dead branch

**Delete `replay_disclosures()`'s `reconciliation_adjustment` branch (`performance.py:225-229`).** Rewrite the function to read from the shared classifier:

```python
def replay_disclosures(states: list[DailyPortfolioState]) -> tuple[list[str], str | None]:
    reasons = [(state.date, _withheld_return_cause(state)) for state in states]
    withheld = [date for date, cause in reasons if cause is not None]
    if not withheld:
        return withheld, None
    causes = list(dict.fromkeys(cause for _, cause in reasons if cause is not None))
    return withheld, "Return withheld: " + "; ".join(causes) + "."
```

This is not a style preference between two defensible options — it is compelled by AC4. AC4 requires `replay_disclosures()` and the per-point field to "read one classification, not two independently maintained ones." The classifier has exactly one branch (`return_is_publishable` is today driven solely by `unbacked_cash_flow` materiality — 03-quant-research.md § Classification branches, confirmed by code, test, and independent recompute). Keeping branch 1 alive, unconverted, as a second inline check bolted onto the side of a call to the new shared classifier would be precisely the "two independently maintained classifications" AC4 forbids — the classifier says one cause; the old branch would still independently probe `reconciliation_adjustment`.

It is also not merely inert. `reconciliation_adjustment` is set only on the terminal state, and nothing structurally prevents a future statement's terminal date from *also* independently carrying a material `unbacked_cash_flow` (the coincidence 03-quant-research.md names, not proven impossible — only unobserved on the current fixture). In that coincidence, branch 1 would fire and append "the state was adjusted to match the statement's ending NAV..." as a *cause of withholding* — but `return_is_publishable`'s own logic (`reconciliation.py:624`, `if not self.unbacked_cash_flow: return True`) makes clear the reconciliation adjustment contributes nothing to withholding; only `unbacked_cash_flow` does. Left in place, branch 1 is a latent disclosure-honesty defect (attributing withholding to a cause that isn't the cause), not just dead code — guardrail 4 territory, not a hygiene call.

This resolves the story's "Out of scope" line ("Deleting or otherwise changing `replay_disclosures()`'s currently-dead `reconciliation_adjustment` branch") — that line predates this design pass and is explicitly listed under "Open decisions" as deferred to it, not as a ban. The story's out-of-scope guard that remains binding — "no change to which dates are withheld, or to `return_is_publishable`'s classification rule" — is untouched: this refactor changes only how an already-computed classification is surfaced in text, not the boolean itself.

## Frontend visual treatment

**Data (pure passthrough, no client-side re-derivation):** extend `IndexedPoint` (`PerformanceBenchmarkCard.tsx:46`) with `withheldReason: string | null`, copied straight from `p.withheld_reason ?? null` inside `buildIndexedSeries`'s existing `.map()` (line 67-98) — zero new logic, matching the story's explicit thin-backend-field mandate (`## Notes / decisions`).

**Marker:** a Recharts `ReferenceDot` per point where `withheldReason != null`, at `x={date}` and `y={100}` — the same y-value the chart already draws a dashed neutral baseline at (`<ReferenceLine y={100} .../>`, line 162). Placing the marker exactly on that existing line, x-aligned to the withheld date:
- satisfies "the exact date... right there on the chart" (AC1) — it sits at the precise x-position of the line's actual gap (`connectNulls={false}` already breaks the portfolio line there);
- avoids fabricating a data value (guardrail 4) — 100 is the chart's own "no information yet" anchor, not a plausible-looking indexed return.

Custom `shape` render function (confirmed against installed Recharts 3.8.1's `ReferenceDot.d.ts`: `shape?: (props: DotProps) => ReactElement<SVGElement>`, receiving `cx`/`cy` pixel coordinates) — a small named component, e.g. `WithheldMarker`, rendering:
- a diamond (not a circle) in `var(--color-status-warn)` (`#efd694`, the existing "warn" token already used in `ImportAdmissionReviewCard.tsx` — reused, not invented) — shape-distinct from the circular data-point convention and color-distinct from both `--color-line-portfolio` (blue) and `--color-line-benchmark`/`--color-text-muted` (same value, `#94a3b8` — reusing that token for the marker would visually read as "a benchmark-related value," which it is not);
- `tabIndex={0}`, `role="img"`, `aria-label={`Return withheld for ${date}: ${reason}`}` — the full classifier sentence, so a screen-reader user gets the complete cause on focus with no further interaction (keyboard-reachable per the DoD, not hover-only);
- `onMouseEnter`/`onFocus` → call a parent-owned setter `setActiveWithheldDate(date)`; `onMouseLeave`/`onBlur` → clear it only if it currently equals this marker's own date (guards against a stale blur clobbering a newly-focused marker).

**Caption:** one `<p className="helper">` (this file's own existing pattern, e.g. line 228 or 237) placed directly below `ChartShell` and above `benchmark-card-summary`, rendered only when `activeWithheldDate != null`: `${formatDateLabel(activeWithheldDate)} — ${reason for that date}`. This is what makes the reason *visible* (not just screen-reader-announced) to a sighted keyboard user tabbing through the chart, without building a floating/positioned tooltip — it reuses the card's own established disclosure-paragraph language instead of inventing a new interaction pattern. Absent (not rendered, not an empty string) when nothing is focused/hovered — consistent with AC3's "absence is absence."

**Rejected alternative:** an axis-anchored icon via `ReferenceLine x={date}`'s `label` prop, sitting below the x-axis rather than on the y=100 line. Considered because it reads even more clearly as "not a data value," but `ReferenceLine`'s label positioning for a bottom-anchored custom shape is a less direct Recharts idiom than `ReferenceDot`'s `shape` prop, and y=100 already carries the right "neutral, not a real value" reading via the pre-existing dashed reference line at that exact position. Not specifying both as an open choice — one committed design, per the pack's caution against two lanes independently guessing.

**No opportunistic migration:** continue using only the primitives this file already imports (`ChartShell`, `chartDefaults`). Do not introduce `CardShell`, `TrustBadge`, or `WindowSelector` here — the Dashboard tab is explicitly excluded from the audited design system (ui-polish § Migration notes; frontend.md § "Do not opportunistically migrate").

## Test-plan resolution

The story's test plan says vitest should assert "the chart renders the inline annotation at a withheld date, and renders nothing at a non-withheld null point" — but `PerformanceBenchmarkCard.test.tsx` already mocks `LineChart` down to `<div data-testid="indexed-chart-data">{JSON.stringify(data)}</div>` (lines 15-29), so nothing inside `<LineChart>` — including any `ReferenceDot` — ever actually mounts through that mock today. Two-tier resolution, not a single test:

1. **Data-shape coverage (extends the existing mock, near-zero new machinery):** add `withheldReason` to the fields the `LineChart` mock captures and dumps to `data-testid="indexed-chart-data"` (one-line change to the existing mock at line 27), then assert via the existing `getChartData()` helper that `withheldReason` is non-null exactly on `withheld_return_dates` and null elsewhere in the chart's own windowed slice — covers AC1/AC2/AC3 at the data layer, in the same style the file already uses for `portfolio`/`benchmark` values.
2. **Marker/accessibility coverage (new, isolated):** the `WithheldMarker` component must be a named, separately-importable function component (not an inline arrow function passed straight to `shape`) — the same pattern `DrawdownAnalyticsCard.tsx`'s `UnderwaterTooltip` already establishes for testable sub-components. Render it directly with fixed `cx`/`cy`/`date`/`reason` props via RTL, independent of Recharts' real layout, and assert: `role="img"`, `aria-label` contains the full reason text, and `fireEvent.focus`/`fireEvent.mouseEnter` triggers the activation callback — this is what actually proves AC6 (same-register text) and the keyboard-reachability requirement, which the data-shape test in (1) cannot reach.

## Lane split and order

Backend contract before frontend consumer, implementation before tests, docs last — this project's established convention (also this run's own precedent: 11-integration.md's chart-audit CRs landed backend/schema before the chart-facing frontend fix).

1. **T-41.1.1 — backend-engineer.** `performance.py` classifier + `PerformancePoint.withheld_reason` schema field + `replay_disclosures()` rewrite (§ Decision: delete the dead branch). Scope: `services/quant-engine/app/**` only — per `backend.md`, does NOT touch `types.ts` or `docs/contracts/`. Emits `contract_notes` naming the exact TS field/location and the dashboard-fields.md row, per backend.md's own "Contract notes you must emit."
2. **T-41.1.2 — frontend-engineer.** Consumes T-41.1.1's `contract_notes`: applies the `types.ts` mirror (§ Contract) first, then `IndexedPoint`/`buildIndexedSeries` passthrough, then the `WithheldMarker` + caption (§ Frontend visual treatment).
3. **T-41.1.3 — test-engineer.** Backend regression pin (`withheld_reason` non-null exactly on `withheld_return_dates`, including the two immaterial-unbacked-cash dates) + the existing `test_withheld_days_are_named_with_only_the_causes_that_fired` re-run unmodified (confirms § Decision's rewrite preserves output) + the two-tier frontend coverage in § Test-plan resolution. Depends on both 1 and 2 landing.
4. **T-41.1.4 — docs-engineer.** `financial-methodology.md`'s two-granularities note (near lines 622-638, the existing "other cause" discussion) + the `dashboard-fields.md` contract row (§ Contract) in the same dispatch. Last, once the field and its consumer both exist to document accurately.

## AC traceability

| AC | Covered by |
|---|---|
| AC1 — inline reason at the withheld point | T-41.1.1 (field) + T-41.1.2 (marker, § Frontend visual treatment) |
| AC2 — no reason for the other two null causes | T-41.1.1 (classifier gates on `return_is_publishable` only, § Contract) |
| AC3 — non-withheld date carries no value, never a placeholder | T-41.1.1 (classifier returns `None`, no default) + T-41.1.2 (marker/caption absent, not empty-string, when null) |
| AC4 — shared classifier, one source for both surfaces | T-41.1.1 (§ Contract classifier + § Decision rewrite of `replay_disclosures()`) |
| AC5 — run-level disclosures unaffected | T-41.1.1 (rewrite preserves exact output shape/text) verified by T-41.1.3 (existing test re-run unmodified) |
| AC6 — same register, specific cause | T-41.1.1 (classifier text is the literal existing sentence, not reworded) + T-41.1.2 (renders it verbatim) |

No AC is without a covering ticket.
