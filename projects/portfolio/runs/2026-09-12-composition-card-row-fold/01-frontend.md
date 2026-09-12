REPORT 2026-09-12-composition-card-row-fold/01
status:      DONE
verdict:     NONE

changed:
  - apps/desktop/src/features/portfolio/DashboardPanel.tsx — added `compositionExpanded` fold state and a single header/toggle button for the shared card; body wraps both sub-sections in a new `dashboard-composition-row` container, rendered only when expanded.
  - apps/desktop/src/features/portfolio/BenchmarkPositioningCard.tsx — removed its own `expanded` useState, the fold button, and the `aria-controls`/conditional-render wrapper; content now always renders (fold ownership moved to `DashboardPanel`).
  - apps/desktop/src/features/portfolio/SectorPieCard.tsx — updated the doc comment only, to describe the row layout and the shared card's single fold ownership; no behavioural change.
  - apps/desktop/src/app/styles.css — added `.dashboard-composition-row` (grid, `1fr auto 1fr`) for the side-by-side layout, and changed `.dashboard-composition-divider` from horizontal (`border-top`) to vertical (`border-left`).
  - apps/desktop/src/app/styles.css — added a `max-width: 1100px` media query collapsing `.dashboard-composition-row` to one column and the divider back to horizontal.
  - apps/desktop/src/app/styles.css — added `min-width: 0` to `.sector-pie-card` and `.benchmark-positioning-card` for grid-item safety.

verification:
  command:   cd apps/desktop && npx tsc --noEmit
  result:    PASS
  detail:    tsc --noEmit completed with no output (no errors)

contract_notes:
  - docs/contracts/dashboard-fields.md "Factor / Composition cards" table (or equivalent) still describes Benchmark Positioning as independently foldable per the prior run's contract note — that description is now stale and needs the docs lane to update it to a single shared-card fold.

pack_corrections:
  - none

handoff:
  - BenchmarkPositioningCard.test.tsx's five "fold/expand" tests (default-expanded, toggle collapses/expands, coverageNote stays visible, aria-controls) now fail because that toggle no longer exists on this component — they need to move to DashboardPanel.test.tsx, asserting the single shared toggle governs both SectorPieCard and BenchmarkPositioningCard content.
  - New coverage needed: DashboardPanel's `dashboard-composition-card` toggle defaults expanded, collapsing hides both `role="group"` sub-sections' content, and re-expanding restores both.
  - SectorPieCard.test.tsx and DashboardPanel.test.tsx (32 existing tests) pass unmodified against the new markup — confirmed by running `npx vitest run` against both files.

risks:
  - none
