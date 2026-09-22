# Platform research — 2026-09-18-vertical-volume-indicator

Written by the orchestrating session, not a dispatched lane, at the same
structural position `compile.md` occupies (project.md § "Why this project is
unusual"): no lane in this project's roster holds WebSearch/WebFetch, so this
external technical-feasibility lookup — recommended by `01-product.md` §
"Sequencing and the external-research gap" — happens here and is written down
so a downstream `quant` RESEARCH order can cite it as a sourced `inputs` path
rather than being asked to verify it itself.

## 1. TradingView already has a native Volume Profile tool matching the description

"Indicators" → "Volume Profile" → **Visible Range**, **Fixed Range**, **Session
Volume**, or **Periodic Volume Profile**. All four render as a horizontal
histogram anchored to the price axis at the right edge of the chart — taller
bars where more volume traded at that price, shorter where less — exactly the
"vertical, bottom is the right side of the screen" shape the trader described.
Includes Point of Control (the single highest-volume price level) and a Value
Area (the shaded high-activity band). This is a chart tool, not a script — no
Pine required, nothing to build, applies to any symbol immediately.

Source: [Volume profile indicators: basic concepts — TradingView](https://www.tradingview.com/support/solutions/43000502040-volume-profile-indicators-basic-concepts/)

## 2. A custom Pine v6 script *can* also build this, with a known accuracy ceiling

Pine's native per-bar data is OHLC plus one aggregate volume number — no
within-bar price distribution. Two ways a script gets closer:

- **`request.security_lower_tf()`** — pull lower-timeframe bars inside each
  bar, bucket their closes by price, accumulate volume per bucket, render with
  `box.new()`/`line.new()`. This is an *estimate* from lower-timeframe candles,
  not real tick data, and it is not exact — "accurate mode gets close; it will
  never be tick-perfect." It also falls back to a cruder method on bars beyond
  TradingView's intrabar history limit.
- **`request.footprint()`** — a newer, purpose-built v6 API for intrabar
  volume/order-flow data (splits, delta, POC/VAH/VAL) without the
  lower-timeframe workaround.

Either path is a genuine approximation, not the same fidelity as the native
tool (which TradingView computes server-side from its own tick data). Relevant
to guardrail 5 (degrade visibly) if a custom build is chosen: the header would
need to say plainly that it's a candle-derived approximation.

Sources: [Volume footprints are now available in Pine scripts — TradingView Blog](https://www.tradingview.com/blog/en/volume-footprints-in-pine-scripts-56908/) ·
[mervinj3546/volume-profile — GitHub](https://github.com/mervinj3546/volume-profile)

## 3. "VSA Wyckoff Volume" and "volume profile" are not the same category of tool

A VSA/Wyckoff volume indicator — what the trader currently uses — classifies
each *time-axis* bar (the ordinary bottom-of-chart histogram) by the
relationship between volume, price spread and close position: Demand /
Supply / No Demand / No Supply / Stopping Volume / Absorption / Buying or
Selling Climax, etc. It answers "what does this bar's volume mean." A volume
profile answers a different question — "at which *prices* did volume trade" —
and says nothing about VSA's demand/supply classification.

So the trader's two statements — "show volume vertically, right side of
screen" and "better than my VSA Wyckoff indicator" — may describe two
different upgrades that don't obviously combine into one script: a profile
render is not a replacement for a VSA-style signal, and a better VSA-style
signal would not look like a profile. This is exactly `01-product.md`'s Open
decision 1, now with a concrete reason behind it rather than just the
question.

Source: [Volume Spread Analysis 2026 — Tom Williams VSA Guide](https://takeprofitapp.com/en/learn/volume-spread-analysis-vsa)

## 4. Addendum, 2026-09-18: resolving 02-quant.md § Unpinned API details, item 1

`02-quant.md` flagged an open risk: if `request.security_lower_tf()`'s
degradation past TradingView's intrabar limit is *silent* (a populated but
coarser array, rather than `na`), the brief's coverage counter `C` (bars for
which intrabar data was returned at all) cannot detect it, and guardrail 5
would not be met by detection alone.

Further web research resolves the mechanism, and refines the risk rather than
retiring it:

- **The limit is a shared budget, not a per-bar cliff.** Scripts can retrieve
  up to 100,000 intrabars total (Basic/Essential/Plus/Premium plans), 125,000
  (Expert) or 200,000 (Ultimate) — governed by the `calc_bars_count` parameter
  (default 100,000 if unspecified). This is one pool shared across every chart
  bar the request covers, not a fixed per-bar allowance.
- **When a request would exceed the budget, there is a trade-off between
  intrabars-per-bar and chart bars covered** — TradingView reduces precision
  (fewer intrabars analyzed per chart bar) to keep covering the full requested
  range, rather than dropping specific bars to `na`. Exact behaviour (does it
  bias toward recent bars, older bars, or degrade uniformly?) was not found in
  a form specific enough to cite.

**What this means for the brief's coverage diagnostic**: a binary "did bar `i`
return any intrabar data" check, as specified, would likely read `C = M`
(fully covered) even on a request that silently degraded from ~78
intrabars/bar to a handful — because *some* data still came back for every
bar. That is exactly the plausible-looking-wrong output guardrail 5 exists to
catch.

**Recommended refinement for the build lane**: in addition to `C of M bars
covered`, track and display the **realised intrabars-per-bar** (via
`array.size()` on the returned array, averaged or min'd over the window) against
`02-quant.md`'s own target band (50–100 intrabars/bar, § Data requirements).
A bar realising materially fewer than the target is degraded precision, not
full coverage, and should be reflected in the diagnostic even when `C` alone
would read as fully covered. This is a refinement of the brief's existing
diagnostic, not a new construction — it does not touch the formula quant
specified (binning, normalisation, window) and does not require another
research round.

Source: [Concepts / Other timeframes and data — TradingView Pine Script docs](https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/)

## Dated caveat

Current as of 2026-09-18, from public web sources, not TradingView's own Pine
reference manual read line-by-line. Re-verify `request.footprint()`'s exact
signature and any object-count limits against the official Pine v6 reference
before writing a `quant` RESEARCH order that depends on it.
