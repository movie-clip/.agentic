REPORT 2026-09-12-rolling-factor-f1-f7/03
status:      DONE
verdict:     NONE

changed:
  - apps/desktop/src/app/primitives/TrustBadge.tsx — added `'degraded'` to `TrustType` union and `LABELS.degraded = 'Degraded'`, per the primitive's own docstring extension path, no new CSS.
  - apps/desktop/src/features/portfolio/RollingFactorLoadingsCard.tsx — imports `TrustBadge`, derives a degraded badge from `selectedWindowSummary.status` with the two named tooltips, renders it next to `panel-label` in the header.
  - apps/desktop/src/features/portfolio/types.ts — removed `alpha: number | null` from all three `rolling_loadings_{20,60,252}d` element types (F7).

verification:
  command:   cd apps/desktop && npx tsc --noEmit
  result:    PASS
  detail:    exit code 0, no diagnostics emitted; also confirmed via mcp__project__run_tests(scope="typecheck") — exit_code 0, failure_count 0

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Test lane owes `TrustBadge.test.tsx` a `renders_degraded_label` case mirroring the existing `synthetic`/`unavailable` cases.
  - Test lane owes `RollingFactorLoadingsCard.test.tsx` render cases: no "Degraded" text at `'ok'`; "Degraded" present at `'partial'`; "Degraded" present at `'degraded_unverified_return_basis'` (needs a new fixture window override, none exists yet).
  - Test lane owes removal of the `alpha: 0.0002`/`alpha: null` entries at `portfolioFixtures.ts:958-960` and of `'alpha'` from `REQUIRED_LOADING_KEYS` at `FactorDriftSummaryCard.test.tsx:13`.
  - `portfolioFixtures.ts:958-960` still fabricates `alpha` keys but does not fail `tsc --noEmit` today — the literal is returned from an untyped function, so no excess-property check fires at its construction site.

risks:
  - none
