REPORT 2026-09-12-rolling-factor-f1-f7/13
status:      DONE
verdict:     NONE

changed:
  - docs/contracts/dashboard-fields.md — extended the "Rolling Factor Analysis" row's Notes column (line 248) with the five-value `statistical_factor_model.status` / `windows[].status` enum (`ok`, `partial`, `insufficient_history`, `degraded_unverified_return_basis`, `unavailable`), citing `risk.py:773-776`, `:954-969`, `:1086-1110`, `:1321-1373` and `diagnostics_engine.py:604`, plus the shipped UI mapping — content per 05-quant-audit.md § FINDING 2 and 01-design.md § Doc contract row.
  - <agenticRoot>/projects/portfolio/capabilities/frontend.md — applied the one pack correction in pack-corrections.md: `TrustBadge`'s type row now reads `{type: 'synthetic'|'unavailable'|'degraded', tooltip?}`, matching `TrustBadge.tsx:14`.
  - docs/tech-debt-register.md — removed the F1 row (Rolling Factor Analysis, Dashboard) and the F7 row (Rolling Factor Analysis — alpha field); both are shipped and verified (11-quant-audit.md verdict PASS, 12-integration.md verdict PASS).

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Order names verification: NONE. docs-engineer has no Bash; verified by reading all three edited files back and cross-checking against 05-quant-audit.md, 09-frontend.md, 11-quant-audit.md, 12-integration.md, and TrustBadge.tsx:14 directly.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - The one entry in pack-corrections.md (frontend.md TrustBadge type union) was verified against TrustBadge.tsx:14 and applied as given; no new corrections found while doing this close-out.
  - Two SHOULD_FIX items already carried in run.md's Open table (tooltip precedence ambiguity at the 252d window; `TrustBadge.tsx`'s stale docstring at lines 5-11) are source-code/test items outside docs/** scope for this order — not attempted here, per non_goals.
  - F2, F3, F5, F6, F8, F9, F10 tech-debt-register rows were left untouched, as scoped — none of them were reported shipped by this run's lanes.

risks:
  - none
