REPORT 2026-09-18-vertical-volume-indicator/07

status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    AUDIT mode, delta re-verification; order's verification field was NONE. Anchor = a constructed partial-na case built on 02-quant.md's hand-computed worked example (3 bars x 4 intrabars, B=4, R_lo=10.00, R_hi=12.50, h=0.625, clean V_j=(550,720,970,230)). Making bar 2's second intrabar (11.1, 400) na in volume gives V_j=(550,320,970,230), Sum=2070, POC=bin 2, Status "OK - 1 na intrabar(s) skipped", ratio 0.8381 - CHECK. The close-is-na twin ((na, 400)) gives the identical result with no index computation reached. The all-na case reproduces vj all 0.0, vMax 0.0, reason "n/a - no volume reported for this symbol", unchanged from 04-quant-audit. Re-derived in an independent Python transcription of volume_profile.pine:245-302 and 339-349. See section 1.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - CR-1 is satisfied: F1's failure mode (a na-poisoned bin losing POC under Status "OK") is eliminated at volume_profile.pine:282-286 — see § 2
  - two new findings, both SHOULD_FIX, neither blocking: F6 MATERIAL (doc/code), F7 MINOR — see § Findings
  - F6 for docs or backend: the header's Reconciliation bullet (lines 81-89) still calls ~1.00 "a closed invariant"; after this fix a skipped intrabar makes it fall below 1.00 by construction — see § Findings F6
  - F7 for backend: "Intrabars/bar (avg)" counts skipped intrabars in its numerator, so it now reports returned-per-bar, not binned-per-bar — see § Findings F7
  - for test-engineer: the six cases in § 1 are usable as fixture expectations, with exact V_j, POC, ratio and Status strings
  - for integration: `pine_check.py volume_profile.pine` (non-strict) still exits 0; the single P008 at line 193 is the same documented false positive, renumbered from 182 by the header addition

risks:
  - I could not execute Pine. Every statement is re-derivation of the code's logic plus numeric recomputation outside Pine; it is not evidence the script compiles.
  - The skip-and-flag design choice (06-backend § risks) is arithmetically sound and I confirm it does what it claims, but whether the softer degrade or full n/a is the intended reading of CR-1 remains the human's call, as the order says.
  - Status still begins with the literal word "OK" in the flagged form. It is distinguishable (suffix plus orange cell) and I do not raise it as a finding, but a glance that reads only the first two characters is misled; that is inherent to the chosen wording, not a defect in it.
  - F2-F5 from 04-quant-audit.md were not re-opened, per this order. Nothing in the changed lines touches them; F4's "0 of M" coverage row behaviour on the early-exit paths is confirmed unchanged in § 3.
  - `n` is taken from `array.size(closesArr)` only (line 269) while `array.get(volsArr, k)` is indexed by the same k. A shorter volume array would throw before the new na-guard can see it. Pre-existing, unchanged by this fix, out of scope here.

## Orchestrator brief
- verdict PASS. CR-1 is satisfied: F1's failure mode is gone and nothing 04-quant-audit proved has regressed.
- anchor: a constructed partial-na case on 02-quant's worked example - one of bar 2's four intrabars made na. V_j=(550,320,970,230), POC bin 2, ratio 0.8381 CHECK, Status "OK - 1 na intrabar(s) skipped".
- the skip-and-flag choice is arithmetically sound and does what 06-backend claims. Whether it is the right design stays the human's call, not re-litigated here.
- close-is-na now degrades instead of throwing - `na(p)` is tested before `binIdx` is computed. Traced, not observed; nobody here can run Pine.
- all-na case re-derived independently, not accepted from backend: bins stay 0.0, vMax 0.0, same `vMax <= 0` branch, same string. Unchanged.
- `naIntrabars` cannot read stale - plain local above the `reason` guard, and both readers short-circuit on `reason`, so every early-exit path is safe.
- reconciliation stays honest: skipped volume leaves the numerator, its bar stays in the denominator, ratio falls and flags. The bar's other intrabars bin normally.
- 2 new findings, both SHOULD_FIX, neither blocking: F6 MATERIAL (header's "closed invariant" wording now false), F7 MINOR (Intrabars/bar counts skipped prints).
- F2-F5 not re-opened, per the order.
- sections: 1. The constructed partial-na case, re-derived / 2. Does the fix eliminate F1 / 3. Early-exit paths and `naIntrabars` / 4. What I rely on from 04-quant-audit / Findings / What would have made this FAIL.

## 1. The constructed partial-na case, re-derived

I transcribed volume_profile.pine:245-302 (declarations, binning loop, POC loop,
sumVj) and 339-349 (avgIntrabars, ratio, statusText) into an independent Python
implementation and ran it on 02-quant.md's worked example plus five mutations of
it. Bar volumes taken as the sum of each bar's intrabars (750, 850, 870).

| case | mutation | V_j | Sum V_j | POC | ratio | Status |
|---|---|---|---|---|---|---|
| A | none (prior audit's anchor) | 550, 720, 970, 230 | 2470 | 2 (11.5625) | 1.0000 | `OK` |
| B | bar 2 ib 2 -> (11.1, na) | 550, **320**, 970, 230 | 2070 | 2 (11.5625) | 0.8381 CHECK | `OK — 1 na intrabar(s) skipped` |
| C | bar 2 ib 2 -> (na, 400) | 550, **320**, 970, 230 | 2070 | 2 (11.5625) | 0.8381 CHECK | `OK — 1 na intrabar(s) skipped` |
| D | bar 3 ib 2 -> (11.7, na) | 550, 720, **470**, 230 | 1970 | **1** (10.9375) | 0.7976 CHECK | `OK — 1 na intrabar(s) skipped` |
| E | every intrabar volume na | 0, 0, 0, 0 | na | — | n/a | `n/a — no volume reported for this symbol` |
| F | case B + includeCurrentBar | 550, 320, 970, 230 | 2070 | 2 | 0.8381 CHECK | `OK — PROVISIONAL — 1 na intrabar(s) skipped` |

Case A reproduces the prior audit's anchor exactly (`L_j` = 0.5670, 0.7423,
1.0000, 0.2371), which is what licenses treating the rest of 04-quant-audit's
§ 1 as still standing: the binning expression at line 285 is character-for-
character the old line 265, only relocated into the `else` arm.

**Every other guarantee survives.** Bin construction (`h = (rHi - rLo)/binCount`,
line 264) untouched. The clamp `math.max(0, math.min(binCount - 1, floor(...)))`
untouched, so the top bin is still closed at `R_hi`. Close-binning: one bin per
intrabar, whole volume, no spreading — case B's bins 0, 2 and 3 are bit-identical
to case A, and only the skipped intrabar's own bin changes, by exactly its own
400. Normalisation `L_j = V_j / vMax` and the strict-`>` ascending POC tie-break
at lines 291-295 are unchanged and now operate on strictly non-na floats, which
is a strengthening: after the fix `vj` cannot hold `na` at all, because every
element starts at `0.0` (line 265) and only non-na `v` is ever added.

**Case D is the one that matters for trust.** Under the old code, bin 2 would
have gone `na`, `na > vMax` is false, and POC would have been awarded to bin 1
(720) with the Status row reading a bare `OK` — F1's exact failure mode. Under
the fix POC is *also* bin 1, but for an honest reason (470 < 720 on the data
that actually exists), and the chart says so in two places.

## 2. Does the fix eliminate F1

Yes, on both halves of the finding.

- **Volume-is-na.** Line 282's `if na(p) or na(v)` short-circuits before line 286's
  `array.set(vj, binIdx, array.get(vj, binIdx) + v)`, so no `na` ever enters `vj`.
  A bin can no longer become unwinnable for POC, and `sumVj` can no longer become
  `na` through a poisoned element.
- **Close-is-na.** `na(p)` is tested before line 285 computes `binIdx`, so
  `math.floor((p - rLo)/h)` is never evaluated on `na` and `array.set` is never
  called with an `na` index. The runtime-error path CR-1 names is unreachable by
  construction rather than by luck. This is a code-path trace, not an observation
  — neither I nor the backend lane can execute Pine, and I do not claim otherwise.
- **Status.** `reason` stays `""` in the partial case, so the profile still
  renders, but line 349 selects `statusOkFlagged` whenever `naIntrabars > 0`, and
  line 380 turns the cell orange. The bare `OK` that F1 called the real defect is
  no longer reachable while any intrabar was skipped.

**The reconciliation invariant.** The skipped intrabar leaves the numerator
(`sumVj`, lines 299-302, summed from `vj`) but its *bar* is still covered, so
`sumBarVolumeCovered` (line 273, inside the `n > 0` guard) still carries that
bar's full native volume. The ratio therefore falls below 1.00 by exactly the
skipped volume's share — 2070/2470 = 0.8381 in case B — and trips the 2% CHECK
flag. That is the correct behaviour and it is what the ratio is for: volume
genuinely is being dropped. The rest of that bar's genuine intrabars are
unaffected, as case B's untouched bins 0, 2 and 3 show. Uncovered bars remain
excluded from both sides, exactly as 04-quant-audit § 5 established.

## 3. Early-exit paths and `naIntrabars`

`int naIntrabars = 0` sits at line 254, inside the `barstate.islast` block, above
the `if reason == ""` guard at 256, and is **not** `var` — so it is
re-initialised on every execution of the block and can never carry a value from a
previous bar or tick. It has exactly four textual occurrences (283 increment, 348
text, 349 selector, 380 bgcolor), all inside the same block.

Both readers short-circuit on `reason` first: line 349 is
`reason != "" ? reason : (naIntrabars > 0 ? ... )`, and line 380 is
`reason != "" ? gray : (naIntrabars > 0 ? orange : na)`. So on the below-minBars
path (242) and the degenerate-range path (261) — the two 04-quant-audit § 3 / F4
found return before the binning loop runs — `naIntrabars` is not read at all, and
would be `0` if it were. The same holds for the `c == 0` (288) and `vMax <= 0`
(296) branches. No stale or uninitialised read exists on any branch.

**Case E verified independently, not accepted from 06-backend § handoff.** With
every intrabar volume `na`: the loop still runs, `c` increments (line 271, guarded
on `n > 0`, which is about array size and not about `na`), all twelve intrabars
are skipped, every `vj` element stays `0.0`. `0.0 > 0.0` is false, so `vMax`
stays `0.0` and `pocIdx` stays `-1`; line 296's `vMax <= 0` fires and sets
`"n/a — no volume reported for this symbol"`. Same branch, same string as
04-quant-audit § 3. The only difference from before is internal — the bins are
`0.0` rather than `na` — and it is invisible downstream because both fail
`> vMax`. `sumVj` is never assigned, so `ratio` is `na` and the row reads `n/a`,
also as before. Backend's claim is correct.

## 4. What I rely on from 04-quant-audit

Cited rather than redone, with the reason each is untouched by lines 245-286 and
347-358:

- **§ 1 (anchor)** — re-run in full above as case A; reproduces exactly.
- **§ 2 (window / repaint, 8-case simulation)** — the fix touches nothing inside
  the index arithmetic. `srcLow = low[1]` (now 209), `rangeLen` (211),
  `usableSize`/`m` (238-239), `endIdx = qSize - 2` / `startIdx` (257-258) and the
  queue cap at `lookbackBars + 1` (203) are all present and unchanged in
  substance, renumbered by +11 from the header addition only. The simulation's
  result stands.
- **§ 3 (failure-mode table)** — all four `n/a` branches and their ordering are
  unchanged (242, 262, 289, 297); the four strings are still distinct. The `c == 0`
  branch is still reached the same way. Only the all-na row's internal mechanism
  changed, re-verified above.
- **§ 4 (forbidden implementations)** — re-checked by pattern search, not by
  reading: no `nz(`, no `fixnan`, no `high - low`, and the only `var`
  declarations in the file are the six queue/draw/table objects at 196-221. The
  fix introduced no value substitution — a skipped intrabar contributes nothing,
  it does not contribute a plausible default. Guardrail 5 upheld.
- **§ 5 (diagnostics)** — `c`, `totalIntrabars` and `sumBarVolumeCovered` are
  still computed from the real arrays inside the `n > 0` guard; the ratio's
  definition is unchanged. See F7 for the one row whose meaning shifted.

## Findings

Two, both new, both SHOULD_FIX. Neither blocks. F1-F5 are not re-opened.

```
FINDING 6
severity:   MATERIAL
where:      volume_profile.pine:81-89 (header, "Reconciliation" bullet)
claim:      the ratio ~1.00 is "a closed invariant of the construction (every
            intrabar's volume goes to exactly one bin)", and far from 1.00 means
            "the WHOLE profile is suspect".
actual:     after the fix that invariant is conditional. A skipped intrabar's
            volume leaves the numerator while its bar's native volume stays in
            the denominator, so the ratio falls below 1.00 *by construction*
            whenever naIntrabars > 0. Recomputed: one na intrabar out of twelve
            gives 2070/2470 = 0.8381, a red CHECK, next to a Status row reading
            "OK — 1 na intrabar(s) skipped". The new Status bullet (lines 90-100)
            does not mention the interaction, and the Reconciliation bullet was
            not updated.
impact:     the trader reads two rows giving opposite severities for one cause,
            and the header tells him the whole profile is suspect when in fact a
            known, counted and displayed quantity of volume was deliberately
            excluded. Doc and code disagree; the arithmetic is right.
expected:   amend the Reconciliation bullet to say the invariant holds only when
            naIntrabars = 0, and that a shortfall matching the skipped intrabars
            is the expected reading of the flagged Status, not a separate defect.
```

```
FINDING 7
severity:   MINOR
where:      volume_profile.pine:272, 339, 345 (and header line 70)
claim:      "Intrabars/bar (avg)" is the realised average intrabars-per-bar for
            the covered window, against the 50-100 target.
actual:     `totalIntrabars += n` at 272 counts every returned intrabar, including
            those line 283 then skips. After the fix, returned and binned counts
            can differ: case B returns 12 and bins 11, and the row reads the same
            4 (truncated, per F3) either way. The row measures request coverage,
            not binning coverage, and nothing on the chart states which.
impact:     a reader calibrating the close-binning error against the 50-100 target
            is using a count that includes prints that never entered a bin. Small
            in the normal case, because naIntrabars is displayed separately and
            can be subtracted by hand.
expected:   either state in the header that the count is intrabars returned, or
            exclude skipped intrabars and let the Status count carry them.
```

## What would have made this FAIL

Stated so the PASS is falsifiable. Each was checked and each is absent:

1. `na(p) or na(v)` tested *after* `binIdx` is computed — it is tested before
   (282 vs 285), so the close-is-na runtime error is genuinely unreachable.
2. The skip replacing the contribution with `0`, `nz(v)` or the previous
   intrabar's value — no substitution exists; the contribution is simply absent.
3. The skipped intrabar's volume removed from the reconciliation *denominator*
   as well, which would have hidden the loss by keeping the ratio at 1.00.
4. `naIntrabars` declared `var`, or read on a branch where it was never set —
   neither; it is a plain local above the `reason` guard and both readers
   short-circuit on `reason`.
5. The all-na case falling out of the `vMax <= 0` branch because the bins now
   hold `0.0` rather than `na` — re-derived: it still fires, same string.
6. A bin other than the skipped intrabar's own changing value — case B's bins 0,
   2 and 3 are identical to the clean case, to the digit.
7. The flagged Status reachable while `reason != ""`, which would have shown
   "OK" on an n/a profile — line 349 orders the ternary the other way.
