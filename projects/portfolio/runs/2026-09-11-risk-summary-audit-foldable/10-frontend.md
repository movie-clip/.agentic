REPORT 2026-09-11-risk-summary-audit-foldable/10
status:      DONE
verdict:     NONE

changed:
  - apps/desktop/src/features/portfolio/RiskSummaryCard.tsx — line 95 sentence changed from "Risk contribution basis: {trust}" to "Risk contribution basis (adjusted-close price provenance only): {trust}"; `sectionTrustLabel` left untouched.

verification:
  command:   cd apps/desktop && npx tsc --noEmit
  result:    PASS
  detail:    exit_code 0, 0 failures reported.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Test lane: add/update a Vitest assertion on the rendered "Risk contribution basis" text for the `verified_adjusted_close` case, confirming the new copy does not contain the bare word "Verified" without the adjacent price-provenance qualifier (per plan § Fix 3 test coverage note).
  - Docs lane: `docs/contracts/dashboard-fields.md`'s "Risk contribution basis label" row (Risk Summary card table) needs its Notes cell updated to state the label is scoped to price-field provenance, using the exact shipped copy: "Risk contribution basis (adjusted-close price provenance only): {trust}".

risks:
  - Followed the plan's recommended option 2 (edit the surrounding sentence at RiskSummaryCard.tsx:95) rather than option 1, no deviation. Confirmed via grep that `sectionTrustLabel` (lines 23-32) has exactly one call site (line 64) before deciding not to touch it, as the order required.
  - The working tree already carried an uncommitted, unrelated diff in this file (the US-45.1 fold/expand toggle) before this order started; this order did not touch it, per non_goals. Noted so the reviewer does not mistake it for scope creep here.
