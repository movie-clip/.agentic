REPORT 2026-09-12-rolling-factor-f1-f7/09
status:      DONE
verdict:     NONE

changed:
  - apps/desktop/src/features/portfolio/RollingFactorLoadingsCard.tsx — gated the model-level `partial` badge branch on `(missingFactorKeysForWindow?.length ?? 0) > 0` instead of `modelTrustStatus === 'partial'`, per FINDING 4's exact expected fix.
  - apps/desktop/src/features/portfolio/RollingFactorLoadingsCard.tsx — removed the generic fallback tooltip text from `modelPartialTooltip`, since the branch is now unreachable without a non-empty `missingFactorLabelsForWindow`.

verification:
  command:   cd apps/desktop && npx tsc --noEmit
  result:    PASS
  detail:    clean run, exit code 0, no diagnostics printed.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - RollingFactorLoadingsCard.test.tsx:106 must invert to assert `queryByText('Degraded')` is null for the short-history-only fixture (150/100/40-day cases, all 16 proxies present) — named in CR-3 and 08-quant-audit.md § FINDING 4, owned by the test lane.

risks:
  - Removed the generic fallback tooltip text rather than leaving it as dead code, per the order's discretion clause.
  - No TypeScript narrowing gap from that removal: `modelPartialTooltip` is a plain string, not a conditional type, so nothing depends on the old ternary for type safety.
  - The tooltip string is only read inside the branch now gated on `missingFactorKeysForWindow.length > 0`, so it is always populated with at least one label when it renders.
