REPORT 2026-09-15-fix-systemic-stress-dashboard/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only research order, no verification command named. Specification was checked by independent Python re-implementation of the proposed rules over 6 dispersion scenarios and 3 basis scenarios; it reproduced the prior audit's 71.03 and -24.0 and -14.0 figures before fixing them (see § Method and independent check).

contract_notes:
  - No input signature change. The dispersion floor is two script-level constants, NOT input.float() — rationale in § FINDING 1 fix, item 6.
  - New table row "Basis" proposed for FINDING 3's level jump, taking the table from 6 rows to 7; table.new(..., 2, 6, ...) at :113-115 must become 2, 7 or the row silently does not render; see § FINDING 3.

pack_corrections:
  - none

handoff:
  - FINDING 1 fix: replace :63-70 with hoisted dispersion-guarded percentrank; exact Pine given, variable names included, applies to vixClose, corClose, creditRawStress; see § FINDING 1 fix
  - Floor formula is disp <= ABS_FLOOR + REL_FLOOR * scale over the L+1 bar set src[0..L], with ABS_FLOOR=1e-10, REL_FLOOR=1e-9; see § FINDING 1 fix
  - The two constants are derived, not tuned: the result is invariant across an 11-decade band between IEEE noise (5.6e-14) and the smallest quotable move (1e-2); see § Is the floor a tuned constant
  - Header must still disclose the floor as a numerical guard with its derivation — this is a docs-lane item, wording supplied; see § Header disclosure required
  - FINDING 2/3 fix: option (a) chosen — carry an integer basisCode bitmask and na the impulse when basisCode[t] != basisCode[t-impulseLen]; exact Pine given; see § FINDING 2 and 3 fix
  - basisCode must be a 1/2/4 bitmask, NOT sumWeights: at default weights {VIX} and {COR1M} both give sumWeights 1.0 but composites 30 and 90, so a sumWeights key passes a 60-point spurious impulse; see § Why sumWeights is not a valid basis key
  - Basis membership counts a component only when non-na AND its weight != 0, so a zero-weighted component dropping out correctly does not suppress the impulse; verified, see § FINDING 2 and 3 fix
  - FINDING 3's bar-272 case resolves to na at bars 272-276 and 0.0 from bar 277; walked bar by bar with the numbers; see § FINDING 3 walk-through
  - Option (b), component-level differencing, is specified and REJECTED — it publishes 0.0 at bar 272 while the plotted composite visibly drops 14 points; see § Option (b) and why it is rejected
  - Must not change: creditRawStress sign, regime band boundaries, renormalisation scale preservation, percentrank construction, impulse sign; checked against this spec item by item; see § What this spec must not disturb
  - The FINDING 3 composite level jump (80 -> 66) is NOT fixed by the impulse rule; a producer/owner decision is needed between displaying the basis and withholding the composite; see § FINDING 3

risks:
  - Whether ta.percentrank returns na during its first `percentileLookback` bars or computes on partial history is still unsettled (the prior audit's risk 3). My spec does not depend on it: the dispersion guard uses ta.highest/ta.lowest over L+1 bars, which are documented to be na until the window fills, so the guard yields na over the warm-up under either behaviour.
  - I specify the guard as hoisted top-level assignments rather than ta.* calls inside a ternary. This incidentally removes the prior audit's risk 4 (possible non-hoisting of ta.* inside a ternary) for these lines. That is a side effect of the fix, not a separate change I am authorising.
  - The absolute floor 1e-10 is stated in the units of the ranked series. For a source whose absolute magnitude is below roughly 1e-8 it would dominate the relative term and could over-suppress. No default symbol here is anywhere near that, but a user swapping in such a symbol is outside what I verified.
  - ta.roc's denominator (creditRatio[creditRocLen]) is unguarded against zero. Out of scope for FINDING 1/2/3 and I did not specify a fix; noting it so it is not assumed covered.
  - I did not compile this script and cannot. Nothing here asserts that any specified expression compiles.

## Orchestrator brief

- Mode RESEARCH. No code written, no .pine touched. This is a settled specification for FINDING 1, 2 and 3 only.
- FINDING 1 decision: a two-term dispersion floor, `disp <= 1e-10 + 1e-9 * scale`, over the L+1 bar set, applied to vixClose, corClose and creditRawStress. Catches both the true-tie and the float-noise case.
- The floor constants are derived from IEEE-754 double precision, not tuned. Result is invariant across an 11-decade band. Not an input.
- FINDING 2/3 decision: option (a). An integer `basisCode` bitmask (1/2/4) carried per bar; impulse is na when basisCode differs across impulseLen. Option (b) specified and rejected.
- The bitmask must not be replaced by sumWeights — sumWeights collides at the default weights. This is the single most likely implementation slip.
- Input signature: UNCHANGED. No new input.* is needed or wanted. Feeds the design-phase trigger as "no signature change".
- Contract note: the proposed Basis table row requires table.new's row count to go 6 -> 7.
- Open decision for the owner/producer: FINDING 3's composite LEVEL jump is not fixed by the impulse rule. Two options are laid out; I recommend displaying the basis, not withholding the composite.
- Lane split: all specified code lands on `backend` (single .pine file). The header disclosure wording in § Header disclosure required lands on `docs`.
- Blocks dispatch: nothing, unless the owner wants the FINDING 3 level decision settled before backend starts.
- Sections: § Method and independent check, § FINDING 1 fix, § Is the floor a tuned constant, § Header disclosure required, § Why sumWeights is not a valid basis key, § FINDING 2 and 3 fix, § FINDING 3 walk-through, § Option (b) and why it is rejected, § FINDING 3, § Input signature, § What this spec must not disturb, § Repaint analysis.

## Method and independent check

Per the order's non_goals I took FINDING 1/2/3 as established and did not re-derive them. What I did do is write an independent Python implementation of the *proposed* rules and run it, because a specification whose numbers were never executed is a proposal, not a specification.

The implementation reproduces the prior audit's figures before applying my fix — 71.03 on the float-noise credit tail, -24.0 at the one-bar COR1M gap, -14.0 at bar 272 — which is my evidence that I am specifying against the same construction the audit measured, not a paraphrase of it. Then it applies the proposed rules to the same scenarios.

Scenarios run: constant VIX (true tie); the audit's `hyg = 80*1.001^i, lqd = 100*1.001^i` float-noise case; a genuinely small (1bp) credit move that must survive the floor; a flat history with a breakout current bar that must survive; a one-tick VIX wobble; a not-yet-full window; the one-bar COR1M gap; the 272-bar warm-up boundary; and a zero-weighted component dropping out.

This is re-derivation from definitions plus boundary analysis — anchors 2 and 4 in the quant pack. There is no primary source to anchor against: the script is a declared ORIGINAL approximation.

## FINDING 1 fix

**The rule.** For a series `src` ranked over lookback `L`, the percentile is unavailable when the set `src[0..L]` — the L values `ta.percentrank` compares against, *plus* the current value being ranked — has dispersion at or below a floor:

```
disp  = max(src[0..L]) - min(src[0..L])
scale = max( |max(src[0..L])| , |min(src[0..L])| )
floor = ABS_FLOOR + REL_FLOOR * scale
percentile is na  iff  disp <= floor
```

with `ABS_FLOOR = 1e-10` and `REL_FLOOR = 1e-9`. This is the standard two-term `isclose` form. The relative term handles level-valued series (VIX, COR1M) whose noise scales with their magnitude; the absolute term handles series that live near zero (creditRawStress is a percent centred on 0), where a purely relative test degenerates — at bar 299 of the float-noise case `scale` is 2.78e-14, so `REL_FLOOR * scale` is 2.8e-23 and only the absolute term has any authority.

**Six points the implementer must get right.**

1. **The window is L+1 bars, not L.** `ta.highest(src, percentileLookback + 1)`. `ta.highest(src, n)` spans `src[0..n-1]`, so `n = L+1` gives exactly the comparison set plus the current bar. Using `L` would omit the current value and wrongly suppress the legitimate case where a flat history is broken by the current bar.
2. **The guard applies to the ranked series, not the raw feed.** For credit that is `creditRawStress`, not `creditRatio` and not `hygClose`/`lqdClose`. This is what makes the float-noise case detectable at all: the ratio's noise is invisible at ratio scale and only becomes the whole signal after the ROC.
3. **No separate guard on creditRatio is needed.** A constant `creditRatio` produces a constant `creditRawStress`, which the guard on `creditRawStress` already catches. Verified: scenario S2 is exactly this path.
4. **Hoist the `ta.*` calls.** Assign `ta.highest`/`ta.lowest`/`ta.percentrank` to top-level variables and use those in the ternary, rather than calling them inside one. Pine's evaluation of built-ins inside a conditional branch is the prior audit's open risk 4; hoisting makes the question moot for these lines.
5. **na propagation.** Over the warm-up `ta.highest` is na, so `disp` is na and the comparison is not a reliable false. Guard with an explicit `na()` test so the result is na by construction rather than by a comparison's incidental behaviour.
6. **Constants, not inputs.** See § Input signature.

**Exact Pine, replacing lines 63-70.** Variable names are part of the specification.

```pine
// --- dispersion floor: a percentile rank is meaningless when its own comparison
// window has no dispersion. Derived from IEEE-754 double precision, not tuned.
// See header. ABS term guards series that live near zero (a percent-valued ROC);
// REL term guards level-valued series whose float noise scales with magnitude.
DISPERSION_ABS_FLOOR = 1e-10
DISPERSION_REL_FLOOR = 1e-9

hasDispersion(hi, lo) =>
    na(hi) or na(lo) ? false : (hi - lo) > DISPERSION_ABS_FLOOR + DISPERSION_REL_FLOOR * math.max(math.abs(hi), math.abs(lo))

dispLen = percentileLookback + 1

vixHi = ta.highest(vixClose, dispLen)
vixLo = ta.lowest(vixClose,  dispLen)
vixPr = ta.percentrank(vixClose, percentileLookback)
vixPct = na(vixClose) or not hasDispersion(vixHi, vixLo) ? na : vixPr

corHi = ta.highest(corClose, dispLen)
corLo = ta.lowest(corClose,  dispLen)
corPr = ta.percentrank(corClose, percentileLookback)
corPct = na(corClose) or not hasDispersion(corHi, corLo) ? na : corPr

creditRatio     = (na(hygClose) or na(lqdClose)) ? na : hygClose / lqdClose
creditRawStress = na(creditRatio) ? na : -ta.roc(creditRatio, creditRocLen)

credHi = ta.highest(creditRawStress, dispLen)
credLo = ta.lowest(creditRawStress,  dispLen)
credPr = ta.percentrank(creditRawStress, percentileLookback)
creditPct = na(creditRawStress) or not hasDispersion(credHi, credLo) ? na : credPr
```

**Verified behaviour**, from the independent implementation:

| scenario | window disp | unguarded | guarded |
|---|---|---|---|
| VIX constant at 18.0, 300 bars, L=252 | 0 | **100.0** | **na** |
| audit's float-noise credit, last bar | 5.551e-14 | **71.03** | **na** |
| audit's float-noise credit, whole tail | 5.551e-14 | 2.0 .. 99.6 | **na on every bar** |
| genuine 1bp ratio drift | 4.89e-3 | 100.0 | **100.0** (survives) |
| flat history, current bar breaks to 25.0 | 7.0 | 100.0 | **100.0** (survives) |
| one-tick VIX wobble 18.00/18.01 | 0.01 | 100.0 | **100.0** (survives) |
| bar 251, window not yet full | na | na | **na** |

The 71.03 and the 2.0..99.6 range are the prior audit's own reported numbers, reproduced independently here, then suppressed.

## Is the floor a tuned constant

The order asks this directly, and the honest answer is: **no, and here is the arithmetic that makes it not one** — but it must still be disclosed.

The argument is that the result is *invariant* to the constants' values across a very wide band, which is precisely what distinguishes a derived guard from a tuned parameter. The weights, lookback and thresholds the header already apologises for are tuned in the strict sense: every value gives a different published number. These do not.

**Lower bound — where IEEE noise ends.** Double precision has relative error 2^-53 = 1.11e-16. A percent-valued ROC computed from two doubles carries absolute error of order a few ulps times 100, i.e. ~4.4e-14. The audit's float-noise case measured 5.55e-14, which sits exactly on that estimate — confirming the noise floor is a property of the arithmetic and not of the data.

**Upper bound — where economics begins.** The smallest dispersion any real input can produce:

| smallest real dispersion | value | margin over ABS_FLOOR |
|---|---|---|
| VIX / COR1M one-tick window range (0.01 index pt) | 1e-2 | 1e8 x |
| credit ROC range from a 1bp ratio move | 1e-2 | 1e8 x |
| credit ROC range from a 0.01bp ratio move | 1e-4 | 1e6 x |

**The band between them is about 11 decades wide**, and every choice inside it produces identical output on every scenario above. `ABS_FLOOR = 1e-10` sits ~1800x above the measured noise and ~1e8 below the smallest quotable move; `REL_FLOOR = 1e-9` at VIX's scale of 18 gives 1.8e-8, still ~6e5 below one tick. The values are chosen to sit near the geometric middle of the empty band, which is the only choice that has to be made at all.

**But it must still be disclosed**, for two reasons. First, guardrail 2: a computed value traces to a named source or the header declares it original, and this is a new decision rule, not arithmetic that follows from anything cited. Second, guardrail 5 asks missing data to degrade *visibly* — a reader seeing "n/a" on a live VIX cell is entitled to know a dispersion test caused it, otherwise they will conclude the symbol failed, which is exactly FINDING 4's failure mode reappearing under a new cause.

## Header disclosure required

Docs-lane wording. This is not optional; it is what stops the new guard from being an undocumented rule.

> Degenerate-input guard: a percentile rank is only published when its own
> comparison window actually has dispersion. A window is treated as having
> none when its range falls at or below `1e-10 + 1e-9 * (largest absolute
> value in the window)`, and the percentile then reads `n/a` rather than a
> number. This catches a frozen or halted feed (a constant series would
> otherwise rank at the maximum and report the "Stressed" regime) and a
> series that is economically constant but numerically noisy at the
> IEEE-754 level (the HYG/LQD ratio when both legs move identically).
> These two constants are NOT tuned parameters like the weights and
> thresholds below: they sit in an ~11-decade band between double-precision
> rounding noise (~5e-14) and the smallest dispersion any real quote can
> produce (~1e-2), and any value inside that band gives identical output.

Note for docs: this **adds** an admission, it does not weaken one. The existing caveats at header lines 20-27 stay verbatim.

## Why sumWeights is not a valid basis key

This is the most likely way the FINDING 2 fix gets implemented wrongly, so it is stated before the fix rather than after.

`sumWeights` is the obvious handle — it already exists at line 77 and it changes when a component drops out. It is not injective. At the default weights 1.0 / 1.0 / 0.5:

| basis | sumWeights | basisCode | composite |
|---|---|---|---|
| {VIX} only | **1.0** | 1 | 30.0 |
| {COR1M} only | **1.0** | 2 | 90.0 |
| {VIX, Credit} | **1.5** | 5 | 30.0 |
| {COR1M, Credit} | **1.5** | 6 | 70.0 |

A basis test of `sumWeights == sumWeights[impulseLen]` passes the first pair as "same basis" and publishes an impulse of **60.0** when VIX dropped out and COR1M appeared and no percentile moved. That is FINDING 2 with a bigger number. The membership bitmask separates them.

## FINDING 2 and 3 fix

**Option (a) is chosen**: carry the composite's basis alongside `systemicStress` on every bar, and define the impulse as na whenever the basis at bar `t` differs from the basis at bar `t - impulseLen`.

**What "basis" means, exactly.** The set of components that *contribute* to the composite on that bar. A component contributes when it is non-na **and** its weight is non-zero. Weight *values* need not be compared: Pine inputs are constant for the whole evaluation of a chart, so `wVix` at bar t always equals `wVix` at bar t-impulseLen. Basis equality therefore reduces exactly to **membership equality**, encoded as a bitmask.

**Why the weight != 0 clause matters.** A component with weight 0 contributes nothing; the composite is bit-identical whether it is present or absent. Requiring its presence to match would suppress the impulse for no reason. Verified: with `wCredit = 0` and credit absent at bar 5, basisCode stays 3 throughout and the impulse stays 0.0 on every bar, correctly.

The test is `!= 0` rather than `> 0` deliberately, so the rule is correct whether or not FINDING 7's `minval = 0` on the weights is applied. Under `minval = 0` the two are identical.

**Exact Pine.** Insert after line 80, replacing line 83.

```pine
// Basis: which components actually contribute on this bar. A bitmask, NOT
// sumWeights -- sumWeights collides ({VIX} and {COR1M} both sum to 1.0 at the
// default weights), so it cannot distinguish two different bases.
vixInBasis    = not na(vixPct)    and wVix    != 0
corInBasis    = not na(corPct)    and wCor    != 0
creditInBasis = not na(creditPct) and wCredit != 0
basisCode = (vixInBasis ? 1 : 0) + (corInBasis ? 2 : 0) + (creditInBasis ? 4 : 0)

// The impulse is a difference of two composites. It is only meaningful when both
// were computed over the same set of components; otherwise the "move" is a
// change of definition, not a change in stress.
basisStable = not na(basisCode[impulseLen]) and basisCode == basisCode[impulseLen] and basisCode != 0
stressImpulse = na(systemicStress) or na(systemicStress[impulseLen]) or not basisStable ? na : systemicStress - systemicStress[impulseLen]
```

`basisCode != 0` is redundant under non-negative weights (an empty basis makes sumWeights 0 and `systemicStress` already na) but is cheap and holds the rule together if a negative weight ever reaches line 77. Keeping it is a deliberate choice, not an oversight.

**Verified on FINDING 2's own scenario** (vixPct 30, corPct 90, creditPct 30 held flat, weights 1.0/1.0/0.5, COR1M missing at bar 5 only, impulseLen 5):

| bar | basisCode | composite | old impulse | new impulse |
|---|---|---|---|---|
| 4 | 7 | 54.0 | na | na |
| **5** | **5** | 30.0 | **-24.0** | **na** |
| 6-9 | 7 | 54.0 | 0.0 | 0.0 |
| **10** | 7 | 54.0 | **+24.0** | **na** |
| 11-12 | 7 | 54.0 | 0.0 | 0.0 |

The rule suppresses **exactly the two bars** whose raw difference is corrupted — bar 5, where the audit reported -24.0, and bar 10, where the gapped value re-enters as the lagged term and produces a spurious +24.0 that the original audit did not enumerate. Bars 6-9 are untouched and still publish 0.0. The suppression is minimal, not blanket.

## FINDING 3 walk-through

The order asks explicitly that the FINDING 2 fix be walked through FINDING 3's bar-271/272 scenario. Setup: `percentileLookback = 252`, `creditRocLen = 20`, `impulseLen = 5`. vixPct and corPct become available at bar 252 and are pinned at 80; creditPct needs 20 bars for the ROC plus 252 to rank it, so it appears at bar 272 pinned at 10.

| bar | vix | cor | cred | composite | basisCode | basisCode[t-5] | old impulse | **new impulse** |
|---|---|---|---|---|---|---|---|---|
| 251 | na | na | na | na | 0 | — | na | na |
| 252 | 80 | 80 | na | 80.0 | 3 | 0 | na | na |
| 257 | 80 | 80 | na | 80.0 | 3 | 3 | 0.0 | **0.0** |
| **271** | 80 | 80 | na | 80.0 | 3 | 3 (bar 266) | 0.0 | **0.0** |
| **272** | 80 | 80 | 10 | 66.0 | **7** | **3** (bar 267) | **-14.0** | **na** |
| 273 | 80 | 80 | 10 | 66.0 | 7 | 3 | -14.0 | **na** |
| 276 | 80 | 80 | 10 | 66.0 | 7 | 3 (bar 271) | -14.0 | **na** |
| **277** | 80 | 80 | 10 | 66.0 | 7 | **7** (bar 272) | 0.0 | **0.0** |
| 278 | 80 | 80 | 10 | 66.0 | 7 | 7 | 0.0 | **0.0** |

**The answer the order asks for:**

- **Bar 271 publishes 0.0, and that is correct.** The basis is {VIX, COR1M} at both bar 271 and bar 266. Nothing moved, and the impulse says so. The fix does not suppress this bar, which matters: a rule that blanked the whole warm-up region would be over-broad.
- **Bar 272 publishes na, and that is correct.** The old -14.0 was not a stress move; it was the composite changing from a two-component average to a three-component one. The two operands of the subtraction are 80.0 computed over {VIX, COR1M} and 66.0 computed over {VIX, COR1M, Credit}. They are not the same quantity, so their difference has no meaning and the honest output is "unavailable", not a number. This is the missing-input-produces-unavailable-output rule, not a fallback.
- **Bars 273-276 also publish na**, for the same reason: their lagged operand still sits on the old basis. The suppression lasts exactly `impulseLen` bars.
- **Bar 277 resumes at 0.0**, the first bar whose lagged operand (bar 272) shares the new basis. Correct: the composite has been flat at 66.0 across those five bars.

So one rule fixes both findings' impulse defect, and it degrades for exactly the window over which the difference is undefined — five bars, once, at the boundary.

## Option (b) and why it is rejected

The order permits an alternative, so it is specified rather than dismissed. Option (b): difference each component percentile and reweight, using only components present at both `t` and `t - impulseLen`:

```
impulse = sum over i in (present at both) of w_i * (pct_i[t] - pct_i[t-impulseLen])
          / sum over i in (present at both) of w_i
```

It is a defensible construction and it is not arithmetically wrong. It is rejected for three reasons, in order of weight:

1. **It publishes a number in exactly the degenerate case.** At FINDING 3's bar 272 the components present at both bars are {VIX, COR1M}, both flat, so option (b) publishes **0.0** — "no change in stress" — while the `systemicStress` line plotted directly above it visibly drops from 80.0 to 66.0. The panel contradicts itself on screen, and the reading that gets believed is the number, because it is the more precise-looking of the two. A plausible number in a degenerate case is worse than na.
2. **It needs its own basis rule anyway.** A component present at t but not at t-impulseLen has an undefined difference, so option (b) does not avoid the basis question; it relocates it into the summation and makes the denominator vary bar to bar.
3. **It changes the published quantity's definition.** The header says the impulse is "how much Systemic Stress has moved over the last N bars". Option (b) is a reweighted average of component moves, which equals that only when the basis is stable — i.e. exactly where option (a) also publishes. Where they differ, option (b) is no longer measuring what the header says it measures, so it would force a header rewrite as well as a code change.

Option (a) is chosen.

## FINDING 3

FINDING 3 has two halves and the order's definition_of_done scopes only one of them to me.

**The impulse half is fixed** by the basis rule above — specified, walked through, verified.

**The composite LEVEL half is not, and cannot be by any impulse rule.** The plotted `systemicStress` still steps from 80.0 to 66.0 at bar 272 with no input moving, because the renormalisation is scale-correct but not level-correct. That is a real remaining defect and I do not want it recorded as closed.

The prior audit offered two resolutions. They have different costs and **the choice is an owner/producer decision, not mine**:

- **Display the basis** (audit's second branch). Keep the exclude-and-renormalise behaviour exactly as it is, and add a table row naming which components are in the composite — "VIX+COR1M" versus "VIX+COR1M+Credit". The step is still there but is no longer silent, which is what guardrail 5's "degrade visibly" actually asks for.
- **Withhold the composite** until every non-zero-weight component is available (audit's first branch). This removes the step entirely, and I note it is the option the standing preference for withholding over publishing would normally favour.

**I recommend displaying the basis**, and the reason is specific rather than a preference for the lighter change: withholding would blank the entire panel for the first 272 bars of any chart, and would blank it *permanently* for any user whose plan does not carry COR1M. The header at lines 20-24 makes exclude-and-renormalise a deliberate design choice precisely for that user. Withholding would reverse that decision for everyone in order to fix a 20-bar warm-up artefact, and reversing a deliberate trust decision is not something to do in passing.

If the basis row is adopted, the contract note applies: `table.new(..., 2, 6, ...)` at :113-115 must become `2, 7`, because the maximum row count rises to 7 when `showComponents` is true.

## Input signature

**No input signature change.** Stated explicitly because it feeds the design-phase trigger.

- No new `input.*` for the dispersion floor. `DISPERSION_ABS_FLOOR` and `DISPERSION_REL_FLOOR` are script-level constants.
- No new `input.*` for the basis rule. It reads existing weights and `impulseLen`.
- No existing input's type, default, title, group or options change.

**Why the floor must not be an input**, since that is the tempting alternative. An `input.float` is an invitation to tune, and this is the one constant in the script that must not be tuned: the whole argument that it is not an arbitrary parameter (§ Is the floor a tuned constant) is that any value in an 11-decade band gives identical results. Exposing it puts a control in the user's hands whose only reachable non-identical settings are wrong ones — set it to 1.0 and every percentile on the panel goes permanently n/a; set it to 0 and FINDING 1 returns intact. It would also land in the "Calculation" group next to the lookback, where the header's existing "tune them to your taste" invitation would read as applying to it. That is how a derived guard becomes a tuned constant the header has to apologise for.

The only signature-adjacent change in this spec is the table row count in the contract notes, and that is a consequence of the FINDING 3 display option, not of the two fixes.

## What this spec must not disturb

Checked item by item against the prior audit's "What re-derived clean" list.

| Cleared item | Does this spec touch it? |
|---|---|
| **creditRawStress sign** | No. Line 69's `-ta.roc(creditRatio, creditRocLen)` is reproduced verbatim in the specified replacement. The negation and its position are unchanged; the guard is applied downstream of it and is monotone-neutral. |
| **Regime band boundaries** | No. Lines 86-94 are not touched at all. The half-open `[lower, upper)` ladder, the strict `<` at each step, and the `bgcolor` complement at :110 are untouched. The only change reaching them is that `systemicStress` is na more often, which the existing `na(systemicStress) ? "N/A"` branch already handles correctly. |
| **Renormalisation scale preservation** | No. Lines 73-80 are unchanged. `basisCode` is read-only with respect to the composite — it is computed from the same na-tests but feeds only the impulse. `systemicStress` stays inside [0,100] exactly as the audit's 20,000-triple check established. |
| **Percentile construction** | No. `ta.percentrank(src, percentileLookback)` is called with the identical source and identical length, and still excludes the current bar from its own comparison set. The guard gates *whether* the value is published, never *what* it is. Worked example A's 90.0 and 100.0 are unaffected: that window has dispersion 11 and passes the floor by ten decades. |
| **Impulse sign** | No. The subtraction is `systemicStress - systemicStress[impulseLen]` in the same order. Positive still means stress building. The basis rule gates availability only. |
| **The `sumWeights > 0` guard at :80** | No. Unchanged. The audit called it right and it stays. |
| **The redundant-but-harmless double na-guard at :78** | No. Unchanged. The audit declined to make it a finding and I am not reopening it. |
| **Table geometry** | Only if the FINDING 3 basis row is adopted, and then only the row count 6 -> 7. Raised as a contract note rather than done silently. |

Two things the implementer should know are *deliberately* changed and are not on the cleared list: the `ta.*` calls at :63/:64/:70 move out of their ternaries into hoisted assignments (§ FINDING 1 fix, item 4), and line 83 is replaced wholesale.

## Repaint analysis

Required in every artifact touching a computed series, even when the answer is that nothing changes.

Neither specified fix introduces a repaint, and neither fixes one.

- **The dispersion guard** reads `ta.highest`/`ta.lowest` over `src[0..L]` — backward-looking only, no forward index, no higher timeframe. It inherits the provisional-last-bar behaviour already documented as FINDING 5: on a forming bar the current `vixClose` is provisional, so `disp` and therefore the guard's verdict can flip intrabar. A percentile could read n/a at 11:00 and a number at the close. This is the same existing repaint, not a new one, and it is in FINDING 5's scope, not mine.
- **The basis rule** reads `basisCode[impulseLen]`, a historical reference to a settled bar, and compares it to the current bar's value. Historical bars are immutable; only the current bar's `basisCode` is provisional, and only via the same provisional closes. No `ta.valuewhen`, no pivot, no `lookahead`, no alert.
- **Neither fix adds a `request.security` call**, so FINDING 6's missing `lookahead` argument count stays at four and the `--strict` exit status is unchanged by this spec.

One consequence worth stating for the header: after this fix the panel will show n/a in more situations than before, and on the forming bar that n/a can turn into a number at the close. That combination — an availability flag that itself repaints — is worth a sentence in whatever FINDING 5's header disclosure ends up saying. It is a note for the docs lane, not a finding here.
