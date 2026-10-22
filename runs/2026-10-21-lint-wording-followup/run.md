# RUN 2026-10-21-lint-wording-followup
request:      Lint four wording fixes that follow run 2026-10-21-move-capability-layer: a lint run's run_dir (PROTOCOL.md), agentic/runs/README.md at onboarding (authoring.md), who commits pack corrections (packs.md), and a tracked run's run dir staying out of the pull request (orchestrator.md).
agentic_root: C:\projects\investments\.agentic
project:      none
story:        NONE
status:       CLOSED
phase:        close
plan:         v2
budget:       2 — protocol-lint 1 + re-lint 1 (v2)
spent:        2
next:         none — CLOSED
gates:        protocol-lint PASS (02; FAIL 01)

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
| finding | 01-protocol-lint | 02-protocol-lint — F1 RESOLVED at packs.md:20 | packs.md:20-21 contradicted orchestrator.md § 8 on who commits pack corrections |

## Rounds
| finding | lane | round | of | caused by |
|---|---|---|---|---|
| F1 | main session (authoring.md § Linting a network edit, step 3) | 1 | 2 | independent |

## Replans
| plan | because | change |
|---|---|---|
| v2 | 01 FAIL: F1 blocking — packs.md:20-21 restated orchestrator.md § 8's commit rule without its build condition | main session replaced packs.md:20-21 with a pointer to § 8; one re-lint (02); budget 1 -> 2 |
