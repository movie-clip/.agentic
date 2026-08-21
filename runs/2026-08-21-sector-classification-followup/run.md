# RUN 2026-08-21-sector-classification-followup
request:      Address the remaining, non-ETF-look-through findings surfaced during
              the US-37.1 run (2026-08-21-dynamic-sector-classification): the MINOR
              taxonomy case/whitespace-sensitivity finding from quant-audit, the
              MarketDataService.get_company_profile `cached` flag hardcoded True bug,
              and the FMP-profile mock/stub duplication across 3 test files. Explicitly
              excludes ETF look-through (F-B) and both epic-24 tech-debt entries.
agentic_root: C:\projects\investments\.agentic
story:        docs/product/stories/US-37.2-sector-classification-followups.md
status:       CLOSED
route:        story (lighter weight — no design pass, no quant-audit/integration gate per human's explicit approval)
express:      no

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | story | — | story-author | sonnet | 01-story.md | DONE | — |
| 02 | story | — | story-author | sonnet | 01-story.md (fix) | DONE | — |
| 03 | backend | T-37.2.1 | backend-engineer | sonnet | 03-backend.md | DONE | — |
| 04 | backend | T-37.2.2 | backend-engineer | sonnet | 04-backend.md | DONE | — |
| 05 | test | T-37.2.3 | test-engineer | sonnet | 05-test.md | DONE | — |
| 06 | test | T-37.2.4 | test-engineer | sonnet | 06-test.md | DONE | — |
| 07 | review | — | reviewer | sonnet | 07-review.md | DONE | PASS |
| 08 | docs | close-out | docs-engineer | sonnet | 08-docs-closeout.md | DONE | — |
| 09 | docs | close-out (fmt fix) | docs-engineer | sonnet | 08-docs-closeout.md | DONE | — |
| 10 | docs | close-out (fmt fix) | docs-engineer | sonnet | 08-docs-closeout.md | DONE | — |
| 11 | docs | close-out (slice log) | docs-engineer | sonnet | 11-docs-slicelog.md | DONE | — |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| human_decision | user | (prior turn) | placement: Backlog story, no new epic (same pattern as US-37.1) | CARRIED |
| source | 2026-08-21-dynamic-sector-classification/10-quant-audit.md | § Findings FINDING 2 | MINOR: taxonomy lookup case/whitespace-sensitive vs FMP drift | OPEN |
| source | 2026-08-21-dynamic-sector-classification/run.md | Open table | get_company_profile `cached` meta flag hardcoded True (market_data.py:474) | OPEN |
| source | 2026-08-21-dynamic-sector-classification/09-test.md | § risks | FMP-profile mock/stub pattern duplicated across 3 test files, no shared scaffolding | ABSORBED (T-37.2.3) |
| filing_note | 01-story | story "Filing note" | filed as US-37.2 under existing Epic 37, matching US-9.6/US-27.9 follow-up-story convention | OPEN |
| finding | 01-story | § risks | same hardcoded cached:True bug shape exists in 4 other MarketDataService methods beyond get_company_profile — undiagnosed, out of scope | CARRIED |
| infra | dispatch 01 | (report format) | check_report.py failed on `command: NONE — <trailing text>`; fixed by dispatch 02 (bare NONE required) | ABSORBED |
| should_fix | 04-backend | § risks | cache-flag fix re-derives fmp.py's internal cache-key formula from outside (scope excluded fmp.py); clean fix belongs in fmp.py itself — future small follow-up | CARRIED |
| risk | 04-backend | § risks | edge case: miss-then-failed-fetch-falls-back-to-stale-cache still reports cached:False though data was cache-served — not in AC3/AC4's primary path | CARRIED |
| risk | 07-review | § Dead-code note | fixtures.py's DEFAULT_COMPANY_PROFILE unreferenced by executable code, silent at gate's 80% confidence threshold — worth an eyeball only if threshold tightens | CARRIED |
| open_decision | 08-docs-closeout | § Handoff detail: slice-log draft | slice-log one-liner — human approved, written verbatim by 11-docs-slicelog | ABSORBED |
| infra | dispatch 08 | (report format) | check_report.py failed: 4 bullets over 400-char hard limit; fixed by 09, which then needed 10 to add missing Orchestrator brief header | ABSORBED |

## Rounds
| finding | lane | round | of |
|---|---|---|---|

## Cost
| metric | value |
|---|---|
| dispatches | 11 |
| rounds | 0 |
| by model | sonnet 11 |
| escalations | none |

## Cost note
Full suite green post T-37.2.4: 77 tests in the touched files pass; full
run_all_tests.py green, no goldens drift, dead-code gate clean.
