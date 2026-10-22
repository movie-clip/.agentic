# RUN 2026-10-21-move-capability-layer
request:      Lint the network edits that move each project's profile, packs and runs out of .agentic/projects/ into <repo>/agentic/, drop protocol-lint on pack corrections, and file network lint runs under .agentic/runs/.
agentic_root: C:\projects\investments\.agentic
project:      none
story:        NONE
status:       CLOSED
phase:        close
plan:         v3
budget:       3 — protocol-lint 1 + re-lint 1 (v2) + re-lint 1 (v3)
spent:        3
next:         none — CLOSED
gates:        protocol-lint PASS (03; FAIL 01, 02)

## Phases
| phase | lane | fires when | state |
|---|---|---|---|
| verify | protocol-lint | always — the run exists to lint a network edit | satisfied — 03 |

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | protocol-lint | — | protocol-linter | opus | 01-protocol-lint.md | DONE | FAIL |
| 02 | protocol-lint | — | protocol-linter | opus | 02-protocol-lint.md | DONE | FAIL |
| 03 | protocol-lint | — | protocol-linter | opus | 03-protocol-lint.md | DONE | PASS |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|
| finding | 01-protocol-lint | 02-protocol-lint — F1-F9 RESOLVED | 5 duplicated rules, 3 conflicting instructions, 1 missing Contents entry |
| finding | 02-protocol-lint | 03-protocol-lint — F10 RESOLVED at orchestrator.md:17-21 | onboarding lint runs missing from orchestrator.md § 1 run location (caused by F3 fix) |

## Rounds
| finding | lane | round | of | caused by |
|---|---|---|---|---|
| F1-F2, F4-F9 | main session (authoring.md § Linting a network edit, step 3) | 1 | 2 | independent |
| F3 | main session | 1 | 2 | independent |
| F10 | main session | 2 | 2 | F3 |

## Replans
| plan | because | change |
|---|---|---|
| v2 | 01 FAIL: 9 blocking (F1-F9) | main session fixed all nine in authoring.md, orchestrator.md, packs.md and agentic-protocol/SKILL.md; one re-lint (02); budget 1 -> 2 |
| v3 | 02: F1-F9 resolved, F10 new (caused by the F3 fix) | main session widened orchestrator.md:17-21 to name onboarding lint runs; one re-lint (03) pending human approval past the hard stop; budget 2 -> 3 |
