REPORT 2026-09-17-fix-mm-cot-long-short-index/13
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   python C:\projects\investments\.agentic\scripts\pine_check.py C:\projects\investments\tradingview\*.pine --strict
  result:    FAIL
  detail:    exit 1. mm_cot_long_short_index.pine: PASS 0 findings. strategy13_trend_carry.pine: 3 SHOULD_FIX (missing slippage :14; missing lookahead :73,:74). systemic_stress_dashboard.pine: 4 SHOULD_FIX (missing lookahead :57-:60). All 7 are the same pre-existing debt 09-integration.md already scoped out (git diff confirms both files byte-identical to the initial commit); the order's own definition_of_done names only mm_cot_long_short_index.pine as this order's concern and says not to re-raise this debt. Verdict PASS rests on the target file being 0 findings, not on repo-wide exit code — consistent with 09's judgment call.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

risks:
  - Same scoping judgment as 09-integration.md's risks: I read "confirm mm_cot_long_short_index.pine is still 0 findings" (this order's actual DoD wording) as the literal bar for PASS, not the repo-wide exit code, which the order itself tells me to expect and not re-raise.
  - I have no Pine compiler; nothing here is evidence the script compiles. The TradingView compile check remains this project's outstanding acceptance command, unchanged by this gate.
  - The two carried Open rows (08-quant-audit FINDING 8; the two other scripts' pine_check debt) are unchanged by this order and remain for the human at close-out.

## Orchestrator brief

- Verdict PASS. All four DoD checks hold: (1) `pine_check.py --strict` on mm_cot_long_short_index.pine is 0 findings (repo-wide exit is 1, but only on the same 7 pre-existing SHOULD_FIX findings in the other two untouched scripts, already tracked in run.md § Open — not re-raised here per non_goals; full output in § Verification detail); (2) header lines 6-22 state the bare defaults `088691_F_MMP_L`/`088691_F_MMP_S` and match `input.symbol(...)` at lines 82-83 exactly; (3) docs/mm-cot-long-short-index.md's symbol claims all match the current code; (4) grepped `COT2:`, `COT:`, `_ALL` across both files — every hit is contrastive/historical prose, none is a live default. See § Symbol reconciliation for the line-by-line check.
- git diff confirms only `mm_cot_long_short_index.pine` changed in the working tree (128 insertions / 42 deletions vs. HEAD); `docs/` is untracked/new. No other regression surface.
- Not re-litigated: 08-quant-audit's FINDING 8 and the two other scripts' pre-existing pine_check debt, both carried as-is in run.md § Open, per non_goals.
- Blocks dispatch: nothing. TradingView compile check remains outstanding, unchanged by this gate.
- Sections below: § Symbol reconciliation (line-by-line code/header/docs/grep check), § Verification detail (full pine_check output and the scoping argument for PASS).

---

## Symbol reconciliation

**Code** (`mm_cot_long_short_index.pine`):
- Line 82: `input.symbol("088691_F_MMP_L", ...)`
- Line 83: `input.symbol("088691_F_MMP_S", ...)`
Both bare — no exchange prefix, no `_ALL`/`_OLD`/`_OTHER` suffix.

**Header** (lines 6-22, "SYMBOLS — CONFIRMED, GUARDRAIL 3 SATISFIED"): states the defaults are `088691_F_MMP_L` / `088691_F_MMP_S`, bare, confirmed 2026-09-17 via TradingView's live symbol search and a Pine-editor paste with zero compile/runtime errors; explicitly says neither `COT2:` nor `COT:` is a valid prefix and no `_ALL`/`_OLD`/`_OTHER` suffix applies to Gold's aggregate category. Matches the code exactly.

**Docs** (`docs/mm-cot-long-short-index.md`): top summary (line 13-14), § Still open (lines 40-50), Inputs table (lines 124-125, 129-131) and § Known limits (lines 210-214, 237) all state the same bare tickers and the same 2026-09-17 confirmation, and all correctly describe the prior `COT2:..._ALL` form as what it *changed from*, not what it is now.

**Grep sweep** for `COT2:`, `COT:`, `_ALL` across both files: 3 hits in the script (lines 11, 12, 21) and 5 in the doc (lines 42, 43, 129, 130, 212, plus the findings table). Every hit is either (a) explicitly negating the prefix ("neither COT2: nor COT: is valid here"), (b) instructing a future user not to add one, or (c) describing the prior, now-superseded value in a "changed from X to Y" or findings-table context. None is a live default or an unqualified current-state claim — the leftover-reference check in the DoD is satisfied.

## Verification detail

Full `pine_check.py --strict` output, repo-wide:

```
mm_cot_long_short_index.pine: PASS 0 findings
strategy13_trend_carry.pine:14: SHOULD_FIX P013 strategy() declares no slippage
strategy13_trend_carry.pine:73: SHOULD_FIX P008 request.security() without an explicit lookahead
strategy13_trend_carry.pine:74: SHOULD_FIX P008 request.security() without an explicit lookahead
systemic_stress_dashboard.pine:57-60: SHOULD_FIX P008 request.security() without an explicit lookahead (x4)
```

`git diff --stat -- strategy13_trend_carry.pine systemic_stress_dashboard.pine` against HEAD returns empty — confirmed neither file has changed since 09-integration.md last reported the identical 7 findings. This order's own goal and non_goals name mm_cot_long_short_index.pine as the sole subject and explicitly say not to re-raise this debt; verdict PASS is scoped to that file, matching both this order's DoD and 09-integration.md's precedent.
