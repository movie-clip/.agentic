REPORT 2026-08-24-sbio-still-unclassified-bug/T2
status:      DONE
verdict:     NONE

changed:
  - apps/desktop/src/test/portfolioFixtures.ts — reviewed prior attempt's 9-line diff; confirmed correct (verified below)
  - apps/desktop/src/app/App.test.tsx — reviewed prior attempt's diff; confirmed all 5 coverage points present and correctly asserting
  - apps/desktop/src/app/portfolioWorkspaceStorage.test.ts — reviewed prior attempt's diff; confirmed coverage point 1 and persistence half of point 3 present

verification:
  command:   cd apps/desktop && npx tsc --noEmit ; npx vitest run ; cd .. && python scripts/run_all_tests.py
  result:    PASS
  detail:    tsc: 0 errors. vitest: 37 files, 337 tests, all passed. run_all_tests.py: backend 905 passed, frontend 337 passed (37 files), dead-code gate clean (ruff/vulture/knip), tsc clean, "All tests passed."

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - No new shared fixtures added; App.test.tsx's buildSbioCorrectExposureOverride/buildSbioLossyExposure are test-local helpers built on the existing createExposureEngineFixture.
  - portfolioWorkspaceStorage.test.ts's createFakePortfolioDb() (one Map backing both withStore/withStores) is local to that file — worth promoting to a shared util if reused again.
  - dashboardGoldens.ts unaffected by this work — git status confirms no diff after the full run_all_tests.py regen, no golden drift to clean up.

risks:
  - none
