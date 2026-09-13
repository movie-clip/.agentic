REPORT 2026-09-12-rolling-factor-f1-f7/07
status:      DONE
verdict:     NONE

changed:
  - apps/desktop/src/features/portfolio/RollingFactorLoadingsCard.test.tsx — relabeled the window-level `partial` test to state it exercises a defensive branch unreachable by the current engine (FINDING 3), not a live engine state.
  - apps/desktop/src/features/portfolio/RollingFactorLoadingsCard.test.tsx — added a render case for model-level `partial` naming missing factors from `insufficient_history` for the selected window.
  - apps/desktop/src/features/portfolio/RollingFactorLoadingsCard.test.tsx — added a render case for model-level `partial` falling back to the generic tooltip when `insufficient_history` has no entry for the selected window.
  - apps/desktop/src/features/portfolio/RollingFactorLoadingsCard.test.tsx — fixed the pre-existing "no badge when window is ok" test, which now also needs model-level `status` and `insufficient_history` forced to non-degraded, since CR-1's landed fix (FINDING 1) reads model-level status too and the base fixture defaults it to `partial`.
  - apps/desktop/src/features/portfolio/RollingFactorLoadingsCard.test.tsx — extended the local `buildFactorModel` helper with an optional `factorModelOverrides` param (layered onto `createImportedStatisticalFactorModelFixture`'s output) so the model-level cases still go through the real adapter chain (`composeExposureView` / `buildExposureFactorModel`) instead of a hand-built response literal.

verification:
  command:   cd apps/desktop && npx vitest run
  result:    PASS
  detail:    43 test files passed, 394 tests passed (0 failed). Also ran `npx tsc --noEmit` clean and the file in isolation (7/7 passed) before the full run.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - `buildFactorModel` in this test file now takes an optional 2nd param `factorModelOverrides: Partial<StatisticalFactorModel>`, spread onto the fixture before the adapter chain runs.
  - Reuse that param, not a hand-built literal, for future model-level status/insufficient_history cases in this file.
  - The "no badge" case needs both `windowStatusOverrides` and `{ status: 'ok', insufficient_history: [] }` — base fixture defaults model status to `partial`.

risks:
  - Pre-existing test `does not render a Degraded badge when the selected window status is ok` was failing before my edit, from CR-1's already-landed model-level fix reading `status: 'partial'` in the base fixture regardless of the window override.
  - Fixed that pre-existing test in-scope since it's the exact gap CR-2 closes, though the order's `definition_of_done` did not name it explicitly.
  - `missing_factors: ['growth']` in the new "named" test resolves via the fixture's own 2-entry factor registry, chosen deliberately to exercise the label lookup, not the raw-key fallback.
