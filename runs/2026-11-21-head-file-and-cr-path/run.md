# RUN 2026-11-21-head-file-and-cr-path
request:      Lint two wording edits observed in los-tres run 2026-11-21-s2-4-hide: the orchestrator validates a head file the hook already saved and does not rewrite it (protocol/orchestrator.md § 5, orchestrate-feature SKILL.md checklist), and a change request's `raised by:` names the artifact by its file name in the run dir (PROTOCOL.md § change requests).
agentic_root: C:\projects\investments\.agentic
network:      0.10.8
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
| 01 | protocol-lint | — | protocol-linter | opus | 01-protocol-lint.md | DONE | PASS |
| 02 | protocol-lint | — | protocol-linter | opus | 02-protocol-lint.md | DONE | PASS |
