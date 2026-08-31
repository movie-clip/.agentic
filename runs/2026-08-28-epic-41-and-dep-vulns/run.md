# RUN 2026-08-28-epic-41-and-dep-vulns
request:      1. open Epic 41   3. create story for this problem   4. fix it
              [clarified: open Epic 41 (Documentation & Roadmap Accuracy Reconciliation);
               Epic 41 gets a doc-reconciliation story (CARRIED item 4 from run
               2026-08-27-next-epic-or-story); dependency vulnerabilities get their
               OWN separate story (CARRIED item 3); build both]
agentic_root: C:\projects\investments\.agentic
story:        NONE
status:       CLOSED
next:         none — CLOSED
final_verify: python scripts/run_all_tests.py — exit 0 "All tests passed" (backend pytest + desktop vitest + tsc --noEmit + dead-code strict gate; test_roadmap_epic_ordering.py GREEN with Epic 41/42 sections inserted, 42>41>40>…>8). Ready for human commit.
final_verify: b3ug4z39e — python scripts/run_all_tests.py exit 0 "All tests passed" after 06+07 landed; US-41.3 impl verified, 07 roadmap guard now GREEN
route:        full
express:      no
decisions:    user 2026-08-28 — (1) dep-vuln work → NEW Epic 42 "Dependency Vulnerability Remediation" (findings-first, sibling Epic 21/36); (2) US-41.1 → under Epic 41 with WIDENED charter line ("...plus one carried Dashboard-trust story"); (3) Story B → AUDIT story (US-42.1) this run only, remediation deferred to a follow-up run
gates:        quant-audit skipped (US-41.3 AC3 re-audit found no methodology/trust staleness; US-42.1 audit-only, 0 analytic movement in trial bumps, owner waived) · integration PASS (11, both stories) · review PASS (12, both stories; full suite green: backend 949 / frontend 359 / tsc / dead-code clean)

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | product | — | producer | sonnet | 01-delivery-brief.md | DONE | — |
| 02 | story | — | story-author | sonnet | 02-story-us41.3.md | DONE | — |
| 03 | story | — | story-author | sonnet | 03-story-us42.1.md | DONE | — |
| 04 | design | DESIGN | tech-lead | sonnet | 04-design-us41.3.md | DONE | — |
| 05 | design | DESIGN | tech-lead | sonnet | 05-design-us42.1.md | DONE | — |
| 06 | docs | — | docs-engineer | sonnet | 06-docs-us41.3.md | DONE | — |
| 07 | test | — | test-engineer | sonnet | 07-test-us41.3.md | PARTIAL | — |
| 08 | backend | — | backend-engineer | sonnet | 08-backend-us42.1.md | DONE (PARTIAL: 1 fail exogenous = red-before roadmap guard, fixed by 06) | — |
| 09 | frontend | — | frontend-engineer | sonnet | 09-frontend-us42.1.md | DONE | PASS |
| 10 | docs | — | docs-engineer | sonnet | 10-docs-us42.1.md | DONE | — |
| 11 | integration | INTEGRATION | tech-lead | sonnet | 11-integration.md | DONE | PASS |
| 12 | review | — | reviewer | sonnet | 12-review.md | DONE | PASS |
| 13 | docs | — | docs-engineer | sonnet | 13-docs-closeout.md | DONE | — |

## Open  (all CARRIED — handoffs to the human / the deferred remediation run)
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| quant_referral | 06-docs / 13-docs (F-10) | financial-methodology.md:2425/581/587/2427 vs US-34.3 | −$53.13 (US-34.3) unreconciled with −$58.11/−$19.98 (methodology); scout § F 2026-08-27, still live; needs a standalone quant-lane look — barred from every docs order this run | CARRIED |
| plan | 10-docs / 13-docs (Epic 42 PRD) | Epic 42 forward plan | remediation stories NOT authored (deferred run): (a) 1 backend golden-safe bump story F-2/F-3/F-4/F-5; (a) 1 lockfile-only apps/desktop story F-6; (c) a FastAPI-bump story must land before F-1 starlette | CARRIED |
| finding | 09/10/13-docs | Epic 42 scope | broader apps/desktop advisories (vite, esbuild, postcss, nanoid, @vitest/mocker, vite-node) are in Epic 42 scope but UNASSESSED — need their own US-42.x assessment story; do NOT `npm audit fix` F-6 blindly | CARRIED |
| finding | 08-backend | assessment doc + Epic 42 PRD | pip-audit found 37 advisory records across the 5 backend packages (22 for pypdf) — the "6 advisories" framing undercounts; one-finding-per-package structure holds, real count recorded | CARRIED |
| limitation | 08-backend / 12-review | assessment doc provenance | US-42.1 AC5 golden/analytic impact assessed on a 16-file/437-test sensitive subset, not the full suite — a bump moving an output covered only by an excluded test would not have been caught; disclosed in the doc | CARRIED |
| story | 13-docs | US-41.1 | stays Backlog under Epic 41 — a Dashboard-trust chart-annotation feature, needs its own build run; dead-branch DELETE decision already made (2026-08-27) | CARRIED |
| should_fix | 13-docs | § risks | US-41.1 + US-41.2 story files keep stale in-body prose ("Backlog, no epic yet" / "shipped as a standalone Backlog story") — order 13 flipped only the Epic: field; a later docs pass could reconcile the prose | CARRIED |

## Closed  (absorbed / resolved this run)
| kind | from | absorbed by | one-line |
|---|---|---|---|
| context | prev run | 01-brief, 13-docs | Epic 41 recommendation + US-41.2 "no epic home" → Epic 41 opened, US-41.2 record migrated into its roadmap section |
| decision | 01-brief § Open decisions | user 2026-08-28 | Story B → Epic 42 (new); US-41.1 → Epic 41 with widened charter line; Story B → audit-only this run; US-42.1 quant sign-off → not required |
| decision | 01-brief § Open decisions | 04-design | US-41.3 guard test → SHIPS (test_roadmap_epic_ordering.py) |
| draft | 02/03-story | 04/05 DESIGN → build → gates | US-41.3 + US-42.1 both approved as-is, designed, built, integration PASS, acceptance PASS |
| plan | 04-design | 06-docs / 07-test | US-41.3: AC1 confirmation, AC2 one-line citation, AC4 Epic 23/24 block swap, guard shipped — all landed |
| risk | 04-design § risks | 06-docs | AC6 in-place-only rule respected; prd/README.md needed no edit (residue already closed by prior runs) |
| plan | 05-design | 08/09/10 | US-42.1: 3-lane split, worktree-isolated trial bumps, offline degrade path — all executed (network was available, real bumps ran) |
| risk | 05-design § risks | 08-backend | pypdf placeholder GHSA not carried into F-2; starlette → bucket (c) blocked as predicted |
| risk | 05-design § risks | 08-backend | AC5 guardrail-1: trial bumps moved ZERO goldens/analytic outputs → nothing to carry to remediation quant-audit |
| status | 07-test | b3ug4z39e | roadmap guard red-before (Epic 23<24) → GREEN after 06's swap; final suite exit 0 |
| status | 08-backend | b3ug4z39e | PARTIAL/FAIL was exogenous (red-before guard); manifests byte-identical, findings transcribed verbatim by 10 |
| finding | 09-frontend | 10-docs / Epic 42 PRD | F-6 @babel/core GHSA-4x5r-pxfx-6jf8 (low), build-time only, lockfile-only bump → bucket (a) |
| finding | 06-docs | 11 integration / 12 review | US-41.3 six items landed; AC3 body re-audit found NO methodology/trust staleness |
| finding | 08-backend | 10-docs / Epic 42 PRD | F-1..F-5: pypdf/multipart/pydantic-settings/python-dotenv golden-safe (a); starlette blocked (c) |
| risk | 06-docs § risks | 11 integration | AC3 "~16→~25 service files" edit ruled correct factual-staleness fix (dir has 25 modules) |
| finding | 10-docs | 12 review / 13 PRD fold-in | dependency-advisory-assessment-2026-08.md written; AC1-AC11 ticked; folded into Epic 42 PRD |
| CR-1 | 11 integration | 13-docs | US-42.1 draft banner cleared, Open-decisions resolved |
| CR-2 | 11 integration | 13-docs | US-41.3 → Status Done + close-out block, AC7 + T-41.3.4 ticked |

## Rounds
| finding | lane | round | of |
|---|---|---|---|
<!-- none — integration PASS both stories first pass; CR-1/CR-2 are SHOULD_FIX for close-out 13, not blocking rounds -->

## Change requests (non-blocking, → close-out 13)
| id | lane | severity | one-line |
|---|---|---|---|
| CR-1 | docs | SHOULD_FIX | US-42.1 story: clear draft/not-approved banner + resolve stale Open-decisions section (quant sign-off already decided: no) |
| CR-2 | docs | SHOULD_FIX | US-41.3 story: flip Status Next phase → Done + close-out block, to match US-42.1 |

## Cost
| metric | value |
|---|---|
| dispatches | 13 |
| rounds | 0 |
| by model | sonnet 13 |
| escalations | none |
| notes | 2 SHOULD_FIX CRs (CR-1/CR-2) applied in the existing close-out order 13, not re-dispatch rounds. 3 background suite runs by the orchestrator (b3ug4z39e mid-run, b7u7xx3df final, + one earlier). 10-integration ran on a session that briefly hit a rate-limit in an earlier run — not this run. |
