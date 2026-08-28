# RUN 2026-08-27-next-epic-or-story
request:      start working on epic 41 or what is the next epic or story
agentic_root: C:\projects\investments\.agentic
story:        C:\projects\investments\portfolio\docs\product\stories\US-41.2-system-architecture-doc-accuracy-and-route-guard.md  (APPROVED 2026-08-27, build now)
status:       CLOSED
next:         none — CLOSED
final_verify: python scripts/run_all_tests.py — exit 0, "All tests passed" (backend pytest + desktop vitest + tsc --noEmit + dead-code strict gate). Ready for human commit.
decisions:    user 2026-08-27 — Unit 1 + author Unit 2 story · NO new epic (loose Backlog, US-41.1 keeps its number) · INCLUDE exhaustive 12-contract×20-schema diff · US-41.2 draft APPROVED + build now
state_check:  python scripts/run_all_tests.py — exit 0, "All tests passed" (pytest + vitest + tsc --noEmit + dead-code strict gate all green). Project is in a working state. Kept out of findings per review-route rule.
route:        review  (user pivoted from "build next story" to "review + clean roadmap/docs to a known-good state")
express:      no
gates:        quant-audit — skipped (US-41.2 touches no formula/trust label; DESIGN confirmed no schema/formula/trust change; §F verified clerical by producer) · integration — PASS (10-integration.md) · review — PASS (11-review.md; all 13 ACs satisfied, full suite green: backend 947 / frontend 359 / tsc clean / dead-code clean)

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | product | — | producer | sonnet | 01-delivery-brief.md | DONE | — |
| 02 | recon | — | scout | sonnet | 02-scout.md | DONE | — |
| 03 | product | — | producer | sonnet | 03-delivery-brief.md | DONE | — |
| 04 | docs | — | docs-engineer | sonnet | 04-docs.md | DONE | — |
| 05 | docs | — | docs-engineer | sonnet | 05-docs.md | DONE | — |
| 06 | story | — | story-author | sonnet | 06-story.md | DONE | — |
| 07 | design | DESIGN | tech-lead | sonnet | 07-technical-plan.md | DONE | — |
| 08 | docs | — | docs-engineer | sonnet | 08-docs.md | DONE | — |
| 09 | test | — | test-engineer | sonnet | 09-test.md | DONE | PASS(6 tests) |
| 10 | integration | INTEGRATION | tech-lead | sonnet | 10-integration.md | DONE | PASS |
| 11 | review | — | reviewer | sonnet | 11-review.md | DONE | PASS |
| 12 | docs | — | docs-engineer | sonnet | 12-docs.md | DONE | — |

## Open  (all CARRIED — handoffs to the human, surfaced at close-out)
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| decision | 12-docs | § risks 1 / § handoff | US-41.2 (+US-41.1) have no epic home: roadmap slice log is epic-partitioned, US-41.2 recorded as a narrative para in the living-snapshot section instead — human: confirm that home or open "Epic 41" (would renumber both story files, needs a human `git rm`) | CARRIED |
| finding | 01-delivery-brief | § Already covered | US-41.1 (inline withheld-return annotation) is fully planned in run 2026-08-26-missing-chart-data-0414 but unbuilt — user deferred it this run; dead-branch DELETE decision already made (accept) for whenever it resumes | CARRIED |
| finding | 01-delivery-brief | § Already covered | dependency-vuln hygiene pass (starlette/pypdf/python-multipart/pydantic-settings/python-dotenv + @babel/core) — real advisories, no story exists, needs producer+story | CARRIED |
| should_fix | 05-docs | apps/desktop/src/features/portfolio/types.ts | TS-type columns for the DriftWindow table + relocated `coverage` row that order 05 added to correlation-fields.md are unverified against types.ts — route to a frontend/test lane | CARRIED |
| should_fix | 05-docs / 12-docs | correlation-fields.md, factor-drift-fields.md | "**Backend schema:**" header lines cite analytics functions; the actual Pydantic class (RollingRiskPoint) is in reconciliation.py — header-citation nuance, future doc pass | CARRIED |
| should_fix | 04-docs / 12-docs | current-product-state.md | body below the header was not re-audited against shipped code this run — "current through Epic 40" rests on scout + producer spot-checks, not a fresh audit | CARRIED |
| should_fix | 04-docs | epic-roadmap.md | roadmap's own per-epic section ordering is non-monotonic (Epic 23 section precedes Epic 24) — cosmetic, future roadmap pass | CARRIED |
| should_fix | 12-docs | CLAUDE.md | "Where to find what" doc map does not list the new docs/contracts/currency-risk-fields.md — one-row add next time CLAUDE.md is touched | CARRIED |

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|
| pivot | user | — | route changed full→review — user declined building US-41.1 now, asked for a roadmap/doc clean-up to a known-good baseline |
| finding | 02-scout § A | 08/09/10/11 (US-41.2) | system-architecture.md ~30 epics stale — rewritten to the 15 shipped routers + a new route-inventory guard; integration + acceptance PASS |
| finding | 02-scout § B | 04-docs | stories/README.md 6 stale labels, missing Epic 30 heading, orphan US-41.1, build-story prose — all reconciled |
| finding | 02-scout § C,D,E,G | 04-docs | Epic 40 "PRD: none" x3-4, prd/README.md index ~35 epics stale, current-product-state header date, build-story prose — all fixed; CLAUDE.md Epic-34 pointer left (hedged by design, not a finding) |
| finding | 02-scout § F | 04-docs | financial-methodology.md withholding rule confirmed consistent (no action); −$53.13 clerical strings in US-34.3 → −$58.11 |
| finding | 02-scout § H | 05-docs | exhaustive contract-doc × schema sweep: 11 docs diffed, correlation-fields.md + diagnostics-fields.md corrected (5 rows), 0 schema-side smells |
| finding | 02-scout § I | — | confirmed NOT drifted: epic-roadmap.md snapshot, CLAUDE.md route list, current-product-state.md body, methodology withholding passages |
| plan | 03-delivery-brief Unit 1 | 04-docs | docs-lane reconciliation pass, no story — landed |
| plan | 03-delivery-brief Unit 2 | 06-story → US-41.2 | proposed story authored, approved by user, built, gated |
| decision | 01/03 delivery-brief | user 2026-08-27 | epic framing → NO new epic (loose Backlog); exhaustive contract diff → INCLUDE; US-41.2 draft → approve + build |
| decision | user 2026-08-27 | — | US-41.1 dead-branch: accept DESIGN's DELETE — carried to whenever US-41.1 build resumes |
| pack_correction | 03 / 07 | 04-docs (item 1), 12-docs (item 2) | pack-corrections.md fully applied: project.md build-story para (04) + capabilities/architecture.md "The seams" currency-risk (12) |
| contract_note | 07-plan | DESIGN | US-41.2 changes NO schema/route/response shape — nothing to mirror |
| plan | 07-plan § Guard / § Data Flow | 09-test / 08-docs | guard design + Data Flow rewrite bounds — both absorbed as specified |
| should_fix | 07-plan § risks | 08-docs | 3 out-of-AC-map removed-surface refs (lines 24/25/357) swept; line-246 clause dropped — integration PASS confirms both |
| deviation | 08-docs § risks | 10-integration | blank-line-vs-not in router list: tech-lead adjudicated NO blank line correct (plan example was self-inconsistent) |
| handoff | 04-docs | 12-docs | US-41.2 index row + roadmap header-date bump + project.md clause tighten — all landed |
| handoff | 05-docs | 12-docs | currency_risk.py had no contract doc — new docs/contracts/currency-risk-fields.md authored from the schema |
| risk | 09-test § risks | 11-review | guard is structure-scoped; reviewer independently greped the doc for phantom route paths (AC1) — clean |
| validation | orchestrator | — | 4 minor check_report nits (01 headline len; 02 brief section-name form; 05 "## Summary table" first; 09 my incomplete head file) — each dispositioned, artifact read where needed, no work dropped |

## Rounds
| finding | lane | round | of |
|---|---|---|---|

## Cost
| metric | value |
|---|---|
| dispatches | 12 |
| rounds | 0 |
| by model | sonnet 12 |
| escalations | none |
| retries | 10-integration hit a session rate-limit mid-run, auto-resumed and completed (not a round, not an escalation) |
