REPORT 2026-09-18-vertical-volume-indicator/04
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    AUDIT mode; order's verification field was NONE. Anchor used = 02-quant.md's hand-computed worked example (3 bars x 4 intrabars, B=4, R_lo=10.00, R_hi=12.50, h=0.625). The code's literal binning/POC/normalisation logic, transcribed from volume_profile.pine:249-291 into an independent Python implementation, reproduces V_j = (550, 720, 970, 230), Sum V_j = 2470, POC = bin 2, L_j = (0.5670, 0.7423, 1.0000, 0.2371) exactly. Window/queue index arithmetic re-simulated separately over 8 bar_index/includeCurrentBar cases: binning window and range window are the identical bar set in all 8. See section 1 and section 2.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - 5 findings, all SHOULD_FIX, none blocking. Severest is F1 (MATERIAL) — see § Findings
  - F1 for backend: an `na` element inside a returned intrabar array poisons its bin and can publish a wrong POC under Status "OK" — see § Findings F1
  - F2 for backend: the `C = 0` -> "n/a — no intrabar data" branch has no `na()` guard on the arrays themselves — see § Findings F2
  - F3/F4/F5 for backend: diagnostics-row defects only, no effect on V_j, L_j or POC — see § Findings
  - for integration: `pine_check.py volume_profile.pine` (non-strict) exits 0; the sole --strict P008 at line 182 is the documented deviation 03-backend.md already raised, not a quant finding
  - for docs: the header's claims at lines 38-46, 59-96 and 98-104 were each checked against the code and each is true as written — see § Header claims checked

risks:
  - I could not execute Pine. Every statement here is re-derivation of the code's logic, plus numeric re-computation of that logic outside Pine. It is not evidence the script compiles or runs, and I make no such claim.
  - The audit rests on Pine rolling back `var` array state on realtime ticks. If it does not, the queue accumulates duplicate entries for the developing bar. That failure is self-detecting: the Reconciliation row would read well above 1.00 and flag CHECK. Worth confirming at the compile check.
  - `request.security_lower_tf()`'s behaviour on a bar with no intrabar data — empty array vs `na` array — is unverified by me and by the implementer (03-backend.md § risks). F2 depends on it. It is a chart-error-vs-`n/a` question, not a wrong-number question.
  - The close-binning-vs-range-spreading choice is definitional, not arithmetic (02-quant § Formula says so). The code implements close-binning and the header names it. I audited it as a match to the spec, not as the correct choice.

## Orchestrator brief
- verdict PASS. The formula is implemented correctly: the worked-example anchor reproduces to the digit, and the window arithmetic has no off-by-one.
- anchor: 02-quant § Formula's worked example (550/720/970/230, sum 2470, POC bin 2). Re-derived twice — once from the spec prose, once from the code's literal logic. Both agree with each other and with the brief.
- top bin closed at R_hi: confirmed, a print at 12.50 lands in bin 3 via the clamp, not a 5th bin.
- POC tie-break: explicit (`if vv > vMax`, strict, ascending j). Not left to `array.indexof`.
- V_max = 0 provably never reaches the L_j division; all four `n/a` branches are real, distinct and correctly ordered.
- both FORBIDDEN implementations are absent from the file — verified by pattern search, not by reading comments.
- guardrail 1: the default genuinely excludes the developing bar, in both the binning window and the range window. Verified by simulation, not by prose.
- the coverage/reconciliation table is computed from the real arrays, not cosmetic.
- 5 findings, all SHOULD_FIX: F1 MATERIAL (`na` intrabar poisons a bin, POC can be wrong under Status "OK"), F2-F5 MINOR. None blocks dispatch.
- sections below: 1. Anchor re-derivation (the worked example, re-derived twice) · 2. Window and repaint (the 8-case index simulation) · 3. Failure-mode table walk (every 02-quant row) · 4. Forbidden implementations (both absent) · 5. Diagnostics (coverage/reconciliation, not cosmetic) · 6. Units and signs · Findings (F1-F5) · Header claims checked · What would have made this FAIL.

## 1. Anchor re-derivation

02-quant.md § Formula states, for 3 bars of 4 intrabars each, `B = 4`,
`R_lo = 10.00`, `R_hi = 12.50`, `h = 0.625`:

| bin j | span | `V_j` | `L_j` |
|---|---|---|---|
| 0 | [10.000, 10.625) | 550 | 0.5670 |
| 1 | [10.625, 11.250) | 720 | 0.7423 |
| 2 | [11.250, 11.875) | 970 | 1.0000 POC |
| 3 | [11.875, 12.500] | 230 | 0.2371 |

I wrote two independent implementations in Python. The first from the brief's
prose alone (`bin(p) = clamp(floor((p - R_lo)/h), 0, B-1)`, `V_j` summed,
`L_j = V_j/V_max`, POC = lowest `j` attaining the max). The second transcribed
line-for-line from the code:

```
volume_profile.pine:252   h := (rHi - rLo) / binCount
volume_profile.pine:265   binIdx = math.max(0, math.min(binCount - 1, math.floor((p - rLo) / h)))
volume_profile.pine:266   array.set(vj, binIdx, array.get(vj, binIdx) + v)
volume_profile.pine:271-275   for j = 0 to binCount - 1 / if vv > vMax / vMax := vv / pocIdx := j
volume_profile.pine:291   lj = array.get(vj, j) / vMax
```

Both produce `V_j = (550, 720, 970, 230)`, `sum = 2470`, `POC = 2`,
`L_j = (0.5670, 0.7423, 1.0000, 0.2371)`. Exact agreement with the brief on
every bin, the sum and the POC index.

**Bin construction.** Bin *count* over `[R_lo, R_hi]`, not bin width
(`volume_profile.pine:252`). Top bin closed at `R_hi`: a print at exactly 12.50
gives `floor(2.5/0.625) = 4`, which `math.min(binCount - 1, 4)` clamps to 3 —
bin `B-1`, no overflow and no `B`-th bin. Confirmed numerically.

**Close-binning, not range-spreading.** `volume_profile.pine:262-266` iterates
the intrabar arrays and adds `v` — the intrabar's entire volume — to exactly one
`binIdx`, keyed on `p`, the intrabar close from the `[close, volume]` tuple
requested at line 182. There is no loop over an intrabar's range and no
proportional distribution anywhere in the file.

**Normalisation.** `L_j = V_j / vMax` at line 291. `vMax` is established at
lines 271-275 and the branch at lines 276-277 sets `reason` when `vMax <= 0`;
the render block at line 284 runs only on `reason == ""`. So the division at 291
is unreachable with `vMax = 0`. This is a structural guarantee, not a comment.

**POC tie-break.** Lines 271-275 iterate `j` ascending with a **strict** `>`
comparison from `vMax = 0.0`. A tie therefore keeps the first — lowest — `j`.
Checked on `V = (10, 10, 5, 0)`: returns 0, the lower price bin. Explicit in
code as 02-quant requires, not delegated to `array.indexof`.

## 2. Window and repaint

The window is defined twice in the script, and the risk is that the two
definitions disagree: the price range comes from `ta.lowest`/`ta.highest` on a
shifted source (lines 198-205), while the binning comes from queue indices
(lines 226-228, 245-246). A mismatch would produce bins whose extremes are set
by bars whose volume is not in the profile.

I simulated both index computations over 8 cases:

| bar_index | N | includeCurrentBar | m | rangeLen | binned bars | ranged bars | identical |
|---|---|---|---|---|---|---|---|
| 500 | 120 | false | 120 | 120 | 380..499 | 380..499 | yes |
| 500 | 120 | true | 120 | 120 | 381..500 | 381..500 | yes |
| 30 | 120 | false | 30 | 30 | 0..29 | 0..29 | yes |
| 30 | 120 | true | 31 | 31 | 0..30 | 0..30 | yes |
| 120 | 120 | false | 120 | 120 | 0..119 | 0..119 | yes |
| 121 | 120 | false | 120 | 120 | 1..120 | 1..120 | yes |
| 20 | 120 | false | 20 | 20 | 0..19 | 0..19 | yes |
| 0 | 120 | false | 0 | 0 | (empty) | (empty) | yes |

The two windows are the **same bar set** in every case. No off-by-one, and the
queue cap at `lookbackBars + 1` (line 192) is the correct size to keep one spare
slot for the developing bar.

**The developing bar is genuinely excluded by default.** At `bar_index = 500`
with `includeCurrentBar = false`, both the binned set and the ranged set end at
bar 499. Bar 500 is pushed to the queue (line 189-191) but `endIdx = qSize - 2`
(line 245) never reaches it, and `srcLow = low[1]` (line 198) never sees it. So
on the realtime bar the `barstate.islast` block recomputes every tick from an
unchanging input and produces an unchanging profile. Guardrail 1 is met in the
default state by construction, not by disclosure.

`includeCurrentBar = true` is the disclosed-live case 02-quant § Repaint
analysis permits. The toggle does change the on-chart label: a red `PROVISIONAL
— includes unclosed bar` label at lines 312-316, placed **outside** the
`reason == ""` guard so it appears even when the profile is `n/a`, and the
Status row reads `OK — PROVISIONAL` (line 327). Both requirements met.

Walking the pack's repaint table against the code rather than 02-quant's prose:
no higher-timeframe request (line 182 is strictly lower-timeframe), no
`ta.pivothigh`/`ta.pivotlow`, no `ta.valuewhen`, no alerts, no `strategy.*` —
`indicator()` at line 149. The one live row, "a window that includes the
current unclosed bar", is the default-off toggle above.

## 3. Failure-mode table walk

Every row of 02-quant § Failure modes, checked against the code's actual
branches and their ordering, not their comments.

| 02-quant requirement | Code | Behaviour I derived |
|---|---|---|
| `< minBars` -> `n/a`, no padding | 231-232 | `reason := "n/a — fewer than minimum bars required (m/minBars)"`. Set before any binning. No pad, no borrow. Correct. |
| `minBars..N` available -> compute over `M`, label it | 228, 323 | `m = min(lookbackBars, usableSize)`; Window row reads `M of N` with `M < N` visible. Never padded. Correct. |
| `R_hi - R_lo <= 0` -> `n/a`, never one collapsed bar | 249-250 | `reason := "n/a — degenerate range (window high <= low)"` **before** `h` is ever assigned. No single-bin collapse exists anywhere. Correct. |
| `C = 0` -> `n/a — no intrabar data`, no rendered profile | 268-269 | Exact string. `reason != ""` so line 284's render block is skipped, and lines 219-224 already cleared the previous boxes. Correct — see F2 for the one dependency. |
| `sum V_j = 0` -> `n/a` with the stated reason, `V_max = 0` never divides | 276-277 | `if vMax <= 0` -> `"n/a — no volume reported for this symbol"`. 02-quant's wording, reproduced. Division at 291 unreachable. Correct. |

The four `n/a` branches produce four **distinct** strings, as
03-backend.md's handoff to the test lane asks. Branch ordering is right: minBars
before range, range before coverage, coverage before zero-volume. Each later
test would be meaningless if an earlier one had not already fired.

One case worth recording because it degrades correctly by an accident of
arithmetic rather than by design: a symbol reporting no volume at all gives
`na` for every intrabar volume, so every touched bin becomes `na` and every
untouched bin stays `0.0`. `na > 0.0` is false and `0.0 > 0.0` is false, so
`vMax` stays 0 and the zero-volume branch fires as intended. The **partial**
version of this case does not degrade correctly — that is F1.

`rLo`/`rHi` cannot be `na` when the range test at line 249 runs: `rangeLen` and
`m` are the same quantity (section 2), so `m >= minBars >= 4` implies
`rangeLen >= 4 > 0`, and line 204-205's `na` guard cannot have fired. The
degenerate-range test is therefore always evaluated on real numbers.

## 4. Forbidden implementations

02-quant § Data requirements points 5 and 6. I searched for the computation
rather than for a name — patterns for range arithmetic (`high - low`, `low +`,
`(high`), for value substitution (`nz(`, `fixnan`), and for carry-forward (`var`
declarations reassigned from a prior bar, `[1]` on the right of a `:=`).

**No matches in the file.**

- *Spreading a chart bar's aggregate volume across `[low, high]`*: absent. The
  only use of `volume` is line 191, pushing the bar's native volume to
  `barVolQueue`, which feeds the reconciliation **denominator** (line 261) and
  nothing else. It never enters `vj`.
- *Carrying the previous profile forward on failure*: absent, and structurally
  prevented. `reason`, `vj`, `c`, `vMax`, `pocIdx`, `sumVj` are all declared
  fresh inside the `barstate.islast` block (lines 230-243) — none is `var`. The
  box and label arrays are cleared unconditionally at lines 219-224, **before**
  any `reason` can be set, so a failing recompute leaves an empty chart plus an
  `n/a` Status, never a stale shape.

The absence of `nz()` anywhere is worth stating positively: there is no point in
this script where a missing input is replaced by a plausible value.

## 5. Diagnostics

It is. Each displayed quantity traces to the actual arrays:

- `c` (line 259) increments only inside `if n > 0`, where `n =
  array.size(closesArr)` — the real returned array, per window bar.
- `totalIntrabars` (line 260) accumulates those same sizes.
- `sumBarVolumeCovered` (line 261) accumulates `barVolQueue` **inside the same
  `n > 0` guard**, so the denominator is exactly "the covered bars' volume",
  which is what 02-quant § Data requirements point 2 specifies. A denominator
  over all `M` bars would have been a finding; it is not what the code does.
- `sumVj` (lines 279-282) is summed from `vj` itself after binning.
- `ratio = sumVj / sumBarVolumeCovered` (line 321), guarded against a zero
  denominator, flagged `— CHECK` beyond 2% from 1.00 with a red cell (lines
  326, 348).
- `avgIntrabars = totalIntrabars / c` (line 319), flagged `DEGRADED (target
  50-100)` below 50 (lines 320, 325, 341).

The table is written at lines 329-358, outside the `reason == ""` guard, so the
diagnostics render even when the profile does not — which is what makes the
`n/a` legible rather than a blank chart. Position `bottom_right`, a real
`table`, not a tooltip. 02-quant contract_note #2 is satisfied.

The `DEGRADED` flag fires only *below* 50, not above 100. That matches this
order's wording ("flagged DEGRADED below it") and 02-quant's, which treats the
upper bound as a budget concern rather than a data-quality one. Not a finding.

## 6. Units and signs

- `L_j` is unitless in `[0, 1]` and is used only as a multiplier on a bar-count
  width (line 292). No percent/fraction mixing.
- The reconciliation ratio is a fraction near 1.00, labelled `Σ bins / Σ volume`
  and formatted `#.####` — not a percent. Consistent.
- POC price is formatted with `format.mintick` (line 213), raw volume with
  `#,###`. Correct kinds for each.
- No rate, return, volatility or annualisation appears anywhere, so the 252-day
  convention does not engage.
- No signed quantity is published, so the repo's positive-is-bullish convention
  does not engage either.
- Every `input.int` names its unit in bars or bins in its tooltip (lines 154,
  157, 163), as the pack's Units section requires, and `ltfResolution` derives
  from `timeframe.period` via `timeframe.in_seconds()` at line 169 rather than
  being hard-coded.

## Findings

All five are SHOULD_FIX. None is CRITICAL, and none blocks the run.

```
FINDING 1
severity:   MATERIAL
where:      volume_profile.pine:262-275
claim:      every intrabar's volume lands in exactly one bin, and POC = argmax_j V_j.
actual:     there is no na-guard on the array elements. If any returned intrabar
            volume is na, `array.get(vj, binIdx) + v` makes that bin na for the
            rest of the run. The POC loop's `if vv > vMax` is false for na, so a
            poisoned bin can never win — POC is silently awarded to the largest
            *unpoisoned* bin. `sumVj` becomes na, so Reconciliation reads "n/a",
            but `reason` is still "" and the Status row reads "OK". If instead an
            intrabar *close* is na, binIdx is na and array.set raises a runtime
            error rather than rendering n/a.
impact:     the trader places a stop against a POC line that is not the busiest
            price in the window, on a chart whose Status row says OK. The
            all-na case degrades correctly (§ 3); only the partial case fails.
expected:   skip an intrabar whose close or volume is na and count it, or set
            reason when any na is encountered. Either way Status must not read OK.
```

```
FINDING 2
severity:   MINOR
where:      volume_profile.pine:182-195, 258
claim:      line 166's tooltip says a non-lower timeframe "returns no intrabar
            data for every bar, which reads as n/a here rather than a fabricated
            value (guardrail 5)"; line 268 implements C = 0 -> "n/a — no intrabar data".
actual:     `array.size(closesArr)` at line 258 is reached with no `na(ltfCloses)`
            guard at push time (189-190). The n/a branch is reachable only if
            request.security_lower_tf() returns an *empty* array in that case.
            If it returns an na array id, array.size raises instead. 03-backend.md
            § risks lists this construct as one it could not verify.
impact:     the headline guardrail-5 branch may be a chart error rather than the
            specified n/a. Not a wrong number — a wrong failure mode.
expected:   guard the push or the read with na(), so C = 0 is reached either way.
            Confirm the API's empty-vs-na behaviour at the compile check.
```

```
FINDING 3
severity:   MINOR
where:      volume_profile.pine:319
claim:      "Intrabars/bar (avg)" shows the realised average against the 50-100 target.
actual:     `totalIntrabars / c` divides two `int`s, which truncates in Pine.
            Recomputed: 3899 intrabars over 78 bars displays 49 where the true
            value is 49.9872; 3899 over 79 displays 49 against 49.3544 — the same
            figure for materially different coverage, and the first crosses the
            DEGRADED threshold on rounding alone.
impact:     a window at effectively 50 intrabars/bar is flagged DEGRADED, and two
            different coverage levels are indistinguishable in the row.
expected:   force float division, e.g. totalIntrabars / math.max(c, 1) * 1.0, or
            declare totalIntrabars as float.
```

```
FINDING 4
severity:   MINOR
where:      volume_profile.pine:324, 234
claim:      the "Coverage (C of M)" row reports intrabar coverage of the window.
actual:     `c` is initialised 0 and only incremented inside the binning loop at
            259. In the below-minBars branch (231) and the degenerate-range
            branch (249) that loop never runs, so the row reads "0 of M" —
            visually identical to genuine total intrabar loss, when in fact
            coverage was never measured.
impact:     a reader diagnosing a blank chart is pointed at intrabar data when
            the real cause is window length or a pegged series. The Status row
            does disambiguate, so this is a legibility defect, not a wrong number.
expected:   render the row as "not measured" when the failure preceded binning.
```

```
FINDING 5
severity:   MINOR
where:      volume_profile.pine:301-307, 350-351
claim:      the label reads "POC <price>" and the table has a "POC price" row.
actual:     both publish `pocMid`, the midpoint of a bin of height
            h = (R_hi - R_lo)/binCount, formatted to mintick — a point price to
            full instrument precision for a level that is only resolved to one
            bin. On a $400 ETF over a 120-bar range of $60 at B = 24, h = $2.50.
            Neither h nor the POC bin's bounds appear anywhere on the chart.
impact:     the POC is read as a price rather than as a band, and a stop is
            placed with a precision the construction does not support.
expected:   show the POC bin's [lo, hi) bounds, or add a "Bin height (h)" row to
            the table so the resolution is visible next to the price.
```

## Header claims checked

02-quant § Source and the project's header contract make the header's admissions
part of what I audit. I checked each claim against the code rather than
accepting it:

- "ORIGINAL construction, no external authority" (lines 23-29) — present, with
  the Steidlmayer/TPO reasoning 02-quant gave. Guardrail 2 met.
- "built from lower-timeframe candle closes, never tick data" (30-32) — true;
  line 182 requests `[close, volume]` at `ltfActual`.
- "NOT TradingView's native Volume Profile" (33-36) — present.
- "close-binning, not range-spreading" (38-46) — true, verified in § 1 and § 4.
- "FORBIDDEN, and NOT implemented anywhere in this script" (90-96) — I verified
  both claims independently in § 4 rather than taking the comment's word.
- rolling-window / bin-instability caveat (48-57) — present and accurate; bin
  boundaries do move with `rLo`/`rHi` (line 252).
- gaps, half-days, session setting, ETF creation/redemption, tick-count volume
  (106-119) — all five disclosures 02-quant § Failure modes asks for are present.

No admission from 02-quant is missing, and none is weakened.

## What would have made this FAIL

Stated so the PASS is falsifiable, per the pack. Any one of these would have
been CRITICAL and blocking. Each was checked and each is absent:

1. `floor` without the upper clamp, so a print at `R_hi` created a `B`-th bin or
   overflowed — checked numerically, clamped at line 265.
2. POC left to `array.indexof(vj, vMax)` or a `>=` comparison, either of which
   resolves ties to the *higher* `j` — line 273 is a strict `>`, ascending.
3. The range window and the binning window covering different bar sets — 8 cases
   simulated, identical in all 8.
4. `vMax = 0` reaching line 291 — structurally unreachable via lines 276-284.
5. Range-spreading present as a fallback, or the previous profile carried
   forward — neither exists in the file.
6. `includeCurrentBar = false` still admitting the developing bar into `rLo`,
   `rHi` or `vj` — it does not; bar 500 is excluded from both at bar_index 500.
7. Any of the four `n/a` conditions producing a plausible-looking profile
   instead of a label — all four set `reason` and skip the render block.
