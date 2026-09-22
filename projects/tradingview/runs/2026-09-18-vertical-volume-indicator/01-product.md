REPORT 2026-09-18-vertical-volume-indicator/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only planning artifact; order's verification field was NONE and this lane holds no Bash-runnable check for a brief

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - verdict: needs research first, not yet buildable — see § Placement and § Sequencing and the external-research gap
  - open decision: what "better than VSA Wyckoff Volume" means, and whether the ask replaces or supplements it — see § Open decisions
  - open decision: Pine v6's data-access and TradingView's native tooling are unresearchable by any lane in this roster (no WebSearch/WebFetch anywhere) — see § Sequencing and the external-research gap
  - already covered: nothing — no script or prior artifact occupies volume territory — see § Already covered
  - quant question, deferred until the open decisions above resolve — see § Research questions for quant

risks:
  - I have not verified Pine v6's actual data-access model (whether a script can read volume distributed by price at all, vs. only aggregate bar volume) or TradingView's native Volume Profile tooling — I flag this as unverifiable by any lane here rather than asserting an answer.
  - I have not seen the "VSA Wyckoff Volume" community indicator's source or behaviour; the brief treats the trader's dissatisfaction with it as unverified context, not a diagnosis.
  - I am relying on the hypothesis in my work order (volume-by-price rendering) as the most likely reading of "goes vertically, bottom is right side of screen" — this is language for a market/volume profile, but I have not asked the trader to confirm it, per the order's own instruction to treat it as a hypothesis, not a premise.

## Orchestrator brief
- verdict: needs research first — no script or prior decision covers this; a real formula/rendering question sits underneath, and part of it is external to what any lane here can check
- epic/placement: n/a — project has no epic tree (flat backlog per product.md § Delivery model); nearest precedent scripts named in § Placement, neither a sibling
- 0 stories, 0 scripts proposed yet — premature before scope is known (one script vs. two; rendering vs. signal)
- blocks dispatch: (a) human answers § Open decisions; (b) external technical-feasibility research happens outside the lane roster before quant RESEARCH is usefully dispatched — see § Sequencing and the external-research gap
- sections below: Placement · Already covered · Sequencing and the external-research gap · Open decisions · Research questions for quant · Non-goals for this stage

## Placement
This project carries no epic tree — product.md § Delivery model: "Request → script. There is no PRD and no epic tree here; the backlog is the set of scripts that exist plus the ones the trader wants next." So placement here means: which existing script, if any, is this a sibling of, and precedent for how a genuinely new script gets framed.

Neither existing script is a sibling. `mm_cot_long_short_index.pine` (positioning/sentiment from CFTC COT data) and `strategy13_trend_carry.pine` (trend-following position sizing) do not touch volume-by-price at all. `systemic_stress_dashboard.pine` is the nearest precedent in *kind* — it is an original construction with no external formula to reproduce, which is the precedent for how this repo handles "no published spec to follow, so the header must say so." I independently confirmed the inventory: grep for "volume" across all three `.pine` files returns exactly one hit, a book-citation comment in `mm_cot_long_short_index.pine` ("Book-level citation only... I have not opened either volume to cite a chapter") — a reference to a printed volume, not trading volume. Nothing in the repo computes or displays traded volume today, matching product.md § "What the repo already has": "Nothing yet occupies the volume territory... a volume request is genuinely new work; do not force it into one of these three." This is well inside the trader's stated main interest (product.md § "Who this is for": "the standing research question... is analysing volume to understand when to open or close positions"), so it is a high-value slot to get right rather than rush.

## Already covered
- No `docs/backlog.md` exists to check against (confirmed via file search).
- No prior run under `.agentic/projects/tradingview/runs/` mentions volume-by-price, market profile, VSA or Wyckoff — checked by grepping every prior run artifact, `project.md`, `phases.md` and `docs/`; the only hits were false positives on the unrelated word "profile" as in "project profile" / "capability profile".
- `docs/` currently holds `mm-cot-long-short-index.md` and `testing-methodology.md`, neither about volume.
- Conclusion: this is not shipped, not in flight, and not a previously-recorded deliberate deferral — there is no prior decision this brief would be overriding.

## Sequencing and the external-research gap
The trader's core ask — a volume display anchored to price rather than time, bars running horizontally from the right edge — is the standard description of a volume/market profile, as distinct from the ordinary time-axis volume histogram (offered as a hypothesis per the order, not a settled premise). Whether that is buildable as a **Pine v6 script** turns on a fact this project's lane roster cannot establish: what volume-by-price data a script can actually read. Pine's native per-bar data is OHLC plus one aggregate volume figure; a genuine price-anchored profile needs volume distributed *within* that range, which is either unavailable to a script, or only approximable (e.g., via lower-timeframe aggregation), or already offered natively by TradingView's own charting tools outside of Pine entirely. Which of these is true is a fact about the platform, not about this repo, and confirming it needs documentation or web lookup.

No lane here can do that lookup. `quant` RESEARCH's tools are Read, Write, Glob, Grep, Bash, `mcp__project__*` — all repo-scoped or mechanical; none reach the web or TradingView's own docs. `Bash` does not help either: per project.md § "Why this project is unusual," there is no local Pine compiler or toolchain — Pine only compiles inside TradingView's own editor, the same reason the compile check itself sits outside every lane and is run by the orchestrating session/human. Dispatching `quant` RESEARCH now would have it either guess at Pine's data model or stall with nothing to work from.

Recommended sequencing:
1. The orchestrating session or the human — at the same structural boundary the compile check already occupies — does the external technical-feasibility research directly: (a) what volume-by-price data Pine v6 scripts can actually access and how, (b) whether TradingView's native Volume Profile drawing tools (session/visible-range/fixed-range) already give the trader what they described, without any script, (c) a factual read of what a typical "VSA Wyckoff Volume" community indicator computes, so "better" has something concrete to be better than.
2. That sourced input, plus the human's answer to § Open decisions, becomes the `inputs:` of a `quant` RESEARCH order — not a claim the lane is asked to independently verify.
3. `design`, then `build`, follow only once `quant` RESEARCH has produced a spec, per `phases.md`.

## Open decisions
- What does "better than VSA Wyckoff Volume" mean? The trader named a comparison with no stated dimension. Does the vertical/profile rendering *replace* the current indicator, *supplement* it (both stay on the chart), or is "want better" a second, separate complaint about the VSA-style signal itself (its reading of climax volume, no-demand, no-supply, etc.) independent of the rendering ask? If both are wanted, this is two pieces of work, not one, and the brief cannot split them without this answer.
- Is a custom Pine script the right vehicle at all, or does TradingView's built-in Volume Profile tool already do what is being described, making this a "turn on a native chart tool" answer rather than a build? This is the kind of already-covered check that belongs in Step 1, but the fact lives in TradingView's own product, not this repo — the human is best placed to check it directly in the editor.
- If a custom script is warranted despite the above, what degree of approximation is acceptable per guardrail 5 ("degrade visibly")? A profile built from lower-timeframe bars is materially less accurate than true tick-level volume-by-price, and the header would need to disclose that plainly rather than presenting it as exact.

## Research questions for quant
Deferred until the open decisions above resolve — asked here so the question is not lost, not as a dispatch to make now:
- Given whichever volume-by-price data access is confirmed available in Pine v6, what binning/aggregation method produces a defensible distribution, and does it trace to a named source (e.g., a stated market-profile methodology) or must the header declare it an original approximation, per guardrail 2?
- If the "better than VSA" complaint turns out to be about the *signal* rather than the *rendering*: what published Wyckoff/VSA volume-reading rule would the improvement trace to, as distinct from whatever the current unverified community indicator does? This cannot usefully be asked until the first § Open decisions bullet is answered.

## Non-goals for this stage
- No `.pine` file is created or edited by this brief.
- No story is drafted — premature before scope is known (one script vs. two; rendering vs. signal vs. both).
- No decision on Pine drawing approach (`box.new`/`line.new`/`polyline`) or on which native TradingView tool exists — that is the external research, then `design`'s territory, not this brief's.
- No formula, binning rule or normalisation is specified here — `quant` RESEARCH's territory, once dispatched with sourced inputs.
- No claim that the VSA Wyckoff Volume indicator is deficient in any specific, named way — only that the trader is dissatisfied, which is context, not a diagnosis.
