REPORT 2026-09-18-vertical-volume-indicator/05
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   python ../.agentic/scripts/pine_check.py *.pine --strict (run from tradingview/)
  result:    FAIL
  detail:    7 SHOULD_FIX findings across the repo, 0 BLOCKING. volume_profile.pine:182 P008 is the sole finding on this run's file — confirmed a checker false positive (see risks), not a code defect, so it does not hold the run. The other 6 (strategy13_trend_carry.pine:14 P013, :73/:74 P008; systemic_stress_dashboard.pine:57-60 P008 x4) are pre-existing, on files byte-identical to the initial commit — unrelated to this run, out of scope for this gate.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - volume_profile.pine:182 P008 is a checker false positive: request.security_lower_tf()'s real v6 signature (symbol, timeframe, expression, ignore_invalid_symbol, currency, ignore_invalid_timeframe, calc_bars_count) has no lookahead parameter.
  - I confirmed that signature independently, from my own knowledge of the v6 reference, not just by accepting the order's sourced claim. Nothing to fix in the script; no CR written.
  - This finding is already carried in run.md's Open table (should_fix, CARRIED, 03-backend + pine_check.py source) — that row is the correct home for it at close-out, not a new CR.
  - The checker's SECURITY_CALL regex matches request.security_lower_tf() identically to request.security() (scripts/pine_check.py:75, and its own test test_security_lower_tf_is_checked_too) — a real checker limitation.
  - Fixing the checker is out of this run's scope; no lane here owns pine_check.py. Worth a future checker-maintenance order.
  - Repo-wide run surfaced 6 pre-existing SHOULD_FIX findings in strategy13_trend_carry.pine and systemic_stress_dashboard.pine (missing slippage, missing explicit lookahead on genuine request.security() calls).
  - I verified via git diff against the initial commit that both files are byte-identical — untouched by this run, so not collateral damage from volume_profile.pine.
  - Not written as CRs here per "adjacent improvements are a new order, not a bonus" (PROTOCOL.md § 5). Worth a separate backlog item to the human.
  - 04-quant-audit.md's F1 (MATERIAL) and F2-F5 (MINOR) already carry their own grading and Open-table rows; I did not re-litigate them, per this order.
  - F1's shape (an na intrabar can poison a bin while Status still reads OK) is guardrail-5-adjacent and worth the human's attention at close-out, but it is quant-audit's finding to own, not mine to duplicate.
  - mm_cot_long_short_index.pine carries uncommitted working-tree changes (git status: M) unrelated to this run — it already has docs/mm-cot-long-short-index.md dated before this run started.
  - That file passes pine_check.py --strict clean (0 findings); flagging only so the orchestrator does not conflate its diff with this run's deliverable.

risks:
  - I hold Bash but not a browser/compiler; my read of request.security_lower_tf()'s signature is corroboration from training knowledge, not a fresh fetch of TradingView's live reference.
  - The compile check in TradingView remains the acceptance command per project.md, and should confirm this construct along with everything 03-backend.md and 04-quant-audit.md already flagged as unverified (tuple-return form, ignore_invalid_timeframe, nested typed arrays, str.tostring(x, format.mintick), the input.timeframe("") sentinel).
  - I did not independently re-derive the quant-audit's F1-F5 findings or their severities; I read them only to confirm they are engineering-adjacent rather than pure-formula, per this order's instruction not to re-litigate.
  - Reuse/consistency was checked by direct comparison against mm_cot_long_short_index.pine and systemic_stress_dashboard.pine's existing style (banner comments, header contract, fmt-helper pattern, var-vs-local usage, table guarded by barstate.islast).
  - volume_profile.pine matches on every point I checked against those two files — no inconsistency found.
