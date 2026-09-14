REPORT 2026-09-14-audit-systemic-stress-dashboard/03
status:      DONE
verdict:     FAIL

changed:
  - none

verification:
  command:   python C:\projects\investments\.agentic\scripts\pine_check.py C:\projects\investments\tradingview\systemic_stress_dashboard.pine --strict
  result:    FAIL
  detail:    exit 1, 4 SHOULD_FIX P008 (lines 57-60, request.security without explicit lookahead), 0 BLOCKING. Math anchor was NOT the script's own comments: re-derivation from the standard definitions of percentile rank / rate-of-change / weighted average, in an independent Python implementation, run over 13 hand-checked scenarios (see § Anchor and method, § Worked example A).

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - FINDING 1 CRITICAL line 63/64/70 — ta.percentrank on a zero-variance or stale series publishes a hard 100 (or 0) instead of n/a; a frozen VIX feed reports regime "Stressed"; breaches guardrail 5; see § FINDING 1
  - FINDING 2 CRITICAL line 83 — stressImpulse differences systemicStress across a change in which components are present, so a component appearing or dropping out is published as a real stress move; see § FINDING 2
  - FINDING 3 MATERIAL lines 73-80 — the renormalisation is scale-correct but not level-correct, and switches basis silently mid-series at the 272-bar credit warm-up boundary; see § FINDING 3
  - FINDING 4 MATERIAL header lines 21-24 — the header's diagnostic "if it stays blank, the symbol didn't resolve" is false during warm-up and during one-bar data gaps, both of which also blank the cell; see § FINDING 4
  - FINDING 5 MATERIAL lines 57-60 — the last bar's close is provisional, so every published value, the regime label and the bgcolor rewrite intrabar, and the header discloses no repainting at all; see § FINDING 5
  - FINDING 6 MINOR lines 57-60 — no explicit lookahead argument; guardrail 1 requires it textually even though at timeframe.period it is inert; this is what fails the static check; see § FINDING 6
  - FINDING 7 MINOR lines 44-50 — no minval and no ordering validation on weights or thresholds; negative weights put systemicStress at 250, mis-ordered thresholds silently make a band unreachable; see § FINDING 7
  - FINDING 8 MINOR header — guardrail 3's third clause unmet: the header never states whether TVC:VIX, CBOE:COR1M, AMEX:LQD, AMEX:HYG were confirmed against TradingView symbol search; see § FINDING 8
  - Confirmed CORRECT and not to be touched: creditRawStress sign, regime band boundaries, renormalisation scale preservation, percentrank usage against its standard definition; see § What re-derived clean

risks:
  - I could not verify any of the four ticker identities: no browser tool in this lane and TradingView symbol search is the only authority. FINDING 8 is about the header's missing statement, not a claim that any ticker is wrong.
  - FINDING 1's exact degenerate value depends on ta.percentrank's tie rule (<= gives 100, < gives 0). I could not execute Pine to settle it. The finding holds under either rule and under neither is n/a produced; § FINDING 1 shows both.
  - Whether ta.percentrank returns na during its first `percentileLookback` bars, or computes on partial history, is an undocumented assumption the script rests on and I cannot execute Pine to settle. If it computes on partial history, FINDING 3's severity rises sharply.
  - Pine's evaluation of ta.* built-ins inside a ternary (lines 63, 64, 70) may or may not be hoisted to every bar. If it is not, a mid-series na in a source series desynchronises that percentrank's window. Only the TradingView compile check can settle this.
  - I did not compile this script and cannot. Nothing in this report asserts that it compiles.

## Orchestrator brief

- Verdict FAIL. Two CRITICAL findings, three MATERIAL, three MINOR. The two CRITICALs are genuine bugs distinct from anything the header discloses.
- The anchor was NOT the script's comments: an independent Python re-implementation from the standard definitions, 13 scenarios, numbers in § Worked example A and § FINDING 1-3.
- FINDING 1 (CRITICAL, lines 63/64/70): a constant or stale input series publishes percentile 100, not n/a. Flat VIX reads "Stressed". Guardrail 5.
- FINDING 2 (CRITICAL, line 83): Stress Impulse differences across a change of basis and reports -24.0 when nothing moved.
- MATERIAL: FINDING 3 silent basis switch at bar 272; FINDING 4 the header's blank-cell diagnostic is wrong; FINDING 5 undisclosed last-bar repaint.
- MINOR: FINDING 6 missing explicit lookahead (this is what fails --strict); FINDING 7 no input validation; FINDING 8 guardrail 3 header clause unmet.
- Explicitly cleared, do not let a fix disturb them: creditRawStress sign, regime band boundaries, renormalisation scale. See § What re-derived clean.
- Lane split: all eight findings land on `backend` (the single .pine file) except FINDING 4 and 8, which are header text and belong to `docs`. FINDING 1 and 3 need a quant RESEARCH decision on what the correct degenerate-case behaviour is before code is written — this audit says "n/a", it does not specify a variance floor.
- Blocks dispatch: nothing. The run has no build lane yet; these findings are what would create one.
- Sections below: § Anchor and method, § Worked example A, § FINDING 1 § FINDING 2 § FINDING 3 § FINDING 4 § FINDING 5 § FINDING 6 § FINDING 7 § FINDING 8, § What re-derived clean, § Repaint analysis.

## Anchor and method

`project.md` and the quant pack both say this script is an ORIGINAL approximation with no external authority, so anchor 1 (a cited primary source) does not exist for it. I used anchors 2 and 4 from the pack: a hand-computed worked example, and dimensional/boundary analysis.

Concretely: I wrote an independent implementation in Python of `ta.percentrank`, `ta.roc`, the na-renormalised weighted average, the impulse difference and the regime ladder — each from its **standard definition**, not from the script's expression — and ran the two side by side over 13 constructed scenarios. Where they agree I have evidence; where they diverge, or where the standard definition itself produces a wrong-looking number, I have a finding.

What is explicitly **not** my anchor: the script's own header comments, and `docs/systemic_stress_dashboard.md` (which does not exist in this repo anyway — recon confirmed `docs/` is absent entirely).

Definitions used:
- **percentile rank** — the percentage of the previous `length` values that are less than (or equal to) the current value; undefined before `length` bars exist. TradingView documents `ta.percentrank` with the `<=` tie rule; I ran both rules where the tie mattered.
- **rate of change** — `ta.roc(src, n) = 100 * (src - src[n]) / src[n]`, in percent.
- **weighted average** — `sum(w_i * x_i) / sum(w_i)` over the components with a defined `x_i`.

## Worked example A

VIX series, `percentileLookback = 10`:

| bar | vix | previous 10 | count <= current | pct |
|---|---|---|---|---|
| 0-9 | 12,13,11,14,16,15,18,17,19,22 | window not yet full | — | na |
| 10 | 20 | 12,13,11,14,16,15,18,17,19,22 | 9 | **90.0** |
| 11 | 25 | 13,11,14,16,15,18,17,19,22,20 | 10 | **100.0** |

Counted by hand: at bar 10 every previous value except 22 is <= 20, so 9/10 = 90.0. My implementation returns 90.0 and 100.0. The script's `ta.percentrank(vixClose, percentileLookback)` is the standard construction, applied to the right series, with the current bar excluded from its own comparison set — which is the correct choice for an "unusual versus normal" reading and is what the quant pack asks for. **No finding on the percentile construction itself.**

## FINDING 1

```
severity:   CRITICAL
where:      systemic_stress_dashboard.pine:63, :64, :70
claim:      vixPct / corPct / creditPct are "percentile rank ... within its own
            recent history" (header lines 9-14), and guardrail 5 requires missing
            or stale data to render as n/a and never as a plausible value.
actual:     A series with no variance is not guarded anywhere. Re-derived:
              - VIX constant at 18.0 for 300 bars, lookback 252
                  -> vixPct = 100.0
                  -> systemicStress = 100.0
                  -> regimeLabel   = "Stressed", bgcolor red
              - creditRatio exactly constant (HYG and LQD moving identically)
                  -> ta.roc = -0.0, creditRawStress = -0.0
                  -> creditPct = 100.0 under the <= tie rule, 0.0 under <
              - creditRatio economically constant but computed in floats
                (hyg = 80*1.001^i, lqd = 100*1.001^i):
                  rawStress takes 5 distinct values spanning 5.551e-14 percent
                  -- pure IEEE-754 rounding, zero economic content --
                  and creditPct then ranges over 2.0 to 99.6 across the tail,
                  reading 71.03 at the last bar.
impact:     A frozen, halted or holiday-stalled VIX feed reports the MAXIMUM
            stress regime rather than "n/a". The trader sees a red-shaded chart
            and a "Stressed" label produced by a feed that stopped updating.
            The float-noise case is worse still: a credit signal containing
            literally no information publishes a freely-moving, entirely
            plausible 0-100 percentile that nothing marks as unavailable.
            This is exactly the failure guardrail 5 names -- a plausible value
            substituted for a missing one -- and it is invisible on the chart.
expected:   Each percentile is unavailable when its source window has no
            dispersion. A variance/range floor on the lookback window, with the
            result forced to na below it, so fmt() renders "n/a" and the plot
            gaps. Note this is NOT solvable by picking the other tie rule:
            <= yields 100, < yields 0, and both are confident wrong answers.
            The float-noise case is not a tie problem at all and needs the
            dispersion floor to be an absolute one, not a test for exact equality.
```

This is a bug, not a disclosed caveat. The header discloses that the weights, lookback and thresholds are untuned. It says nothing about degenerate inputs, and no reading of "reasonable defaults, not a match to any specific published index" covers a constant series reporting maximum stress.

## FINDING 2

```
severity:   CRITICAL
where:      systemic_stress_dashboard.pine:83
claim:      "Stress Impulse : how much Systemic Stress has moved over the last N
            bars (negative = stress easing, positive = stress building)"
            (header lines 16-17).
actual:     stressImpulse = systemicStress - systemicStress[impulseLen] is a
            difference of two values that need not share a definition, because
            systemicStress is renormalised per bar over whichever components
            happen to be non-na on THAT bar. Re-derived, vixPct = 30, corPct =
            90, creditPct = 30 held flat, weights 1.0/1.0/0.5, COR1M missing for
            exactly one bar (bar 5):
              bar 4: ss = 54.0  "Elevated"   impulse = na
              bar 5: ss = 30.0  "Normal"     impulse = -24.0
              bar 6: ss = 54.0  "Elevated"   impulse =   0.0
            Not one component percentile changed value on any of those bars.
            The same artefact at the warm-up boundary (see FINDING 3): with all
            three percentiles pinned flat, impulse reads -14.0 at bar 272.
impact:     The panel publishes "stress easing hard" -- a 24-point negative
            impulse and a regime flip from Elevated to Normal -- on a single
            missing COR1M print. The trader reading "negative = stress easing"
            concludes conditions improved. Nothing improved; a data cell went
            blank. A one-bar gap in a Cboe index feed is an ordinary event, not
            a pathological one, so this fires in normal operation.
expected:   The impulse is defined only where the composite's basis at bar t and
            at bar t-impulseLen is the same. Either carry the basis (the set of
            contributing components, or sumWeights) alongside systemicStress and
            return na when it differs across the lookback, or difference each
            component percentile and reweight the differences. Until then the
            published number is not "how much Systemic Stress has moved".
```

## FINDING 3

```
severity:   MATERIAL
where:      systemic_stress_dashboard.pine:73-80
claim:      "If it fails to resolve, this script excludes it and re-normalizes
            the remaining weights rather than erroring out" (header lines 21-23)
            -- presented as a safe, lossless degradation.
actual:     The renormalisation IS arithmetically correct as a weighted average
            and IS scale-preserving: over 20,000 random percentile triples across
            all eight na-masks, systemicStress stayed inside [0.0019, 99.999].
            That part is sound and I want it on record as sound.
            What it is not is LEVEL-preserving, and the switch is silent.
            Re-derived at the default lookback 252 / creditRocLen 20, with all
            three percentiles held at their stated values:
              bar 251: vix=na  cor=na  cred=na   -> ss = na    "N/A"
              bar 252: vix=80  cor=80  cred=na   -> ss = 80.0  "Stressed"
              bar 271: vix=80  cor=80  cred=na   -> ss = 80.0  "Stressed"
              bar 272: vix=80  cor=80  cred=10   -> ss = 66.0  "Elevated"
            A 14-point drop and a regime change at bar 272 with no input moving.
            The cause is a warm-up asymmetry the script never accounts for:
            vixPct and corPct are defined from bar 252, but creditPct needs
            creditRocLen (20) bars to form creditRatio's ROC and then 252 more
            to rank it -- 272 bars. For 20 bars the composite is a VIX+COR1M
            average wearing the name of a three-component one.
impact:     The first 20 bars after the composite appears are computed on a
            different basis from every bar after them, and the transition is
            rendered as a real move in systemic stress. On a fresh chart, or
            after any symbol change, that is the most recent history the trader
            has. Downstream it also feeds FINDING 2.
expected:   The composite is unavailable until every component whose weight is
            non-zero is available, or the basis is displayed so the reader can
            see which components are in it. The header's own framing -- exclude
            and renormalise -- is a reasonable convention for a permanently
            missing symbol; it is the wrong convention for a warm-up, where the
            component is not missing, merely not ready yet.
```

Stated precisely against the standing rule on "wrong" versus "differently defined": the weighted average itself is a defensible definition and is implemented correctly. The finding is that the basis changes without being disclosed or marked, which is a documentation-and-availability defect, not an arithmetic one.

## FINDING 4

```
severity:   MATERIAL
where:      systemic_stress_dashboard.pine header lines 21-24, against :64 and :127
claim:      "check the COR1M Percentile cell; if it stays blank, the symbol
            didn't resolve and you may need a different ticker/exchange prefix."
actual:     Three distinct conditions render the COR1M cell as the string "n/a"
            via fmt() at line 127, and the header names only one of them:
              1. the symbol did not resolve (ignore_invalid_symbol = true at :58
                 yields an all-na series) -- the disclosed case;
              2. the symbol resolved fine but fewer than percentileLookback bars
                 of its history exist on this chart -- ta.percentrank undefined;
              3. the symbol resolved and has history, but this particular bar has
                 no print (a feed gap or a session mismatch with the chart symbol).
impact:     The header instructs the reader to conclude "bad ticker" from an
            observation that has two other far more likely causes. A user
            following it will replace a correct CBOE:COR1M with a guessed
            alternative prefix -- which is precisely the ticker-reconstruction
            failure guardrail 3 exists to prevent, induced by the script's own
            documentation. In case 2 and 3 the composite meanwhile silently
            renormalises (FINDING 3) and the impulse fires (FINDING 2), so the
            user sees corroborating "evidence" of a real stress move.
expected:   The header distinguishes the three cases and names the observation
            that separates them (a permanently blank cell across the whole chart
            versus a blank cell only at the left edge versus an isolated blank).
            Better, the cell itself distinguishes them -- "n/a (no symbol)"
            versus "n/a (warming up)" -- which is what guardrail 5's "degrade
            VISIBLY" actually asks for.
```

## FINDING 5

```
severity:   MATERIAL
where:      systemic_stress_dashboard.pine:57-60, and everything downstream
claim:      The header (lines 1-27) makes no statement about repainting at all.
            Guardrail 1 and the quant pack require that a construction which
            repaints says so in the header.
actual:     All four request.security() calls pull `close` at timeframe.period.
            On the forming bar that close is provisional, so on every realtime
            bar vixClose/corClose/lqdClose/hygClose change tick by tick. Every
            value in the panel is therefore provisional too: vixPct, corPct,
            creditRatio, creditRawStress, creditPct, systemicStress, the regime
            label at :86, the regime cell colour at :140 and the red bgcolor at
            :110 all rewrite intrabar and settle only at the close. The table is
            drawn under barstate.islast (:119), i.e. exactly on the bar where
            this is happening, and there is no barstate.isconfirmed guard
            anywhere in the file.
impact:     A regime can read "Stressed" with a red-shaded background at
            11:00 and "Elevated" unshaded at the close of the same bar. On
            historical bars no trace of this remains, so the trader's
            impression of how stable the regime label is comes entirely from
            settled history and is wrong about live behaviour. This is the
            "historical versus realtime disagreement" sense of repainting that
            guardrail 1 is about, and it is separate from the lookahead question
            in FINDING 6.
expected:   Not necessarily a code change -- a dashboard showing the live
            provisional state is a legitimate design, and the quant pack says
            so. What is required is that the header says it: that the current
            bar's readings are provisional and settle at the close. Per the
            pack's grading, MATERIAL because a displayed value misleads; it
            would be CRITICAL if an alert or a backtest depended on it, and
            neither does -- recon confirmed there is no alert() or
            alertcondition() and no strategy() in this file.
```

## FINDING 6

```
severity:   MINOR
where:      systemic_stress_dashboard.pine:57, :58, :59, :60
claim:      Guardrail 1: "request.security() passes lookahead=barmerge.lookahead_off
            explicitly."
actual:     None of the four calls passes a lookahead argument. This is what the
            order's verification command reports, four times, and it is why
            --strict exits 1:
              :57 SHOULD_FIX P008  :58 SHOULD_FIX P008
              :59 SHOULD_FIX P008  :60 SHOULD_FIX P008
            On the mathematics I want to be exact rather than alarming: every
            call requests timeframe.period, the chart's own timeframe, so there
            is no higher timeframe to look ahead into and lookahead_on and
            lookahead_off would be observably identical here. There is no actual
            forward-looking repaint from this. The repaint that does exist in
            this script is FINDING 5, and adding lookahead_off will not fix it.
impact:     The script fails the repo's mandated static check, so no build lane
            touching it can close with verification PASS, and the integration
            gate will report it. Graded MINOR because no published number is
            wrong because of it.
expected:   lookahead = barmerge.lookahead_off on all four calls. Guardrail 1
            asks for the intent on the page, not merely for the right runtime
            default, and this is a one-word change per line.
```

## FINDING 7

```
severity:   MINOR
where:      systemic_stress_dashboard.pine:44-46 (weights), :48-50 (thresholds)
claim:      systemicStress is a 0-100 composite (it is plotted against hlines at
            25/50/75 and bucketed into four named regimes), and the four regime
            bands partition it.
actual:     Neither input group has minval/maxval, and nothing checks ordering.
              - negative weight: wVix=-1, wCor=1, wCredit=0.5 with vixPct=10,
                corPct=90, creditPct=90 gives sumWeights=0.5 and
                systemicStress = 250.0 -- off the pane, off the hline scale,
                permanently "Stressed".
              - mis-ordered thresholds: calmMax=60, normalMax=50, elevatedMax=75
                makes "Normal" unreachable. Re-derived: ss=10, 30 and 55 all
                return "Calm"; ss=70 returns "Elevated". No error, no warning,
                and the three hlines still draw at 60/50/75 in the wrong order.
            All-zero weights are handled correctly: sumWeights=0 fails the
            `sumWeights > 0` test at :80 and the panel reads "N/A". That guard
            is right and should stay.
impact:     A user tuning the panel -- which the header actively invites -- can
            silently reach a configuration where a regime never fires or the
            composite leaves its own scale. Nothing on the chart says so.
expected:   minval=0 on the three weights; and either minval/maxval 0-100 plus a
            runtime ordering check on the thresholds (runtime.error, or a visible
            "thresholds mis-ordered" cell), or the bands derived from a sorted
            copy of the three inputs.
```

## FINDING 8

```
severity:   MINOR
where:      systemic_stress_dashboard.pine header, against :33-36
claim:      Guardrail 3, third clause: a symbol not confirmed against
            TradingView's own symbol search "must be an input.symbol() the user
            can correct, must handle non-resolution as visible n/a, and must be
            flagged as unverified in the header."
actual:     Clauses one and two are satisfied and satisfied well -- all four are
            input.symbol() at :33-36, and ignore_invalid_symbol = true plus the
            na-guards plus fmt()'s "n/a" give visible non-resolution. The third
            clause is unmet for all four. The header says COR1M "may not be
            available on your TradingView plan/exchange feed", which is a
            statement about entitlement, not a statement about whether the
            ticker string was confirmed. TVC:VIX, AMEX:LQD and AMEX:HYG carry no
            statement of any kind.
impact:     A reader cannot tell whether these four strings were confirmed or
            typed from memory. Compare mm_cot_long_short_index.pine, which says
            outright that its tickers were reconstructed from search results and
            not confirmed -- project.md calls that the repo's most valuable
            habit, and this file does not follow it.
expected:   One line per symbol in the header stating confirmed or unconfirmed,
            and by what. If they were confirmed, say so and say how; if they
            were not, say that, which is the more useful admission.
```

I did not attempt to settle the ticker identities myself and I am not claiming any of them is wrong. This lane has no browser and TradingView's symbol search is the only authority; per the order's non_goals I am reporting that I could not, rather than guessing. The finding is about the header's silence, which I can observe directly.

## What re-derived clean

Stated explicitly so that a fix for the findings above does not disturb these, and so the PASS-able parts of this script are on record.

**creditRawStress sign is correct.** The header claims a falling HYG/LQD ratio reads as rising stress. Re-derived with LQD flat at 100 and HYG declining 0.5/bar, creditRocLen=5: at bar 20 the ratio is 0.7450 against 0.7700 five bars earlier, `ta.roc` = -3.2468 (negative, ratio falling), and the negation at :69 gives creditRawStress = +3.2468 (positive, stress rising). The composition of `ta.roc` with the unary minus does what the comment at :66-67 says. `ta.percentrank` at :70 is monotone in its input, so the sign survives into creditPct. **No finding.**

**Regime bands partition [0,100] with no gap and no overlap** at the default 25/50/75, given the thresholds are ordered. Re-derived across the boundaries:

| systemicStress | regimeLabel |
|---|---|
| 0, 24.999 | Calm |
| 25, 25.001, 49.999 | Normal |
| 50, 74.999 | Elevated |
| 75, 75.001, 100 | Stressed |

Every band is half-open `[lower, upper)`, the four are contiguous, and the strict `<` at :88, :89 and :90 is the right operator at each step. `regimeColor` at :91-94 uses the identical ladder, so label and colour cannot disagree. The `bgcolor` at :110 fires on `systemicStress >= elevatedMax`, which is the exact complement of `< elevatedMax` and therefore lights precisely on "Stressed" and nowhere else. The three `hline` labels name their boundaries correctly ("Calm / Normal" at calmMax, and so on). **No finding** beyond the missing ordering validation already raised as FINDING 7.

**The renormalisation preserves the 0-100 scale.** Over 20,000 random percentile triples crossed with all eight na-masks at the default weights, systemicStress stayed within [0.0019, 99.999] and never left the range its plot, its hlines and its regime bands assume. The `sumWeights > 0 ? ... : na` guard at :80 correctly produces na rather than a division by zero when every component is missing or every weight is zero. The double na-guard at :78 (`na(vixPct) ? 0.0 : vixPct * wVixEff`) is redundant given wVixEff is already 0 in that case, but it is harmless and not a finding. FINDING 3 is about the level and the silence, not about this.

**The percentile construction matches its standard definition** and excludes the current bar from its own comparison window — see § Worked example A.

**The impulse sign matches the header.** `systemicStress - systemicStress[impulseLen]` is positive when stress has risen over the lookback, which is what "positive = stress building" states. FINDING 2 is about the basis, not the sign.

**Table geometry is sound.** `table.new(..., 2, 6, ...)` at :113-115 against a maximum of six rows used when showComponents is true (0-5) and five when it is false. No overflow.

**The quant pack's sign-convention rule is satisfied.** The pack requires an index that rises when conditions worsen to be labelled as an inversion. Here the name "Systemic Stress", the four regime labels and the header's "negative = stress easing, positive = stress building" all label it. **No finding.**

## Repaint analysis

Required in every artifact that touched a computed series. Walking the quant pack's table against this construction:

| Pattern | Present? |
|---|---|
| Higher-timeframe value used before that timeframe's bar closes | **No.** All four `request.security` calls use `timeframe.period`, the chart's own timeframe. There is no higher timeframe involved, which is also why the missing `lookahead` argument (FINDING 6) is textually a guardrail breach but numerically inert. |
| `ta.pivothigh` / `ta.pivotlow` plotted at the pivot bar | **No.** Neither appears in the file. |
| A threshold computed from a window that includes the current, unclosed bar | **Partially, and this is FINDING 5.** `ta.percentrank` excludes the current bar from its comparison window, which is correct — but the value being ranked is the current bar's provisional close, so the rank itself moves intrabar. The regime thresholds are constant inputs and do not move. |
| `ta.valuewhen` on a repainting condition | **No.** Not used. |
| An alert not guarded by `barstate.isconfirmed` | **Not applicable.** No `alert()` and no `alertcondition()` in the file. This is why FINDING 5 is MATERIAL rather than CRITICAL. |
| `strategy.entry` on an intrabar condition with `calc_on_every_tick=true` | **Not applicable.** This is an `indicator()`, not a `strategy()`. Guardrail 4 does not apply to it. |

Conclusion: this script repaints in exactly one way — the last bar's readings are provisional and settle at the close — and the header does not say so. Per the pack, the finding is not that it repaints but that it repaints undisclosed. FINDING 5.
