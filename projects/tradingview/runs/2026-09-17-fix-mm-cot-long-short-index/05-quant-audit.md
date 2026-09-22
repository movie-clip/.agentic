REPORT 2026-09-17-fix-mm-cot-long-short-index/05
status:      DONE
verdict:     FAIL

changed:
  - none

verification:
  command:   python C:\projects\investments\.agentic\scripts\pine_check.py C:\projects\investments\tradingview\mm_cot_long_short_index.pine --strict
  result:    PASS
  detail:    exit 0, "mm_cot_long_short_index.pine: PASS 0 findings" — re-run by me, not reused from 02-backend.md. Anchors: Briese/Williams 0..100 net COT Index definition re-implemented independently in Python; my own 12-week and 60-week synthetic series (no numbers shared with 01-quant or 03-test); a bar-by-bar emulation of the shipped Pine across weekly / daily / monthly chart timeframes; CFTC release mechanics; Pine v6 documented request.security and var-array rollback semantics.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - FINDING 1 (MATERIAL, :89-96 + header :53-54) — the weekly window is timeframe-invariant only for chart TF <= "W"; on a monthly chart it collects one observation per month. Owner: backend. BLOCKING. See § FINDING 1 — partially resolved.
  - FINDING 1 evidence — same data, same date: weekly chart reads 4.06, monthly chart reads 9.25, "12 weeks" spans 48. See § FINDING 1 — partially resolved.
  - FINDING 2 (MINOR, docs/mm-cot-long-short-index.md:28-34,54,58,125) — every `file:line` citation in the doc is 26-34 lines short of the actual code. Owner: docs. See § FINDING 2.
  - FINDING 3 (MINOR, docs/mm-cot-long-short-index.md:8) — "Six of the audit's eight findings are resolved" contradicts its own table, which lists seven. Owner: docs. See § FINDING 3.
  - FINDING 4 (MINOR, :137) — `text_color = color.white` on the index cell is not in the Table contract and is unreadable on a light chart theme when untinted. Owner: backend. See § FINDING 4.
  - FINDING 5 (MINOR, :74-75) — `lookbackWeeks` has no `minval`; 0 or negative drives `array.min`/`array.max` on an empty array. Owner: backend. See § FINDING 5.
  - FINDING 6 (MINOR, header :52-62) — the header does not disclose that the live-bar reading ranks against W+1 observations and can move at the weekly close. Owner: docs. See § FINDING 6.
  - FINDING 7 (MINOR, :107 + tooltip :72) — staleness is measured from the weekly bar's OPEN time, so the "~13 days" justification holds on sub-weekly charts only. Owner: docs. See § FINDING 7.
  - Prior-audit status: 1 PARTIALLY RESOLVED; 2,3,4,5,7,8 RESOLVED; 6 OPEN by design. See § Prior findings, re-checked against current code.

risks:
  - 01-quant.md's falsification test ("weekly chart vs 1-hour chart must be identical") cannot observe § FINDING 1, because both sides of it are sub-weekly. A criterion that cannot produce the falsifying observation is the gates.md § 2 trap.
  - I have no Pine compiler. Whether `array.min()` on an empty array raises a runtime error or returns `na` is unexecuted; FINDING 5 stands either way, since neither outcome is a defined index.
  - I have no browser tool, so the COT2 `_ALL` tickers are still unconfirmed and guardrail 3 is still unmet. Expected per the order's non_goals; recorded, not re-flagged as new.
  - Whether `request.security()` with `ignore_invalid_symbol = true` returns `[na, na]` for a tuple expression is unexecuted, carried from 01-quant.md and 02-backend.md. My § FINDING 1 emulation assumes it does; the finding does not depend on it.
  - `stale` reads `timenow`, which is wall-clock, so on every historical bar `stale` is true. It is only consumed under `barstate.islast`, so this is harmless today, but it makes `stale` unsafe to reuse in any future alert or plot.

## Orchestrator brief

- Verdict FAIL, on one MATERIAL finding. Six MINOR findings do not block.
- `pine_check.py --strict` re-run by me: exit 0, 0 findings. 02-backend's PASS is confirmed, independently.
- Prior FINDING 1 is PARTIALLY RESOLVED: the array fixes chart TF <= "W" and leaves chart TF > "W" broken. Numerically: 4.06 (weekly) vs 9.25 (monthly) on identical data.
- Prior FINDINGS 2, 3, 4, 5, 7, 8 are RESOLVED, each verified against the current code, not against backend's or docs' claim.
- Prior FINDING 6 remains OPEN, correctly documented, expected per the order.
- `barstate.isconfirmed` gate is present and correctly placed at :93, guarding the mutation itself — not a comment.
- Repaint: no closed bar rewrites, on either evaluation path. Reasoned from Pine's execution model, in § Repaint re-verification.
- Arithmetic: my independent implementation reproduces 01-quant's and 03-test's vectors exactly, and my own series reproduces against the definition. The rescale is correct.
- Neither the header nor `docs/mm-cot-long-short-index.md` claims the script works or compiles. Both are explicit that only the static check ran. No overclaim on that axis.
- Lane split: new FINDING 1 and FINDINGS 4, 5 are backend. FINDINGS 2, 3, 6, 7 are docs. Header claim at :53-54 must change with the code fix, whichever way it goes.
- Sections: § Anchors used · § Prior findings, re-checked against current code · § FINDING 1 — partially resolved · § FINDING 2 · § FINDING 3 · § FINDING 4 · § FINDING 5 · § FINDING 6 · § FINDING 7 · § Independent worked example · § Repaint re-verification · § Overclaim check.
- Blocks dispatch: nothing. One BLOCKING change request, owner backend.

---

## Anchors used

Per `protocol/gates.md` § 2 and the quant pack's "Audit mode: the anchors
available here". Re-reading the script's comments, `02-backend.md` or
`docs/mm-cot-long-short-index.md` was not treated as an anchor.

1. **The cited primary definition.** Briese (2008) / Williams (2005): a
   stochastic rescale of a trader category's **net** position over a rolling
   window onto 0..100, extremes at 80/20. I wrote `cot_index_definition()` from
   that sentence alone, before reading the Pine expression.
2. **A separate emulation of the shipped code.** `pine_emulate()` reproduces
   lines :89-104 bar by bar, including the `barstate.isconfirmed` gate, the
   `array.shift` cap and the step-4 union. The two implementations are compared
   against each other and against three chart-timeframe samplings of the same
   weekly data.
3. **My own series.** A 12-observation and a 60-observation synthetic net
   series, neither sharing a single value with 01-quant.md's Example A/B or
   03-test.md's W=4 trace. Cross-checks against both of those were run
   afterwards, as a check and not as the evidence.
4. **CFTC release mechanics.** Positions as of Tuesday's close, published the
   following Friday 15:30 ET; the ALL/OLD/OTHER breakout is a crop-year
   construct.
5. **Pine v6 documented semantics.** `request.security()` `lookahead`,
   `gaps_off`, and the fact that `var`-declared collection state is not rolled
   back on realtime ticks.
6. **The mechanical gate**, re-run: `pine_check.py --strict`, exit 0.

## Prior findings, re-checked against current code

Every row was checked by reading the current file at the cited line, not by
accepting `02-backend.md` or the docs table.

| Prior finding | Status | Evidence in the current file |
|---|---|---|
| 1 — window counts chart bars, not weeks | **PARTIALLY RESOLVED** | `ta.lowest`/`ta.highest` are gone; `netHist` at :89-96 pushes on `newWeekly` (:91). Correct for chart TF <= "W". **Still wrong for chart TF > "W"** — see § FINDING 1 — partially resolved |
| 2 — inverted ±80 guide labels on the red plot | **RESOLVED** | one plot at :110; `hline(80) "Crowded long (80)"`, `hline(20) "Crowded short (20)"` at :111-113. There is no second series for which a guide line means the opposite thing |
| 3 — index on gross long/short, not net | **RESOLVED** | `net = mmLongPos - mmShortPos` at :86, single `cotIndex` at :104. Gross survives only as table rows :125-129 |
| 4 — ±80 was 90/10, not the conventional 80/20 | **RESOLVED** | scale is 0..100 (:104), guide lines are literally 80 and 20 (:111,:113). The rescale mismatch no longer exists to mislabel |
| 5 — "several COT analysts" named no source | **RESOLVED** | header :36-42 names Briese (2008) and Williams (2005) with publisher and year, and :44-50 states the two departures. No chapter invented |
| 6 — `_OLD` suffix meaningless for a metal | **OPEN, correctly documented** | defaults are `_ALL` at :68-69; header :6-18 keeps the "VERIFY THE SYMBOLS" admission and adds that `_ALL` is reasoning, "STILL NOT A CONFIRMATION". Guardrail 3 remains unmet and says so. Expected per the order's non_goals |
| 7 — no explicit `lookahead` | **RESOLVED** | `lookahead = barmerge.lookahead_off` at :79 and :81, named arguments, sibling of the `[close, time]` expression. `pine_check --strict` exit 0, 0 findings, re-run by me |
| 8 — no as-of date, no staleness test | **RESOLVED** | `time` requested from both legs :78-81; `legsAligned` :84; `stale` :107; table row 5 :142-144 shows the date and appends `— STALE`; `Window` row :139-140 separates "still collecting" from "did not resolve"; `legsMisaligned` :121-122 keeps a misaligned pair distinguishable from an unresolved symbol |

## FINDING 1 — partially resolved

```
severity:   MATERIAL
where:      mm_cot_long_short_index.pine:89-96, claim at header :53-54
            and docs/mm-cot-long-short-index.md:31-35
claim:      "The window counts WEEKLY COT REPORTS, not chart bars, so it means
            the same thing on every chart timeframe" (header :53-54); "so
            lookbackWeeks means the same span of time on a 1-hour chart, a
            daily chart and a monthly chart alike" (docs :33-34).
actual:     The push at :93-96 fires on a CHART bar where asOfTime changed.
            That is one push per weekly report only while the chart timeframe
            is at or below "W". Above it, request.security(sym, "W", ...)
            delivers one value per CHART bar — the last weekly value inside it
            — so asOfTime changes once per chart bar and the array collects
            one observation per MONTH on a monthly chart.

            Emulated on 60 weekly observations of my own synthetic net series,
            W = 12, reading the same final date:

              weekly chart  -> cotIndex =  4.06, window = last 12 weeks
              monthly chart -> cotIndex =  9.25, window = last 12 MONTHS

            The monthly window spans 48 weeks of data while the input, the
            tooltip and the table's "12/12 weeks" row all say 12. Roughly
            three of every four COT reports are silently dropped from the
            range. With the shipped default the monthly chart ranks against
            156 months — about 13 years — not 3.

            This is precisely the inverse branch the prior audit named ("on a
            monthly chart, 156 bars is 13 years of monthly samples of a weekly
            series"). The array fixed the sub-weekly branch and left this one.
impact:     A trader on a monthly gold chart reads an index whose header
            promises a 3-year window and gets a 13-year one, built from a
            quarter of the reports. Longer window, wider range, so the reading
            is systematically pulled toward the middle: an actual 3-year
            extreme reads as unremarkable and the crowded-positioning signal
            the script exists to give is suppressed exactly when it fires.
            It is a plausible-looking number in a degenerate case, which is
            the outcome that never gets questioned. Guardrail 5 asks for
            visible degradation; the "156/156 weeks" row actively asserts the
            opposite.
expected:   Either (a) detect the case and degrade visibly — when
            timeframe.in_seconds() > timeframe.in_seconds("W"), publish na and
            say why in the table, which is the guardrail-5 answer and the
            smaller change; or (b) restrict the claim: header :53-54 and the
            lookbackWeeks tooltip say "weekly or lower chart timeframes", and
            the table row says what it is actually counting. Doing neither
            leaves the file asserting invariance it does not have.
            (Audit only; not fixing.)
```

## FINDING 2

```
severity:   MINOR
where:      docs/mm-cot-long-short-index.md:28-29, :31-33, :54, :58, :125
claim:      net at ":52", cotIndex at ":70", netHist at ":55-62",
            barstate.isconfirmed at ":59", plot at ":76", table at ":82-110",
            request.security at ":44-47".
actual:     Current file: net :86, cotIndex :104, netHist :89-96,
            barstate.isconfirmed :93, plot :110, table :116-145,
            request.security :78-81. Every citation is 26-34 lines short,
            consistently — the numbers were taken before the header block grew
            from 27 to 63 lines.
impact:     Low on the numbers, real on the audit trail. The doc's whole value
            is that a reader can check a claim at the line it names; :59 in the
            current file is the middle of a header sentence. A citation that
            does not resolve reads as a citation nobody checked.
expected:   Re-take the line numbers against the current file, or drop them and
            cite the section names, which do not move.
            (Audit only; not fixing.)
```

## FINDING 3

```
severity:   MINOR
where:      docs/mm-cot-long-short-index.md:8
claim:      "Six of the audit's eight findings are resolved by this run; two
            remain open".
actual:     The document's own § Known limits table lists FINDINGS 1, 3, 5, 7,
            8 as "Fixed this run" and 2, 4 as "Dissolved by the redesign" —
            seven — with only FINDING 6 open. "Two remain open" then counts
            the compile check, which is not one of the eight.
impact:     A reader reconciling the prose against the table has to guess which
            count is the real one, on the single sentence that summarises
            whether the run succeeded.
expected:   State it once and consistently. Note that my § FINDING 1 changes
            the answer anyway: five fixed, two dissolved, one partially
            resolved, one open.
            (Audit only; not fixing.)
```

## FINDING 4

```
severity:   MINOR
where:      mm_cot_long_short_index.pine:137
claim:      Table contract (01-quant.md § Table contract) specifies row 3's
            background tint and says nothing about text colour.
actual:     `text_color = color.white` is applied unconditionally, while
            bgcolor is `na` for every index value strictly between 20 and 80.
            On a light chart theme that is white text on the table's default
            light background — the primary output of the indicator is
            invisible for the whole mid-range, which is most readings.
            No other cell in the table sets a text colour, so the row is also
            internally inconsistent.
impact:     The number the script exists to publish is unreadable on a
            common theme, in the ordinary case rather than the extreme one.
expected:   Drop `text_color`, or set it only on the branch where a tint is
            applied. (Audit only; not fixing.)
```

## FINDING 5

```
severity:   MINOR
where:      mm_cot_long_short_index.pine:74-75
claim:      `lookbackWeeks = input.int(156, ...)` with no `minval`. The
            adjacent `staleAfterDays` does carry `minval = 8`.
actual:     A user can set 0 or a negative value. Traced through :93-104 with
            W = 0: push makes size 1, the cap at :95 immediately shifts it back
            to 0, so netHist is permanently empty; `histReady` is
            `0 >= 0` = true, and :100-101 then call `array.min`/`array.max` on
            an empty array. W = 1 is defined but useless — the array holds only
            the current observation, so hi == lo and the index is always na.
impact:     Bounded: the guardrail-5 outcome (na, or a visible runtime error)
            rather than a wrong number, which is why this is MINOR. But it is
            an input the settings dialog invites the user to change, and
            neither 0 nor 1 is rejected at the point of entry.
            Pre-existing in kind — the old `ta.lowest(x, 0)` was also invalid —
            but the array path adds the empty-collection case.
expected:   `minval = 2` on `lookbackWeeks`, matching the treatment
            `staleAfterDays` already gets. (Audit only; not fixing.)
```

## FINDING 6

```
severity:   MINOR
where:      mm_cot_long_short_index.pine header :52-62
claim:      "WHAT DEGRADES, AND HOW YOU SEE IT" enumerates four ways the index
            reads n/a and says nothing about the live bar.
actual:     By design (01-quant.md § Formula — specification, step 4), the
            current observation is not in netHist until its bar confirms, so
            the live bar ranks against W + 1 observations and the oldest
            observation has not yet dropped out. The displayed value can
            therefore move at the bar's close. On a weekly chart that is the
            state for the entire week, not an instant. The implementation
            matches the spec; the spec accepted the imprecision and the header
            did not carry the disclosure forward.
impact:     Negligible at W = 156 (one observation in 157). Material at the
            small windows the tooltip invites (26 weeks) and larger still if
            someone sets 12. The pack's rule is that a provisional displayed
            value is legitimate and an undisclosed one is not.
expected:   One line in "WHAT DEGRADES": the reading for the week in progress
            is provisional and is finalised when the bar closes.
            (Audit only; not fixing.)
```

## FINDING 7

```
severity:   MINOR
where:      mm_cot_long_short_index.pine:107, tooltip at :72
claim:      Tooltip: "the newest closed weekly bar is normally at most about 13
            days behind wall clock. 21 days absorbs that ordinary lag plus one
            holiday-delayed release".
actual:     `asOfTime` is the weekly bar's OPEN time, and which weekly bar it
            is depends on the chart timeframe. On a sub-weekly chart
            lookahead_off yields the last CLOSED weekly bar, so the age runs
            7-13 days and the tooltip's arithmetic is right. On a weekly chart
            the requested timeframe equals the chart timeframe, so asOfTime is
            the CURRENT week's open and the age runs 0-6 days. The same missing
            report is therefore flagged STALE about a week later on a weekly
            chart than on a daily one.
impact:     Small and in the permissive direction, which is the direction that
            matters here: the staleness flag is the only thing standing between
            `gaps_off` carrying a dead value forward and the trader believing
            it. The tooltip states one basis for a quantity that has two.
expected:   Say in the tooltip that the age is measured from the weekly series
            bar's open and runs about a week younger on a weekly chart, or
            derive the threshold from the chart timeframe.
            (Audit only; not fixing.)
```

## Independent worked example

My own series, chosen so that none of its values appear in 01-quant.md or
03-test.md. Managed Money gross contracts, `lookbackWeeks = 6`.

| wk | L | S | net | expected `cotIndex` |
|---|---|---|---|---|
| 1 | 90,000 | 67,000 | 23,000 | na — window not full |
| 2 | 104,000 | 61,000 | 43,000 | na |
| 3 | 112,000 | 58,000 | 54,000 | na |
| 4 | 99,000 | 72,000 | 27,000 | na |
| 5 | 121,000 | 55,000 | 66,000 | na |
| 6 | 133,000 | 49,000 | 84,000 | **100.00** |
| 7 | 118,000 | 63,000 | 55,000 | **49.12** |
| 8 | 127,000 | 60,000 | 67,000 | **70.18** |
| 9 | 86,000 | 81,000 | 5,000 | **0.00** |
| 10 | 94,000 | 95,000 | −1,000 | **0.00** |
| 11 | 140,000 | 52,000 | 88,000 | **100.00** |
| 12 | 111,000 | 70,000 | 41,000 | **47.19** |

Hand check on the row least likely to be right by accident. Week 8, window is
weeks 3-8: `{54, 27, 66, 84, 55, 67}`k. `lo = 27,000`, `hi = 84,000`,
`net = 67,000`.
`100 × (67,000 − 27,000) / (84,000 − 27,000) = 100 × 40/57 = 70.175…` →
**70.18**. Agrees.

Week 10 is the sign check the pack asks for: `net = −1,000`, Managed Money is
net **short**, and the index reads **0.00** — the bottom of the window, not a
negative number and not a fabricated 50. The 0..100 scale has no room for the
sign, and 0 is the correct encoding of "most net short in the window". `fmtPos`
renders the net position itself as `-1,000`, so the sign survives in the table
where it belongs.

**Both implementations agree on every row**, and the definition-first
implementation was written before the Pine expression was read.

Cross-checks against the other lanes, run afterwards and not as the evidence:

| Vector | Source | My result |
|---|---|---|
| Example A, W=5 | 01-quant.md | `na,na,na,na,0.00` — agrees |
| Example A, W=3 | 01-quant.md | `na,na,100.00,100.00,0.00` — agrees |
| Example B, W=12 | 01-quant.md | week 12 = **67.59** — agrees, and reproduces the 2026-09-16 audit's figure by a third independent path |
| Example B, W=5 | 01-quant.md | `100.00, 78.33, 12.50, 0.00, 0.00, 0.00, 0.00, 100.00` — agrees on all eight |
| 12-week W=4 trace | 03-test.md | `na,na,na,100.00,na,100.00,na,0.00,0.00,0.00,na,100.00` and window sizes `1,2,3,4,4,4,4,4,4,4,4,4` — agrees on every row including the two na-net weeks that must leave the array untouched, and the week-11 `hi == lo` row that must be na and not 50 |

**The arithmetic of the rescale is correct, the degenerate cases return `na`
rather than a value, and 0 is correctly distinguishable from `na`.** Nothing in
this section is the basis for the FAIL; the FAIL is § FINDING 1 alone.

## Repaint re-verification

Reasoned from Pine v6's execution model, per the order. The script's own
comments were not used as evidence.

**The `barstate.isconfirmed` gate is present and correctly placed.** Line 93:

```pine
if newWeekly and barstate.isconfirmed and not na(net)
    array.push(netHist, net)
```

It is a term of the `if` condition, so it guards the mutation itself — both the
`array.push` at :94 and the cap at :95-96 — rather than appearing in a comment
or guarding only the read. This is the one thing 01-quant.md said backend must
not miss, and it was not missed.

**Why it is necessary, from the model rather than from the comment.** Pine
re-executes the script on every tick of a realtime bar and rolls back *series*
variables to their state at the bar's open before each re-execution.
`var`-declared collections are not series and are not rolled back: a mutation
performed on tick *n* survives into tick *n+1*. Ungated, `array.push` inside a
`newWeekly` block would therefore append once per tick for as long as the
condition held, growing the array without bound and poisoning every subsequent
`array.min`/`array.max` — invisibly, because historical bars execute once and
would look correct. The gate reduces the realtime bar to a single push on its
closing tick, which is the same one push a historical bar performs.

**Historical and realtime agree.** On a historical bar `barstate.isconfirmed`
is true, so one push occurs per `asOfTime` transition. On a realtime bar the
push is deferred to the closing tick, where `newWeekly` still holds because
`asOfTime[1]` is the previous chart bar's value. Both paths deposit exactly one
final value per weekly observation, in the same order, so a chart reloaded
tomorrow reconstructs the identical array. No closed bar's plotted value
changes after the fact.

**`lookahead = barmerge.lookahead_off` (:79, :81) is doing real work here even
though it is the documented default.** With the chart timeframe below `"W"` it
guarantees each chart bar receives the most recently *closed* weekly bar, so
`asOfTime` cannot advance to a weekly bar the market has not finished. That is
what makes the `newWeekly` transition a safe trigger for an irreversible array
mutation: the value pushed is final at the moment it is pushed. Had the call
been `lookahead_on`, the gate would not have saved it — the array would have
been permanently seeded with values from the future on every historical bar,
which is the worst version of this defect because it is baked into state rather
than recomputed.

**What still moves, and it is not a repaint.** The live bar's displayed value
ranks against `W + 1` observations until that bar confirms (§ FINDING 6). That
is a provisional current reading being finalised, not a closed bar being
rewritten, and the pack explicitly allows it — provided it is disclosed, which
is FINDING 6's whole content.

**The unresolved timing question is carried forward, unchanged.** Whether
TradingView stamps the COT2 weekly bar at CFTC's Tuesday as-of date or the
Friday release date is still unverified, and on a chart symbol whose Friday
session ends before 15:30 ET the first branch would leak. The table's "Data as
of (series bar)" row is the disclosed remedy and the label correctly declines
to assert which stamping it is.

**Nothing else repaints.** No `ta.pivothigh`/`ta.pivotlow`, no `ta.valuewhen`,
no alerts, no forward series indexing, no strategy calls. `ta.lowest`/
`ta.highest` are gone from the file.

## Overclaim check

Required by the order: neither document may say the script "works" or
"compiles".

**Header** — no claim of either. `pine_check.py` is not mentioned; nothing
asserts the script loads. The "WHAT DEGRADES" block (:52-62) describes
behaviour, which is a claim about the specification rather than about a run.
**No overclaim on the compile axis.** Its one false statement is the
timeframe-invariance sentence at :53-54, which is § FINDING 1, not an
overclaim about verification.

**`docs/mm-cot-long-short-index.md`** — explicitly disclaims both, twice, at
:9-11 and :135-142: "the static checker passed, but that is not the compile
check"; "This doc does not claim the script works; it claims the static check
passed and an independent hand-derivation of the formula agrees with what the
code implements." It also correctly labels the worked examples as hand
computations rather than executed tests (:155-156), and correctly records
guardrail 3 as still unmet (:130-134). **No overclaim.** Its defects are
FINDING 2 (citations), FINDING 3 (count) and the inherited FINDING 1 claim at
:31-35.

One caveat on that last sentence of :141-142: "an independent hand-derivation
of the formula agrees with what the code implements" is true as far as it goes
— my § Independent worked example confirms it — but every derivation in this
run tested the sub-weekly branch only, so the agreement it reports is narrower
than it sounds. That is the § risks note, not a separate finding.
