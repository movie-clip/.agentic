REPORT 2026-09-12-composition-card-row-fold/02
status:      DONE
verdict:     NONE

changed:
  - apps/desktop/src/features/portfolio/BenchmarkPositioningCard.test.tsx — removed the five fold/expand tests (default-expanded, collapse/expand, coverageNote-visible, aria-controls) and the now-unused `getToggle`/`mockExposureView` helpers, since the component no longer owns a toggle.
  - apps/desktop/src/features/portfolio/DashboardPanel.test.tsx — added three tests under a new "composition card fold/expand" section: default expanded showing both `role="group"` sub-sections, collapsing hides both, re-expanding restores both.

verification:
  command:   cd apps/desktop && npx vitest run
  result:    PASS
  detail:    43 test files passed, 388 tests passed, 0 failed, 0 skipped

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - No new shared fixture or helper added — reused `mockExposureView` (composeExposureView + existing fixtures) already present in DashboardPanel.test.tsx.
  - New tests match the toggle by its `aria-label` text (`Collapse/Expand Sector and Benchmark Composition`).
  - No `aria-controls`/`getElementById` assertion was re-added, since DashboardPanel conditionally renders the detail block rather than always mounting it.

risks:
  - none
