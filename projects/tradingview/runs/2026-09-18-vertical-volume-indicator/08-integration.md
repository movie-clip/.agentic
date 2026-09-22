REPORT 2026-09-18-vertical-volume-indicator/08
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   python ../.agentic/scripts/pine_check.py *.pine --strict (run from tradingview/)
  result:    FAIL
  detail:    7 SHOULD_FIX findings across the repo, 0 BLOCKING — unchanged in count and substance from my first pass (05-integration.md). volume_profile.pine:193 P008 is the sole finding on this run's file (shifted from line 182 by the header's growth); I opened the line myself and it is still request.security_lower_tf(), the same confirmed checker false positive, not a new hit. The other 6 (strategy13_trend_carry.pine:14 P013, :73/:74 P008; systemic_stress_dashboard.pine:57-60 P008 x4) are byte-identical pre-existing findings, unrelated to this run.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Confirmed by direct read that volume_profile.pine:262-286 now matches 06-backend's description exactly: `if na(p) or na(v)` (282) increments `naIntrabars` and skips the contribution; the else branch (285-286) computes `binIdx` and accumulates, unchanged from the pre-fix arithmetic otherwise.
  - Confirmed Status wiring at lines 347-349 and the cell bgcolor at 378-380: `reason != ""` is checked before `naIntrabars > 0` in both the text ternary and the bgcolor ternary, so a flagged-but-not-n/a profile can never render as bare "OK" and an n/a profile can never render orange-not-gray. No stale or misordered read.
  - 06-backend's declared scope-fence overrun (touched 245-254 for the `naIntrabars` declaration, CR-1's fence named 262-275) is a disclosed, in-lane deviation to hold a counter the loop had nowhere else to put — not a violation, not a new CR.
  - F6 (MATERIAL) and F7 (MINOR) from 07-quant-audit.md are real and I read the header myself: lines 81-89's "Reconciliation... a closed invariant... far from 1.00... the WHOLE profile is suspect" still contradicts the now-true case where a flagged skip drops the ratio below 1.00 by design. This is quant-audit's finding, already routed to docs at close — not duplicated here.
  - Repo-wide 6 pre-existing findings on strategy13_trend_carry.pine and systemic_stress_dashboard.pine remain out of scope for this run, per my first pass — nothing to add.

risks:
  - none
