# RUN 2026-08-25-leftover-findings-fold-in
request:      take all 3 points and any other left over tasks and combine
              them into 1 story 1 epic
agentic_root: C:\projects\investments\.agentic
story:        NONE
status:       CLOSED
next:         none — CLOSED
route:        review
express:      no

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | recon | — | scout | haiku | 01-scout.md | DONE | — |
| 02 | product | — | producer | sonnet | 02-delivery-brief.md | DONE | — |
| 03 | quant | RESEARCH | quant-analyst | opus | 03-quant-research.md | DONE | — |
| 04 | story | — | story-author | sonnet | 04-stories.md | DONE | — |
| 05 | design | DESIGN | tech-lead | sonnet | 05-technical-plan.md | DONE | — |
| T-40.1.1 | docs | T-40.1.1 | docs-engineer | sonnet | T-40.1.1-docs.md | DONE | — |
| T-40.1.2 | frontend | T-40.1.2 | frontend-engineer | sonnet | T-40.1.2-frontend.md | DONE | — |
| T-40.1.3+T-40.2.2a | backend | — | backend-engineer | sonnet | T-40.1.3-T-40.2.2a-backend.md | DONE | — |
| T-40.2.2b | frontend | T-40.2.2b | frontend-engineer | sonnet | T-40.2.2b-frontend.md | PARTIAL | — |
| T-40.1.4+T-40.2.3 | test | — | test-engineer | sonnet | T-40.1.4-T-40.2.3-test.md | DONE | — |
| 06 | quant | AUDIT | quant-analyst | opus | AUDIT-quant.md | DONE | FAIL |
| 07 | backend | — | backend-engineer | sonnet | 07-backend.md | DONE | — |
| 08 | test | — | test-engineer | sonnet | 08-test.md | DONE | — |
| 09 | docs | — | docs-engineer | sonnet | 09-docs.md | PARTIAL | — |
| 10 | quant | AUDIT | quant-analyst | opus | 10-quant-reaudit.md | DONE | PASS |
| 11 | integration | INTEGRATION | tech-lead | sonnet | 11-integration.md | DONE | PASS |
| 12 | docs | — | docs-engineer | sonnet | 12-docs-closeout.md | PARTIAL | — |
| 13 | review | — | reviewer | sonnet | 13-review.md | DONE | PASS |
| 14 | docs | — | docs-engineer | sonnet | 14-docs-prd.md | DONE | — |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| protocol_note | 01-scout | 01-head.txt | brief failed to name 6 of its own sections per validator; orchestrator read full artifact directly, content coherent and complete | ABSORBED |
| finding | 01-scout | § Other doc candidates ruled out | "3 points" confirmed = 3 of the 4 CARRIED findings in the just-closed SBIO run's Open table; no other doc enumerates exactly 3 open items | ABSORBED |
| finding | 01-scout | § The 3 CARRIED items + § 4th scope item | all 4 items (staleness-signal UX gap, run_metadata staleness residual, add_snapshot lossy mode, risk.py market_data arg) independently reconfirmed live in current code, none tracked in tech-debt-register.md or epic-roadmap.md | ABSORBED |
| finding | 01-scout | § Other open/carried items | 2 more prior-run leftovers found and reconfirmed live: RecordingMarketData missing get_company_profile/get_etf_sector_weightings (Epic 39), dead market_data param in _build_shared_sector_overlap (Epic 38) | ABSORBED |
| finding | 01-scout | § tech-debt-register open rows, § epic-roadmap Open items | a large, PRE-EXISTING, unrelated backlog also exists (~15 tech-debt-register rows, mostly tiny epic-24-era hardcoded literals; US-26.3/26.4; 3 Epic-34 findings; Epic-36 carries; dependency advisories) — distinct from this week's "leftover" items, not something the user's phrasing obviously intended to sweep in | CARRIED |
| finding | 01-scout | § Blast-radius / conflict notes | no direct code conflicts between the 4 in-scope items (3 different files/layers); items 2+4 share a file (risk.py-adjacent modules) but not a function — producer may want to weigh bundling | ABSORBED |
| finding | 02-delivery-brief | § Placement | new epic verdict, sibling to Epic 38/39, following the same never-reopen-a-closed-epic precedent used 3 times running | ABSORBED |
| finding | 02-delivery-brief | § Stories | 2 stories recommended over literal 1 — items 1+2 (staleness-signal completeness, quant-gated) vs item 3 (add_snapshot data loss, needs its own DESIGN pass, deferred twice already) — bundling all 3 into one story judged not one reviewable slice | ABSORBED |
| finding | 02-delivery-brief | § Stories, Item 4 | risk.py market_data kwarg recommended NOT a story — confirmed inert, not express-eligible (analytics/ disqualifier), routes to tech-debt-register or ticket-of-opportunity | ABSORBED |
| human_decision | user | this turn | epic title accepted verbatim: "Snapshot Trust & Fidelity Follow-Through" | ABSORBED |
| human_decision | user | this turn | 2 stories confirmed (not literal 1) | ABSORBED |
| human_decision | user | this turn | both extra leftovers (RecordingMarketData gap, dead market_data param) included in this epic's scope — ticket placement left to story-author/tech-lead | ABSORBED |
| human_decision | user | this turn | large pre-existing tech-debt-register/epic-roadmap backlog excluded from this epic | ABSORBED |
| protocol_note | 03-quant-research | 03-head.txt | 5 handoff/risk/contract_note bullets exceeded the 400-char hard limit; quant-analyst has Bash but didn't self-check — orchestrator read full artifact directly, content coherent | ABSORBED |
| finding | 03-quant-research | § Fix direction | recommend option (b): retire run_metadata.source_status/.confidence as a trust source (contract-doc note + preventive regression test) rather than extending the freeze mechanism (option a) — no backend/schema change needed, fields are dormant (zero current consumers) and redundant with already-frozen availability | ABSORBED |
| finding | 03-quant-research | § Same bug class? | materially different from Finding 1: no live consumer reads these fields today (exhaustive grep) — MATERIAL/preventive, not CRITICAL/urgent | ABSORBED |
| finding | 03-quant-research | § Duplication finding | genuine code duplication independent of the staleness question: _build_exposure_source_status separately re-implements _build_exposure_availability's identical conditional logic, and calls the same _classify_benchmark_holdings_support twice — worth flagging to tech-lead DESIGN as a simplification, not itself a correctness bug | ABSORBED |
| contract_note | 03-quant-research | docs/contracts/exposure-fields.md:37 | needs a sibling sentence: run_metadata.source_status.*/.confidence are always live, redundant with availability, must never be read as a trust source for a frozen node | ABSORBED |
| head_mismatch | 04-stories | 04-head.txt | head undercounted handoff (5 vs 6); one risks bullet exceeded the 400-char hard limit — orchestrator read full artifact directly, content clean | ABSORBED |
| finding | 04-stories | § risks | picker-label date source (US-40.1 AC1/AC2) deliberately left as an open design question for tech-lead — client-persisted field vs engine's per-render reproducibility metadata, which is only populated for the currently-active exposure result | ABSORBED |
| decision | 04-stories | § Notes / decisions | both extra leftovers placed under US-40.1 as a non-AC-traced Housekeeping ticket (T-40.1.3) rather than split — US-40.2 is frontend-only with no adjacency to either | ABSORBED |
| human_decision | user | this turn | both story drafts approved as presented, no changes requested | ABSORBED |
| validator_encoding | 05-technical-plan | 05-head.txt | check_report.py em-dash encoding mismatch (recurring quirk) — orchestrator read full artifact, content clean | ABSORBED |
| finding | 05-technical-plan | § Picker freeze-date | resolved: node.portfolioSnapshot.importedMeta.importedAt (client-persisted, present on every node) — NOT the engine's per-render reproducibility metadata, which would need an engine call per picker node | ABSORBED |
| finding | 05-technical-plan | § T-40.1.3 | dead market_data param confirmed NOT caught by detect_deadcode.py --strict today — routes to tech-debt-register.md instead of removal in this story | ABSORBED |
| finding | 05-technical-plan | § Duplication finding disposition | source_status/availability duplication NOTED, NOT TICKETED — touches core exposure-classification logic, needs quant-lane involvement, out of proportion for this doc-only story; routes to tech-debt-register.md | ABSORBED |
| finding | 05-technical-plan | § US-40.2 design | major deviation from order's client-side assumption: new backend endpoint (CombineImportedSnapshotsRequest schema + POST /portfolios/import/combine-snapshots route) reusing existing, already-tested combine_imported_snapshots — avoids porting ~250 lines of TWR-compounding/dedup merge math to TypeScript as a second, unaudited implementation | ABSORBED |
| human_decision | user | this turn | confirmed the backend-endpoint deviation for US-40.2 — proceed as designed | ABSORBED |
| contract_note | 05-technical-plan | docs/contracts/exposure-fields.md:38 | sibling sentence per T-40.1.1's exact spec — landed, confirmed by direct read | ABSORBED |
| head_mismatch | T-40.1.1-docs | T-40.1.1-head.txt | head claimed pack_corrections:1 but artifact has 0 (same shell-less-lane pattern seen repeatedly); orchestrator read full artifact, content clean | ABSORBED |
| contract_note | 05-technical-plan | dashboard-fields.md (docs-engineer's call) | new entry needed once T-40.2.2a's combine-snapshots route lands — landed, still open for docs close-out | ABSORBED |
| contract_note | T-40.1.3-T-40.2.2a-backend | apps/desktop/src/features/portfolio/types.ts | TS type for CombineImportedSnapshotsRequest needed — owned by T-40.2.2b (frontend), not this ticket | ABSORBED |
| finding | T-40.1.3-T-40.2.2a-backend | § verification | -k filter keywords didn't match new files by name (expected, no coverage exists yet); agent independently confirmed app imports cleanly with 28 routes registered (no new include_router needed) and dead-code gate clean | ABSORBED |
| validator_encoding | T-40.2.2b-frontend | T-40.2.2b-head.txt | check_report.py em-dash encoding mismatch again (same recurring quirk) — orchestrator read full artifact, content clean | ABSORBED |
| tests_expected_broken | T-40.2.2b-frontend | § risks | "refreshes dashboard...adding a statement snapshot" needs one more mocked fetch response (the new combine-snapshots call) — fixed by T-40.1.4+T-40.2.3 | ABSORBED |
| tests_expected_broken | T-40.2.2b-frontend | § risks | "shows base and child variant lineage" asserts the OLD no-date label — fixed by T-40.1.4+T-40.2.3 | ABSORBED |
| decision | T-40.2.2b-frontend | § contract_notes | no named TS interface for CombineImportedSnapshotsRequest — inline {snapshots} object, matching runImportedDiagnosticsEngine's existing no-wrapper convention | ABSORBED |
| finding | T-40.1.4-T-40.2.3-test | § risks | T-40.1.3's RecordingMarketData test coverage not added here (out of this order's scope, that ticket's own backend-engineer work) — flagged for orchestrator awareness, not a gap in this dispatch | CARRIED |
| validator_encoding | AUDIT-quant | AUDIT-head.txt | check_report.py em-dash detail-mismatch (recurring quirk) + 3 bullets 10-14 chars over the 200 soft target; orchestrator read full artifact, content clean and coherent | ABSORBED |
| finding | AUDIT-quant | § Finding 1 (MATERIAL) | combine_imported_snapshots double-counts same-account positions/NAV when account_id fails to parse on either input (reproduced 2x: both-None, one-None) — reachable via new add_snapshot flow; pre-existing bug in reused statement_importer.py:243-280, not new code | ABSORBED (fixed by 07-backend, re-audit PASS via 10-quant-reaudit) |
| finding | AUDIT-quant | § Finding 2 (MATERIAL) | financial-methodology.md has no section for combine_imported_snapshots' multi-statement merge (earliest starting_nav / latest terminal ending_nav / geometric TWR compounding) despite feeding the documented cash-anchor formula | ABSORBED (fixed by 09-docs, re-audit PASS via 10-quant-reaudit) |
| finding | AUDIT-quant | § US-40.1/US-40.2 verification | both halves of this epic's own new code independently re-verified clean: no findings, hand-computed 3-statement TWR chain matched to the decimal, AC3 degraded-path traced end to end | ABSORBED |
| protocol_note | 07-backend | 07-head.txt | validator failed on a non-standard "## Orchestrator brief" section this implementation report shouldn't carry (that format is for planning lanes) — content otherwise clean, orchestrator read full artifact | ABSORBED |
| finding | 07-backend | Fix Finding 1 | _validate_compatible_snapshots now raises ValueError on any falsy account_id in a >1-length combine; all 3 audit repro cases confirmed fixed via ad hoc script, 25 existing tests incl. 3-broker fixture pass unmodified | ABSORBED |
| decision | 07-backend | § Generalization judgment | fix applies the ambiguous-account-id guard to any-length combine (not just the 2-input add_snapshot case) since the same reasoning holds for N inputs — doesn't change any currently-tested behavior; will be checked by round-2 re-audit | ABSORBED (assessed SOUND by 10-quant-reaudit) |
| finding | 07-backend | § handoff | ValueError propagates through the existing route's HTTP 400 mapping unchanged, no route/schema edit needed | ABSORBED |
| finding | 08-test | § handoff | 3 permanent regressions added (latest-wins unaffected, both-falsy raises, one-falsy raises); only 2-input shape covered per DoD, 3+-input generalization not additionally tested | ABSORBED |
| finding | 08-test | § fixtures gotcha | statement_totals fixtures must set cash_total/stock_total explicitly — _merge_statement_totals derives ending_nav from their sum, ignores a bare ending_nav field; fixtures.py docstring doesn't mention this, minor doc-hygiene note only | ABSORBED (docstring added by 12-docs-closeout) |
| finding | 09-docs | § changed | new "## Multi-Statement Snapshot Merge" section added to financial-methodology.md (~line 2263), every claim re-verified against current post-CR-1 code by direct read, not transcribed from AUDIT-quant.md's pre-fix prose | ABSORBED |
| protocol_note | 09-docs | § risks | pack/order conflict per PROTOCOL.md's own documented rule: docs pack convention says new methodology sections are flag-for-human, not auto-write; order explicitly directed writing with a fully-specified DoD, lane correctly followed order + set PARTIAL + flagged conflict | ABSORBED |
| human_decision | user | this turn | accepted 09-docs' auto-written methodology section as-is (not re-routed for separate human review) — content independently re-verified against post-CR-1 code | ABSORBED |
| finding | 10-quant-reaudit | § Finding 1/2 re-audit | both MATERIAL findings independently re-verified CLOSED via fresh scripts (not trusting 07/09's own claims); N>2 distinct-account path confirmed not overcorrected; generalization judgment assessed SOUND (fail-closed is the only safe choice) | ABSORBED |
| finding | 10-quant-reaudit | § Finding 3 (new, MINOR) | financial-methodology.md's new TWR section doesn't document that a single None-TWR input nulls the whole compounded result rather than partial-compounding — undocumented edge case, not a formula error, non-blocking | ABSORBED (sentence added by 12-docs-closeout) |
| finding | 10-quant-reaudit | § risks | golden PDF-based multi-statement tests silently no-op (docs/IB2026.pdf, docs/U8516450_...pdf absent locally) — pre-existing test-infra gap, not introduced by this epic; re-auditor substituted independent synthetic scripts instead of trusting the skip | ABSORBED (tech-debt row added by 12-docs-closeout) |
| finding | 11-integration | § Close-out items | 6-item punch list for docs close-out, all non-blocking: (1) docs/contracts/ entry for combine-snapshots route, (2) tech-debt row for dead market_data param, (3) tech-debt row for source_status/availability duplication, (4) methodology doc missing Finding-3 null-TWR sentence, (5) fixtures.py docstring gap, (6) tech-debt row for missing golden PDF fixtures | ABSORBED (all 6 landed by 12-docs-closeout) |
| finding | 11-integration | § Unrelated uncommitted diff | 10 modified files (App.tsx hunk + BenchmarkPositioningCard + import_bootstrap/engine/composer.py etc.) predate this run (HEAD 59387c7, 2026-08-24 18:50) — a prior, already-audited epic's CR fix, uncommitted per "no agent commits" rule, shares no files with this epic's diff, run_all_tests.py green either way — flagged so the human splits commits rather than bundling both epics | CARRIED |
| finding | 12-docs-closeout | § changed | 9 DoD docs landed: roadmap Epic 40 section, current-product-state, both story files (Done, ACs/tickets ticked), story index, dashboard-fields.md combine-snapshots entry, 3 tech-debt-register rows, methodology Finding-3 sentence, fixtures.py docstring line | ABSORBED |
| protocol_note | 12-docs-closeout | § risks | same pack/order conflict pattern as 09-docs (methodology-doc edit followed explicit order over pack's flag-for-human convention), status PARTIAL — mirrors already-accepted 09-docs precedent this run | ABSORBED |
| finding | 12-docs-closeout | § risks, § handoff | gap: no reviewer ACCEPTANCE lane ran this run; both stories' ACs were ticked from tech-lead INTEGRATION's DoD cross-check + quant-audit PASS, not an independent AC-by-AC reviewer trace (unlike Epic 39's story, which cites one) | ABSORBED (filled by 13-review, PASS) |
| finding | 12-docs-closeout | § handoff | scope miss: this order excluded docs/product/prd/, so no Epic 40 PRD file was created — confirmed Epic 37/38/39 each have one (ls docs/product/prd/), so this breaks an established precedent, orchestrator's scoping error not docs-engineer's | ABSORBED (filled by 14-docs-prd) |
| human_decision | user | this turn | fill both close-out gaps now: dispatch reviewer ACCEPTANCE, then docs-engineer PRD backfill (sequential — PRD should reflect a confirmed-accepted epic) | ABSORBED |
| validator_encoding | 13-review | 13-head.txt | check_report.py em-dash detail-mismatch (recurring quirk, no other findings) — orchestrator read full artifact, content clean | ABSORBED |
| finding | 13-review | Acceptance verdict | all 6 US-40.1 ACs + 4 US-40.2 ACs independently traced to landed code/tests, genuinely SATISFIED — both stories' "Done" status confirmed earned, not just self-reported | ABSORBED |
| finding | 13-review | § risks | App.tsx:793's degraded-combination message example names only "differing base currency", not CR-1's newer account-identity failure mode — truthful/non-exhaustive wording, AC3 still met, non-blocking polish item | CARRIED |
| protocol_note | 14-docs-prd | 14-head.txt | validator FAIL on verification result NOT_RUN vs status DONE — expected shell-less-lane pattern (docs-engineer has no Bash), orchestrator independently ran the named command directly and confirmed the file exists (14559 bytes, 6 "## " headers) | ABSORBED |
| finding | 14-docs-prd | § changed | docs/product/prd/epic-40-snapshot-trust-and-fidelity-follow-through.md created, matching Epic 38/39's structure and filename convention; content sourced entirely from already-landed epic-roadmap.md/story files/AUDIT-quant.md/10-quant-reaudit.md, no new claims invented | ABSORBED |

## Rounds
| finding | lane | round | of |
|---|---|---|---|
| AUDIT-quant Finding 1 (account_id combine double-count) | backend-engineer | 1 (closed: PASS via 10-quant-reaudit) | 2 |
| AUDIT-quant Finding 2 (missing methodology section) | docs-engineer | 1 (closed: PASS via 10-quant-reaudit) | 2 |

## Cost
| metric | value |
|---|---|
| dispatches | 19 |
| rounds | 2 (AUDIT-quant Finding 1 + Finding 2, both closed round 1 of 2 via 10-quant-reaudit PASS) |
| by model | sonnet 15 · opus 3 · haiku 1 |
| escalations | none |
