CHANGE REQUEST CR-1 — 2026-09-17-fix-mm-cot-long-short-index
lane:        backend
severity:    BLOCKING
round:       1 of 2
raised by:   C:\projects\investments\.agentic\projects\tradingview\runs\2026-09-17-fix-mm-cot-long-short-index\05-quant-audit.md § FINDING 1 — partially resolved
scope fence: C:\projects\investments\tradingview\mm_cot_long_short_index.pine (code only, below the header comment block)

The finding is fully stated at the path above — read it there, this is not a
restatement. In short: the weekly-observation array only collects one entry
per COT report while the chart timeframe is at or below "W"; above it (a
monthly chart, for instance), `request.security(sym, "W", ...)` delivers one
value per chart bar rather than per report, so the array silently collects
one observation per chart bar (e.g. per month) instead of per week. The
header and docs both claim timeframe invariance that does not hold in this
branch.

Pick one of the two remedies the finding names in its `expected:` field
(§ FINDING 1 — partially resolved), and implement it — do not leave the file
asserting an invariance it does not have:

(a) detect `timeframe.in_seconds() > timeframe.in_seconds("W")` and publish
    `na` with a visible reason in the table (the guardrail-5 answer, and the
    finding's own preference as the smaller change), or
(b) restrict the header's and tooltip's claim to "weekly or lower chart
    timeframes" and make the table row state what it is actually counting
    above that.
