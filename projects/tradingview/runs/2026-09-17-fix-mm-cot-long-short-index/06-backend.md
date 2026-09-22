REPORT 2026-09-17-fix-mm-cot-long-short-index/06
status:      DONE
verdict:     NONE

changed:
  - mm_cot_long_short_index.pine:97 — added `tfTooCoarse = timeframe.in_seconds() > timeframe.in_seconds("W")` (CR-1 remedy a).
  - mm_cot_long_short_index.pine:103 — netHist push now also gated `and not tfTooCoarse`, so a coarser-than-weekly chart stops silently collecting one observation per chart bar.
  - mm_cot_long_short_index.pine:114 — `cotIndex` formula now includes `tfTooCoarse` as an explicit na-forcing condition, alongside the existing degenerate cases.
  - mm_cot_long_short_index.pine:134-135 — new `indexText`/`windowText` locals render `"n/a (chart TF > W)"` in the index and window table cells when `tfTooCoarse`, instead of a bare "n/a" indistinguishable from "still collecting".
  - mm_cot_long_short_index.pine:148-150 — table row 3's `text_color = color.white` (FINDING 4) is no longer unconditional; it is now `na` unless `cotIndex >= 80 or cotIndex <= 20`, matching exactly the branch where `bgcolor` applies a tint.
  - mm_cot_long_short_index.pine:74 — `lookbackWeeks` input gained `minval = 2` (FINDING 5), matching the treatment `staleAfterDays` already has.
  - mm_cot_long_short_index.pine:75 — `lookbackWeeks` tooltip rewritten to state the timeframe invariance holds only "AT OR BELOW W" and that above it the index reads n/a; this is an input tooltip (code), not header prose, so I edited it directly rather than leaving a NOTE.
  - mm_cot_long_short_index.pine:88-96 — added a `// NOTE for docs:` comment at the exact spot the CR-1 fix lands, naming what header lines 53-54 must say instead (invariance holds for chart TF <= "W" only, na above it).

verification:
  command:   python C:\projects\investments\.agentic\scripts\pine_check.py C:\projects\investments\tradingview\mm_cot_long_short_index.pine --strict
  result:    PASS
  detail:    exit 0, "mm_cot_long_short_index.pine: PASS 0 findings" — re-run after all edits.

contract_notes:
  - header comment block lines 53-54 ("...so it means the same thing on every chart timeframe...") now overclaims; docs must restrict it to chart TF <= "W", per the `// NOTE for docs:` comment left at mm_cot_long_short_index.pine:89-96. Out of scope for this order (header prose is docs-owned).
  - docs/mm-cot-long-short-index.md:31-35 asserts the same unqualified invariance claim (05-quant-audit.md § FINDING 1's `where:`); it needs the same TF<=W qualification plus a description of the new "n/a (chart TF > W)" table state. Out of scope here (FINDING 2/3/6/7 owner is docs, per non_goals).
  - 01-quant.md § Inputs contract and § Table contract quote the pre-CR-1 tooltip and cell text verbatim; both now lag the shipped code (tooltip reworded, index/window cells gained a third branch). A run artifact, not docs/**, so no lane action beyond awareness.

pack_corrections:
  - none

handoff:
  - The four fixed values (CR-1, FINDING 4, FINDING 5, plus the tooltip accuracy fix) all land in the same file region (:74-153); a reviewer checking CR-1 in isolation should read :88-153 together since the table-cell and cotIndex changes are shared machinery.
  - test-engineer: no fixture in this repo yet exercises the chart-TF > "W" branch; a monthly-chart scenario (or a hand trace of `tfTooCoarse` true with `net` populated) is the case CR-1 was written to cover and is not in 03-test.md.

risks:
  - I read the DoD's "do NOT edit header prose, leave a NOTE for docs" as scoped to the header comment block (lines 1-63) only, not to the `lookbackWeeks` tooltip or table cells — both are ordinary backend-owned code per project.md § Lane routing.
  - Given that reading, I edited the tooltip and table cells directly rather than leaving NOTE comments for them. If the intent was broader, that is a second read of the same instruction and should come back as a scoped correction, not a re-litigation of CR-1.
  - I have no Pine compiler. `timeframe.in_seconds()` (no argument, current chart) and `timeframe.in_seconds("W")` are documented v6 functions and this is the exact expression CR-1's remedy (a) names verbatim, but whether it evaluates as expected (e.g., on a non-standard chart timeframe string) is unexecuted.
  - I could not verify whether Pine reloads the script (resetting the `var float[] netHist`) on every chart-timeframe change, which is the assumption behind `tfTooCoarse` alone being sufficient — I did not additionally clear `netHist` when `tfTooCoarse` becomes true, reasoning from Pine's documented execution model rather than a compiled test.
  - `pine_check.py --strict` exited 0, but per backend.md this is evidence about the text only; I am not claiming the script compiles or was tested on a chart.

## Orchestrator brief

- CR-1 (BLOCKING): implemented remedy (a) exactly as named — `tfTooCoarse` guard stops the array push above "W" and forces `cotIndex` to `na`, with the table showing `"n/a (chart TF > W)"` in both the index and window rows so the reason is visible, not a bare `n/a`.
- FINDING 4 (MINOR): `text_color = color.white` is no longer unconditional; it now fires only on the same branch as the green/red `bgcolor` tint.
- FINDING 5 (MINOR): `lookbackWeeks` now has `minval = 2`.
- Header prose (lines 1-63) was not touched, per non_goals; a `// NOTE for docs:` comment at :89-96 names exactly what header :53-54 must say next. The `lookbackWeeks` tooltip WAS edited directly (see risks — a scoping judgment call, not a header edit).
- `pine_check.py --strict` exits 0, 0 findings, re-run after all edits — see verification block.
- No compile check was run or claimed; TradingView remains the acceptance command, per project.md.
