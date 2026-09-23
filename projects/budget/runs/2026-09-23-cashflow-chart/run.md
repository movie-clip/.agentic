# RUN 2026-09-23-cashflow-chart
request:      review Cash Flow Trend chart in Dashboard, make sure it is representing accurate correct values, check that it is reading correct data and properly represents it. Do UI pass, chart looks boaring, make it better, more up to date design, with better colors
agentic_root: C:\projects\investments\.agentic
project:      budget (projects/budget/project.md)
story:        NONE
status:       CLOSED
phase:        close
plan:         v2
budget:       7 — ground-truth(1) + build(3 lanes: backend, frontend, test) + verify:integration(1) + close(1) + protocol-lint(1) on the testing.md capability-pack edit
spent:        7
next:         none — CLOSED
gates:        integration PASS · review skipped (no story exists to accept against) · protocol-lint PASS (testing.md pack correction)

## Phases
| phase | lane | fires when | state |
|---|---|---|---|
| ground-truth | recon | request names an existing view (Dashboard's monthly trend chart) and rests on an unverified claim about current data-accuracy behavior | satisfied — 01 |
| framing | product | request is a new use case or changes what an existing one is for | not triggered (correctness fix + restyle of shipped Dashboard behavior; nothing about what the trend chart is for changes — 01-recon.md confirms no use-case-shape change) |
| specification | story | scope spans more than one layer's contract with no existing brief, or touches a migration/Contracts interface already relied on by shipped code | not triggered (01-recon.md § Blast radius: all in-scope findings confined to one layer each; no Contracts interface or use-case signature changes) |
| design | design | a Contracts interface or use-case shape changes, or a new migration is introduced | not triggered (finding 4 — currency — is the only one that would cross a contract, and it is out of scope this run: the 7-column bank import format carries no currency field, so it is not a reachable risk for this user's data; recorded as a Closed/dismissed note, not acted on) |
| build | backend, frontend, test, docs | anything that edits src/**, tests/**, docs/** | satisfied — 02, 03, 04 |
| verify | integration | any build lane dispatched | satisfied — 05 |
| verify | review | run carries a story whose criteria someone must accept | not triggered (no story exists to accept against) |
| close | docs | always | satisfied — 06 |

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | recon | — | scout | sonnet | 01-recon.md | DONE | — |
| 02 | backend | — | backend-engineer | sonnet | 02-backend.md | DONE | — |
| 03 | frontend | — | frontend-engineer | sonnet | 03-frontend.md | DONE | — |
| 04 | test | — | test-engineer | sonnet | 04-test.md | DONE | — |
| 05 | integration | INTEGRATION | tech-lead | sonnet | 05-integration.md | DONE | PASS |
| 06 | docs | — | docs-engineer | sonnet | 06-docs.md | DONE | — |
| 07 | protocol-lint | — | protocol-linter | opus | 07-protocol-lint.md | DONE | PASS |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| should_fix | 05-integration | 05-integration.md § risks | is_deleted=0 filter fix's blast radius is wider than the trend chart (also affects ledger entries, rule application, export/backup use cases) — correct, but currently inert; worth the human knowing | CARRIED |
| should_fix | 05-integration | 05-integration.md § risks | MainWindowViewModelTrendBarScalingTests couples to the full 22-arg constructor — real maintenance liability, not a guardrail violation | CARRIED |

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|
| finding | 01-recon | dismissed — no currency column in the 7-column bank import format, not a reachable risk for this user's data today | finding 4 (currency mixing in trend sums) would need a design pass only if multi-currency import is ever added |
| should_fix | 04-test | 06-docs | testing.md pack corrected: Application.Tests already references HomeCharts.Presentation, so Presentation view-model behavior is coverable there without a separate Presentation.Tests project |

## Rounds
| finding | lane | round | of | caused by |
|---|---|---|---|---|

## Replans
| plan | because | change |
|---|---|---|
| v2 | 06-docs edited projects/budget/capabilities/testing.md directly (an authoring edit to a network file) without going through a pack-corrections.md file first — protocol-lint is the declared gate for any order that edits a capability pack and was not yet dispatched | budget 6 → 7; dispatch protocol-lint against the testing.md edit before close |
