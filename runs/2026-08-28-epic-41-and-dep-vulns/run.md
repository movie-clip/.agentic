# RUN 2026-08-28-epic-41-and-dep-vulns
request:      1. open Epic 41   3. create story for this problem   4. fix it
              [clarified: open Epic 41 (Documentation & Roadmap Accuracy Reconciliation);
               Epic 41 gets a doc-reconciliation story (CARRIED item 4 from run
               2026-08-27-next-epic-or-story); dependency vulnerabilities get their
               OWN separate story (CARRIED item 3); build both]
agentic_root: C:\projects\investments\.agentic
story:        NONE
status:       DISPATCHING
next:         await 13 close-out head; derive (--emit-head); orchestrator runs python scripts/run_all_tests.py (roadmap guard checks epic-section order); final ledger walk + Cost + run_cost.py; status CLOSED
final_verify: b3ug4z39e — python scripts/run_all_tests.py exit 0 "All tests passed" after 06+07 landed; US-41.3 impl verified, 07 roadmap guard now GREEN
route:        full
express:      no
decisions:    user 2026-08-28 — (1) dep-vuln work → NEW Epic 42 "Dependency Vulnerability Remediation" (findings-first, sibling Epic 21/36); (2) US-41.1 → under Epic 41 with WIDENED charter line ("...plus one carried Dashboard-trust story"); (3) Story B → AUDIT story (US-42.1) this run only, remediation deferred to a follow-up run
gates:        quant-audit — SKIPPED (US-41.3 AC3 re-audit found no methodology/trust staleness; US-42.1 audit-only, 0 analytic movement in trial bumps, owner waived) · integration — PASS both (11) · review — PASS both (12; full suite green: backend 949 / frontend 359 / tsc / dead-code clean)

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
| 11 | integration | INTEGRATION | tech-lead | sonnet | 11-integration.md | DONE | PASS (both) |
| 12 | review | — | reviewer | sonnet | 12-review.md | DONE | PASS (both) |
| 13 | docs | — | docs-engineer | sonnet | 13-docs-closeout.md | pending | — |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| context | prev run | runs/2026-08-27-next-epic-or-story/03-delivery-brief.md | producer already recommended "Epic 41 — Documentation & Roadmap Accuracy Reconciliation", sibling to Epic 32/36, findings-first | OPEN |
| context | prev run | runs/2026-08-27-next-epic-or-story/run.md § Open | US-41.2 shipped (integration+review PASS) but recorded as a narrative para, no epic home; US-41.1 deferred, its header reserves US-41.1 under any Epic 41 | OPEN |
| plan | 01-brief | § Stories | Epic 41 setup = docs-lane close-out (PRD folding 02-scout §A-I, migrate US-41.2 record, reslot index, flip Epic field, NO renames) | OPEN — 12+ close-out |
| plan | 01-brief | § Stories | Story A US-41.3 = 6 carried doc-reconciliation items; ACs one-per-item + suite green; item (3) current-product-state body re-audit may spawn quant referral | OPEN — 02 authors |
| plan | 01-brief | § Stories | Story B = US-42.1 audit-only (6 advisories: reachability, min safe version, golden impact; NO version change); Epic 42 setup = docs close-out; remediation stories deferred | OPEN — 03 authors |
| decision | 01-brief | § Open decisions | Story A guard test — producer says leave to tech-lead/story-author, not a blocker (only the roadmap-ordering item is mechanically guardable) | OPEN — DESIGN call |
| decision | 01-brief | § Open decisions | quant-audit for Story B remediation bumps — DESIGN-time call per remediation story; not this run | CARRIED (remediation run) |
| draft | 02-story | docs/product/stories/US-41.3-status-and-navigation-doc-reconciliation.md | US-41.3 — APPROVED as-is by user 2026-08-28 | ABSORBED (04 DESIGN) |
| draft | 03-story | docs/product/stories/US-42.1-assess-outstanding-dependency-advisories.md | US-42.1 — APPROVED as-is by user 2026-08-28; quant sign-off NOT required (gate line = integration + review only) | ABSORBED (05 DESIGN) |
| plan | 04-design | § verdicts | US-41.3: T-41.3.4 guard SHIPS (new test_roadmap_epic_ordering.py); AC1=confirmation; AC2=1 line (correlation-fields.md:84→reconciliation.py); factor-drift-fields.md N/A; AC4=swap Epic 23/24 blocks; no schema/route/golden impact | OPEN — 06/07 absorb |
| risk | 04-design | § risks | AC6 tension: in-place label/pointer/date fixes YES, structural index regroup NO; prd/README.md § Index → minimal de-assert only, full rebuild is Epic 41 close-out | OPEN — 06 absorbs |
| plan | 05-design | § Lane split | US-42.1: T-42.1.1→backend-engineer (F-1..F-5), T-42.1.2→frontend-engineer (F-6), T-42.1.3→docs-engineer (write-up); trial bump in git worktree/out-of-repo venv; offline degrade per-finding | OPEN — 08/09/10 absorb |
| risk | 05-design | § risks | test_audit_dependencies.py:43 has placeholder GHSA-xxxx-xxxx-xxxx for pypdf — fixture text, do NOT carry into F-2; starlette bump breaks FastAPI 0.119.1 collection → "blocked" finding bucket (c) | OPEN — 08 absorbs |
| risk | 05-design | § risks | AC5 trial-bump guardrail-1 tension: owner waived quant-audit for US-42.1; 08 must carry forward which observations touched analytic output so REMEDIATION stories route them to quant | OPEN — 08 absorbs, then CARRIED to remediation run |
| status | 07-test | test_roadmap_epic_ordering.py | PARTIAL / verification FAIL = INTENDED red-before (Epic 23 before 24 in current roadmap); guard goes GREEN automatically once 06 swaps the blocks. Final suite run after 06 confirms. Not a defect | OPEN — resolves when 06 lands |
| finding | 09-frontend | § F-6 | @babel/core GHSA-4x5r-pxfx-6jf8/CVE-2026-49356 (low), build-time only, NO runtime surface, lockfile-only bump 7.29.0→7.29.6/7.29.7 resolves it; bucket (a) safe; live GH Advisory DB query (env HAS network); manifests byte-identical, vitest+tsc green | OPEN — 10 consolidates |
| finding | 06-docs | § handoff | US-41.3 landed: AC2 citation fixed, AC4 roadmap 23/24 swap (now 33 headings strict-descending 40→8), AC5 CLAUDE.md row, AC3 one stale service-file count fixed (NO methodology staleness — quant-referral branch did not fire), AC6 all residue already closed | OPEN — 06/07 → integration+review |
| quant_referral | 06-docs | financial-methodology.md:2425/581/587/2427 vs US-34.3 | −$53.13 (US-34.3) still unreconciled with −$58.11/−$19.98 (methodology); scout § F 2026-08-27, still live; methodology-doc figure reconciliation, out of every docs order's scope — needs a quant look | CARRIED (surface to user) |
| risk | 06-docs | § risks | AC3 "~16→~25 service files" edit borderline shipped-feature-desc vs architecture-count; treated as factual staleness, reviewer may revert that one line | OPEN — 11 reviewer |
| finding | 08-backend | § Findings | F-2 pypdf→6.15.0, F-3 python-multipart→0.0.31, F-4 pydantic-settings→2.14.2, F-5 python-dotenv→1.2.2 all bucket (a) golden-safe (437-test subset identical); F-1 starlette bucket (c) BLOCKED (FastAPI 0.119.1 pins starlette<0.49; needs FastAPI-bump story first). NO analytic movement anywhere → no remediation needs quant-audit | OPEN — 10 consolidates |
| finding | 08-backend | § risks | pip-audit found 37 advisory records across the 5 packages (22 for pypdf) — far more than the "5 advisories" story framing; one-finding-per-package structure still holds but framing was inaccurate | CARRIED (note to user + PRD) |
| finding | 10-docs / 09-frontend | § handoff | apps/desktop tree ALSO carries moderate/high advisories on vite, esbuild, postcss, nanoid, @vitest/mocker, vite-node — out of US-42.1 scope; Epic 42 remediation scope is bigger than the 6 advisories | CARRIED (Epic 42 PRD + user) |
| plan | 10-docs | § handoff | remediation roadmap: (a) 1 backend golden-safe bump story F-2/3/4/5; (a) 1 lockfile-only @babel/core story F-6; (c) F-1 starlette needs a FastAPI-bump story FIRST | CARRIED (remediation run) |
| should_fix | 10-docs | § risks | US-42.1 file now Status Done but still has "Draft for human review / not owner-approved" banner + stale "Open decisions" (quant sign-off — owner resolved: no) — clear at close-out (order 13) | OPEN — 13 absorbs |
| finding | 10-docs | docs/product/dependency-advisory-assessment-2026-08.md | NEW findings doc: F-1..F-6, bucket (a) 5 safe / (b) 0 needs-quant / (c) 1 blocked (starlette); live pip-audit + GH Advisory DB (network available); manifests byte-identical; AC1-AC11 ticked | OPEN — 12 review + 13 PRD fold-in |
| status | 08-backend | verification | PARTIAL/FAIL is EXOGENOUS — sole fail was red-before roadmap guard (06 has since swapped the blocks); 08 wrote nothing, manifests byte-identical (AC9 holds) | CLOSED — full suite b3ug4z39e exit 0 "All tests passed" after 06 landed; 07 guard now GREEN |

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|

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
| dispatches | — |
| rounds | — |
| by model | — |
| escalations | — |
