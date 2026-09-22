REPORT 2026-09-17-fix-mm-cot-long-short-index/02
status:      DONE
verdict:     NONE

changed:
  - mm_cot_long_short_index.pine — implemented the `var float[] netHist` weekly-observation window gated on `barstate.isconfirmed`, replacing `ta.lowest`/`ta.highest` (FINDING 1 fix).
  - mm_cot_long_short_index.pine — replaced per-side gross long/gross short indices with `net = mmLongPos - mmShortPos` rescaled 0..100, with `na` on unresolved symbol, misaligned legs, incomplete window, or `hi==lo` (D-1).
  - mm_cot_long_short_index.pine — removed the two-plot green/red pair and the ±80/0 hlines; added the single `MM Net COT Index` plot and the 80/50/20 guide lines (FINDING 2, FINDING 4).
  - mm_cot_long_short_index.pine — replaced the 2x4 table with the 2x6 table: gross long, gross short, net, index, window count, and "as of" date with a `staleAfterDays`-driven STALE flag (FINDING 8).
  - mm_cot_long_short_index.pine — updated `mmLongSymbol`/`mmShortSymbol` defaults from `_OLD` to `_ALL`, added the `staleAfterDays` input, and rewrote the `lookbackWeeks` tooltip (FINDING 6, FINDING 8, Inputs contract).
  - mm_cot_long_short_index.pine — added explicit `lookahead = barmerge.lookahead_off` to both `request.security()` calls, which now request `[close, time]` tuples (FINDING 7).
  - mm_cot_long_short_index.pine — left the header prose untouched per non_goals; added two `// NOTE for docs:` comments flagging the now-stale ticker-suffix admission and the "WHAT THIS COMPUTES" paragraph.

verification:
  command:   python C:\projects\investments\.agentic\scripts\pine_check.py C:\projects\investments\tradingview\mm_cot_long_short_index.pine --strict
  result:    PASS
  detail:    exit 0, "mm_cot_long_short_index.pine: PASS 0 findings" — no BLOCKING or SHOULD_FIX findings; both request.security() calls now carry an explicit lookahead so the prior P008 hits are gone.

contract_notes:
  - mm_cot_long_short_index.pine — `mmLongSymbol`/`mmShortSymbol` defaults changed `_OLD` -> `_ALL`; no `docs/<slug>.md` exists yet to update (per 01-quant.md's own contract_notes).
  - mm_cot_long_short_index.pine — two plots (`MM Long Index`, `MM Short Index`) removed and replaced by one plot (`MM Net COT Index`); any saved chart layout referencing the old plot names will not pick up the new one.
  - mm_cot_long_short_index.pine — new input `staleAfterDays` added to the settings dialog; it did not exist before, so no existing setting is reset, but the dialog's shape changed.
  - mm_cot_long_short_index.pine — the header's "WHAT THIS COMPUTES" paragraph and the "_OLD" defaults in the symbol admission are now stale; two `// NOTE for docs:` comments mark where, and 01-quant.md § Header text for docs carries the replacement.

pack_corrections:
  - none

handoff:
  - docs: 01-quant.md § Header text for docs carries the verbatim replacement for the "WHAT THIS COMPUTES" paragraph and the ticker-suffix line inside the existing admission block; the two `// NOTE for docs:` comments in the file mark exactly where.
  - test: 01-quant.md § Worked examples has two full hand-computed series (5-week and 12-week) plus four degenerate check vectors to cover; no `fixtures/` directory exists yet.
  - orchestrator: the compile check in TradingView is still required before this is accepted; no lane in this dispatch holds a browser tool.

risks:
  - I cannot compile or open this in TradingView; `pine_check.py --strict` passing is evidence about the text only, not that the script loads or plots correctly.
  - `_ALL` symbol defaults are a reasoned correction from CFTC's report structure, not a confirmation against TradingView's symbol search; guardrail 3 remains unmet exactly as 01-quant.md flags.
  - The specified `lookbackWeeks` tooltip text used markdown emphasis (`**COT reports**`, backtick `n/a`) that Pine's plain-text tooltip does not render; I stripped the markdown syntax and kept the words unchanged rather than reproducing literal asterisks/backticks on screen.
  - I added a `tooltip=` to the new `staleAfterDays` input (justification prose from 01-quant.md), though that section's literal constructor showed none; backend.md requires a tooltip on a judgement-call default, so I treated this as a compatible addition, not a deviation.
  - Whether `request.security()` with `ignore_invalid_symbol = true` returns `[na, na]` cleanly for a tuple expression, as opposed to erroring, is documented behaviour I could not compile-check, per 01-quant.md's own stated risk.
