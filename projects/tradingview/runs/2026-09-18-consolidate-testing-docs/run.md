# RUN 2026-09-18-consolidate-testing-docs
request:      Test mm_cot_long_short_index.pine live using the official Pine Logs
              method before writing anything, then document the verified
              method and findings, and consolidate the existing testing docs
              down to one clean, current file rather than leaving old
              documentation layered alongside the new content.
agentic_root: C:\projects\investments\.agentic
project:      tradingview
story:        NONE
status:       CLOSED
phase:        close
plan:         v1
budget:       1 — close/docs (1), the only phase whose trigger is true: no
              .pine/fixture/header edit (build not triggered), no new script
              (framing not triggered), no formula change (specification/quant
              not triggered), single lane (design not triggered), no story
              (review not triggered)
spent:        1
next:         none — CLOSED
gates:        quant-audit skipped (no formula/threshold/symbol-mapping touched
              by this run) · integration skipped (no .pine file touched) ·
              review skipped (no story to accept)

## Phases
| phase | lane | fires when | state |
|---|---|---|---|
| ground-truth | recon | the request names an existing script, or rests on an unverified claim | not triggered (the orchestrator's own first-hand live Pine Logs test against mm_cot_long_short_index.pine on TradingView, performed this session before this run opened, is the verified ground truth this run documents) |
| framing | product | the request is a new script, or changes what an existing script is for | not triggered (documentation of an already-verified testing method; no new script, no change to any script's purpose) |
| specification (quant) | quant RESEARCH | the work introduces or changes a formula, a normalisation or a threshold | not triggered (no formula involved) |
| specification (story) | story | framing produced scope no approved story covers, and the slice spans >1 script or a published signature | not triggered (framing did not fire) |
| design | design | more than one script changes together, or a published input/plot/alert signature changes | not triggered (no script changes at all — docs files only) |
| build | backend, test, docs | anything edits a .pine file, a fixture or a script header | not triggered (no .pine file, fixture, or header touched — docs files only) |
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
| handoff | 01-docs | orchestrator (this ledger) | docs-engineer's lane holds no delete tool (PROTOCOL.md); orchestrator ran `rm docs/tradingview-symbol-verification.md` directly — the file was untracked/uncommitted scratch content, its substance already fully merged and verified in 01-docs.md, so this was mechanical cleanup, not a content decision |

## Rounds
| finding | lane | round | of | caused by |
|---|---|---|---|---|

## Replans
| plan | because | change |
|---|---|---|
