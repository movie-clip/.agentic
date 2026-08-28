REPORT 2026-08-28-epic-41-and-dep-vulns/10
status:      DONE
verdict:     NONE

changed:
  - docs/product/dependency-advisory-assessment-2026-08.md — NEW consolidated dependency-advisory assessment: F-1..F-6 findings table + per-finding prose, three-bucket remediation grouping (AC7), advisory-data provenance (AC6), PRD fold-in table (AC8)
  - docs/product/stories/US-42.1-assess-outstanding-dependency-advisories.md — appended dated "Close-out — 2026-08-28" block; ticked AC1-AC11 and tickets T-42.1.1/T-42.1.2/T-42.1.3; flipped Status "Next phase" -> "Done"

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    docs lane has no Bash; order's verification field is NONE. Per the order, the full suite (python scripts/run_all_tests.py) already passed exit 0 on 2026-08-28 after orders 06/07, and the orchestrator re-runs it before close-out.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Epic 42 PRD close-out order: fold the assessment doc's "## PRD fold-in list (AC8)" table (id / source / disposition per F-n) into the PRD's "### Findings and disposition" section — the doc is written in that form
  - roadmap / story-index close-out order: US-42.1 is now Status Done; add the epic-roadmap.md slice-log row and the stories/README.md index-row — deliberately NOT done in this order (non_goals)
  - remediation stories are scoped by the three-bucket grouping: (a) one golden-safe backend bump story covering F-2 pypdf / F-3 python-multipart / F-4 pydantic-settings / F-5 python-dotenv; (a) one lockfile-only apps/desktop story for F-6 @babel/core; (c) F-1 starlette needs a FastAPI-bump story to land first
  - frontend lane 09 flagged the apps/desktop tree also carries moderate/high advisories on vite, esbuild, postcss, nanoid, @vitest/mocker, vite-node — out of scope for US-42.1 / F-6, needs its own assessment when Epic 42 is scoped

risks:
  - US-42.1 still carries a top-of-file "Draft for human review — not owner-approved" banner and an "Open decisions" section; the order scoped me to append a close-out block and tick ACs (which I did, incl. Status -> Done), not to edit that prose, so the file now reads inconsistently and a human should clear the banner
  - backend lane report 08 is status PARTIAL / verification FAIL — its sole failure (test_roadmap_epic_ordering.py) is an exogenous in-flight sibling Epic-41 change in the shared tree, not dependency-related; I transcribed 08's findings verbatim as the order directs and did not re-assess
  - AC11 was ticked on the order's statement that the orchestrator ran python scripts/run_all_tests.py to exit 0 on 2026-08-28 after orders 06/07; I have no Bash and did not run it myself
  - the assessment records AC5 golden/analytic impact as observed across a 16-file / 437-test sensitive subset (goldens + route inventory + analytics + importer tests), not the full suite, per backend lane 08 — a bump moving an output covered only by an excluded test would not have been caught; this limit is stated in the doc's provenance section
