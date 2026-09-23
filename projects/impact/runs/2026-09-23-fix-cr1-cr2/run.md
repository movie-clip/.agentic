# RUN 2026-09-23-fix-cr1-cr2
request:      Fix the two carried SHOULD_FIX change requests from run
              2026-09-22-session-start-diagnostic: CR-1 (test lane,
              Impact\Tools\Run-UnityTests.ps1 — `-CoreOnly` maps to
              `-testFilter "Core"` instead of `-testCategory "Core"`, silently
              under-running the Core regression suite) and CR-2 (backend lane,
              Impact\Packages\athena.core\Runtime\Systems\SessionStartDiagnosticSystem.cs
              — OnCreate should end with `state.Enabled = false;`, matching the
              GameSessionSystem.cs precedent). Full text at
              ../2026-09-22-session-start-diagnostic/cr/CR-1.md and CR-2.md.
agentic_root: C:\projects\investments\.agentic
project:      impact
story:        NONE
status:       CLOSED
phase:        close
plan:         v2
budget:       6 — build(2: backend CR-2, test CR-1) + verify(1: integration) +
              close(1: docs) + protocol-lint(1); ground-truth/framing/
              specification/design not triggered
spent:        5
next:         none -- CLOSED
gates:        integration PASS -- 03 . review skipped (no story) . protocol-lint PASS -- 05 (PC-1)

## Phases
| phase | lane | fires when | state |
|---|---|---|---|
| ground-truth | recon | the request names an existing system/behaviour, or rests on an unverified claim about current behaviour | not triggered (both findings are already verified with file:line citations in the prior run's cr/CR-1.md, cr/CR-2.md and 04-integration.md; this run touches exactly those two named files) |
| framing | product | the request is a new gameplay system or feature surface, or changes what an existing one is for | not triggered (both are internal correctness fixes to existing code — a test-runner flag mapping and an existing system's lifecycle — no new gameplay surface) |
| specification | story | framing produced scope no approved brief covers, and the slice crosses more than one lane's contract | not triggered (each CR is single-lane — CR-1 test only, CR-2 backend only — and the CR file itself is the specification, same shape as project.md § Delivery model) |
| design | design | the change crosses a package-boundary contract — a shared singleton/component shape, the crate/content-loading pipeline, a new cross-package .asmdef reference | not triggered (CR-1 touches a PowerShell script, not code; CR-2 adds one line to an existing system's OnCreate with no new/changed component or singleton shape) |
| build | backend, test | anything that edits Impact/Packages/**, Impact/Assets/**, Impact/Tools/**, or Impact/*.md | satisfied — 01, 02 |
| verify | integration | any build lane was dispatched | satisfied — 03, PASS |
| verify | review | the run carries a story whose acceptance criteria someone must accept | not triggered (no story) |
| close | docs | always | satisfied — 04 |

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | backend | — | backend-engineer | sonnet | 01-backend.md | DONE | — |
| 02 | test | — | test-engineer | sonnet | 02-test.md | DONE | — |
| 03 | integration | INTEGRATION | tech-lead | sonnet | 03-integration.md | DONE | PASS |
| 04 | docs | — | docs-engineer | sonnet | 04-docs.md | DONE | — |
| 05 | protocol-lint | — | protocol-linter | opus | 05-protocol-lint.md | DONE | PASS |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|
| handoff | 02-test | 04-docs — dismissed - Impact/Tools/TESTING.md checked, no stale -CoreOnly text found, left unchanged | Impact\Tools\TESTING.md may still reference stale -CoreOnly/-testFilter behaviour |

## Rounds
| finding | lane | round | of | caused by |
|---|---|---|---|---|

## Replans
| plan | because | change |
|---|---|---|
| v2 | 02-test.md's pack_corrections is non-empty (PC-1, capabilities/testing.md), so protocol-lint is owed at close per phases.md's gates accounting | budget 4 -> 6 |
