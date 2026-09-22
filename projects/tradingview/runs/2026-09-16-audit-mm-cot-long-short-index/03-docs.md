REPORT 2026-09-16-audit-mm-cot-long-short-index/03
status:      DONE
verdict:     NONE

changed:
  - C:\projects\investments\tradingview\docs\mm-cot-long-short-index.md — created; first docs/<slug>.md in the repo, records what the script computes today and all 8 numbered findings from 02-quant-audit.md as an unfixed audit record.

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Order's verification field was NONE; docs-engineer has no Bash tool per protocol § 8.

contract_notes:
  - docs/mm-cot-long-short-index.md now exists and is stale the moment any of FINDINGS 1-8 are fixed in mm_cot_long_short_index.pine — whichever lane closes a finding must update the matching section here rather than leave it describing a defect that no longer exists.
  - FINDING 3's human decision (net-position rescale vs. relabel as gross-long/gross-short variant) gates FINDING 5 (citation) and touches the header's "WHAT THIS COMPUTES" paragraph and § Sources / § What it computes in the new doc — both need a follow-up docs pass once the human rules on it.

pack_corrections:
  - none

handoff:
  - The script header itself (mm_cot_long_short_index.pine:1-26) was not touched, per non_goals — it still reads exactly as before, including the unverified-symbol admission. A future backend/docs order should update the header's "WHAT THIS COMPUTES" citation once FINDING 3 is decided and FINDING 6's symbol is re-verified in TradingView's symbol search.
  - No fixture exists for this script (no strategy(), no CSV) — § Reproducing the fixture in the new doc states this explicitly rather than leaving section 6 silently empty.
  - Test lane (when dispatched against any FINDING fix) should cover: FINDING 1's timeframe-dependent window (verify lookbackWeeks means weeks on a non-weekly chart after a fix), and FINDING 2/4's guide-line semantics after relabeling or rescaling.

risks:
  - none
