# RUN 2026-10-22-runs-gitignored
request:      Lint the network edit that makes project runs local and never committed: orchestrator.md § "Every unfinished run is shown to the human at intake" and § "Closed runs are pruned", authoring.md § "Adding a project", ARCHITECTURE.md's capability-layer paragraph and README.md's tree line say `agentic/runs/` is gitignored and pruning deletes a run for good.
agentic_root: C:\projects\investments\.agentic
project:      none
story:        NONE
status:       CLOSED
phase:        close
plan:         v2
budget:       2 — protocol-lint 2
spent:        2
blocked_on:   none
next:         none — CLOSED
gates:        protocol-lint PASS (02)

## Phases
| phase | lane | fires when | state |
|---|---|---|---|
| verify | protocol-lint | always — the run exists to lint a network edit | satisfied — 02 |

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | protocol-lint | — | protocol-linter | opus | 01-protocol-lint.md | DONE | FAIL |
| 02 | protocol-lint | — | protocol-linter | opus | 02-protocol-lint.md | DONE | PASS |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|

## Rounds
| finding | lane | round | of | caused by |
|---|---|---|---|---|
| F1 | protocol-lint | 1 | 2 | — |

## Replans
| plan | because | change |
|---|---|---|
| v2 | 01 FAIL (F1) needs a re-lint past budget 1; decisions.md D-1 | budget 1 -> 2; designer.md added to 02's scope |
