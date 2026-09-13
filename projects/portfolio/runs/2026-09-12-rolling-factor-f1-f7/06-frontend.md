REPORT 2026-09-12-rolling-factor-f1-f7/06
status:      DONE
verdict:     NONE

changed:
  - apps/desktop/src/features/portfolio/RollingFactorLoadingsCard.tsx — trust badge now also degrades on `statisticalFactorModel.status` (model-level `'partial'` or `'degraded_unverified_return_basis'`), not window-level status alone.

verification:
  command:   cd apps/desktop && npx tsc --noEmit
  result:    PASS
  detail:    exit_code 0, 0 failures reported by the project tool server's typecheck run

contract_notes:
  - none

pack_corrections:
  - capabilities/frontend.md § The eight primitives — table states `TrustBadge` accepts `{type: 'synthetic'|'unavailable'}`; `TrustBadge.tsx:14` also has a `'degraded'` member already in the union and in production use (this file, pre-existing). Replace with `{type: 'synthetic'|'unavailable'|'degraded'}`.

handoff:
  - New model-level `'partial'` branch and its distinct tooltip (RollingFactorLoadingsCard.tsx, `modelPartialTooltip`) are untested — no *.test.tsx edits are in this lane's scope; the test lane should cover both the missing-factors-named case and the generic-fallback case (when `insufficient_history` has no entry for the selected window).

risks:
  - Model-level `'partial'` tooltip prose is my own judgment per the order's explicit delegation (audit wanted a design ruling; order overrode that). Names missing factor labels when available, else a generic fallback sentence.
  - Precedence when both levels are degraded at once is unspecified by the order; I check window-level status first (already audit-clean), model-level as fallback, so window-level tooltips win on overlap.
