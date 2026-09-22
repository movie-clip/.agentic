CHANGE REQUEST CR-1 — 2026-09-18-vertical-volume-indicator
lane:        backend
severity:    BLOCKING
round:       1 of 2
raised by:   C:\projects\investments\.agentic\projects\tradingview\runs\2026-09-18-vertical-volume-indicator\04-quant-audit.md § Findings, FINDING 1
scope fence: C:\projects\investments\tradingview\volume_profile.pine — only the
             intrabar accumulation loop and the POC/Status logic it feeds
             (volume_profile.pine:262-275 and whatever else reads their
             output for the Status row). No other file, no formula change
             outside this na-handling path.

The finding (04-quant-audit.md § Findings, FINDING 1, MATERIAL): there is no
`na` guard on the intrabar array elements at the point volume is accumulated
into a bin (`array.get(vj, binIdx) + v`). If any returned intrabar volume is
`na`, that bin becomes `na` for the rest of the run; the POC loop's `if vv >
vMax` comparison is false against `na`, so a poisoned bin can never win POC —
it is silently awarded to the largest *unpoisoned* bin instead. `sumVj`
becomes `na` so the Reconciliation row correctly reads "n/a", but `reason` is
still `""` and the Status row reads "OK" regardless. If an intrabar *close*
(not volume) is `na`, `binIdx` itself is `na` and `array.set` raises a runtime
error rather than degrading to `n/a`.

Why it matters: the trader can be shown a POC line that is not actually the
busiest price in the window, on a chart whose Status row says everything is
fine. That is precisely the plausible-looking-wrong output this project's
guardrail 5 ("degrade visibly... never substitute a plausible value") exists
to prevent — the all-`na` case already degrades correctly (the audit
confirmed this separately); only the *partial*-na case fails.

What would satisfy it, per the audit's own `expected` line: skip an intrabar
whose close or volume is `na` (and count it toward a new diagnostic, or at
minimum ensure it cannot silently win/poison the POC computation), or set
`reason` so the profile is `n/a` when any `na` is encountered — either way,
`Status` must never read `OK` while a bin's data was actually incomplete.
Guard the `close`-is-`na` case too, so it degrades to `n/a` rather than
throwing a runtime error.

The human ruled to fix this now rather than carry it — see
`decisions.md § D-3`.
