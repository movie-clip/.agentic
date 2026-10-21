# RUN 2026-10-21-s6-1-leftovers
request:      collect leftovers from implementing 6.1, and start working on fixing them
agentic_root: C:\projects\investments\.agentic
project:      projects/los-tres/project.md
story:        NONE
status:       CLOSED
phase:        verify
plan:         v1
budget:       4 — build 1 (test) + integration 1 + close docs 1 (pack fixes) + protocol-lint 1
spent:        4
next:         none — CLOSED
gates:        review skipped (no story file, leftover fixes from runs/2026-10-21-s6-1-product-jsonld) · integration PASS (02) · ux-review skipped (no screen change) · protocol-lint PASS (04)

## Phases
| phase | lane | fires when | state |
|---|---|---|---|
| ground-truth | recon | the request names existing code or rests on an unverified claim about current behaviour | not triggered (each leftover is located by file:line in runs/2026-10-21-s6-1-product-jsonld/05-integration.md and 07-protocol-lint.md § handoff) |
| framing | product | the request adds a user-facing surface, changes what one is for, or mvp.md does not exist yet | not triggered (no user-facing change; test and pack hygiene only) |
| specification | story | framing produced scope no approved brief covers, and the slice crosses more than one lane's contract or changes a data model | not triggered (framing did not fire; no contract or data model change) |
| design | ux | the request adds or changes a public or admin screen, a user flow, or user-facing copy | not triggered (no screen, flow or copy change) |
| design | design | the change crosses the frontend/backend contract or more than one build lane touches it | not triggered (one build lane, test; no contract crossing) |
| build | test | anything that edits repo code, tests or docs/** | satisfied — 01 |
| verify | integration | any build lane was dispatched | satisfied — 02 |
| verify | ux-review | ux was satisfied, or a build lane changed what a public screen renders | not triggered (test-only change) |
| verify | review | the run carries a story whose acceptance criteria someone must accept | not triggered (no story) |
| close | docs | always | satisfied — 03 |

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | test | — | test-engineer | sonnet | 01-test.md | DONE | — |
| 02 | integration | INTEGRATION | tech-lead | opus | 02-integration.md | DONE | PASS |
| 03 | docs | — | docs-engineer | sonnet | 03-docs.md | DONE | — |
| 04 | protocol-lint | — | protocol-linter | opus | 04-protocol-lint.md | DONE | PASS |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| risk | s6-1/01-design | src/components/JsonLd.tsx | no lint rule bans dangerouslySetInnerHTML yet; nothing to allow-list | CARRIED |
| should_fix | 04-protocol-lint | capabilities/testing.md | :93 names a regex literal as the cause, fix reads like the hazard | CARRIED |

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|
| should_fix | s6-1/05-integration | 01-test | raw U+2028/U+2029 in test strings; write as escapes -> test |
| should_fix | s6-1/07-protocol-lint | 03-docs | :95 raw U+2028 byte, and split the 4-fact bullet into :93 -> close docs |
| should_fix | s6-1/07-protocol-lint | 03-docs | :28 add why product-jsonld.ts stays free of server-only -> close docs |

## Rounds
| finding | lane | round | of | caused by |
|---|---|---|---|---|

## Replans
| plan | because | change |
|---|---|---|
