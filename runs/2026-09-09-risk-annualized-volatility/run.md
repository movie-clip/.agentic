# RUN 2026-09-09-risk-annualized-volatility
request:      Add a portfolio-level annualized volatility metric to the Risk tab. Compute it from the daily returns of the current portfolio's synthetic history, and show it in the risk summary area alongside the existing risk figures. When there is not enough return history to compute it responsibly, it must not display a number — show the appropriate trust state instead. I have not decided which annualization convention to use, or what the minimum amount of history should be. Treat both as open questions. Keep it sourced and rendered consistently with the other Risk tab metrics.
agentic_root: C:\projects\investments\.agentic
story:        NONE
status:       BLOCKED
blocked_on:   human must (1) rule on open decisions (a) annualization convention and (b) minimum history, (2) confirm whether ce9c97d's deletion of docs/product planning corpus was intended
next:         await human verdict on 01 brief; then dispatch story-author (+ quant RESEARCH if a Risk-tab-native computation is chosen)
route:        full
express:      no
gates:        quant-audit pending · integration pending · review pending

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | product | — | producer | sonnet | 01-delivery-brief.md | DONE | — |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| decision | 01-delivery-brief | 01-delivery-brief.md § Open decisions (a) | annualization/source: reuse Dashboard diagnostics figure (A) vs Risk-tab-native from distribution engine (B) vs calendar basis (C) | CARRIED |
| decision | 01-delivery-brief | 01-delivery-brief.md § Open decisions (b) | min history: inherit product-wide 20-obs floor (A) vs stricter annualized-vol floor e.g. 60/252 (B) vs tie to window selector (C) | CARRIED |
| blocker | 01-delivery-brief | git HEAD ce9c97d | "cleanup" commit deleted docs/product/epic-roadmap.md, prd/**, stories/** from tree; story-author writes into stories/ — human must confirm intent | CARRIED |
| finding | 01-delivery-brief | 01-delivery-brief.md § Already covered | metric already ships on Dashboard (volatility_summary.portfolio_volatility_pct, stdev*sqrt(252), 20-obs floor); only its Risk-tab appearance is new | CARRIED |
| finding | 01-delivery-brief | 01-delivery-brief.md § Placement | producer recommends Backlog, one story, no new epic — epic placement is the human's call | CARRIED |

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|

## Rounds
| finding | lane | round | of |
|---|---|---|---|

## Cost
| metric | value |
|---|---|
| dispatches | — |
| rounds | — |
| by model | — |
| escalations | — |
