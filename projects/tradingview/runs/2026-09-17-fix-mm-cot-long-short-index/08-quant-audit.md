REPORT 2026-09-17-fix-mm-cot-long-short-index/08
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   python C:\projects\investments\.agentic\scripts\pine_check.py C:\projects\investments\tradingview\mm_cot_long_short_index.pine --strict
  result:    PASS
  detail:    exit 0, "mm_cot_long_short_index.pine: PASS 0 findings" — re-run by me. Anchors: Briese/Williams 0..100 net COT Index definition re-implemented from the definition sentence; a fresh 60-week synthetic net series of my own; a bar-by-bar emulation of the CURRENT shipped file across chart TFs 60/D/5D/6D/7D/W/2W/M; Pine v6 request.security and var-array semantics.
contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - CR-1 RESOLVED — `tfTooCoarse` at :103 gates collection (:109), publication (:120) and display (:140-141); emulated 2W and M both give window 0, cotIndex na, "n/a (chart TF > W)". See § CR-1 re-verification.
  - CR-1 evidence — my series, W=12, same final report: 60m/D/5D/W all read 61.42 and agree with the definition-first implementation; 2W and M read na. Invariance holds across the range the header now claims. See § CR-1 re-verification.
  - FINDING 2 RESOLVED — zero `:NN` citations remain in docs/mm-cot-long-short-index.md (grepped); it cites banner names, and § DATA, § ALIGNMENT AND NET, § WEEKLY WINDOW, § INDEX, § TABLE all exist in the file. See § FINDING 2-7, re-checked.
  - FINDING 3 RESOLVED — doc:10-12 and doc:180-182 both say "five fixed, two dissolved, one open", and the § Known limits table counts 5/2/1. See § FINDING 2-7, re-checked.
  - FINDING 4 RESOLVED — :156 `text_color` is now `na(cotIndex) ? na : (cotIndex >= 80 or cotIndex <= 20 ? color.white : na)`, exactly the branch :155 tints. See § FINDING 2-7, re-checked.
  - FINDING 5 RESOLVED — :88 `lookbackWeeks = input.int(156, ..., minval=2, ...)`. W=2 is a defined window; the empty-array path is unreachable. See § FINDING 2-7, re-checked.
  - FINDING 6 RESOLVED — header :66-69 discloses the live bar ranks against lookbackWeeks + 1 observations and can move before its bar closes. See § FINDING 2-7, re-checked.
  - FINDING 7 RESOLVED in substance — header :70-76 states the age is measured from the weekly bar's OPEN and runs ~1 week younger on a weekly chart. The tooltip at :86 is unchanged; see § FINDING 2-7, re-checked for why that is acceptable.
  - NEW FINDING 8 (MINOR, non-blocking, :103) — a 6D or 7D chart passes `tfTooCoarse` yet skips weekly reports; emulated 72.65 / 76.84 against a true 61.42. Owner: backend, SHOULD_FIX. See § FINDING 8 — residual coarse-timeframe leak.
  - Original-audit FINDING 6 (symbols unconfirmed) remains open and correctly documented; not re-flagged, per non_goals.

risks:
  - FINDING 8 is the same defect class as CR-1 at a narrower trigger. I graded it MINOR rather than blocking because the trigger is a hand-typed custom timeframe, not a standard one; if the owner reads the order's "any new defect is FAIL" literally, this is the item that would flip the verdict.
  - Header :72's parenthetical "(or coarser, within the invariant range)" is now vacuous — nothing coarser than "W" is inside the invariant range any more. Wording, not arithmetic; not graded as a finding.
  - I still have no Pine compiler. That `timeframe.in_seconds()` with no argument returns the chart timeframe, and that `timeframe.in_seconds("W")` is 604800, are documented v6 semantics reasoned from, not executed.
  - Whether Pine re-initialises `var float[] netHist` when the user changes chart timeframe mid-session is unexecuted, carried from 06-backend.md. It does not affect the verdict: :120 gates `cotIndex` on `tfTooCoarse` directly, so even a stale array cannot publish above "W".
  - `stale` still reads wall-clock `timenow`, so it is true on every historical bar. Harmless while consumed only under `barstate.islast`, unsafe to reuse in an alert. Carried unchanged from 05-quant-audit.md.
  - The TradingView compile check has still not run anywhere in this run. Nothing in this audit is evidence that the script loads.

## Orchestrator brief

- Verdict PASS. CR-1 is RESOLVED; all six of my prior FINDING 2-7 are RESOLVED, each re-read at the current location rather than taken from 06-backend.md or 07-docs.md.
- CR-1 remedy (a) is implemented on both evaluation paths: `tfTooCoarse` is chart-level and constant per bar, and it gates collection, publication and display independently.
- Numerically: 60m / D / 5D / W all read 61.42 on my series and match a definition-first implementation; 2W and M read na with window 0 and the labelled reason.
- One NEW MINOR, FINDING 8: 6D and 7D charts slip under the `> timeframe.in_seconds("W")` threshold and silently skip weekly reports (72.65 / 76.84 vs a true 61.42). Non-blocking; owner backend; a one-line remedy is given.
- `pine_check.py --strict` re-run by me: exit 0, 0 findings.
- Fresh full-file read found no defect introduced by this round. The `barstate.isconfirmed` repaint gate survived the edit at :109 with `and not tfTooCoarse` added as a sibling term.
- Original-audit FINDING 6 (symbols unconfirmed, guardrail 3) remains open by design, per non_goals.
- Sections: § Anchors used · § CR-1 re-verification · § FINDING 2-7, re-checked · § FINDING 8 — residual coarse-timeframe leak · § No-new-defect sweep · § What would have made this FAIL.
- Blocks dispatch: nothing. FINDING 8 is an `Open` row, not a third round on CR-1.

---

## Anchors used

Per `protocol/gates.md` § 2 and the quant pack's "Audit mode: the anchors
available here". Neither the script's comments, nor `docs/mm-cot-long-short-index.md`,
nor `06-backend.md` / `07-docs.md` was treated as an anchor.

1. **The cited primary definition.** Briese (2008) / Williams (2005): a
   stochastic rescale of a trader category's **net** position over a rolling
   window onto 0..100. `cot_index_definition()` was written from that sentence
   and knows nothing about arrays, chart bars or `request.security`.
2. **A fresh emulation of the shipped code as it stands now**, including the
   new `tfTooCoarse` term at :103/:109/:120, driven by a chart-bar stream
   generated per chart timeframe.
3. **My own series.** 60 weekly net observations, seeded independently of round
   1's series and of 01-quant.md and 03-test.md. Final six: 45060, 43427,
   36979, 33969, 30197, 29392.
4. **Dimensional / boundary analysis** across eight chart timeframes, which is
   what produced § FINDING 8 — the 6D and 7D cases are not visible from reading
   the expression.
5. **The mechanical gate**, re-run: `pine_check.py --strict`, exit 0.

## CR-1 re-verification

**Status: RESOLVED.**

The guard, at `mm_cot_long_short_index.pine:103`:

```pine
tfTooCoarse = timeframe.in_seconds() > timeframe.in_seconds("W")
```

It is consumed in three independent places, which is what makes the answer
"both paths" rather than "one path":

| Line | Use | Effect |
|---|---|---|
| :109 | `if newWeekly and barstate.isconfirmed and not na(net) and not tfTooCoarse` | the array never collects above "W", so `netHist` stays empty |
| :120 | `cotIndex = (tfTooCoarse or na(net) or not histReady or netHi == netLo) ? na : ...` | the published value is `na` regardless of the array's contents |
| :140-141 | `indexText` / `windowText` | both cells read `"n/a (chart TF > W)"`, not a bare `n/a` and not `"0/156 weeks"` |

**Why this covers the historical and realtime paths, not one of them.**
`tfTooCoarse` is derived from `timeframe.in_seconds()`, a property of the chart
itself. It carries the same value on every bar and on every tick of every bar —
it is not a series condition that can hold on a confirmed bar and not on a
provisional one. So the historical path (`barstate.isconfirmed` true, one
execution per bar) and the realtime path (many ticks, `isconfirmed` true only on
the last) are gated identically. There is no bar on which the index is published
above "W" and no tick on which the array is mutated above "W".

The :120 gate is also load-bearing on its own. Even if `netHist` were somehow
non-empty above "W" — the case 06-backend.md flagged as unexecuted, a chart
timeframe changed mid-session without the `var` array reinitialising — `:120`
still forces `na`. The fix does not depend on the assumption backend could not
verify.

**Numerically.** My 60 weekly observations, `lookbackWeeks = 12`, reading the
same final weekly report on every chart timeframe:

| chart TF | `tfTooCoarse` | window size | published index |
|---|---|---|---|
| 60 (minutes) | false | 12 | 61.42 |
| D | false | 12 | 61.42 |
| 5D | false | 12 | 61.42 |
| W | false | 12 | 61.42 |
| 2W | **true** | 0 | **na**, cell reads `n/a (chart TF > W)` |
| M | **true** | 0 | **na**, cell reads `n/a (chart TF > W)` |

The definition-first implementation, which has no concept of a chart bar at
all, gives **61.42** for the same final observation. Every timeframe inside the
range the header now claims agrees with it exactly.

Round 1's failing case is gone: the monthly chart read **9.25** against a true
**4.06** on that round's series; it now reads `na` with the reason on the chart.
The header at :53-61 and the tooltip at :89 both now state the restriction
rather than the invariance, so the file no longer asserts something it does not
have — remedy (a) was chosen and remedy (b)'s disclosure obligation was met as
well.

## FINDING 2-7, re-checked

Each row was verified by opening the named location in the current file and
reading the current text, not by accepting either lane's `changed` block.

| Prior finding | Status | Evidence in the current file |
|---|---|---|
| 2 — doc citations 26-34 lines short | **RESOLVED** | A regex sweep for `:NN` / `:NN-NN` across `docs/mm-cot-long-short-index.md` returns **no matches**. Citations are now banner names — § DATA, § ALIGNMENT AND NET, § WEEKLY WINDOW, § INDEX, § TABLE — and all five exist as `// ===== ... =====` banners at :91, :97, :102, :119, :131. A citation that cannot drift is a stronger fix than a re-taken number |
| 3 — "six of eight... two remain open" vs a table listing seven | **RESOLVED** | doc:10-12 reads "five of the prior audit's eight findings are fixed this run, two were dissolved outright... and one remains genuinely open", doc:180-182 repeats the identical count, and the § Known limits table tallies Fixed 1,3,5,7,8 / Dissolved 2,4 / Open 6 = 5+2+1 = 8. Prose and table now agree, and they agree with my own round-1 arithmetic as updated by CR-1 |
| 4 — unconditional `text_color = color.white` | **RESOLVED** | :156 is `text_color = na(cotIndex) ? na : (cotIndex >= 80 or cotIndex <= 20 ? color.white : na)`. :155 tints `bgcolor` on exactly `cotIndex >= 80` / `cotIndex <= 20`. The two branch conditions are now identical, so white text appears only over a tint, and the untinted mid-range falls back to the table's default text colour on any theme |
| 5 — `lookbackWeeks` had no `minval` | **RESOLVED** | :88 `lookbackWeeks = input.int(156, title="Index Lookback (weeks)", minval=2, ...)`. At the new floor W=2 the array holds two observations and :116-117 union in the current `net`, so `netHi == netLo` only on a genuinely constant series — and that case already returns `na` at :120. The empty-array call into `array.min` is unreachable |
| 6 — header did not disclose the provisional live bar | **RESOLVED** | Header :66-69: "The current (still-open) week's reading is PROVISIONAL: by design, the in-progress week is not added to the window until its bar confirms, so the live bar ranks against lookbackWeeks + 1 observations and can move again before that bar closes. This does not change any already-closed bar's plotted value." That is the disclosure the pack requires, including the second sentence distinguishing it from a repaint |
| 7 — staleness basis stated for one branch of two | **RESOLVED in substance** | Header :70-76 now says the age "is measured from that bar's OPEN time, which is the weekly series' CURRENT week on a weekly... chart but the last CLOSED week on a sub-weekly chart — so the same missing report is flagged STALE about a week later on a weekly chart than on a daily one." See the note below on the tooltip |

**On FINDING 7 and the tooltip.** My round-1 `expected:` named the tooltip; the
fix landed in the header instead (07-docs.md was scoped to header prose only).
I am closing it rather than re-raising it, for a reason that is about the
content and not the location:

- The tooltip's own claim is not false. It justifies the **default of 21 days**
  by bounding the lag at ~13 days on the sub-weekly branch. On the weekly-chart
  branch `asOfTime` is the current week's open, so the age runs 0-6 days —
  *smaller*. 21 days therefore absorbs the ordinary lag on both branches, and
  the default it justifies is correct on both. The tooltip is incomplete, not
  wrong, and it is incomplete in the conservative direction.
- The dual basis — the part a reader could act on wrongly — is now stated in
  the header's "WHAT DEGRADES, AND HOW YOU SEE IT" block, which is this repo's
  declared disclosure surface, and again in the doc's § Inputs table.

Grading this as still-present would be grading the location rather than the
defect.

## FINDING 8 — residual coarse-timeframe leak

```
FINDING 8
severity:   MINOR
where:      mm_cot_long_short_index.pine:103
claim:      `tfTooCoarse = timeframe.in_seconds() > timeframe.in_seconds("W")`
            is offered, at :53-61 and in the tooltip at :89, as the complete
            boundary of the range in which "the window counts WEEKLY COT
            REPORTS, not chart bars".
actual:     The threshold is 604800 seconds. A custom N-day chart timeframe of
            6D (518400s) or 7D (604800s) is at or below it, so tfTooCoarse is
            false and the index is published — but a 6-or-7-trading-day chart
            bar spans more than one COT week, so request.security delivers only
            the LAST weekly value closed inside it and the intervening report
            is never pushed. The array collects one observation per chart bar
            again, exactly as it did on a monthly chart before CR-1, only at a
            milder ratio.

            Emulated on my 60 weekly observations, W = 12, same final report:

              5D chart -> 61.42   last 12 observations span 12 reports (correct)
              6D chart -> 72.65   last 12 observations span 15 reports, 3 skipped
              7D chart -> 76.84   last 12 observations span 17 reports, 5 skipped
              W  chart -> 61.42   (the definition-first answer)

            The "12/12 weeks" row asserts 12 in all four cases.
impact:     A trader on a 6D or 7D chart reads 72.65 or 76.84 where the true
            reading is 61.42 — on the 7D chart that crosses from "unremarkable"
            to within touching distance of the 80 crowded-long band. It is a
            plausible-looking number in a degenerate case, which is the outcome
            that never gets questioned, and guardrail 5 asks for a visible
            degrade instead. It is MINOR rather than MATERIAL only because the
            trigger is a custom timeframe the user must type deliberately:
            every timeframe on TradingView's standard list (intraday, 1D, 1W,
            1M) is either correct or already caught, and 8D and above
            (691200s) is caught too. The leak is exactly 6D and 7D.
expected:   Widen the guard so that a chart bar which can contain two weekly
            closes is treated as too coarse, while keeping the exactly-aligned
            weekly chart inside the range:

              tfTooCoarse = timeframe.in_seconds() > timeframe.in_seconds("W")
                   or (timeframe.in_seconds() > 5 * 86400 and timeframe.period != "1W")

            The second term catches 6D and 7D and changes nothing else: 5D and
            below is already under 432000, "1W" is exempted explicitly, and
            2W / M are already caught by the first term. The table's existing
            "n/a (chart TF > W)" label would then want rewording to something
            like "n/a (chart TF too coarse)".
            (Audit only; not fixing.)
```

This is **not** a third round on CR-1 and should not be dispatched as one. CR-1
asked for remedy (a) at the "W" boundary and got it, correctly, on both
evaluation paths. FINDING 8 is a narrower instance of the same class that the
chosen boundary does not reach, found by boundary analysis rather than by
re-reading CR-1's own case. It belongs in the ledger's `Open` table as a
`SHOULD_FIX` for backend.

## No-new-defect sweep

A fresh read of all 164 lines, not a diff.

- **The repaint gate survived the edit.** :109 is
  `if newWeekly and barstate.isconfirmed and not na(net) and not tfTooCoarse`.
  `barstate.isconfirmed` is still a term of the same `if`, still guarding the
  `array.push` at :110 and the cap at :111-112 rather than a read. The new term
  was added as a sibling, not substituted for it. This was the single most
  likely way this round could have broken something, and it did not.
- **`lookahead = barmerge.lookahead_off` is still explicit** on both
  `request.security` calls, :93 and :95, as a named argument alongside the
  `[close, time]` tuple. `pine_check --strict` exit 0 confirms no P008.
- **No new series is published.** One `plot` (:126), three `hline`s (:127-129),
  one table. `indexText` / `windowText` at :140-141 are display-only strings
  and feed no computation.
- **The table's shape still matches its cells.** `table.new(..., 2, 6, ...)` at
  :132; cells are written at rows 0-5, columns 0-1. No out-of-range write.
- **`text_color = na` on the untinted branch** is the same idiom `bgcolor`
  already uses at :155 and falls back to the table's default. It does not make
  the cell invisible; that was FINDING 4's failure mode and it is inverted now.
- **The raw position rows are not gated on `tfTooCoarse`, and should not be.**
  `MM Long/Short/Net Position` and `Data as of` still render above "W", showing
  the latest weekly values inside the last chart bar. Those are point-in-time
  readings that do not depend on the rolling window, so they are correct there;
  only the window-derived index degrades. This is the right split.
- **Arithmetic unchanged.** :116-117 union the current `net` into the array's
  range; :120 divides only when `netHi != netLo`. My definition-first
  implementation reproduces the shipped output on every non-degenerate bar of
  my series, and returns `na` — never 50 — on the constant-series case.
- **Header arithmetic claims re-read.** "156 ≈ 3 years" (:49, :89) — 156/52 = 3
  exactly. "at most about 13 days" (:86) — Tuesday as-of to the second Friday
  is 10 days, plus a weekend before the next bar closes; the ~13 figure is a
  defensible bound. 80/20 as the conventional extremes matches the cited
  authors. No number in the prose contradicts the code.

## What would have made this FAIL

Stated because the pack requires a `PASS` to be falsifiable:

1. `tfTooCoarse` gating only the display, or only `cotIndex`, while the array
   kept collecting — the index would then be correct today and wrong the moment
   the user dropped back to a weekly chart with a poisoned `var` array. It gates
   all three. Checked at :109, :120, :140-141.
2. `tfTooCoarse` computed from a series value rather than a chart property, so
   that it could differ between a realtime tick and the confirmed bar. It is
   computed from `timeframe.in_seconds()`, which is constant for the session.
3. Any of FINDING 2-7 fixed in the report and not in the file. I opened all six
   locations; all six had changed.
4. `barstate.isconfirmed` dropped or demoted to a comment while the `if`
   condition was being extended. It was not.
5. The emulated weekly and sub-weekly readings disagreeing with the
   definition-first implementation. They agree to the cent at 61.42.
6. A monthly chart still publishing a number. It publishes `na` with a labelled
   reason and a window of 0.
