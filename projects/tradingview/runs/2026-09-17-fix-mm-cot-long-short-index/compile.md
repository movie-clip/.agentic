# TradingView compile check — mm_cot_long_short_index.pine

Run by the orchestrator (main session, browser automation) on 2026-09-17,
against the final state of `mm_cot_long_short_index.pine` after dispatch 13
(integration PASS, round 2). This is the project's acceptance command —
no lane in this network holds browser tools, so nothing else in the run
verifies that the script actually loads and computes in TradingView's own
editor.

## Method

1. Opened TradingView's Pine Editor on a live chart (personal account,
   layout "Main"; nothing was saved to the account at any point — every
   edit below is a local, unsaved editor/session state).
2. Pasted the exact current contents of `mm_cot_long_short_index.pine`
   (163 lines, byte-identical to the repo file) via a real clipboard
   copy/paste (`Ctrl+C`/`Ctrl+V`), which preserves indentation exactly —
   Monaco's own auto-indent corrupts multi-line indentation when text is
   inserted via simulated typing or `execCommand('insertText')`, so paste
   was the only reliable path for a script this size.
3. Clicked "Add to chart" / "Update on chart" and read the browser
   console and the indicator's own error state for compiler/runtime
   errors.

## Result: PASS

- **Compiles.** Every version of the script tested — including the three
  intermediate, now-superseded symbol strings below — reached the "start"
  stage, which only happens after successful Pine compilation. No syntax
  error was ever observed at any point in this run's testing.
- **Runs and computes a real value.** With the final symbol defaults
  (`088691_F_MMP_L` / `088691_F_MMP_S`, bare, no exchange prefix, no
  suffix), the indicator started with **zero console errors** and the
  chart legend showed `MM COT Long/Short Index  65.80` — a live, computed
  net-COT-index reading, not `n/a` and not an error state. Confirmed
  twice: once immediately after applying the final script, and again
  after explicitly re-selecting both symbols through TradingView's own
  "Change symbol" picker inside the indicator's settings dialog and
  clicking OK.

## What this compile check itself found and fixed

The mandatory compile step did more than confirm success — it caught a
real bug the static checker and the quant-audit gate could not:

| Symbol string tried | Result |
|---|---|
| `COT2:088691_F_MMP_L_ALL` / `COT2:088691_F_MMP_S_ALL` (original) | `start failed, Invalid symbol, COT2:088691_F_MMP_S_ALL` |
| `COT:088691_F_MMP_L` / `COT:088691_F_MMP_S` (round 1 fix, prefix only) | `start failed, Invalid symbol, COT:088691_F_MMP_S` |
| `088691_F_MMP_L` / `088691_F_MMP_S` (final, bare) | No error. Computes a real value. |

Independently confirmed via TradingView's own live symbol search (not
just a compile attempt): searching `088691_F_MMP_L` / `088691_F_MMP_S`
returns them as the top results, described as "G(Old) - COMEX - Futures -
Managed Money Positions Long/Short (All)" — the "(All)" is descriptive
prose in the search UI, not part of the ticker; only the `_OLD` and
`_OTHER` crop-year sub-breakouts take an explicit suffix, and Gold has no
crop year, so neither applies. Applying each bare symbol directly as a
chart's primary series also loaded real, live price/data.

This is a genuine upgrade to guardrail 3 for this script: the symbols are
now **confirmed** to resolve, not merely reasoned from CFTC's report
structure. `run.md`'s `## Closed` table and `docs/mm-cot-long-short-index.md`
record this; see run.md's `## Replans` v3/v4 rows for the two extra
dispatches this finding cost.

## What this does NOT confirm

- Behaviour across chart timeframes above weekly (the `tfTooCoarse`
  degrade path, CR-1's fix) was not separately re-exercised on a live
  monthly chart in this session — it was verified by 08-quant-audit.md's
  independent hand-derivation, not by this compile check.
- Long-run behaviour (does the weekly array actually accumulate correctly
  over months of real bars) is not something a single "add to chart"
  moment can show — it needs time or a longer loaded history, which was
  not attempted here.
- Whether TradingView's own COT2 data feed is genuinely CFTC's official
  Disaggregated report data (as opposed to some other vendor's
  reconstruction) is outside what a symbol-resolution check can tell you;
  that trust sits with TradingView's own data licensing, unchanged by
  this run.

## Cleanup

The indicator was removed and the Pine Editor content discarded after
testing. No chart layout was saved at any point — the account's real
"Main" layout is unchanged by any of this run's browser exploration.
