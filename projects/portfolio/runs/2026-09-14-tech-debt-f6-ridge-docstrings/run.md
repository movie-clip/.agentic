# RUN 2026-09-14-tech-debt-f6-ridge-docstrings
request:      fix F6 from docs/tech-debt-register.md: test_analytics.py docstrings (around lines 7848, 7905-7907) describe an unshipped λ=0.01 / 25-obs / 8-df mechanism that doesn't match the shipped λ=1e-5 ridge model. Correct the docstrings to match reality.
agentic_root: C:\projects\investments\.agentic
project:      portfolio
story:        NONE
status:       BLOCKED
phase:        ground-truth
plan:         v1
budget:       5 - 3 triggered phases (ground-truth, build is 1 lane, close) + 2 gates (quant-audit, integration)
spent:        1
blocked_on:   human ruling on whether risk.py:1636 joins this run's scope
next:         human stop: rule on risk.py:1636 scope, then dispatch 02 test
gates:        quant-audit pending . integration pending . review skipped (no story - the story row did not fire)

## Phases
| phase | lane | fires when | state |
|---|---|---|---|
| ground-truth | recon | the area is unfamiliar, or the run would otherwise build on an unverified claim - a bug report, a findings doc, a "this number looks wrong" | satisfied — 01 |
| framing | product | the request changes what the product does: a new capability, new scope, or a re-prioritisation | not triggered (corrects prose inside an existing test file; no new capability, no new scope, no re-prioritisation) |
| specification | quant (RESEARCH) | the work introduces or changes a metric, formula, weighting, return basis or trust classification | not triggered (the shipped ridge model is not changed by this run - only the prose describing it) |
| specification | story | framing produced scope that no approved, ticketed story covers, and the slice needs ticketing | not triggered (framing did not fire, so its precondition is false) |
| design | design | the change crosses a contract boundary, or more than one build lane touches it | not triggered (one build lane - test-engineer owns app/tests/**; no schema, no contract field) |
| build | test | anything that edits the repo | pending |
| verify | quant-audit | any lane touched analytics/, a formula, a weighting, a return basis or a trust label | pending |
| verify | integration | any build lane was dispatched | pending |
| verify | review | the run carries a story whose acceptance criteria someone must accept | not triggered (no story - the specification/story row did not fire) |
| close | docs | always - contract notes against docs/, and pack-corrections.md against capabilities/ when a lane emitted one | pending |

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | recon | — | scout | sonnet | 01-recon.md | DONE | — |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| should_fix | 01-recon | analytics/risk.py:1636 | docstring says "window-proportional floor"; shipped ROLLING_RIDGE_FLOOR is uniform 1e-5 | OPEN |

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|

## Rounds
| finding | lane | round | of | caused by |
|---|---|---|---|---|

## Replans
| plan | because | change |
|---|---|---|
