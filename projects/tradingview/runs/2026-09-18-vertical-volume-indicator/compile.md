# Compile check — 2026-09-18-vertical-volume-indicator

Run in the main session, driving TradingView's browser editor, per
project.md § "Why this project is unusual" and phases.md § "Where the
compile check sits" — this is the one thing the orchestrating session does
that looks like lane work and is not: no agent in this project's roster
holds browser tools, so this step happens here.

## Attempt 1 — 2026-09-18, FAIL

**Method**: `volume_profile.pine` (post-CR-1, post-08-integration — the
version with the na-skip fix) pasted into a fresh TradingView Pine Editor
buffer via the clipboard method (`docs/testing-methodology.md`): hidden
textarea populated via JS, real trusted `Ctrl+C`, verified byte-for-byte in a
second hidden textarea before pasting (24,859 chars, exact match), then real
`Ctrl+A`/`Ctrl+V` into the editor. Editor showed 395 lines after paste,
matching the file — no indentation corruption.

Clicked "Add to chart" (compiles + runs).

**Result: compile error, 1 of 1 problem.**

```
Error at 210:10
Arrays of type array are not supported. (CE10022)
```

Line 210 is:

```pine
var array<array<float>> closesQueue = array.new<array<float>>()
```

**Root cause**: Pine v6 does not support nested typed arrays
(`array<array<T>>`). This script declares three such variables —
`closesQueue`, `volsQueue` (both `array<array<float>>`) — to hold, per bar in
the rolling window, the lower-timeframe intrabar close/volume arrays
`request.security_lower_tf()` returns. That representation does not compile
at all; the script never reaches "start", so nothing downstream of this line
(the binning loop, the na-skip fix, the diagnostics table) has ever actually
run in TradingView.

**This confirms a risk flagged, but not resolved, at every prior stage**:
03-backend.md § risks named `array<array<float>>` explicitly as "a standard
v6 pattern per training but none compiled live" — the honest disclosure this
project's convention asks for. 04-quant-audit.md and 07-quant-audit.md both
independently re-derived the code's *logic* in Python and confirmed it
correct against the worked example, but neither audit — nor the integration
gate, which is a text-pattern checker (`pine_check.py`), not a compiler —
could have caught this, because it is not a logic error. It is exactly the
class of failure this project's three-layer verification model
(`docs/testing-methodology.md`) says only the live compile check can catch:
"the script actually loads" is a claim only TradingView's own compiler can
settle.

**Disposition**: BLOCKING. The run is not closing on this state. See
`cr/CR-2.md` — dispatched to backend to replace the nested-array
representation with a Pine v6-supported structure (flat arrays + per-bar
length bookkeeping, or an equivalent the implementer chooses), preserving
the formula, the window semantics and the na-skip fix exactly. Re-verification
required: quant-audit (delta, since the data representation the window/binning
logic reads from is changing) and integration (repo-wide static check), both
before the next compile attempt.

**A second finding surfaced by the delta re-audit, before any further compile
attempt**: 11-quant-audit.md § FINDING 8 (MATERIAL) — two array-clearing
loops (`profileBoxes`/`profileLabels`) would iterate backwards on an empty
`var` array on every chart's first render, per Pine's documented `for`-loop
direction inference (`start > end` counts down, not zero times). This was
masked by CE10022 aborting the script before any bar had ever executed, so
this run had never actually reached this code live either. Fixed via CR-3
(`cr/CR-3.md`, `12-backend.md`) before the next compile attempt — the same
guard pattern already correct at three other sites in the file.

## Attempt 2 — 2026-09-18, PASS

**Method**: same clipboard method, same buffer, re-populated with the
current file (post-CR-2, post-CR-3; 436 lines, 27,418 chars, verified
byte-for-byte before paste). Pasted into the same Pine Editor instance
already added to a chart from Attempt 1 (its "Add to chart" button had
become an "Update on chart" sync icon, since the script — despite never
compiling — had already been added as a chart instance); clicked that sync
icon rather than re-adding a second instance.

**Result: "Updated on chart." — no error.** This is the first time this
script has ever actually executed in TradingView; every prior state (Attempt
1, plus everything CR-1's fix and both quant-audit passes verified before
Attempt 1) had never run live.

Chart: SPX, Daily, `lookbackBars = 120` (default), auto LTF = 5 minutes
(default, per the chart timeframe being Daily-and-above). Diagnostics table
read directly off the rendered chart (zoomed screenshot, not OCR'd from a
description):

| Row | Value |
|---|---|
| Window (bars, M of N) | 120 of 120 |
| Coverage (C of M) | 120 of 120 |
| Intrabars/bar (avg) | 79.525 (target 50-100) — no DEGRADED flag |
| LTF used | 5 |
| Reconciliation (Σ bins / Σ volume) | 0.9918 — no CHECK flag |
| POC price | 7410.51 |
| POC raw volume | ~55,413,639 |
| Status | OK — bare, no na-skip note, no PROVISIONAL |

Profile boxes (the price-anchored horizontal histogram) rendered visibly at
the right edge of the chart. Console checked for `Study|Invalid|error`: no
script-specific runtime error (two unrelated browser-extension messaging
exceptions, not TradingView/Pine errors).

**This satisfies header falsification check #1** ("Reconciliation" row must
read ~1.00): 0.9918 is inside the ±0.02 tolerance the script itself defines
for the `CHECK` flag, on 120 bars of real SPX daily data with full coverage
and no na-skips. Falsification checks #2 (compare against TradingView's
native Fixed Range Volume Profile) and #3 (closing-auction concentration)
were not run in this session — they are comparative/visual checks the
trader can run at their own pace on their own instruments, not a compile-check
blocker; noted at close-out as follow-up the trader may want to do.

**Disposition: PASS.** The script loads, compiles, resolves its own
(chart-symbol, lower-timeframe) data request, and computes a sane, correctly-
degrading result on real data. Nothing was saved to the TradingView account
at any point in this run — every attempt used a fresh, unsaved editor buffer,
per `docs/testing-methodology.md` § "Experimenting safely".
