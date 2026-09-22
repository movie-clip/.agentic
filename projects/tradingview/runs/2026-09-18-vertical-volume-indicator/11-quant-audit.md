REPORT 2026-09-18-vertical-volume-indicator/11

status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    AUDIT mode, delta re-verification; order's verification field was NONE. Anchors: (1) 02-quant.md's hand-computed worked example (3 bars x 4 intrabars, B=4, R_lo=10.00, R_hi=12.50, h=0.625) re-derived from the NEW flat-array code, reproducing V_j=(550,720,970,230), Sum=2470, POC bin 2, L_j=(0.5670,0.7423,1.0000,0.2371); (2) 07-quant-audit case B (bar 2 intrabar 2 volume na) reproducing V_j=(550,320,970,230), Sum=2070, denom 2470, ratio 0.8381 CHECK, POC bin 2, naIntrabars=1; (3) a differential oracle — an independent nested-list implementation of the OLD storage run against the NEW flat+counts storage over 4,000 randomised histories (varying lookback, binCount, includeCurrentBar, bars with 0 intrabars, na closes and na volumes): 0 mismatches on every published field; (4) 40,606 bar-level push/shift invariant assertions and 36,162 offset-cursor position checks: 0 failures. Both anchors were reproduced with startIdx=0 AND with startIdx=1, the latter with leading filler bars of 3/5/2 intrabars so a wrong offset could not coincide. See § 1-§ 4.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - CR-2's storage rewrite is arithmetically inert: every published field is bit-identical to the audited nested-array version across 4,000 randomised histories — see § 2.
  - One new finding, F8 MATERIAL, SHOULD_FIX, not blocking and NOT introduced by CR-2 — see § Findings F8.
  - F8 for backend: lines 268 and 271 are the two `for i = 0 to array.size(...) - 1` sites the file's own 228-231 comment says must be guarded, and they are not — see § 4.
  - For the main session's next compile attempt: F8 is a runtime (not compile) failure if the down-counting premise at lines 228-231 holds; watch for an out-of-bounds error on the first render — see § 4.
  - F2-F5 (04-quant-audit) and F6-F7 (07-quant-audit) were not re-opened, per the order; nothing in the changed lines touches them.

risks:
  - I could not execute Pine. Every statement is re-derivation of the code's logic plus numeric recomputation outside Pine; it is not evidence the script compiles or runs.
  - F8's severity depends on Pine's `for` direction inference when `to < from`, which the backend lane asserted from training data and nobody has compiled. I audit the file's internal inconsistency with its own stated premise, not TradingView's semantics.
  - `startIdx` is provably only ever 0 or 1 on the reachable paths (§ 3), so the offset precompute loop is exercised at a single iteration in practice; my confidence that it generalises comes from the differential oracle, not from that loop being stressed.
  - 07-quant-audit § risks' pre-existing note that `n` is taken from one array while the other is indexed by the same `k` now reads from `countsQueue` rather than `array.size(closesArr)`; the mismatch class is unchanged and still out of scope here.

## Orchestrator brief
- verdict PASS. CR-2's storage rewrite changes no published number: 4,000 randomised histories run through an independent implementation of the OLD nested-array storage and the NEW flat+counts storage agree on every field, 0 mismatches.
- Both worked examples reproduce independently, and reproduce with startIdx=1 as well as startIdx=0 — the case 10-backend.md's own hand-trace did not cover. Clean: 550/720/970/230, POC bin 2. Partial-na case B: 550/320/970/230, ratio 0.8381 CHECK.
- startIdx > 0 IS reachable, exactly when includeCurrentBar=true and the queue is full; its only reachable value is 1. The offset precompute lands correctly there — verified with leading bars of 3, 5 and 2 intrabars so a wrong cursor could not coincide.
- Shift removes exactly the oldest bar's intrabar count; flat arrays, countsQueue and barVolQueue stay in sync at every bar (40,606 assertions, 0 failures). barVolQueue's idx is still the same idx.
- 04-quant-audit § 2's 8-case window simulation re-run and reproduced identically: qSize has one entry per bar under the new storage exactly as under the old, so the window is unchanged.
- One new finding, F8 MATERIAL / SHOULD_FIX, pre-existing, not blocking: the zero-length for-loop guard is applied at 3 of 5 sites that need it; 268 and 271 are unguarded.
- Sections: 1. The two worked examples, re-derived · 2. Differential oracle (old vs new storage) · 3. offset, startIdx and shift-sync · 4. The for-loop direction gotcha, site by site · Findings (F8) · What would have made this FAIL.

## 1. The two worked examples, re-derived

I did not check 10-backend.md's hand-trace. I transcribed the **new** code —
`volume_profile.pine:221-244` (push/shift) and `275-334` (qSize, window indices,
offset cursor, binning, na-skip) plus `339-350` (POC, sumVj) and `387-394`
(avgIntrabars, ratio) — into an independent Python implementation and ran the
anchor through it.

**Clean case** (02-quant.md's anchor: 3 bars x 4 intrabars, `B = 4`,
`R_lo = 10.00`, `R_hi = 12.50`, `h = 0.625`):

| bin j | V_j | L_j |
|---|---|---|
| 0 | 550 | 0.5670 |
| 1 | 720 | 0.7423 |
| 2 | 970 | 1.0000 POC |
| 3 | 230 | 0.2371 |

`Sum V_j = 2470`, `vMax = 970` at `j = 2`, `c = 3`, `naIntrabars = 0`,
`ratio = 1.0000`. Digit for digit 04-quant-audit.md § 1 and 07-quant-audit.md
case A.

**Partial-na case B** (bar 2's second intrabar volume `na`, close stays 11.1):
`V_j = (550, 320, 970, 230)`, `Sum V_j = 2070`, POC still bin 2,
`naIntrabars = 1`, `sumBarVolumeCovered = 2470` (750 + 850 + 870, bar 2's full
native volume retained), `ratio = 2070/2470 = 0.838056` → `#.####` renders
`0.8381`, `math.abs(ratio - 1.0) = 0.1619 > 0.02` → `— CHECK`, red cell. Status
`OK — 1 na intrabar(s) skipped`. Matches 07-quant-audit.md case B exactly. The
close-is-na twin (case C) gives the identical result.

**The part 10-backend.md did not trace.** I re-ran both examples with the three
worked-example bars preceded by filler bars of **3, 5 and 2** intrabars, at
`lookbackBars = 3` with `includeCurrentBar = true`, which forces `startIdx = 1`
and an `offset` precompute of a non-trivial, non-round value. The filler bars
carry closes at 10.1, 12.4 and 11.0 — bins 0, 3 and 1 — so any off-by-one in the
cursor would have leaked filler volume into a bin and moved a V_j. It did not:
`V_j = (550, 720, 970, 230)` and `(550, 320, 970, 230)` respectively, unchanged,
and the reconciliation denominator stayed 2470 rather than picking up a filler
bar's volume.

So my independent trace **agrees** with 10-backend.md's, and extends it to the
case that report's own § risks left open.

## 2. Differential oracle (old vs new storage)

Reproducing the anchor proves the new code right on one history. The change
being audited is a *representation* change, so the stronger test is
equivalence over many histories.

I implemented the **old** storage semantics (per-bar nested lists,
push/shift-when-over-length, `array.get(closesQueue, idx)` reads — the exact
shape 04-quant-audit.md and 07-quant-audit.md passed) and the **new** storage
semantics (`closesFlat`/`volsFlat`/`countsQueue` with the `offset` cursor,
transcribed from lines 221-244 and 304-334) as two separate functions, and ran
both over 4,000 randomised histories:

- `lookbackBars` 4-12, `binCount` 4-8, `includeCurrentBar` both values
- 1-30 bars, each with 0, 1, 2, 3, 5 or 8 intrabars — **zero-intrabar bars
  included**, so the `n == 0` path and the `oldCount == 0` shift path are both
  exercised inside and at the front of the window
- na volumes and na closes injected at random

Compared on every field that reaches the chart: `V_j`, `Sum V_j`, `vMax`,
`pocIdx`, `c`, `totalIntrabars`, `sumBarVolumeCovered`, `naIntrabars`, `ratio`,
`m`, `startIdx`, `endIdx`, and the `reason` string.

**4,000 trials, 0 mismatches.** The rewrite is arithmetically inert.

## 3. offset, startIdx and shift-sync

**Is `startIdx > 0` reachable?** Yes, and only at the value 1. With
`includeCurrentBar = false`, `endIdx = qSize - 2` and `m = min(lookbackBars,
qSize - 1)`, so `startIdx = qSize - 1 - m`, which is 0 both while history is
short (`m = qSize - 1`) and in steady state (`qSize = lookbackBars + 1`,
`m = lookbackBars`). With `includeCurrentBar = true` and the queue full,
`m = lookbackBars`, `endIdx = qSize - 1 = lookbackBars`, so `startIdx = 1` —
the flat arrays then hold one bar's intrabars ahead of the window's true start.
Enumerated over `lookbackBars` in {4, 5, 20, 120} x both toggle values x every
bar count up to `lookbackBars + 7` under the real `minBars >= 4` path, the set
of reachable `(startIdx)` values is exactly {0, 1}, and `endIdx - startIdx + 1
== m` in every one.

`startIdx` is never negative on a reachable path: `reason == ""` requires
`m >= minBars >= 4`, and `m <= usableSize` by construction, so
`startIdx = endIdx - m + 1 >= 0`. It follows that `for idx = startIdx to endIdx`
(line 315) always has `endIdx - startIdx = m - 1 >= 3 > 0` and can never
reverse — that site needs no guard and has none, correctly.

**Does the cursor land on the right slice?** The invariant the code needs is
"at entry to iteration `idx`, `offset == sum(countsQueue[0 .. idx-1])`". Checked
directly over 3,000 randomised count vectors containing zeros, both starting
values of `startIdx`, walking every position: **36,162 positions checked, 0
wrong**. `offset += n` sits at line 334 *outside* the `if n > 0` guard and
inside the `for idx` loop, which is what makes a zero-intrabar bar advance the
cursor by 0 rather than being skipped — the one place this could have gone
wrong, and it is right.

**Does the shift stay in sync?** I asserted, after **every bar** of 2,000
randomised histories (40,606 assertions, 0 failures):
`countsQueue == [len(b) for b in nested]`, `len(closesFlat) == sum(countsQueue)`,
`closesFlat == concat(nested)`, `volsFlat == concat(nested_vols)`, and
`len(barVolQueue) == len(countsQueue)` with equal contents. The shift removes
`oldCount` elements — the exact count popped from `countsQueue` at line 238, read
*before* the pops — so no off-by-one is possible; the count is not recomputed
from anything that the pops mutate.

**`barVolQueue` alignment.** `array.push(barVolQueue, volume)` (236) and
`array.shift(barVolQueue)` (244) sit in the same unconditional push site and the
same over-length `if` as `countsQueue`'s, and both queues take exactly one entry
per bar. So `len(barVolQueue) == len(countsQueue) == qSize` at all times and
`array.get(barVolQueue, idx)` at line 320 indexes the same bar as
`array.get(countsQueue, idx)` at 316. Swapping the governing size check from the
removed `closesQueue` to `countsQueue` (line 237) changed nothing: `closesQueue`
also held exactly one entry per bar. Confirmed by the bar-level assertions above
and by case B's denominator staying 2470 with fillers present.

**Window unchanged.** Because `qSize` is still one entry per bar capped at
`lookbackBars + 1`, 04-quant-audit.md § 2's 8-case simulation re-runs
identically under the new storage — I re-computed it rather than citing it:

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

A storage change could only have moved the window through `qSize`, and `qSize`
is unmoved. Repaint posture is therefore unchanged: with the default
`includeCurrentBar = false`, `endIdx = qSize - 2` still never reaches the
developing bar and `srcLow = low[1]` still never sees it. Guardrail 1 holds as
04-quant-audit.md § 2 established.

The only residual mention of the removed identifiers in the file is the
explanatory comment at line 217; no live code reads `closesQueue`/`volsQueue`.

## 4. The for-loop direction gotcha, site by site

The order asks me to confirm 10-backend.md § risks' self-caught gotcha —
Pine's `for i = start to end` with `end < start` and no explicit `step` counts
DOWN, so an unguarded loop over a zero-length collection runs twice
(`i = 0`, then `i = -1`) instead of zero times. The file states that premise in
its own comment at lines 228-231. I audit the file against its own premise; I
cannot compile Pine and do not adjudicate TradingView's actual semantics.

All ten `for` sites, and whether the upper bound can fall below the lower:

| line | loop | can reverse? | guarded? |
|---|---|---|---|
| 232 | `for k = 0 to nIntrabars - 1` | yes, `nIntrabars = 0` | yes — `if nIntrabars > 0` (227) |
| 241 | `for k = 0 to oldCount - 1` | yes, `oldCount = 0` | yes — `if oldCount > 0` (239) |
| 268 | `for i = 0 to array.size(profileBoxes) - 1` | **yes, size 0 on the first render** | **NO** |
| 271 | `for i = 0 to array.size(profileLabels) - 1` | **yes, size 0 on the first render** | **NO** |
| 313 | `for i = 0 to startIdx - 1` | yes, `startIdx = 0` | yes — `if startIdx > 0` (311) |
| 315 | `for idx = startIdx to endIdx` | no — `endIdx - startIdx = m - 1 >= 3` (§ 3) | n/a |
| 321 | `for k = 0 to n - 1` | yes, `n = 0` | yes — `if n > 0` (317) |
| 339, 348, 356 | `for j = 0 to binCount - 1` | no — `binCount` minval 4 (187) | n/a |

So the claim in 10-backend.md § risks — "I guarded all three sites" — is true of
the three sites CR-2's scope fence let it touch, and I confirm those three are
correctly guarded. It is **not** true that every site that can have a
zero-length bound is guarded: lines 268 and 271 are not, and they are the
clearing loops that run on **every** execution of the `barstate.islast` block,
with the arrays empty on the first one. That is F8. It is pre-existing — it is
04-quant-audit.md's lines 219-224 unchanged — and CR-2 neither caused it nor
was scoped to fix it, so it does not bear on this delta's verdict.

## Findings

One, new, SHOULD_FIX. It does not block: it is pre-existing, outside CR-2's
scope fence, and it fails loudly rather than publishing a wrong number.
F1-F5 (04-quant-audit.md) and F6-F7 (07-quant-audit.md) are not re-opened.

```
FINDING 8
severity:   MATERIAL
where:      volume_profile.pine:268 and 271 (and the premise at 228-231)
claim:      lines 228-231 state, as this file's own premise, that a bare
            "for k = 0 to n - 1" with n == 0 counts DOWN and runs twice rather
            than zero times, and the fix guards all three of its own loops on
            that basis (227, 239, 311).
actual:     the premise is applied at 3 of the 5 sites where the bound can go
            negative. Lines 268 and 271 iterate "0 to array.size(profileBoxes)
            - 1" and "0 to array.size(profileLabels) - 1" with no size guard.
            Both arrays are `var` and empty on the first execution of the
            barstate.islast block, so the bound is -1 and, under the file's own
            premise, the body runs with i = 0 against a size-0 array:
            array.get(profileBoxes, 0) is out of bounds. Not introduced by CR-2
            — identical to 04-quant-audit.md's lines 219-224.
impact:     under the stated premise the indicator raises a runtime error on
            its first render and draws nothing, on every chart. No wrong number
            is published — the failure is loud — but the profile never appears,
            and the failure is invisible to pine_check.py and was masked from
            the live compile check by CE10022 aborting at line 210 before any
            bar executed. If the premise is false, then the three guards at
            227/239/311 are merely redundant and nothing here breaks; the file
            cannot be right both ways.
expected:   wrap both clearing loops in "if array.size(...) > 0", matching the
            three guards the same change already added, so the file applies its
            stated premise uniformly. Then confirm the premise itself at the
            next TradingView compile attempt and record which way it went.
```

## What would have made this FAIL

Stated so the PASS is falsifiable. Each was checked numerically and each is
absent:

1. `offset` precomputed from the wrong prefix — e.g. `for i = 0 to startIdx`
   (inclusive) or summing through `endIdx` — which would have shifted every
   window bar's slice by one bar's intrabar count. Checked at 36,162 cursor
   positions; the invariant `offset == sum(counts[0..idx-1])` never broke.
2. `offset += n` placed *inside* the `if n > 0` block, which would have
   desynchronised the cursor permanently the first time a window bar returned
   zero intrabars. It is at line 334, outside the guard; the fuzz explicitly
   included zero-intrabar bars and found no divergence.
3. The over-length shift removing a fixed number of elements, or recomputing
   `oldCount` after the pops, instead of the shifted bar's own count. Verified
   by 40,606 bar-level invariant assertions against a nested-list oracle.
4. `barVolQueue` shifted on a different condition from `countsQueue`, which
   would have misaligned the reconciliation denominator by one bar while
   leaving every V_j correct — the hardest version of this bug to see. Both
   sit in the same `if`; case B's denominator is 2470 with and without leading
   filler bars.
5. The anchor reproducing only at `startIdx = 0`. It reproduces at
   `startIdx = 1` with leading bars of 3, 5 and 2 intrabars binning to bins 0,
   3 and 1 — a wrong cursor would have leaked their volume into the profile.
6. Any change to the binning expression, the clamp, the strict-`>` ascending
   POC tie-break, or the na-skip. All are untouched, and the differential
   oracle would have caught any change in their output.
7. The window moving. `qSize` is still one entry per bar; 04-quant-audit.md
   § 2's 8 cases re-computed identically.
