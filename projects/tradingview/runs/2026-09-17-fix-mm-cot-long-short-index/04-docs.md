REPORT 2026-09-17-fix-mm-cot-long-short-index/04
status:      DONE
verdict:     NONE

changed:
  - mm_cot_long_short_index.pine — header block (lines above `//@version=6`) rewritten: "WHAT THIS COMPUTES" now describes the net (long − short) index on 0..100; both `// NOTE for docs:` markers removed and replaced with correct prose; ticker strings updated `_OLD` -> `_ALL` with one added sentence on the reasoning; a named SOURCE block (Briese 2008, Williams 2005) and declared departures added, verbatim per 01-quant.md § Header text for docs.
  - docs/mm-cot-long-short-index.md — rewritten in full: "What it computes" now describes the net index; "Known limits" carries a per-finding resolution table (6 fixed/dissolved this run, FINDING 6 and the symbol-verification guardrail explicitly open, compile check explicitly outstanding); "Reproducing the fixture" now cites 01-quant.md § Worked examples and 03-test.md § Worked example by path instead of asserting no example exists.

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Order's verification field was NONE (docs-only close-out order, no Bash tool granted to this lane).

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - orchestrator: the TradingView compile check (`compile.md`) is still outstanding for this script — nothing in this run, including this docs pass, has loaded it in the editor. docs/mm-cot-long-short-index.md and the header both say so explicitly and this must not be closed out as accepted until that check runs.
  - test (future): if a `fixtures/` CSV is ever added for this script, docs/mm-cot-long-short-index.md § Reproducing the fixture needs its own update to point at it — right now it only points at the two hand-traced worked examples in the run dir.

risks:
  - none
