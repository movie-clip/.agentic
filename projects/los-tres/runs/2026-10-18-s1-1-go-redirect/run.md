# RUN 2026-10-18-s1-1-go-redirect
request:      Implement slice 1: #19 S1.1 Visitor goes to a shop through a logged redirect. Close: remove the stale "§ Stack reads not chosen" conditions at phases.md:14, :32, :43 and architecture.md:22 (the stack is recorded), and reword project.md:12-13 to match.
agentic_root: C:\projects\investments\.agentic
project:      projects/los-tres/project.md
story:        NONE
status:       CLOSED
phase:        close
plan:         v2
budget:       10 — design 1 + build 3 (backend, frontend, test) + integration 1 + review 1 + close docs 1 + protocol-lint 1 (close edits network files)
spent:        10
next:         none — CLOSED
gates:        integration PASS (05) · review PASS (06) · protocol-lint FAIL (08) then PASS (10)

## Phases
| phase | lane | fires when | state |
|---|---|---|---|
| ground-truth | recon | the request names existing code or rests on an unverified claim about current behaviour | not triggered (prior artifacts cover the offer and product-page area: runs/2026-10-17-tracer-bullet-b/01-design.md, 02-backend.md, 03-frontend.md; design reads the code it plans against) |
| framing | product | the request adds a user-facing surface, changes what one is for, or mvp.md does not exist yet | not triggered (surface already framed and approved: runs/2026-10-17-mvp-backlog-revision/01-product.md § Backlog S1.1, D-1; #19 moved to Ready by the human) |
| specification | story | framing produced scope no approved brief covers, and the slice crosses more than one lane's contract | not triggered (the approved brief runs/2026-10-17-mvp-backlog-revision/01-product.md § S1.1 is the specification; #19 marks Story file: no) |
| design | design | the change crosses the frontend/backend contract, or more than one build lane touches it | satisfied — 01 |
| build | backend, frontend, test | anything that edits repo code, tests or docs/** | satisfied — 02, 03, 04 |
| verify | integration | any build lane was dispatched | satisfied — 05 |
| verify | review | the run carries a story whose acceptance criteria someone must accept | satisfied — 06 |
| close | docs | always | satisfied — 07 |

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | design | DESIGN | tech-lead | sonnet | 01-design.md | DONE | — |
| 02 | backend | — | backend-engineer | sonnet | 02-backend.md | DONE | — |
| 03 | frontend | — | frontend-engineer | sonnet | 03-frontend.md | DONE | — |
| 04 | test | — | test-engineer | sonnet | 04-test.md | DONE | — |
| 05 | integration | INTEGRATION | tech-lead | sonnet | 05-integration.md | DONE | PASS |
| 06 | review | — | reviewer | sonnet | 06-review.md | DONE | PASS |
| 07 | docs | — | docs-engineer | sonnet | 07-docs.md | DONE | — |
| 08 | protocol-lint | — | protocol-linter | opus | 08-protocol-lint.md | DONE | FAIL |
| 09 | docs | — | docs-engineer | sonnet | 09-docs.md | DONE | — |
| 10 | protocol-lint | — | protocol-linter | opus | 10-protocol-lint.md | DONE | PASS |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| should_fix | CR-5 | cr/CR-5.md | fixed by 09-docs; kept here because check_report.py requires an Open row for a SHOULD_FIX CR | CARRIED |
| should_fix | CR-6 | cr/CR-6.md | partly fixed by 09-docs (backend.md:62-65 still trails, 10-protocol-lint); kept here because check_report.py requires an Open row for a SHOULD_FIX CR | CARRIED |
| should_fix | CR-7 | cr/CR-7.md | fixed by 09-docs; kept here because check_report.py requires an Open row for a SHOULD_FIX CR | CARRIED |
| should_fix | CR-8 | cr/CR-8.md | fixed by 09-docs; kept here because check_report.py requires an Open row for a SHOULD_FIX CR | CARRIED |
| risk | 07-docs | 07-docs.md § handoff | leftover stack wording: project.md:119 'stack proposals', capabilities/docs.md:5, phases.md build row | CARRIED |
| should_fix | 10-protocol-lint | 10-protocol-lint.md § handoff (backend.md:62-65) | four trailing facts after the (5) sub-bullets read as part of :61 | CARRIED |
| should_fix | 10-protocol-lint | 10-protocol-lint.md § handoff (testing.md:82) | moved page.route bullet carries three facts | CARRIED |
| should_fix | orchestrator | scripts/check_report.py check_cr | requires an Open row for a fixed SHOULD_FIX CR, contradicting orchestrator.md § 1 'Open holds what is still open' | CARRIED |

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|
| decision | 01-design | decisions.md § D-2 (human: yes); applied by close docs | optional decision 0009 addendum needs the human's yes |
| contract_note | 01-design | 02-backend (comment updated) | PublicOffer.offerId comment says no link may render; stale |
| contract_note | 01-design | 02-backend (migration 0001; test lane pins columns) | clicks table + migration 0001 is the shape S1.3 reads |
| contract_note | 01-design | 03-frontend (OfferRow goHref/goLabel, rel sponsored nofollow) | OfferRow gains goHref/goLabel; existing no-link unit test flips on purpose |
| contract_note | 01-design | 03-frontend (Product.goToShop + messages.test.ts) | messages/es-ES.json gains Product.goToShop; messages.test.ts must list it |
| contract_note | 03-frontend | 04-test (product.spec.ts case rewritten) | tests/e2e/product.spec.ts no-link case is stale; order 04 rewrites it |
| contract_note | 01-design | 04-test (go-redirect, go.spec pin the contract; S6.2 robots carried via #39 note at close) | /go/<offer> is a new public contract; frontend link, e2e and S6.2 robots depend on it |
| contract_note | 01-design | merged into 02-backend.md § contract_notes (on delete restrict) row | clicks.offer_id on delete restrict: S3.3 must not hard-delete offers with clicks |
| contract_note | 02-backend | 04-test (seams.test.ts pins offers.url readers) | only offer-target.ts may read offers.url outside src/db and importer; test lane seam scan pins it |
| risk | 04-test | 05-integration (§ Severity call on the e2e click-through: non-blocking, accepted) | e2e asserts the request to the shop host, not a loaded shop page; deviates from § Tests owed |
| contract_note | 02-backend | carried to the later stories as tracker comments on #28 S3.3, #43 S7.4, #44 S7.5 | clicks FKs to offer, shop and product are restrict: S3.3, S7.4/S7.5 must not hard-delete clicked rows |
| contract_note | 01-design | carried to #50 S9.1 as a tracker comment | S9.1 reverse proxy must pass original Host or source_page is always null |

## Rounds
| finding | lane | round | of | caused by |
|---|---|---|---|---|
| CR-1 | docs | 1 | 2 | — |
| CR-2 | docs | 1 | 2 | — |
| CR-3 | docs | 1 | 2 | — |
| CR-4 | docs | 1 | 2 | — |
| CR-5 | docs | 1 | 2 | — |
| CR-6 | docs | 1 | 2 | — |
| CR-7 | docs | 1 | 2 | — |
| CR-8 | docs | 1 | 2 | — |

## Replans
| plan | because | change |
|---|---|---|
| v2 | 08-protocol-lint FAIL: 4 blocking contradictions in edited network files | docs fix (09) + re-lint (10); budget 8 → 10 |
