REPORT 2026-09-17-fix-mm-cot-long-short-index/03
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Order's verification field was NONE. Per testing.md this project has no Pine test runner; the worked example below is a hand-computed trace only, checkable by a human or quant-audit against § Formula — specification in 01-quant.md, never executed by anything in this network.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - quant-audit: an independent 12-week, W=4 worked example is in § Worked example below; it exercises all four required boundary rows (window not yet full, a bar where a leg misaligns, a bar where a leg fails to resolve, a constant-net stretch at the hi==lo boundary) plus the bar where the window first becomes full, none of which the 01-quant.md examples cover in one series.
  - docs: this report's § Worked example is citable evidence for docs/mm_cot_long_short_index.md when it is created; it is not itself docs content and was not written there per this order's non_goals.

risks:
  - This is a hand trace, not an executed test; if `request.security()`'s tuple behaviour under `ignore_invalid_symbol = true` does not actually yield `[na, na]` on a single-leg failure (flagged as unresolved by both 01-quant.md and 02-backend.md), week 7 of my trace would need re-deriving once that is confirmed on a real chart.
  - I assumed, as the spec does, that a misaligned/unresolved leg this week does not corrupt `netHist` — the array is only mutated on `not na(net)`, so a skipped week leaves the prior window exactly as it was. This is stated in the spec (step 3) but is easy to get wrong when implementing, so I traced it explicitly at weeks 5 and 7 rather than asserting it.

## Orchestrator brief

- Worked example only, per testing.md: no `.pine` written, no fixture created, nothing here executes.
- One 12-week, `lookbackWeeks = 4` series, independently constructed (not copied from 01-quant.md's Example A/B data) to exercise: window-not-full (weeks 1-3), first-full bar (week 4), a legs-misaligned bar (week 5), a symbol-unresolved bar (week 7), a constant-net-stretch `hi==lo` bar (week 11), and recovery (week 12).
- Every non-`na` value: week 4 = 100.00, week 6 = 100.00, week 8 = 0.00, week 9 = 0.00, week 10 = 0.00, week 12 = 100.00. All `na` weeks and reasons are in the table below.
- Agreement with 01-quant.md noted at the end of § Worked example: same qualitative shape (window-not-full na, first-full-bar value, constant-stretch na, never a fabricated 50) as its Example A/B and its Degenerate check vectors table, on independently chosen numbers.
- Section: § Worked example (single section, the whole body of this artifact beyond the block above).

---

## Worked example

**This is a worked example, not an executable test.** Nothing below runs
automatically or is loaded onto a chart; it is a hand computation from
01-quant.md § Formula — specification, for a human or `quant-audit` to check
the implemented script against — by hand, or via TradingView's Pine Logs on
the compiled indicator, once it exists.

`lookbackWeeks (W) = 4`, chosen small enough to force the window to fill and
empty within a 12-week trace while still being large enough to hold a
4-element rolling min/max. All positions are Managed Money gross contracts;
`net = L - S`.

Legend for the "legs" column: **A** = aligned (both legs report the same
week), **M** = misaligned (both legs resolve but report different weeks —
`net_t` is `na` per step 2), **U** = one leg unresolved (`ignore_invalid_symbol`
degrades that leg to `na`, so `net_t` is `na` regardless of alignment).

| wk | L | S | legs | net | pushed? | `netHist` after this bar (oldest→newest) | `histReady` | `lo` | `hi` | `cotIndex` | why |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 100,000 | 40,000 | A | 60,000 | yes | `[60]` | no (1<4) | — | — | **na** | window not yet full |
| 2 | 110,000 | 50,000 | A | 60,000 | yes | `[60,60]` | no (2<4) | — | — | **na** | window not yet full |
| 3 | 120,000 | 60,000 | A | 60,000 | yes | `[60,60,60]` | no (3<4) | — | — | **na** | window not yet full |
| 4 | 130,000 | 60,000 | A | 70,000 | yes | `[60,60,60,70]` | **yes (4=4)** | 60,000 | 70,000 | **100.00** | **window first full — first non-na bar** |
| 5 | 130,000 | 65,000 | **M** | **na** | no (na net) | `[60,60,60,70]` unchanged | yes | — | — | **na** | legs report different weeks; net degrades to na, array not touched |
| 6 | 140,000 | 70,000 | A | 70,000 | yes | `[60,60,70,70]` (shift oldest 60) | yes | 60,000 | 70,000 | **100.00** | realigned; net back at top of window |
| 7 | 150,000 | **n/a** | **U** | **na** | no (na net) | `[60,60,70,70]` unchanged | yes | — | — | **na** | short leg fails to resolve; long-only reading must not substitute a value |
| 8 | 150,000 | 90,000 | A | 60,000 | yes | `[60,70,70,60]` (shift oldest 60) | yes | 60,000 | 70,000 | **0.00** | net at bottom of window — real 0, not na |
| 9 | 145,000 | 85,000 | A | 60,000 | yes | `[70,70,60,60]` (shift oldest 60) | yes | 60,000 | 70,000 | **0.00** | still at bottom |
| 10 | 140,000 | 80,000 | A | 60,000 | yes | `[70,60,60,60]` (shift oldest 70) | yes | 60,000 | 70,000 | **0.00** | still at bottom |
| 11 | 135,000 | 75,000 | A | 60,000 | yes | `[60,60,60,60]` (shift oldest 60) | yes | **60,000** | **60,000** | **na** | **constant-net stretch — hi==lo, never 50** |
| 12 | 155,000 | 85,000 | A | 70,000 | yes | `[60,60,60,70]` (shift oldest 60) | yes | 60,000 | 70,000 | **100.00** | breaks out of the constant stretch |

Hand check on the two arithmetic rows a reader is most likely to doubt:

- Week 4: window `{60,60,60,70}`k ∪ `{net=70}`k → `lo=60,000`, `hi=70,000`.
  `100 × (70,000 − 60,000) / (70,000 − 60,000) = 100 × 1 = 100.00`.
- Week 8: window `{60,70,70,60}`k ∪ `{net=60}`k → `lo=60,000`, `hi=70,000`.
  `100 × (60,000 − 60,000) / (70,000 − 60,000) = 0.00`.
- Week 11: window `{60,60,60,60}`k ∪ `{net=60}`k → `lo=hi=60,000`. Division by
  zero is guarded by the spec's `netHi == netLo` branch: the result is `na`,
  **not** `50` and **not** an error. This is the row a regression is most
  likely to get wrong, because "constant input → midpoint output" is the
  intuitive-but-forbidden answer per § Formula — specification, step 5.

Table row 5 ("Data as of / legs") behaviour implied by this trace, per the
01-quant.md § Table contract cell rules:

- Week 5 (misaligned, both legs otherwise numeric): `n/a (legs misaligned)`.
- Week 7 (short leg unresolved): plain `n/a` — **not** "misaligned", because
  `mmShortPos` itself is `na`, so `legsMisaligned` (which requires both legs
  to be non-na) is false. A script that shows "misaligned" here instead of a
  plain `n/a` has conflated the two failure modes the table is required to
  keep distinguishable.

**Agreement with 01-quant.md.** This series is independently constructed —
none of its `L`/`S` pairs are copied from Example A or Example B — but it
reproduces the same three invariants those examples and the Degenerate check
vectors table assert: an index value is `na` for every bar before the window
first fills (matches Example A weeks 1-4 and Example B weeks 1-11), a
constant-net window produces `na` rather than a fabricated `50` (matches the
Degenerate check vectors table's first row, `net constant at 50,000 for 6
weeks → na on every bar`), and no computed value ever falls outside `[0,100]`
(matches Example B's step-4 union rationale). It additionally exercises two
rows neither 01-quant.md example carries in the same series: a legs-misaligned
bar arriving *after* the window is already full (week 5), and a single-leg
symbol failure arriving after that (week 7) — both of which must read `na`
for a different stated reason, which is exactly the discrepancy a regression
that collapses the two failure modes into one code path would expose.
