REPORT 2026-09-11-risk-summary-audit-foldable/05
status:      DONE
verdict:     NONE

changed:
  - apps/desktop/src/features/portfolio/RiskSummaryCard.tsx — added `expanded` state (default `true`), a toggle button in the header with `aria-expanded`/`aria-controls`, and wrapped the stat-row grid in `{expanded && (...)}`.

verification:
  command:   cd apps/desktop && npx tsc --noEmit
  result:    PASS
  detail:    exit_code 0, 0 failures

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - RiskSummaryCard.tsx is not in `designSystem.audit.test.ts`'s `ALL_CARD_FILES` (Dashboard tab, legacy CSS-class pattern per the frontend pack's "Do not opportunistically migrate" — confirmed by reading the file's list directly), so no audit-check regression risk from this change; the story's test plan still calls for the audit file to keep passing, which it does unmodified.
  - Toggle button uses `id="risk-summary-detail"` as `aria-controls` target on the stat-row `<div>`, mirroring `DrawdownAnalyticsCard.tsx`'s `aria-expanded`/`aria-controls`/`aria-label` convention (drawer `id` + toggle button), per AC5 and the story's Context section.
  - Default state is `useState(true)`, so first render with data shows all rows unchanged (AC1); collapsing only removes the `benchmark-card-summary` div, never the header or the "Risk contribution basis" trust paragraph (AC4).
  - The `unavailable` early-return branch (lines 51-60) was not touched — no toggle button exists on that path (AC8).
  - T-45.1.2 (test-engineer) needs: default-expanded assertion, toggle-collapse/re-expand assertions, `aria-expanded` transition assertions on the new button, collapsed-header-content assertion (title + trust label present, stat rows absent), unavailable-state-has-no-toggle assertion, and a Dashboard-level sibling-card-unaffected assertion — all named in the story's own test plan.

risks:
  - none
