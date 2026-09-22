REPORT 2026-09-18-vertical-volume-indicator/02
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order's verification field was NONE; RESEARCH mode produces a specification, not a runnable check. Formula self-checked against a 3-bar/12-intrabar hand example computed independently in Python (see § Formula, worked example) — that is an internal consistency check, not an external anchor, and is labelled as such.

contract_notes:
  - the profile is declared ORIGINAL per guardrail 2 — the script header must say so, and must say it is a candle-derived approximation, not TradingView's native Volume Profile — see § Source
  - the coverage diagnostic (bars covered C of N, and binned/reported volume ratio) is a required displayed element, not decoration — a build that drops it makes the guardrail-5 degradation invisible — see § Data requirements
  - guardrail 3 is trivially satisfied: this script requests no external symbol, only the chart symbol at a lower timeframe — see § Data requirements

pack_corrections:
  - none

handoff:
  - formula is fully specified and implementable: bin count over the window's [lowest low, highest high], close-binning of lower-timeframe volume, normalised to the window max — see § Formula
  - window is bar-count based: last N confirmed bars, N default 120, current unclosed bar excluded by default — TradingView's visible range is not a safe basis and the reason is stated — see § Formula, § Repaint analysis
  - primary data path is `request.security_lower_tf()`; `request.footprint()` named as an option with its tradeoff, not specified — see § Data requirements
  - three exact API details this brief could not pin and the build lane must verify against the Pine v6 reference before relying on them — see § Unpinned API details
  - two forbidden implementations (spreading bar volume across its range; scaling a partial profile up to look complete) — both are guardrail-5 violations that would look correct — see § Failure modes
  - the falsification test is concrete and runnable by the human in the editor during the compile check — see § What would falsify it
  - parameter defaults and which of them are chosen by feel are stated per parameter — see § Formula, parameter table

risks:
  - platform-research.md says `request.security_lower_tf()` "falls back to a cruder method" beyond TradingView's intrabar history limit. If that fallback is silent — i.e. the call returns a populated but coarse array rather than `na` — the script cannot detect degraded bars, and guardrail 5 cannot be satisfied by detection alone. The mitigation I specify is a conservative default window plus a header disclosure; see § Unpinned API details, item 1.
  - `request.footprint()`'s signature, availability by plan and by symbol, and its own history limits are not pinned by platform-research.md's own caveat, and I hold no web tools. I name it as an option and specify nothing that depends on its parameters.
  - Value Area (the shaded high-activity band the native tool draws) is deliberately unspecified: implementing the ~70% band correctly needs a named Market Profile construction I cannot cite from here, and guessing one would breach guardrail 2. Point of Control is specified because it is argmax and needs no external authority.
  - The default bin count (24) and window length (120 bars) are chosen by feel against a daily-chart ETF use case, per the pack's rule that a feel-chosen default is declared as such. Neither is derived from a source.

## Orchestrator brief
- decision: declared **ORIGINAL** per guardrail 2 — no citable canonical volume-profile construction is reachable from this lane; header must say so.
- decision: window is **last N confirmed bars** (N=120 default), not TradingView's visible range — visible range is unreadable/unstable from Pine; reasoning in § Formula.
- decision: **bin count** (24), not bin width — a fixed price width is not portable across instruments.
- decision: **close-binning** of lower-timeframe intrabar volume; range-spreading named and rejected, with the tradeoff stated.
- decision: current unclosed bar **excluded by default** (opt-in input, labelled provisional) — keeps guardrail 1 clean without losing live use.
- decision: primary data path `request.security_lower_tf()`; `request.footprint()` is an option, not specified.
- blocks dispatch: nothing. Three API details need verification by the build lane, not by a further research round — § Unpinned API details.
- lane split: none set — single script, `backend` builds from § Formula + § Data requirements; `docs` owns the header admissions in § Source.
- sections: Concept · Formula (incl. parameter table + worked example) · Source · Data requirements · Unpinned API details · Repaint analysis · Failure modes · What would falsify it · Out of scope.

## Concept

A volume profile answers a different question from the ordinary volume histogram at the bottom of the chart. The usual histogram is indexed by *time* — it says how much traded during each bar. A profile is indexed by *price* — it says how much has traded at each price level over a stated stretch of history, drawn as horizontal bars running leftward from the right edge, so the long bars sit at the prices where the most business was done. For the repo's standing research question — what volume behaviour says about when to open and close a position — the profile is a *location* tool rather than a timing one: it identifies high-volume nodes, prices at which a large amount of stock changed hands and where subsequent trade tends to pause, and low-volume nodes, prices that were passed through quickly and which price tends to traverse fast again. A trader deciding where to place a stop, where to expect an advance to stall, or whether the current price is at a level the market has already accepted rather than one it merely visited, reads that from the shape of the profile. It says nothing about direction and nothing about whether the volume was buying or selling — that is order-flow/VSA territory, ruled out of this run by D-2.

## Formula

### Notation

- `N` — window length in bars.
- `B` — bin count.
- Window `W` = the last `N` **confirmed** bars, i.e. bars `bar_index-N` through `bar_index-1` when `includeCurrentBar = false`. If fewer than `N` bars of history exist, `W` is all available confirmed bars and `M = |W|`.
- `R_lo = min over i in W of low[i]`, `R_hi = max over i in W of high[i]`.
- For each bar `i` in `W`, `S_i` = the set of lower-timeframe intrabars inside bar `i`, each intrabar `k` carrying a close `c_{i,k}` and a volume `v_{i,k}`.

### Bin construction — bin *count*, not bin width

```
h   = (R_hi - R_lo) / B                        bin height, price units
bin j spans [ R_lo + j*h , R_lo + (j+1)*h )    for j = 0 .. B-1
the top bin is closed at R_hi: a print exactly at R_hi lands in bin B-1
```

**Why count and not width.** A fixed bin width in price units is not portable: 0.25 is fine resolution on a $30 ETF and absurd on a $600 one, and the same script on two instruments would produce profiles that are not the same object. A bin count over the window's own range auto-scales to whatever the instrument and the window are doing, and makes `B` a resolution knob the trader can reason about ("24 slices of the range") rather than a per-symbol tuning chore. The cost is that `h` changes whenever the window's extremes change, so bin boundaries are not stable across bars — that is an honest property of the construction and is covered in § Repaint analysis.

### Volume aggregation per bin — close-binning

```
V_j = SUM over i in W, SUM over k in S_i  of  v_{i,k} * 1[ bin(c_{i,k}) = j ]

bin(p) = clamp( floor( (p - R_lo) / h ), 0, B-1 )
```

Each intrabar contributes its **entire** volume to the single bin containing its **close**. Nothing is split, nothing is weighted.

**The rejected alternative, and why.** The other defensible rule is range-spreading: distribute each intrabar's volume evenly (or proportionally) across every bin its `[low, high]` touches. It is arguably more faithful for a wide intrabar, but its error mode is worse for this use: it smears volume into prices where nothing necessarily traded, which manufactures apparent high-volume nodes at bin boundaries and softens exactly the sharp POC the trader is looking for. Close-binning's error is easier to state and easier to bound — it concentrates each intrabar's volume at the price it last printed at, and that error shrinks as the lower timeframe gets finer. **This is a definitional choice, not a correctness one**; the build must not silently switch to the other rule, and the header must name which one is implemented.

### Normalisation to a bar length

```
V_max = max over j of V_j
L_j   = V_j / V_max                            unitless, in [0, 1]
```

`L_j` is what the renderer multiplies by whatever maximum width it uses. The brief stops at `L_j` deliberately — the mapping from `L_j` to boxes/lines/bars is the build lane's (non-goal).

**What the normalisation means and does not mean.** The profile is **self-relative**: it is normalised to the largest bin in *this window on this symbol*, so a full-length bar means "the busiest price in this window", never an absolute quantity. Two charts' profiles are not comparable by bar length, and the same chart's profile is not comparable across a change of `N`. This matches the pack's rule that raw volume is not comparable across instruments or eras — normalising against the window max is the declared choice here. The raw `V_j` must remain recoverable (a tooltip or a table row on the POC bin at minimum), because a length that is 1.0 in a dead window and 1.0 in a frantic one are not the same fact.

`V_max = 0` (no volume anywhere in the window) is not a normalisation edge to be smoothed — it is an unavailable profile. See § Failure modes.

### Point of Control

```
POC = argmax_j V_j ,  ties resolved to the lower j (the lower price)
```

Stated because it is argmax and needs no external authority. The tie rule must be explicit in code rather than left to whatever `array.indexof` happens to do, so that two runs on the same data draw the same line. **Value Area is out of scope** — see § Out of scope.

### Parameters and defaults

| Parameter | Default | Basis for the default |
|---|---|---|
| `lookbackBars` N | 120 | Feel-chosen, with one hard constraint behind it: ~6 months of daily bars is a window over which "where has business been done" is still a live question rather than archaeology, and it is short enough to stay well inside TradingView's intrabar history budget at a 5-minute lower timeframe (§ Data requirements). Declared as chosen by feel per the pack. |
| `binCount` B | 24 | Feel-chosen. Reasoning, stated so it can be argued with: below ~12 the POC band is too wide to place a stop against; above ~48 each bin holds too few intrabar prints on a typical daily-chart window and the profile becomes a comb of sampling noise rather than a distribution. 24 sits in the middle. |
| `minBars` | 20 | Feel-chosen floor. Below 20 bars the range extremes are set by one or two bars and the binning is not describing a distribution. Below this, output is `n/a`, not a profile. |
| `ltfResolution` | auto-derived from `timeframe.period`; overridable | See § Data requirements. Not hard-coded, per the pack's rule that a timeframe-dependent parameter must derive from `timeframe.period` or say so in its tooltip. |
| `includeCurrentBar` | false | Guardrail 1. See § Repaint analysis. When true, the input's tooltip and the on-chart label must both say the profile is provisional. |

Every `input.int` carries a tooltip naming its unit in **bars** (pack § Units): `N` is 120 bars, which is six months on a daily chart and six hours on a 3-minute one.

### Worked example

Three bars, four intrabars each, `B = 4`, window extremes `R_lo = 10.00`, `R_hi = 12.50`, so `h = 0.625`.

| bar | intrabar (close, volume) |
|---|---|
| 1 | (10.2, 100) (10.6, 300) (10.9, 200) (10.4, 150) |
| 2 | (11.4, 250) (11.1, 400) (10.8, 120) (11.9, 80) |
| 3 | (12.3, 60) (11.7, 500) (11.5, 220) (12.0, 90) |

| bin j | price span | `V_j` | `L_j` |
|---|---|---|---|
| 0 | [10.000, 10.625) | 550 | 0.5670 |
| 1 | [10.625, 11.250) | 720 | 0.7423 |
| 2 | [11.250, 11.875) | 970 | **1.0000** ← POC |
| 3 | [11.875, 12.500] | 230 | 0.2371 |

`Σ V_j = 2470`, which equals the sum of all intrabar volume — the invariant in § What would falsify it. Computed independently in Python from the formula above, not read off an implementation; there is no implementation yet. This is an internal consistency check on the brief's own arithmetic, not an external anchor.

### The window, and why not "visible range"

The native tool's most-used mode is Visible Range, and that is not available here in the same way. Two candidate mechanisms exist and both are rejected as the default:

1. **Chart visible-range variables.** Pine exposes chart-extent variables (`chart.left_visible_bar_time` / `chart.right_visible_bar_time` by my recollection — *not* pinned by platform-research.md, see § Unpinned API details item 3). Even granting they exist, a window defined by them makes the script's output a function of where the user has scrolled: the profile changes when nothing about the market changed, and two screenshots of "the profile" at the same moment disagree. For a repo whose first guardrail is that a displayed value must not move after its bar closed, that is the wrong default even though it is not literally repainting.
2. **Session or period anchoring** (`ta.change(time("D"))` and similar) — a real and defensible alternative that maps to the native tool's Session Volume mode. Rejected as the default only because it makes the window length a function of the chart timeframe rather than a stated number, and because the trader's framing ("where has business been done lately") is not session-bounded. Worth offering later as an anchor mode; explicitly not specified here.

**A bar-count window is defensible rather than arbitrary** because it is the only one of the three that is (a) stated as a number the trader sets and can quote, (b) identical for two people looking at the same symbol at the same moment, and (c) directly commensurable with the intrabar history limit that actually constrains this script — you can reason about whether 120 bars of 5-minute data is available in a way you cannot reason about "whatever is on screen".

## Source

**ORIGINAL**, declared per guardrail 2. The script header must say so.

The reasoning, because guardrail 2 asks for it rather than for a bare label:

- There is no regulator or exchange spec for this the way there is for a COT field. Volume-at-price is a family of constructions, not one.
- The nearest named methodology is J. Peter Steidlmayer's Market Profile (CBOT), but that is **TPO** — time-at-price, counting how many time brackets traded at each level — which is a genuinely different measurement from volume-at-price. Citing it for this construction would be a false citation, which is worse than declaring ORIGINAL.
- TradingView's own Volume Profile is computed server-side from its tick data (platform-research.md § 1). Its exact construction is not published as a formula, so it cannot be reproduced — only approximated. A header claiming to implement it would be claiming an authority that does not exist.

The header therefore owes the reader three admissions, in the repo's established style (`systemic_stress_dashboard.pine` is the precedent — an original approximation that says so):

1. Original construction; no external authority.
2. Built from **lower-timeframe candle closes, not tick data** — an estimate, and never tick-exact even when the intrabar data is fully available (platform-research.md § 2).
3. **Not** TradingView's native Volume Profile and will not agree with it bar for bar.

## Data requirements

**No external symbol is requested.** The script reads the chart symbol only, at a lower timeframe. Guardrail 3 is therefore satisfied without any `input.symbol()`: there is no ticker to reconstruct and nothing to verify. If a future version adds a comparison symbol, guardrail 3 re-engages in full and it must be an `input.symbol()` with visible `n/a` on non-resolution.

### Primary path: `request.security_lower_tf()`

Specified as the primary because platform-research.md § 2 describes it concretely and because it is the older, more broadly available of the two. It returns, per chart bar, an array of the lower-timeframe series requested — here, the intrabar closes and the intrabar volumes. Two calls (one for close, one for volume) with matching indices, or one call returning a tuple/UDT, is the build lane's mechanical choice.

### Lower-timeframe resolution

Derived from `timeframe.period`, not hard-coded, with an override input. The rule: **target 50–100 intrabars per chart bar**, which is the band where the close-binning error is small relative to `h` without exhausting the intrabar budget.

| Chart timeframe | Default LTF | Intrabars per bar (US equity RTH) |
|---|---|---|
| 1D | 5 minutes | 78 |
| 4H / 1H | 1 minute | ~60–240 |
| 30m / 15m | 1 minute | 15–30 (below target; accept, and see below) |
| < 15m | 1 minute | few — the profile is thin and must say so |

Below the target band the profile is built from too few prints per bar to be a distribution; the script should apply the same coverage labelling (below) rather than refusing outright, because a thin profile that says it is thin is legitimate and a thin profile that does not is the failure guardrail 5 names.

### Degrading visibly — the required behaviour

Let `C` = the number of bars in `W` for which intrabar data was actually returned, and `M = |W|`.

1. **Always display `C of M bars covered`**, on the chart, next to the profile. Not a tooltip. This is the single element that makes every other degradation legible, and it must be present even when `C = M`, so the trader learns to read it.
2. **Always display the volume-reconciliation ratio** `Σ_j V_j / Σ_{i in covered bars} volume[i]`. It should be ~1.00. Anything else means intrabars are being dropped, double-counted, or the LTF request is misaligned. See § What would falsify it.
3. `C = 0` → render **no profile at all** and display `n/a — no intrabar data`. Not an empty axis that looks like a flat profile: an explicit `n/a`.
4. `0 < C < M` → render the profile from the covered bars **and** label it. Do **not** renormalise, extrapolate or scale up to compensate for the missing bars.
5. **Forbidden**: falling back to distributing each chart bar's aggregate `volume` across its own `[low, high]` when intrabar data is unavailable. It produces a smooth, complete, entirely plausible profile that is not a measurement of anything, which is precisely the substitution guardrail 5 prohibits. If the build lane finds itself wanting a fallback, the correct output is `n/a`.
6. **Forbidden**: carrying the previous bar's profile forward when the current computation fails.

### The alternative: `request.footprint()`

Named as an option, **not specified**. The tradeoff, as far as this lane can establish it:

- *For*: purpose-built for intrabar volume distribution (platform-research.md § 2 says it exposes splits, delta and POC/VAH/VAL directly), so the binning would be done by TradingView rather than approximated from closes — strictly higher fidelity, and it would make range-vs-close binning moot.
- *Against*: newer, and platform-research.md's own dated caveat says its signature, parameters and limits were not verified against the Pine v6 reference. Availability may be gated by plan or by symbol, which would turn a script that works for the author into one that silently does not for a different instrument. Its own history limits are unknown.

**Recommendation**: build on `request.security_lower_tf()` first, because its failure mode is understood and the coverage diagnostic above makes it visible. If the build lane verifies `request.footprint()` against the official reference and finds it available for this trader's instruments, switching is a strict improvement — but it changes the construction enough that the header's admissions (§ Source items 2 and 3) must be rewritten, not merely kept.

## Unpinned API details

Named here because the order asks me to state where my formula depends on something platform-research.md did not pin, and because I hold no web tools to close these myself. None of them block the build; each is a check the build lane does against the official Pine v6 reference before relying on it.

1. **Does `request.security_lower_tf()` signal its own degradation?** platform-research.md says it "falls back to a cruder method on bars beyond TradingView's intrabar history limit." If the fallback returns `na`/an empty array, the coverage counter `C` detects it and guardrail 5 is satisfied mechanically. **If the fallback is silent — a populated but coarser array — then `C` will read `M` on bars that are in fact degraded, and no diagnostic in this brief catches it.** In that case the only honest mitigation is (a) keep `N` conservative so the window stays inside the limit, and (b) state the limit and the silent fallback in the header. This is the most consequential open item in the brief.
2. **The exact intrabar history limit**, in intrabars and/or in bars, and whether it varies by plan. `N = 120` and the LTF table above are sized to sit comfortably inside what I believe the limit to be, but "comfortably" is not a number I can quote. If the real limit is materially smaller, `N`'s default must come down — the parameter, not the construction, changes.
3. **Whether chart visible-range variables exist under the names I recalled** (`chart.left_visible_bar_time` / `chart.right_visible_bar_time`) and their recalculation semantics. Nothing in the specified construction depends on them — I rejected that window in § Formula on grounds that hold regardless — so this is verification of a *rejection's* premise, not of a dependency.
4. **`request.footprint()`'s signature and availability**, per platform-research.md's own caveat. Nothing specified depends on it.

## Repaint analysis

Walked against the pack's pattern table, construction by construction.

| Pattern | Applies here? |
|---|---|
| A higher-timeframe value used before that timeframe's bar closes | **No, and the direction is inverted.** This script requests a *lower* timeframe, so there is no provisional HTF value rewriting itself. The lower-timeframe bars inside a closed chart bar are themselves closed. |
| `ta.pivothigh` / `ta.pivotlow` plotted at the pivot bar | Not used. |
| A threshold computed from a window that includes the current, unclosed bar | **Yes — this is the live one.** Addressed below. |
| `ta.valuewhen` on a repainting condition | Not used. |
| An alert not guarded by `barstate.isconfirmed` | No alerts in scope. If the build adds one on a POC crossing, it must be gated — that would be a new finding, not a covered one. |
| `strategy.entry` on an intrabar condition | Not applicable; indicator, not strategy. Guardrail 4 (declared costs) does not engage. |

### The current unclosed bar

If the window includes the developing bar, its intrabar volume accumulates through the session. Because `V_max` is taken over the same window, **every** `L_j` shifts as that bar develops, not just the current bar's own bin — and `R_lo`/`R_hi` can move too, which re-lays every bin boundary. The visible consequence is that the POC can migrate and migrate back within a single session.

The pack's ruling applies directly: a dashboard showing the current provisional state is legitimate *when disclosed*; the finding is never "this repaints" but "this repaints and the header does not say so". So:

- **Default `includeCurrentBar = false`.** The window is the last `N` confirmed bars. The profile then changes only at a bar close, which is the behaviour a trader reading it as "where business has been done" expects. This also matches the pack's volume rule that a rolling window should exclude the bar it is measuring against.
- **The opt-in is allowed and must be labelled.** When `includeCurrentBar = true`, the on-chart label must read that the profile is provisional and includes an incomplete bar, and the header must say the same. This is the disclosed-live case, `MINOR` in the pack's grading, not a defect.

### Does the rolling window change history after the fact?

**The script renders exactly one profile, anchored at the right edge, describing the last `N` bars as of now.** It attributes no value to any historical bar, so there is no per-bar series that can be rewritten — nothing repaints in the strict sense.

There is a weaker effect that must still be disclosed, because a trader will otherwise read the chart wrongly: as the window rolls forward, the profile you see today is *not* the profile that existed when you took a trade three weeks ago, even though it is drawn over the same chart. Anyone scrolling back and reasoning "the POC was here when I entered" is reading a level that was computed from bars that had not happened yet. That is a property of a rolling-window profile rather than a bug, and the header should name it in one sentence. It also means bar-replay review of this indicator is misleading unless the replay itself re-anchors the window.

Bin boundaries are likewise not stable across bars: a new extreme changes `h` and re-lays every bin. Two consecutive bars' profiles are therefore not strictly comparable bin-for-bin. This is inherent to a count-based binning over a rolling range, is the price of portability across instruments (§ Formula), and should be stated in the header rather than engineered around.

## Failure modes

| Condition | Required behaviour |
|---|---|
| Fewer than `minBars` (20) confirmed bars — new listing, recent IPO, a symbol that just started trading | `n/a`. No profile, no padding, no borrowing from a related symbol. |
| Between `minBars` and `N` bars available | Compute over the `M` bars that exist, and the coverage label reads `C of M`, with `M` visibly less than `N`. Never pad the window. |
| `R_hi - R_lo <= 0` — a halted, pegged or constant series | `h` is zero or negative and binning is undefined. `n/a`. Do not collapse to a single bin: one full-length bar at one price is a plausible-looking output for a degenerate case, which is the worst outcome available. |
| `Σ V_j = 0` — a symbol that reports no volume (many indices, most spot FX) | `n/a`, with the reason stated in the label (`no volume reported for this symbol`). `V_max = 0` must never reach the division in `L_j = V_j / V_max`. |
| A symbol whose volume is a **tick count** rather than a traded quantity (common on FX and some CFDs) | The profile is still well-defined but measures something else — ticks at price, not size at price. Detectable only by the trader; disclose in the header rather than attempting to detect it. |
| Overnight gaps | Bins spanning a gap legitimately receive zero volume, and render identically to a genuine low-volume node. **These are different facts with the same appearance.** Do not impute across the gap. Disclose in the header; a build-lane option to mark empty bins distinctly (rather than as very short bars) is a rendering choice worth considering and is not specified here. |
| Holidays and half-days | Fewer intrabars and less volume. Because the profile is volume-weighted rather than bar-weighted, a half-day contributes proportionately and needs no correction — unlike a bar-count threshold, which the pack warns about. No special handling; state the reasoning so no one adds one. |
| Chart session setting (RTH vs extended hours) | Changes which intrabars exist, so the same symbol on two chart configurations yields different profiles. Not a bug; disclose. Particularly relevant to the closing-auction print, which carries a large share of a US equity's daily volume. |
| ETF creation/redemption volume | Per the pack: an ETF's volume can spike from authorised-participant activity that carries no directional information. A high-volume node on an ETF profile may be a creation event, not accepted value. Disclose in the header; not detectable from the script. |
| Intrabar data unavailable for part or all of the window | § Data requirements, items 3–6. The two forbidden fallbacks are restated there because they are the ones an eager implementer reaches for. |
| A symbol that fails to resolve | Cannot arise — no external symbol is requested (§ Data requirements). |

## What would falsify it

Three observations, in descending order of strength. The first two are runnable by the human in the TradingView editor during the compile check, which is this project's acceptance command.

1. **The volume reconciliation fails.** `Σ_j V_j` must equal `Σ volume[i]` over the covered bars, to within floating-point rounding. This is a closed invariant of the construction — every intrabar's volume goes to exactly one bin, and intrabar volumes over a chart bar sum to that bar's volume. If the displayed ratio is not ~1.00, the profile is **not** a decomposition of the traded volume it claims to decompose: intrabars are being dropped past the history limit, double-counted across a bar boundary, or the close array and volume array are misaligned by an index. Any of those invalidates the whole output, not part of it. This is why § Data requirements makes the ratio a required on-chart element rather than a debug aid.
2. **It disagrees with the native tool beyond its stated tolerance.** Set TradingView's native Fixed Range Volume Profile over the same bar range on the same symbol and compare. The script's POC bin should contain the native POC, and the top three bins by volume should be the same three, in the same order. If the POC lands two or more bins away, or the top-three ordering differs, then close-binning at the chosen LTF is not recovering the volume distribution and the construction is measuring the lower-timeframe *sampling grid* more than it is measuring volume at price. Note the direction of this test: it falsifies the approximation, it does not validate it — agreement on one symbol proves little, because the native tool is the thing this script is explicitly not reproducing (§ Source).
3. **Known auction concentration does not appear.** On a liquid US equity, a large, identifiable share of the day's volume prints in the closing auction at a single price. If the profile shows no node at the closing prints across a window of such days, volume is being dropped at a point where we know it exists — most likely because the auction print falls outside the LTF bars being sampled, or outside the chart's session setting. That is a specific, checkable reason to distrust the profile on every instrument, not just the one tested.

A fourth, which is *not* falsification and should not be mistaken for it: the profile looking different from the trader's VSA Wyckoff indicator. They measure different things (platform-research.md § 3), and D-2 ruled the comparison out of this run.

## Out of scope

Recorded so the build lane knows these were considered and excluded, not overlooked.

- **Value Area / VAH / VAL.** The shaded ~70%-of-volume band. Excluded on guardrail 2: the convention traces to Market Profile's one-standard-deviation heuristic, and I cannot cite a specific construction (which volume — total or excluding the POC bin; expanded pairwise from the POC or by sorted bins; 68%, 70% or user-set) from this lane without web access. Specifying one by inference and letting it ship under the header's authority is exactly the unauditable number the guardrail exists to prevent. It is a good candidate for a follow-up order with a sourced input, as this one had.
- **Buy/sell split, delta, order-flow classification.** D-2, and it needs `request.footprint()` or equivalent.
- **Any VSA/Wyckoff demand-supply classification.** D-2.
- **Rendering mechanics** — `box.new` vs `line.new` vs `polyline`, object-count limits and pruning, colours, the left/right anchor, how `L_j` maps to a width in bars or pixels. The brief stops at the unitless `L_j`. Build lane, per the order's non-goals.
- **Multiple profiles per chart** (per-session, developing profile, split profiles). One profile, one window.
- **Alerts.** None specified; if added later, guardrail 1 requires `barstate.isconfirmed` gating and that is a fresh quant question.
