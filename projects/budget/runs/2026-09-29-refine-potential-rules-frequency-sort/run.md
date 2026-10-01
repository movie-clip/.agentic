# RUN 2026-09-29-refine-potential-rules-frequency-sort
request:      Refine the Potential New Rules frequency sort shipped in run 2026-09-27-sort-potential-rules-by-frequency (committed in dbfe30e). 1) Tie order: rows whose pattern counts are equal must stay grouped by pattern, and the groups ordered by where each pattern first appears in the file — never interleaved. Sort by OccurrenceCount descending, then by the first line where the pattern appears. Update ExecuteAsync_PatternsWithEqualOccurrenceCounts_PreserveOriginalParseOrder: rename it to state the grouping, and change its expected LineNumber order from [1,2,3,4] to [1,3,2,4]. 2) Show each row's OccurrenceCount on the Import screen (e.g. "×3") so the order is readable; count 1 may be shown or hidden, match the existing row layout. 3) Cleanups: remove the unused "= 0" default on PotentialRuleRow.OccurrenceCount, and in FromRow_StartsAtBaselineAndUnmodified remove the Assert on row.OccurrenceCount, which checks a value the test set itself. Count scope stays "within the current import file" (already decided in that run's ledger). This spans Application and Presentation, so run the design phase.
agentic_root: C:\projects\investments\.agentic
project:      budget
story:        NONE
status:       DISPATCHING
phase:        build
plan:         v1
budget:       7 — ground-truth 1 (recon) + design 1 + build 3 (backend, frontend, test) + integration 1 + close 1
spent:        4
next:         dispatch 05 test — rename ExecuteAsync_PatternsWithEqualOccurrenceCounts_PreserveOriginalParseOrder, expect LineNumber [1,3,2,4], assert OccurrenceText ×1/×3, drop the OccurrenceCount Assert in FromRow_StartsAtBaselineAndUnmodified
gates:        integration pending · review skipped (no story to accept)

## Phases
| phase | lane | fires when | state |
|---|---|---|---|
| ground-truth | recon | request names existing use case/view model, or unverified claim | satisfied — 01 |
| framing | product | new use case, or changes what an existing one is for | not triggered (tie-order refinement and a count label change how well the Potential New Rules list works, not what it is for) |
| specification | story | framing produced scope no approved story covers, and spans >1 layer / migration / Contracts | not triggered (framing produced no scope; the user's request states each outcome and test change checkably) |
| design | design | >1 layer changes together, Contracts/use-case shape changes, or new migration | satisfied — 02 |
| build | backend, frontend, test, docs | edits src/**, tests/**, docs/** | pending |
| verify (integration) | integration | any build lane dispatched | pending |
| verify (review) | review | run carries a story with acceptance criteria | not triggered (no story) |
| close | docs | always | pending |

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | recon | — | scout | sonnet | 01-recon.md | DONE | — |
| 02 | design | DESIGN | tech-lead | sonnet | 02-design.md | DONE | — |
| 03 | backend | — | backend-engineer | sonnet | 03-backend.md | DONE | — |
| 04 | frontend | — | frontend-engineer | sonnet | 04-frontend.md | PARTIAL | — |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| contract_note | 02-design | 02-design.md § contract (OccurrenceText) | PotentialRuleRowViewModel.OccurrenceText + new Count column in MainWindow.axaml | OPEN |
| contract_note | 02-design | 02-design.md § lanes (docs) | docs/PROJECT_GUIDE.md:30-33 tie-order sentence goes stale | OPEN |
| handoff | 03-backend | 03-backend.md § handoff | tie-order test fails until test lane renames it and expects [1,3,2,4] | OPEN |
| handoff | 04-frontend | 04-frontend.md § handoff | test lane asserts OccurrenceText as ×N, U+00D7 then the integer, no space | OPEN |
| contract_note | 04-frontend | docs/PROJECT_GUIDE.md:34-36 | per-row description lacks the new Count column; docs lane owns it at close-out | OPEN |

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|
| contract_note | 01-recon | 02-design (planned as OccurrenceText in § contract) | PotentialRuleRowViewModel must gain an OccurrenceCount property; it discards it today |
| contract_note | 01-recon | 02-design (planned in § contract) | removing '= 0' default touches one prod and one test PotentialRuleRow construction |
| contract_note | 02-design | 03-backend | drop '= 0' on OccurrenceCount; sort by count desc, first line asc, line asc |
| contract_note | 02-design | dismissed — informational; 03-backend confirmed only PreviewPotentialRulesUseCase.cs changed | Contracts, migrations, paging untouched — informational |

## Rounds
| finding | lane | round | of | caused by |
|---|---|---|---|---|

## Replans
| plan | because | change |
|---|---|---|
