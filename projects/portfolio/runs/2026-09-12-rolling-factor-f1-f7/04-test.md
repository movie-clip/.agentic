REPORT 2026-09-12-rolling-factor-f1-f7/04
status:      DONE
verdict:     NONE

changed:
  - apps/desktop/src/app/primitives/TrustBadge.test.tsx — added `renders_degraded_label` case mirroring `renders_synthetic_label`/`renders_unavailable_label`.
  - apps/desktop/src/features/portfolio/RollingFactorLoadingsCard.test.tsx — added three render cases (no badge at `ok`, badge at `partial`, badge at `degraded_unverified_return_basis`) built via the real adapter chain.
  - apps/desktop/src/test/portfolioFixtures.ts — removed the fabricated `alpha: 0.0002`/`alpha: null` entries; exported `createImportedStatisticalFactorModelFixture` with a new optional `windowStatusOverrides` param so tests can force a window's `status` without hand-building a parallel fixture.
  - apps/desktop/src/features/portfolio/FactorDriftSummaryCard.test.tsx — removed `'alpha'` from `REQUIRED_LOADING_KEYS`.

verification:
  command:   cd apps/desktop && npx vitest run
  result:    PASS
  detail:    43 test files passed, 392 tests passed, 0 failed. Also ran narrow: TrustBadge.test.tsx (5 tests), RollingFactorLoadingsCard.test.tsx (5 tests), FactorDriftSummaryCard.test.tsx (8 tests), all green. check_gates(): deadcode clean, typecheck 0 errors, goldens_drifted false.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - New shared fixture: `createImportedStatisticalFactorModelFixture` in `portfolioFixtures.ts` is now exported and takes an optional `windowStatusOverrides: Partial<Record<20 | 60 | 252, string>>`.
  - Example: `createImportedStatisticalFactorModelFixture({ 60: 'degraded_unverified_return_basis' })` forces one window's status without a parallel literal; reuse this for any future window-status test case.
  - `RollingFactorLoadingsCard.test.tsx`'s new cases build `factorModel`/`result` via `createExposureEngineFixture()` + a shallow-overridden `createDiagnosticsEngineFixture()` + `composeExposureView` + `buildExposureFactorModel`, per 01-design.md § Reuse and placement — reuse this pattern for any further RollingFactorLoadingsCard render tests instead of hand-building `ExposureFactorModelResponse`.
  - Backend-side `test_analytics.py`'s `"alpha": None,` key (test_analytics.py:5419 per 01-design.md) was already absent when this lane started — grepped and confirmed removed, so no backend test edit was needed from this lane (backend/test_analytics.py was outside this order's scope in any case).

risks:
  - none
