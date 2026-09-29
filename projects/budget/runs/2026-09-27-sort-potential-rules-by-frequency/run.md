# RUN 2026-09-27-sort-potential-rules-by-frequency
request:      design and implement new feature in Import screen, sory Potential New Rules list after import to have the most repeated expenses first
agentic_root: C:\projects\investments\.agentic
project:      budget
story:        NONE
status:       CLOSED
phase:        close
plan:         v1
budget:       5 — 1 ground-truth + 1 build (backend only — recon found sort is a single-layer Application change, Presentation already preserves returned order unchanged) + 1 build (test) + 1 integration + 1 close
spent:        5
next:         none — CLOSED
gates:        integration PASS · review skipped (no story) · protocol-lint skipped (no pack-corrections.md — no lane emitted a correction)

## Phases
| phase | lane | fires when | state |
|---|---|---|---|
| ground-truth | recon | request names existing use case (Potential New Rules list) | satisfied — 01 |
| framing | product | request is new use case, or changes what it's for | not triggered (sorting order is a display/UX refinement of existing "Potential New Rules" feature — how well it does it, not what it's for) |
| specification | story | framing produced scope with no brief, spans >1 layer or touches migration/Contracts relied on by shipped code | not triggered (single-layer slice; 01-recon.md establishes PotentialRulesViewModel already preserves Application's returned row order unchanged, so no Presentation change is needed — Application-only) |
| design | design | >1 layer changes together, Contracts interface changes, or new migration | not triggered (01-recon.md § Layers affected: single layer — Application only; § Contracts impact: no Contracts change needed for in-file-scope counting, no migration) |
| build | backend/frontend/test/docs | edits src/**, tests/**, docs/** | satisfied — 02, 03 |
| verify (integration) | integration | any build lane dispatched | satisfied — 04 |
| verify (review) | review | run carries a story with acceptance criteria | not triggered (no story) |
| close | docs | always | satisfied — 05 |

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | recon | — | scout | sonnet | 01-recon.md | DONE | — |
| 02 | backend | — | backend-engineer | sonnet | 02-backend.md | DONE | — |
| 03 | test | — | test-engineer | sonnet | 03-test.md | DONE | — |
| 04 | integration | INTEGRATION | tech-lead | sonnet | 04-integration.md | DONE | PASS |
| 05 | docs | — | docs-engineer | sonnet | 05-docs.md | DONE | — |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| contract_note | 02-backend | 02-backend.md § contract_notes | OccurrenceCount not surfaced to Presentation UI — optional future enhancement, not required by this request | CARRIED |

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|
| risk | 01-recon | 02-backend (scoped in work order) | count scope resolved to within-the-just-imported-file only, per request's own "after import" wording and to avoid new Contracts/repository work; not a historical cross-import count |
| contract_note | 02-backend | 05-docs | docs/PROJECT_GUIDE.md § Rule Management updated to document most-repeated-first default order and tie-break |

## Rounds
| finding | lane | round | of | caused by |
|---|---|---|---|---|

## Replans
| plan | because | change |
|---|---|---|
