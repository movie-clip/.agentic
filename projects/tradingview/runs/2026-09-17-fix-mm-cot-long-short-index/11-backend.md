REPORT 2026-09-17-fix-mm-cot-long-short-index/11
status:      DONE
verdict:     NONE

changed:
  - tradingview/mm_cot_long_short_index.pine:81 — `mmLongSymbol` default now `088691_F_MMP_L`, bare, no prefix and no suffix.
  - tradingview/mm_cot_long_short_index.pine:82 — `mmShortSymbol` default now `088691_F_MMP_S`, bare, no prefix and no suffix.

verification:
  command:   python C:\projects\investments\.agentic\scripts\pine_check.py C:\projects\investments\tradingview\mm_cot_long_short_index.pine --strict
  result:    PASS
  detail:    PASS 0 findings, exit 0.

contract_notes:
  - docs/mm-cot-long-short-index.md lines 42, 113, 114 still cite `COT2:088691_F_MMP_L_ALL` / `COT2:088691_F_MMP_S_ALL` — now stale against the code on both the prefix and the suffix, a docs-lane fix.
  - The script's own header (lines 10, 16, not touched per non_goals) still says "COT2:088691_F_MMP_L_ALL / _S_ALL" and instructs the user to "look through the COT2-prefixed results" — now stale against the bare-ticker code, a docs-lane fix.

pack_corrections:
  - none

handoff:
  - Next docs dispatch should reconcile header/doc text against the code as it now stands (`088691_F_MMP_L` / `088691_F_MMP_S`, no prefix, no suffix) — see § Two-round correction.
  - The coordinator reported having applied both bare strings directly in TradingView's Pine editor with zero compile/runtime errors, and independently confirmed via TradingView's live symbol search that "(All)" is description prose, not part of the ticker — this lane did not and cannot verify that itself, having no browser tool.

risks:
  - This is the second round of this symbol correction: my first edit (this same report, prior version) stripped only the `COT2:` prefix and kept `_ALL`, per the order's own quoted strings being stale against the file at that time — see § Two-round correction.
  - The coordinator has now stated the `_ALL` suffix is also wrong and supplied its own independent TradingView symbol-search verification for the fully bare form; I applied that correction as given rather than re-deriving or second-guessing it, per guardrail 3's rule against reconstructing symbols myself.
  - I still have not verified either ticker resolves myself; no lane here holds a browser tool. The compile check in TradingView remains the project's acceptance command per project.md, independent of what any lane's report says.

## Orchestrator brief

Second edit to the same two lines in one order: line 81/82 are now `input.symbol("088691_F_MMP_L", ...)` / `input.symbol("088691_F_MMP_S", ...)` — fully bare, no exchange prefix and no `_ALL` suffix — per the coordinator's own live TradingView symbol-search verification, relayed after my first edit's risk flag. Static check passes clean. See § Two-round correction for why this took two rounds; docs/header still say `COT2:..._ALL` and need a follow-up docs dispatch.

## Two-round correction

Round 1 (this order, as originally dispatched): the order's DoD quoted the
existing defaults as `"COT:088691_F_MMP_L"` / `"COT:088691_F_MMP_S"`, but the
file had never held that literal text at any commit — the actual default was
`COT2:088691_F_MMP_L_ALL` / `COT2:088691_F_MMP_S_ALL` (confirmed via
`git log -p`). I resolved that mismatch by reading run.md's v3 replan
("neither `COT2:` nor `COT:` is a valid exchange prefix... resolves bare, with
no exchange prefix"), stripped only the `COT2:` prefix, and kept `_ALL` since
it was a separately audited correction (FINDING 6) the order's text gave no
reason to reverse. I flagged this as an open question for the human to
confirm rather than a settled fact.

Round 2 (this message): the coordinator confirmed, from its own live
TradingView symbol search plus a direct Pine-editor compile/runtime check of
both bare strings, that `_ALL` is not a real suffix here — "(All)" is prose in
the search result's description column, not part of the ticker, and only
`_OLD` / `_OTHER` are real suffixes for the crop-year sub-breakouts the
aggregate category has none of. That is exactly the missing confirmation
round 1's risks section asked for, so I applied the fully bare form as given:
`088691_F_MMP_L` / `088691_F_MMP_S`. Static check re-run and still PASS 0
findings after this change.
