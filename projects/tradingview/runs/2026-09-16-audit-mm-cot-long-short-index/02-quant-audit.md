REPORT 2026-09-16-audit-mm-cot-long-short-index/02
status:      DONE
verdict:     FAIL

changed:
  - none

verification:
  command:   python C:\projects\investments\.agentic\scripts\pine_check.py C:\projects\investments\tradingview\mm_cot_long_short_index.pine --strict
  result:    FAIL
  detail:    Anchors: CFTC COT release schedule (as-of Tue, published Fri 15:30 ET); Briese/Williams standard COT Index definition; Pine v6 request.security lookahead default; 12-point hand computation. pine_check --strict: FAIL (exit 1), 2x P008 at :39,:40.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - FINDING 1 (CRITICAL, :43-48) — `ta.lowest/ta.highest(..., lookbackWeeks)` counts chart bars, not weeks; on a daily chart 156 bars is 31 weeks, not 3 years. Owner: backend. See § FINDING 1.
  - FINDING 2 (CRITICAL, :55-56) — the +80/-80 hlines are labelled for the long plot only; on the red short plot -80 reads "Short Extreme (crowded)" when shorts are at a range low. Owner: backend. See § FINDING 2.
  - FINDING 3 (MATERIAL, :24-26,:43-49) — index is applied to gross long and gross short separately; the standard COT Index it claims is defined on the net position. See § FINDING 3.
  - FINDING 4 (MATERIAL, :55-56) — +/-80 on this -100..+100 scale equals 90/10 on the conventional 0..100 COT Index, not the conventional 80/20. See § FINDING 4.
  - FINDING 5 (MATERIAL, :24-26) — guardrail 2 unmet: "several COT analysts" names no source. Briese (2008) and Williams (2005) are the citable ones. Owner: docs. See § FINDING 5.
  - FINDING 6 (MATERIAL, :32-33) — the `_OLD` suffix denotes CFTC's old-crop-year breakout, which does not exist for Gold (088691), a non-agricultural contract. Owner: backend. See § FINDING 6.
  - FINDING 7 (MATERIAL, :39-40) — guardrail 1's literal text requires an explicit `lookahead=barmerge.lookahead_off`; both calls omit it and `pine_check --strict` fails on it. See § FINDING 7.
  - FINDING 8 (MATERIAL, :39-40,:59-77) — no as-of date and no staleness test; `request.security` default `barmerge.gaps_off` holds the last value forward forever. See § FINDING 8.

risks:
  - I have no browser tool, so I could NOT open TradingView's symbol search. Whether `COT2:088691_F_MMP_L_OLD` resolves at all is unconfirmed by me, exactly as the header admits. FINDING 6 is reasoning from CFTC's published report structure, not a confirmation.
  - I have no Pine compiler. Whether `ta.lowest` returns `na` or a partial-window value before `length` bars exist is a runtime fact I could not execute; FINDING 1 holds either way, because it is timeframe arithmetic, not a null-handling question.
  - Whether TradingView stamps the COT2 series at the Tuesday as-of date or the Friday release date is unverified; § Repaint analysis works through both branches and neither branch clears FINDING 8.
  - I could not reproduce any live value of this indicator (no data layer, no chart). Every number in this report is hand-computed from the definition on synthetic inputs, per the pack's "re-derivation from the definition" standard.

## Orchestrator brief

- Verdict: FAIL. Two CRITICAL findings, six MATERIAL. Do not trade Gold positioning off this script as written.
- FINDING 1 is the headline: the 156 "weeks" lookback is measured in chart bars, so on any non-weekly chart the rolling range is far shorter than advertised and the index reads far more extreme than it should.
- FINDING 2 is the one that misleads fastest: the -80 guide line is labelled "Short Extreme (crowded)" but the red short-index plot at -80 means Managed Money shorts are at a 3-year LOW. Inverted reading.
- FINDING 3: the script rescales gross long and gross short separately; the standard COT Index is defined on the net position. Both plots can print +100 at once (worked example below) while net positioning is exactly neutral.
- Guardrail status: 1 unmet in letter (FINDING 7) though not repainting in fact; 2 unmet (FINDING 5); 3 still unmet and now worse (FINDING 6); 4 n/a; 5 unmet (FINDING 8); 6 satisfied.
- Lane split: FINDINGS 1, 2, 4, 6, 7 are backend (Pine edits). FINDING 3 needs a human decision (change formula vs change claim) before dispatch. FINDING 5 is docs, after 3 resolves.
- Sections: § Anchors used · § FINDING 1 · § FINDING 2 · § FINDING 3 · § FINDING 4 (+/-80 guides are the 90/10 extremes, not the conventional 80/20) · § FINDING 5 · § FINDING 6 · § FINDING 7 · § FINDING 8 · § Worked example (12 hand-computed weeks) · § Repaint analysis.
- Blocks dispatch: FINDING 3 only. The rest are dispatchable now.

## Anchors used

Per `protocol/gates.md` § 2 and the quant pack's "Audit mode: the anchors available here". Re-reading the script's own comments was not treated as an anchor.

1. **CFTC's published COT release mechanics.** The Commitments of Traders report is compiled from positions held at the **close of business Tuesday** and published the **following Friday at 3:30 p.m. Eastern Time**. When a federal holiday falls in the reporting week the release slips to the next business day (Monday or Tuesday) and the as-of date moves with it. The trader's stated premise — "COT comes out Friday" — is correct about the *publication* day and silent about the three-day lag to the *as-of* date. That lag is the part that matters for a chart.
2. **The standard COT Index definition.** Stephen Briese, *The Commitments of Traders Bible* (Wiley, 2008), and Larry Williams, *Trade Stocks & Commodities with the Insiders: Secrets of the COT Report* (Wiley, 2005). Both define the index as a stochastic rescale of the **net** commercial/large-speculator position over a rolling window to a **0..100** scale, with 80/20 as the conventional extremes and 26-week, 1-year and 3-year windows all in common use.
3. **CFTC's report structure.** The `ALL / OLD / OTHER` breakout exists because certain agricultural contracts have crop years; it is not published for metals and other non-agricultural markets. The Disaggregated report (which is where the "Managed Money" category lives) covers physical commodities including COMEX Gold, contract market code `088691`.
4. **Pine v6 `request.security()` documented semantics.** `lookahead` defaults to `barmerge.lookahead_off`; `gaps` defaults to `barmerge.gaps_off`; the returned value is a series **on the chart's timeframe**, not on the requested timeframe.
5. **A 12-point hand computation**, reproduced in § Worked example, run independently against the formula as the definition states it and against the formula as the script writes it.

---

## FINDING 1

```
severity:   CRITICAL
where:      mm_cot_long_short_index.pine:43-44, :47-48 (claim at :35-36)
claim:      The tooltip states the lookback is a "Rolling window ... COT is
            published weekly, so this is requested on a fixed weekly timeframe
            regardless of your chart's timeframe. 156 = 3 years".
actual:     `request.security()` returns a series on the CHART's timeframe, not
            on "W". So `ta.lowest(mmLongPos, 156)` counts 156 CHART bars:
              chart W    -> 156 bars = 156.0 weeks = 3.00 years  (correct)
              chart D    -> 156 bars =  31.2 weeks = 0.60 years
              chart 240  -> 156 bars =  19.2 weeks = 0.37 years
              chart 60   -> 156 bars =   4.8 weeks = 0.09 years
            Only the weekly chart gets the advertised window. Pinning the
            *request* to "W" does not pin the *window* to weeks.
impact:     On a daily Gold chart the index ranks the current Managed Money
            position against roughly seven months of history while the tooltip
            says three years. A seven-month range is much narrower, so the
            index saturates at +/-100 far more often. The trader reads "MM longs
            are at a three-year extreme, this is a contrarian top" when the
            actual statement is "MM longs are at a seven-month high" — an
            ordinary event in a trending gold market. This is the single most
            likely way this script loses money.
            The inverse also bites: on a monthly chart, 156 bars is 13 years of
            monthly samples of a weekly series, silently discarding ~3 of every
            4 COT reports from the min/max range.
expected:   The min/max must be evaluated on weekly data. Compute the range
            inside the request — request the already-ranked value, or request
            `ta.lowest(close, lookbackWeeks)` / `ta.highest(close,
            lookbackWeeks)` on the "W" timeframe — so that `lookbackWeeks`
            means weeks on every chart timeframe. (Audit only; not fixing.)
```

## FINDING 2

```
severity:   CRITICAL
where:      mm_cot_long_short_index.pine:55-56
claim:      hline(80)  is labelled "Long Extreme (crowded)"
            hline(-80) is labelled "Short Extreme (crowded)"
actual:     Both plots (:52 green longIndex, :53 red shortIndex) share one pane
            and therefore share both guide lines. The labels are written as if
            the pane held a single net series. For the RED short index:
              shortIndex = +80  -> MM gross shorts near the TOP of their range
                                   = genuinely crowded short
              shortIndex = -80  -> MM gross shorts near the BOTTOM of their
                                   range = the opposite of crowded short
            So the red line touching the line labelled "Short Extreme
            (crowded)" means shorts are at a multi-year LOW.
impact:     A Gold trader watching the red line drop to -80 and land on a
            dashed line reading "Short Extreme (crowded)" concludes Managed
            Money is maximally short and takes the contrarian long. The data
            says the reverse: MM has almost no shorts on, which is the crowded-
            LONG condition. The sign is inverted on exactly the reading the
            labels invite you to act on, and nothing else on the chart
            contradicts it.
expected:   Either label the guide lines neutrally for a two-plot pane
            ("Upper extreme (+80)" / "Lower extreme (-80)"), or plot a single
            net-based index for which a signed label is meaningful (see
            FINDING 3). (Audit only; not fixing.)
```

## FINDING 3

```
severity:   MATERIAL
where:      mm_cot_long_short_index.pine:43-49, claim at :24-26
claim:      ":24-26  This is standard 'COT Index' methodology (a stochastic-
            style oscillator on positioning), popularized by several COT
            analysts".
actual:     The standard COT Index, as Briese and Williams define it, is
            computed on the NET position (long - short) and scaled 0..100.
            This script computes it twice, on GROSS long and GROSS short
            independently (:43-45, :47-49), each ranked against its own range.
            That is a defensible variant — it is DIFFERENTLY DEFINED, not
            arithmetically wrong — but it does not behave like the thing it
            names, because gross long and gross short both rise with total
            open interest. Hand-computed, 5 weeks:
              L = 100k,110k,120k,130k,200k   -> script long index  = +100.0
              S =  50k, 55k, 60k, 65k,150k   -> script short index = +100.0
              net = 50k,55k,60k,65k,50k      -> standard COT Index =    0.0
            Both plots print the maximum extreme simultaneously while net
            positioning is exactly at the bottom of its range and the standard
            index reads dead neutral.
impact:     "Crowded long AND crowded short at the same time" is not a
            positioning signal; it is a reading of open interest wearing a
            positioning label. For Gold, where MM gross longs and gross shorts
            do expand together on volatility spikes, this state is common
            rather than exotic, and the trader has no way to tell it apart
            from a genuine one-sided extreme.
expected:   A human decision, not an engineering one: either (a) compute the
            index on the net position and scale 0..100 to match the cited
            methodology, keeping gross long/short as raw table rows, or (b)
            keep the two gross indices and rewrite :24-26 to state plainly
            that this is a per-side variant, NOT the standard COT Index, and
            that simultaneous extremes mean rising open interest. Do not do
            neither. (Audit only; not fixing.)
```

## FINDING 4

```
severity:   MATERIAL
where:      mm_cot_long_short_index.pine:55-56
claim:      +/-80 mark the "extreme (crowded)" levels, implicitly the
            conventional COT Index extremes.
actual:     The script's scale is -100..+100; the conventional COT Index scale
            is 0..100 with extremes at 80 and 20. Mapping between them,
            x_0_100 = (x_script + 100) / 2:
              script +80 == standard 90      script -80 == standard 10
              standard 80 == script +60      standard 20 == script -60
            So the shipped guide lines are the 90/10 extremes, materially
            stricter than the 80/20 the "standard COT Index" framing implies.
impact:     The trader sees roughly half as many extreme signals as the
            literature he is calibrating against would produce, and will
            conclude the indicator is quiet or that Gold positioning is rarely
            stretched. Combined with FINDING 1 (which pushes the index toward
            saturation on sub-weekly charts) the two errors partly cancel in
            an unpredictable, timeframe-dependent way, which is worse than
            either alone because the net bias is invisible.
expected:   Either move the guide lines to +/-60 to match the 80/20
            convention, or make them an input with the default stated and
            justified, and say in the header that +/-80 here is 90/10 in
            conventional terms. (Audit only; not fixing.)
```

## FINDING 5

```
severity:   MATERIAL
where:      mm_cot_long_short_index.pine:24-26
claim:      "This is standard 'COT Index' methodology ... popularized by
            several COT analysts."
actual:     Guardrail 2 requires every computed value to trace to a NAMED
            source — a book and chapter, a paper, an exchange or regulator
            spec — or the header to declare the construction original. "Several
            COT analysts" is neither: it gestures at prior art without naming
            any, so a reader cannot check the definition, and it forecloses the
            original-construction route by asserting a standard exists.
            Citable sources do exist and are given in § Anchors used: Briese,
            The Commitments of Traders Bible (Wiley, 2008); Williams, Trade
            Stocks & Commodities with the Insiders (Wiley, 2005).
impact:     The reader cannot discover FINDING 3 for himself. The header says
            "standard", so the natural assumption is that the plotted series
            behaves like the indices published elsewhere, and the per-side
            departure is undiscoverable without reading the arithmetic.
expected:   Name the source, and state which part of it this script follows
            and which part it departs from. Ordering matters: FINDING 3 must be
            decided first, because it determines what the citation can honestly
            claim. (Audit only; not fixing.)
```

## FINDING 6

```
severity:   MATERIAL
where:      mm_cot_long_short_index.pine:32-33
claim:      Defaults `COT2:088691_F_MMP_L_OLD` and `COT2:088691_F_MMP_S_OLD`
            are "my best reconstruction for Gold" (:10).
actual:     `088691` is correct — it is the CFTC contract market code for
            COMEX Gold, and Gold is covered by the Disaggregated report where
            the Managed Money category lives. The `_F_` (futures-only, as
            against futures-and-options) segment is a legitimate choice.
            The `_OLD` suffix is the problem. In CFTC's report structure the
            ALL / OLD / OTHER breakout exists only because certain
            AGRICULTURAL contracts have crop years; "old crop" has no meaning
            for a metal. For Gold the only meaningful aggregation is ALL. An
            `_OLD` ticker on a non-crop-year contract therefore either fails
            to resolve, or resolves to a series that is identical to ALL by
            construction and could silently diverge if the vendor ever changes
            how it fills the unused breakout.
            I could NOT open TradingView's symbol search to confirm which of
            those two happens — see risks. This is reasoning from CFTC's
            published report structure, not a confirmation.
impact:     Best case the trader sees "n/a" in the table and knows something is
            wrong (guardrail 5 holds, credit where due). Worst case the symbol
            resolves to an empty or stale series and the table shows a frozen
            number that looks live (see FINDING 8). Either way the shipped
            default is a reconstruction whose one identifiable component is
            drawn from a part of the report that does not apply to Gold, which
            lowers the prior that the rest of the reconstruction is right.
expected:   The `_ALL` variant is the one to try first for Gold. The header's
            existing "VERIFY THE SYMBOLS BEFORE TRUSTING THIS" block must be
            preserved, not deleted, until someone actually opens the symbol
            search — per the pack's note on this script and the recon lane's
            handoff. (Audit only; not fixing.)
```

## FINDING 7

```
severity:   MATERIAL
where:      mm_cot_long_short_index.pine:39-40
claim:      The calls pass only `ignore_invalid_symbol = true`; no `lookahead`
            argument appears anywhere in the file.
actual:     Pine v6 documents `request.security()`'s `lookahead` as defaulting
            to `barmerge.lookahead_off`. So on the runtime question the recon
            lane could not settle: **the omission does not by itself cause a
            repaint**. On a chart timeframe below "W" the default returns the
            last CLOSED weekly bar's value, which is the non-repainting
            behaviour. The answer is "it does not repaint for this reason" —
            see § Repaint analysis for the reasons it might repaint anyway.
            But guardrail 1's text is not about behaviour, it is about the
            page: "request.security() passes lookahead=barmerge.lookahead_off
            explicitly". That is unmet, and `pine_check.py --strict` exits 1
            on it (P008 at both :39 and :40), which is a mechanical gate
            failure and mechanical gates are never bypassed.
impact:     Low on the numbers, real on the audit trail. A future edit that
            switches the request to a daily timeframe, or a reader checking
            for repaint, has to know Pine's default rather than read the file.
            Guardrail 1 exists precisely to remove that dependency.
expected:   Pass `lookahead = barmerge.lookahead_off` explicitly on both calls.
            This is the cheapest finding in the report to close, and closing it
            turns the verification command green. (Audit only; not fixing.)
```

## FINDING 8

```
severity:   MATERIAL
where:      mm_cot_long_short_index.pine:39-40, table at :59-77
claim:      Guardrail 5 is satisfied because an unresolved symbol renders
            "n/a" (:61-62). The recon lane recorded this as satisfied.
actual:     It is satisfied for the UNRESOLVED case and not for the STALE
            case, and the two are distinct. `request.security()` defaults to
            `barmerge.gaps_off`, which repeats the last known value on every
            subsequent chart bar indefinitely. A COT2 series that resolves once
            and then stops updating — vendor outage, a CFTC release delayed by
            a federal holiday, a renamed ticker, a market that stopped being
            reported — produces a table showing a confident, comma-formatted
            contract count with no indication of how old it is.
            The table also shows no as-of date at all. Given CFTC's mechanics
            (as-of Tuesday, published the following Friday 15:30 ET), a correct
            reading is ALWAYS between 3 and 10 days old, and the trader has no
            way to tell 3 from 10, or 10 from 400.
impact:     "Never carry the last good one forward silently" is the exact
            wording of guardrail 5, and `gaps_off` does exactly that. For Gold
            this matters most around a holiday-delayed release, which is when
            the trader is most likely to check positioning and least likely to
            notice the number has not moved.
expected:   Display the as-of bar time of the requested series alongside the
            value, and render the reading as stale when it is older than one
            report cycle. That is a design decision for the human, not
            something to bolt on. (Audit only; not fixing.)
```

---

## Worked example (12 hand-computed weeks)

Written from the definition, then compared against the script's expression.
Units are contracts of Managed Money gross open interest.

| week | MM long | MM short | net |
|---|---|---|---|
| 1  | 120,000 | 60,000 |  60,000 |
| 2  | 135,000 | 55,000 |  80,000 |
| 3  | 150,000 | 50,000 | 100,000 |
| 4  | 168,000 | 45,000 | 123,000 |
| 5  | 180,000 | 40,000 | 140,000 |
| 6  | 175,000 | 48,000 | 127,000 |
| 7  | 160,000 | 55,000 | 105,000 |
| 8  | 140,000 | 70,000 |  70,000 |
| 9  | 125,000 | 85,000 |  40,000 |
| 10 | 110,000 | 95,000 |  15,000 |
| 11 | 100,000 | 105,000 | -5,000 |
| 12 | 155,000 | 62,000 |  93,000 |

Long side, window = 12: min 100,000, max 180,000, current 155,000.
`(155000 - 100000) / (180000 - 100000) * 200 - 100 = 0.6875 * 200 - 100 = +37.5`
Script expression at :45 yields **+37.5**. Agrees.

Short side, window = 12: min 40,000, max 105,000, current 62,000.
`(62000 - 40000) / (105000 - 40000) * 200 - 100 = 0.33846 * 200 - 100 = -32.31`
Script expression at :49 yields **-32.31**. Agrees.

**The arithmetic of the rescale is correct.** The affine map to -100..+100 is
sound, the degenerate `max == min` case returns `na` rather than a midpoint
(:45, :49) which is the right call and worth crediting, and the `na(mmLongPos)`
guard is correctly placed before the division.

The standard COT Index on the same 12 weeks, computed on the net column:
min -5,000, max 140,000, current 93,000 -> `100 * (93000 + 5000) / 145000 =
67.59` on a 0..100 scale, i.e. **+35.2** if mapped onto the script's scale.
Close to the long index here by coincidence; § FINDING 3's five-week example
shows how far apart they go when gross long and gross short move together.

Note what this example cannot show: it is 12 *weekly* observations, which is
what the script computes only on a weekly chart. On a daily chart the same 12
COT reports occupy 60 chart bars, and the window semantics of FINDING 1 apply.

## Repaint analysis

Required by the pack for any artifact touching a computed series.

**The omitted `lookahead` does not cause a repaint.** Pine v6 defaults
`request.security()`'s `lookahead` to `barmerge.lookahead_off`, so on a chart
timeframe below "W" each chart bar receives the value of the most recently
CLOSED weekly bar. Historical bars do not rewrite. This settles the question
the recon lane flagged and could not answer. FINDING 7 stands on guardrail 1's
explicitness requirement and on the mechanical gate, not on repainting.

**The current week's reading is provisional, and that is not flagged.** On a
weekly chart, the requested timeframe equals the chart timeframe, so the last
bar carries the developing weekly close and updates intrabar. The table is
drawn under `barstate.islast` (:64) with no `barstate.isconfirmed` gate
anywhere in the file, so the displayed "Long Index" for the week in progress
can change. For a series that only changes once a week this is mostly benign —
until it is not, which is the week of the release.

**The timing question, worked through both branches.** CFTC's mechanics are:
positions as of Tuesday close, published Friday 15:30 ET.

- *If TradingView stamps the COT2 bar at the Tuesday as-of date* — the value
  sits inside the same calendar week whose bar closes Friday. With
  `lookahead_off`, a lower-timeframe chart does not see it until that weekly
  bar closes. For a US equity or ETF chart the weekly bar closes Friday 16:00
  ET, after the 15:30 ET release: no leak, by about half an hour. For any chart
  symbol whose Friday session ends before 15:30 ET — a London- or Frankfurt-
  listed gold ETF closes 11:30 ET — the weekly bar closes BEFORE the report is
  public, and the script would deliver a number the market did not yet have.
  That is a genuine forward-looking leak on a specific and not exotic class of
  chart symbol, and the script has no guard for it.
- *If TradingView stamps the bar at the Friday release date* — the alignment is
  correct by construction and no leak exists on any chart symbol.

I could not determine which branch is real without opening the data (see
risks). The margin in the first branch is half an hour on the trader's likely
chart symbol, which is too thin to call safe by inspection and too
instrument-dependent to call broken. It is recorded here rather than raised as
a separate finding because the remedy is the same as FINDING 8's: publish the
as-of date of the requested series, and the question answers itself on screen.

**Nothing else in the file repaints.** No `ta.pivothigh`/`ta.pivotlow`, no
`ta.valuewhen`, no alerts, no forward series indexing, no strategy calls. The
rolling `ta.lowest`/`ta.highest` windows include the current bar, which is
correct for a stochastic-style oscillator and is not a repaint — the value at
bar close is final for every closed bar.
