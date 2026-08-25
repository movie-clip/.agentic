REPORT 2026-08-25-leftover-findings-fold-in/07
status:      DONE
verdict:     NONE

## Orchestrator brief
Fixed statement_importer.py per CR-1 against AUDIT-quant.md Finding 1: combine_imported_snapshots now
raises ValueError on ambiguous same-account combines instead of silently summing. All 25
test_importer.py tests pass unmodified, including the multi-broker fixture. Two named sections below
carry detail behind short handoff/risks bullets, not new findings:
- § Route mapping — confirms the existing HTTP 400 mapping needed no change (handoff bullet 4).
- § Generalization judgment — flags that the fix's guard applies to any >1-length combine, not just
  literal pairs, for human confirmation against the DoD's 2-input framing (risks bullet 1).

changed:
  - services/quant-engine/app/services/statement_importer.py — _validate_compatible_snapshots raises ValueError when any combine input has a falsy account_id, instead of silently treating it as a distinct account.

verification:
  command:   cd services/quant-engine && python -m pytest app/tests/test_importer.py -v
  result:    PASS
  detail:    25 passed, 0 failed, including test_three_broker_combine_ib_ff_espp unmodified and passing.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Ad hoc repro script (not committed) confirmed all 3 AUDIT-quant.md Finding 1 cases: account_id="U1234567" on both sides -> unaffected, positions=[('AAPL', 15.0)] latest-wins, ending_nav=3000.0.
  - Same script: account_id=None on both sides -> now raises ValueError instead of summing to positions=[10,15]/ending_nav=5000.0.
  - Same script: account_id="U1234567" on base only, None on new -> now raises ValueError, same as the both-None case.
  - Permanent regression tests for these 3 cases are test-engineer's follow-up (dispatch 08), per this order's non_goals — no test files were touched here.
  - The ValueError propagates unchanged through the existing POST /portfolios/import/combine-snapshots route's ValueError->HTTPException(400) mapping — no route/schema change needed. See § Route mapping.
  - python scripts/detect_deadcode.py --strict run manually (not this order's verification command) and confirmed clean after the edit.

risks:
  - The fix raises whenever len(snapshots)>1 and ANY snapshot's account_id is falsy, not just the literal 2-input add_snapshot case the DoD examples name. See § Generalization judgment.
  - _latest_snapshot_by_account's fallback branch (Finding 1's root cause) is now unreachable via combine_imported_snapshots, since validation runs first — left untouched, scope named no refactor of it.

## Route mapping
Traced imports.py's /combine-snapshots route (unedited): `except ValueError as exc: raise HTTPException(status_code=400, detail=str(exc)) from exc`. This already existed before this change (confirmed by AUDIT-quant.md's US-40.2 trace) and needed no edit — the new ValueError from statement_importer.py surfaces through it identically to the currency-mismatch ValueError it already handled, reaching the frontend's setImportError degradation path unchanged.

## Generalization judgment
The order's worked examples are all 2-input (base + new), matching the add_snapshot flow. combine_imported_snapshots's signature takes an arbitrary-length list (also used by the initial multi-file import path). I applied the "falsy account_id is ambiguous" rule to any snapshot in a >1-length combine, not just pairs, because the same reasoning applies: _latest_snapshot_by_account cannot distinguish "same account, unparsed id" from "another account, unparsed id" regardless of how many other snapshots are present. This does not change the tested 3-broker case (all three have valid distinct account_ids, so nothing is falsy). Flagging for human confirmation since the DoD language was framed around two inputs specifically.
