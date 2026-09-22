REPORT 2026-09-17-fix-mm-cot-long-short-index/10
status:      DONE
verdict:     NONE

changed:
  - docs/mm-cot-long-short-index.md — added a summary paragraph stating both gates (quant-audit 08, integration 09) PASSED on 2026-09-17, with what each gate actually confirmed.
  - docs/mm-cot-long-short-index.md — added new § Still open after this run, naming the three genuinely open items and pointing at the two other scripts' pre-existing pine_check debt.
  - docs/mm-cot-long-short-index.md — expanded § Known limits' Numbering note to account for the third audit (08-quant-audit.md) and its new FINDING 8, cross-referenced to § Still open after this run.
  - mm_cot_long_short_index.pine — header comment block only: removed the now-vacuous "(or coarser, within the invariant range)" parenthetical flagged in 09-integration.md risks; nothing below `//@version=6` touched.

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order's verification field is NONE; no Bash tool granted to this lane per PROTOCOL.md § 4/§ 8.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - The three carried-forward Open rows in run.md (symbol confirmation, 08-quant-audit FINDING 8, and the other two scripts' pine_check debt) are now also recorded in docs/mm-cot-long-short-index.md § Still open after this run, so a reader of the doc alone (not the run ledger) sees them.
  - The TradingView compile check is still the outstanding acceptance command for this run, per project.md's "Why this project is unusual" — nothing in this dispatch is evidence the script loads or plots.
  - A future lane that resolves 08-quant-audit.md's FINDING 8 (the 6D/7D leak) should update both the header's "WHAT DEGRADES" bullet and docs § Still open after this run item 2, not just the code — the doc's wording assumes the leak is still present.

risks:
  - none

## Orchestrator brief

Close-out reconciliation. Both gates (08-quant-audit.md, 09-integration.md)
PASSED 2026-09-17; docs/mm-cot-long-short-index.md now states that plainly and
fixed the header's vacuous "(or coarser, within the invariant range)" wording
09-integration.md's risks flagged.

New § Still open after this run in the doc names the three items from run.md's
`## Open` table (symbol confirmation unconfirmed / 08-quant-audit FINDING 8,
MINOR / TradingView compile check not run), plus a pointer to the other two
scripts' pre-existing pine_check debt — not fixed, per non_goals.

Neither file claims the script "works" or "compiles". Header edit is
comment-block-only; nothing below `//@version=6` touched. No sections in this
artifact beyond this brief.
