# RUN 2026-11-22-model-tiers
request:      Lint the owner's model ruling of 2026-11-22: engineer and reviewer move to opus/medium, tech-lead from low to medium effort, test-engineer from medium to high effort; protocol/authoring.md is rewritten to state the ruling, and the examples in protocol/orchestrator.md and the orchestrate-feature skill follow.
agentic_root: C:\projects\investments\.agentic
network:      0.10.10
project:      none
story:        NONE
status:       CLOSED
phase:        close
plan:         v1
budget:       3 — protocol-lint 1, two re-lints 2
intake:       3
spent:        2
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
