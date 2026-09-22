# RUN 2026-09-18-testing-methodology-docs
request:      Move the testing/findings write-up from the orchestrator's own session memory into the repo, as two separate files: one documenting the TradingView Pine compile-check testing methodology, one documenting the COT symbol-verification findings from the 2026-09-17 fix run. Content is supplied directly by the orchestrator in the work order (already researched during that run); this is a placement/writing task, not a research task.
agentic_root: C:\projects\investments\.agentic
project:      tradingview
story:        NONE
status:       CLOSED
phase:        close
plan:         v1
budget:       1 — close/docs (1), the only phase whose trigger is true: no .pine/fixture/header edit (build not triggered), no new script (framing not triggered), no formula change (specification/quant not triggered), single lane (design not triggered), no story (review not triggered)
spent:        1
next:         none — CLOSED
gates:        quant-audit skipped (no formula/threshold/symbol-mapping touched by this run) · integration skipped (no .pine file touched) · review skipped (no story to accept)

## Phases
| phase | lane | fires when | state |
|---|---|---|---|
| ground-truth | recon | the request names an existing script, or rests on an unverified claim | not triggered (content is the orchestrator's own first-hand findings from run 2026-09-17-fix-mm-cot-long-short-index, already verified there; nothing further to establish) |
| framing | product | the request is a new script, or changes what an existing script is for | not triggered (documentation of existing, already-closed work; no new script, no change to any script's purpose) |
| specification (quant) | quant RESEARCH | the work introduces or changes a formula, a normalisation or a threshold | not triggered (no formula involved) |
| specification (story) | story | framing produced scope no approved story covers, and the slice spans >1 script or a published signature | not triggered (framing did not fire) |
| design | design | more than one script changes together, or a published input/plot/alert signature changes | not triggered (no script changes at all — two new docs files only) |
| build | backend, test, docs | anything edits a .pine file, a fixture or a script header | not triggered (no .pine file, fixture, or header touched — two new standalone docs files) |
| verify — quant-audit | quant-audit | any lane touched a formula/threshold/normalisation/symbol mapping | not triggered (nothing touched) |
| verify — integration | integration | any build lane was dispatched | not triggered (build did not fire) |
| verify — review | review | the run carries a story whose criteria someone must accept | not triggered (no story) |
| close | docs | always | satisfied — 01 |

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | docs | — | docs-engineer | sonnet | 01-docs.md | DONE | — |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|

## Rounds
| finding | lane | round | of | caused by |
|---|---|---|---|---|

## Replans
| plan | because | change |
|---|---|---|
