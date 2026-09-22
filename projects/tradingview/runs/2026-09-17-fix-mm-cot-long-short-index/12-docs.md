REPORT 2026-09-17-fix-mm-cot-long-short-index/12
status:      DONE
verdict:     NONE

changed:
  - tradingview/mm_cot_long_short_index.pine:6-21 — header's "VERIFY THE SYMBOLS BEFORE TRUSTING THIS" block replaced with "SYMBOLS — CONFIRMED, GUARDRAIL 3 SATISFIED", stating the bare confirmed tickers and the 2026-09-17 live-search + Pine-editor confirmation.
  - tradingview/mm_cot_long_short_index.pine:11,20-21 — CFTC-code remediation instructions updated to point at the bare-ticker form (no `COT2:`/`COT:` prefix, no `_ALL`/`_OLD`/`_OTHER` suffix unless TradingView's search shows one).
  - tradingview/docs/mm-cot-long-short-index.md — top summary changed from "five fixed / one open (FINDING 6)" to "six fixed, none open"; "Still open after this run" section now leads with a RESOLVED note for FINDING 6/guardrail 3 and lists the remaining two open items (FINDING 8 leak; whole-script compile check) as the only open ones.
  - tradingview/docs/mm-cot-long-short-index.md — Inputs table: `mmLongSymbol`/`mmShortSymbol` defaults changed from `COT2:088691_F_MMP_L_ALL` / `COT2:088691_F_MMP_S_ALL` to bare `088691_F_MMP_L` / `088691_F_MMP_S`; the table's changelog note updated to describe the full prefix+suffix change.
  - tradingview/docs/mm-cot-long-short-index.md — § Known limits intro paragraph, the prior-FINDING-6 table row, the summary line beneath the table, and the bar-stamping paragraph's stray "COT2 weekly bar" reference all updated to the resolved/bare-ticker state.

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Order's verification field is NONE; this lane holds no Bash tool in any case. No claim is made that the script compiles — only that these two symbol strings were confirmed per 11-backend.md and run.md's v3 row.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - The TradingView compile check for the script as a whole is still outstanding and remains the project's acceptance command (project.md § "Why this project is unusual"); nothing in this order performed or claims it.
  - 08-quant-audit.md § FINDING 8 (6D/7D chart-timeframe leak) remains open exactly as before, untouched by this order — carried in run.md's Open table.

risks:
  - TradingView's symbol database is not under this repo's control; if it ever renumbers or retires `088691_F_MMP_L` / `088691_F_MMP_S`, today's confirmation (2026-09-17) would go stale silently until someone re-checks it in the live symbol search.
