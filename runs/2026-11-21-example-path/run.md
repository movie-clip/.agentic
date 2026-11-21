# RUN 2026-11-21-example-path
request:      Lint a one-line edit: the example of an absolute project_dir in protocol/orchestrator.md § "Two field rules" names portfolio, not los-tres, because the los-tres folder is about to move one level deeper.
agentic_root: C:\projects\investments\.agentic
network:      0.10.9
project:      none
story:        NONE
status:       CLOSED
phase:        close
plan:         v1
budget:       3 — protocol-lint 1, two re-lints 2
intake:       3
spent:        1
next:         none — CLOSED

gates:        protocol-lint PASS (01)
## Phases
| phase | lane | fires when | state |
|---|---|---|---|
| verify | protocol-lint | always — the run exists to lint a network edit | satisfied — 01 |

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | protocol-lint | — | protocol-linter | opus | 01-protocol-lint.md | DONE | PASS |
