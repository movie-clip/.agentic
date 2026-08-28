REPORT 2026-08-28-epic-41-and-dep-vulns/11
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd services/quant-engine && python -m pytest app/tests/test_roadmap_epic_ordering.py app/tests/test_route_inventory.py app/tests/test_architecture_doc_route_inventory.py app/tests/test_docs_paths.py -q && git diff --stat <the 4 manifests>
  result:    PASS
  detail:    pytest 19 passed (test_roadmap_epic_ordering now GREEN + 3 sibling doc guards). git diff --stat on requirements.txt, requirements-dev.txt, package.json, package-lock.json all empty — manifests byte-identical (AC9). dashboardGoldens.ts unchanged.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - CR-1 (SHOULD_FIX, docs) cr/CR-1.md — US-42.1 story file Status:Done contradicts its still-present draft/not-owner-approved banner and stale Open decisions section; route to close-out order 13
  - CR-2 (SHOULD_FIX, docs) cr/CR-2.md — US-41.3 left Status:Next phase while sibling US-42.1 was flipped to Done in the same run; align at close-out order 13
  - No BLOCKING change requests. Both slices pass engineering integration; close-out (order 13) and the human's AC7 suite run remain

risks:
  - The DriftWindow table + coverage-row relocation visible in `git diff docs/contracts/correlation-fields.md` are run 2026-08-27 residue (prior run order 05-docs.md § changed), NOT this run — this run's only correlation-fields.md change is the L84 RollingRiskPoint citation (AC2). Confirmed against the prior run's artifact. Excluded from review per the work order.
  - 08-backend-us42.1.md is status PARTIAL / verification FAIL; the sole failure was test_roadmap_epic_ordering red-before (now green after order 06's swap landed). Not dependency-related. 10-docs transcribed 08's findings verbatim, correctly.
  - AC3 full line-by-line re-audit of current-product-state.md's 220-line body cannot be independently re-verified here; the docs lane's itemised account is specific and its one correction is factually right. Body AC completeness is the reviewer's gate (order 12).
  - test_roadmap_epic_ordering._MIN_EXPECTED_HEADINGS = 20 vs DESIGN's "N ~= 25" (33 headings today); a looser floor than designed but still non-vacuous. Reasonable test-lane call, not a change request.

## Orchestrator brief

- Overall verdict: PASS. US-41.3: PASS. US-42.1: PASS. No BLOCKING findings; two SHOULD_FIX items, both docs-lane story-file hygiene for close-out order 13.
- Adjudication of 10 § risks item 1 (asked by the work order): SHOULD_FIX, not BLOCKING. The US-42.1 assessment deliverable is complete and correct; a stale "not owner-approved / do not dispatch" banner on a Done story is docs hygiene, owned by order 13 which already touches that file. Nothing engineering-substantive turns on it. Recorded as CR-1.
- US-41.3 verified: AC4 Epic 23/24 swap is a pure block move — Epic 22/23/24/25/26 section blocks are byte-identical HEAD vs working tree; heading run is now strictly descending 40->8 (33 headings). AC2 citation correct — `class RollingRiskPoint` is at schemas/reconciliation.py:122; builder `build_rolling_risk_series` at analytics/risk.py:572 kept as parenthetical. Guard test encodes descending assert + non-vacuous scan + names the offending pair, and is now GREEN. AC3 "~16 -> ~25 service files" is non-methodology, non-trust factual staleness (app/services/ holds 25 non-__init__ modules) — correctly corrected in place.
- US-42.1 verified: F-1..F-6 in the assessment doc are transcribed verbatim from 08 (F-1..F-5) and 09 (F-6) with no softening — the 37-records note, the pypdf CVSS-4.0-unverified severity, and the 16-file/437-test subset limit are all preserved in the findings table, per-finding prose, provenance, and the carried-forward-unverified list. Three-bucket grouping is complete and bijective: (a) F-2,F-3,F-4,F-5,F-6; (b) none; (c) F-1.
- Neither story changed any schema, route, response shape, or analytic output. No app/schemas or app/api edit. dashboardGoldens.ts and backend goldens byte-identical. All four dependency manifests byte-identical (AC9 holds for US-42.1).
- Sections below: none beyond this brief and the report block.
