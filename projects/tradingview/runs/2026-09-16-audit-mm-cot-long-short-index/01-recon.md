REPORT 2026-09-16-audit-mm-cot-long-short-index/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Order's verification field was NONE; recon is read-only per non_goals (no pine_check.py run).

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Quant-audit should independently verify whether "COT Index" min-max rescale (lines 43-49) matches a named published methodology, since the header cites no specific source (book/paper/analyst) — see § Header claims.
  - Quant-audit / integration should check whether omitting explicit `lookahead=` on `request.security()` (lines 39-40) is safe given `"W"` is requested against an unknown chart timeframe — see § Data timing and repaint surface.
  - Any downstream fix to the symbol/header should preserve, not delete, the existing "reconstructed, unconfirmed" admission per project.md's header contract, until someone actually re-verifies the symbol in TradingView's symbol search.

risks:
  - I have not run TradingView's symbol search, so I cannot state whether `COT2:088691_F_MMP_L_OLD` / `_S_OLD` actually resolve today — the header itself says this was never confirmed, and I have no tool to confirm it either.
  - I cannot verify Pine v6's *default* `lookahead` for `request.security()` on a higher timeframe than the chart — that's a runtime fact needing a compiler, not inferable from script text alone. Flagged in § Guardrail observations as an observation, not a verdict, per non_goals.

## Orchestrator brief

- Header claims: no single named source for the "COT Index" min-max rescale; header self-admits both COT2 symbols were reconstructed, not confirmed.
- Symbol handling and Gold-goal fit: `input.symbol()` satisfies guardrail 3 mechanically; default `088691` targets Gold per the header's own (unverified) CFTC-code claim.
- Data timing and repaint surface: no explicit `lookahead=` on the weekly `request.security()` calls; timing relies solely on Pine's own `"W"` semantics, no `isconfirmed` gating.
- Index calculation as written: rolling min-max rescale of MM long/short positions to -100..100 over `lookbackWeeks`; recorded for quant-audit, not evaluated here.
- Guardrail observations (recon-level, not verdicts): 1 unattributed default lookahead, 2 no named source, 3 self-disclosed unverified symbols, 4 n/a (indicator, not strategy), 5 satisfied, 6 satisfied.

## Header claims

- **What it computes** (`mm_cot_long_short_index.pine:19-26`): a "Long/Short Index" that is *not* the raw Managed Money position size, but where the current position sits within its own rolling min/max range over `lookbackWeeks`, rescaled to -100..+100. +100 = at the top of its recent range for that side; -100 = at the bottom.
- **Declared source** (`:24-26`): "This is standard 'COT Index' methodology (a stochastic-style oscillator on positioning), popularized by several COT analysts." No single named source (no specific book, paper, analyst name, or spec) is cited — it names a category of prior art ("several COT analysts") rather than one traceable authority.
- **What it admits is unverified** (`:6-17`): the header states, in an "IMPORTANT — VERIFY THE SYMBOLS BEFORE TRUSTING THIS" block, that the exact TradingView ticker for "Managed Money Positions - Long/Short" was *reconstructed from search results, not confirmed* by opening the live TradingView symbol page, because "my usual double-check tools were unavailable when this was written." It gives the reader explicit remediation steps (search CFTC code "088691" in the symbol input, look for COT2-prefixed "Managed Money Positions - Long/Short" entries, and notes an unresolved symbol shows as "n/a" in the table).
- The header does not separately flag `lookbackWeeks` (156) as an unverified/feel-based parameter, though it does note in the input tooltip (`:36`) that "some analysts use 52 (1yr) or 260 (5yr)" as alternatives, implying 156 is a convention choice rather than a derived/sourced number.

## Symbol handling and Gold-goal fit

- Inputs (`:32-33`): `mmLongSymbol` defaults to `"COT2:088691_F_MMP_L_OLD"`, `mmShortSymbol` defaults to `"COT2:088691_F_MMP_S_OLD"`, both declared via `input.symbol(...)`, so both are user-editable in the indicator's settings (satisfies the "must be an `input.symbol()` the user can correct" clause of guardrail 3, independent of whether the symbol itself later proves correct).
- CFTC code `088691` is stated in the header (`:9-10, :12`) to be "Gold's CFTC code." The header's own remediation instructions (`:12-13`) explicitly tell the reader to search "088691" for Gold. Taken together with the default symbols, the script's **current default does target Gold** Managed Money long/short positioning — it is not hardcoded to a different, unrelated commodity.
- This default-to-Gold claim rests entirely on the header's self-reported CFTC code and the unconfirmed COT2 ticker reconstruction (see § Header claims); I did not independently verify against CFTC's published contract-code table or TradingView's symbol search, and neither tool is available to me as a Bash-less recon lane.
- The tooltip on `lookbackWeeks` (`:36`) states "For a different commodity/future, look up its CFTC code ... and search for that code instead" — confirming the script is designed to be portable beyond Gold, with Gold only as the shipped default.

## Data timing and repaint surface

- The only "new report" trigger in the script is the `request.security(mmLongSymbol, "W", close, ignore_invalid_symbol = true)` / `request.security(mmShortSymbol, "W", close, ignore_invalid_symbol = true)` pair (`mm_cot_long_short_index.pine:39-40`). There is no day-of-week check, no bar-count offset, and no `barstate.isconfirmed` gating anywhere in the file.
- The comment directly above (`:38`) states the intent: "COT is weekly — pin to W regardless of chart TF." The mechanism for "pinning" is purely the `"W"` timeframe string argument to `request.security()`; the script relies entirely on Pine's own `request.security()` semantics to align COT-report cadence with weekly bars, rather than any bespoke gating logic in this script.
- Neither call passes a `lookahead` argument — only `ignore_invalid_symbol = true` is set (`:39-40`). No `lookahead=barmerge.lookahead_off` (or `_on`) appears anywhere in the file.
- `ignore_invalid_symbol = true` means an unresolved symbol returns `na` rather than raising a runtime error; the script's downstream `na(mmLongPos)` / `na(mmShortPos)` checks (`:45, :49`) and the table's `fmtPos`/`fmt` helpers (`:61-62`) render that as the literal string `"n/a"` in the on-chart table rather than silently substituting a value.
- No other timing mechanism (e.g. `request.security(..., barstate.isconfirmed)`, session/day checks, or manual bar-offset math) exists in the file — the entire "is this the latest published COT report" question is delegated to Pine's own weekly-timeframe `request.security()` resolution.

## Index calculation as written

(Recorded for downstream quant-audit; not evaluated for correctness here per non_goals.)

- `longMin`/`longMax` = `ta.lowest`/`ta.highest` of `mmLongPos` over `lookbackWeeks` (`:43-44`); `longIndex` = `na` if `mmLongPos` is `na` or `longMax == longMin`, else `(mmLongPos - longMin) / (longMax - longMin) * 200 - 100` (`:45`).
- Same pattern independently for `shortIndex` from `mmShortPos` (`:47-49`) — long and short sides are ranked against their own independent rolling ranges, not against each other or a combined long-minus-short series.
- Plots: `longIndex` in green, `shortIndex` in red (`:52-53`), with reference lines at 0 (midpoint), +80 ("Long Extreme (crowded)"), -80 ("Short Extreme (crowded)") (`:54-56`). The ±80 "crowded" threshold levels are not attributed to any named source in the header or inline.
- The on-chart table (`:59-77`) shows raw `mmLongPos`/`mmShortPos` alongside the computed indices, each rendering `"n/a"` when the underlying series is `na` (satisfies guardrail 5's "degrade visibly" requirement in this specific rendering path).

## Guardrail observations (recon-level, not verdicts)

- **Guardrail 1 (no repainting):** `mm_cot_long_short_index.pine:39-40` — `request.security()` is called without an explicit `lookahead=` argument, whereas project.md's guardrail 1 states the convention is "`request.security()` passes `lookahead=barmerge.lookahead_off` explicitly." Whether the Pine v6 default behaves equivalently to `lookahead_off` when requesting a `"W"` series against an arbitrary (likely sub-weekly) chart timeframe is a runtime fact I could not verify without a compiler; flagged as an observation only.
- **Guardrail 2 (formula traceability):** `mm_cot_long_short_index.pine:24-26` — the header attributes the index formula to "standard 'COT Index' methodology... popularized by several COT analysts" rather than one named source (book/chapter, paper, or spec), which is looser than the guardrail's "traces to a named source" language; the header does not instead declare it an "original construction" either — it sits between the two stated options.
- **Guardrail 3 (verified symbols):** `mm_cot_long_short_index.pine:6-17` — the header itself states the symbols were reconstructed from search results, not confirmed against TradingView's live symbol page; this is the guardrail's own example failure mode, self-disclosed rather than hidden. The script does satisfy the guardrail's *mechanical* requirements (`input.symbol()`, `ignore_invalid_symbol` producing visible `n/a`), leaving only the underlying confirmation step outstanding.
- **Guardrail 4 (costs declared):** not applicable — this file is an `indicator()`, not a `strategy()` (`mm_cot_long_short_index.pine:29`), so no commission/slippage declaration is expected here.
- **Guardrail 5 (degrade visibly):** satisfied in the observed code paths — `na` positions flow through to `"n/a"` in the table (`:61-62, :66, :69, :72, :76`) rather than being substituted with a prior or plausible value.
- **Guardrail 6 (no execution):** satisfied — the script only calls `indicator()`, `plot()`, `hline()` and `table.*`; no `strategy.entry`/`strategy.order`/alert-to-webhook construct appears anywhere in the file.
