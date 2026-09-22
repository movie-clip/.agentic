CHANGE REQUEST CR-3 — 2026-09-18-vertical-volume-indicator
lane:        backend
severity:    BLOCKING
round:       1 of 2
raised by:   C:\projects\investments\.agentic\projects\tradingview\runs\2026-09-18-vertical-volume-indicator\11-quant-audit.md § FINDING 8
scope fence: C:\projects\investments\tradingview\volume_profile.pine — only
             the two unguarded array-clearing loops the finding names
             (currently around lines 268 and 271: `for i = 0 to
             array.size(profileBoxes) - 1` / `for i = 0 to
             array.size(profileLabels) - 1`). No other line.

The finding (11-quant-audit.md § FINDING 8, MATERIAL): `profileBoxes` and
`profileLabels` are `var` arrays, empty (size 0) on the first execution of
the `barstate.islast` block — which is every chart's first render. Their
clearing loops (`for i = 0 to array.size(profileBoxes) - 1`, same for
`profileLabels`) then read as `for i = 0 to -1`. Pine's documented `for`
semantics infer the iteration direction from whether `start <= end` at loop
entry when no explicit `by` step is given: `start > end` iterates
*descending*, not zero times. That means the loop body executes twice
(`i = 0`, then `i = -1`) and calls `array.get(profileBoxes, i)` /
`array.get(profileLabels, i)` with an out-of-bounds index on an empty array
— a runtime error, on every chart's first render.

This is a pre-existing defect (unrelated to CR-1 or CR-2, present since
03-backend.md's original version and identical in shape to lines
04-quant-audit.md already read at 219-224) that was masked in the first live
compile attempt because CE10022 aborted the script before any bar ever
executed — this run has never actually reached this code live. The same
file already guards three structurally identical sites correctly (per
11-quant-audit.md's answer to its order's question 5: lines 232, 241, 313
all check the relevant count is `> 0` before looping) — this is the same
pattern, missed at two sites, not a new construction to design.

What would satisfy it: wrap both clearing loops in the same guard already
used elsewhere in this file — `if array.size(profileBoxes) > 0` /
`if array.size(profileLabels) > 0` around each `for`, or an equivalent that
makes both loops correctly run zero times when the array is empty. No other
behaviour changes: the loops' bodies (`box.delete(...)` /
`label.delete(...)` followed by `array.clear(...)`) are otherwise unchanged.

Re-verification note (from the orchestrating session, not the audit): this
CR does not touch any formula, binning, normalisation, POC or window
arithmetic — it is a defensive loop-bounds guard, mechanically identical to
three already-audited-correct sites in the same file. A further quant-audit
round is not being requested for this specific fix; the repo-wide
integration check and the next live compile attempt are this fix's
verification.
