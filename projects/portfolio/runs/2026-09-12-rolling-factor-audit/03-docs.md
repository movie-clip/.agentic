REPORT 2026-09-12-rolling-factor-audit/03
status:      DONE
verdict:     NONE

changed:
  - docs/finance/financial-methodology.md — corrected §Statistical Factor Model → "Per-window orthogonalization" Edge Cases bullet 1: `WINDOW_MIN_OBSERVATIONS[w]` is now stated as a history-length prerequisite, not the estimation window's observation count, and the 20d window is stated as 20 observations / 17 params / 3 residual dof (per FINDING 4's own `expected` text in 02-quant-audit.md).
  - docs/tech-debt-register.md — added 10 entries, one per finding F1-F10 from run 2026-09-12-rolling-factor-audit, each carrying the defect, file:line, severity, and run origin; F2 explicitly flagged as requiring a methodology-owner ruling, not an engineering fix.

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order verification field was NONE (docs-only, no code touched)

contract_notes:
  - `statistical_factor_model.status` / `windows[].status` missing row in dashboard-fields.md:248 (02's contract_note 1) — dismissed: not added, per this order's explicit instruction not to invent a contract-table row ahead of the F1 frontend fix; logged instead as the F1 tech-debt-register entry.
  - `RollingFactorLoadingPoint.alpha` always-null / fabricated fixture value (02's contract_note 2) — dismissed: requires a schema/type/fixture code change (F7), not a doc edit; logged as the F7 tech-debt-register entry.
  - `residual_vol` missing `_pct` suffix (02's contract_note 3) — dismissed: requires a backend rename (F8), not a doc edit; logged as the F8 tech-debt-register entry.
  - types.ts optional/required mismatch on 4 of 16 factor keys (02's contract_note 4) — dismissed: requires a frontend type-file edit (F9), not a doc edit; logged as the F9 tech-debt-register entry.
  - No methodology section defines `residual_vol` (02's contract_note 5) — dismissed here as a doc edit because writing the section means composing formula wording (whether to document the current biased denominator or the fixed one, per capability-pack "flag for human" rule); folded into the F8 tech-debt-register entry and named again in handoff for the quant lane.

pack_corrections:
  - none

handoff:
  - The `residual_vol` methodology section (02's contract_note 5 / part of F3) needs the quant lane to author it, once F3's owner decision on the (n-1) vs (n-K-1) denominator is made — this docs lane cannot compose the formula per capabilities/docs.md "Auto-update vs flag-for-human."
  - F6 (test_analytics.py:7848, :7905-7907 docstrings describing an unshipped λ=0.01/25-obs/8-df mechanism) is a test-file correction, out of this order's `docs/**` scope; it needs the test lane, and is logged as its own tech-debt entry so it is not lost.
  - F2 remains blocked on a methodology-owner ruling per the audit's own § Orchestrator brief; the tech-debt entry names the three options the audit offered (withdraw/gate the 20d window, dof-adjust R², or document E[R²|null] per window) without picking one.
  - F1, F3, F5, F7-F10 all require code changes this order did not make; each has its own tech-debt-register entry with file:line for the lane that eventually picks it up.

risks:
  - The order's DoD referred to "the 5 contract_notes ... that are pure documentation corrections," citing the 20-obs/ridge-floor example — but that example is actually FINDING 4/6's territory, not literally any of 02-quant-audit.md's 5 `contract_notes` bullets, none of which are pure-prose fixes (all five either require a code change or would require inventing a contract-table row this order forbids). I applied the one genuine doc-only fix that exists (F4's Edge Cases prose) and dismissed the 5 contract_notes into tech-debt entries instead of forcing a fix; flagging this mismatch rather than silently reinterpreting the DoD's word "5."
  - The methodology doc's ridge-floor prose (line ~1212-1216) was already correct (states shipped λ=1e-5 and frames λ=0.01 as the rejected alternative) — there was no ridge-floor doc error to fix; the λ=0.01 error the audit found lives only in test_analytics.py docstrings (F6), outside this order's scope.

---

## Orchestrator brief

- 10 tech-debt-register entries added (F1-F10), each self-contained with file:line, severity, and run origin; F2 marked as owner-ruling-required, not dispatchable as an engineering CR.
- One documentation-only correction landed: financial-methodology.md's Edge Cases bullet for the rolling-window estimation now states the 20-obs/17-param/3-dof reading directly, closing the misreading FINDING 4 named.
- All 5 of 02-quant-audit.md's `contract_notes` were resolved by dismissal into the tech-debt entries above, not by editing contract docs — each required either a code change or an invented contract row this order's DoD explicitly forbade.
- Open thread for the quant lane: the `residual_vol` methodology section still does not exist; it needs composing once F3's denominator question is settled.
- Open thread for the test lane: F6's docstrings in test_analytics.py still misstate the shipped ridge floor and observation count.
- See § risks for the mismatch between the DoD's "5 contract_notes" framing and what 02-quant-audit.md's contract_notes section actually contains.
