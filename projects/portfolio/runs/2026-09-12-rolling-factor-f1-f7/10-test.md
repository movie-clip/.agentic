REPORT 2026-09-12-rolling-factor-f1-f7/10
status:      DONE
verdict:     NONE

changed:
  - apps/desktop/src/features/portfolio/RollingFactorLoadingsCard.test.tsx — inverted the test at ~line 106 (short-history-only, all-16-proxies-present fixture): now asserts `queryByText('Degraded')` is null, and renamed/re-commented it to describe FINDING 4's fixed behavior instead of pinning the false generic-fallback tooltip.

verification:
  command:   cd apps/desktop && npx vitest run
  result:    PASS
  detail:    43 test files passed, 394 tests passed, 0 failed.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

risks:
  - The "named missing factors" test (~line 93-104) and the "defensive window-level partial branch" test (~line 80-85) were reviewed against the shipped RollingFactorLoadingsCard.tsx and both still reflect reachable/documented branches after CR-3's fix — no change needed to either.
  - The generic-fallback-tooltip case was inverted in place, per CR-4's exact wording, rather than deleted as a separate step.
  - That single inversion also satisfies the work order's "adjust the now-untestable fallback case" clause — one test, one fix, no separate deletion needed.
