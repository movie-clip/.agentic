# RUN 2026-09-24-import-rules-redesign
request:      redesign and implement Potential New Rules list in Import screen. It should have at least same functionality, editing text of description, category drop dawn etc, you can remove and delete anything outdated do not keep two different implementations, leave only one
agentic_root: C:\projects\investments\.agentic
project:      budget
story:        NONE
status:       CLOSED
phase:        close
plan:         v3
budget:       8 — recon + design + backend + frontend + frontend cleanup + test + integration + docs
spent:        8
next:         none — CLOSED
gates:        integration PASS · review skipped (no story to accept)

## Phases
| phase | lane | fires when | state |
|---|---|---|---|
| ground-truth | recon | request names an existing view and asserts unverified claims (two implementations) | satisfied — 01 |
| framing | product | changes what the product does | not triggered (redesign of existing view, same functionality; how well, not what for) |
| specification | story | framing produced uncovered multi-layer scope | not triggered (framing not triggered; no uncovered scope) |
| design | design | multi-layer, Contracts change or migration | satisfied — 02 |
| build | frontend, test, docs | anything that edits the repo | satisfied — 04,05,06 |
| verify | integration | any build lane dispatched | satisfied — 07 |
| verify | review | run carries a story | not triggered (no story) |
| close | docs | always | satisfied — 08 |

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | recon | — | scout | sonnet | 01-recon.md | DONE | — |
| 02 | design | DESIGN | tech-lead | sonnet | 02-design.md | DONE | — |
| 03 | backend | — | backend-engineer | sonnet | 03-backend.md | DONE | — |
| 04 | frontend | — | frontend-engineer | sonnet | 04-frontend.md | DONE | — |
| 05 | frontend | — | frontend-engineer | sonnet | 05-frontend.md | DONE | — |
| 06 | test | — | test-engineer | sonnet | 06-test.md | DONE | — |
| 07 | integration | INTEGRATION | tech-lead | sonnet | 07-integration.md | DONE | PASS |
| 08 | docs | — | docs-engineer | sonnet | 08-docs.md | DONE | — |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|
| contract_note | 02-design | 04-frontend (consumed contract) | 4 contract notes to route to backend/frontend/test/docs orders |
| contract_note | 03-backend | 08-docs (docs reconciled) | PotentialRuleRow reshaped; Preview ctor + Apply use case; VM/CompositionRoot/tests lag |
| contract_note | 04-frontend | 08-docs (docs reconciled) | VM ctor/members changed; test factories, docs lag |
| handoff | 03-backend | 06-test (coverage list absorbed) | Application/Domain test coverage list for test lane |
| handoff | 04-frontend | 06-test (VM/D1/D2 coverage absorbed) | VM test list for test lane |

## Rounds
| finding | lane | round | of | caused by |
|---|---|---|---|---|

## Replans
| plan | because | change |
|---|---|---|
| v2 | 01-recon § Q3 showed decision logic (default category, IsModified, Apply All filter, prefix-derived pattern) in Presentation; guardrail 3 | design re-triggered, backend lane added; budget 5 -> 7 |
| v3 | 04-frontend risk 4: two old row VMs unreferenced in src, kept alive only by tests/Test1.cs; user asked for one implementation only | extra frontend cleanup order before test lane; budget 7 -> 8 |
