# RUN 2026-09-30-import-critical-fixes
request:      okay, put all your findings into docs/tech-debt-register.md, and then start working to fix critical problems
agentic_root: C:\projects\investments\.agentic
project:      projects/portfolio/project.md
story:        docs/product/stories/US-46.1..US-46.4
status:       BLOCKED
phase:        build
plan:         v4
budget:       19 — design split build into 9 orders (BE-1..BE-4, FE-1, FE-2, T-1..T-3) + story amendment for D-7 (1) + protocol-lint gate (1, 02 emitted a pack correction) + framing (1) + quant RESEARCH (1) + story (1) + design (1) + build 3 lanes (backend, frontend, test) + 3 gates (quant-audit, integration, review) + close docs (1); minus ground-truth (covered by prior run artifacts)
spent:        13
blocked_on:   human H-1 golden recapture + build_roadmap.py (D-10)
next:         after H-1: dispatch 14 test T-2; then gates quant-audit -> integration -> review
gates:        quant-audit pending · integration pending · review pending · protocol-lint pending (pack-corrections.md has 1 entry)

## Phases
| phase | lane | fires when | state |
|---|---|---|---|
| ground-truth | recon | the area is unfamiliar, or the run would otherwise build on an unverified claim | not triggered (prior artifacts cover the area: runs/2026-09-29-statement-import-audit/01-recon.md and 02-quant-audit.md) |
| framing | product | the request changes what the product does: new capability, new scope, or a re-prioritisation | satisfied — 01 |
| specification | quant (RESEARCH) | the work changes a trust classification | satisfied — 02 |
| specification | story | framing produced scope no approved story covers and the slice needs ticketing (two build lanes, schema contract crossing) | satisfied — 03, 04 |
| design | design | the change crosses a contract boundary, or more than one build lane touches it | satisfied — 05 |
| build | backend, frontend, test | anything that edits the repo | pending |
| verify | quant-audit | any lane touched a formula, a return basis or a trust label | pending |
| verify | integration | any build lane was dispatched | pending |
| verify | review | the run carries a story whose acceptance criteria someone must accept | pending |
| close | docs | always | pending |

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | product | — | producer | sonnet | 01-product.md | DONE | — |
| 02 | quant | RESEARCH | quantitative-researcher | opus | 02-quant.md | DONE | — |
| 03 | story | — | story-author | sonnet | 03-story.md | DONE | — |
| 04 | story | — | story-author | sonnet | 04-story.md | DONE | — |
| 05 | design | DESIGN | tech-lead | sonnet | 05-design.md | DONE | — |
| 07 | backend | — | backend-engineer | sonnet | 07-backend.md | DONE | — |
| 06 | backend | — | backend-engineer | sonnet | 06-backend.md | DONE | — |
| 08 | backend | — | backend-engineer | sonnet | 08-backend.md | DONE | — |
| 09 | frontend | — | frontend-engineer | sonnet | 09-frontend.md | DONE | — |
| 10 | test | — | test-engineer | sonnet | 10-test.md | PARTIAL | — |
| 12 | backend | — | backend-engineer | sonnet | 12-backend.md | DONE | — |
| 11 | frontend | — | frontend-engineer | sonnet | 11-frontend.md | PARTIAL | — |
| 13 | test | — | test-engineer | sonnet | 13-test.md | DONE | — |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| contract_note | 01-product | 01-product.md#contract_notes-1 | F4 makes cost_basis/unrealized_pnl Optional; types.ts + new imports-fields contract doc | OPEN |
| contract_note | 01-product | 01-product.md#contract_notes-2 | F2/F3 stories must cite import-admission-fields.md and methodology merge section | OPEN |
| contract_note | 02-quant | 02-quant.md#contract_notes-1 | ImportedPosition cost_basis/unrealized_pnl -> optional float; no imports contract doc | OPEN |
| contract_note | 02-quant | 02-quant.md#contract_notes-2 | PortfolioOverview totals + top_positions unrealized_pnl nullable; types.ts:56-57,61 | OPEN |
| contract_note | 02-quant | 02-quant.md#contract_notes-3 | EnrichedPosition.unrealized_pnl non-nullable; no production caller | OPEN |
| contract_note | 02-quant | 02-quant.md#contract_notes-4 | import-admission-fields.md needs combined-snapshot section; combine response carries admission | OPEN |
| contract_note | 02-quant | 02-quant.md#contract_notes-5 | FF dashboard goldens + golden_market_data.json need live FMP recapture after F1 | OPEN |
| finding | 02-quant | 02-quant.md#risks | monthly returns include terminal reconciliation adjustment (-0.87% vs -1.20%); needs register row | OPEN |
| register_row | decisions.md D-8 | decisions.md#D-8 | IB malformed Cost Basis cell drops whole position; register at close | OPEN |
| register_row | decisions.md D-4 | decisions.md#D-4 | FF replay period-start anchoring deferred; register at close | OPEN |
| contract_note | 04-story | 04-story.md#contract_notes-1 | saved-node re-derive shared by T-46.1.3 and T-46.3.3; design decides | OPEN |
| contract_note | 07-backend | 07-backend.md#contract_notes-1 | FF2026 now 7 ledger entries; E1 + single-charge rule docs at close (T-46.2.4) | OPEN |
| contract_note | 07-backend | 07-backend.md#contract_notes-2 | frozen market data misses FF window; H-1 required | OPEN |
| contract_note | 06-backend | 06-backend.md#contract_notes-4..7 | contract docs, architecture route list, methodology E2/E3 lag; docs close-out | OPEN |
| risk | 06-backend | 06-backend.md#risks-2,3 | shared-account guard also refuses identical combined inputs; combine-snapshots now 400s chained input | OPEN |
| contract_note | 08-backend | 08-backend.md#contract_notes-4,5,7 | imports-fields.md create, methodology E4, exposure contract nullability; docs close-out | OPEN |
| risk | 08-backend | 08-backend.md#risks-1 | exposure_engine.py annotation edited outside fence (no logic); integration to judge | OPEN |
| risk | 08-backend | 08-backend.md#risks-5 | persisted override lacking cost_basis_trust reads stated; only D-5 re-derive (FE-2/BE-4) fixes | OPEN |
| contract_note | 09-frontend | 09-frontend.md#contract_notes-1,2,4 | import-admission-fields, imports-fields (constituents, derivationVersion), dashboard-fields combine route; docs close | OPEN |
| risk | 09-frontend | 09-frontend.md#risks-1 | processImportedFiles catch edited outside add/replace branches; integration to judge | OPEN |
| risk | 09-frontend | 09-frontend.md#risks-5 | legacy base w/o constituents + same-account add hits chained-input guard; FE-2 must cover | OPEN |
| partial | 10-test | 10-test.md#verification | 4 reds: FF dashboard truth (T-2), golden determinism x2 (H-1), ROADMAP.md stale (build_roadmap.py) | OPEN |
| risk | 10-test | 10-test.md#risks-1 | clean + totals-less distinct-account combine recompute is withheld not degraded (pre-existing merge) | OPEN |
| contract_note | 12-backend | 12-backend.md#contract_notes-1 | imports-fields.md + E4 must state FF scrub on analyze-combined (D-12); docs close | OPEN |
| risk | 12-backend | 12-backend.md#risks-3 | /combine-snapshots route not scrubbed (desktop no longer calls it); integration to judge | OPEN |
| contract_note | 11-frontend | 11-frontend.md#contract_notes-1,2 | imports-fields + import-admission-fields must document on-load re-derive and carried origin; docs close | OPEN |
| risk | 11-frontend | 11-frontend.md#risks-3 | dirty WorkingDraft on legacy node keeps doubled figures; review vs US-46.1 AC 12 | OPEN |
| risk | 11-frontend | 11-frontend.md#risks-1 | legacy multi-account base: later same-account add refused, user must re-import | OPEN |
| risk | 11-frontend | 11-frontend.md#risks-9 | lane ran rm on its own temp scratch test inside src/; nothing remains | OPEN |
| finding | 13-test | 13-test.md#risks-2 | portfolioSnapshot.ts:31 sums null quantities to 0 (pre-existing); register at close | OPEN |
| risk | 13-test | 13-test.md#risks-1 | portfolioWorkspaceStorage.ts:346 null admission falls back to root label; unreachable today | OPEN |

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|
| contract_note | 06-backend | 09-frontend | types.ts lags C3/C4 rollup, constituent_snapshots, analyze-combined request; FE-1 |
| contract_note | 08-backend | 09-frontend | types.ts PortfolioOverview nullable totals + cost_basis_trust; FE-1 |
| note | orchestrator | dismissed — head derived and validated, no work dropped | lane head headline 201 chars; head re-derived with --emit-head, counts matched |
| handoff | 07-backend | 10-test (FF pins updated) | test_importer.py:287/:332 red; stale 'grouped sell trade' description text |
| partial | 11-frontend | 13-test (desktop 470/470 green) | 26 vitest reds (9 overlay, 5 add, 12 restore fixtures lack derivationVersion) for T-3 |

## Rounds
| finding | lane | round | of | caused by |
|---|---|---|---|---|

## Replans
| plan | because | change |
|---|---|---|
| v2 | 02-quant emitted a pack correction, so protocol-lint becomes accountable; 01-product split F1-F4 into four stories (drafted in one story dispatch) | budget 11 -> 12 |
| v3 | human ruling D-7 (re-derive saved nodes on load) adds ACs + persistence tickets to US-46.1/46.3, which only the story lane may write | budget 12 -> 13 |
| v4 | 05-design split build into 9 lane orders (BE-1,BE-2,BE-3,FE-1,T-1,T-2,FE-2,BE-4,T-3) where v3 assumed 3; human ruled BE-4 in (D-12) and ceiling 30 (D-13) | budget 13 -> 19 |
