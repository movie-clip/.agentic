REPORT 2026-09-17-fix-mm-cot-long-short-index/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Order's verification field was NONE (read-only specification lane; no .pine edited, so pine_check.py has nothing new to check). Independent anchor used: Briese/Williams 0..100 net COT Index definition, re-derived and hand-computed on two synthetic series, cross-checked against the prior audit's own 12-week figure (67.59) which it reproduces exactly.

contract_notes:
  - INPUTS: `mmLongSymbol` default becomes `COT2:088691_F_MMP_L_ALL`, `mmShortSymbol` default becomes `COT2:088691_F_MMP_S_ALL` (`_OLD` -> `_ALL`, FINDING 6). See § Data requirements.
  - INPUTS: one new input `staleAfterDays = input.int(21, ...)` in group "Data Source". `lookbackWeeks` keeps default 156 but its tooltip text must change. See § Inputs contract.
  - PLOTS: the two plots `MM Long Index` (green) and `MM Short Index` (red) are REMOVED and replaced by a single plot `MM Net COT Index` on 0..100. See § Plot and guide-line contract.
  - HLINES: `hline(0)`, `hline(80)`, `hline(-80)` are removed; replaced by `hline(80)`, `hline(50)`, `hline(20)` with the labels given in § Plot and guide-line contract.
  - TABLE: `table.new(position.top_right, 2, 4, ...)` becomes `2, 6`. Exact row order and cell text in § Table contract.
  - HEADER: the "WHAT THIS COMPUTES" paragraph must be rewritten for the net index, and a named SOURCE block added. Exact text in § Header text for docs.
  - DOCS: this script has no `docs/<slug>.md`; if one is created it lands at `docs/mm_cot_long_short_index.md` per CLAUDE.md.

pack_corrections:
  - none

handoff:
  - backend: implement § Formula — specification exactly as written; every construct, gate and degenerate case is pinned there, and no mathematical choice is left open.
  - backend: the rolling window MUST be an array of confirmed weekly observations, not `ta.lowest`/`ta.highest` on the chart-timeframe series — that is FINDING 1's whole fix. See § Formula — specification, step 3.
  - backend: the array push MUST be gated on `barstate.isconfirmed`; Pine does not roll back `var` array mutations on the realtime bar. See § Repaint analysis.
  - backend: range must be taken as the union of the array and the current `net` (`math.min`/`math.max`), or the index can print above 100 for one bar. See § Formula — specification, step 4.
  - backend: both `request.security()` calls take `lookahead = barmerge.lookahead_off` explicitly, outside the expression argument. See § FINDING 7 — exact argument.
  - docs: header citation and the preserved unverified-symbol admission are drafted verbatim in § Header text for docs.
  - quant-audit: expected index values for both worked series are in § Worked examples; the W=12 case reproduces the prior audit's 67.59 independently.
  - test: fixture-able check vectors are the two tables in § Worked examples (no fixtures exist in this repo yet; `fixtures/*.csv` is the convention if one is created).

risks:
  - The array window can only be built from weekly transitions visible in the chart's loaded bars. On a very low chart timeframe (1m/5m) fewer than `lookbackWeeks` weeks are ever loaded, so the index stays `n/a` forever. This is honest degradation, not a bug, but it MUST be disclosed in the header and is a visible behaviour change from today's script.
  - `_ALL` is reasoned from CFTC's report structure, not confirmed in TradingView's symbol search. I have no browser tool. Guardrail 3 remains unmet and the header's "VERIFY THE SYMBOLS BEFORE TRUSTING THIS" block must survive verbatim in intent.
  - I could not open Briese (2008) or Williams (2005), so the citation I drafted names book/publisher/year only. I deliberately did not invent chapter numbers; a chapter-level citation should be added only by someone who opens the book.
  - Whether `ignore_invalid_symbol = true` yields `[na, na]` for a tuple-valued `request.security()` is documented behaviour I could not compile-check. If it errors instead, backend must fall back to four scalar `request.security()` calls, each with explicit `lookahead`.
  - Whether TradingView stamps the COT2 weekly bar at CFTC's Tuesday as-of date or the Friday release date is still unverified (carried from the audit's § Repaint analysis). This is why § Table contract labels the row "Data as of (series bar)" rather than claiming it is the CFTC as-of date.
  - I have no Pine compiler and no chart. Every number here is hand-computed from the definition on synthetic inputs, per the pack's "re-derivation from the definition" standard. I make no claim that the specified script compiles.

## Orchestrator brief

- Mode RESEARCH; specification only, no code written. All eight audit findings in scope are now pinned to a single implementable formula.
- D-1 is implemented as: `net = mmLongPos - mmShortPos`, rescaled 0..100 over `lookbackWeeks` weekly observations. One plot replaces the green/red pair; gross long/short survive as table rows only.
- FINDING 1 fix: a `var float[]` of confirmed weekly observations, pushed once per weekly bar, capped at `lookbackWeeks`. Timeframe-invariant by construction; `ta.lowest`/`ta.highest` are removed entirely.
- FINDING 2 and FINDING 4 are dissolved by the redesign: one signed series makes 80/50/20 labels unambiguous and conventional.
- FINDING 6: defaults become `COT2:088691_F_MMP_L_ALL` / `_S_ALL`. Reasoned, NOT confirmed — the header's unverified-symbol admission must survive verbatim in intent.
- FINDING 8: two weekly `time` values are requested, leg alignment is required, an "as of" date is always shown, and `staleAfterDays` (default 21, justified) flags a missing report.
- Index is `na` until the full window exists — no partial-window value is ever published (guardrail 5).
- Sections: § Concept · § Source and citation · § Formula — specification (the implementable spec, 6 numbered steps) · § FINDING 7 — exact argument · § Data requirements · § Inputs contract · § Plot and guide-line contract · § Table contract · § Header text for docs · § Worked examples · § Repaint analysis · § Failure modes · § What would falsify it.
- Blocks dispatch: nothing. backend can build from § Formula — specification without asking a question.

---

## Concept

Managed Money is the speculative trend-following money in CFTC's Disaggregated
Commitments of Traders report. What matters to a trader is not how many
contracts it holds but **how stretched that holding is against its own recent
history** — 200,000 net long contracts is an extreme in one market and a
Tuesday in another.

The net COT Index answers one question: *where does Managed Money's current net
position sit inside its own range over the last N weeks?* It is a stochastic
rescale of the net position to 0..100.

- **100** — Managed Money is at the **most net long** it has been in the window.
- **50** — the middle of the window's range.
- **0** — the **most net short** it has been in the window.
- **>= 80** — conventionally "crowded long"; **<= 20** — "crowded short".

The number describes **positioning**, not a trade. Briese and Williams read
these bands contrarily for the speculative categories, but that interpretation
belongs to the reader; the script must not encode a buy or a sell into the
labels. This is also what killed the old ±80 labels (FINDING 2): a signed label
on a pane holding two unsigned gross series could not be read correctly.

Why net and not gross (already ruled in decisions.md § D-1, not re-litigated
here): gross long and gross short both expand with open interest, so both can
print an extreme at once while net positioning is flat. That is a reading of
open interest wearing a positioning label.

## Source and citation

Not original. The construction is the standard COT Index:

1. **Stephen Briese, *The Commitments of Traders Bible*, Wiley, 2008.**
2. **Larry Williams, *Trade Stocks & Commodities with the Insiders: Secrets of
   the COT Report*, Wiley, 2005.**

Both define the index as a stochastic rescale of a trader category's **net**
position over a rolling window onto **0..100**, with **80/20** as the
conventional extremes, and 26-week / 1-year / 3-year windows all in common use.
This spec follows that definition exactly, which is what makes FINDING 5's
citation honest — the old header claimed "standard" while computing a per-side
variant.

**Two departures must be declared in the header, because they are real:**

- Briese and Williams work primarily from the **legacy** COT report's Commercial
  and Large Speculator categories. This script applies the same index to
  **Managed Money** from the **Disaggregated** report. Managed Money is the
  closest modern analogue of the legacy large-speculator bucket, but it is not
  the same series and the published thresholds were not calibrated on it.
- Neither author, to my knowledge, publishes a per-timeframe rule for how many
  weekly observations to use; **156 weeks (3 years) is a convention choice, not
  a derived number** — and the old tooltip already said so, which is to its
  credit. Keep that admission.

**I did not open either book.** The citation above is deliberately at
book/publisher/year granularity. Do not add a chapter or page number unless
someone actually reads it — an invented chapter is a fabricated citation, which
is worse for guardrail 2 than a coarse one.

## Formula — specification

Symbols:

| Symbol | Meaning | Units |
|---|---|---|
| `L_t` | Managed Money gross LONG positions, weekly observation *t* | contracts |
| `S_t` | Managed Money gross SHORT positions, weekly observation *t* | contracts |
| `net_t` | `L_t - S_t` | contracts, **signed** |
| `W` | `lookbackWeeks` | weekly observations |
| `H_t` | the most recent `W` confirmed weekly `net` observations, ending at *t* | set |

**Sign convention, stated explicitly:** `net > 0` means Managed Money is **net
long** (bullish positioning). `net < 0` means net short. This matches the pack's
"positive is bullish/long/risk-on across every script here". The subtraction is
long minus short, never the reverse.

The index:

```
        lo_t = min( H_t ∪ {net_t} )
        hi_t = max( H_t ∪ {net_t} )

        cotIndex_t =  na                                if net_t is na
                      na                                if |H_t| < W
                      na                                if hi_t == lo_t
                      100 * (net_t - lo_t) / (hi_t - lo_t)   otherwise
```

Range is **[0, 100] inclusive**, guaranteed by including `net_t` in the range.

### Step 1 — request both legs on "W", with times

```pine
[mmLongPos,  asOfLong]  = request.security(mmLongSymbol,  "W", [close, time],
     lookahead = barmerge.lookahead_off, ignore_invalid_symbol = true)
[mmShortPos, asOfShort] = request.security(mmShortSymbol, "W", [close, time],
     lookahead = barmerge.lookahead_off, ignore_invalid_symbol = true)
```

`time` inside the expression argument is the **requested (weekly) bar's open
time**, which is what FINDING 8 needs. Requesting it from **both** legs is
deliberate: it lets step 2 detect one leg going stale while the other updates.

### Step 2 — alignment and net

```pine
legsAligned = not na(asOfLong) and not na(asOfShort) and asOfLong == asOfShort
asOfTime    = legsAligned ? asOfLong : na
net         = (na(mmLongPos) or na(mmShortPos) or not legsAligned) ? na
                                                 : mmLongPos - mmShortPos
```

If the two legs report different weekly bars, `net` would mix two different
reporting weeks. That is exactly the "plausible value" guardrail 5 forbids, so
it degrades to `na` instead.

### Step 3 — the weekly window (this is FINDING 1's fix)

`ta.lowest` / `ta.highest` are **removed from the script entirely.** They walk
the **chart's** bar series, so `ta.lowest(x, 156)` is 156 *chart bars* — 3 years
on a weekly chart, 7 months on a daily one, 5 weeks on an hourly one. Pinning
the *request* to `"W"` does not pin the *window* to weeks, because
`request.security()` returns a series sampled onto the chart's timeframe.

The replacement counts **weekly observations**, not bars:

```pine
var float[] netHist = array.new_float()

newWeekly = not na(asOfTime) and (na(asOfTime[1]) or asOfTime != asOfTime[1])

if newWeekly and barstate.isconfirmed and not na(net)
    array.push(netHist, net)
    if array.size(netHist) > lookbackWeeks
        array.shift(netHist)
```

**Why this is timeframe-invariant.** `asOfTime` is the open time of the weekly
bar of the COT2 series. It changes exactly once per weekly observation, whatever
the chart's timeframe, so `array.size(netHist)` is a count of COT reports and
`lookbackWeeks` genuinely means weeks on a 1-hour chart, a daily chart and a
monthly chart alike. `array.shift` caps it at `W`, so the array is exactly the
`W` most recent confirmed weekly nets.

**The `barstate.isconfirmed` gate is mandatory, not stylistic** — see
§ Repaint analysis. Push-then-compute is the required order within the bar.

### Step 4 — range, including the current observation

```pine
histReady = array.size(netHist) >= lookbackWeeks
netLo = (histReady and not na(net)) ? math.min(array.min(netHist), net) : na
netHi = (histReady and not na(net)) ? math.max(array.max(netHist), net) : na
```

The union with `net` is a no-op on every confirmed bar (the value is already in
the array) and matters on exactly one case: the realtime bar on which a new
weekly observation has appeared but has not yet been pushed. Without the union
the index can print **above 100 or below 0** for that bar. With it, the bound
holds always.

Consequence, disclosed rather than engineered away: during that interval the
effective window is `W + 1` observations rather than `W`. That is a bounded,
one-observation imprecision on the live bar only, and it never affects a closed
bar.

### Step 5 — the index

```pine
cotIndex = (na(net) or not histReady or netHi == netLo) ? na
            : 100.0 * (net - netLo) / (netHi - netLo)
```

Three degenerate cases, all resolving to `na`, none resolving to a value:

| Case | Result | Why not a number |
|---|---|---|
| Either symbol unresolved, or legs misaligned (`net` is `na`) | `na` | guardrail 5: a failed symbol must never read as a zero |
| Fewer than `W` weekly observations collected | `na` | a 9-week range dressed as a 156-week range is the FINDING 1 failure in a new costume |
| `netHi == netLo` (constant net across the whole window) | `na` | division by zero; and there is no meaningful "position within a range" when the range is a point. **Never 50.** |

`0` is a real, meaningful output (net is at the bottom of its range) and must be
distinguishable from `na` in the table. `na` renders `"n/a"`.

### Step 6 — staleness

```pine
stale = not na(asOfTime) and (timenow - asOfTime) > staleAfterDays * 86400000
```

`asOfTime` is the open time of the newest **closed** weekly bar of the COT2
series. In normal operation that is at most ~13 days behind wall-clock (the
previous week's Monday open, viewed on the current week's Sunday).
`staleAfterDays = 21` therefore absorbs the ordinary lag plus one holiday slip,
and fires only when a weekly report has genuinely gone missing. See § Inputs
contract for the default's justification.

## FINDING 7 — exact argument

`lookahead = barmerge.lookahead_off`, passed explicitly on **both**
`request.security()` calls in step 1, as a named argument alongside
`ignore_invalid_symbol = true`.

**It does not move under FINDING 1's fix.** The two fixes touch different
places: `lookahead` is an argument of `request.security()`, while FINDING 1's
fix is entirely outside the call (the array in step 3 operates on the returned
series). The expression argument changed from `close` to `[close, time]`;
`lookahead` is a sibling of that argument, not part of it, so it is written the
same way it would have been before.

Both calls being explicit is what clears `pine_check.py`'s two P008 hits at
:39 and :40 and makes `--strict` exit 0 on this point.

## Data requirements

| Item | Value | Status |
|---|---|---|
| Long leg (default) | `COT2:088691_F_MMP_L_ALL` | **RECONSTRUCTED, NOT CONFIRMED** |
| Short leg (default) | `COT2:088691_F_MMP_S_ALL` | **RECONSTRUCTED, NOT CONFIRMED** |
| Timeframe requested | `"W"` | fixed, not an input |
| Non-resolution behaviour | `ignore_invalid_symbol = true` -> `na` -> `"n/a"` in table | required |

**FINDING 6 — why `_ALL` and not `_OLD`.** CFTC's `ALL / OLD / OTHER` breakout
exists because certain **agricultural** contracts have crop years. "Old crop"
has no meaning for a metal. Gold (contract market code `088691`) is not a
crop-year contract, so the only meaningful aggregation for it is `ALL`. An
`_OLD` ticker on Gold either fails to resolve or resolves to a series identical
to `ALL` by construction that could silently diverge if the vendor changes how
it fills the unused breakout. `_F_` (futures-only, as against
futures-and-options) is a legitimate choice and is retained unchanged.

**This is a reasoned correction, not a confirmation.** I have no browser tool
and did not open TradingView's symbol search. The prior of the reconstruction
being right is now higher; it is not 1. **Guardrail 3 remains unmet.**

Therefore, and this is not negotiable under project.md § The script header
contract: **the header's "IMPORTANT — VERIFY THE SYMBOLS BEFORE TRUSTING THIS"
block must survive verbatim in intent.** Only the two quoted default strings
change from `_OLD` to `_ALL`. The admission that the tickers were reconstructed
from search results rather than confirmed, the instruction to search `088691`
in the symbol input, and the note that an unresolved symbol shows `n/a`, all
stay. Deleting or softening any of it is a regression regardless of the code
improving around it. The exact replacement text is in § Header text for docs.

## Inputs contract

| Input | Before | After | Note |
|---|---|---|---|
| `mmLongSymbol` | `input.symbol("COT2:088691_F_MMP_L_OLD", ...)` | same call, default `"COT2:088691_F_MMP_L_ALL"` | title and group unchanged |
| `mmShortSymbol` | `input.symbol("COT2:088691_F_MMP_S_OLD", ...)` | same call, default `"COT2:088691_F_MMP_S_ALL"` | title and group unchanged |
| `lookbackWeeks` | `input.int(156, ...)` | **default unchanged at 156**; tooltip rewritten | now genuinely weeks |
| `staleAfterDays` | — | **NEW** `input.int(21, title="Flag data stale after (days)", minval=8, group="Data Source")` | see justification |

**`lookbackWeeks` stays at 156.** It is 3 years, a convention both cited authors
treat as standard alongside 26 weeks and 52 weeks. It is a convention choice,
not a derived number, and the tooltip must keep saying so. New tooltip text:

> Rolling window of **COT reports** (one per week) the current net position is
> ranked against. This now counts weekly reports, not chart bars, so it means
> the same window on every chart timeframe. 156 ≈ 3 years, a common convention;
> some analysts use 26 (6mo), 52 (1yr) or 260 (5yr). The index reads `n/a` until
> this many weekly reports have been collected from the chart's loaded history.

**`staleAfterDays` default 21, justified.** CFTC compiles positions as of
Tuesday's close and publishes the following Friday 15:30 ET. The newest closed
weekly bar's open time is therefore at most about 13 days behind wall clock in
ordinary operation. 21 days clears that ordinary lag with room for one
holiday-delayed release, and fires when a full report cycle has been missed.
`minval = 8` prevents a setting below one report cycle, which would flag stale
permanently.

**No input for the guide lines.** FINDING 4 offered "move them, or make them an
input"; on a 0..100 scale the conventional values are 80 and 20 and there is no
longer a scale mismatch to parameterise. Fixed `hline`s, matching the cited
source, are the simpler and more honest choice.

## Plot and guide-line contract

**Removed:** `plot(longIndex, "MM Long Index", green)`,
`plot(shortIndex, "MM Short Index", red)`, `hline(0, "Midpoint")`,
`hline(80, "Long Extreme (crowded)")`, `hline(-80, "Short Extreme (crowded)")`.

**Added — one plot:**

```pine
plot(cotIndex, title = "MM Net COT Index", color = color.new(color.blue, 0), linewidth = 2)
hline(80, "Crowded long (80)",  color = color.new(color.green, 60), linestyle = hline.style_dashed)
hline(50, "Midpoint (50)",      color = color.gray,                 linestyle = hline.style_dotted)
hline(20, "Crowded short (20)", color = color.new(color.red, 60),   linestyle = hline.style_dashed)
```

A single neutral plot colour is deliberate: green/red belonged to the two gross
series and would now read as a directional recommendation the script is not
making.

**FINDING 2 is dissolved, not patched.** There is one signed series, so "80 =
crowded long" is unambiguous — there is no second plot for which the same guide
line means the opposite thing.

**FINDING 4 is dissolved too.** The scale is 0..100, so 80/20 *are* the
conventional Briese/Williams extremes. The old ±80 on a −100..+100 scale were
the 90/10 extremes wearing the 80/20 name.

## Table contract

`table.new(position.top_right, 2, 6, border_width = 1)` — **2 columns, 6 rows**
(was 2 × 4). Column 0 left-aligned label, column 1 right-aligned value. Rendered
under `barstate.islast` as today.

| Row | Label (col 0) | Value (col 1) | `na` / degenerate rendering |
|---|---|---|---|
| 0 | `MM Long Position` | `fmtPos(mmLongPos)` | `n/a` |
| 1 | `MM Short Position` | `fmtPos(mmShortPos)` | `n/a` |
| 2 | `MM Net Position` | `fmtPos(net)`, **signed** | `n/a` |
| 3 | `Net COT Index (0-100)` | `fmt(cotIndex)` | `n/a` |
| 4 | `Window` | `array.size(netHist) + "/" + lookbackWeeks + " weeks"` | always a number, never `n/a` |
| 5 | `Data as of (series bar)` | `str.format_time(asOfTime, "yyyy-MM-dd", "GMT")`, with `" — STALE"` appended when `stale` | `n/a` when `asOfTime` is `na`; `n/a (legs misaligned)` when both legs resolved but `legsAligned` is false |

Rows 0 and 1 are where the **gross** long/short survive, per D-1: raw numbers in
the table, never their own index plots.

Row 4 exists so that "why is the index `n/a`?" is answerable on screen — it
distinguishes "still collecting history" from "symbol did not resolve", which
guardrail 5 requires to be distinguishable.

Row 5's label says **"series bar"**, not "CFTC as-of". Whether TradingView
stamps the COT2 weekly bar at CFTC's Tuesday as-of date or at the Friday
release date is unverified (carried from the prior audit's § Repaint analysis),
and the label must not assert the one I could not check.

Cell background: row 3 tinted green when `cotIndex >= 80`, red when
`<= 20`, otherwise no tint; `na` when `cotIndex` is `na`. Row 5 tinted with a
warning colour when `stale`. `fmt`/`fmtPos` helpers are unchanged.

## Header text for docs

Text only — docs places it, backend does not compose it. It replaces lines
:19-26 ("WHAT THIS COMPUTES") and amends the two ticker strings inside the
existing :6-17 block, which is otherwise untouched.

```
// IMPORTANT — VERIFY THE SYMBOLS BEFORE TRUSTING THIS:
// TradingView's exact ticker for "Managed Money Positions - Long/Short" was reconstructed
// from search results, not confirmed by opening the live TradingView symbol page (my usual
// double-check tools were unavailable when this was written). The defaults below
// (COT2:088691_F_MMP_L_ALL / _S_ALL) are my best reconstruction for Gold. The _ALL suffix
// is a reasoned correction from an earlier _OLD: CFTC's ALL/OLD/OTHER breakout exists for
// crop-year agricultural contracts and has no meaning for a metal, so ALL is the only
// aggregation that applies to Gold. That is reasoning from CFTC's report structure — it is
// STILL NOT A CONFIRMATION that the ticker resolves. To confirm or fix them yourself: click
// the symbol inputs below in this indicator's settings, type "088691" (Gold's CFTC code)
// into the symbol search, and look through the COT2-prefixed results for "Managed Money
// Positions - Long" and "... - Short" — pick those exact entries. If a symbol input shows
// "n/a" in the table, that symbol didn't resolve.
//
// For a different commodity/future, look up its CFTC code (visible on the CFTC COT report
// itself, or via a site like tradingster.com/cot) and search for that code instead.
//
// WHAT THIS COMPUTES:
// The NET COT Index. net = Managed Money gross longs - gross shorts (positive = net long).
// The index is not the position size — it is where the current net position sits inside its
// own range over the last N weekly COT reports, rescaled to 0..100:
//   100 = the most net long Managed Money has been in the window
//    50 = the middle of the window's range
//     0 = the most net short it has been in the window
// 80 and 20 are the conventional "crowded" extremes. This describes POSITIONING, not a
// trade — the contrarian reading of a crowded extreme is the reader's call, not the
// script's. Gross long and gross short are shown as raw table rows only; they are NOT
// indexed separately, because both sides expand together with open interest and can print
// simultaneous "extremes" while net positioning is flat.
//
// SOURCE:
// The COT Index — a stochastic rescale of a trader category's NET position over a rolling
// window onto 0..100, with 80/20 as the conventional extremes — as defined in:
//   Stephen Briese, "The Commitments of Traders Bible", Wiley, 2008.
//   Larry Williams, "Trade Stocks & Commodities with the Insiders: Secrets of the COT
//     Report", Wiley, 2005.
// (Book-level citation only: I have not opened either volume to cite a chapter.)
//
// WHERE THIS DEPARTS FROM THE SOURCE:
// - Both authors work mainly from the LEGACY report's Commercial and Large Speculator
//   categories. This applies the same index to MANAGED MONEY from the DISAGGREGATED
//   report — the closest modern analogue of the large-speculator bucket, but not the same
//   series, and the published 80/20 thresholds were not calibrated on it.
// - 156 weeks (3 years) is a convention choice, not a derived number. 26, 52 and 260 are
//   all in common use.
//
// WHAT DEGRADES, AND HOW YOU SEE IT:
// - The window counts WEEKLY COT REPORTS, not chart bars, so it means the same thing on
//   every chart timeframe. It is built from the weekly reports visible in the chart's
//   loaded history, so on a very low timeframe (1m/5m) the chart never loads enough weeks
//   and the index stays "n/a" — the table's "Window" row shows how many it has.
// - The index is "n/a", never a number, when: a symbol doesn't resolve; the two legs report
//   different weeks; fewer than N reports have been collected; or the net position was
//   constant across the whole window (no range to rank against).
// - The table shows the date of the weekly series bar the reading came from, and marks it
//   STALE past the configured age. Note: whether that date is CFTC's Tuesday as-of date or
//   the Friday release date is NOT verified.
```

## Worked examples

Both series are hand-computed from § Formula — specification and then
recomputed by an independent script. These are the expected values backend
should see and quant-audit should check against.

### Example A — the audit's FINDING 3 five-week series

The case that motivated D-1. `lookbackWeeks = 5`.

| week | `L` | `S` | `net` | expected `cotIndex` |
|---|---|---|---|---|
| 1 | 100,000 | 50,000 | 50,000 | `na` — window not full |
| 2 | 110,000 | 55,000 | 55,000 | `na` — window not full |
| 3 | 120,000 | 60,000 | 60,000 | `na` — window not full |
| 4 | 130,000 | 65,000 | 65,000 | `na` — window not full |
| 5 | 200,000 | 150,000 | 50,000 | **0.00** |

Week 5 by hand: window `{50, 55, 60, 65, 50}`k, `lo = 50,000`, `hi = 65,000`,
`net = 50,000` → `100 × (50,000 − 50,000) / 15,000` = **0.00**.

This is the headline contrast. The **old** script printed **long index +100 and
short index +100 simultaneously** on this series. The new index prints **0** —
Managed Money's net position is at the bottom of its five-week range, which is
what actually happened. The old reading was open interest wearing a positioning
label.

With `lookbackWeeks = 3` on the same series, for a second check vector:
`na, na, 100.00, 100.00, 0.00`.

### Example B — the audit's twelve-week series

| week | `L` | `S` | `net` |
|---|---|---|---|
| 1 | 120,000 | 60,000 | 60,000 |
| 2 | 135,000 | 55,000 | 80,000 |
| 3 | 150,000 | 50,000 | 100,000 |
| 4 | 168,000 | 45,000 | 123,000 |
| 5 | 180,000 | 40,000 | 140,000 |
| 6 | 175,000 | 48,000 | 127,000 |
| 7 | 160,000 | 55,000 | 105,000 |
| 8 | 140,000 | 70,000 | 70,000 |
| 9 | 125,000 | 85,000 | 40,000 |
| 10 | 110,000 | 95,000 | 15,000 |
| 11 | 100,000 | 105,000 | −5,000 |
| 12 | 155,000 | 62,000 | 93,000 |

**`lookbackWeeks = 12`** — weeks 1-11 are `na`, week 12 is:
`lo = −5,000`, `hi = 140,000`, `net = 93,000` →
`100 × 98,000 / 145,000` = **67.59**.

This independently reproduces the figure the prior audit reached on the same
series by a separate hand computation, which is the cross-check that the
rescale is the one the cited definition describes.

**`lookbackWeeks = 5`**, giving eight defined values to check:

| week | window (k) | `lo` | `hi` | expected `cotIndex` |
|---|---|---|---|---|
| 5 | 60,80,100,123,140 | 60,000 | 140,000 | **100.00** |
| 6 | 80,100,123,140,127 | 80,000 | 140,000 | **78.33** |
| 7 | 100,123,140,127,105 | 100,000 | 140,000 | **12.50** |
| 8 | 123,140,127,105,70 | 70,000 | 140,000 | **0.00** |
| 9 | 140,127,105,70,40 | 40,000 | 140,000 | **0.00** |
| 10 | 127,105,70,40,15 | 15,000 | 127,000 | **0.00** |
| 11 | 105,70,40,15,−5 | −5,000 | 105,000 | **0.00** |
| 12 | 70,40,15,−5,93 | −5,000 | 93,000 | **100.00** |

Note week 7: the index reads 12.50 — inside the "crowded short" band — while
net positioning is **+105,000 contracts net long**. That is correct behaviour
for a stochastic, and it is exactly why the window length is a material choice
and why the header must keep saying 156 is a convention rather than a
derivation. A short window makes the index say "low within its recent range",
which is not the same statement as "net short".

### Degenerate check vectors

| Input | `lookbackWeeks` | Expected |
|---|---|---|
| `net` constant at 50,000 for 6 weeks | 3 | `na` on every bar (`hi == lo`) |
| Long symbol unresolved, short resolves | any | `net` = `na`, index `na`, table row 0 `n/a`, row 1 a number |
| 9 weekly observations collected | 156 | `na`, table Window row reads `9/156 weeks` |
| Legs report different weekly bars | any | `net` `na`, index `na`, row 5 `n/a (legs misaligned)` |

## Repaint analysis

Required by the pack for any artifact touching a computed series. Walked against
the pack's table.

**Explicit `lookahead_off` on both calls** means each chart bar receives the
most recently **closed** weekly bar's value when the chart timeframe is below
`"W"`. Historical bars do not rewrite. This was already true by Pine's default;
FINDING 7 makes it readable in the file rather than inferable from
documentation, which is guardrail 1's actual requirement.

**The array is the new repaint surface, and it is the one thing in this spec
that can go wrong silently.** Pine rolls back *series* variables on each
realtime tick, but **mutations to a `var` array are not rolled back**. Pushing
on an unconfirmed bar would append the developing value on every tick, growing
the array without bound and corrupting every subsequent min/max — and the
corruption would be invisible on historical bars, appearing only in live use.
`barstate.isconfirmed` on the push is therefore **mandatory**. Stated here
rather than left to the implementer because it is not inferable from the
formula.

**`newWeekly` is evaluated from `asOfTime`, which is itself
`lookahead_off`-sourced**, so on a sub-weekly chart the transition fires on the
first chart bar after a weekly close and pushes an already-final value. On a
weekly chart the transition fires at the new bar's open and the push happens at
that bar's confirm, so the value pushed is that week's final close. Both paths
push exactly one final value per week.

**The displayed reading on the live bar is provisional on a weekly chart**, as
it was before: the chart bar has not closed, so `mmLongPos`/`mmShortPos` are the
developing week. Step 4's union with `net` keeps the index inside 0..100 while
that is true. This is disclosed by the table's "Data as of (series bar)" row —
a dashboard showing the current provisional state is legitimate; showing it
without saying so is not.

**The timing question from the prior audit is unresolved and carried forward.**
If TradingView stamps the COT2 bar at the Tuesday as-of date, then on a chart
symbol whose Friday session ends before 15:30 ET (a London- or Frankfurt-listed
gold ETF closes 11:30 ET) the weekly bar could close before the report is
public. I could not determine which stamping is real. The remedy is the same one
already specified: the as-of date is on screen, so the reader can answer it from
their own chart.

**Nothing else repaints.** No `ta.pivothigh`/`ta.pivotlow`, no `ta.valuewhen`,
no alerts, no forward series indexing, no strategy calls. `ta.lowest`/
`ta.highest` are gone entirely.

## Failure modes

| Mode | Behaviour under this spec | Visible? |
|---|---|---|
| Symbol does not resolve | `na` → `"n/a"` in table, no plot | yes |
| `_ALL` also turns out to be wrong | same as above — `n/a`, not a wrong number | yes |
| One leg stale, other updating | legs misaligned → index `na`, row 5 says so | yes |
| Both legs stale (vendor outage, delisted series) | `gaps_off` holds the last value, but row 5 shows an old date and `— STALE` past `staleAfterDays` | yes |
| Insufficient loaded history | index `na`, Window row shows the count | yes |
| Very low chart timeframe (1m/5m) | never enough weeks loaded → permanent `n/a` | yes, via Window row |
| Constant net across the window | `na`, never 50 | yes |
| CFTC release delayed by a federal holiday | one extra week of lag; `staleAfterDays = 21` absorbs it without a false flag | n/a |
| Gold's contract code changes, or the trader switches commodity without changing both inputs | one leg resolves, one does not, or legs misalign → `na` | yes |
| `lookbackWeeks` set very low | index saturates at 0/100 frequently — mathematically correct, interpretively weak; tooltip warns | partially |

Every one of these degrades to `n/a` or an explicit disclosure. **No failure
mode in this spec produces a plausible-looking number.**

## What would falsify it

The metric claims: *this number is where Managed Money's current net position
sits inside its own N-week range.* Observations that would show it is not:

- Plot the index on a weekly chart and on a 1-hour chart of the same instrument
  on the same date. **They must be identical.** If they differ, the window is
  still being counted in bars and FINDING 1 is not fixed. This is the single
  most important check, and it is the one the old script fails.
- Read the raw `MM Long Position` and `MM Short Position` table rows over N
  weeks, compute `L − S` by hand, rank the current value in that set, and
  compare. A discrepancy falsifies the rescale.
- Set `lookbackWeeks` to a value larger than the loaded history. The index must
  read `n/a`. A number here means a partial window is being published.
- Find a week where the index prints outside `[0, 100]`. That falsifies step 4's
  union.
- Find a table showing a comma-formatted position count with no as-of date, or
  an as-of date more than `staleAfterDays` old without the STALE marker. Either
  falsifies FINDING 8's fix.
- Compare against a published COT Index for the same market and window from
  either cited author. Agreement is not provable here (different trader
  category, see § Source and citation), but a systematic sign or scale
  disagreement would falsify the implementation rather than the definition.
