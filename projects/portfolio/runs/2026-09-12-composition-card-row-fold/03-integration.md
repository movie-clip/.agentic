REPORT 2026-09-12-composition-card-row-fold/03
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   python scripts/run_all_tests.py (via mcp__project__run_tests scope=full)
  result:    PASS
  detail:    exit_code 0, failure_count 0; backend pytest, desktop vitest, tsc --noEmit, dead-code gate (ruff+vulture+knip) all ran; tail: "All tests passed."

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - docs-engineer should update docs/contracts/dashboard-fields.md per frontend lane's (01) contract note — stale per-card fold description.
  - SHOULD_FIX (human-facing, not blocking): DashboardPanel.tsx's shared header reuses class `benchmark-card-header`, now misnamed — see § Reuse and consistency.

risks:
  - none

## Orchestrator brief
- Verdict: PASS. Frontend (01) and test (02) lanes are engineering-coherent; full suite green.
- Single fold control (`compositionExpanded` in DashboardPanel) governs both `role="group"` sub-sections; no dead state/props left in BenchmarkPositioningCard.
- Accessibility intact (§ Guardrails): aria-label/aria-expanded/aria-controls all consistent between component and tests.
- Responsive row/column behavior sound (§ Correctness against prior state): grid `1fr auto 1fr`, 1100px breakpoint collapses to one column.
- One SHOULD_FIX, not blocking (§ Reuse and consistency): reused CSS class name now misdescribes its consumer.
- § Contract alignment: no schema/type changes this slice; only the already-flagged stale doc note applies.
- § Verification: full canonical suite green, no golden drift.
- § Coverage adequacy: new tests assert against the contract, not implementation.
- § Change requests: none (no BLOCKING findings).

## Contract alignment
No backend/schema changes in this slice — purely a frontend layout/fold refactor. No `types.ts` or Pydantic schema touched. Not applicable beyond the stale contract-doc note already surfaced by the frontend lane.

## Correctness against prior state
- `DashboardPanel.tsx`: new `compositionExpanded` state + single header/toggle wraps both sub-sections in `dashboard-composition-row`, rendered only when expanded. Matches both lanes' own descriptions.
- `BenchmarkPositioningCard.tsx`: local `expanded` state, toggle button, and conditional-render wrapper fully removed; content always renders unconditionally now that the parent owns folding. Verified no orphaned `detailId`/`aria-controls` remnants.
- `SectorPieCard.tsx`: comment-only change, no behavioural diff — confirmed via diff.
- Tests: the five old per-card fold tests in `BenchmarkPositioningCard.test.tsx` were removed (including now-unused `getToggle`/`mockExposureView` helpers — confirmed no leftover unused imports), and three equivalent tests were added to `DashboardPanel.test.tsx` asserting default-expanded, collapse hides both sub-sections, re-expand restores both. Toggle name regex (`Collapse Sector and Benchmark Composition` / `Expand Sector and Benchmark Composition`) matches the `aria-label` values actually rendered in `DashboardPanel.tsx`.

## Reuse and consistency
- Fold convention (local `useState`, `aria-expanded`, no shared primitive) correctly follows the project's existing `RiskSummaryCard` (US-45.1) one-off pattern, as the code comments claim.
- SHOULD_FIX: `DashboardPanel.tsx`'s new composition-card header reuses the CSS class `benchmark-card-header` (previously scoped to `BenchmarkPositioningCard`'s own header) for a header that is no longer benchmark-specific — it now labels the shared Sector+Benchmark card. The class itself is generic (flex row, no benchmark-specific styling) so this is not a functional bug, but the name now misdescribes its consumer. A neighbour reading `DashboardPanel.tsx` sees a `benchmark-card-header` div wrapping a "Sector & Benchmark Composition" label, which reads as copy-paste rather than intentional reuse.
- No duplicated fold/formula logic found elsewhere.

## Guardrails
No trust-state, truth-class, or methodology surface touched. Guardrails 1-5 not implicated by a pure layout/fold change with no data-shape edits. Accessibility structure (role=group, aria-label, aria-expanded) confirmed intact on the remaining control and both sub-sections.

## Verification
- `mcp__project__run_tests(scope="full")` -> `exit_code: 0`, `failure_count: 0`, tail shows backend pytest, desktop vitest, `tsc --noEmit`, dead-code gate (ruff+vulture+knip) all run, ending "All tests passed."
- Confirmed no stray `dashboardGoldens.ts` drift (`git status --porcelain` on that file: empty).
- Confirmed no orphaned references to the removed `benchmark-positioning-detail` id or old per-card `dashboard-composition-card` semantics via repo-wide grep.

## Coverage adequacy
The three new `DashboardPanel.test.tsx` tests assert against the contract (toggle text/aria-expanded state, both sub-sections' visible content via role/aria-label queries) rather than implementation details (no snapshot/exact-DOM assertions), and would fail if the shared-fold requirement regressed to independent per-card folding or to no fold at all. This satisfies the definition-of-done's coverage bar.

## Change requests
- none (no BLOCKING findings; one SHOULD_FIX recorded above, not blocking)
