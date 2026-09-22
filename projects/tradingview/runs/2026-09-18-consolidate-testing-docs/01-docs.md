REPORT 2026-09-18-consolidate-testing-docs/01
status:      PARTIAL
verdict:     NONE

changed:
  - tradingview/docs/testing-methodology.md — rewrote as the single consolidated reference: kept the three-layers framing, paste method, and "why naive alternatives fail" verbatim in substance; rewrote layer 3 around Pine Logs as the primary live-verification technique; added a dated "Worked example: verifying mm_cot_long_short_index.pine" section (2026-09-18 evidence); merged in the "Verifying symbols, especially COT data" section from tradingview-symbol-verification.md, trimming its cross-reference framing; kept "Experimenting safely" unchanged in substance.

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Order specified verification: NONE — docs-only prose change, no Bash-runnable check applies, and this lane holds no Bash tool.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - tradingview/docs/tradingview-symbol-verification.md still exists on disk with its old (now-superseded) content — I have no delete tool. Its substance has been fully merged into the new testing-methodology.md § "Verifying symbols, especially COT data". Run: git rm tradingview/docs/tradingview-symbol-verification.md to complete the consolidation the order specifies.
  - No other file in the repo was touched: mm_cot_long_short_index.pine, its header, and docs/mm-cot-long-short-index.md are untouched, per the order's non-goals.

risks:
  - The order's "definition of done" requires tradingview-symbol-verification.md to no longer exist, but no lane in this project's roster holds a delete tool (PROTOCOL.md § "You cannot delete or rename files"). I completed the half I can (the new consolidated content is fully written and the old file's content is superseded) and surfaced the remaining `git rm` as a handoff item rather than silently leaving a stale duplicate undocumented. Reporting status: PARTIAL rather than DONE for this reason, since the file-deletion half of the definition of done was not satisfied.
