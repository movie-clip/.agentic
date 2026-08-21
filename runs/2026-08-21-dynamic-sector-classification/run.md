# RUN 2026-08-21-dynamic-sector-classification
request:      Research and find a solution to the problem occurring when an unknown ETF ticker is added — it falls into "Other" sector, but I want to have a mechanism how to dynamically understand to which sector ETF or company belongs. right now using file from project docs/IB2026.csv SBIO will be in "Others" sector, but it is Health Care ETF, biotech ETF
agentic_root: C:\projects\investments\.agentic
story:        docs/product/stories/US-37.1-dynamic-equity-sector-classification.md
status:       CLOSED
route:        full
express:      no

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | product | — | producer | sonnet | 01-delivery-brief.md | DONE | — |
| 02 | quant | RESEARCH | quant-analyst | opus | 02-quant-research.md | DONE | — |
| 03 | story | — | story-author | sonnet | 03-story.md | DONE | — |
| 04 | story | — | story-author | sonnet | 04-story-renumber.md | PARTIAL | — |
| 05 | design | DESIGN | tech-lead | sonnet | 05-technical-plan.md | DONE | — |
| 06 | backend | T-37.1.1 | backend-engineer | sonnet | 06-backend.md | DONE | — |
| 07 | backend | T-37.1.2 | backend-engineer | sonnet | 07-backend.md | DONE | — |
| 08 | docs | T-37.1.3 | docs-engineer | sonnet | 08-docs.md | DONE | — |
| 09 | test | T-37.1.4 | test-engineer | sonnet | 09-test.md | DONE | — |
| 10 | quant-audit | AUDIT | quant-analyst | opus | 10-quant-audit.md | DONE | FAIL |
| 11 | backend | CR-1 | backend-engineer | sonnet | 11-backend-cr1.md | DONE | — |
| 12 | test | T-37.1.4 (CR-1) | test-engineer | sonnet | 12-test-cr1.md | DONE | — |
| 13 | quant-audit | AUDIT (recheck) | quant-analyst | opus | 13-quant-audit-recheck.md | DONE | PASS |
| 14 | integration | INTEGRATION | tech-lead | sonnet | 14-integration.md | DONE | PASS |
| 15 | review | — | reviewer | sonnet | 15-review.md | DONE | PASS |
| 16 | docs | close-out | docs-engineer | sonnet | 16-docs-closeout.md | DONE | — |
| 17 | docs | close-out (slice log) | docs-engineer | sonnet | 17-docs-slicelog.md | DONE | — |
| 18 | docs | housekeeping | test-engineer | sonnet | 18-cleanup.md | PARTIAL | — |
| 19 | docs | housekeeping | test-engineer | sonnet | 19-cleanup2.md | DONE | — |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| trigger_correction | 01-delivery-brief | § Trigger-case correction | SBIO already classifies Health Care today; not the real bug | CARRIED |
| finding | 01-delivery-brief | § Findings F-A | equities never get dynamic sector classification, ever (registry.py:256-265) | OPEN |
| finding | 01-delivery-brief | § Findings F-B | ETF look-through constituents never get dynamic classification (risk.py:1031-1038) | OPEN |
| finding | 01-delivery-brief | § Findings F-C | FMP profile already returns `sector`; enrichment deliberately discards it (US-14.3) | OPEN |
| prior_decision | 01-delivery-brief | § Prior recorded decision | US-14.3 explicitly declined to bypass keyword classifier w/ FMP sector | CARRIED |
| tech_debt | 01-delivery-brief | § Tech-debt overlap | registry.py keyword classifier (epic-24, open, unresolved) | OPEN |
| tech_debt | 01-delivery-brief | § Tech-debt overlap | risk.py duplicated proxy-ticker sector inference (epic-24, open, unresolved) | OPEN |
| open_decision | 01-delivery-brief | § Open decisions #1 | trust rung — ANSWERED: `classification_source` enum, not `verified` | ABSORBED |
| open_decision | 01-delivery-brief | § Open decisions #2 | data source — ANSWERED: FMP live-verified for INTU/PANW/VICI/SPCX | ABSORBED |
| open_decision | 01-delivery-brief | § Open decisions #3 | scope — ANSWERED: human chose F-A (equities) only | ABSORBED |
| open_decision | 01-delivery-brief | § Open decisions #4 | caching — ANSWERED: widen TTL off 300s quote tier, should not block | ABSORBED |
| open_decision | 01-delivery-brief | § Open decisions #5 | no-coverage fallback — ANSWERED: explicit None, not "Other" string | ABSORBED |
| open_decision | 01-delivery-brief | § Open decisions #6 | US-14.3 precedent — ANSWERED: does not transfer as blanket rule to F-A | ABSORBED |
| human_decision | user | run.md | human chose narrower scope: F-A (equities) only, skip audit-first shape and F-B (look-through) | CARRIED |
| deferred | 01-delivery-brief | § Findings F-B | ETF look-through dynamic classification — deliberately deferred, not this run | CARRIED |
| deferred | 01-delivery-brief | § Proposed shape | audit-first / impact-quantification story — deliberately deferred, not this run | CARRIED |
| finding | 02-quant-research | § Identity risk | ticker-collision trap (DFND/CIBR/SEMI/DFNS) — FMP lookup MUST be ISIN-gated | OPEN |
| finding | 02-quant-research | § Sector taxonomy normalization | FMP sector strings differ from project's on 5/11 GICS sectors — mapping table mandatory | OPEN |
| contract_note | 02-quant-research | § Trust-class analysis | exposure-fields.md sector rows lack per-instrument provenance today | OPEN |
| contract_note | 02-quant-research | § Methodology-doc gap | financial-methodology.md has no section on sector classification sourcing | OPEN |
| should_fix | 02-quant-research | § Caching recommendation | get_profile() 300s quote-TTL too short for a multi-year-cadence fact | OPEN |
| risk | 02-quant-research | § risks | SPCX resolves to a live tradeable FMP profile though not known public — data-quality anomaly, not chased | CARRIED |
| risk | 02-quant-research | § risks | ETF-side FMP sector unreliable as constituent proxy — F-B territory, not cleared | CARRIED |
| risk | 02-quant-research | § risks | get_company_profile `cached` meta flag hardcoded True (market_data.py:474) — noticed, unrelated to F-A | CARRIED |
| open_decision | 03-story | story § Open decisions #1 | SETTLED by 05-technical-plan: `classification_source: Literal["static","fmp_identity_confirmed","unavailable"]\|None` | ABSORBED |
| open_decision | 03-story | story § Open decisions #2 | SETTLED by 05-technical-plan: sector stays None at domain layer, "Unclassified" sentinel only at overview.py seam | ABSORBED |
| open_decision | 03-story | story § Open decisions #3 | SETTLED by 05-technical-plan: ISIN-mismatch collapses into "unavailable" (deliberate, nothing downstream reads finer state) | ABSORBED |
| open_decision | 03-story | story § Open decisions #4 | SETTLED by 05-technical-plan: pragmatic v1 — widen get_profile() TTL to 30d, not a persisted record | ABSORBED |
| filing_note | 03-story | story "Filing note" | epic-24 reopening — RESOLVED: human chose new dedicated Epic 37 instead | ABSORBED |
| judgment_call | 03-story | story "Notes / decisions" | no frontend ticket — CONFIRMED by 05-technical-plan after reading ExposurePanel.tsx in full | ABSORBED |
| contract_note | 05-technical-plan | § Contract | `Instrument.classification_source` new field (backend-internal, no TS mirror needed) | OPEN |
| contract_note | 05-technical-plan | § Contract | `PortfolioOverview.sector_allocation`/`sector_position_breakdown` gain "Unclassified" value, no type change | OPEN |
| contract_note | 05-technical-plan | § Contract | exposure-fields.md sector rows need "Unclassified" bucket note — T-37.1.3 | OPEN |
| contract_note | 05-technical-plan | § Contract | financial-methodology.md needs new "Sector/Industry Classification" section — T-37.1.3 | OPEN |
| decision | 05-technical-plan | § Decisions (additional) | FMP dependency is opt-in via keyword-only `market_data` param — risk.py callers unaffected, zero added I/O | ABSORBED |
| risk | 05-technical-plan | § Risks | ISIN-mismatch vs no-coverage collapse loses field-level debug signal (code comments only) | CARRIED |
| risk | 05-technical-plan | § Risks | 30-day TTL makes a transient empty FMP response sticky for up to 30 days | CARRIED |
| risk | 05-technical-plan | § Risks | goldens: unconfirmed whether INTU/PANW/VICI/SPCX are open positions in committed snapshot — T-37.1.4 must re-verify before pinning | OPEN |
| risk | 05-technical-plan | § Risks | taxonomy map covers only the 11 verified sectors; a 12th FMP string falls through correctly but untested beyond 5 pinned pairs | CARRIED |
| contract_note | 06-backend | § contract_notes | classification_source backend-internal, no TS mirror needed (confirms plan) | ABSORBED |
| finding | 06-backend | § handoff | real import cycle registry<->equity_sector_resolution<->instrument_identity resolved via lazy import — next lanes must not move it to module level | OPEN |
| finding | 06-backend | § handoff | _merge_known_instrument_metadata no longer short-circuits to same object instance when no other updates — test-engineer must account for this | OPEN |
| handoff | 06-backend | § handoff | resolve_equity_sector's market_data param is duck-typed for mocking — any object with get_company_profile(symbol) | OPEN |
| handoff | 07-backend | § handoff | overview.py now builds its own MarketDataService() — needs planned _mock_overview_engine_market_data conftest fixture | OPEN |
| handoff | 07-backend | § handoff | AC9 needs regression: unclassified equity in distinct "Unclassified" bucket, weight included in totals, never "Other" | OPEN |
| risk | 08-docs | § risks | new methodology section is normally flag-for-human per docs pack convention, not auto-written — this order directed writing it directly; recommend human review before treating final | OPEN |
| finding | 09-test | § risks | INTU/PANW/VICI/SPCX confirmed CLOSED positions (net-zero qty) in current docs/IB2026.csv — golden pins correctly NOT added | ABSORBED |
| risk | 09-test | § risks | get_company_profile fake/stub pattern now duplicated across 3 test files, no shared scaffolding — fixtures.py candidate, out of scope | CARRIED |
| should_fix | run.md | § Open (tombstone) | old US-24.12 tombstone still needs deletion — no lane in this run has filesystem-delete access (docs/story-author lack Bash) | ABSORBED (deleted by 19-cleanup2) |
| finding | 10-quant-audit | cr/CR-1.md | MATERIAL: no-imported-instrument catch-all still hardcodes "Other" (registry.py:337-346), violates AC9 — FIXED by 11-backend-cr1 | ABSORBED |
| should_fix | 11-backend-cr1 | § handoff | no test pins "Unclassified" for the zero-matching-instrument catch-all path specifically — regression test recommended | ABSORBED |
| infra | dispatch 12 | (no artifact) | first test-engineer dispatch for CR-1 regression test failed mid-task (session/API limit) before writing anything — confirmed clean via git status/ast-parse/grep, no partial edit; re-dispatched | ABSORBED |
| should_fix | 10-quant-audit | § Findings FINDING 2 | MINOR: taxonomy lookup is case/whitespace-sensitive, untested against FMP casing drift — not blocking | CARRIED |
| should_fix | 14-integration | § risks | design-pass blind spot pattern: trace every producer of a seam's input, not just the seam's own null-check — noted for future design passes | CARRIED |
| open_decision | 16-docs-closeout | § Draft slice-log line | slice-log one-liner — human approved, written verbatim by 17-docs-slicelog | ABSORBED |
| should_fix | 16-docs-closeout | § handoff | epic-37 PRD's own "Status:" header still reads "Backlog" | ABSORBED (fixed by 18-cleanup) |
| risk | 08-docs / 16-docs-closeout | § risks | new financial-methodology.md section was auto-written, not flag-for-human per docs pack convention — recommend human review before treating final | CARRIED |
| risk | 10-quant-audit | § risks | misconfigured FMP_API_KEY silently degrades every non-static equity with zero disclosure — pre-existing, not new to this audit | CARRIED |
| contract_note | 08-docs | § contract_notes | docs lane is terminus — all pending docs notes from 02/05/06/07 landed, nothing further downstream | ABSORBED |
| finding | 03-story | story § Context | analytics/overview.py:50 has its own get_sector() fallback that would silently re-coerce None back to "Other" — folded into T-37.1.2 | ABSORBED |
| should_fix | 04-story-renumber | docs/product/stories/US-24.12-dynamic-equity-sector-classification.md | old US-24.12 file could not be deleted (story-author has no Bash/delete tool) — left as a tombstone | ABSORBED (deleted by 19-cleanup2) |
| infra | 18-cleanup | (n/a) | first deletion attempt correctly REFUSED — file had a full duplicate body behind the banner, failing its own stop condition; orchestrator verified content directly, confirmed safe, re-dispatched | ABSORBED |

## Rounds
| finding | lane | round | of |
|---|---|---|---|
| CR-1 | backend | 1 | 2 |

## Cost
| metric | value |
|---|---|
| dispatches | 19 |
| rounds | 1 |
| by model | sonnet 16 · opus 3 |
| escalations | none |

## Cost note
Full suite green post T-37.1.4: backend 840 passed, frontend 331 passed (37 files),
tsc clean, dead-code gate clean, dashboardGoldens.ts unchanged.
