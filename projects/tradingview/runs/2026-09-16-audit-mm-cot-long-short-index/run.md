# RUN 2026-09-16-audit-mm-cot-long-short-index
request:      review mm_cot_long_short_index.pine script, main idea is that on friday it should be official reports of players in the market about their short and long positions, my main goal to analyze Gold price. Review, analyse, try to find any bugs
agentic_root: C:\projects\investments\.agentic
project:      tradingview
story:        NONE
status:       CLOSED
phase:        close
plan:         v1
budget:       3 — ground-truth (recon, 1) + verify/quant-audit (1) + close/docs (1)
spent:        3
next:         none — CLOSED
gates:        quant-audit FAIL · integration skipped (no build lane dispatched) · review skipped (no story to accept)

## Phases
| phase | lane | fires when | state |
|---|---|---|---|
| ground-truth | recon | the request names an existing script (mm_cot_long_short_index.pine) | satisfied — 01 |
| framing | product | the request is a new script, or changes what an existing script is for | not triggered (pure analysis/audit request, no new script and no change to purpose) |
| specification (quant) | quant RESEARCH | the work introduces or changes a formula | not triggered (no new formula being introduced; auditing an existing one) |
| specification (story) | story | framing produced scope no approved story covers, spanning >1 script or a published signature | not triggered (framing did not fire; nothing being built) |
| design | design | more than one script changes together, or a published signature changes | not triggered (nothing changes) |
| build | backend/test/docs | anything edits a .pine file, fixture or header | not triggered (read-only investigation; no repo edits planned this run) |
| verify — quant-audit | quant-audit | any lane touched a formula/threshold/sizing/normalisation/symbol mapping | satisfied — 02 (FAIL) |
| verify — integration | integration | any build lane was dispatched | not triggered (no build lane dispatched) |
| verify — review | review | the run carries a story whose criteria someone must accept | not triggered (no story) |
| close | docs | always | satisfied — 03 |

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | recon | — | scout | sonnet | 01-recon.md | DONE | — |
| 02 | quant-audit | AUDIT | quantitative-researcher | opus | 02-quant-audit.md | DONE | FAIL |
| 03 | docs | — | docs-engineer | sonnet | 03-docs.md | DONE | — |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| bug | 02-quant-audit | 02-quant-audit.md § FINDING 1 | CRITICAL: 156-week lookback counts chart bars not weeks; index saturates on non-weekly charts | CARRIED |
| bug | 02-quant-audit | 02-quant-audit.md § FINDING 2 | CRITICAL: -80 guide line labelled inverted for the short-index plot | CARRIED |
| bug | 02-quant-audit | 02-quant-audit.md § FINDING 3 | MATERIAL: index rescales gross long/short separately, not net as the cited methodology defines it — needs a human decision | CARRIED |
| bug | 02-quant-audit | 02-quant-audit.md § FINDING 4 | MATERIAL: +/-80 guides are the 90/10 extremes on this scale, not the conventional 80/20 | CARRIED |
| should_fix | 02-quant-audit | 02-quant-audit.md § FINDING 5 | MATERIAL: header cites no named source; Briese (2008)/Williams (2005) are citable | CARRIED |
| bug | 02-quant-audit | 02-quant-audit.md § FINDING 6 | MATERIAL: _OLD ticker suffix implies a crop-year breakout that does not exist for Gold | CARRIED |
| should_fix | 02-quant-audit | 02-quant-audit.md § FINDING 7 | MATERIAL: request.security() omits explicit lookahead=barmerge.lookahead_off; pine_check --strict fails | CARRIED |
| bug | 02-quant-audit | 02-quant-audit.md § FINDING 8 | MATERIAL: no as-of date/staleness test; gaps_off holds last value forward forever | CARRIED |
| should_fix | 03-docs | docs/mm-cot-long-short-index.md § contract_notes | doc goes stale the moment any FINDING is fixed — whichever lane closes a finding must update the matching section | CARRIED |
| should_fix | 03-docs | 03-docs.md § handoff | header's WHAT THIS COMPUTES citation and symbol re-verification still owed once FINDING 3/6 are decided | CARRIED |

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|

## Rounds
| finding | lane | round | of | caused by |
|---|---|---|---|---|

## Replans
| plan | because | change |
|---|---|---|
